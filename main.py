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
