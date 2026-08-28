#
==================================================================================================
# R35A - DURABLE EXACTLY-ONCE SYNTHETIC STRATEGY LIFECYCLE VALIDATION
# ==================================================================================================
#
# PURPOSE
#
#   R35A advances the validated R34Z synthetic lifecycle into durable exactly-once
#   lifecycle transition testing.
#
#   It validates:
#
#       LIVE READ-ONLY ACCOUNT STATE
#                    ↓
#       LIVE READ-ONLY MARKET STATE
#                    ↓
#       STRATEGY BUDGET / QUANTITY NORMALIZATION
#                    ↓
#       DURABLE PREPARE
#                    ↓
#       DURABLE COMMIT
#                    ↓
#       SYNTHETIC DISPATCH
#                    ↓
#       DURABLE RECEIPT
#                    ↓
#       DURABLE APPLY
#                    ↓
#       RESTART / RECOVERY
#                    ↓
#       EXACTLY-ONCE FENCING
#
#
# SAFETY MODEL
#
#   - AUTHENTICATED GET ONLY
#   - PUBLIC GET ONLY
#   - SYNTHETIC TRANSPORT ONLY
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
#
# IMPORTANT
#
#   R35A DOES NOT place any order.
#
#   R35A DOES NOT contain a functioning order-writing HTTP transport.
#
#   Every "dispatch" performed by the lifecycle engine is LOCAL AND SYNTHETIC.
#
#
# STRATEGY PARAMETERS
#
#   SYMBOL                       BTCUSDT
#   MARGIN TYPE                  ISOLATED
#   TARGET LEVERAGE              100x
#   INITIAL ENTRY                5%
#   MAX PYRAMID ADDS             1
#   PYRAMID SIZE                 5%
#   MAX BACKUPS                  3
#   BACKUP SIZE                  5%
#   MAX FUND EXPOSURE            35%
#   TP1 SHARE                    20%
#   TP2 SHARE                    20%
#   TP3 SHARE                    60%
#   TP1 TRIGGER                  0.5%
#   TP2 TRIGGER                  1.0%
#   TRAILING DISTANCE            0.20%
#
#
# DURABILITY MODEL
#
#   Each synthetic mutation follows:
#
#       PREPARED
#          ↓
#       COMMITTED
#          ↓
#       DISPATCHED
#          ↓
#       APPLIED
#
#   A durable dispatch receipt is written before the engine reports successful
#   synthetic dispatch completion.
#
#   Restart recovery therefore distinguishes:
#
#       PREPARED only:
#           not authorized for dispatch
#
#       COMMITTED:
#           eligible for one synthetic dispatch
#
#       DISPATCHED:
#           receipt already exists - dispatch MUST NOT happen again
#
#       APPLIED:
#           terminal transition result - replay MUST be rejected
#
#
# ==================================================================================================

import base64
import copy
import hashlib
import hmac
import json
import os
import shutil
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# ==================================================================================================
# CONFIGURATION
# ==================================================================================================

VERSION = "R35A"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper().strip()

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

PORT = int(os.getenv("PORT", "10000"))

STATE_DIR = os.getenv("R35A_STATE_DIR", "/tmp/r35a_state")
STATE_FILE = os.path.join(STATE_DIR, "strategy_state.json")
JOURNAL_FILE = os.path.join(STATE_DIR, "transition_journal.jsonl")

AUTHENTICATED_TRANSPORT_READ_ONLY = True
PUBLIC_TRANSPORT_READ_ONLY = True
SYNTHETIC_TRANSPORT_ONLY = True

NETWORK_WRITES_ENABLED = False
REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_SIZE_PERCENT = Decimal("5")
BACKUP_SIZE_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_SHARE_PERCENT = Decimal("20")
TP2_SHARE_PERCENT = Decimal("20")
TP3_SHARE_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

REQUEST_TIMEOUT_SECONDS = 15

BALANCE_PATH = "/capi/v3/account/balance"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
POSITION_PATH = "/capi/v3/account/position/allPosition"
MARKET_PRICE_PATH = "/capi/v3/market/symbolPrice"
EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"


# ==================================================================================================
# API CREDENTIALS
# ==================================================================================================

WEEX_API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("API_KEY")
    or ""
).strip()

WEEX_API_SECRET = (
    os.getenv("WEEX_API_SECRET")
    or os.getenv("WEEX_SECRET_KEY")
    or os.getenv("WEEX_SECRET")
    or os.getenv("API_SECRET")
    or ""
).strip()

WEEX_API_PASSPHRASE = (
    os.getenv("WEEX_API_PASSPHRASE")
    or os.getenv("WEEX_PASSPHRASE")
    or os.getenv("API_PASSPHRASE")
    or ""
).strip()


# ==================================================================================================
# DISPLAY HELPERS
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


def assert_test(name, condition):
    if condition:
        pass_test(name)
        return True

    fail_test(name)
    raise AssertionError(name)


# ==================================================================================================
# BASIC HELPERS
# ==================================================================================================

def decimal_value(value, default="0"):
    try:
        if value is None:
            return Decimal(default)
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def decimal_string(value):
    value = Decimal(str(value))

    text = format(value, "f")

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


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_object(value):
    return sha256_text(canonical_json(value))


def utc_ms():
    return int(time.time() * 1000)


def deep_copy(value):
    return copy.deepcopy(value)


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/health", "/healthz"):
            body = json.dumps(
                {
                    "status": "ok",
                    "version": VERSION,
                    "symbol": SYMBOL,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                    "network_writes_enabled": NETWORK_WRITES_ENABLED,
                },
                separators=(",", ":"),
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():
    try:
        server = ThreadingHTTPServer(("0.0.0.0", PORT), HealthHandler)

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        return server

    except OSError as exc:
        log(f"{VERSION}: HEALTH SERVER WARNING={exc}")
        return None


# ==================================================================================================
# HARD NETWORK WRITE FIREBREAK
# ==================================================================================================

class NetworkWriteRejected(RuntimeError):
    pass


def reject_network_write(operation):
    raise NetworkWriteRejected(
        f"{VERSION}: NETWORK WRITE REJECTED: {operation}"
    )


def http_post(*args, **kwargs):
    return reject_network_write("HTTP POST")


def http_put(*args, **kwargs):
    return reject_network_write("HTTP PUT")


def http_patch(*args, **kwargs):
    return reject_network_write("HTTP PATCH")


def http_delete(*args, **kwargs):
    return reject_network_write("HTTP DELETE")


def generic_network_write(*args, **kwargs):
    return reject_network_write("GENERIC NETWORK WRITE")


def place_real_order(*args, **kwargs):
    return reject_network_write("REAL ORDER")


def place_demo_order(*args, **kwargs):
    return reject_network_write("DEMO ORDER")


def mutate_leverage(*args, **kwargs):
    return reject_network_write("LEVERAGE MUTATION")


def mutate_margin_type(*args, **kwargs):
    return reject_network_write("MARGIN TYPE MUTATION")


def mutate_position(*args, **kwargs):
    return reject_network_write("POSITION MUTATION")


# ==================================================================================================
# READ-ONLY HTTP TRANSPORT
# ==================================================================================================

def encode_query(params):
    if not params:
        return ""

    clean = []

    for key, value in params.items():
        if value is None:
            continue

        clean.append((str(key), str(value)))

    return urllib.parse.urlencode(clean)


def public_get(path, params=None):
    if not PUBLIC_TRANSPORT_READ_ONLY:
        raise RuntimeError("Public read-only transport is disabled")

    query = encode_query(params)

    url = BASE_URL + path

    if query:
        url += "?" + query

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"{VERSION}-readonly",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode("utf-8")

    except urllib.error.HTTPError as exc:
        body = ""

        try:
            body = exc.read().decode("utf-8")
        except Exception:
            pass

        raise RuntimeError(
            f"Public GET failed: {path} | "
            f"HTTP {exc.code} | {body}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Public GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Public GET returned invalid JSON: {path}"
        ) from exc


def create_auth_signature(timestamp, method, path, query=""):
    method = method.upper()

    if method != "GET":
        raise NetworkWriteRejected(
            f"{VERSION}: authenticated transport permits GET only"
        )

    if query:
        message = f"{timestamp}{method}{path}?{query}"
    else:
        message = f"{timestamp}{method}{path}"

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def authenticated_get(path, params=None):
    if not AUTHENTICATED_TRANSPORT_READ_ONLY:
        raise RuntimeError("Authenticated read-only transport disabled")

    if not WEEX_API_KEY:
        raise RuntimeError("WEEX API key is missing")

    if not WEEX_API_SECRET:
        raise RuntimeError("WEEX API secret is missing")

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError("WEEX API passphrase is missing")

    query = encode_query(params)

    timestamp = str(utc_ms())

    signature = create_auth_signature(
        timestamp=timestamp,
        method="GET",
        path=path,
        query=query,
    )

    url = BASE_URL + path

    if query:
        url += "?" + query

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "ACCESS-KEY": WEEX_API_KEY,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
            "ACCESS-TIMESTAMP": timestamp,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"{VERSION}-readonly",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode("utf-8")

    except urllib.error.HTTPError as exc:
        body = ""

        try:
            body = exc.read().decode("utf-8")
        except Exception:
            pass

        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"HTTP {exc.code} | {body}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Authenticated GET returned invalid JSON: {path}"
        ) from exc


# ==================================================================================================
# RESPONSE UNWRAPPING
# ==================================================================================================

def unwrap_data(value):
    current = value

    for _ in range(4):
        if not isinstance(current, dict):
            break

        moved = False

        for key in ("data", "result"):
            if key in current and current[key] is not None:
                current = current[key]
                moved = True
                break

        if not moved:
            break

    return current


def as_list(value):
    value = unwrap_data(value)

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        return [value]

    return []


# ==================================================================================================
# LIVE BALANCE PARSER
# ==================================================================================================

def parse_available_usdt(payload):
    value = unwrap_data(payload)

    records = value if isinstance(value, list) else [value]

    for record in records:
        if not isinstance(record, dict):
            continue

        asset = str(
            record.get("asset")
            or record.get("coin")
            or record.get("marginCoin")
            or ""
        ).upper()

        if asset and asset not in ("USDT", "SUSDT"):
            continue

        for key in (
            "availableBalance",
            "available",
            "availableEquity",
            "free",
        ):
            if key in record:
                amount = decimal_value(record.get(key))

                if amount >= 0:
                    return amount

    raise RuntimeError(
        f"Unable to parse available USDT from balance response: {payload}"
    )


# ==================================================================================================
# SYMBOL CONFIG PARSER
# ==================================================================================================

def parse_symbol_config(payload):
    records = as_list(payload)

    for record in records:
        if not isinstance(record, dict):
            continue

        record_symbol = str(
            record.get("symbol")
            or record.get("contractCode")
            or ""
        ).upper()

        if record_symbol == SYMBOL:
            return record

    if len(records) == 1 and isinstance(records[0], dict):
        return records[0]

    raise RuntimeError(
        f"Unable to locate {SYMBOL} symbol configuration"
    )


# ==================================================================================================
# POSITION PARSER
# ==================================================================================================

def parse_positions(payload):
    records = as_list(payload)

    parsed = []

    for record in records:
        if isinstance(record, dict):
            parsed.append(record)

    return parsed


def position_symbol(record):
    return str(
        record.get("symbol")
        or record.get("contractCode")
        or ""
    ).upper()


def position_size(record):
    for key in (
        "size",
        "positionAmt",
        "positionSize",
        "available",
        "total",
    ):
        if key in record:
            return abs(decimal_value(record.get(key)))

    return Decimal("0")


# ==================================================================================================
# MARKET PRICE PARSER
# ==================================================================================================

def parse_market_price(payload):
    value = unwrap_data(payload)

    if isinstance(value, list):
        records = value
    else:
        records = [value]

    for record in records:
        if not isinstance(record, dict):
            continue

        record_symbol = str(record.get("symbol") or "").upper()

        if record_symbol and record_symbol != SYMBOL:
            continue

        for key in (
            "price",
            "markPrice",
            "indexPrice",
            "last",
            "lastPrice",
        ):
            if key in record:
                price = decimal_value(record.get(key))

                if price > 0:
                    return price

    raise RuntimeError(
        f"Unable to parse market price from response: {payload}"
    )


# ==================================================================================================
# EXCHANGE INFORMATION PARSER
# ==================================================================================================

def find_symbol_record(payload):
    root = unwrap_data(payload)

    candidates = []

    if isinstance(root, list):
        candidates.extend(root)

    elif isinstance(root, dict):
        if isinstance(root.get("symbols"), list):
            candidates.extend(root["symbols"])

        if isinstance(root.get("contracts"), list):
            candidates.extend(root["contracts"])

        candidates.append(root)

    for record in candidates:
        if not isinstance(record, dict):
            continue

        symbol = str(
            record.get("symbol")
            or record.get("contractCode")
            or ""
        ).upper()

        if symbol == SYMBOL:
            return record

    raise RuntimeError(
        f"Unable to locate {SYMBOL} in exchange information"
    )


def first_positive_decimal(record, keys, default=None):
    for key in keys:
        if key not in record:
            continue

        value = decimal_value(record.get(key))

        if value > 0:
            return value

    if default is not None:
        return Decimal(str(default))

    raise RuntimeError(
        f"Unable to locate positive decimal from keys: {keys}"
    )


def parse_contract_information(payload):
    record = find_symbol_record(payload)

    min_qty = first_positive_decimal(
        record,
        (
            "minQty",
            "minOrderQty",
            "minOrderAmount",
            "minTradeNum",
            "minTradeAmount",
            "minimumOrderQuantity",
        ),
        default="0.0001",
    )

    qty_step = first_positive_decimal(
        record,
        (
            "quantityStep",
            "qtyStep",
            "stepSize",
            "sizeIncrement",
            "size_increment",
            "quantityIncrement",
        ),
        default="0.0001",
    )

    price_step = first_positive_decimal(
        record,
        (
            "priceStep",
            "tickSize",
            "tick_size",
            "priceEndStep",
            "priceIncrement",
        ),
        default="0.1",
    )

    return {
        "record": record,
        "min_qty": min_qty,
        "qty_step": qty_step,
        "price_step": price_step,
    }


# ==================================================================================================
# QUANTITY NORMALIZATION
# ==================================================================================================

def normalize_quantity_down(raw_qty, qty_step):
    raw_qty = Decimal(raw_qty)
    qty_step = Decimal(qty_step)

    if raw_qty <= 0:
        return Decimal("0")

    if qty_step <= 0:
        raise ValueError("Quantity step must be positive")

    units = (raw_qty / qty_step).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * qty_step


# ==================================================================================================
# DURABLE FILE HELPERS
# ==================================================================================================

def ensure_state_directory():
    os.makedirs(STATE_DIR, exist_ok=True)


def atomic_write_text(path, text):
    ensure_state_directory()

    temp_path = (
        path
        + ".tmp."
        + str(os.getpid())
        + "."
        + str(time.time_ns())
    )

    with open(temp_path, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temp_path, path)


def fsync_directory(path):
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except Exception:
        return

    try:
        os.fsync(descriptor)
    except Exception:
        pass
    finally:
        os.close(descriptor)


def atomic_write_json(path, value):
    atomic_write_text(
        path,
        canonical_json(value),
    )

    fsync_directory(os.path.dirname(path) or ".")


# ==================================================================================================
# SNAPSHOT INTEGRITY
# ==================================================================================================

def snapshot_payload(state):
    payload = deep_copy(state)
    payload.pop("integrity_sha256", None)
    return payload


def calculate_snapshot_hash(state):
    return sha256_object(snapshot_payload(state))


def seal_snapshot(state):
    sealed = deep_copy(state)
    sealed["integrity_sha256"] = calculate_snapshot_hash(sealed)
    return sealed


def snapshot_integrity_valid(state):
    if not isinstance(state, dict):
        return False

    expected = state.get("integrity_sha256")

    if not expected:
        return False

    return hmac.compare_digest(
        str(expected),
        calculate_snapshot_hash(state),
    )


def save_snapshot(state):
    sealed = seal_snapshot(state)
    atomic_write_json(STATE_FILE, sealed)
    return sealed


def load_snapshot():
    with open(STATE_FILE, "r", encoding="utf-8") as handle:
        state = json.load(handle)

    if not snapshot_integrity_valid(state):
        raise RuntimeError("Snapshot integrity validation failed")

    return state


# ==================================================================================================
# HASH-CHAIN JOURNAL
# ==================================================================================================

def journal_records():
    if not os.path.exists(JOURNAL_FILE):
        return []

    records = []

    with open(JOURNAL_FILE, "r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Journal JSON corruption at line {line_number}"
                ) from exc

            records.append(record)

    return records


def journal_record_hash(record):
    payload = deep_copy(record)
    payload.pop("record_sha256", None)
    return sha256_object(payload)


def validate_journal():
    records = journal_records()

    previous_hash = "GENESIS"

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            return False

        if record.get("previous_sha256") != previous_hash:
            return False

        claimed_hash = record.get("record_sha256")

        if not claimed_hash:
            return False

        calculated_hash = journal_record_hash(record)

        if not hmac.compare_digest(
            str(claimed_hash),
            calculated_hash,
        ):
            return False

        previous_hash = claimed_hash

    return True


def append_journal(event_type, transition_id, details=None):
    ensure_state_directory()

    existing = journal_records()

    if existing:
        previous_hash = existing[-1]["record_sha256"]
    else:
        previous_hash = "GENESIS"

    record = {
        "version": VERSION,
        "sequence": len(existing) + 1,
        "time_ms": utc_ms(),
        "event": event_type,
        "transition_id": transition_id,
        "details": details or {},
        "previous_sha256": previous_hash,
    }

    record["record_sha256"] = journal_record_hash(record)

    line = canonical_json(record) + "\n"

    with open(JOURNAL_FILE, "a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())

    fsync_directory(STATE_DIR)

    return record


# ==================================================================================================
# STRATEGY STATE
# ==================================================================================================

def create_initial_state():
    return {
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": 1,
        "strategy_phase": "NEW",

        "initial_entry_completed": False,
        "pyramid_count": 0,
        "backup_count": 0,

        "tp1_completed": False,
        "tp2_completed": False,
        "trailing_armed": False,
        "tp3_completed": False,
        "terminal_exit_completed": False,

        "transitions": {},
        "consumed_intents": [],
        "dispatch_receipts": [],

        "synthetic_dispatch_count": 0,
        "network_write_count": 0,

        "last_transition_id": None,
        "created_ms": utc_ms(),
        "updated_ms": utc_ms(),
    }


# ==================================================================================================
# SYNTHETIC INTENT CREATION
# ==================================================================================================

def create_transition_intent(
    transition_name,
    action,
    quantity,
    metadata=None,
):
    quantity_text = decimal_string(quantity)

    identity_payload = {
        "version": VERSION,
        "symbol": SYMBOL,
        "transition_name": transition_name,
        "action": action,
        "quantity": quantity_text,
        "metadata": metadata or {},
    }

    intent_hash = sha256_object(identity_payload)

    transition_id = (
        f"{VERSION.lower()}-"
        f"{transition_name.lower().replace('_', '-')}-"
        f"{intent_hash[:20]}"
    )

    return {
        "transition_id": transition_id,
        "intent_sha256": intent_hash,
        "version": VERSION,
        "symbol": SYMBOL,
        "transition_name": transition_name,
        "action": action,
        "quantity": quantity_text,
        "metadata": metadata or {},
    }


# ==================================================================================================
# EXACTLY-ONCE TRANSITION ENGINE
# ==================================================================================================

class DurableTransitionEngine:

    def __init__(self, state=None):
        if state is None:
            state = create_initial_state()

        self.state = state

    @classmethod
    def restore(cls):
        return cls(load_snapshot())

    def persist(self):
        self.state["updated_ms"] = utc_ms()
        self.state = save_snapshot(self.state)

    def get_transition(self, transition_id):
        return self.state["transitions"].get(transition_id)

    def prepare(self, intent):
        transition_id = intent["transition_id"]

        existing = self.get_transition(transition_id)

        if existing is not None:
            return existing

        record = {
            "transition_id": transition_id,
            "intent": deep_copy(intent),
            "intent_sha256": intent["intent_sha256"],
            "status": "PREPARED",
            "prepared_ms": utc_ms(),
            "committed_ms": None,
            "dispatched_ms": None,
            "applied_ms": None,
            "receipt": None,
        }

        self.state["transitions"][transition_id] = record
        self.state["last_transition_id"] = transition_id

        append_journal(
            "PREPARED",
            transition_id,
            {
                "intent_sha256": intent["intent_sha256"],
            },
        )

        self.persist()

        return self.get_transition(transition_id)

    def commit(self, transition_id):
        record = self.get_transition(transition_id)

        if record is None:
            raise RuntimeError("Cannot commit missing transition")

        status = record["status"]

        if status in ("COMMITTED", "DISPATCHED", "APPLIED"):
            return record

        if status != "PREPARED":
            raise RuntimeError(
                f"Invalid commit status: {status}"
            )

        record["status"] = "COMMITTED"
        record["committed_ms"] = utc_ms()

        append_journal(
            "COMMITTED",
            transition_id,
            {
                "intent_sha256": record["intent_sha256"],
            },
        )

        self.persist()

        return self.get_transition(transition_id)

    def synthetic_dispatch(self, transition_id):
        record = self.get_transition(transition_id)

        if record is None:
            raise RuntimeError("Cannot dispatch missing transition")

        if record["status"] in ("DISPATCHED", "APPLIED"):
            return record["receipt"]

        if record["status"] != "COMMITTED":
            raise RuntimeError(
                "Synthetic dispatch requires COMMITTED state"
            )

        if NETWORK_WRITES_ENABLED:
            raise RuntimeError(
                "Unsafe configuration: network writes enabled"
            )

        if not SYNTHETIC_TRANSPORT_ONLY:
            raise RuntimeError(
                "Unsafe configuration: synthetic-only transport disabled"
            )

        intent = record["intent"]

        receipt_payload = {
            "synthetic_only": True,
            "transmitted": False,
            "network_write": False,
            "version": VERSION,
            "symbol": SYMBOL,
            "transition_id": transition_id,
            "intent_sha256": intent["intent_sha256"],
            "action": intent["action"],
            "quantity": intent["quantity"],
            "time_ms": utc_ms(),
        }

        receipt_payload["receipt_sha256"] = sha256_object(
            receipt_payload
        )

        record["receipt"] = receipt_payload
        record["status"] = "DISPATCHED"
        record["dispatched_ms"] = utc_ms()

        if transition_id not in self.state["consumed_intents"]:
            self.state["consumed_intents"].append(transition_id)

        existing_receipt_ids = {
            item.get("transition_id")
            for item in self.state["dispatch_receipts"]
            if isinstance(item, dict)
        }

        if transition_id not in existing_receipt_ids:
            self.state["dispatch_receipts"].append(
                deep_copy(receipt_payload)
            )

            self.state["synthetic_dispatch_count"] += 1

        append_journal(
            "DISPATCHED",
            transition_id,
            {
                "receipt_sha256":
                    receipt_payload["receipt_sha256"],
            },
        )

        # Critical durable fencing point:
        #
        # The receipt and consumed intent are persisted before this method
        # returns. A restart after this point therefore sees DISPATCHED and
        # must never dispatch the same transition again.
        self.persist()

        return deep_copy(receipt_payload)

    def apply(self, transition_id):
        record = self.get_transition(transition_id)

        if record is None:
            raise RuntimeError("Cannot apply missing transition")

        if record["status"] == "APPLIED":
            return record

        if record["status"] != "DISPATCHED":
            raise RuntimeError(
                "Apply requires durable DISPATCHED state"
            )

        intent = record["intent"]
        transition_name = intent["transition_name"]

        self.apply_strategy_effect(transition_name)

        record["status"] = "APPLIED"
        record["applied_ms"] = utc_ms()

        append_journal(
            "APPLIED",
            transition_id,
            {
                "strategy_phase":
                    self.state["strategy_phase"],
            },
        )

        self.persist()

        return self.get_transition(transition_id)

    def apply_strategy_effect(self, transition_name):

        if transition_name == "INITIAL_ENTRY":
            if self.state["initial_entry_completed"]:
                return

            self.state["initial_entry_completed"] = True
            self.state["strategy_phase"] = "ENTRY_ACTIVE"
            return

        if transition_name == "PYRAMID_1":
            if self.state["pyramid_count"] >= MAX_PYRAMID_ADDS:
                return

            self.state["pyramid_count"] += 1
            self.state["strategy_phase"] = "PYRAMID_COMPLETE"
            return

        if transition_name.startswith("BACKUP_"):
            if self.state["backup_count"] >= MAX_BACKUPS:
                return

            self.state["backup_count"] += 1
            self.state["strategy_phase"] = "BACKUP_ACTIVE"

            if self.state["backup_count"] == MAX_BACKUPS:
                self.state["strategy_phase"] = "BACKUPS_COMPLETE"

            return

        if transition_name == "TP1":
            self.state["tp1_completed"] = True
            self.state["strategy_phase"] = "TP1_COMPLETE"
            return

        if transition_name == "TP2":
            self.state["tp2_completed"] = True
            self.state["strategy_phase"] = "TP2_COMPLETE"
            return

        if transition_name == "TRAILING_ARM":
            if (
                self.state["tp1_completed"]
                and self.state["tp2_completed"]
            ):
                self.state["trailing_armed"] = True
                self.state["strategy_phase"] = "TRAILING_ARMED"

            return

        if transition_name == "TP3":
            self.state["tp3_completed"] = True
            self.state["strategy_phase"] = "TP3_COMPLETE"
            return

        if transition_name == "TERMINAL_EXIT":
            self.state["terminal_exit_completed"] = True
            self.state["strategy_phase"] = "TERMINAL"
            return

        raise RuntimeError(
            f"Unknown strategy transition: {transition_name}"
        )

    def execute_exactly_once(self, intent):
        transition_id = intent["transition_id"]

        record = self.get_transition(transition_id)

        if record is None:
            record = self.prepare(intent)

        if record["status"] == "PREPARED":
            record = self.commit(transition_id)

        if record["status"] == "COMMITTED":
            self.synthetic_dispatch(transition_id)
            record = self.get_transition(transition_id)

        if record["status"] == "DISPATCHED":
            record = self.apply(transition_id)

        return record

    def recover_transition(self, transition_id):
        record = self.get_transition(transition_id)

        if record is None:
            raise RuntimeError(
                "Cannot recover unknown transition"
            )

        if record["status"] == "PREPARED":
            # PREPARED by itself is not considered committed authority.
            return {
                "recovered": True,
                "action": "WAIT_FOR_COMMIT",
                "dispatched": False,
                "status": "PREPARED",
            }

        if record["status"] == "COMMITTED":
            receipt = self.synthetic_dispatch(transition_id)

            self.apply(transition_id)

            return {
                "recovered": True,
                "action": "DISPATCH_AND_APPLY",
                "dispatched": True,
                "receipt": receipt,
                "status": "APPLIED",
            }

        if record["status"] == "DISPATCHED":
            self.apply(transition_id)

            return {
                "recovered": True,
                "action": "APPLY_ONLY",
                "dispatched": False,
                "status": "APPLIED",
            }

        if record["status"] == "APPLIED":
            return {
                "recovered": True,
                "action": "NOOP_ALREADY_APPLIED",
                "dispatched": False,
                "status": "APPLIED",
            }

        raise RuntimeError(
            f"Unknown recovery status: {record['status']}"
        )

    def replay_allowed(self, transition_id):
        return transition_id not in self.state["consumed_intents"]


# ==================================================================================================
# TEST HELPERS
# ==================================================================================================

def reset_test_state():
    if os.path.exists(STATE_DIR):
        shutil.rmtree(STATE_DIR)

    ensure_state_directory()


def function_rejected(function):
    try:
        function()
    except NetworkWriteRejected:
        return True
    except Exception:
        return False

    return False


def transition_receipt_is_safe(receipt):
    return (
        isinstance(receipt, dict)
        and receipt.get("synthetic_only") is True
        and receipt.get("transmitted") is False
        and receipt.get("network_write") is False
    )


def transition_status(engine, transition_id):
    record = engine.get_transition(transition_id)

    if not record:
        return None

    return record.get("status")


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def main():
    health_server = start_health_server()

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={PORT}")
    log(f"{VERSION}: STATE DIR={STATE_DIR}")
    log(f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED")
    log(f"{VERSION}: PUBLIC READ-ONLY ENABLED")
    log(f"{VERSION}: SYNTHETIC TRANSPORT ONLY")
    log(f"{VERSION}: NETWORK WRITES DISABLED")
    log(f"{VERSION}: REAL ORDERS DISABLED")
    log(f"{VERSION}: DEMO ORDERS DISABLED")

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(f"{VERSION} TEST 1: SAFETY CONSTANTS")

    assert_test(
        "Authenticated Transport Is Read Only",
        AUTHENTICATED_TRANSPORT_READ_ONLY is True,
    )

    assert_test(
        "Public Transport Is Read Only",
        PUBLIC_TRANSPORT_READ_ONLY is True,
    )

    assert_test(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    assert_test(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    assert_test(
        "Real Orders Are Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    assert_test(
        "Demo Orders Are Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    assert_test(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    assert_test(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    assert_test(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(f"{VERSION} TEST 2: API CREDENTIALS")

    assert_test(
        "WEEX API Key Is Present",
        bool(WEEX_API_KEY),
    )

    assert_test(
        "WEEX API Secret Is Present",
        bool(WEEX_API_SECRET),
    )

    assert_test(
        "WEEX API Passphrase Is Present",
        bool(WEEX_API_PASSPHRASE),
    )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(f"{VERSION} TEST 3: LIVE BALANCE")

    balance_payload = authenticated_get(BALANCE_PATH)

    available_usdt = parse_available_usdt(balance_payload)

    assert_test(
        "Available Balance Was Read",
        available_usdt is not None,
    )

    assert_test(
        "Available Balance Is Positive",
        available_usdt > 0,
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_string(available_usdt)}"
    )

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(f"{VERSION} TEST 4: LIVE ACCOUNT CONFIGURATION")

    config_payload = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    symbol_config = parse_symbol_config(config_payload)

    assert_test(
        "Symbol Configuration Was Read",
        isinstance(symbol_config, dict),
    )

    margin_type = str(
        symbol_config.get("marginType")
        or symbol_config.get("margin_type")
        or ""
    ).upper()

    long_leverage = decimal_value(
        symbol_config.get("isolatedLongLeverage")
        or symbol_config.get("isolated_long_leverage")
    )

    short_leverage = decimal_value(
        symbol_config.get("isolatedShortLeverage")
        or symbol_config.get("isolated_short_leverage")
    )

    assert_test(
        "Margin Type Is ISOLATED",
        margin_type == TARGET_MARGIN_TYPE,
    )

    assert_test(
        "Isolated Long Leverage Is 100x",
        long_leverage == TARGET_LEVERAGE,
    )

    assert_test(
        "Isolated Short Leverage Is 100x",
        short_leverage == TARGET_LEVERAGE,
    )

    log(
        f"{VERSION}: SYMBOL CONFIG="
        f"{canonical_json(symbol_config)}"
    )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(f"{VERSION} TEST 5: LIVE POSITION STATE")

    position_payload = authenticated_get(POSITION_PATH)

    positions = parse_positions(position_payload)

    btc_positions = [
        item
        for item in positions
        if position_symbol(item) == SYMBOL
    ]

    open_btc_positions = [
        item
        for item in btc_positions
        if position_size(item) > 0
    ]

    assert_test(
        "Position Endpoint Was Read",
        position_payload is not None,
    )

    assert_test(
        "Position Records Were Parsed",
        isinstance(positions, list),
    )

    log(f"{VERSION}: POSITION ENDPOINT={POSITION_PATH}")
    log(f"{VERSION}: TOTAL POSITION RECORDS={len(positions)}")
    log(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(btc_positions)}"
    )
    log(
        f"{VERSION}: {SYMBOL} OPEN POSITIONS="
        f"{len(open_btc_positions)}"
    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(f"{VERSION} TEST 6: LIVE MARKET PRICE")

    market_payload = public_get(
        MARKET_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    market_price = parse_market_price(market_payload)

    assert_test(
        "Market Price Was Read",
        market_price is not None,
    )

    assert_test(
        "Market Price Is Positive",
        market_price > 0,
    )

    log(f"{VERSION}: MARKET PRICE PATH={MARKET_PRICE_PATH}")
    log(
        f"{VERSION}: MARK PRICE="
        f"{decimal_string(market_price)}"
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(f"{VERSION} TEST 7: LIVE CONTRACT INFORMATION")

    exchange_payload = public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    contract_info = parse_contract_information(
        exchange_payload
    )

    min_qty = contract_info["min_qty"]
    qty_step = contract_info["qty_step"]
    price_step = contract_info["price_step"]

    assert_test(
        "Exchange Information Was Read",
        exchange_payload is not None,
    )

    assert_test(
        "Minimum Quantity Is Positive",
        min_qty > 0,
    )

    assert_test(
        "Quantity Step Is Positive",
        qty_step > 0,
    )

    assert_test(
        "Price Step Is Positive",
        price_step > 0,
    )

    log(f"{VERSION}: MIN QTY={decimal_string(min_qty)}")
    log(f"{VERSION}: QTY STEP={decimal_string(qty_step)}")
    log(f"{VERSION}: PRICE STEP={decimal_string(price_step)}")

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(f"{VERSION} TEST 8: STRATEGY BUDGET")

    initial_entry_margin_budget = (
        available_usdt
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    planned_notional = (
        initial_entry_margin_budget
        * TARGET_LEVERAGE
    )

    raw_qty = planned_notional / market_price

    normalized_qty = normalize_quantity_down(
        raw_qty,
        qty_step,
    )

    normalized_notional = normalized_qty * market_price

    normalized_margin = (
        normalized_notional
        / TARGET_LEVERAGE
    )

    planned_max_strategy_margin = (
        available_usdt
        * (
            INITIAL_ENTRY_PERCENT
            + PYRAMID_SIZE_PERCENT
            * Decimal(MAX_PYRAMID_ADDS)
            + BACKUP_SIZE_PERCENT
            * Decimal(MAX_BACKUPS)
        )
        / Decimal("100")
    )

    max_allowed_strategy_margin = (
        available_usdt
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    assert_test(
        "Initial Entry Margin Budget Is Positive",
        initial_entry_margin_budget > 0,
    )

    assert_test(
        "Normalized Quantity Is Positive",
        normalized_qty > 0,
    )

    assert_test(
        "Normalized Quantity Meets Minimum",
        normalized_qty >= min_qty,
    )

    assert_test(
        "Normalized Margin Does Not Exceed 5% Entry Budget",
        normalized_margin <= initial_entry_margin_budget,
    )

    assert_test(
        "Planned Maximum Strategy Margin Is Within 35%",
        planned_max_strategy_margin
        <= max_allowed_strategy_margin,
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_string(initial_entry_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: RAW QTY="
        f"{decimal_string(raw_qty)} BTC"
    )

    log(
        f"{VERSION}: NORMALIZED QTY="
        f"{decimal_string(normalized_qty)} BTC"
    )

    log(
        f"{VERSION}: NORMALIZED MARGIN="
        f"{decimal_string(normalized_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_string(planned_max_strategy_margin)} USDT"
    )

    # ==============================================================================================
    # RESET R35A LOCAL DIAGNOSTIC STATE
    # ==============================================================================================

    reset_test_state()

    engine = DurableTransitionEngine()

    engine.persist()

    # ==============================================================================================
    # TEST 9 - DURABLE PREPARE CRASH WINDOW
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: DURABLE PREPARE CRASH WINDOW"
    )

    initial_intent = create_transition_intent(
        transition_name="INITIAL_ENTRY",
        action="OPEN_LONG_SYNTHETIC",
        quantity=normalized_qty,
        metadata={
            "entry_margin_percent":
                decimal_string(INITIAL_ENTRY_PERCENT),
            "leverage":
                decimal_string(TARGET_LEVERAGE),
            "margin_type":
                TARGET_MARGIN_TYPE,
            "market_price":
                decimal_string(market_price),
        },
    )

    initial_id = initial_intent["transition_id"]

    engine.prepare(initial_intent)

    assert_test(
        "Initial Transition Was Durably Prepared",
        transition_status(engine, initial_id)
        == "PREPARED",
    )

    dispatch_count_before_restart = (
        engine.state["synthetic_dispatch_count"]
    )

    engine = DurableTransitionEngine.restore()

    assert_test(
        "Prepared Transition Survived Restart",
        transition_status(engine, initial_id)
        == "PREPARED",
    )

    recovery = engine.recover_transition(initial_id)

    assert_test(
        "Prepared-Only Recovery Did Not Dispatch",
        recovery["dispatched"] is False,
    )

    assert_test(
        "Prepared-Only Recovery Preserved Dispatch Count",
        engine.state["synthetic_dispatch_count"]
        == dispatch_count_before_restart,
    )

    # ==============================================================================================
    # TEST 10 - COMMIT CRASH WINDOW
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: DURABLE COMMIT CRASH WINDOW"
    )

    engine.commit(initial_id)

    assert_test(
        "Initial Transition Was Durably Committed",
        transition_status(engine, initial_id)
        == "COMMITTED",
    )

    engine = DurableTransitionEngine.restore()

    assert_test(
        "Committed Transition Survived Restart",
        transition_status(engine, initial_id)
        == "COMMITTED",
    )

    recovery = engine.recover_transition(initial_id)

    assert_test(
        "Committed Recovery Performed Synthetic Dispatch",
        recovery["dispatched"] is True,
    )

    assert_test(
        "Recovered Initial Transition Was Applied",
        transition_status(engine, initial_id)
        == "APPLIED",
    )

    assert_test(
        "Initial Entry State Is Completed",
        engine.state["initial_entry_completed"] is True,
    )

    assert_test(
        "Exactly One Synthetic Dispatch Exists",
        engine.state["synthetic_dispatch_count"] == 1,
    )

    # ==============================================================================================
    # TEST 11 - INITIAL REPLAY FENCE
    # ==============================================================================================

    section(f"{VERSION} TEST 11: INITIAL REPLAY FENCE")

    count_before_replay = engine.state[
        "synthetic_dispatch_count"
    ]

    engine.execute_exactly_once(initial_intent)

    assert_test(
        "Consumed Initial Intent Is Recorded",
        initial_id in engine.state["consumed_intents"],
    )

    assert_test(
        "Initial Replay Produced No Additional Dispatch",
        engine.state["synthetic_dispatch_count"]
        == count_before_replay,
    )

    assert_test(
        "Initial Transition Remains Applied",
        transition_status(engine, initial_id)
        == "APPLIED",
    )

    # ==============================================================================================
    # TEST 12 - PYRAMID EXACTLY ONCE
    # ==============================================================================================

    section(f"{VERSION} TEST 12: PYRAMID EXACTLY-ONCE")

    pyramid_intent = create_transition_intent(
        transition_name="PYRAMID_1",
        action="ADD_LONG_SYNTHETIC",
        quantity=normalized_qty,
        metadata={
            "size_percent":
                decimal_string(PYRAMID_SIZE_PERCENT),
        },
    )

    pyramid_id = pyramid_intent["transition_id"]

    engine.execute_exactly_once(pyramid_intent)

    pyramid_dispatch_count = engine.state[
        "synthetic_dispatch_count"
    ]

    assert_test(
        "Pyramid Transition Is Applied",
        transition_status(engine, pyramid_id)
        == "APPLIED",
    )

    assert_test(
        "Pyramid Count Is One",
        engine.state["pyramid_count"] == 1,
    )

    engine.execute_exactly_once(pyramid_intent)

    assert_test(
        "Pyramid Replay Produced No Additional Dispatch",
        engine.state["synthetic_dispatch_count"]
        == pyramid_dispatch_count,
    )

    assert_test(
        "Pyramid Count Remains One",
        engine.state["pyramid_count"] == 1,
    )

    # ==============================================================================================
    # TEST 13 - BACKUP 1 EXACTLY ONCE
    # ==============================================================================================

    section(f"{VERSION} TEST 13: BACKUP 1 EXACTLY-ONCE")

    backup1 = create_transition_intent(
        "BACKUP_1",
        "BACKUP_LONG_SYNTHETIC",
        normalized_qty,
        {
            "backup_number": 1,
            "size_percent":
                decimal_string(BACKUP_SIZE_PERCENT),
        },
    )

    engine.execute_exactly_once(backup1)

    backup1_count = engine.state[
        "synthetic_dispatch_count"
    ]

    engine.execute_exactly_once(backup1)

    assert_test(
        "Backup 1 Is Applied",
        transition_status(
            engine,
            backup1["transition_id"],
        ) == "APPLIED",
    )

    assert_test(
        "Backup Count Is One",
        engine.state["backup_count"] == 1,
    )

    assert_test(
        "Backup 1 Replay Produced No Additional Dispatch",
        engine.state["synthetic_dispatch_count"]
        == backup1_count,
    )

    # ==============================================================================================
    # TEST 14 - BACKUP 2 RESTART EXACTLY ONCE
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: BACKUP 2 RESTART EXACTLY-ONCE"
    )

    backup2 = create_transition_intent(
        "BACKUP_2",
        "BACKUP_LONG_SYNTHETIC",
        normalized_qty,
        {
            "backup_number": 2,
            "size_percent":
                decimal_string(BACKUP_SIZE_PERCENT),
        },
    )

    backup2_id = backup2["transition_id"]

    engine.prepare(backup2)
    engine.commit(backup2_id)
    engine.synthetic_dispatch(backup2_id)

    count_after_backup2_dispatch = engine.state[
        "synthetic_dispatch_count"
    ]

    assert_test(
        "Backup 2 Durable Receipt Exists Before Restart",
        transition_status(engine, backup2_id)
        == "DISPATCHED",
    )

    engine = DurableTransitionEngine.restore()

    recovery = engine.recover_transition(backup2_id)

    assert_test(
        "Backup 2 Recovery Used Apply-Only Path",
        recovery["action"] == "APPLY_ONLY",
    )

    assert_test(
        "Backup 2 Recovery Did Not Redispatch",
        recovery["dispatched"] is False,
    )

    assert_test(
        "Backup 2 Dispatch Count Remained Stable",
        engine.state["synthetic_dispatch_count"]
        == count_after_backup2_dispatch,
    )

    assert_test(
        "Backup Count Is Two",
        engine.state["backup_count"] == 2,
    )

    # ==============================================================================================
    # TEST 15 - BACKUP 3 EXACTLY ONCE
    # ==============================================================================================

    section(f"{VERSION} TEST 15: BACKUP 3 EXACTLY-ONCE")

    backup3 = create_transition_intent(
        "BACKUP_3",
        "BACKUP_LONG_SYNTHETIC",
        normalized_qty,
        {
            "backup_number": 3,
            "size_percent":
                decimal_string(BACKUP_SIZE_PERCENT),
        },
    )

    engine.execute_exactly_once(backup3)

    backup3_dispatch_count = engine.state[
        "synthetic_dispatch_count"
    ]

    engine.execute_exactly_once(backup3)

    assert_test(
        "Backup 3 Is Applied",
        transition_status(
            engine,
            backup3["transition_id"],
        ) == "APPLIED",
    )

    assert_test(
        "Backup Count Is Three",
        engine.state["backup_count"] == 3,
    )

    assert_test(
        "Backup 3 Replay Produced No Additional Dispatch",
        engine.state["synthetic_dispatch_count"]
        == backup3_dispatch_count,
    )

    # ==============================================================================================
    # TEST 16 - TP1 EXACTLY ONCE
    # ==============================================================================================

    section(f"{VERSION} TEST 16: TP1 EXACTLY-ONCE")

    tp1_quantity = normalize_quantity_down(
        normalized_qty
        * TP1_SHARE_PERCENT
        / Decimal("100"),
        qty_step,
    )

    if tp1_quantity <= 0:
        tp1_quantity = min_qty

    tp1 = create_transition_intent(
        "TP1",
        "REDUCE_LONG_SYNTHETIC",
        tp1_quantity,
        {
            "share_percent":
                decimal_string(TP1_SHARE_PERCENT),
            "trigger_percent":
                decimal_string(TP1_TRIGGER_PERCENT),
        },
    )

    engine.execute_exactly_once(tp1)

    tp1_dispatch_count = engine.state[
        "synthetic_dispatch_count"
    ]

    engine.execute_exactly_once(tp1)

    assert_test(
        "TP1 Is Applied",
        transition_status(
            engine,
            tp1["transition_id"],
        ) == "APPLIED",
    )

    assert_test(
        "TP1 State Is Completed",
        engine.state["tp1_completed"] is True,
    )

    assert_test(
        "TP1 Replay Produced No Additional Dispatch",
        engine.state["synthetic_dispatch_count"]
        == tp1_dispatch_count,
    )

    # ==============================================================================================
    # TEST 17 - TP2 CRASH AFTER COMMIT
    # ==============================================================================================

    section(
        f"{VERSION} TEST 17: TP2 COMMIT CRASH RECOVERY"
    )

    tp2_quantity = normalize_quantity_down(
        normalized_qty
        * TP2_SHARE_PERCENT
        / Decimal("100"),
        qty_step,
    )

    if tp2_quantity <= 0:
        tp2_quantity = min_qty

    tp2 = create_transition_intent(
        "TP2",
        "REDUCE_LONG_SYNTHETIC",
        tp2_quantity,
        {
            "share_percent":
                decimal_string(TP2_SHARE_PERCENT),
            "trigger_percent":
                decimal_string(TP2_TRIGGER_PERCENT),
        },
    )

    tp2_id = tp2["transition_id"]

    engine.prepare(tp2)
    engine.commit(tp2_id)

    count_before_tp2_recovery = engine.state[
        "synthetic_dispatch_count"
    ]

    engine = DurableTransitionEngine.restore()

    tp2_recovery = engine.recover_transition(tp2_id)

    assert_test(
        "TP2 Recovery Dispatched From Durable Commit",
        tp2_recovery["dispatched"] is True,
    )

    assert_test(
        "TP2 Added Exactly One Dispatch",
        engine.state["synthetic_dispatch_count"]
        == count_before_tp2_recovery + 1,
    )

    assert_test(
        "TP2 State Is Completed",
        engine.state["tp2_completed"] is True,
    )

    # ==============================================================================================
    # TEST 18 - TRAILING ARM
    # ==============================================================================================

    section(f"{VERSION} TEST 18: DURABLE TRAILING ARM")

    trailing_reference = (
        market_price
        * (
            Decimal("1")
            + TP2_TRIGGER_PERCENT / Decimal("100")
        )
    )

    trailing_intent = create_transition_intent(
        "TRAILING_ARM",
        "ARM_TRAILING_SYNTHETIC",
        Decimal("0"),
        {
            "trailing_distance_percent":
                decimal_string(
                    TRAILING_DISTANCE_PERCENT
                ),
            "reference_price":
                decimal_string(trailing_reference),
        },
    )

    engine.execute_exactly_once(trailing_intent)

    trailing_dispatch_count = engine.state[
        "synthetic_dispatch_count"
    ]

    engine.execute_exactly_once(trailing_intent)

    assert_test(
        "Trailing Arm Transition Is Applied",
        transition_status(
            engine,
            trailing_intent["transition_id"],
        ) == "APPLIED",
    )

    assert_test(
        "Trailing Is Armed",
        engine.state["trailing_armed"] is True,
    )

    assert_test(
        "Trailing Replay Produced No Additional Dispatch",
        engine.state["synthetic_dispatch_count"]
        == trailing_dispatch_count,
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{decimal_string(TRAILING_DISTANCE_PERCENT)}%"
    )

    log(
        f"{VERSION}: TRAILING REFERENCE="
        f"{decimal_string(trailing_reference)}"
    )

    # ==============================================================================================
    # TEST 19 - TP3 DISPATCH/APPLY CRASH WINDOW
    # ==============================================================================================

    section(
        f"{VERSION} TEST 19: TP3 DISPATCH/APPLY CRASH WINDOW"
    )

    tp3_quantity = normalize_quantity_down(
        normalized_qty
        * TP3_SHARE_PERCENT
        / Decimal("100"),
        qty_step,
    )

    if tp3_quantity <= 0:
        tp3_quantity = min_qty

    tp3 = create_transition_intent(
        "TP3",
        "REDUCE_LONG_SYNTHETIC",
        tp3_quantity,
        {
            "share_percent":
                decimal_string(TP3_SHARE_PERCENT),
            "trailing_distance_percent":
                decimal_string(
                    TRAILING_DISTANCE_PERCENT
                ),
        },
    )

    tp3_id = tp3["transition_id"]

    engine.prepare(tp3)
    engine.commit(tp3_id)

    tp3_receipt = engine.synthetic_dispatch(tp3_id)

    dispatch_count_before_tp3_restart = engine.state[
        "synthetic_dispatch_count"
    ]

    assert_test(
        "TP3 Synthetic Receipt Is Safe",
        transition_receipt_is_safe(tp3_receipt),
    )

    assert_test(
        "TP3 Is Durable DISPATCHED Before Crash",
        transition_status(engine, tp3_id)
        == "DISPATCHED",
    )

    engine = DurableTransitionEngine.restore()

    tp3_recovery = engine.recover_transition(tp3_id)

    assert_test(
        "TP3 Recovery Used Apply-Only Path",
        tp3_recovery["action"] == "APPLY_ONLY",
    )

    assert_test(
        "TP3 Was Not Redispatched After Restart",
        engine.state["synthetic_dispatch_count"]
        == dispatch_count_before_tp3_restart,
    )

    assert_test(
        "TP3 State Is Completed",
        engine.state["tp3_completed"] is True,
    )

    # ==============================================================================================
    # TEST 20 - TERMINAL EXIT
    # ==============================================================================================

    section(
        f"{VERSION} TEST 20: TERMINAL EXIT EXACTLY-ONCE"
    )

    terminal_intent = create_transition_intent(
        "TERMINAL_EXIT",
        "CLOSE_REMAINDER_SYNTHETIC",
        normalized_qty,
        {
            "reason":
                "SYNTHETIC_STRATEGY_COMPLETION",
        },
    )

    engine.execute_exactly_once(terminal_intent)

    terminal_count = engine.state[
        "synthetic_dispatch_count"
    ]

    engine.execute_exactly_once(terminal_intent)

    assert_test(
        "Terminal Exit Transition Is Applied",
        transition_status(
            engine,
            terminal_intent["transition_id"],
        ) == "APPLIED",
    )

    assert_test(
        "Terminal Exit State Is Completed",
        engine.state[
            "terminal_exit_completed"
        ] is True,
    )

    assert_test(
        "Final Strategy Phase Is Terminal",
        engine.state["strategy_phase"] == "TERMINAL",
    )

    assert_test(
        "Terminal Replay Produced No Additional Dispatch",
        engine.state["synthetic_dispatch_count"]
        == terminal_count,
    )

    # ==============================================================================================
    # TEST 21 - COMPLETE LIFECYCLE
    # ==============================================================================================

    section(f"{VERSION} TEST 21: COMPLETE LIFECYCLE")

    assert_test(
        "Initial Entry Completed",
        engine.state["initial_entry_completed"] is True,
    )

    assert_test(
        "Exactly One Pyramid Completed",
        engine.state["pyramid_count"]
        == MAX_PYRAMID_ADDS,
    )

    assert_test(
        "Exactly Three Backups Completed",
        engine.state["backup_count"]
        == MAX_BACKUPS,
    )

    assert_test(
        "TP1 Completed",
        engine.state["tp1_completed"] is True,
    )

    assert_test(
        "TP2 Completed",
        engine.state["tp2_completed"] is True,
    )

    assert_test(
        "Trailing Was Armed",
        engine.state["trailing_armed"] is True,
    )

    assert_test(
        "TP3 Completed",
        engine.state["tp3_completed"] is True,
    )

    assert_test(
        "Terminal Exit Completed",
        engine.state[
            "terminal_exit_completed"
        ] is True,
    )

    assert_test(
        "Network Write Count Is Zero",
        engine.state["network_write_count"] == 0,
    )

    # ==============================================================================================
    # TEST 22 - RECEIPT UNIQUENESS
    # ==============================================================================================

    section(
        f"{VERSION} TEST 22: DURABLE RECEIPT UNIQUENESS"
    )

    receipts = engine.state["dispatch_receipts"]

    receipt_ids = [
        receipt["transition_id"]
        for receipt in receipts
    ]

    assert_test(
        "Dispatch Receipts Exist",
        len(receipts) > 0,
    )

    assert_test(
        "Every Receipt Transition ID Is Unique",
        len(receipt_ids) == len(set(receipt_ids)),
    )

    assert_test(
        "Dispatch Counter Matches Durable Receipts",
        engine.state["synthetic_dispatch_count"]
        == len(receipts),
    )

    assert_test(
        "Every Receipt Is Synthetic Only",
        all(
            receipt.get("synthetic_only") is True
            for receipt in receipts
        ),
    )

    assert_test(
        "No Receipt Was Transmitted",
        all(
            receipt.get("transmitted") is False
            for receipt in receipts
        ),
    )

    assert_test(
        "No Receipt Made Network Write",
        all(
            receipt.get("network_write") is False
            for receipt in receipts
        ),
    )

    # ==============================================================================================
    # TEST 23 - SNAPSHOT RESTART
    # ==============================================================================================

    section(f"{VERSION} TEST 23: TERMINAL RESTART RESTORE")

    final_dispatch_count = engine.state[
        "synthetic_dispatch_count"
    ]

    final_consumed_count = len(
        engine.state["consumed_intents"]
    )

    final_receipt_count = len(
        engine.state["dispatch_receipts"]
    )

    restored_engine = DurableTransitionEngine.restore()

    assert_test(
        "Restart State Was Restored",
        isinstance(restored_engine.state, dict),
    )

    assert_test(
        "Restart Snapshot Integrity Is Valid",
        snapshot_integrity_valid(
            restored_engine.state
        ),
    )

    assert_test(
        "Terminal State Survived Restart",
        restored_engine.state["strategy_phase"]
        == "TERMINAL",
    )

    assert_test(
        "Dispatch Count Survived Restart",
        restored_engine.state[
            "synthetic_dispatch_count"
        ] == final_dispatch_count,
    )

    assert_test(
        "Consumed Intents Survived Restart",
        len(restored_engine.state["consumed_intents"])
        == final_consumed_count,
    )

    assert_test(
        "Dispatch Receipts Survived Restart",
        len(restored_engine.state["dispatch_receipts"])
        == final_receipt_count,
    )

    engine = restored_engine

    # ==============================================================================================
    # TEST 24 - TERMINAL REPLAY SWEEP
    # ==============================================================================================

    section(f"{VERSION} TEST 24: TERMINAL REPLAY SWEEP")

    all_original_intents = [
        initial_intent,
        pyramid_intent,
        backup1,
        backup2,
        backup3,
        tp1,
        tp2,
        trailing_intent,
        tp3,
        terminal_intent,
    ]

    before_replay_sweep = engine.state[
        "synthetic_dispatch_count"
    ]

    for intent in all_original_intents:
        engine.execute_exactly_once(intent)

    assert_test(
        "All Consumed Intents Reject Duplicate Dispatch",
        engine.state["synthetic_dispatch_count"]
        == before_replay_sweep,
    )

    assert_test(
        "Replay Sweep Preserved Terminal Phase",
        engine.state["strategy_phase"] == "TERMINAL",
    )

    assert_test(
        "Replay Sweep Preserved Pyramid Count",
        engine.state["pyramid_count"] == 1,
    )

    assert_test(
        "Replay Sweep Preserved Backup Count",
        engine.state["backup_count"] == 3,
    )

    # ==============================================================================================
    # TEST 25 - JOURNAL HASH CHAIN
    # ==============================================================================================

    section(f"{VERSION} TEST 25: JOURNAL HASH CHAIN")

    records = journal_records()

    assert_test(
        "Transition Journal Exists",
        os.path.exists(JOURNAL_FILE),
    )

    assert_test(
        "Transition Journal Contains Records",
        len(records) > 0,
    )

    assert_test(
        "Journal Hash Chain Is Valid",
        validate_journal() is True,
    )

    assert_test(
        "Journal Begins From Genesis",
        records[0].get("previous_sha256")
        == "GENESIS",
    )

    assert_test(
        "Journal Final Record Has SHA256",
        bool(records[-1].get("record_sha256")),
    )

    log(
        f"{VERSION}: JOURNAL RECORDS={len(records)}"
    )

    log(
        f"{VERSION}: JOURNAL FILE={JOURNAL_FILE}"
    )

    # ==============================================================================================
    # TEST 26 - SNAPSHOT TAMPER REJECTION
    # ==============================================================================================

    section(
        f"{VERSION} TEST 26: SNAPSHOT TAMPER REJECTION"
    )

    good_state = load_snapshot()

    tampered_state = deep_copy(good_state)

    tampered_state["backup_count"] = 999

    assert_test(
        "Tampered Snapshot Fails Integrity Validation",
        snapshot_integrity_valid(tampered_state)
        is False,
    )

    assert_test(
        "Untampered Snapshot Retains Valid Integrity",
        snapshot_integrity_valid(good_state)
        is True,
    )

    # ==============================================================================================
    # TEST 27 - COMMITTED TRANSITION SINGLE-WINNER RECOVERY
    # ==============================================================================================

    section(
        f"{VERSION} TEST 27: SINGLE-WINNER RECOVERY FENCE"
    )

    # Create a completely separate synthetic test transition.
    # It has no exchange-writing capability.
    recovery_probe = create_transition_intent(
        "RECOVERY_PROBE",
        "LOCAL_SYNTHETIC_PROBE",
        Decimal("0"),
        {
            "purpose":
                "single-winner recovery validation",
        },
    )

    probe_id = recovery_probe["transition_id"]

    engine.prepare(recovery_probe)
    engine.commit(probe_id)

    before_probe_dispatch = engine.state[
        "synthetic_dispatch_count"
    ]

    # First recovery instance.
    recovery_engine_one = DurableTransitionEngine.restore()

    receipt_one = recovery_engine_one.synthetic_dispatch(
        probe_id
    )

    after_first_probe_dispatch = recovery_engine_one.state[
        "synthetic_dispatch_count"
    ]

    # Second recovery instance starts only after durable receipt was written.
    recovery_engine_two = DurableTransitionEngine.restore()

    receipt_two = recovery_engine_two.synthetic_dispatch(
        probe_id
    )

    after_second_probe_dispatch = recovery_engine_two.state[
        "synthetic_dispatch_count"
    ]

    assert_test(
        "First Recovery Produced One Synthetic Dispatch",
        after_first_probe_dispatch
        == before_probe_dispatch + 1,
    )

    assert_test(
        "Second Recovery Produced No Additional Dispatch",
        after_second_probe_dispatch
        == after_first_probe_dispatch,
    )

    assert_test(
        "Both Recovery Attempts Resolve Same Receipt",
        receipt_one.get("receipt_sha256")
        == receipt_two.get("receipt_sha256"),
    )

    assert_test(
        "Recovery Probe Receipt Is Synthetic Only",
        transition_receipt_is_safe(receipt_two),
    )

    # Do not apply RECOVERY_PROBE because it is not a strategy mutation.
    # The durability test is specifically about the dispatch fence.

    engine = recovery_engine_two

    # ==============================================================================================
    # TEST 28 - WRITE FIREBREAK
    # ==============================================================================================

    section(f"{VERSION} TEST 28: WRITE FIREBREAK")

    assert_test(
        "HTTP POST Is Rejected",
        function_rejected(http_post),
    )

    assert_test(
        "HTTP PUT Is Rejected",
        function_rejected(http_put),
    )

    assert_test(
        "HTTP PATCH Is Rejected",
        function_rejected(http_patch),
    )

    assert_test(
        "HTTP DELETE Is Rejected",
        function_rejected(http_delete),
    )

    assert_test(
        "Generic Network Write Is Rejected",
        function_rejected(generic_network_write),
    )

    assert_test(
        "Real Order Function Is Rejected",
        function_rejected(place_real_order),
    )

    assert_test(
        "Demo Order Function Is Rejected",
        function_rejected(place_demo_order),
    )

    assert_test(
        "Leverage Mutation Function Is Rejected",
        function_rejected(mutate_leverage),
    )

    assert_test(
        "Margin Mutation Function Is Rejected",
        function_rejected(mutate_margin_type),
    )

    assert_test(
        "Position Mutation Function Is Rejected",
        function_rejected(mutate_position),
    )

    # ==============================================================================================
    # TEST 29 - FINAL SAFETY INVARIANTS
    # ==============================================================================================

    section(f"{VERSION} TEST 29: FINAL SAFETY INVARIANTS")

    assert_test(
        "Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    assert_test(
        "Synthetic Transport Remains Mandatory",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    assert_test(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    assert_test(
        "Demo Order Execution Remains Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    assert_test(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    assert_test(
        "Margin Mutation Remains Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    assert_test(
        "Position Mutation Remains Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    assert_test(
        "Durable Journal Remains Valid",
        validate_journal() is True,
    )

    final_state = load_snapshot()

    assert_test(
        "Final Snapshot Integrity Is Valid",
        snapshot_integrity_valid(final_state),
    )

    assert_test(
        "Strategy Remains Terminal",
        final_state["strategy_phase"]
        == "TERMINAL",
    )

    assert_test(
        "Strategy Network Write Count Is Zero",
        final_state["network_write_count"] == 0,
    )

    # ==============================================================================================
    # FINAL SUMMARY
    # ==============================================================================================

    section(f"{VERSION}: VALIDATION SUMMARY")

    log(
        f"{VERSION}: LIVE BALANCE READ="
        f"{decimal_string(available_usdt)} USDT"
    )

    log(
        f"{VERSION}: LIVE MARK PRICE="
        f"{decimal_string(market_price)}"
    )

    log(
        f"{VERSION}: MARGIN TYPE="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: ISOLATED LONG LEVERAGE="
        f"{decimal_string(long_leverage)}x"
    )

    log(
        f"{VERSION}: ISOLATED SHORT LEVERAGE="
        f"{decimal_string(short_leverage)}x"
    )

    log(
        f"{VERSION}: NORMALIZED ENTRY QUANTITY="
        f"{decimal_string(normalized_qty)} BTC"
    )

    log(
        f"{VERSION}: INITIAL ENTRY MARGIN="
        f"{decimal_string(normalized_margin)} USDT"
    )

    log(
        f"{VERSION}: FINAL STRATEGY PHASE="
        f"{final_state['strategy_phase']}"
    )

    log(
        f"{VERSION}: PYRAMID COUNT="
        f"{final_state['pyramid_count']}"
    )

    log(
        f"{VERSION}: BACKUP COUNT="
        f"{final_state['backup_count']}"
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCH COUNT="
        f"{final_state['synthetic_dispatch_count']}"
    )

    log(
        f"{VERSION}: DURABLE RECEIPTS="
        f"{len(final_state['dispatch_receipts'])}"
    )

    log(
        f"{VERSION}: CONSUMED INTENTS="
        f"{len(final_state['consumed_intents'])}"
    )

    log(
        f"{VERSION}: NETWORK WRITE COUNT="
        f"{final_state['network_write_count']}"
    )

    log(
        f"{VERSION}: STATE FILE="
        f"{STATE_FILE}"
    )

    log(
        f"{VERSION}: JOURNAL FILE="
        f"{JOURNAL_FILE}"
    )

    section(f"{VERSION}: FINAL RESULT")

    log(
        f"{VERSION}: DURABLE EXACTLY-ONCE "
        f"SYNTHETIC LIFECYCLE VALIDATION PASSED"
    )

    log(
        f"{VERSION}: PREPARE / COMMIT / DISPATCH / "
        f"APPLY FENCING VERIFIED"
    )

    log(
        f"{VERSION}: CRASH-WINDOW RECOVERY VERIFIED"
    )

    log(
        f"{VERSION}: RESTART REPLAY REJECTION VERIFIED"
    )

    log(
        f"{VERSION}: DURABLE RECEIPT UNIQUENESS VERIFIED"
    )

    log(
        f"{VERSION}: SNAPSHOT INTEGRITY VERIFIED"
    )

    log(
        f"{VERSION}: JOURNAL HASH CHAIN VERIFIED"
    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO DEMO ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO NETWORK WRITE WAS PERFORMED"
    )

    log(
        f"{VERSION}: NO LEVERAGE MUTATION WAS PERFORMED"
    )

    log(
        f"{VERSION}: NO MARGIN MUTATION WAS PERFORMED"
    )

    log(
        f"{VERSION}: NO POSITION MUTATION WAS PERFORMED"
    )

    log(LINE)

    # Keep Render service alive after validation.
    heartbeat = 0

    while True:
        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"STATUS=PASSED | "
            f"SYNTHETIC_ONLY=TRUE | "
            f"NETWORK_WRITES=0"
        )

        time.sleep(60)


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        log(f"{VERSION}: STOPPED")

    except Exception as exc:
        section(f"{VERSION}: FATAL ERROR")

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        log(
            f"{VERSION}: SAFETY STATUS="
            f"NETWORK WRITES REMAIN DISABLED"
        )

        # Keep Render alive so the failure remains visible
        # instead of creating a rapid restart loop.
        heartbeat = 0

        while True:
            heartbeat += 1

            log(
                f"{VERSION}: FAILURE HEARTBEAT "
                f"{heartbeat} | "
                f"NETWORK_WRITES=0"
            )

            time.sleep(60)



