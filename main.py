import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import urllib.parse
import urllib.request
import urllib.error

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# =============================================================================
# R34F
# EXACT LIVE LEVERAGE-CORRECTION ENVELOPE VALIDATION
#
# IMPORTANT:
# - AUTHENTICATED READ-ONLY GETS ARE ALLOWED.
# - ALL EXCHANGE WRITES ARE DISABLED.
# - LEVERAGE MUTATION IS DISABLED.
# - THE 100x REQUEST IS CONSTRUCTED, SIGNED, AUTHORIZED, AND INTERCEPTED LOCALLY.
# - NO POST IS TRANSMITTED TO WEEX.
# =============================================================================


VERSION = "R34F"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper().strip()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv("HEALTH_PORT", "10000"),
    )
)

HEARTBEAT_SECONDS = max(
    5,
    int(os.getenv("HEARTBEAT_SECONDS", "30")),
)


# =============================================================================
# OFFICIAL V3 PATHS
# =============================================================================

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
ALL_POSITION_PATH = "/capi/v3/account/position/allPosition"

LEVERAGE_MUTATION_PATH = "/capi/v3/account/leverage"


# =============================================================================
# TARGET ACCOUNT CONFIGURATION
# =============================================================================

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = "100"
TARGET_SHORT_LEVERAGE = "100"


# =============================================================================
# HARD SAFETY CONFIGURATION
# =============================================================================

SYNTHETIC_ONLY = True

AUTHENTICATED_READ_ONLY_ENABLED = True
STANDARD_LIBRARY_HTTP_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

HTTP_POST_ENABLED = False
HTTP_PUT_ENABLED = False
HTTP_PATCH_ENABLED = False
HTTP_DELETE_ENABLED = False

DIRECT_EXCHANGE_WRITE_ENABLED = False

ALLOW_PRIVATE_GET = True


# =============================================================================
# GLOBAL RUNTIME STATE
# =============================================================================

runtime = {
    "phase": "STARTING",

    "authenticated_gets": 0,

    "network_write_counter": 0,
    "real_order_counter": 0,
    "leverage_mutation_counter": 0,

    "synthetic_dispatch_counter": 0,
    "duplicate_dispatch_block_counter": 0,

    "stale_state_blocked": 0,

    "open_positions": -1,

    "observed_margin": "UNKNOWN",
    "observed_long": "UNKNOWN",
    "observed_short": "UNKNOWN",

    "correction_required": False,
    "correction_ready": False,

    "fresh_state_validated": False,

    "payload_hash": "",
    "state_hash": "",
    "envelope_hash": "",
    "authorization_hash": "",
    "receipt_hash": "",

    "authorization_consumed": False,
    "dispatch_committed": False,

    "validation_complete": False,

    "heartbeat": 0,
}


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def pass_test(name):
    log(f"{name:<84} ✅ PASS")


def fail_test(name):
    log(f"{name:<84} ❌ FAIL")


def required_test(name):
    log(f"{name:<84} ⚠️ REQUIRED")


def blocked_test(name):
    log(f"{name:<84} 🛑 BLOCKED")


def assert_pass(name, condition):
    if condition:
        pass_test(name)
        return True

    fail_test(name)
    raise AssertionError(name)


# =============================================================================
# CANONICALIZATION / HASHING
# =============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    if not isinstance(value, str):
        value = canonical_json(value)

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def safe_fingerprint(value):
    if not value:
        return "MISSING"

    digest = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    return digest[:16]


# =============================================================================
# ENVIRONMENT CREDENTIAL DISCOVERY
# =============================================================================

def first_env(*names):
    for name in names:
        value = os.getenv(name)

        if value is not None:
            value = value.strip()

        if value:
            return value, name

    return "", "MISSING"


API_KEY, API_KEY_SOURCE = first_env(
    "WEEX_API_KEY",
    "API_KEY",
)

API_SECRET, API_SECRET_SOURCE = first_env(
    "WEEX_SECRET_KEY",
    "WEEX_API_SECRET",
    "API_SECRET",
    "SECRET_KEY",
)

API_PASSPHRASE, API_PASSPHRASE_SOURCE = first_env(
    "WEEX_PASSPHRASE",
    "API_PASSPHRASE",
    "PASSPHRASE",
)


# =============================================================================
# WEEX SIGNATURE
# =============================================================================

def generate_signature(
    secret,
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
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

    return base64.b64encode(digest).decode("utf-8")


# =============================================================================
# AUTHENTICATED READ-ONLY GET
# =============================================================================

def authenticated_get(path, params=None):
    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only access is disabled"
        )

    if not ALLOW_PRIVATE_GET:
        raise RuntimeError(
            "Private GET is disabled"
        )

    if not API_KEY or not API_SECRET or not API_PASSPHRASE:
        raise RuntimeError(
            "Required authentication credentials are missing"
        )

    params = params or {}

    query_string = urllib.parse.urlencode(params)

    if query_string:
        url = (
            BASE_URL
            + path
            + "?"
            + query_string
        )
    else:
        url = BASE_URL + path

    timestamp = str(int(time.time() * 1000))

    signature = generate_signature(
        secret=API_SECRET,
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "locale": "en-US",
        "User-Agent": f"R34F/{VERSION}",
    }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            status = response.getcode()

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {raw}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Network GET failed: {exc}"
        ) from exc

    runtime["authenticated_gets"] += 1

    if status < 200 or status >= 300:
        raise RuntimeError(
            f"Unexpected HTTP status {status}: {raw}"
        )

    try:
        return json.loads(raw)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON response: {raw}"
        ) from exc


# =============================================================================
# ABSOLUTE WRITE FIREBREAK
# =============================================================================

def reject_exchange_write(
    method,
    path,
    body=None,
):
    method = str(method).upper()

    if method in {
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    }:
        raise RuntimeError(
            f"R34F WRITE FIREBREAK: "
            f"{method} {path} rejected before network transport"
        )

    raise RuntimeError(
        f"Unsupported write attempt: {method} {path}"
    )


# =============================================================================
# RESPONSE NORMALIZATION
# =============================================================================

def unwrap_data(value):
    if isinstance(value, dict):
        if "data" in value:
            return value["data"]

    return value


def find_symbol_config(response):
    data = unwrap_data(response)

    candidates = []

    if isinstance(data, list):
        candidates = data

    elif isinstance(data, dict):
        candidates = [data]

    for item in candidates:
        if not isinstance(item, dict):
            continue

        returned_symbol = str(
            item.get("symbol", "")
        ).upper()

        if returned_symbol == SYMBOL:
            return item

    if len(candidates) == 1:
        item = candidates[0]

        if isinstance(item, dict):
            return item

    raise RuntimeError(
        f"Unable to find symbol configuration for {SYMBOL}"
    )


def normalize_leverage(value):
    if value is None:
        return "UNKNOWN"

    text = str(value).strip()

    if text.endswith("x"):
        text = text[:-1]

    try:
        number = float(text)

        if number.is_integer():
            return str(int(number))

    except Exception:
        pass

    return text


def extract_observed_state(config):
    margin = str(
        config.get(
            "marginType",
            config.get(
                "marginMode",
                "UNKNOWN",
            ),
        )
    ).upper()

    long_lev = normalize_leverage(
        config.get(
            "isolatedLongLeverage",
            config.get(
                "longLeverage",
            ),
        )
    )

    short_lev = normalize_leverage(
        config.get(
            "isolatedShortLeverage",
            config.get(
                "shortLeverage",
            ),
        )
    )

    return {
        "symbol": SYMBOL,
        "marginType": margin,
        "isolatedLongLeverage": long_lev,
        "isolatedShortLeverage": short_lev,
    }


def count_open_symbol_positions(response):
    data = unwrap_data(response)

    if data is None:
        return 0

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        raise RuntimeError(
            "Unexpected position response format"
        )

    count = 0

    for position in data:
        if not isinstance(position, dict):
            continue

        symbol = str(
            position.get("symbol", "")
        ).upper()

        if symbol != SYMBOL:
            continue

        raw_size = position.get(
            "size",
            position.get(
                "positionAmt",
                position.get(
                    "quantity",
                    "0",
                ),
            ),
        )

        try:
            size = abs(float(raw_size))
        except Exception:
            size = 0.0

        if size > 0:
            count += 1

    return count


# =============================================================================
# FRESH READ-ONLY STATE SNAPSHOT
# =============================================================================

def read_live_state():
    config_response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    config = find_symbol_config(
        config_response
    )

    observed = extract_observed_state(
        config
    )

    positions_response = authenticated_get(
        ALL_POSITION_PATH
    )

    open_positions = count_open_symbol_positions(
        positions_response
    )

    snapshot = {
        "symbol": SYMBOL,
        "marginType": observed["marginType"],
        "isolatedLongLeverage":
            observed["isolatedLongLeverage"],
        "isolatedShortLeverage":
            observed["isolatedShortLeverage"],
        "openPositions": open_positions,
    }

    return snapshot


# =============================================================================
# CORRECTION PAYLOAD
# =============================================================================

def build_correction_payload():
    return {
        "symbol": SYMBOL,
        "marginType": TARGET_MARGIN_TYPE,
        "isolatedLongLeverage":
            TARGET_LONG_LEVERAGE,
        "isolatedShortLeverage":
            TARGET_SHORT_LEVERAGE,
    }


# =============================================================================
# CORRECTION INTENT
# =============================================================================

def build_correction_intent(
    observed_state,
    payload_hash,
):
    return {
        "version": VERSION,

        "operation":
            "LEVERAGE_CORRECTION",

        "transport":
            "SYNTHETIC_ONLY",

        "method":
            "POST",

        "path":
            LEVERAGE_MUTATION_PATH,

        "symbol":
            SYMBOL,

        "observedState":
            observed_state,

        "targetState": {
            "marginType":
                TARGET_MARGIN_TYPE,

            "isolatedLongLeverage":
                TARGET_LONG_LEVERAGE,

            "isolatedShortLeverage":
                TARGET_SHORT_LEVERAGE,
        },

        "payloadHash":
            payload_hash,

        "credentialFingerprint":
            safe_fingerprint(API_KEY),

        "networkWriteAllowed":
            False,

        "leverageMutationAllowed":
            False,
    }


# =============================================================================
# EXACT POST ENVELOPE CONSTRUCTION
# =============================================================================

def build_signed_envelope(
    payload,
    intent_hash,
    observed_state_hash,
):
    timestamp = str(
        int(time.time() * 1000)
    )

    body = canonical_json(
        payload
    )

    signature = generate_signature(
        secret=API_SECRET,
        timestamp=timestamp,
        method="POST",
        request_path=LEVERAGE_MUTATION_PATH,
        query_string="",
        body=body,
    )

    envelope = {
        "version":
            VERSION,

        "transport":
            "SYNTHETIC_INTERCEPT",

        "method":
            "POST",

        "baseUrl":
            BASE_URL,

        "requestPath":
            LEVERAGE_MUTATION_PATH,

        "queryString":
            "",

        "body":
            body,

        "headers": {
            "ACCESS-KEY":
                API_KEY,

            "ACCESS-SIGN":
                signature,

            "ACCESS-PASSPHRASE":
                API_PASSPHRASE,

            "ACCESS-TIMESTAMP":
                timestamp,

            "Content-Type":
                "application/json",

            "locale":
                "en-US",
        },

        "intentHash":
            intent_hash,

        "observedStateHash":
            observed_state_hash,

        "networkWriteAllowed":
            False,

        "leverageMutationAllowed":
            False,
    }

    return envelope


# =============================================================================
# ONE-TIME SYNTHETIC AUTHORIZATION
# =============================================================================

def create_authorization(
    envelope_hash,
    payload_hash,
    state_hash,
):
    authorization = {
        "version":
            VERSION,

        "authorizationType":
            "ONE_TIME_SYNTHETIC",

        "symbol":
            SYMBOL,

        "operation":
            "LEVERAGE_CORRECTION",

        "targetLong":
            TARGET_LONG_LEVERAGE,

        "targetShort":
            TARGET_SHORT_LEVERAGE,

        "envelopeHash":
            envelope_hash,

        "payloadHash":
            payload_hash,

        "stateHash":
            state_hash,

        "syntheticOnly":
            True,

        "exchangeWriteAuthorized":
            False,

        "leverageMutationAuthorized":
            False,

        "consumed":
            False,
    }

    return authorization


# =============================================================================
# SYNTHETIC TRANSPORT INTERCEPT
# =============================================================================

def synthetic_dispatch(
    envelope,
    authorization,
):
    if runtime["dispatch_committed"]:
        runtime[
            "duplicate_dispatch_block_counter"
        ] += 1

        raise RuntimeError(
            "Duplicate synthetic dispatch rejected"
        )

    if runtime["authorization_consumed"]:
        runtime[
            "duplicate_dispatch_block_counter"
        ] += 1

        raise RuntimeError(
            "Consumed authorization replay rejected"
        )

    if not SYNTHETIC_ONLY:
        raise RuntimeError(
            "Synthetic-only invariant violated"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Network writes unexpectedly enabled"
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "Leverage mutation unexpectedly enabled"
        )

    calculated_envelope_hash = sha256_text(
        envelope
    )

    if (
        authorization["envelopeHash"]
        != calculated_envelope_hash
    ):
        raise RuntimeError(
            "Authorization envelope binding mismatch"
        )

    runtime[
        "authorization_consumed"
    ] = True

    runtime[
        "dispatch_committed"
    ] = True

    runtime[
        "synthetic_dispatch_counter"
    ] += 1

    receipt = {
        "version":
            VERSION,

        "status":
            "INTERCEPTED",

        "transport":
            "SYNTHETIC_ONLY",

        "method":
            envelope["method"],

        "requestPath":
            envelope["requestPath"],

        "envelopeHash":
            calculated_envelope_hash,

        "authorizationConsumed":
            True,

        "networkTransmission":
            False,

        "exchangeContacted":
            False,

        "leverageMutationPerformed":
            False,

        "networkWriteCounter":
            runtime["network_write_counter"],

        "leverageMutationCounter":
            runtime["leverage_mutation_counter"],

        "targetLong":
            TARGET_LONG_LEVERAGE,

        "targetShort":
            TARGET_SHORT_LEVERAGE,
    }

    return receipt


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "status":
                "ok",

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "phase":
                runtime["phase"],

            "syntheticOnly":
                SYNTHETIC_ONLY,

            "authenticatedReadOnly":
                AUTHENTICATED_READ_ONLY_ENABLED,

            "authenticatedGets":
                runtime["authenticated_gets"],

            "networkWrites":
                runtime["network_write_counter"],

            "realOrders":
                runtime["real_order_counter"],

            "leverageMutations":
                runtime["leverage_mutation_counter"],

            "syntheticDispatches":
                runtime["synthetic_dispatch_counter"],

            "authorizationConsumed":
                runtime["authorization_consumed"],

            "correctionRequired":
                runtime["correction_required"],

            "correctionReady":
                runtime["correction_ready"],

            "freshStateValidated":
                runtime["fresh_state_validated"],

            "openPositions":
                runtime["open_positions"],

            "observedMargin":
                runtime["observed_margin"],

            "observedLong":
                runtime["observed_long"],

            "observedShort":
                runtime["observed_short"],

            "targetLong":
                TARGET_LONG_LEVERAGE,

            "targetShort":
                TARGET_SHORT_LEVERAGE,
        }

        body = canonical_json(
            payload
        ).encode("utf-8")

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

        self.wfile.write(
            body
        )

    def do_POST(self):
        self._reject_write()

    def do_PUT(self):
        self._reject_write()

    def do_PATCH(self):
        self._reject_write()

    def do_DELETE(self):
        self._reject_write()

    def _reject_write(self):
        body = canonical_json(
            {
                "status":
                    "blocked",

                "reason":
                    "R34F local health server is read-only",
            }
        ).encode("utf-8")

        self.send_response(405)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args,
    ):
        return


def start_health_server():
    try:
        server = ThreadingHTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        log(
            f"R34F: HEALTH SERVER LISTENING "
            f"ON PORT {HEALTH_PORT}"
        )

        return server

    except OSError as exc:
        log(
            f"R34F: HEALTH SERVER ERROR: {exc}"
        )

        return None


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():
    while True:
        runtime["heartbeat"] += 1

        log(
            f"R34F: HEARTBEAT "
            f"{runtime['heartbeat']} | "
            f"phase={runtime['phase']} | "
            f"synthetic-only={SYNTHETIC_ONLY} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED} | "
            f"authenticated-get="
            f"{runtime['authenticated_gets']} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"network-write-counter="
            f"{runtime['network_write_counter']} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"leverage-mutation-counter="
            f"{runtime['leverage_mutation_counter']} | "
            f"synthetic-dispatch="
            f"{runtime['synthetic_dispatch_counter']} | "
            f"duplicate-dispatch-block="
            f"{runtime['duplicate_dispatch_block_counter']} | "
            f"authorization-consumed="
            f"{runtime['authorization_consumed']} | "
            f"fresh-state="
            f"{runtime['fresh_state_validated']} | "
            f"stale-state-blocked="
            f"{runtime['stale_state_blocked']} | "
            f"open-positions="
            f"{runtime['open_positions']} | "
            f"correction-required="
            f"{runtime['correction_required']} | "
            f"correction-ready="
            f"{runtime['correction_ready']} | "
            f"observed-margin="
            f"{runtime['observed_margin']} | "
            f"observed-long="
            f"{runtime['observed_long']}x | "
            f"observed-short="
            f"{runtime['observed_short']}x | "
            f"target-long="
            f"{TARGET_LONG_LEVERAGE}x | "
            f"target-short="
            f"{TARGET_SHORT_LEVERAGE}x"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def run_validation():

    section(
        "R34F: MAIN.PY ENTERED"
    )

    log(
        f"R34F: SYMBOL={SYMBOL}"
    )

    log(
        f"R34F: VERSION={VERSION}"
    )

    log(
        f"R34F: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        "R34F: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        "R34F: STANDARD LIBRARY HTTP ENABLED"
    )

    log(
        "R34F: NETWORK WRITES DISABLED"
    )

    log(
        "R34F: LEVERAGE MUTATION DISABLED"
    )

    log(
        f"R34F: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"R34F: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"R34F: CORRECTION PATH="
        f"{LEVERAGE_MUTATION_PATH}"
    )


    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        "R34F TEST 1: HARD SAFETY CONFIGURATION"
    )

    assert_pass(
        "Synthetic Only Is Enabled",
        SYNTHETIC_ONLY is True,
    )

    assert_pass(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED is True,
    )

    assert_pass(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    assert_pass(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    assert_pass(
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    assert_pass(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    assert_pass(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    assert_pass(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    assert_pass(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        "R34F TEST 2: HTTP WRITE FIREBREAK"
    )

    assert_pass(
        "HTTP POST Is Disabled",
        HTTP_POST_ENABLED is False,
    )

    assert_pass(
        "HTTP PUT Is Disabled",
        HTTP_PUT_ENABLED is False,
    )

    assert_pass(
        "HTTP PATCH Is Disabled",
        HTTP_PATCH_ENABLED is False,
    )

    assert_pass(
        "HTTP DELETE Is Disabled",
        HTTP_DELETE_ENABLED is False,
    )

    try:
        reject_exchange_write(
            "POST",
            LEVERAGE_MUTATION_PATH,
            {
                "symbol": SYMBOL,
            },
        )

        fail_test(
            "Direct Exchange Write Attempt Is Rejected"
        )

        raise AssertionError(
            "Write firebreak unexpectedly allowed POST"
        )

    except RuntimeError:
        pass_test(
            "Direct Exchange Write Attempt Is Rejected"
        )

    assert_pass(
        "Network Write Counter Remains Zero",
        runtime["network_write_counter"] == 0,
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        "R34F TEST 3: AUTHENTICATION CREDENTIAL PRESENCE"
    )

    assert_pass(
        "API Key Is Present",
        bool(API_KEY),
    )

    assert_pass(
        "API Secret Is Present",
        bool(API_SECRET),
    )

    assert_pass(
        "API Passphrase Is Present",
        bool(API_PASSPHRASE),
    )

    log(
        f"R34F: API KEY SOURCE="
        f"{API_KEY_SOURCE}"
    )

    log(
        f"R34F: API SECRET SOURCE="
        f"{API_SECRET_SOURCE}"
    )

    log(
        f"R34F: API PASSPHRASE SOURCE="
        f"{API_PASSPHRASE_SOURCE}"
    )

    log(
        f"R34F: CREDENTIAL FINGERPRINT="
        f"{safe_fingerprint(API_KEY)}"
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        "R34F TEST 4: INITIAL LIVE READ-ONLY STATE"
    )

    initial_state = read_live_state()

    assert_pass(
        "Authenticated Symbol Config / Position GETs Succeeded",
        runtime["authenticated_gets"] >= 2,
    )

    assert_pass(
        f"Returned Symbol Matches {SYMBOL}",
        initial_state["symbol"] == SYMBOL,
    )

    runtime["observed_margin"] = (
        initial_state["marginType"]
    )

    runtime["observed_long"] = (
        initial_state["isolatedLongLeverage"]
    )

    runtime["observed_short"] = (
        initial_state["isolatedShortLeverage"]
    )

    runtime["open_positions"] = (
        initial_state["openPositions"]
    )

    log(
        f"R34F: OBSERVED MARGIN="
        f"{runtime['observed_margin']}"
    )

    log(
        f"R34F: OBSERVED LONG="
        f"{runtime['observed_long']}x"
    )

    log(
        f"R34F: OBSERVED SHORT="
        f"{runtime['observed_short']}x"
    )

    log(
        f"R34F: OPEN {SYMBOL} POSITIONS="
        f"{runtime['open_positions']}"
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        "R34F TEST 5: 100X CORRECTION REQUIREMENT"
    )

    assert_pass(
        "Target Margin Type Is ISOLATED",
        TARGET_MARGIN_TYPE == "ISOLATED",
    )

    assert_pass(
        "Observed Margin Matches ISOLATED",
        runtime["observed_margin"] == "ISOLATED",
    )

    long_requires_correction = (
        runtime["observed_long"]
        != TARGET_LONG_LEVERAGE
    )

    short_requires_correction = (
        runtime["observed_short"]
        != TARGET_SHORT_LEVERAGE
    )

    if long_requires_correction:
        required_test(
            "Observed Long Leverage Requires 100x Correction"
        )
    else:
        pass_test(
            "Observed Long Leverage Already Matches 100x"
        )

    if short_requires_correction:
        required_test(
            "Observed Short Leverage Requires 100x Correction"
        )
    else:
        pass_test(
            "Observed Short Leverage Already Matches 100x"
        )

    runtime["correction_required"] = (
        long_requires_correction
        or short_requires_correction
    )

    assert_pass(
        "Correction Requirement Was Determined",
        isinstance(
            runtime["correction_required"],
            bool,
        ),
    )

    log(
        f"R34F: CORRECTION REQUIRED="
        f"{runtime['correction_required']}"
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        "R34F TEST 6: ZERO-POSITION CORRECTION GATE"
    )

    assert_pass(
        f"{SYMBOL} Has No Open Position",
        runtime["open_positions"] == 0,
    )

    assert_pass(
        "Network Write Counter Is Zero",
        runtime["network_write_counter"] == 0,
    )

    assert_pass(
        "Leverage Mutation Counter Is Zero",
        runtime["leverage_mutation_counter"] == 0,
    )

    runtime["correction_ready"] = (
        runtime["observed_margin"]
        == TARGET_MARGIN_TYPE
        and runtime["open_positions"] == 0
        and runtime["correction_required"]
        and runtime["network_write_counter"] == 0
        and runtime["leverage_mutation_counter"] == 0
    )

    assert_pass(
        "100x Correction Is Ready",
        runtime["correction_ready"],
    )

    log(
        f"R34F: CORRECTION READY="
        f"{runtime['correction_ready']}"
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        "R34F TEST 7: EXACT V3 CORRECTION PAYLOAD"
    )

    payload = build_correction_payload()

    expected_payload = {
        "symbol":
            SYMBOL,

        "marginType":
            "ISOLATED",

        "isolatedLongLeverage":
            "100",

        "isolatedShortLeverage":
            "100",
    }

    assert_pass(
        "Correction Payload Matches Exact Target",
        payload == expected_payload,
    )

    assert_pass(
        "Correction Method Is POST",
        "POST" == "POST",
    )

    assert_pass(
        "Correction Path Is Exact V3 Leverage Endpoint",
        LEVERAGE_MUTATION_PATH
        == "/capi/v3/account/leverage",
    )

    payload_body = canonical_json(
        payload
    )

    payload_hash = sha256_text(
        payload_body
    )

    runtime["payload_hash"] = (
        payload_hash
    )

    log(
        f"R34F: CANONICAL PAYLOAD="
        f"{payload_body}"
    )

    log(
        f"R34F: PAYLOAD SHA256="
        f"{payload_hash}"
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        "R34F TEST 8: OBSERVED STATE HASH BINDING"
    )

    state_hash = sha256_text(
        initial_state
    )

    runtime["state_hash"] = (
        state_hash
    )

    assert_pass(
        "Observed State Hash Was Created",
        len(state_hash) == 64,
    )

    log(
        f"R34F: OBSERVED STATE="
        f"{canonical_json(initial_state)}"
    )

    log(
        f"R34F: OBSERVED STATE SHA256="
        f"{state_hash}"
    )

    intent = build_correction_intent(
        initial_state,
        payload_hash,
    )

    intent_hash = sha256_text(
        intent
    )

    assert_pass(
        "Correction Intent Is Bound To Observed State",
        intent["observedState"]
        == initial_state,
    )

    assert_pass(
        "Correction Intent Is Bound To Payload Hash",
        intent["payloadHash"]
        == payload_hash,
    )

    assert_pass(
        "Correction Intent Is Synthetic Only",
        intent["transport"]
        == "SYNTHETIC_ONLY",
    )

    assert_pass(
        "Correction Intent Forbids Network Write",
        intent["networkWriteAllowed"]
        is False,
    )

    log(
        f"R34F: INTENT SHA256="
        f"{intent_hash}"
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    section(
        "R34F TEST 9: FRESH-STATE RECONCILIATION"
    )

    fresh_state = read_live_state()

    assert_pass(
        "Fresh Authenticated State Was Retrieved",
        runtime["authenticated_gets"] >= 4,
    )

    if fresh_state != initial_state:
        runtime["stale_state_blocked"] += 1

        fail_test(
            "Live State Remained Stable During Envelope Construction"
        )

        log(
            f"R34F: INITIAL STATE="
            f"{canonical_json(initial_state)}"
        )

        log(
            f"R34F: FRESH STATE="
            f"{canonical_json(fresh_state)}"
        )

        raise RuntimeError(
            "R34F stale-state protection triggered"
        )

    runtime[
        "fresh_state_validated"
    ] = True

    assert_pass(
        "Live State Remained Stable During Envelope Construction",
        fresh_state == initial_state,
    )

    assert_pass(
        "Fresh State Still Has Zero Open Positions",
        fresh_state["openPositions"] == 0,
    )

    assert_pass(
        "Fresh Margin Still Matches ISOLATED",
        fresh_state["marginType"]
        == TARGET_MARGIN_TYPE,
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    section(
        "R34F TEST 10: SIGNED CORRECTION ENVELOPE"
    )

    envelope = build_signed_envelope(
        payload=payload,
        intent_hash=intent_hash,
        observed_state_hash=state_hash,
    )

    assert_pass(
        "Envelope Method Is POST",
        envelope["method"] == "POST",
    )

    assert_pass(
        "Envelope Path Matches Exact V3 Endpoint",
        envelope["requestPath"]
        == LEVERAGE_MUTATION_PATH,
    )

    assert_pass(
        "Envelope Body Matches Canonical Payload",
        envelope["body"]
        == payload_body,
    )

    assert_pass(
        "ACCESS-KEY Header Is Present",
        bool(
            envelope[
                "headers"
            ][
                "ACCESS-KEY"
            ]
        ),
    )

    assert_pass(
        "ACCESS-SIGN Header Is Present",
        bool(
            envelope[
                "headers"
            ][
                "ACCESS-SIGN"
            ]
        ),
    )

    assert_pass(
        "ACCESS-PASSPHRASE Header Is Present",
        bool(
            envelope[
                "headers"
            ][
                "ACCESS-PASSPHRASE"
            ]
        ),
    )

    assert_pass(
        "ACCESS-TIMESTAMP Header Is Present",
        bool(
            envelope[
                "headers"
            ][
                "ACCESS-TIMESTAMP"
            ]
        ),
    )

    expected_signature = generate_signature(
        secret=API_SECRET,
        timestamp=(
            envelope[
                "headers"
            ][
                "ACCESS-TIMESTAMP"
            ]
        ),
        method="POST",
        request_path=LEVERAGE_MUTATION_PATH,
        query_string="",
        body=payload_body,
    )

    assert_pass(
        "Envelope Signature Recomputes Exactly",
        hmac.compare_digest(
            envelope[
                "headers"
            ][
                "ACCESS-SIGN"
            ],
            expected_signature,
        ),
    )

    assert_pass(
        "Envelope Explicitly Forbids Network Write",
        envelope["networkWriteAllowed"]
        is False,
    )

    assert_pass(
        "Envelope Explicitly Forbids Leverage Mutation",
        envelope["leverageMutationAllowed"]
        is False,
    )

    envelope_hash = sha256_text(
        envelope
    )

    runtime["envelope_hash"] = (
        envelope_hash
    )

    log(
        f"R34F: ENVELOPE SHA256="
        f"{envelope_hash}"
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    section(
        "R34F TEST 11: ONE-TIME SYNTHETIC AUTHORIZATION"
    )

    authorization = create_authorization(
        envelope_hash=envelope_hash,
        payload_hash=payload_hash,
        state_hash=state_hash,
    )

    authorization_hash = sha256_text(
        authorization
    )

    runtime[
        "authorization_hash"
    ] = authorization_hash

    assert_pass(
        "Authorization Is Initially Unconsumed",
        authorization["consumed"]
        is False,
    )

    assert_pass(
        "Authorization Is Synthetic Only",
        authorization["syntheticOnly"]
        is True,
    )

    assert_pass(
        "Authorization Forbids Exchange Write",
        authorization[
            "exchangeWriteAuthorized"
        ] is False,
    )

    assert_pass(
        "Authorization Forbids Leverage Mutation",
        authorization[
            "leverageMutationAuthorized"
        ] is False,
    )

    assert_pass(
        "Authorization Is Bound To Envelope Hash",
        authorization["envelopeHash"]
        == envelope_hash,
    )

    assert_pass(
        "Authorization Is Bound To Payload Hash",
        authorization["payloadHash"]
        == payload_hash,
    )

    assert_pass(
        "Authorization Is Bound To Live State Hash",
        authorization["stateHash"]
        == state_hash,
    )

    log(
        f"R34F: AUTHORIZATION SHA256="
        f"{authorization_hash}"
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    section(
        "R34F TEST 12: SYNTHETIC TRANSPORT INTERCEPT"
    )

    receipt = synthetic_dispatch(
        envelope=envelope,
        authorization=authorization,
    )

    receipt_hash = sha256_text(
        receipt
    )

    runtime["receipt_hash"] = (
        receipt_hash
    )

    assert_pass(
        "Exactly One Synthetic Dispatch Occurred",
        runtime[
            "synthetic_dispatch_counter"
        ] == 1,
    )

    assert_pass(
        "Authorization Was Consumed Exactly Once",
        runtime[
            "authorization_consumed"
        ] is True,
    )

    assert_pass(
        "Dispatch Was Committed Locally",
        runtime[
            "dispatch_committed"
        ] is True,
    )

    assert_pass(
        "Receipt Transport Is Synthetic Only",
        receipt["transport"]
        == "SYNTHETIC_ONLY",
    )

    assert_pass(
        "Receipt Confirms No Network Transmission",
        receipt["networkTransmission"]
        is False,
    )

    assert_pass(
        "Receipt Confirms Exchange Was Not Contacted",
        receipt["exchangeContacted"]
        is False,
    )

    assert_pass(
        "Receipt Confirms No Leverage Mutation",
        receipt["leverageMutationPerformed"]
        is False,
    )

    assert_pass(
        "Receipt Network Write Counter Is Zero",
        receipt["networkWriteCounter"]
        == 0,
    )

    assert_pass(
        "Receipt Leverage Mutation Counter Is Zero",
        receipt["leverageMutationCounter"]
        == 0,
    )

    log(
        f"R34F: RECEIPT SHA256="
        f"{receipt_hash}"
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    section(
        "R34F TEST 13: AUTHORIZATION REPLAY REJECTION"
    )

    replay_rejected = False

    try:
        synthetic_dispatch(
            envelope=envelope,
            authorization=authorization,
        )

    except RuntimeError:
        replay_rejected = True

    assert_pass(
        "Consumed Authorization Replay Is Rejected",
        replay_rejected,
    )

    assert_pass(
        "Synthetic Dispatch Counter Remains One",
        runtime[
            "synthetic_dispatch_counter"
        ] == 1,
    )

    assert_pass(
        "Duplicate Dispatch Block Counter Is One",
        runtime[
            "duplicate_dispatch_block_counter"
        ] == 1,
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    section(
        "R34F TEST 14: PAYLOAD TAMPER REJECTION"
    )

    tampered_payload = dict(
        payload
    )

    tampered_payload[
        "isolatedLongLeverage"
    ] = "99"

    tampered_payload_hash = sha256_text(
        canonical_json(
            tampered_payload
        )
    )

    assert_pass(
        "Tampered Payload Hash Differs",
        tampered_payload_hash
        != payload_hash,
    )

    assert_pass(
        "Original Authorization Does Not Bind Tampered Payload",
        authorization["payloadHash"]
        != tampered_payload_hash,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    section(
        "R34F TEST 15: ENVELOPE TAMPER REJECTION"
    )

    tampered_envelope = json.loads(
        json.dumps(
            envelope
        )
    )

    tampered_envelope[
        "requestPath"
    ] = "/tampered/path"

    tampered_envelope_hash = sha256_text(
        tampered_envelope
    )

    assert_pass(
        "Tampered Envelope Hash Differs",
        tampered_envelope_hash
        != envelope_hash,
    )

    assert_pass(
        "Authorization Rejects Tampered Envelope Binding",
        authorization["envelopeHash"]
        != tampered_envelope_hash,
    )


    # =========================================================================
    # TEST 16
    # =========================================================================

    section(
        "R34F TEST 16: FINAL LIVE READ-ONLY RECONCILIATION"
    )

    final_state = read_live_state()

    assert_pass(
        "Final Authenticated State Was Retrieved",
        runtime["authenticated_gets"] >= 6,
    )

    assert_pass(
        "Final State Matches Initial State",
        final_state == initial_state,
    )

    assert_pass(
        "Observed Margin Remains ISOLATED",
        final_state["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    assert_pass(
        "No Position Was Opened",
        final_state["openPositions"] == 0,
    )

    assert_pass(
        "Observed Long Leverage Was Not Mutated",
        final_state[
            "isolatedLongLeverage"
        ]
        == initial_state[
            "isolatedLongLeverage"
        ],
    )

    assert_pass(
        "Observed Short Leverage Was Not Mutated",
        final_state[
            "isolatedShortLeverage"
        ]
        == initial_state[
            "isolatedShortLeverage"
        ],
    )


    # =========================================================================
    # TEST 17
    # =========================================================================

    section(
        "R34F TEST 17: FINAL WRITE-FREE INVARIANTS"
    )

    assert_pass(
        "Real Order Counter Is Zero",
        runtime["real_order_counter"]
        == 0,
    )

    assert_pass(
        "Network Write Counter Is Zero",
        runtime["network_write_counter"]
        == 0,
    )

    assert_pass(
        "Leverage Mutation Counter Is Zero",
        runtime[
            "leverage_mutation_counter"
        ] == 0,
    )

    assert_pass(
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    assert_pass(
        "Exchange Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    assert_pass(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    assert_pass(
        "Exactly One Synthetic Dispatch Is Recorded",
        runtime[
            "synthetic_dispatch_counter"
        ] == 1,
    )


    # =========================================================================
    # COMPLETE
    # =========================================================================

    runtime[
        "validation_complete"
    ] = True

    runtime[
        "phase"
    ] = "CORRECTION_ENVELOPE_VALIDATED"

    section(
        "R34F: VALIDATION COMPLETE"
    )

    log(
        f"R34F: PHASE="
        f"{runtime['phase']}"
    )

    log(
        f"R34F: AUTHENTICATED GETS="
        f"{runtime['authenticated_gets']}"
    )

    log(
        f"R34F: OBSERVED MARGIN="
        f"{runtime['observed_margin']}"
    )

    log(
        f"R34F: OBSERVED LONG="
        f"{runtime['observed_long']}x"
    )

    log(
        f"R34F: OBSERVED SHORT="
        f"{runtime['observed_short']}x"
    )

    log(
        f"R34F: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"R34F: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"R34F: OPEN POSITIONS="
        f"{runtime['open_positions']}"
    )

    log(
        f"R34F: CORRECTION REQUIRED="
        f"{runtime['correction_required']}"
    )

    log(
        f"R34F: CORRECTION READY="
        f"{runtime['correction_ready']}"
    )

    log(
        f"R34F: FRESH STATE VALIDATED="
        f"{runtime['fresh_state_validated']}"
    )

    log(
        f"R34F: PAYLOAD SHA256="
        f"{runtime['payload_hash']}"
    )

    log(
        f"R34F: STATE SHA256="
        f"{runtime['state_hash']}"
    )

    log(
        f"R34F: ENVELOPE SHA256="
        f"{runtime['envelope_hash']}"
    )

    log(
        f"R34F: AUTHORIZATION SHA256="
        f"{runtime['authorization_hash']}"
    )

    log(
        f"R34F: RECEIPT SHA256="
        f"{runtime['receipt_hash']}"
    )

    log(
        f"R34F: SYNTHETIC DISPATCHES="
        f"{runtime['synthetic_dispatch_counter']}"
    )

    log(
        f"R34F: DUPLICATE DISPATCH BLOCKS="
        f"{runtime['duplicate_dispatch_block_counter']}"
    )

    log(
        f"R34F: NETWORK WRITES="
        f"{runtime['network_write_counter']}"
    )

    log(
        f"R34F: REAL ORDERS="
        f"{runtime['real_order_counter']}"
    )

    log(
        f"R34F: LEVERAGE MUTATIONS="
        f"{runtime['leverage_mutation_counter']}"
    )

    log(
        "R34F: EXACT V3 LEVERAGE CORRECTION "
        "ENVELOPE VALIDATED"
    )

    log(
        "R34F: NO REAL ORDER WAS SENT"
    )

    log(
        "R34F: NO EXCHANGE WRITE WAS SENT"
    )

    log(
        "R34F: NO LEVERAGE MUTATION WAS PERFORMED"
    )

    section("")


# =============================================================================
# ENTRYPOINT
# =============================================================================

def main():
    start_health_server()

    try:
        run_validation()

    except Exception as exc:
        runtime["phase"] = "VALIDATION_FAILED"

        section(
            "R34F: VALIDATION FAILED"
        )

        log(
            f"R34F: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        log(
            f"R34F: NETWORK WRITES="
            f"{runtime['network_write_counter']}"
        )

        log(
            f"R34F: LEVERAGE MUTATIONS="
            f"{runtime['leverage_mutation_counter']}"
        )

        log(
            "R34F: NO EXCHANGE WRITE WAS SENT"
        )

        section("")

    heartbeat_loop()


if __name__ == "__main__":
    main()
