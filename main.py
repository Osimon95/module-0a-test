# ==================================================================================================
# R35A - DURABLE EXACTLY-ONCE SYNTHETIC STRATEGY LIFECYCLE VALIDATION
# PART 1/4
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
        server = ThreadingHTTPServer(
            ("0.0.0.0", PORT),
            HealthHandler,
        )

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
        raise RuntimeError(
            "Public read-only transport is disabled"
        )

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


def create_auth_signature(
    timestamp,
    method,
    path,
    query="",
):
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

    return base64.b64encode(
        digest
    ).decode("utf-8")


def authenticated_get(path, params=None):
    if not AUTHENTICATED_TRANSPORT_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only transport disabled"
        )

    if not WEEX_API_KEY:
        raise RuntimeError(
            "WEEX API key is missing"
        )

    if not WEEX_API_SECRET:
        raise RuntimeError(
            "WEEX API secret is missing"
        )

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError(
            "WEEX API passphrase is missing"
        )

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
# END OF R35A PART 1/4
# NEXT: PART 2/4 STARTS WITH RESPONSE UNWRAPPING AND LIVE RESPONSE PARSERS
# ==================================================================================================
# ==================================================================================================
# R35A - DURABLE EXACTLY-ONCE SYNTHETIC STRATEGY LIFECYCLE VALIDATION
# PART 2/4
# ==================================================================================================
#
# CONTINUES DIRECTLY FROM PART 1/4
#
# ==================================================================================================


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
                amount = decimal_value(
                    record.get(key)
                )

                if amount >= 0:
                    return amount

    raise RuntimeError(
        f"Unable to parse available USDT "
        f"from balance response: {payload}"
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

    if (
        len(records) == 1
        and isinstance(records[0], dict)
    ):
        return records[0]

    raise RuntimeError(
        f"Unable to locate {SYMBOL} "
        f"symbol configuration"
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
            return abs(
                decimal_value(
                    record.get(key)
                )
            )

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

        record_symbol = str(
            record.get("symbol")
            or ""
        ).upper()

        if (
            record_symbol
            and record_symbol != SYMBOL
        ):
            continue

        for key in (
            "price",
            "markPrice",
            "indexPrice",
            "last",
            "lastPrice",
        ):
            if key in record:
                price = decimal_value(
                    record.get(key)
                )

                if price > 0:
                    return price

    raise RuntimeError(
        f"Unable to parse market price "
        f"from response: {payload}"
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
        if isinstance(
            root.get("symbols"),
            list,
        ):
            candidates.extend(
                root["symbols"]
            )

        if isinstance(
            root.get("contracts"),
            list,
        ):
            candidates.extend(
                root["contracts"]
            )

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
        f"Unable to locate {SYMBOL} "
        f"in exchange information"
    )


def first_positive_decimal(
    record,
    keys,
    default=None,
):
    for key in keys:
        if key not in record:
            continue

        value = decimal_value(
            record.get(key)
        )

        if value > 0:
            return value

    if default is not None:
        return Decimal(
            str(default)
        )

    raise RuntimeError(
        f"Unable to locate positive decimal "
        f"from keys: {keys}"
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

def normalize_quantity_down(
    raw_qty,
    qty_step,
):
    raw_qty = Decimal(
        raw_qty
    )

    qty_step = Decimal(
        qty_step
    )

    if raw_qty <= 0:
        return Decimal("0")

    if qty_step <= 0:
        raise ValueError(
            "Quantity step must be positive"
        )

    units = (
        raw_qty
        / qty_step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        units
        * qty_step
    )


# ==================================================================================================
# DURABLE FILE HELPERS
# ==================================================================================================

def ensure_state_directory():
    os.makedirs(
        STATE_DIR,
        exist_ok=True,
    )


def atomic_write_text(
    path,
    text,
):
    ensure_state_directory()

    temp_path = (
        path
        + ".tmp."
        + str(os.getpid())
        + "."
        + str(time.time_ns())
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(text)
        handle.flush()
        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_path,
        path,
    )


def fsync_directory(path):
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY,
        )

    except Exception:
        return

    try:
        os.fsync(
            descriptor
        )

    except Exception:
        pass

    finally:
        os.close(
            descriptor
        )


def atomic_write_json(
    path,
    value,
):
    atomic_write_text(
        path,
        canonical_json(value),
    )

    fsync_directory(
        os.path.dirname(path)
        or "."
    )


# ==================================================================================================
# SNAPSHOT INTEGRITY
# ==================================================================================================

def snapshot_payload(state):
    payload = deep_copy(
        state
    )

    payload.pop(
        "integrity_sha256",
        None,
    )

    return payload


def calculate_snapshot_hash(state):
    return sha256_object(
        snapshot_payload(state)
    )


def seal_snapshot(state):
    sealed = deep_copy(
        state
    )

    sealed[
        "integrity_sha256"
    ] = calculate_snapshot_hash(
        sealed
    )

    return sealed


def snapshot_integrity_valid(state):
    if not isinstance(
        state,
        dict,
    ):
        return False

    expected = state.get(
        "integrity_sha256"
    )

    if not expected:
        return False

    return hmac.compare_digest(
        str(expected),
        calculate_snapshot_hash(
            state
        ),
    )


def save_snapshot(state):
    sealed = seal_snapshot(
        state
    )

    atomic_write_json(
        STATE_FILE,
        sealed,
    )

    return sealed


def load_snapshot():
    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as handle:

        state = json.load(
            handle
        )

    if not snapshot_integrity_valid(
        state
    ):
        raise RuntimeError(
            "Snapshot integrity validation failed"
        )

    return state


# ==================================================================================================
# HASH-CHAIN JOURNAL
# ==================================================================================================

def journal_records():
    if not os.path.exists(
        JOURNAL_FILE
    ):
        return []

    records = []

    with open(
        JOURNAL_FILE,
        "r",
        encoding="utf-8",
    ) as handle:

        for (
            line_number,
            raw_line,
        ) in enumerate(
            handle,
            start=1,
        ):
            line = raw_line.strip()

            if not line:
                continue

            try:
                record = json.loads(
                    line
                )

            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Journal JSON corruption "
                    f"at line {line_number}"
                ) from exc

            records.append(
                record
            )

    return records


def journal_record_hash(record):
    payload = deep_copy(
        record
    )

    payload.pop(
        "record_sha256",
        None,
    )

    return sha256_object(
        payload
    )


def validate_journal():
    records = journal_records()

    previous_hash = "GENESIS"

    for record in records:
        if not isinstance(
            record,
            dict,
        ):
            return False

        if (
            record.get(
                "previous_sha256"
            )
            != previous_hash
        ):
            return False

        claimed_hash = record.get(
            "record_sha256"
        )

        if not claimed_hash:
            return False

        calculated_hash = (
            journal_record_hash(
                record
            )
        )

        if not hmac.compare_digest(
            str(claimed_hash),
            calculated_hash,
        ):
            return False

        previous_hash = claimed_hash

    return True


def append_journal(
    event_type,
    transition_id,
    details=None,
):
    ensure_state_directory()

    existing = journal_records()

    if existing:
        previous_hash = existing[
            -1
        ]["record_sha256"]

    else:
        previous_hash = "GENESIS"

    record = {
        "version": VERSION,
        "sequence": (
            len(existing)
            + 1
        ),
        "time_ms": utc_ms(),
        "event": event_type,
        "transition_id": transition_id,
        "details": (
            details
            or {}
        ),
        "previous_sha256":
            previous_hash,
    }

    record[
        "record_sha256"
    ] = journal_record_hash(
        record
    )

    line = (
        canonical_json(record)
        + "\n"
    )

    with open(
        JOURNAL_FILE,
        "a",
        encoding="utf-8",
    ) as handle:

        handle.write(
            line
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    fsync_directory(
        STATE_DIR
    )

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
    quantity_text = decimal_string(
        quantity
    )

    identity_payload = {
        "version": VERSION,
        "symbol": SYMBOL,
        "transition_name":
            transition_name,
        "action": action,
        "quantity": quantity_text,
        "metadata":
            metadata
            or {},
    }

    intent_hash = sha256_object(
        identity_payload
    )

    transition_id = (
        f"{VERSION.lower()}-"
        f"{transition_name.lower().replace('_', '-')}-"
        f"{intent_hash[:20]}"
    )

    return {
        "transition_id":
            transition_id,
        "intent_sha256":
            intent_hash,
        "version":
            VERSION,
        "symbol":
            SYMBOL,
        "transition_name":
            transition_name,
        "action":
            action,
        "quantity":
            quantity_text,
        "metadata":
            metadata
            or {},
    }


# ==================================================================================================
# DURABLE EXACTLY-ONCE TRANSITION ENGINE
# ==================================================================================================

class DurableTransitionEngine:

    def __init__(
        self,
        state=None,
    ):
        if state is None:
            state = create_initial_state()

        self.state = state


    @classmethod
    def restore(cls):
        return cls(
            load_snapshot()
        )


    def persist(self):
        self.state[
            "updated_ms"
        ] = utc_ms()

        self.state = save_snapshot(
            self.state
        )


    def get_transition(
        self,
        transition_id,
    ):
        return self.state[
            "transitions"
        ].get(
            transition_id
        )


    def prepare(
        self,
        intent,
    ):
        transition_id = intent[
            "transition_id"
        ]

        existing = self.get_transition(
            transition_id
        )

        if existing is not None:
            return existing

        record = {
            "transition_id":
                transition_id,

            "intent":
                deep_copy(
                    intent
                ),

            "intent_sha256":
                intent[
                    "intent_sha256"
                ],

            "status":
                "PREPARED",

            "prepared_ms":
                utc_ms(),

            "committed_ms":
                None,

            "dispatched_ms":
                None,

            "applied_ms":
                None,

            "receipt":
                None,
        }

        self.state[
            "transitions"
        ][
            transition_id
        ] = record

        self.state[
            "last_transition_id"
        ] = transition_id

        append_journal(
            "PREPARED",
            transition_id,
            {
                "intent_sha256":
                    intent[
                        "intent_sha256"
                    ],
            },
        )

        self.persist()

        return self.get_transition(
            transition_id
        )


    def commit(
        self,
        transition_id,
    ):
        record = self.get_transition(
            transition_id
        )

        if record is None:
            raise RuntimeError(
                "Cannot commit missing transition"
            )

        status = record[
            "status"
        ]

        if status in (
            "COMMITTED",
            "DISPATCHED",
            "APPLIED",
        ):
            return record

        if status != "PREPARED":
            raise RuntimeError(
                f"Invalid commit status: "
                f"{status}"
            )

        record[
            "status"
        ] = "COMMITTED"

        record[
            "committed_ms"
        ] = utc_ms()

        append_journal(
            "COMMITTED",
            transition_id,
            {
                "intent_sha256":
                    record[
                        "intent_sha256"
                    ],
            },
        )

        self.persist()

        return self.get_transition(
            transition_id
        )


    def synthetic_dispatch(
        self,
        transition_id,
    ):
        record = self.get_transition(
            transition_id
        )

        if record is None:
            raise RuntimeError(
                "Cannot dispatch missing transition"
            )

        if record[
            "status"
        ] in (
            "DISPATCHED",
            "APPLIED",
        ):
            return record[
                "receipt"
            ]

        if record[
            "status"
        ] != "COMMITTED":
            raise RuntimeError(
                "Synthetic dispatch requires "
                "COMMITTED state"
            )

        if NETWORK_WRITES_ENABLED:
            raise RuntimeError(
                "Unsafe configuration: "
                "network writes enabled"
            )

        if not SYNTHETIC_TRANSPORT_ONLY:
            raise RuntimeError(
                "Unsafe configuration: "
                "synthetic-only transport disabled"
            )

        intent = record[
            "intent"
        ]

        receipt_payload = {
            "synthetic_only":
                True,

            "transmitted":
                False,

            "network_write":
                False,

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "transition_id":
                transition_id,

            "intent_sha256":
                intent[
                    "intent_sha256"
                ],

            "action":
                intent[
                    "action"
                ],

            "quantity":
                intent[
                    "quantity"
                ],

            "time_ms":
                utc_ms(),
        }

        receipt_payload[
            "receipt_sha256"
        ] = sha256_object(
            receipt_payload
        )

        record[
            "receipt"
        ] = receipt_payload

        record[
            "status"
        ] = "DISPATCHED"

        record[
            "dispatched_ms"
        ] = utc_ms()

        if (
            transition_id
            not in self.state[
                "consumed_intents"
            ]
        ):
            self.state[
                "consumed_intents"
            ].append(
                transition_id
            )

        existing_receipt_ids = {
            item.get(
                "transition_id"
            )
            for item
            in self.state[
                "dispatch_receipts"
            ]
            if isinstance(
                item,
                dict,
            )
        }

        if (
            transition_id
            not in existing_receipt_ids
        ):
            self.state[
                "dispatch_receipts"
            ].append(
                deep_copy(
                    receipt_payload
                )
            )

            self.state[
                "synthetic_dispatch_count"
            ] += 1

        append_journal(
            "DISPATCHED",
            transition_id,
            {
                "receipt_sha256":
                    receipt_payload[
                        "receipt_sha256"
                    ],
            },
        )

        # Critical durable fencing point:
        #
        # Receipt + consumed intent are persisted
        # before this method returns.
        #
        # Any restart after this point must see
        # DISPATCHED and must not redispatch.

        self.persist()

        return deep_copy(
            receipt_payload
        )


    def apply(
        self,
        transition_id,
    ):
        record = self.get_transition(
            transition_id
        )

        if record is None:
            raise RuntimeError(
                "Cannot apply missing transition"
            )

        if record[
            "status"
        ] == "APPLIED":
            return record

        if record[
            "status"
        ] != "DISPATCHED":
            raise RuntimeError(
                "Apply requires durable "
                "DISPATCHED state"
            )

        intent = record[
            "intent"
        ]

        transition_name = intent[
            "transition_name"
        ]

        self.apply_strategy_effect(
            transition_name
        )

        record[
            "status"
        ] = "APPLIED"

        record[
            "applied_ms"
        ] = utc_ms()

        append_journal(
            "APPLIED",
            transition_id,
            {
                "strategy_phase":
                    self.state[
                        "strategy_phase"
                    ],
            },
        )

        self.persist()

        return self.get_transition(
            transition_id
        )


# ==================================================================================================
# END OF R35A PART 2/4
#
# IMPORTANT:
# DO NOT RUN YET.
#
# NEXT:
# PART 3/4 CONTINUES INSIDE DurableTransitionEngine
# STARTING WITH:
#
#     def apply_strategy_effect(self, transition_name):
#
# ==================================================================================================

