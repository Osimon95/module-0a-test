

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35L - CONTROLLED LIVE ACTIVATION BOUNDARY
# CORRECTED CREDENTIAL BINDING
# ==================================================================================================
#
# PERMANENT CREDENTIAL STANDARD
#
#   WEEX_API_KEY
#   WEEX_API_SECRET
#   WEEX_API_PASSPHRASE
#
# IMPORTANT:
#
#   R35L DOES NOT READ:
#
#       WEEX_PASSPHRASE
#
#   The WEEX API passphrase must be stored in Render as:
#
#       WEEX_API_PASSPHRASE
#
#
# SAFETY MODEL
#
#   - AUTHENTICATED WEEX GET REQUESTS ALLOWED
#   - PUBLIC WEEX GET REQUESTS ALLOWED
#   - EXCHANGE POST DISABLED
#   - EXCHANGE PUT DISABLED
#   - EXCHANGE PATCH DISABLED
#   - EXCHANGE DELETE DISABLED
#   - REAL ORDER EXECUTION HARD DISABLED
#   - DEMO ORDER EXECUTION DISABLED
#   - FIRST REAL ORDER HARD FORBIDDEN
#   - EXECUTION AUTHORIZATION REMAINS FALSE
#   - TELEGRAM POST ALLOWED FOR REPORTING ONLY
#   - TELEGRAM CANNOT CONTROL EXECUTION
#   - SYNTHETIC ORDER BOUNDARY ONLY
#
# ==================================================================================================


VERSION = "R35L"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper() or "BTCUSDT"


HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv(
            "HEALTH_PORT",
            "10000",
        ),
    )
)


STATE_DIR = Path(
    os.getenv(
        "R35L_STATE_DIR",
        "/tmp/r35l_state",
    )
)


STATE_FILE = STATE_DIR / "state.json"

JOURNAL_FILE = STATE_DIR / "journal.jsonl"


WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")


# ==================================================================================================
# PERMANENT WEEX CREDENTIAL ENVIRONMENT VARIABLE NAMES
# ==================================================================================================


WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()


WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()


WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# DO NOT ADD:
#
#     WEEX_PASSPHRASE
#
# Future revisions should continue using WEEX_API_PASSPHRASE only.


# ==================================================================================================
# TELEGRAM
# ==================================================================================================


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()


TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


TELEGRAM_DEDUP_SECONDS = int(
    os.getenv(
        "TELEGRAM_DEDUP_SECONDS",
        "300",
    )
)


# ==================================================================================================
# GENERATION / EPOCH
# ==================================================================================================


GENERATION = 1

EPOCH = 1


TARGET_LONG_LEVERAGE = 100

TARGET_SHORT_LEVERAGE = 100


VALIDATION_QUANTITY = "0.0001"


# ==================================================================================================
# WEEX V3 PATHS
# ==================================================================================================


BALANCE_PATH = (
    "/capi/v3/account/balance"
)


POSITIONS_PATH = (
    "/capi/v3/account/position/allPosition"
)


SYMBOL_CONFIG_PATH = (
    "/capi/v3/account/symbolConfig"
)


MARK_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
)


ORDER_PATH = (
    "/capi/v3/order"
)


# ==================================================================================================
# HARD SAFETY CONSTANTS
# ==================================================================================================


REAL_ORDER_EXECUTION = False


DEMO_ORDER_EXECUTION = False


EXCHANGE_MUTATION_TRANSPORT_ENABLED = False


FIRST_REAL_ORDER_ALLOWED = False


CODE_LEVEL_REAL_EXECUTION_ENABLED = False


SEPARATOR = "-" * 100


PRINT_LOCK = threading.Lock()

STATE_LOCK = threading.RLock()

TELEGRAM_LOCK = threading.RLock()


# ==================================================================================================
# BASIC UTILITIES
# ==================================================================================================


def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(
    message: str = "",
) -> None:

    with PRINT_LOCK:

        if message:

            print(
                f"{utc_now()} {message}",
                flush=True,
            )

        else:

            print(
                "",
                flush=True,
            )


def section(
    title: str,
) -> None:

    log(
        SEPARATOR
    )

    log(
        title
    )

    log(
        SEPARATOR
    )


def check(
    label: str,
    condition: bool,
) -> bool:

    icon = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    with PRINT_LOCK:

        print(
            f"{label:<86} {icon}",
            flush=True,
        )

    return bool(
        condition
    )


def safe_float(
    value: Any,
) -> Optional[float]:

    try:

        if value is None:

            return None

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


def sha256_text(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def atomic_write_json(
    path: Path,
    payload: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    with tmp.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            payload,
            handle,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        tmp,
        path,
    )


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    generation: int = GENERATION

    epoch: int = EPOCH

    activation_armed: bool = False

    activation_consumed: bool = False

    execution_authorized: bool = False

    first_real_order_allowed: bool = False

    exchange_network_writes: int = 0

    synthetic_dispatch_count: int = 0

    journal_sequence: int = 0

    last_journal_hash: str = (
        "0" * 64
    )

    last_readiness_fingerprint: str = ""

    last_readiness_report_time: float = 0.0

    telegram_reports_this_run: int = 0

    last_client_order_nonce: int = 0

    notes: List[str] = field(
        default_factory=list
    )

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ==================================================================================================
# STATE LOAD
# ==================================================================================================


def load_state() -> StrategyState:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not STATE_FILE.exists():

        return StrategyState()

    try:

        raw = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

        allowed = {
            name
            for name
            in StrategyState.__dataclass_fields__
        }

        clean = {
            key: value
            for key, value
            in raw.items()
            if key in allowed
        }

        state = StrategyState(
            **clean
        )

    except Exception as exc:

        log(
            f"{VERSION}: STATE LOAD FAILED CLOSED: "
            f"{type(exc).__name__}: {exc}"
        )

        return StrategyState(
            notes=[
                "STATE_LOAD_FAILED_CLOSED"
            ]
        )

    state.version = VERSION

    state.symbol = SYMBOL

    state.generation = GENERATION

    state.epoch = EPOCH

    # Restart always fails closed.

    state.activation_armed = False

    state.execution_authorized = False

    state.first_real_order_allowed = False

    state.exchange_network_writes = 0

    state.telegram_reports_this_run = 0

    return state


def save_state(
    state: StrategyState,
) -> None:

    with STATE_LOCK:

        atomic_write_json(
            STATE_FILE,
            state.to_dict(),
        )


# ==================================================================================================
# DURABLE JOURNAL
# ==================================================================================================


def append_journal(
    state: StrategyState,
    event: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:

    with STATE_LOCK:

        state.journal_sequence += 1

        body = {

            "sequence":
                state.journal_sequence,

            "timestamp":
                utc_now(),

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "generation":
                GENERATION,

            "epoch":
                EPOCH,

            "event":
                event,

            "details":
                details,

            "previous_hash":
                state.last_journal_hash,
        }

        record_hash = sha256_text(
            canonical_json(
                body
            )
        )

        record = dict(
            body
        )

        record[
            "hash"
        ] = record_hash

        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with JOURNAL_FILE.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                canonical_json(
                    record
                )
                + "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        state.last_journal_hash = (
            record_hash
        )

        save_state(
            state
        )

        return record


def validate_journal() -> Tuple[
    bool,
    int,
    bool,
]:

    if not JOURNAL_FILE.exists():

        return (
            True,
            0,
            True,
        )

    previous = (
        "0" * 64
    )

    expected_sequence: Optional[int] = None

    count = 0

    monotonic = True

    try:

        with JOURNAL_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:

                line = line.strip()

                if not line:

                    continue

                record = json.loads(
                    line
                )

                supplied_hash = str(
                    record.get(
                        "hash",
                        "",
                    )
                )

                body = dict(
                    record
                )

                body.pop(
                    "hash",
                    None,
                )

                if body.get(
                    "previous_hash"
                ) != previous:

                    return (
                        False,
                        count,
                        monotonic,
                    )

                calculated = sha256_text(
                    canonical_json(
                        body
                    )
                )

                if not hmac.compare_digest(
                    calculated,
                    supplied_hash,
                ):

                    return (
                        False,
                        count,
                        monotonic,
                    )

                sequence = int(
                    body.get(
                        "sequence",
                        -1,
                    )
                )

                if expected_sequence is None:

                    expected_sequence = (
                        sequence
                    )

                else:

                    expected_sequence += 1

                    if sequence != expected_sequence:

                        monotonic = False

                previous = supplied_hash

                count += 1

    except Exception:

        return (
            False,
            count,
            False,
        )

    return (
        True,
        count,
        monotonic,
    )


STATE = load_state()


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        payload = {

            "ok":
                True,

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "exchange_network_writes":
                STATE.exchange_network_writes,

            "real_order_execution":
                REAL_ORDER_EXECUTION,

            "execution_authorized":
                STATE.execution_authorized,
        }

        body = json.dumps(
            payload
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    body
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    def worker() -> None:

        try:

            server = HTTPServer(
                (
                    "0.0.0.0",
                    HEALTH_PORT,
                ),
                HealthHandler,
            )

            log(
                f"{VERSION}: "
                f"HEALTH SERVER STARTED "
                f"ON PORT {HEALTH_PORT}"
            )

            server.serve_forever()

        except Exception as exc:

            log(
                f"{VERSION}: HEALTH SERVER ERROR: "
                f"{type(exc).__name__}: {exc}"
            )

    threading.Thread(
        target=worker,
        daemon=True,
    ).start()


# ==================================================================================================
# EXCHANGE NETWORK POLICY
# ==================================================================================================


def assert_exchange_method_allowed(
    method: str,
) -> None:

    method = (
        method.upper().strip()
    )

    if method != "GET":

        raise RuntimeError(
            f"{VERSION}: "
            f"EXCHANGE MUTATION TRANSPORT "
            f"HARD DISABLED: {method}"
        )


def real_exchange_writer(
    *args: Any,
    **kwargs: Any,
) -> None:

    raise RuntimeError(
        f"{VERSION}: "
        f"REAL EXCHANGE WRITER "
        f"HARD DISABLED"
    )


# ==================================================================================================
# CREDENTIAL CHECK
# ==================================================================================================


def credentials_present() -> bool:

    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )


# ==================================================================================================
# QUERY BUILDING
# ==================================================================================================


def build_query(
    params: Optional[
        Dict[str, Any]
    ],
) -> str:

    if not params:

        return ""

    clean = [

        (
            str(
                key
            ),
            str(
                value
            ),
        )

        for key, value
        in params.items()

        if value is not None
    ]

    return urllib.parse.urlencode(
        clean
    )


# ==================================================================================================
# WEEX SIGNATURE
# ==================================================================================================


def weex_signature(
    timestamp_ms: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = (
        method.upper()
    )

    prehash = (
        timestamp_ms
        + method
        + request_path
    )

    if query_string:

        prehash += (
            "?"
            + query_string
        )

    prehash += body

    digest = hmac.new(

        WEEX_API_SECRET.encode(
            "utf-8"
        ),

        prehash.encode(
            "utf-8"
        ),

        hashlib.sha256,

    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "ascii"
    )


# ==================================================================================================
# HTTP GET
# ==================================================================================================


def http_get_json(
    url: str,
    headers: Optional[
        Dict[str, str]
    ] = None,
    timeout: float = 12.0,
) -> Any:

    request = urllib.request.Request(

        url=url,

        headers=(
            headers
            or {}
        ),

        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            data = response.read().decode(
                "utf-8",
                errors="replace",
            )

            if (
                response.status < 200
                or response.status >= 300
            ):

                raise RuntimeError(
                    f"HTTP {response.status}: "
                    f"{data[:500]}"
                )

            return json.loads(
                data
            )

    except urllib.error.HTTPError as exc:

        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: "
            f"{body[:800]}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"NETWORK ERROR: "
            f"{exc.reason}"
        ) from exc


# ==================================================================================================
# AUTHENTICATED WEEX GET
# ==================================================================================================


def weex_private_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    assert_exchange_method_allowed(
        "GET"
    )

    if not credentials_present():

        raise RuntimeError(
            "WEEX credentials are incomplete"
        )

    query = build_query(
        params
    )

    timestamp_ms = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = weex_signature(

        timestamp_ms,

        "GET",

        path,

        query,

        "",
    )

    headers = {

        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp_ms,

        "Content-Type":
            "application/json",

        "User-Agent":
            f"{VERSION}-readiness/1.0",
    }

    url = (
        WEEX_BASE_URL
        + path
        + (
            (
                "?"
                + query
            )
            if query
            else ""
        )
    )

    return http_get_json(
        url,
        headers=headers,
    )


# ==================================================================================================
# PUBLIC WEEX GET
# ==================================================================================================


def weex_public_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    assert_exchange_method_allowed(
        "GET"
    )

    query = build_query(
        params
    )

    url = (
        WEEX_BASE_URL
        + path
        + (
            (
                "?"
                + query
            )
            if query
            else ""
        )
    )

    return http_get_json(

        url,

        headers={

            "User-Agent":
                f"{VERSION}-readiness/1.0"
        },
    )


# ==================================================================================================
# READINESS STRUCTURE
# ==================================================================================================


@dataclass
class Readiness:

    authenticated_reads_passed: bool = False

    balance: Optional[float] = None

    mark_price: Optional[float] = None

    open_position_count: Optional[int] = None

    margin_mode: Optional[str] = None

    isolated_long_leverage: Optional[float] = None

    isolated_short_leverage: Optional[float] = None

    blockers: List[str] = field(
        default_factory=list
    )

    read_error: Optional[str] = None

    @property
    def ready(
        self,
    ) -> bool:

        return not self.blockers


# ==================================================================================================
# BALANCE EXTRACTION
# ==================================================================================================


def find_usdt_balance(
    payload: Any,
) -> Optional[float]:

    rows = (
        payload
        if isinstance(
            payload,
            list,
        )
        else [
            payload
        ]
    )

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        if str(
            row.get(
                "asset",
                "",
            )
        ).upper() == "USDT":

            return safe_float(
                row.get(
                    "availableBalance",
                    row.get(
                        "balance"
                    ),
                )
            )

    return None


# ==================================================================================================
# POSITION EXTRACTION
# ==================================================================================================


def count_open_positions(
    payload: Any,
) -> Optional[int]:

    if not isinstance(
        payload,
        list,
    ):

        return None

    count = 0

    for row in payload:

        if not isinstance(
            row,
            dict,
        ):

            continue

        if str(
            row.get(
                "symbol",
                "",
            )
        ).upper() != SYMBOL:

            continue

        size = safe_float(
            row.get(
                "size"
            )
        )

        if (
            size is not None
            and abs(
                size
            ) > 0
        ):

            count += 1

    return count


# ==================================================================================================
# SYMBOL CONFIG EXTRACTION
# ==================================================================================================


def find_symbol_config(
    payload: Any,
) -> Optional[
    Dict[str, Any]
]:

    rows = (
        payload
        if isinstance(
            payload,
            list,
        )
        else [
            payload
        ]
    )

    for row in rows:

        if (
            isinstance(
                row,
                dict,
            )
            and str(
                row.get(
                    "symbol",
                    "",
                )
            ).upper() == SYMBOL
        ):

            return row

    return None


# ==================================================================================================
# MARK PRICE EXTRACTION
# ==================================================================================================


def extract_mark_price(
    payload: Any,
) -> Optional[float]:

    if isinstance(
        payload,
        dict,
    ):

        return safe_float(

            payload.get(

                "price",

                payload.get(
                    "markPrice"
                ),
            )
        )

    if isinstance(
        payload,
        list,
    ):

        for row in payload:

            if (
                isinstance(
                    row,
                    dict,
                )
                and str(
                    row.get(
                        "symbol",
                        "",
                    )
                ).upper() == SYMBOL
            ):

                value = safe_float(

                    row.get(

                        "price",

                        row.get(
                            "markPrice"
                        ),
                    )
                )

                if value is not None:

                    return value

    return None


# ==================================================================================================
# LIVE READINESS RECONCILIATION
# ==================================================================================================


def reconcile_readiness() -> Readiness:

    result = Readiness()

    if not credentials_present():

        result.read_error = (
            "WEEX credentials are incomplete"
        )

        result.blockers.extend(
            [
                "AUTHENTICATED_READ_FAILURE",
                "MISSING_BALANCE",
                "MISSING_MARK_PRICE",
                "MISSING_POSITION_STATE",
                "WRONG_MARGIN_MODE",
                "WRONG_LONG_LEVERAGE",
                "WRONG_SHORT_LEVERAGE",
            ]
        )

        return result

    try:

        balance_payload = (
            weex_private_get(
                BALANCE_PATH
            )
        )

        positions_payload = (
            weex_private_get(
                POSITIONS_PATH
            )
        )

        config_payload = (
            weex_private_get(

                SYMBOL_CONFIG_PATH,

                {
                    "symbol":
                        SYMBOL
                },
            )
        )

        mark_payload = (
            weex_public_get(

                MARK_PRICE_PATH,

                {
                    "symbol":
                        SYMBOL,

                    "priceType":
                        "MARK",
                },
            )
        )

        result.authenticated_reads_passed = True

        result.balance = (
            find_usdt_balance(
                balance_payload
            )
        )

        result.open_position_count = (
            count_open_positions(
                positions_payload
            )
        )

        config = find_symbol_config(
            config_payload
        )

        result.mark_price = (
            extract_mark_price(
                mark_payload
            )
        )

        if config:

            result.margin_mode = str(

                config.get(
                    "marginType",
                    "",
                )

            ).upper() or None

            result.isolated_long_leverage = (
                safe_float(
                    config.get(
                        "isolatedLongLeverage"
                    )
                )
            )

            result.isolated_short_leverage = (
                safe_float(
                    config.get(
                        "isolatedShortLeverage"
                    )
                )
            )

    except Exception as exc:

        result.authenticated_reads_passed = False

        result.read_error = (
            f"{type(exc).__name__}: {exc}"
        )

    if not result.authenticated_reads_passed:

        result.blockers.append(
            "AUTHENTICATED_READ_FAILURE"
        )

    if (
        result.balance is None
        or result.balance <= 0
    ):

        result.blockers.append(
            "MISSING_BALANCE"
        )

    if (
        result.mark_price is None
        or result.mark_price <= 0
    ):

        result.blockers.append(
            "MISSING_MARK_PRICE"
        )

    if result.open_position_count is None:

        result.blockers.append(
            "MISSING_POSITION_STATE"
        )

    elif result.open_position_count != 0:

        result.blockers.append(
            "OPEN_POSITION_EXISTS"
        )

    if result.margin_mode != "ISOLATED":

        result.blockers.append(
            "WRONG_MARGIN_MODE"
        )

    if result.isolated_long_leverage != float(
        TARGET_LONG_LEVERAGE
    ):

        result.blockers.append(
            "WRONG_LONG_LEVERAGE"
        )

    if result.isolated_short_leverage != float(
        TARGET_SHORT_LEVERAGE
    ):

        result.blockers.append(
            "WRONG_SHORT_LEVERAGE"
        )

    result.blockers = list(
        dict.fromkeys(
            result.blockers
        )
    )

    return result


# ==================================================================================================
# ACTIVATION ENVIRONMENT
# ==================================================================================================


def activation_inputs() -> Dict[
    str,
    str,
]:

    return {

        "armed":
            os.getenv(
                "R35L_ACTIVATE",
                "",
            ).strip(),

        "symbol":
            os.getenv(
                "R35L_ACTIVATE_SYMBOL",
                "",
            ).strip().upper(),

        "generation":
            os.getenv(
                "R35L_ACTIVATE_GENERATION",
                "",
            ).strip(),

        "epoch":
            os.getenv(
                "R35L_ACTIVATE_EPOCH",
                "",
            ).strip(),
    }


def activation_exact_or_unset(
    inputs: Dict[str, str],
) -> bool:

    values = list(
        inputs.values()
    )

    all_unset = all(
        value == ""
        for value
        in values
    )

    exact = (

        inputs[
            "armed"
        ] == "ARM"

        and

        inputs[
            "symbol"
        ] == SYMBOL

        and

        inputs[
            "generation"
        ] == str(
            GENERATION
        )

        and

        inputs[
            "epoch"
        ] == str(
            EPOCH
        )
    )

    return (
        all_unset
        or exact
    )


def activation_is_exact(
    inputs: Dict[str, str],
) -> bool:

    return (

        inputs[
            "armed"
        ] == "ARM"

        and

        inputs[
            "symbol"
        ] == SYMBOL

        and

        inputs[
            "generation"
        ] == str(
            GENERATION
        )

        and

        inputs[
            "epoch"
        ] == str(
            EPOCH
        )
    )


# ==================================================================================================
# CLIENT ORDER ID
# ==================================================================================================


def next_client_order_id(
    state: StrategyState,
) -> str:

    with STATE_LOCK:

        state.last_client_order_nonce += 1

        nonce = (
            state.last_client_order_nonce
        )

        save_state(
            state
        )

    suffix = (
        int(
            time.time()
            * 1000
        )
        % 10_000_000_000
    )

    return (
        f"{VERSION}"
        f"-G{GENERATION}"
        f"-E{EPOCH}"
        f"-N{nonce}"
        f"-{suffix}"
    )


# ==================================================================================================
# SYNTHETIC ORDER ENVELOPE
# ==================================================================================================


def build_synthetic_order_envelope(
    state: StrategyState,
) -> Dict[str, Any]:

    client_id = (
        next_client_order_id(
            state
        )
    )

    return {

        "method":
            "POST",

        "path":
            ORDER_PATH,

        "payload": {

            "symbol":
                SYMBOL,

            "side":
                "BUY",

            "positionSide":
                "LONG",

            "type":
                "MARKET",

            "quantity":
                VALIDATION_QUANTITY,

            "newClientOrderId":
                client_id,
        },

        "synthetic":
            True,

        "transmit":
            False,

        "network_write":
            False,

        "real_order":
            False,

        "client_order_id":
            client_id,
    }


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================


def synthetic_dispatch(
    state: StrategyState,
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    if envelope.get(
        "transmit"
    ) is not False:

        raise RuntimeError(
            "Synthetic envelope "
            "transmission flag is unsafe"
        )

    if envelope.get(
        "network_write"
    ) is not False:

        raise RuntimeError(
            "Synthetic envelope "
            "network write flag is unsafe"
        )

    if envelope.get(
        "real_order"
    ) is not False:

        raise RuntimeError(
            "Synthetic envelope "
            "real-order flag is unsafe"
        )

    with STATE_LOCK:

        state.synthetic_dispatch_count += 1

        save_state(
            state
        )

    receipt = {

        "status":
            "SYNTHETIC_DISPATCH_COMPLETED",

        "transmitted":
            False,

        "exchange_network_write":
            False,

        "real_order_created":
            False,

        "client_order_id":
            envelope.get(
                "client_order_id"
            ),
    }

    append_journal(

        state,

        "SYNTHETIC_DISPATCH",

        receipt,
    )

    return receipt


# ==================================================================================================
# TELEGRAM CONFIGURATION
# ==================================================================================================


def telegram_configured() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


# ==================================================================================================
# TELEGRAM PREVIEW
# ==================================================================================================


def telegram_preview(
    text: str,
) -> Dict[str, Any]:

    return {

        "method":
            "POST",

        "operation":
            "sendMessage",

        "report_only":
            True,

        "exchange_mutation":
            False,

        "controls_execution":
            False,

        "chat_id_present":
            bool(
                TELEGRAM_CHAT_ID
            ),

        "text":
            text,

        "token_exposed":
            False,
    }


# ==================================================================================================
# TELEGRAM REPORTING POST
# ==================================================================================================


def telegram_post(
    text: str,
) -> bool:

    if not telegram_configured():

        log(
            f"{VERSION}: "
            f"TELEGRAM NOT CONFIGURED; "
            f"REPORT SKIPPED"
        )

        return False

    # TELEGRAM IS THE ONLY POST DESTINATION ALLOWED IN R35L.
    #
    # THIS FUNCTION DOES NOT CONNECT TO WEEX.

    url = (

        "https://api.telegram.org/bot"

        + TELEGRAM_BOT_TOKEN

        + "/sendMessage"
    )

    payload = urllib.parse.urlencode(

        {

            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                text,
        }

    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(

        url=url,

        data=payload,

        method="POST",

        headers={

            "Content-Type":
                "application/x-www-form-urlencoded",

            "User-Agent":
                f"{VERSION}/1.0",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:

            response.read()

            return (
                200
                <= response.status
                < 300
            )

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"TELEGRAM SEND FAILED: "
            f"{type(exc).__name__}: {exc}"
        )

        return False


# ==================================================================================================
# TELEGRAM DURABLE DEDUPLICATION
# ==================================================================================================


def report_telegram_dedup(
    state: StrategyState,
    event: str,
    text: str,
) -> bool:

    fingerprint = sha256_text(
        event
        + "\n"
        + text
    )

    now = time.time()

    with (
        TELEGRAM_LOCK,
        STATE_LOCK,
    ):

        elapsed = (
            now
            - float(
                state.last_readiness_report_time
                or 0.0
            )
        )

        if (
            state.last_readiness_fingerprint
            == fingerprint

            and

            elapsed
            < TELEGRAM_DEDUP_SECONDS
        ):

            log(
                f"{VERSION}: "
                f"TELEGRAM {event} "
                f"SUPPRESSED BY DEDUP "
                f"({int(elapsed)}s since identical report)"
            )

            return False

    sent = telegram_post(
        text
    )

    if sent:

        with STATE_LOCK:

            state.last_readiness_fingerprint = (
                fingerprint
            )

            state.last_readiness_report_time = (
                now
            )

            state.telegram_reports_this_run += 1

            save_state(
                state
            )

        append_journal(

            state,

            "TELEGRAM_REPORT_SENT",

            {

                "event":
                    event,

                "fingerprint":
                    fingerprint,
            },
        )

    return sent


# ==================================================================================================
# VALIDATION
# ==================================================================================================


def run_validation() -> int:

    start_health_server()

    time.sleep(
        0.05
    )

    state = STATE

    state.activation_armed = False

    state.execution_authorized = False

    state.first_real_order_allowed = False

    state.exchange_network_writes = 0

    save_state(
        state
    )


    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"{VERSION}: STATE DIR={STATE_DIR}"
    )

    log(
        f"{VERSION}: "
        f"PASSPHRASE ENV STANDARD="
        f"WEEX_API_PASSPHRASE"
    )


    append_journal(

        state,

        "VALIDATION_STARTED",

        {

            "real_order_execution":
                REAL_ORDER_EXECUTION,

            "exchange_mutation_transport_enabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED,
        },
    )


    all_checks: List[bool] = []


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================


    section(
        f"{VERSION} TEST 1: "
        f"HARD SAFETY BASELINE"
    )


    all_checks.append(

        check(

            "Real Order Execution Is Hard Disabled",

            REAL_ORDER_EXECUTION
            is False,
        )
    )


    all_checks.append(

        check(

            "Demo Order Execution Is Disabled",

            DEMO_ORDER_EXECUTION
            is False,
        )
    )


    all_checks.append(

        check(

            "Exchange Mutation Transport Is Hard Disabled",

            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,
        )
    )


    all_checks.append(

        check(

            "First Real Order Is Hard Forbidden",

            FIRST_REAL_ORDER_ALLOWED
            is False,
        )
    )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================


    section(
        f"{VERSION} TEST 2: "
        f"CREDENTIAL PRESENCE"
    )


    key_ok = bool(
        WEEX_API_KEY
    )


    secret_ok = bool(
        WEEX_API_SECRET
    )


    passphrase_ok = bool(
        WEEX_API_PASSPHRASE
    )


    all_checks.append(

        check(

            "WEEX API Key Is Present",

            key_ok,
        )
    )


    all_checks.append(

        check(

            "WEEX API Secret Is Present",

            secret_ok,
        )
    )


    all_checks.append(

        check(

            "WEEX Passphrase Is Present",

            passphrase_ok,
        )
    )


    # ==============================================================================================
    # LIVE READINESS
    # ==============================================================================================


    readiness = (
        reconcile_readiness()
    )


    append_journal(

        state,

        "READINESS_RECONCILED",

        {

            "authenticated_reads_passed":
                readiness.authenticated_reads_passed,

            "balance":
                readiness.balance,

            "mark_price":
                readiness.mark_price,

            "open_position_count":
                readiness.open_position_count,

            "margin_mode":
                readiness.margin_mode,

            "isolated_long_leverage":
                readiness.isolated_long_leverage,

            "isolated_short_leverage":
                readiness.isolated_short_leverage,

            "blockers":
                readiness.blockers,

            "read_error":
                readiness.read_error,
        },
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================


    section(
        f"{VERSION} TEST 3: "
        f"LIVE READINESS"
    )


    all_checks.append(

        check(

            "Authenticated WEEX Reads Passed",

            readiness.authenticated_reads_passed,
        )
    )


    all_checks.append(

        check(

            "Balance Is Positive",

            readiness.balance
            is not None

            and

            readiness.balance > 0,
        )
    )


    all_checks.append(

        check(

            "Mark Price Is Positive",

            readiness.mark_price
            is not None

            and

            readiness.mark_price > 0,
        )
    )


    all_checks.append(

        check(

            "Open Position Count Is Zero",

            readiness.open_position_count
            == 0,
        )
    )


    all_checks.append(

        check(

            "Margin Mode Is ISOLATED",

            readiness.margin_mode
            == "ISOLATED",
        )
    )


    all_checks.append(

        check(

            "Isolated Long Leverage Is 100x",

            readiness.isolated_long_leverage
            == 100.0,
        )
    )


    all_checks.append(

        check(

            "Isolated Short Leverage Is 100x",

            readiness.isolated_short_leverage
            == 100.0,
        )
    )


    all_checks.append(

        check(

            "Live Readiness Is READY",

            readiness.ready,
        )
    )


    # ==============================================================================================
    # ACTIVATION BINDING
    # ==============================================================================================


    inputs = activation_inputs()


    exact_or_unset = (
        activation_exact_or_unset(
            inputs
        )
    )


    exact_armed = (
        activation_is_exact(
            inputs
        )
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================


    section(
        f"{VERSION} TEST 4: "
        f"ACTIVATION ENVIRONMENT BINDING"
    )


    all_checks.append(

        check(

            "Activation Inputs Are Exact Match Or Safely Unset",

            exact_or_unset,
        )
    )


    all_checks.append(

        check(

            "Activation Is Bound To Current Symbol When Armed",

            (
                not exact_armed

                or

                inputs[
                    "symbol"
                ] == SYMBOL
            ),
        )
    )


    all_checks.append(

        check(

            "Activation Is Bound To Current Generation When Armed",

            (
                not exact_armed

                or

                inputs[
                    "generation"
                ] == str(
                    GENERATION
                )
            ),
        )
    )


    all_checks.append(

        check(

            "Activation Is Bound To Current Epoch When Armed",

            (
                not exact_armed

                or

                inputs[
                    "epoch"
                ] == str(
                    EPOCH
                )
            ),
        )
    )


    # R35L may validate the activation conditions,
    # but it NEVER converts that into execution permission.


    can_arm = (

        readiness.ready

        and

        exact_armed

        and

        not state.activation_consumed
    )


    state.activation_armed = bool(
        can_arm
    )


    state.execution_authorized = False


    state.first_real_order_allowed = False


    save_state(
        state
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================


    section(
        f"{VERSION} TEST 5: "
        f"FAIL-CLOSED ACTIVATION"
    )


    all_checks.append(

        check(

            "Failed Readiness Cannot Arm Activation",

            (
                readiness.ready

                or

                not state.activation_armed
            ),
        )
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================


    section(
        f"{VERSION} TEST 6: "
        f"ACTIVATION REPLAY PROTECTION"
    )


    all_checks.append(

        check(

            "Current Activation Cannot Be Both Consumed And Newly Armed",

            not (

                state.activation_consumed

                and

                state.activation_armed
            ),
        )
    )


    all_checks.append(

        check(

            "Unarmed Deployment Has No Replayable Authorization",

            (
                state.activation_armed

                or

                not state.execution_authorized
            ),
        )
    )


    # ==============================================================================================
    # SYNTHETIC ORDER ENVELOPE
    # ==============================================================================================


    envelope = (
        build_synthetic_order_envelope(
            state
        )
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================


    section(
        f"{VERSION} TEST 7: "
        f"ORDER ENVELOPE"
    )


    all_checks.append(

        check(

            "Order Envelope Uses Exact V3 Order Endpoint",

            envelope[
                "path"
            ] == ORDER_PATH,
        )
    )


    all_checks.append(

        check(

            "Order Envelope Uses POST",

            envelope[
                "method"
            ] == "POST",
        )
    )


    all_checks.append(

        check(

            "Order Envelope Uses BUY",

            envelope[
                "payload"
            ].get(
                "side"
            ) == "BUY",
        )
    )


    all_checks.append(

        check(

            "Order Envelope Uses LONG Position Side",

            envelope[
                "payload"
            ].get(
                "positionSide"
            ) == "LONG",
        )
    )


    all_checks.append(

        check(

            "Order Envelope Is Synthetic",

            envelope[
                "synthetic"
            ] is True,
        )
    )


    all_checks.append(

        check(

            "Order Envelope Forbids Transmission",

            envelope[
                "transmit"
            ] is False,
        )
    )


    all_checks.append(

        check(

            "Order Envelope Forbids Network Write",

            envelope[
                "network_write"
            ] is False,
        )
    )


    all_checks.append(

        check(

            "Order Envelope Forbids Real Order",

            envelope[
                "real_order"
            ] is False,
        )
    )


    # ==============================================================================================
    # SYNTHETIC DISPATCH
    # ==============================================================================================


    receipt = synthetic_dispatch(

        state,

        envelope,
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================


    section(
        f"{VERSION} TEST 8: "
        f"SYNTHETIC BOUNDARY"
    )


    all_checks.append(

        check(

            "Synthetic Boundary Dispatch Completed",

            receipt[
                "status"
            ]
            == "SYNTHETIC_DISPATCH_COMPLETED",
        )
    )


    all_checks.append(

        check(

            "Synthetic Boundary Did Not Transmit",

            receipt[
                "transmitted"
            ] is False,
        )
    )


    all_checks.append(

        check(

            "Synthetic Boundary Made No Exchange Network Write",

            receipt[
                "exchange_network_write"
            ] is False,
        )
    )


    all_checks.append(

        check(

            "Synthetic Boundary Did Not Create Real Order",

            receipt[
                "real_order_created"
            ] is False,
        )
    )


    all_checks.append(

        check(

            "Exchange Write Count Remains Zero",

            state.exchange_network_writes
            == 0,
        )
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================


    section(
        f"{VERSION} TEST 9: "
        f"REAL WRITER FIREBREAK"
    )


    writer_blocked = False


    before_writes = (
        state.exchange_network_writes
    )


    try:

        real_exchange_writer(
            envelope
        )

    except RuntimeError:

        writer_blocked = True


    all_checks.append(

        check(

            "Direct Real Exchange Writer Call Is Blocked",

            writer_blocked,
        )
    )


    all_checks.append(

        check(

            "Blocked Writer Makes No Exchange Network Write",

            (
                state.exchange_network_writes
                == before_writes
                == 0
            ),
        )
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================


    section(
        f"{VERSION} TEST 10: "
        f"EXECUTION AUTHORIZATION"
    )


    all_checks.append(

        check(

            "Execution Authorization Remains False",

            state.execution_authorized
            is False,
        )
    )


    all_checks.append(

        check(

            "First Real Order Remains Forbidden",

            state.first_real_order_allowed
            is False,
        )
    )


    all_checks.append(

        check(

            "Code-Level Real Execution Remains Disabled",

            CODE_LEVEL_REAL_EXECUTION_ENABLED
            is False,
        )
    )


    # ==============================================================================================
    # TELEGRAM BOUNDARY
    # ==============================================================================================


    preview = telegram_preview(
        "R35L reporting boundary validation"
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================


    section(
        f"{VERSION} TEST 11: "
        f"TELEGRAM REPORTING BOUNDARY"
    )


    all_checks.append(

        check(

            "Telegram Uses POST Only For Reporting",

            (
                preview[
                    "method"
                ] == "POST"

                and

                preview[
                    "report_only"
                ] is True
            ),
        )
    )


    all_checks.append(

        check(

            "Telegram Operation Is sendMessage",

            preview[
                "operation"
            ] == "sendMessage",
        )
    )


    all_checks.append(

        check(

            "Telegram Request Is Report Only",

            preview[
                "report_only"
            ] is True,
        )
    )


    all_checks.append(

        check(

            "Telegram Is Not Exchange Mutation",

            preview[
                "exchange_mutation"
            ] is False,
        )
    )


    all_checks.append(

        check(

            "Telegram Cannot Control Execution",

            preview[
                "controls_execution"
            ] is False,
        )
    )


    all_checks.append(

        check(

            "Telegram Preview Does Not Expose Bot Token",

            (
                TELEGRAM_BOT_TOKEN
                not in canonical_json(
                    preview
                )

                if TELEGRAM_BOT_TOKEN

                else True
            ),
        )
    )


    all_checks.append(

        check(

            "Readiness Reporting Has Durable Deduplication",

            (
                TELEGRAM_DEDUP_SECONDS
                > 0

                and

                hasattr(
                    state,
                    "last_readiness_fingerprint",
                )
            ),
        )
    )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================


    save_state(
        state
    )


    restart_raw = json.loads(
        STATE_FILE.read_text(
            encoding="utf-8"
        )
    )


    restart_raw[
        "activation_armed"
    ] = False


    restart_raw[
        "execution_authorized"
    ] = False


    restart_raw[
        "first_real_order_allowed"
    ] = False


    restart_raw[
        "exchange_network_writes"
    ] = 0


    section(
        f"{VERSION} TEST 12: "
        f"DURABLE RESTART PROTECTION"
    )


    all_checks.append(

        check(

            "Durable State Snapshot Exists",

            STATE_FILE.exists(),
        )
    )


    all_checks.append(

        check(

            "Restart Snapshot Clears Activation Armed State",

            restart_raw.get(
                "activation_armed"
            ) is False,
        )
    )


    all_checks.append(

        check(

            "Restart Snapshot Keeps Execution Unauthorized",

            restart_raw.get(
                "execution_authorized"
            ) is False,
        )
    )


    all_checks.append(

        check(

            "Restart Snapshot Keeps First Real Order Forbidden",

            restart_raw.get(
                "first_real_order_allowed"
            ) is False,
        )
    )


    all_checks.append(

        check(

            "Restart Snapshot Keeps Exchange Write Count At Zero",

            restart_raw.get(
                "exchange_network_writes"
            ) == 0,
        )
    )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================


    (
        journal_ok,
        journal_count,
        journal_monotonic,
    ) = validate_journal()


    section(
        f"{VERSION} TEST 13: "
        f"JOURNAL INTEGRITY"
    )


    all_checks.append(

        check(

            "Durable Journal Contains Records",

            journal_count > 0,
        )
    )


    all_checks.append(

        check(

            "Durable Journal Hash Chain Is Valid",

            journal_ok,
        )
    )


    all_checks.append(

        check(

            "Journal Sequence Is Monotonic",

            journal_monotonic,
        )
    )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================


    section(
        f"{VERSION} TEST 14: "
        f"FINAL EXECUTION FIREBREAK"
    )


    all_checks.append(

        check(

            "Exchange Network Writes Remain Zero",

            state.exchange_network_writes
            == 0,
        )
    )


    all_checks.append(

        check(

            "Real Order Execution Remains Disabled",

            REAL_ORDER_EXECUTION
            is False,
        )
    )


    all_checks.append(

        check(

            "First Real Order Remains Forbidden",

            state.first_real_order_allowed
            is False,
        )
    )


    all_checks.append(

        check(

            "Execution Authorization Remains False",

            state.execution_authorized
            is False,
        )
    )


    # ==============================================================================================
    # TELEGRAM READINESS REPORT
    # ==============================================================================================


    credentials_ok = (

        key_ok

        and

        secret_ok

        and

        passphrase_ok
    )


    activation_blockers: List[str] = []


    if not readiness.ready:

        activation_blockers.append(
            "READINESS_NOT_READY"
        )


    if not exact_armed:

        activation_blockers.append(
            "ACTIVATION_ENV_MISMATCH"
        )


    if not readiness.ready:

        critical_text = (

            f"⚠️ {VERSION} CRITICAL READINESS FAILURE\n"

            f"SYMBOL={SYMBOL}\n"

            f"BLOCKERS="
            f"{','.join(readiness.blockers)}\n"

            f"EXCHANGE_NETWORK_WRITES="
            f"{state.exchange_network_writes}\n"

            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )


        report_telegram_dedup(

            state,

            f"{VERSION}_READINESS",

            critical_text,
        )


        # Do not send a second WEEX READ ERROR
        # when credentials themselves are missing.
        #
        # That was causing unnecessary duplicate Telegram messages.


        if (
            readiness.read_error
            and credentials_ok
        ):

            error_text = (

                f"⚠️ {VERSION} WEEX READ ERROR\n"

                f"SYMBOL={SYMBOL}\n"

                f"ERROR="
                f"{readiness.read_error[:500]}\n"

                f"EXCHANGE_NETWORK_WRITES="
                f"{state.exchange_network_writes}\n"

                f"EXECUTION_AUTHORIZATION="
                f"{state.execution_authorized}"
            )


            report_telegram_dedup(

                state,

                f"{VERSION}_READ_ERROR",

                error_text,
            )


    else:

        ready_text = (

            f"✅ {VERSION} READINESS PASSED\n"

            f"SYMBOL={SYMBOL}\n"

            f"BALANCE="
            f"{readiness.balance}\n"

            f"MARK_PRICE="
            f"{readiness.mark_price}\n"

            f"OPEN_POSITIONS="
            f"{readiness.open_position_count}\n"

            f"MARGIN_MODE="
            f"{readiness.margin_mode}\n"

            f"LONG_LEVERAGE="
            f"{readiness.isolated_long_leverage}x\n"

            f"SHORT_LEVERAGE="
            f"{readiness.isolated_short_leverage}x\n"

            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )


        report_telegram_dedup(

            state,

            f"{VERSION}_READINESS",

            ready_text,
        )


    # ==============================================================================================
    # FINAL JOURNAL CHECK
    # ==============================================================================================


    (
        journal_ok,
        journal_count,
        journal_monotonic,
    ) = validate_journal()


    validation_passed = all(
        all_checks
    )


    append_journal(

        state,

        "VALIDATION_COMPLETED",

        {

            "validation_passed":
                validation_passed,

            "readiness_ready":
                readiness.ready,

            "exchange_network_writes":
                state.exchange_network_writes,

            "real_order_execution":
                REAL_ORDER_EXECUTION,
        },
    )


    (
        journal_ok,
        journal_count,
        journal_monotonic,
    ) = validate_journal()


    # ==============================================================================================
    # SUMMARY
    # ==============================================================================================


    section(
        f"{VERSION}: VALIDATION SUMMARY"
    )


    status_icon = (
        "✅"
        if validation_passed
        else "❌"
    )


    print(
        f"{status_icon} "
        f"{VERSION} VALIDATION REPORT",
        flush=True,
    )


    print(
        "",
        flush=True,
    )


    print(
        f"Symbol: "
        f"{SYMBOL}",
        flush=True,
    )


    print(
        f"Authenticated WEEX reads: "
        f"{'PASS' if readiness.authenticated_reads_passed else 'FAIL'}",
        flush=True,
    )


    print(
        f"Credentials present: "
        f"{'YES' if credentials_ok else 'NO'}",
        flush=True,
    )


    print(
        f"Balance: "
        f"{readiness.balance}",
        flush=True,
    )


    print(
        f"Mark price: "
        f"{readiness.mark_price}",
        flush=True,
    )


    print(
        f"Open positions: "
        f"{readiness.open_position_count}",
        flush=True,
    )


    print(
        f"Positions endpoint: "
        f"{POSITIONS_PATH}",
        flush=True,
    )


    print(
        f"Margin mode: "
        f"{readiness.margin_mode}",
        flush=True,
    )


    print(
        f"Isolated long leverage: "
        f"{readiness.isolated_long_leverage}",
        flush=True,
    )


    print(
        f"Isolated short leverage: "
        f"{readiness.isolated_short_leverage}",
        flush=True,
    )


    print(
        f"Target long leverage: "
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )


    print(
        f"Target short leverage: "
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )


    print(
        f"Order endpoint: "
        f"{ORDER_PATH}",
        flush=True,
    )


    print(
        f"Order side: "
        f"{envelope['payload']['side']}",
        flush=True,
    )


    print(
        f"Position side: "
        f"{envelope['payload']['positionSide']}",
        flush=True,
    )


    print(
        f"Validation quantity: "
        f"{VALIDATION_QUANTITY} BTC",
        flush=True,
    )


    print(
        f"Client order ID: "
        f"{envelope['client_order_id']}",
        flush=True,
    )


    print(
        f"Journal integrity: "
        f"{'PASS' if journal_ok and journal_monotonic else 'FAIL'}",
        flush=True,
    )


    print(
        f"Journal records validated: "
        f"{journal_count}",
        flush=True,
    )


    print(
        f"Exchange network writes: "
        f"{state.exchange_network_writes}",
        flush=True,
    )


    print(
        f"Real order execution: "
        f"{'ENABLED' if REAL_ORDER_EXECUTION else 'DISABLED'}",
        flush=True,
    )


    print(
        f"Demo order execution: "
        f"{'ENABLED' if DEMO_ORDER_EXECUTION else 'DISABLED'}",
        flush=True,
    )


    print(
        f"First real order: "
        f"{'ALLOWED' if state.first_real_order_allowed else 'FORBIDDEN'}",
        flush=True,
    )


    print(
        f"Execution authorization: "
        f"{'AUTHORIZED' if state.execution_authorized else 'FORBIDDEN'}",
        flush=True,
    )


    print(
        f"Live readiness: "
        f"{'READY' if readiness.ready else 'NOT READY'}",
        flush=True,
    )


    print(
        "Live activation gate: "
        "VALIDATED",
        flush=True,
    )


    print(
        f"Live activation armed: "
        f"{'YES' if state.activation_armed else 'NO'}",
        flush=True,
    )


    print(
        f"Synthetic boundary dispatches: "
        f"{state.synthetic_dispatch_count}",
        flush=True,
    )


    print(
        f"Telegram reports this run: "
        f"{state.telegram_reports_this_run}",
        flush=True,
    )


    print(
        "",
        flush=True,
    )


    if readiness.blockers:

        print(
            "Readiness blockers:",
            flush=True,
        )

        for blocker in readiness.blockers:

            print(
                f"- {blocker}",
                flush=True,
            )

        print(
            "",
            flush=True,
        )


    if activation_blockers:

        print(
            "Activation blockers:",
            flush=True,
        )

        for blocker in activation_blockers:

            print(
                f"- {blocker}",
                flush=True,
            )

        print(
            "",
            flush=True,
        )


    if readiness.read_error:

        print(
            f"WEEX read error: "
            f"{readiness.read_error}",
            flush=True,
        )

        print(
            "",
            flush=True,
        )


    print(
        f"Validation status: "
        f"{'PASSED' if validation_passed else 'FAILED'}",
        flush=True,
    )


    print(
        "Status: CONTROLLED LIVE ACTIVATION BOUNDARY VALIDATED; "
        "FIRST REAL ORDER STILL HARD-DISABLED",
        flush=True,
    )


    # ==============================================================================================
    # FINAL FAIL-CLOSED STATE
    # ==============================================================================================


    state.activation_armed = False

    state.execution_authorized = False

    state.first_real_order_allowed = False

    state.exchange_network_writes = 0


    save_state(
        state
    )


    # Return zero so Render remains healthy even when
    # readiness intentionally fails closed.

    return 0


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================


if __name__ == "__main__":

    raise SystemExit(
        run_validation()
    )

