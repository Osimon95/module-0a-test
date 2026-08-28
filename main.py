# ==================================================================================================
# R34W - LIVE STATE + SYNTHETIC STRATEGY DECISION / ORDER CANDIDATE VALIDATION
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
# R34W validates:
#
#   LIVE ACCOUNT STATE
#       ↓
#   LIVE MARKET PRICE
#       ↓
#   STRATEGY BUDGET
#       ↓
#   SYNTHETIC DECISION
#       ↓
#   NORMALIZED QUANTITY
#       ↓
#   EXACT ORDER INTENT
#       ↓
#   EXACT SYNTHETIC PAYLOAD
#       ↓
#   SHA256 BINDING
#       ↓
#   NON-TRANSMITTABLE EXECUTION CANDIDATE
#
# NO REAL ORDER IS SENT.
# ==================================================================================================

import os
import sys
import json
import time
import hmac
import hashlib
import threading
import traceback
import urllib.parse
import urllib.request
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# VERSION
# ==================================================================================================

VERSION = "R34W"
SYMBOL = "BTCUSDT"
HEALTH_PORT = int(os.getenv("PORT", "10000"))


# ==================================================================================================
# EXCHANGE
# ==================================================================================================

BASE_URL = os.getenv("WEEX_BASE_URL", "https://api-contract.weex.com").rstrip("/")

API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("WEEX_ACCESS_KEY")
    or ""
).strip()

API_SECRET = (
    os.getenv("WEEX_API_SECRET")
    or os.getenv("WEEX_SECRET_KEY")
    or ""
).strip()

API_PASSPHRASE = (
    os.getenv("WEEX_API_PASSPHRASE")
    or os.getenv("WEEX_PASSPHRASE")
    or ""
).strip()


# ==================================================================================================
# ABSOLUTE SAFETY FIREBREAK
# ==================================================================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

NETWORK_WRITES_ENABLED = False
REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# ==================================================================================================
# STRATEGY BASELINE
# ==================================================================================================

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

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ==================================================================================================
# BTCUSDT NORMALIZATION RULES
# ==================================================================================================

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
PRICE_STEP = Decimal("0.1")

QTY_PRECISION = 4
PRICE_PRECISION = 1


# ==================================================================================================
# COUNTERS
# ==================================================================================================

COUNTERS = {
    "authenticated_gets": 0,
    "public_gets": 0,

    "network_writes": 0,

    "real_orders": 0,
    "demo_orders": 0,

    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "synthetic_intents": 0,
    "synthetic_payloads": 0,
    "synthetic_candidates": 0,
    "synthetic_dispatches": 0,
}


# ==================================================================================================
# RUNTIME STATE
# ==================================================================================================

STATE = {
    "phase": "STARTING",

    "available_usdt": None,

    "open_positions": None,

    "margin_type": None,
    "position_mode": None,
    "cross_leverage": None,
    "long_leverage": None,
    "short_leverage": None,

    "configuration_verified": False,
    "correction_required": None,

    "mark_price": None,

    "entry_margin_budget": None,
    "entry_notional": None,
    "raw_qty": None,
    "normalized_qty": None,

    "decision": None,
    "intent_hash": None,
    "payload_hash": None,
    "candidate_hash": None,

    "validation_complete": False,
}


# ==================================================================================================
# OUTPUT HELPERS
# ==================================================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def check(label, condition):
    condition = bool(condition)

    suffix = "✅ PASS" if condition else "❌ FAIL"

    log(f"{label:<88}{suffix}")

    if not condition:
        raise RuntimeError(f"Validation failed: {label}")

    return True


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps(
            {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": STATE["phase"],
                "validation_complete": STATE["validation_complete"],
                "authenticated_gets": COUNTERS["authenticated_gets"],
                "public_gets": COUNTERS["public_gets"],
                "network_writes": COUNTERS["network_writes"],
                "real_orders": COUNTERS["real_orders"],
                "demo_orders": COUNTERS["demo_orders"],
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


def start_health_server():

    def run():
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
        server.serve_forever()

    thread = threading.Thread(
        target=run,
        name="health-server",
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# DECIMAL HELPERS
# ==================================================================================================

def D(value, default=None):
    try:
        if value is None:
            return default

        text = str(value).strip()

        if text == "":
            return default

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return default


def decimal_text(value):
    if value is None:
        return "None"

    if not isinstance(value, Decimal):
        value = D(value)

    if value is None:
        return "None"

    return format(value, "f")


def normalized_quantity(raw_qty):
    if raw_qty <= 0:
        return Decimal("0")

    steps = (raw_qty / QTY_STEP).to_integral_value(
        rounding=ROUND_DOWN
    )

    qty = steps * QTY_STEP

    if qty < MIN_QTY:
        return Decimal("0")

    return qty.quantize(QTY_STEP)


def normalized_price(raw_price):
    steps = (raw_price / PRICE_STEP).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (steps * PRICE_STEP).quantize(PRICE_STEP)


# ==================================================================================================
# CANONICAL JSON / HASHING
# ==================================================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_object(value):
    raw = canonical_json(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# ==================================================================================================
# HTTP SAFETY
# ==================================================================================================

def assert_safe_http_method(method):
    method = method.upper()

    if method != "GET":
        raise RuntimeError(
            f"{VERSION}: ABSOLUTE FIREBREAK REJECTED HTTP {method}"
        )


def reject_network_write(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: NETWORK WRITE FIREBREAK ACTIVE"
    )


def reject_real_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: REAL ORDER EXECUTION FIREBREAK ACTIVE"
    )


def reject_demo_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: DEMO ORDER EXECUTION FIREBREAK ACTIVE"
    )


def reject_leverage_mutation(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: LEVERAGE MUTATION FIREBREAK ACTIVE"
    )


def reject_margin_mutation(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: MARGIN MUTATION FIREBREAK ACTIVE"
    )


def reject_position_mutation(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: POSITION MUTATION FIREBREAK ACTIVE"
    )


def reject_account_mutation(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: ACCOUNT MUTATION FIREBREAK ACTIVE"
    )


# Explicit aliases.

network_write = reject_network_write
send_real_order = reject_real_order
send_demo_order = reject_demo_order
change_leverage = reject_leverage_mutation
change_margin = reject_margin_mutation
change_position = reject_position_mutation
change_account = reject_account_mutation


# ==================================================================================================
# HTTP RESPONSE
# ==================================================================================================

def decode_json_response(response):

    raw = response.read().decode(
        "utf-8",
        errors="replace",
    )

    if not raw.strip():
        return {}

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        raise RuntimeError(
            f"Non-JSON API response: {raw[:500]}"
        )


# ==================================================================================================
# WEEX AUTHENTICATED GET
# ==================================================================================================

def authenticated_get(path, params=None):

    assert_safe_http_method("GET")

    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError("Authenticated read-only disabled")

    if not API_KEY:
        raise RuntimeError("WEEX_API_KEY missing")

    if not API_SECRET:
        raise RuntimeError("WEEX_API_SECRET missing")

    if not API_PASSPHRASE:
        raise RuntimeError("WEEX_API_PASSPHRASE missing")

    params = params or {}

    query = urllib.parse.urlencode(params)

    request_path = path

    if query:
        request_path += "?" + query

    timestamp = str(int(time.time() * 1000))

    # WEEX/Bitget-style canonical GET prehash:
    #
    # timestamp + HTTP_METHOD + request_path
    #
    # There is deliberately no request body because R34W allows GET only.

    prehash = timestamp + "GET" + request_path

    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}/read-only",
    }

    url = BASE_URL + request_path

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

            data = decode_json_response(response)

            COUNTERS["authenticated_gets"] += 1

            return data

    except Exception as exc:

        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        ) from exc


# ==================================================================================================
# PUBLIC GET
# ==================================================================================================

def public_get(path, params=None):

    assert_safe_http_method("GET")

    if not PUBLIC_READ_ONLY:
        raise RuntimeError("Public read-only disabled")

    params = params or {}

    query = urllib.parse.urlencode(params)

    url = BASE_URL + path

    if query:
        url += "?" + query

    request = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}/public-read-only",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            data = decode_json_response(response)

            COUNTERS["public_gets"] += 1

            return data

    except Exception as exc:

        raise RuntimeError(
            f"Public GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        ) from exc


# ==================================================================================================
# GENERIC API DATA HELPERS
# ==================================================================================================

def unwrap_data(obj):

    if isinstance(obj, dict):

        for key in (
            "data",
            "result",
            "list",
            "rows",
        ):
            if key in obj:
                return obj[key]

    return obj


def records_from_response(obj):

    value = unwrap_data(obj)

    if isinstance(value, list):
        return value

    if isinstance(value, dict):

        for key in (
            "list",
            "rows",
            "items",
            "positions",
            "data",
        ):
            candidate = value.get(key)

            if isinstance(candidate, list):
                return candidate

        return [value]

    return []


def field(record, *names):

    if not isinstance(record, dict):
        return None

    lower_map = {
        str(k).lower(): v
        for k, v in record.items()
    }

    for name in names:

        if name in record:
            return record[name]

        lowered = str(name).lower()

        if lowered in lower_map:
            return lower_map[lowered]

    return None


# ==================================================================================================
# BALANCE PARSING
# ==================================================================================================

def read_available_usdt():

    path = "/capi/v3/account/balance"

    response = authenticated_get(path)

    log(f"{VERSION}: BALANCE PATH={path}")

    records = records_from_response(response)

    candidates = []

    if isinstance(response, dict):
        candidates.append(response)

    candidates.extend(records)

    for record in candidates:

        if not isinstance(record, dict):
            continue

        currency = field(
            record,
            "coin",
            "currency",
            "asset",
            "marginCoin",
        )

        if currency is not None:
            currency = str(currency).upper()

            if currency not in ("USDT", "USD"):
                continue

        value = field(
            record,
            "available",
            "availableBalance",
            "availableBal",
            "availableMargin",
            "free",
            "balance",
        )

        amount = D(value)

        if amount is not None:
            return amount

    raise RuntimeError(
        "Unable to parse available USDT balance"
    )


# ==================================================================================================
# POSITION PARSING
# ==================================================================================================

def read_positions():

    path = "/capi/v3/account/position/allPosition"

    response = authenticated_get(path)

    log(f"{VERSION}: POSITION PATH={path}")

    records = records_from_response(response)

    symbol_records = []
    open_positions = []

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = field(
            record,
            "symbol",
            "contractCode",
            "contract",
        )

        if symbol is None:
            continue

        if str(symbol).upper() != SYMBOL:
            continue

        symbol_records.append(record)

        qty_value = field(
            record,
            "total",
            "size",
            "position",
            "positionAmt",
            "available",
            "holdVolume",
            "volume",
        )

        qty = D(qty_value, Decimal("0"))

        if qty is not None and abs(qty) > Decimal("0"):
            open_positions.append(record)

    return records, symbol_records, open_positions


# ==================================================================================================
# ACCOUNT CONFIG PARSING
# ==================================================================================================

def read_symbol_configuration():

    path = "/capi/v3/account/symbolConfig"

    response = authenticated_get(
        path,
        {
            "symbol": SYMBOL,
        },
    )

    log(
        f"{VERSION}: ACCOUNT CONFIGURATION PATH={path}"
    )

    records = records_from_response(response)

    target = None

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = field(
            record,
            "symbol",
            "contractCode",
            "contract",
        )

        if symbol is None:
            target = record
            continue

        if str(symbol).upper() == SYMBOL:
            target = record
            break

    if target is None:
        raise RuntimeError(
            f"No configuration record found for {SYMBOL}"
        )

    margin_type = field(
        target,
        "marginType",
        "marginMode",
        "margin_type",
    )

    position_mode = field(
        target,
        "positionMode",
        "holdMode",
        "position_mode",
    )

    cross_leverage = D(
        field(
            target,
            "crossLeverage",
            "crossMarginLeverage",
            "cross_leverage",
        )
    )

    long_leverage = D(
        field(
            target,
            "longLeverage",
            "isolatedLongLeverage",
            "long_leverage",
            "buyLeverage",
        )
    )

    short_leverage = D(
        field(
            target,
            "shortLeverage",
            "isolatedShortLeverage",
            "short_leverage",
            "sellLeverage",
        )
    )

    return {
        "record": target,
        "margin_type": (
            str(margin_type).upper()
            if margin_type is not None
            else None
        ),
        "position_mode": (
            str(position_mode).upper()
            if position_mode is not None
            else None
        ),
        "cross_leverage": cross_leverage,
        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
    }


# ==================================================================================================
# MARKET PRICE PARSING
# ==================================================================================================

def extract_price(response):

    records = records_from_response(response)

    candidates = []

    if isinstance(response, dict):
        candidates.append(response)

    candidates.extend(records)

    for record in candidates:

        if not isinstance(record, dict):
            continue

        symbol = field(
            record,
            "symbol",
            "contractCode",
        )

        if symbol is not None:
            if str(symbol).upper() != SYMBOL:
                continue

        value = field(
            record,
            "markPrice",
            "mark_price",
            "last",
            "lastPrice",
            "close",
            "price",
        )

        price = D(value)

        if price is not None and price > 0:
            return price

    return None


def read_market_price():

    # Public GET fallbacks only.
    #
    # Every candidate below is GET-only. Failure of an individual public
    # endpoint does not weaken any write firebreak.

    attempts = [
        (
            "/capi/v3/market/ticker",
            {"symbol": SYMBOL},
        ),
        (
            "/capi/v3/market/tickers",
            {"symbol": SYMBOL},
        ),
    ]

    errors = []

    for path, params in attempts:

        try:
            response = public_get(path, params)

            price = extract_price(response)

            if price is not None and price > 0:
                log(
                    f"{VERSION}: MARKET PRICE PATH={path}"
                )
                return price

            errors.append(
                f"{path}: response contained no usable price"
            )

        except Exception as exc:
            errors.append(
                f"{path}: {type(exc).__name__}: {exc}"
            )

    raise RuntimeError(
        "Unable to obtain public BTCUSDT market price | "
        + " | ".join(errors)
    )


# ==================================================================================================
# SYNTHETIC DECISION
# ==================================================================================================

def build_synthetic_decision(mark_price):

    # IMPORTANT:
    #
    # This is deliberately NOT a live trading signal.
    #
    # R34W merely freezes a deterministic synthetic LONG decision so that
    # downstream quantity normalization, intent binding and execution
    # candidate construction can be validated.
    #
    # Nothing here is allowed to transmit.

    decision = {
        "version": VERSION,
        "symbol": SYMBOL,

        "decision_type": "SYNTHETIC_VALIDATION_ONLY",
        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,

        "signal": "LONG",
        "side": "BUY",
        "positionSide": "LONG",
        "orderType": "MARKET",

        "reference_mark_price": decimal_text(
            normalized_price(mark_price)
        ),

        "created_epoch_ms": int(time.time() * 1000),
        "expires_after_seconds": SIGNAL_EXPIRY_SECONDS,
    }

    COUNTERS["synthetic_intents"] += 1

    return decision


# ==================================================================================================
# EXACT ORDER INTENT
# ==================================================================================================

def build_order_intent(
    decision,
    available_usdt,
    mark_price,
):

    entry_margin_budget = (
        available_usdt
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    leverage = TARGET_LONG_LEVERAGE

    entry_notional = (
        entry_margin_budget
        * leverage
    )

    raw_qty = (
        entry_notional
        / mark_price
    )

    qty = normalized_quantity(raw_qty)

    if qty <= 0:
        raise RuntimeError(
            "Normalized entry quantity is zero"
        )

    client_order_seed = canonical_json(
        {
            "version": VERSION,
            "symbol": SYMBOL,
            "decision": decision,
            "quantity": decimal_text(qty),
        }
    )

    client_order_hash = hashlib.sha256(
        client_order_seed.encode("utf-8")
    ).hexdigest()

    client_order_id = (
        "r34w-" + client_order_hash[:20]
    )

    intent = {
        "version": VERSION,

        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,

        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",

        "quantity": decimal_text(qty),

        "leverage_context": "100",
        "margin_context": TARGET_MARGIN_TYPE,

        "available_usdt": decimal_text(
            available_usdt
        ),

        "initial_entry_percent": decimal_text(
            INITIAL_ENTRY_PERCENT
        ),

        "entry_margin_budget": decimal_text(
            entry_margin_budget
        ),

        "reference_mark_price": decimal_text(
            mark_price
        ),

        "calculated_notional": decimal_text(
            entry_notional
        ),

        "newClientOrderId": client_order_id,

        "decision_hash": sha256_object(
            decision
        ),
    }

    return (
        intent,
        entry_margin_budget,
        entry_notional,
        raw_qty,
        qty,
    )


# ==================================================================================================
# SYNTHETIC EXCHANGE PAYLOAD
# ==================================================================================================

def build_synthetic_payload(intent):

    payload = {
        "symbol": intent["symbol"],
        "side": intent["side"],
        "positionSide": intent["positionSide"],
        "type": intent["type"],
        "quantity": intent["quantity"],
        "newClientOrderId": intent["newClientOrderId"],
    }

    COUNTERS["synthetic_payloads"] += 1

    return payload


# ==================================================================================================
# NON-TRANSMITTABLE EXECUTION CANDIDATE
# ==================================================================================================

def build_execution_candidate(
    decision,
    intent,
    payload,
):

    candidate = {
        "version": VERSION,

        "candidate_type":
            "SYNTHETIC_AUTHENTICATED_EXECUTION_CANDIDATE",

        "synthetic_only": True,

        "transmission_allowed": False,
        "network_write_allowed": False,
        "real_order_allowed": False,
        "demo_order_allowed": False,

        "account_mutation_allowed": False,
        "position_mutation_allowed": False,
        "margin_mutation_allowed": False,
        "leverage_mutation_allowed": False,

        "decision_hash": sha256_object(
            decision
        ),

        "intent_hash": sha256_object(
            intent
        ),

        "payload_hash": sha256_object(
            payload
        ),

        "payload": payload,
    }

    COUNTERS["synthetic_candidates"] += 1

    return candidate


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

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
        f"{VERSION}: NETWORK WRITES DISABLED"
    )
    log(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )
    log(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
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


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: ABSOLUTE SAFETY FIREBREAK"
    )

    check(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION_ENABLED,
    )

    check(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION_ENABLED,
    )

    check(
        "Network Writes Are Disabled",
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

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY,
    )

    check(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY,
    )

    check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: CREDENTIAL PRESENCE"
    )

    check(
        "WEEX API Key Is Present",
        bool(API_KEY),
    )

    check(
        "WEEX API Secret Is Present",
        bool(API_SECRET),
    )

    check(
        "WEEX API Passphrase Is Present",
        bool(API_PASSPHRASE),
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: LIVE BALANCE RECONCILIATION"
    )

    available_usdt = read_available_usdt()

    STATE["available_usdt"] = available_usdt

    check(
        "Available Balance Was Read",
        available_usdt is not None,
    )

    check(
        "Available Balance Is Positive",
        available_usdt > 0,
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_usdt)}"
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: POSITION RECONCILIATION"
    )

    (
        all_positions,
        symbol_positions,
        open_positions,
    ) = read_positions()

    STATE["open_positions"] = len(open_positions)

    check(
        "Position Response Was Read",
        isinstance(all_positions, list),
    )

    check(
        "BTCUSDT Open Position Count Is Zero",
        len(open_positions) == 0,
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(all_positions)}"
    )

    log(
        f"{VERSION}: BTCUSDT POSITION RECORDS="
        f"{len(symbol_positions)}"
    )

    log(
        f"{VERSION}: BTCUSDT OPEN POSITIONS="
        f"{len(open_positions)}"
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    config = read_symbol_configuration()

    margin_type = config["margin_type"]
    position_mode = config["position_mode"]
    cross_leverage = config["cross_leverage"]
    long_leverage = config["long_leverage"]
    short_leverage = config["short_leverage"]

    STATE["margin_type"] = margin_type
    STATE["position_mode"] = position_mode
    STATE["cross_leverage"] = cross_leverage
    STATE["long_leverage"] = long_leverage
    STATE["short_leverage"] = short_leverage

    check(
        "BTCUSDT Configuration Record Was Read",
        config["record"] is not None,
    )

    check(
        "Margin Type Was Read",
        margin_type is not None,
    )

    check(
        "Margin Type Is ISOLATED",
        margin_type == TARGET_MARGIN_TYPE,
    )

    check(
        "Isolated Long Leverage Was Read",
        long_leverage is not None,
    )

    check(
        "Isolated Short Leverage Was Read",
        short_leverage is not None,
    )

    check(
        "Isolated Long Leverage Is 100x",
        long_leverage == TARGET_LONG_LEVERAGE,
    )

    check(
        "Isolated Short Leverage Is 100x",
        short_leverage == TARGET_SHORT_LEVERAGE,
    )

    configuration_verified = (
        margin_type == TARGET_MARGIN_TYPE
        and long_leverage == TARGET_LONG_LEVERAGE
        and short_leverage == TARGET_SHORT_LEVERAGE
    )

    correction_required = not configuration_verified

    STATE["configuration_verified"] = (
        configuration_verified
    )

    STATE["correction_required"] = (
        correction_required
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: OBSERVED POSITION MODE="
        f"{position_mode}"
    )

    log(
        f"{VERSION}: OBSERVED CROSS LEVERAGE="
        f"{decimal_text(cross_leverage)}"
    )

    log(
        f"{VERSION}: OBSERVED LONG LEVERAGE="
        f"{decimal_text(long_leverage)}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT LEVERAGE="
        f"{decimal_text(short_leverage)}x"
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

    log(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{correction_required}"
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: LIVE MARKET PRICE"
    )

    mark_price = read_market_price()

    STATE["mark_price"] = mark_price

    check(
        "BTCUSDT Market Price Was Read",
        mark_price is not None,
    )

    check(
        "BTCUSDT Market Price Is Positive",
        mark_price > 0,
    )

    normalized_mark = normalized_price(
        mark_price
    )

    check(
        "BTCUSDT Market Price Normalizes To Price Step",
        normalized_mark > 0,
    )

    log(
        f"{VERSION}: RAW MARKET PRICE="
        f"{decimal_text(mark_price)}"
    )

    log(
        f"{VERSION}: NORMALIZED REFERENCE PRICE="
        f"{decimal_text(normalized_mark)}"
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: INITIAL ENTRY CALCULATION"
    )

    entry_margin_budget = (
        available_usdt
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    entry_notional = (
        entry_margin_budget
        * TARGET_LONG_LEVERAGE
    )

    raw_qty = (
        entry_notional
        / mark_price
    )

    qty = normalized_quantity(
        raw_qty
    )

    STATE["entry_margin_budget"] = (
        entry_margin_budget
    )

    STATE["entry_notional"] = (
        entry_notional
    )

    STATE["raw_qty"] = raw_qty
    STATE["normalized_qty"] = qty

    check(
        "Initial Entry Percent Is Positive",
        INITIAL_ENTRY_PERCENT > 0,
    )

    check(
        "Initial Entry Margin Budget Is Positive",
        entry_margin_budget > 0,
    )

    check(
        "Initial Entry Notional Is Positive",
        entry_notional > 0,
    )

    check(
        "Raw Entry Quantity Is Positive",
        raw_qty > 0,
    )

    check(
        "Normalized Entry Quantity Meets Minimum",
        qty >= MIN_QTY,
    )

    check(
        "Normalized Entry Quantity Is Not Greater Than Raw Quantity",
        qty <= raw_qty,
    )

    log(
        f"{VERSION}: INITIAL ENTRY PERCENT="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: INITIAL ENTRY MARGIN BUDGET="
        f"{decimal_text(entry_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: INITIAL ENTRY NOTIONAL AT 100x="
        f"{decimal_text(entry_notional)} USDT"
    )

    log(
        f"{VERSION}: RAW BTC QUANTITY="
        f"{decimal_text(raw_qty)}"
    )

    log(
        f"{VERSION}: NORMALIZED BTC QUANTITY="
        f"{decimal_text(qty)}"
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: MAXIMUM STRATEGY EXPOSURE"
    )

    planned_strategy_percent = (
        INITIAL_ENTRY_PERCENT
        + (PYRAMID_PERCENT * MAX_PYRAMID_ADDS)
        + (BACKUP_PERCENT * MAX_BACKUPS)
    )

    max_allowed_strategy_margin = (
        available_usdt
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    planned_max_strategy_margin = (
        available_usdt
        * planned_strategy_percent
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
        "Planned Strategy Exposure Is 25%",
        planned_strategy_percent == Decimal("25"),
    )

    check(
        "Planned Strategy Exposure Is Within 35%",
        planned_strategy_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    check(
        "Planned Maximum Strategy Margin Is Within Cap",
        planned_max_strategy_margin
        <= max_allowed_strategy_margin,
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: PLANNED STRATEGY EXPOSURE="
        f"{decimal_text(planned_strategy_percent)}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{decimal_text(max_allowed_strategy_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_text(planned_max_strategy_margin)} USDT"
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: SYNTHETIC STRATEGY DECISION"
    )

    decision = build_synthetic_decision(
        mark_price
    )

    STATE["decision"] = decision["signal"]

    decision_hash = sha256_object(
        decision
    )

    check(
        "Decision Is Synthetic Only",
        decision["synthetic_only"] is True,
    )

    check(
        "Decision Forbids Transmission",
        decision["transmission_allowed"] is False,
    )

    check(
        "Decision Forbids Network Write",
        decision["network_write_allowed"] is False,
    )

    check(
        "Decision Symbol Is BTCUSDT",
        decision["symbol"] == SYMBOL,
    )

    check(
        "Synthetic Validation Signal Is LONG",
        decision["signal"] == "LONG",
    )

    check(
        "Synthetic Decision Side Is BUY",
        decision["side"] == "BUY",
    )

    check(
        "Synthetic Decision Position Side Is LONG",
        decision["positionSide"] == "LONG",
    )

    check(
        "Decision Hash Exists",
        len(decision_hash) == 64,
    )

    log(
        f"{VERSION}: SYNTHETIC DECISION="
        f"{canonical_json(decision)}"
    )

    log(
        f"{VERSION}: DECISION SHA256="
        f"{decision_hash}"
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: EXACT SYNTHETIC ORDER INTENT"
    )

    (
        intent,
        intent_margin,
        intent_notional,
        intent_raw_qty,
        intent_qty,
    ) = build_order_intent(
        decision,
        available_usdt,
        mark_price,
    )

    intent_hash = sha256_object(
        intent
    )

    STATE["intent_hash"] = intent_hash

    check(
        "Intent Is Synthetic Only",
        intent["synthetic_only"] is True,
    )

    check(
        "Intent Forbids Transmission",
        intent["transmission_allowed"] is False,
    )

    check(
        "Intent Forbids Network Write",
        intent["network_write_allowed"] is False,
    )

    check(
        "Intent Symbol Is BTCUSDT",
        intent["symbol"] == SYMBOL,
    )

    check(
        "Intent Side Is BUY",
        intent["side"] == "BUY",
    )

    check(
        "Intent Position Side Is LONG",
        intent["positionSide"] == "LONG",
    )

    check(
        "Intent Type Is MARKET",
        intent["type"] == "MARKET",
    )

    check(
        "Intent Quantity Matches Normalized Quantity",
        intent["quantity"]
        == decimal_text(qty),
    )

    check(
        "Intent Decision Hash Matches Decision",
        intent["decision_hash"]
        == decision_hash,
    )

    check(
        "Intent Client Order ID Exists",
        str(intent["newClientOrderId"]).startswith(
            "r34w-"
        ),
    )

    check(
        "Intent Hash Exists",
        len(intent_hash) == 64,
    )

    log(
        f"{VERSION}: SYNTHETIC INTENT="
        f"{canonical_json(intent)}"
    )

    log(
        f"{VERSION}: INTENT SHA256="
        f"{intent_hash}"
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: EXACT SYNTHETIC EXCHANGE PAYLOAD"
    )

    payload = build_synthetic_payload(
        intent
    )

    payload_hash = sha256_object(
        payload
    )

    STATE["payload_hash"] = payload_hash

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
        f"{canonical_json(payload)}"
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD SHA256="
        f"{payload_hash}"
    )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: SYNTHETIC EXECUTION CANDIDATE"
    )

    candidate = build_execution_candidate(
        decision,
        intent,
        payload,
    )

    candidate_hash = sha256_object(
        candidate
    )

    STATE["candidate_hash"] = (
        candidate_hash
    )

    check(
        "Candidate Is Synthetic Only",
        candidate["synthetic_only"] is True,
    )

    check(
        "Candidate Forbids Transmission",
        candidate["transmission_allowed"] is False,
    )

    check(
        "Candidate Forbids Network Write",
        candidate["network_write_allowed"] is False,
    )

    check(
        "Candidate Forbids Real Order",
        candidate["real_order_allowed"] is False,
    )

    check(
        "Candidate Forbids Demo Order",
        candidate["demo_order_allowed"] is False,
    )

    check(
        "Candidate Forbids Account Mutation",
        candidate["account_mutation_allowed"] is False,
    )

    check(
        "Candidate Forbids Position Mutation",
        candidate["position_mutation_allowed"] is False,
    )

    check(
        "Candidate Forbids Margin Mutation",
        candidate["margin_mutation_allowed"] is False,
    )

    check(
        "Candidate Forbids Leverage Mutation",
        candidate["leverage_mutation_allowed"] is False,
    )

    check(
        "Candidate Decision Hash Matches",
        candidate["decision_hash"]
        == decision_hash,
    )

    check(
        "Candidate Intent Hash Matches",
        candidate["intent_hash"]
        == intent_hash,
    )

    check(
        "Candidate Payload Hash Matches",
        candidate["payload_hash"]
        == payload_hash,
    )

    check(
        "Candidate Hash Exists",
        len(candidate_hash) == 64,
    )

    log(
        f"{VERSION}: SYNTHETIC EXECUTION CANDIDATE="
        f"{canonical_json(candidate)}"
    )

    log(
        f"{VERSION}: CANDIDATE SHA256="
        f"{candidate_hash}"
    )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    section(
        f"{VERSION} TEST 13: EXECUTION-CANDIDATE FIREBREAK"
    )

    check(
        "Account Configuration Is Verified",
        configuration_verified,
    )

    check(
        "Correction Is Not Required",
        correction_required is False,
    )

    check(
        "BTCUSDT Is Flat",
        len(open_positions) == 0,
    )

    check(
        "Normalized Candidate Quantity Is Valid",
        qty >= MIN_QTY,
    )

    check(
        "Network Writes Remain Zero",
        COUNTERS["network_writes"] == 0,
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
        "No Synthetic Candidate Was Dispatched",
        COUNTERS["synthetic_dispatches"] == 0,
    )

    check(
        "Exactly One Synthetic Intent Exists",
        COUNTERS["synthetic_intents"] == 1,
    )

    check(
        "Exactly One Synthetic Payload Exists",
        COUNTERS["synthetic_payloads"] == 1,
    )

    check(
        "Exactly One Synthetic Candidate Exists",
        COUNTERS["synthetic_candidates"] == 1,
    )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: WRITE API REJECTION"
    )

    rejected_post = False
    rejected_put = False
    rejected_patch = False
    rejected_delete = False

    try:
        assert_safe_http_method("POST")
    except RuntimeError:
        rejected_post = True

    try:
        assert_safe_http_method("PUT")
    except RuntimeError:
        rejected_put = True

    try:
        assert_safe_http_method("PATCH")
    except RuntimeError:
        rejected_patch = True

    try:
        assert_safe_http_method("DELETE")
    except RuntimeError:
        rejected_delete = True

    check(
        "HTTP POST Is Rejected",
        rejected_post,
    )

    check(
        "HTTP PUT Is Rejected",
        rejected_put,
    )

    check(
        "HTTP PATCH Is Rejected",
        rejected_patch,
    )

    check(
        "HTTP DELETE Is Rejected",
        rejected_delete,
    )

    check(
        "Write Rejection Did Not Increment Network Writes",
        COUNTERS["network_writes"] == 0,
    )


    # ==============================================================================================
    # COMPLETE
    # ==============================================================================================

    STATE["phase"] = (
        "LIVE_STATE_SYNTHETIC_EXECUTION_CANDIDATE_VALIDATED"
    )

    STATE["validation_complete"] = True

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        f"{VERSION}: PHASE="
        f"{STATE['phase']}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_usdt)}"
    )

    log(
        f"{VERSION}: BTCUSDT OPEN POSITIONS="
        f"{len(open_positions)}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{decimal_text(long_leverage)}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{decimal_text(short_leverage)}x"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{decimal_text(mark_price)}"
    )

    log(
        f"{VERSION}: ENTRY QTY="
        f"{decimal_text(qty)}"
    )

    log(
        f"{VERSION}: SYNTHETIC DECISION="
        f"{decision['signal']}"
    )

    log(
        f"{VERSION}: INTENT SHA256="
        f"{intent_hash}"
    )

    log(
        f"{VERSION}: PAYLOAD SHA256="
        f"{payload_hash}"
    )

    log(
        f"{VERSION}: CANDIDATE SHA256="
        f"{candidate_hash}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{COUNTERS['authenticated_gets']}"
    )

    log(
        f"{VERSION}: PUBLIC GETS="
        f"{COUNTERS['public_gets']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{COUNTERS['network_writes']}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{COUNTERS['real_orders']}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{COUNTERS['demo_orders']}"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{COUNTERS['leverage_mutations']}"
    )

    log(
        f"{VERSION}: MARGIN MUTATIONS="
        f"{COUNTERS['margin_mutations']}"
    )

    log(
        f"{VERSION}: POSITION MUTATIONS="
        f"{COUNTERS['position_mutations']}"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATIONS="
        f"{COUNTERS['account_mutations']}"
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{COUNTERS['synthetic_dispatches']}"
    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO DEMO ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO ACCOUNT MUTATION WAS SENT"
    )

    log(
        f"{VERSION}: SYNTHETIC EXECUTION CANDIDATE "
        f"WAS CREATED BUT NOT TRANSMITTED"
    )


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def stable_heartbeat():

    section(
        f"{VERSION}: ENTERING STABLE HEARTBEAT"
    )

    heartbeat = 0

    while True:

        time.sleep(30)

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT {heartbeat}"
            f" | phase={STATE['phase']}"
            f" | authenticated-read-only={AUTHENTICATED_READ_ONLY}"
            f" | authenticated-get={COUNTERS['authenticated_gets']}"
            f" | public-get={COUNTERS['public_gets']}"
            f" | network-writes={COUNTERS['network_writes']}"
            f" | real-orders={COUNTERS['real_orders']}"
            f" | demo-orders={COUNTERS['demo_orders']}"
            f" | margin={STATE['margin_type']}"
            f" | long={decimal_text(STATE['long_leverage'])}"
            f" | short={decimal_text(STATE['short_leverage'])}"
            f" | correction-required={STATE['correction_required']}"
            f" | mark-price={decimal_text(STATE['mark_price'])}"
            f" | entry-qty={decimal_text(STATE['normalized_qty'])}"
            f" | synthetic-candidates={COUNTERS['synthetic_candidates']}"
            f" | synthetic-dispatches={COUNTERS['synthetic_dispatches']}"
        )


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

def main():

    start_health_server()

    try:

        run_validation()

        stable_heartbeat()

    except KeyboardInterrupt:

        log(
            f"{VERSION}: INTERRUPTED"
        )

        raise

    except Exception as exc:

        STATE["phase"] = "VALIDATION_FAILED"

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        log(LINE)

        log(
            f"{VERSION}: NETWORK WRITES="
            f"{COUNTERS['network_writes']}"
        )

        log(
            f"{VERSION}: REAL ORDERS="
            f"{COUNTERS['real_orders']}"
        )

        log(
            f"{VERSION}: DEMO ORDERS="
            f"{COUNTERS['demo_orders']}"
        )

        log(
            f"{VERSION}: SYNTHETIC DISPATCHES="
            f"{COUNTERS['synthetic_dispatches']}"
        )

        log(
            f"{VERSION}: NO REAL ORDER WAS SENT"
        )

        log(
            f"{VERSION}: NO ACCOUNT MUTATION WAS SENT"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
