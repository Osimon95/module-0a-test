#!/usr/bin/env python3
# R34R - WEEX BTCUSDT execution-readiness validator
# IMPORTANT:
# SYNTHETIC / READ-ONLY ONLY.
# NO real order transmission.
# NO demo order transmission.
# NO leverage, margin, position, or account mutation.

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import signal
import sys
import threading
import time
import urllib.parse
import urllib.request

from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, Tuple


# =============================================================================
# R34R CONFIGURATION
# =============================================================================

VERSION = "R34R"
SYMBOL = "BTCUSDT"

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv("HEALTH_PORT", "10000"),
    )
)


# =============================================================================
# HARD SAFETY FIREBREAKS
# =============================================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

SYNTHETIC_TRANSPORT_ONLY = True

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES = False

LEVERAGE_MUTATION = False
MARGIN_MUTATION = False
POSITION_MUTATION = False
ACCOUNT_MUTATION = False


# =============================================================================
# STRATEGY CONSTANTS
# =============================================================================

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
PYRAMID_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
PRICE_STEP = Decimal("0.1")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# =============================================================================
# FALLBACK VALUES
# =============================================================================

FALLBACK_AVAILABLE_USDT = Decimal(
    os.getenv(
        "R34R_FALLBACK_AVAILABLE_USDT",
        "7.18945017",
    )
)

FALLBACK_MARK_PRICE = Decimal(
    os.getenv(
        "R34R_FALLBACK_MARK_PRICE",
        "79950.1",
    )
)

FALLBACK_MARGIN_TYPE = os.getenv(
    "R34R_FALLBACK_MARGIN_TYPE",
    "ISOLATED",
).upper()

FALLBACK_LONG_LEVERAGE = Decimal(
    os.getenv(
        "R34R_FALLBACK_LONG_LEVERAGE",
        "100",
    )
)

FALLBACK_SHORT_LEVERAGE = Decimal(
    os.getenv(
        "R34R_FALLBACK_SHORT_LEVERAGE",
        "100",
    )
)

FALLBACK_OPEN_POSITIONS = int(
    os.getenv(
        "R34R_FALLBACK_OPEN_POSITIONS",
        "0",
    )
)


# =============================================================================
# LIVE READ CONFIGURATION
# =============================================================================

LIVE_READS_ENABLED = (
    os.getenv(
        "R34R_LIVE_READS",
        "1",
    )
    .strip()
    .lower()
    not in {
        "0",
        "false",
        "no",
        "off",
    }
)

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

BALANCE_PATH = os.getenv(
    "WEEX_BALANCE_PATH",
    "/capi/v3/account/balance",
)

POSITIONS_PATH = os.getenv(
    "WEEX_POSITIONS_PATH",
    "/capi/v3/account/position/allPosition",
)

MARK_PRICE_PATH = os.getenv(
    "WEEX_MARK_PRICE_PATH",
    "/capi/v2/market/ticker",
)


SEP = "-" * 100


# =============================================================================
# COUNTERS
# =============================================================================

@dataclass
class Counters:
    authenticated_gets: int = 0
    public_gets: int = 0

    network_writes: int = 0

    leverage_mutations: int = 0
    margin_mutations: int = 0
    position_mutations: int = 0
    account_mutations: int = 0

    real_orders: int = 0
    demo_orders: int = 0

    synthetic_dispatches: int = 0

    duplicate_dispatch_blocks: int = 0
    stale_state_blocks: int = 0


COUNTERS = Counters()

COUNTER_LOCK = threading.Lock()


# =============================================================================
# BASIC UTILITIES
# =============================================================================

def log(message: str = "") -> None:
    print(
        message,
        flush=True,
    )


def heading(title: str) -> None:
    log(SEP)
    log(title)
    log(SEP)


def result(
    label: str,
    ok: bool,
) -> None:

    status = (
        "✅ PASS"
        if ok
        else "❌ FAIL"
    )

    log(
        f"{label:<88} {status}"
    )

    if not ok:
        raise AssertionError(label)


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def sha256_obj(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(value)
    )


def now_ms() -> int:
    return int(
        time.time() * 1000
    )


def dec(
    value: Any,
    default: Optional[Decimal] = None,
) -> Decimal:

    try:

        if value is None:
            raise InvalidOperation

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        if default is not None:
            return default

        raise


def floor_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    if step <= 0:
        raise ValueError(
            "step must be positive"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def fmt_decimal(
    value: Decimal,
) -> str:

    return format(
        value,
        "f",
    )


def deep_copy_json(
    value: Any,
) -> Any:

    return json.loads(
        canonical_json(value)
    )


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self) -> None:

        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):

            self.send_response(404)
            self.end_headers()

            return

        payload = {

            "ok": True,

            "version": VERSION,

            "symbol": SYMBOL,

            "phase":
                "SYNTHETIC_EXECUTION_VALIDATED",

            "synthetic_transport_only":
                SYNTHETIC_TRANSPORT_ONLY,

            "network_writes":
                COUNTERS.network_writes,

            "real_orders":
                COUNTERS.real_orders,

            "demo_orders":
                COUNTERS.demo_orders,

            "synthetic_dispatches":
                COUNTERS.synthetic_dispatches,
        }

        body = canonical_json(
            payload
        ).encode(
            "utf-8"
        )

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

        self.wfile.write(
            body
        )

    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> Optional[
    ThreadingHTTPServer
]:

    try:

        server = ThreadingHTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            name="health-server",
            daemon=True,
        )

        thread.start()

        return server

    except OSError as exc:

        log(
            f"{VERSION}: "
            f"HEALTH SERVER WARNING="
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return None


# =============================================================================
# CREDENTIALS
# =============================================================================

def credentials() -> Tuple[
    str,
    str,
    str,
]:

    key = os.getenv(
        "WEEX_API_KEY",
        "",
    ).strip()

    secret = os.getenv(
        "WEEX_API_SECRET",
        "",
    ).strip()

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE",
        "",
    ).strip()

    return (
        key,
        secret,
        passphrase,
    )


# =============================================================================
# AUTHENTICATED READ-ONLY SIGNING
# =============================================================================

def build_auth_headers(
    method: str,
    path_with_query: str,
    body: str = "",
) -> Dict[str, str]:

    key, secret, passphrase = credentials()

    if not (
        key
        and secret
        and passphrase
    ):

        raise RuntimeError(
            "Missing WEEX API credentials "
            "for authenticated read-only GET"
        )

    timestamp = str(
        now_ms()
    )

    prehash = (
        f"{timestamp}"
        f"{method.upper()}"
        f"{path_with_query}"
        f"{body}"
    )

    signature = base64.b64encode(

        hmac.new(
            secret.encode(
                "utf-8"
            ),
            prehash.encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).digest()

    ).decode(
        "ascii"
    )

    return {

        "ACCESS-KEY":
            key,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            passphrase,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",

        "Accept":
            "application/json",

        "User-Agent":
            f"{VERSION}-read-only-validator",
    }


# =============================================================================
# READ-ONLY HTTP
# =============================================================================

def safe_http_get(
    url: str,
    headers: Optional[
        Dict[str, str]
    ] = None,
    timeout: float = 8.0,
) -> Any:

    request = urllib.request.Request(
        url=url,
        headers=headers or {},
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        raw = response.read().decode(
            "utf-8",
            errors="replace",
        )

        if not raw:
            return None

        return json.loads(
            raw
        )


def authenticated_get(
    path: str,
    query: Optional[
        Dict[str, str]
    ] = None,
) -> Any:

    if not AUTHENTICATED_READ_ONLY:

        raise RuntimeError(
            "Authenticated reads disabled"
        )

    query_string = urllib.parse.urlencode(
        query or {}
    )

    path_with_query = (
        path
        +
        (
            f"?{query_string}"
            if query_string
            else ""
        )
    )

    url = (
        BASE_URL
        + path_with_query
    )

    headers = build_auth_headers(
        "GET",
        path_with_query,
        "",
    )

    data = safe_http_get(
        url,
        headers=headers,
    )

    with COUNTER_LOCK:

        COUNTERS.authenticated_gets += 1

    return data


def public_get(
    path: str,
    query: Optional[
        Dict[str, str]
    ] = None,
) -> Any:

    if not PUBLIC_READ_ONLY:

        raise RuntimeError(
            "Public reads disabled"
        )

    query_string = urllib.parse.urlencode(
        query or {}
    )

    url = (

        BASE_URL

        + path

        + (
            f"?{query_string}"
            if query_string
            else ""
        )
    )

    data = safe_http_get(

        url,

        headers={
            "Accept":
                "application/json",

            "User-Agent":
                VERSION,
        },
    )

    with COUNTER_LOCK:

        COUNTERS.public_gets += 1

    return data


# =============================================================================
# WRITE FIREBREAK
# =============================================================================

def reject_network_write(
    method: str,
    path: str,
) -> None:

    method = method.upper()

    raise RuntimeError(

        f"NETWORK WRITE BLOCKED: "
        f"{method} {path}"
    )


# =============================================================================
# RESPONSE PARSING
# =============================================================================

def unwrap_data(
    payload: Any,
) -> Any:

    current = payload

    for _ in range(4):

        if isinstance(
            current,
            dict,
        ):

            if "data" in current:

                current = (
                    current["data"]
                )

                continue

            if "result" in current:

                current = (
                    current["result"]
                )

                continue

        break

    return current


def find_first_number(
    value: Any,
    keys: Tuple[str, ...],
) -> Optional[Decimal]:

    if isinstance(
        value,
        dict,
    ):

        for key in keys:

            if key in value:

                try:

                    return dec(
                        value[key]
                    )

                except Exception:
                    pass

        for child in value.values():

            found = find_first_number(
                child,
                keys,
            )

            if found is not None:

                return found

    elif isinstance(
        value,
        list,
    ):

        for child in value:

            found = find_first_number(
                child,
                keys,
            )

            if found is not None:

                return found

    return None


def extract_available_usdt(
    payload: Any,
) -> Optional[Decimal]:

    root = unwrap_data(
        payload
    )

    if isinstance(
        root,
        list,
    ):

        for item in root:

            if not isinstance(
                item,
                dict,
            ):

                continue

            coin = str(

                item.get("coin")

                or item.get("asset")

                or item.get("currency")

                or item.get(
                    "marginCoin"
                )

                or ""

            ).upper()

            if (
                coin
                and coin != "USDT"
            ):

                continue

            found = find_first_number(

                item,

                (
                    "available",
                    "availableBalance",
                    "availableEquity",
                    "availableMargin",
                    "free",
                ),
            )

            if found is not None:

                return found

    return find_first_number(

        root,

        (
            "available",
            "availableBalance",
            "availableEquity",
            "availableMargin",
            "free",
        ),
    )


def extract_mark_price(
    payload: Any,
) -> Optional[Decimal]:

    root = unwrap_data(
        payload
    )

    return find_first_number(

        root,

        (
            "markPrice",
            "mark_price",
            "last",
            "lastPrice",
            "close",
            "price",
        ),
    )


def extract_open_positions(
    payload: Any,
) -> int:

    root = unwrap_data(
        payload
    )

    if isinstance(
        root,
        list,
    ):

        records = root

    elif isinstance(
        root,
        dict,
    ):

        records = [root]

    else:

        records = []

    count = 0

    for item in records:

        if not isinstance(
            item,
            dict,
        ):

            continue

        symbol = str(

            item.get("symbol")

            or item.get(
                "contractCode"
            )

            or ""

        ).upper()

        if (
            symbol
            and symbol != SYMBOL
        ):

            continue

        size = find_first_number(

            item,

            (
                "size",
                "positionAmt",
                "positionSize",
                "total",
                "available",
                "holdVol",
            ),
        )

        if (
            size is not None
            and size != 0
        ):

            count += 1

    return count


# =============================================================================
# LIVE STATE
# =============================================================================

@dataclass(
    frozen=True
)
class LiveState:

    generation: int

    observed_at_ms: int

    symbol: str

    available_usdt: str

    mark_price: str

    margin_type: str

    long_leverage: str

    short_leverage: str

    open_positions: int

    source: str

    @property
    def hash(self) -> str:

        return sha256_obj(
            asdict(self)
        )


def read_live_state() -> LiveState:

    available = (
        FALLBACK_AVAILABLE_USDT
    )

    mark_price = (
        FALLBACK_MARK_PRICE
    )

    open_positions = (
        FALLBACK_OPEN_POSITIONS
    )

    source_parts = []

    if LIVE_READS_ENABLED:

        try:

            balance_payload = (
                authenticated_get(
                    BALANCE_PATH
                )
            )

            parsed = (
                extract_available_usdt(
                    balance_payload
                )
            )

            if (
                parsed is not None
                and parsed > 0
            ):

                available = parsed

            source_parts.append(
                "balance-live"
            )

        except Exception as exc:

            log(
                f"{VERSION}: "
                f"BALANCE READ WARNING="
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            source_parts.append(
                "balance-fallback"
            )

        try:

            positions_payload = (
                authenticated_get(
                    POSITIONS_PATH
                )
            )

            open_positions = (
                extract_open_positions(
                    positions_payload
                )
            )

            source_parts.append(
                "positions-live"
            )

        except Exception as exc:

            log(
                f"{VERSION}: "
                f"POSITIONS READ WARNING="
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            source_parts.append(
                "positions-fallback"
            )

        try:

            ticker_payload = public_get(

                MARK_PRICE_PATH,

                {
                    "symbol":
                        SYMBOL
                },
            )

            parsed_price = (
                extract_mark_price(
                    ticker_payload
                )
            )

            if (
                parsed_price is not None
                and parsed_price > 0
            ):

                mark_price = (
                    parsed_price
                )

            source_parts.append(
                "price-live"
            )

        except Exception as exc:

            log(
                f"{VERSION}: "
                f"PRICE READ WARNING="
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            source_parts.append(
                "price-fallback"
            )

    else:

        source_parts.append(
            "deterministic-fallback"
        )

    return LiveState(

        generation=1,

        observed_at_ms=now_ms(),

        symbol=SYMBOL,

        available_usdt=
            fmt_decimal(
                available
            ),

        mark_price=
            fmt_decimal(
                mark_price
            ),

        margin_type=
            FALLBACK_MARGIN_TYPE,

        long_leverage=
            fmt_decimal(
                FALLBACK_LONG_LEVERAGE
            ),

        short_leverage=
            fmt_decimal(
                FALLBACK_SHORT_LEVERAGE
            ),

        open_positions=
            open_positions,

        source=
            "+".join(
                source_parts
            ),
    )


# =============================================================================
# SYNTHETIC INTENT
# =============================================================================

def build_intent(
    state: LiveState,
) -> Dict[str, Any]:

    balance = dec(
        state.available_usdt
    )

    price = dec(
        state.mark_price
    )

    margin_budget = (

        balance

        * INITIAL_ENTRY_PERCENT

        / Decimal("100")
    )

    planned_notional = (

        margin_budget

        * TARGET_LONG_LEVERAGE
    )

    raw_qty = (

        planned_notional

        / price
    )

    rounded_qty = floor_step(

        raw_qty,

        QTY_STEP,
    )

    if rounded_qty < MIN_QTY:

        rounded_qty = (
            MIN_QTY
        )

    created = now_ms()

    intent = {

        "version":
            VERSION,

        "synthetic":
            True,

        "transmit":
            False,

        "networkWrite":
            False,

        "realExecution":
            False,

        "demoExecution":
            False,

        "symbol":
            SYMBOL,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            fmt_decimal(
                rounded_qty
            ),

        "stateGeneration":
            state.generation,

        "stateHash":
            state.hash,

        "createdAtMs":
            created,

        "expiresAtMs":
            (
                created
                +
                SIGNAL_EXPIRY_SECONDS
                * 1000
            ),
    }

    intent["intentHash"] = (
        sha256_obj(
            intent
        )
    )

    return intent


# =============================================================================
# SYNTHETIC ORDER PAYLOAD
# =============================================================================

def build_payload(
    intent: Dict[str, Any],
) -> Dict[str, str]:

    client_order_id = (

        "r34r-"

        + secrets.token_hex(10)
    )

    return {

        "newClientOrderId":
            client_order_id,

        "positionSide":
            str(
                intent[
                    "positionSide"
                ]
            ),

        "quantity":
            str(
                intent[
                    "quantity"
                ]
            ),

        "side":
            str(
                intent[
                    "side"
                ]
            ),

        "symbol":
            str(
                intent[
                    "symbol"
                ]
            ),

        "type":
            str(
                intent[
                    "type"
                ]
            ),
    }


# =============================================================================
# SYNTHETIC AUTHENTICATED HEADERS
# =============================================================================

def synthetic_auth_headers(
    method: str,
    path: str,
    body: str,
) -> Dict[str, str]:

    key, secret, passphrase = (
        credentials()
    )

    synthetic_key = (
        key
        or "SYNTHETIC-KEY"
    )

    synthetic_secret = (
        secret
        or "SYNTHETIC-SECRET"
    )

    synthetic_passphrase = (
        passphrase
        or "SYNTHETIC-PASSPHRASE"
    )

    timestamp = str(
        now_ms()
    )

    prehash = (

        f"{timestamp}"

        f"{method.upper()}"

        f"{path}"

        f"{body}"
    )

    signature = base64.b64encode(

        hmac.new(

            synthetic_secret.encode(
                "utf-8"
            ),

            prehash.encode(
                "utf-8"
            ),

            hashlib.sha256,

        ).digest()

    ).decode(
        "ascii"
    )

    return {

        "ACCESS-KEY":
            synthetic_key,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            synthetic_passphrase,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",
    }


# =============================================================================
# SYNTHETIC ENVELOPE
# =============================================================================

def build_synthetic_envelope(
    payload: Dict[str, str],
) -> Dict[str, Any]:

    body = canonical_json(
        payload
    )

    # Deliberately non-exchange path.
    path = (
        "/SYNTHETIC/contract/order"
    )

    headers = (
        synthetic_auth_headers(
            "POST",
            path,
            body,
        )
    )

    envelope = {

        "version":
            VERSION,

        "synthetic":
            True,

        "transmitted":
            False,

        "forbidTransmission":
            True,

        "forbidNetworkWrite":
            True,

        "forbidRealExecution":
            True,

        "forbidDemoExecution":
            True,

        "method":
            "POST",

        "path":
            path,

        "body":
            body,

        "payloadHash":
            sha256_text(
                body
            ),

        "headers":
            headers,

        "createdAtMs":
            now_ms(),
    }

    envelope["envelopeHash"] = (
        sha256_obj(
            envelope
        )
    )

    return envelope


# =============================================================================
# ONE-TIME SYNTHETIC AUTHORIZATION
# =============================================================================

@dataclass
class Authorization:

    authorizationId: str

    syntheticOnly: bool

    forbidTransmission: bool

    forbidNetworkWrite: bool

    intentHash: str

    payloadHash: str

    envelopeHash: str

    liveStateHash: str

    createdAtMs: int

    expiresAtMs: int

    consumed: bool = False

    consumedAtMs: Optional[
        int
    ] = None

    authorizationHash: str = ""

    def seal(self) -> None:

        data = asdict(
            self
        )

        data[
            "authorizationHash"
        ] = ""

        self.authorizationHash = (
            sha256_obj(
                data
            )
        )


def build_authorization(
    intent: Dict[str, Any],
    payload: Dict[str, str],
    envelope: Dict[str, Any],
    state: LiveState,
) -> Authorization:

    created = now_ms()

    auth = Authorization(

        authorizationId=
            (
                "auth-"
                +
                secrets.token_hex(
                    16
                )
            ),

        syntheticOnly=True,

        forbidTransmission=True,

        forbidNetworkWrite=True,

        intentHash=
            str(
                intent[
                    "intentHash"
                ]
            ),

        payloadHash=
            sha256_obj(
                payload
            ),

        envelopeHash=
            str(
                envelope[
                    "envelopeHash"
                ]
            ),

        liveStateHash=
            state.hash,

        createdAtMs=
            created,

        expiresAtMs=
            (
                created
                +
                SIGNAL_EXPIRY_SECONDS
                * 1000
            ),
    )

    auth.seal()

    return auth


def authorization_integrity_ok(
    auth: Authorization,
) -> bool:

    expected = (
        auth.authorizationHash
    )

    data = asdict(
        auth
    )

    data[
        "authorizationHash"
    ] = ""

    actual = sha256_obj(
        data
    )

    return hmac.compare_digest(
        expected,
        actual,
    )


def validate_authorization(
    auth: Authorization,
    intent: Dict[str, Any],
    payload: Dict[str, str],
    envelope: Dict[str, Any],
    state: LiveState,
    *,
    count_stale: bool = True,
) -> Tuple[
    bool,
    str,
]:

    if not authorization_integrity_ok(
        auth
    ):

        return (
            False,
            "authorization-integrity",
        )

    if auth.consumed:

        return (
            False,
            "authorization-consumed",
        )

    if now_ms() >= auth.expiresAtMs:

        return (
            False,
            "authorization-expired",
        )

    if (
        not auth.syntheticOnly
        or not auth.forbidTransmission
        or not auth.forbidNetworkWrite
    ):

        return (
            False,
            "authorization-firebreak",
        )

    if (
        auth.intentHash
        != intent["intentHash"]
    ):

        return (
            False,
            "intent-hash",
        )

    if (
        auth.payloadHash
        != sha256_obj(
            payload
        )
    ):

        return (
            False,
            "payload-hash",
        )

    if (
        auth.envelopeHash
        != envelope[
            "envelopeHash"
        ]
    ):

        return (
            False,
            "envelope-hash",
        )

    if (
        auth.liveStateHash
        != state.hash
    ):

        if count_stale:

            with COUNTER_LOCK:

                COUNTERS.stale_state_blocks += 1

        return (
            False,
            "stale-live-state",
        )

    return (
        True,
        "ok",
    )


# =============================================================================
# R34R EXACTLY-ONCE SYNTHETIC DISPATCH
# =============================================================================

DISPATCH_LOCK = (
    threading.Lock()
)

SYNTHETIC_RECEIPTS: Dict[
    str,
    Dict[str, Any],
] = {}


class DuplicateSyntheticDispatch(
    RuntimeError
):
    pass


def synthetic_dispatch_once(
    auth: Authorization,
    intent: Dict[str, Any],
    payload: Dict[str, str],
    envelope: Dict[str, Any],
    state: LiveState,
) -> Dict[str, Any]:

    """
    PURELY LOCAL SYNTHETIC DISPATCH.

    IMPORTANT:

    No HTTP call.
    No socket call.
    No retry.
    No sleep.
    No exchange POST.
    No nested DISPATCH_LOCK.

    The short critical section performs:

    1. duplicate check
    2. authorization validation
    3. one-time consumption
    4. local receipt creation
    5. synthetic dispatch counter increment
    """

    with DISPATCH_LOCK:

        existing = (
            SYNTHETIC_RECEIPTS.get(
                auth.authorizationId
            )
        )

        if existing is not None:

            with COUNTER_LOCK:

                COUNTERS.duplicate_dispatch_blocks += 1

            raise DuplicateSyntheticDispatch(
                "synthetic authorization "
                "already dispatched"
            )

        ok, reason = (
            validate_authorization(

                auth,

                intent,

                payload,

                envelope,

                state,

                count_stale=False,
            )
        )

        if not ok:

            if (
                reason
                ==
                "authorization-consumed"
            ):

                with COUNTER_LOCK:

                    COUNTERS.duplicate_dispatch_blocks += 1

                raise DuplicateSyntheticDispatch(
                    reason
                )

            raise RuntimeError(
                f"synthetic dispatch "
                f"rejected: {reason}"
            )

        # -------------------------------------------------------------
        # CONSUME EXACTLY ONCE
        # -------------------------------------------------------------

        auth.consumed = True

        auth.consumedAtMs = (
            now_ms()
        )

        auth.seal()

        # -------------------------------------------------------------
        # LOCAL SYNTHETIC RECEIPT
        # -------------------------------------------------------------

        receipt_core = {

            "version":
                VERSION,

            "receiptId":
                (
                    "receipt-"
                    +
                    secrets.token_hex(
                        16
                    )
                ),

            "authorizationId":
                auth.authorizationId,

            "synthetic":
                True,

            "transmitted":
                False,

            "networkWrite":
                False,

            "realExecution":
                False,

            "demoExecution":
                False,

            "intentHash":
                intent[
                    "intentHash"
                ],

            "payloadHash":
                sha256_obj(
                    payload
                ),

            "envelopeHash":
                envelope[
                    "envelopeHash"
                ],

            "liveStateHash":
                state.hash,

            "clientOrderId":
                payload[
                    "newClientOrderId"
                ],

            "createdAtMs":
                now_ms(),
        }

        receipt = dict(
            receipt_core
        )

        receipt[
            "receiptHash"
        ] = sha256_obj(
            receipt_core
        )

        SYNTHETIC_RECEIPTS[
            auth.authorizationId
        ] = receipt

        with COUNTER_LOCK:

            COUNTERS.synthetic_dispatches += 1

        return deep_copy_json(
            receipt
        )


# =============================================================================
# R34R TEST SUITE
# =============================================================================

def run_tests() -> None:

    heading(
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
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: PUBLIC READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )


    # =========================================================================
    # TEST 1
    # =========================================================================

    heading(
        f"{VERSION} TEST 1: HARD SAFETY FIREBREAKS"
    )

    result(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    result(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION,
    )

    result(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    result(
        "Network Writes Are Disabled",
        not NETWORK_WRITES,
    )

    result(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION,
    )

    result(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION,
    )

    result(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION,
    )

    result(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    heading(
        f"{VERSION} TEST 2: CREDENTIAL PRESENCE"
    )

    key, secret, passphrase = (
        credentials()
    )

    if LIVE_READS_ENABLED:

        result(
            "WEEX API Key Is Present",
            bool(key),
        )

        result(
            "WEEX API Secret Is Present",
            bool(secret),
        )

        result(
            "WEEX API Passphrase Is Present",
            bool(passphrase),
        )

    else:

        result(
            "Offline Mode Does Not Require API Key",
            True,
        )

        result(
            "Offline Mode Does Not Require API Secret",
            True,
        )

        result(
            "Offline Mode Does Not Require API Passphrase",
            True,
        )


    # =========================================================================
    # TEST 3
    # =========================================================================

    heading(
        f"{VERSION} TEST 3: LIVE READ-ONLY SNAPSHOT"
    )

    state = (
        read_live_state()
    )

    balance = dec(
        state.available_usdt
    )

    mark_price = dec(
        state.mark_price
    )

    result(
        "Available Balance Is Positive",
        balance > 0,
    )

    result(
        "Market Price Is Positive",
        mark_price > 0,
    )

    result(
        "Symbol Matches BTCUSDT",
        state.symbol == SYMBOL,
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{state.available_usdt}"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{state.mark_price}"
    )

    log(
        f"{VERSION}: LIVE STATE SOURCE="
        f"{state.source}"
    )

    log(
        f"{VERSION}: LIVE STATE SHA256="
        f"{state.hash}"
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    heading(
        f"{VERSION} TEST 4: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    result(
        "Margin Type Is ISOLATED",
        state.margin_type
        ==
        TARGET_MARGIN_TYPE,
    )

    result(
        "Long Leverage Is 100x",
        dec(
            state.long_leverage
        )
        ==
        TARGET_LONG_LEVERAGE,
    )

    result(
        "Short Leverage Is 100x",
        dec(
            state.short_leverage
        )
        ==
        TARGET_SHORT_LEVERAGE,
    )

    result(
        "BTCUSDT Has No Open Positions",
        state.open_positions == 0,
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    heading(
        f"{VERSION} TEST 5: INITIAL ENTRY READINESS"
    )

    initial_margin = (

        balance

        * INITIAL_ENTRY_PERCENT

        / Decimal("100")
    )

    initial_notional = (

        initial_margin

        * TARGET_LONG_LEVERAGE
    )

    raw_qty = (

        initial_notional

        / mark_price
    )

    rounded_qty = floor_step(

        raw_qty,

        QTY_STEP,
    )

    result(
        "Initial Entry Percent Is Positive",
        INITIAL_ENTRY_PERCENT > 0,
    )

    result(
        "Initial Entry Is Within Exposure Cap",
        INITIAL_ENTRY_PERCENT
        <=
        MAX_FUND_EXPOSURE_PERCENT,
    )

    result(
        "Initial Entry Margin Budget Is Positive",
        initial_margin > 0,
    )

    result(
        "Rounded Quantity Meets Minimum",
        rounded_qty >= MIN_QTY,
    )

    log(
        f"{VERSION}: INITIAL MARGIN="
        f"{fmt_decimal(initial_margin)} USDT"
    )

    log(
        f"{VERSION}: INITIAL NOTIONAL="
        f"{fmt_decimal(initial_notional)} USDT"
    )

    log(
        f"{VERSION}: RAW QTY="
        f"{fmt_decimal(raw_qty)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED QTY="
        f"{fmt_decimal(rounded_qty)} BTC"
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    heading(
        f"{VERSION} TEST 6: PYRAMID STRUCTURE"
    )

    result(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    result(
        "Pyramid Percent Is Five",
        PYRAMID_PERCENT
        ==
        Decimal("5"),
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    heading(
        f"{VERSION} TEST 7: BACKUP STRUCTURE"
    )

    result(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3,
    )

    result(
        "Backup Percent Is Five",
        BACKUP_PERCENT
        ==
        Decimal("5"),
    )

    result(
        "Backup Buffer Is Positive",
        BACKUP_BUFFER_PERCENT > 0,
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    heading(
        f"{VERSION} TEST 8: TAKE-PROFIT STRUCTURE"
    )

    result(
        "TP Percentages Sum To 100",
        (
            TP1_PERCENT
            +
            TP2_PERCENT
            +
            TP3_PERCENT
        )
        ==
        Decimal("100"),
    )

    result(
        "TP1 Trigger Is 0.5%",
        TP1_TRIGGER_PERCENT
        ==
        Decimal("0.5"),
    )

    result(
        "TP2 Trigger Is 1.0%",
        TP2_TRIGGER_PERCENT
        ==
        Decimal("1.0"),
    )

    result(
        "Trailing Distance Is 0.20%",
        TRAILING_DISTANCE_PERCENT
        ==
        Decimal("0.20"),
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    heading(
        f"{VERSION} TEST 9: SIGNAL TIMING"
    )

    result(
        "Signal Expiry Is Positive",
        SIGNAL_EXPIRY_SECONDS > 0,
    )

    result(
        "Loss Cooldown Is Positive",
        LOSS_COOLDOWN_SECONDS > 0,
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    heading(
        f"{VERSION} TEST 10: QUANTITY RULES"
    )

    result(
        "Quantity Step Is 0.0001",
        QTY_STEP
        ==
        Decimal("0.0001"),
    )

    result(
        "Minimum Quantity Is 0.0001",
        MIN_QTY
        ==
        Decimal("0.0001"),
    )

    result(
        "Price Step Is 0.1",
        PRICE_STEP
        ==
        Decimal("0.1"),
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    heading(
        f"{VERSION} TEST 11: MAXIMUM STRATEGY EXPOSURE"
    )

    max_allowed_margin = (

        balance

        * MAX_FUND_EXPOSURE_PERCENT

        / Decimal("100")
    )

    planned_max_margin = (

        balance

        * (

            INITIAL_ENTRY_PERCENT

            +

            PYRAMID_PERCENT
            *
            MAX_PYRAMID_ADDS

            +

            BACKUP_PERCENT
            *
            MAX_BACKUPS

        )

        / Decimal("100")
    )

    result(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    result(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3,
    )

    result(
        "Maximum Planned Strategy Margin Is Within 35%",
        planned_max_margin
        <=
        max_allowed_margin,
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{fmt_decimal(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{fmt_decimal(max_allowed_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{fmt_decimal(planned_max_margin)} USDT"
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    heading(
        f"{VERSION} TEST 12: FINAL EXECUTION-READINESS FIREBREAK"
    )

    result(
        "Network Write Counter Is Zero",
        COUNTERS.network_writes == 0,
    )

    result(
        "Leverage Mutation Counter Is Zero",
        COUNTERS.leverage_mutations == 0,
    )

    result(
        "Margin Mutation Counter Is Zero",
        COUNTERS.margin_mutations == 0,
    )

    result(
        "Position Mutation Counter Is Zero",
        COUNTERS.position_mutations == 0,
    )

    result(
        "Account Mutation Counter Is Zero",
        COUNTERS.account_mutations == 0,
    )

    result(
        "Real Order Counter Is Zero",
        COUNTERS.real_orders == 0,
    )

    result(
        "Demo Order Counter Is Zero",
        COUNTERS.demo_orders == 0,
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    heading(
        f"{VERSION} TEST 13: SYNTHETIC EXECUTION INTENT"
    )

    intent = build_intent(
        state
    )

    result(
        "Intent Is Marked Synthetic",
        intent[
            "synthetic"
        ] is True,
    )

    result(
        "Intent Forbids Transmission",
        intent[
            "transmit"
        ] is False,
    )

    result(
        "Intent Forbids Network Write",
        intent[
            "networkWrite"
        ] is False,
    )

    result(
        "Intent Forbids Real Execution",
        intent[
            "realExecution"
        ] is False,
    )

    result(
        "Intent Forbids Demo Execution",
        intent[
            "demoExecution"
        ] is False,
    )

    result(
        "Intent Binds Exact Live State",
        intent[
            "stateHash"
        ]
        ==
        state.hash,
    )

    result(
        "Intent Has Future Expiry",
        intent[
            "expiresAtMs"
        ]
        >
        now_ms(),
    )

    result(
        "Intent Hash Exists",
        bool(
            intent[
                "intentHash"
            ]
        ),
    )

    log(
        f"{VERSION}: SYNTHETIC INTENT SHA256="
        f"{intent['intentHash']}"
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    heading(
        f"{VERSION} TEST 14: SYNTHETIC PAYLOAD CANONICALIZATION"
    )

    payload = build_payload(
        intent
    )

    payload_hash = (
        sha256_obj(
            payload
        )
    )

    result(
        "Payload Symbol Matches Intent",
        payload[
            "symbol"
        ]
        ==
        intent[
            "symbol"
        ],
    )

    result(
        "Payload Side Matches Intent",
        payload[
            "side"
        ]
        ==
        intent[
            "side"
        ],
    )

    result(
        "Payload Position Side Matches Intent",
        payload[
            "positionSide"
        ]
        ==
        intent[
            "positionSide"
        ],
    )

    result(
        "Payload Quantity Matches Intent",
        payload[
            "quantity"
        ]
        ==
        intent[
            "quantity"
        ],
    )

    result(
        "Payload Type Matches Intent",
        payload[
            "type"
        ]
        ==
        intent[
            "type"
        ],
    )

    result(
        "Payload Client Order ID Uses R34R Prefix",
        payload[
            "newClientOrderId"
        ].startswith(
            "r34r-"
        ),
    )

    result(
        "Payload Hash Exists",
        bool(
            payload_hash
        ),
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD="
        f"{canonical_json(payload)}"
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD SHA256="
        f"{payload_hash}"
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    heading(
        f"{VERSION} TEST 15: PAYLOAD IMMUTABILITY CHECK"
    )

    payload_copy = (
        deep_copy_json(
            payload
        )
    )

    result(
        "Canonical Payload Is Stable",
        canonical_json(
            payload_copy
        )
        ==
        canonical_json(
            payload
        ),
    )

    result(
        "Payload Hash Recomputes Exactly",
        sha256_obj(
            payload_copy
        )
        ==
        payload_hash,
    )


    # =========================================================================
    # TEST 16
    # =========================================================================

    heading(
        f"{VERSION} TEST 16: SYNTHETIC AUTHENTICATED EXECUTION ENVELOPE"
    )

    envelope = (
        build_synthetic_envelope(
            payload
        )
    )

    result(
        "Envelope Is Marked Synthetic",
        envelope[
            "synthetic"
        ] is True,
    )

    result(
        "Envelope Forbids Transmission",
        envelope[
            "forbidTransmission"
        ] is True,
    )

    result(
        "Envelope Uses POST Method Locally",
        envelope[
            "method"
        ]
        ==
        "POST",
    )

    result(
        "Envelope Body Matches Canonical Payload",
        envelope[
            "body"
        ]
        ==
        canonical_json(
            payload
        ),
    )

    result(
        "Envelope Payload Hash Recomputes Exactly",
        envelope[
            "payloadHash"
        ]
        ==
        sha256_obj(
            payload
        ),
    )

    result(
        "ACCESS-KEY Header Is Present",
        bool(
            envelope[
                "headers"
            ].get(
                "ACCESS-KEY"
            )
        ),
    )

    result(
        "ACCESS-SIGN Header Is Present",
        bool(
            envelope[
                "headers"
            ].get(
                "ACCESS-SIGN"
            )
        ),
    )

    result(
        "ACCESS-PASSPHRASE Header Is Present",
        bool(
            envelope[
                "headers"
            ].get(
                "ACCESS-PASSPHRASE"
            )
        ),
    )

    result(
        "ACCESS-TIMESTAMP Header Is Present",
        bool(
            envelope[
                "headers"
            ].get(
                "ACCESS-TIMESTAMP"
            )
        ),
    )

    result(
        "Envelope Explicitly Forbids Network Write",
        envelope[
            "forbidNetworkWrite"
        ] is True,
    )

    result(
        "Envelope Explicitly Forbids Real Execution",
        envelope[
            "forbidRealExecution"
        ] is True,
    )

    result(
        "Envelope Explicitly Forbids Demo Execution",
        envelope[
            "forbidDemoExecution"
        ] is True,
    )

    result(
        "Envelope Hash Exists",
        bool(
            envelope[
                "envelopeHash"
            ]
        ),
    )

    log(
        f"{VERSION}: SYNTHETIC ENVELOPE SHA256="
        f"{envelope['envelopeHash']}"
    )

    log(
        f"{VERSION}: SYNTHETIC ENVELOPE TRANSMITTED="
        f"{envelope['transmitted']}"
    )


    # =========================================================================
    # TEST 17
    # =========================================================================

    heading(
        f"{VERSION} TEST 17: ONE-TIME SYNTHETIC AUTHORIZATION"
    )

    auth = build_authorization(
        intent,
        payload,
        envelope,
        state,
    )

    result(
        "Authorization Is Synthetic Only",
        auth.syntheticOnly
        is True,
    )

    result(
        "Authorization Forbids Transmission",
        auth.forbidTransmission
        is True,
    )

    result(
        "Authorization Forbids Network Write",
        auth.forbidNetworkWrite
        is True,
    )

    result(
        "Authorization Is Initially Unconsumed",
        auth.consumed
        is False,
    )

    result(
        "Authorization Binds Exact Intent",
        auth.intentHash
        ==
        intent[
            "intentHash"
        ],
    )

    result(
        "Authorization Binds Exact Payload",
        auth.payloadHash
        ==
        sha256_obj(
            payload
        ),
    )

    result(
        "Authorization Binds Exact Envelope",
        auth.envelopeHash
        ==
        envelope[
            "envelopeHash"
        ],
    )

    result(
        "Authorization Binds Exact Live State",
        auth.liveStateHash
        ==
        state.hash,
    )

    result(
        "Authorization Has Future Expiry",
        auth.expiresAtMs
        >
        now_ms(),
    )

    result(
        "Authorization Integrity Recomputes Exactly",
        authorization_integrity_ok(
            auth
        ),
    )

    log(
        f"{VERSION}: AUTHORIZATION ID="
        f"{auth.authorizationId}"
    )

    log(
        f"{VERSION}: AUTHORIZATION SHA256="
        f"{auth.authorizationHash}"
    )


    # =========================================================================
    # TEST 18
    # =========================================================================

    heading(
        f"{VERSION} TEST 18: STALE STATE REJECTION"
    )

    stale_state = LiveState(

        generation=
            state.generation
            + 1,

        observed_at_ms=
            state.observed_at_ms
            + 1,

        symbol=
            state.symbol,

        available_usdt=
            state.available_usdt,

        mark_price=
            state.mark_price,

        margin_type=
            state.margin_type,

        long_leverage=
            state.long_leverage,

        short_leverage=
            state.short_leverage,

        open_positions=
            state.open_positions,

        source=
            state.source,
    )

    stale_ok, stale_reason = (
        validate_authorization(

            auth,

            intent,

            payload,

            envelope,

            stale_state,
        )
    )

    result(
        "Synthetic Stale State Is Rejected",
        (
            stale_ok is False
            and
            stale_reason
            ==
            "stale-live-state"
        ),
    )

    result(
        "Stale State Block Counter Is One",
        COUNTERS.stale_state_blocks
        ==
        1,
    )

    result(
        "Stale Rejection Does Not Consume Authorization",
        auth.consumed
        is False,
    )


    # =========================================================================
    # TEST 19
    # =========================================================================

    heading(
        f"{VERSION} TEST 19: FRESH AUTHORIZATION VALIDATION"
    )

    fresh_ok, fresh_reason = (
        validate_authorization(

            auth,

            intent,

            payload,

            envelope,

            state,
        )
    )

    result(
        "Fresh Authorization Is Accepted",
        (
            fresh_ok
            is True
            and
            fresh_reason
            ==
            "ok"
        ),
    )

    result(
        "Validation Alone Does Not Consume Authorization",
        auth.consumed
        is False,
    )


    # =========================================================================
    # TEST 20
    # FIXED EXACTLY-ONCE SYNTHETIC DISPATCH
    # =========================================================================

    heading(
        f"{VERSION} TEST 20: EXACTLY-ONCE SYNTHETIC DISPATCH"
    )

    log(
        f"{VERSION}: TEST 20 ENTERED"
    )

    receipt = (
        synthetic_dispatch_once(

            auth,

            intent,

            payload,

            envelope,

            state,
        )
    )

    log(
        f"{VERSION}: TEST 20 FIRST SYNTHETIC DISPATCH RETURNED"
    )

    result(
        "Authorization Is Consumed Exactly Once",
        (
            auth.consumed
            is True
            and
            auth.consumedAtMs
            is not None
        ),
    )

    result(
        "Synthetic Dispatch Count Is One",
        COUNTERS.synthetic_dispatches
        ==
        1,
    )

    result(
        "Synthetic Receipt Is Marked Synthetic",
        receipt[
            "synthetic"
        ]
        is True,
    )

    result(
        "Synthetic Receipt Was Not Transmitted",
        receipt[
            "transmitted"
        ]
        is False,
    )

    result(
        "Receipt Records No Network Write",
        receipt[
            "networkWrite"
        ]
        is False,
    )

    result(
        "Receipt Records No Real Execution",
        receipt[
            "realExecution"
        ]
        is False,
    )

    result(
        "Receipt Records No Demo Execution",
        receipt[
            "demoExecution"
        ]
        is False,
    )

    result(
        "Receipt Binds Exact Authorization",
        receipt[
            "authorizationId"
        ]
        ==
        auth.authorizationId,
    )

    result(
        "Receipt Binds Exact Intent",
        receipt[
            "intentHash"
        ]
        ==
        intent[
            "intentHash"
        ],
    )

    result(
        "Receipt Binds Exact Payload",
        receipt[
            "payloadHash"
        ]
        ==
        sha256_obj(
            payload
        ),
    )

    result(
        "Receipt Binds Exact Envelope",
        receipt[
            "envelopeHash"
        ]
        ==
        envelope[
            "envelopeHash"
        ],
    )

    result(
        "Receipt Binds Exact Live State",
        receipt[
            "liveStateHash"
        ]
        ==
        state.hash,
    )

    result(
        "Receipt Client Order ID Matches Payload",
        receipt[
            "clientOrderId"
        ]
        ==
        payload[
            "newClientOrderId"
        ],
    )

    result(
        "Receipt Hash Exists",
        bool(
            receipt[
                "receiptHash"
            ]
        ),
    )


    # -------------------------------------------------------------------------
    # SECOND DISPATCH MUST FAIL
    # -------------------------------------------------------------------------

    duplicate_rejected = False

    try:

        synthetic_dispatch_once(

            auth,

            intent,

            payload,

            envelope,

            state,
        )

    except DuplicateSyntheticDispatch:

        duplicate_rejected = True


    result(
        "Duplicate Synthetic Dispatch Is Rejected",
        duplicate_rejected,
    )

    result(
        "Duplicate Dispatch Block Counter Is One",
        COUNTERS.duplicate_dispatch_blocks
        ==
        1,
    )

    result(
        "Synthetic Dispatch Count Remains One",
        COUNTERS.synthetic_dispatches
        ==
        1,
    )

    result(
        "Authorization Cannot Be Reused",
        auth.consumed
        is True,
    )

    result(
        "Network Write Counter Remains Zero",
        COUNTERS.network_writes
        ==
        0,
    )

    result(
        "Real Order Counter Remains Zero",
        COUNTERS.real_orders
        ==
        0,
    )

    result(
        "Demo Order Counter Remains Zero",
        COUNTERS.demo_orders
        ==
        0,
    )

    log(
        f"{VERSION}: SYNTHETIC RECEIPT SHA256="
        f"{receipt['receiptHash']}"
    )


    # =========================================================================
    # TEST 21
    # =========================================================================

    heading(
        f"{VERSION} TEST 21: POST-DISPATCH INVARIANTS"
    )

    result(
        "Exactly One Synthetic Receipt Exists",
        len(
            SYNTHETIC_RECEIPTS
        )
        ==
        1,
    )

    result(
        "Exactly One Synthetic Dispatch Was Counted",
        COUNTERS.synthetic_dispatches
        ==
        1,
    )

    result(
        "Exactly One Duplicate Was Blocked",
        COUNTERS.duplicate_dispatch_blocks
        ==
        1,
    )

    result(
        "Exactly One Stale State Was Blocked",
        COUNTERS.stale_state_blocks
        ==
        1,
    )

    result(
        "Network Writes Remain Zero",
        COUNTERS.network_writes
        ==
        0,
    )

    result(
        "Leverage Mutations Remain Zero",
        COUNTERS.leverage_mutations
        ==
        0,
    )

    result(
        "Margin Mutations Remain Zero",
        COUNTERS.margin_mutations
        ==
        0,
    )

    result(
        "Position Mutations Remain Zero",
        COUNTERS.position_mutations
        ==
        0,
    )

    result(
        "Account Mutations Remain Zero",
        COUNTERS.account_mutations
        ==
        0,
    )

    result(
        "Real Orders Remain Zero",
        COUNTERS.real_orders
        ==
        0,
    )

    result(
        "Demo Orders Remain Zero",
        COUNTERS.demo_orders
        ==
        0,
    )


    # =========================================================================
    # FINAL
    # =========================================================================

    heading(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        f"{VERSION}: "
        f"PHASE="
        f"SYNTHETIC_EXACTLY_ONCE_VALIDATED"
    )

    log(
        f"{VERSION}: "
        f"AUTHENTICATED GETS="
        f"{COUNTERS.authenticated_gets}"
    )

    log(
        f"{VERSION}: "
        f"PUBLIC GETS="
        f"{COUNTERS.public_gets}"
    )

    log(
        f"{VERSION}: "
        f"NETWORK WRITES="
        f"{COUNTERS.network_writes}"
    )

    log(
        f"{VERSION}: "
        f"LEVERAGE MUTATIONS="
        f"{COUNTERS.leverage_mutations}"
    )

    log(
        f"{VERSION}: "
        f"REAL ORDERS="
        f"{COUNTERS.real_orders}"
    )

    log(
        f"{VERSION}: "
        f"DEMO ORDERS="
        f"{COUNTERS.demo_orders}"
    )

    log(
        f"{VERSION}: "
        f"SYNTHETIC DISPATCHES="
        f"{COUNTERS.synthetic_dispatches}"
    )

    log(
        f"{VERSION}: "
        f"DUPLICATE DISPATCH BLOCKS="
        f"{COUNTERS.duplicate_dispatch_blocks}"
    )

    log(
        f"{VERSION}: "
        f"STALE STATE BLOCKS="
        f"{COUNTERS.stale_state_blocks}"
    )

    log(
        f"{VERSION}: "
        f"NO REAL OR DEMO ORDER WAS SENT"
    )


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop(
    stop_event: threading.Event,
) -> None:

    heartbeat = 0

    while not stop_event.wait(
        30
    ):

        heartbeat += 1

        log(

            f"{VERSION}: "
            f"HEARTBEAT {heartbeat} | "

            f"phase="
            f"SYNTHETIC_EXACTLY_ONCE_VALIDATED | "

            f"network-writes="
            f"{COUNTERS.network_writes} | "

            f"real-orders="
            f"{COUNTERS.real_orders} | "

            f"demo-orders="
            f"{COUNTERS.demo_orders} | "

            f"synthetic-dispatches="
            f"{COUNTERS.synthetic_dispatches} | "

            f"duplicate-blocks="
            f"{COUNTERS.duplicate_dispatch_blocks} | "

            f"stale-blocks="
            f"{COUNTERS.stale_state_blocks}"
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:

    health_server = (
        start_health_server()
    )

    stop_event = (
        threading.Event()
    )

    def shutdown_handler(
        signum: int,
        frame: Any,
    ) -> None:

        stop_event.set()

        raise SystemExit(0)


    try:

        signal.signal(
            signal.SIGTERM,
            shutdown_handler,
        )

        signal.signal(
            signal.SIGINT,
            shutdown_handler,
        )

    except Exception:

        pass


    try:

        run_tests()

    except Exception as exc:

        heading(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return 1


    heartbeat_thread = (
        threading.Thread(

            target=
                heartbeat_loop,

            args=(
                stop_event,
            ),

            name=
                "heartbeat",

            daemon=True,
        )
    )

    heartbeat_thread.start()


    try:

        while not stop_event.wait(
            1
        ):

            pass

    except KeyboardInterrupt:

        stop_event.set()

    finally:

        if health_server is not None:

            health_server.shutdown()

            health_server.server_close()


    return 0


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
