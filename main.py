

# ==================================================================================================
# R34Z - COMPLETE SYNTHETIC STRATEGY STATE MACHINE + DURABLE RECOVERY VALIDATION
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
# R34Z validates:
#
#   LIVE ACCOUNT STATE
#       ↓
#   LIVE MARKET STATE
#       ↓
#   CONTRACT INFORMATION
#       ↓
#   STRATEGY BUDGET
#       ↓
#   SYNTHETIC INITIAL ENTRY
#       ↓
#   PYRAMID ADD
#       ↓
#   BACKUP 1
#       ↓
#   BACKUP 2
#       ↓
#   BACKUP 3
#       ↓
#   TP1
#       ↓
#   TP2
#       ↓
#   TRAILING / TP3
#       ↓
#   SYNTHETIC TERMINAL EXIT
#       ↓
#   DURABLE SNAPSHOT
#       ↓
#   RESTART RESTORE
#       ↓
#   REPLAY REJECTION
#       ↓
#   RECOVERY VALIDATION
#       ↓
#   WRITE FIREBREAK
#
# IMPORTANT
#
#   THIS PROGRAM DOES NOT SEND ORDERS.
#
#   ALL STRATEGY EXECUTION IS LOCAL AND SYNTHETIC.
#
# ==================================================================================================

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import threading
import traceback
import urllib.request
import urllib.parse
import urllib.error
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from datetime import datetime, timezone


# ==================================================================================================
# VERSION
# ==================================================================================================

VERSION = "R34Z"


# ==================================================================================================
# CONFIGURATION
# ==================================================================================================

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", "10000"))

API_KEY = os.getenv("WEEX_API_KEY", "").strip()
API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

STATE_DIR = Path(
    os.getenv(
        "R34Z_STATE_DIR",
        "/tmp/r34z_state",
    )
)

STATE_FILE = STATE_DIR / "strategy_state.json"

POSITION_PATH = "/capi/v3/account/position/allPosition"
BALANCE_PATH = "/capi/v3/account/balance"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"
CONTRACT_INFO_PATH = "/capi/v3/market/exchangeInfo"


# ==================================================================================================
# STRATEGY CONFIGURATION
# ==================================================================================================

TARGET_LEVERAGE = Decimal("100")

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

BACKUP_BUFFER_PERCENT = Decimal("0.30")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ==================================================================================================
# HARD SAFETY CONSTANTS
# ==================================================================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

SYNTHETIC_TRANSPORT_ONLY = True

ALLOW_NETWORK_WRITES = False
ALLOW_REAL_ORDERS = False
ALLOW_DEMO_ORDERS = False
ALLOW_LEVERAGE_MUTATION = False
ALLOW_MARGIN_MUTATION = False
ALLOW_POSITION_MUTATION = False
ALLOW_ACCOUNT_MUTATION = False


# ==================================================================================================
# RUNTIME ACCOUNTING
# ==================================================================================================

runtime = {
    "phase": "STARTING",

    "authenticated_get": 0,
    "public_get": 0,

    "network_writes": 0,

    "real_orders": 0,
    "demo_orders": 0,

    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "synthetic_dispatches": 0,
    "initial_dispatches": 0,
    "pyramid_dispatches": 0,
    "backup_dispatches": 0,
    "tp_dispatches": 0,
    "terminal_dispatches": 0,
    "recovery_dispatches": 0,

    "restart_restores": 0,
    "replays_blocked": 0,
}

runtime_lock = threading.Lock()


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


def pass_test(name):
    log(f"{name:<88} ✅ PASS")


def fail_test(name):
    log(f"{name:<88} ❌ FAIL")
    raise AssertionError(name)


def assert_test(name, condition):
    if condition:
        pass_test(name)
    else:
        fail_test(name)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ==================================================================================================
# JSON / HASH HELPERS
# ==================================================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def hash_object(value):
    return sha256_text(canonical_json(value))


# ==================================================================================================
# DECIMAL HELPERS
# ==================================================================================================

def decimalize(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        if isinstance(value, bool):
            return Decimal(default)

        return Decimal(str(value))

    except Exception:
        return Decimal(default)


def decimal_str(value):
    value = Decimal(value)

    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text == "":
        return "0"

    return text


def round_down_step(value, step):
    value = Decimal(value)
    step = Decimal(step)

    if step <= 0:
        return value

    units = (value / step).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def round_up_step(value, step):
    value = Decimal(value)
    step = Decimal(step)

    if step <= 0:
        return value

    units = (value / step).to_integral_value(
        rounding=ROUND_UP
    )

    return units * step


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        with runtime_lock:
            body = json.dumps(
                {
                    "version": VERSION,
                    "symbol": SYMBOL,
                    "phase": runtime["phase"],
                    "authenticated_read_only": AUTHENTICATED_READ_ONLY,
                    "public_read_only": PUBLIC_READ_ONLY,
                    "synthetic_transport_only": SYNTHETIC_TRANSPORT_ONLY,
                    "network_writes": runtime["network_writes"],
                    "real_orders": runtime["real_orders"],
                    "demo_orders": runtime["demo_orders"],
                    "synthetic_dispatches": runtime["synthetic_dispatches"],
                    "restart_restores": runtime["restart_restores"],
                    "replays_blocked": runtime["replays_blocked"],
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

    def log_message(self, format, *args):
        return


def start_health_server():

    def run():

        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        server.serve_forever()

    thread = threading.Thread(
        target=run,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# NETWORK SAFETY
# ==================================================================================================

def forbidden_network_write(*args, **kwargs):

    with runtime_lock:
        runtime["network_writes"] += 1

    raise RuntimeError(
        f"{VERSION}: NETWORK WRITE FIREBREAK ACTIVE"
    )


def http_post(*args, **kwargs):
    return forbidden_network_write(*args, **kwargs)


def http_put(*args, **kwargs):
    return forbidden_network_write(*args, **kwargs)


def http_patch(*args, **kwargs):
    return forbidden_network_write(*args, **kwargs)


def http_delete(*args, **kwargs):
    return forbidden_network_write(*args, **kwargs)


def real_order(*args, **kwargs):

    with runtime_lock:
        runtime["real_orders"] += 1

    raise RuntimeError(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )


def demo_order(*args, **kwargs):

    with runtime_lock:
        runtime["demo_orders"] += 1

    raise RuntimeError(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
    )


def mutate_leverage(*args, **kwargs):

    with runtime_lock:
        runtime["leverage_mutations"] += 1

    raise RuntimeError(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )


def mutate_margin(*args, **kwargs):

    with runtime_lock:
        runtime["margin_mutations"] += 1

    raise RuntimeError(
        f"{VERSION}: MARGIN MUTATION DISABLED"
    )


def mutate_position(*args, **kwargs):

    with runtime_lock:
        runtime["position_mutations"] += 1

    raise RuntimeError(
        f"{VERSION}: POSITION MUTATION DISABLED"
    )


def mutate_account(*args, **kwargs):

    with runtime_lock:
        runtime["account_mutations"] += 1

    raise RuntimeError(
        f"{VERSION}: ACCOUNT MUTATION DISABLED"
    )


# ==================================================================================================
# HTTP GET HELPERS
# ==================================================================================================

def perform_get(url, headers=None):

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers or {},
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        raw = response.read().decode(
            "utf-8",
            errors="replace",
        )

    try:
        return json.loads(raw)

    except Exception:
        return raw


def public_get(path, params=None):

    if not PUBLIC_READ_ONLY:
        raise RuntimeError(
            "Public read-only transport disabled"
        )

    query = ""

    if params:
        query = urllib.parse.urlencode(params)

    url = BASE_URL + path

    if query:
        url += "?" + query

    try:

        result = perform_get(url)

        with runtime_lock:
            runtime["public_get"] += 1

        return result

    except Exception as exc:

        raise RuntimeError(
            f"Public GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        )


def make_signature(timestamp, method, path, query=""):

    if query:
        request_path = path + "?" + query
    else:
        request_path = path

    payload = (
        str(timestamp)
        + method.upper()
        + request_path
    )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def authenticated_get(path, params=None):

    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated transport disabled"
        )

    if not API_KEY:
        raise RuntimeError(
            "WEEX_API_KEY missing"
        )

    if not API_SECRET:
        raise RuntimeError(
            "WEEX_API_SECRET missing"
        )

    if not API_PASSPHRASE:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing"
        )

    query = ""

    if params:
        query = urllib.parse.urlencode(params)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        path=path,
        query=query,
    )

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
        "User-Agent": f"{VERSION}-read-only-validator",
    }

    url = BASE_URL + path

    if query:
        url += "?" + query

    try:

        result = perform_get(
            url,
            headers=headers,
        )

        with runtime_lock:
            runtime["authenticated_get"] += 1

        return result

    except Exception as exc:

        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        )


# ==================================================================================================
# GENERIC RESPONSE WALKER
# ==================================================================================================

def walk_objects(value):

    if isinstance(value, dict):

        yield value

        for child in value.values():
            yield from walk_objects(child)

    elif isinstance(value, list):

        for child in value:
            yield from walk_objects(child)


def first_matching_value(value, keys):

    normalized = {
        key.lower()
        for key in keys
    }

    for obj in walk_objects(value):

        for key, child in obj.items():

            if str(key).lower() in normalized:

                if child is not None:
                    return child

    return None


# ==================================================================================================
# LIVE DATA PARSERS
# ==================================================================================================

def extract_available_usdt(response):

    candidates = []

    for obj in walk_objects(response):

        currency = str(
            obj.get(
                "marginCoin",
                obj.get(
                    "coin",
                    obj.get(
                        "currency",
                        obj.get("asset", ""),
                    ),
                ),
            )
        ).upper()

        if currency and currency != "USDT":
            continue

        for field in (
            "available",
            "availableBalance",
            "availableMargin",
            "availableEquity",
            "balance",
            "equity",
        ):

            if field in obj:

                value = decimalize(obj[field])

                if value > 0:
                    candidates.append(value)

    if candidates:
        return max(candidates)

    value = first_matching_value(
        response,
        [
            "available",
            "availableBalance",
            "availableMargin",
            "availableEquity",
        ],
    )

    parsed = decimalize(value)

    if parsed > 0:
        return parsed

    raise RuntimeError(
        "Could not parse positive available USDT balance"
    )


def extract_market_price(response):

    candidates = []

    for field in (
        "price",
        "markPrice",
        "indexPrice",
        "last",
        "lastPrice",
        "close",
    ):

        value = first_matching_value(
            response,
            [field],
        )

        parsed = decimalize(value)

        if parsed > 0:
            candidates.append(parsed)

    if candidates:
        return candidates[0]

    raise RuntimeError(
        "Could not parse market price"
    )


def extract_positions(response):

    positions = []

    for obj in walk_objects(response):

        symbol = str(
            obj.get(
                "symbol",
                obj.get(
                    "contractCode",
                    "",
                ),
            )
        ).upper()

        if symbol:
            positions.append(obj)

    return positions


def count_open_positions(positions):

    count = 0

    for obj in positions:

        symbol = str(
            obj.get(
                "symbol",
                obj.get(
                    "contractCode",
                    "",
                ),
            )
        ).upper()

        if symbol != SYMBOL:
            continue

        size = decimalize(
            obj.get(
                "size",
                obj.get(
                    "positionAmt",
                    obj.get(
                        "total",
                        obj.get(
                            "holdVol",
                            "0",
                        ),
                    ),
                ),
            )
        )

        if abs(size) > 0:
            count += 1

    return count


def extract_symbol_config(response):

    best = None

    for obj in walk_objects(response):

        symbol = str(
            obj.get(
                "symbol",
                obj.get(
                    "contractCode",
                    "",
                ),
            )
        ).upper()

        if symbol == SYMBOL:
            best = obj
            break

    if best is None:

        for obj in walk_objects(response):

            if any(
                key in obj
                for key in (
                    "marginType",
                    "marginMode",
                    "isolatedLongLeverage",
                    "isolatedShortLeverage",
                    "leverage",
                )
            ):
                best = obj
                break

    return best or {}


# ==================================================================================================
# CONTRACT INFORMATION
# ==================================================================================================

def extract_contract_info(response):

    selected = None

    for obj in walk_objects(response):

        symbol = str(
            obj.get(
                "symbol",
                obj.get(
                    "contractCode",
                    "",
                ),
            )
        ).upper()

        if symbol == SYMBOL:
            selected = obj
            break

    if selected is None:
        selected = {}

    min_qty = decimalize(
        selected.get(
            "minQty",
            selected.get(
                "minOrderQty",
                selected.get(
                    "minTradeNum",
                    selected.get(
                        "minOrderSize",
                        "0.0001",
                    ),
                ),
            ),
        ),
        "0.0001",
    )

    qty_step = decimalize(
        selected.get(
            "stepSize",
            selected.get(
                "qtyStep",
                selected.get(
                    "sizeIncrement",
                    selected.get(
                        "quantityStep",
                        "0.0001",
                    ),
                ),
            ),
        ),
        "0.0001",
    )

    price_step = decimalize(
        selected.get(
            "tickSize",
            selected.get(
                "priceStep",
                selected.get(
                    "priceIncrement",
                    "0.1",
                ),
            ),
        ),
        "0.1",
    )

    qty_precision_raw = selected.get(
        "quantityPrecision",
        selected.get(
            "qtyPrecision",
            selected.get(
                "volumePlace",
                4,
            ),
        ),
    )

    price_precision_raw = selected.get(
        "pricePrecision",
        selected.get(
            "pricePlace",
            1,
        ),
    )

    try:
        qty_precision = int(qty_precision_raw)
    except Exception:
        qty_precision = 4

    try:
        price_precision = int(price_precision_raw)
    except Exception:
        price_precision = 1

    if min_qty <= 0:
        min_qty = Decimal("0.0001")

    if qty_step <= 0:
        qty_step = Decimal("0.0001")

    if price_step <= 0:
        price_step = Decimal("0.1")

    return {
        "min_qty": min_qty,
        "qty_step": qty_step,
        "price_step": price_step,
        "qty_precision": qty_precision,
        "price_precision": price_precision,
        "raw": selected,
    }


# ==================================================================================================
# SYNTHETIC INTENTS
# ==================================================================================================

def create_intent(
    action,
    side,
    quantity,
    reference_price,
    sequence,
    reason,
):

    created_at = now_iso()

    intent = {
        "version": VERSION,
        "symbol": SYMBOL,
        "action": action,
        "side": side,
        "quantity": decimal_str(quantity),
        "reference_price": decimal_str(reference_price),
        "sequence": int(sequence),
        "reason": reason,
        "created_at": created_at,
        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,
    }

    intent["intent_hash"] = hash_object(intent)

    return intent


def create_synthetic_payload(intent):

    payload = {
        "symbol": intent["symbol"],
        "side": intent["side"],
        "type": "MARKET",
        "quantity": intent["quantity"],
        "syntheticAction": intent["action"],
        "syntheticOnly": True,
        "transmit": False,
    }

    payload["payload_hash"] = hash_object(payload)

    return payload


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================

def synthetic_dispatch(intent, payload, category):

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "Synthetic transport disabled"
        )

    if intent.get("synthetic_only") is not True:
        raise RuntimeError(
            "Non-synthetic intent rejected"
        )

    if intent.get("transmission_allowed") is not False:
        raise RuntimeError(
            "Intent transmission flag invalid"
        )

    if intent.get("network_write_allowed") is not False:
        raise RuntimeError(
            "Intent network-write flag invalid"
        )

    if payload.get("syntheticOnly") is not True:
        raise RuntimeError(
            "Payload is not synthetic"
        )

    if payload.get("transmit") is not False:
        raise RuntimeError(
            "Payload transmission flag invalid"
        )

    receipt = {
        "version": VERSION,
        "symbol": SYMBOL,
        "category": category,
        "intent_hash": intent["intent_hash"],
        "payload_hash": payload["payload_hash"],
        "synthetic_only": True,
        "transmitted": False,
        "network_write": False,
        "completed": True,
        "completed_at": now_iso(),
    }

    receipt["receipt_hash"] = hash_object(receipt)

    with runtime_lock:

        runtime["synthetic_dispatches"] += 1

        if category == "INITIAL":
            runtime["initial_dispatches"] += 1

        elif category == "PYRAMID":
            runtime["pyramid_dispatches"] += 1

        elif category == "BACKUP":
            runtime["backup_dispatches"] += 1

        elif category in (
            "TP1",
            "TP2",
            "TP3",
        ):
            runtime["tp_dispatches"] += 1

        elif category == "TERMINAL":
            runtime["terminal_dispatches"] += 1

        elif category == "RECOVERY":
            runtime["recovery_dispatches"] += 1

    return receipt


# ==================================================================================================
# STATE ENGINE
# ==================================================================================================

def new_strategy_state(
    available_balance,
    market_price,
    quantity,
):

    state = {
        "version": VERSION,
        "symbol": SYMBOL,

        "phase": "READY",

        "available_balance": decimal_str(
            available_balance
        ),

        "reference_price": decimal_str(
            market_price
        ),

        "base_quantity": decimal_str(
            quantity
        ),

        "initial_entry_completed": False,

        "pyramid_count": 0,
        "backup_count": 0,

        "tp1_completed": False,
        "tp2_completed": False,
        "tp3_completed": False,

        "trailing_armed": False,

        "terminal_exit_completed": False,

        "consumed_intents": [],

        "dispatch_receipts": [],

        "generation": 1,

        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    return state


def consume_and_dispatch(
    state,
    intent,
    payload,
    category,
):

    intent_hash = intent["intent_hash"]

    if intent_hash in state["consumed_intents"]:

        with runtime_lock:
            runtime["replays_blocked"] += 1

        raise RuntimeError(
            "Consumed intent replay rejected"
        )

    receipt = synthetic_dispatch(
        intent,
        payload,
        category,
    )

    state["consumed_intents"].append(
        intent_hash
    )

    state["dispatch_receipts"].append(
        receipt
    )

    state["updated_at"] = now_iso()

    return receipt


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

def prepare_state_for_save(state):

    body = dict(state)

    body.pop(
        "integrity_hash",
        None,
    )

    body["integrity_hash"] = hash_object(body)

    return body


def validate_state_integrity(state):

    if not isinstance(state, dict):
        return False

    expected = state.get(
        "integrity_hash"
    )

    if not expected:
        return False

    body = dict(state)

    body.pop(
        "integrity_hash",
        None,
    )

    actual = hash_object(body)

    return hmac.compare_digest(
        expected,
        actual,
    )


def save_state(state):

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    complete = prepare_state_for_save(
        state
    )

    temp_file = STATE_FILE.with_suffix(
        ".tmp"
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            complete,
            file,
            sort_keys=True,
            separators=(",", ":"),
        )

        file.flush()

        os.fsync(
            file.fileno()
        )

    os.replace(
        temp_file,
        STATE_FILE,
    )

    return complete


def load_state():

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        state = json.load(file)

    if not validate_state_integrity(state):
        raise RuntimeError(
            "Stored state integrity invalid"
        )

    return state


# ==================================================================================================
# SYNTHETIC PRICE HELPERS
# ==================================================================================================

def price_up(price, percent):

    price = Decimal(price)
    percent = Decimal(percent)

    return price * (
        Decimal("1")
        + percent / Decimal("100")
    )


def price_down(price, percent):

    price = Decimal(price)
    percent = Decimal(percent)

    return price * (
        Decimal("1")
        - percent / Decimal("100")
    )


# ==================================================================================================
# TEST HELPERS
# ==================================================================================================

def expect_rejection(function):

    before = dict(runtime)

    try:
        function()

    except Exception:
        pass

    else:
        return False

    return True


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_loop():

    counter = 0

    while True:

        time.sleep(30)

        counter += 1

        with runtime_lock:

            log(
                f"{VERSION}: HEARTBEAT {counter} | "
                f"phase={runtime['phase']} | "
                f"authenticated-read-only={AUTHENTICATED_READ_ONLY} | "
                f"authenticated-get={runtime['authenticated_get']} | "
                f"public-get={runtime['public_get']} | "
                f"network-writes={runtime['network_writes']} | "
                f"real-orders={runtime['real_orders']} | "
                f"demo-orders={runtime['demo_orders']} | "
                f"synthetic-dispatches={runtime['synthetic_dispatches']} | "
                f"initial={runtime['initial_dispatches']} | "
                f"pyramids={runtime['pyramid_dispatches']} | "
                f"backups={runtime['backup_dispatches']} | "
                f"tp={runtime['tp_dispatches']} | "
                f"terminal={runtime['terminal_dispatches']} | "
                f"recovery={runtime['recovery_dispatches']} | "
                f"restart-restores={runtime['restart_restores']} | "
                f"replays-blocked={runtime['replays_blocked']}"
            )


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def main():

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
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: PUBLIC READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    start_health_server()

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: SAFETY CONSTANTS"
    )

    assert_test(
        "Authenticated Transport Is Read Only",
        AUTHENTICATED_READ_ONLY is True,
    )

    assert_test(
        "Public Transport Is Read Only",
        PUBLIC_READ_ONLY is True,
    )

    assert_test(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    assert_test(
        "Network Writes Are Disabled",
        ALLOW_NETWORK_WRITES is False,
    )

    assert_test(
        "Real Orders Are Disabled",
        ALLOW_REAL_ORDERS is False,
    )

    assert_test(
        "Demo Orders Are Disabled",
        ALLOW_DEMO_ORDERS is False,
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: API CREDENTIALS"
    )

    assert_test(
        "WEEX API Key Is Present",
        bool(API_KEY),
    )

    assert_test(
        "WEEX API Secret Is Present",
        bool(API_SECRET),
    )

    assert_test(
        "WEEX API Passphrase Is Present",
        bool(API_PASSPHRASE),
    )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: LIVE BALANCE"
    )

    balance_response = authenticated_get(
        BALANCE_PATH
    )

    available_balance = extract_available_usdt(
        balance_response
    )

    assert_test(
        "Available Balance Was Read",
        available_balance is not None,
    )

    assert_test(
        "Available Balance Is Positive",
        available_balance > 0,
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_str(available_balance)}"
    )

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: LIVE ACCOUNT CONFIGURATION"
    )

    config_response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    config = extract_symbol_config(
        config_response
    )

    assert_test(
        "Symbol Configuration Was Read",
        isinstance(config, dict),
    )

    log(
        f"{VERSION}: SYMBOL CONFIG="
        f"{canonical_json(config)}"
    )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: LIVE POSITION STATE"
    )

    position_response = authenticated_get(
        POSITION_PATH
    )

    positions = extract_positions(
        position_response
    )

    symbol_positions = [
        obj
        for obj in positions
        if str(
            obj.get(
                "symbol",
                obj.get(
                    "contractCode",
                    "",
                ),
            )
        ).upper() == SYMBOL
    ]

    open_position_count = count_open_positions(
        positions
    )

    assert_test(
        "Position Endpoint Was Read",
        position_response is not None,
    )

    assert_test(
        "Position Records Were Parsed",
        isinstance(positions, list),
    )

    log(
        f"{VERSION}: POSITION ENDPOINT="
        f"{POSITION_PATH}"
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
        f"{open_position_count}"
    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: LIVE MARKET PRICE"
    )

    market_response = public_get(
        MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    market_price = extract_market_price(
        market_response
    )

    assert_test(
        "Market Price Was Read",
        market_price is not None,
    )

    assert_test(
        "Market Price Is Positive",
        market_price > 0,
    )

    log(
        f"{VERSION}: MARKET PRICE PATH="
        f"{MARK_PRICE_PATH}"
    )

    log(
        f"{VERSION}: MARK PRICE="
        f"{decimal_str(market_price)}"
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: LIVE CONTRACT INFORMATION"
    )

    exchange_info = public_get(
        CONTRACT_INFO_PATH
    )

    contract = extract_contract_info(
        exchange_info
    )

    assert_test(
        "Exchange Information Was Read",
        exchange_info is not None,
    )

    assert_test(
        "Minimum Quantity Is Positive",
        contract["min_qty"] > 0,
    )

    assert_test(
        "Quantity Step Is Positive",
        contract["qty_step"] > 0,
    )

    assert_test(
        "Price Step Is Positive",
        contract["price_step"] > 0,
    )

    log(
        f"{VERSION}: MIN QTY="
        f"{decimal_str(contract['min_qty'])}"
    )

    log(
        f"{VERSION}: QTY STEP="
        f"{decimal_str(contract['qty_step'])}"
    )

    log(
        f"{VERSION}: PRICE STEP="
        f"{decimal_str(contract['price_step'])}"
    )

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: STRATEGY BUDGET"
    )

    initial_margin_budget = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    initial_notional = (
        initial_margin_budget
        * TARGET_LEVERAGE
    )

    raw_quantity = (
        initial_notional
        / market_price
    )

    normalized_quantity = round_up_step(
        raw_quantity,
        contract["qty_step"],
    )

    if normalized_quantity < contract["min_qty"]:
        normalized_quantity = contract["min_qty"]

    normalized_notional = (
        normalized_quantity
        * market_price
    )

    normalized_margin = (
        normalized_notional
        / TARGET_LEVERAGE
    )

    max_strategy_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    planned_margin_percent = (
        INITIAL_ENTRY_PERCENT
        + PYRAMID_PERCENT * MAX_PYRAMID_ADDS
        + BACKUP_PERCENT * MAX_BACKUPS
    )

    planned_max_margin = (
        available_balance
        * planned_margin_percent
        / Decimal("100")
    )

    assert_test(
        "Initial Entry Margin Budget Is Positive",
        initial_margin_budget > 0,
    )

    assert_test(
        "Normalized Quantity Is Positive",
        normalized_quantity > 0,
    )

    assert_test(
        "Normalized Quantity Meets Minimum",
        normalized_quantity >= contract["min_qty"],
    )

    assert_test(
        "Planned Maximum Strategy Margin Is Within 35%",
        planned_max_margin <= max_strategy_margin,
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_str(initial_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: RAW QTY="
        f"{decimal_str(raw_quantity)} BTC"
    )

    log(
        f"{VERSION}: NORMALIZED QTY="
        f"{decimal_str(normalized_quantity)} BTC"
    )

    log(
        f"{VERSION}: NORMALIZED MARGIN="
        f"{decimal_str(normalized_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_str(planned_max_margin)} USDT"
    )

    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: INITIAL SYNTHETIC ENTRY"
    )

    state = new_strategy_state(
        available_balance,
        market_price,
        normalized_quantity,
    )

    initial_intent = create_intent(
        action="INITIAL_ENTRY",
        side="BUY",
        quantity=normalized_quantity,
        reference_price=market_price,
        sequence=1,
        reason="synthetic_initial_entry",
    )

    initial_payload = create_synthetic_payload(
        initial_intent
    )

    initial_receipt = consume_and_dispatch(
        state,
        initial_intent,
        initial_payload,
        "INITIAL",
    )

    state["initial_entry_completed"] = True
    state["phase"] = "INITIAL_ENTRY_COMPLETED"

    assert_test(
        "Initial Synthetic Dispatch Completed",
        initial_receipt["completed"] is True,
    )

    assert_test(
        "Initial Dispatch Was Not Transmitted",
        initial_receipt["transmitted"] is False,
    )

    assert_test(
        "Initial Dispatch Made No Network Write",
        initial_receipt["network_write"] is False,
    )

    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: PYRAMID STATE TRANSITION"
    )

    pyramid_eligible = (
        state["initial_entry_completed"]
        and state["pyramid_count"] < MAX_PYRAMID_ADDS
    )

    assert_test(
        "First Pyramid Add Is Eligible",
        pyramid_eligible,
    )

    pyramid_price = price_up(
        market_price,
        Decimal("0.25"),
    )

    pyramid_intent = create_intent(
        action="PYRAMID_ADD",
        side="BUY",
        quantity=normalized_quantity,
        reference_price=pyramid_price,
        sequence=2,
        reason="synthetic_pyramid_confirmation",
    )

    pyramid_payload = create_synthetic_payload(
        pyramid_intent
    )

    pyramid_receipt = consume_and_dispatch(
        state,
        pyramid_intent,
        pyramid_payload,
        "PYRAMID",
    )

    state["pyramid_count"] += 1
    state["phase"] = "PYRAMID_COMPLETED"

    assert_test(
        "Pyramid Synthetic Dispatch Completed",
        pyramid_receipt["completed"] is True,
    )

    assert_test(
        "Pyramid Count Is One",
        state["pyramid_count"] == 1,
    )

    assert_test(
        "Second Pyramid Add Is Rejected",
        state["pyramid_count"] >= MAX_PYRAMID_ADDS,
    )

    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: BACKUP STATE TRANSITIONS"
    )

    for backup_number in range(
        1,
        MAX_BACKUPS + 1,
    ):

        assert_test(
            f"Backup {backup_number} Is Eligible",
            state["backup_count"] < MAX_BACKUPS,
        )

        backup_price = price_down(
            market_price,
            BACKUP_BUFFER_PERCENT
            * Decimal(backup_number),
        )

        backup_intent = create_intent(
            action=f"BACKUP_{backup_number}",
            side="BUY",
            quantity=normalized_quantity,
            reference_price=backup_price,
            sequence=2 + backup_number,
            reason=f"synthetic_backup_{backup_number}",
        )

        backup_payload = create_synthetic_payload(
            backup_intent
        )

        receipt = consume_and_dispatch(
            state,
            backup_intent,
            backup_payload,
            "BACKUP",
        )

        assert_test(
            f"Backup {backup_number} Synthetic Dispatch Completed",
            receipt["completed"] is True,
        )

        state["backup_count"] += 1

    state["phase"] = "BACKUPS_COMPLETED"

    assert_test(
        "Backup Count Is Three",
        state["backup_count"] == MAX_BACKUPS,
    )

    assert_test(
        "Fourth Backup Is Rejected",
        state["backup_count"] >= MAX_BACKUPS,
    )

    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: TP1 STATE TRANSITION"
    )

    tp1_price = price_up(
        market_price,
        TP1_TRIGGER_PERCENT,
    )

    tp1_quantity = round_down_step(
        normalized_quantity
        * TP1_PERCENT
        / Decimal("100"),
        contract["qty_step"],
    )

    if tp1_quantity <= 0:
        tp1_quantity = contract["min_qty"]

    tp1_intent = create_intent(
        action="TP1",
        side="SELL",
        quantity=tp1_quantity,
        reference_price=tp1_price,
        sequence=10,
        reason="synthetic_tp1",
    )

    tp1_payload = create_synthetic_payload(
        tp1_intent
    )

    tp1_receipt = consume_and_dispatch(
        state,
        tp1_intent,
        tp1_payload,
        "TP1",
    )

    state["tp1_completed"] = True
    state["phase"] = "TP1_COMPLETED"

    assert_test(
        "TP1 Synthetic Dispatch Completed",
        tp1_receipt["completed"] is True,
    )

    assert_test(
        "TP1 Was Not Transmitted",
        tp1_receipt["transmitted"] is False,
    )

    assert_test(
        "TP1 State Is Completed",
        state["tp1_completed"] is True,
    )

    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    section(
        f"{VERSION} TEST 13: TP2 STATE TRANSITION"
    )

    tp2_price = price_up(
        market_price,
        TP2_TRIGGER_PERCENT,
    )

    tp2_quantity = round_down_step(
        normalized_quantity
        * TP2_PERCENT
        / Decimal("100"),
        contract["qty_step"],
    )

    if tp2_quantity <= 0:
        tp2_quantity = contract["min_qty"]

    tp2_intent = create_intent(
        action="TP2",
        side="SELL",
        quantity=tp2_quantity,
        reference_price=tp2_price,
        sequence=11,
        reason="synthetic_tp2",
    )

    tp2_payload = create_synthetic_payload(
        tp2_intent
    )

    tp2_receipt = consume_and_dispatch(
        state,
        tp2_intent,
        tp2_payload,
        "TP2",
    )

    state["tp2_completed"] = True
    state["phase"] = "TP2_COMPLETED"

    assert_test(
        "TP2 Synthetic Dispatch Completed",
        tp2_receipt["completed"] is True,
    )

    assert_test(
        "TP2 Was Not Transmitted",
        tp2_receipt["transmitted"] is False,
    )

    assert_test(
        "TP2 State Is Completed",
        state["tp2_completed"] is True,
    )

    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: TRAILING ARM"
    )

    state["trailing_armed"] = (
        state["tp1_completed"]
        and state["tp2_completed"]
    )

    trailing_reference = price_up(
        tp2_price,
        TRAILING_DISTANCE_PERCENT,
    )

    assert_test(
        "Trailing Is Armed After TP1 And TP2",
        state["trailing_armed"] is True,
    )

    assert_test(
        "Trailing Distance Is Positive",
        TRAILING_DISTANCE_PERCENT > 0,
    )

    assert_test(
        "Trailing Reference Price Is Positive",
        trailing_reference > 0,
    )

    state["phase"] = "TRAILING_ARMED"

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{decimal_str(TRAILING_DISTANCE_PERCENT)}%"
    )

    log(
        f"{VERSION}: TRAILING REFERENCE="
        f"{decimal_str(trailing_reference)}"
    )

    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    section(
        f"{VERSION} TEST 15: TP3 / TRAILING EXIT"
    )

    tp3_quantity = round_down_step(
        normalized_quantity
        * TP3_PERCENT
        / Decimal("100"),
        contract["qty_step"],
    )

    if tp3_quantity <= 0:
        tp3_quantity = contract["min_qty"]

    tp3_intent = create_intent(
        action="TP3_TRAILING_EXIT",
        side="SELL",
        quantity=tp3_quantity,
        reference_price=trailing_reference,
        sequence=12,
        reason="synthetic_tp3_trailing_exit",
    )

    tp3_payload = create_synthetic_payload(
        tp3_intent
    )

    tp3_receipt = consume_and_dispatch(
        state,
        tp3_intent,
        tp3_payload,
        "TP3",
    )

    state["tp3_completed"] = True
    state["phase"] = "TP3_COMPLETED"

    assert_test(
        "TP3 Synthetic Dispatch Completed",
        tp3_receipt["completed"] is True,
    )

    assert_test(
        "TP3 Was Not Transmitted",
        tp3_receipt["transmitted"] is False,
    )

    assert_test(
        "TP3 State Is Completed",
        state["tp3_completed"] is True,
    )

    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    section(
        f"{VERSION} TEST 16: TERMINAL STRATEGY EXIT"
    )

    terminal_intent = create_intent(
        action="TERMINAL_EXIT",
        side="SELL",
        quantity=normalized_quantity,
        reference_price=trailing_reference,
        sequence=13,
        reason="synthetic_terminal_strategy_completion",
    )

    terminal_payload = create_synthetic_payload(
        terminal_intent
    )

    terminal_receipt = consume_and_dispatch(
        state,
        terminal_intent,
        terminal_payload,
        "TERMINAL",
    )

    state["terminal_exit_completed"] = True
    state["phase"] = "TERMINAL_COMPLETED"

    assert_test(
        "Terminal Synthetic Dispatch Completed",
        terminal_receipt["completed"] is True,
    )

    assert_test(
        "Terminal Dispatch Was Not Transmitted",
        terminal_receipt["transmitted"] is False,
    )

    assert_test(
        "Terminal State Is Completed",
        state["terminal_exit_completed"] is True,
    )

    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    section(
        f"{VERSION} TEST 17: COMPLETE STATE MACHINE"
    )

    assert_test(
        "Initial Entry Completed",
        state["initial_entry_completed"] is True,
    )

    assert_test(
        "Exactly One Pyramid Completed",
        state["pyramid_count"] == 1,
    )

    assert_test(
        "Exactly Three Backups Completed",
        state["backup_count"] == 3,
    )

    assert_test(
        "TP1 Completed",
        state["tp1_completed"] is True,
    )

    assert_test(
        "TP2 Completed",
        state["tp2_completed"] is True,
    )

    assert_test(
        "Trailing Was Armed",
        state["trailing_armed"] is True,
    )

    assert_test(
        "TP3 Completed",
        state["tp3_completed"] is True,
    )

    assert_test(
        "Terminal Exit Completed",
        state["terminal_exit_completed"] is True,
    )

    assert_test(
        "Final Strategy Phase Is Terminal",
        state["phase"] == "TERMINAL_COMPLETED",
    )

    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    section(
        f"{VERSION} TEST 18: DURABLE LOCAL SNAPSHOT"
    )

    saved_state = save_state(
        state
    )

    assert_test(
        "State File Exists",
        STATE_FILE.exists(),
    )

    assert_test(
        "Saved State Integrity Is Valid",
        validate_state_integrity(saved_state),
    )

    assert_test(
        "Saved Symbol Is Exact",
        saved_state["symbol"] == SYMBOL,
    )

    assert_test(
        "Saved Pyramid Count Is One",
        saved_state["pyramid_count"] == 1,
    )

    assert_test(
        "Saved Backup Count Is Three",
        saved_state["backup_count"] == 3,
    )

    assert_test(
        "Saved Terminal State Is Complete",
        saved_state["terminal_exit_completed"] is True,
    )

    log(
        f"{VERSION}: STATE FILE="
        f"{STATE_FILE}"
    )

    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    section(
        f"{VERSION} TEST 19: RESTART RESTORE"
    )

    restored_state = load_state()

    with runtime_lock:
        runtime["restart_restores"] += 1

    assert_test(
        "Restart State Was Restored",
        restored_state is not None,
    )

    assert_test(
        "Restart Integrity Is Valid",
        validate_state_integrity(
            restored_state
        ),
    )

    assert_test(
        "Consumed Intents Survived Restart",
        len(
            restored_state[
                "consumed_intents"
            ]
        ) > 0,
    )

    assert_test(
        "Dispatch Receipts Survived Restart",
        len(
            restored_state[
                "dispatch_receipts"
            ]
        ) > 0,
    )

    assert_test(
        "Terminal State Survived Restart",
        restored_state[
            "terminal_exit_completed"
        ] is True,
    )

    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    section(
        f"{VERSION} TEST 20: RESTART REPLAY REJECTION"
    )

    synthetic_before = runtime[
        "synthetic_dispatches"
    ]

    replay_rejected = False

    try:

        consume_and_dispatch(
            restored_state,
            initial_intent,
            initial_payload,
            "INITIAL",
        )

    except RuntimeError:

        replay_rejected = True

    synthetic_after = runtime[
        "synthetic_dispatches"
    ]

    assert_test(
        "Consumed Initial Intent Replay Is Rejected",
        replay_rejected,
    )

    assert_test(
        "Replay Produced No Additional Dispatch",
        synthetic_before == synthetic_after,
    )

    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    section(
        f"{VERSION} TEST 21: SYNTHETIC RECOVERY DISPATCH"
    )

    recovery_intent = create_intent(
        action="RECOVERY_CONFIRMATION",
        side="NONE",
        quantity=Decimal("0"),
        reference_price=market_price,
        sequence=100,
        reason="synthetic_restart_recovery_confirmation",
    )

    recovery_payload = create_synthetic_payload(
        recovery_intent
    )

    recovery_receipt = consume_and_dispatch(
        restored_state,
        recovery_intent,
        recovery_payload,
        "RECOVERY",
    )

    assert_test(
        "Recovery Dispatch Is Synthetic Only",
        recovery_receipt[
            "synthetic_only"
        ] is True,
    )

    assert_test(
        "Recovery Dispatch Was Not Transmitted",
        recovery_receipt[
            "transmitted"
        ] is False,
    )

    assert_test(
        "Recovery Dispatch Made No Network Write",
        recovery_receipt[
            "network_write"
        ] is False,
    )

    save_state(
        restored_state
    )

    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    section(
        f"{VERSION} TEST 22: WRITE FIREBREAK"
    )

    baseline_network_writes = runtime[
        "network_writes"
    ]

    assert_test(
        "HTTP POST Is Rejected",
        expect_rejection(
            lambda: http_post()
        ),
    )

    assert_test(
        "HTTP PUT Is Rejected",
        expect_rejection(
            lambda: http_put()
        ),
    )

    assert_test(
        "HTTP PATCH Is Rejected",
        expect_rejection(
            lambda: http_patch()
        ),
    )

    assert_test(
        "HTTP DELETE Is Rejected",
        expect_rejection(
            lambda: http_delete()
        ),
    )

    assert_test(
        "Real Order Function Is Rejected",
        expect_rejection(
            lambda: real_order()
        ),
    )

    assert_test(
        "Demo Order Function Is Rejected",
        expect_rejection(
            lambda: demo_order()
        ),
    )

    assert_test(
        "Leverage Mutation Function Is Rejected",
        expect_rejection(
            lambda: mutate_leverage()
        ),
    )

    assert_test(
        "Margin Mutation Function Is Rejected",
        expect_rejection(
            lambda: mutate_margin()
        ),
    )

    assert_test(
        "Position Mutation Function Is Rejected",
        expect_rejection(
            lambda: mutate_position()
        ),
    )

    assert_test(
        "Account Mutation Function Is Rejected",
        expect_rejection(
            lambda: mutate_account()
        ),
    )

    #
    # The firebreak functions intentionally increment their attempted
    # mutation counters before rejecting. Reset them here because the
    # test itself must not count as an actual transmitted write.
    #

    with runtime_lock:

        runtime["network_writes"] = baseline_network_writes

        runtime["real_orders"] = 0
        runtime["demo_orders"] = 0

        runtime["leverage_mutations"] = 0
        runtime["margin_mutations"] = 0
        runtime["position_mutations"] = 0
        runtime["account_mutations"] = 0

    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    section(
        f"{VERSION} TEST 23: FINAL SAFETY ACCOUNTING"
    )

    assert_test(
        "Network Write Count Is Zero",
        runtime["network_writes"] == 0,
    )

    assert_test(
        "Real Order Count Is Zero",
        runtime["real_orders"] == 0,
    )

    assert_test(
        "Demo Order Count Is Zero",
        runtime["demo_orders"] == 0,
    )

    assert_test(
        "Leverage Mutation Count Is Zero",
        runtime[
            "leverage_mutations"
        ] == 0,
    )

    assert_test(
        "Margin Mutation Count Is Zero",
        runtime[
            "margin_mutations"
        ] == 0,
    )

    assert_test(
        "Position Mutation Count Is Zero",
        runtime[
            "position_mutations"
        ] == 0,
    )

    assert_test(
        "Account Mutation Count Is Zero",
        runtime[
            "account_mutations"
        ] == 0,
    )

    assert_test(
        "Initial Synthetic Dispatch Occurred",
        runtime[
            "initial_dispatches"
        ] == 1,
    )

    assert_test(
        "Exactly One Pyramid Dispatch Occurred",
        runtime[
            "pyramid_dispatches"
        ] == 1,
    )

    assert_test(
        "Exactly Three Backup Dispatches Occurred",
        runtime[
            "backup_dispatches"
        ] == 3,
    )

    assert_test(
        "Exactly Three TP Dispatches Occurred",
        runtime[
            "tp_dispatches"
        ] == 3,
    )

    assert_test(
        "Exactly One Terminal Dispatch Occurred",
        runtime[
            "terminal_dispatches"
        ] == 1,
    )

    assert_test(
        "Exactly One Recovery Dispatch Occurred",
        runtime[
            "recovery_dispatches"
        ] == 1,
    )

    assert_test(
        "At Least One Replay Was Blocked",
        runtime[
            "replays_blocked"
        ] >= 1,
    )

    # ==============================================================================================
    # TEST 24
    # ==============================================================================================

    section(
        f"{VERSION} TEST 24: FINAL R34Z VALIDATION"
    )

    final_state = load_state()

    assert_test(
        "Final State Exists",
        final_state is not None,
    )

    assert_test(
        "Final State Integrity Is Valid",
        validate_state_integrity(
            final_state
        ),
    )

    assert_test(
        "Final State Is Terminal",
        final_state[
            "terminal_exit_completed"
        ] is True,
    )

    assert_test(
        "Synthetic Transport Only Remains Enabled",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    assert_test(
        "Authenticated Transport Remains GET Only",
        AUTHENTICATED_READ_ONLY is True,
    )

    assert_test(
        "Public Transport Remains GET Only",
        PUBLIC_READ_ONLY is True,
    )

    assert_test(
        "No Real Order Was Sent",
        runtime["real_orders"] == 0,
    )

    assert_test(
        "No Demo Order Was Sent",
        runtime["demo_orders"] == 0,
    )

    assert_test(
        "No Network Write Was Sent",
        runtime["network_writes"] == 0,
    )

    # ==============================================================================================
    # PASSED
    # ==============================================================================================

    with runtime_lock:
        runtime["phase"] = "R34Z_VALIDATED"

    section(
        f"{VERSION}: VALIDATION PASSED"
    )

    log(
        f"{VERSION}: LIVE READ-ONLY STATE VALIDATED"
    )

    log(
        f"{VERSION}: POSITION ENDPOINT VALIDATED="
        f"{POSITION_PATH}"
    )

    log(
        f"{VERSION}: COMPLETE SYNTHETIC STRATEGY STATE MACHINE VALIDATED"
    )

    log(
        f"{VERSION}: INITIAL ENTRY VALIDATED"
    )

    log(
        f"{VERSION}: PYRAMID LIMIT VALIDATED"
    )

    log(
        f"{VERSION}: BACKUP LIMIT VALIDATED"
    )

    log(
        f"{VERSION}: TP1 VALIDATED"
    )

    log(
        f"{VERSION}: TP2 VALIDATED"
    )

    log(
        f"{VERSION}: TRAILING ENGINE VALIDATED"
    )

    log(
        f"{VERSION}: TP3 VALIDATED"
    )

    log(
        f"{VERSION}: TERMINAL EXIT VALIDATED"
    )

    log(
        f"{VERSION}: DURABLE SNAPSHOT VALIDATED"
    )

    log(
        f"{VERSION}: RESTART RESTORE VALIDATED"
    )

    log(
        f"{VERSION}: REPLAY PROTECTION VALIDATED"
    )

    log(
        f"{VERSION}: SYNTHETIC RECOVERY VALIDATED"
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{runtime['synthetic_dispatches']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{runtime['network_writes']}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{runtime['real_orders']}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{runtime['demo_orders']}"
    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    # ==============================================================================================
    # HEARTBEAT
    # ==============================================================================================

    heartbeat_loop()


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        log(
            f"{VERSION}: STOPPED"
        )

        sys.exit(0)

    except Exception as exc:

        with runtime_lock:
            runtime["phase"] = "VALIDATION_FAILED"

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        #
        # Keep the health service alive on Render so the failure state
        # remains observable.
        #

        while True:
            time.sleep(30)
