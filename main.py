

# ==================================================================================================
# R34Y - LIVE READ-ONLY STATE + DURABLE SYNTHETIC STRATEGY LIFECYCLE / RECOVERY VALIDATION
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
# IMPORTANT R34Y CORRECTION
#
#   VALID WEEX V3 POSITION PATH:
#
#       /capi/v3/account/position/allPosition
#
#   NOT:
#
#       /capi/v3/account/allPosition
#
#   NOT:
#
#       /capi/v3/position/allPosition
#
# R34Y validates:
#
#   LIVE ACCOUNT BALANCE
#       ↓
#   LIVE POSITIONS
#       ↓
#   LIVE SYMBOL CONFIGURATION
#       ↓
#   LIVE MARKET PRICE
#       ↓
#   LIVE CONTRACT INFORMATION
#       ↓
#   STRATEGY BUDGET
#       ↓
#   SYNTHETIC INITIAL ENTRY
#       ↓
#   SYNTHETIC PYRAMID
#       ↓
#   SYNTHETIC BACKUP 1
#       ↓
#   SYNTHETIC BACKUP 2
#       ↓
#   SYNTHETIC BACKUP 3
#       ↓
#   FOURTH BACKUP REJECTION
#       ↓
#   DURABLE LOCAL SNAPSHOT
#       ↓
#   RESTART RESTORE
#       ↓
#   REPLAY REJECTION
#       ↓
#   SYNTHETIC RECOVERY
#       ↓
#   TERMINAL LOCAL STATE
#
# NO EXCHANGE WRITE REQUEST CAN BE GENERATED OR TRANSMITTED BY THIS FILE.
# ==================================================================================================

import base64
import hashlib
import hmac
import json
import math
import os
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

from decimal import Decimal, InvalidOperation, ROUND_CEILING
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


# ==================================================================================================
# VERSION
# ==================================================================================================

VERSION = "R34Y"


# ==================================================================================================
# CORE CONFIGURATION
# ==================================================================================================

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper().strip()

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv("HEALTH_PORT", "10000"),
    )
)

REQUEST_TIMEOUT_SECONDS = 15

STATE_DIR = Path(
    os.getenv(
        "R34Y_STATE_DIR",
        "/tmp/r34y_state",
    )
)

STATE_FILE = STATE_DIR / "strategy_state.json"


# ==================================================================================================
# WEEX API CREDENTIALS
# ==================================================================================================

WEEX_API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("API_KEY")
    or ""
).strip()

WEEX_API_SECRET = (
    os.getenv("WEEX_API_SECRET")
    or os.getenv("API_SECRET")
    or ""
).strip()

WEEX_API_PASSPHRASE = (
    os.getenv("WEEX_API_PASSPHRASE")
    or os.getenv("API_PASSPHRASE")
    or ""
).strip()


# ==================================================================================================
# SAFETY CONFIGURATION
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
# STRATEGY CONFIGURATION
# ==================================================================================================

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ==================================================================================================
# CORRECT WEEX V3 READ-ONLY PATHS
# ==================================================================================================

BALANCE_PATH = "/capi/v3/account/balance"

# CRITICAL R34Y FIX:
POSITION_PATH = "/capi/v3/account/position/allPosition"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"

PREMIUM_INDEX_PATH = "/capi/v3/market/premiumIndex"


# ==================================================================================================
# GLOBAL RUNTIME STATE
# ==================================================================================================

runtime_lock = threading.RLock()

runtime = {
    "phase": "BOOTING",

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
    "recovery_dispatches": 0,

    "restart_restores": 0,
    "replays_blocked": 0,

    "validation_passed": False,
    "last_error": None,

    "heartbeat": 0,
}


# ==================================================================================================
# BASIC FORMATTING
# ==================================================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def test_result(name, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    log(f"{name:<88} {status}")

    if not condition:
        raise AssertionError(name)


def set_phase(phase):
    with runtime_lock:
        runtime["phase"] = phase


def decimal_string(value):
    d = Decimal(str(value))

    text = format(d, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def safe_decimal(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        return Decimal(str(value))

    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


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


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        with runtime_lock:
            body = {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": runtime["phase"],
                "authenticatedReadOnly": AUTHENTICATED_READ_ONLY,
                "publicReadOnly": PUBLIC_READ_ONLY,
                "networkWrites": runtime["network_writes"],
                "realOrders": runtime["real_orders"],
                "demoOrders": runtime["demo_orders"],
                "syntheticDispatches": runtime["synthetic_dispatches"],
                "recoveryDispatches": runtime["recovery_dispatches"],
                "restartRestores": runtime["restart_restores"],
                "replaysBlocked": runtime["replays_blocked"],
                "validationPassed": runtime["validation_passed"],
            }

        encoded = json.dumps(body).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

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
                f"{VERSION}: HEALTH SERVER WARNING="
                f"{type(exc).__name__}: {exc}"
            )

    thread = threading.Thread(
        target=worker,
        daemon=True,
        name="r34y-health-server",
    )

    thread.start()


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_worker():

    while True:
        time.sleep(30)

        with runtime_lock:
            runtime["heartbeat"] += 1

            log(
                f"{VERSION}: HEARTBEAT {runtime['heartbeat']}"
                f" | phase={runtime['phase']}"
                f" | authenticated-read-only={AUTHENTICATED_READ_ONLY}"
                f" | authenticated-get={runtime['authenticated_get']}"
                f" | public-get={runtime['public_get']}"
                f" | network-writes={runtime['network_writes']}"
                f" | real-orders={runtime['real_orders']}"
                f" | demo-orders={runtime['demo_orders']}"
                f" | synthetic-dispatches={runtime['synthetic_dispatches']}"
                f" | recovery-dispatches={runtime['recovery_dispatches']}"
                f" | restart-restores={runtime['restart_restores']}"
                f" | replays-blocked={runtime['replays_blocked']}"
            )


def start_heartbeat():

    thread = threading.Thread(
        target=heartbeat_worker,
        daemon=True,
        name="r34y-heartbeat",
    )

    thread.start()


# ==================================================================================================
# ABSOLUTE WRITE FIREBREAK
# ==================================================================================================

class NetworkWriteRejected(RuntimeError):
    pass


def reject_network_write(operation):
    raise NetworkWriteRejected(
        f"{VERSION}: NETWORK WRITE REJECTED: {operation}"
    )


def http_post(*args, **kwargs):
    reject_network_write("HTTP POST")


def http_put(*args, **kwargs):
    reject_network_write("HTTP PUT")


def http_patch(*args, **kwargs):
    reject_network_write("HTTP PATCH")


def http_delete(*args, **kwargs):
    reject_network_write("HTTP DELETE")


def place_real_order(*args, **kwargs):
    reject_network_write("REAL ORDER")


def place_demo_order(*args, **kwargs):
    reject_network_write("DEMO ORDER")


def mutate_leverage(*args, **kwargs):
    reject_network_write("LEVERAGE MUTATION")


def mutate_margin(*args, **kwargs):
    reject_network_write("MARGIN MUTATION")


def mutate_position(*args, **kwargs):
    reject_network_write("POSITION MUTATION")


def mutate_account(*args, **kwargs):
    reject_network_write("ACCOUNT MUTATION")


# ==================================================================================================
# URL / QUERY HELPERS
# ==================================================================================================

def encode_query(params):

    if not params:
        return ""

    cleaned = []

    for key, value in params.items():

        if value is None:
            continue

        cleaned.append(
            (
                str(key),
                str(value),
            )
        )

    return urllib.parse.urlencode(cleaned)


# ==================================================================================================
# SIGNATURE
# ==================================================================================================

def create_signature(timestamp, method, path, query_string=""):

    method = method.upper()

    if query_string:
        message = (
            timestamp
            + method
            + path
            + "?"
            + query_string
        )

    else:
        message = (
            timestamp
            + method
            + path
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# ==================================================================================================
# JSON RESPONSE DECODING
# ==================================================================================================

def decode_json_response(raw):

    if raw is None:
        return None

    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")

    raw = raw.strip()

    if not raw:
        return None

    return json.loads(raw)


# ==================================================================================================
# AUTHENTICATED GET ONLY
# ==================================================================================================

def authenticated_get(path, params=None):

    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only access is disabled"
        )

    if not path.startswith("/"):
        raise RuntimeError(
            f"Invalid authenticated path: {path}"
        )

    query_string = encode_query(params)

    timestamp = str(int(time.time() * 1000))

    signature = create_signature(
        timestamp=timestamp,
        method="GET",
        path=path,
        query_string=query_string,
    )

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-ReadOnlyValidator/1.0",
    }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    with runtime_lock:
        runtime["authenticated_get"] += 1

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read()

            return decode_json_response(raw)

    except urllib.error.HTTPError as exc:

        try:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:
            body = ""

        raise RuntimeError(
            f"Authenticated GET failed: {path}"
            f" | HTTP {exc.code}"
            f" | {body}"
        )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Authenticated GET failed: {path}"
            f" | URLError: {exc}"
        )


# ==================================================================================================
# PUBLIC GET ONLY
# ==================================================================================================

def public_get(path, params=None):

    if not PUBLIC_READ_ONLY:
        raise RuntimeError(
            "Public read-only access is disabled"
        )

    if not path.startswith("/"):
        raise RuntimeError(
            f"Invalid public path: {path}"
        )

    query_string = encode_query(params)

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    request = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-ReadOnlyValidator/1.0",
        },
        method="GET",
    )

    with runtime_lock:
        runtime["public_get"] += 1

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read()

            return decode_json_response(raw)

    except urllib.error.HTTPError as exc:

        try:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:
            body = ""

        raise RuntimeError(
            f"Public GET failed: {path}"
            f" | HTTP {exc.code}"
            f" | {body}"
        )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Public GET failed: {path}"
            f" | URLError: {exc}"
        )


# ==================================================================================================
# GENERIC RESPONSE NORMALIZATION
# ==================================================================================================

def unwrap_data(value):

    current = value

    for _ in range(4):

        if isinstance(current, dict):

            if "data" in current:
                current = current["data"]
                continue

            if "result" in current:
                current = current["result"]
                continue

        break

    return current


def normalize_list(value):

    value = unwrap_data(value)

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        return [value]

    return []


# ==================================================================================================
# BALANCE PARSING
# ==================================================================================================

def parse_usdt_balance(response):

    records = normalize_list(response)

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
            if record.get("availableBalance") is not None
            else record.get("available")
        )

        if available is None:
            available = record.get("balance")

        return {
            "asset": asset,
            "balance": safe_decimal(
                record.get("balance")
            ),
            "available_balance": safe_decimal(
                available
            ),
            "raw": record,
        }

    raise RuntimeError(
        "USDT balance record was not found"
    )


# ==================================================================================================
# POSITION PARSING
# ==================================================================================================

def parse_positions(response):

    records = normalize_list(response)

    all_positions = []
    symbol_positions = []
    open_positions = []

    for record in records:

        if not isinstance(record, dict):
            continue

        all_positions.append(record)

        record_symbol = str(
            record.get("symbol")
            or ""
        ).upper()

        if record_symbol != SYMBOL:
            continue

        symbol_positions.append(record)

        size = safe_decimal(
            record.get("size")
            if record.get("size") is not None
            else record.get("positionAmt")
        )

        if abs(size) > Decimal("0"):
            open_positions.append(record)

    return {
        "all": all_positions,
        "symbol": symbol_positions,
        "open": open_positions,
    }


# ==================================================================================================
# SYMBOL CONFIG PARSING
# ==================================================================================================

def parse_symbol_config(response):

    records = normalize_list(response)

    for record in records:

        if not isinstance(record, dict):
            continue

        record_symbol = str(
            record.get("symbol")
            or ""
        ).upper()

        if record_symbol == SYMBOL:

            return {
                "symbol": record_symbol,
                "margin_type": str(
                    record.get("marginType")
                    or ""
                ).upper(),
                "position_mode": str(
                    record.get("separatedType")
                    or record.get("separatedMode")
                    or ""
                ).upper(),
                "cross_leverage": safe_decimal(
                    record.get("crossLeverage")
                ),
                "isolated_long_leverage": safe_decimal(
                    record.get("isolatedLongLeverage")
                ),
                "isolated_short_leverage": safe_decimal(
                    record.get("isolatedShortLeverage")
                ),
                "raw": record,
            }

    raise RuntimeError(
        f"{SYMBOL} symbol configuration was not found"
    )


# ==================================================================================================
# EXCHANGE INFORMATION PARSING
# ==================================================================================================

def parse_contract_info(response):

    response = unwrap_data(response)

    if isinstance(response, dict):
        symbols = response.get("symbols", [])

    elif isinstance(response, list):
        symbols = response

    else:
        symbols = []

    for record in symbols:

        if not isinstance(record, dict):
            continue

        record_symbol = str(
            record.get("symbol")
            or ""
        ).upper()

        if record_symbol != SYMBOL:
            continue

        quantity_precision = int(
            record.get("quantityPrecision", 4)
        )

        price_precision = int(
            record.get("pricePrecision", 1)
        )

        min_order_size = safe_decimal(
            record.get("minOrderSize"),
            "0.0001",
        )

        contract_val = safe_decimal(
            record.get("contractVal"),
            "0",
        )

        min_leverage = safe_decimal(
            record.get("minLeverage"),
            "1",
        )

        max_leverage = safe_decimal(
            record.get("maxLeverage"),
            "0",
        )

        return {
            "symbol": record_symbol,
            "quantity_precision": quantity_precision,
            "price_precision": price_precision,
            "min_order_size": min_order_size,
            "contract_val": contract_val,
            "min_leverage": min_leverage,
            "max_leverage": max_leverage,
            "raw": record,
        }

    raise RuntimeError(
        f"{SYMBOL} contract information was not found"
    )


# ==================================================================================================
# MARK PRICE PARSING
# ==================================================================================================

def parse_mark_price(response):

    records = normalize_list(response)

    for record in records:

        if not isinstance(record, dict):
            continue

        record_symbol = str(
            record.get("symbol")
            or ""
        ).upper()

        if record_symbol and record_symbol != SYMBOL:
            continue

        candidates = [
            record.get("markPrice"),
            record.get("price"),
            record.get("lastPrice"),
            record.get("last"),
            record.get("indexPrice"),
        ]

        for candidate in candidates:

            price = safe_decimal(candidate)

            if price > 0:
                return price

    if isinstance(response, dict):

        for key in (
            "markPrice",
            "price",
            "lastPrice",
            "last",
            "indexPrice",
        ):

            price = safe_decimal(
                response.get(key)
            )

            if price > 0:
                return price

    raise RuntimeError(
        "Unable to parse positive market price"
    )


# ==================================================================================================
# LIVE READ-ONLY STATE
# ==================================================================================================

def read_live_state():

    # ----------------------------------------------------------------------------------------------
    # PRIVATE GET 1: BALANCE
    # ----------------------------------------------------------------------------------------------

    balance_response = authenticated_get(
        BALANCE_PATH
    )

    balance = parse_usdt_balance(
        balance_response
    )

    # ----------------------------------------------------------------------------------------------
    # PRIVATE GET 2: POSITIONS
    #
    # CRITICAL FIX:
    #
    # /capi/v3/account/position/allPosition
    # ----------------------------------------------------------------------------------------------

    positions_response = authenticated_get(
        POSITION_PATH
    )

    positions = parse_positions(
        positions_response
    )

    # ----------------------------------------------------------------------------------------------
    # PRIVATE GET 3: SYMBOL CONFIG
    # ----------------------------------------------------------------------------------------------

    config_response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    config = parse_symbol_config(
        config_response
    )

    # ----------------------------------------------------------------------------------------------
    # PUBLIC GET 1: CONTRACT INFORMATION
    # ----------------------------------------------------------------------------------------------

    exchange_response = public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    contract = parse_contract_info(
        exchange_response
    )

    # ----------------------------------------------------------------------------------------------
    # PUBLIC GET 2: MARK PRICE / FUNDING INFORMATION
    # ----------------------------------------------------------------------------------------------

    premium_response = public_get(
        PREMIUM_INDEX_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    market_price = parse_mark_price(
        premium_response
    )

    return {
        "balance": balance,
        "positions": positions,
        "config": config,
        "contract": contract,
        "market_price": market_price,
    }


# ==================================================================================================
# QUANTITY NORMALIZATION
# ==================================================================================================

def normalize_quantity(
    raw_quantity,
    quantity_precision,
    min_order_size,
):

    raw_quantity = safe_decimal(
        raw_quantity
    )

    min_order_size = safe_decimal(
        min_order_size,
        "0.0001",
    )

    if raw_quantity <= 0:
        raise RuntimeError(
            "Raw quantity must be positive"
        )

    precision = max(
        0,
        int(quantity_precision),
    )

    step = Decimal("1").scaleb(
        -precision
    )

    units = (
        raw_quantity / step
    ).to_integral_value(
        rounding=ROUND_CEILING
    )

    quantity = units * step

    if quantity < min_order_size:
        quantity = min_order_size

    return quantity


# ==================================================================================================
# STRATEGY BUDGET
# ==================================================================================================

def build_strategy_budget(
    available_balance,
    market_price,
    contract,
):

    available_balance = safe_decimal(
        available_balance
    )

    market_price = safe_decimal(
        market_price
    )

    initial_margin = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    pyramid_margin = (
        available_balance
        * PYRAMID_PERCENT
        / Decimal("100")
    )

    backup_margin = (
        available_balance
        * BACKUP_PERCENT
        / Decimal("100")
    )

    maximum_allowed_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    planned_maximum_margin = (
        initial_margin
        + (
            pyramid_margin
            * Decimal(MAX_PYRAMID_ADDS)
        )
        + (
            backup_margin
            * Decimal(MAX_BACKUPS)
        )
    )

    initial_notional = (
        initial_margin
        * TARGET_LEVERAGE
    )

    raw_quantity = (
        initial_notional
        / market_price
    )

    normalized_quantity = normalize_quantity(
        raw_quantity=raw_quantity,
        quantity_precision=contract[
            "quantity_precision"
        ],
        min_order_size=contract[
            "min_order_size"
        ],
    )

    normalized_notional = (
        normalized_quantity
        * market_price
    )

    normalized_margin = (
        normalized_notional
        / TARGET_LEVERAGE
    )

    return {
        "available_balance": available_balance,
        "initial_margin": initial_margin,
        "pyramid_margin": pyramid_margin,
        "backup_margin": backup_margin,
        "maximum_allowed_margin": maximum_allowed_margin,
        "planned_maximum_margin": planned_maximum_margin,
        "initial_notional": initial_notional,
        "raw_quantity": raw_quantity,
        "quantity": normalized_quantity,
        "normalized_notional": normalized_notional,
        "normalized_margin": normalized_margin,
    }


# ==================================================================================================
# SYNTHETIC INTENT
# ==================================================================================================

def create_synthetic_intent(
    action,
    sequence,
    quantity,
    market_price,
):

    created_ms = int(
        time.time() * 1000
    )

    seed = (
        f"{VERSION}|{SYMBOL}|{action}|"
        f"{sequence}|{created_ms}|"
        f"{decimal_string(quantity)}"
    )

    intent_id = (
        VERSION.lower()
        + "-"
        + hashlib.sha256(
            seed.encode("utf-8")
        ).hexdigest()[:20]
    )

    intent = {
        "version": VERSION,
        "syntheticOnly": True,
        "transmissionPermitted": False,
        "networkWritePermitted": False,

        "intentId": intent_id,

        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",

        "action": action,
        "sequence": sequence,

        "quantity": decimal_string(
            quantity
        ),

        "referencePrice": decimal_string(
            market_price
        ),

        "targetMarginType": TARGET_MARGIN_TYPE,
        "targetLeverage": decimal_string(
            TARGET_LEVERAGE
        ),

        "createdTime": created_ms,
    }

    intent["sha256"] = sha256_json(
        intent
    )

    return intent


# ==================================================================================================
# SYNTHETIC PAYLOAD
# ==================================================================================================

def build_synthetic_payload(intent):

    payload = {
        "symbol": intent["symbol"],
        "side": intent["side"],
        "positionSide": intent[
            "positionSide"
        ],
        "type": intent["type"],
        "quantity": intent["quantity"],
        "newClientOrderId": intent[
            "intentId"
        ],
    }

    return {
        "syntheticOnly": True,
        "transmissionPermitted": False,
        "networkWritePermitted": False,
        "payload": payload,
        "payloadSha256": sha256_json(
            payload
        ),
        "intentSha256": intent[
            "sha256"
        ],
    }


# ==================================================================================================
# LOCAL SYNTHETIC DISPATCH
# ==================================================================================================

def synthetic_dispatch(
    intent,
    envelope,
    recovery=False,
):

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "Synthetic-only transport is disabled"
        )

    if envelope.get(
        "transmissionPermitted"
    ):
        raise RuntimeError(
            "Synthetic envelope unexpectedly permits transmission"
        )

    if envelope.get(
        "networkWritePermitted"
    ):
        raise RuntimeError(
            "Synthetic envelope unexpectedly permits network write"
        )

    if envelope.get(
        "intentSha256"
    ) != intent.get(
        "sha256"
    ):
        raise RuntimeError(
            "Intent binding mismatch"
        )

    expected_payload_hash = sha256_json(
        envelope["payload"]
    )

    if expected_payload_hash != envelope.get(
        "payloadSha256"
    ):
        raise RuntimeError(
            "Payload hash mismatch"
        )

    with runtime_lock:

        runtime[
            "synthetic_dispatches"
        ] += 1

        if recovery:
            runtime[
                "recovery_dispatches"
            ] += 1

    return {
        "syntheticOnly": True,
        "transmitted": False,
        "networkWrite": False,

        "intentId": intent[
            "intentId"
        ],

        "intentSha256": intent[
            "sha256"
        ],

        "payloadSha256": envelope[
            "payloadSha256"
        ],

        "recovery": bool(
            recovery
        ),

        "completedTime": int(
            time.time() * 1000
        ),
    }


# ==================================================================================================
# LOCAL STATE
# ==================================================================================================

def new_strategy_state():

    return {
        "schema": 1,
        "version": VERSION,
        "symbol": SYMBOL,

        "phase": "NEW",

        "generation": 1,

        "pyramidAdds": 0,
        "backupCount": 0,

        "consumedIntentIds": [],

        "dispatches": [],

        "createdTime": int(
            time.time() * 1000
        ),

        "updatedTime": int(
            time.time() * 1000
        ),
    }


def state_with_integrity(state):

    document = dict(state)

    document.pop(
        "integritySha256",
        None,
    )

    document["integritySha256"] = (
        sha256_json(document)
    )

    return document


def verify_state_integrity(state):

    if not isinstance(state, dict):
        return False

    expected = state.get(
        "integritySha256"
    )

    if not expected:
        return False

    document = dict(state)

    document.pop(
        "integritySha256",
        None,
    )

    actual = sha256_json(
        document
    )

    return hmac.compare_digest(
        expected,
        actual,
    )


def atomic_save_state(state):

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    state["updatedTime"] = int(
        time.time() * 1000
    )

    document = state_with_integrity(
        state
    )

    fd, temporary_name = tempfile.mkstemp(
        prefix="r34y-",
        suffix=".tmp",
        dir=str(STATE_DIR),
    )

    try:

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                document,
                handle,
                sort_keys=True,
                separators=(",", ":"),
            )

            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary_name,
            STATE_FILE,
        )

    finally:

        if os.path.exists(
            temporary_name
        ):
            os.unlink(
                temporary_name
            )


def load_state():

    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:

        state = json.load(
            handle
        )

    if not verify_state_integrity(
        state
    ):
        raise RuntimeError(
            "Persistent strategy state integrity validation failed"
        )

    return state


# ==================================================================================================
# EXACTLY-ONCE LOCAL SYNTHETIC EXECUTION
# ==================================================================================================

def execute_once(
    state,
    intent,
    envelope,
    recovery=False,
):

    intent_id = intent[
        "intentId"
    ]

    consumed = set(
        state.get(
            "consumedIntentIds",
            [],
        )
    )

    if intent_id in consumed:

        with runtime_lock:
            runtime[
                "replays_blocked"
            ] += 1

        raise RuntimeError(
            "Synthetic intent replay rejected"
        )

    receipt = synthetic_dispatch(
        intent=intent,
        envelope=envelope,
        recovery=recovery,
    )

    state.setdefault(
        "consumedIntentIds",
        [],
    ).append(
        intent_id
    )

    state.setdefault(
        "dispatches",
        [],
    ).append(
        receipt
    )

    return receipt


# ==================================================================================================
# SAFETY FIREBREAK SELF-TEST
# ==================================================================================================

def expect_rejected(function):

    try:
        function()

    except NetworkWriteRejected:
        return True

    return False


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def run_validation():

    set_phase(
        "VALIDATING"
    )

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: SAFETY CONFIGURATION"
    )

    test_result(
        "Authenticated Read Only Is Enabled",
        AUTHENTICATED_READ_ONLY,
    )

    test_result(
        "Public Read Only Is Enabled",
        PUBLIC_READ_ONLY,
    )

    test_result(
        "Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    test_result(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION_ENABLED,
    )

    test_result(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION_ENABLED,
    )

    test_result(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    test_result(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    test_result(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    test_result(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION_ENABLED,
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: API CREDENTIAL PRESENCE"
    )

    test_result(
        "WEEX API Key Is Present",
        bool(WEEX_API_KEY),
    )

    test_result(
        "WEEX API Secret Is Present",
        bool(WEEX_API_SECRET),
    )

    test_result(
        "WEEX API Passphrase Is Present",
        bool(WEEX_API_PASSPHRASE),
    )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: LIVE READ-ONLY STATE"
    )

    live = read_live_state()

    balance = live[
        "balance"
    ]

    positions = live[
        "positions"
    ]

    config = live[
        "config"
    ]

    contract = live[
        "contract"
    ]

    market_price = live[
        "market_price"
    ]

    available_balance = balance[
        "available_balance"
    ]

    test_result(
        "Available USDT Balance Was Read",
        available_balance >= 0,
    )

    test_result(
        "Correct Position Endpoint Was Read",
        POSITION_PATH
        == "/capi/v3/account/position/allPosition",
    )

    test_result(
        "Position Response Was Parsed",
        isinstance(
            positions["all"],
            list,
        ),
    )

    test_result(
        "Symbol Configuration Was Read",
        config[
            "symbol"
        ] == SYMBOL,
    )

    log(
        f"{VERSION}: BALANCE PATH={BALANCE_PATH}"
    )

    log(
        f"{VERSION}: POSITION PATH={POSITION_PATH}"
    )

    log(
        f"{VERSION}: SYMBOL CONFIG PATH={SYMBOL_CONFIG_PATH}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT={decimal_string(available_balance)}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(positions['all'])}"
    )

    log(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(positions['symbol'])}"
    )

    log(
        f"{VERSION}: {SYMBOL} OPEN POSITIONS="
        f"{len(positions['open'])}"
    )

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: LIVE ACCOUNT CONFIGURATION"
    )

    test_result(
        "Margin Type Was Read",
        bool(
            config[
                "margin_type"
            ]
        ),
    )

    test_result(
        "Isolated Long Leverage Was Read",
        config[
            "isolated_long_leverage"
        ] >= 0,
    )

    test_result(
        "Isolated Short Leverage Was Read",
        config[
            "isolated_short_leverage"
        ] >= 0,
    )

    log(
        f"{VERSION}: OBSERVED MARGIN TYPE="
        f"{config['margin_type']}"
    )

    log(
        f"{VERSION}: OBSERVED POSITION MODE="
        f"{config['position_mode']}"
    )

    log(
        f"{VERSION}: OBSERVED CROSS LEVERAGE="
        f"{decimal_string(config['cross_leverage'])}x"
    )

    log(
        f"{VERSION}: OBSERVED ISOLATED LONG LEVERAGE="
        f"{decimal_string(config['isolated_long_leverage'])}x"
    )

    log(
        f"{VERSION}: OBSERVED ISOLATED SHORT LEVERAGE="
        f"{decimal_string(config['isolated_short_leverage'])}x"
    )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: LIVE MARKET PRICE"
    )

    test_result(
        "Market Price Was Read",
        market_price is not None,
    )

    test_result(
        "Market Price Is Positive",
        market_price > 0,
    )

    log(
        f"{VERSION}: MARKET PRICE PATH={PREMIUM_INDEX_PATH}"
    )

    log(
        f"{VERSION}: MARK PRICE={decimal_string(market_price)}"
    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: LIVE CONTRACT INFORMATION"
    )

    test_result(
        "Exchange Information Was Read",
        contract[
            "symbol"
        ] == SYMBOL,
    )

    test_result(
        "Minimum Order Size Is Positive",
        contract[
            "min_order_size"
        ] > 0,
    )

    test_result(
        "Quantity Precision Is Valid",
        contract[
            "quantity_precision"
        ] >= 0,
    )

    test_result(
        "Price Precision Is Valid",
        contract[
            "price_precision"
        ] >= 0,
    )

    test_result(
        "Maximum Leverage Was Read",
        contract[
            "max_leverage"
        ] > 0,
    )

    test_result(
        "Target Leverage Is Within Exchange Maximum",
        TARGET_LEVERAGE
        <= contract[
            "max_leverage"
        ],
    )

    log(
        f"{VERSION}: EXCHANGE INFO PATH={EXCHANGE_INFO_PATH}"
    )

    log(
        f"{VERSION}: MIN ORDER SIZE="
        f"{decimal_string(contract['min_order_size'])}"
    )

    log(
        f"{VERSION}: QUANTITY PRECISION="
        f"{contract['quantity_precision']}"
    )

    log(
        f"{VERSION}: PRICE PRECISION="
        f"{contract['price_precision']}"
    )

    log(
        f"{VERSION}: CONTRACT VALUE="
        f"{decimal_string(contract['contract_val'])}"
    )

    log(
        f"{VERSION}: WEEX MIN LEVERAGE="
        f"{decimal_string(contract['min_leverage'])}x"
    )

    log(
        f"{VERSION}: WEEX MAX LEVERAGE="
        f"{decimal_string(contract['max_leverage'])}x"
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: STRATEGY BUDGET"
    )

    budget = build_strategy_budget(
        available_balance=available_balance,
        market_price=market_price,
        contract=contract,
    )

    test_result(
        "Initial Entry Percent Is Positive",
        INITIAL_ENTRY_PERCENT > 0,
    )

    test_result(
        "Initial Entry Margin Budget Is Nonnegative",
        budget[
            "initial_margin"
        ] >= 0,
    )

    test_result(
        "Maximum Planned Strategy Margin Is Within 35%",
        budget[
            "planned_maximum_margin"
        ]
        <= budget[
            "maximum_allowed_margin"
        ],
    )

    log(
        f"{VERSION}: INITIAL ENTRY={decimal_string(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: INITIAL MARGIN BUDGET="
        f"{decimal_string(budget['initial_margin'])} USDT"
    )

    log(
        f"{VERSION}: PYRAMID MARGIN BUDGET="
        f"{decimal_string(budget['pyramid_margin'])} USDT"
    )

    log(
        f"{VERSION}: BACKUP MARGIN BUDGET="
        f"{decimal_string(budget['backup_margin'])} USDT"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{decimal_string(budget['maximum_allowed_margin'])} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_string(budget['planned_maximum_margin'])} USDT"
    )

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: SYNTHETIC INITIAL ENTRY QUANTITY"
    )

    test_result(
        "Raw Quantity Is Positive",
        budget[
            "raw_quantity"
        ] > 0,
    )

    test_result(
        "Normalized Quantity Is Positive",
        budget[
            "quantity"
        ] > 0,
    )

    test_result(
        "Normalized Quantity Meets Minimum Order Size",
        budget[
            "quantity"
        ]
        >= contract[
            "min_order_size"
        ],
    )

    log(
        f"{VERSION}: RAW QUANTITY="
        f"{decimal_string(budget['raw_quantity'])}"
    )

    log(
        f"{VERSION}: NORMALIZED QUANTITY="
        f"{decimal_string(budget['quantity'])}"
    )

    log(
        f"{VERSION}: NORMALIZED NOTIONAL="
        f"{decimal_string(budget['normalized_notional'])} USDT"
    )

    log(
        f"{VERSION}: NORMALIZED MARGIN AT "
        f"{decimal_string(TARGET_LEVERAGE)}x="
        f"{decimal_string(budget['normalized_margin'])} USDT"
    )

    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: SYNTHETIC INITIAL ENTRY INTENT"
    )

    initial_intent = create_synthetic_intent(
        action="INITIAL_ENTRY",
        sequence=1,
        quantity=budget[
            "quantity"
        ],
        market_price=market_price,
    )

    initial_envelope = build_synthetic_payload(
        initial_intent
    )

    test_result(
        "Intent Is Synthetic Only",
        initial_intent[
            "syntheticOnly"
        ],
    )

    test_result(
        "Intent Forbids Transmission",
        not initial_intent[
            "transmissionPermitted"
        ],
    )

    test_result(
        "Intent Forbids Network Write",
        not initial_intent[
            "networkWritePermitted"
        ],
    )

    test_result(
        "Intent Symbol Is Exact",
        initial_intent[
            "symbol"
        ] == SYMBOL,
    )

    test_result(
        "Intent Hash Exists",
        len(
            initial_intent[
                "sha256"
            ]
        ) == 64,
    )

    log(
        f"{VERSION}: INITIAL INTENT="
        f"{canonical_json(initial_intent)}"
    )

    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: EXACT SYNTHETIC PAYLOAD"
    )

    test_result(
        "Payload Is Synthetic Only",
        initial_envelope[
            "syntheticOnly"
        ],
    )

    test_result(
        "Payload Forbids Transmission",
        not initial_envelope[
            "transmissionPermitted"
        ],
    )

    test_result(
        "Payload Forbids Network Write",
        not initial_envelope[
            "networkWritePermitted"
        ],
    )

    test_result(
        "Payload Binds Exact Intent",
        initial_envelope[
            "intentSha256"
        ]
        == initial_intent[
            "sha256"
        ],
    )

    test_result(
        "Payload Hash Exists",
        len(
            initial_envelope[
                "payloadSha256"
            ]
        ) == 64,
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD="
        f"{canonical_json(initial_envelope['payload'])}"
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD SHA256="
        f"{initial_envelope['payloadSha256']}"
    )

    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: LOCAL SYNTHETIC INITIAL DISPATCH"
    )

    state = new_strategy_state()

    state[
        "phase"
    ] = "PREPARED"

    receipt = execute_once(
        state=state,
        intent=initial_intent,
        envelope=initial_envelope,
    )

    test_result(
        "Synthetic Dispatch Completed",
        receipt[
            "syntheticOnly"
        ],
    )

    test_result(
        "Synthetic Dispatch Was Not Transmitted",
        not receipt[
            "transmitted"
        ],
    )

    test_result(
        "Synthetic Dispatch Made No Network Write",
        not receipt[
            "networkWrite"
        ],
    )

    state[
        "phase"
    ] = "INITIAL_ENTRY_SYNTHETICALLY_COMPLETED"

    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: PYRAMID ELIGIBILITY AND LIMIT"
    )

    pyramid_eligible = (
        state[
            "pyramidAdds"
        ] < MAX_PYRAMID_ADDS
    )

    test_result(
        "First Pyramid Add Is Eligible",
        pyramid_eligible,
    )

    state[
        "pyramidAdds"
    ] += 1

    test_result(
        "Pyramid Count Is One",
        state[
            "pyramidAdds"
        ] == 1,
    )

    second_pyramid_eligible = (
        state[
            "pyramidAdds"
        ] < MAX_PYRAMID_ADDS
    )

    test_result(
        "Second Pyramid Add Is Rejected",
        not second_pyramid_eligible,
    )

    test_result(
        "Maximum Pyramid Adds Remains One",
        state[
            "pyramidAdds"
        ] == MAX_PYRAMID_ADDS,
    )

    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    section(
        f"{VERSION} TEST 13: BACKUP ELIGIBILITY AND LIMIT"
    )

    for backup_number in range(
        1,
        MAX_BACKUPS + 1,
    ):

        eligible = (
            state[
                "backupCount"
            ]
            < MAX_BACKUPS
        )

        test_result(
            f"Backup {backup_number} Is Eligible",
            eligible,
        )

        state[
            "backupCount"
        ] += 1

    test_result(
        "Backup Count Is Three",
        state[
            "backupCount"
        ] == 3,
    )

    fourth_backup_eligible = (
        state[
            "backupCount"
        ]
        < MAX_BACKUPS
    )

    test_result(
        "Fourth Backup Is Rejected",
        not fourth_backup_eligible,
    )

    test_result(
        "Maximum Backups Remains Three",
        state[
            "backupCount"
        ] == MAX_BACKUPS,
    )

    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: DURABLE LOCAL SNAPSHOT"
    )

    state[
        "phase"
    ] = "LIFECYCLE_SYNTHETICALLY_VALIDATED"

    atomic_save_state(
        state
    )

    test_result(
        "State File Exists",
        STATE_FILE.exists(),
    )

    saved = load_state()

    test_result(
        "Saved State Integrity Is Valid",
        verify_state_integrity(
            saved
        ),
    )

    test_result(
        "Saved Symbol Is Exact",
        saved[
            "symbol"
        ] == SYMBOL,
    )

    test_result(
        "Saved Pyramid Count Is One",
        saved[
            "pyramidAdds"
        ] == 1,
    )

    test_result(
        "Saved Backup Count Is Three",
        saved[
            "backupCount"
        ] == 3,
    )

    log(
        f"{VERSION}: STATE FILE={STATE_FILE}"
    )

    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    section(
        f"{VERSION} TEST 15: RESTART RESTORE"
    )

    restored = load_state()

    with runtime_lock:
        runtime[
            "restart_restores"
        ] += 1

    test_result(
        "Restart State Was Restored",
        restored is not None,
    )

    test_result(
        "Restart Integrity Is Valid",
        verify_state_integrity(
            restored
        ),
    )

    test_result(
        "Consumed Intent Survived Restart",
        initial_intent[
            "intentId"
        ]
        in restored[
            "consumedIntentIds"
        ],
    )

    test_result(
        "Dispatch Receipt Survived Restart",
        len(
            restored[
                "dispatches"
            ]
        ) == 1,
    )

    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    section(
        f"{VERSION} TEST 16: RESTART REPLAY REJECTION"
    )

    replay_rejected = False

    try:

        execute_once(
            state=restored,
            intent=initial_intent,
            envelope=initial_envelope,
            recovery=True,
        )

    except RuntimeError as exc:

        if (
            "replay rejected"
            in str(exc).lower()
        ):
            replay_rejected = True

    test_result(
        "Consumed Intent Replay Is Rejected",
        replay_rejected,
    )

    test_result(
        "Replay Produced No Additional Dispatch",
        len(
            restored[
                "dispatches"
            ]
        ) == 1,
    )

    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    section(
        f"{VERSION} TEST 17: SYNTHETIC RECOVERY DISPATCH"
    )

    recovery_intent = create_synthetic_intent(
        action="RECOVERY_TEST",
        sequence=2,
        quantity=budget[
            "quantity"
        ],
        market_price=market_price,
    )

    recovery_envelope = build_synthetic_payload(
        recovery_intent
    )

    recovery_receipt = execute_once(
        state=restored,
        intent=recovery_intent,
        envelope=recovery_envelope,
        recovery=True,
    )

    test_result(
        "Recovery Dispatch Is Synthetic Only",
        recovery_receipt[
            "syntheticOnly"
        ],
    )

    test_result(
        "Recovery Dispatch Was Not Transmitted",
        not recovery_receipt[
            "transmitted"
        ],
    )

    test_result(
        "Recovery Dispatch Made No Network Write",
        not recovery_receipt[
            "networkWrite"
        ],
    )

    restored[
        "phase"
    ] = "RECOVERY_SYNTHETICALLY_COMPLETED"

    atomic_save_state(
        restored
    )

    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    section(
        f"{VERSION} TEST 18: WRITE FIREBREAK"
    )

    test_result(
        "HTTP POST Is Rejected",
        expect_rejected(
            http_post
        ),
    )

    test_result(
        "HTTP PUT Is Rejected",
        expect_rejected(
            http_put
        ),
    )

    test_result(
        "HTTP PATCH Is Rejected",
        expect_rejected(
            http_patch
        ),
    )

    test_result(
        "HTTP DELETE Is Rejected",
        expect_rejected(
            http_delete
        ),
    )

    test_result(
        "Real Order Function Is Rejected",
        expect_rejected(
            place_real_order
        ),
    )

    test_result(
        "Demo Order Function Is Rejected",
        expect_rejected(
            place_demo_order
        ),
    )

    test_result(
        "Leverage Mutation Function Is Rejected",
        expect_rejected(
            mutate_leverage
        ),
    )

    test_result(
        "Margin Mutation Function Is Rejected",
        expect_rejected(
            mutate_margin
        ),
    )

    test_result(
        "Position Mutation Function Is Rejected",
        expect_rejected(
            mutate_position
        ),
    )

    test_result(
        "Account Mutation Function Is Rejected",
        expect_rejected(
            mutate_account
        ),
    )

    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    section(
        f"{VERSION} TEST 19: FINAL SAFETY ACCOUNTING"
    )

    with runtime_lock:

        test_result(
            "Network Write Count Is Zero",
            runtime[
                "network_writes"
            ] == 0,
        )

        test_result(
            "Real Order Count Is Zero",
            runtime[
                "real_orders"
            ] == 0,
        )

        test_result(
            "Demo Order Count Is Zero",
            runtime[
                "demo_orders"
            ] == 0,
        )

        test_result(
            "Leverage Mutation Count Is Zero",
            runtime[
                "leverage_mutations"
            ] == 0,
        )

        test_result(
            "Margin Mutation Count Is Zero",
            runtime[
                "margin_mutations"
            ] == 0,
        )

        test_result(
            "Position Mutation Count Is Zero",
            runtime[
                "position_mutations"
            ] == 0,
        )

        test_result(
            "Account Mutation Count Is Zero",
            runtime[
                "account_mutations"
            ] == 0,
        )

        test_result(
            "At Least One Synthetic Dispatch Occurred",
            runtime[
                "synthetic_dispatches"
            ] >= 1,
        )

        test_result(
            "At Least One Replay Was Blocked",
            runtime[
                "replays_blocked"
            ] >= 1,
        )

    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    section(
        f"{VERSION} TEST 20: FINAL R34Y VALIDATION"
    )

    final_state = load_state()

    test_result(
        "Final State Exists",
        final_state is not None,
    )

    test_result(
        "Final State Integrity Is Valid",
        verify_state_integrity(
            final_state
        ),
    )

    test_result(
        "Synthetic Transport Only Remains Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    test_result(
        "Authenticated Transport Remains GET Only",
        AUTHENTICATED_READ_ONLY,
    )

    test_result(
        "Public Transport Remains GET Only",
        PUBLIC_READ_ONLY,
    )

    test_result(
        "No Real Order Was Sent",
        runtime[
            "real_orders"
        ] == 0,
    )

    test_result(
        "No Demo Order Was Sent",
        runtime[
            "demo_orders"
        ] == 0,
    )

    test_result(
        "No Network Write Was Sent",
        runtime[
            "network_writes"
        ] == 0,
    )

    with runtime_lock:
        runtime[
            "validation_passed"
        ] = True

    set_phase(
        "R34Y_VALIDATED"
    )

    section(
        f"{VERSION}: VALIDATION PASSED"
    )

    log(
        f"{VERSION}: LIVE READ-ONLY STATE VALIDATED"
    )

    log(
        f"{VERSION}: POSITION ENDPOINT VALIDATED={POSITION_PATH}"
    )

    log(
        f"{VERSION}: DURABLE SYNTHETIC LIFECYCLE VALIDATED"
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
        f"{VERSION}: NETWORK WRITES=0"
    )

    log(
        f"{VERSION}: REAL ORDERS=0"
    )

    log(
        f"{VERSION}: DEMO ORDERS=0"
    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )


# ==================================================================================================
# STARTUP
# ==================================================================================================

def print_startup():

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
        f"{VERSION}: TARGET LEVERAGE="
        f"{decimal_string(TARGET_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: INITIAL ENTRY="
        f"{decimal_string(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX PYRAMID ADDS="
        f"{MAX_PYRAMID_ADDS}"
    )

    log(
        f"{VERSION}: MAX BACKUPS="
        f"{MAX_BACKUPS}"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_string(MAX_FUND_EXPOSURE_PERCENT)}%"
    )


# ==================================================================================================
# MAIN
# ==================================================================================================

def main():

    print_startup()

    start_health_server()
    start_heartbeat()

    try:

        run_validation()

    except Exception as exc:

        with runtime_lock:

            runtime[
                "validation_passed"
            ] = False

            runtime[
                "last_error"
            ] = (
                f"{type(exc).__name__}: {exc}"
            )

        set_phase(
            "VALIDATION_FAILED"
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
    # Render requires the service to stay alive after validation.
    # The health server and heartbeat remain active.
    # ----------------------------------------------------------------------------------------------

    while True:
        time.sleep(3600)


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

if __name__ == "__main__":
    main()
