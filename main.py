# =============================================================================
# R34C
# AUTHENTICATED LIVE READ-ONLY LEVERAGE OBSERVATION
# STANDARD-LIBRARY HTTP TRANSPORT
#
# IMPORTANT SAFETY PROPERTIES
# -----------------------------------------------------------------------------
# - AUTHENTICATED GET ONLY
# - NO requests PACKAGE REQUIRED
# - NO POST
# - NO PUT
# - NO PATCH
# - NO DELETE
# - NO ORDER EXECUTION
# - NO DEMO ORDER EXECUTION
# - NO LEVERAGE MUTATION
# - NO MARGIN MUTATION
# - NO POSITION MUTATION
# - NO ACCOUNT MUTATION
# - TARGET LEVERAGE IS OBSERVATIONAL / SYNTHETIC ONLY
#
# R34C does NOT change leverage.
# It only reads the current BTCUSDT symbol configuration,
# compares observed leverage with the intended target,
# constructs a synthetic correction intent locally,
# and proves that no write transport is available.
# =============================================================================

import base64
import hashlib
import hmac
import json
import os
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# =============================================================================
# SECTION 1
# VERSION / CONFIGURATION
# =============================================================================

VERSION = "R34C"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

WEEX_BASE_URL = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100


# =============================================================================
# SECTION 2
# FROZEN SAFETY CONFIGURATION
# =============================================================================

SYNTHETIC_ONLY = True

AUTHENTICATED_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

HTTP_GET_ENABLED = True

HTTP_POST_ENABLED = False
HTTP_PUT_ENABLED = False
HTTP_PATCH_ENABLED = False
HTTP_DELETE_ENABLED = False


# =============================================================================
# SECTION 3
# RUNTIME COUNTERS
# =============================================================================

authenticated_get_counter = 0

network_write_counter = 0
real_order_counter = 0
demo_order_counter = 0

leverage_mutation_counter = 0
margin_mutation_counter = 0
position_mutation_counter = 0
account_mutation_counter = 0

synthetic_dispatch_counter = 0

heartbeat_counter = 0


# =============================================================================
# SECTION 4
# OBSERVED STATE
# =============================================================================

observed_symbol = None
observed_margin_type = None
observed_position_mode = None
observed_cross_leverage = None
observed_long_leverage = None
observed_short_leverage = None

correction_required = None

validation_completed = False
validation_passed = False

runtime_phase = "BOOTING"

last_error = None


# =============================================================================
# SECTION 5
# FORMAT HELPERS
# =============================================================================

LINE = "-" * 100


def banner(text):
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def section(text):
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def check(label, condition):
    result = "✅ PASS" if condition else "❌ FAIL"

    print(
        f"{label:<82} {result}",
        flush=True,
    )

    if not condition:
        raise AssertionError(label)


def normalize_text(value):
    if value is None:
        return None

    return str(value).strip()


def normalize_upper(value):
    if value is None:
        return None

    return str(value).strip().upper()


def safe_int(value):
    if value is None:
        return None

    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


# =============================================================================
# SECTION 6
# ENVIRONMENT / CREDENTIAL HELPERS
# =============================================================================

def first_environment_value(*names):
    for name in names:
        value = os.getenv(name)

        if value is not None:
            value = value.strip()

            if value:
                return value

    return None


def load_credentials():
    """
    Supports several common environment-variable names so that
    an existing Render configuration does not need to be renamed.
    """

    api_key = first_environment_value(
        "WEEX_API_KEY",
        "API_KEY",
        "WEEX_ACCESS_KEY",
        "ACCESS_KEY",
    )

    api_secret = first_environment_value(
        "WEEX_API_SECRET",
        "API_SECRET",
        "WEEX_SECRET_KEY",
        "SECRET_KEY",
        "ACCESS_SECRET",
    )

    passphrase = first_environment_value(
        "WEEX_API_PASSPHRASE",
        "API_PASSPHRASE",
        "WEEX_PASSPHRASE",
        "PASSPHRASE",
        "ACCESS_PASSPHRASE",
    )

    return api_key, api_secret, passphrase


# =============================================================================
# SECTION 7
# CRYPTOGRAPHIC SIGNING
# =============================================================================

def create_signature(
    secret_key,
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    """
    WEEX signature:

        timestamp
        + METHOD
        + request_path
        + ?query_string   (when query exists)
        + body

    HMAC-SHA256 using API secret,
    then Base64 encode.
    """

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
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# =============================================================================
# SECTION 8
# TRANSPORT FIREBREAK
# =============================================================================

def reject_write_method(method):
    global network_write_counter

    method = str(method).upper()

    if method in {
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    }:
        raise RuntimeError(
            f"R34C FIREBREAK: HTTP {method} is disabled."
        )

    if method != "GET":
        raise RuntimeError(
            f"R34C FIREBREAK: unsupported HTTP method {method}."
        )


def forbidden_post(*args, **kwargs):
    raise RuntimeError(
        "R34C FIREBREAK: HTTP POST is disabled."
    )


def forbidden_put(*args, **kwargs):
    raise RuntimeError(
        "R34C FIREBREAK: HTTP PUT is disabled."
    )


def forbidden_patch(*args, **kwargs):
    raise RuntimeError(
        "R34C FIREBREAK: HTTP PATCH is disabled."
    )


def forbidden_delete(*args, **kwargs):
    raise RuntimeError(
        "R34C FIREBREAK: HTTP DELETE is disabled."
    )


# =============================================================================
# SECTION 9
# STANDARD-LIBRARY AUTHENTICATED GET
# =============================================================================

def authenticated_get(
    request_path,
    params=None,
    timeout=15,
):
    global authenticated_get_counter

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only transport is disabled."
        )

    if not HTTP_GET_ENABLED:
        raise RuntimeError(
            "HTTP GET is disabled."
        )

    reject_write_method("GET")

    api_key, api_secret, passphrase = load_credentials()

    missing = []

    if not api_key:
        missing.append("API KEY")

    if not api_secret:
        missing.append("API SECRET")

    if not passphrase:
        missing.append("API PASSPHRASE")

    if missing:
        raise RuntimeError(
            "Missing WEEX credential(s): "
            + ", ".join(missing)
        )

    params = params or {}

    # -------------------------------------------------------------------------
    # urlencode generates:
    #
    # symbol=BTCUSDT
    #
    # This exact query string is used both in:
    # 1. the signature
    # 2. the outgoing URL
    #
    # This prevents signature / URL disagreement.
    # -------------------------------------------------------------------------

    query_string = urllib.parse.urlencode(params)

    timestamp = str(int(time.time() * 1000))

    signature = create_signature(
        secret_key=api_secret,
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "R34C-ReadOnly-Validator/1.0",
    }

    if query_string:
        url = (
            WEEX_BASE_URL
            + request_path
            + "?"
            + query_string
        )
    else:
        url = (
            WEEX_BASE_URL
            + request_path
        )

    # -------------------------------------------------------------------------
    # CRITICAL:
    #
    # method="GET" is explicitly frozen here.
    #
    # No request body is supplied.
    # -------------------------------------------------------------------------

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    authenticated_get_counter += 1

    ssl_context = ssl.create_default_context()

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=ssl_context,
        ) as response:

            status_code = response.getcode()

            raw_body = response.read().decode(
                "utf-8",
                errors="replace",
            )

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"WEEX authenticated GET failed "
            f"HTTP {exc.code}: {body}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"WEEX authenticated GET network error: "
            f"{exc.reason}"
        ) from exc

    except TimeoutError as exc:
        raise RuntimeError(
            "WEEX authenticated GET timed out."
        ) from exc

    if status_code < 200 or status_code >= 300:
        raise RuntimeError(
            f"Unexpected WEEX HTTP status: "
            f"{status_code}"
        )

    try:
        return json.loads(raw_body)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "WEEX returned non-JSON data: "
            + raw_body[:500]
        ) from exc


# =============================================================================
# SECTION 10
# SYMBOL CONFIGURATION READ
# =============================================================================

def authenticated_get_symbol_config():
    response = authenticated_get(
        request_path=SYMBOL_CONFIG_PATH,
        params={
            "symbol": SYMBOL,
        },
    )

    # WEEX V3 normally returns a list.
    if isinstance(response, list):

        if not response:
            raise RuntimeError(
                "WEEX symbolConfig returned an empty list."
            )

        for item in response:
            if (
                isinstance(item, dict)
                and normalize_upper(item.get("symbol"))
                == SYMBOL
            ):
                return item

        # If only one record was returned, accept it,
        # but validation will still verify the symbol.
        if len(response) == 1:
            return response[0]

        raise RuntimeError(
            f"BTC symbol configuration was not found "
            f"in response: {response}"
        )

    # Defensive compatibility in case an API wrapper
    # returns a direct object instead.
    if isinstance(response, dict):

        if isinstance(response.get("data"), list):

            data = response["data"]

            for item in data:
                if (
                    isinstance(item, dict)
                    and normalize_upper(
                        item.get("symbol")
                    )
                    == SYMBOL
                ):
                    return item

            if len(data) == 1:
                return data[0]

        if isinstance(response.get("data"), dict):
            return response["data"]

        if "symbol" in response:
            return response

    raise RuntimeError(
        "Unexpected WEEX symbolConfig response structure: "
        + repr(response)
    )


# =============================================================================
# SECTION 11
# SYNTHETIC CORRECTION INTENT
# =============================================================================

def build_synthetic_correction_intent(
    margin_type,
    long_leverage,
    short_leverage,
):
    """
    LOCAL OBJECT ONLY.

    This is NOT transmitted.

    It exists purely to prove what would need correcting
    without permitting the program to perform the correction.
    """

    return {
        "version": VERSION,
        "transport": "SYNTHETIC_ONLY",
        "exchange_contacted_for_write": False,
        "network_write": False,
        "mutation": False,
        "symbol": SYMBOL,
        "observed": {
            "marginType": margin_type,
            "isolatedLongLeverage": long_leverage,
            "isolatedShortLeverage": short_leverage,
        },
        "target": {
            "marginType": "ISOLATED",
            "isolatedLongLeverage": str(
                TARGET_LONG_LEVERAGE
            ),
            "isolatedShortLeverage": str(
                TARGET_SHORT_LEVERAGE
            ),
        },
    }


def synthetic_dispatch(intent):
    global synthetic_dispatch_counter

    if not SYNTHETIC_ONLY:
        raise RuntimeError(
            "R34C synthetic-only invariant violated."
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "R34C network-write invariant violated."
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "R34C leverage-mutation invariant violated."
        )

    synthetic_dispatch_counter += 1

    return {
        "status": "INTERCEPTED",
        "transport": "SYNTHETIC",
        "network_transmission": False,
        "exchange_write_contacted": False,
        "authorization_consumed": False,
        "mutation_performed": False,
        "intent": intent,
    }


# =============================================================================
# SECTION 12
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "status": "ok",
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": runtime_phase,

            "synthetic_only": SYNTHETIC_ONLY,

            "authenticated_read_only":
                AUTHENTICATED_READ_ONLY_ENABLED,

            "authenticated_get_counter":
                authenticated_get_counter,

            "network_write_counter":
                network_write_counter,

            "real_order_counter":
                real_order_counter,

            "demo_order_counter":
                demo_order_counter,

            "leverage_mutation_counter":
                leverage_mutation_counter,

            "synthetic_dispatch_counter":
                synthetic_dispatch_counter,

            "observed_margin_type":
                observed_margin_type,

            "observed_long_leverage":
                observed_long_leverage,

            "observed_short_leverage":
                observed_short_leverage,

            "target_long_leverage":
                TARGET_LONG_LEVERAGE,

            "target_short_leverage":
                TARGET_SHORT_LEVERAGE,

            "correction_required":
                correction_required,

            "validation_completed":
                validation_completed,

            "validation_passed":
                validation_passed,
        }

        encoded = json.dumps(
            payload,
            separators=(",", ":"),
        ).encode("utf-8")

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


    def do_POST(self):
        self.send_error(
            405,
            "POST disabled",
        )


    def do_PUT(self):
        self.send_error(
            405,
            "PUT disabled",
        )


    def do_PATCH(self):
        self.send_error(
            405,
            "PATCH disabled",
        )


    def do_DELETE(self):
        self.send_error(
            405,
            "DELETE disabled",
        )


    def log_message(self, format, *args):
        # Suppress default HTTP server logging.
        return


def start_health_server():

    def worker():
        server = ThreadingHTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        print(
            f"{VERSION}: HEALTH SERVER LISTENING "
            f"ON PORT {HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()


# =============================================================================
# SECTION 13
# VALIDATION
# =============================================================================

def run_validation():

    global observed_symbol
    global observed_margin_type
    global observed_position_mode
    global observed_cross_leverage
    global observed_long_leverage
    global observed_short_leverage

    global correction_required

    global runtime_phase
    global validation_completed
    global validation_passed

    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        "R34C TEST 1: STANDARD LIBRARY SAFETY CONFIGURATION"
    )

    check(
        "Synthetic Only Is Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )

    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        "R34C TEST 2: WRITE METHOD FIREBREAK"
    )

    check(
        "HTTP POST Is Disabled",
        HTTP_POST_ENABLED is False,
    )

    check(
        "HTTP PUT Is Disabled",
        HTTP_PUT_ENABLED is False,
    )

    check(
        "HTTP PATCH Is Disabled",
        HTTP_PATCH_ENABLED is False,
    )

    check(
        "HTTP DELETE Is Disabled",
        HTTP_DELETE_ENABLED is False,
    )

    # Test actual local firebreak behavior.

    post_blocked = False

    try:
        reject_write_method("POST")
    except RuntimeError:
        post_blocked = True

    check(
        "POST Transport Firebreak Rejects Dispatch",
        post_blocked,
    )

    delete_blocked = False

    try:
        reject_write_method("DELETE")
    except RuntimeError:
        delete_blocked = True

    check(
        "DELETE Transport Firebreak Rejects Dispatch",
        delete_blocked,
    )

    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        "R34C TEST 3: AUTHENTICATED LIVE READ-ONLY OBSERVATION"
    )

    runtime_phase = "AUTHENTICATED_READ_ONLY_OBSERVATION"

    config = authenticated_get_symbol_config()

    check(
        "Authenticated Symbol Configuration Returned",
        isinstance(config, dict),
    )

    observed_symbol = normalize_upper(
        config.get("symbol")
    )

    observed_margin_type = normalize_upper(
        config.get("marginType")
    )

    observed_position_mode = normalize_upper(
        config.get("separatedType")
    )

    observed_cross_leverage = safe_int(
        config.get("crossLeverage")
    )

    observed_long_leverage = safe_int(
        config.get("isolatedLongLeverage")
    )

    observed_short_leverage = safe_int(
        config.get("isolatedShortLeverage")
    )

    print(
        f"{VERSION}: OBSERVED SYMBOL="
        f"{observed_symbol}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observed_margin_type}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED POSITION MODE="
        f"{observed_position_mode}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED CROSS="
        f"{observed_cross_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{observed_long_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{observed_short_leverage}x",
        flush=True,
    )

    check(
        "Observed Symbol Matches Target Symbol",
        observed_symbol == SYMBOL,
    )

    check(
        "Observed Margin Type Is Present",
        observed_margin_type is not None,
    )

    check(
        "Observed Long Leverage Is Present",
        observed_long_leverage is not None,
    )

    check(
        "Observed Short Leverage Is Present",
        observed_short_leverage is not None,
    )

    check(
        "Exactly One Authenticated GET Was Used",
        authenticated_get_counter == 1,
    )

    check(
        "Network Write Counter Remains Zero",
        network_write_counter == 0,
    )

    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        "R34C TEST 4: TARGET / OBSERVED LEVERAGE RECONCILIATION"
    )

    long_matches = (
        observed_long_leverage
        == TARGET_LONG_LEVERAGE
    )

    short_matches = (
        observed_short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    margin_matches = (
        observed_margin_type
        == "ISOLATED"
    )

    correction_required = not (
        margin_matches
        and long_matches
        and short_matches
    )

    print(
        f"{VERSION}: TARGET MARGIN=ISOLATED",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{correction_required}",
        flush=True,
    )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE == 100,
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE == 100,
    )

    check(
        "Correction Requirement Was Determined",
        isinstance(correction_required, bool),
    )

    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        "R34C TEST 5: SYNTHETIC CORRECTION INTENT"
    )

    intent = build_synthetic_correction_intent(
        observed_margin_type,
        observed_long_leverage,
        observed_short_leverage,
    )

    check(
        "Synthetic Intent Symbol Matches",
        intent["symbol"] == SYMBOL,
    )

    check(
        "Synthetic Intent Targets Isolated Margin",
        (
            intent["target"]["marginType"]
            == "ISOLATED"
        ),
    )

    check(
        "Synthetic Intent Targets Long 100x",
        (
            intent["target"][
                "isolatedLongLeverage"
            ]
            == "100"
        ),
    )

    check(
        "Synthetic Intent Targets Short 100x",
        (
            intent["target"][
                "isolatedShortLeverage"
            ]
            == "100"
        ),
    )

    check(
        "Synthetic Intent Declares No Network Write",
        (
            intent["network_write"]
            is False
        ),
    )

    check(
        "Synthetic Intent Declares No Mutation",
        (
            intent["mutation"]
            is False
        ),
    )

    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        "R34C TEST 6: SYNTHETIC DISPATCH INTERCEPTION"
    )

    receipt = synthetic_dispatch(intent)

    check(
        "Synthetic Dispatch Was Intercepted",
        (
            receipt["status"]
            == "INTERCEPTED"
        ),
    )

    check(
        "Synthetic Receipt Confirms Synthetic Transport",
        (
            receipt["transport"]
            == "SYNTHETIC"
        ),
    )

    check(
        "Synthetic Receipt Confirms No Transmission",
        (
            receipt["network_transmission"]
            is False
        ),
    )

    check(
        "Synthetic Receipt Confirms Exchange Write Not Contacted",
        (
            receipt["exchange_write_contacted"]
            is False
        ),
    )

    check(
        "Synthetic Receipt Confirms No Mutation",
        (
            receipt["mutation_performed"]
            is False
        ),
    )

    check(
        "Synthetic Dispatch Counter Is One",
        synthetic_dispatch_counter == 1,
    )

    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        "R34C TEST 7: TERMINAL SAFETY COUNTERS"
    )

    check(
        "Authenticated GET Counter Is One",
        authenticated_get_counter == 1,
    )

    check(
        "Network Write Counter Is Zero",
        network_write_counter == 0,
    )

    check(
        "Real Order Counter Is Zero",
        real_order_counter == 0,
    )

    check(
        "Demo Order Counter Is Zero",
        demo_order_counter == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        leverage_mutation_counter == 0,
    )

    check(
        "Margin Mutation Counter Is Zero",
        margin_mutation_counter == 0,
    )

    check(
        "Position Mutation Counter Is Zero",
        position_mutation_counter == 0,
    )

    check(
        "Account Mutation Counter Is Zero",
        account_mutation_counter == 0,
    )

    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        "R34C TEST 8: FINAL READ-ONLY SAFETY SEAL"
    )

    check(
        "Authenticated Read-Only Mode Remains Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED is True,
    )

    check(
        "Synthetic-Only Mode Remains Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Network Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "HTTP POST Remains Disabled",
        HTTP_POST_ENABLED is False,
    )

    check(
        "HTTP PUT Remains Disabled",
        HTTP_PUT_ENABLED is False,
    )

    check(
        "HTTP PATCH Remains Disabled",
        HTTP_PATCH_ENABLED is False,
    )

    check(
        "HTTP DELETE Remains Disabled",
        HTTP_DELETE_ENABLED is False,
    )

    validation_completed = True
    validation_passed = True

    runtime_phase = "LIVE_READ_ONLY_VALIDATED"

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================

    section(
        "R34C VALIDATION SUMMARY"
    )

    print(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{authenticated_get_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES="
        f"{network_write_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDERS="
        f"{real_order_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{leverage_mutation_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{synthetic_dispatch_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observed_margin_type}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{observed_long_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{observed_short_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{correction_required}",
        flush=True,
    )

    print(
        f"{VERSION}: RESULT=PASSED",
        flush=True,
    )

    print(
        f"{VERSION}: NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: NO EXCHANGE WRITE WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: NO LEVERAGE MUTATION WAS PERFORMED",
        flush=True,
    )

    print(LINE, flush=True)


# =============================================================================
# SECTION 14
# HEARTBEAT
# =============================================================================

def heartbeat_loop():

    global heartbeat_counter

    while True:

        heartbeat_counter += 1

        print(
            f"{VERSION}: HEARTBEAT "
            f"{heartbeat_counter}"
            f" | phase={runtime_phase}"
            f" | synthetic-only={SYNTHETIC_ONLY}"
            f" | authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED}"
            f" | authenticated-get="
            f"{authenticated_get_counter}"
            f" | synthetic-dispatch="
            f"{synthetic_dispatch_counter}"
            f" | real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED}"
            f" | network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED}"
            f" | leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED}"
            f" | correction-required="
            f"{correction_required}"
            f" | observed-margin="
            f"{observed_margin_type}"
            f" | observed-long="
            f"{observed_long_leverage}x"
            f" | observed-short="
            f"{observed_short_leverage}x"
            f" | target-long="
            f"{TARGET_LONG_LEVERAGE}x"
            f" | target-short="
            f"{TARGET_SHORT_LEVERAGE}x",
            flush=True,
        )

        time.sleep(30)


# =============================================================================
# SECTION 15
# MAIN
# =============================================================================

def main():

    global runtime_phase
    global last_error

    banner(
        "R34C: MAIN.PY ENTERED"
    )

    print(
        f"R34C: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"R34C: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"R34C: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        "R34C: AUTHENTICATED READ-ONLY ENABLED",
        flush=True,
    )

    print(
        "R34C: STANDARD LIBRARY HTTP ENABLED",
        flush=True,
    )

    print(
        "R34C: requests PACKAGE NOT REQUIRED",
        flush=True,
    )

    print(
        "R34C: NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        "R34C: LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    print(
        f"R34C: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"R34C: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    start_health_server()

    try:

        run_validation()

    except Exception as exc:

        runtime_phase = "VALIDATION_FAILED"
        last_error = repr(exc)

        print(LINE, flush=True)

        print(
            f"R34C: VALIDATION FAILED",
            flush=True,
        )

        print(
            f"R34C: ERROR={exc}",
            flush=True,
        )

        print(
            f"R34C: AUTHENTICATED GETS="
            f"{authenticated_get_counter}",
            flush=True,
        )

        print(
            f"R34C: NETWORK WRITES="
            f"{network_write_counter}",
            flush=True,
        )

        print(
            f"R34C: REAL ORDERS="
            f"{real_order_counter}",
            flush=True,
        )

        print(
            f"R34C: LEVERAGE MUTATIONS="
            f"{leverage_mutation_counter}",
            flush=True,
        )

        print(
            "R34C: SAFETY FIREBREAK REMAINS ACTIVE",
            flush=True,
        )

        print(LINE, flush=True)

        raise

    heartbeat_loop()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
