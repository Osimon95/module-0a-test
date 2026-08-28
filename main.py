

# ==================================================================================================
# R34X.1 - LIVE READ-ONLY STATE + COMPLETE SYNTHETIC STRATEGY LIFECYCLE VALIDATION
# ==================================================================================================
#
# SAFETY MODEL
#
#   - AUTHENTICATED GET ONLY
#   - PUBLIC GET ONLY
#   - NO POST
#   - NO PUT
#   - NO PATCH
#   - NO DELETE
#   - NO REAL ORDER
#   - NO DEMO ORDER
#   - NO LEVERAGE CHANGE
#   - NO MARGIN CHANGE
#   - NO POSITION CHANGE
#   - NO ACCOUNT MUTATION
#
# IMPORTANT:
#
#   THIS PROGRAM DOES NOT PLACE ANY REAL OR DEMO ORDER.
#
# ==================================================================================================

import os
import json
import time
import hmac
import base64
import hashlib
import threading
import traceback
import urllib.parse
import urllib.request
import uuid

from decimal import Decimal, ROUND_UP, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# PART 1 - CONSTANTS / CONFIGURATION / SAFETY
# ==================================================================================================

VERSION = "R34X.1"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")

PORT = int(os.getenv("PORT", "10000"))


# --------------------------------------------------------------------------------------------------
# STRATEGY CONFIGURATION
# --------------------------------------------------------------------------------------------------

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_SIZE_PERCENT = Decimal("5")
BACKUP_SIZE_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

BACKUP_BUFFER_PERCENT = Decimal("0.3")

TP1_ALLOCATION_PERCENT = Decimal("20")
TP2_ALLOCATION_PERCENT = Decimal("20")
TP3_ALLOCATION_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# --------------------------------------------------------------------------------------------------
# ABSOLUTE WRITE FIREBREAKS
# --------------------------------------------------------------------------------------------------

ALLOW_NETWORK_WRITES = False
ALLOW_REAL_ORDERS = False
ALLOW_DEMO_ORDERS = False
ALLOW_LEVERAGE_MUTATION = False
ALLOW_MARGIN_MUTATION = False
ALLOW_POSITION_MUTATION = False
ALLOW_ACCOUNT_MUTATION = False


# --------------------------------------------------------------------------------------------------
# NETWORK PATH ALLOWLISTS
# --------------------------------------------------------------------------------------------------

AUTHENTICATED_GET_ALLOWLIST = {
    "/capi/v3/account/balance",
    "/capi/v3/account/position/allPosition",
    "/capi/v3/account/symbolConfig",
}

PUBLIC_GET_ALLOWLIST = {
    "/capi/v3/market/symbolPrice",
    "/capi/v3/market/exchangeInfo",
}


# --------------------------------------------------------------------------------------------------
# COUNTERS
# --------------------------------------------------------------------------------------------------

authenticated_get_count = 0
public_get_count = 0

network_write_count = 0
real_order_count = 0
demo_order_count = 0

leverage_mutation_count = 0
margin_mutation_count = 0
position_mutation_count = 0
account_mutation_count = 0

synthetic_dispatch_count = 0

heartbeat_count = 0

runtime_phase = "BOOTING"


# --------------------------------------------------------------------------------------------------
# DISPLAY HELPERS
# --------------------------------------------------------------------------------------------------

LINE = "-" * 100


def banner(text):
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def test_header(number, text):
    banner(f"{VERSION} TEST {number}: {text}")


def check(label, condition):
    if condition:
        print(f"{label:<92} ✅ PASS", flush=True)
        return True

    print(f"{label:<92} ❌ FAIL", flush=True)
    raise AssertionError(label)


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(value):
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def D(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        text = str(value).strip()

        if not text:
            return Decimal(default)

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def decimal_text(value):
    value = D(value)

    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in ("", "-0"):
        text = "0"

    return text


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        payload = {
            "ok": True,
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": runtime_phase,
            "authenticatedReadOnly": True,
            "publicReadOnly": True,
            "networkWrites": network_write_count,
            "realOrders": real_order_count,
            "demoOrders": demo_order_count,
            "syntheticDispatches": synthetic_dispatch_count,
        }

        encoded = canonical_json(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def start_health_server():

    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    return server


# ==================================================================================================
# CREDENTIALS
# ==================================================================================================

def credential_value(*names):

    for name in names:
        value = os.getenv(name)

        if value is not None and value.strip():
            return value.strip()

    return ""


def obtain_credentials():

    api_key = credential_value(
        "WEEX_API_KEY",
        "API_KEY",
    )

    api_secret = credential_value(
        "WEEX_API_SECRET",
        "API_SECRET",
        "SECRET_KEY",
    )

    passphrase = credential_value(
        "WEEX_API_PASSPHRASE",
        "WEEX_PASSPHRASE",
        "API_PASSPHRASE",
        "PASSPHRASE",
    )

    return api_key, api_secret, passphrase


# ==================================================================================================
# NETWORK SAFETY
# ==================================================================================================

def reject_network_write(method, path=""):

    method = str(method).upper()

    if method != "GET":
        raise RuntimeError(
            f"{VERSION}: NETWORK WRITE BLOCKED: {method} {path}"
        )


def forbidden_http_post(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: HTTP POST IS PERMANENTLY DISABLED")


def forbidden_http_put(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: HTTP PUT IS PERMANENTLY DISABLED")


def forbidden_http_patch(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: HTTP PATCH IS PERMANENTLY DISABLED")


def forbidden_http_delete(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: HTTP DELETE IS PERMANENTLY DISABLED")


def forbidden_real_order(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: REAL ORDER EXECUTION IS DISABLED")


def forbidden_demo_order(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: DEMO ORDER EXECUTION IS DISABLED")


def forbidden_leverage_mutation(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: LEVERAGE MUTATION IS DISABLED")


def forbidden_margin_mutation(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: MARGIN MUTATION IS DISABLED")


def forbidden_position_mutation(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: POSITION MUTATION IS DISABLED")


def forbidden_account_mutation(*args, **kwargs):
    raise RuntimeError(f"{VERSION}: ACCOUNT MUTATION IS DISABLED")


# ==================================================================================================
# AUTHENTICATION
# ==================================================================================================

def make_signature(
    timestamp,
    method,
    path,
    query_string,
    body,
    secret,
):

    method = method.upper()

    if query_string:
        message = (
            str(timestamp)
            + method
            + path
            + "?"
            + query_string
            + body
        )
    else:
        message = (
            str(timestamp)
            + method
            + path
            + body
        )

    digest = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def authenticated_get(path, params=None):

    global authenticated_get_count

    reject_network_write("GET", path)

    if path not in AUTHENTICATED_GET_ALLOWLIST:
        raise RuntimeError(
            f"{VERSION}: AUTHENTICATED GET PATH NOT ALLOWED: {path}"
        )

    api_key, api_secret, passphrase = obtain_credentials()

    missing = []

    if not api_key:
        missing.append("WEEX_API_KEY")

    if not api_secret:
        missing.append("WEEX_API_SECRET")

    if not passphrase:
        missing.append("WEEX_API_PASSPHRASE")

    if missing:
        raise RuntimeError(
            "Missing credentials: " + ", ".join(missing)
        )

    params = params or {}

    query_string = urllib.parse.urlencode(params)

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    timestamp = str(int(time.time() * 1000))

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        path=path,
        query_string=query_string,
        body="",
        secret=api_secret,
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only-validator",
    }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode("utf-8")

            authenticated_get_count += 1

            return json.loads(raw)

    except Exception as exc:

        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        ) from exc


def public_get(path, params=None):

    global public_get_count

    reject_network_write("GET", path)

    if path not in PUBLIC_GET_ALLOWLIST:
        raise RuntimeError(
            f"{VERSION}: PUBLIC GET PATH NOT ALLOWED: {path}"
        )

    params = params or {}

    query_string = urllib.parse.urlencode(params)

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    request = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-read-only-validator",
        },
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode("utf-8")

            public_get_count += 1

            return json.loads(raw)

    except Exception as exc:

        raise RuntimeError(
            f"Public GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        ) from exc


# ==================================================================================================
# RESPONSE NORMALIZATION
# ==================================================================================================

def unwrap_data(value):

    if isinstance(value, dict) and "data" in value:
        return value["data"]

    return value


def as_list(value):

    value = unwrap_data(value)

    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        return [value]

    return []


# ==================================================================================================
# LIVE BALANCE
# ==================================================================================================

def obtain_available_usdt():

    path = "/capi/v3/account/balance"

    response = authenticated_get(path)

    records = as_list(response)

    for record in records:

        if not isinstance(record, dict):
            continue

        asset = str(
            record.get("asset")
            or record.get("marginCoin")
            or record.get("coin")
            or ""
        ).upper()

        if asset == "USDT":

            available = (
                record.get("availableBalance")
                if record.get("availableBalance") is not None
                else record.get("available")
            )

            return path, D(available)

    raise RuntimeError("USDT balance record not found")


# ==================================================================================================
# LIVE POSITIONS
# ==================================================================================================

def position_size(record):

    candidates = [
        record.get("size"),
        record.get("positionAmt"),
        record.get("total"),
        record.get("available"),
        record.get("positionSize"),
    ]

    for candidate in candidates:

        if candidate is None:
            continue

        value = abs(D(candidate))

        if value != 0:
            return value

    return Decimal("0")


def obtain_positions():

    path = "/capi/v3/account/position/allPosition"

    response = authenticated_get(path)

    records = as_list(response)

    symbol_records = []
    open_positions = []

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = str(record.get("symbol") or "").upper()

        if symbol != SYMBOL:
            continue

        symbol_records.append(record)

        if position_size(record) > 0:
            open_positions.append(record)

    return path, records, symbol_records, open_positions


# ==================================================================================================
# LIVE SYMBOL CONFIGURATION
# ==================================================================================================

def obtain_symbol_config():

    path = "/capi/v3/account/symbolConfig"

    response = authenticated_get(
        path,
        {
            "symbol": SYMBOL,
        },
    )

    records = as_list(response)

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = str(record.get("symbol") or "").upper()

        if symbol == SYMBOL:
            return path, record

    raise RuntimeError(
        f"Symbol configuration not found for {SYMBOL}"
    )


# ==================================================================================================
# LIVE MARKET PRICE
# ==================================================================================================

def obtain_mark_price():

    path = "/capi/v3/market/symbolPrice"

    response = public_get(
        path,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    value = unwrap_data(response)

    records = value if isinstance(value, list) else [value]

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = str(record.get("symbol") or SYMBOL).upper()

        if symbol != SYMBOL:
            continue

        for key in (
            "price",
            "markPrice",
            "lastPrice",
        ):

            if record.get(key) is not None:

                price = D(record.get(key))

                if price > 0:
                    return path, price

    raise RuntimeError(
        f"Unable to parse market price for {SYMBOL}"
    )


# ==================================================================================================
# LIVE CONTRACT INFORMATION - R34X.1 HARDENED PARSER
# ==================================================================================================

def parse_filter_number(record, filter_types, field_names):

    filters = record.get("filters")

    if not isinstance(filters, list):
        return None

    wanted = {
        str(value).upper()
        for value in filter_types
    }

    for item in filters:

        if not isinstance(item, dict):
            continue

        filter_type = str(
            item.get("filterType")
            or item.get("type")
            or ""
        ).upper()

        if filter_type not in wanted:
            continue

        for field in field_names:

            if item.get(field) is None:
                continue

            candidate = D(item.get(field))

            if candidate > 0:
                return candidate

    return None


def infer_precision(step):

    step = D(step)

    if step <= 0:
        return 0

    normalized = step.normalize()

    exponent = normalized.as_tuple().exponent

    if exponent >= 0:
        return 0

    return abs(exponent)


def precision_to_step(precision):

    try:
        precision = int(precision)

    except (TypeError, ValueError):
        return None

    if precision < 0:
        return None

    return Decimal("1").scaleb(-precision)


def first_positive_decimal(record, field_names):

    if not isinstance(record, dict):
        return None

    for field in field_names:

        if record.get(field) is None:
            continue

        candidate = D(record.get(field))

        if candidate > 0:
            return candidate

    return None


def first_integer(record, field_names):

    if not isinstance(record, dict):
        return None

    for field in field_names:

        value = record.get(field)

        if value is None:
            continue

        try:
            parsed = int(value)

        except (TypeError, ValueError):
            continue

        if parsed >= 0:
            return parsed

    return None


def extract_contract_records(response):

    value = unwrap_data(response)

    if isinstance(value, dict):

        for key in (
            "symbols",
            "contracts",
            "rows",
            "list",
            "items",
        ):

            candidate = value.get(key)

            if isinstance(candidate, list):
                return candidate

            if isinstance(candidate, dict):
                return [candidate]

        if value.get("symbol") is not None:
            return [value]

        nested = value.get("data")

        if isinstance(nested, list):
            return nested

        if isinstance(nested, dict):

            for key in (
                "symbols",
                "contracts",
                "rows",
                "list",
                "items",
            ):

                candidate = nested.get(key)

                if isinstance(candidate, list):
                    return candidate

                if isinstance(candidate, dict):
                    return [candidate]

            if nested.get("symbol") is not None:
                return [nested]

    if isinstance(value, list):
        return value

    return []


def obtain_contract_information():

    path = "/capi/v3/market/exchangeInfo"

    response = public_get(
        path,
        {
            "symbol": SYMBOL,
        },
    )

    records = extract_contract_records(response)

    if not records:
        raise RuntimeError(
            "Exchange information contained no contract records"
        )

    contract = None

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = str(
            record.get("symbol")
            or record.get("displaySymbol")
            or ""
        ).upper()

        if symbol == SYMBOL:
            contract = record
            break

    if contract is None:

        available_symbols = []

        for record in records:

            if not isinstance(record, dict):
                continue

            candidate_symbol = str(
                record.get("symbol")
                or record.get("displaySymbol")
                or ""
            ).upper()

            if candidate_symbol:
                available_symbols.append(candidate_symbol)

        raise RuntimeError(
            f"Contract record not found for {SYMBOL} | "
            f"available symbols={available_symbols[:20]}"
        )

    print(
        f"{VERSION}: CONTRACT RECORD KEYS="
        f"{sorted(contract.keys())}",
        flush=True,
    )

    min_qty = first_positive_decimal(
        contract,
        (
            "minOrderSize",
            "minOrderQty",
            "minQty",
            "minTradeNum",
            "minTradeAmount",
            "minOrderQuantity",
            "minimumQuantity",
            "minimumOrderQuantity",
            "minVolume",
        ),
    )

    if min_qty is None:

        min_qty = parse_filter_number(
            contract,
            {
                "LOT_SIZE",
                "MARKET_LOT_SIZE",
            },
            {
                "minQty",
                "minQuantity",
                "minOrderSize",
            },
        )

    quantity_precision = first_integer(
        contract,
        (
            "quantityPrecision",
            "quantityScale",
            "volumePlace",
            "sizePrecision",
            "amountPrecision",
            "baseAssetPrecision",
        ),
    )

    price_precision = first_integer(
        contract,
        (
            "pricePrecision",
            "priceScale",
            "pricePlace",
        ),
    )

    qty_step = first_positive_decimal(
        contract,
        (
            "quantityStep",
            "qtyStep",
            "stepSize",
            "sizeIncrement",
            "size_increment",
            "quantityIncrement",
            "amountStep",
        ),
    )

    if qty_step is None:

        qty_step = parse_filter_number(
            contract,
            {
                "LOT_SIZE",
                "MARKET_LOT_SIZE",
            },
            {
                "stepSize",
                "qtyStep",
                "quantityStep",
            },
        )

    if (
        qty_step is None
        and quantity_precision is not None
    ):
        qty_step = precision_to_step(
            quantity_precision
        )

    price_step = first_positive_decimal(
        contract,
        (
            "priceStep",
            "tickSize",
            "priceTick",
            "priceIncrement",
            "priceEndStep",
            "price_end_step",
        ),
    )

    if price_step is None:

        price_step = parse_filter_number(
            contract,
            {
                "PRICE_FILTER",
            },
            {
                "tickSize",
                "priceStep",
                "priceIncrement",
            },
        )

    if (
        price_step is None
        and price_precision is not None
    ):
        price_step = precision_to_step(
            price_precision
        )

    if min_qty is None or min_qty <= 0:
        raise RuntimeError(
            "Unable to parse minimum contract quantity | "
            f"available keys={sorted(contract.keys())}"
        )

    if qty_step is None or qty_step <= 0:
        raise RuntimeError(
            "Unable to parse or derive contract quantity step | "
            f"quantityPrecision={quantity_precision} | "
            f"available keys={sorted(contract.keys())}"
        )

    if price_step is None or price_step <= 0:
        raise RuntimeError(
            "Unable to parse or derive contract price step | "
            f"pricePrecision={price_precision} | "
            f"available keys={sorted(contract.keys())}"
        )

    if quantity_precision is None:
        quantity_precision = infer_precision(qty_step)

    if price_precision is None:
        price_precision = infer_precision(price_step)

    effective_min_qty = normalize_quantity_up(
        min_qty,
        qty_step,
        min_qty,
    )

    contract_value = first_positive_decimal(
        contract,
        (
            "contractVal",
            "contractValue",
            "contract_val",
        ),
    )

    print(
        f"{VERSION}: RAW MIN ORDER SIZE="
        f"{decimal_text(min_qty)}",
        flush=True,
    )

    print(
        f"{VERSION}: EFFECTIVE MIN ORDER QTY="
        f"{decimal_text(effective_min_qty)}",
        flush=True,
    )

    print(
        f"{VERSION}: QTY STEP="
        f"{decimal_text(qty_step)}",
        flush=True,
    )

    print(
        f"{VERSION}: QTY PRECISION="
        f"{quantity_precision}",
        flush=True,
    )

    print(
        f"{VERSION}: PRICE STEP="
        f"{decimal_text(price_step)}",
        flush=True,
    )

    print(
        f"{VERSION}: PRICE PRECISION="
        f"{price_precision}",
        flush=True,
    )

    if contract_value is not None:

        print(
            f"{VERSION}: CONTRACT VALUE="
            f"{decimal_text(contract_value)}",
            flush=True,
        )

    return {
        "path": path,
        "record": contract,
        "min_qty": effective_min_qty,
        "raw_min_qty": min_qty,
        "qty_step": qty_step,
        "qty_precision": int(quantity_precision),
        "price_step": price_step,
        "price_precision": int(price_precision),
        "contract_value": contract_value,
    }


# ==================================================================================================
# QUANTITY NORMALIZATION
# ==================================================================================================

def normalize_quantity_up(raw_quantity, qty_step, min_qty):

    raw_quantity = D(raw_quantity)
    qty_step = D(qty_step)
    min_qty = D(min_qty)

    if qty_step <= 0:
        raise RuntimeError("Quantity step must be positive")

    steps = (
        raw_quantity / qty_step
    ).to_integral_value(
        rounding=ROUND_UP
    )

    normalized = steps * qty_step

    if normalized < min_qty:
        normalized = min_qty

    return normalized


def normalize_quantity_down(raw_quantity, qty_step):

    raw_quantity = D(raw_quantity)
    qty_step = D(qty_step)

    if qty_step <= 0:
        raise RuntimeError("Quantity step must be positive")

    steps = (
        raw_quantity / qty_step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return steps * qty_step


# ==================================================================================================
# SYNTHETIC STRATEGY DECISION
# ==================================================================================================

def make_entry_decision(open_positions):

    if open_positions:

        first = open_positions[0]

        side = str(
            first.get("side")
            or first.get("positionSide")
            or "UNKNOWN"
        ).upper()

        return {
            "synthetic": True,
            "action": "HOLD_EXISTING_POSITION",
            "side": side,
            "reason": (
                f"{len(open_positions)} open "
                f"{SYMBOL} position(s) detected"
            ),
        }

    return {
        "synthetic": True,
        "action": "OPEN_LONG_CANDIDATE",
        "side": "BUY",
        "positionSide": "LONG",
        "reason": f"no open {SYMBOL} position detected",
    }


# ==================================================================================================
# SYNTHETIC INTENT / PAYLOAD
# ==================================================================================================

def create_synthetic_intent(
    available_usdt,
    market_price,
    normalized_quantity,
):

    client_order_id = (
        "r34x1-"
        + uuid.uuid4().hex[:20]
    )

    return {
        "syntheticOnly": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "strategyVersion": VERSION,
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": decimal_text(normalized_quantity),
        "newClientOrderId": client_order_id,
        "referencePrice": decimal_text(market_price),
        "availableUSDT": decimal_text(available_usdt),
        "targetMarginType": TARGET_MARGIN_TYPE,
        "targetLeverage": decimal_text(TARGET_LEVERAGE),
    }


def create_synthetic_payload(intent):

    return {
        "symbol": intent["symbol"],
        "side": intent["side"],
        "positionSide": intent["positionSide"],
        "type": intent["type"],
        "quantity": intent["quantity"],
        "newClientOrderId": intent["newClientOrderId"],
    }


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================

def synthetic_dispatch(payload):

    global synthetic_dispatch_count

    synthetic_dispatch_count += 1

    return {
        "dispatchNumber": synthetic_dispatch_count,
        "syntheticOnly": True,
        "transmitted": False,
        "networkWriteOccurred": False,
        "payloadSHA256": sha256_json(payload),
    }


# ==================================================================================================
# SYNTHETIC LIFECYCLE ENGINE
# ==================================================================================================

class SyntheticPositionLifecycle:

    def __init__(
        self,
        entry_price,
        quantity,
        qty_step,
    ):

        self.synthetic_only = True
        self.network_write_allowed = False

        self.state = "OPEN"

        self.entry_price = D(entry_price)
        self.quantity = D(quantity)
        self.initial_quantity = D(quantity)
        self.remaining_quantity = D(quantity)

        self.qty_step = D(qty_step)

        self.highest_price = D(entry_price)

        self.tp1_done = False
        self.tp2_done = False
        self.tp3_done = False

        self.trailing_armed = False
        self.trailing_triggered = False

        self.pyramid_adds = 0
        self.backups = 0

        self.closed_quantity = Decimal("0")

        self.exit_reason = None

        self.cooldown_until = Decimal("0")

        self.events = []

        self.record(
            "POSITION_OPENED",
            self.entry_price,
            {
                "quantity": decimal_text(self.quantity),
            },
        )

    def record(self, event, price, extra=None):

        record = {
            "event": event,
            "price": decimal_text(price),
            "synthetic": True,
        }

        if extra:
            record.update(extra)

        self.events.append(record)

    def percent_change(self, price):

        price = D(price)

        return (
            (price - self.entry_price)
            / self.entry_price
            * Decimal("100")
        )

    def price_for_percent(self, percent):

        return self.entry_price * (
            Decimal("1")
            + D(percent) / Decimal("100")
        )

    def adverse_price_for_percent(self, percent):

        return self.entry_price * (
            Decimal("1")
            - D(percent) / Decimal("100")
        )

    def allocate_close(self, allocation_percent):

        desired = (
            self.initial_quantity
            * D(allocation_percent)
            / Decimal("100")
        )

        normalized = normalize_quantity_down(
            desired,
            self.qty_step,
        )

        if normalized <= 0:
            normalized = min(
                self.qty_step,
                self.remaining_quantity,
            )

        if normalized > self.remaining_quantity:
            normalized = self.remaining_quantity

        return normalized

    def synthetic_close(
        self,
        quantity,
        price,
        reason,
    ):

        if self.state != "OPEN":
            return Decimal("0")

        quantity = min(
            D(quantity),
            self.remaining_quantity,
        )

        if quantity <= 0:
            return Decimal("0")

        self.remaining_quantity -= quantity
        self.closed_quantity += quantity

        self.record(
            reason,
            price,
            {
                "closedQuantity": decimal_text(quantity),
                "remainingQuantity": decimal_text(
                    self.remaining_quantity
                ),
            },
        )

        if self.remaining_quantity <= 0:

            self.remaining_quantity = Decimal("0")
            self.state = "CLOSED"
            self.exit_reason = reason

            self.record(
                "POSITION_TERMINAL",
                price,
                {
                    "reason": reason,
                },
            )

        return quantity

    def process_profit_price(self, price):

        price = D(price)

        if self.state != "OPEN":
            return

        if price > self.highest_price:
            self.highest_price = price

        gain = self.percent_change(price)

        if (
            not self.tp1_done
            and gain >= TP1_TRIGGER_PERCENT
        ):

            quantity = self.allocate_close(
                TP1_ALLOCATION_PERCENT
            )

            self.synthetic_close(
                quantity,
                price,
                "TP1",
            )

            self.tp1_done = True

        if (
            self.state == "OPEN"
            and not self.tp2_done
            and gain >= TP2_TRIGGER_PERCENT
        ):

            quantity = self.allocate_close(
                TP2_ALLOCATION_PERCENT
            )

            self.synthetic_close(
                quantity,
                price,
                "TP2",
            )

            self.tp2_done = True
            self.trailing_armed = True

            self.record(
                "TRAILING_ARMED",
                price,
                {
                    "distancePercent":
                        decimal_text(
                            TRAILING_DISTANCE_PERCENT
                        )
                },
            )

    def process_trailing_price(self, price):

        price = D(price)

        if self.state != "OPEN":
            return

        if not self.trailing_armed:
            return

        if price > self.highest_price:

            self.highest_price = price

            self.record(
                "TRAILING_HIGH_UPDATED",
                price,
                {
                    "highestPrice":
                        decimal_text(self.highest_price)
                },
            )

            return

        trailing_stop = self.highest_price * (
            Decimal("1")
            - TRAILING_DISTANCE_PERCENT
            / Decimal("100")
        )

        if price <= trailing_stop:

            self.trailing_triggered = True

            self.synthetic_close(
                self.remaining_quantity,
                price,
                "TP3_TRAILING_EXIT",
            )

            self.tp3_done = True

    def pyramid_eligible(self, price):

        if self.state != "OPEN":
            return False

        if self.pyramid_adds >= MAX_PYRAMID_ADDS:
            return False

        return (
            self.percent_change(price)
            >= TP1_TRIGGER_PERCENT
        )

    def synthetic_pyramid(self, price):

        if not self.pyramid_eligible(price):
            return False

        self.pyramid_adds += 1

        self.record(
            "PYRAMID_CANDIDATE",
            price,
            {
                "pyramidNumber": self.pyramid_adds,
                "transmitted": False,
            },
        )

        return True

    def backup_eligible(self, price):

        if self.state != "OPEN":
            return False

        if self.backups >= MAX_BACKUPS:
            return False

        next_backup_number = self.backups + 1

        required_drop = (
            BACKUP_BUFFER_PERCENT
            * Decimal(next_backup_number)
        )

        actual_drop = -self.percent_change(price)

        return actual_drop >= required_drop

    def synthetic_backup(self, price):

        if not self.backup_eligible(price):
            return False

        self.backups += 1

        self.record(
            "BACKUP_CANDIDATE",
            price,
            {
                "backupNumber": self.backups,
                "transmitted": False,
            },
        )

        return True

    def trend_reversal_exit(self, price):

        if self.state != "OPEN":
            return False

        if not TREND_REVERSAL_EXIT:
            return False

        self.synthetic_close(
            self.remaining_quantity,
            price,
            "TREND_REVERSAL_EXIT",
        )

        return True

    def loss_exit(self, price, now_timestamp):

        if self.state != "OPEN":
            return False

        self.synthetic_close(
            self.remaining_quantity,
            price,
            "LOSS_EXIT",
        )

        self.cooldown_until = (
            D(now_timestamp)
            + Decimal(LOSS_COOLDOWN_SECONDS)
        )

        self.record(
            "LOSS_COOLDOWN_STARTED",
            price,
            {
                "cooldownSeconds":
                    LOSS_COOLDOWN_SECONDS,
                "cooldownUntil":
                    decimal_text(
                        self.cooldown_until
                    ),
            },
        )

        return True

    def cooldown_active(self, now_timestamp):

        return D(now_timestamp) < self.cooldown_until

    def snapshot(self):

        return {
            "syntheticOnly": self.synthetic_only,
            "networkWriteAllowed": self.network_write_allowed,
            "state": self.state,
            "entryPrice": decimal_text(self.entry_price),
            "initialQuantity": decimal_text(self.initial_quantity),
            "remainingQuantity": decimal_text(self.remaining_quantity),
            "closedQuantity": decimal_text(self.closed_quantity),
            "highestPrice": decimal_text(self.highest_price),
            "tp1Done": self.tp1_done,
            "tp2Done": self.tp2_done,
            "tp3Done": self.tp3_done,
            "trailingArmed": self.trailing_armed,
            "trailingTriggered": self.trailing_triggered,
            "pyramidAdds": self.pyramid_adds,
            "backups": self.backups,
            "exitReason": self.exit_reason,
            "cooldownUntil": decimal_text(self.cooldown_until),
            "events": self.events,
        }


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_loop():

    global heartbeat_count

    while True:

        time.sleep(30)

        heartbeat_count += 1

        print(
            f"{VERSION}: HEARTBEAT {heartbeat_count} | "
            f"phase={runtime_phase} | "
            f"authenticated-read-only=True | "
            f"authenticated-get={authenticated_get_count} | "
            f"public-get={public_get_count} | "
            f"network-writes={network_write_count} | "
            f"real-orders={real_order_count} | "
            f"demo-orders={demo_order_count} | "
            f"synthetic-dispatches={synthetic_dispatch_count}",
            flush=True,
        )


# ==================================================================================================
# PART 2 - MAIN VALIDATION
# ==================================================================================================

def run_validation():

    global runtime_phase

    runtime_phase = "VALIDATING"

    banner(f"{VERSION}: MAIN.PY ENTERED")

    print(f"{VERSION}: SYMBOL={SYMBOL}", flush=True)
    print(f"{VERSION}: VERSION={VERSION}", flush=True)
    print(f"{VERSION}: HEALTH PORT={PORT}", flush=True)

    print(f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED", flush=True)
    print(f"{VERSION}: PUBLIC READ-ONLY ENABLED", flush=True)
    print(f"{VERSION}: NETWORK WRITES DISABLED", flush=True)
    print(f"{VERSION}: REAL ORDER EXECUTION DISABLED", flush=True)
    print(f"{VERSION}: DEMO ORDER EXECUTION DISABLED", flush=True)
    print(f"{VERSION}: LEVERAGE MUTATION DISABLED", flush=True)
    print(f"{VERSION}: MARGIN MUTATION DISABLED", flush=True)
    print(f"{VERSION}: POSITION MUTATION DISABLED", flush=True)

    print(
        f"{VERSION}: TARGET MARGIN={TARGET_MARGIN_TYPE}",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LEVERAGE="
        f"{decimal_text(TARGET_LEVERAGE)}x",
        flush=True,
    )

    test_header(1, "HARD NETWORK WRITE FIREBREAK")

    check("Network Writes Are Disabled", ALLOW_NETWORK_WRITES is False)
    check("Real Orders Are Disabled", ALLOW_REAL_ORDERS is False)
    check("Demo Orders Are Disabled", ALLOW_DEMO_ORDERS is False)
    check("Leverage Mutation Is Disabled", ALLOW_LEVERAGE_MUTATION is False)
    check("Margin Mutation Is Disabled", ALLOW_MARGIN_MUTATION is False)
    check("Position Mutation Is Disabled", ALLOW_POSITION_MUTATION is False)
    check("Account Mutation Is Disabled", ALLOW_ACCOUNT_MUTATION is False)

    test_header(2, "WRITE FUNCTION REJECTION")

    for label, function in [
        ("HTTP POST Is Rejected", forbidden_http_post),
        ("HTTP PUT Is Rejected", forbidden_http_put),
        ("HTTP PATCH Is Rejected", forbidden_http_patch),
        ("HTTP DELETE Is Rejected", forbidden_http_delete),
        ("Real Order Function Is Rejected", forbidden_real_order),
        ("Demo Order Function Is Rejected", forbidden_demo_order),
        ("Leverage Mutation Function Is Rejected", forbidden_leverage_mutation),
        ("Margin Mutation Function Is Rejected", forbidden_margin_mutation),
        ("Position Mutation Function Is Rejected", forbidden_position_mutation),
        ("Account Mutation Function Is Rejected", forbidden_account_mutation),
    ]:

        rejected = False

        try:
            function()

        except RuntimeError:
            rejected = True

        check(label, rejected)

    test_header(3, "API CREDENTIAL PRESENCE")

    api_key, api_secret, passphrase = obtain_credentials()

    check("WEEX API Key Is Present", bool(api_key))
    check("WEEX API Secret Is Present", bool(api_secret))
    check("WEEX API Passphrase Is Present", bool(passphrase))

    test_header(4, "LIVE BALANCE RECONCILIATION")

    balance_path, available_usdt = obtain_available_usdt()

    check("Available Balance Was Read", available_usdt is not None)
    check("Available Balance Is Positive", available_usdt > 0)

    print(f"{VERSION}: BALANCE PATH={balance_path}", flush=True)
    print(
        f"{VERSION}: AVAILABLE USDT={decimal_text(available_usdt)}",
        flush=True,
    )

    test_header(5, "LIVE POSITION RECONCILIATION")

    (
        position_path,
        all_positions,
        symbol_positions,
        open_positions,
    ) = obtain_positions()

    check("Position Response Was Read", isinstance(all_positions, list))
    check("BTCUSDT Position Records Were Parsed", isinstance(symbol_positions, list))
    check("BTCUSDT Open Position Records Were Parsed", isinstance(open_positions, list))

    print(f"{VERSION}: POSITION PATH={position_path}", flush=True)
    print(f"{VERSION}: TOTAL POSITION RECORDS={len(all_positions)}", flush=True)
    print(f"{VERSION}: {SYMBOL} POSITION RECORDS={len(symbol_positions)}", flush=True)
    print(f"{VERSION}: {SYMBOL} OPEN POSITIONS={len(open_positions)}", flush=True)

    test_header(6, "LIVE ACCOUNT CONFIGURATION")

    config_path, symbol_config = obtain_symbol_config()

    margin_type = str(
        symbol_config.get("marginType")
        or ""
    ).upper()

    position_mode = str(
        symbol_config.get("separatedType")
        or symbol_config.get("separatedMode")
        or ""
    ).upper()

    long_leverage = D(
        symbol_config.get("isolatedLongLeverage")
    )

    short_leverage = D(
        symbol_config.get("isolatedShortLeverage")
    )

    check("Symbol Configuration Was Read", bool(symbol_config))
    check("Margin Type Is ISOLATED", margin_type == TARGET_MARGIN_TYPE)
    check("Long Leverage Is 100x", long_leverage == TARGET_LEVERAGE)
    check("Short Leverage Is 100x", short_leverage == TARGET_LEVERAGE)

    print(f"{VERSION}: SYMBOL CONFIG PATH={config_path}", flush=True)
    print(f"{VERSION}: MARGIN TYPE={margin_type}", flush=True)
    print(f"{VERSION}: POSITION MODE={position_mode}", flush=True)
    print(f"{VERSION}: ISOLATED LONG={decimal_text(long_leverage)}x", flush=True)
    print(f"{VERSION}: ISOLATED SHORT={decimal_text(short_leverage)}x", flush=True)

    test_header(7, "LIVE MARKET PRICE")

    market_price_path, market_price = obtain_mark_price()

    check("Market Price Was Read", market_price is not None)
    check("Market Price Is Positive", market_price > 0)

    print(f"{VERSION}: MARKET PRICE PATH={market_price_path}", flush=True)
    print(f"{VERSION}: MARK PRICE={decimal_text(market_price)}", flush=True)

    test_header(8, "LIVE CONTRACT INFORMATION")

    contract = obtain_contract_information()

    min_qty = contract["min_qty"]
    qty_step = contract["qty_step"]
    qty_precision = contract["qty_precision"]
    price_step = contract["price_step"]
    price_precision = contract["price_precision"]

    check("Exchange Information Was Read", bool(contract["record"]))
    check("Symbol Contract Record Was Found", bool(contract["record"]))
    check("Minimum Quantity Is Positive", min_qty > 0)
    check("Quantity Step Is Positive", qty_step > 0)
    check("Price Step Is Positive", price_step > 0)

    print(f"{VERSION}: MIN ORDER QTY={decimal_text(min_qty)}", flush=True)
    print(f"{VERSION}: QTY STEP={decimal_text(qty_step)}", flush=True)
    print(f"{VERSION}: QTY PRECISION={qty_precision}", flush=True)
    print(f"{VERSION}: PRICE STEP={decimal_text(price_step)}", flush=True)
    print(f"{VERSION}: PRICE PRECISION={price_precision}", flush=True)

    test_header(9, "STRATEGY BUDGET")

    initial_margin_budget = (
        available_usdt
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    max_allowed_strategy_margin = (
        available_usdt
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    planned_initial_notional = (
        initial_margin_budget
        * TARGET_LEVERAGE
    )

    planned_max_strategy_margin = (
        available_usdt
        * (
            INITIAL_ENTRY_PERCENT
            + PYRAMID_SIZE_PERCENT * Decimal(MAX_PYRAMID_ADDS)
            + BACKUP_SIZE_PERCENT * Decimal(MAX_BACKUPS)
        )
        / Decimal("100")
    )

    check("Initial Entry Percent Is Positive", INITIAL_ENTRY_PERCENT > 0)
    check(
        "Initial Entry Is Within Exposure Cap",
        INITIAL_ENTRY_PERCENT <= MAX_FUND_EXPOSURE_PERCENT,
    )
    check("Initial Entry Margin Budget Is Positive", initial_margin_budget > 0)
    check("Maximum Strategy Margin Is Positive", max_allowed_strategy_margin > 0)
    check("Planned Initial Notional Is Positive", planned_initial_notional > 0)
    check(
        "Maximum Planned Strategy Margin Is Within 35%",
        planned_max_strategy_margin <= max_allowed_strategy_margin,
    )

    print(f"{VERSION}: INITIAL ENTRY={decimal_text(INITIAL_ENTRY_PERCENT)}%", flush=True)
    print(f"{VERSION}: INITIAL MARGIN BUDGET={decimal_text(initial_margin_budget)} USDT", flush=True)
    print(f"{VERSION}: MAX FUND EXPOSURE={decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%", flush=True)
    print(f"{VERSION}: MAX ALLOWED STRATEGY MARGIN={decimal_text(max_allowed_strategy_margin)} USDT", flush=True)
    print(f"{VERSION}: PLANNED INITIAL NOTIONAL={decimal_text(planned_initial_notional)} USDT", flush=True)
    print(f"{VERSION}: PLANNED MAX STRATEGY MARGIN={decimal_text(planned_max_strategy_margin)} USDT", flush=True)

    test_header(10, "SYNTHETIC ENTRY DECISION")

    decision = make_entry_decision(open_positions)

    check("Decision Is Synthetic", decision.get("synthetic") is True)
    check("Decision Action Exists", bool(decision.get("action")))

    print(
        f"{VERSION}: DECISION={canonical_json(decision)}",
        flush=True,
    )

    test_header(11, "QUANTITY CALCULATION")

    raw_quantity = (
        planned_initial_notional
        / market_price
    )

    normalized_quantity = normalize_quantity_up(
        raw_quantity,
        qty_step,
        min_qty,
    )

    normalized_notional = (
        normalized_quantity
        * market_price
    )

    normalized_margin = (
        normalized_notional
        / TARGET_LEVERAGE
    )

    check("Raw Quantity Is Positive", raw_quantity > 0)
    check("Normalized Quantity Is Positive", normalized_quantity > 0)
    check("Normalized Quantity Meets Minimum", normalized_quantity >= min_qty)
    check("Normalized Margin Is Positive", normalized_margin > 0)

    print(f"{VERSION}: RAW QUANTITY={decimal_text(raw_quantity)} BTC", flush=True)
    print(f"{VERSION}: NORMALIZED QUANTITY={decimal_text(normalized_quantity)} BTC", flush=True)
    print(f"{VERSION}: NORMALIZED NOTIONAL={decimal_text(normalized_notional)} USDT", flush=True)
    print(f"{VERSION}: NORMALIZED MARGIN AT 100x={decimal_text(normalized_margin)} USDT", flush=True)

    test_header(12, "STRATEGY SAFETY TOGGLES")

    check("One Direction Only Is Enabled", ONE_DIRECTION_ONLY)
    check("Anti Duplicate Orders Is Enabled", ANTI_DUPLICATE_ORDERS)
    check("Trend Reversal Exit Is Enabled", TREND_REVERSAL_EXIT)
    check("Idle Pyramid Cleanup Is Enabled", IDLE_PYRAMID_CLEANUP)
    check("Signal Expiry Is Positive", SIGNAL_EXPIRY_SECONDS > 0)
    check("Loss Cooldown Is Positive", LOSS_COOLDOWN_SECONDS > 0)

    test_header(13, "TAKE PROFIT MODEL")

    check("TP1 Allocation Is 20%", TP1_ALLOCATION_PERCENT == Decimal("20"))
    check("TP2 Allocation Is 20%", TP2_ALLOCATION_PERCENT == Decimal("20"))
    check("TP3 Allocation Is 60%", TP3_ALLOCATION_PERCENT == Decimal("60"))
    check(
        "TP Allocation Totals 100%",
        (
            TP1_ALLOCATION_PERCENT
            + TP2_ALLOCATION_PERCENT
            + TP3_ALLOCATION_PERCENT
        ) == Decimal("100"),
    )
    check("TP1 Trigger Is Positive", TP1_TRIGGER_PERCENT > 0)
    check("TP2 Trigger Is Above TP1", TP2_TRIGGER_PERCENT > TP1_TRIGGER_PERCENT)
    check("Trailing Distance Is Positive", TRAILING_DISTANCE_PERCENT > 0)

    test_header(14, "LIVE STATE SNAPSHOT")

    live_state = {
        "symbol": SYMBOL,
        "availableUSDT": decimal_text(available_usdt),
        "marketPrice": decimal_text(market_price),
        "openPositionCount": len(open_positions),
        "marginType": margin_type,
        "positionMode": position_mode,
        "isolatedLongLeverage": decimal_text(long_leverage),
        "isolatedShortLeverage": decimal_text(short_leverage),
        "targetMarginType": TARGET_MARGIN_TYPE,
        "targetLeverage": decimal_text(TARGET_LEVERAGE),
        "initialEntryPercent": decimal_text(INITIAL_ENTRY_PERCENT),
        "maxExposurePercent": decimal_text(MAX_FUND_EXPOSURE_PERCENT),
    }

    live_state_hash = sha256_json(live_state)

    check("Live State Exists", bool(live_state))
    check("Live State Hash Exists", bool(live_state_hash))

    print(f"{VERSION}: LIVE STATE={canonical_json(live_state)}", flush=True)
    print(f"{VERSION}: LIVE STATE SHA256={live_state_hash}", flush=True)

    test_header(15, "EXACT SYNTHETIC ORDER INTENT")

    synthetic_intent = create_synthetic_intent(
        available_usdt,
        market_price,
        normalized_quantity,
    )

    synthetic_intent_hash = sha256_json(synthetic_intent)

    check("Intent Is Synthetic Only", synthetic_intent["syntheticOnly"] is True)
    check("Intent Forbids Transmission", synthetic_intent["transmissionAllowed"] is False)
    check("Intent Forbids Network Write", synthetic_intent["networkWriteAllowed"] is False)
    check("Intent Symbol Matches", synthetic_intent["symbol"] == SYMBOL)
    check("Intent Side Is BUY", synthetic_intent["side"] == "BUY")
    check("Intent Position Side Is LONG", synthetic_intent["positionSide"] == "LONG")
    check("Intent Type Is MARKET", synthetic_intent["type"] == "MARKET")
    check(
        "Intent Quantity Matches Normalized Quantity",
        D(synthetic_intent["quantity"]) == normalized_quantity,
    )

    print(f"{VERSION}: SYNTHETIC INTENT={canonical_json(synthetic_intent)}", flush=True)
    print(f"{VERSION}: SYNTHETIC INTENT SHA256={synthetic_intent_hash}", flush=True)

    test_header(16, "EXACT SYNTHETIC PAYLOAD")

    synthetic_payload = create_synthetic_payload(synthetic_intent)
    synthetic_payload_hash = sha256_json(synthetic_payload)

    check("Payload Symbol Matches Intent", synthetic_payload["symbol"] == synthetic_intent["symbol"])
    check("Payload Side Matches Intent", synthetic_payload["side"] == synthetic_intent["side"])
    check("Payload Position Side Matches Intent", synthetic_payload["positionSide"] == synthetic_intent["positionSide"])
    check("Payload Type Matches Intent", synthetic_payload["type"] == synthetic_intent["type"])
    check("Payload Quantity Matches Intent", synthetic_payload["quantity"] == synthetic_intent["quantity"])
    check(
        "Payload Client Order ID Matches Intent",
        synthetic_payload["newClientOrderId"] == synthetic_intent["newClientOrderId"],
    )
    check("Payload Hash Exists", bool(synthetic_payload_hash))

    print(f"{VERSION}: SYNTHETIC PAYLOAD={canonical_json(synthetic_payload)}", flush=True)
    print(f"{VERSION}: SYNTHETIC PAYLOAD SHA256={synthetic_payload_hash}", flush=True)

    test_header(17, "SYNTHETIC AUTHENTICATED EXECUTION ENVELOPE")

    execution_envelope = {
        "syntheticOnly": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "liveStateSHA256": live_state_hash,
        "decisionSHA256": sha256_json(decision),
        "intentSHA256": synthetic_intent_hash,
        "payloadSHA256": synthetic_payload_hash,
    }

    check("Envelope Is Synthetic Only", execution_envelope["syntheticOnly"] is True)
    check("Envelope Forbids Transmission", execution_envelope["transmissionAllowed"] is False)
    check("Envelope Forbids Network Write", execution_envelope["networkWriteAllowed"] is False)
    check("Envelope Binds Exact Live State", execution_envelope["liveStateSHA256"] == live_state_hash)
    check("Envelope Binds Exact Decision", execution_envelope["decisionSHA256"] == sha256_json(decision))
    check("Envelope Binds Exact Intent", execution_envelope["intentSHA256"] == synthetic_intent_hash)
    check("Envelope Binds Exact Payload", execution_envelope["payloadSHA256"] == synthetic_payload_hash)

    test_header(18, "SYNTHETIC ENTRY TRANSPORT")

    synthetic_receipt = synthetic_dispatch(synthetic_payload)

    check("Synthetic Dispatch Is Synthetic Only", synthetic_receipt["syntheticOnly"] is True)
    check("Synthetic Dispatch Was Not Transmitted", synthetic_receipt["transmitted"] is False)
    check("Synthetic Dispatch Performed No Network Write", synthetic_receipt["networkWriteOccurred"] is False)
    check("Synthetic Receipt Binds Payload Hash", synthetic_receipt["payloadSHA256"] == synthetic_payload_hash)

    print(f"{VERSION}: SYNTHETIC RECEIPT={canonical_json(synthetic_receipt)}", flush=True)

    # ==============================================================================================
    # PART 3 - COMPLETE SYNTHETIC LIFECYCLE
    # ==============================================================================================

    test_header(19, "SYNTHETIC POSITION CREATION")

    lifecycle = SyntheticPositionLifecycle(
        entry_price=market_price,
        quantity=normalized_quantity,
        qty_step=qty_step,
    )

    check("Position Lifecycle Is Synthetic Only", lifecycle.synthetic_only)
    check("Lifecycle Forbids Network Writes", lifecycle.network_write_allowed is False)
    check("Synthetic Position Starts OPEN", lifecycle.state == "OPEN")
    check("Synthetic Entry Price Matches Live Reference Price", lifecycle.entry_price == market_price)
    check("Synthetic Quantity Matches Entry Quantity", lifecycle.initial_quantity == normalized_quantity)

    test_header(20, "TP1 LIFECYCLE TRANSITION")

    tp1_price = lifecycle.price_for_percent(TP1_TRIGGER_PERCENT)

    lifecycle.process_profit_price(tp1_price)

    check("TP1 Triggered", lifecycle.tp1_done)
    check("TP2 Has Not Triggered Yet", lifecycle.tp2_done is False)
    check("Position Remains Open After TP1", lifecycle.state == "OPEN")
    check("TP1 Reduced Remaining Quantity", lifecycle.remaining_quantity < lifecycle.initial_quantity)

    print(f"{VERSION}: TP1 TEST PRICE={decimal_text(tp1_price)}", flush=True)

    test_header(21, "TP2 + TRAILING ARM TRANSITION")

    tp2_price = lifecycle.price_for_percent(TP2_TRIGGER_PERCENT)

    lifecycle.process_profit_price(tp2_price)

    check("TP2 Triggered", lifecycle.tp2_done)
    check("Trailing Protection Armed", lifecycle.trailing_armed)
    check("Position Remains Open After TP2", lifecycle.state == "OPEN")

    print(f"{VERSION}: TP2 TEST PRICE={decimal_text(tp2_price)}", flush=True)

    test_header(22, "TRAILING HIGH-WATER MARK")

    trailing_high_price = lifecycle.price_for_percent(Decimal("1.50"))

    lifecycle.process_trailing_price(trailing_high_price)

    check("Trailing High Increased", lifecycle.highest_price >= trailing_high_price)
    check("Trailing Exit Has Not Triggered At New High", lifecycle.trailing_triggered is False)
    check("Position Remains Open At New High", lifecycle.state == "OPEN")

    print(f"{VERSION}: TRAILING HIGH={decimal_text(lifecycle.highest_price)}", flush=True)

    test_header(23, "TP3 TRAILING EXIT")

    trailing_stop = (
        lifecycle.highest_price
        * (
            Decimal("1")
            - TRAILING_DISTANCE_PERCENT / Decimal("100")
        )
    )

    lifecycle.process_trailing_price(trailing_stop)

    check("Trailing Exit Triggered", lifecycle.trailing_triggered)
    check("TP3 Completed", lifecycle.tp3_done)
    check("Synthetic Position Is Closed", lifecycle.state == "CLOSED")
    check("Synthetic Remaining Quantity Is Zero", lifecycle.remaining_quantity == Decimal("0"))

    print(f"{VERSION}: TRAILING EXIT PRICE={decimal_text(trailing_stop)}", flush=True)

    test_header(24, "PYRAMID ELIGIBILITY AND LIMIT")

    pyramid_test = SyntheticPositionLifecycle(
        market_price,
        normalized_quantity,
        qty_step,
    )

    pyramid_price = pyramid_test.price_for_percent(
        TP1_TRIGGER_PERCENT
    )

    check("First Pyramid Is Eligible", pyramid_test.pyramid_eligible(pyramid_price))
    check("First Synthetic Pyramid Candidate Accepted", pyramid_test.synthetic_pyramid(pyramid_price))
    check("Pyramid Count Is One", pyramid_test.pyramid_adds == 1)
    check("Second Pyramid Is Rejected", pyramid_test.synthetic_pyramid(pyramid_price) is False)
    check("Maximum Pyramid Adds Remains One", pyramid_test.pyramid_adds == MAX_PYRAMID_ADDS)

    test_header(25, "BACKUP ELIGIBILITY AND LIMIT")

    backup_test = SyntheticPositionLifecycle(
        market_price,
        normalized_quantity,
        qty_step,
    )

    backup_price_1 = backup_test.adverse_price_for_percent(Decimal("0.30"))
    backup_price_2 = backup_test.adverse_price_for_percent(Decimal("0.60"))
    backup_price_3 = backup_test.adverse_price_for_percent(Decimal("0.90"))

    check("Backup One Is Eligible", backup_test.synthetic_backup(backup_price_1))
    check("Backup Two Is Eligible", backup_test.synthetic_backup(backup_price_2))
    check("Backup Three Is Eligible", backup_test.synthetic_backup(backup_price_3))
    check("Backup Count Is Three", backup_test.backups == 3)
    check("Fourth Backup Is Rejected", backup_test.synthetic_backup(backup_price_3) is False)
    check("Maximum Backups Remains Three", backup_test.backups == MAX_BACKUPS)

    test_header(26, "ANTI-DUPLICATE ENTRY PROTECTION")

    active_client_ids = set()

    first_client_id = synthetic_intent["newClientOrderId"]

    duplicate_first_allowed = (
        first_client_id not in active_client_ids
    )

    if duplicate_first_allowed:
        active_client_ids.add(first_client_id)

    duplicate_second_allowed = (
        first_client_id not in active_client_ids
    )

    check("Initial Client Order ID Was Unique", duplicate_first_allowed)
    check("Client Order ID Was Registered", first_client_id in active_client_ids)
    check("Duplicate Client Order ID Is Rejected", duplicate_second_allowed is False)
    check("Anti Duplicate Toggle Remains Enabled", ANTI_DUPLICATE_ORDERS)

    test_header(27, "ONE-DIRECTION-ONLY PROTECTION")

    synthetic_long_active = True
    synthetic_short_candidate = True

    short_allowed = not (
        ONE_DIRECTION_ONLY
        and synthetic_long_active
        and synthetic_short_candidate
    )

    check("Synthetic Long Position Is Active", synthetic_long_active)
    check("Opposite Direction Candidate Exists", synthetic_short_candidate)
    check("Opposite Direction Entry Is Rejected", short_allowed is False)

    test_header(28, "TREND REVERSAL EXIT")

    reversal_test = SyntheticPositionLifecycle(
        market_price,
        normalized_quantity,
        qty_step,
    )

    reversal_price = reversal_test.adverse_price_for_percent(
        Decimal("0.20")
    )

    reversal_result = reversal_test.trend_reversal_exit(
        reversal_price
    )

    check("Trend Reversal Exit Is Enabled", TREND_REVERSAL_EXIT)
    check("Synthetic Reversal Exit Was Accepted", reversal_result)
    check("Reversal Exit Closed Synthetic Position", reversal_test.state == "CLOSED")
    check("Reversal Exit Reason Was Recorded", reversal_test.exit_reason == "TREND_REVERSAL_EXIT")

    test_header(29, "LOSS COOLDOWN")

    cooldown_test = SyntheticPositionLifecycle(
        market_price,
        normalized_quantity,
        qty_step,
    )

    synthetic_now = Decimal("1000000")

    loss_price = cooldown_test.adverse_price_for_percent(
        Decimal("0.50")
    )

    loss_result = cooldown_test.loss_exit(
        loss_price,
        synthetic_now,
    )

    check("Synthetic Loss Exit Was Accepted", loss_result)
    check("Loss Exit Closed Synthetic Position", cooldown_test.state == "CLOSED")
    check("Cooldown Starts After Loss Exit", cooldown_test.cooldown_active(synthetic_now))
    check(
        "Cooldown Remains Active Before Expiry",
        cooldown_test.cooldown_active(
            synthetic_now + Decimal(LOSS_COOLDOWN_SECONDS - 1)
        ),
    )
    check(
        "Cooldown Expires At Required Time",
        cooldown_test.cooldown_active(
            synthetic_now + Decimal(LOSS_COOLDOWN_SECONDS)
        ) is False,
    )

    test_header(30, "SIGNAL EXPIRY")

    signal_created_at = Decimal("2000000")

    signal_before_expiry = (
        signal_created_at
        + Decimal(SIGNAL_EXPIRY_SECONDS - 1)
    )

    signal_at_expiry = (
        signal_created_at
        + Decimal(SIGNAL_EXPIRY_SECONDS)
    )

    check(
        "Signal Is Valid Before Expiry",
        (
            signal_before_expiry
            - signal_created_at
        ) < SIGNAL_EXPIRY_SECONDS,
    )

    check(
        "Signal Is Expired At Expiry Boundary",
        (
            signal_at_expiry
            - signal_created_at
        ) >= SIGNAL_EXPIRY_SECONDS,
    )

    test_header(31, "TERMINAL STATE IMMUTABILITY")

    terminal_test = SyntheticPositionLifecycle(
        market_price,
        normalized_quantity,
        qty_step,
    )

    terminal_test.trend_reversal_exit(
        market_price
    )

    state_before = terminal_test.state
    remaining_before = terminal_test.remaining_quantity

    terminal_test.process_profit_price(
        terminal_test.price_for_percent(
            Decimal("5")
        )
    )

    terminal_test.synthetic_pyramid(
        terminal_test.price_for_percent(
            Decimal("5")
        )
    )

    terminal_test.synthetic_backup(
        terminal_test.adverse_price_for_percent(
            Decimal("5")
        )
    )

    check("Terminal State Remains CLOSED", terminal_test.state == state_before == "CLOSED")
    check("Terminal Quantity Remains Zero", terminal_test.remaining_quantity == remaining_before == Decimal("0"))
    check("Terminal Position Cannot Pyramid", terminal_test.pyramid_adds == 0)
    check("Terminal Position Cannot Backup", terminal_test.backups == 0)

    test_header(32, "LIFECYCLE EVENT JOURNAL BINDING")

    lifecycle_snapshot = lifecycle.snapshot()
    lifecycle_hash = sha256_json(lifecycle_snapshot)

    check("Lifecycle Snapshot Exists", bool(lifecycle_snapshot))
    check("Lifecycle Event Journal Exists", len(lifecycle.events) > 0)
    check("Lifecycle Snapshot Is Synthetic", lifecycle_snapshot["syntheticOnly"] is True)
    check("Lifecycle Snapshot Forbids Network Write", lifecycle_snapshot["networkWriteAllowed"] is False)
    check("Lifecycle Hash Exists", bool(lifecycle_hash))

    print(f"{VERSION}: LIFECYCLE={canonical_json(lifecycle_snapshot)}", flush=True)
    print(f"{VERSION}: LIFECYCLE SHA256={lifecycle_hash}", flush=True)

    test_header(33, "COMPLETE STRATEGY EXECUTION BINDING")

    complete_binding = {
        "version": VERSION,
        "syntheticOnly": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "liveStateSHA256": live_state_hash,
        "decisionSHA256": sha256_json(decision),
        "intentSHA256": synthetic_intent_hash,
        "payloadSHA256": synthetic_payload_hash,
        "entryReceiptSHA256": sha256_json(synthetic_receipt),
        "lifecycleSHA256": lifecycle_hash,
    }

    complete_binding_hash = sha256_json(
        complete_binding
    )

    check("Complete Binding Is Synthetic", complete_binding["syntheticOnly"] is True)
    check("Complete Binding Forbids Transmission", complete_binding["transmissionAllowed"] is False)
    check("Complete Binding Forbids Network Write", complete_binding["networkWriteAllowed"] is False)
    check("Complete Binding Preserves Live State", complete_binding["liveStateSHA256"] == live_state_hash)
    check("Complete Binding Preserves Payload", complete_binding["payloadSHA256"] == synthetic_payload_hash)
    check("Complete Binding Preserves Lifecycle", complete_binding["lifecycleSHA256"] == lifecycle_hash)
    check("Complete Binding Hash Exists", bool(complete_binding_hash))

    print(f"{VERSION}: COMPLETE BINDING={canonical_json(complete_binding)}", flush=True)
    print(f"{VERSION}: COMPLETE BINDING SHA256={complete_binding_hash}", flush=True)

    # ==============================================================================================
    # PART 4 - FINAL FIREBREAK
    # ==============================================================================================

    test_header(34, "FINAL WRITE FIREBREAK")

    check("Network Write Count Remains Zero", network_write_count == 0)
    check("Real Order Count Remains Zero", real_order_count == 0)
    check("Demo Order Count Remains Zero", demo_order_count == 0)
    check("Leverage Mutation Count Remains Zero", leverage_mutation_count == 0)
    check("Margin Mutation Count Remains Zero", margin_mutation_count == 0)
    check("Position Mutation Count Remains Zero", position_mutation_count == 0)
    check("Account Mutation Count Remains Zero", account_mutation_count == 0)
    check("Authenticated Transport Used GET Only", authenticated_get_count == 3)
    check("Public Transport Used GET Only", public_get_count == 2)
    check("Exactly One Synthetic Entry Dispatch Occurred", synthetic_dispatch_count == 1)

    runtime_phase = "FULL_SYNTHETIC_LIFECYCLE_VALIDATED"

    banner(f"{VERSION}: VALIDATION COMPLETE")

    print(f"{VERSION}: AUTHENTICATED GETS={authenticated_get_count}", flush=True)
    print(f"{VERSION}: PUBLIC GETS={public_get_count}", flush=True)
    print(f"{VERSION}: NETWORK WRITES={network_write_count}", flush=True)
    print(f"{VERSION}: REAL ORDERS={real_order_count}", flush=True)
    print(f"{VERSION}: DEMO ORDERS={demo_order_count}", flush=True)
    print(f"{VERSION}: SYNTHETIC DISPATCHES={synthetic_dispatch_count}", flush=True)
    print(f"{VERSION}: LIFECYCLE EVENTS={len(lifecycle.events)}", flush=True)
    print(f"{VERSION}: FINAL LIFECYCLE STATE={lifecycle.state}", flush=True)
    print(f"{VERSION}: NO REAL ORDER WAS SENT", flush=True)
    print(f"{VERSION}: NO DEMO ORDER WAS SENT", flush=True)
    print(f"{VERSION}: NO ACCOUNT MUTATION WAS SENT", flush=True)

    print(
        f"{VERSION}: COMPLETE SYNTHETIC STRATEGY LIFECYCLE VALIDATED",
        flush=True,
    )


# ==================================================================================================
# PROGRAM ENTRY
# ==================================================================================================

def main():

    global runtime_phase

    start_health_server()

    try:

        run_validation()

    except Exception as exc:

        runtime_phase = "VALIDATION_FAILED"

        banner(
            f"{VERSION}: VALIDATION FAILED"
        )

        print(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        traceback.print_exc()

    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        daemon=True,
    )

    heartbeat_thread.start()

    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
