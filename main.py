# ======================================================================================
# R34M MAIN.PY
# READ-ONLY LIVE RECONCILIATION + LOCAL ORDER ENVELOPE VALIDATION
#
# IMPORTANT SAFETY BOUNDARY:
#   - AUTHENTICATED GETS: ENABLED
#   - PUBLIC GETS: ENABLED
#   - REAL ORDERS: DISABLED
#   - DEMO ORDERS: DISABLED
#   - NETWORK WRITES: DISABLED
#   - ACCOUNT MUTATIONS: DISABLED
#
# R34M validates:
#   1. Safety configuration
#   2. Credentials
#   3. Live balance
#   4. Position state
#   5. Symbol configuration
#   6. Public mark price
#   7. Strategy budget
#   8. Local quantity calculation
#   9. Quantity step / precision / minimum checks
#  10. Notional and margin reconciliation
#  11. Maximum exposure gate
#  12. BUY/LONG intent binding
#  13. SELL/SHORT intent binding
#  14. Stale market-data rejection
#  15. Duplicate intent rejection
#  16. Deterministic order payload construction
#  17. Payload hashing / tamper detection
#  18. Synthetic dispatch receipt
#  19. Final write-firebreak verification
#
# NO ORDER IS TRANSMITTED.
# ======================================================================================

import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import urllib.request
import urllib.parse
import urllib.error

from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer


# ======================================================================================
# VERSION / BASIC CONFIGURATION
# ======================================================================================

VERSION = "R34M"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api.weex.com"
).rstrip("/")


# ======================================================================================
# SECURITY / EXECUTION FIREBREAK
# ======================================================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES = False

LEVERAGE_MUTATION = False
MARGIN_MUTATION = False
POSITION_MUTATION = False
ACCOUNT_MUTATION = False


# ======================================================================================
# STRATEGY CONFIGURATION
# ======================================================================================

TARGET_MARGIN = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")

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

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ======================================================================================
# CONTRACT CONSTRAINTS
#
# These are used only for LOCAL quantity validation.
#
# If WEEX later changes the BTCUSDT contract specification, update these constants
# before any future validation stage.
# ======================================================================================

MIN_ORDER_QTY = Decimal(
    os.getenv("BTCUSDT_MIN_ORDER_QTY", "0.0001")
)

QTY_STEP = Decimal(
    os.getenv("BTCUSDT_QTY_STEP", "0.0001")
)

QTY_PRECISION = int(
    os.getenv("BTCUSDT_QTY_PRECISION", "4")
)

PRICE_STEP = Decimal(
    os.getenv("BTCUSDT_PRICE_STEP", "0.1")
)

PRICE_PRECISION = int(
    os.getenv("BTCUSDT_PRICE_PRECISION", "1")
)


# ======================================================================================
# READ-ONLY API PATHS
# ======================================================================================

BALANCE_PATH = "/capi/v3/account/balance"

POSITION_PATH = "/capi/v3/account/position/allPosition"

SYMBOL_CONFIG_PATH = (
    "/capi/v3/account/symbolConfig"
    f"?symbol={urllib.parse.quote(SYMBOL)}"
)

MARKET_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
    f"?symbol={urllib.parse.quote(SYMBOL)}&priceType=MARK"
)


# ======================================================================================
# CREDENTIALS
# ======================================================================================

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()

WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    ""
).strip()


# ======================================================================================
# RUNTIME STATE
# ======================================================================================

state = {
    "phase": "BOOTING",

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
    "btc_position_records": 0,
    "active_positions": 0,

    "observed_margin": None,
    "observed_position_mode": None,
    "observed_cross_leverage": None,
    "observed_long_leverage": None,
    "observed_short_leverage": None,

    "market_price": None,
    "market_price_time": None,
    "market_price_ready": False,

    "initial_margin_budget": None,
    "initial_notional_target": None,
    "maximum_exposure_budget": None,

    "raw_quantity": None,
    "rounded_quantity": None,
    "rounded_notional": None,
    "rounded_margin_required": None,

    "quantity_ready": False,
    "exposure_ready": False,

    "long_intent_hash": None,
    "short_intent_hash": None,

    "long_payload_hash": None,
    "short_payload_hash": None,

    "synthetic_dispatch_count": 0,

    "execution_envelope_ready": False,

    "final_validation_status": "NOT_RUN",

    "heartbeat": 0,
}


# ======================================================================================
# OUTPUT HELPERS
# ======================================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def check(label, condition):
    result = bool(condition)

    suffix = "✅ PASS" if result else "❌ FAIL"

    log(f"{label:<85} {suffix}")

    if not result:
        raise RuntimeError(
            f"{VERSION}: validation failure: {label}"
        )

    return True


# ======================================================================================
# DECIMAL HELPERS
# ======================================================================================

def D(value, default=None):
    if value is None:
        return default

    try:
        text = str(value).strip()

        if text == "":
            return default

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return default


def decimal_text(value):
    if value is None:
        return "None"

    value = D(value)

    if value is None:
        return "None"

    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def floor_to_step(value, step):
    value = D(value)
    step = D(step)

    if value is None or step is None or step <= 0:
        raise ValueError("Invalid value or step")

    units = (value / step).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def is_step_aligned(value, step):
    value = D(value)
    step = D(step)

    if value is None or step is None or step <= 0:
        return False

    return (value % step) == 0


# ======================================================================================
# JSON / HASH HELPERS
# ======================================================================================

def canonical_json(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def hash_object(obj):
    return sha256_text(
        canonical_json(obj)
    )


# ======================================================================================
# RESPONSE EXTRACTION
# ======================================================================================

def unwrap_data(payload):
    current = payload

    for _ in range(5):

        if not isinstance(current, dict):
            break

        if "data" in current:
            current = current["data"]
            continue

        break

    return current


def find_first(obj, keys):
    wanted = {str(k).lower() for k in keys}

    if isinstance(obj, dict):

        for key, value in obj.items():

            if str(key).lower() in wanted:
                return value

        for value in obj.values():

            result = find_first(value, keys)

            if result is not None:
                return result

    elif isinstance(obj, list):

        for item in obj:

            result = find_first(item, keys)

            if result is not None:
                return result

    return None


# ======================================================================================
# WEEX SIGNING
#
# GET ONLY.
#
# R34M contains no POST transport implementation.
# ======================================================================================

def make_signature(timestamp, method, request_path, body=""):

    prehash = (
        str(timestamp)
        + method.upper()
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


def authenticated_get(request_path):

    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only access is disabled"
        )

    if not all([
        WEEX_API_KEY,
        WEEX_API_SECRET,
        WEEX_API_PASSPHRASE,
    ]):
        raise RuntimeError(
            "Authenticated GET requested without complete credentials"
        )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = make_signature(
        timestamp,
        "GET",
        request_path,
        "",
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only",
    }

    request = urllib.request.Request(
        WEEX_BASE_URL + request_path,
        method="GET",
        headers=headers,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Authenticated GET HTTP {exc.code}: "
            f"{request_path} | {raw[:500]}"
        )

    except Exception as exc:

        raise RuntimeError(
            f"Authenticated GET failed: "
            f"{request_path} | {exc}"
        )

    state["authenticated_get_count"] += 1

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        raise RuntimeError(
            f"Authenticated GET returned invalid JSON: "
            f"{raw[:500]}"
        )


def public_get(request_path):

    if not PUBLIC_READ_ONLY:
        raise RuntimeError(
            "Public read-only access is disabled"
        )

    headers = {
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-public-read-only",
    }

    request = urllib.request.Request(
        WEEX_BASE_URL + request_path,
        method="GET",
        headers=headers,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Public GET HTTP {exc.code}: "
            f"{request_path} | {raw[:500]}"
        )

    except Exception as exc:

        raise RuntimeError(
            f"Public GET failed: "
            f"{request_path} | {exc}"
        )

    state["public_get_count"] += 1

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        raise RuntimeError(
            f"Public GET returned invalid JSON: "
            f"{raw[:500]}"
        )


# ======================================================================================
# WRITE FIREBREAK
#
# These functions intentionally reject every mutation attempt.
# ======================================================================================

def authenticated_post(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: authenticated POST rejected locally "
        f"because NETWORK_WRITES=False"
    )


def execute_real_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: real order execution rejected locally"
    )


def execute_demo_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: demo order execution rejected locally"
    )


def mutate_leverage(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: leverage mutation rejected locally"
    )


def mutate_margin(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: margin mutation rejected locally"
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: position mutation rejected locally"
    )


def mutate_account(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: account mutation rejected locally"
    )


def expect_local_rejection(function):
    try:
        function()

    except RuntimeError:
        return True

    return False


# ======================================================================================
# BALANCE RECONCILIATION
# ======================================================================================

def read_available_usdt():

    payload = authenticated_get(
        BALANCE_PATH
    )

    data = unwrap_data(payload)

    candidates = []

    if isinstance(data, list):
        candidates = data

    elif isinstance(data, dict):

        nested_list = find_first(
            data,
            [
                "list",
                "balances",
                "assets",
            ],
        )

        if isinstance(nested_list, list):
            candidates = nested_list

        else:
            candidates = [data]

    for item in candidates:

        if not isinstance(item, dict):
            continue

        coin = find_first(
            item,
            [
                "coin",
                "currency",
                "asset",
                "marginCoin",
            ],
        )

        if coin is not None:
            if str(coin).upper() != "USDT":
                continue

        amount = find_first(
            item,
            [
                "available",
                "availableBalance",
                "availableAmount",
                "availableMargin",
                "maxWithdrawAmount",
            ],
        )

        value = D(amount)

        if value is not None:
            return value

    amount = find_first(
        payload,
        [
            "available",
            "availableBalance",
            "availableAmount",
            "availableMargin",
        ],
    )

    return D(amount)


# ======================================================================================
# POSITION RECONCILIATION
# ======================================================================================

def normalize_position_records(payload):

    data = unwrap_data(payload)

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in [
            "list",
            "positions",
            "positionList",
            "rows",
        ]:

            value = data.get(key)

            if isinstance(value, list):
                return value

        if any(
            key in data
            for key in [
                "symbol",
                "size",
                "positionAmt",
                "total",
            ]
        ):
            return [data]

    return []


def position_size(record):

    value = find_first(
        record,
        [
            "size",
            "positionAmt",
            "positionSize",
            "total",
            "holdVol",
            "available",
        ],
    )

    size = D(value, Decimal("0"))

    return abs(size)


# ======================================================================================
# SYMBOL CONFIGURATION
# ======================================================================================

def parse_symbol_config(payload):

    data = unwrap_data(payload)

    if isinstance(data, list):

        selected = None

        for item in data:

            symbol = find_first(
                item,
                ["symbol"],
            )

            if symbol is not None:
                if str(symbol).upper() == SYMBOL:
                    selected = item
                    break

        if selected is None and data:
            selected = data[0]

        data = selected

    if not isinstance(data, dict):
        data = payload

    result = {
        "symbol": find_first(
            data,
            ["symbol"],
        ),

        "margin": find_first(
            data,
            [
                "marginMode",
                "marginType",
                "margin_mode",
                "margin_type",
            ],
        ),

        "position_mode": find_first(
            data,
            [
                "positionMode",
                "holdMode",
            ],
        ),

        "cross_leverage": D(
            find_first(
                data,
                [
                    "crossLeverage",
                    "cross_leverage",
                ],
            )
        ),

        "long_leverage": D(
            find_first(
                data,
                [
                    "isolatedLongLeverage",
                    "longLeverage",
                    "long_leverage",
                ],
            )
        ),

        "short_leverage": D(
            find_first(
                data,
                [
                    "isolatedShortLeverage",
                    "shortLeverage",
                    "short_leverage",
                ],
            )
        ),
    }

    return result


# ======================================================================================
# MARKET PRICE
# ======================================================================================

def parse_market_price(payload):

    price_raw = find_first(
        payload,
        [
            "price",
            "markPrice",
            "mark_price",
        ],
    )

    timestamp_raw = find_first(
        payload,
        [
            "time",
            "timestamp",
            "ts",
        ],
    )

    price = D(price_raw)

    timestamp = None

    try:
        if timestamp_raw is not None:
            timestamp = int(
                Decimal(
                    str(timestamp_raw)
                )
            )

    except Exception:
        timestamp = None

    return price, timestamp


# ======================================================================================
# LOCAL ORDER INTENT
# ======================================================================================

def make_order_intent(
    *,
    side,
    position_side,
    quantity,
    reference_price,
    leverage,
):

    intent = {
        "version": VERSION,
        "symbol": SYMBOL,

        "side": side,
        "positionSide": position_side,

        "marginMode": TARGET_MARGIN,

        "leverage": decimal_text(leverage),

        "quantity": decimal_text(quantity),

        "referencePrice": decimal_text(
            reference_price
        ),

        "executionMode": "SYNTHETIC_ONLY",

        "networkWriteAllowed": False,

        "realOrderAllowed": False,

        "demoOrderAllowed": False,
    }

    return intent


# ======================================================================================
# LOCAL ORDER PAYLOAD
#
# This is deliberately NOT signed for POST and is never sent.
# ======================================================================================

def make_local_order_payload(intent):

    return {
        "symbol": intent["symbol"],

        "side": intent["side"],

        "positionSide": intent[
            "positionSide"
        ],

        "marginMode": intent[
            "marginMode"
        ],

        "leverage": intent[
            "leverage"
        ],

        "quantity": intent[
            "quantity"
        ],

        "referencePrice": intent[
            "referencePrice"
        ],

        "orderType": "MARKET",

        "reduceOnly": False,

        "executionPolicy": (
            "LOCAL_VALIDATION_ONLY"
        ),

        "networkTransmission": False,
    }


# ======================================================================================
# DUPLICATE INTENT GUARD
# ======================================================================================

class DuplicateIntentGuard:

    def __init__(self):
        self._seen = set()

    def accept(self, intent_hash):

        if intent_hash in self._seen:
            return False

        self._seen.add(
            intent_hash
        )

        return True


# ======================================================================================
# STALE PRICE VALIDATION
# ======================================================================================

def market_timestamp_age_seconds(
    exchange_timestamp_ms
):

    if exchange_timestamp_ms is None:
        return None

    now_ms = int(
        time.time() * 1000
    )

    age_ms = (
        now_ms
        - exchange_timestamp_ms
    )

    return Decimal(
        str(age_ms)
    ) / Decimal("1000")


def is_market_data_fresh(
    exchange_timestamp_ms,
    maximum_age_seconds,
):

    age = market_timestamp_age_seconds(
        exchange_timestamp_ms
    )

    if age is None:
        return False

    if age < Decimal("-5"):
        return False

    return age <= Decimal(
        str(maximum_age_seconds)
    )


# ======================================================================================
# SYNTHETIC DISPATCH
#
# Absolutely no network operation occurs here.
# ======================================================================================

def synthetic_dispatch(
    payload,
    payload_hash,
):

    receipt = {
        "version": VERSION,

        "symbol": SYMBOL,

        "payloadHash": payload_hash,

        "synthetic": True,

        "transmitted": False,

        "networkWrite": False,

        "realOrder": False,

        "demoOrder": False,

        "status": "INTERCEPTED_LOCALLY",
    }

    state[
        "synthetic_dispatch_count"
    ] += 1

    return receipt


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        body = json.dumps(
            {
                "status": "ok",

                "version": VERSION,

                "symbol": SYMBOL,

                "phase": state[
                    "phase"
                ],

                "authenticated_read_only":
                    AUTHENTICATED_READ_ONLY,

                "public_read_only":
                    PUBLIC_READ_ONLY,

                "real_execution":
                    REAL_ORDER_EXECUTION,

                "demo_execution":
                    DEMO_ORDER_EXECUTION,

                "network_writes":
                    NETWORK_WRITES,

                "execution_envelope_ready":
                    state[
                        "execution_envelope_ready"
                    ],

                "heartbeat":
                    state["heartbeat"],
            },
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
        format,
        *args,
    ):
        return


def start_health_server():

    server = HTTPServer(
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
# MAIN VALIDATION
# ======================================================================================

def run_validation():

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
        f"{VERSION}: TARGET MARGIN={TARGET_MARGIN}"
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
        f"{VERSION}: MARKET PRICE ENDPOINT="
        f"{MARKET_PRICE_PATH}"
    )


    # ==================================================================================
    # TEST 1
    # ==================================================================================

    section(
        f"{VERSION} TEST 1: SAFETY CONFIGURATION"
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY is True,
    )

    check(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY is True,
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    check(
        "Exchange Network Writes Are Disabled",
        NETWORK_WRITES is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION is False,
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION is False,
    )


    # ==================================================================================
    # TEST 2
    # ==================================================================================

    section(
        f"{VERSION} TEST 2: AUTHENTICATED READ-ONLY CREDENTIALS"
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
    # TEST 3
    # ==================================================================================

    section(
        f"{VERSION} TEST 3: LIVE BALANCE RECONCILIATION"
    )

    available_usdt = read_available_usdt()

    state[
        "available_usdt"
    ] = available_usdt

    log(
        f"{VERSION}: BALANCE PATH="
        f"{BALANCE_PATH}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_usdt)}"
    )

    check(
        "Available Balance Was Read",
        available_usdt is not None,
    )

    check(
        "Available Balance Is Positive",
        available_usdt > 0,
    )


    # ==================================================================================
    # TEST 4
    # ==================================================================================

    section(
        f"{VERSION} TEST 4: POSITION RECONCILIATION"
    )

    position_payload = authenticated_get(
        POSITION_PATH
    )

    records = normalize_position_records(
        position_payload
    )

    btc_records = []

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = find_first(
            record,
            ["symbol"],
        )

        if symbol is None:
            continue

        if str(symbol).upper() == SYMBOL:
            btc_records.append(
                record
            )

    active_positions = [
        item
        for item in btc_records
        if position_size(item) > 0
    ]

    state[
        "position_records"
    ] = len(records)

    state[
        "btc_position_records"
    ] = len(btc_records)

    state[
        "active_positions"
    ] = len(active_positions)

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
        f"{len(btc_records)}"
    )

    log(
        f"{VERSION}: {SYMBOL} ACTIVE POSITIONS="
        f"{len(active_positions)}"
    )

    check(
        "Position Endpoint Was Read",
        position_payload is not None,
    )

    check(
        "Position Response Is Reconciled",
        isinstance(records, list),
    )

    check(
        f"{SYMBOL} Position State Was Reconciled",
        isinstance(btc_records, list),
    )

    check(
        "Zero Open Positions Is Required For R34M",
        len(active_positions) == 0,
    )


    # ==================================================================================
    # TEST 5
    # ==================================================================================

    section(
        f"{VERSION} TEST 5: SYMBOL CONFIGURATION READ-BACK"
    )

    config_payload = authenticated_get(
        SYMBOL_CONFIG_PATH
    )

    config = parse_symbol_config(
        config_payload
    )

    observed_symbol = config[
        "symbol"
    ]

    observed_margin = config[
        "margin"
    ]

    observed_position_mode = config[
        "position_mode"
    ]

    observed_cross = config[
        "cross_leverage"
    ]

    observed_long = config[
        "long_leverage"
    ]

    observed_short = config[
        "short_leverage"
    ]

    state[
        "observed_margin"
    ] = observed_margin

    state[
        "observed_position_mode"
    ] = observed_position_mode

    state[
        "observed_cross_leverage"
    ] = observed_cross

    state[
        "observed_long_leverage"
    ] = observed_long

    state[
        "observed_short_leverage"
    ] = observed_short

    log(
        f"{VERSION}: SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observed_margin}"
    )

    log(
        f"{VERSION}: OBSERVED POSITION MODE="
        f"{observed_position_mode}"
    )

    log(
        f"{VERSION}: OBSERVED CROSS LEVERAGE="
        f"{decimal_text(observed_cross)}x"
    )

    log(
        f"{VERSION}: OBSERVED ISOLATED LONG="
        f"{decimal_text(observed_long)}x"
    )

    log(
        f"{VERSION}: OBSERVED ISOLATED SHORT="
        f"{decimal_text(observed_short)}x"
    )

    check(
        "Symbol Configuration Was Read",
        config_payload is not None,
    )

    check(
        f"Configuration Belongs To {SYMBOL}",
        (
            observed_symbol is None
            or str(observed_symbol).upper()
            == SYMBOL
        ),
    )

    check(
        "Margin Type Is ISOLATED",
        str(observed_margin).upper()
        == TARGET_MARGIN,
    )

    check(
        "Isolated Long Leverage Is 100x",
        observed_long
        == TARGET_LONG_LEVERAGE,
    )

    check(
        "Isolated Short Leverage Is 100x",
        observed_short
        == TARGET_SHORT_LEVERAGE,
    )


    # ==================================================================================
    # TEST 6
    # ==================================================================================

    section(
        f"{VERSION} TEST 6: LIVE PUBLIC MARK PRICE"
    )

    price_payload = public_get(
        MARKET_PRICE_PATH
    )

    market_price, market_time = (
        parse_market_price(
            price_payload
        )
    )

    state[
        "market_price"
    ] = market_price

    state[
        "market_price_time"
    ] = market_time

    state[
        "market_price_ready"
    ] = (
        market_price is not None
        and market_price > 0
    )

    log(
        f"{VERSION}: MARKET PRICE PATH="
        f"{MARKET_PRICE_PATH}"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{decimal_text(market_price)}"
    )

    log(
        f"{VERSION}: MARKET PRICE TIME="
        f"{market_time}"
    )

    check(
        "Correct Contract Market Price Endpoint Was Read",
        price_payload is not None,
    )

    check(
        "Public GET Count Is At Least One",
        state["public_get_count"] >= 1,
    )

    check(
        f"{SYMBOL} Market Price Was Read",
        market_price is not None,
    )

    check(
        f"{SYMBOL} Market Price Is Positive",
        market_price > 0,
    )


    # ==================================================================================
    # TEST 7
    # ==================================================================================

    section(
        f"{VERSION} TEST 7: STRATEGY BUDGET RECONCILIATION"
    )

    initial_margin_budget = (
        available_usdt
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    initial_notional_target = (
        initial_margin_budget
        * TARGET_LONG_LEVERAGE
    )

    maximum_exposure_budget = (
        available_usdt
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    state[
        "initial_margin_budget"
    ] = initial_margin_budget

    state[
        "initial_notional_target"
    ] = initial_notional_target

    state[
        "maximum_exposure_budget"
    ] = maximum_exposure_budget

    log(
        f"{VERSION}: AVAILABLE BALANCE="
        f"{decimal_text(available_usdt)} USDT"
    )

    log(
        f"{VERSION}: INITIAL ENTRY PERCENT="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: INITIAL MARGIN BUDGET="
        f"{decimal_text(initial_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: TARGET INITIAL NOTIONAL AT 100x="
        f"{decimal_text(initial_notional_target)} USDT"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE PERCENT="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE BUDGET="
        f"{decimal_text(maximum_exposure_budget)} USDT"
    )

    check(
        "Initial Entry Percent Is 5%",
        INITIAL_ENTRY_PERCENT
        == Decimal("5"),
    )

    check(
        "Maximum Fund Exposure Is 35%",
        MAX_FUND_EXPOSURE_PERCENT
        == Decimal("35"),
    )

    check(
        "Initial Margin Budget Is Positive",
        initial_margin_budget > 0,
    )

    check(
        "Maximum Exposure Budget Is Positive",
        maximum_exposure_budget > 0,
    )

    check(
        "Initial Budget Is Below Maximum Exposure",
        initial_margin_budget
        < maximum_exposure_budget,
    )


    # ==================================================================================
    # TEST 8
    # ==================================================================================

    section(
        f"{VERSION} TEST 8: LOCAL INITIAL QUANTITY CALCULATION"
    )

    raw_quantity = (
        initial_notional_target
        / market_price
    )

    # Safety-biased rounding:
    #
    # R34M always rounds DOWN to the exchange quantity step so the
    # resulting local order envelope cannot exceed the configured
    # initial margin budget merely because of quantity rounding.

    rounded_quantity = floor_to_step(
        raw_quantity,
        QTY_STEP,
    )

    rounded_notional = (
        rounded_quantity
        * market_price
    )

    rounded_margin_required = (
        rounded_notional
        / TARGET_LONG_LEVERAGE
    )

    state[
        "raw_quantity"
    ] = raw_quantity

    state[
        "rounded_quantity"
    ] = rounded_quantity

    state[
        "rounded_notional"
    ] = rounded_notional

    state[
        "rounded_margin_required"
    ] = rounded_margin_required

    log(
        f"{VERSION}: RAW INITIAL QUANTITY="
        f"{decimal_text(raw_quantity)} BTC"
    )

    log(
        f"{VERSION}: QTY STEP="
        f"{decimal_text(QTY_STEP)} BTC"
    )

    log(
        f"{VERSION}: SAFETY-ROUNDED QUANTITY="
        f"{decimal_text(rounded_quantity)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{decimal_text(rounded_notional)} USDT"
    )

    log(
        f"{VERSION}: ROUNDED MARGIN AT 100x="
        f"{decimal_text(rounded_margin_required)} USDT"
    )

    check(
        "Raw Quantity Is Positive",
        raw_quantity > 0,
    )

    check(
        "Rounded Quantity Is Positive",
        rounded_quantity > 0,
    )

    check(
        "Rounded Quantity Does Not Exceed Raw Quantity",
        rounded_quantity <= raw_quantity,
    )


    # ==================================================================================
    # TEST 9
    # ==================================================================================

    section(
        f"{VERSION} TEST 9: QUANTITY PRECISION AND STEP INTEGRITY"
    )

    check(
        "Rounded Quantity Meets Minimum Quantity",
        rounded_quantity
        >= MIN_ORDER_QTY,
    )

    check(
        "Rounded Quantity Is Step-Aligned",
        is_step_aligned(
            rounded_quantity,
            QTY_STEP,
        ),
    )

    quantity_decimal_places = max(
        0,
        -rounded_quantity.as_tuple().exponent,
    )

    check(
        "Rounded Quantity Fits Configured Precision",
        quantity_decimal_places
        <= QTY_PRECISION,
    )

    state[
        "quantity_ready"
    ] = True


    # ==================================================================================
    # TEST 10
    # ==================================================================================

    section(
        f"{VERSION} TEST 10: NOTIONAL AND MARGIN RECONCILIATION"
    )

    check(
        "Rounded Notional Is Positive",
        rounded_notional > 0,
    )

    check(
        "Rounded Margin Requirement Is Positive",
        rounded_margin_required > 0,
    )

    check(
        "Rounded Margin Does Not Exceed Initial 5% Budget",
        rounded_margin_required
        <= initial_margin_budget,
    )

    check(
        "Rounded Margin Is Below Available Balance",
        rounded_margin_required
        <= available_usdt,
    )


    # ==================================================================================
    # TEST 11
    # ==================================================================================

    section(
        f"{VERSION} TEST 11: MAXIMUM EXPOSURE GATE"
    )

    check(
        "Initial Rounded Margin Is Below 35% Maximum Exposure",
        rounded_margin_required
        <= maximum_exposure_budget,
    )

    hypothetical_full_margin = (
        initial_margin_budget
        + (
            available_usdt
            * PYRAMID_SIZE_PERCENT
            / Decimal("100")
            * MAX_PYRAMID_ADDS
        )
        + (
            available_usdt
            * BACKUP_SIZE_PERCENT
            / Decimal("100")
            * MAX_BACKUPS
        )
    )

    log(
        f"{VERSION}: HYPOTHETICAL INITIAL+PYRAMID+BACKUPS MARGIN="
        f"{decimal_text(hypothetical_full_margin)} USDT"
    )

    log(
        f"{VERSION}: MAXIMUM ALLOWED EXPOSURE MARGIN="
        f"{decimal_text(maximum_exposure_budget)} USDT"
    )

    check(
        "Configured Initial Plus Pyramid Plus Backups Fits 35% Cap",
        hypothetical_full_margin
        <= maximum_exposure_budget,
    )

    state[
        "exposure_ready"
    ] = True


    # ==================================================================================
    # TEST 12
    # ==================================================================================

    section(
        f"{VERSION} TEST 12: BUY / LONG INTENT BINDING"
    )

    long_intent = make_order_intent(
        side="BUY",
        position_side="LONG",
        quantity=rounded_quantity,
        reference_price=market_price,
        leverage=TARGET_LONG_LEVERAGE,
    )

    long_intent_hash = hash_object(
        long_intent
    )

    state[
        "long_intent_hash"
    ] = long_intent_hash

    log(
        f"{VERSION}: LONG INTENT SHA256="
        f"{long_intent_hash}"
    )

    check(
        "Long Intent Symbol Is Correct",
        long_intent["symbol"]
        == SYMBOL,
    )

    check(
        "Long Intent Side Is BUY",
        long_intent["side"]
        == "BUY",
    )

    check(
        "Long Intent Position Side Is LONG",
        long_intent["positionSide"]
        == "LONG",
    )

    check(
        "Long Intent Margin Is ISOLATED",
        long_intent["marginMode"]
        == TARGET_MARGIN,
    )

    check(
        "Long Intent Leverage Is 100x",
        long_intent["leverage"]
        == "100",
    )

    check(
        "Long Intent Explicitly Forbids Network Write",
        long_intent[
            "networkWriteAllowed"
        ] is False,
    )


    # ==================================================================================
    # TEST 13
    # ==================================================================================

    section(
        f"{VERSION} TEST 13: SELL / SHORT INTENT BINDING"
    )

    short_intent = make_order_intent(
        side="SELL",
        position_side="SHORT",
        quantity=rounded_quantity,
        reference_price=market_price,
        leverage=TARGET_SHORT_LEVERAGE,
    )

    short_intent_hash = hash_object(
        short_intent
    )

    state[
        "short_intent_hash"
    ] = short_intent_hash

    log(
        f"{VERSION}: SHORT INTENT SHA256="
        f"{short_intent_hash}"
    )

    check(
        "Short Intent Symbol Is Correct",
        short_intent["symbol"]
        == SYMBOL,
    )

    check(
        "Short Intent Side Is SELL",
        short_intent["side"]
        == "SELL",
    )

    check(
        "Short Intent Position Side Is SHORT",
        short_intent["positionSide"]
        == "SHORT",
    )

    check(
        "Short Intent Margin Is ISOLATED",
        short_intent["marginMode"]
        == TARGET_MARGIN,
    )

    check(
        "Short Intent Leverage Is 100x",
        short_intent["leverage"]
        == "100",
    )

    check(
        "Short Intent Explicitly Forbids Network Write",
        short_intent[
            "networkWriteAllowed"
        ] is False,
    )

    check(
        "Long And Short Intent Hashes Are Different",
        long_intent_hash
        != short_intent_hash,
    )


    # ==================================================================================
    # TEST 14
    # ==================================================================================

    section(
        f"{VERSION} TEST 14: STALE MARKET-DATA REJECTION"
    )

    fresh_status = (
        is_market_data_fresh(
            market_time,
            SIGNAL_EXPIRY_SECONDS,
        )
    )

    synthetic_stale_time = (
        int(time.time() * 1000)
        - (
            SIGNAL_EXPIRY_SECONDS
            + 30
        )
        * 1000
    )

    stale_status = (
        is_market_data_fresh(
            synthetic_stale_time,
            SIGNAL_EXPIRY_SECONDS,
        )
    )

    market_age = (
        market_timestamp_age_seconds(
            market_time
        )
    )

    log(
        f"{VERSION}: LIVE MARKET AGE="
        f"{decimal_text(market_age)} seconds"
    )

    check(
        "Live Market Timestamp Is Fresh",
        fresh_status is True,
    )

    check(
        "Synthetic Stale Market Timestamp Is Rejected",
        stale_status is False,
    )


    # ==================================================================================
    # TEST 15
    # ==================================================================================

    section(
        f"{VERSION} TEST 15: DUPLICATE INTENT REJECTION"
    )

    guard = DuplicateIntentGuard()

    first_accept = guard.accept(
        long_intent_hash
    )

    duplicate_accept = guard.accept(
        long_intent_hash
    )

    different_accept = guard.accept(
        short_intent_hash
    )

    check(
        "First Long Intent Is Accepted",
        first_accept is True,
    )

    check(
        "Duplicate Long Intent Is Rejected",
        duplicate_accept is False,
    )

    check(
        "Different Short Intent Is Accepted",
        different_accept is True,
    )


    # ==================================================================================
    # TEST 16
    # ==================================================================================

    section(
        f"{VERSION} TEST 16: DETERMINISTIC LOCAL ORDER PAYLOAD"
    )

    long_payload = make_local_order_payload(
        long_intent
    )

    short_payload = make_local_order_payload(
        short_intent
    )

    long_payload_hash = hash_object(
        long_payload
    )

    short_payload_hash = hash_object(
        short_payload
    )

    state[
        "long_payload_hash"
    ] = long_payload_hash

    state[
        "short_payload_hash"
    ] = short_payload_hash

    log(
        f"{VERSION}: LONG LOCAL PAYLOAD="
        f"{canonical_json(long_payload)}"
    )

    log(
        f"{VERSION}: LONG PAYLOAD SHA256="
        f"{long_payload_hash}"
    )

    log(
        f"{VERSION}: SHORT LOCAL PAYLOAD="
        f"{canonical_json(short_payload)}"
    )

    log(
        f"{VERSION}: SHORT PAYLOAD SHA256="
        f"{short_payload_hash}"
    )

    check(
        "Long Payload Is Local Validation Only",
        long_payload[
            "executionPolicy"
        ] == "LOCAL_VALIDATION_ONLY",
    )

    check(
        "Short Payload Is Local Validation Only",
        short_payload[
            "executionPolicy"
        ] == "LOCAL_VALIDATION_ONLY",
    )

    check(
        "Long Payload Explicitly Forbids Transmission",
        long_payload[
            "networkTransmission"
        ] is False,
    )

    check(
        "Short Payload Explicitly Forbids Transmission",
        short_payload[
            "networkTransmission"
        ] is False,
    )

    check(
        "Long And Short Payload Hashes Are Different",
        long_payload_hash
        != short_payload_hash,
    )


    # ==================================================================================
    # TEST 17
    # ==================================================================================

    section(
        f"{VERSION} TEST 17: PAYLOAD HASH / TAMPER DETECTION"
    )

    repeat_long_payload = (
        make_local_order_payload(
            long_intent
        )
    )

    repeat_hash = hash_object(
        repeat_long_payload
    )

    tampered_payload = dict(
        long_payload
    )

    tampered_payload[
        "quantity"
    ] = "999"

    tampered_hash = hash_object(
        tampered_payload
    )

    check(
        "Identical Payload Recomputes Same SHA256",
        repeat_hash
        == long_payload_hash,
    )

    check(
        "Tampered Payload Produces Different SHA256",
        tampered_hash
        != long_payload_hash,
    )


    # ==================================================================================
    # TEST 18
    # ==================================================================================

    section(
        f"{VERSION} TEST 18: SYNTHETIC DISPATCH INTERCEPTION"
    )

    synthetic_receipt = synthetic_dispatch(
        long_payload,
        long_payload_hash,
    )

    log(
        f"{VERSION}: SYNTHETIC RECEIPT="
        f"{canonical_json(synthetic_receipt)}"
    )

    check(
        "Synthetic Receipt Was Created",
        synthetic_receipt is not None,
    )

    check(
        "Synthetic Receipt Marks Dispatch As Synthetic",
        synthetic_receipt[
            "synthetic"
        ] is True,
    )

    check(
        "Synthetic Receipt Confirms No Transmission",
        synthetic_receipt[
            "transmitted"
        ] is False,
    )

    check(
        "Synthetic Receipt Confirms No Network Write",
        synthetic_receipt[
            "networkWrite"
        ] is False,
    )

    check(
        "Synthetic Receipt Confirms No Real Order",
        synthetic_receipt[
            "realOrder"
        ] is False,
    )

    check(
        "Synthetic Receipt Confirms No Demo Order",
        synthetic_receipt[
            "demoOrder"
        ] is False,
    )

    check(
        "Synthetic Dispatch Count Is Exactly One",
        state[
            "synthetic_dispatch_count"
        ] == 1,
    )


    # ==================================================================================
    # TEST 19
    # ==================================================================================

    section(
        f"{VERSION} TEST 19: FINAL WRITE FIREBREAK VERIFICATION"
    )

    check(
        "Authenticated POST Is Rejected Locally",
        expect_local_rejection(
            authenticated_post
        ),
    )

    check(
        "Real Order Function Is Rejected Locally",
        expect_local_rejection(
            execute_real_order
        ),
    )

    check(
        "Demo Order Function Is Rejected Locally",
        expect_local_rejection(
            execute_demo_order
        ),
    )

    check(
        "Leverage Mutation Is Rejected Locally",
        expect_local_rejection(
            mutate_leverage
        ),
    )

    check(
        "Margin Mutation Is Rejected Locally",
        expect_local_rejection(
            mutate_margin
        ),
    )

    check(
        "Position Mutation Is Rejected Locally",
        expect_local_rejection(
            mutate_position
        ),
    )

    check(
        "Account Mutation Is Rejected Locally",
        expect_local_rejection(
            mutate_account
        ),
    )

    check(
        "Exchange Network Writes Remain Zero",
        state[
            "network_writes"
        ] == 0,
    )

    check(
        "Leverage Mutations Remain Zero",
        state[
            "leverage_mutations"
        ] == 0,
    )

    check(
        "Margin Mutations Remain Zero",
        state[
            "margin_mutations"
        ] == 0,
    )

    check(
        "Position Mutations Remain Zero",
        state[
            "position_mutations"
        ] == 0,
    )

    check(
        "Account Mutations Remain Zero",
        state[
            "account_mutations"
        ] == 0,
    )

    check(
        "Real Orders Remain Zero",
        state[
            "real_orders"
        ] == 0,
    )

    check(
        "Demo Orders Remain Zero",
        state[
            "demo_orders"
        ] == 0,
    )


    # ==================================================================================
    # TEST 20
    # ==================================================================================

    section(
        f"{VERSION} TEST 20: FINAL EXECUTION ENVELOPE READINESS"
    )

    check(
        "Authenticated Credentials Are Ready",
        all([
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        ]),
    )

    check(
        "Available Balance Is Ready",
        available_usdt > 0,
    )

    check(
        f"{SYMBOL} Has Zero Active Positions",
        len(active_positions) == 0,
    )

    check(
        "ISOLATED Margin Is Ready",
        str(observed_margin).upper()
        == TARGET_MARGIN,
    )

    check(
        "100x Long And Short Leverage Are Ready",
        (
            observed_long
            == TARGET_LONG_LEVERAGE
            and
            observed_short
            == TARGET_SHORT_LEVERAGE
        ),
    )

    check(
        "Live Market Price Is Ready",
        state[
            "market_price_ready"
        ] is True,
    )

    check(
        "Quantity Construction Is Ready",
        state[
            "quantity_ready"
        ] is True,
    )

    check(
        "Exposure Gate Is Ready",
        state[
            "exposure_ready"
        ] is True,
    )

    check(
        "Long Intent Hash Exists",
        bool(
            state[
                "long_intent_hash"
            ]
        ),
    )

    check(
        "Short Intent Hash Exists",
        bool(
            state[
                "short_intent_hash"
            ]
        ),
    )

    check(
        "Long Payload Hash Exists",
        bool(
            state[
                "long_payload_hash"
            ]
        ),
    )

    check(
        "Short Payload Hash Exists",
        bool(
            state[
                "short_payload_hash"
            ]
        ),
    )

    check(
        "Synthetic Dispatch Was Intercepted",
        state[
            "synthetic_dispatch_count"
        ] == 1,
    )

    check(
        "Write Firebreak Remains Intact",
        (
            NETWORK_WRITES is False
            and
            state[
                "network_writes"
            ] == 0
            and
            state[
                "real_orders"
            ] == 0
            and
            state[
                "demo_orders"
            ] == 0
        ),
    )

    state[
        "execution_envelope_ready"
    ] = True

    state[
        "phase"
    ] = "LOCAL_EXECUTION_ENVELOPE_VALIDATED"

    state[
        "final_validation_status"
    ] = "PASS"


    # ==================================================================================
    # FINAL SUMMARY
    # ==================================================================================

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        f"{VERSION}: PHASE="
        f"{state['phase']}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GET COUNT="
        f"{state['authenticated_get_count']}"
    )

    log(
        f"{VERSION}: PUBLIC GET COUNT="
        f"{state['public_get_count']}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_usdt)}"
    )

    log(
        f"{VERSION}: ACTIVE POSITIONS="
        f"{state['active_positions']}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{state['observed_margin']}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{decimal_text(observed_long)}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{decimal_text(observed_short)}x"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{decimal_text(market_price)}"
    )

    log(
        f"{VERSION}: INITIAL MARGIN BUDGET="
        f"{decimal_text(initial_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: INITIAL NOTIONAL TARGET="
        f"{decimal_text(initial_notional_target)} USDT"
    )

    log(
        f"{VERSION}: RAW QUANTITY="
        f"{decimal_text(raw_quantity)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED QUANTITY="
        f"{decimal_text(rounded_quantity)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{decimal_text(rounded_notional)} USDT"
    )

    log(
        f"{VERSION}: ROUNDED MARGIN="
        f"{decimal_text(rounded_margin_required)} USDT"
    )

    log(
        f"{VERSION}: LONG INTENT SHA256="
        f"{long_intent_hash}"
    )

    log(
        f"{VERSION}: SHORT INTENT SHA256="
        f"{short_intent_hash}"
    )

    log(
        f"{VERSION}: LONG PAYLOAD SHA256="
        f"{long_payload_hash}"
    )

    log(
        f"{VERSION}: SHORT PAYLOAD SHA256="
        f"{short_payload_hash}"
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{state['synthetic_dispatch_count']}"
    )

    log(
        f"{VERSION}: EXECUTION ENVELOPE READY="
        f"{state['execution_envelope_ready']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{state['network_writes']}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{state['real_orders']}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{state['demo_orders']}"
    )

    log(
        f"{VERSION}: FINAL VALIDATION STATUS="
        f"{state['final_validation_status']}"
    )

    section(
        f"{VERSION}: IMPORTANT: "
        f"ORDER TRANSMISSION REMAINS DISABLED"
    )


# ======================================================================================
# HEARTBEAT
# ======================================================================================

def heartbeat_loop():

    section(
        f"{VERSION}: ENTERING PERSISTENT HEALTH / HEARTBEAT MODE"
    )

    while True:

        time.sleep(30)

        state[
            "heartbeat"
        ] += 1

        log(
            f"{VERSION}: HEARTBEAT "
            f"{state['heartbeat']} | "
            f"phase={state['phase']} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get="
            f"{state['authenticated_get_count']} | "
            f"public-get="
            f"{state['public_get_count']} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION} | "
            f"demo-execution="
            f"{DEMO_ORDER_EXECUTION} | "
            f"network-writes="
            f"{NETWORK_WRITES} | "
            f"available-usdt="
            f"{decimal_text(state['available_usdt'])} | "
            f"active-positions="
            f"{state['active_positions']} | "
            f"observed-margin="
            f"{state['observed_margin']} | "
            f"observed-long="
            f"{decimal_text(state['observed_long_leverage'])} | "
            f"observed-short="
            f"{decimal_text(state['observed_short_leverage'])} | "
            f"market-price="
            f"{decimal_text(state['market_price'])} | "
            f"rounded-qty="
            f"{decimal_text(state['rounded_quantity'])} | "
            f"synthetic-dispatch="
            f"{state['synthetic_dispatch_count']} | "
            f"execution-envelope-ready="
            f"{state['execution_envelope_ready']}"
        )


# ======================================================================================
# ENTRYPOINT
# ======================================================================================

def main():

    try:

        start_health_server()

        run_validation()

        heartbeat_loop()

    except KeyboardInterrupt:

        log(
            f"{VERSION}: STOPPED"
        )

        sys.exit(0)

    except Exception as exc:

        state[
            "phase"
        ] = "VALIDATION_FAILED"

        state[
            "final_validation_status"
        ] = "FAIL"

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        log(
            f"{VERSION}: NETWORK WRITES="
            f"{state['network_writes']}"
        )

        log(
            f"{VERSION}: REAL ORDERS="
            f"{state['real_orders']}"
        )

        log(
            f"{VERSION}: DEMO ORDERS="
            f"{state['demo_orders']}"
        )

        raise


if __name__ == "__main__":
    main()
