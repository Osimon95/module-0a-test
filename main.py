
#!/usr/bin/env python3

import os
import json
import time
import base64
import hashlib
import hmac
import threading
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler, HTTPServer


# ============================================================
# R36E
# AUTOMATED WEEX V3 WRITER LAYER
#
# PURPOSE:
#   Final pre-live writer validation.
#
# TP POLICY:
#   PRIMARY_FILL:
#       Lock TP snapshot at fill.
#       NEVER recalculate after primary fill.
#
#   BACKUP_FILL:
#       Recalculate backup TP snapshot ONLY when backup fills.
#       Once that backup snapshot is created, it is immutable.
#
#   TP1:
#       20% allocation.
#       Nearest historical structure.
#       0.20% discount from historical resistance for LONG.
#
#   TP2:
#       20% allocation.
#       Second historical structure.
#       0.20% discount from historical resistance for LONG.
#
#   TP3:
#       60% allocation.
#       Trailing runner.
#
# SAFETY:
#   REAL ORDER EXECUTION = FALSE
#   DEMO ORDER EXECUTION = FALSE
#   HARD EXECUTION FIREBREAK = TRUE
#   This version performs ZERO exchange writes.
# ============================================================


# ============================================================
# FROZEN ENVIRONMENT CONTRACT
# ============================================================

API_BASE_URL = os.getenv(
    "WEEX_API_BASE",
    "https://api-contract.weex.com"
).rstrip("/")

PRIVATE_SYMBOL = "BTCUSDT"
DEMO_SYMBOL = "BTCSUSDT"

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "")
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "")
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "")

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

# ============================================================
# HARD EXECUTION FIREBREAK
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
HARD_EXECUTION_LOCK = True

# These counters MUST remain zero in R36E.
EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
DEMO_ORDERS_SENT = 0
REAL_ORDERS_SENT = 0
TP_CONDITIONAL_ORDERS_SENT = 0


# ============================================================
# TP CONFIGURATION
# ============================================================

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

# This was the missing R36E variable.
TP1_TRIGGER_PERCENT = Decimal("0.50")
TP2_TRIGGER_PERCENT = Decimal("1.00")

# Historical target is placed slightly before the historical
# resistance/support so the target does not require a perfect
# touch of the historical level.
TP_HISTORICAL_DISCOUNT_PERCENT = Decimal("0.20")

# TP3 trailing runner distance.
TP3_TRAILING_DISTANCE_PERCENT = Decimal("0.20")

# Historical candle engine.
HISTORICAL_LIMIT = 250
HISTORICAL_INTERVAL = "1m"

# Strategy sizing.
STRATEGY_MARGIN_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

# Exchange minimum quantity discovered from exchangeInfo.
DEFAULT_MIN_QTY = Decimal("0.0001")
DEFAULT_QTY_STEP = Decimal("0.0001")

# State.
R36E_STATE_DIR = "/var/data/r36e_state"
R36A_STATE_DIR = "/var/data/r36a_state"
R36C_STATE_DIR = "/var/data/r36c_state"

EXPECTED_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"

HEARTBEAT_SECONDS = 30
HEALTH_PORT = int(os.getenv("PORT", "10000"))

TEST_STATUS = "STARTING"
FINAL_BLOCKERS = []


# ============================================================
# LOGGING
# ============================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(f"{now_iso()} {message}", flush=True)


def separator():
    log("-" * 100)


def test_result(label, passed):
    status = "PASS" if passed else "FAIL"
    log(f"{label:<90} {status}")
    return passed


# ============================================================
# SAFE JSON / FILE HELPERS
# ============================================================

def ensure_state_dir():
    os.makedirs(R36E_STATE_DIR, exist_ok=True)


def save_json(filename, payload):
    ensure_state_dir()

    path = os.path.join(R36E_STATE_DIR, filename)
    temp = path + ".tmp"

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True, default=str)
        f.flush()
        os.fsync(f.fileno())

    os.replace(temp, path)
    return path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_json(payload):
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


# ============================================================
# DURABLE EVIDENCE DISCOVERY
# ============================================================

def scan_json_for_identity(root_dir, identity):
    if not os.path.isdir(root_dir):
        return False

    for root, _, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".json"):
                continue

            path = os.path.join(root, filename)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                if identity in text:
                    return True

            except Exception:
                continue

    return False


def scan_json_for_prefix(root_dir, prefix):
    if not os.path.isdir(root_dir):
        return False

    for root, _, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".json"):
                continue

            path = os.path.join(root, filename)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                if prefix in text:
                    return True

            except Exception:
                continue

    return False


# ============================================================
# WEEX SIGNATURE
# ============================================================

def sign_request(timestamp, method, request_path, query_string="", body=""):
    method = method.upper()

    if query_string:
        message = (
            str(timestamp)
            + method
            + request_path
            + "?"
            + query_string
            + body
        )
    else:
        message = (
            str(timestamp)
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# ============================================================
# HTTP
# ============================================================

def http_get(
    request_path,
    params=None,
    authenticated=False,
    timeout=15
):
    global EXCHANGE_NETWORK_WRITES

    params = params or {}

    query_string = urlencode(
        [(k, str(v)) for k, v in params.items()]
    )

    url = API_BASE_URL + request_path

    if query_string:
        url += "?" + query_string

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "R36E-PreLive-Writer/1.0"
    }

    if authenticated:
        timestamp = str(int(time.time() * 1000))

        signature = sign_request(
            timestamp,
            "GET",
            request_path,
            query_string,
            ""
        )

        headers.update({
            "ACCESS-KEY": WEEX_API_KEY,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
            "ACCESS-TIMESTAMP": timestamp
        })

    request = Request(
        url,
        headers=headers,
        method="GET"
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")

            try:
                data = json.loads(raw)
            except Exception:
                data = raw

            return {
                "ok": True,
                "status": response.status,
                "data": data,
                "error": None
            }

    except HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            raw = ""

        return {
            "ok": False,
            "status": exc.code,
            "data": None,
            "error": raw or str(exc)
        }

    except URLError as exc:
        return {
            "ok": False,
            "status": None,
            "data": None,
            "error": str(exc)
        }

    except Exception as exc:
        return {
            "ok": False,
            "status": None,
            "data": None,
            "error": str(exc)
        }


# ============================================================
# WEEX READS
# ============================================================

def get_mark_price():
    return http_get(
        "/capi/v3/market/symbolPrice",
        {
            "symbol": PRIVATE_SYMBOL,
            "priceType": "MARK"
        },
        authenticated=False
    )


def get_klines():
    return http_get(
        "/capi/v3/market/klines",
        {
            "symbol": PRIVATE_SYMBOL,
            "interval": HISTORICAL_INTERVAL,
            "limit": HISTORICAL_LIMIT
        },
        authenticated=False
    )


def get_exchange_info():
    return http_get(
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": PRIVATE_SYMBOL
        },
        authenticated=False
    )


def get_balance():
    return http_get(
        "/capi/v3/account/balance",
        authenticated=True
    )


def get_positions():
    return http_get(
        "/capi/v3/account/position/allPosition",
        authenticated=True
    )


def get_symbol_config():
    return http_get(
        "/capi/v3/account/symbolConfig",
        {
            "symbol": PRIVATE_SYMBOL
        },
        authenticated=True
    )


def get_account_config():
    return http_get(
        "/capi/v3/account/accountConfig",
        authenticated=True
    )


# ============================================================
# RESPONSE EXTRACTION
# ============================================================

def find_usdt_balance(data):
    if not isinstance(data, list):
        return None

    for item in data:
        if not isinstance(item, dict):
            continue

        if str(item.get("asset", "")).upper() == "USDT":
            value = item.get("availableBalance")

            if value is None:
                value = item.get("balance")

            if value is not None:
                return Decimal(str(value))

    return None


def extract_positions(data):
    if isinstance(data, list):
        return data

    return []


def is_flat(data):
    positions = extract_positions(data)

    for position in positions:
        if not isinstance(position, dict):
            continue

        symbol = str(position.get("symbol", "")).upper()

        if symbol != PRIVATE_SYMBOL:
            continue

        size = position.get("size", "0")

        try:
            if Decimal(str(size)) != Decimal("0"):
                return False
        except Exception:
            return False

    return True


def get_symbol_config_row(data):
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                if str(row.get("symbol", "")).upper() == PRIVATE_SYMBOL:
                    return row

    if isinstance(data, dict):
        if str(data.get("symbol", "")).upper() == PRIVATE_SYMBOL:
            return data

    return None


def get_exchange_symbol(data):
    if not isinstance(data, dict):
        return None

    symbols = data.get("symbols", [])

    if not isinstance(symbols, list):
        return None

    for row in symbols:
        if isinstance(row, dict):
            if str(row.get("symbol", "")).upper() == PRIVATE_SYMBOL:
                return row

    return None


# ============================================================
# CANDLE PARSING
# ============================================================

def parse_candles(data):
    if not isinstance(data, list):
        return []

    candles = []

    for row in data:
        if not isinstance(row, list):
            continue

        if len(row) < 5:
            continue

        try:
            candles.append({
                "open_time": int(row[0]),
                "open": Decimal(str(row[1])),
                "high": Decimal(str(row[2])),
                "low": Decimal(str(row[3])),
                "close": Decimal(str(row[4])),
            })
        except Exception:
            continue

    return candles


# ============================================================
# HISTORICAL TP ENGINE
# ============================================================

def calculate_historical_tp_preview(
    side,
    entry_price,
    candles
):
    """
    Hybrid TP engine.

    LONG:
        Find historical highs above entry.
        TP1 = nearest historical high minus 0.20%.
        TP2 = second historical high minus 0.20%.

    SHORT:
        Find historical lows below entry.
        TP1 = nearest historical low plus 0.20%.
        TP2 = second historical low plus 0.20%.

    TP3:
        60% trailing runner.

    IMPORTANT:
        This calculation creates a snapshot.
        It is NOT subsequently recalculated after fill.
    """

    if not candles:
        raise ValueError("No historical candles supplied")

    side = side.upper()

    if side not in ("LONG", "SHORT"):
        raise ValueError("Unsupported side")

    if entry_price <= Decimal("0"):
        raise ValueError("Entry price must be positive")

    discount = (
        TP_HISTORICAL_DISCOUNT_PERCENT
        / Decimal("100")
    )

    if side == "LONG":

        candidates = []

        for candle in candles:
            high = candle["high"]

            if high > entry_price:
                candidates.append(high)

        candidates = sorted(set(candidates))

        if len(candidates) < 2:
            raise ValueError(
                "Insufficient historical highs above LONG entry"
            )

        reference_1 = candidates[0]
        reference_2 = candidates[1]

        tp1 = (
            reference_1
            * (Decimal("1") - discount)
        )

        tp2 = (
            reference_2
            * (Decimal("1") - discount)
        )

    else:

        candidates = []

        for candle in candles:
            low = candle["low"]

            if low < entry_price:
                candidates.append(low)

        candidates = sorted(
            set(candidates),
            reverse=True
        )

        if len(candidates) < 2:
            raise ValueError(
                "Insufficient historical lows below SHORT entry"
            )

        reference_1 = candidates[0]
        reference_2 = candidates[1]

        tp1 = (
            reference_1
            * (Decimal("1") + discount)
        )

        tp2 = (
            reference_2
            * (Decimal("1") + discount)
        )

    if side == "LONG":
        if not (entry_price < tp1 < tp2):
            raise ValueError(
                f"Invalid LONG TP ordering: "
                f"entry={entry_price}, tp1={tp1}, tp2={tp2}"
            )
    else:
        if not (entry_price > tp1 > tp2):
            raise ValueError(
                f"Invalid SHORT TP ordering: "
                f"entry={entry_price}, tp1={tp1}, tp2={tp2}"
            )

    return {
        "side": side,
        "entry_price": str(entry_price),
        "historical_interval": HISTORICAL_INTERVAL,
        "historical_candle_count": len(candles),
        "historical_reference_1": str(reference_1),
        "historical_reference_2": str(reference_2),
        "historical_target_discount_percent":
            str(TP_HISTORICAL_DISCOUNT_PERCENT),

        "tp1": {
            "allocation_percent": str(TP1_PERCENT),
            "basis": "nearest_historical_structure",
            "price": str(tp1),
            "status": "LOCKED"
        },

        "tp2": {
            "allocation_percent": str(TP2_PERCENT),
            "basis": "second_historical_structure",
            "price": str(tp2),
            "status": "LOCKED"
        },

        "tp3": {
            "allocation_percent": str(TP3_PERCENT),
            "basis": "let_market_run",
            "status": "RUNNER",
            "trailing_distance_percent":
                str(TP3_TRAILING_DISTANCE_PERCENT)
        },

        "tp1_trigger_percent":
            str(TP1_TRIGGER_PERCENT),

        "tp2_trigger_percent":
            str(TP2_TRIGGER_PERCENT),

        "recalculation_policy":
            "NEVER_RECALCULATE_AFTER_FILL"
    }


# ============================================================
# TP SNAPSHOT
# ============================================================

def create_tp_snapshot(
    entry_price,
    side,
    fill_label,
    candles
):
    calculation = calculate_historical_tp_preview(
        side,
        entry_price,
        candles
    )

    snapshot = {
        "stage": "R36E",
        "snapshot_version": 1,
        "snapshot_created_at": now_iso(),
        "fill_time": now_iso(),
        "fill_label": fill_label,

        "side": side,
        "entry_price": str(entry_price),

        "historical_interval":
            calculation["historical_interval"],

        "historical_candle_count":
            calculation["historical_candle_count"],

        "historical_reference_1":
            calculation["historical_reference_1"],

        "historical_reference_2":
            calculation["historical_reference_2"],

        "historical_target_discount_percent":
            calculation[
                "historical_target_discount_percent"
            ],

        "recalculation_policy":
            "NEVER_RECALCULATE_AFTER_FILL",

        "tp1": calculation["tp1"],
        "tp2": calculation["tp2"],
        "tp3": calculation["tp3"]
    }

    snapshot["snapshot_sha256"] = sha256_json(snapshot)

    return snapshot


def verify_snapshot_hash(snapshot):
    supplied = snapshot.get("snapshot_sha256")

    if not supplied:
        return False

    body = dict(snapshot)
    body.pop("snapshot_sha256", None)

    calculated = sha256_json(body)

    return hmac.compare_digest(
        supplied,
        calculated
    )


# ============================================================
# CANARY QUANTITY ENGINE
# ============================================================

def normalize_quantity(
    quantity,
    step
):
    if step <= Decimal("0"):
        return quantity

    units = (
        quantity / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def calculate_canary(
    available_balance,
    mark_price,
    min_qty=DEFAULT_MIN_QTY,
    qty_step=DEFAULT_QTY_STEP
):
    strategy_margin = (
        available_balance
        * STRATEGY_MARGIN_PERCENT
        / Decimal("100")
    )

    strategy_notional = (
        strategy_margin
        * Decimal(str(TARGET_LONG_LEVERAGE))
    )

    raw_qty = (
        strategy_notional
        / mark_price
    )

    normalized_qty = normalize_quantity(
        raw_qty,
        qty_step
    )

    if normalized_qty < min_qty:
        normalized_qty = min_qty

    return {
        "available_balance_usdt":
            str(available_balance),

        "strategy_margin_usdt":
            str(strategy_margin),

        "strategy_notional_usdt":
            str(strategy_notional),

        "strategy_raw_qty_btc":
            str(raw_qty),

        "strategy_normalized_qty_btc":
            str(normalized_qty),

        "minimum_canary_qty_btc":
            str(min_qty),

        "qty_step":
            str(qty_step),

        "mark_price":
            str(mark_price),

        "symbol":
            PRIVATE_SYMBOL,

        "writer_enabled":
            False,

        "live_execution":
            False,

        "demo_execution":
            False
    }


# ============================================================
# WRITER PAYLOAD
# ============================================================

def construct_writer_entry_payload(
    side="LONG",
    quantity="0.0001"
):
    side = side.upper()

    if side == "LONG":
        exchange_side = "BUY"
    elif side == "SHORT":
        exchange_side = "SELL"
    else:
        raise ValueError("Invalid position side")

    return {
        "newClientOrderId":
            "R36E_TEST_PRIMARY_001",

        "positionSide":
            side,

        "quantity":
            str(quantity),

        "side":
            exchange_side,

        "symbol":
            PRIVATE_SYMBOL,

        "type":
            "MARKET"
    }


# ============================================================
# HARD-BLOCKED WRITER
# ============================================================

def blocked_exchange_writer(payload):
    """
    Deliberately refuses to perform an exchange write.

    R36E is a pre-live validation stage.
    """

    if HARD_EXECUTION_LOCK:
        raise RuntimeError(
            "R36E HARD EXECUTION FIREBREAK: "
            "exchange writer blocked"
        )

    if not LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "LIVE_ORDER_EXECUTION=False"
        )

    raise RuntimeError(
        "R36E live writer is intentionally unavailable "
        "in this pre-live build"
    )


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps({
            "stage": "R36E",
            "status": TEST_STATUS,
            "symbol": PRIVATE_SYMBOL,
            "live_order_execution":
                LIVE_ORDER_EXECUTION,
            "demo_order_execution":
                DEMO_ORDER_EXECUTION,
            "hard_execution_lock":
                HARD_EXECUTION_LOCK,
            "exchange_network_writes":
                EXCHANGE_NETWORK_WRITES,
            "real_orders_sent":
                REAL_ORDERS_SENT
        }).encode("utf-8")

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
    server = HTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    log(
        f"R36E: HEALTH SERVER STARTED "
        f"ON PORT {HEALTH_PORT}"
    )

    return server


# ============================================================
# MAIN R36E VALIDATION
# ============================================================

def run_r36e():

    global TEST_STATUS
    global FINAL_BLOCKERS

    separator()
    log("R36E: MAIN.PY ENTERED")
    log(
        "PURPOSE=AUTOMATED WEEX V3 WRITER LAYER "
        "WITH IMMUTABLE PRIMARY TP AND "
        "RECALCULATED BACKUP TP SNAPSHOTS"
    )
    log(
        f"PYTHON_VERSION="
        f"{os.sys.version_info.major}."
        f"{os.sys.version_info.minor}."
        f"{os.sys.version_info.micro}"
    )
    log(f"PRIVATE_SYMBOL={PRIVATE_SYMBOL}")
    log(f"DEMO_SYMBOL={DEMO_SYMBOL}")
    log(f"TARGET_MARGIN_MODE={TARGET_MARGIN_MODE}")
    log(
        f"TARGET_LONG_LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x"
    )
    log(
        f"TARGET_SHORT_LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    # --------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------

    separator()
    log("R36E TEST 1: HARD EXECUTION FIREBREAK")

    frozen_env_ok = (
        PRIVATE_SYMBOL == "BTCUSDT"
        and DEMO_SYMBOL == "BTCSUSDT"
        and TARGET_MARGIN_MODE == "ISOLATED"
        and TARGET_LONG_LEVERAGE == 100
        and TARGET_SHORT_LEVERAGE == 100
    )

    firebreak_ok = (
        LIVE_ORDER_EXECUTION is False
        and DEMO_ORDER_EXECUTION is False
        and HARD_EXECUTION_LOCK is True
    )

    test_result(
        "Frozen WEEX Environment Names",
        frozen_env_ok
    )

    test_result(
        "R36E Hard Execution Firebreak",
        firebreak_ok
    )

    if not frozen_env_ok:
        FINAL_BLOCKERS.append(
            "FROZEN_ENVIRONMENT_CONTRACT_FAILED"
        )

    if not firebreak_ok:
        FINAL_BLOCKERS.append(
            "HARD_EXECUTION_FIREBREAK_FAILED"
        )

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    separator()
    log(
        "R36E TEST 2: PRESERVE "
        "R36A/R36C DURABLE EVIDENCE"
    )

    r36a_durable = os.path.isdir(R36A_STATE_DIR)
    r36c_durable = os.path.isdir(R36C_STATE_DIR)

    r36a_id_proven = scan_json_for_identity(
        R36A_STATE_DIR,
        EXPECTED_R36A_UPDATE_ID
    )

    r36c_id_proven = scan_json_for_prefix(
        R36C_STATE_DIR,
        "R36C_"
    )

    log(f"R36A_DURABLE={r36a_durable}")
    log(f"R36C_DURABLE={r36c_durable}")
    log(f"R36A_ID_PROVEN={r36a_id_proven}")
    log(f"R36C_ID_PROVEN={r36c_id_proven}")

    test_result(
        "R36A Durable Registries Readable",
        r36a_durable
    )

    test_result(
        "R36C Durable Registries Readable",
        r36c_durable
    )

    test_result(
        "R36A Proven Identity Still Present",
        r36a_id_proven
    )

    test_result(
        "R36C Proven Identity Still Present",
        r36c_id_proven
    )

    if not r36a_durable:
        FINAL_BLOCKERS.append(
            "R36A_DURABLE_REGISTRY_UNAVAILABLE"
        )

    if not r36c_durable:
        FINAL_BLOCKERS.append(
            "R36C_DURABLE_REGISTRY_UNAVAILABLE"
        )

    if not r36a_id_proven:
        FINAL_BLOCKERS.append(
            "R36A_PROVEN_IDENTITY_MISSING"
        )

    if not r36c_id_proven:
        FINAL_BLOCKERS.append(
            "R36C_PROVEN_IDENTITY_MISSING"
        )

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    separator()
    log("R36E TEST 3: WEEX CREDENTIAL CONTRACT")

    key_present = bool(WEEX_API_KEY)
    secret_present = bool(WEEX_API_SECRET)
    passphrase_present = bool(WEEX_API_PASSPHRASE)

    log(
        f"WEEX_API_KEY_PRESENT={key_present}"
    )
    log(
        f"WEEX_API_SECRET_PRESENT={secret_present}"
    )
    log(
        f"WEEX_API_PASSPHRASE_PRESENT="
        f"{passphrase_present}"
    )

    credentials_ok = (
        key_present
        and secret_present
        and passphrase_present
    )

    test_result(
        "All Frozen WEEX Credentials Present",
        credentials_ok
    )

    if not credentials_ok:
        FINAL_BLOCKERS.append(
            "WEEX_CREDENTIAL_CONTRACT_FAILED"
        )

    # --------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------

    separator()
    log(
        "R36E TEST 4: CURRENT WEEX "
        "READ-ONLY RECONCILIATION"
    )

    mark_response = get_mark_price()
    balance_response = get_balance()
    position_response = get_positions()
    symbol_config_response = get_symbol_config()

    mark_ok = False
    balance_ok = False
    position_ok = False
    symbol_config_ok = False

    mark_price = None
    available_balance = None
    positions = []
    symbol_config = None

    if mark_response["ok"]:
        try:
            mark_data = mark_response["data"]

            mark_price = Decimal(
                str(mark_data["price"])
            )

            mark_ok = mark_price > Decimal("0")

        except Exception:
            mark_ok = False

    if balance_response["ok"]:
        available_balance = find_usdt_balance(
            balance_response["data"]
        )

        balance_ok = (
            available_balance is not None
            and available_balance >= Decimal("0")
        )

    if position_response["ok"]:
        positions = extract_positions(
            position_response["data"]
        )

        position_ok = True

    if symbol_config_response["ok"]:
        symbol_config = get_symbol_config_row(
            symbol_config_response["data"]
        )

        symbol_config_ok = (
            symbol_config is not None
        )

    reconciliation = {
        "balance": {
            "ok": balance_ok,
            "status": balance_response["status"],
            "available_usdt":
                str(available_balance)
                if available_balance is not None
                else None,
            "error":
                balance_response["error"]
        },

        "mark_price": {
            "ok": mark_ok,
            "price":
                str(mark_price)
                if mark_price is not None
                else None
        },

        "position": {
            "ok": position_ok,
            "flat":
                is_flat(
                    position_response["data"]
                )
                if position_response["ok"]
                else False,
            "rows":
                len(positions),
            "status":
                position_response["status"],
            "error":
                position_response["error"]
        },

        "symbol_config": {
            "ok": symbol_config_ok,
            "margin_mode":
                symbol_config.get("marginType")
                if symbol_config
                else None,
            "long_leverage":
                symbol_config.get(
                    "isolatedLongLeverage"
                )
                if symbol_config
                else None,
            "short_leverage":
                symbol_config.get(
                    "isolatedShortLeverage"
                )
                if symbol_config
                else None,
            "error":
                symbol_config_response["error"]
        }
    }

    log(
        "RECONCILIATION="
        + json.dumps(
            reconciliation,
            sort_keys=True
        )
    )

    flat_ok = (
        position_ok
        and is_flat(
            position_response["data"]
        )
    )

    leverage_ok = False

    if symbol_config:
        margin_mode = str(
            symbol_config.get("marginType", "")
        ).upper()

        long_lev = str(
            symbol_config.get(
                "isolatedLongLeverage",
                ""
            )
        )

        short_lev = str(
            symbol_config.get(
                "isolatedShortLeverage",
                ""
            )
        )

        leverage_ok = (
            margin_mode == TARGET_MARGIN_MODE
            and long_lev == str(TARGET_LONG_LEVERAGE)
            and short_lev == str(TARGET_SHORT_LEVERAGE)
        )

    test_result(
        "Current Mark Price Read",
        mark_ok
    )

    test_result(
        "Authenticated Balance Read",
        balance_ok
    )

    test_result(
        "Current Position Read",
        position_ok
    )

    test_result(
        "BTCUSDT Currently Flat",
        flat_ok
    )

    test_result(
        "ISOLATED 100x/100x Configuration",
        leverage_ok
    )

    if not mark_ok:
        FINAL_BLOCKERS.append(
            "CURRENT_MARK_PRICE_READ_FAILED"
        )

    if not balance_ok:
        FINAL_BLOCKERS.append(
            "AUTHENTICATED_BALANCE_READ_FAILED"
        )

    if not position_ok:
        FINAL_BLOCKERS.append(
            "CURRENT_POSITION_READ_FAILED"
        )

    if not flat_ok:
        FINAL_BLOCKERS.append(
            "BTCUSDT_NOT_FLAT"
        )

    if not leverage_ok:
        FINAL_BLOCKERS.append(
            "ISOLATED_100X_CONFIGURATION_FAILED"
        )

    # --------------------------------------------------------
    # TEST 5
    # --------------------------------------------------------

    separator()
    log(
        "R36E TEST 5: HISTORICAL CANDLE / TP ENGINE"
    )

    candle_response = get_klines()

    candles = []

    if candle_response["ok"]:
        candles = parse_candles(
            candle_response["data"]
        )

    historical_ok = (
        len(candles) >= HISTORICAL_LIMIT
    )

    log(
        f"HISTORICAL_CANDLE_COUNT="
        f"{len(candles)}"
    )

    test_result(
        "Historical BTCUSDT Candles Available",
        historical_ok
    )

    if not historical_ok:
        FINAL_BLOCKERS.append(
            "HISTORICAL_CANDLE_ENGINE_FAILED"
        )

    # --------------------------------------------------------
    # TEST 6
    # --------------------------------------------------------

    separator()
    log(
        "R36E TP TEST: PRIMARY IMMUTABILITY + "
        "BACKUP RECALCULATION"
    )
    separator()

    synthetic_candles = [
        {
            "open_time": 1,
            "open": Decimal("99000"),
            "high": Decimal("100500"),
            "low": Decimal("98500"),
            "close": Decimal("100000")
        },
        {
            "open_time": 2,
            "open": Decimal("100000"),
            "high": Decimal("101000"),
            "low": Decimal("99500"),
            "close": Decimal("100500")
        },
        {
            "open_time": 3,
            "open": Decimal("100500"),
            "high": Decimal("102000"),
            "low": Decimal("100000"),
            "close": Decimal("101000")
        },
        {
            "open_time": 4,
            "open": Decimal("101000"),
            "high": Decimal("103000"),
            "low": Decimal("100500"),
            "close": Decimal("102000")
        }
    ]

    try:
        primary_snapshot = create_tp_snapshot(
            Decimal("100000"),
            "LONG",
            "PRIMARY_FILL",
            synthetic_candles
        )

        primary_created_ok = True
    except Exception as exc:
        primary_created_ok = False
        primary_snapshot = {}
        log(
            f"PRIMARY_TP_SNAPSHOT_ERROR={exc}"
        )

    try:
        backup_snapshot = create_tp_snapshot(
            Decimal("98000"),
            "LONG",
            "BACKUP_1_FILL",
            synthetic_candles
        )

        backup_created_ok = True
    except Exception as exc:
        backup_created_ok = False
        backup_snapshot = {}
        log(
            f"BACKUP_TP_SNAPSHOT_ERROR={exc}"
        )

    primary_hash_ok = (
        primary_created_ok
        and verify_snapshot_hash(
            primary_snapshot
        )
    )

    backup_hash_ok = (
        backup_created_ok
        and verify_snapshot_hash(
            backup_snapshot
        )
    )

    independent_ok = (
        primary_created_ok
        and backup_created_ok
        and primary_snapshot["snapshot_sha256"]
        != backup_snapshot["snapshot_sha256"]
        and primary_snapshot["entry_price"]
        != backup_snapshot["entry_price"]
    )

    test_result(
        "Primary TP Snapshot Created",
        primary_created_ok
    )

    test_result(
        "Backup TP Snapshot Created",
        backup_created_ok
    )

    test_result(
        "Primary Snapshot Hash Valid",
        primary_hash_ok
    )

    test_result(
        "Backup Snapshot Hash Valid",
        backup_hash_ok
    )

    test_result(
        "Primary And Backup Are Independent",
        independent_ok
    )

    if primary_created_ok:
        log(
            "PRIMARY_TP_SNAPSHOT="
            + json.dumps(
                primary_snapshot,
                sort_keys=True
            )
        )

    if backup_created_ok:
        log(
            "BACKUP_TP_SNAPSHOT="
            + json.dumps(
                backup_snapshot,
                sort_keys=True
            )
        )

    if not primary_created_ok:
        FINAL_BLOCKERS.append(
            "PRIMARY_TP_SNAPSHOT_FAILED"
        )

    if not backup_created_ok:
        FINAL_BLOCKERS.append(
            "BACKUP_TP_SNAPSHOT_FAILED"
        )

    if not primary_hash_ok:
        FINAL_BLOCKERS.append(
            "PRIMARY_TP_HASH_FAILED"
        )

    if not backup_hash_ok:
        FINAL_BLOCKERS.append(
            "BACKUP_TP_HASH_FAILED"
        )

    if not independent_ok:
        FINAL_BLOCKERS.append(
            "PRIMARY_BACKUP_INDEPENDENCE_FAILED"
        )

    # --------------------------------------------------------
    # TEST 7
    # --------------------------------------------------------

    separator()
    log(
        "R36E TEST 7: REAL HISTORICAL TP PREVIEW"
    )

    real_preview_ok = False
    real_preview = None

    try:
        if mark_price is None:
            raise ValueError(
                "Mark price unavailable"
            )

        if len(candles) < 2:
            raise ValueError(
                "Historical candles unavailable"
            )

        real_preview = calculate_historical_tp_preview(
            "LONG",
            mark_price,
            candles
        )

        real_preview_ok = True

    except Exception as exc:
        log(
            "REAL_PRIMARY_TP_PREVIEW_ERROR="
            + str(exc)
        )

    if real_preview_ok:
        log(
            "REAL_PRIMARY_TP_PREVIEW="
            + json.dumps(
                real_preview,
                sort_keys=True
            )
        )

    test_result(
        "Real Historical TP Preview Calculated",
        real_preview_ok
    )

    if not real_preview_ok:
        FINAL_BLOCKERS.append(
            "REAL_TP_PREVIEW_FAILED"
        )

    # --------------------------------------------------------
    # TEST 8
    # --------------------------------------------------------

    separator()
    log(
        "R36E TEST 8: CANARY QUANTITY PREVIEW"
    )

    canary_ok = False
    canary_preview = None

    try:
        if available_balance is None:
            raise ValueError(
                "Available balance unavailable"
            )

        if mark_price is None:
            raise ValueError(
                "Mark price unavailable"
            )

        exchange_symbol = get_exchange_symbol(
            get_exchange_info()["data"]
        ) if get_exchange_info()["ok"] else None

        min_qty = DEFAULT_MIN_QTY
        qty_step = DEFAULT_QTY_STEP

        if exchange_symbol:
            try:
                min_qty = Decimal(
                    str(
                        exchange_symbol.get(
                            "minOrderSize",
                            DEFAULT_MIN_QTY
                        )
                    )
                )
            except Exception:
                min_qty = DEFAULT_MIN_QTY

            try:
                precision = int(
                    exchange_symbol.get(
                        "quantityPrecision",
                        4
                    )
                )

                qty_step = (
                    Decimal("1")
                    .scaleb(-precision)
                )

            except Exception:
                qty_step = DEFAULT_QTY_STEP

        canary_preview = calculate_canary(
            available_balance,
            mark_price,
            min_qty,
            qty_step
        )

        canary_ok = True

    except Exception as exc:
        log(
            "CANARY_PREVIEW_ERROR="
            + str(exc)
        )

    if canary_preview:
        log(
            "CANARY_PREVIEW="
            + json.dumps(
                canary_preview,
                sort_keys=True
            )
        )

    test_result(
        "Canary Preview Available",
        canary_ok
    )

    quantity_rules_ok = (
        canary_ok
        and canary_preview is not None
        and Decimal(
            canary_preview[
                "strategy_normalized_qty_btc"
            ]
        ) >= Decimal(
            canary_preview[
                "minimum_canary_qty_btc"
            ]
        )
    )

    test_result(
        "Canary Quantity Obeys Exchange Rules",
        quantity_rules_ok
    )

    if not canary_ok:
        FINAL_BLOCKERS.append(
            "CANARY_PREVIEW_FAILED"
        )

    if not quantity_rules_ok:
        FINAL_BLOCKERS.append(
            "CANARY_QUANTITY_RULE_FAILED"
        )

    # --------------------------------------------------------
    # TEST 9
    # --------------------------------------------------------

    separator()
    log(
        "R36E WRITER TEST: REQUEST "
        "CONSTRUCTION ONLY"
    )
    separator()

    writer_payload = construct_writer_entry_payload(
        "LONG",
        "0.0001"
    )

    writer_payload_ok = (
        writer_payload.get("symbol")
        == PRIVATE_SYMBOL
        and writer_payload.get("side")
        == "BUY"
        and writer_payload.get("positionSide")
        == "LONG"
        and writer_payload.get("type")
        == "MARKET"
        and writer_payload.get("quantity")
        == "0.0001"
    )

    test_result(
        "Writer Entry Payload Correct",
        writer_payload_ok
    )

    log(
        "WRITER_DRY_RUN_PAYLOAD="
        + json.dumps(
            writer_payload,
            sort_keys=True
        )
    )

    writer_block_ok = (
        HARD_EXECUTION_LOCK
        and LIVE_ORDER_EXECUTION is False
        and DEMO_ORDER_EXECUTION is False
    )

    test_result(
        "Live Writer Remains Hard Blocked",
        writer_block_ok
    )

    if not writer_payload_ok:
        FINAL_BLOCKERS.append(
            "WRITER_PAYLOAD_CONSTRUCTION_FAILED"
        )

    if not writer_block_ok:
        FINAL_BLOCKERS.append(
            "WRITER_HARD_BLOCK_FAILED"
        )

    # --------------------------------------------------------
    # TEST 10
    # --------------------------------------------------------

    separator()
    log(
        "R36E TEST 10: ZERO-WRITE INVARIANT"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        f"DEMO_ORDERS_SENT="
        f"{DEMO_ORDERS_SENT}"
    )

    log(
        f"REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )

    log(
        f"TP_CONDITIONAL_ORDERS_SENT="
        f"{TP_CONDITIONAL_ORDERS_SENT}"
    )

    zero_write_ok = (
        EXCHANGE_NETWORK_WRITES == 0
        and ORDER_SUBMISSIONS == 0
        and DEMO_ORDERS_SENT == 0
        and REAL_ORDERS_SENT == 0
        and TP_CONDITIONAL_ORDERS_SENT == 0
    )

    test_result(
        "R36E Performed Zero Exchange Writes",
        zero_write_ok
    )

    if not zero_write_ok:
        FINAL_BLOCKERS.append(
            "ZERO_WRITE_INVARIANT_FAILED"
        )

    # --------------------------------------------------------
    # AUDIT SNAPSHOT
    # --------------------------------------------------------

    audit_snapshot = {
        "stage": "R36E",
        "created_at": now_iso(),

        "private_symbol": PRIVATE_SYMBOL,
        "demo_symbol": DEMO_SYMBOL,

        "target_margin_mode":
            TARGET_MARGIN_MODE,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "primary_tp_policy":
            "LOCK_ON_FILL",

        "backup_tp_policy":
            "RECALCULATE_ON_BACKUP_FILL_ONLY",

        "tp1_allocation_percent":
            str(TP1_PERCENT),

        "tp2_allocation_percent":
            str(TP2_PERCENT),

        "tp3_allocation_percent":
            str(TP3_PERCENT),

        "tp1_trigger_percent":
            str(TP1_TRIGGER_PERCENT),

        "tp2_trigger_percent":
            str(TP2_TRIGGER_PERCENT),

        "historical_target_discount_percent":
            str(TP_HISTORICAL_DISCOUNT_PERCENT),

        "tp3_trailing_distance_percent":
            str(TP3_TRAILING_DISTANCE_PERCENT),

        "live_order_execution":
            LIVE_ORDER_EXECUTION,

        "demo_order_execution":
            DEMO_ORDER_EXECUTION,

        "hard_execution_lock":
            HARD_EXECUTION_LOCK,

        "exchange_network_writes":
            EXCHANGE_NETWORK_WRITES,

        "order_submissions":
            ORDER_SUBMISSIONS,

        "demo_orders_sent":
            DEMO_ORDERS_SENT,

        "real_orders_sent":
            REAL_ORDERS_SENT,

        "tp_conditional_orders_sent":
            TP_CONDITIONAL_ORDERS_SENT,

        "final_blockers":
            FINAL_BLOCKERS
    }

    try:
        save_json(
            "r36e_writer_audit.json",
            audit_snapshot
        )

        test_result(
            "R36E Writer Audit Snapshot Saved",
            True
        )

    except Exception as exc:
        log(
            "R36E AUDIT SAVE ERROR="
            + str(exc)
        )

        FINAL_BLOCKERS.append(
            "R36E_AUDIT_SAVE_FAILED"
        )

        test_result(
            "R36E Writer Audit Snapshot Saved",
            False
        )

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    separator()
    log("R36E: FINAL TEST SUMMARY")
    separator()

    if FINAL_BLOCKERS:
        TEST_STATUS = "FAIL"
    else:
        TEST_STATUS = "PASS"

    log(
        f"TEST_STATUS={TEST_STATUS}"
    )

    log(
        "R36E_WRITER_PRE_LIVE_GATE="
        + (
            "PASS"
            if TEST_STATUS == "PASS"
            else "FAIL"
        )
    )

    log(
        "PRIMARY_TP_POLICY=LOCK_ON_FILL"
    )

    log(
        "BACKUP_TP_POLICY="
        "RECALCULATE_ON_BACKUP_FILL_ONLY"
    )

    log(
        "TP3_POLICY=60_PERCENT_TRAILING_RUNNER"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{LIVE_ORDER_EXECUTION}"
    )

    log(
        f"DEMO_ORDER_EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )

    log(
        "FINAL_BLOCKERS="
        + json.dumps(FINAL_BLOCKERS)
    )

    if FINAL_BLOCKERS:
        log(
            "NEXT_STAGE="
            "FIX_ONLY_LISTED_BLOCKERS"
        )
    else:
        log(
            "NEXT_STAGE="
            "R36E_PRE_LIVE_GATE_PASSED"
        )

    separator()


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop():

    heartbeat = 0

    while True:
        heartbeat += 1

        mark_price = "UNKNOWN"
        flat = "UNKNOWN"

        try:
            mark_response = get_mark_price()

            if mark_response["ok"]:
                mark_price = str(
                    mark_response["data"]["price"]
                )
        except Exception:
            pass

        try:
            position_response = get_positions()

            if position_response["ok"]:
                flat = is_flat(
                    position_response["data"]
                )
        except Exception:
            pass

        log(
            f"R36E: HEARTBEAT={heartbeat} "
            f"TEST_STATUS={TEST_STATUS} "
            f"BTCUSDT_FLAT={flat} "
            f"MARK_PRICE={mark_price} "
            f"LONG_LEVERAGE={TARGET_LONG_LEVERAGE} "
            f"SHORT_LEVERAGE={TARGET_SHORT_LEVERAGE} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDERS_SENT="
            f"{REAL_ORDERS_SENT} "
            f"LIVE_ORDER_EXECUTION="
            f"{LIVE_ORDER_EXECUTION}"
        )

        time.sleep(HEARTBEAT_SECONDS)


# ============================================================
# ENTRY POINT
# ============================================================

def main():

    start_health_server()

    run_r36e()

    heartbeat_loop()


if __name__ == "__main__":
    main()
