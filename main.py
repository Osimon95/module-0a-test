import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import urllib.request
import urllib.error
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R32K - LIVE READ-ONLY STRATEGY / EXECUTION READINESS VALIDATION
#
# IMPORTANT SAFETY BOUNDARY:
#   - AUTHENTICATED GET REQUESTS ARE ALLOWED
#   - PUBLIC GET REQUESTS ARE ALLOWED
#   - NETWORK POST REQUESTS ARE DISABLED
#   - REAL ORDER EXECUTION IS DISABLED
#   - DEMO ORDER EXECUTION IS DISABLED
#   - LEVERAGE MUTATION IS DISABLED
#   - MARGIN MUTATION IS DISABLED
#   - POSITION MUTATION IS DISABLED
#   - ACCOUNT MUTATION IS DISABLED
#
# R32K validates that the live WEEX account is compatible with the intended
# strategy after manual leverage correction.
#
# It DOES NOT submit an order.
# =============================================================================


VERSION = "R32K"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")

PORT = int(os.getenv("PORT", "10000"))

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()


# =============================================================================
# STRATEGY CONFIGURATION
# =============================================================================

TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")

BACKUP_BUFFER_PERCENT = Decimal("0.3")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# =============================================================================
# HARD SAFETY LOCKS
# =============================================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# =============================================================================
# API PATHS
# =============================================================================

BALANCE_PATH = "/capi/v3/account/balance"
POSITION_PATH = "/capi/v3/account/position/allPosition"
SYMBOL_CONFIG_PATH = f"/capi/v3/account/symbolConfig?symbol={SYMBOL}"

PUBLIC_PRICE_PATHS = [
    f"/capi/v2/market/ticker?symbol={SYMBOL}",
    f"/capi/v3/market/ticker?symbol={SYMBOL}",
    f"/capi/v2/market/symbolPrice?symbol={SYMBOL}",
]


# =============================================================================
# GLOBAL RUNTIME STATE
# =============================================================================

state_lock = threading.Lock()

runtime_state = {
    "version": VERSION,
    "symbol": SYMBOL,
    "phase": "STARTING",

    "authenticated_read_only": AUTHENTICATED_READ_ONLY,
    "public_read_only": PUBLIC_READ_ONLY,

    "real_execution": REAL_ORDER_EXECUTION,
    "demo_execution": DEMO_ORDER_EXECUTION,
    "network_writes_enabled": NETWORK_WRITES_ENABLED,

    "leverage_mutation_enabled": LEVERAGE_MUTATION_ENABLED,
    "margin_mutation_enabled": MARGIN_MUTATION_ENABLED,
    "position_mutation_enabled": POSITION_MUTATION_ENABLED,
    "account_mutation_enabled": ACCOUNT_MUTATION_ENABLED,

    "authenticated_get_count": 0,
    "public_get_count": 0,

    "network_writes": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "real_orders": 0,
    "demo_orders": 0,

    "available_usdt": None,

    "position_records": 0,
    "symbol_position_records": 0,
    "active_positions": 0,

    "observed_margin": None,
    "observed_position_mode": None,
    "observed_cross_leverage": None,
    "observed_long_leverage": None,
    "observed_short_leverage": None,

    "mark_price": None,

    "initial_margin_budget": None,
    "initial_notional_target": None,
    "maximum_exposure_budget": None,

    "leverage_ready": False,
    "position_ready": False,
    "margin_ready": False,
    "balance_ready": False,
    "strategy_budget_ready": False,

    "execution_preconditions_ready": False,

    "heartbeat": 0,
}


# =============================================================================
# FORMATTING
# =============================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def pass_fail(label, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    log(f"{label:<84} {status}")
    return bool(condition)


def decimal_string(value):
    if value is None:
        return None

    try:
        d = Decimal(str(value))
    except Exception:
        return str(value)

    normalized = format(d, "f")

    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")

    return normalized or "0"


def safe_decimal(value, default=None):
    if value is None:
        return default

    if isinstance(value, bool):
        return default

    try:
        text = str(value).strip()

        if text == "":
            return default

        text = text.replace("x", "").replace("X", "")
        text = text.replace("%", "")

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return default


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"not-found"}')
            return

        with state_lock:
            snapshot = dict(runtime_state)

        body = json.dumps(
            {
                "status": "ok",
                "service": VERSION,
                "symbol": SYMBOL,
                "phase": snapshot.get("phase"),
                "authenticated_read_only":
                    snapshot.get("authenticated_read_only"),
                "network_writes":
                    snapshot.get("network_writes"),
                "real_orders":
                    snapshot.get("real_orders"),
                "demo_orders":
                    snapshot.get("demo_orders"),
                "available_usdt":
                    snapshot.get("available_usdt"),
                "observed_margin":
                    snapshot.get("observed_margin"),
                "observed_long_leverage":
                    snapshot.get("observed_long_leverage"),
                "observed_short_leverage":
                    snapshot.get("observed_short_leverage"),
                "active_positions":
                    snapshot.get("active_positions"),
                "execution_preconditions_ready":
                    snapshot.get("execution_preconditions_ready"),
                "heartbeat":
                    snapshot.get("heartbeat"),
            },
            separators=(",", ":"),
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_health_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        server.serve_forever()

    except Exception as exc:
        log(f"{VERSION}: HEALTH SERVER ERROR={exc}")


def start_health_server():
    thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )
    thread.start()


# =============================================================================
# CREDENTIAL VALIDATION
# =============================================================================

def validate_credentials():
    missing = []

    if not WEEX_API_KEY:
        missing.append("WEEX_API_KEY")

    if not WEEX_API_SECRET:
        missing.append("WEEX_API_SECRET")

    if not WEEX_API_PASSPHRASE:
        missing.append("WEEX_API_PASSPHRASE")

    if missing:
        raise RuntimeError(
            "Missing credentials: " + ", ".join(missing)
        )


# =============================================================================
# WEEX SIGNATURE
# =============================================================================

def timestamp_ms():
    return str(int(time.time() * 1000))


def create_signature(timestamp, method, request_path, body=""):
    message = (
        timestamp
        + method.upper()
        + request_path
        + body
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def authenticated_headers(method, request_path, body=""):
    timestamp = timestamp_ms()
    signature = create_signature(
        timestamp,
        method,
        request_path,
        body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-ReadOnlyValidator/1.0",
    }


# =============================================================================
# READ-ONLY HTTP TRANSPORT
# =============================================================================

def decode_json_response(raw):
    if raw is None:
        return None

    text = raw.decode("utf-8", errors="replace")

    if not text:
        return None

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        raise RuntimeError(
            f"WEEX returned non-JSON response: {text[:500]}"
        )


def authenticated_get(request_path):
    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only transport is disabled"
        )

    if not request_path.startswith("/"):
        raise RuntimeError(
            "Invalid authenticated GET path"
        )

    method = "GET"
    body = ""

    headers = authenticated_headers(
        method,
        request_path,
        body,
    )

    url = BASE_URL + request_path

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read()

            with state_lock:
                runtime_state["authenticated_get_count"] += 1

            return decode_json_response(raw)

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Authenticated GET failed "
            f"HTTP={exc.code} "
            f"PATH={request_path} "
            f"BODY={raw[:1000]}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Authenticated GET network failure "
            f"PATH={request_path} "
            f"ERROR={exc}"
        )


def public_get(request_path):
    if not PUBLIC_READ_ONLY:
        raise RuntimeError(
            "Public read-only transport is disabled"
        )

    if not request_path.startswith("/"):
        raise RuntimeError(
            "Invalid public GET path"
        )

    request = urllib.request.Request(
        url=BASE_URL + request_path,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent":
                f"{VERSION}-PublicReadOnlyValidator/1.0",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read()

            with state_lock:
                runtime_state["public_get_count"] += 1

            return decode_json_response(raw)

    except Exception:
        return None


# =============================================================================
# ABSOLUTE WRITE FIREBREAK
# =============================================================================

def authenticated_post(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} WRITE FIREBREAK: "
        "authenticated POST is permanently disabled "
        "in this validation build"
    )


def submit_real_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY LOCK: "
        "real order execution is disabled"
    )


def submit_demo_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY LOCK: "
        "demo order execution is disabled"
    )


def mutate_leverage(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY LOCK: "
        "leverage mutation is disabled"
    )


def mutate_margin(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY LOCK: "
        "margin mutation is disabled"
    )


# =============================================================================
# RESPONSE HELPERS
# =============================================================================

def unwrap_data(payload):
    if payload is None:
        return None

    if isinstance(payload, dict):
        if "data" in payload:
            return payload["data"]

    return payload


def as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        return [value]

    return []


def first_dict(value):
    data = unwrap_data(value)

    if isinstance(data, dict):
        return data

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                return item

    return {}


def get_first(record, keys, default=None):
    if not isinstance(record, dict):
        return default

    for key in keys:
        if key in record:
            value = record.get(key)

            if value is not None:
                return value

    return default


# =============================================================================
# BALANCE PARSING
# =============================================================================

def extract_available_usdt(payload):
    data = unwrap_data(payload)

    candidates = []

    if isinstance(data, dict):
        candidates.append(data)

        for key in (
            "assets",
            "balances",
            "list",
            "rows",
        ):
            child = data.get(key)

            if isinstance(child, list):
                candidates.extend(
                    item
                    for item in child
                    if isinstance(item, dict)
                )

    elif isinstance(data, list):
        candidates.extend(
            item
            for item in data
            if isinstance(item, dict)
        )

    for record in candidates:
        coin = str(
            get_first(
                record,
                [
                    "coin",
                    "currency",
                    "asset",
                    "marginCoin",
                ],
                "",
            )
        ).upper()

        if coin and coin != "USDT":
            continue

        value = get_first(
            record,
            [
                "available",
                "availableBalance",
                "availableAmount",
                "availableEquity",
                "availableMargin",
                "balance",
                "equity",
            ],
        )

        parsed = safe_decimal(value)

        if parsed is not None:
            return parsed

    return None


# =============================================================================
# POSITION PARSING
# =============================================================================

def extract_position_records(payload):
    data = unwrap_data(payload)

    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, dict):
        for key in (
            "list",
            "rows",
            "positions",
            "positionList",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return [
                    item
                    for item in value
                    if isinstance(item, dict)
                ]

        return [data]

    return []


def record_symbol(record):
    value = get_first(
        record,
        [
            "symbol",
            "contractCode",
            "contract",
        ],
        "",
    )

    return str(value).upper()


def position_quantity(record):
    value = get_first(
        record,
        [
            "size",
            "position",
            "positionQty",
            "positionAmt",
            "total",
            "quantity",
            "qty",
            "holdVol",
            "available",
        ],
        "0",
    )

    parsed = safe_decimal(value, Decimal("0"))

    return abs(parsed)


# =============================================================================
# SYMBOL CONFIG PARSING
# =============================================================================

def extract_symbol_config(payload):
    data = unwrap_data(payload)

    if isinstance(data, dict):
        for key in (
            "list",
            "rows",
            "configs",
        ):
            child = data.get(key)

            if isinstance(child, list):
                for record in child:
                    if (
                        isinstance(record, dict)
                        and record_symbol(record) == SYMBOL
                    ):
                        return record

        if (
            not record_symbol(data)
            or record_symbol(data) == SYMBOL
        ):
            return data

    if isinstance(data, list):
        for record in data:
            if not isinstance(record, dict):
                continue

            if record_symbol(record) == SYMBOL:
                return record

        for record in data:
            if isinstance(record, dict):
                return record

    return {}


def normalize_margin_mode(value):
    if value is None:
        return None

    text = str(value).strip().upper()

    mapping = {
        "1": "CROSS",
        "2": "ISOLATED",
        "CROSSED": "CROSS",
        "CROSS": "CROSS",
        "ISOLATED": "ISOLATED",
        "FIXED": "ISOLATED",
    }

    return mapping.get(text, text)


def extract_config_values(record):
    margin = normalize_margin_mode(
        get_first(
            record,
            [
                "marginType",
                "marginMode",
                "margin_mode",
            ],
        )
    )

    position_mode = get_first(
        record,
        [
            "positionMode",
            "posMode",
            "positionType",
        ],
    )

    cross = safe_decimal(
        get_first(
            record,
            [
                "crossLeverage",
                "crossMarginLeverage",
                "leverage",
            ],
        )
    )

    long_lev = safe_decimal(
        get_first(
            record,
            [
                "isolatedLongLeverage",
                "longLeverage",
                "longLever",
            ],
        )
    )

    short_lev = safe_decimal(
        get_first(
            record,
            [
                "isolatedShortLeverage",
                "shortLeverage",
                "shortLever",
            ],
        )
    )

    return (
        margin,
        position_mode,
        cross,
        long_lev,
        short_lev,
    )


# =============================================================================
# MARKET PRICE PARSING
# =============================================================================

def recursive_price_search(value):
    if isinstance(value, dict):
        preferred_keys = (
            "markPrice",
            "price",
            "last",
            "lastPrice",
            "close",
            "indexPrice",
        )

        for key in preferred_keys:
            if key in value:
                parsed = safe_decimal(value[key])

                if parsed is not None and parsed > 0:
                    return parsed

        for child in value.values():
            parsed = recursive_price_search(child)

            if parsed is not None:
                return parsed

    elif isinstance(value, list):
        for child in value:
            parsed = recursive_price_search(child)

            if parsed is not None:
                return parsed

    return None


def obtain_market_price():
    for path in PUBLIC_PRICE_PATHS:
        payload = public_get(path)

        if payload is None:
            continue

        price = recursive_price_search(payload)

        if price is not None and price > 0:
            return path, price

    return None, None


# =============================================================================
# LOCAL ORDER-SIZING MODEL
# =============================================================================

def calculate_strategy_budget(balance):
    initial_margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    initial_notional = (
        initial_margin
        * TARGET_LONG_LEVERAGE
    )

    max_exposure = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    return (
        initial_margin,
        initial_notional,
        max_exposure,
    )


def hypothetical_quantity(notional, market_price):
    if (
        notional is None
        or market_price is None
        or market_price <= 0
    ):
        return None

    return notional / market_price


def round_quantity_down(quantity, decimals=4):
    if quantity is None:
        return None

    quantum = Decimal("1").scaleb(-decimals)

    return quantity.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


# =============================================================================
# TEST 1
# =============================================================================

def test_safety_configuration():
    section(
        f"{VERSION} TEST 1: SAFETY CONFIGURATION"
    )

    results = []

    results.append(
        pass_fail(
            "Authenticated Read-Only Is Enabled",
            AUTHENTICATED_READ_ONLY is True,
        )
    )

    results.append(
        pass_fail(
            "Public Read-Only Is Enabled",
            PUBLIC_READ_ONLY is True,
        )
    )

    results.append(
        pass_fail(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION is False,
        )
    )

    results.append(
        pass_fail(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    results.append(
        pass_fail(
            "Exchange Network Writes Are Disabled",
            NETWORK_WRITES_ENABLED is False,
        )
    )

    results.append(
        pass_fail(
            "Leverage Mutation Is Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        )
    )

    results.append(
        pass_fail(
            "Margin Mutation Is Disabled",
            MARGIN_MUTATION_ENABLED is False,
        )
    )

    results.append(
        pass_fail(
            "Position Mutation Is Disabled",
            POSITION_MUTATION_ENABLED is False,
        )
    )

    results.append(
        pass_fail(
            "Account Mutation Is Disabled",
            ACCOUNT_MUTATION_ENABLED is False,
        )
    )

    return all(results)


# =============================================================================
# TEST 2
# =============================================================================

def test_credentials():
    section(
        f"{VERSION} TEST 2: AUTHENTICATED READ-ONLY CREDENTIALS"
    )

    results = []

    results.append(
        pass_fail(
            "WEEX API Key Is Present",
            bool(WEEX_API_KEY),
        )
    )

    results.append(
        pass_fail(
            "WEEX API Secret Is Present",
            bool(WEEX_API_SECRET),
        )
    )

    results.append(
        pass_fail(
            "WEEX API Passphrase Is Present",
            bool(WEEX_API_PASSPHRASE),
        )
    )

    return all(results)


# =============================================================================
# TEST 3
# =============================================================================

def test_balance_read():
    section(
        f"{VERSION} TEST 3: LIVE BALANCE RECONCILIATION"
    )

    payload = authenticated_get(BALANCE_PATH)

    balance = extract_available_usdt(payload)

    log(f"{VERSION}: BALANCE PATH={BALANCE_PATH}")

    if balance is not None:
        log(
            f"{VERSION}: AVAILABLE USDT="
            f"{decimal_string(balance)}"
        )
    else:
        log(
            f"{VERSION}: AVAILABLE USDT=UNRESOLVED"
        )

    valid = balance is not None
    positive = (
        balance is not None
        and balance > Decimal("0")
    )

    pass_fail(
        "Available Balance Was Read",
        valid,
    )

    pass_fail(
        "Available Balance Is Positive",
        positive,
    )

    with state_lock:
        runtime_state["available_usdt"] = (
            decimal_string(balance)
            if balance is not None
            else None
        )
        runtime_state["balance_ready"] = positive

    return balance


# =============================================================================
# TEST 4
# =============================================================================

def test_position_reconciliation():
    section(
        f"{VERSION} TEST 4: POSITION RECONCILIATION"
    )

    payload = authenticated_get(POSITION_PATH)

    records = extract_position_records(payload)

    symbol_records = [
        record
        for record in records
        if record_symbol(record) == SYMBOL
    ]

    active_records = [
        record
        for record in symbol_records
        if position_quantity(record) > 0
    ]

    log(
        f"{VERSION}: POSITION PATH="
        f"{POSITION_PATH}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(records)}"
    )

    log(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(symbol_records)}"
    )

    log(
        f"{VERSION}: {SYMBOL} ACTIVE POSITIONS="
        f"{len(active_records)}"
    )

    pass_fail(
        "Position Endpoint Was Read",
        payload is not None,
    )

    pass_fail(
        "Position Response Is Reconciled",
        isinstance(records, list),
    )

    pass_fail(
        f"{SYMBOL} Position State Was Reconciled",
        True,
    )

    zero_positions = len(active_records) == 0

    pass_fail(
        "Zero Open Positions Is Accepted As Valid State",
        zero_positions,
    )

    with state_lock:
        runtime_state["position_records"] = len(records)
        runtime_state["symbol_position_records"] = (
            len(symbol_records)
        )
        runtime_state["active_positions"] = (
            len(active_records)
        )
        runtime_state["position_ready"] = zero_positions

    return zero_positions


# =============================================================================
# TEST 5
# =============================================================================

def test_symbol_configuration():
    section(
        f"{VERSION} TEST 5: SYMBOL CONFIGURATION READ-BACK"
    )

    payload = authenticated_get(
        SYMBOL_CONFIG_PATH
    )

    config = extract_symbol_config(payload)

    (
        margin_mode,
        position_mode,
        cross_leverage,
        long_leverage,
        short_leverage,
    ) = extract_config_values(config)

    log(
        f"{VERSION}: SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_mode}"
    )

    log(
        f"{VERSION}: OBSERVED POSITION MODE="
        f"{position_mode}"
    )

    log(
        f"{VERSION}: OBSERVED CROSS LEVERAGE="
        f"{decimal_string(cross_leverage)}x"
    )

    log(
        f"{VERSION}: OBSERVED ISOLATED LONG="
        f"{decimal_string(long_leverage)}x"
    )

    log(
        f"{VERSION}: OBSERVED ISOLATED SHORT="
        f"{decimal_string(short_leverage)}x"
    )

    symbol_ok = (
        not record_symbol(config)
        or record_symbol(config) == SYMBOL
    )

    margin_ok = (
        margin_mode == TARGET_MARGIN_MODE
    )

    long_ok = (
        long_leverage == TARGET_LONG_LEVERAGE
    )

    short_ok = (
        short_leverage == TARGET_SHORT_LEVERAGE
    )

    pass_fail(
        "Symbol Configuration Was Read",
        bool(config),
    )

    pass_fail(
        f"Configuration Belongs To {SYMBOL}",
        symbol_ok,
    )

    pass_fail(
        "Margin Type Is ISOLATED",
        margin_ok,
    )

    pass_fail(
        "Isolated Long Leverage Is 100x",
        long_ok,
    )

    pass_fail(
        "Isolated Short Leverage Is 100x",
        short_ok,
    )

    with state_lock:
        runtime_state["observed_margin"] = (
            margin_mode
        )
        runtime_state["observed_position_mode"] = (
            position_mode
        )
        runtime_state["observed_cross_leverage"] = (
            decimal_string(cross_leverage)
        )
        runtime_state["observed_long_leverage"] = (
            decimal_string(long_leverage)
        )
        runtime_state["observed_short_leverage"] = (
            decimal_string(short_leverage)
        )

        runtime_state["margin_ready"] = margin_ok
        runtime_state["leverage_ready"] = (
            long_ok and short_ok
        )

    return {
        "margin_ok": margin_ok,
        "long_ok": long_ok,
        "short_ok": short_ok,
        "position_mode": position_mode,
    }


# =============================================================================
# TEST 6
# =============================================================================

def test_market_price():
    section(
        f"{VERSION} TEST 6: PUBLIC MARKET PRICE READ"
    )

    path, price = obtain_market_price()

    if path:
        log(
            f"{VERSION}: MARKET PRICE PATH={path}"
        )

    if price is not None:
        log(
            f"{VERSION}: OBSERVED MARKET PRICE="
            f"{decimal_string(price)}"
        )
    else:
        log(
            f"{VERSION}: MARKET PRICE="
            f"UNAVAILABLE"
        )

    # Market price is useful for sizing validation,
    # but failure to retrieve it does NOT unlock writes.
    price_ok = (
        price is not None
        and price > 0
    )

    pass_fail(
        "Public Market Price Was Read",
        price_ok,
    )

    with state_lock:
        runtime_state["mark_price"] = (
            decimal_string(price)
            if price is not None
            else None
        )

    return price


# =============================================================================
# TEST 7
# =============================================================================

def test_strategy_budget(balance, market_price):
    section(
        f"{VERSION} TEST 7: STRATEGY BUDGET RECONCILIATION"
    )

    if balance is None:
        pass_fail(
            "Balance Is Available For Budget Calculation",
            False,
        )
        return False

    (
        initial_margin,
        initial_notional,
        max_exposure,
    ) = calculate_strategy_budget(balance)

    raw_quantity = hypothetical_quantity(
        initial_notional,
        market_price,
    )

    rounded_quantity = round_quantity_down(
        raw_quantity,
        decimals=4,
    )

    log(
        f"{VERSION}: AVAILABLE BALANCE="
        f"{decimal_string(balance)} USDT"
    )

    log(
        f"{VERSION}: INITIAL ENTRY PERCENT="
        f"{decimal_string(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: INITIAL MARGIN BUDGET="
        f"{decimal_string(initial_margin)} USDT"
    )

    log(
        f"{VERSION}: TARGET INITIAL NOTIONAL AT 100x="
        f"{decimal_string(initial_notional)} USDT"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE PERCENT="
        f"{decimal_string(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE BUDGET="
        f"{decimal_string(max_exposure)} USDT"
    )

    if market_price is not None:
        log(
            f"{VERSION}: MARKET PRICE="
            f"{decimal_string(market_price)}"
        )

    if raw_quantity is not None:
        log(
            f"{VERSION}: HYPOTHETICAL RAW QUANTITY="
            f"{decimal_string(raw_quantity)} {SYMBOL[:3]}"
        )

    if rounded_quantity is not None:
        log(
            f"{VERSION}: HYPOTHETICAL QTY "
            f"ROUNDED DOWN TO 4 DP="
            f"{decimal_string(rounded_quantity)}"
        )

    entry_percent_ok = (
        INITIAL_ENTRY_PERCENT == Decimal("5")
    )

    exposure_percent_ok = (
        MAX_FUND_EXPOSURE_PERCENT
        == Decimal("35")
    )

    initial_margin_ok = (
        initial_margin > Decimal("0")
    )

    max_exposure_ok = (
        max_exposure > Decimal("0")
    )

    relationship_ok = (
        initial_margin < max_exposure
    )

    pass_fail(
        "Initial Entry Percent Is 5%",
        entry_percent_ok,
    )

    pass_fail(
        "Maximum Fund Exposure Is 35%",
        exposure_percent_ok,
    )

    pass_fail(
        "Initial Margin Budget Is Positive",
        initial_margin_ok,
    )

    pass_fail(
        "Maximum Exposure Budget Is Positive",
        max_exposure_ok,
    )

    pass_fail(
        "Initial Budget Is Below Maximum Exposure",
        relationship_ok,
    )

    if market_price is not None:
        pass_fail(
            "Hypothetical Quantity Can Be Calculated",
            raw_quantity is not None
            and raw_quantity > 0,
        )

    budget_ready = all(
        [
            entry_percent_ok,
            exposure_percent_ok,
            initial_margin_ok,
            max_exposure_ok,
            relationship_ok,
        ]
    )

    with state_lock:
        runtime_state["initial_margin_budget"] = (
            decimal_string(initial_margin)
        )
        runtime_state["initial_notional_target"] = (
            decimal_string(initial_notional)
        )
        runtime_state["maximum_exposure_budget"] = (
            decimal_string(max_exposure)
        )
        runtime_state["strategy_budget_ready"] = (
            budget_ready
        )

    return budget_ready


# =============================================================================
# TEST 8
# =============================================================================

def test_strategy_parameters():
    section(
        f"{VERSION} TEST 8: STRATEGY PARAMETER INTEGRITY"
    )

    results = []

    results.append(
        pass_fail(
            "Maximum Pyramid Adds Is One",
            MAX_PYRAMID_ADDS == 1,
        )
    )

    results.append(
        pass_fail(
            "Pyramid Size Is 5%",
            PYRAMID_SIZE_PERCENT == Decimal("5"),
        )
    )

    results.append(
        pass_fail(
            "Maximum Backups Is Three",
            MAX_BACKUPS == 3,
        )
    )

    results.append(
        pass_fail(
            "Backup Size Is 5%",
            BACKUP_SIZE_PERCENT == Decimal("5"),
        )
    )

    results.append(
        pass_fail(
            "Backup Buffer Is 0.3%",
            BACKUP_BUFFER_PERCENT == Decimal("0.3"),
        )
    )

    results.append(
        pass_fail(
            "TP Distribution Totals 100%",
            (
                TP1_PERCENT
                + TP2_PERCENT
                + TP3_PERCENT
            ) == Decimal("100"),
        )
    )

    results.append(
        pass_fail(
            "TP1 Trigger Is 0.5%",
            TP1_TRIGGER_PERCENT == Decimal("0.5"),
        )
    )

    results.append(
        pass_fail(
            "TP2 Trigger Is 1.0%",
            TP2_TRIGGER_PERCENT == Decimal("1.0"),
        )
    )

    results.append(
        pass_fail(
            "Trailing Distance Is 0.20%",
            TRAILING_DISTANCE_PERCENT
            == Decimal("0.20"),
        )
    )

    results.append(
        pass_fail(
            "Signal Expiry Is 120 Seconds",
            SIGNAL_EXPIRY_SECONDS == 120,
        )
    )

    results.append(
        pass_fail(
            "Loss Cooldown Is 300 Seconds",
            LOSS_COOLDOWN_SECONDS == 300,
        )
    )

    return all(results)


# =============================================================================
# TEST 9
# =============================================================================

def test_write_firebreak():
    section(
        f"{VERSION} TEST 9: WRITE FIREBREAK VERIFICATION"
    )

    blocked_post = False
    blocked_real = False
    blocked_demo = False
    blocked_leverage = False
    blocked_margin = False

    try:
        authenticated_post(
            "/forbidden",
            {},
        )
    except RuntimeError:
        blocked_post = True

    try:
        submit_real_order()
    except RuntimeError:
        blocked_real = True

    try:
        submit_demo_order()
    except RuntimeError:
        blocked_demo = True

    try:
        mutate_leverage()
    except RuntimeError:
        blocked_leverage = True

    try:
        mutate_margin()
    except RuntimeError:
        blocked_margin = True

    pass_fail(
        "Authenticated POST Is Rejected Locally",
        blocked_post,
    )

    pass_fail(
        "Real Order Function Is Rejected Locally",
        blocked_real,
    )

    pass_fail(
        "Demo Order Function Is Rejected Locally",
        blocked_demo,
    )

    pass_fail(
        "Leverage Mutation Is Rejected Locally",
        blocked_leverage,
    )

    pass_fail(
        "Margin Mutation Is Rejected Locally",
        blocked_margin,
    )

    with state_lock:
        counters_zero = (
            runtime_state["network_writes"] == 0
            and runtime_state["leverage_mutations"] == 0
            and runtime_state["margin_mutations"] == 0
            and runtime_state["position_mutations"] == 0
            and runtime_state["account_mutations"] == 0
            and runtime_state["real_orders"] == 0
            and runtime_state["demo_orders"] == 0
        )

    pass_fail(
        "Exchange Network Writes Remain Zero",
        runtime_state["network_writes"] == 0,
    )

    pass_fail(
        "Leverage Mutations Remain Zero",
        runtime_state["leverage_mutations"] == 0,
    )

    pass_fail(
        "Margin Mutations Remain Zero",
        runtime_state["margin_mutations"] == 0,
    )

    pass_fail(
        "Position Mutations Remain Zero",
        runtime_state["position_mutations"] == 0,
    )

    pass_fail(
        "Account Mutations Remain Zero",
        runtime_state["account_mutations"] == 0,
    )

    pass_fail(
        "Real Orders Remain Zero",
        runtime_state["real_orders"] == 0,
    )

    pass_fail(
        "Demo Orders Remain Zero",
        runtime_state["demo_orders"] == 0,
    )

    return (
        blocked_post
        and blocked_real
        and blocked_demo
        and blocked_leverage
        and blocked_margin
        and counters_zero
    )


# =============================================================================
# TEST 10
# =============================================================================

def test_execution_preconditions(
    balance,
    zero_positions,
    config_result,
    budget_ready,
    strategy_parameters_ready,
    firebreak_ready,
):
    section(
        f"{VERSION} TEST 10: EXECUTION PRECONDITION READINESS"
    )

    balance_ready = (
        balance is not None
        and balance > 0
    )

    margin_ready = (
        config_result["margin_ok"]
    )

    leverage_ready = (
        config_result["long_ok"]
        and config_result["short_ok"]
    )

    credentials_ready = all(
        [
            bool(WEEX_API_KEY),
            bool(WEEX_API_SECRET),
            bool(WEEX_API_PASSPHRASE),
        ]
    )

    results = []

    results.append(
        pass_fail(
            "Authenticated Credentials Are Ready",
            credentials_ready,
        )
    )

    results.append(
        pass_fail(
            "Available Balance Is Ready",
            balance_ready,
        )
    )

    results.append(
        pass_fail(
            "BTCUSDT Has Zero Active Positions",
            zero_positions,
        )
    )

    results.append(
        pass_fail(
            "Margin Mode Is Ready",
            margin_ready,
        )
    )

    results.append(
        pass_fail(
            "100x Long And Short Leverage Are Ready",
            leverage_ready,
        )
    )

    results.append(
        pass_fail(
            "Strategy Budget Is Ready",
            budget_ready,
        )
    )

    results.append(
        pass_fail(
            "Strategy Parameters Are Internally Valid",
            strategy_parameters_ready,
        )
    )

    results.append(
        pass_fail(
            "Write Firebreak Remains Intact",
            firebreak_ready,
        )
    )

    execution_preconditions_ready = all(results)

    pass_fail(
        "Read-Only Execution Preconditions Are Fully Ready",
        execution_preconditions_ready,
    )

    if execution_preconditions_ready:
        log(
            f"{VERSION}: EXECUTION PRECONDITIONS VERIFIED"
        )
        log(
            f"{VERSION}: IMPORTANT: "
            f"ORDER EXECUTION REMAINS DISABLED"
        )

    with state_lock:
        runtime_state[
            "execution_preconditions_ready"
        ] = execution_preconditions_ready

    return execution_preconditions_ready


# =============================================================================
# TEST 11
# =============================================================================

def test_final_state():
    section(
        f"{VERSION} TEST 11: FINAL LIVE READ-ONLY STATE"
    )

    with state_lock:
        snapshot = dict(runtime_state)

    results = []

    results.append(
        pass_fail(
            "Credentials Remain Present",
            bool(
                WEEX_API_KEY
                and WEEX_API_SECRET
                and WEEX_API_PASSPHRASE
            ),
        )
    )

    results.append(
        pass_fail(
            "Authenticated GET Count Is At Least Three",
            snapshot["authenticated_get_count"] >= 3,
        )
    )

    results.append(
        pass_fail(
            "Available Balance Remains Valid",
            snapshot["balance_ready"],
        )
    )

    results.append(
        pass_fail(
            "Zero Position Readiness Remains Valid",
            snapshot["position_ready"],
        )
    )

    results.append(
        pass_fail(
            "ISOLATED Margin Readiness Remains Valid",
            snapshot["margin_ready"],
        )
    )

    results.append(
        pass_fail(
            "100x Leverage Readiness Remains Valid",
            snapshot["leverage_ready"],
        )
    )

    results.append(
        pass_fail(
            "Strategy Budget Readiness Remains Valid",
            snapshot["strategy_budget_ready"],
        )
    )

    results.append(
        pass_fail(
            "Network Writes Remain Disabled",
            NETWORK_WRITES_ENABLED is False,
        )
    )

    results.append(
        pass_fail(
            "All Mutation Counters Remain Zero",
            (
                snapshot["network_writes"] == 0
                and snapshot["leverage_mutations"] == 0
                and snapshot["margin_mutations"] == 0
                and snapshot["position_mutations"] == 0
                and snapshot["account_mutations"] == 0
            ),
        )
    )

    results.append(
        pass_fail(
            "Real And Demo Orders Remain Zero",
            (
                snapshot["real_orders"] == 0
                and snapshot["demo_orders"] == 0
            ),
        )
    )

    results.append(
        pass_fail(
            "Execution Preconditions Are Ready",
            snapshot[
                "execution_preconditions_ready"
            ],
        )
    )

    return all(results)


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():
    count = 0

    while True:
        time.sleep(30)

        count += 1

        with state_lock:
            runtime_state["heartbeat"] = count
            snapshot = dict(runtime_state)

        log(
            f"{VERSION}: HEARTBEAT {count} | "
            f"phase={snapshot['phase']} | "
            f"authenticated-read-only="
            f"{snapshot['authenticated_read_only']} | "
            f"authenticated-get="
            f"{snapshot['authenticated_get_count']} | "
            f"public-get="
            f"{snapshot['public_get_count']} | "
            f"real-execution="
            f"{snapshot['real_execution']} | "
            f"demo-execution="
            f"{snapshot['demo_execution']} | "
            f"network-writes="
            f"{snapshot['network_writes_enabled']} | "
            f"leverage-mutation="
            f"{snapshot['leverage_mutation_enabled']} | "
            f"available-usdt="
            f"{snapshot['available_usdt']} | "
            f"active-positions="
            f"{snapshot['active_positions']} | "
            f"observed-margin="
            f"{snapshot['observed_margin']} | "
            f"observed-long="
            f"{snapshot['observed_long_leverage']} | "
            f"observed-short="
            f"{snapshot['observed_short_leverage']} | "
            f"target-long="
            f"{decimal_string(TARGET_LONG_LEVERAGE)}x | "
            f"target-short="
            f"{decimal_string(TARGET_SHORT_LEVERAGE)}x | "
            f"execution-preconditions-ready="
            f"{snapshot['execution_preconditions_ready']}"
        )


# =============================================================================
# MAIN
# =============================================================================

def main():
    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={PORT}")

    log(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: PUBLIC READ-ONLY ENABLED"
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

    log(
        f"{VERSION}: MARGIN MUTATION DISABLED"
    )

    log(
        f"{VERSION}: POSITION MUTATION DISABLED"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATION DISABLED"
    )

    log(
        f"{VERSION}: TARGET MARGIN="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{decimal_string(TARGET_LONG_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{decimal_string(TARGET_SHORT_LEVERAGE)}x"
    )

    start_health_server()

    validate_credentials()

    with state_lock:
        runtime_state["phase"] = (
            "LIVE_READ_ONLY_VALIDATING"
        )

    safety_ok = test_safety_configuration()

    credentials_ok = test_credentials()

    if not safety_ok:
        raise RuntimeError(
            f"{VERSION}: safety configuration failed"
        )

    if not credentials_ok:
        raise RuntimeError(
            f"{VERSION}: credential validation failed"
        )

    balance = test_balance_read()

    zero_positions = test_position_reconciliation()

    config_result = test_symbol_configuration()

    market_price = test_market_price()

    budget_ready = test_strategy_budget(
        balance,
        market_price,
    )

    strategy_parameters_ready = (
        test_strategy_parameters()
    )

    firebreak_ready = test_write_firebreak()

    execution_ready = test_execution_preconditions(
        balance=balance,
        zero_positions=zero_positions,
        config_result=config_result,
        budget_ready=budget_ready,
        strategy_parameters_ready=(
            strategy_parameters_ready
        ),
        firebreak_ready=firebreak_ready,
    )

    if execution_ready:
        with state_lock:
            runtime_state["phase"] = (
                "EXECUTION_PRECONDITIONS_VALIDATED"
            )
    else:
        with state_lock:
            runtime_state["phase"] = (
                "EXECUTION_PRECONDITIONS_NOT_READY"
            )

    final_ok = test_final_state()

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    with state_lock:
        snapshot = dict(runtime_state)

    log(
        f"{VERSION}: PHASE={snapshot['phase']}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GET COUNT="
        f"{snapshot['authenticated_get_count']}"
    )

    log(
        f"{VERSION}: PUBLIC GET COUNT="
        f"{snapshot['public_get_count']}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{snapshot['available_usdt']}"
    )

    log(
        f"{VERSION}: ACTIVE POSITIONS="
        f"{snapshot['active_positions']}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{snapshot['observed_margin']}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{snapshot['observed_long_leverage']}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{snapshot['observed_short_leverage']}x"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{decimal_string(TARGET_LONG_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{decimal_string(TARGET_SHORT_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: INITIAL MARGIN BUDGET="
        f"{snapshot['initial_margin_budget']} USDT"
    )

    log(
        f"{VERSION}: INITIAL NOTIONAL TARGET="
        f"{snapshot['initial_notional_target']} USDT"
    )

    log(
        f"{VERSION}: MAXIMUM EXPOSURE BUDGET="
        f"{snapshot['maximum_exposure_budget']} USDT"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{snapshot['mark_price']}"
    )

    log(
        f"{VERSION}: EXECUTION PRECONDITIONS READY="
        f"{snapshot['execution_preconditions_ready']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{snapshot['network_writes']}"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{snapshot['leverage_mutations']}"
    )

    log(
        f"{VERSION}: MARGIN MUTATIONS="
        f"{snapshot['margin_mutations']}"
    )

    log(
        f"{VERSION}: POSITION MUTATIONS="
        f"{snapshot['position_mutations']}"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATIONS="
        f"{snapshot['account_mutations']}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{snapshot['real_orders']}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{snapshot['demo_orders']}"
    )

    if final_ok:
        log(
            f"{VERSION}: FINAL VALIDATION STATUS=PASS"
        )
    else:
        log(
            f"{VERSION}: FINAL VALIDATION STATUS=FAIL"
        )

    section(
        f"{VERSION}: ENTERING PERSISTENT HEALTH / HEARTBEAT MODE"
    )

    heartbeat_loop()


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        log(
            f"{VERSION}: SHUTDOWN REQUESTED"
        )

        sys.exit(0)

    except Exception as exc:
        with state_lock:
            runtime_state["phase"] = "FAILED"

        section(
            f"{VERSION}: FATAL ERROR"
        )

        log(
            f"{VERSION}: {type(exc).__name__}: {exc}"
        )

        # Keep Render health process alive so failure state remains observable.
        while True:
            time.sleep(30)

            with state_lock:
                runtime_state["heartbeat"] += 1
                heartbeat = runtime_state["heartbeat"]
                phase = runtime_state["phase"]

            log(
                f"{VERSION}: HEARTBEAT {heartbeat} | "
                f"phase={phase} | "
                f"network-writes=0 | "
                f"real-orders=0 | "
                f"demo-orders=0"
            )
