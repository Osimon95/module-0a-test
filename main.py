

# ============================================================
# R35P-F main.py
# AUTHENTICATED WEEX READ-ONLY RECONCILIATION
#
# PURPOSE:
#   1. Preserve confirmed R35P-E V2 ticker symbol:
#          cmt_btcusdt
#
#   2. Confirm authenticated WEEX V3 reads use:
#          BTCUSDT
#
#   3. Read ONLY:
#          - Public mark price
#          - Account balance
#          - BTCUSDT position
#          - BTCUSDT symbol configuration
#
#   4. Perform ZERO exchange writes.
#
# SAFETY:
#   REAL_ORDER_EXECUTION=False
#   FIRST_REAL_ORDER_ALLOWED=False
#   EXCHANGE_NETWORK_WRITES=0
#   ORDER_SUBMISSIONS=0
#   LEVERAGE_MUTATIONS=0
#   MARGIN_MODE_MUTATIONS=0
#   POSITION_MUTATIONS=0
#
# R35P-F MUST NOT:
#   - submit orders
#   - cancel orders
#   - modify leverage
#   - modify margin mode
#   - modify positions
# ============================================================

import os
import sys
import json
import time
import hmac
import base64
import hashlib
import socket
import threading
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ============================================================
# CONSTANTS
# ============================================================

UNIT = "R35P-F"

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"

CANONICAL_SYMBOL = "BTCUSDT"

# Confirmed by R35P-E:
V2_MARKET_SYMBOL = "cmt_btcusdt"

PUBLIC_MARK_PRICE_PATH = "/capi/v2/market/ticker"

ACCOUNT_BALANCE_PATH = "/capi/v3/account/balance"

SINGLE_POSITION_PATH = (
    "/capi/v3/account/position/singlePosition"
)

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100.0
TARGET_SHORT_LEVERAGE = 100.0

REQUEST_TIMEOUT_SECONDS = 15

HEARTBEAT_SECONDS = 30


# ============================================================
# HARD SAFETY FLAGS
# ============================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

ORDER_SUBMISSION_ENABLED = False


# ============================================================
# COUNTERS
# ============================================================

PUBLIC_MARKET_GETS = 0
AUTHENTICATED_WEEX_READS = 0

EXCHANGE_NETWORK_WRITES = 0

ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0


# ============================================================
# DIAGNOSTIC STATE
# ============================================================

failure_stage = None
exception_class = None
exception_message = None

dns_ok = False

public_mark_price_read_ok = False
mark_price = None
mark_price_field = None
response_market_symbol = None

credentials_present = False

balance_read_ok = False
available_balance = None
total_balance = None

position_read_ok = False
open_positions = None
position_response_count = None

symbol_config_read_ok = False
observed_margin_mode = None
observed_separated_type = None
observed_cross_leverage = None
observed_long_leverage = None
observed_short_leverage = None

authenticated_weex_read_ok = False
activation_env_match = False

test_status = "NOT_RUN"


# ============================================================
# BASIC HELPERS
# ============================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def separator():
    log("-" * 100)


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def bool_text(value):
    return "True" if bool(value) else "False"


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "status": "ok",
            "unit": UNIT,
            "symbol": CANONICAL_SYMBOL,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
        }

        body = json.dumps(payload).encode("utf-8")

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

    port = int(os.environ.get("PORT", "10000"))

    try:
        server = HTTPServer(
            ("0.0.0.0", port),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        log(
            f"{UNIT}: HEALTH SERVER STARTED "
            f"ON PORT {port}"
        )

    except Exception as exc:
        log(
            f"{UNIT}: HEALTH SERVER ERROR "
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# ABSOLUTE WRITE FIREBREAK
# ============================================================

def forbidden_exchange_write(
    method,
    path,
    body=None,
):
    """
    Any attempt to route a non-GET exchange request
    through R35P-F must immediately fail.

    This function NEVER performs network transmission.
    """

    global EXCHANGE_NETWORK_WRITES
    global ORDER_SUBMISSIONS
    global LEVERAGE_MUTATIONS
    global MARGIN_MODE_MUTATIONS
    global POSITION_MUTATIONS

    raise RuntimeError(
        f"{UNIT}: EXCHANGE WRITE HARD BLOCKED: "
        f"method={method} path={path}"
    )


# ============================================================
# LOW-LEVEL READ-ONLY HTTP
# ============================================================

def read_only_http_get(
    url,
    headers=None,
    authenticated=False,
):
    """
    The ONLY external HTTP transport allowed in R35P-F.

    GET ONLY.

    No POST.
    No PUT.
    No PATCH.
    No DELETE.
    """

    global PUBLIC_MARKET_GETS
    global AUTHENTICATED_WEEX_READS

    request = Request(
        url=url,
        headers=headers or {},
        method="GET",
    )

    if request.get_method().upper() != "GET":
        raise RuntimeError(
            f"{UNIT}: NON-GET REQUEST BLOCKED"
        )

    if authenticated:
        AUTHENTICATED_WEEX_READS += 1
    else:
        PUBLIC_MARKET_GETS += 1

    with urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        status = response.getcode()

        raw = response.read().decode(
            "utf-8",
            errors="replace",
        )

        return status, raw


# ============================================================
# DNS TEST
# ============================================================

def test_dns():

    global dns_ok

    separator()
    log(f"{UNIT}: DNS")
    separator()

    host = "api-contract.weex.com"

    try:

        resolved = socket.gethostbyname(host)

        dns_ok = bool(resolved)

        log(f"HOST={host}")
        log(f"RESOLVED_IP={resolved}")
        log(f"DNS_OK={bool_text(dns_ok)}")

    except Exception as exc:

        dns_ok = False

        log(f"HOST={host}")
        log("RESOLVED_IP=UNKNOWN")
        log("DNS_OK=False")
        log(
            f"DNS_EXCEPTION="
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# PUBLIC V2 MARK PRICE
# ============================================================

def read_public_mark_price():

    global public_mark_price_read_ok
    global mark_price
    global mark_price_field
    global response_market_symbol

    separator()
    log(f"{UNIT}: PUBLIC V2 MARK PRICE")
    separator()

    query = urlencode(
        {
            "symbol": V2_MARKET_SYMBOL,
        }
    )

    url = (
        WEEX_CONTRACT_BASE
        + PUBLIC_MARK_PRICE_PATH
        + "?"
        + query
    )

    log(
        f"CANONICAL_SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"V2_MARKET_SYMBOL="
        f"{V2_MARKET_SYMBOL}"
    )

    log(
        f"PATH="
        f"{PUBLIC_MARK_PRICE_PATH}"
    )

    status, raw = read_only_http_get(
        url,
        authenticated=False,
    )

    log(f"HTTP_STATUS={status}")

    if status != 200:
        raise RuntimeError(
            f"PUBLIC_MARK_HTTP_STATUS_{status}"
        )

    data = json.loads(raw)

    # WEEX may return either an object,
    # list, or wrapped object.
    candidates = []

    if isinstance(data, dict):

        candidates.append(data)

        inner = data.get("data")

        if isinstance(inner, dict):
            candidates.append(inner)

        elif isinstance(inner, list):
            candidates.extend(inner)

    elif isinstance(data, list):

        candidates.extend(data)

    selected = None

    for item in candidates:

        if not isinstance(item, dict):
            continue

        symbol_value = (
            item.get("symbol")
            or item.get("contract")
        )

        if symbol_value == V2_MARKET_SYMBOL:
            selected = item
            break

    if selected is None:

        for item in candidates:

            if isinstance(item, dict):
                selected = item
                break

    if selected is None:
        raise RuntimeError(
            "PUBLIC_MARK_RESPONSE_OBJECT_NOT_FOUND"
        )

    response_market_symbol = (
        selected.get("symbol")
        or selected.get("contract")
    )

    candidate_fields = [
        "markPrice",
        "mark_price",
        "mark",
    ]

    found_value = None
    found_field = None

    for field in candidate_fields:

        if field in selected:

            value = safe_float(
                selected.get(field)
            )

            if value is not None:
                found_value = value
                found_field = field
                break

    if found_value is None:
        raise RuntimeError(
            "MARK_PRICE_FIELD_NOT_FOUND"
        )

    if found_value <= 0:
        raise RuntimeError(
            "MARK_PRICE_NOT_POSITIVE"
        )

    if (
        response_market_symbol
        and response_market_symbol
        != V2_MARKET_SYMBOL
    ):
        raise RuntimeError(
            "PUBLIC_RESPONSE_SYMBOL_MISMATCH"
        )

    mark_price = found_value
    mark_price_field = found_field

    public_mark_price_read_ok = True

    log(
        f"RESPONSE_SYMBOL="
        f"{response_market_symbol}"
    )

    log(
        f"RESPONSE_SYMBOL_MATCH="
        f"{bool_text(response_market_symbol == V2_MARKET_SYMBOL)}"
    )

    log(
        f"MARK_PRICE="
        f"{mark_price}"
    )

    log(
        f"MARK_PRICE_FIELD="
        f"{mark_price_field}"
    )

    log(
        "PUBLIC_MARK_PRICE_READ_OK=True"
    )


# ============================================================
# WEEX AUTHENTICATION
# ============================================================

def get_credentials():

    api_key = (
        os.environ.get("WEEX_API_KEY", "")
        .strip()
    )

    api_secret = (
        os.environ.get("WEEX_API_SECRET", "")
        .strip()
    )

    api_passphrase = (
        os.environ.get(
            "WEEX_API_PASSPHRASE",
            "",
        )
        .strip()
    )

    return (
        api_key,
        api_secret,
        api_passphrase,
    )


def create_signature(
    secret,
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    """
    WEEX authenticated signature.

    Query string must NOT begin with '?' here.
    """

    method = method.upper()

    if method != "GET":
        raise RuntimeError(
            f"{UNIT}: AUTHENTICATED "
            f"NON-GET SIGNING BLOCKED"
        )

    if query_string:

        prehash = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        prehash = (
            timestamp
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    signature = base64.b64encode(
        digest
    ).decode("utf-8")

    return signature


def authenticated_get(
    request_path,
    params=None,
):

    api_key, api_secret, passphrase = (
        get_credentials()
    )

    if not api_key:
        raise RuntimeError(
            "WEEX_API_KEY_MISSING"
        )

    if not api_secret:
        raise RuntimeError(
            "WEEX_API_SECRET_MISSING"
        )

    if not passphrase:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE_MISSING"
        )

    query_string = ""

    if params:

        query_string = urlencode(params)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = create_signature(
        secret=api_secret,
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = (
        WEEX_CONTRACT_BASE
        + request_path
    )

    if query_string:
        url += "?" + query_string

    status, raw = read_only_http_get(
        url,
        headers=headers,
        authenticated=True,
    )

    if status != 200:
        raise RuntimeError(
            f"AUTH_HTTP_STATUS_{status}"
        )

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        raise RuntimeError(
            "AUTH_RESPONSE_JSON_PARSE_FAILED"
        )


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_list_response(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        inner = data.get("data")

        if isinstance(inner, list):
            return inner

        if isinstance(inner, dict):
            return [inner]

        return [data]

    return []


def find_symbol_object(
    data,
    symbol,
):

    items = normalize_list_response(data)

    for item in items:

        if not isinstance(item, dict):
            continue

        if item.get("symbol") == symbol:
            return item

    return None


# ============================================================
# CREDENTIAL CHECK
# ============================================================

def check_credentials():

    global credentials_present

    separator()
    log(f"{UNIT}: CREDENTIAL CHECK")
    separator()

    key, secret, passphrase = (
        get_credentials()
    )

    key_ok = bool(key)
    secret_ok = bool(secret)
    passphrase_ok = bool(passphrase)

    credentials_present = (
        key_ok
        and secret_ok
        and passphrase_ok
    )

    log(
        f"WEEX_API_KEY_PRESENT="
        f"{bool_text(key_ok)}"
    )

    log(
        f"WEEX_API_SECRET_PRESENT="
        f"{bool_text(secret_ok)}"
    )

    log(
        f"WEEX_API_PASSPHRASE_PRESENT="
        f"{bool_text(passphrase_ok)}"
    )

    log(
        f"CREDENTIALS_PRESENT="
        f"{bool_text(credentials_present)}"
    )

    # Never print credentials.


# ============================================================
# AUTHENTICATED BALANCE
# ============================================================

def read_balance():

    global balance_read_ok
    global available_balance
    global total_balance

    separator()
    log(f"{UNIT}: AUTHENTICATED BALANCE")
    separator()

    log(
        f"PATH={ACCOUNT_BALANCE_PATH}"
    )

    data = authenticated_get(
        ACCOUNT_BALANCE_PATH
    )

    items = normalize_list_response(data)

    usdt = None

    for item in items:

        if not isinstance(item, dict):
            continue

        if (
            str(item.get("asset", "")).upper()
            == "USDT"
        ):
            usdt = item
            break

    if usdt is None:
        raise RuntimeError(
            "USDT_BALANCE_OBJECT_NOT_FOUND"
        )

    available = safe_float(
        usdt.get("availableBalance")
    )

    balance = safe_float(
        usdt.get("balance")
    )

    if available is None:
        raise RuntimeError(
            "AVAILABLE_BALANCE_NOT_NUMERIC"
        )

    if balance is None:
        raise RuntimeError(
            "TOTAL_BALANCE_NOT_NUMERIC"
        )

    available_balance = available
    total_balance = balance

    balance_read_ok = True

    log("ASSET=USDT")

    log(
        f"AVAILABLE_BALANCE="
        f"{available_balance}"
    )

    log(
        f"TOTAL_BALANCE="
        f"{total_balance}"
    )

    log(
        "BALANCE_READ_OK=True"
    )


# ============================================================
# AUTHENTICATED POSITION
# ============================================================

def read_position():

    global position_read_ok
    global open_positions
    global position_response_count

    separator()
    log(f"{UNIT}: AUTHENTICATED POSITION")
    separator()

    log(
        f"CANONICAL_SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"PATH={SINGLE_POSITION_PATH}"
    )

    data = authenticated_get(
        SINGLE_POSITION_PATH,
        {
            "symbol": CANONICAL_SYMBOL,
        },
    )

    items = normalize_list_response(data)

    relevant = []

    for item in items:

        if not isinstance(item, dict):
            continue

        item_symbol = item.get("symbol")

        if (
            item_symbol is None
            or item_symbol == CANONICAL_SYMBOL
        ):
            relevant.append(item)

    position_response_count = len(
        relevant
    )

    active_count = 0

    for item in relevant:

        size = safe_float(
            item.get("size")
        )

        if size is None:

            # Empty position objects should not
            # automatically be counted active.
            continue

        if abs(size) > 0:
            active_count += 1

    open_positions = active_count

    position_read_ok = True

    log(
        f"POSITION_RESPONSE_COUNT="
        f"{position_response_count}"
    )

    log(
        f"OPEN_POSITIONS="
        f"{open_positions}"
    )

    log(
        f"BTCUSDT_FLAT="
        f"{bool_text(open_positions == 0)}"
    )

    log(
        "POSITION_READ_OK=True"
    )


# ============================================================
# AUTHENTICATED SYMBOL CONFIG
# ============================================================

def read_symbol_config():

    global symbol_config_read_ok
    global observed_margin_mode
    global observed_separated_type
    global observed_cross_leverage
    global observed_long_leverage
    global observed_short_leverage

    separator()
    log(f"{UNIT}: AUTHENTICATED SYMBOL CONFIG")
    separator()

    log(
        f"CANONICAL_SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"PATH={SYMBOL_CONFIG_PATH}"
    )

    data = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": CANONICAL_SYMBOL,
        },
    )

    config = find_symbol_object(
        data,
        CANONICAL_SYMBOL,
    )

    if config is None:
        raise RuntimeError(
            "BTCUSDT_SYMBOL_CONFIG_NOT_FOUND"
        )

    response_symbol = config.get(
        "symbol"
    )

    if response_symbol != CANONICAL_SYMBOL:
        raise RuntimeError(
            "SYMBOL_CONFIG_RESPONSE_SYMBOL_MISMATCH"
        )

    observed_margin_mode = config.get(
        "marginType"
    )

    observed_separated_type = config.get(
        "separatedType"
    )

    observed_cross_leverage = safe_float(
        config.get("crossLeverage")
    )

    observed_long_leverage = safe_float(
        config.get(
            "isolatedLongLeverage"
        )
    )

    observed_short_leverage = safe_float(
        config.get(
            "isolatedShortLeverage"
        )
    )

    symbol_config_read_ok = True

    log(
        f"RESPONSE_SYMBOL="
        f"{response_symbol}"
    )

    log(
        f"MARGIN_MODE="
        f"{observed_margin_mode}"
    )

    log(
        f"SEPARATED_TYPE="
        f"{observed_separated_type}"
    )

    log(
        f"CROSS_LEVERAGE="
        f"{observed_cross_leverage}"
    )

    log(
        f"LONG_LEVERAGE="
        f"{observed_long_leverage}"
    )

    log(
        f"SHORT_LEVERAGE="
        f"{observed_short_leverage}"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{bool_text(observed_margin_mode == TARGET_MARGIN_MODE)}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{bool_text(observed_long_leverage == TARGET_LONG_LEVERAGE)}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{bool_text(observed_short_leverage == TARGET_SHORT_LEVERAGE)}"
    )

    log(
        "SYMBOL_CONFIG_READ_OK=True"
    )


# ============================================================
# SAFETY VALIDATION
# ============================================================

def safety_invariants_ok():

    return all(
        [
            REAL_ORDER_EXECUTION is False,
            FIRST_REAL_ORDER_ALLOWED is False,
            DEMO_ORDER_EXECUTION is False,

            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,

            LEVERAGE_MUTATION_ENABLED is False,
            MARGIN_MODE_MUTATION_ENABLED is False,
            POSITION_MUTATION_ENABLED is False,

            ORDER_SUBMISSION_ENABLED is False,

            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,
        ]
    )


# ============================================================
# FINAL RECONCILIATION
# ============================================================

def reconcile():

    global authenticated_weex_read_ok
    global activation_env_match
    global test_status

    authenticated_weex_read_ok = all(
        [
            balance_read_ok,
            position_read_ok,
            symbol_config_read_ok,
        ]
    )

    activation_env_match = all(
        [
            public_mark_price_read_ok,
            authenticated_weex_read_ok,
            open_positions == 0,
            observed_margin_mode
            == TARGET_MARGIN_MODE,
            observed_long_leverage
            == TARGET_LONG_LEVERAGE,
            observed_short_leverage
            == TARGET_SHORT_LEVERAGE,
            safety_invariants_ok(),
        ]
    )

    if (
        public_mark_price_read_ok
        and authenticated_weex_read_ok
        and safety_invariants_ok()
    ):
        test_status = "PASS"
    else:
        test_status = "FAIL"


# ============================================================
# REPORT
# ============================================================

def print_report():

    separator()
    log(f"{UNIT}: ERROR DIAGNOSTIC")
    separator()

    log(
        f"FAILURE_STAGE={failure_stage}"
    )

    log(
        f"EXCEPTION_CLASS={exception_class}"
    )

    log(
        f"EXCEPTION_MESSAGE="
        f"{exception_message}"
    )

    separator()
    log(f"{UNIT}: SAFETY")
    separator()

    log(
        f"PUBLIC_MARKET_GETS="
        f"{PUBLIC_MARKET_GETS}"
    )

    log(
        f"AUTHENTICATED_WEEX_READS="
        f"{AUTHENTICATED_WEEX_READS}"
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
        f"LEVERAGE_MUTATIONS="
        f"{LEVERAGE_MUTATIONS}"
    )

    log(
        f"MARGIN_MODE_MUTATIONS="
        f"{MARGIN_MODE_MUTATIONS}"
    )

    log(
        f"POSITION_MUTATIONS="
        f"{POSITION_MUTATIONS}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{bool_text(REAL_ORDER_EXECUTION)}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{bool_text(FIRST_REAL_ORDER_ALLOWED)}"
    )

    log(
        f"SAFETY_INVARIANTS_OK="
        f"{bool_text(safety_invariants_ok())}"
    )

    separator()
    log(f"{UNIT} RESULT")
    separator()

    log(
        "TEST="
        "AUTHENTICATED_V3_BTCUSDT_"
        "READ_ONLY_RECONCILIATION"
    )

    log(
        f"CANONICAL_SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"V2_MARKET_SYMBOL="
        f"{V2_MARKET_SYMBOL}"
    )

    log(
        f"DNS_OK="
        f"{bool_text(dns_ok)}"
    )

    log(
        f"CREDENTIALS_PRESENT="
        f"{bool_text(credentials_present)}"
    )

    log(
        f"PUBLIC_MARK_PRICE_READ_OK="
        f"{bool_text(public_mark_price_read_ok)}"
    )

    log(
        f"MARK_PRICE="
        f"{mark_price}"
    )

    log(
        f"BALANCE_READ_OK="
        f"{bool_text(balance_read_ok)}"
    )

    log(
        f"AVAILABLE_BALANCE="
        f"{available_balance}"
    )

    log(
        f"POSITION_READ_OK="
        f"{bool_text(position_read_ok)}"
    )

    log(
        f"OPEN_POSITIONS="
        f"{open_positions}"
    )

    log(
        f"SYMBOL_CONFIG_READ_OK="
        f"{bool_text(symbol_config_read_ok)}"
    )

    log(
        f"MARGIN_MODE="
        f"{observed_margin_mode}"
    )

    log(
        f"SEPARATED_TYPE="
        f"{observed_separated_type}"
    )

    log(
        f"CROSS_LEVERAGE="
        f"{observed_cross_leverage}"
    )

    log(
        f"LONG_LEVERAGE="
        f"{observed_long_leverage}"
    )

    log(
        f"SHORT_LEVERAGE="
        f"{observed_short_leverage}"
    )

    log(
        f"AUTHENTICATED_WEEX_READ_OK="
        f"{bool_text(authenticated_weex_read_ok)}"
    )

    log(
        f"ACTIVATION_ENV_MATCH="
        f"{bool_text(activation_env_match)}"
    )

    log(
        f"PUBLIC_MARKET_GETS="
        f"{PUBLIC_MARKET_GETS}"
    )

    log(
        f"AUTHENTICATED_WEEX_READS="
        f"{AUTHENTICATED_WEEX_READS}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{bool_text(REAL_ORDER_EXECUTION)}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{bool_text(FIRST_REAL_ORDER_ALLOWED)}"
    )

    log(
        f"STATUS={test_status}"
    )

    if test_status == "PASS":

        log(
            "R35P-E_ROOT_CAUSE_FIX="
            "PRESERVED"
        )

        log(
            "V2_MARKET_SYMBOL_FORMAT="
            "cmt_btcusdt"
        )

        log(
            "V3_AUTH_SYMBOL_FORMAT="
            "BTCUSDT"
        )

        if activation_env_match:

            log(
                "RECONCILIATION="
                "FULL_MATCH"
            )

            log(
                "NEXT_UNIT=R35P-G"
            )

        else:

            blockers = []

            if open_positions != 0:
                blockers.append(
                    "BTCUSDT_NOT_FLAT"
                )

            if (
                observed_margin_mode
                != TARGET_MARGIN_MODE
            ):
                blockers.append(
                    "MARGIN_MODE_MISMATCH"
                )

            if (
                observed_long_leverage
                != TARGET_LONG_LEVERAGE
            ):
                blockers.append(
                    "LONG_LEVERAGE_MISMATCH"
                )

            if (
                observed_short_leverage
                != TARGET_SHORT_LEVERAGE
            ):
                blockers.append(
                    "SHORT_LEVERAGE_MISMATCH"
                )

            if blockers:

                log(
                    "RECONCILIATION_BLOCKERS="
                    + ",".join(blockers)
                )

            log(
                "NEXT_UNIT="
                "R35P-G_DIAGNOSTIC"
            )

    else:

        log(
            "NEXT_UNIT="
            "R35P-F_DIAGNOSE_FAILED_READ"
        )

    separator()


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: HEARTBEAT={heartbeat} "
            f"PUBLIC_MARK_PRICE_READ_OK="
            f"{bool_text(public_mark_price_read_ok)} "
            f"MARK_PRICE={mark_price} "
            f"BALANCE_READ_OK="
            f"{bool_text(balance_read_ok)} "
            f"POSITION_READ_OK="
            f"{bool_text(position_read_ok)} "
            f"OPEN_POSITIONS={open_positions} "
            f"SYMBOL_CONFIG_READ_OK="
            f"{bool_text(symbol_config_read_ok)} "
            f"AUTHENTICATED_WEEX_READ_OK="
            f"{bool_text(authenticated_weex_read_ok)} "
            f"ACTIVATION_ENV_MATCH="
            f"{bool_text(activation_env_match)} "
            f"TEST_STATUS={test_status} "
            f"PUBLIC_MARKET_GETS="
            f"{PUBLIC_MARKET_GETS} "
            f"AUTHENTICATED_WEEX_READS="
            f"{AUTHENTICATED_WEEX_READS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION="
            f"{bool_text(REAL_ORDER_EXECUTION)}"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================
# MAIN
# ============================================================

def main():

    global failure_stage
    global exception_class
    global exception_message
    global test_status

    start_health_server()

    separator()
    log(f"{UNIT}: MAIN.PY ENTERED")
    separator()

    log(
        f"{UNIT}: CANONICAL SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"{UNIT}: V2 MARKET SYMBOL="
        f"{V2_MARKET_SYMBOL}"
    )

    log(
        f"{UNIT}: WEEX CONTRACT BASE="
        f"{WEEX_CONTRACT_BASE}"
    )

    log(
        f"{UNIT}: PUBLIC MARK PRICE PATH="
        f"{PUBLIC_MARK_PRICE_PATH}"
    )

    log(
        f"{UNIT}: BALANCE PATH="
        f"{ACCOUNT_BALANCE_PATH}"
    )

    log(
        f"{UNIT}: POSITION PATH="
        f"{SINGLE_POSITION_PATH}"
    )

    log(
        f"{UNIT}: SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    log(
        f"{UNIT}: TARGET MARGIN MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"{UNIT}: TARGET LONG LEVERAGE="
        f"{TARGET_LONG_LEVERAGE:.0f}x"
    )

    log(
        f"{UNIT}: TARGET SHORT LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE:.0f}x"
    )

    separator()
    log(f"{UNIT}: WRITE FIREBREAK")
    separator()

    log(
        "REAL_ORDER_EXECUTION=False"
    )

    log(
        "FIRST_REAL_ORDER_ALLOWED=False"
    )

    log(
        "DEMO_ORDER_EXECUTION=False"
    )

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED=False"
    )

    log(
        "ORDER_SUBMISSION_ENABLED=False"
    )

    log(
        "LEVERAGE_MUTATION_ENABLED=False"
    )

    log(
        "MARGIN_MODE_MUTATION_ENABLED=False"
    )

    log(
        "POSITION_MUTATION_ENABLED=False"
    )

    try:

        failure_stage = "DNS"

        test_dns()

        if not dns_ok:
            raise RuntimeError(
                "DNS_RESOLUTION_FAILED"
            )

        failure_stage = "CREDENTIAL_CHECK"

        check_credentials()

        if not credentials_present:
            raise RuntimeError(
                "WEEX_CREDENTIALS_MISSING"
            )

        # --------------------------------------------
        # Preserve R35P-E success.
        # --------------------------------------------

        failure_stage = "PUBLIC_MARK_PRICE"

        read_public_mark_price()

        # --------------------------------------------
        # R35P-F authenticated reads.
        # --------------------------------------------

        failure_stage = "AUTH_BALANCE"

        read_balance()

        failure_stage = "AUTH_POSITION"

        read_position()

        failure_stage = "AUTH_SYMBOL_CONFIG"

        read_symbol_config()

        failure_stage = None
        exception_class = None
        exception_message = None

    except HTTPError as exc:

        exception_class = type(exc).__name__

        try:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            body = ""

        exception_message = (
            f"HTTP {exc.code}: {body}"
        )

        log(
            f"{UNIT}: HTTP ERROR "
            f"AT STAGE={failure_stage}"
        )

        log(
            f"{UNIT}: "
            f"{exception_message}"
        )

    except URLError as exc:

        exception_class = type(exc).__name__

        exception_message = str(
            exc.reason
        )

        log(
            f"{UNIT}: URL ERROR "
            f"AT STAGE={failure_stage}: "
            f"{exception_message}"
        )

    except Exception as exc:

        exception_class = type(exc).__name__

        exception_message = str(exc)

        log(
            f"{UNIT}: ERROR "
            f"AT STAGE={failure_stage}: "
            f"{exception_class}: "
            f"{exception_message}"
        )

        traceback.print_exc()

    # --------------------------------------------
    # Always reconcile and report.
    # --------------------------------------------

    reconcile()

    print_report()

    # --------------------------------------------
    # Final invariant assertion.
    # --------------------------------------------

    if not safety_invariants_ok():

        raise RuntimeError(
            f"{UNIT}: SAFETY INVARIANT FAILURE"
        )

    # --------------------------------------------
    # Keep Render service alive.
    # --------------------------------------------

    heartbeat_loop()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

