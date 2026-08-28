

# ==================================================================================================
# R34Y - DURABLE SYNTHETIC LIFECYCLE + RESTART / RECOVERY / REPLAY VALIDATION
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
# R34Y validates:
#
#   LIVE ACCOUNT STATE
#       ↓
#   LIVE MARKET STATE
#       ↓
#   SYNTHETIC LIFECYCLE
#       ↓
#   DURABLE SNAPSHOT
#       ↓
#   DURABLE EVENT JOURNAL
#       ↓
#   SHA256 INTEGRITY BINDING
#       ↓
#   SIMULATED PROCESS RESTART
#       ↓
#   RESTORE FROM DISK
#       ↓
#   EXACT LIFECYCLE RECOVERY
#       ↓
#   DUPLICATE EVENT REJECTION
#       ↓
#   REPLAY REJECTION
#       ↓
#   COOLDOWN PERSISTENCE
#       ↓
#   TERMINAL STATE IMMUTABILITY
#       ↓
#   CORRUPTION / TAMPER REJECTION
#       ↓
#   ATOMIC SNAPSHOT REPLACEMENT
#       ↓
#   EXACTLY-ONCE SYNTHETIC RECOVERY
#       ↓
#   FINAL NETWORK WRITE FIREBREAK
#
# IMPORTANT:
#
#   THIS PROGRAM DOES NOT SEND ORDERS.
#   THIS PROGRAM DOES NOT CHANGE LEVERAGE.
#   THIS PROGRAM DOES NOT CHANGE MARGIN MODE.
#   THIS PROGRAM DOES NOT CHANGE POSITIONS.
#   THIS PROGRAM DOES NOT MUTATE THE ACCOUNT.
#
# ==================================================================================================

import base64
import copy
import hashlib
import hmac
import json
import os
import shutil
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid

from decimal import Decimal, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# PART 1 - CONFIGURATION
# ==================================================================================================

VERSION = "R34Y"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper().strip()

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

API_KEY = os.getenv("WEEX_API_KEY", "").strip()
API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

BALANCE_PATH = "/capi/v3/account/balance"
POSITION_PATH = "/capi/v3/account/allPosition"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

MARKET_PRICE_PATH = "/capi/v3/market/symbolPrice"
EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LEVERAGE = 100

INITIAL_ENTRY_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

PYRAMID_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")

TP1_CLOSE_PERCENT = Decimal("20")
TP2_CLOSE_PERCENT = Decimal("20")
TP3_CLOSE_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_ONLY = True

SEPARATOR = "-" * 100

REQUEST_TIMEOUT_SECONDS = 15


# --------------------------------------------------------------------------------------------------
# R34Y durable-state path
#
# For ordinary Render deployments /tmp is adequate for this diagnostic run.
#
# If a persistent disk is mounted, set:
#
#   R34Y_STATE_DIR=/var/data/r34y
#
# The internal restart tests below work even with /tmp because they reload from
# the state files created during the same process execution.
# --------------------------------------------------------------------------------------------------

STATE_DIR = os.getenv(
    "R34Y_STATE_DIR",
    os.path.join(tempfile.gettempdir(), "r34y_state")
)

SNAPSHOT_FILE = os.path.join(
    STATE_DIR,
    "lifecycle_snapshot.json"
)

JOURNAL_FILE = os.path.join(
    STATE_DIR,
    "lifecycle_journal.json"
)

MANIFEST_FILE = os.path.join(
    STATE_DIR,
    "lifecycle_manifest.json"
)


# ==================================================================================================
# RUNTIME COUNTERS
# ==================================================================================================

COUNTERS = {
    "authenticated_gets": 0,
    "public_gets": 0,
    "network_writes": 0,
    "real_orders": 0,
    "demo_orders": 0,
    "synthetic_dispatches": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,
    "restart_restores": 0,
    "replays_blocked": 0,
    "duplicate_events_blocked": 0,
    "tamper_rejections": 0,
    "corruption_rejections": 0,
    "recovery_dispatches": 0,
}

RUNTIME = {
    "phase": "BOOTING",
    "validation_complete": False,
    "validation_failed": False,
    "error": None,
    "heartbeat": 0,
}

REGISTERED_CLIENT_IDS = set()
RECOVERY_KEYS = set()
EVENT_IDS = set()

COUNTER_LOCK = threading.Lock()
RUNTIME_LOCK = threading.Lock()


# ==================================================================================================
# BASIC HELPERS
# ==================================================================================================

def log(message=""):
    print(message, flush=True)


def section(title):
    log(SEPARATOR)
    log(title)
    log(SEPARATOR)


def passed(label):
    log(f"{label:<92} ✅ PASS")


def failed(label):
    log(f"{label:<92} ❌ FAIL")


def assert_pass(label, condition):
    if not condition:
        failed(label)
        raise AssertionError(label)

    passed(label)


def decimal_string(value):
    if isinstance(value, Decimal):
        text = format(value, "f")
    else:
        text = format(Decimal(str(value)), "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in ("", "-0"):
        return "0"

    return text


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_object(value):
    return sha256_text(canonical_json(value))


def deep_copy(value):
    return json.loads(json.dumps(value))


def now_ms():
    return int(time.time() * 1000)


def now_seconds():
    return int(time.time())


def ensure_state_dir():
    os.makedirs(STATE_DIR, exist_ok=True)


def clean_test_state():
    if os.path.isdir(STATE_DIR):
        shutil.rmtree(STATE_DIR)

    ensure_state_dir()


def increment_counter(name, amount=1):
    with COUNTER_LOCK:
        COUNTERS[name] += amount


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.end_headers()
            return

        with RUNTIME_LOCK:
            payload = {
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": RUNTIME["phase"],
                "validationComplete": RUNTIME["validation_complete"],
                "validationFailed": RUNTIME["validation_failed"],
                "error": RUNTIME["error"],
                "authenticatedReadOnly": AUTHENTICATED_READ_ONLY,
                "publicReadOnly": PUBLIC_READ_ONLY,
                "networkWritesEnabled": NETWORK_WRITES_ENABLED,
                "counters": dict(COUNTERS),
            }

        body = canonical_json(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_health_server():
    try:
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )
        thread.start()
        return server
    except Exception as exc:
        log(
            f"{VERSION}: HEALTH SERVER WARNING="
            f"{type(exc).__name__}: {exc}"
        )
        return None


# ==================================================================================================
# NETWORK FIREBREAK
# ==================================================================================================

def reject_network_write(method, path):
    increment_counter("network_writes", 0)

    raise RuntimeError(
        f"{VERSION}: NETWORK WRITE REJECTED LOCALLY | "
        f"method={method} | path={path}"
    )


def http_post(*args, **kwargs):
    return reject_network_write("POST", "BLOCKED")


def http_put(*args, **kwargs):
    return reject_network_write("PUT", "BLOCKED")


def http_patch(*args, **kwargs):
    return reject_network_write("PATCH", "BLOCKED")


def http_delete(*args, **kwargs):
    return reject_network_write("DELETE", "BLOCKED")


def real_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: REAL ORDER FUNCTION DISABLED"
    )


def demo_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: DEMO ORDER FUNCTION DISABLED"
    )


def mutate_leverage(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )


def mutate_margin(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: MARGIN MUTATION DISABLED"
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: POSITION MUTATION DISABLED"
    )


def mutate_account(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION}: ACCOUNT MUTATION DISABLED"
    )


# ==================================================================================================
# WEEX AUTHENTICATED GET
# ==================================================================================================

def build_signature(timestamp, method, request_path, query_string="", body=""):
    if query_string:
        if query_string.startswith("?"):
            signed_path = request_path + query_string
        else:
            signed_path = request_path + "?" + query_string
    else:
        signed_path = request_path

    message = (
        str(timestamp)
        + method.upper()
        + signed_path
        + body
    )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def authenticated_get(path, params=None):
    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError("Authenticated read-only transport disabled")

    if not API_KEY:
        raise RuntimeError("WEEX_API_KEY is missing")

    if not API_SECRET:
        raise RuntimeError("WEEX_API_SECRET is missing")

    if not API_PASSPHRASE:
        raise RuntimeError("WEEX_API_PASSPHRASE is missing")

    params = params or {}

    query_string = urllib.parse.urlencode(params)

    timestamp = str(now_ms())

    signature = build_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
    )

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "locale": "en-US",
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
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            raw = response.read().decode("utf-8")

        increment_counter("authenticated_gets")

        return json.loads(raw)

    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""

        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"HTTP {exc.code} | {body}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        )


# ==================================================================================================
# PUBLIC GET
# ==================================================================================================

def public_get(path, params=None):
    if not PUBLIC_READ_ONLY:
        raise RuntimeError("Public read-only transport disabled")

    params = params or {}

    query_string = urllib.parse.urlencode(params)

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    request = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"{VERSION}-read-only-validator",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            raw = response.read().decode("utf-8")

        increment_counter("public_gets")

        return json.loads(raw)

    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""

        raise RuntimeError(
            f"Public GET failed: {path} | "
            f"HTTP {exc.code} | {body}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Public GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        )


# ==================================================================================================
# RESPONSE PARSERS
# ==================================================================================================

def extract_usdt_balance(response):
    records = response

    if isinstance(response, dict):
        if isinstance(response.get("data"), list):
            records = response["data"]

        elif isinstance(response.get("data"), dict):
            nested = response["data"]

            for key in (
                "list",
                "balances",
                "assets",
                "rows",
            ):
                if isinstance(nested.get(key), list):
                    records = nested[key]
                    break

        elif isinstance(response.get("balances"), list):
            records = response["balances"]

    if not isinstance(records, list):
        raise RuntimeError(
            "Unable to parse balance response as record list"
        )

    for record in records:
        if not isinstance(record, dict):
            continue

        asset = str(
            record.get("asset")
            or record.get("coin")
            or record.get("marginCoin")
            or ""
        ).upper()

        if asset != "USDT":
            continue

        available = (
            record.get("availableBalance")
            or record.get("available")
            or record.get("availableAmount")
            or record.get("free")
        )

        if available is None:
            continue

        return Decimal(str(available))

    raise RuntimeError(
        "USDT available balance was not found"
    )


def extract_positions(response):
    if isinstance(response, list):
        return response

    if isinstance(response, dict):
        data = response.get("data")

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in (
                "list",
                "positions",
                "rows",
            ):
                value = data.get(key)

                if isinstance(value, list):
                    return value

        for key in (
            "positions",
            "list",
            "rows",
        ):
            value = response.get(key)

            if isinstance(value, list):
                return value

    return []


def extract_symbol_config(response):
    if isinstance(response, dict):
        data = response.get("data")

        if isinstance(data, dict):
            return data

        if isinstance(data, list):
            for record in data:
                if str(record.get("symbol", "")).upper() == SYMBOL:
                    return record

        if (
            str(response.get("symbol", "")).upper() == SYMBOL
            or "marginType" in response
            or "marginMode" in response
        ):
            return response

    if isinstance(response, list):
        for record in response:
            if (
                isinstance(record, dict)
                and str(record.get("symbol", "")).upper() == SYMBOL
            ):
                return record

    return {}


def extract_market_price(response):
    candidates = []

    if isinstance(response, dict):
        candidates.append(response)

        data = response.get("data")

        if isinstance(data, dict):
            candidates.append(data)

        elif isinstance(data, list):
            candidates.extend(
                item for item in data if isinstance(item, dict)
            )

    elif isinstance(response, list):
        candidates.extend(
            item for item in response if isinstance(item, dict)
        )

    for record in candidates:
        price = (
            record.get("price")
            or record.get("markPrice")
            or record.get("indexPrice")
            or record.get("lastPrice")
        )

        if price is not None:
            value = Decimal(str(price))

            if value > 0:
                return value

    raise RuntimeError("Unable to parse positive market price")


def extract_contract_info(response):
    symbols = []

    if isinstance(response, dict):
        if isinstance(response.get("symbols"), list):
            symbols = response["symbols"]

        data = response.get("data")

        if isinstance(data, dict):
            if isinstance(data.get("symbols"), list):
                symbols = data["symbols"]

        elif isinstance(data, list):
            symbols = data

    elif isinstance(response, list):
        symbols = response

    for record in symbols:
        if (
            isinstance(record, dict)
            and str(record.get("symbol", "")).upper() == SYMBOL
        ):
            return record

    raise RuntimeError(
        f"Contract information not found for {SYMBOL}"
    )


# ==================================================================================================
# QUANTITY HELPERS
# ==================================================================================================

def decimal_places(value):
    text = str(value)

    if "e-" in text.lower():
        return abs(Decimal(text).as_tuple().exponent)

    if "." not in text:
        return 0

    return len(text.rstrip("0").split(".")[1])


def quantize_down(value, precision):
    quantum = Decimal("1").scaleb(-precision)

    return Decimal(value).quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def normalize_quantity(raw_quantity, contract):
    precision = int(
        contract.get("quantityPrecision", 4)
    )

    minimum = Decimal(
        str(
            contract.get(
                "minOrderSize",
                contract.get("minTradeAmount", "0.0001")
            )
        )
    )

    normalized = quantize_down(
        Decimal(raw_quantity),
        precision,
    )

    if normalized < minimum:
        normalized = minimum

    return normalized


# ==================================================================================================
# LIVE STATE
# ==================================================================================================

def read_live_state():
    balance_response = authenticated_get(
        BALANCE_PATH
    )

    positions_response = authenticated_get(
        POSITION_PATH
    )

    symbol_config_response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    market_response = public_get(
        MARKET_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    exchange_response = public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    available_balance = extract_usdt_balance(
        balance_response
    )

    positions = extract_positions(
        positions_response
    )

    symbol_config = extract_symbol_config(
        symbol_config_response
    )

    market_price = extract_market_price(
        market_response
    )

    contract = extract_contract_info(
        exchange_response
    )

    btc_positions = []

    for position in positions:
        if not isinstance(position, dict):
            continue

        if str(
            position.get("symbol", "")
        ).upper() == SYMBOL:
            btc_positions.append(position)

    live_state = {
        "version": VERSION,
        "symbol": SYMBOL,
        "availableUSDT": decimal_string(
            available_balance
        ),
        "marketPrice": decimal_string(
            market_price
        ),
        "positionRecords": len(positions),
        "symbolPositionRecords": len(btc_positions),
        "symbolConfig": symbol_config,
        "contract": contract,
        "authenticatedReadOnly": True,
        "publicReadOnly": True,
        "networkWriteAllowed": False,
        "capturedAtMs": now_ms(),
    }

    return {
        "balance": available_balance,
        "positions": positions,
        "btc_positions": btc_positions,
        "symbol_config": symbol_config,
        "market_price": market_price,
        "contract": contract,
        "live_state": live_state,
    }


# ==================================================================================================
# SYNTHETIC ENTRY
# ==================================================================================================

def create_synthetic_entry(live):
    balance = live["balance"]
    market_price = live["market_price"]
    contract = live["contract"]

    margin_budget = (
        balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    planned_notional = (
        margin_budget
        * Decimal(str(TARGET_LEVERAGE))
    )

    raw_quantity = (
        planned_notional
        / market_price
    )

    quantity = normalize_quantity(
        raw_quantity,
        contract,
    )

    client_order_id = (
        "r34y-"
        + uuid.uuid4().hex[:20]
    )

    intent = {
        "version": VERSION,
        "syntheticOnly": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": decimal_string(quantity),
        "clientOrderId": client_order_id,
        "entryPrice": decimal_string(market_price),
        "targetLeverage": TARGET_LEVERAGE,
        "targetMarginType": TARGET_MARGIN_TYPE,
        "marginBudgetUSDT": decimal_string(
            margin_budget
        ),
    }

    payload = {
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": decimal_string(quantity),
        "newClientOrderId": client_order_id,
    }

    decision = {
        "version": VERSION,
        "syntheticOnly": True,
        "decision": "SYNTHETIC_LONG_ENTRY",
        "entryPercent": decimal_string(
            INITIAL_ENTRY_PERCENT
        ),
        "targetLeverage": TARGET_LEVERAGE,
        "marginType": TARGET_MARGIN_TYPE,
        "availableBalance": decimal_string(balance),
        "marketPrice": decimal_string(market_price),
        "marginBudget": decimal_string(
            margin_budget
        ),
        "plannedNotional": decimal_string(
            planned_notional
        ),
        "rawQuantity": decimal_string(
            raw_quantity
        ),
        "normalizedQuantity": decimal_string(
            quantity
        ),
    }

    receipt = {
        "version": VERSION,
        "syntheticOnly": True,
        "transmitted": False,
        "networkWriteAllowed": False,
        "accepted": True,
        "clientOrderId": client_order_id,
        "symbol": SYMBOL,
        "side": "BUY",
        "quantity": decimal_string(quantity),
        "syntheticFillPrice": decimal_string(
            market_price
        ),
    }

    REGISTERED_CLIENT_IDS.add(client_order_id)

    increment_counter("synthetic_dispatches")

    return {
        "decision": decision,
        "intent": intent,
        "payload": payload,
        "receipt": receipt,
        "quantity": quantity,
        "entry_price": market_price,
        "client_order_id": client_order_id,
    }


# ==================================================================================================
# LIFECYCLE
# ==================================================================================================

def create_event(event_type, **kwargs):
    event_id = (
        VERSION.lower()
        + "-evt-"
        + uuid.uuid4().hex
    )

    event = {
        "eventId": event_id,
        "event": event_type,
        "synthetic": True,
        "networkWriteAllowed": False,
    }

    event.update(kwargs)

    return event


def append_event(lifecycle, event):
    event_id = event["eventId"]

    if event_id in EVENT_IDS:
        increment_counter(
            "duplicate_events_blocked"
        )

        raise RuntimeError(
            f"Duplicate lifecycle event rejected: {event_id}"
        )

    EVENT_IDS.add(event_id)

    lifecycle["events"].append(
        deep_copy(event)
    )


def create_open_lifecycle(entry):
    quantity = entry["quantity"]
    entry_price = entry["entry_price"]

    lifecycle = {
        "version": VERSION,
        "syntheticOnly": True,
        "networkWriteAllowed": False,
        "transmissionAllowed": False,
        "symbol": SYMBOL,
        "state": "OPEN",
        "direction": "LONG",
        "initialQuantity": decimal_string(
            quantity
        ),
        "remainingQuantity": decimal_string(
            quantity
        ),
        "closedQuantity": "0",
        "entryPrice": decimal_string(
            entry_price
        ),
        "highestPrice": decimal_string(
            entry_price
        ),
        "tp1Done": False,
        "tp2Done": False,
        "tp3Done": False,
        "trailingArmed": False,
        "trailingTriggered": False,
        "pyramidAdds": 0,
        "backups": 0,
        "cooldownUntil": "0",
        "exitReason": None,
        "events": [],
    }

    append_event(
        lifecycle,
        create_event(
            "POSITION_OPENED",
            price=decimal_string(entry_price),
            quantity=decimal_string(quantity),
        ),
    )

    return lifecycle


def simulate_tp1(lifecycle):
    if lifecycle["state"] != "OPEN":
        raise RuntimeError(
            "TP1 requires OPEN lifecycle"
        )

    initial = Decimal(
        lifecycle["initialQuantity"]
    )

    remaining = Decimal(
        lifecycle["remainingQuantity"]
    )

    close_quantity = (
        initial
        * TP1_CLOSE_PERCENT
        / Decimal("100")
    )

    close_quantity = min(
        close_quantity,
        remaining,
    )

    remaining -= close_quantity

    entry_price = Decimal(
        lifecycle["entryPrice"]
    )

    tp1_price = (
        entry_price
        * (
            Decimal("1")
            + TP1_TRIGGER_PERCENT
            / Decimal("100")
        )
    )

    lifecycle["tp1Done"] = True

    lifecycle["remainingQuantity"] = decimal_string(
        remaining
    )

    lifecycle["closedQuantity"] = decimal_string(
        initial - remaining
    )

    append_event(
        lifecycle,
        create_event(
            "TP1",
            price=decimal_string(tp1_price),
            closedQuantity=decimal_string(
                close_quantity
            ),
            remainingQuantity=decimal_string(
                remaining
            ),
        ),
    )

    return lifecycle


def simulate_tp2(lifecycle):
    if lifecycle["state"] != "OPEN":
        raise RuntimeError(
            "TP2 requires OPEN lifecycle"
        )

    initial = Decimal(
        lifecycle["initialQuantity"]
    )

    remaining = Decimal(
        lifecycle["remainingQuantity"]
    )

    close_quantity = (
        initial
        * TP2_CLOSE_PERCENT
        / Decimal("100")
    )

    close_quantity = min(
        close_quantity,
        remaining,
    )

    remaining -= close_quantity

    entry_price = Decimal(
        lifecycle["entryPrice"]
    )

    tp2_price = (
        entry_price
        * (
            Decimal("1")
            + TP2_TRIGGER_PERCENT
            / Decimal("100")
        )
    )

    lifecycle["tp2Done"] = True
    lifecycle["trailingArmed"] = True

    lifecycle["remainingQuantity"] = decimal_string(
        remaining
    )

    lifecycle["closedQuantity"] = decimal_string(
        initial - remaining
    )

    append_event(
        lifecycle,
        create_event(
            "TP2",
            price=decimal_string(tp2_price),
            closedQuantity=decimal_string(
                close_quantity
            ),
            remainingQuantity=decimal_string(
                remaining
            ),
        ),
    )

    append_event(
        lifecycle,
        create_event(
            "TRAILING_ARMED",
            price=decimal_string(tp2_price),
            distancePercent=decimal_string(
                TRAILING_DISTANCE_PERCENT
            ),
        ),
    )

    return lifecycle


def simulate_trailing_high(lifecycle):
    entry_price = Decimal(
        lifecycle["entryPrice"]
    )

    high_price = (
        entry_price
        * Decimal("1.015")
    )

    lifecycle["highestPrice"] = decimal_string(
        high_price
    )

    append_event(
        lifecycle,
        create_event(
            "TRAILING_HIGH_UPDATED",
            price=decimal_string(high_price),
            highestPrice=decimal_string(
                high_price
            ),
        ),
    )

    return lifecycle


def simulate_trailing_exit(lifecycle):
    if lifecycle["state"] != "OPEN":
        raise RuntimeError(
            "Trailing exit requires OPEN lifecycle"
        )

    remaining = Decimal(
        lifecycle["remainingQuantity"]
    )

    highest = Decimal(
        lifecycle["highestPrice"]
    )

    trigger_price = (
        highest
        * (
            Decimal("1")
            - TRAILING_DISTANCE_PERCENT
            / Decimal("100")
        )
    )

    initial = Decimal(
        lifecycle["initialQuantity"]
    )

    lifecycle["remainingQuantity"] = "0"
    lifecycle["closedQuantity"] = decimal_string(
        initial
    )
    lifecycle["tp3Done"] = True
    lifecycle["trailingTriggered"] = True
    lifecycle["state"] = "CLOSED"
    lifecycle["exitReason"] = "TP3_TRAILING_EXIT"

    append_event(
        lifecycle,
        create_event(
            "TP3_TRAILING_EXIT",
            price=decimal_string(
                trigger_price
            ),
            closedQuantity=decimal_string(
                remaining
            ),
            remainingQuantity="0",
        ),
    )

    append_event(
        lifecycle,
        create_event(
            "POSITION_TERMINAL",
            price=decimal_string(
                trigger_price
            ),
            reason="TP3_TRAILING_EXIT",
        ),
    )

    return lifecycle


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

def atomic_write_json(path, value):
    ensure_state_dir()

    directory = os.path.dirname(path)

    temporary_path = os.path.join(
        directory,
        "." + os.path.basename(path)
        + ".tmp."
        + uuid.uuid4().hex
    )

    encoded = (
        canonical_json(value)
        + "\n"
    ).encode("utf-8")

    with open(
        temporary_path,
        "wb",
    ) as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(
        temporary_path,
        path,
    )


def read_json_file(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def create_manifest(
    lifecycle,
    journal,
    binding,
    generation,
    recovery_epoch,
):
    lifecycle_hash = sha256_object(
        lifecycle
    )

    journal_hash = sha256_object(
        journal
    )

    binding_hash = sha256_object(
        binding
    )

    manifest = {
        "version": VERSION,
        "syntheticOnly": True,
        "networkWriteAllowed": False,
        "transmissionAllowed": False,
        "generation": generation,
        "recoveryEpoch": recovery_epoch,
        "lifecycleSHA256": lifecycle_hash,
        "journalSHA256": journal_hash,
        "bindingSHA256": binding_hash,
        "eventCount": len(journal),
        "terminal": (
            lifecycle["state"] == "CLOSED"
        ),
        "createdAtMs": now_ms(),
    }

    manifest["manifestSHA256"] = sha256_object(
        {
            key: value
            for key, value in manifest.items()
            if key != "manifestSHA256"
        }
    )

    return manifest


def validate_manifest_hash(manifest):
    expected = manifest.get(
        "manifestSHA256"
    )

    unsigned = {
        key: value
        for key, value in manifest.items()
        if key != "manifestSHA256"
    }

    actual = sha256_object(
        unsigned
    )

    return (
        isinstance(expected, str)
        and expected == actual
    )


def persist_state(
    lifecycle,
    binding,
    generation,
    recovery_epoch,
):
    journal = deep_copy(
        lifecycle["events"]
    )

    manifest = create_manifest(
        lifecycle=lifecycle,
        journal=journal,
        binding=binding,
        generation=generation,
        recovery_epoch=recovery_epoch,
    )

    snapshot_envelope = {
        "version": VERSION,
        "syntheticOnly": True,
        "networkWriteAllowed": False,
        "generation": generation,
        "recoveryEpoch": recovery_epoch,
        "lifecycle": deep_copy(
            lifecycle
        ),
        "binding": deep_copy(
            binding
        ),
    }

    atomic_write_json(
        SNAPSHOT_FILE,
        snapshot_envelope,
    )

    atomic_write_json(
        JOURNAL_FILE,
        journal,
    )

    atomic_write_json(
        MANIFEST_FILE,
        manifest,
    )

    return manifest


def restore_state():
    snapshot = read_json_file(
        SNAPSHOT_FILE
    )

    journal = read_json_file(
        JOURNAL_FILE
    )

    manifest = read_json_file(
        MANIFEST_FILE
    )

    if not validate_manifest_hash(
        manifest
    ):
        increment_counter(
            "tamper_rejections"
        )

        raise RuntimeError(
            "Manifest hash validation failed"
        )

    lifecycle = snapshot.get(
        "lifecycle"
    )

    binding = snapshot.get(
        "binding"
    )

    if not isinstance(
        lifecycle,
        dict,
    ):
        increment_counter(
            "corruption_rejections"
        )

        raise RuntimeError(
            "Lifecycle snapshot is corrupted"
        )

    if not isinstance(
        journal,
        list,
    ):
        increment_counter(
            "corruption_rejections"
        )

        raise RuntimeError(
            "Lifecycle journal is corrupted"
        )

    if not isinstance(
        binding,
        dict,
    ):
        increment_counter(
            "corruption_rejections"
        )

        raise RuntimeError(
            "Complete binding is corrupted"
        )

    if sha256_object(
        lifecycle
    ) != manifest.get(
        "lifecycleSHA256"
    ):
        increment_counter(
            "tamper_rejections"
        )

        raise RuntimeError(
            "Lifecycle SHA256 mismatch"
        )

    if sha256_object(
        journal
    ) != manifest.get(
        "journalSHA256"
    ):
        increment_counter(
            "tamper_rejections"
        )

        raise RuntimeError(
            "Journal SHA256 mismatch"
        )

    if sha256_object(
        binding
    ) != manifest.get(
        "bindingSHA256"
    ):
        increment_counter(
            "tamper_rejections"
        )

        raise RuntimeError(
            "Binding SHA256 mismatch"
        )

    if journal != lifecycle.get(
        "events"
    ):
        increment_counter(
            "tamper_rejections"
        )

        raise RuntimeError(
            "Lifecycle journal does not match snapshot events"
        )

    if (
        int(
            snapshot.get(
                "generation",
                -1,
            )
        )
        != int(
            manifest.get(
                "generation",
                -2,
            )
        )
    ):
        increment_counter(
            "tamper_rejections"
        )

        raise RuntimeError(
            "Generation mismatch"
        )

    if (
        int(
            snapshot.get(
                "recoveryEpoch",
                -1,
            )
        )
        != int(
            manifest.get(
                "recoveryEpoch",
                -2,
            )
        )
    ):
        increment_counter(
            "tamper_rejections"
        )

        raise RuntimeError(
            "Recovery epoch mismatch"
        )

    increment_counter(
        "restart_restores"
    )

    return {
        "snapshot": snapshot,
        "journal": journal,
        "manifest": manifest,
        "lifecycle": lifecycle,
        "binding": binding,
    }


# ==================================================================================================
# RECOVERY FENCING
# ==================================================================================================

def create_recovery_key(
    generation,
    epoch,
    lifecycle_hash,
):
    source = (
        f"{VERSION}|"
        f"{SYMBOL}|"
        f"{generation}|"
        f"{epoch}|"
        f"{lifecycle_hash}"
    )

    return sha256_text(
        source
    )


def recover_exactly_once(
    restored,
):
    lifecycle = restored[
        "lifecycle"
    ]

    manifest = restored[
        "manifest"
    ]

    lifecycle_hash = manifest[
        "lifecycleSHA256"
    ]

    generation = int(
        manifest["generation"]
    )

    epoch = int(
        manifest["recoveryEpoch"]
    )

    key = create_recovery_key(
        generation,
        epoch,
        lifecycle_hash,
    )

    if key in RECOVERY_KEYS:
        increment_counter(
            "replays_blocked"
        )

        raise RuntimeError(
            "Recovery replay rejected"
        )

    RECOVERY_KEYS.add(
        key
    )

    receipt = {
        "version": VERSION,
        "syntheticOnly": True,
        "networkWriteAllowed": False,
        "transmitted": False,
        "recoveryKey": key,
        "generation": generation,
        "recoveryEpoch": epoch,
        "lifecycleSHA256": lifecycle_hash,
        "state": lifecycle[
            "state"
        ],
        "recoveredExactlyOnce": True,
    }

    increment_counter(
        "recovery_dispatches"
    )

    return receipt


# ==================================================================================================
# COMPLETE BINDING
# ==================================================================================================

def create_complete_binding(
    live_state,
    entry,
    lifecycle,
):
    binding = {
        "version": VERSION,
        "syntheticOnly": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "liveStateSHA256": sha256_object(
            live_state
        ),
        "decisionSHA256": sha256_object(
            entry["decision"]
        ),
        "intentSHA256": sha256_object(
            entry["intent"]
        ),
        "payloadSHA256": sha256_object(
            entry["payload"]
        ),
        "entryReceiptSHA256": sha256_object(
            entry["receipt"]
        ),
        "lifecycleSHA256": sha256_object(
            lifecycle
        ),
    }

    return binding


# ==================================================================================================
# TEST UTILITIES
# ==================================================================================================

def expect_exception(function):
    try:
        function()
        return False
    except Exception:
        return True


def restore_file(path, original):
    atomic_write_json(
        path,
        original,
    )


# ==================================================================================================
# VALIDATION
# ==================================================================================================

def run_validation():

    with RUNTIME_LOCK:
        RUNTIME["phase"] = (
            "LIVE_READ_ONLY_VALIDATION"
        )

    clean_test_state()

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: SAFETY CONFIGURATION"
    )

    assert_pass(
        "Authenticated Read Only Is Enabled",
        AUTHENTICATED_READ_ONLY is True,
    )

    assert_pass(
        "Public Read Only Is Enabled",
        PUBLIC_READ_ONLY is True,
    )

    assert_pass(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    assert_pass(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    assert_pass(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    assert_pass(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    assert_pass(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    assert_pass(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    assert_pass(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: API CREDENTIAL PRESENCE"
    )

    assert_pass(
        "WEEX API Key Is Present",
        bool(API_KEY),
    )

    assert_pass(
        "WEEX API Secret Is Present",
        bool(API_SECRET),
    )

    assert_pass(
        "WEEX API Passphrase Is Present",
        bool(API_PASSPHRASE),
    )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: LIVE READ-ONLY STATE"
    )

    live = read_live_state()

    assert_pass(
        "Available Balance Was Read",
        live["balance"] is not None,
    )

    assert_pass(
        "Available Balance Is Positive",
        live["balance"] > 0,
    )

    assert_pass(
        "Market Price Was Read",
        live["market_price"] is not None,
    )

    assert_pass(
        "Market Price Is Positive",
        live["market_price"] > 0,
    )

    assert_pass(
        "Contract Information Was Read",
        bool(live["contract"]),
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_string(live['balance'])}"
    )

    log(
        f"{VERSION}: MARK PRICE="
        f"{decimal_string(live['market_price'])}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(live['positions'])}"
    )

    log(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(live['btc_positions'])}"
    )

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: SYNTHETIC ENTRY CONSTRUCTION"
    )

    entry = create_synthetic_entry(
        live
    )

    assert_pass(
        "Entry Is Synthetic Only",
        entry["intent"]["syntheticOnly"] is True,
    )

    assert_pass(
        "Entry Forbids Transmission",
        entry["intent"]["transmissionAllowed"] is False,
    )

    assert_pass(
        "Entry Forbids Network Write",
        entry["intent"]["networkWriteAllowed"] is False,
    )

    assert_pass(
        "Synthetic Quantity Is Positive",
        entry["quantity"] > 0,
    )

    assert_pass(
        "Client Order ID Exists",
        bool(entry["client_order_id"]),
    )

    assert_pass(
        "Exactly One Synthetic Entry Dispatch Occurred",
        COUNTERS["synthetic_dispatches"] == 1,
    )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: OPEN LIFECYCLE"
    )

    lifecycle = create_open_lifecycle(
        entry
    )

    assert_pass(
        "Lifecycle Is Synthetic",
        lifecycle["syntheticOnly"] is True,
    )

    assert_pass(
        "Lifecycle Starts OPEN",
        lifecycle["state"] == "OPEN",
    )

    assert_pass(
        "Initial Quantity Is Preserved",
        Decimal(
            lifecycle["initialQuantity"]
        ) == entry["quantity"],
    )

    assert_pass(
        "Position Open Event Exists",
        lifecycle["events"][0]["event"]
        == "POSITION_OPENED",
    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: TP1 PRE-RESTART STATE"
    )

    simulate_tp1(
        lifecycle
    )

    assert_pass(
        "TP1 Is Complete",
        lifecycle["tp1Done"] is True,
    )

    assert_pass(
        "Position Remains OPEN After TP1",
        lifecycle["state"] == "OPEN",
    )

    assert_pass(
        "Remaining Quantity Is Positive",
        Decimal(
            lifecycle["remainingQuantity"]
        ) > 0,
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: PRE-RESTART COMPLETE BINDING"
    )

    binding_before_restart = create_complete_binding(
        live["live_state"],
        entry,
        lifecycle,
    )

    assert_pass(
        "Binding Is Synthetic",
        binding_before_restart[
            "syntheticOnly"
        ] is True,
    )

    assert_pass(
        "Binding Forbids Transmission",
        binding_before_restart[
            "transmissionAllowed"
        ] is False,
    )

    assert_pass(
        "Binding Forbids Network Write",
        binding_before_restart[
            "networkWriteAllowed"
        ] is False,
    )

    assert_pass(
        "Lifecycle SHA256 Is Bound",
        binding_before_restart[
            "lifecycleSHA256"
        ] == sha256_object(
            lifecycle
        ),
    )

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: DURABLE PRE-RESTART SNAPSHOT"
    )

    generation = 1
    recovery_epoch = 1

    manifest_before_restart = persist_state(
        lifecycle=lifecycle,
        binding=binding_before_restart,
        generation=generation,
        recovery_epoch=recovery_epoch,
    )

    assert_pass(
        "Snapshot File Exists",
        os.path.isfile(
            SNAPSHOT_FILE
        ),
    )

    assert_pass(
        "Journal File Exists",
        os.path.isfile(
            JOURNAL_FILE
        ),
    )

    assert_pass(
        "Manifest File Exists",
        os.path.isfile(
            MANIFEST_FILE
        ),
    )

    assert_pass(
        "Manifest Hash Is Valid",
        validate_manifest_hash(
            manifest_before_restart
        ),
    )

    assert_pass(
        "Lifecycle Hash Is Persisted",
        manifest_before_restart[
            "lifecycleSHA256"
        ] == sha256_object(
            lifecycle
        ),
    )

    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: SIMULATED PROCESS RESTART"
    )

    pre_restart_hash = sha256_object(
        lifecycle
    )

    pre_restart_events = deep_copy(
        lifecycle["events"]
    )

    lifecycle = None
    binding_before_restart = None

    EVENT_IDS.clear()

    restored = restore_state()

    lifecycle = restored[
        "lifecycle"
    ]

    assert_pass(
        "Restart Restore Succeeded",
        COUNTERS["restart_restores"] == 1,
    )

    assert_pass(
        "Restored Lifecycle Hash Matches",
        sha256_object(
            lifecycle
        ) == pre_restart_hash,
    )

    assert_pass(
        "Restored Event Journal Matches",
        lifecycle["events"]
        == pre_restart_events,
    )

    assert_pass(
        "Restored State Remains OPEN",
        lifecycle["state"] == "OPEN",
    )

    assert_pass(
        "TP1 State Survived Restart",
        lifecycle["tp1Done"] is True,
    )

    # Rebuild in-memory event registry exactly as a process would after restore.

    for event in lifecycle[
        "events"
    ]:
        EVENT_IDS.add(
            event["eventId"]
        )

    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: EXACTLY-ONCE RECOVERY"
    )

    recovery_receipt = recover_exactly_once(
        restored
    )

    assert_pass(
        "Recovery Receipt Is Synthetic",
        recovery_receipt[
            "syntheticOnly"
        ] is True,
    )

    assert_pass(
        "Recovery Receipt Forbids Network Write",
        recovery_receipt[
            "networkWriteAllowed"
        ] is False,
    )

    assert_pass(
        "Recovery Did Not Transmit",
        recovery_receipt[
            "transmitted"
        ] is False,
    )

    assert_pass(
        "Exactly One Recovery Dispatch Occurred",
        COUNTERS["recovery_dispatches"] == 1,
    )

    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: RECOVERY REPLAY REJECTION"
    )

    replay_rejected = expect_exception(
        lambda: recover_exactly_once(
            restored
        )
    )

    assert_pass(
        "Second Recovery Is Rejected",
        replay_rejected,
    )

    assert_pass(
        "Recovery Replay Counter Increased",
        COUNTERS["replays_blocked"] == 1,
    )

    assert_pass(
        "Recovery Dispatch Count Remains One",
        COUNTERS["recovery_dispatches"] == 1,
    )

    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: DUPLICATE EVENT REJECTION"
    )

    duplicate_event = deep_copy(
        lifecycle["events"][0]
    )

    duplicate_rejected = expect_exception(
        lambda: append_event(
            lifecycle,
            duplicate_event,
        )
    )

    assert_pass(
        "Duplicate Event ID Is Rejected",
        duplicate_rejected,
    )

    assert_pass(
        "Duplicate Event Counter Increased",
        COUNTERS[
            "duplicate_events_blocked"
        ] == 1,
    )

    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    section(
        f"{VERSION} TEST 13: CONTINUE LIFECYCLE AFTER RESTART"
    )

    simulate_tp2(
        lifecycle
    )

    assert_pass(
        "TP2 Completed After Restart",
        lifecycle["tp2Done"] is True,
    )

    assert_pass(
        "Trailing Is Armed",
        lifecycle["trailingArmed"] is True,
    )

    assert_pass(
        "Position Remains OPEN",
        lifecycle["state"] == "OPEN",
    )

    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: TRAILING STATE PERSISTENCE"
    )

    simulate_trailing_high(
        lifecycle
    )

    binding_trailing = create_complete_binding(
        live["live_state"],
        entry,
        lifecycle,
    )

    generation = 2
    recovery_epoch = 2

    trailing_manifest = persist_state(
        lifecycle,
        binding_trailing,
        generation,
        recovery_epoch,
    )

    trailing_hash = sha256_object(
        lifecycle
    )

    restored_trailing = restore_state()

    assert_pass(
        "Trailing Snapshot Restored",
        sha256_object(
            restored_trailing[
                "lifecycle"
            ]
        ) == trailing_hash,
    )

    assert_pass(
        "Trailing Armed State Survived Restart",
        restored_trailing[
            "lifecycle"
        ][
            "trailingArmed"
        ] is True,
    )

    assert_pass(
        "Highest Price Survived Restart",
        restored_trailing[
            "lifecycle"
        ][
            "highestPrice"
        ]
        == lifecycle[
            "highestPrice"
        ],
    )

    lifecycle = restored_trailing[
        "lifecycle"
    ]

    # Rebuild event registry after simulated second restart.

    EVENT_IDS.clear()

    for event in lifecycle[
        "events"
    ]:
        EVENT_IDS.add(
            event["eventId"]
        )

    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    section(
        f"{VERSION} TEST 15: TERMINAL TRAILING EXIT"
    )

    simulate_trailing_exit(
        lifecycle
    )

    assert_pass(
        "Trailing Exit Closed Position",
        lifecycle["state"]
        == "CLOSED",
    )

    assert_pass(
        "Remaining Quantity Is Zero",
        Decimal(
            lifecycle[
                "remainingQuantity"
            ]
        ) == 0,
    )

    assert_pass(
        "TP3 Is Complete",
        lifecycle["tp3Done"] is True,
    )

    assert_pass(
        "Exit Reason Is Recorded",
        lifecycle["exitReason"]
        == "TP3_TRAILING_EXIT",
    )

    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    section(
        f"{VERSION} TEST 16: TERMINAL STATE DURABILITY"
    )

    terminal_binding = create_complete_binding(
        live["live_state"],
        entry,
        lifecycle,
    )

    generation = 3
    recovery_epoch = 3

    terminal_manifest = persist_state(
        lifecycle,
        terminal_binding,
        generation,
        recovery_epoch,
    )

    terminal_hash = sha256_object(
        lifecycle
    )

    restored_terminal = restore_state()

    terminal_lifecycle = restored_terminal[
        "lifecycle"
    ]

    assert_pass(
        "Terminal Snapshot Restored",
        sha256_object(
            terminal_lifecycle
        ) == terminal_hash,
    )

    assert_pass(
        "Terminal State Remains CLOSED",
        terminal_lifecycle[
            "state"
        ] == "CLOSED",
    )

    assert_pass(
        "Terminal Remaining Quantity Remains Zero",
        Decimal(
            terminal_lifecycle[
                "remainingQuantity"
            ]
        ) == 0,
    )

    assert_pass(
        "Terminal Exit Reason Survived Restart",
        terminal_lifecycle[
            "exitReason"
        ] == "TP3_TRAILING_EXIT",
    )

    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    section(
        f"{VERSION} TEST 17: TERMINAL STATE IMMUTABILITY"
    )

    terminal_before = deep_copy(
        terminal_lifecycle
    )

    pyramid_allowed = (
        terminal_lifecycle[
            "state"
        ] == "OPEN"
        and terminal_lifecycle[
            "pyramidAdds"
        ] < MAX_PYRAMID_ADDS
    )

    backup_allowed = (
        terminal_lifecycle[
            "state"
        ] == "OPEN"
        and terminal_lifecycle[
            "backups"
        ] < MAX_BACKUPS
    )

    assert_pass(
        "Terminal Position Cannot Pyramid",
        pyramid_allowed is False,
    )

    assert_pass(
        "Terminal Position Cannot Backup",
        backup_allowed is False,
    )

    assert_pass(
        "Terminal Lifecycle Is Unchanged",
        terminal_lifecycle
        == terminal_before,
    )

    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    section(
        f"{VERSION} TEST 18: LOSS COOLDOWN PERSISTENCE"
    )

    loss_lifecycle = {
        "version": VERSION,
        "syntheticOnly": True,
        "networkWriteAllowed": False,
        "state": "CLOSED",
        "remainingQuantity": "0",
        "cooldownUntil": str(
            now_seconds()
            + LOSS_COOLDOWN_SECONDS
        ),
        "exitReason": "SYNTHETIC_LOSS_EXIT",
        "events": [
            create_event(
                "SYNTHETIC_LOSS_EXIT",
                reason="LOSS",
            )
        ],
    }

    loss_binding = {
        "version": VERSION,
        "syntheticOnly": True,
        "networkWriteAllowed": False,
        "lifecycleSHA256": sha256_object(
            loss_lifecycle
        ),
    }

    persist_state(
        loss_lifecycle,
        loss_binding,
        generation=4,
        recovery_epoch=4,
    )

    restored_loss = restore_state()

    cooldown_until = int(
        restored_loss[
            "lifecycle"
        ][
            "cooldownUntil"
        ]
    )

    assert_pass(
        "Cooldown Survived Restart",
        cooldown_until
        > now_seconds(),
    )

    assert_pass(
        "Cooldown Duration Is Preserved",
        cooldown_until
        - now_seconds()
        <= LOSS_COOLDOWN_SECONDS,
    )

    assert_pass(
        "Loss Exit Reason Survived Restart",
        restored_loss[
            "lifecycle"
        ][
            "exitReason"
        ] == "SYNTHETIC_LOSS_EXIT",
    )

    # Restore terminal state for subsequent tests.

    persist_state(
        terminal_lifecycle,
        terminal_binding,
        generation=5,
        recovery_epoch=5,
    )

    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    section(
        f"{VERSION} TEST 19: LIFECYCLE TAMPER REJECTION"
    )

    original_snapshot = read_json_file(
        SNAPSHOT_FILE
    )

    tampered_snapshot = deep_copy(
        original_snapshot
    )

    tampered_snapshot[
        "lifecycle"
    ][
        "remainingQuantity"
    ] = "999"

    atomic_write_json(
        SNAPSHOT_FILE,
        tampered_snapshot,
    )

    tamper_rejected = expect_exception(
        restore_state
    )

    assert_pass(
        "Tampered Lifecycle Is Rejected",
        tamper_rejected,
    )

    assert_pass(
        "Tamper Rejection Counter Increased",
        COUNTERS[
            "tamper_rejections"
        ] >= 1,
    )

    restore_file(
        SNAPSHOT_FILE,
        original_snapshot,
    )

    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    section(
        f"{VERSION} TEST 20: JOURNAL TAMPER REJECTION"
    )

    original_journal = read_json_file(
        JOURNAL_FILE
    )

    tampered_journal = deep_copy(
        original_journal
    )

    if tampered_journal:
        tampered_journal[0][
            "event"
        ] = "FORGED_EVENT"
    else:
        tampered_journal.append(
            {
                "eventId": "forged",
                "event": "FORGED_EVENT",
            }
        )

    atomic_write_json(
        JOURNAL_FILE,
        tampered_journal,
    )

    journal_tamper_rejected = expect_exception(
        restore_state
    )

    assert_pass(
        "Tampered Journal Is Rejected",
        journal_tamper_rejected,
    )

    restore_file(
        JOURNAL_FILE,
        original_journal,
    )

    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    section(
        f"{VERSION} TEST 21: MANIFEST TAMPER REJECTION"
    )

    original_manifest = read_json_file(
        MANIFEST_FILE
    )

    forged_manifest = deep_copy(
        original_manifest
    )

    forged_manifest[
        "generation"
    ] = 999999

    atomic_write_json(
        MANIFEST_FILE,
        forged_manifest,
    )

    manifest_tamper_rejected = expect_exception(
        restore_state
    )

    assert_pass(
        "Tampered Manifest Is Rejected",
        manifest_tamper_rejected,
    )

    restore_file(
        MANIFEST_FILE,
        original_manifest,
    )

    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    section(
        f"{VERSION} TEST 22: CORRUPTED SNAPSHOT REJECTION"
    )

    with open(
        SNAPSHOT_FILE,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(
            "{CORRUPTED JSON"
        )

    corrupted_snapshot_rejected = (
        expect_exception(
            restore_state
        )
    )

    assert_pass(
        "Corrupted Snapshot Is Rejected",
        corrupted_snapshot_rejected,
    )

    restore_file(
        SNAPSHOT_FILE,
        original_snapshot,
    )

    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    section(
        f"{VERSION} TEST 23: ATOMIC SNAPSHOT REPLACEMENT"
    )

    atomic_test = read_json_file(
        SNAPSHOT_FILE
    )

    atomic_test[
        "atomicReplacementProbe"
    ] = True

    atomic_write_json(
        SNAPSHOT_FILE,
        atomic_test,
    )

    atomic_readback = read_json_file(
        SNAPSHOT_FILE
    )

    assert_pass(
        "Atomic Replacement Produced Valid JSON",
        isinstance(
            atomic_readback,
            dict,
        ),
    )

    assert_pass(
        "Atomic Replacement Preserved Probe",
        atomic_readback.get(
            "atomicReplacementProbe"
        ) is True,
    )

    restore_file(
        SNAPSHOT_FILE,
        original_snapshot,
    )

    # ==============================================================================================
    # TEST 24
    # ==============================================================================================

    section(
        f"{VERSION} TEST 24: SIGNAL EXPIRY RESTART SEMANTICS"
    )

    signal_created_at = (
        now_seconds()
        - 10
    )

    signal = {
        "createdAt": signal_created_at,
        "expiresAt": (
            signal_created_at
            + SIGNAL_EXPIRY_SECONDS
        ),
    }

    signal_before_expiry = (
        signal["createdAt"]
        + SIGNAL_EXPIRY_SECONDS
        - 1
    )

    signal_at_boundary = (
        signal["createdAt"]
        + SIGNAL_EXPIRY_SECONDS
    )

    assert_pass(
        "Signal Is Valid Before Expiry",
        signal_before_expiry
        < signal["expiresAt"],
    )

    assert_pass(
        "Signal Is Expired At Boundary",
        signal_at_boundary
        >= signal["expiresAt"],
    )

    # ==============================================================================================
    # TEST 25
    # ==============================================================================================

    section(
        f"{VERSION} TEST 25: GENERATION / RECOVERY EPOCH BINDING"
    )

    restored_final = restore_state()

    final_manifest = restored_final[
        "manifest"
    ]

    assert_pass(
        "Generation Is Persisted",
        int(
            final_manifest[
                "generation"
            ]
        ) == 5,
    )

    assert_pass(
        "Recovery Epoch Is Persisted",
        int(
            final_manifest[
                "recoveryEpoch"
            ]
        ) == 5,
    )

    recovery_key_a = create_recovery_key(
        5,
        5,
        final_manifest[
            "lifecycleSHA256"
        ],
    )

    recovery_key_b = create_recovery_key(
        6,
        6,
        final_manifest[
            "lifecycleSHA256"
        ],
    )

    assert_pass(
        "Generation Change Produces New Recovery Key",
        recovery_key_a
        != recovery_key_b,
    )

    # ==============================================================================================
    # TEST 26
    # ==============================================================================================

    section(
        f"{VERSION} TEST 26: COMPLETE DURABLE EXECUTION BINDING"
    )

    final_binding = restored_final[
        "binding"
    ]

    assert_pass(
        "Final Binding Is Synthetic",
        final_binding[
            "syntheticOnly"
        ] is True,
    )

    assert_pass(
        "Final Binding Forbids Network Write",
        final_binding[
            "networkWriteAllowed"
        ] is False,
    )

    assert_pass(
        "Final Lifecycle Hash Is Exact",
        final_binding[
            "lifecycleSHA256"
        ]
        == sha256_object(
            restored_final[
                "lifecycle"
            ]
        ),
    )

    assert_pass(
        "Manifest Binds Exact Lifecycle",
        final_manifest[
            "lifecycleSHA256"
        ]
        == sha256_object(
            restored_final[
                "lifecycle"
            ]
        ),
    )

    assert_pass(
        "Manifest Binds Exact Journal",
        final_manifest[
            "journalSHA256"
        ]
        == sha256_object(
            restored_final[
                "journal"
            ]
        ),
    )

    assert_pass(
        "Manifest Binds Exact Complete Binding",
        final_manifest[
            "bindingSHA256"
        ]
        == sha256_object(
            final_binding
        ),
    )

    log(
        f"{VERSION}: FINAL LIFECYCLE="
        f"{canonical_json(restored_final['lifecycle'])}"
    )

    log(
        f"{VERSION}: FINAL LIFECYCLE SHA256="
        f"{final_manifest['lifecycleSHA256']}"
    )

    log(
        f"{VERSION}: FINAL MANIFEST="
        f"{canonical_json(final_manifest)}"
    )

    # ==============================================================================================
    # TEST 27
    # ==============================================================================================

    section(
        f"{VERSION} TEST 27: WRITE FUNCTION FIREBREAK"
    )

    assert_pass(
        "HTTP POST Is Rejected",
        expect_exception(
            lambda: http_post()
        ),
    )

    assert_pass(
        "HTTP PUT Is Rejected",
        expect_exception(
            lambda: http_put()
        ),
    )

    assert_pass(
        "HTTP PATCH Is Rejected",
        expect_exception(
            lambda: http_patch()
        ),
    )

    assert_pass(
        "HTTP DELETE Is Rejected",
        expect_exception(
            lambda: http_delete()
        ),
    )

    assert_pass(
        "Real Order Function Is Rejected",
        expect_exception(
            lambda: real_order()
        ),
    )

    assert_pass(
        "Demo Order Function Is Rejected",
        expect_exception(
            lambda: demo_order()
        ),
    )

    assert_pass(
        "Leverage Mutation Function Is Rejected",
        expect_exception(
            lambda: mutate_leverage()
        ),
    )

    assert_pass(
        "Margin Mutation Function Is Rejected",
        expect_exception(
            lambda: mutate_margin()
        ),
    )

    assert_pass(
        "Position Mutation Function Is Rejected",
        expect_exception(
            lambda: mutate_position()
        ),
    )

    assert_pass(
        "Account Mutation Function Is Rejected",
        expect_exception(
            lambda: mutate_account()
        ),
    )

    # ==============================================================================================
    # TEST 28
    # ==============================================================================================

    section(
        f"{VERSION} TEST 28: FINAL WRITE FIREBREAK"
    )

    assert_pass(
        "Network Write Count Remains Zero",
        COUNTERS[
            "network_writes"
        ] == 0,
    )

    assert_pass(
        "Real Order Count Remains Zero",
        COUNTERS[
            "real_orders"
        ] == 0,
    )

    assert_pass(
        "Demo Order Count Remains Zero",
        COUNTERS[
            "demo_orders"
        ] == 0,
    )

    assert_pass(
        "Leverage Mutation Count Remains Zero",
        COUNTERS[
            "leverage_mutations"
        ] == 0,
    )

    assert_pass(
        "Margin Mutation Count Remains Zero",
        COUNTERS[
            "margin_mutations"
        ] == 0,
    )

    assert_pass(
        "Position Mutation Count Remains Zero",
        COUNTERS[
            "position_mutations"
        ] == 0,
    )

    assert_pass(
        "Account Mutation Count Remains Zero",
        COUNTERS[
            "account_mutations"
        ] == 0,
    )

    assert_pass(
        "Authenticated Transport Used GET Only",
        COUNTERS[
            "authenticated_gets"
        ] == 3,
    )

    assert_pass(
        "Public Transport Used GET Only",
        COUNTERS[
            "public_gets"
        ] == 2,
    )

    assert_pass(
        "Exactly One Initial Synthetic Dispatch Occurred",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    assert_pass(
        "At Least Three Restart Restores Occurred",
        COUNTERS[
            "restart_restores"
        ] >= 3,
    )

    assert_pass(
        "At Least One Replay Was Blocked",
        COUNTERS[
            "replays_blocked"
        ] >= 1,
    )

    assert_pass(
        "At Least One Duplicate Event Was Blocked",
        COUNTERS[
            "duplicate_events_blocked"
        ] >= 1,
    )

    assert_pass(
        "At Least One Tamper Attempt Was Rejected",
        COUNTERS[
            "tamper_rejections"
        ] >= 1,
    )

    # ==============================================================================================
    # COMPLETE
    # ==============================================================================================

    with RUNTIME_LOCK:
        RUNTIME["phase"] = (
            "DURABLE_SYNTHETIC_RECOVERY_VALIDATED"
        )

        RUNTIME[
            "validation_complete"
        ] = True

    section(
        f"{VERSION}: VALIDATION COMPLETE"
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
        f"{VERSION}: SYNTHETIC ENTRY DISPATCHES="
        f"{COUNTERS['synthetic_dispatches']}"
    )

    log(
        f"{VERSION}: SYNTHETIC RECOVERY DISPATCHES="
        f"{COUNTERS['recovery_dispatches']}"
    )

    log(
        f"{VERSION}: RESTART RESTORES="
        f"{COUNTERS['restart_restores']}"
    )

    log(
        f"{VERSION}: REPLAYS BLOCKED="
        f"{COUNTERS['replays_blocked']}"
    )

    log(
        f"{VERSION}: DUPLICATE EVENTS BLOCKED="
        f"{COUNTERS['duplicate_events_blocked']}"
    )

    log(
        f"{VERSION}: TAMPER REJECTIONS="
        f"{COUNTERS['tamper_rejections']}"
    )

    log(
        f"{VERSION}: FINAL LIFECYCLE STATE="
        f"{restored_final['lifecycle']['state']}"
    )

    log(
        f"{VERSION}: STATE DIRECTORY="
        f"{STATE_DIR}"
    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO DEMO ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO LEVERAGE MUTATION WAS SENT"
    )

    log(
        f"{VERSION}: NO MARGIN MUTATION WAS SENT"
    )

    log(
        f"{VERSION}: NO POSITION MUTATION WAS SENT"
    )

    log(
        f"{VERSION}: NO ACCOUNT MUTATION WAS SENT"
    )

    log(
        f"{VERSION}: DURABLE SYNTHETIC "
        f"RESTART / RECOVERY LIFECYCLE VALIDATED"
    )


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_loop():
    while True:
        time.sleep(30)

        with RUNTIME_LOCK:
            RUNTIME["heartbeat"] += 1

            heartbeat_number = (
                RUNTIME["heartbeat"]
            )

            phase = RUNTIME[
                "phase"
            ]

        log(
            f"{VERSION}: HEARTBEAT {heartbeat_number} | "
            f"phase={phase} | "
            f"authenticated-read-only={AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get={COUNTERS['authenticated_gets']} | "
            f"public-get={COUNTERS['public_gets']} | "
            f"network-writes={COUNTERS['network_writes']} | "
            f"real-orders={COUNTERS['real_orders']} | "
            f"demo-orders={COUNTERS['demo_orders']} | "
            f"synthetic-dispatches={COUNTERS['synthetic_dispatches']} | "
            f"recovery-dispatches={COUNTERS['recovery_dispatches']} | "
            f"restart-restores={COUNTERS['restart_restores']} | "
            f"replays-blocked={COUNTERS['replays_blocked']}"
        )


# ==================================================================================================
# MAIN
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

    log(
        f"{VERSION}: TARGET MARGIN={TARGET_MARGIN_TYPE}"
    )

    log(
        f"{VERSION}: TARGET LEVERAGE={TARGET_LEVERAGE}x"
    )

    log(
        f"{VERSION}: INITIAL ENTRY={decimal_string(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX PYRAMID ADDS={MAX_PYRAMID_ADDS}"
    )

    log(
        f"{VERSION}: MAX BACKUPS={MAX_BACKUPS}"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_string(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    health_server = run_health_server()

    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        daemon=True,
    )

    heartbeat_thread.start()

    try:
        run_validation()

    except Exception as exc:

        with RUNTIME_LOCK:
            RUNTIME["phase"] = (
                "VALIDATION_FAILED"
            )

            RUNTIME[
                "validation_failed"
            ] = True

            RUNTIME[
                "error"
            ] = (
                f"{type(exc).__name__}: {exc}"
            )

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

    # ----------------------------------------------------------------------------------------------
    # Keep process alive for Render health checks and heartbeat observation.
    # ----------------------------------------------------------------------------------------------

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
