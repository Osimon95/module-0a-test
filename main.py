

# =============================================================================
# R35P-I main.py
#
# PURPOSE
# -------
# Smallest-unit WEEX authenticated-request diagnostic.
#
# This unit tests:
#   1. Health server
#   2. DNS resolution
#   3. Credential environment presence
#   4. Public V2 mark-price sanity check
#   5. EXACTLY ONE authenticated V3 account-balance GET
#   6. HTTP error-body capture for authentication diagnosis
#
# SAFETY
# ------
#   REAL ORDER EXECUTION            = FALSE
#   FIRST REAL ORDER ALLOWED        = FALSE
#   DEMO ORDER EXECUTION            = FALSE
#   EXCHANGE MUTATION TRANSPORT     = FALSE
#   ORDER SUBMISSION                = FALSE
#   LEVERAGE MUTATION               = FALSE
#   MARGIN MODE MUTATION            = FALSE
#   POSITION MUTATION               = FALSE
#
# There is NO exchange POST/PUT/PATCH/DELETE transport in this file.
# There is NO order endpoint in this file.
# There is NO leverage mutation endpoint in this file.
#
# R35P-I stops after the authenticated balance diagnostic.
# =============================================================================

import os
import json
import time
import hmac
import base64
import hashlib
import socket
import threading
import urllib.request
import urllib.parse
import urllib.error

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# VERSION
# =============================================================================

VERSION = "R35P-I"


# =============================================================================
# CORE CONFIGURATION
# =============================================================================

CANONICAL_SYMBOL = "BTCUSDT"

# WEEX V2 public-market representation.
V2_MARKET_SYMBOL = "cmt_btcusdt"

# WEEX V3 authenticated/account representation.
V3_AUTH_SYMBOL = "BTCUSDT"

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"

MARK_PRICE_PATH = "/capi/v2/market/ticker"
BALANCE_PATH = "/capi/v3/account/balance"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

ENTRY_BALANCE_PERCENT = 5
MAX_FUND_EXPOSURE_PERCENT = 35

QTY_STEP = 0.0001
MIN_QTY = 0.0001


# =============================================================================
# HARD SAFETY FIREBREAK
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
# DIAGNOSTIC COUNTERS
# =============================================================================

PUBLIC_MARKET_GETS = 0
AUTHENTICATED_WEEX_READS = 0

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0


# =============================================================================
# RUNTIME STATE
# =============================================================================

DNS_OK = False

PUBLIC_MARK_PRICE_READ_OK = False
MARK_PRICE = None

BALANCE_READ_OK = False
AVAILABLE_BALANCE = None

AUTH_HTTP_STATUS = None
AUTH_ERROR_BODY = None
AUTH_ERROR_CODE = None
AUTH_ERROR_MESSAGE = None

SIGNATURE_MESSAGE_FORMAT_OK = False
SIGNATURE_BASE64_FORMAT_OK = False

TEST_STATUS = "NOT_RUN"
EXECUTION_PERMISSION = "NOT_GRANTED"


# =============================================================================
# LOGGING
# =============================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{utc_now()} {message}", flush=True)


def separator():
    log("-" * 100)


def heading(text):
    separator()
    log(text)
    separator()


def safe_bool(value):
    return "True" if bool(value) else "False"


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "status": "ok",
            "version": VERSION,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
            "test_status": TEST_STATUS,
        }

        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))

    server = HTTPServer(("0.0.0.0", port), HealthHandler)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(f"{VERSION}: HEALTH SERVER STARTED ON PORT {port}")


# =============================================================================
# ENVIRONMENT HELPERS
# =============================================================================

def env_value(name):
    value = os.environ.get(name)

    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    return value


def safe_length(value):
    if value is None:
        return 0
    return len(value)


def masked_prefix(value, length=4):
    if not value:
        return "NONE"

    visible = value[:length]

    return visible + "***"


def masked_suffix(value, length=4):
    if not value:
        return "NONE"

    visible = value[-length:]

    return "***" + visible


# =============================================================================
# DNS TEST
# =============================================================================

def run_dns_test():

    global DNS_OK

    heading(f"{VERSION}: TEST 1: DNS")

    host = urllib.parse.urlparse(
        WEEX_CONTRACT_BASE
    ).hostname

    log(f"HOST={host}")

    try:
        ip = socket.gethostbyname(host)

        DNS_OK = True

        log(f"RESOLVED_IP={ip}")
        log("DNS_OK=True")

    except Exception as exc:

        DNS_OK = False

        log("RESOLVED_IP=UNKNOWN")
        log("DNS_OK=False")
        log(f"DNS_EXCEPTION_CLASS={type(exc).__name__}")
        log(f"DNS_EXCEPTION_MESSAGE={exc}")


# =============================================================================
# CREDENTIAL CHECK
# =============================================================================

def credential_check():

    heading(f"{VERSION}: TEST 2: CREDENTIAL CHECK")

    api_key = env_value("WEEX_API_KEY")
    api_secret = env_value("WEEX_API_SECRET")
    api_passphrase = env_value("WEEX_API_PASSPHRASE")

    key_present = api_key is not None
    secret_present = api_secret is not None
    passphrase_present = api_passphrase is not None

    credentials_present = (
        key_present
        and secret_present
        and passphrase_present
    )

    log(f"WEEX_API_KEY_PRESENT={safe_bool(key_present)}")
    log(f"WEEX_API_SECRET_PRESENT={safe_bool(secret_present)}")
    log(
        "WEEX_API_PASSPHRASE_PRESENT="
        f"{safe_bool(passphrase_present)}"
    )

    log(
        "CREDENTIALS_PRESENT="
        f"{safe_bool(credentials_present)}"
    )

    # Lengths are useful diagnostically without exposing credentials.
    log(f"WEEX_API_KEY_LENGTH={safe_length(api_key)}")
    log(f"WEEX_API_SECRET_LENGTH={safe_length(api_secret)}")
    log(
        "WEEX_API_PASSPHRASE_LENGTH="
        f"{safe_length(api_passphrase)}"
    )

    # Only a tiny masked portion of the API key is printed.
    # Secret and passphrase are NEVER printed.
    log(
        "WEEX_API_KEY_PREFIX="
        f"{masked_prefix(api_key)}"
    )

    log(
        "WEEX_API_KEY_SUFFIX="
        f"{masked_suffix(api_key)}"
    )

    log("WEEX_API_SECRET_VALUE=REDACTED")
    log("WEEX_API_PASSPHRASE_VALUE=REDACTED")

    return (
        api_key,
        api_secret,
        api_passphrase,
        credentials_present,
    )


# =============================================================================
# PUBLIC V2 MARK PRICE
# =============================================================================

def read_public_mark_price():

    global PUBLIC_MARKET_GETS
    global PUBLIC_MARK_PRICE_READ_OK
    global MARK_PRICE

    heading(f"{VERSION}: TEST 3: PUBLIC V2 MARK PRICE")

    log(f"CANONICAL_SYMBOL={CANONICAL_SYMBOL}")
    log(f"V2_MARKET_SYMBOL={V2_MARKET_SYMBOL}")
    log(f"PATH={MARK_PRICE_PATH}")

    query = urllib.parse.urlencode(
        {
            "symbol": V2_MARKET_SYMBOL,
        }
    )

    url = (
        WEEX_CONTRACT_BASE
        + MARK_PRICE_PATH
        + "?"
        + query
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}/1.0",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            PUBLIC_MARKET_GETS += 1

            status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

        log(f"HTTP_STATUS={status}")

        payload = json.loads(raw)

        response_symbol = None
        mark_price = None
        mark_price_field = None

        # WEEX V2 ticker may return an object directly.
        if isinstance(payload, dict):

            candidate = payload

            # Some APIs wrap the actual result in "data".
            if "data" in payload:

                data = payload.get("data")

                if isinstance(data, dict):
                    candidate = data

                elif (
                    isinstance(data, list)
                    and len(data) > 0
                    and isinstance(data[0], dict)
                ):
                    candidate = data[0]

            response_symbol = candidate.get("symbol")

            possible_fields = [
                "markPrice",
                "mark_price",
                "last",
                "lastPrice",
                "price",
            ]

            for field in possible_fields:

                value = candidate.get(field)

                if value is not None:

                    try:
                        parsed = float(value)

                        if parsed > 0:
                            mark_price = parsed
                            mark_price_field = field
                            break

                    except Exception:
                        pass

        response_symbol_match = (
            response_symbol == V2_MARKET_SYMBOL
        )

        log(
            "RESPONSE_SYMBOL="
            f"{response_symbol}"
        )

        log(
            "RESPONSE_SYMBOL_MATCH="
            f"{safe_bool(response_symbol_match)}"
        )

        if mark_price is not None:

            MARK_PRICE = mark_price
            PUBLIC_MARK_PRICE_READ_OK = True

            log(f"MARK_PRICE={MARK_PRICE}")
            log(f"MARK_PRICE_FIELD={mark_price_field}")
            log("PUBLIC_MARK_PRICE_READ_OK=True")

        else:

            MARK_PRICE = None
            PUBLIC_MARK_PRICE_READ_OK = False

            log("MARK_PRICE=UNKNOWN")
            log("MARK_PRICE_FIELD=UNKNOWN")
            log("PUBLIC_MARK_PRICE_READ_OK=False")

    except urllib.error.HTTPError as exc:

        PUBLIC_MARKET_GETS += 1
        PUBLIC_MARK_PRICE_READ_OK = False

        body = ""

        try:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            body = ""

        log(f"HTTP_STATUS={exc.code}")
        log(f"HTTP_ERROR_BODY={body}")
        log("PUBLIC_MARK_PRICE_READ_OK=False")

    except Exception as exc:

        PUBLIC_MARK_PRICE_READ_OK = False

        log(
            "PUBLIC_MARK_PRICE_EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            "PUBLIC_MARK_PRICE_EXCEPTION_MESSAGE="
            f"{exc}"
        )

        log("PUBLIC_MARK_PRICE_READ_OK=False")


# =============================================================================
# WEEX SIGNATURE
# =============================================================================

def build_signature(
    api_secret,
    timestamp_ms,
    method,
    request_path,
    query_string="",
    body="",
):
    """
    WEEX signing rule:

    If queryString is empty:

        timestamp
        + METHOD
        + requestPath
        + body

    If queryString exists:

        timestamp
        + METHOD
        + requestPath
        + "?"
        + queryString
        + body

    For R35P-I:

        GET /capi/v3/account/balance

    has:

        query_string = ""
        body         = ""

    Therefore the unsigned message shape is:

        <timestamp>GET/capi/v3/account/balance

    The secret itself is never logged.
    """

    global SIGNATURE_MESSAGE_FORMAT_OK
    global SIGNATURE_BASE64_FORMAT_OK

    method_upper = method.upper()

    if query_string:

        unsigned_message = (
            str(timestamp_ms)
            + method_upper
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        unsigned_message = (
            str(timestamp_ms)
            + method_upper
            + request_path
            + body
        )

    expected_message = (
        str(timestamp_ms)
        + "GET"
        + BALANCE_PATH
    )

    SIGNATURE_MESSAGE_FORMAT_OK = (
        unsigned_message == expected_message
    )

    digest = hmac.new(
        api_secret.encode("utf-8"),
        unsigned_message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    signature = base64.b64encode(
        digest
    ).decode("utf-8")

    try:
        decoded = base64.b64decode(
            signature,
            validate=True,
        )

        SIGNATURE_BASE64_FORMAT_OK = (
            len(decoded) == 32
        )

    except Exception:

        SIGNATURE_BASE64_FORMAT_OK = False

    return signature


# =============================================================================
# SAFE ERROR BODY PARSER
# =============================================================================

def parse_weex_error_body(raw_body):

    error_code = None
    error_message = None

    if not raw_body:
        return error_code, error_message

    try:

        parsed = json.loads(raw_body)

        if isinstance(parsed, dict):

            possible_code_fields = [
                "code",
                "errorCode",
                "error_code",
            ]

            possible_message_fields = [
                "msg",
                "message",
                "error",
                "errorMessage",
                "error_message",
            ]

            for field in possible_code_fields:

                if parsed.get(field) is not None:
                    error_code = parsed.get(field)
                    break

            for field in possible_message_fields:

                if parsed.get(field) is not None:
                    error_message = parsed.get(field)
                    break

    except Exception:

        # Preserve raw body at caller level.
        pass

    return error_code, error_message


# =============================================================================
# EXACTLY ONE AUTHENTICATED BALANCE GET
# =============================================================================

def authenticated_balance_diagnostic(
    api_key,
    api_secret,
    api_passphrase,
):

    global AUTHENTICATED_WEEX_READS
    global BALANCE_READ_OK
    global AVAILABLE_BALANCE

    global AUTH_HTTP_STATUS
    global AUTH_ERROR_BODY
    global AUTH_ERROR_CODE
    global AUTH_ERROR_MESSAGE

    heading(
        f"{VERSION}: TEST 4: "
        "AUTHENTICATED BALANCE SIGNATURE DIAGNOSTIC"
    )

    method = "GET"
    request_path = BALANCE_PATH

    query_string = ""
    body = ""

    timestamp_ms = str(
        int(time.time() * 1000)
    )

    log(f"METHOD={method}")
    log(f"PATH={request_path}")
    log("QUERY_STRING=<EMPTY>")
    log("BODY=<EMPTY>")

    log(f"TIMESTAMP_MS={timestamp_ms}")
    log(
        "TIMESTAMP_DIGITS="
        f"{len(timestamp_ms)}"
    )

    signature = build_signature(
        api_secret=api_secret,
        timestamp_ms=timestamp_ms,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    log(
        "SIGNATURE_MESSAGE_FORMAT_OK="
        f"{safe_bool(SIGNATURE_MESSAGE_FORMAT_OK)}"
    )

    log(
        "SIGNATURE_BASE64_FORMAT_OK="
        f"{safe_bool(SIGNATURE_BASE64_FORMAT_OK)}"
    )

    # Never print the actual signature.
    log(
        "SIGNATURE_LENGTH="
        f"{len(signature)}"
    )

    log("ACCESS_SIGN_VALUE=REDACTED")

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": api_passphrase,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}/1.0",
    }

    url = (
        WEEX_CONTRACT_BASE
        + request_path
    )

    # -------------------------------------------------------------------------
    # IMPORTANT:
    #
    # This is the ONLY authenticated WEEX request in R35P-I.
    #
    # It is GET only.
    #
    # There is no POST, PUT, PATCH or DELETE exchange request anywhere
    # in this program.
    # -------------------------------------------------------------------------

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            AUTHENTICATED_WEEX_READS += 1

            AUTH_HTTP_STATUS = response.getcode()

            raw_body = response.read().decode(
                "utf-8",
                errors="replace",
            )

        log(f"HTTP_STATUS={AUTH_HTTP_STATUS}")

        payload = json.loads(raw_body)

        usdt_record = None

        if isinstance(payload, list):

            for item in payload:

                if (
                    isinstance(item, dict)
                    and str(
                        item.get("asset", "")
                    ).upper() == "USDT"
                ):
                    usdt_record = item
                    break

        elif isinstance(payload, dict):

            data = payload.get("data")

            if isinstance(data, list):

                for item in data:

                    if (
                        isinstance(item, dict)
                        and str(
                            item.get("asset", "")
                        ).upper() == "USDT"
                    ):
                        usdt_record = item
                        break

            elif isinstance(data, dict):

                if str(
                    data.get("asset", "")
                ).upper() == "USDT":
                    usdt_record = data

            elif str(
                payload.get("asset", "")
            ).upper() == "USDT":

                usdt_record = payload

        if usdt_record is not None:

            raw_available = usdt_record.get(
                "availableBalance"
            )

            try:

                AVAILABLE_BALANCE = float(
                    raw_available
                )

            except Exception:

                AVAILABLE_BALANCE = None

        if (
            AUTH_HTTP_STATUS == 200
            and AVAILABLE_BALANCE is not None
        ):

            BALANCE_READ_OK = True

            log("AUTHENTICATED_BALANCE_HTTP_OK=True")
            log("BALANCE_READ_OK=True")
            log(
                "AVAILABLE_BALANCE="
                f"{AVAILABLE_BALANCE}"
            )

        else:

            BALANCE_READ_OK = False

            log(
                "AUTHENTICATED_BALANCE_HTTP_OK="
                f"{safe_bool(AUTH_HTTP_STATUS == 200)}"
            )

            log("BALANCE_READ_OK=False")
            log("AVAILABLE_BALANCE=UNKNOWN")

    except urllib.error.HTTPError as exc:

        # The server responded, so count this as an authenticated
        # read attempt even though authentication failed.
        AUTHENTICATED_WEEX_READS += 1

        AUTH_HTTP_STATUS = exc.code
        BALANCE_READ_OK = False
        AVAILABLE_BALANCE = None

        try:

            AUTH_ERROR_BODY = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:

            AUTH_ERROR_BODY = ""

        (
            AUTH_ERROR_CODE,
            AUTH_ERROR_MESSAGE,
        ) = parse_weex_error_body(
            AUTH_ERROR_BODY
        )

        log(f"HTTP_STATUS={AUTH_HTTP_STATUS}")

        log(
            "HTTP_REASON="
            f"{getattr(exc, 'reason', 'UNKNOWN')}"
        )

        log(
            "WEEX_ERROR_BODY="
            f"{AUTH_ERROR_BODY}"
        )

        log(
            "WEEX_ERROR_CODE="
            f"{AUTH_ERROR_CODE}"
        )

        log(
            "WEEX_ERROR_MESSAGE="
            f"{AUTH_ERROR_MESSAGE}"
        )

        log("BALANCE_READ_OK=False")
        log("AVAILABLE_BALANCE=UNKNOWN")

    except urllib.error.URLError as exc:

        BALANCE_READ_OK = False
        AVAILABLE_BALANCE = None

        log("HTTP_STATUS=NO_RESPONSE")

        log(
            "URL_ERROR_REASON="
            f"{exc.reason}"
        )

        log("BALANCE_READ_OK=False")
        log("AVAILABLE_BALANCE=UNKNOWN")

    except Exception as exc:

        BALANCE_READ_OK = False
        AVAILABLE_BALANCE = None

        log("HTTP_STATUS=UNKNOWN")

        log(
            "EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            "EXCEPTION_MESSAGE="
            f"{exc}"
        )

        log("BALANCE_READ_OK=False")
        log("AVAILABLE_BALANCE=UNKNOWN")


# =============================================================================
# SAFETY INVARIANT CHECK
# =============================================================================

def safety_invariants_ok():

    return (
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


# =============================================================================
# FINAL DIAGNOSTIC
# =============================================================================

def final_report(credentials_present):

    global TEST_STATUS
    global EXECUTION_PERMISSION

    heading(
        f"{VERSION}: AUTHENTICATION DIAGNOSTIC RESULT"
    )

    safety_ok = safety_invariants_ok()

    log(f"DNS_OK={safe_bool(DNS_OK)}")

    log(
        "CREDENTIALS_PRESENT="
        f"{safe_bool(credentials_present)}"
    )

    log(
        "PUBLIC_MARK_PRICE_READ_OK="
        f"{safe_bool(PUBLIC_MARK_PRICE_READ_OK)}"
    )

    if MARK_PRICE is None:
        log("MARK_PRICE=UNKNOWN")
    else:
        log(f"MARK_PRICE={MARK_PRICE}")

    log(
        "SIGNATURE_MESSAGE_FORMAT_OK="
        f"{safe_bool(SIGNATURE_MESSAGE_FORMAT_OK)}"
    )

    log(
        "SIGNATURE_BASE64_FORMAT_OK="
        f"{safe_bool(SIGNATURE_BASE64_FORMAT_OK)}"
    )

    log(
        "BALANCE_READ_OK="
        f"{safe_bool(BALANCE_READ_OK)}"
    )

    if AVAILABLE_BALANCE is None:
        log("AVAILABLE_BALANCE=UNKNOWN")
    else:
        log(
            "AVAILABLE_BALANCE="
            f"{AVAILABLE_BALANCE}"
        )

    log(
        "AUTH_HTTP_STATUS="
        f"{AUTH_HTTP_STATUS}"
    )

    log(
        "AUTH_ERROR_CODE="
        f"{AUTH_ERROR_CODE}"
    )

    log(
        "AUTH_ERROR_MESSAGE="
        f"{AUTH_ERROR_MESSAGE}"
    )

    log(
        "PUBLIC_MARKET_GETS="
        f"{PUBLIC_MARKET_GETS}"
    )

    log(
        "AUTHENTICATED_WEEX_READS="
        f"{AUTHENTICATED_WEEX_READS}"
    )

    log(
        "EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        "ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        "LEVERAGE_MUTATIONS="
        f"{LEVERAGE_MUTATIONS}"
    )

    log(
        "MARGIN_MODE_MUTATIONS="
        f"{MARGIN_MODE_MUTATIONS}"
    )

    log(
        "POSITION_MUTATIONS="
        f"{POSITION_MUTATIONS}"
    )

    log(
        "SAFETY_INVARIANTS_OK="
        f"{safe_bool(safety_ok)}"
    )

    if (
        DNS_OK
        and credentials_present
        and PUBLIC_MARK_PRICE_READ_OK
        and SIGNATURE_MESSAGE_FORMAT_OK
        and SIGNATURE_BASE64_FORMAT_OK
        and BALANCE_READ_OK
        and safety_ok
    ):

        TEST_STATUS = "PASS"

        log("AUTHENTICATED_WEEX_READ_OK=True")

    else:

        TEST_STATUS = "FAIL"

        log("AUTHENTICATED_WEEX_READ_OK=False")

    # R35P-I never grants execution permission.
    EXECUTION_PERMISSION = "NOT_GRANTED"

    log(f"TEST_STATUS={TEST_STATUS}")
    log(
        "EXECUTION_PERMISSION="
        f"{EXECUTION_PERMISSION}"
    )

    log("REAL_ORDER_PATH=ABSENT")
    log("MUTATION_PATH=ABSENT")


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop(credentials_present):

    heartbeat = 0

    while True:

        heartbeat += 1

        safety_ok = safety_invariants_ok()

        mark_value = (
            MARK_PRICE
            if MARK_PRICE is not None
            else "UNKNOWN"
        )

        balance_value = (
            AVAILABLE_BALANCE
            if AVAILABLE_BALANCE is not None
            else "UNKNOWN"
        )

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"DNS_OK={safe_bool(DNS_OK)} "
            f"CREDENTIALS_PRESENT={safe_bool(credentials_present)} "
            f"PUBLIC_MARK_PRICE_READ_OK="
            f"{safe_bool(PUBLIC_MARK_PRICE_READ_OK)} "
            f"MARK_PRICE={mark_value} "
            f"SIGNATURE_MESSAGE_FORMAT_OK="
            f"{safe_bool(SIGNATURE_MESSAGE_FORMAT_OK)} "
            f"SIGNATURE_BASE64_FORMAT_OK="
            f"{safe_bool(SIGNATURE_BASE64_FORMAT_OK)} "
            f"BALANCE_READ_OK="
            f"{safe_bool(BALANCE_READ_OK)} "
            f"AVAILABLE_BALANCE={balance_value} "
            f"AUTH_HTTP_STATUS={AUTH_HTTP_STATUS} "
            f"AUTH_ERROR_CODE={AUTH_ERROR_CODE} "
            f"TEST_STATUS={TEST_STATUS} "
            f"SAFETY_INVARIANTS_OK="
            f"{safe_bool(safety_ok)} "
            f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS} "
            f"AUTHENTICATED_WEEX_READS="
            f"{AUTHENTICATED_WEEX_READS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{safe_bool(REAL_ORDER_EXECUTION)}"
        )

        time.sleep(60)


# =============================================================================
# MAIN
# =============================================================================

def main():

    start_health_server()

    heading(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: VERSION={VERSION}")

    log(
        f"{VERSION}: "
        f"CANONICAL_SYMBOL={CANONICAL_SYMBOL}"
    )

    log(
        f"{VERSION}: "
        f"V2_MARKET_SYMBOL={V2_MARKET_SYMBOL}"
    )

    log(
        f"{VERSION}: "
        f"V3_AUTH_SYMBOL={V3_AUTH_SYMBOL}"
    )

    log(
        f"{VERSION}: "
        f"WEEX CONTRACT BASE={WEEX_CONTRACT_BASE}"
    )

    log(
        f"{VERSION}: "
        f"MARK PRICE PATH={MARK_PRICE_PATH}"
    )

    log(
        f"{VERSION}: "
        f"BALANCE PATH={BALANCE_PATH}"
    )

    log(
        f"{VERSION}: "
        f"TARGET MARGIN MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"{VERSION}: "
        f"TARGET LONG LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"{VERSION}: "
        f"TARGET SHORT LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"{VERSION}: "
        f"ENTRY BALANCE PERCENT="
        f"{ENTRY_BALANCE_PERCENT}%"
    )

    log(
        f"{VERSION}: "
        f"MAX FUND EXPOSURE PERCENT="
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    log(
        f"{VERSION}: "
        f"QTY STEP={QTY_STEP}"
    )

    log(
        f"{VERSION}: "
        f"MIN QTY={MIN_QTY}"
    )

    heading(f"{VERSION}: HARD WRITE FIREBREAK")

    log(
        "REAL_ORDER_EXECUTION="
        f"{safe_bool(REAL_ORDER_EXECUTION)}"
    )

    log(
        "FIRST_REAL_ORDER_ALLOWED="
        f"{safe_bool(FIRST_REAL_ORDER_ALLOWED)}"
    )

    log(
        "DEMO_ORDER_EXECUTION="
        f"{safe_bool(DEMO_ORDER_EXECUTION)}"
    )

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{safe_bool(EXCHANGE_MUTATION_TRANSPORT_ENABLED)}"
    )

    log(
        "ORDER_SUBMISSION_ENABLED="
        f"{safe_bool(ORDER_SUBMISSION_ENABLED)}"
    )

    log(
        "LEVERAGE_MUTATION_ENABLED="
        f"{safe_bool(LEVERAGE_MUTATION_ENABLED)}"
    )

    log(
        "MARGIN_MODE_MUTATION_ENABLED="
        f"{safe_bool(MARGIN_MODE_MUTATION_ENABLED)}"
    )

    log(
        "POSITION_MUTATION_ENABLED="
        f"{safe_bool(POSITION_MUTATION_ENABLED)}"
    )

    # -------------------------------------------------------------------------
    # TEST 1
    # -------------------------------------------------------------------------

    run_dns_test()

    # -------------------------------------------------------------------------
    # TEST 2
    # -------------------------------------------------------------------------

    (
        api_key,
        api_secret,
        api_passphrase,
        credentials_present,
    ) = credential_check()

    # -------------------------------------------------------------------------
    # TEST 3
    # -------------------------------------------------------------------------

    read_public_mark_price()

    # -------------------------------------------------------------------------
    # TEST 4
    #
    # EXACTLY ONE authenticated balance GET.
    # -------------------------------------------------------------------------

    if not credentials_present:

        heading(
            f"{VERSION}: TEST 4: "
            "AUTHENTICATED BALANCE SIGNATURE DIAGNOSTIC"
        )

        log(
            "AUTHENTICATED_BALANCE_TEST_SKIPPED=True"
        )

        log(
            "REASON=MISSING_REQUIRED_CREDENTIAL"
        )

    else:

        authenticated_balance_diagnostic(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
        )

    # -------------------------------------------------------------------------
    # FINAL REPORT
    # -------------------------------------------------------------------------

    final_report(
        credentials_present=credentials_present
    )

    # -------------------------------------------------------------------------
    # R35P-I intentionally ends all exchange testing here.
    #
    # No position GET.
    # No symbol-config GET.
    # No order calculation.
    # No synthetic order envelope.
    # No exchange write.
    # -------------------------------------------------------------------------

    heartbeat_loop(
        credentials_present=credentials_present
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        log(f"{VERSION}: STOPPED")

    except Exception as exc:

        heading(
            f"{VERSION}: UNHANDLED ERROR DIAGNOSTIC"
        )

        log(
            "EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            "EXCEPTION_MESSAGE="
            f"{exc}"
        )

        log(
            "EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES}"
        )

        log(
            "ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS}"
        )

        log(
            "REAL_ORDER_EXECUTION="
            f"{safe_bool(REAL_ORDER_EXECUTION)}"
        )

        log(
            "FIRST_REAL_ORDER_ALLOWED="
            f"{safe_bool(FIRST_REAL_ORDER_ALLOWED)}"
        )

        log(
            "SAFETY_INVARIANTS_OK="
            f"{safe_bool(safety_invariants_ok())}"
        )

        # Keep Render service alive so the diagnostic remains visible.
        heartbeat = 0

        while True:

            heartbeat += 1

            log(
                f"{VERSION}: "
                f"ERROR_HEARTBEAT={heartbeat} "
                f"EXCHANGE_NETWORK_WRITES="
                f"{EXCHANGE_NETWORK_WRITES} "
                f"ORDER_SUBMISSIONS="
                f"{ORDER_SUBMISSIONS} "
                f"REAL_ORDER_EXECUTION="
                f"{safe_bool(REAL_ORDER_EXECUTION)}"
            )

            time.sleep(60)

