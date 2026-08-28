import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
from decimal import Decimal, ROUND_DOWN, InvalidOperation, getcontext
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

getcontext().prec = 50

# ============================================================================
# R34P - LIVE EXECUTION ENVELOPE / PREFLIGHT VALIDATION
# ----------------------------------------------------------------------------
# IMPORTANT SAFETY BOUNDARY
#   * Live PUBLIC GET requests are allowed.
#   * Live AUTHENTICATED GET requests are allowed.
#   * ALL exchange network writes are forbidden.
#   * Real orders are forbidden.
#   * Demo orders are forbidden.
#   * Leverage / margin / position / account mutations are forbidden.
#   * R34P constructs and validates a synthetic order envelope only.
# ============================================================================

VERSION = "R34P"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()
BASE_URL = os.getenv("WEEX_BASE_URL", "https://api-contract.weex.com").rstrip("/")
HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")
ENTRY_BALANCE_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")
MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = Decimal("5")
MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")
TP1_ALLOCATION_PERCENT = Decimal("20")
TP2_ALLOCATION_PERCENT = Decimal("20")
TP3_ALLOCATION_PERCENT = Decimal("60")
TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")
SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

# R34P preflight-specific limits.
MAX_BOOK_SPREAD_PERCENT = Decimal("0.20")
MAX_REFERENCE_DRIFT_PERCENT = Decimal("0.50")
ORDER_SIDE = os.getenv("R34P_ORDER_SIDE", "BUY").strip().upper()
POSITION_SIDE = os.getenv("R34P_POSITION_SIDE", "LONG").strip().upper()
ORDER_TYPE = "MARKET"
ORDER_PATH = "/capi/v3/order"

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True
REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

COUNTERS = {
    "public_get": 0,
    "authenticated_get": 0,
    "network_writes": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,
    "real_orders": 0,
    "demo_orders": 0,
    "synthetic_envelopes": 0,
}

STATE = {
    "phase": "STARTING",
    "correction_required": None,
    "observed_margin": "UNKNOWN",
    "observed_long": "UNKNOWN",
    "observed_short": "UNKNOWN",
    "entry_qty": "0",
    "mark_price": "0",
    "bid_price": "0",
    "ask_price": "0",
    "spread_percent": "0",
    "synthetic_envelope_hash": "",
    "validated": False,
}

SEP = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(SEP)
    log(title)
    log(SEP)


def check(label, condition):
    ok = bool(condition)
    suffix = "✅ PASS" if ok else "❌ FAIL"
    log(f"{label:<86} {suffix}")
    if not ok:
        raise RuntimeError(f"Validation failed: {label}")
    return True


def D(value, default=None):
    try:
        if value is None:
            if default is None:
                raise InvalidOperation
            return Decimal(str(default))
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        if default is None:
            raise
        return Decimal(str(default))


def canonical_json(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)


def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_ms():
    return str(int(time.time() * 1000))


def percent_diff(a, b):
    a = D(a)
    b = D(b)
    if b == 0:
        return Decimal("0") if a == 0 else Decimal("Infinity")
    return abs(a - b) / abs(b) * Decimal("100")


def floor_to_precision(value, precision):
    value = D(value)
    quantum = Decimal("1").scaleb(-int(precision))
    return value.quantize(quantum, rounding=ROUND_DOWN)


def floor_to_step(value, step):
    value = D(value)
    step = D(step)
    if step <= 0:
        return value
    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


def stringify_decimal(value):
    value = D(value)
    s = format(value, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


# ============================================================================
# NETWORK TRANSPORT
# ============================================================================


def _encode_query(params):
    if not params:
        return ""
    items = []
    for key in sorted(params.keys()):
        value = params[key]
        if value is None:
            continue
        items.append((key, str(value)))
    return urlencode(items)


def _signature(timestamp, method, path, query_string="", body=""):
    method = method.upper()
    request_target = path
    if query_string:
        request_target += "?" + query_string
    prehash = f"{timestamp}{method}{request_target}{body}"
    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def _http_get(path, params=None, authenticated=False, timeout=12):
    query_string = _encode_query(params or {})
    url = BASE_URL + path + (("?" + query_string) if query_string else "")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"{VERSION}-read-only-validator/1.0",
    }

    if authenticated:
        timestamp = now_ms()
        headers.update({
            "ACCESS-KEY": WEEX_API_KEY,
            "ACCESS-SIGN": _signature(timestamp, "GET", path, query_string, ""),
            "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
            "ACCESS-TIMESTAMP": timestamp,
        })

    req = Request(url=url, method="GET", headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            if authenticated:
                COUNTERS["authenticated_get"] += 1
            else:
                COUNTERS["public_get"] += 1
            return json.loads(raw)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GET failed {path}: HTTP {exc.code}: {body[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(f"GET failed {path}: {exc}") from exc


def public_get(path, params=None):
    if not PUBLIC_READ_ONLY:
        raise RuntimeError("Public read-only transport is disabled")
    return _http_get(path, params=params, authenticated=False)


def authenticated_get(path, params=None):
    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError("Authenticated read-only transport is disabled")
    return _http_get(path, params=params, authenticated=True)


# ============================================================================
# HARD WRITE FIREBREAK
# ============================================================================


def reject_write(kind="Generic Network Write"):
    raise RuntimeError(f"{VERSION}: {kind} rejected: exchange network writes are disabled")


def http_post(*args, **kwargs):
    return reject_write("HTTP POST")


def http_put(*args, **kwargs):
    return reject_write("HTTP PUT")


def http_patch(*args, **kwargs):
    return reject_write("HTTP PATCH")


def http_delete(*args, **kwargs):
    return reject_write("HTTP DELETE")


def network_write(*args, **kwargs):
    return reject_write("Generic Network Write")


def place_real_order(*args, **kwargs):
    return reject_write("Real Order Function")


def place_demo_order(*args, **kwargs):
    return reject_write("Demo Order Function")


def mutate_leverage(*args, **kwargs):
    return reject_write("Leverage Mutation Function")


def mutate_margin(*args, **kwargs):
    return reject_write("Margin Mutation Function")


def mutate_position(*args, **kwargs):
    return reject_write("Position Mutation Function")


def mutate_account(*args, **kwargs):
    return reject_write("Account Mutation Function")


def expect_rejection(label, fn):
    try:
        fn()
    except RuntimeError:
        check(label, True)
        return
    check(label, False)


# ============================================================================
# RESPONSE NORMALIZATION
# ============================================================================


def unwrap_data(payload):
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def listify(payload):
    payload = unwrap_data(payload)
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return [payload]
    return []


def locate_contract(payload, symbol):
    payload = unwrap_data(payload)
    candidates = []

    if isinstance(payload, dict):
        symbols = payload.get("symbols")
        if isinstance(symbols, list):
            candidates.extend(symbols)
        elif isinstance(symbols, dict):
            candidates.append(symbols)

        if str(payload.get("symbol", "")).upper() == symbol:
            candidates.append(payload)

    elif isinstance(payload, list):
        candidates.extend(payload)

    for item in candidates:
        if isinstance(item, dict) and str(item.get("symbol", "")).upper() == symbol:
            return item

    return None


def obtain_contract_info():
    path = "/capi/v3/market/exchangeInfo"
    payload = public_get(path, {"symbol": SYMBOL})
    contract = locate_contract(payload, SYMBOL)

    if contract is None:
        raise RuntimeError(f"Contract information for {SYMBOL} not found")

    return path, contract


def obtain_mark_price():
    path = "/capi/v3/market/symbolPrice"
    payload = public_get(path, {"symbol": SYMBOL, "priceType": "MARK"})
    data = unwrap_data(payload)

    if isinstance(data, list):
        data = next(
            (
                x for x in data
                if isinstance(x, dict)
                and str(x.get("symbol", "")).upper() == SYMBOL
            ),
            None,
        )

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected mark-price response")

    price = D(data.get("price", data.get("markPrice")))
    return path, price


def obtain_book_ticker():
    path = "/capi/v3/market/ticker/bookTicker"
    payload = public_get(path, {"symbol": SYMBOL})
    records = listify(payload)

    record = next(
        (
            x for x in records
            if isinstance(x, dict)
            and str(x.get("symbol", "")).upper() == SYMBOL
        ),
        records[0] if records else None,
    )

    if not isinstance(record, dict):
        raise RuntimeError("Unexpected book-ticker response")

    bid = D(record.get("bidPrice"))
    ask = D(record.get("askPrice"))

    return path, bid, ask


def obtain_available_balance():
    path = "/capi/v3/account/balance"
    payload = authenticated_get(path)
    records = listify(payload)

    usdt = next(
        (
            x for x in records
            if isinstance(x, dict)
            and str(x.get("asset", "")).upper() == "USDT"
        ),
        None,
    )

    if usdt is None:
        raise RuntimeError("USDT balance record not found")

    available = D(usdt.get("availableBalance", usdt.get("available")))
    return path, available


def obtain_symbol_config():
    path = "/capi/v3/account/symbolConfig"
    payload = authenticated_get(path, {"symbol": SYMBOL})
    records = listify(payload)

    config = next(
        (
            x for x in records
            if isinstance(x, dict)
            and str(x.get("symbol", "")).upper() == SYMBOL
        ),
        records[0] if records else None,
    )

    if not isinstance(config, dict):
        raise RuntimeError(f"Symbol configuration for {SYMBOL} not found")

    return path, config


def obtain_positions():
    path = "/capi/v3/account/position/allPosition"
    payload = authenticated_get(path)
    records = listify(payload)

    symbol_records = [
        x for x in records
        if isinstance(x, dict)
        and str(x.get("symbol", "")).upper() == SYMBOL
    ]

    open_records = []

    for record in symbol_records:
        size = D(record.get("size", "0"), "0")
        if size != 0:
            open_records.append(record)

    return path, records, symbol_records, open_records


# ============================================================================
# CONTRACT PARSING / ENTRY READINESS
# ============================================================================


def contract_decimal(contract, *names, default=None):
    for name in names:
        if name in contract and contract[name] not in (None, ""):
            return D(contract[name])

    if default is None:
        raise RuntimeError(f"Missing required contract numeric field: {names}")

    return D(default)


def contract_int(contract, *names, default=None):
    for name in names:
        if name in contract and contract[name] not in (None, ""):
            return int(contract[name])

    if default is None:
        raise RuntimeError(f"Missing required contract integer field: {names}")

    return int(default)


def calculate_entry(balance, mark_price, contract):
    qty_precision = contract_int(
        contract,
        "quantityPrecision",
        "qtyPrecision",
        default=4,
    )

    min_order = contract_decimal(
        contract,
        "minOrderSize",
        "minOrderQty",
        "minQty",
        default="0.0001",
    )

    max_order = contract_decimal(
        contract,
        "maxOrderSize",
        "maxOrderQty",
        "maxQty",
        default="999999999",
    )

    margin_budget = (
        balance
        * ENTRY_BALANCE_PERCENT
        / Decimal("100")
    )

    planned_notional = (
        margin_budget
        * TARGET_LONG_LEVERAGE
    )

    raw_qty = (
        planned_notional
        / mark_price
    )

    qty_step = None

    for field in ("quantityStep", "qtyStep", "stepSize"):
        if contract.get(field) not in (None, ""):
            qty_step = D(contract[field])
            break

    if qty_step is not None and qty_step > 0:
        rounded_qty = floor_to_step(raw_qty, qty_step)
        rounded_qty = floor_to_precision(
            rounded_qty,
            qty_precision,
        )
    else:
        rounded_qty = floor_to_precision(
            raw_qty,
            qty_precision,
        )

    rounded_notional = (
        rounded_qty
        * mark_price
    )

    estimated_margin = (
        rounded_notional
        / TARGET_LONG_LEVERAGE
    )

    exposure_cap = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    return {
        "qty_precision": qty_precision,
        "min_order": min_order,
        "max_order": max_order,
        "margin_budget": margin_budget,
        "planned_notional": planned_notional,
        "raw_qty": raw_qty,
        "rounded_qty": rounded_qty,
        "rounded_notional": rounded_notional,
        "estimated_margin": estimated_margin,
        "exposure_cap": exposure_cap,
    }


# ============================================================================
# R34P SYNTHETIC ORDER ENVELOPE
# ============================================================================


def make_client_order_id(intent_hash):
    return f"r34p-{intent_hash[:20]}"


def build_synthetic_order_intent(
    mark_price,
    bid_price,
    ask_price,
    quantity,
):
    created_ms = int(time.time() * 1000)
    expires_ms = (
        created_ms
        + SIGNAL_EXPIRY_SECONDS * 1000
    )

    unsigned = {
        "version": VERSION,
        "synthetic": True,
        "transmit": False,
        "symbol": SYMBOL,
        "side": ORDER_SIDE,
        "positionSide": POSITION_SIDE,
        "type": ORDER_TYPE,
        "quantity": stringify_decimal(quantity),
        "referenceMarkPrice": stringify_decimal(mark_price),
        "referenceBidPrice": stringify_decimal(bid_price),
        "referenceAskPrice": stringify_decimal(ask_price),
        "createdAtMs": created_ms,
        "expiresAtMs": expires_ms,
        "signalExpirySeconds": SIGNAL_EXPIRY_SECONDS,
        "targetMarginType": TARGET_MARGIN_TYPE,
        "targetLeverage": "100",
        "networkWriteAllowed": False,
        "realExecutionAllowed": False,
        "demoExecutionAllowed": False,
    }

    unsigned_body = canonical_json(unsigned)
    intent_hash = sha256_hex(unsigned_body)

    intent = dict(unsigned)
    intent["intentSha256"] = intent_hash
    intent["newClientOrderId"] = make_client_order_id(intent_hash)

    return intent


def build_order_payload(intent):
    # Local synthetic payload candidate only.
    # It MUST NOT be transmitted.
    return {
        "symbol": intent["symbol"],
        "side": intent["side"],
        "positionSide": intent["positionSide"],
        "type": intent["type"],
        "quantity": intent["quantity"],
        "newClientOrderId": intent["newClientOrderId"],
    }


def build_synthetic_execution_envelope(intent, payload):
    body = canonical_json(payload)
    synthetic_timestamp = now_ms()

    synthetic_signature = _signature(
        synthetic_timestamp,
        "POST",
        ORDER_PATH,
        "",
        body,
    )

    envelope = {
        "version": VERSION,
        "synthetic": True,
        "transmit": False,
        "method": "POST",
        "path": ORDER_PATH,
        "body": body,
        "bodySha256": sha256_hex(body),
        "intentSha256": intent["intentSha256"],
        "headers": {
            "ACCESS-KEY": WEEX_API_KEY,
            "ACCESS-SIGN": synthetic_signature,
            "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
            "ACCESS-TIMESTAMP": synthetic_timestamp,
            "Content-Type": "application/json",
        },
        "networkWriteAllowed": False,
        "realExecutionAllowed": False,
        "demoExecutionAllowed": False,
    }

    envelope_body = canonical_json(envelope)
    envelope["envelopeSha256"] = sha256_hex(envelope_body)

    COUNTERS["synthetic_envelopes"] += 1

    return envelope


def validate_client_order_id(value):
    if not isinstance(value, str):
        return False

    if not (1 <= len(value) <= 36):
        return False

    allowed = set(
        ".ABCDEFGHIJKLMNOPQRSTUVWXYZ:/"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789_-"
    )

    return all(
        ch in allowed
        for ch in value
    )


# ============================================================================
# HEALTH SERVER
# ============================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps(
            {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": STATE["phase"],
                "validated": STATE["validated"],
                "networkWrites": COUNTERS["network_writes"],
                "realOrders": COUNTERS["real_orders"],
                "demoOrders": COUNTERS["demo_orders"],
                "syntheticEnvelopes": COUNTERS["synthetic_envelopes"],
            },
            separators=(",", ":"),
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

    def log_message(self, fmt, *args):
        return


def start_health_server():

    def worker():
        try:
            server = ThreadingHTTPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            )
            server.serve_forever()

        except Exception as exc:
            log(
                f"{VERSION}: HEALTH SERVER ERROR="
                f"{type(exc).__name__}: {exc}"
            )

    thread = threading.Thread(
        target=worker,
        name=f"{VERSION}-health",
        daemon=True,
    )

    thread.start()


# ============================================================================
# VALIDATION SUITE
# ============================================================================


def run_validation():

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")
    log(f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED")
    log(f"{VERSION}: PUBLIC READ-ONLY ENABLED")
    log(f"{VERSION}: REAL ORDER EXECUTION DISABLED")
    log(f"{VERSION}: DEMO ORDER EXECUTION DISABLED")
    log(f"{VERSION}: NETWORK WRITES DISABLED")
    log(f"{VERSION}: LEVERAGE MUTATION DISABLED")
    log(f"{VERSION}: MARGIN MUTATION DISABLED")
    log(f"{VERSION}: POSITION MUTATION DISABLED")
    log(f"{VERSION}: ACCOUNT MUTATION DISABLED")
    log(f"{VERSION}: TARGET MARGIN={TARGET_MARGIN_TYPE}")
    log(f"{VERSION}: TARGET LONG=100x")
    log(f"{VERSION}: TARGET SHORT=100x")

    section(
        f"{VERSION} TEST 1: SAFETY CONFIGURATION"
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY,
    )

    check(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY,
    )

    check(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION,
    )

    check(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    check(
        "Exchange Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    check(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    check(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    check(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    check(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION_ENABLED,
    )

    section(
        f"{VERSION} TEST 2: WRITE FIREBREAK"
    )

    expect_rejection(
        "HTTP POST Is Rejected",
        http_post,
    )

    expect_rejection(
        "HTTP PUT Is Rejected",
        http_put,
    )

    expect_rejection(
        "HTTP PATCH Is Rejected",
        http_patch,
    )

    expect_rejection(
        "HTTP DELETE Is Rejected",
        http_delete,
    )

    expect_rejection(
        "Generic Network Write Is Rejected",
        network_write,
    )

    expect_rejection(
        "Real Order Function Is Rejected",
        place_real_order,
    )

    expect_rejection(
        "Demo Order Function Is Rejected",
        place_demo_order,
    )

    expect_rejection(
        "Leverage Mutation Function Is Rejected",
        mutate_leverage,
    )

    expect_rejection(
        "Margin Mutation Function Is Rejected",
        mutate_margin,
    )

    expect_rejection(
        "Position Mutation Function Is Rejected",
        mutate_position,
    )

    expect_rejection(
        "Account Mutation Function Is Rejected",
        mutate_account,
    )

    section(
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

    section(
        f"{VERSION} TEST 4: LIVE EXCHANGE INFORMATION"
    )

    contract_path, contract = obtain_contract_info()

    price_precision = contract_int(
        contract,
        "pricePrecision",
        default=1,
    )

    qty_precision = contract_int(
        contract,
        "quantityPrecision",
        "qtyPrecision",
        default=4,
    )

    min_order = contract_decimal(
        contract,
        "minOrderSize",
        "minOrderQty",
        "minQty",
        default="0.0001",
    )

    max_order = contract_decimal(
        contract,
        "maxOrderSize",
        "maxOrderQty",
        "maxQty",
        default="999999999",
    )

    min_leverage = contract_decimal(
        contract,
        "minLeverage",
        default="1",
    )

    max_leverage = contract_decimal(
        contract,
        "maxLeverage",
        default="1",
    )

    check(
        "Contract Information Was Located",
        contract is not None,
    )

    check(
        f"Contract Symbol Matches {SYMBOL}",
        str(
            contract.get("symbol", "")
        ).upper() == SYMBOL,
    )

    check(
        "Price Precision Is Valid",
        price_precision >= 0,
    )

    check(
        "Quantity Precision Is Valid",
        qty_precision >= 0,
    )

    check(
        "Minimum Order Size Is Positive",
        min_order > 0,
    )

    check(
        "Maximum Order Size Is Positive",
        max_order > 0,
    )

    check(
        "Minimum Leverage Is Positive",
        min_leverage > 0,
    )

    check(
        "Exchange Supports Target 100x Leverage",
        max_leverage >= Decimal("100"),
    )

    log(
        f"{VERSION}: CONTRACT PATH="
        f"{contract_path}"
    )

    log(
        f"{VERSION}: CONTRACT SYMBOL="
        f"{contract.get('symbol', '')}"
    )

    log(
        f"{VERSION}: BASE ASSET="
        f"{contract.get('baseAsset', '')}"
    )

    log(
        f"{VERSION}: QUOTE ASSET="
        f"{contract.get('quoteAsset', '')}"
    )

    log(
        f"{VERSION}: MARGIN ASSET="
        f"{contract.get('marginAsset', '')}"
    )

    log(
        f"{VERSION}: PRICE PRECISION="
        f"{price_precision}"
    )

    log(
        f"{VERSION}: QUANTITY PRECISION="
        f"{qty_precision}"
    )

    log(
        f"{VERSION}: MIN ORDER="
        f"{stringify_decimal(min_order)}"
    )

    log(
        f"{VERSION}: MAX ORDER="
        f"{stringify_decimal(max_order)}"
    )

    log(
        f"{VERSION}: MIN LEVERAGE="
        f"{stringify_decimal(min_leverage)}"
    )

    log(
        f"{VERSION}: MAX LEVERAGE="
        f"{stringify_decimal(max_leverage)}"
    )

    section(
        f"{VERSION} TEST 5: LIVE MARK PRICE"
    )

    mark_path, mark_price = obtain_mark_price()

    check(
        "Market Price Was Read",
        mark_price is not None,
    )

    check(
        "Market Price Is Positive",
        mark_price > 0,
    )

    STATE["mark_price"] = stringify_decimal(
        mark_price
    )

    log(
        f"{VERSION}: MARKET PRICE PATH="
        f"{mark_path}"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{stringify_decimal(mark_price)}"
    )

    section(
        f"{VERSION} TEST 6: LIVE BEST BID / ASK"
    )

    book_path, bid_price, ask_price = (
        obtain_book_ticker()
    )

    spread = (
        ask_price
        - bid_price
    )

    spread_percent = (
        spread
        / mark_price
        * Decimal("100")
        if mark_price > 0
        else Decimal("Infinity")
    )

    bid_mark_drift = percent_diff(
        bid_price,
        mark_price,
    )

    ask_mark_drift = percent_diff(
        ask_price,
        mark_price,
    )

    check(
        "Best Bid Was Read",
        bid_price > 0,
    )

    check(
        "Best Ask Was Read",
        ask_price > 0,
    )

    check(
        "Best Ask Is Not Below Best Bid",
        ask_price >= bid_price,
    )

    check(
        "Book Spread Is Within Preflight Limit",
        spread_percent
        <= MAX_BOOK_SPREAD_PERCENT,
    )

    check(
        "Bid Is Near Reference Mark Price",
        bid_mark_drift
        <= MAX_REFERENCE_DRIFT_PERCENT,
    )

    check(
        "Ask Is Near Reference Mark Price",
        ask_mark_drift
        <= MAX_REFERENCE_DRIFT_PERCENT,
    )

    STATE["bid_price"] = stringify_decimal(
        bid_price
    )

    STATE["ask_price"] = stringify_decimal(
        ask_price
    )

    STATE["spread_percent"] = stringify_decimal(
        spread_percent
    )

    log(
        f"{VERSION}: BOOK PATH="
        f"{book_path}"
    )

    log(
        f"{VERSION}: BEST BID="
        f"{stringify_decimal(bid_price)}"
    )

    log(
        f"{VERSION}: BEST ASK="
        f"{stringify_decimal(ask_price)}"
    )

    log(
        f"{VERSION}: SPREAD="
        f"{stringify_decimal(spread)}"
    )

    log(
        f"{VERSION}: SPREAD PERCENT="
        f"{stringify_decimal(spread_percent)}%"
    )

    log(
        f"{VERSION}: MAX SPREAD="
        f"{stringify_decimal(MAX_BOOK_SPREAD_PERCENT)}%"
    )

    section(
        f"{VERSION} TEST 7: LIVE BALANCE RECONCILIATION"
    )

    balance_path, available_balance = (
        obtain_available_balance()
    )

    check(
        "Available Balance Was Read",
        available_balance is not None,
    )

    check(
        "Available Balance Is Positive",
        available_balance > 0,
    )

    log(
        f"{VERSION}: BALANCE PATH="
        f"{balance_path}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{stringify_decimal(available_balance)}"
    )

    section(
        f"{VERSION} TEST 8: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    config_path, config = obtain_symbol_config()

    margin_type = str(
        config.get(
            "marginType",
            "",
        )
    ).upper()

    position_mode = str(
        config.get(
            "separatedType",
            config.get(
                "separatedMode",
                "UNKNOWN",
            ),
        )
    ).upper()

    observed_long = D(
        config.get(
            "isolatedLongLeverage",
            "0",
        ),
        "0",
    )

    observed_short = D(
        config.get(
            "isolatedShortLeverage",
            "0",
        ),
        "0",
    )

    correction_required = not (
        margin_type == TARGET_MARGIN_TYPE
        and observed_long == TARGET_LONG_LEVERAGE
        and observed_short == TARGET_SHORT_LEVERAGE
    )

    check(
        "Margin Type Is ISOLATED",
        margin_type == TARGET_MARGIN_TYPE,
    )

    check(
        "Long Leverage Is 100x",
        observed_long == TARGET_LONG_LEVERAGE,
    )

    check(
        "Short Leverage Is 100x",
        observed_short == TARGET_SHORT_LEVERAGE,
    )

    check(
        "Account Configuration Requires No Correction",
        not correction_required,
    )

    STATE["correction_required"] = (
        correction_required
    )

    STATE["observed_margin"] = (
        margin_type
    )

    STATE["observed_long"] = (
        stringify_decimal(observed_long)
    )

    STATE["observed_short"] = (
        stringify_decimal(observed_short)
    )

    log(
        f"{VERSION}: SYMBOL CONFIG PATH="
        f"{config_path}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: POSITION MODE="
        f"{position_mode}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{stringify_decimal(observed_long)}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{stringify_decimal(observed_short)}x"
    )

    section(
        f"{VERSION} TEST 9: LIVE POSITION RECONCILIATION"
    )

    (
        position_path,
        all_positions,
        symbol_positions,
        open_positions,
    ) = obtain_positions()

    check(
        "Position Response Is Valid",
        isinstance(all_positions, list),
    )

    check(
        f"{SYMBOL} Open Position Count Is Non-Negative",
        len(open_positions) >= 0,
    )

    check(
        "Execution Preflight Starts Flat",
        len(open_positions) == 0,
    )

    log(
        f"{VERSION}: POSITION PATH="
        f"{position_path}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(all_positions)}"
    )

    log(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(symbol_positions)}"
    )

    log(
        f"{VERSION}: {SYMBOL} OPEN POSITIONS="
        f"{len(open_positions)}"
    )

    section(
        f"{VERSION} TEST 10: INITIAL ENTRY READINESS CALCULATION"
    )

    entry = calculate_entry(
        available_balance,
        mark_price,
        contract,
    )

    check(
        "Initial Entry Percent Is Positive",
        ENTRY_BALANCE_PERCENT > 0,
    )

    check(
        "Initial Entry Is Within Exposure Cap",
        ENTRY_BALANCE_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    check(
        "Initial Entry Margin Budget Is Positive",
        entry["margin_budget"] > 0,
    )

    check(
        "Planned Notional Is Positive",
        entry["planned_notional"] > 0,
    )

    check(
        "Raw Quantity Is Positive",
        entry["raw_qty"] > 0,
    )

    check(
        "Rounded Quantity Is Positive",
        entry["rounded_qty"] > 0,
    )

    check(
        "Rounded Quantity Meets Exchange Minimum",
        entry["rounded_qty"]
        >= entry["min_order"],
    )

    check(
        "Rounded Quantity Is Below Exchange Maximum",
        entry["rounded_qty"]
        <= entry["max_order"],
    )

    check(
        "Estimated Entry Margin Is Within Exposure Cap",
        entry["estimated_margin"]
        <= entry["exposure_cap"],
    )

    STATE["entry_qty"] = stringify_decimal(
        entry["rounded_qty"]
    )

    log(
        f"{VERSION}: ENTRY BALANCE PERCENT="
        f"{stringify_decimal(ENTRY_BALANCE_PERCENT)}%"
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{stringify_decimal(entry['margin_budget'])} USDT"
    )

    log(
        f"{VERSION}: PLANNED NOTIONAL="
        f"{stringify_decimal(entry['planned_notional'])} USDT"
    )

    log(
        f"{VERSION}: RAW QUANTITY="
        f"{stringify_decimal(entry['raw_qty'])} BTC"
    )

    log(
        f"{VERSION}: ROUNDED QUANTITY="
        f"{stringify_decimal(entry['rounded_qty'])} BTC"
    )

    log(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{stringify_decimal(entry['rounded_notional'])} USDT"
    )

    log(
        f"{VERSION}: ESTIMATED MARGIN AT 100x="
        f"{stringify_decimal(entry['estimated_margin'])} USDT"
    )

    section(
        f"{VERSION} TEST 11: MAXIMUM STRATEGY EXPOSURE"
    )

    planned_margin_percent = (
        ENTRY_BALANCE_PERCENT
        + Decimal(MAX_PYRAMID_ADDS)
        * PYRAMID_SIZE_PERCENT
        + Decimal(MAX_BACKUPS)
        * BACKUP_SIZE_PERCENT
    )

    max_allowed_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    planned_max_margin = (
        available_balance
        * planned_margin_percent
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
        planned_margin_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{stringify_decimal(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{stringify_decimal(max_allowed_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{stringify_decimal(planned_max_margin)} USDT"
    )

    section(
        f"{VERSION} TEST 12: TAKE-PROFIT STRUCTURE"
    )

    tp_total = (
        TP1_ALLOCATION_PERCENT
        + TP2_ALLOCATION_PERCENT
        + TP3_ALLOCATION_PERCENT
    )

    check(
        "TP Allocation Totals 100 Percent",
        tp_total == 100,
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

    log(
        f"{VERSION}: TP1="
        f"{stringify_decimal(TP1_ALLOCATION_PERCENT)}% "
        f"AT +{stringify_decimal(TP1_TRIGGER_PERCENT)}%"
    )

    log(
        f"{VERSION}: TP2="
        f"{stringify_decimal(TP2_ALLOCATION_PERCENT)}% "
        f"AT +{stringify_decimal(TP2_TRIGGER_PERCENT)}%"
    )

    log(
        f"{VERSION}: TP3="
        f"{stringify_decimal(TP3_ALLOCATION_PERCENT)}% "
        f"TRAILING"
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{stringify_decimal(TRAILING_DISTANCE_PERCENT)}%"
    )

    section(
        f"{VERSION} TEST 13: SYNTHETIC ORDER INTENT"
    )

    intent = build_synthetic_order_intent(
        mark_price,
        bid_price,
        ask_price,
        entry["rounded_qty"],
    )

    check(
        "Synthetic Intent Is Marked Synthetic",
        intent["synthetic"] is True,
    )

    check(
        "Synthetic Intent Forbids Transmission",
        intent["transmit"] is False,
    )

    check(
        f"Synthetic Intent Symbol Matches {SYMBOL}",
        intent["symbol"] == SYMBOL,
    )

    check(
        "Synthetic Intent Quantity Matches Readiness Calculation",
        intent["quantity"]
        == stringify_decimal(
            entry["rounded_qty"]
        ),
    )

    check(
        "Synthetic Intent Side Is Supported",
        intent["side"]
        in {"BUY", "SELL"},
    )

    check(
        "Synthetic Intent Position Side Is Supported",
        intent["positionSide"]
        in {"LONG", "SHORT"},
    )

    check(
        "Synthetic Intent Uses Market Type",
        intent["type"] == "MARKET",
    )

    check(
        "Synthetic Intent Client Order ID Is Valid",
        validate_client_order_id(
            intent["newClientOrderId"]
        ),
    )

    check(
        "Synthetic Intent Hash Exists",
        len(intent["intentSha256"]) == 64,
    )

    check(
        "Synthetic Intent Has Future Expiry",
        intent["expiresAtMs"]
        > intent["createdAtMs"],
    )

    log(
        f"{VERSION}: SYNTHETIC INTENT SHA256="
        f"{intent['intentSha256']}"
    )

    log(
        f"{VERSION}: SYNTHETIC CLIENT ORDER ID="
        f"{intent['newClientOrderId']}"
    )

    log(
        f"{VERSION}: SYNTHETIC INTENT TRANSMITTED=False"
    )

    section(
        f"{VERSION} TEST 14: SYNTHETIC ORDER PAYLOAD"
    )

    payload = build_order_payload(
        intent
    )

    payload_body = canonical_json(
        payload
    )

    payload_hash = sha256_hex(
        payload_body
    )

    check(
        "Payload Symbol Matches Intent",
        payload["symbol"]
        == intent["symbol"],
    )

    check(
        "Payload Side Matches Intent",
        payload["side"]
        == intent["side"],
    )

    check(
        "Payload Position Side Matches Intent",
        payload["positionSide"]
        == intent["positionSide"],
    )

    check(
        "Payload Type Matches Intent",
        payload["type"]
        == intent["type"],
    )

    check(
        "Payload Quantity Matches Intent",
        payload["quantity"]
        == intent["quantity"],
    )

    check(
        "Payload Client Order ID Matches Intent",
        payload["newClientOrderId"]
        == intent["newClientOrderId"],
    )

    check(
        "Payload Hash Exists",
        len(payload_hash) == 64,
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD="
        f"{payload_body}"
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD SHA256="
        f"{payload_hash}"
    )

    section(
        f"{VERSION} TEST 15: SYNTHETIC AUTHENTICATED EXECUTION ENVELOPE"
    )

    envelope = build_synthetic_execution_envelope(
        intent,
        payload,
    )

    check(
        "Envelope Is Marked Synthetic",
        envelope["synthetic"] is True,
    )

    check(
        "Envelope Forbids Transmission",
        envelope["transmit"] is False,
    )

    check(
        "Envelope Uses POST Method Locally",
        envelope["method"] == "POST",
    )

    check(
        "Envelope Body Matches Canonical Payload",
        envelope["body"]
        == payload_body,
    )

    check(
        "Envelope Payload Hash Recomputes Exactly",
        envelope["bodySha256"]
        == payload_hash,
    )

    check(
        "ACCESS-KEY Header Is Present",
        bool(
            envelope["headers"]["ACCESS-KEY"]
        ),
    )

    check(
        "ACCESS-SIGN Header Is Present",
        bool(
            envelope["headers"]["ACCESS-SIGN"]
        ),
    )

    check(
        "ACCESS-PASSPHRASE Header Is Present",
        bool(
            envelope["headers"]["ACCESS-PASSPHRASE"]
        ),
    )

    check(
        "ACCESS-TIMESTAMP Header Is Present",
        bool(
            envelope["headers"]["ACCESS-TIMESTAMP"]
        ),
    )

    check(
        "Envelope Explicitly Forbids Network Write",
        envelope["networkWriteAllowed"]
        is False,
    )

    check(
        "Envelope Explicitly Forbids Real Execution",
        envelope["realExecutionAllowed"]
        is False,
    )

    check(
        "Envelope Explicitly Forbids Demo Execution",
        envelope["demoExecutionAllowed"]
        is False,
    )

    check(
        "Envelope Hash Exists",
        len(
            envelope["envelopeSha256"]
        ) == 64,
    )

    STATE["synthetic_envelope_hash"] = (
        envelope["envelopeSha256"]
    )

    log(
        f"{VERSION}: SYNTHETIC ENVELOPE SHA256="
        f"{envelope['envelopeSha256']}"
    )

    log(
        f"{VERSION}: SYNTHETIC ENVELOPE TRANSMITTED=False"
    )

    section(
        f"{VERSION} TEST 16: ENVELOPE TAMPER / EXPIRY REJECTION"
    )

    tampered_payload = dict(
        payload
    )

    tampered_payload["quantity"] = (
        stringify_decimal(
            entry["rounded_qty"]
            + Decimal("0.0001")
        )
    )

    tampered_hash = sha256_hex(
        canonical_json(
            tampered_payload
        )
    )

    check(
        "Payload Tamper Changes Hash",
        tampered_hash
        != payload_hash,
    )

    expired_intent = dict(
        intent
    )

    expired_intent["expiresAtMs"] = (
        expired_intent["createdAtMs"]
        - 1
    )

    check(
        "Expired Synthetic Intent Is Detectable",
        expired_intent["expiresAtMs"]
        <= int(time.time() * 1000),
    )

    invalid_client_id = (
        intent["newClientOrderId"]
        + "*"
    )

    check(
        "Invalid Client Order ID Is Rejected Locally",
        not validate_client_order_id(
            invalid_client_id
        ),
    )

    section(
        f"{VERSION} TEST 17: FINAL EXECUTION-ENVELOPE FIREBREAK"
    )

    check(
        "Network Writes Remain Zero",
        COUNTERS["network_writes"] == 0,
    )

    check(
        "Leverage Mutations Remain Zero",
        COUNTERS["leverage_mutations"] == 0,
    )

    check(
        "Margin Mutations Remain Zero",
        COUNTERS["margin_mutations"] == 0,
    )

    check(
        "Position Mutations Remain Zero",
        COUNTERS["position_mutations"] == 0,
    )

    check(
        "Account Mutations Remain Zero",
        COUNTERS["account_mutations"] == 0,
    )

    check(
        "Real Orders Remain Zero",
        COUNTERS["real_orders"] == 0,
    )

    check(
        "Demo Orders Remain Zero",
        COUNTERS["demo_orders"] == 0,
    )

    check(
        "Exactly One Synthetic Envelope Was Constructed",
        COUNTERS["synthetic_envelopes"] == 1,
    )

    check(
        "Account Configuration Requires No Correction",
        STATE["correction_required"] is False,
    )

    check(
        "Synthetic Envelope Was Not Transmitted",
        envelope["transmit"] is False,
    )

    STATE["phase"] = (
        "LIVE_EXECUTION_ENVELOPE_PREFLIGHT_VALIDATED"
    )

    STATE["validated"] = True

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    check(
        "Live Execution Envelope / Preflight Readiness",
        True,
    )

    check(
        "WEEX V3 Contract Information Located",
        True,
    )

    check(
        "Account Is Already ISOLATED 100x / 100x",
        STATE["correction_required"] is False,
    )

    check(
        "Initial Entry Calculation Is Exchange Compatible",
        entry["rounded_qty"]
        >= entry["min_order"],
    )

    check(
        "Best Bid / Ask Preflight Is Acceptable",
        spread_percent
        <= MAX_BOOK_SPREAD_PERCENT,
    )

    check(
        "Synthetic Order Intent Was Constructed",
        True,
    )

    check(
        "Synthetic Order Payload Was Constructed",
        True,
    )

    check(
        "Synthetic Authenticated Envelope Was Constructed",
        True,
    )

    check(
        "Synthetic Envelope Was Not Transmitted",
        envelope["transmit"] is False,
    )

    check(
        "No Account Mutation Was Performed",
        COUNTERS["account_mutations"] == 0,
    )

    check(
        "No Real Order Was Sent",
        COUNTERS["real_orders"] == 0,
    )

    check(
        "No Demo Order Was Sent",
        COUNTERS["demo_orders"] == 0,
    )

    check(
        "Network Writes Remain Zero",
        COUNTERS["network_writes"] == 0,
    )


def heartbeat_loop():
    count = 0

    while True:
        count += 1

        log(
            f"{VERSION}: HEARTBEAT {count} | "
            f"phase={STATE['phase']} | "
            f"authenticated-read-only={AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get={COUNTERS['authenticated_get']} | "
            f"public-get={COUNTERS['public_get']} | "
            f"network-writes={COUNTERS['network_writes']} | "
            f"leverage-mutations={COUNTERS['leverage_mutations']} | "
            f"real-orders={COUNTERS['real_orders']} | "
            f"demo-orders={COUNTERS['demo_orders']} | "
            f"synthetic-envelopes={COUNTERS['synthetic_envelopes']} | "
            f"correction-required={STATE['correction_required']} | "
            f"observed-margin={STATE['observed_margin']} | "
            f"observed-long={STATE['observed_long']} | "
            f"observed-short={STATE['observed_short']} | "
            f"target-long=100x | "
            f"target-short=100x | "
            f"entry-qty={STATE['entry_qty']} | "
            f"spread-pct={STATE['spread_percent']}"
        )

        time.sleep(30)


def main():
    start_health_server()

    try:
        run_validation()

    except Exception as exc:
        STATE["phase"] = (
            "VALIDATION_FAILED"
        )

        STATE["validated"] = False

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        raise

    heartbeat_loop()


if __name__ == "__main__":
    main()
