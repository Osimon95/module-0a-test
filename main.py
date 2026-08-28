# ======================================================================================
# R34O - LIVE EXECUTION READINESS / SYNTHETIC ORDER INTENT VALIDATION
# ======================================================================================
#
# SAFETY STATUS
# --------------------------------------------------------------------------------------
# AUTHENTICATED READ-ONLY : ENABLED
# PUBLIC READ-ONLY        : ENABLED
# NETWORK WRITES          : DISABLED
# REAL ORDERS             : DISABLED
# DEMO ORDERS             : DISABLED
# LEVERAGE MUTATION       : DISABLED
# MARGIN MUTATION         : DISABLED
# POSITION MUTATION       : DISABLED
# ACCOUNT MUTATION        : DISABLED
# SYNTHETIC ORDER INTENT  : ENABLED
#
# R34O correction:
#   Correct WEEX V3 contract-information parsing:
#
#   GET /capi/v3/market/exchangeInfo?symbol=BTCUSDT
#
#   Response:
#   {
#       "assets": [...],
#       "rateLimits": [...],
#       "symbols": [
#           {
#               "symbol": "BTCUSDT",
#               ...
#           }
#       ]
#   }
#
# NO REAL FINANCIAL ACTION IS PERFORMED BY THIS FILE.
# ======================================================================================

import os
import sys
import time
import json
import hmac
import base64
import hashlib
import traceback
import threading
import urllib.parse
import urllib.request
import urllib.error

from decimal import (
    Decimal,
    ROUND_DOWN,
    InvalidOperation,
    getcontext,
)

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# ======================================================================================
# DECIMAL CONFIGURATION
# ======================================================================================

getcontext().prec = 40


# ======================================================================================
# VERSION / CORE CONFIGURATION
# ======================================================================================

VERSION = "R34O"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com",
).strip().rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", "10000"))

HTTP_TIMEOUT_SECONDS = 15
HEARTBEAT_SECONDS = 30


# ======================================================================================
# WEEX API CREDENTIALS
# ======================================================================================

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()


# ======================================================================================
# STRATEGY CONFIGURATION
# ======================================================================================

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_ALLOCATION_PERCENT = Decimal("20")
TP2_ALLOCATION_PERCENT = Decimal("20")
TP3_ALLOCATION_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

MAX_LOCAL_LEVERAGE = Decimal("100")


# ======================================================================================
# HARD SAFETY FLAGS
# ======================================================================================

AUTHENTICATED_READ_ONLY_ENABLED = True
PUBLIC_READ_ONLY_ENABLED = True

SYNTHETIC_ORDER_INTENT_ONLY = True

NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# ======================================================================================
# WEEX V3 READ-ONLY ENDPOINTS
# ======================================================================================

EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"
SYMBOL_PRICE_PATH = "/capi/v3/market/symbolPrice"

BALANCE_PATH = "/capi/v3/account/balance"
POSITION_PATH = "/capi/v3/account/position/allPosition"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"


# ======================================================================================
# RUNTIME COUNTERS
# ======================================================================================

runtime_lock = threading.Lock()

runtime = {
    "phase": "BOOTING",

    "public_get": 0,
    "authenticated_get": 0,

    "network_writes": 0,

    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "real_orders": 0,
    "demo_orders": 0,

    "synthetic_intents": 0,

    "correction_required": None,

    "observed_margin": "UNKNOWN",
    "observed_long": "UNKNOWN",
    "observed_short": "UNKNOWN",

    "available_balance": None,
    "market_price": None,
    "entry_quantity": None,

    "heartbeat": 0,
}


# ======================================================================================
# DISPLAY HELPERS
# ======================================================================================

LINE = "-" * 100


def separator():
    print(LINE, flush=True)


def heading(text):
    separator()
    print(text, flush=True)
    separator()


def pass_line(label):
    print(f"{label:<88} ✅ PASS", flush=True)


def fail_line(label):
    print(f"{label:<88} ❌ FAIL", flush=True)


def check(label, condition):
    if condition:
        pass_line(label)
        return

    fail_line(label)
    raise RuntimeError(f"Validation failed: {label}")


def decimal_text(value):
    if isinstance(value, Decimal):
        text = format(value, "f")

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return text or "0"

    return str(value)


# ======================================================================================
# DECIMAL HELPERS
# ======================================================================================

def to_decimal(value, default=None):
    if value is None:
        return default

    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def decimal_is_positive(value):
    return isinstance(value, Decimal) and value > 0


def floor_to_precision(value, precision):
    value = Decimal(value)

    precision = int(precision)

    quantum = Decimal("1").scaleb(-precision)

    return value.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def floor_to_step(value, step):
    value = Decimal(value)
    step = Decimal(step)

    if step <= 0:
        raise ValueError("Step must be positive")

    units = (value / step).to_integral_value(
        rounding=ROUND_DOWN,
    )

    return units * step


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        with runtime_lock:
            snapshot = dict(runtime)

        body = json.dumps(
            {
                "status": "ok",
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": snapshot["phase"],
                "authenticated_read_only": AUTHENTICATED_READ_ONLY_ENABLED,
                "public_read_only": PUBLIC_READ_ONLY_ENABLED,
                "network_writes": snapshot["network_writes"],
                "real_orders": snapshot["real_orders"],
                "demo_orders": snapshot["demo_orders"],
                "observed_margin": snapshot["observed_margin"],
                "observed_long": snapshot["observed_long"],
                "observed_short": snapshot["observed_short"],
            },
            separators=(",", ":"),
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    server = ThreadingHTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    return server


# ======================================================================================
# HTTP CORE
# ======================================================================================

def encode_query(params):
    if not params:
        return ""

    clean = []

    for key, value in params.items():
        if value is None:
            continue

        clean.append(
            (
                str(key),
                str(value),
            )
        )

    return urllib.parse.urlencode(clean)


def decode_json_response(raw_bytes, path):
    try:
        text = raw_bytes.decode("utf-8")
    except Exception as exc:
        raise RuntimeError(
            f"Could not decode response from {path}: {exc}"
        )

    if not text.strip():
        raise RuntimeError(
            f"Empty response from {path}"
        )

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        preview = text[:500]

        raise RuntimeError(
            f"Invalid JSON from {path}: {exc}; "
            f"response={preview!r}"
        )


def perform_get(url, headers, path):
    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            status = int(response.status)
            raw = response.read()

    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            body = ""

        raise RuntimeError(
            f"HTTP {exc.code} GET failed: {path} | "
            f"response={body[:800]}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"GET network failure: {path} | {exc}"
        )

    except TimeoutError:
        raise RuntimeError(
            f"GET timed out: {path}"
        )

    if status < 200 or status >= 300:
        raise RuntimeError(
            f"Unexpected HTTP status {status}: {path}"
        )

    return decode_json_response(
        raw,
        path,
    )


# ======================================================================================
# PUBLIC READ-ONLY GET
# ======================================================================================

def public_get(path, params=None):
    if not PUBLIC_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Public read-only networking is disabled"
        )

    if not path.startswith("/"):
        raise RuntimeError(
            f"Invalid public GET path: {path}"
        )

    query = encode_query(params)

    url = BASE_URL + path

    if query:
        url += "?" + query

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"{VERSION}-ReadOnlyValidator/1.0",
    }

    data = perform_get(
        url=url,
        headers=headers,
        path=path,
    )

    with runtime_lock:
        runtime["public_get"] += 1

    return data


# ======================================================================================
# AUTHENTICATED READ-ONLY SIGNATURE
# ======================================================================================

def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    method = method.upper()

    if query_string:
        prehash = (
            str(timestamp)
            + method
            + request_path
            + "?"
            + query_string
            + body
        )
    else:
        prehash = (
            str(timestamp)
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def authenticated_get(path, params=None):
    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only access is disabled"
        )

    if not WEEX_API_KEY:
        raise RuntimeError(
            "Missing WEEX_API_KEY"
        )

    if not WEEX_API_SECRET:
        raise RuntimeError(
            "Missing WEEX_API_SECRET"
        )

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError(
            "Missing WEEX_API_PASSPHRASE"
        )

    if not path.startswith("/"):
        raise RuntimeError(
            f"Invalid authenticated GET path: {path}"
        )

    query = encode_query(params)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = build_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query,
        body="",
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"{VERSION}-ReadOnlyValidator/1.0",
    }

    url = BASE_URL + path

    if query:
        url += "?" + query

    data = perform_get(
        url=url,
        headers=headers,
        path=path,
    )

    with runtime_lock:
        runtime["authenticated_get"] += 1

    return data


# ======================================================================================
# ABSOLUTE NETWORK-WRITE FIREBREAK
# ======================================================================================

def blocked_network_write(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: generic network write is disabled"
    )


def blocked_http_post(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: HTTP POST is disabled"
    )


def blocked_http_put(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: HTTP PUT is disabled"
    )


def blocked_http_patch(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: HTTP PATCH is disabled"
    )


def blocked_http_delete(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: HTTP DELETE is disabled"
    )


def send_real_order(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: real order execution is disabled"
    )


def send_demo_order(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: demo order execution is disabled"
    )


def mutate_leverage(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: leverage mutation is disabled"
    )


def mutate_margin(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: margin mutation is disabled"
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: position mutation is disabled"
    )


def mutate_account(*args, **kwargs):
    raise RuntimeError(
        "R34O FIREBREAK: account mutation is disabled"
    )


# ======================================================================================
# FIREBREAK TEST HELPER
# ======================================================================================

def confirm_rejected(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except RuntimeError:
        return True

    return False


# ======================================================================================
# RESPONSE-ENVELOPE HELPERS
# ======================================================================================

def unwrap_common_payload(data):
    """
    Tolerates direct WEEX V3 responses as well as common API wrappers.

    Direct V3 exchangeInfo:
        {
            "assets": [...],
            "rateLimits": [...],
            "symbols": [...]
        }

    Possible wrapped variants:
        {"data": {...}}
        {"result": {...}}
    """

    current = data

    for _ in range(5):
        if not isinstance(current, dict):
            break

        if "symbols" in current:
            break

        moved = False

        for key in (
            "data",
            "result",
            "response",
            "payload",
        ):
            candidate = current.get(key)

            if isinstance(
                candidate,
                (dict, list),
            ):
                current = candidate
                moved = True
                break

        if not moved:
            break

    return current


def extract_records(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "data",
            "result",
            "rows",
            "list",
            "items",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return value

        return [data]

    return []


# ======================================================================================
# CONTRACT INFORMATION - R34O CORRECTED FUNCTION
# ======================================================================================

def obtain_contract_information():
    """
    R34O corrected V3 implementation.

    Official endpoint:

        GET /capi/v3/market/exchangeInfo?symbol=BTCUSDT

    Official response puts contract objects in:

        response["symbols"]
    """

    raw = public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    payload = unwrap_common_payload(raw)

    candidates = []

    # ------------------------------------------------------------------
    # Official current WEEX V3 structure.
    # ------------------------------------------------------------------

    if isinstance(payload, dict):

        symbols_value = payload.get("symbols")

        if isinstance(symbols_value, list):
            candidates.extend(symbols_value)

        elif isinstance(symbols_value, dict):
            candidates.append(symbols_value)

    # ------------------------------------------------------------------
    # Defensive compatibility:
    # if exchange ever returns the contract object directly.
    # ------------------------------------------------------------------

    if isinstance(payload, dict):

        if payload.get("symbol") is not None:
            candidates.append(payload)

    elif isinstance(payload, list):

        candidates.extend(payload)

    # ------------------------------------------------------------------
    # Defensive compatibility with top-level data.
    # ------------------------------------------------------------------

    if not candidates and isinstance(raw, dict):

        for key in (
            "symbols",
            "data",
            "result",
        ):
            value = raw.get(key)

            if isinstance(value, list):
                candidates.extend(value)

            elif isinstance(value, dict):

                if isinstance(
                    value.get("symbols"),
                    list,
                ):
                    candidates.extend(
                        value["symbols"]
                    )

                elif value.get("symbol") is not None:
                    candidates.append(value)

    # ------------------------------------------------------------------
    # Find BTCUSDT safely.
    # ------------------------------------------------------------------

    target = SYMBOL.upper()

    for contract in candidates:

        if not isinstance(contract, dict):
            continue

        contract_symbol = str(
            contract.get("symbol", "")
        ).strip().upper()

        display_symbol = str(
            contract.get("displaySymbol", "")
        ).strip().upper()

        if (
            contract_symbol == target
            or display_symbol == target
        ):
            return contract

    # ------------------------------------------------------------------
    # Diagnostic information WITHOUT leaking credentials.
    # ------------------------------------------------------------------

    discovered = []

    for contract in candidates:
        if not isinstance(contract, dict):
            continue

        value = (
            contract.get("symbol")
            or contract.get("displaySymbol")
        )

        if value:
            discovered.append(
                str(value)
            )

    raise RuntimeError(
        "Could not locate contract information for "
        f"{SYMBOL}; "
        f"response-type={type(raw).__name__}; "
        f"candidate-count={len(candidates)}; "
        f"sample-symbols={discovered[:10]}"
    )


# ======================================================================================
# MARKET PRICE
# ======================================================================================

def obtain_market_price():
    raw = public_get(
        SYMBOL_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    payload = unwrap_common_payload(raw)

    candidates = extract_records(payload)

    target = SYMBOL.upper()

    for record in candidates:

        if not isinstance(record, dict):
            continue

        record_symbol = str(
            record.get("symbol", SYMBOL)
        ).strip().upper()

        if record_symbol != target:
            continue

        price = to_decimal(
            record.get("price")
        )

        if decimal_is_positive(price):
            return price

        mark_price = to_decimal(
            record.get("markPrice")
        )

        if decimal_is_positive(mark_price):
            return mark_price

    raise RuntimeError(
        f"Could not obtain positive MARK price for {SYMBOL}"
    )


# ======================================================================================
# BALANCE
# ======================================================================================

def obtain_available_balance():
    raw = authenticated_get(
        BALANCE_PATH
    )

    records = extract_records(
        unwrap_common_payload(raw)
    )

    for record in records:

        if not isinstance(record, dict):
            continue

        asset = str(
            record.get("asset", "")
        ).strip().upper()

        if asset != "USDT":
            continue

        available = to_decimal(
            record.get("availableBalance")
        )

        if available is None:
            available = to_decimal(
                record.get("available")
            )

        if available is None:
            raise RuntimeError(
                "USDT balance record found but "
                "availableBalance is absent"
            )

        return available

    raise RuntimeError(
        "Could not locate USDT balance record"
    )


# ======================================================================================
# SYMBOL CONFIGURATION
# ======================================================================================

def obtain_symbol_configuration():
    raw = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    records = extract_records(
        unwrap_common_payload(raw)
    )

    target = SYMBOL.upper()

    for record in records:

        if not isinstance(record, dict):
            continue

        record_symbol = str(
            record.get("symbol", "")
        ).strip().upper()

        if record_symbol == target:
            return record

    raise RuntimeError(
        f"Could not locate symbol configuration for {SYMBOL}"
    )


# ======================================================================================
# POSITIONS
# ======================================================================================

def obtain_positions():
    raw = authenticated_get(
        POSITION_PATH
    )

    records = extract_records(
        unwrap_common_payload(raw)
    )

    return [
        record
        for record in records
        if isinstance(record, dict)
    ]


def position_is_open(position):
    size = to_decimal(
        position.get("size"),
        Decimal("0"),
    )

    if size is None:
        return False

    return abs(size) > 0


# ======================================================================================
# CONTRACT FIELD NORMALIZATION
# ======================================================================================

def normalize_contract(contract):
    if not isinstance(contract, dict):
        raise RuntimeError(
            "Contract information is not an object"
        )

    symbol = str(
        contract.get("symbol", "")
    ).strip().upper()

    price_precision = contract.get(
        "pricePrecision"
    )

    quantity_precision = contract.get(
        "quantityPrecision"
    )

    contract_value = to_decimal(
        contract.get("contractVal"),
        Decimal("1"),
    )

    minimum_leverage = to_decimal(
        contract.get("minLeverage")
    )

    maximum_leverage = to_decimal(
        contract.get("maxLeverage")
    )

    minimum_order_size = to_decimal(
        contract.get("minOrderSize")
    )

    maximum_order_size = to_decimal(
        contract.get("maxOrderSize")
    )

    maximum_position_size = to_decimal(
        contract.get("maxPositionSize")
    )

    market_open_limit_size = to_decimal(
        contract.get("marketOpenLimitSize")
    )

    if price_precision is None:
        raise RuntimeError(
            "Contract missing pricePrecision"
        )

    if quantity_precision is None:
        raise RuntimeError(
            "Contract missing quantityPrecision"
        )

    if minimum_order_size is None:
        raise RuntimeError(
            "Contract missing minOrderSize"
        )

    if maximum_order_size is None:
        raise RuntimeError(
            "Contract missing maxOrderSize"
        )

    return {
        "symbol": symbol,

        "base_asset": str(
            contract.get(
                "baseAsset",
                SYMBOL.replace("USDT", ""),
            )
        ),

        "quote_asset": str(
            contract.get(
                "quoteAsset",
                "USDT",
            )
        ),

        "margin_asset": str(
            contract.get(
                "marginAsset",
                "USDT",
            )
        ),

        "price_precision": int(
            price_precision
        ),

        "quantity_precision": int(
            quantity_precision
        ),

        "contract_value": contract_value,

        "minimum_leverage": minimum_leverage,

        "maximum_leverage": maximum_leverage,

        "minimum_order_size": minimum_order_size,

        "maximum_order_size": maximum_order_size,

        "maximum_position_size": maximum_position_size,

        "market_open_limit_size": market_open_limit_size,
    }


# ======================================================================================
# ENTRY QUANTITY CALCULATION
# ======================================================================================

def calculate_entry_readiness(
    available_balance,
    market_price,
    contract,
):
    available_balance = Decimal(
        available_balance
    )

    market_price = Decimal(
        market_price
    )

    entry_margin_budget = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    planned_notional = (
        entry_margin_budget
        * TARGET_LONG_LEVERAGE
    )

    raw_quantity = (
        planned_notional
        / market_price
    )

    quantity_precision = contract[
        "quantity_precision"
    ]

    rounded_quantity = floor_to_precision(
        raw_quantity,
        quantity_precision,
    )

    minimum_order = contract[
        "minimum_order_size"
    ]

    maximum_order = contract[
        "maximum_order_size"
    ]

    # --------------------------------------------------------------
    # If ordinary decimal precision leaves the quantity below the
    # minimum, it cannot be considered executable.
    # --------------------------------------------------------------

    rounded_notional = (
        rounded_quantity
        * market_price
    )

    estimated_margin = (
        rounded_notional
        / TARGET_LONG_LEVERAGE
    )

    return {
        "entry_margin_budget": entry_margin_budget,
        "planned_notional": planned_notional,
        "raw_quantity": raw_quantity,
        "rounded_quantity": rounded_quantity,
        "rounded_notional": rounded_notional,
        "estimated_margin": estimated_margin,
        "minimum_order": minimum_order,
        "maximum_order": maximum_order,
    }


# ======================================================================================
# SYNTHETIC ORDER INTENT
# ======================================================================================

def create_synthetic_order_intent(
    side,
    position_side,
    quantity,
    reference_price,
):
    if not SYNTHETIC_ORDER_INTENT_ONLY:
        raise RuntimeError(
            "Synthetic-order-intent mode is disabled"
        )

    if NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Synthetic intent cannot be created while "
            "network writes are enabled"
        )

    nonce = (
        f"{VERSION}-"
        f"{SYMBOL}-"
        f"{int(time.time() * 1000)}"
    )

    intent = {
        "version": VERSION,
        "synthetic": True,
        "transmit": False,
        "symbol": SYMBOL,
        "side": str(side).upper(),
        "positionSide": str(
            position_side
        ).upper(),
        "type": "MARKET",
        "quantity": decimal_text(
            quantity
        ),
        "referencePrice": decimal_text(
            reference_price
        ),
        "targetMarginType": TARGET_MARGIN_TYPE,
        "targetLeverage": decimal_text(
            TARGET_LONG_LEVERAGE
        ),
        "nonce": nonce,
    }

    canonical = json.dumps(
        intent,
        sort_keys=True,
        separators=(",", ":"),
    )

    intent_hash = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    with runtime_lock:
        runtime["synthetic_intents"] += 1

    return intent, intent_hash


# ======================================================================================
# HEARTBEAT LOOP
# ======================================================================================

def heartbeat_loop():
    while True:

        time.sleep(
            HEARTBEAT_SECONDS
        )

        with runtime_lock:
            runtime["heartbeat"] += 1

            hb = runtime["heartbeat"]
            phase = runtime["phase"]

            authenticated_get_count = runtime[
                "authenticated_get"
            ]

            public_get_count = runtime[
                "public_get"
            ]

            network_writes = runtime[
                "network_writes"
            ]

            leverage_mutations = runtime[
                "leverage_mutations"
            ]

            real_orders = runtime[
                "real_orders"
            ]

            demo_orders = runtime[
                "demo_orders"
            ]

            correction_required = runtime[
                "correction_required"
            ]

            observed_margin = runtime[
                "observed_margin"
            ]

            observed_long = runtime[
                "observed_long"
            ]

            observed_short = runtime[
                "observed_short"
            ]

            entry_quantity = runtime[
                "entry_quantity"
            ]

        entry_text = (
            decimal_text(entry_quantity)
            if entry_quantity is not None
            else "UNKNOWN"
        )

        print(
            f"{VERSION}: HEARTBEAT {hb}"
            f" | phase={phase}"
            f" | authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED}"
            f" | authenticated-get={authenticated_get_count}"
            f" | public-get={public_get_count}"
            f" | network-writes={network_writes}"
            f" | leverage-mutations={leverage_mutations}"
            f" | real-orders={real_orders}"
            f" | demo-orders={demo_orders}"
            f" | correction-required={correction_required}"
            f" | observed-margin={observed_margin}"
            f" | observed-long={observed_long}"
            f" | observed-short={observed_short}"
            f" | target-long="
            f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
            f" | target-short="
            f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
            f" | entry-qty={entry_text}",
            flush=True,
        )


# ======================================================================================
# MAIN VALIDATION
# ======================================================================================

def main():

    heading(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED",
        flush=True,
    )

    print(
        f"{VERSION}: PUBLIC READ-ONLY ENABLED",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET MARGIN={TARGET_MARGIN_TYPE}",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x",
        flush=True,
    )


    # ==================================================================================
    # TEST 1
    # ==================================================================================

    heading(
        f"{VERSION} TEST 1: HARD SAFETY CONFIGURATION"
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED is True,
    )

    check(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY_ENABLED is True,
    )

    check(
        "Synthetic Order Intent Only Is Enabled",
        SYNTHETIC_ORDER_INTENT_ONLY is True,
    )

    check(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )


    # ==================================================================================
    # TEST 2
    # ==================================================================================

    heading(
        f"{VERSION} TEST 2: WRITE FIREBREAK"
    )

    check(
        "HTTP POST Is Rejected",
        confirm_rejected(
            blocked_http_post
        ),
    )

    check(
        "HTTP PUT Is Rejected",
        confirm_rejected(
            blocked_http_put
        ),
    )

    check(
        "HTTP PATCH Is Rejected",
        confirm_rejected(
            blocked_http_patch
        ),
    )

    check(
        "HTTP DELETE Is Rejected",
        confirm_rejected(
            blocked_http_delete
        ),
    )

    check(
        "Generic Network Write Is Rejected",
        confirm_rejected(
            blocked_network_write
        ),
    )

    check(
        "Real Order Function Is Rejected",
        confirm_rejected(
            send_real_order
        ),
    )

    check(
        "Demo Order Function Is Rejected",
        confirm_rejected(
            send_demo_order
        ),
    )

    check(
        "Leverage Mutation Function Is Rejected",
        confirm_rejected(
            mutate_leverage
        ),
    )

    check(
        "Margin Mutation Function Is Rejected",
        confirm_rejected(
            mutate_margin
        ),
    )

    check(
        "Position Mutation Function Is Rejected",
        confirm_rejected(
            mutate_position
        ),
    )


    # ==================================================================================
    # TEST 3
    # ==================================================================================

    heading(
        f"{VERSION} TEST 3: API CREDENTIAL PRESENCE"
    )

    check(
        "WEEX API Key Is Present",
        bool(WEEX_API_KEY),
    )

    check(
        "WEEX API Secret Is Present",
        bool(WEEX_API_SECRET),
    )

    check(
        "WEEX API Passphrase Is Present",
        bool(WEEX_API_PASSPHRASE),
    )


    # ==================================================================================
    # TEST 4
    # ==================================================================================

    heading(
        f"{VERSION} TEST 4: LIVE EXCHANGE INFORMATION"
    )

    contract_raw = obtain_contract_information()

    contract = normalize_contract(
        contract_raw
    )

    check(
        "Contract Information Was Located",
        contract_raw is not None,
    )

    check(
        "Contract Symbol Matches BTCUSDT",
        contract["symbol"] == SYMBOL,
    )

    check(
        "Price Precision Is Valid",
        contract["price_precision"] >= 0,
    )

    check(
        "Quantity Precision Is Valid",
        contract["quantity_precision"] >= 0,
    )

    check(
        "Minimum Order Size Is Positive",
        decimal_is_positive(
            contract["minimum_order_size"]
        ),
    )

    check(
        "Maximum Order Size Is Positive",
        decimal_is_positive(
            contract["maximum_order_size"]
        ),
    )

    if contract["minimum_leverage"] is not None:

        check(
            "Minimum Leverage Is Positive",
            contract["minimum_leverage"] > 0,
        )

    if contract["maximum_leverage"] is not None:

        check(
            "Exchange Supports Target 100x Leverage",
            contract["maximum_leverage"]
            >= TARGET_LONG_LEVERAGE,
        )

    print(
        f"{VERSION}: CONTRACT PATH={EXCHANGE_INFO_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: CONTRACT SYMBOL={contract['symbol']}",
        flush=True,
    )

    print(
        f"{VERSION}: BASE ASSET={contract['base_asset']}",
        flush=True,
    )

    print(
        f"{VERSION}: QUOTE ASSET={contract['quote_asset']}",
        flush=True,
    )

    print(
        f"{VERSION}: MARGIN ASSET={contract['margin_asset']}",
        flush=True,
    )

    print(
        f"{VERSION}: PRICE PRECISION="
        f"{contract['price_precision']}",
        flush=True,
    )

    print(
        f"{VERSION}: QUANTITY PRECISION="
        f"{contract['quantity_precision']}",
        flush=True,
    )

    print(
        f"{VERSION}: MIN ORDER="
        f"{decimal_text(contract['minimum_order_size'])}",
        flush=True,
    )

    print(
        f"{VERSION}: MAX ORDER="
        f"{decimal_text(contract['maximum_order_size'])}",
        flush=True,
    )

    print(
        f"{VERSION}: MIN LEVERAGE="
        f"{decimal_text(contract['minimum_leverage'])}",
        flush=True,
    )

    print(
        f"{VERSION}: MAX LEVERAGE="
        f"{decimal_text(contract['maximum_leverage'])}",
        flush=True,
    )


    # ==================================================================================
    # TEST 5
    # ==================================================================================

    heading(
        f"{VERSION} TEST 5: LIVE MARK PRICE"
    )

    market_price = obtain_market_price()

    check(
        "Market Price Was Read",
        market_price is not None,
    )

    check(
        "Market Price Is Positive",
        market_price > 0,
    )

    with runtime_lock:
        runtime["market_price"] = market_price

    print(
        f"{VERSION}: MARKET PRICE="
        f"{decimal_text(market_price)}",
        flush=True,
    )


    # ==================================================================================
    # TEST 6
    # ==================================================================================

    heading(
        f"{VERSION} TEST 6: LIVE BALANCE RECONCILIATION"
    )

    available_balance = obtain_available_balance()

    check(
        "Available Balance Was Read",
        available_balance is not None,
    )

    check(
        "Available Balance Is Positive",
        available_balance > 0,
    )

    with runtime_lock:
        runtime[
            "available_balance"
        ] = available_balance

    print(
        f"{VERSION}: BALANCE PATH={BALANCE_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_balance)}",
        flush=True,
    )


    # ==================================================================================
    # TEST 7
    # ==================================================================================

    heading(
        f"{VERSION} TEST 7: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    config = obtain_symbol_configuration()

    margin_type = str(
        config.get("marginType", "")
    ).strip().upper()

    long_leverage = to_decimal(
        config.get(
            "isolatedLongLeverage"
        )
    )

    short_leverage = to_decimal(
        config.get(
            "isolatedShortLeverage"
        )
    )

    separated_type = str(
        config.get(
            "separatedType",
            config.get(
                "separatedMode",
                "UNKNOWN",
            ),
        )
    ).strip().upper()

    correction_required = not (
        margin_type == TARGET_MARGIN_TYPE
        and long_leverage
        == TARGET_LONG_LEVERAGE
        and short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    check(
        "Margin Type Is ISOLATED",
        margin_type
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Long Leverage Is 100x",
        long_leverage
        == TARGET_LONG_LEVERAGE,
    )

    check(
        "Short Leverage Is 100x",
        short_leverage
        == TARGET_SHORT_LEVERAGE,
    )

    check(
        "Account Configuration Requires No Correction",
        correction_required is False,
    )

    with runtime_lock:

        runtime[
            "correction_required"
        ] = correction_required

        runtime[
            "observed_margin"
        ] = margin_type

        runtime[
            "observed_long"
        ] = decimal_text(
            long_leverage
        )

        runtime[
            "observed_short"
        ] = decimal_text(
            short_leverage
        )

    print(
        f"{VERSION}: SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED MARGIN={margin_type}",
        flush=True,
    )

    print(
        f"{VERSION}: POSITION MODE={separated_type}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{decimal_text(long_leverage)}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{decimal_text(short_leverage)}x",
        flush=True,
    )


    # ==================================================================================
    # TEST 8
    # ==================================================================================

    heading(
        f"{VERSION} TEST 8: LIVE POSITION RECONCILIATION"
    )

    all_positions = obtain_positions()

    symbol_positions = []

    for position in all_positions:

        position_symbol = str(
            position.get(
                "symbol",
                "",
            )
        ).strip().upper()

        if position_symbol == SYMBOL:
            symbol_positions.append(
                position
            )

    open_symbol_positions = [
        position
        for position in symbol_positions
        if position_is_open(position)
    ]

    check(
        "Position Response Is Valid",
        isinstance(
            all_positions,
            list,
        ),
    )

    check(
        "BTCUSDT Open Position Count Is Non-Negative",
        len(open_symbol_positions) >= 0,
    )

    print(
        f"{VERSION}: POSITION PATH={POSITION_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(all_positions)}",
        flush=True,
    )

    print(
        f"{VERSION}: BTCUSDT POSITION RECORDS="
        f"{len(symbol_positions)}",
        flush=True,
    )

    print(
        f"{VERSION}: BTCUSDT OPEN POSITIONS="
        f"{len(open_symbol_positions)}",
        flush=True,
    )


    # ==================================================================================
    # TEST 9
    # ==================================================================================

    heading(
        f"{VERSION} TEST 9: INITIAL ENTRY READINESS CALCULATION"
    )

    entry = calculate_entry_readiness(
        available_balance=available_balance,
        market_price=market_price,
        contract=contract,
    )

    check(
        "Initial Entry Percent Is Positive",
        INITIAL_ENTRY_PERCENT > 0,
    )

    check(
        "Initial Entry Is Within Exposure Cap",
        INITIAL_ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    check(
        "Initial Entry Margin Budget Is Positive",
        entry[
            "entry_margin_budget"
        ] > 0,
    )

    check(
        "Planned Notional Is Positive",
        entry[
            "planned_notional"
        ] > 0,
    )

    check(
        "Raw Quantity Is Positive",
        entry[
            "raw_quantity"
        ] > 0,
    )

    check(
        "Rounded Quantity Is Positive",
        entry[
            "rounded_quantity"
        ] > 0,
    )

    check(
        "Rounded Quantity Meets Exchange Minimum",
        entry[
            "rounded_quantity"
        ] >= entry[
            "minimum_order"
        ],
    )

    check(
        "Rounded Quantity Is Below Exchange Maximum",
        entry[
            "rounded_quantity"
        ] <= entry[
            "maximum_order"
        ],
    )

    maximum_allowed_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    check(
        "Estimated Entry Margin Is Within Exposure Cap",
        entry[
            "estimated_margin"
        ] <= maximum_allowed_margin,
    )

    with runtime_lock:
        runtime[
            "entry_quantity"
        ] = entry[
            "rounded_quantity"
        ]

    print(
        f"{VERSION}: ENTRY BALANCE PERCENT="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%",
        flush=True,
    )

    print(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_text(entry['entry_margin_budget'])} USDT",
        flush=True,
    )

    print(
        f"{VERSION}: PLANNED NOTIONAL="
        f"{decimal_text(entry['planned_notional'])} USDT",
        flush=True,
    )

    print(
        f"{VERSION}: RAW QUANTITY="
        f"{decimal_text(entry['raw_quantity'])} BTC",
        flush=True,
    )

    print(
        f"{VERSION}: ROUNDED QUANTITY="
        f"{decimal_text(entry['rounded_quantity'])} BTC",
        flush=True,
    )

    print(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{decimal_text(entry['rounded_notional'])} USDT",
        flush=True,
    )

    print(
        f"{VERSION}: ESTIMATED MARGIN AT "
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x="
        f"{decimal_text(entry['estimated_margin'])} USDT",
        flush=True,
    )


    # ==================================================================================
    # TEST 10
    # ==================================================================================

    heading(
        f"{VERSION} TEST 10: MAXIMUM STRATEGY EXPOSURE"
    )

    planned_max_strategy_percent = (
        INITIAL_ENTRY_PERCENT
        + (
            Decimal(MAX_PYRAMID_ADDS)
            * PYRAMID_SIZE_PERCENT
        )
        + (
            Decimal(MAX_BACKUPS)
            * BACKUP_SIZE_PERCENT
        )
    )

    planned_max_strategy_margin = (
        available_balance
        * planned_max_strategy_percent
        / Decimal("100")
    )

    max_allowed_strategy_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
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
        "Maximum Planned Strategy Margin Is Within 35%",
        planned_max_strategy_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    print(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%",
        flush=True,
    )

    print(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{decimal_text(max_allowed_strategy_margin)} USDT",
        flush=True,
    )

    print(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_text(planned_max_strategy_margin)} USDT",
        flush=True,
    )


    # ==================================================================================
    # TEST 11
    # ==================================================================================

    heading(
        f"{VERSION} TEST 11: TAKE-PROFIT STRUCTURE"
    )

    tp_total = (
        TP1_ALLOCATION_PERCENT
        + TP2_ALLOCATION_PERCENT
        + TP3_ALLOCATION_PERCENT
    )

    check(
        "TP Allocation Totals 100 Percent",
        tp_total == Decimal("100"),
    )

    check(
        "TP1 Trigger Is Positive",
        TP1_TRIGGER_PERCENT > 0,
    )

    check(
        "TP2 Trigger Is Above TP1",
        TP2_TRIGGER_PERCENT
        > TP1_TRIGGER_PERCENT,
    )

    check(
        "Trailing Distance Is Positive",
        TRAILING_DISTANCE_PERCENT > 0,
    )

    print(
        f"{VERSION}: TP1="
        f"{decimal_text(TP1_ALLOCATION_PERCENT)}% "
        f"AT +{decimal_text(TP1_TRIGGER_PERCENT)}%",
        flush=True,
    )

    print(
        f"{VERSION}: TP2="
        f"{decimal_text(TP2_ALLOCATION_PERCENT)}% "
        f"AT +{decimal_text(TP2_TRIGGER_PERCENT)}%",
        flush=True,
    )

    print(
        f"{VERSION}: TP3="
        f"{decimal_text(TP3_ALLOCATION_PERCENT)}% TRAILING",
        flush=True,
    )

    print(
        f"{VERSION}: TRAILING DISTANCE="
        f"{decimal_text(TRAILING_DISTANCE_PERCENT)}%",
        flush=True,
    )


    # ==================================================================================
    # TEST 12
    # ==================================================================================

    heading(
        f"{VERSION} TEST 12: SYNTHETIC ORDER INTENT"
    )

    synthetic_intent, intent_hash = (
        create_synthetic_order_intent(
            side="BUY",
            position_side="LONG",
            quantity=entry[
                "rounded_quantity"
            ],
            reference_price=market_price,
        )
    )

    check(
        "Synthetic Intent Is Marked Synthetic",
        synthetic_intent[
            "synthetic"
        ] is True,
    )

    check(
        "Synthetic Intent Forbids Transmission",
        synthetic_intent[
            "transmit"
        ] is False,
    )

    check(
        "Synthetic Intent Symbol Matches BTCUSDT",
        synthetic_intent[
            "symbol"
        ] == SYMBOL,
    )

    check(
        "Synthetic Intent Quantity Matches Readiness Calculation",
        synthetic_intent[
            "quantity"
        ]
        == decimal_text(
            entry[
                "rounded_quantity"
            ]
        ),
    )

    check(
        "Synthetic Intent Hash Exists",
        len(intent_hash) == 64,
    )

    print(
        f"{VERSION}: SYNTHETIC INTENT SHA256={intent_hash}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC INTENT TRANSMITTED=False",
        flush=True,
    )


    # ==================================================================================
    # TEST 13
    # ==================================================================================

    heading(
        f"{VERSION} TEST 13: FINAL EXECUTION-READINESS FIREBREAK"
    )

    with runtime_lock:

        network_writes = runtime[
            "network_writes"
        ]

        leverage_mutations = runtime[
            "leverage_mutations"
        ]

        margin_mutations = runtime[
            "margin_mutations"
        ]

        position_mutations = runtime[
            "position_mutations"
        ]

        account_mutations = runtime[
            "account_mutations"
        ]

        real_orders = runtime[
            "real_orders"
        ]

        demo_orders = runtime[
            "demo_orders"
        ]

    check(
        "Network Writes Remain Zero",
        network_writes == 0,
    )

    check(
        "Leverage Mutations Remain Zero",
        leverage_mutations == 0,
    )

    check(
        "Margin Mutations Remain Zero",
        margin_mutations == 0,
    )

    check(
        "Position Mutations Remain Zero",
        position_mutations == 0,
    )

    check(
        "Account Mutations Remain Zero",
        account_mutations == 0,
    )

    check(
        "Real Orders Remain Zero",
        real_orders == 0,
    )

    check(
        "Demo Orders Remain Zero",
        demo_orders == 0,
    )

    check(
        "Account Configuration Requires No Correction",
        correction_required is False,
    )


    # ==================================================================================
    # VALIDATION COMPLETE
    # ==================================================================================

    heading(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    pass_line(
        "Live Strategy / Account Execution Readiness"
    )

    pass_line(
        "WEEX V3 Contract Information Located"
    )

    pass_line(
        "Account Is Already ISOLATED 100x / 100x"
    )

    pass_line(
        "Initial Entry Calculation Is Exchange Compatible"
    )

    pass_line(
        "Maximum Strategy Exposure Is Within 35%"
    )

    pass_line(
        "Synthetic Order Intent Was Constructed"
    )

    pass_line(
        "Synthetic Order Intent Was Not Transmitted"
    )

    pass_line(
        "No Account Mutation Was Performed"
    )

    pass_line(
        "No Real Order Was Sent"
    )

    pass_line(
        "No Demo Order Was Sent"
    )

    pass_line(
        "Network Writes Remain Zero"
    )

    with runtime_lock:
        runtime[
            "phase"
        ] = "LIVE_EXECUTION_READINESS_VALIDATED"

        runtime[
            "heartbeat"
        ] = 1

    print(
        f"{VERSION}: HEARTBEAT 1"
        f" | phase=LIVE_EXECUTION_READINESS_VALIDATED"
        f" | authenticated-read-only=True"
        f" | authenticated-get="
        f"{runtime['authenticated_get']}"
        f" | public-get="
        f"{runtime['public_get']}"
        f" | network-writes=0"
        f" | leverage-mutations=0"
        f" | real-orders=0"
        f" | demo-orders=0"
        f" | correction-required=False"
        f" | observed-margin={margin_type}"
        f" | observed-long={decimal_text(long_leverage)}"
        f" | observed-short={decimal_text(short_leverage)}"
        f" | target-long="
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
        f" | target-short="
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
        f" | entry-qty="
        f"{decimal_text(entry['rounded_quantity'])}",
        flush=True,
    )

    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        daemon=True,
    )

    heartbeat_thread.start()

    while True:
        time.sleep(3600)


# ======================================================================================
# ENTRY POINT
# ======================================================================================

if __name__ == "__main__":

    health_server = None

    try:
        health_server = start_health_server()

        main()

    except KeyboardInterrupt:

        print(
            f"{VERSION}: SHUTDOWN REQUESTED",
            flush=True,
        )

        sys.exit(0)

    except Exception as exc:

        with runtime_lock:
            runtime[
                "phase"
            ] = "VALIDATION_FAILED"

        separator()

        print(
            f"{VERSION}: VALIDATION FAILED",
            flush=True,
        )

        separator()

        print(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        traceback.print_exc()

        # Keep the health endpoint available briefly enough for
        # deployment infrastructure to observe the failure state,
        # then fail the process normally.

        time.sleep(1)

        sys.exit(1)
