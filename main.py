

import os
import time
import json
import hmac
import base64
import hashlib
import threading
import traceback
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R35P-K
#
# PURPOSE
# -----------------------------------------------------------------------------
# Smallest isolated authenticated-read test for:
#
#   1. BTCUSDT symbol configuration
#   2. Margin mode reconciliation
#   3. Isolated long leverage reconciliation
#   4. Isolated short leverage reconciliation
#
# THIS UNIT MUST NOT:
# -----------------------------------------------------------------------------
# - submit an order
# - change leverage
# - change margin mode
# - change position mode
# - change positions
# - perform any exchange POST
# - grant live execution permission
#
# EXPECTED TARGET:
# -----------------------------------------------------------------------------
# BTCUSDT
# MARGIN MODE = ISOLATED
# LONG LEVERAGE = 100x
# SHORT LEVERAGE = 100x
# =============================================================================


UNIT = "R35P-K"

WEEX_BASE_URL = "https://api-contract.weex.com"

SYMBOL = "BTCUSDT"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

HEALTH_PORT = int(os.getenv("PORT", "10000"))


# =============================================================================
# HARD WRITE FIREBREAK
# =============================================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False


# =============================================================================
# COUNTERS
# =============================================================================

PUBLIC_MARKET_GETS = 0
AUTHENTICATED_WEEX_READS = 0

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0


# =============================================================================
# RESULT STATE
# =============================================================================

DNS_OK = None
CREDENTIALS_PRESENT = None

SYMBOL_CONFIG_HTTP_OK = False
SYMBOL_CONFIG_READ_OK = False

OBSERVED_SYMBOL = None
OBSERVED_MARGIN_MODE = None
OBSERVED_SEPARATED_TYPE = None
OBSERVED_CROSS_LEVERAGE = None
OBSERVED_LONG_LEVERAGE = None
OBSERVED_SHORT_LEVERAGE = None

SYMBOL_MATCH = False
MARGIN_MODE_MATCH = False
LONG_LEVERAGE_MATCH = False
SHORT_LEVERAGE_MATCH = False

CONFIG_RECONCILIATION_OK = False
SAFETY_INVARIANTS_OK = False

AUTH_HTTP_STATUS = None
AUTH_ERROR_CODE = None
AUTH_ERROR_MESSAGE = None

TEST_STATUS = "NOT_RUN"


# =============================================================================
# LOGGING
# =============================================================================

LINE = "-" * 100


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def section(title):
    log(LINE)
    log(f"{UNIT}: {title}")
    log(LINE)


def bool_text(value):
    return "True" if value else "False"


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "unit": UNIT,
            "status": TEST_STATUS,
            "symbol": SYMBOL,
            "symbol_config_read_ok": SYMBOL_CONFIG_READ_OK,
            "config_reconciliation_ok": CONFIG_RECONCILIATION_OK,
            "safety_invariants_ok": SAFETY_INVARIANTS_OK,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
        }

        raw = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()

        self.wfile.write(raw)

    def log_message(self, format, *args):
        return


def start_health_server():

    def run_server():
        try:
            server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
            log(f"{UNIT}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}")
            server.serve_forever()

        except Exception as exc:
            log(
                f"{UNIT}: HEALTH SERVER ERROR "
                f"{exc.__class__.__name__}: {exc}"
            )

    thread = threading.Thread(
        target=run_server,
        daemon=True,
    )

    thread.start()


# =============================================================================
# ENVIRONMENT
# =============================================================================

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# =============================================================================
# SECURITY HELPERS
# =============================================================================

def masked(value):
    if not value:
        return "<EMPTY>"

    if len(value) <= 8:
        return "***"

    return f"{value[:4]}***{value[-4:]}"


# =============================================================================
# SIGNATURE
# =============================================================================

def generate_signature(
    secret,
    timestamp_ms,
    method,
    request_path,
    query_string="",
    body="",
):

    method = method.upper()

    if query_string:
        message = (
            str(timestamp_ms)
            + method
            + request_path
            + "?"
            + query_string
            + body
        )
    else:
        message = (
            str(timestamp_ms)
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    signature = base64.b64encode(digest).decode("utf-8")

    return signature, message


# =============================================================================
# HARD READ-ONLY HTTP TRANSPORT
# =============================================================================

def authenticated_get(
    request_path,
    query_params=None,
    timeout=15,
):

    global AUTHENTICATED_WEEX_READS

    if not WEEX_API_KEY:
        raise RuntimeError("WEEX_API_KEY missing")

    if not WEEX_API_SECRET:
        raise RuntimeError("WEEX_API_SECRET missing")

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError("WEEX_API_PASSPHRASE missing")

    query_string = ""

    if query_params:
        query_string = urllib.parse.urlencode(
            query_params,
            doseq=True,
        )

    timestamp_ms = str(int(time.time() * 1000))

    signature, signature_message = generate_signature(
        secret=WEEX_API_SECRET,
        timestamp_ms=timestamp_ms,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    url = WEEX_BASE_URL + request_path

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
        "User-Agent": f"{UNIT}/read-only",
    }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    AUTHENTICATED_WEEX_READS += 1

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            return {
                "http_status": status,
                "raw": raw,
                "timestamp_ms": timestamp_ms,
                "query_string": query_string,
                "signature_message": signature_message,
                "signature": signature,
                "url": url,
            }

    except urllib.error.HTTPError as exc:

        try:
            raw = exc.read().decode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            raw = ""

        return {
            "http_status": exc.code,
            "raw": raw,
            "timestamp_ms": timestamp_ms,
            "query_string": query_string,
            "signature_message": signature_message,
            "signature": signature,
            "url": url,
        }


# =============================================================================
# SAFE PARSING HELPERS
# =============================================================================

def normalize_text(value):

    if value is None:
        return None

    return str(value).strip()


def normalize_upper(value):

    text = normalize_text(value)

    if text is None:
        return None

    return text.upper()


def parse_numeric(value):

    if value is None:
        return None

    try:
        return float(str(value).replace("x", "").strip())

    except Exception:
        return None


def parse_json(raw):

    try:
        return json.loads(raw)

    except Exception:
        return None


def extract_error(payload):

    error_code = None
    error_message = None

    if isinstance(payload, dict):

        for key in (
            "code",
            "errorCode",
            "error_code",
        ):
            if key in payload:
                error_code = payload.get(key)
                break

        for key in (
            "msg",
            "message",
            "errorMessage",
            "error_message",
        ):
            if key in payload:
                error_message = payload.get(key)
                break

    return error_code, error_message


# =============================================================================
# SYMBOL CONFIG EXTRACTION
# =============================================================================

def find_symbol_config(payload):

    candidates = []

    if isinstance(payload, list):
        candidates.extend(payload)

    elif isinstance(payload, dict):

        # Direct object
        if (
            "symbol" in payload
            or "marginType" in payload
            or "isolatedLongLeverage" in payload
        ):
            candidates.append(payload)

        # Common wrapper possibilities
        for wrapper_key in (
            "data",
            "result",
            "rows",
            "list",
        ):

            wrapped = payload.get(wrapper_key)

            if isinstance(wrapped, list):
                candidates.extend(wrapped)

            elif isinstance(wrapped, dict):
                candidates.append(wrapped)

    for item in candidates:

        if not isinstance(item, dict):
            continue

        item_symbol = normalize_upper(
            item.get("symbol")
        )

        if item_symbol == SYMBOL:
            return item

    # If API returned exactly one config object but symbol
    # normalization differs, retain it for diagnostic output.
    if len(candidates) == 1:
        if isinstance(candidates[0], dict):
            return candidates[0]

    return None


# =============================================================================
# TEST 1
# CREDENTIAL CHECK
# =============================================================================

def run_credential_check():

    global CREDENTIALS_PRESENT

    section("TEST 1: CREDENTIAL CHECK")

    key_present = bool(WEEX_API_KEY)
    secret_present = bool(WEEX_API_SECRET)
    passphrase_present = bool(WEEX_API_PASSPHRASE)

    CREDENTIALS_PRESENT = (
        key_present
        and secret_present
        and passphrase_present
    )

    log(
        f"WEEX_API_KEY_PRESENT="
        f"{bool_text(key_present)}"
    )

    log(
        f"WEEX_API_SECRET_PRESENT="
        f"{bool_text(secret_present)}"
    )

    log(
        f"WEEX_API_PASSPHRASE_PRESENT="
        f"{bool_text(passphrase_present)}"
    )

    log(
        f"CREDENTIALS_PRESENT="
        f"{bool_text(CREDENTIALS_PRESENT)}"
    )

    log(
        f"WEEX_API_KEY_LENGTH="
        f"{len(WEEX_API_KEY)}"
    )

    log(
        f"WEEX_API_SECRET_LENGTH="
        f"{len(WEEX_API_SECRET)}"
    )

    log(
        f"WEEX_API_PASSPHRASE_LENGTH="
        f"{len(WEEX_API_PASSPHRASE)}"
    )

    log(
        f"WEEX_API_KEY_MASKED="
        f"{masked(WEEX_API_KEY)}"
    )

    log("WEEX_API_SECRET_VALUE=REDACTED")
    log("WEEX_API_PASSPHRASE_VALUE=REDACTED")


# =============================================================================
# TEST 2
# SYMBOL CONFIG SIGNATURE DIAGNOSTIC
# =============================================================================

def run_symbol_config_test():

    global SYMBOL_CONFIG_HTTP_OK
    global SYMBOL_CONFIG_READ_OK

    global OBSERVED_SYMBOL
    global OBSERVED_MARGIN_MODE
    global OBSERVED_SEPARATED_TYPE
    global OBSERVED_CROSS_LEVERAGE
    global OBSERVED_LONG_LEVERAGE
    global OBSERVED_SHORT_LEVERAGE

    global SYMBOL_MATCH
    global MARGIN_MODE_MATCH
    global LONG_LEVERAGE_MATCH
    global SHORT_LEVERAGE_MATCH

    global CONFIG_RECONCILIATION_OK

    global AUTH_HTTP_STATUS
    global AUTH_ERROR_CODE
    global AUTH_ERROR_MESSAGE

    section(
        "TEST 2: AUTHENTICATED BTCUSDT SYMBOL CONFIG"
    )

    log("METHOD=GET")
    log(f"PATH={SYMBOL_CONFIG_PATH}")
    log(f"SYMBOL={SYMBOL}")

    query_params = {
        "symbol": SYMBOL,
    }

    expected_query = urllib.parse.urlencode(
        query_params
    )

    log(f"QUERY_STRING={expected_query}")

    result = authenticated_get(
        request_path=SYMBOL_CONFIG_PATH,
        query_params=query_params,
    )

    AUTH_HTTP_STATUS = result["http_status"]

    timestamp_ms = result["timestamp_ms"]
    signature = result["signature"]

    log(
        f"TIMESTAMP_MS="
        f"{timestamp_ms}"
    )

    log(
        f"TIMESTAMP_DIGITS="
        f"{len(timestamp_ms)}"
    )

    log(
        "SIGNATURE_MESSAGE_FORMAT_OK="
        + bool_text(
            len(timestamp_ms) == 13
            and "GET" in result["signature_message"]
            and SYMBOL_CONFIG_PATH
            in result["signature_message"]
            and expected_query
            in result["signature_message"]
        )
    )

    signature_base64_ok = False

    try:
        decoded = base64.b64decode(
            signature,
            validate=True,
        )

        signature_base64_ok = (
            len(decoded) == 32
        )

    except Exception:
        signature_base64_ok = False

    log(
        "SIGNATURE_BASE64_FORMAT_OK="
        + bool_text(signature_base64_ok)
    )

    log(
        f"SIGNATURE_LENGTH="
        f"{len(signature)}"
    )

    log("ACCESS_SIGN_VALUE=REDACTED")

    log(
        f"HTTP_STATUS="
        f"{AUTH_HTTP_STATUS}"
    )

    SYMBOL_CONFIG_HTTP_OK = (
        AUTH_HTTP_STATUS == 200
    )

    log(
        "SYMBOL_CONFIG_HTTP_OK="
        + bool_text(SYMBOL_CONFIG_HTTP_OK)
    )

    payload = parse_json(
        result["raw"]
    )

    AUTH_ERROR_CODE, AUTH_ERROR_MESSAGE = (
        extract_error(payload)
    )

    config = find_symbol_config(
        payload
    )

    if config is None:

        log(
            "SYMBOL_CONFIG_OBJECT_FOUND=False"
        )

        log(
            "SYMBOL_CONFIG_READ_OK=False"
        )

        if result["raw"]:
            safe_raw = result["raw"][:1000]
            log(
                f"RAW_RESPONSE="
                f"{safe_raw}"
            )

        return

    log(
        "SYMBOL_CONFIG_OBJECT_FOUND=True"
    )

    OBSERVED_SYMBOL = normalize_upper(
        config.get("symbol")
    )

    OBSERVED_MARGIN_MODE = normalize_upper(
        config.get("marginType")
    )

    OBSERVED_SEPARATED_TYPE = normalize_upper(
        config.get("separatedType")
    )

    OBSERVED_CROSS_LEVERAGE = parse_numeric(
        config.get("crossLeverage")
    )

    OBSERVED_LONG_LEVERAGE = parse_numeric(
        config.get("isolatedLongLeverage")
    )

    OBSERVED_SHORT_LEVERAGE = parse_numeric(
        config.get("isolatedShortLeverage")
    )

    SYMBOL_MATCH = (
        OBSERVED_SYMBOL == SYMBOL
    )

    MARGIN_MODE_MATCH = (
        OBSERVED_MARGIN_MODE
        == TARGET_MARGIN_MODE
    )

    LONG_LEVERAGE_MATCH = (
        OBSERVED_LONG_LEVERAGE
        == float(TARGET_LONG_LEVERAGE)
    )

    SHORT_LEVERAGE_MATCH = (
        OBSERVED_SHORT_LEVERAGE
        == float(TARGET_SHORT_LEVERAGE)
    )

    SYMBOL_CONFIG_READ_OK = (
        SYMBOL_CONFIG_HTTP_OK
        and OBSERVED_SYMBOL is not None
        and OBSERVED_MARGIN_MODE is not None
        and OBSERVED_LONG_LEVERAGE is not None
        and OBSERVED_SHORT_LEVERAGE is not None
    )

    CONFIG_RECONCILIATION_OK = (
        SYMBOL_CONFIG_READ_OK
        and SYMBOL_MATCH
        and MARGIN_MODE_MATCH
        and LONG_LEVERAGE_MATCH
        and SHORT_LEVERAGE_MATCH
    )

    log(
        f"OBSERVED_SYMBOL="
        f"{OBSERVED_SYMBOL}"
    )

    log(
        f"SYMBOL_MATCH="
        f"{bool_text(SYMBOL_MATCH)}"
    )

    log(
        f"OBSERVED_MARGIN_MODE="
        f"{OBSERVED_MARGIN_MODE}"
    )

    log(
        f"TARGET_MARGIN_MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{bool_text(MARGIN_MODE_MATCH)}"
    )

    log(
        f"OBSERVED_SEPARATED_TYPE="
        f"{OBSERVED_SEPARATED_TYPE}"
    )

    log(
        f"OBSERVED_CROSS_LEVERAGE="
        f"{OBSERVED_CROSS_LEVERAGE}"
    )

    log(
        f"OBSERVED_LONG_LEVERAGE="
        f"{OBSERVED_LONG_LEVERAGE}"
    )

    log(
        f"TARGET_LONG_LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{bool_text(LONG_LEVERAGE_MATCH)}"
    )

    log(
        f"OBSERVED_SHORT_LEVERAGE="
        f"{OBSERVED_SHORT_LEVERAGE}"
    )

    log(
        f"TARGET_SHORT_LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{bool_text(SHORT_LEVERAGE_MATCH)}"
    )

    log(
        f"SYMBOL_CONFIG_READ_OK="
        f"{bool_text(SYMBOL_CONFIG_READ_OK)}"
    )

    log(
        f"CONFIG_RECONCILIATION_OK="
        f"{bool_text(CONFIG_RECONCILIATION_OK)}"
    )


# =============================================================================
# TEST 3
# HARD WRITE FIREBREAK VALIDATION
# =============================================================================

def run_safety_test():

    global SAFETY_INVARIANTS_OK

    section(
        "TEST 3: HARD WRITE FIREBREAK"
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

    SAFETY_INVARIANTS_OK = (
        REAL_ORDER_EXECUTION is False
        and FIRST_REAL_ORDER_ALLOWED is False
        and DEMO_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MODE_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
        and EXCHANGE_NETWORK_WRITES == 0
        and ORDER_SUBMISSIONS == 0
        and LEVERAGE_MUTATIONS == 0
        and MARGIN_MODE_MUTATIONS == 0
        and POSITION_MUTATIONS == 0
    )

    log(
        f"SAFETY_INVARIANTS_OK="
        f"{bool_text(SAFETY_INVARIANTS_OK)}"
    )


# =============================================================================
# FINAL RESULT
# =============================================================================

def finalize():

    global TEST_STATUS

    section(
        "MARGIN / LEVERAGE RECONCILIATION RESULT"
    )

    TEST_STATUS = (
        "PASS"
        if (
            CREDENTIALS_PRESENT
            and SYMBOL_CONFIG_READ_OK
            and CONFIG_RECONCILIATION_OK
            and SAFETY_INVARIANTS_OK
        )
        else "FAIL"
    )

    log(
        f"CREDENTIALS_PRESENT="
        f"{bool_text(bool(CREDENTIALS_PRESENT))}"
    )

    log(
        f"SYMBOL_CONFIG_HTTP_OK="
        f"{bool_text(SYMBOL_CONFIG_HTTP_OK)}"
    )

    log(
        f"SYMBOL_CONFIG_READ_OK="
        f"{bool_text(SYMBOL_CONFIG_READ_OK)}"
    )

    log(
        f"OBSERVED_SYMBOL="
        f"{OBSERVED_SYMBOL}"
    )

    log(
        f"SYMBOL_MATCH="
        f"{bool_text(SYMBOL_MATCH)}"
    )

    log(
        f"OBSERVED_MARGIN_MODE="
        f"{OBSERVED_MARGIN_MODE}"
    )

    log(
        f"TARGET_MARGIN_MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{bool_text(MARGIN_MODE_MATCH)}"
    )

    log(
        f"OBSERVED_SEPARATED_TYPE="
        f"{OBSERVED_SEPARATED_TYPE}"
    )

    log(
        f"OBSERVED_CROSS_LEVERAGE="
        f"{OBSERVED_CROSS_LEVERAGE}"
    )

    log(
        f"OBSERVED_LONG_LEVERAGE="
        f"{OBSERVED_LONG_LEVERAGE}"
    )

    log(
        f"TARGET_LONG_LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{bool_text(LONG_LEVERAGE_MATCH)}"
    )

    log(
        f"OBSERVED_SHORT_LEVERAGE="
        f"{OBSERVED_SHORT_LEVERAGE}"
    )

    log(
        f"TARGET_SHORT_LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{bool_text(SHORT_LEVERAGE_MATCH)}"
    )

    log(
        f"CONFIG_RECONCILIATION_OK="
        f"{bool_text(CONFIG_RECONCILIATION_OK)}"
    )

    log(
        f"AUTH_HTTP_STATUS="
        f"{AUTH_HTTP_STATUS}"
    )

    log(
        f"AUTH_ERROR_CODE="
        f"{AUTH_ERROR_CODE}"
    )

    log(
        f"AUTH_ERROR_MESSAGE="
        f"{AUTH_ERROR_MESSAGE}"
    )

    log(
        f"AUTHENTICATED_WEEX_READS="
        f"{AUTHENTICATED_WEEX_READS}"
    )

    log(
        f"PUBLIC_MARKET_GETS="
        f"{PUBLIC_MARKET_GETS}"
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
        f"{bool_text(SAFETY_INVARIANTS_OK)}"
    )

    log(
        f"TEST_STATUS="
        f"{TEST_STATUS}"
    )

    log(
        "EXECUTION_PERMISSION=NOT_GRANTED"
    )

    log(
        "REAL_ORDER_PATH=ABSENT"
    )

    log(
        "MUTATION_PATH=ABSENT"
    )


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: "
            f"HEARTBEAT={heartbeat} "
            f"CREDENTIALS_PRESENT="
            f"{bool_text(bool(CREDENTIALS_PRESENT))} "
            f"SYMBOL_CONFIG_READ_OK="
            f"{bool_text(SYMBOL_CONFIG_READ_OK)} "
            f"SYMBOL={OBSERVED_SYMBOL} "
            f"MARGIN_MODE={OBSERVED_MARGIN_MODE} "
            f"MARGIN_MODE_MATCH="
            f"{bool_text(MARGIN_MODE_MATCH)} "
            f"LONG_LEVERAGE={OBSERVED_LONG_LEVERAGE} "
            f"LONG_LEVERAGE_MATCH="
            f"{bool_text(LONG_LEVERAGE_MATCH)} "
            f"SHORT_LEVERAGE={OBSERVED_SHORT_LEVERAGE} "
            f"SHORT_LEVERAGE_MATCH="
            f"{bool_text(SHORT_LEVERAGE_MATCH)} "
            f"CONFIG_RECONCILIATION_OK="
            f"{bool_text(CONFIG_RECONCILIATION_OK)} "
            f"AUTH_HTTP_STATUS={AUTH_HTTP_STATUS} "
            f"TEST_STATUS={TEST_STATUS} "
            f"SAFETY_INVARIANTS_OK="
            f"{bool_text(SAFETY_INVARIANTS_OK)} "
            f"AUTHENTICATED_WEEX_READS="
            f"{AUTHENTICATED_WEEX_READS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(60)


# =============================================================================
# MAIN
# =============================================================================

def main():

    start_health_server()

    time.sleep(0.2)

    section(
        "MAIN.PY ENTERED"
    )

    log(
        f"{UNIT}: SYMBOL="
        f"{SYMBOL}"
    )

    log(
        f"{UNIT}: WEEX CONTRACT BASE="
        f"{WEEX_BASE_URL}"
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
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"{UNIT}: TARGET SHORT LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    section(
        "HARD WRITE FIREBREAK"
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

    try:

        run_credential_check()

        if not CREDENTIALS_PRESENT:
            raise RuntimeError(
                "Required WEEX credentials are missing"
            )

        run_symbol_config_test()

        run_safety_test()

        finalize()

    except Exception as exc:

        global TEST_STATUS

        TEST_STATUS = "FAIL"

        section(
            "ERROR DIAGNOSTIC"
        )

        log(
            f"EXCEPTION_CLASS="
            f"{exc.__class__.__name__}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{exc}"
        )

        log(
            "TRACEBACK_BEGIN"
        )

        traceback.print_exc()

        log(
            "TRACEBACK_END"
        )

        run_safety_test()

        finalize()

    heartbeat_loop()


if __name__ == "__main__":
    main()

