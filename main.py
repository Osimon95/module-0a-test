import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import urllib.parse
import urllib.request
import urllib.error

from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R34N
# LIVE STRATEGY / ACCOUNT EXECUTION-READINESS VALIDATION
#
# IMPORTANT SAFETY STATE:
#
#   - AUTHENTICATED READ-ONLY API ACCESS: ENABLED
#   - PUBLIC READ-ONLY API ACCESS: ENABLED
#   - NETWORK WRITES: DISABLED
#   - REAL ORDER EXECUTION: DISABLED
#   - DEMO ORDER EXECUTION: DISABLED
#   - LEVERAGE MUTATION: DISABLED
#   - MARGIN MUTATION: DISABLED
#   - POSITION MUTATION: DISABLED
#
# R34N DOES NOT SEND POST / PUT / PATCH / DELETE REQUESTS.
# =============================================================================


VERSION = "R34N"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()
ASSET = os.getenv("ASSET", "USDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", "10000"))

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

HEARTBEAT_SECONDS = 30

HTTP_TIMEOUT_SECONDS = 15

AUTHENTICATED_READ_ONLY_ENABLED = True
PUBLIC_READ_ONLY_ENABLED = True

NETWORK_WRITES_ENABLED = False
REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# =============================================================================
# GLOBAL STATE
# =============================================================================


STATE_LOCK = threading.Lock()

STATE = {
    "version": VERSION,
    "symbol": SYMBOL,
    "phase": "BOOTING",

    "authenticated_read_only": True,
    "public_read_only": True,

    "authenticated_gets": 0,
    "public_gets": 0,

    "network_writes": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "real_orders": 0,
    "demo_orders": 0,

    "available_balance": None,
    "market_price": None,

    "observed_margin": None,
    "observed_long": None,
    "observed_short": None,
    "position_mode": None,

    "correction_required": None,

    "quantity_precision": None,
    "price_precision": None,
    "min_order_size": None,
    "max_leverage": None,

    "entry_margin_budget": None,
    "planned_notional": None,
    "raw_quantity": None,
    "rounded_quantity": None,
    "rounded_notional": None,
    "estimated_margin": None,

    "validation_passed": False,
}


# =============================================================================
# LOGGING
# =============================================================================


LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def pass_line(label):
    log(f"{label:<88} ✅ PASS")


def fail_line(label):
    log(f"{label:<88} ❌ FAIL")


def require(condition, label):
    if condition:
        pass_line(label)
        return

    fail_line(label)
    raise RuntimeError(label)


# =============================================================================
# DECIMAL HELPERS
# =============================================================================


def D(value, default=None):
    if value is None:
        if default is not None:
            return Decimal(str(default))
        raise ValueError("Decimal value is None")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        if default is not None:
            return Decimal(str(default))
        raise


def decimal_text(value):
    if value is None:
        return "None"

    if not isinstance(value, Decimal):
        value = D(value)

    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def floor_to_precision(value, precision):
    value = D(value)

    precision = int(precision)

    quantum = Decimal("1").scaleb(-precision)

    return value.quantize(
        quantum,
        rounding=ROUND_DOWN
    )


def first_dict(value):
    if isinstance(value, dict):
        return value

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return item

    return None


def unwrap_data(payload):
    if isinstance(payload, dict):
        if "data" in payload and payload["data"] is not None:
            return payload["data"]

    return payload


# =============================================================================
# CREDENTIALS
# =============================================================================


def get_credentials():
    api_key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
        or ""
    ).strip()

    api_secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
        or ""
    ).strip()

    api_passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
        or ""
    ).strip()

    return api_key, api_secret, api_passphrase


# =============================================================================
# SIGNATURE
# =============================================================================


def generate_signature(
    timestamp,
    method,
    request_path,
    query_string,
    body,
    secret
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
        secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# =============================================================================
# HARD HTTP FIREBREAK
# =============================================================================


def assert_read_only_method(method):
    method = str(method).upper()

    if method != "GET":
        raise RuntimeError(
            f"R34N FIREBREAK: HTTP {method} BLOCKED. "
            "ONLY GET IS PERMITTED."
        )


def http_get_json(
    request_path,
    params=None,
    authenticated=False
):
    """
    This transport has NO general-purpose method parameter.

    It can perform GET only.

    POST / PUT / PATCH / DELETE are structurally unavailable here.
    """

    assert_read_only_method("GET")

    if params is None:
        params = {}

    clean_params = {}

    for key, value in params.items():
        if value is not None:
            clean_params[str(key)] = str(value)

    query_string = urllib.parse.urlencode(clean_params)

    url = BASE_URL + request_path

    if query_string:
        url += "?" + query_string

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"{VERSION}-read-only-validator",
    }

    if authenticated:
        api_key, api_secret, api_passphrase = get_credentials()

        if not api_key:
            raise RuntimeError("WEEX_API_KEY is missing")

        if not api_secret:
            raise RuntimeError("WEEX_API_SECRET is missing")

        if not api_passphrase:
            raise RuntimeError("WEEX_API_PASSPHRASE is missing")

        timestamp = str(int(time.time() * 1000))

        signature = generate_signature(
            timestamp=timestamp,
            method="GET",
            request_path=request_path,
            query_string=query_string,
            body="",
            secret=api_secret,
        )

        headers.update({
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": api_passphrase,
            "ACCESS-TIMESTAMP": timestamp,
        })

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            status = response.getcode()

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"HTTP {exc.code} GET {request_path}: {raw}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Network GET failed for {request_path}: {exc}"
        )

    if status < 200 or status >= 300:
        raise RuntimeError(
            f"Unexpected HTTP status {status}: {request_path}"
        )

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"Invalid JSON from {request_path}: "
            f"{raw[:500]}"
        )

    with STATE_LOCK:
        if authenticated:
            STATE["authenticated_gets"] += 1
        else:
            STATE["public_gets"] += 1

    return payload


# =============================================================================
# ABSOLUTE WRITE / ORDER BLOCKS
# =============================================================================


def network_write(*args, **kwargs):
    raise RuntimeError(
        "R34N FIREBREAK: NETWORK WRITE DISABLED"
    )


def place_real_order(*args, **kwargs):
    raise RuntimeError(
        "R34N FIREBREAK: REAL ORDER EXECUTION DISABLED"
    )


def place_demo_order(*args, **kwargs):
    raise RuntimeError(
        "R34N FIREBREAK: DEMO ORDER EXECUTION DISABLED"
    )


def mutate_leverage(*args, **kwargs):
    raise RuntimeError(
        "R34N FIREBREAK: LEVERAGE MUTATION DISABLED"
    )


def mutate_margin(*args, **kwargs):
    raise RuntimeError(
        "R34N FIREBREAK: MARGIN MUTATION DISABLED"
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        "R34N FIREBREAK: POSITION MUTATION DISABLED"
    )


# =============================================================================
# PUBLIC READS
# =============================================================================


def get_exchange_info():
    payload = http_get_json(
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL
        },
        authenticated=False,
    )

    data = unwrap_data(payload)

    if not isinstance(data, dict):
        raise RuntimeError(
            "Exchange info response is not an object"
        )

    symbols = data.get("symbols")

    if not isinstance(symbols, list):
        raise RuntimeError(
            "Exchange info does not contain symbols[]"
        )

    for item in symbols:
        if not isinstance(item, dict):
            continue

        if str(item.get("symbol", "")).upper() == SYMBOL:
            return item

    raise RuntimeError(
        f"{SYMBOL} was not found in exchangeInfo"
    )


def get_mark_price():
    payload = http_get_json(
        "/capi/v3/market/symbolPrice",
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
        authenticated=False,
    )

    data = unwrap_data(payload)

    if isinstance(data, list):
        selected = None

        for item in data:
            if (
                isinstance(item, dict)
                and str(item.get("symbol", "")).upper() == SYMBOL
            ):
                selected = item
                break

        if selected is None:
            selected = first_dict(data)

        data = selected

    if not isinstance(data, dict):
        raise RuntimeError(
            "Market price response is not an object"
        )

    price = data.get("price")

    if price is None:
        price = data.get("markPrice")

    result = D(price)

    if result <= 0:
        raise RuntimeError(
            f"Invalid market price: {result}"
        )

    return result


# =============================================================================
# AUTHENTICATED READS
# =============================================================================


def get_available_balance():
    payload = http_get_json(
        "/capi/v3/account/balance",
        authenticated=True,
    )

    data = unwrap_data(payload)

    if isinstance(data, dict):
        if isinstance(data.get("list"), list):
            data = data["list"]
        elif isinstance(data.get("assets"), list):
            data = data["assets"]
        else:
            data = [data]

    if not isinstance(data, list):
        raise RuntimeError(
            "Balance response does not contain a list"
        )

    for item in data:
        if not isinstance(item, dict):
            continue

        asset = str(
            item.get("asset")
            or item.get("coin")
            or item.get("currency")
            or ""
        ).upper()

        if asset != ASSET:
            continue

        value = (
            item.get("availableBalance")
            if item.get("availableBalance") is not None
            else item.get("available")
        )

        if value is None:
            value = item.get("balance")

        return D(value)

    raise RuntimeError(
        f"{ASSET} balance was not found"
    )


def get_symbol_config():
    payload = http_get_json(
        "/capi/v3/account/symbolConfig",
        {
            "symbol": SYMBOL
        },
        authenticated=True,
    )

    data = unwrap_data(payload)

    if isinstance(data, dict):
        if isinstance(data.get("list"), list):
            data = data["list"]
        elif isinstance(data.get("symbolConfig"), list):
            data = data["symbolConfig"]
        else:
            data = [data]

    if not isinstance(data, list):
        raise RuntimeError(
            "Symbol configuration response is invalid"
        )

    for item in data:
        if not isinstance(item, dict):
            continue

        item_symbol = str(
            item.get("symbol", "")
        ).upper()

        if item_symbol == SYMBOL:
            return item

    raise RuntimeError(
        f"Symbol configuration for {SYMBOL} was not found"
    )


def get_all_positions():
    payload = http_get_json(
        "/capi/v3/account/position/allPosition",
        authenticated=True,
    )

    data = unwrap_data(payload)

    if data is None:
        return []

    if isinstance(data, dict):
        if isinstance(data.get("list"), list):
            data = data["list"]
        elif isinstance(data.get("positions"), list):
            data = data["positions"]
        else:
            data = [data]

    if not isinstance(data, list):
        raise RuntimeError(
            "Position response does not contain a list"
        )

    return data


# =============================================================================
# ACCOUNT CONFIG PARSING
# =============================================================================


def parse_account_configuration(config):
    margin_type = str(
        config.get("marginType", "")
    ).upper()

    position_mode = str(
        config.get("separatedType")
        or config.get("positionMode")
        or config.get("separatedMode")
        or ""
    ).upper()

    long_leverage = D(
        config.get("isolatedLongLeverage"),
        default="0"
    )

    short_leverage = D(
        config.get("isolatedShortLeverage"),
        default="0"
    )

    return (
        margin_type,
        position_mode,
        long_leverage,
        short_leverage,
    )


# =============================================================================
# STRATEGY CALCULATION
# =============================================================================


def calculate_readiness(
    balance,
    market_price,
    exchange_info
):
    quantity_precision = int(
        exchange_info.get("quantityPrecision", 6)
    )

    price_precision = int(
        exchange_info.get("pricePrecision", 1)
    )

    min_order_size = D(
        exchange_info.get("minOrderSize"),
        default="0"
    )

    max_order_size = D(
        exchange_info.get("maxOrderSize"),
        default="999999999"
    )

    min_leverage = D(
        exchange_info.get("minLeverage"),
        default="1"
    )

    max_leverage = D(
        exchange_info.get("maxLeverage"),
        default="0"
    )

    entry_margin_budget = (
        balance
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

    rounded_quantity = floor_to_precision(
        raw_quantity,
        quantity_precision
    )

    rounded_notional = (
        rounded_quantity
        * market_price
    )

    estimated_margin = (
        rounded_notional
        / TARGET_LONG_LEVERAGE
    )

    max_fund_margin = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    planned_max_strategy_margin = (
        entry_margin_budget
        + (
            balance
            * PYRAMID_PERCENT
            / Decimal("100")
            * Decimal(MAX_PYRAMID_ADDS)
        )
        + (
            balance
            * BACKUP_PERCENT
            / Decimal("100")
            * Decimal(MAX_BACKUPS)
        )
    )

    return {
        "quantity_precision": quantity_precision,
        "price_precision": price_precision,

        "min_order_size": min_order_size,
        "max_order_size": max_order_size,

        "min_leverage": min_leverage,
        "max_leverage": max_leverage,

        "entry_margin_budget": entry_margin_budget,
        "planned_notional": planned_notional,

        "raw_quantity": raw_quantity,
        "rounded_quantity": rounded_quantity,

        "rounded_notional": rounded_notional,
        "estimated_margin": estimated_margin,

        "max_fund_margin": max_fund_margin,

        "planned_max_strategy_margin":
            planned_max_strategy_margin,
    }


# =============================================================================
# HEALTH SERVER
# =============================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        with STATE_LOCK:
            snapshot = dict(STATE)

        body = json.dumps(
            snapshot,
            indent=2,
            default=str
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    def run():
        try:
            server = HTTPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler
            )

            server.serve_forever()

        except Exception as exc:
            log(
                f"{VERSION}: HEALTH SERVER ERROR="
                f"{type(exc).__name__}: {exc}"
            )

    thread = threading.Thread(
        target=run,
        daemon=True
    )

    thread.start()


# =============================================================================
# FIREBREAK SELF TEST
# =============================================================================


def expect_block(function, label):
    blocked = False

    try:
        function()

    except RuntimeError:
        blocked = True

    require(
        blocked,
        label
    )


# =============================================================================
# VALIDATION
# =============================================================================


def run_validation():

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")

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
        f"{VERSION}: TARGET MARGIN="
        f"{TARGET_MARGIN_TYPE}"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
    )


    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        f"{VERSION} TEST 1: HARD SAFETY CONFIGURATION"
    )

    require(
        AUTHENTICATED_READ_ONLY_ENABLED,
        "Authenticated Read-Only Is Enabled"
    )

    require(
        PUBLIC_READ_ONLY_ENABLED,
        "Public Read-Only Is Enabled"
    )

    require(
        not NETWORK_WRITES_ENABLED,
        "Network Writes Are Disabled"
    )

    require(
        not REAL_ORDER_EXECUTION_ENABLED,
        "Real Order Execution Is Disabled"
    )

    require(
        not DEMO_ORDER_EXECUTION_ENABLED,
        "Demo Order Execution Is Disabled"
    )

    require(
        not LEVERAGE_MUTATION_ENABLED,
        "Leverage Mutation Is Disabled"
    )

    require(
        not MARGIN_MUTATION_ENABLED,
        "Margin Mutation Is Disabled"
    )

    require(
        not POSITION_MUTATION_ENABLED,
        "Position Mutation Is Disabled"
    )

    require(
        not ACCOUNT_MUTATION_ENABLED,
        "Account Mutation Is Disabled"
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        f"{VERSION} TEST 2: WRITE FIREBREAK"
    )

    expect_block(
        lambda: assert_read_only_method("POST"),
        "HTTP POST Is Rejected"
    )

    expect_block(
        lambda: assert_read_only_method("PUT"),
        "HTTP PUT Is Rejected"
    )

    expect_block(
        lambda: assert_read_only_method("PATCH"),
        "HTTP PATCH Is Rejected"
    )

    expect_block(
        lambda: assert_read_only_method("DELETE"),
        "HTTP DELETE Is Rejected"
    )

    expect_block(
        network_write,
        "Generic Network Write Is Rejected"
    )

    expect_block(
        place_real_order,
        "Real Order Function Is Rejected"
    )

    expect_block(
        place_demo_order,
        "Demo Order Function Is Rejected"
    )

    expect_block(
        mutate_leverage,
        "Leverage Mutation Function Is Rejected"
    )

    expect_block(
        mutate_margin,
        "Margin Mutation Function Is Rejected"
    )

    expect_block(
        mutate_position,
        "Position Mutation Function Is Rejected"
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        f"{VERSION} TEST 3: API CREDENTIAL PRESENCE"
    )

    api_key, api_secret, api_passphrase = get_credentials()

    require(
        bool(api_key),
        "WEEX API Key Is Present"
    )

    require(
        bool(api_secret),
        "WEEX API Secret Is Present"
    )

    require(
        bool(api_passphrase),
        "WEEX API Passphrase Is Present"
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        f"{VERSION} TEST 4: LIVE EXCHANGE INFORMATION"
    )

    exchange_info = get_exchange_info()

    quantity_precision = int(
        exchange_info.get("quantityPrecision", 6)
    )

    price_precision = int(
        exchange_info.get("pricePrecision", 1)
    )

    min_order_size = D(
        exchange_info.get("minOrderSize"),
        default="0"
    )

    max_leverage = D(
        exchange_info.get("maxLeverage"),
        default="0"
    )

    require(
        str(
            exchange_info.get("symbol", "")
        ).upper() == SYMBOL,
        "Exchange Symbol Matches"
    )

    require(
        quantity_precision >= 0,
        "Quantity Precision Is Valid"
    )

    require(
        price_precision >= 0,
        "Price Precision Is Valid"
    )

    require(
        min_order_size > 0,
        "Minimum Order Size Is Positive"
    )

    require(
        max_leverage >= TARGET_LONG_LEVERAGE,
        "Exchange Supports Target Leverage"
    )

    log(
        f"{VERSION}: QUANTITY PRECISION="
        f"{quantity_precision}"
    )

    log(
        f"{VERSION}: PRICE PRECISION="
        f"{price_precision}"
    )

    log(
        f"{VERSION}: MIN ORDER SIZE="
        f"{decimal_text(min_order_size)}"
    )

    log(
        f"{VERSION}: EXCHANGE MAX LEVERAGE="
        f"{decimal_text(max_leverage)}x"
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        f"{VERSION} TEST 5: LIVE MARK PRICE"
    )

    market_price = get_mark_price()

    require(
        market_price > 0,
        "Live Mark Price Was Read"
    )

    log(
        f"{VERSION}: MARK PRICE="
        f"{decimal_text(market_price)}"
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        f"{VERSION} TEST 6: LIVE BALANCE RECONCILIATION"
    )

    balance = get_available_balance()

    require(
        balance >= 0,
        "Available Balance Was Read"
    )

    require(
        balance > 0,
        "Available Balance Is Positive"
    )

    log(
        f"{VERSION}: AVAILABLE {ASSET}="
        f"{decimal_text(balance)}"
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        f"{VERSION} TEST 7: LIVE SYMBOL CONFIGURATION"
    )

    config = get_symbol_config()

    (
        margin_type,
        position_mode,
        long_leverage,
        short_leverage,
    ) = parse_account_configuration(config)

    require(
        margin_type == TARGET_MARGIN_TYPE,
        "Margin Type Matches Strategy"
    )

    require(
        long_leverage == TARGET_LONG_LEVERAGE,
        "Long Leverage Matches 100x"
    )

    require(
        short_leverage == TARGET_SHORT_LEVERAGE,
        "Short Leverage Matches 100x"
    )

    correction_required = not (
        margin_type == TARGET_MARGIN_TYPE
        and
        long_leverage == TARGET_LONG_LEVERAGE
        and
        short_leverage == TARGET_SHORT_LEVERAGE
    )

    require(
        correction_required is False,
        "No Account Correction Is Required"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: POSITION MODE="
        f"{position_mode or 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{decimal_text(long_leverage)}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{decimal_text(short_leverage)}x"
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        f"{VERSION} TEST 8: LIVE POSITION RECONCILIATION"
    )

    positions = get_all_positions()

    symbol_positions = []

    for position in positions:
        if not isinstance(position, dict):
            continue

        if str(
            position.get("symbol", "")
        ).upper() == SYMBOL:
            symbol_positions.append(position)

    open_positions = []

    for position in symbol_positions:
        size = D(
            position.get("size"),
            default="0"
        )

        if size != 0:
            open_positions.append(position)

    require(
        isinstance(positions, list),
        "Position Snapshot Was Read"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(positions)}"
    )

    log(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(symbol_positions)}"
    )

    log(
        f"{VERSION}: {SYMBOL} OPEN POSITIONS="
        f"{len(open_positions)}"
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    section(
        f"{VERSION} TEST 9: INITIAL ENTRY READINESS CALCULATION"
    )

    calc = calculate_readiness(
        balance=balance,
        market_price=market_price,
        exchange_info=exchange_info,
    )

    require(
        INITIAL_ENTRY_PERCENT > 0,
        "Initial Entry Percent Is Positive"
    )

    require(
        INITIAL_ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT,
        "Initial Entry Is Within Exposure Cap"
    )

    require(
        calc["entry_margin_budget"] > 0,
        "Initial Entry Margin Budget Is Positive"
    )

    require(
        calc["planned_notional"] > 0,
        "Planned Notional Is Positive"
    )

    require(
        calc["raw_quantity"] > 0,
        "Raw Quantity Is Positive"
    )

    require(
        calc["rounded_quantity"] > 0,
        "Rounded Quantity Is Positive"
    )

    require(
        calc["rounded_quantity"]
        >= calc["min_order_size"],
        "Rounded Quantity Meets Exchange Minimum"
    )

    require(
        calc["rounded_quantity"]
        <= calc["max_order_size"],
        "Rounded Quantity Is Below Exchange Maximum"
    )

    require(
        calc["estimated_margin"]
        <= calc["max_fund_margin"],
        "Estimated Entry Margin Is Within Exposure Cap"
    )

    log(
        f"{VERSION}: ENTRY BALANCE PERCENT="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_text(calc['entry_margin_budget'])} "
        f"{ASSET}"
    )

    log(
        f"{VERSION}: PLANNED NOTIONAL="
        f"{decimal_text(calc['planned_notional'])} "
        f"{ASSET}"
    )

    log(
        f"{VERSION}: RAW QUANTITY="
        f"{decimal_text(calc['raw_quantity'])} BTC"
    )

    log(
        f"{VERSION}: ROUNDED QUANTITY="
        f"{decimal_text(calc['rounded_quantity'])} BTC"
    )

    log(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{decimal_text(calc['rounded_notional'])} "
        f"{ASSET}"
    )

    log(
        f"{VERSION}: ESTIMATED MARGIN AT 100x="
        f"{decimal_text(calc['estimated_margin'])} "
        f"{ASSET}"
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    section(
        f"{VERSION} TEST 10: MAXIMUM STRATEGY EXPOSURE"
    )

    require(
        MAX_PYRAMID_ADDS == 1,
        "Maximum Pyramid Adds Is One"
    )

    require(
        MAX_BACKUPS == 3,
        "Maximum Backups Is Three"
    )

    require(
        calc["planned_max_strategy_margin"]
        <= calc["max_fund_margin"],
        "Maximum Planned Strategy Margin Is Within 35%"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{decimal_text(calc['max_fund_margin'])} "
        f"{ASSET}"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_text(calc['planned_max_strategy_margin'])} "
        f"{ASSET}"
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    section(
        f"{VERSION} TEST 11: TAKE-PROFIT STRUCTURE"
    )

    require(
        TP1_PERCENT + TP2_PERCENT + TP3_PERCENT
        == Decimal("100"),
        "TP Allocation Totals 100 Percent"
    )

    require(
        TP1_TRIGGER_PERCENT > 0,
        "TP1 Trigger Is Positive"
    )

    require(
        TP2_TRIGGER_PERCENT
        > TP1_TRIGGER_PERCENT,
        "TP2 Trigger Is Above TP1"
    )

    require(
        TRAILING_DISTANCE_PERCENT > 0,
        "Trailing Distance Is Positive"
    )

    log(
        f"{VERSION}: TP1="
        f"{decimal_text(TP1_PERCENT)}% "
        f"AT +{decimal_text(TP1_TRIGGER_PERCENT)}%"
    )

    log(
        f"{VERSION}: TP2="
        f"{decimal_text(TP2_PERCENT)}% "
        f"AT +{decimal_text(TP2_TRIGGER_PERCENT)}%"
    )

    log(
        f"{VERSION}: TP3="
        f"{decimal_text(TP3_PERCENT)}% TRAILING"
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{decimal_text(TRAILING_DISTANCE_PERCENT)}%"
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    section(
        f"{VERSION} TEST 12: FINAL EXECUTION-READINESS FIREBREAK"
    )

    with STATE_LOCK:
        network_writes = STATE["network_writes"]
        leverage_mutations = STATE["leverage_mutations"]
        margin_mutations = STATE["margin_mutations"]
        position_mutations = STATE["position_mutations"]
        real_orders = STATE["real_orders"]
        demo_orders = STATE["demo_orders"]

    require(
        network_writes == 0,
        "Network Writes Remain Zero"
    )

    require(
        leverage_mutations == 0,
        "Leverage Mutations Remain Zero"
    )

    require(
        margin_mutations == 0,
        "Margin Mutations Remain Zero"
    )

    require(
        position_mutations == 0,
        "Position Mutations Remain Zero"
    )

    require(
        real_orders == 0,
        "Real Orders Remain Zero"
    )

    require(
        demo_orders == 0,
        "Demo Orders Remain Zero"
    )

    require(
        correction_required is False,
        "Account Configuration Requires No Correction"
    )


    # =========================================================================
    # COMMIT READ-ONLY VALIDATED STATE
    # =========================================================================

    with STATE_LOCK:

        STATE["phase"] = (
            "LIVE_EXECUTION_READINESS_VALIDATED"
        )

        STATE["available_balance"] = decimal_text(
            balance
        )

        STATE["market_price"] = decimal_text(
            market_price
        )

        STATE["observed_margin"] = margin_type

        STATE["position_mode"] = (
            position_mode or "UNKNOWN"
        )

        STATE["observed_long"] = decimal_text(
            long_leverage
        )

        STATE["observed_short"] = decimal_text(
            short_leverage
        )

        STATE["correction_required"] = (
            correction_required
        )

        STATE["quantity_precision"] = (
            calc["quantity_precision"]
        )

        STATE["price_precision"] = (
            calc["price_precision"]
        )

        STATE["min_order_size"] = decimal_text(
            calc["min_order_size"]
        )

        STATE["max_leverage"] = decimal_text(
            calc["max_leverage"]
        )

        STATE["entry_margin_budget"] = decimal_text(
            calc["entry_margin_budget"]
        )

        STATE["planned_notional"] = decimal_text(
            calc["planned_notional"]
        )

        STATE["raw_quantity"] = decimal_text(
            calc["raw_quantity"]
        )

        STATE["rounded_quantity"] = decimal_text(
            calc["rounded_quantity"]
        )

        STATE["rounded_notional"] = decimal_text(
            calc["rounded_notional"]
        )

        STATE["estimated_margin"] = decimal_text(
            calc["estimated_margin"]
        )

        STATE["validation_passed"] = True


    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    pass_line(
        "Live Strategy / Account Execution Readiness"
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


# =============================================================================
# HEARTBEAT
# =============================================================================


def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        with STATE_LOCK:
            snapshot = dict(STATE)

        log(
            f"{VERSION}: HEARTBEAT {heartbeat}"
            f" | phase={snapshot['phase']}"
            f" | authenticated-read-only="
            f"{snapshot['authenticated_read_only']}"
            f" | authenticated-get="
            f"{snapshot['authenticated_gets']}"
            f" | public-get="
            f"{snapshot['public_gets']}"
            f" | network-writes="
            f"{snapshot['network_writes']}"
            f" | leverage-mutations="
            f"{snapshot['leverage_mutations']}"
            f" | real-orders="
            f"{snapshot['real_orders']}"
            f" | demo-orders="
            f"{snapshot['demo_orders']}"
            f" | correction-required="
            f"{snapshot['correction_required']}"
            f" | observed-margin="
            f"{snapshot['observed_margin']}"
            f" | observed-long="
            f"{snapshot['observed_long']}"
            f" | observed-short="
            f"{snapshot['observed_short']}"
            f" | target-long="
            f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
            f" | target-short="
            f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
            f" | entry-qty="
            f"{snapshot['rounded_quantity']}"
        )

        time.sleep(HEARTBEAT_SECONDS)


# =============================================================================
# MAIN
# =============================================================================


def main():

    start_health_server()

    try:

        run_validation()

    except Exception as exc:

        with STATE_LOCK:
            STATE["phase"] = "VALIDATION_FAILED"
            STATE["validation_passed"] = False

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        sys.exit(1)

    heartbeat_loop()


if __name__ == "__main__":
    main()
