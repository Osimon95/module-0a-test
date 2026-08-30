

#!/usr/bin/env python3
# ============================================================
# R35P-G
# COMPOSITE ACTIVATION GATE
#
# PURPOSE
# ------------------------------------------------------------
# Preserve the proven R35P-F symbol mapping:
#
#   Public V2 market symbol:
#       cmt_btcusdt
#
#   Authenticated V3 account symbol:
#       BTCUSDT
#
# Then combine the already-proven read-only checks into one
# activation-environment gate.
#
# THIS UNIT MUST NOT:
#   - submit an order
#   - create a real order envelope
#   - mutate leverage
#   - mutate margin mode
#   - mutate positions
#   - perform any authenticated POST/PUT/PATCH/DELETE
#
# REAL ORDER EXECUTION REMAINS HARD DISABLED.
# ============================================================

import os
import json
import time
import hmac
import base64
import hashlib
import socket
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ============================================================
# VERSION
# ============================================================

VERSION = "R35P-G"


# ============================================================
# CANONICAL SYMBOLS
# ============================================================

CANONICAL_SYMBOL = "BTCUSDT"

# R35P-E / R35P-F root-cause fix:
V2_MARKET_SYMBOL = "cmt_btcusdt"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100.0
TARGET_SHORT_LEVERAGE = 100.0


# ============================================================
# WEEX ENDPOINTS
# ============================================================

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"

PUBLIC_MARK_PRICE_PATH = "/capi/v2/market/ticker"

BALANCE_PATH = "/capi/v3/account/balance"

POSITION_PATH = "/capi/v3/account/position/singlePosition"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"


# ============================================================
# HARD SAFETY FIREBREAK
# ============================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False

ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False


# ============================================================
# NETWORK COUNTERS
# ============================================================

PUBLIC_MARKET_GETS = 0
AUTHENTICATED_WEEX_READS = 0

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0


# ============================================================
# RESULT STATE
# ============================================================

DNS_OK = False
CREDENTIALS_PRESENT = False

PUBLIC_MARK_PRICE_READ_OK = False
MARK_PRICE = None

BALANCE_READ_OK = False
AVAILABLE_BALANCE = None
TOTAL_BALANCE = None

POSITION_READ_OK = False
OPEN_POSITIONS = None
BTCUSDT_FLAT = False

SYMBOL_CONFIG_READ_OK = False
MARGIN_MODE = None
SEPARATED_TYPE = None
CROSS_LEVERAGE = None
LONG_LEVERAGE = None
SHORT_LEVERAGE = None

MARGIN_MODE_MATCH = False
LONG_LEVERAGE_MATCH = False
SHORT_LEVERAGE_MATCH = False

AUTHENTICATED_WEEX_READ_OK = False
ACTIVATION_ENV_MATCH = False

POSITIVE_BALANCE_OK = False

SAFETY_INVARIANTS_OK = False

COMPOSITE_ACTIVATION_GATE_READY = False

TEST_STATUS = "NOT_RUN"

FAILURE_STAGE = None
EXCEPTION_CLASS = None
EXCEPTION_MESSAGE = None


# ============================================================
# LOGGING
# ============================================================

DIVIDER = "-" * 100


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def section(title):
    log(DIVIDER)
    log(f"{VERSION}: {title}")
    log(DIVIDER)


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.end_headers()
            return

        body = {
            "version": VERSION,
            "status": TEST_STATUS,
            "canonical_symbol": CANONICAL_SYMBOL,
            "v2_market_symbol": V2_MARKET_SYMBOL,
            "dns_ok": DNS_OK,
            "credentials_present": CREDENTIALS_PRESENT,
            "public_mark_price_read_ok": PUBLIC_MARK_PRICE_READ_OK,
            "balance_read_ok": BALANCE_READ_OK,
            "position_read_ok": POSITION_READ_OK,
            "symbol_config_read_ok": SYMBOL_CONFIG_READ_OK,
            "btc_usdt_flat": BTCUSDT_FLAT,
            "activation_env_match": ACTIVATION_ENV_MATCH,
            "composite_activation_gate_ready":
                COMPOSITE_ACTIVATION_GATE_READY,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "first_real_order_allowed": FIRST_REAL_ORDER_ALLOWED,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
        }

        encoded = json.dumps(body).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(encoded)),
        )
        self.end_headers()

        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))

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
        f"{VERSION}: HEALTH SERVER STARTED "
        f"ON PORT {port}"
    )


# ============================================================
# CREDENTIALS
# ============================================================

def get_credentials():

    api_key = os.environ.get(
        "WEEX_API_KEY",
        "",
    ).strip()

    api_secret = os.environ.get(
        "WEEX_API_SECRET",
        "",
    ).strip()

    api_passphrase = os.environ.get(
        "WEEX_API_PASSPHRASE",
        "",
    ).strip()

    return (
        api_key,
        api_secret,
        api_passphrase,
    )


# ============================================================
# AUTH SIGNATURE
# ============================================================

def make_signature(
    timestamp,
    method,
    request_path,
    query_string,
    body,
    secret,
):

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
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ============================================================
# PUBLIC GET
# ============================================================

def public_get(path, params=None):

    global PUBLIC_MARKET_GETS

    if params is None:
        params = {}

    query_string = urlencode(params)

    url = WEEX_CONTRACT_BASE + path

    if query_string:
        url += "?" + query_string

    request = Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}/1.0",
        },
    )

    PUBLIC_MARKET_GETS += 1

    try:
        with urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            return status, json.loads(raw)

    except HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        try:
            body = json.loads(raw)
        except Exception:
            body = raw

        raise RuntimeError(
            f"HTTP {exc.code}: {body}"
        )

    except URLError as exc:
        raise RuntimeError(
            f"URL_ERROR: {exc.reason}"
        )


# ============================================================
# AUTHENTICATED GET
# ============================================================

def authenticated_get(
    path,
    params=None,
):

    global AUTHENTICATED_WEEX_READS

    if params is None:
        params = {}

    (
        api_key,
        api_secret,
        api_passphrase,
    ) = get_credentials()

    if not (
        api_key
        and api_secret
        and api_passphrase
    ):
        raise RuntimeError(
            "WEEX credentials are incomplete"
        )

    query_string = urlencode(params)

    timestamp = str(
        int(time.time() * 1000)
    )

    body = ""

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body=body,
        secret=api_secret,
    )

    url = WEEX_CONTRACT_BASE + path

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": api_passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}/1.0",
    }

    request = Request(
        url=url,
        method="GET",
        headers=headers,
    )

    AUTHENTICATED_WEEX_READS += 1

    try:
        with urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            return status, json.loads(raw)

    except HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        try:
            body_data = json.loads(raw)
        except Exception:
            body_data = raw

        raise RuntimeError(
            f"HTTP {exc.code}: {body_data}"
        )

    except URLError as exc:
        raise RuntimeError(
            f"URL_ERROR: {exc.reason}"
        )


# ============================================================
# RESPONSE NORMALIZER
# ============================================================

def normalize_list(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        if isinstance(
            data.get("data"),
            list,
        ):
            return data["data"]

        if isinstance(
            data.get("result"),
            list,
        ):
            return data["result"]

        return [data]

    return []


# ============================================================
# TEST 1
# DNS
# ============================================================

def test_dns():

    global DNS_OK

    section("TEST 1: DNS")

    host = "api-contract.weex.com"

    log(f"HOST={host}")

    try:

        resolved_ip = socket.gethostbyname(
            host
        )

        DNS_OK = bool(resolved_ip)

        log(
            f"RESOLVED_IP={resolved_ip}"
        )

    except Exception as exc:

        DNS_OK = False

        log(
            f"DNS_EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            f"DNS_EXCEPTION_MESSAGE={exc}"
        )

    log(f"DNS_OK={DNS_OK}")


# ============================================================
# TEST 2
# CREDENTIAL PRESENCE
# ============================================================

def test_credentials():

    global CREDENTIALS_PRESENT

    section("TEST 2: CREDENTIAL CHECK")

    (
        api_key,
        api_secret,
        api_passphrase,
    ) = get_credentials()

    key_present = bool(api_key)
    secret_present = bool(api_secret)
    passphrase_present = bool(
        api_passphrase
    )

    CREDENTIALS_PRESENT = all(
        (
            key_present,
            secret_present,
            passphrase_present,
        )
    )

    log(
        f"WEEX_API_KEY_PRESENT="
        f"{key_present}"
    )

    log(
        f"WEEX_API_SECRET_PRESENT="
        f"{secret_present}"
    )

    log(
        f"WEEX_API_PASSPHRASE_PRESENT="
        f"{passphrase_present}"
    )

    log(
        f"CREDENTIALS_PRESENT="
        f"{CREDENTIALS_PRESENT}"
    )


# ============================================================
# TEST 3
# PUBLIC MARK PRICE
# ============================================================

def test_public_mark_price():

    global PUBLIC_MARK_PRICE_READ_OK
    global MARK_PRICE

    section(
        "TEST 3: PUBLIC V2 MARK PRICE"
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

    status, data = public_get(
        PUBLIC_MARK_PRICE_PATH,
        {
            "symbol": V2_MARKET_SYMBOL,
        },
    )

    log(f"HTTP_STATUS={status}")

    if not isinstance(data, dict):
        raise RuntimeError(
            "Unexpected V2 ticker response type"
        )

    response_symbol = data.get(
        "symbol"
    )

    mark_price_raw = data.get(
        "markPrice"
    )

    mark_price = safe_float(
        mark_price_raw
    )

    symbol_match = (
        str(response_symbol).lower()
        == V2_MARKET_SYMBOL.lower()
    )

    PUBLIC_MARK_PRICE_READ_OK = (
        status == 200
        and symbol_match
        and mark_price is not None
        and mark_price > 0
    )

    MARK_PRICE = mark_price

    log(
        f"RESPONSE_SYMBOL="
        f"{response_symbol}"
    )

    log(
        f"RESPONSE_SYMBOL_MATCH="
        f"{symbol_match}"
    )

    log(
        f"MARK_PRICE={MARK_PRICE}"
    )

    log(
        "MARK_PRICE_FIELD=markPrice"
    )

    log(
        f"PUBLIC_MARK_PRICE_READ_OK="
        f"{PUBLIC_MARK_PRICE_READ_OK}"
    )


# ============================================================
# TEST 4
# ACCOUNT BALANCE
# ============================================================

def test_balance():

    global BALANCE_READ_OK
    global AVAILABLE_BALANCE
    global TOTAL_BALANCE
    global POSITIVE_BALANCE_OK

    section(
        "TEST 4: AUTHENTICATED BALANCE"
    )

    log(
        f"PATH={BALANCE_PATH}"
    )

    status, data = authenticated_get(
        BALANCE_PATH
    )

    records = normalize_list(data)

    usdt = None

    for item in records:

        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get(
                "asset",
                "",
            )
        ).upper()

        if asset == "USDT":
            usdt = item
            break

    if usdt is None:
        raise RuntimeError(
            "USDT balance record not found"
        )

    AVAILABLE_BALANCE = safe_float(
        usdt.get(
            "availableBalance"
        )
    )

    TOTAL_BALANCE = safe_float(
        usdt.get(
            "balance"
        )
    )

    BALANCE_READ_OK = (
        status == 200
        and AVAILABLE_BALANCE
        is not None
        and TOTAL_BALANCE
        is not None
    )

    POSITIVE_BALANCE_OK = (
        BALANCE_READ_OK
        and AVAILABLE_BALANCE > 0
    )

    log("ASSET=USDT")

    log(
        f"AVAILABLE_BALANCE="
        f"{AVAILABLE_BALANCE}"
    )

    log(
        f"TOTAL_BALANCE="
        f"{TOTAL_BALANCE}"
    )

    log(
        f"BALANCE_READ_OK="
        f"{BALANCE_READ_OK}"
    )

    log(
        f"POSITIVE_BALANCE_OK="
        f"{POSITIVE_BALANCE_OK}"
    )


# ============================================================
# TEST 5
# POSITION RECONCILIATION
# ============================================================

def test_position():

    global POSITION_READ_OK
    global OPEN_POSITIONS
    global BTCUSDT_FLAT

    section(
        "TEST 5: AUTHENTICATED POSITION"
    )

    log(
        f"CANONICAL_SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"PATH={POSITION_PATH}"
    )

    status, data = authenticated_get(
        POSITION_PATH,
        {
            "symbol":
                CANONICAL_SYMBOL,
        },
    )

    records = normalize_list(data)

    open_count = 0

    for item in records:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol != CANONICAL_SYMBOL:
            continue

        size = safe_float(
            item.get(
                "size"
            )
        )

        if (
            size is not None
            and abs(size) > 0
        ):
            open_count += 1

    OPEN_POSITIONS = open_count

    BTCUSDT_FLAT = (
        open_count == 0
    )

    POSITION_READ_OK = (
        status == 200
    )

    log(
        f"POSITION_RESPONSE_COUNT="
        f"{len(records)}"
    )

    log(
        f"OPEN_POSITIONS="
        f"{OPEN_POSITIONS}"
    )

    log(
        f"BTCUSDT_FLAT="
        f"{BTCUSDT_FLAT}"
    )

    log(
        f"POSITION_READ_OK="
        f"{POSITION_READ_OK}"
    )


# ============================================================
# TEST 6
# SYMBOL CONFIGURATION
# ============================================================

def test_symbol_config():

    global SYMBOL_CONFIG_READ_OK

    global MARGIN_MODE
    global SEPARATED_TYPE
    global CROSS_LEVERAGE
    global LONG_LEVERAGE
    global SHORT_LEVERAGE

    global MARGIN_MODE_MATCH
    global LONG_LEVERAGE_MATCH
    global SHORT_LEVERAGE_MATCH

    section(
        "TEST 6: AUTHENTICATED SYMBOL CONFIG"
    )

    log(
        f"CANONICAL_SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    status, data = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol":
                CANONICAL_SYMBOL,
        },
    )

    records = normalize_list(data)

    config = None

    for item in records:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol == CANONICAL_SYMBOL:
            config = item
            break

    if config is None:
        raise RuntimeError(
            "BTCUSDT symbol configuration "
            "not found"
        )

    response_symbol = config.get(
        "symbol"
    )

    MARGIN_MODE = str(
        config.get(
            "marginType",
            "",
        )
    ).upper()

    SEPARATED_TYPE = str(
        config.get(
            "separatedType",
            "",
        )
    ).upper()

    CROSS_LEVERAGE = safe_float(
        config.get(
            "crossLeverage"
        )
    )

    LONG_LEVERAGE = safe_float(
        config.get(
            "isolatedLongLeverage"
        )
    )

    SHORT_LEVERAGE = safe_float(
        config.get(
            "isolatedShortLeverage"
        )
    )

    MARGIN_MODE_MATCH = (
        MARGIN_MODE
        == TARGET_MARGIN_MODE
    )

    LONG_LEVERAGE_MATCH = (
        LONG_LEVERAGE
        == TARGET_LONG_LEVERAGE
    )

    SHORT_LEVERAGE_MATCH = (
        SHORT_LEVERAGE
        == TARGET_SHORT_LEVERAGE
    )

    SYMBOL_CONFIG_READ_OK = (
        status == 200
        and str(
            response_symbol
        ).upper()
        == CANONICAL_SYMBOL
    )

    log(
        f"RESPONSE_SYMBOL="
        f"{response_symbol}"
    )

    log(
        f"MARGIN_MODE="
        f"{MARGIN_MODE}"
    )

    log(
        f"SEPARATED_TYPE="
        f"{SEPARATED_TYPE}"
    )

    log(
        f"CROSS_LEVERAGE="
        f"{CROSS_LEVERAGE}"
    )

    log(
        f"LONG_LEVERAGE="
        f"{LONG_LEVERAGE}"
    )

    log(
        f"SHORT_LEVERAGE="
        f"{SHORT_LEVERAGE}"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{MARGIN_MODE_MATCH}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{LONG_LEVERAGE_MATCH}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{SHORT_LEVERAGE_MATCH}"
    )

    log(
        f"SYMBOL_CONFIG_READ_OK="
        f"{SYMBOL_CONFIG_READ_OK}"
    )


# ============================================================
# TEST 7
# SAFETY FIREBREAK
# ============================================================

def test_safety():

    global SAFETY_INVARIANTS_OK

    section(
        "TEST 7: WRITE FIREBREAK"
    )

    SAFETY_INVARIANTS_OK = all(
        (
            REAL_ORDER_EXECUTION
            is False,

            FIRST_REAL_ORDER_ALLOWED
            is False,

            DEMO_ORDER_EXECUTION
            is False,

            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,

            ORDER_SUBMISSION_ENABLED
            is False,

            LEVERAGE_MUTATION_ENABLED
            is False,

            MARGIN_MODE_MUTATION_ENABLED
            is False,

            POSITION_MUTATION_ENABLED
            is False,

            EXCHANGE_NETWORK_WRITES
            == 0,

            ORDER_SUBMISSIONS
            == 0,

            LEVERAGE_MUTATIONS
            == 0,

            MARGIN_MODE_MUTATIONS
            == 0,

            POSITION_MUTATIONS
            == 0,
        )
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"DEMO_ORDER_EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED="
        f"{ORDER_SUBMISSION_ENABLED}"
    )

    log(
        f"LEVERAGE_MUTATION_ENABLED="
        f"{LEVERAGE_MUTATION_ENABLED}"
    )

    log(
        f"MARGIN_MODE_MUTATION_ENABLED="
        f"{MARGIN_MODE_MUTATION_ENABLED}"
    )

    log(
        f"POSITION_MUTATION_ENABLED="
        f"{POSITION_MUTATION_ENABLED}"
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
        f"SAFETY_INVARIANTS_OK="
        f"{SAFETY_INVARIANTS_OK}"
    )


# ============================================================
# TEST 8
# COMPOSITE ACTIVATION GATE
# ============================================================

def test_composite_activation_gate():

    global AUTHENTICATED_WEEX_READ_OK
    global ACTIVATION_ENV_MATCH
    global COMPOSITE_ACTIVATION_GATE_READY
    global TEST_STATUS

    section(
        "TEST 8: COMPOSITE ACTIVATION GATE"
    )

    AUTHENTICATED_WEEX_READ_OK = all(
        (
            BALANCE_READ_OK,
            POSITION_READ_OK,
            SYMBOL_CONFIG_READ_OK,
        )
    )

    ACTIVATION_ENV_MATCH = all(
        (
            DNS_OK,
            CREDENTIALS_PRESENT,
            PUBLIC_MARK_PRICE_READ_OK,
            AUTHENTICATED_WEEX_READ_OK,
            POSITIVE_BALANCE_OK,
            BTCUSDT_FLAT,
            MARGIN_MODE_MATCH,
            LONG_LEVERAGE_MATCH,
            SHORT_LEVERAGE_MATCH,
        )
    )

    COMPOSITE_ACTIVATION_GATE_READY = all(
        (
            ACTIVATION_ENV_MATCH,
            SAFETY_INVARIANTS_OK,
        )
    )

    TEST_STATUS = (
        "PASS"
        if COMPOSITE_ACTIVATION_GATE_READY
        else "FAIL"
    )

    log(
        f"DNS_OK={DNS_OK}"
    )

    log(
        f"CREDENTIALS_PRESENT="
        f"{CREDENTIALS_PRESENT}"
    )

    log(
        f"PUBLIC_MARK_PRICE_READ_OK="
        f"{PUBLIC_MARK_PRICE_READ_OK}"
    )

    log(
        f"MARK_PRICE="
        f"{MARK_PRICE}"
    )

    log(
        f"BALANCE_READ_OK="
        f"{BALANCE_READ_OK}"
    )

    log(
        f"POSITIVE_BALANCE_OK="
        f"{POSITIVE_BALANCE_OK}"
    )

    log(
        f"AVAILABLE_BALANCE="
        f"{AVAILABLE_BALANCE}"
    )

    log(
        f"POSITION_READ_OK="
        f"{POSITION_READ_OK}"
    )

    log(
        f"OPEN_POSITIONS="
        f"{OPEN_POSITIONS}"
    )

    log(
        f"BTCUSDT_FLAT="
        f"{BTCUSDT_FLAT}"
    )

    log(
        f"SYMBOL_CONFIG_READ_OK="
        f"{SYMBOL_CONFIG_READ_OK}"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{MARGIN_MODE_MATCH}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{LONG_LEVERAGE_MATCH}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{SHORT_LEVERAGE_MATCH}"
    )

    log(
        f"AUTHENTICATED_WEEX_READ_OK="
        f"{AUTHENTICATED_WEEX_READ_OK}"
    )

    log(
        f"ACTIVATION_ENV_MATCH="
        f"{ACTIVATION_ENV_MATCH}"
    )

    log(
        f"SAFETY_INVARIANTS_OK="
        f"{SAFETY_INVARIANTS_OK}"
    )

    log(
        "COMPOSITE_ACTIVATION_GATE_READY="
        f"{COMPOSITE_ACTIVATION_GATE_READY}"
    )

    log(
        f"TEST_STATUS={TEST_STATUS}"
    )


# ============================================================
# FINAL REPORT
# ============================================================

def print_final_report():

    section("R35P-G RESULT")

    log(
        "TEST="
        "COMPOSITE_READ_ONLY_ACTIVATION_GATE"
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
        "V2_MARKET_SYMBOL_FORMAT="
        "cmt_btcusdt"
    )

    log(
        "V3_AUTH_SYMBOL_FORMAT="
        "BTCUSDT"
    )

    log(
        f"DNS_OK={DNS_OK}"
    )

    log(
        f"CREDENTIALS_PRESENT="
        f"{CREDENTIALS_PRESENT}"
    )

    log(
        f"PUBLIC_MARK_PRICE_READ_OK="
        f"{PUBLIC_MARK_PRICE_READ_OK}"
    )

    log(
        f"MARK_PRICE={MARK_PRICE}"
    )

    log(
        f"BALANCE_READ_OK="
        f"{BALANCE_READ_OK}"
    )

    log(
        f"AVAILABLE_BALANCE="
        f"{AVAILABLE_BALANCE}"
    )

    log(
        f"POSITIVE_BALANCE_OK="
        f"{POSITIVE_BALANCE_OK}"
    )

    log(
        f"POSITION_READ_OK="
        f"{POSITION_READ_OK}"
    )

    log(
        f"OPEN_POSITIONS="
        f"{OPEN_POSITIONS}"
    )

    log(
        f"BTCUSDT_FLAT="
        f"{BTCUSDT_FLAT}"
    )

    log(
        f"SYMBOL_CONFIG_READ_OK="
        f"{SYMBOL_CONFIG_READ_OK}"
    )

    log(
        f"MARGIN_MODE="
        f"{MARGIN_MODE}"
    )

    log(
        f"LONG_LEVERAGE="
        f"{LONG_LEVERAGE}"
    )

    log(
        f"SHORT_LEVERAGE="
        f"{SHORT_LEVERAGE}"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{MARGIN_MODE_MATCH}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{LONG_LEVERAGE_MATCH}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{SHORT_LEVERAGE_MATCH}"
    )

    log(
        f"AUTHENTICATED_WEEX_READ_OK="
        f"{AUTHENTICATED_WEEX_READ_OK}"
    )

    log(
        f"ACTIVATION_ENV_MATCH="
        f"{ACTIVATION_ENV_MATCH}"
    )

    log(
        f"COMPOSITE_ACTIVATION_GATE_READY="
        f"{COMPOSITE_ACTIVATION_GATE_READY}"
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
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"SAFETY_INVARIANTS_OK="
        f"{SAFETY_INVARIANTS_OK}"
    )

    log(
        f"FAILURE_STAGE="
        f"{FAILURE_STAGE}"
    )

    log(
        f"EXCEPTION_CLASS="
        f"{EXCEPTION_CLASS}"
    )

    log(
        f"EXCEPTION_MESSAGE="
        f"{EXCEPTION_MESSAGE}"
    )

    log(
        f"STATUS={TEST_STATUS}"
    )

    log(
        "R35P-E_ROOT_CAUSE_FIX="
        "PRESERVED"
    )

    log(
        "R35P-F_RECONCILIATION="
        "PRESERVED"
    )

    log(
        "EXECUTION_PERMISSION="
        "NOT_GRANTED"
    )

    log(
        "REAL_ORDER_PATH="
        "ABSENT"
    )

    log(
        "NEXT_UNIT=R35P-H"
    )

    log(DIVIDER)


# ============================================================
# DIAGNOSTIC RUNNER
# ============================================================

def run_diagnostic():

    global FAILURE_STAGE
    global EXCEPTION_CLASS
    global EXCEPTION_MESSAGE
    global TEST_STATUS

    section("MAIN.PY ENTERED")

    log(
        f"{VERSION}: "
        f"CANONICAL SYMBOL="
        f"{CANONICAL_SYMBOL}"
    )

    log(
        f"{VERSION}: "
        f"V2 MARKET SYMBOL="
        f"{V2_MARKET_SYMBOL}"
    )

    log(
        f"{VERSION}: "
        f"WEEX CONTRACT BASE="
        f"{WEEX_CONTRACT_BASE}"
    )

    log(
        f"{VERSION}: "
        f"PUBLIC MARK PRICE PATH="
        f"{PUBLIC_MARK_PRICE_PATH}"
    )

    log(
        f"{VERSION}: "
        f"BALANCE PATH="
        f"{BALANCE_PATH}"
    )

    log(
        f"{VERSION}: "
        f"POSITION PATH="
        f"{POSITION_PATH}"
    )

    log(
        f"{VERSION}: "
        f"SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    log(
        f"{VERSION}: "
        f"TARGET MARGIN MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"{VERSION}: "
        f"TARGET LONG LEVERAGE="
        f"{TARGET_LONG_LEVERAGE:g}x"
    )

    log(
        f"{VERSION}: "
        f"TARGET SHORT LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE:g}x"
    )

    section("WRITE FIREBREAK")

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"DEMO_ORDER_EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED="
        f"{ORDER_SUBMISSION_ENABLED}"
    )

    log(
        f"LEVERAGE_MUTATION_ENABLED="
        f"{LEVERAGE_MUTATION_ENABLED}"
    )

    log(
        f"MARGIN_MODE_MUTATION_ENABLED="
        f"{MARGIN_MODE_MUTATION_ENABLED}"
    )

    log(
        f"POSITION_MUTATION_ENABLED="
        f"{POSITION_MUTATION_ENABLED}"
    )

    try:

        FAILURE_STAGE = "DNS"
        test_dns()

        if not DNS_OK:
            raise RuntimeError(
                "DNS resolution failed"
            )

        FAILURE_STAGE = "CREDENTIAL_CHECK"
        test_credentials()

        if not CREDENTIALS_PRESENT:
            raise RuntimeError(
                "Required WEEX credentials "
                "are not present"
            )

        FAILURE_STAGE = "PUBLIC_MARK_PRICE"
        test_public_mark_price()

        if not PUBLIC_MARK_PRICE_READ_OK:
            raise RuntimeError(
                "Public mark-price "
                "reconciliation failed"
            )

        FAILURE_STAGE = "BALANCE"
        test_balance()

        if not BALANCE_READ_OK:
            raise RuntimeError(
                "Balance reconciliation failed"
            )

        FAILURE_STAGE = "POSITION"
        test_position()

        if not POSITION_READ_OK:
            raise RuntimeError(
                "Position reconciliation failed"
            )

        FAILURE_STAGE = "SYMBOL_CONFIG"
        test_symbol_config()

        if not SYMBOL_CONFIG_READ_OK:
            raise RuntimeError(
                "Symbol configuration "
                "reconciliation failed"
            )

        FAILURE_STAGE = "SAFETY"
        test_safety()

        if not SAFETY_INVARIANTS_OK:
            raise RuntimeError(
                "Safety firebreak failed"
            )

        FAILURE_STAGE = (
            "COMPOSITE_ACTIVATION_GATE"
        )

        test_composite_activation_gate()

        FAILURE_STAGE = None
        EXCEPTION_CLASS = None
        EXCEPTION_MESSAGE = None

    except Exception as exc:

        EXCEPTION_CLASS = (
            type(exc).__name__
        )

        EXCEPTION_MESSAGE = str(exc)

        TEST_STATUS = "FAIL"

        section("ERROR DIAGNOSTIC")

        log(
            f"FAILURE_STAGE="
            f"{FAILURE_STAGE}"
        )

        log(
            f"EXCEPTION_CLASS="
            f"{EXCEPTION_CLASS}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{EXCEPTION_MESSAGE}"
        )

        # Always re-check the hard firebreak.
        test_safety()

    print_final_report()


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"PUBLIC_MARK_PRICE_READ_OK="
            f"{PUBLIC_MARK_PRICE_READ_OK} "
            f"MARK_PRICE={MARK_PRICE} "
            f"BALANCE_READ_OK="
            f"{BALANCE_READ_OK} "
            f"AVAILABLE_BALANCE="
            f"{AVAILABLE_BALANCE} "
            f"POSITION_READ_OK="
            f"{POSITION_READ_OK} "
            f"OPEN_POSITIONS="
            f"{OPEN_POSITIONS} "
            f"BTCUSDT_FLAT="
            f"{BTCUSDT_FLAT} "
            f"SYMBOL_CONFIG_READ_OK="
            f"{SYMBOL_CONFIG_READ_OK} "
            f"ACTIVATION_ENV_MATCH="
            f"{ACTIVATION_ENV_MATCH} "
            f"COMPOSITE_ACTIVATION_GATE_READY="
            f"{COMPOSITE_ACTIVATION_GATE_READY} "
            f"TEST_STATUS="
            f"{TEST_STATUS} "
            f"PUBLIC_MARKET_GETS="
            f"{PUBLIC_MARKET_GETS} "
            f"AUTHENTICATED_WEEX_READS="
            f"{AUTHENTICATED_WEEX_READS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


# ============================================================
# MAIN
# ============================================================

def main():

    start_health_server()

    run_diagnostic()

    heartbeat_loop()


if __name__ == "__main__":
    main()

