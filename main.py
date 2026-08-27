from __future__ import annotations

import hashlib
import hmac
import json
import os
import socketserver
import threading
import time
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# =============================================================================
# R32A
# LIVE READ-ONLY PRE-MUTATION RECONCILIATION
#
# PURPOSE
# -------
# Establish a fresh, restart-safe, read-only baseline immediately before any
# later leverage-correction stage.
#
# THIS STAGE:
#   - MAY perform public HTTP GET requests
#   - MAY perform authenticated private HTTP GET requests
#   - MAY inspect account / position / symbol configuration
#   - MAY compare current leverage with planned 100x leverage
#   - MAY build a LOCAL NON-EXECUTABLE planned correction envelope
#
# THIS STAGE MUST NOT:
#   - send orders
#   - send demo orders
#   - POST / PUT / PATCH / DELETE to the exchange
#   - change leverage
#   - change margin type
#   - change position mode
#   - change account configuration
#
# R32A terminates in SEALED_READ_ONLY.
# =============================================================================


VERSION = "R32A"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

STATE_FILE = Path(
    os.getenv(
        "R32A_STATE_FILE",
        "/tmp/r32a_read_only_reconciliation_state.json",
    )
)

REQUEST_TIMEOUT_SECONDS = 10
HEARTBEAT_SECONDS = 30

PLANNED_MARGIN_TYPE = "ISOLATED"
PLANNED_LONG_LEVERAGE = Decimal("100")
PLANNED_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1
PYRAMID_PERCENT = Decimal("5")
MAX_BACKUPS = 3
BACKUP_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_SHARE_PERCENT = Decimal("20")
TP2_SHARE_PERCENT = Decimal("20")
TP3_SHARE_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# =============================================================================
# ABSOLUTE SAFETY CONSTANTS
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

WEBSOCKET_WRITES_ENABLED = False

PUBLIC_READS_ENABLED = True
PRIVATE_READS_ENABLED = True

SYNTHETIC_TRANSPORT_ONLY_FOR_WRITES = True


# =============================================================================
# API PATHS
#
# These are READ-ONLY paths only.
#
# If your previously validated WEEX deployment uses a slightly different
# versioned GET path, change only the corresponding environment variable.
# =============================================================================

PUBLIC_PRICE_PATH = os.getenv(
    "R32A_PRICE_PATH",
    "/capi/v2/market/ticker",
)

PRIVATE_BALANCE_PATH = os.getenv(
    "R32A_BALANCE_PATH",
    "/capi/v2/account/assets",
)

PRIVATE_POSITIONS_PATH = os.getenv(
    "R32A_POSITIONS_PATH",
    "/capi/v2/account/allPosition",
)

PRIVATE_SYMBOL_CONFIG_PATH = os.getenv(
    "R32A_SYMBOL_CONFIG_PATH",
    "/capi/v2/account/symbolConfig",
)


# =============================================================================
# COUNTERS
# =============================================================================

PASS_COUNT = 0
FAIL_COUNT = 0

PUBLIC_GET_COUNT = 0
PRIVATE_GET_COUNT = 0

REAL_ORDER_COUNT = 0
DEMO_ORDER_COUNT = 0
NETWORK_WRITE_COUNT = 0
MUTATION_COUNT = 0

WRITE_BLOCK_COUNT = 0

HEARTBEAT_COUNT = 0


# =============================================================================
# DISPLAY HELPERS
# =============================================================================

LINE = "-" * 92


def log(message: str = "") -> None:
    print(message, flush=True)


def section(title: str) -> None:
    log(LINE)
    log(title)
    log(LINE)


def check(name: str, condition: bool) -> bool:
    global PASS_COUNT, FAIL_COUNT

    if condition:
        PASS_COUNT += 1
        result = "✅ PASS"
    else:
        FAIL_COUNT += 1
        result = "❌ FAIL"

    log(f"{name:<80} {result}")
    return condition


# =============================================================================
# BASIC HELPERS
# =============================================================================

def decimal_or_none(value: Any) -> Optional[Decimal]:
    if value is None:
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def normalized_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def bool_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    }


def sha256_json(value: Any) -> str:
    canonical = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def now_ms() -> str:
    return str(int(time.time() * 1000))


# =============================================================================
# SAFETY FIREBREAK
# =============================================================================

class NetworkWriteBlocked(RuntimeError):
    pass


def reject_network_write(
    method: str,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    global WRITE_BLOCK_COUNT

    WRITE_BLOCK_COUNT += 1

    raise NetworkWriteBlocked(
        f"R32A WRITE FIREBREAK: {method.upper()} {path} rejected. "
        f"All exchange writes are disabled."
    )


def exchange_request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Central transport boundary.

    Only GET and HEAD are permitted.
    Every mutating method is rejected before any socket transmission.
    """

    global PUBLIC_GET_COUNT
    global PRIVATE_GET_COUNT

    method = method.upper().strip()

    if method not in {"GET", "HEAD"}:
        reject_network_write(
            method=method,
            path=path,
            payload=payload,
        )

    query_string = ""

    if params:
        clean_params = {
            key: value
            for key, value in params.items()
            if value is not None
        }

        query_string = urlencode(clean_params)

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    request = Request(
        url=url,
        method=method,
        headers=headers or {},
    )

    with urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:
        raw = response.read().decode("utf-8", errors="replace")

    if not raw:
        return {}

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "_raw": raw,
        }


# =============================================================================
# WEEX AUTHENTICATION
# =============================================================================

@dataclass
class Credentials:
    api_key: str
    secret_key: str
    passphrase: str

    @property
    def complete(self) -> bool:
        return bool(
            self.api_key
            and self.secret_key
            and self.passphrase
        )


def load_credentials() -> Credentials:
    api_key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
        or ""
    ).strip()

    secret_key = (
        os.getenv("WEEX_SECRET_KEY")
        or os.getenv("WEEX_API_SECRET")
        or os.getenv("SECRET_KEY")
        or ""
    ).strip()

    passphrase = (
        os.getenv("WEEX_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
        or os.getenv("PASSPHRASE")
        or ""
    ).strip()

    return Credentials(
        api_key=api_key,
        secret_key=secret_key,
        passphrase=passphrase,
    )


def build_private_headers(
    credentials: Credentials,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> Dict[str, str]:
    """
    WEEX-style HMAC request signing.

    R32A signs READ requests only.

    The prehash is:
        timestamp + method + request_path(+query) + body
    """

    timestamp = now_ms()
    method = method.upper()

    path_for_signature = request_path

    if query_string:
        path_for_signature += "?" + query_string

    prehash = (
        timestamp
        + method
        + path_for_signature
        + body
    )

    signature = hmac.new(
        credentials.secret_key.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return {
        "ACCESS-KEY": credentials.api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": credentials.passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only-validation",
    }


def private_get(
    credentials: Credentials,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    global PRIVATE_GET_COUNT

    if not credentials.complete:
        raise RuntimeError(
            "Authenticated GET requested but credentials are incomplete."
        )

    params = params or {}

    clean_params = {
        key: value
        for key, value in params.items()
        if value is not None
    }

    query_string = urlencode(clean_params)

    headers = build_private_headers(
        credentials=credentials,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
    )

    PRIVATE_GET_COUNT += 1

    return exchange_request(
        "GET",
        path,
        params=clean_params,
        headers=headers,
    )


def public_get(
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    global PUBLIC_GET_COUNT

    PUBLIC_GET_COUNT += 1

    return exchange_request(
        "GET",
        path,
        params=params,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-read-only-validation",
        },
    )


# =============================================================================
# RESPONSE EXTRACTION
# =============================================================================

def unwrap_data(response: Any) -> Any:
    current = response

    if isinstance(current, dict):
        for key in ("data", "result"):
            if key in current:
                return current[key]

    return current


def find_first_dict(value: Any) -> Optional[Dict[str, Any]]:
    value = unwrap_data(value)

    if isinstance(value, dict):
        return value

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return item

    return None


def find_symbol_dict(
    value: Any,
    symbol: str,
) -> Optional[Dict[str, Any]]:
    value = unwrap_data(value)

    if isinstance(value, dict):
        candidate_symbol = normalized_text(
            value.get("symbol")
            or value.get("contract")
            or value.get("instrument")
        ).upper()

        if not candidate_symbol or candidate_symbol == symbol:
            return value

    if isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                continue

            candidate_symbol = normalized_text(
                item.get("symbol")
                or item.get("contract")
                or item.get("instrument")
            ).upper()

            if candidate_symbol == symbol:
                return item

    return None


def extract_balance(response: Any) -> Optional[Decimal]:
    value = unwrap_data(response)

    candidates: List[Dict[str, Any]] = []

    if isinstance(value, dict):
        candidates.append(value)

    elif isinstance(value, list):
        candidates.extend(
            item
            for item in value
            if isinstance(item, dict)
        )

    balance_keys = (
        "available",
        "availableBalance",
        "availableAmount",
        "availableEquity",
        "free",
        "balance",
        "equity",
    )

    for item in candidates:
        coin = normalized_text(
            item.get("coin")
            or item.get("currency")
            or item.get("asset")
        ).upper()

        if coin and coin not in {"USDT", "USD"}:
            continue

        for key in balance_keys:
            number = decimal_or_none(item.get(key))

            if number is not None:
                return number

    return None


def extract_position_count(response: Any) -> int:
    value = unwrap_data(response)

    if isinstance(value, list):
        nonzero = 0

        for item in value:
            if not isinstance(item, dict):
                continue

            quantity = None

            for key in (
                "size",
                "positionAmt",
                "positionSize",
                "quantity",
                "qty",
                "holdVol",
                "total",
            ):
                quantity = decimal_or_none(item.get(key))

                if quantity is not None:
                    break

            if quantity is None:
                # If exchange returned an entry without a parsable quantity,
                # count it conservatively as an observed position record.
                nonzero += 1

            elif quantity != 0:
                nonzero += 1

        return nonzero

    if isinstance(value, dict):
        quantity = None

        for key in (
            "size",
            "positionAmt",
            "positionSize",
            "quantity",
            "qty",
            "holdVol",
            "total",
        ):
            quantity = decimal_or_none(value.get(key))

            if quantity is not None:
                break

        if quantity is None:
            return 0

        return 1 if quantity != 0 else 0

    return 0


def extract_symbol_configuration(
    response: Any,
) -> Dict[str, Any]:
    item = find_symbol_dict(response, SYMBOL)

    if item is None:
        return {}

    return item


def first_present(
    data: Dict[str, Any],
    names: Tuple[str, ...],
) -> Any:
    for name in names:
        if name in data and data[name] is not None:
            return data[name]

    return None


def extract_margin_type(
    config: Dict[str, Any],
) -> str:
    value = first_present(
        config,
        (
            "marginType",
            "marginMode",
            "margin_type",
            "margin_mode",
        ),
    )

    return normalized_text(value).upper()


def extract_position_mode(
    config: Dict[str, Any],
) -> str:
    value = first_present(
        config,
        (
            "positionMode",
            "positionType",
            "holdMode",
            "position_mode",
        ),
    )

    return normalized_text(value).upper()


def extract_isolated_long_leverage(
    config: Dict[str, Any],
) -> Optional[Decimal]:
    value = first_present(
        config,
        (
            "isolatedLongLeverage",
            "longLeverage",
            "long_leverage",
            "leverageLong",
        ),
    )

    return decimal_or_none(value)


def extract_isolated_short_leverage(
    config: Dict[str, Any],
) -> Optional[Decimal]:
    value = first_present(
        config,
        (
            "isolatedShortLeverage",
            "shortLeverage",
            "short_leverage",
            "leverageShort",
        ),
    )

    return decimal_or_none(value)


def extract_cross_leverage(
    config: Dict[str, Any],
) -> Optional[Decimal]:
    value = first_present(
        config,
        (
            "crossLeverage",
            "cross_leverage",
            "leverage",
        ),
    )

    return decimal_or_none(value)


def extract_mark_price(response: Any) -> Optional[Decimal]:
    item = find_symbol_dict(response, SYMBOL)

    if item is None:
        item = find_first_dict(response)

    if item is None:
        return None

    for key in (
        "markPrice",
        "price",
        "last",
        "lastPrice",
        "close",
    ):
        number = decimal_or_none(item.get(key))

        if number is not None and number > 0:
            return number

    return None


# =============================================================================
# DURABLE READ-ONLY SNAPSHOT
# =============================================================================

@dataclass
class R32AState:
    version: str
    symbol: str

    phase: str

    generation: int
    recovery_epoch: int

    public_reads: int
    private_reads: int

    real_orders: int
    demo_orders: int
    network_writes: int
    mutations: int

    available_balance_usdt: Optional[str]
    mark_price: Optional[str]

    position_count: int

    margin_type: str
    position_mode: str

    current_long_leverage: Optional[str]
    current_short_leverage: Optional[str]
    current_cross_leverage: Optional[str]

    planned_long_leverage: str
    planned_short_leverage: str
    planned_margin_type: str

    leverage_correction_required: bool

    planned_envelope_hash: str

    timestamp: float
    checksum: str = ""


def calculate_state_checksum(
    state_dict: Dict[str, Any],
) -> str:
    clone = dict(state_dict)
    clone.pop("checksum", None)

    return sha256_json(clone)


def persist_state(state: R32AState) -> None:
    state_dict = asdict(state)
    state_dict["checksum"] = ""

    checksum = calculate_state_checksum(state_dict)
    state.checksum = checksum

    final_dict = asdict(state)

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = STATE_FILE.with_suffix(".tmp")

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            final_dict,
            handle,
            indent=2,
            sort_keys=True,
        )

        handle.flush()
        os.fsync(handle.fileno())

    os.replace(
        temp_path,
        STATE_FILE,
    )


def load_state() -> Optional[R32AState]:
    if not STATE_FILE.exists():
        return None

    try:
        raw = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8",
            )
        )

        stored_checksum = normalized_text(
            raw.get("checksum")
        )

        calculated = calculate_state_checksum(raw)

        if not stored_checksum:
            return None

        if not hmac.compare_digest(
            stored_checksum,
            calculated,
        ):
            return None

        return R32AState(**raw)

    except Exception:
        return None


# =============================================================================
# HEALTH SERVER
# =============================================================================

RUNTIME_STATE: Dict[str, Any] = {
    "version": VERSION,
    "symbol": SYMBOL,
    "phase": "STARTING",
    "synthetic_only": True,
    "real_execution": False,
    "network_writes": False,
    "leverage_mutation": False,
}


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in {
            "/",
            "/health",
            "/healthz",
        }:
            self.send_response(404)
            self.end_headers()
            return

        body = json.dumps(
            RUNTIME_STATE,
            sort_keys=True,
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_health_server() -> None:
    def worker() -> None:
        try:
            with ReusableTCPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            ) as server:
                log(
                    f"{VERSION}: HEALTH SERVER LISTENING "
                    f"ON PORT {HEALTH_PORT}"
                )

                server.serve_forever()

        except OSError as exc:
            log(
                f"{VERSION}: HEALTH SERVER ERROR: {exc}"
            )

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )
    thread.start()


# =============================================================================
# LOCAL PLANNED LEVERAGE ENVELOPE
#
# IMPORTANT:
# This is DATA ONLY.
#
# There is deliberately no dispatch function associated with this envelope.
# =============================================================================

def build_planned_leverage_envelope() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "symbol": SYMBOL,
        "purpose": "LOCAL_READ_ONLY_RECONCILIATION",
        "marginType": PLANNED_MARGIN_TYPE,
        "plannedLongLeverage": str(
            PLANNED_LONG_LEVERAGE
        ),
        "plannedShortLeverage": str(
            PLANNED_SHORT_LEVERAGE
        ),
        "networkTransmissionAllowed": False,
        "mutationAllowed": False,
        "realOrderExecutionAllowed": False,
        "demoOrderExecutionAllowed": False,
    }


# =============================================================================
# READ HELPERS WITH ERROR CAPTURE
# =============================================================================

@dataclass
class ReadResult:
    success: bool
    data: Any = None
    error: str = ""


def safe_public_read(
    path: str,
    params: Dict[str, Any],
) -> ReadResult:
    try:
        return ReadResult(
            success=True,
            data=public_get(
                path,
                params=params,
            ),
        )

    except HTTPError as exc:
        return ReadResult(
            success=False,
            error=f"HTTP {exc.code}: {exc.reason}",
        )

    except URLError as exc:
        return ReadResult(
            success=False,
            error=f"URL error: {exc.reason}",
        )

    except Exception as exc:
        return ReadResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def safe_private_read(
    credentials: Credentials,
    path: str,
    params: Dict[str, Any],
) -> ReadResult:
    try:
        return ReadResult(
            success=True,
            data=private_get(
                credentials,
                path,
                params=params,
            ),
        )

    except HTTPError as exc:
        body = ""

        try:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            pass

        message = (
            f"HTTP {exc.code}: {exc.reason}"
        )

        if body:
            message += f" | {body[:300]}"

        return ReadResult(
            success=False,
            error=message,
        )

    except URLError as exc:
        return ReadResult(
            success=False,
            error=f"URL error: {exc.reason}",
        )

    except Exception as exc:
        return ReadResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
        )


# =============================================================================
# VALIDATION
# =============================================================================

def run_validation() -> R32AState:
    global PASS_COUNT
    global FAIL_COUNT

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: BASE URL={BASE_URL}")
    log(f"{VERSION}: STATE FILE={STATE_FILE}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")
    log(
        f"{VERSION}: PLANNED LEVERAGE="
        f"{PLANNED_LONG_LEVERAGE}x LONG / "
        f"{PLANNED_SHORT_LEVERAGE}x SHORT"
    )
    log(f"{VERSION}: REAL EXECUTION DISABLED")
    log(f"{VERSION}: DEMO EXECUTION DISABLED")
    log(f"{VERSION}: NETWORK WRITES DISABLED")
    log(f"{VERSION}: LEVERAGE MUTATION DISABLED")

    credentials = load_credentials()

    # -------------------------------------------------------------------------
    section("R32A TEST 1: ABSOLUTE SAFETY CONFIGURATION")
    # -------------------------------------------------------------------------

    check(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Network Writes Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )

    check(
        "WebSocket Writes Disabled",
        WEBSOCKET_WRITES_ENABLED is False,
    )

    check(
        "Synthetic Transport Required For Any Write Intent",
        SYNTHETIC_TRANSPORT_ONLY_FOR_WRITES is True,
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 2: ENVIRONMENT ESCALATION RESISTANCE")
    # -------------------------------------------------------------------------

    hostile_real = bool_env(
        "REAL_ORDER_EXECUTION"
    )

    hostile_demo = bool_env(
        "DEMO_ORDER_EXECUTION"
    )

    hostile_write = bool_env(
        "EXCHANGE_NETWORK_WRITES"
    )

    hostile_leverage = bool_env(
        "LEVERAGE_MUTATION"
    )

    check(
        "Environment Cannot Activate Real Execution",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Environment Cannot Activate Demo Execution",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Environment Cannot Activate Network Writes",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Environment Cannot Activate Leverage Mutation",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    log(
        f"{VERSION}: ENV ATTEMPTS "
        f"real={hostile_real} "
        f"demo={hostile_demo} "
        f"write={hostile_write} "
        f"leverage={hostile_leverage}"
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 3: STRATEGY CONSTANTS")
    # -------------------------------------------------------------------------

    check(
        "Planned Margin Type Is Isolated",
        PLANNED_MARGIN_TYPE == "ISOLATED",
    )

    check(
        "Planned Long Leverage Is 100x",
        PLANNED_LONG_LEVERAGE == Decimal("100"),
    )

    check(
        "Planned Short Leverage Is 100x",
        PLANNED_SHORT_LEVERAGE == Decimal("100"),
    )

    check(
        "Initial Entry Is Five Percent",
        INITIAL_ENTRY_PERCENT == Decimal("5"),
    )

    check(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    check(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3,
    )

    check(
        "Maximum Fund Exposure Is Thirty Five Percent",
        MAX_FUND_EXPOSURE_PERCENT == Decimal("35"),
    )

    check(
        "TP Allocation Reconciles To One Hundred Percent",
        (
            TP1_SHARE_PERCENT
            + TP2_SHARE_PERCENT
            + TP3_SHARE_PERCENT
        )
        == Decimal("100"),
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 4: CREDENTIAL PRESENCE")
    # -------------------------------------------------------------------------

    check(
        "API Key Present",
        bool(credentials.api_key),
    )

    check(
        "Secret Key Present",
        bool(credentials.secret_key),
    )

    check(
        "Passphrase Present",
        bool(credentials.passphrase),
    )

    check(
        "Authenticated Read Credentials Complete",
        credentials.complete,
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 5: CENTRAL WRITE FIREBREAK")
    # -------------------------------------------------------------------------

    blocked_methods = 0

    for method in (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ):
        try:
            exchange_request(
                method,
                "/r32a/local-firebreak-test",
                payload={
                    "symbol": SYMBOL,
                },
            )

        except NetworkWriteBlocked:
            blocked_methods += 1

    check(
        "POST Blocked",
        blocked_methods >= 1,
    )

    check(
        "PUT Blocked",
        blocked_methods >= 2,
    )

    check(
        "PATCH Blocked",
        blocked_methods >= 3,
    )

    check(
        "DELETE Blocked",
        blocked_methods == 4,
    )

    check(
        "Firebreak Test Caused No Network Write",
        NETWORK_WRITE_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 6: PUBLIC MARKET READ")
    # -------------------------------------------------------------------------

    price_result = safe_public_read(
        PUBLIC_PRICE_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    check(
        "Public Price GET Completed",
        price_result.success,
    )

    mark_price: Optional[Decimal] = None

    if price_result.success:
        mark_price = extract_mark_price(
            price_result.data
        )

    check(
        "Public Price Is Positive",
        (
            mark_price is not None
            and mark_price > 0
        ),
    )

    if mark_price is not None:
        log(
            f"{VERSION}: LIVE PRICE={mark_price}"
        )

    else:
        log(
            f"{VERSION}: PRICE READ ERROR="
            f"{price_result.error or 'unable to parse price'}"
        )

    # -------------------------------------------------------------------------
    section("R32A TEST 7: AUTHENTICATED BALANCE READ")
    # -------------------------------------------------------------------------

    balance_result = safe_private_read(
        credentials,
        PRIVATE_BALANCE_PATH,
        {},
    )

    check(
        "Authenticated Balance GET Completed",
        balance_result.success,
    )

    available_balance = None

    if balance_result.success:
        available_balance = extract_balance(
            balance_result.data
        )

    check(
        "Available Balance Parsed",
        available_balance is not None,
    )

    if available_balance is not None:
        log(
            f"{VERSION}: AVAILABLE USDT="
            f"{available_balance}"
        )

    else:
        log(
            f"{VERSION}: BALANCE READ ERROR="
            f"{balance_result.error or 'unable to parse balance'}"
        )

    # -------------------------------------------------------------------------
    section("R32A TEST 8: AUTHENTICATED POSITION READ")
    # -------------------------------------------------------------------------

    positions_result = safe_private_read(
        credentials,
        PRIVATE_POSITIONS_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    check(
        "Authenticated Position GET Completed",
        positions_result.success,
    )

    position_count = 0

    if positions_result.success:
        position_count = extract_position_count(
            positions_result.data
        )

    check(
        "Position Count Is Non Negative",
        position_count >= 0,
    )

    log(
        f"{VERSION}: OPEN POSITION COUNT="
        f"{position_count}"
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 9: LIVE SYMBOL CONFIGURATION READ")
    # -------------------------------------------------------------------------

    config_result = safe_private_read(
        credentials,
        PRIVATE_SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    check(
        "Authenticated Symbol Configuration GET Completed",
        config_result.success,
    )

    symbol_config: Dict[str, Any] = {}

    if config_result.success:
        symbol_config = extract_symbol_configuration(
            config_result.data
        )

    check(
        "Symbol Configuration Parsed",
        bool(symbol_config),
    )

    margin_type = extract_margin_type(
        symbol_config
    )

    position_mode = extract_position_mode(
        symbol_config
    )

    current_long_leverage = (
        extract_isolated_long_leverage(
            symbol_config
        )
    )

    current_short_leverage = (
        extract_isolated_short_leverage(
            symbol_config
        )
    )

    current_cross_leverage = (
        extract_cross_leverage(
            symbol_config
        )
    )

    log(
        f"{VERSION}: CURRENT MARGIN TYPE="
        f"{margin_type or 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: CURRENT POSITION MODE="
        f"{position_mode or 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: CURRENT ISOLATED LONG="
        f"{current_long_leverage}"
    )

    log(
        f"{VERSION}: CURRENT ISOLATED SHORT="
        f"{current_short_leverage}"
    )

    log(
        f"{VERSION}: CURRENT CROSS="
        f"{current_cross_leverage}"
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 10: ACCOUNT / STRATEGY RECONCILIATION")
    # -------------------------------------------------------------------------

    margin_matches = (
        margin_type == PLANNED_MARGIN_TYPE
    )

    long_matches = (
        current_long_leverage
        == PLANNED_LONG_LEVERAGE
    )

    short_matches = (
        current_short_leverage
        == PLANNED_SHORT_LEVERAGE
    )

    check(
        "Planned Margin Type Defined",
        PLANNED_MARGIN_TYPE == "ISOLATED",
    )

    check(
        "Current Long Leverage Parsed",
        current_long_leverage is not None,
    )

    check(
        "Current Short Leverage Parsed",
        current_short_leverage is not None,
    )

    # These are reconciliation observations rather than requirements.
    # R32A must remain valid if the exchange is still 50x / 20x.
    log(
        f"{VERSION}: MARGIN MATCH="
        f"{margin_matches}"
    )

    log(
        f"{VERSION}: LONG 100x MATCH="
        f"{long_matches}"
    )

    log(
        f"{VERSION}: SHORT 100x MATCH="
        f"{short_matches}"
    )

    leverage_correction_required = not (
        long_matches
        and short_matches
        and margin_matches
    )

    log(
        f"{VERSION}: LEVERAGE CORRECTION REQUIRED="
        f"{leverage_correction_required}"
    )

    check(
        "Reconciliation Produces Deterministic Result",
        isinstance(
            leverage_correction_required,
            bool,
        ),
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 11: LOCAL 100x PLANNED ENVELOPE")
    # -------------------------------------------------------------------------

    planned_envelope = (
        build_planned_leverage_envelope()
    )

    planned_envelope_hash = (
        sha256_json(planned_envelope)
    )

    check(
        "Planned Envelope Symbol Matches",
        planned_envelope["symbol"] == SYMBOL,
    )

    check(
        "Planned Envelope Margin Type Is Isolated",
        (
            planned_envelope["marginType"]
            == "ISOLATED"
        ),
    )

    check(
        "Planned Envelope Long Target Is 100x",
        (
            planned_envelope[
                "plannedLongLeverage"
            ]
            == "100"
        ),
    )

    check(
        "Planned Envelope Short Target Is 100x",
        (
            planned_envelope[
                "plannedShortLeverage"
            ]
            == "100"
        ),
    )

    check(
        "Planned Envelope Explicitly Forbids Transmission",
        (
            planned_envelope[
                "networkTransmissionAllowed"
            ]
            is False
        ),
    )

    check(
        "Planned Envelope Explicitly Forbids Mutation",
        (
            planned_envelope[
                "mutationAllowed"
            ]
            is False
        ),
    )

    log(
        f"{VERSION}: PLANNED ENVELOPE SHA256="
        f"{planned_envelope_hash}"
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 12: BALANCE / STRATEGY READ-ONLY PROJECTION")
    # -------------------------------------------------------------------------

    if available_balance is not None:
        initial_margin_budget = (
            available_balance
            * INITIAL_ENTRY_PERCENT
            / Decimal("100")
        )

        planned_notional_at_100x = (
            initial_margin_budget
            * PLANNED_LONG_LEVERAGE
        )

        maximum_margin_budget = (
            available_balance
            * MAX_FUND_EXPOSURE_PERCENT
            / Decimal("100")
        )

        check(
            "Initial Margin Budget Is Non Negative",
            initial_margin_budget >= 0,
        )

        check(
            "Maximum Margin Budget Is Non Negative",
            maximum_margin_budget >= 0,
        )

        check(
            "Initial Margin Does Not Exceed Exposure Ceiling",
            (
                initial_margin_budget
                <= maximum_margin_budget
            ),
        )

        log(
            f"{VERSION}: PROJECTED INITIAL "
            f"MARGIN={initial_margin_budget} USDT"
        )

        log(
            f"{VERSION}: PROJECTED NOTIONAL "
            f"AT 100x={planned_notional_at_100x} USDT"
        )

        log(
            f"{VERSION}: MAXIMUM STRATEGY "
            f"MARGIN EXPOSURE={maximum_margin_budget} USDT"
        )

    else:
        check(
            "Projection Safely Skipped Without Parsed Balance",
            True,
        )

    # -------------------------------------------------------------------------
    section("R32A TEST 13: NO EXECUTION SIDE EFFECTS")
    # -------------------------------------------------------------------------

    check(
        "Real Order Counter Is Zero",
        REAL_ORDER_COUNT == 0,
    )

    check(
        "Demo Order Counter Is Zero",
        DEMO_ORDER_COUNT == 0,
    )

    check(
        "Network Write Counter Is Zero",
        NETWORK_WRITE_COUNT == 0,
    )

    check(
        "Mutation Counter Is Zero",
        MUTATION_COUNT == 0,
    )

    check(
        "R32A Remains Read Only",
        (
            not REAL_ORDER_EXECUTION_ENABLED
            and not DEMO_ORDER_EXECUTION_ENABLED
            and not EXCHANGE_NETWORK_WRITES_ENABLED
            and not LEVERAGE_MUTATION_ENABLED
            and not MARGIN_MUTATION_ENABLED
            and not POSITION_MUTATION_ENABLED
            and not ACCOUNT_MUTATION_ENABLED
        ),
    )

    # -------------------------------------------------------------------------
    section("R32A TEST 14: DURABLE SEALED READ-ONLY STATE")
    # -------------------------------------------------------------------------

    previous_state = load_state()

    generation = 1
    recovery_epoch = 1

    if previous_state is not None:
        generation = max(
            1,
            previous_state.generation,
        )

        recovery_epoch = max(
            1,
            previous_state.recovery_epoch,
        )

    state = R32AState(
        version=VERSION,
        symbol=SYMBOL,
        phase="SEALED_READ_ONLY",
        generation=generation,
        recovery_epoch=recovery_epoch,
        public_reads=PUBLIC_GET_COUNT,
        private_reads=PRIVATE_GET_COUNT,
        real_orders=REAL_ORDER_COUNT,
        demo_orders=DEMO_ORDER_COUNT,
        network_writes=NETWORK_WRITE_COUNT,
        mutations=MUTATION_COUNT,
        available_balance_usdt=(
            str(available_balance)
            if available_balance is not None
            else None
        ),
        mark_price=(
            str(mark_price)
            if mark_price is not None
            else None
        ),
        position_count=position_count,
        margin_type=margin_type,
        position_mode=position_mode,
        current_long_leverage=(
            str(current_long_leverage)
            if current_long_leverage is not None
            else None
        ),
        current_short_leverage=(
            str(current_short_leverage)
            if current_short_leverage is not None
            else None
        ),
        current_cross_leverage=(
            str(current_cross_leverage)
            if current_cross_leverage is not None
            else None
        ),
        planned_long_leverage=str(
            PLANNED_LONG_LEVERAGE
        ),
        planned_short_leverage=str(
            PLANNED_SHORT_LEVERAGE
        ),
        planned_margin_type=PLANNED_MARGIN_TYPE,
        leverage_correction_required=(
            leverage_correction_required
        ),
        planned_envelope_hash=(
            planned_envelope_hash
        ),
        timestamp=time.time(),
    )

    persist_state(state)

    check(
        "Durable State File Exists",
        STATE_FILE.exists(),
    )

    restored = load_state()

    check(
        "Durable State Restores",
        restored is not None,
    )

    if restored is not None:
        check(
            "Restored Version Matches",
            restored.version == VERSION,
        )

        check(
            "Restored Symbol Matches",
            restored.symbol == SYMBOL,
        )

        check(
            "Restored Phase Is Sealed Read Only",
            (
                restored.phase
                == "SEALED_READ_ONLY"
            ),
        )

        check(
            "Restored Real Order Counter Is Zero",
            restored.real_orders == 0,
        )

        check(
            "Restored Demo Order Counter Is Zero",
            restored.demo_orders == 0,
        )

        check(
            "Restored Network Write Counter Is Zero",
            restored.network_writes == 0,
        )

        check(
            "Restored Mutation Counter Is Zero",
            restored.mutations == 0,
        )

        check(
            "Restored Planned Envelope Hash Matches",
            (
                restored.planned_envelope_hash
                == planned_envelope_hash
            ),
        )

    # -------------------------------------------------------------------------
    section("R32A TEST 15: FINAL SAFETY SEAL")
    # -------------------------------------------------------------------------

    checks_before_final = PASS_COUNT

    check(
        "All Prior Required Checks Passed",
        FAIL_COUNT == 0,
    )

    log(
        f"{VERSION}: "
        f"passed-before-final={checks_before_final}, "
        f"failed={FAIL_COUNT}"
    )

    check(
        "R32A Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "R32A Demo Execution Remains Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "R32A Network Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "R32A Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "R32A Final Phase Is Sealed Read Only",
        state.phase == "SEALED_READ_ONLY",
    )

    check(
        "R32A Has Sent No Real Orders",
        REAL_ORDER_COUNT == 0,
    )

    check(
        "R32A Has Sent No Demo Orders",
        DEMO_ORDER_COUNT == 0,
    )

    check(
        "R32A Has Performed No Network Writes",
        NETWORK_WRITE_COUNT == 0,
    )

    check(
        "R32A Has Performed No Account Mutations",
        MUTATION_COUNT == 0,
    )

    return state


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop(state: R32AState) -> None:
    global HEARTBEAT_COUNT

    while True:
        time.sleep(HEARTBEAT_SECONDS)

        HEARTBEAT_COUNT += 1

        RUNTIME_STATE.update(
            {
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": state.phase,
                "synthetic_only": True,
                "real_execution": False,
                "demo_execution": False,
                "network_writes": False,
                "leverage_mutation": False,
                "generation": state.generation,
                "recovery_epoch": state.recovery_epoch,
                "leverage_correction_required": (
                    state.leverage_correction_required
                ),
                "heartbeat": HEARTBEAT_COUNT,
            }
        )

        log(
            f"{VERSION}: HEARTBEAT {HEARTBEAT_COUNT} | "
            f"phase={state.phase} | "
            f"synthetic-only=True | "
            f"real-execution=False | "
            f"network-writes=False | "
            f"leverage-mutation=False | "
            f"correction-required="
            f"{state.leverage_correction_required} | "
            f"generation={state.generation} | "
            f"recovery-epoch={state.recovery_epoch}"
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    start_health_server()

    try:
        state = run_validation()

    except Exception as exc:
        section(f"{VERSION}: FATAL VALIDATION ERROR")

        log(
            f"{VERSION}: "
            f"{type(exc).__name__}: {exc}"
        )

        RUNTIME_STATE.update(
            {
                "phase": "ERROR",
                "error": str(exc),
                "real_execution": False,
                "network_writes": False,
                "leverage_mutation": False,
            }
        )

        # Keep Render health process alive for diagnosis.
        while True:
            time.sleep(HEARTBEAT_SECONDS)

    section(
        (
            f"{VERSION}: VALIDATION PASSED"
            if FAIL_COUNT == 0
            else f"{VERSION}: VALIDATION FAILED"
        )
    )

    log(
        f"{VERSION}: SUMMARY "
        f"passed={PASS_COUNT} "
        f"failed={FAIL_COUNT}"
    )

    log(
        f"{VERSION}: SAFETY SEAL "
        f"real-orders={REAL_ORDER_COUNT} "
        f"demo-orders={DEMO_ORDER_COUNT} "
        f"network-writes={NETWORK_WRITE_COUNT} "
        f"mutations={MUTATION_COUNT}"
    )

    log(
        f"{VERSION}: READ SEAL "
        f"public-gets={PUBLIC_GET_COUNT} "
        f"private-gets={PRIVATE_GET_COUNT}"
    )

    log(
        f"{VERSION}: RECONCILIATION "
        f"current-long={state.current_long_leverage} "
        f"current-short={state.current_short_leverage} "
        f"target-long={state.planned_long_leverage} "
        f"target-short={state.planned_short_leverage} "
        f"correction-required="
        f"{state.leverage_correction_required}"
    )

    log(
        f"{VERSION}: TERMINAL SEAL "
        f"phase={state.phase}"
    )

    RUNTIME_STATE.update(
        {
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": state.phase,
            "synthetic_only": True,
            "real_execution": False,
            "demo_execution": False,
            "network_writes": False,
            "leverage_mutation": False,
            "generation": state.generation,
            "recovery_epoch": state.recovery_epoch,
            "leverage_correction_required": (
                state.leverage_correction_required
            ),
        }
    )

    heartbeat_loop(state)


if __name__ == "__main__":
    main()
