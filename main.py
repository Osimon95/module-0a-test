# =============================================================================
# R34C - LIVE OBSERVATION -> CORRECTION INTENT BINDING
#
# PURPOSE
# -------
# 1. Perform ONE authenticated READ-ONLY live symbolConfig GET.
# 2. Observe the actual live leverage configuration.
# 3. Detect whether correction to 100x / 100x is required.
# 4. Construct an exact leverage-correction intent.
# 5. Bind the intent cryptographically to the live observation.
# 6. Construct the exact future POST payload synthetically.
# 7. Perform ONE SYNTHETIC dispatch only.
# 8. NEVER execute an HTTP POST.
# 9. NEVER mutate leverage.
# 10. NEVER place an order.
#
# R34C remains NON-MUTATING.
# =============================================================================

import os
import time
import json
import hmac
import hashlib
import base64
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    requests = None


# =============================================================================
# PART 1 OF 4
# CONSTANTS / HARD SAFETY LOCKS
# =============================================================================

VERSION = "R34C"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

BASE_URL = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

# IMPORTANT:
# This path exists only as DATA for synthetic validation.
# R34C will NEVER send an HTTP request to this path.
LEVERAGE_MUTATION_PATH = "/capi/v3/account/leverage"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

HEARTBEAT_SECONDS = 30


# -----------------------------------------------------------------------------
# HARD SAFETY CONSTANTS
# -----------------------------------------------------------------------------

SYNTHETIC_ONLY = True

AUTHENTICATED_READ_ONLY_ENABLED = True

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


# -----------------------------------------------------------------------------
# RUNTIME COUNTERS
# -----------------------------------------------------------------------------

authenticated_get_counter = 0
synthetic_dispatch_counter = 0
real_order_counter = 0
network_write_counter = 0
leverage_mutation_counter = 0

intent_creation_counter = 0
intent_binding_counter = 0
duplicate_dispatch_block_counter = 0


# -----------------------------------------------------------------------------
# RUNTIME STATE
# -----------------------------------------------------------------------------

runtime_state = {
    "phase": "BOOTING",

    "observed_margin_type": "UNKNOWN",
    "observed_long_leverage": None,
    "observed_short_leverage": None,

    "correction_required": None,

    "observation_hash": None,
    "intent_hash": None,
    "payload_hash": None,
    "envelope_hash": None,
    "receipt_hash": None,

    "synthetic_dispatch_committed": False,
}


# =============================================================================
# OUTPUT HELPERS
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
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{label:<82} {status}", flush=True)

    if not condition:
        raise RuntimeError(f"R34C validation failed: {label}")


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_object(value):
    return sha256_text(canonical_json(value))


def normalize_int(value):
    if value is None:
        return None

    try:
        return int(float(str(value)))
    except Exception:
        return None


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path in ("/", "/health", "/healthz"):

            payload = {
                "status": "ok",
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": runtime_state["phase"],
                "synthetic_only": SYNTHETIC_ONLY,
                "real_execution": REAL_ORDER_EXECUTION_ENABLED,
                "network_writes": EXCHANGE_NETWORK_WRITES_ENABLED,
                "leverage_mutation": LEVERAGE_MUTATION_ENABLED,
            }

            body = json.dumps(payload).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()

            self.wfile.write(body)

        else:

            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():

    def runner():
        try:
            server = HTTPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            )

            print(
                f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"{VERSION}: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()


# =============================================================================
# PART 2 OF 4
# AUTHENTICATED READ-ONLY TRANSPORT
# =============================================================================

def get_credentials():

    api_key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
        or ""
    ).strip()

    secret_key = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("WEEX_SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or ""
    ).strip()

    passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("WEEX_PASSPHRASE")
        or os.getenv("PASSPHRASE")
        or ""
    ).strip()

    return api_key, secret_key, passphrase


def generate_signature(
    secret_key,
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):

    method = method.upper()

    if query_string:
        message = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )
    else:
        message = (
            timestamp
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


def authenticated_get_symbol_config():

    global authenticated_get_counter

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only transport is disabled."
        )

    if requests is None:
        raise RuntimeError(
            "Python package 'requests' is unavailable."
        )

    api_key, secret_key, passphrase = get_credentials()

    if not api_key:
        raise RuntimeError("WEEX API key is missing.")

    if not secret_key:
        raise RuntimeError("WEEX API secret is missing.")

    if not passphrase:
        raise RuntimeError("WEEX API passphrase is missing.")

    query_string = urlencode(
        {
            "symbol": SYMBOL,
        }
    )

    timestamp = str(int(time.time() * 1000))

    signature = generate_signature(
        secret_key=secret_key,
        timestamp=timestamp,
        method="GET",
        request_path=SYMBOL_CONFIG_PATH,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
        "locale": "en-US",
    }

    url = (
        BASE_URL
        + SYMBOL_CONFIG_PATH
        + "?"
        + query_string
    )

    response = requests.get(
        url,
        headers=headers,
        timeout=15,
    )

    authenticated_get_counter += 1

    if response.status_code != 200:
        raise RuntimeError(
            f"Authenticated GET failed: "
            f"HTTP {response.status_code} "
            f"{response.text[:500]}"
        )

    try:
        data = response.json()
    except Exception:
        raise RuntimeError(
            "Authenticated GET returned invalid JSON."
        )

    # WEEX normally returns a list.
    if isinstance(data, list):

        if not data:
            raise RuntimeError(
                "symbolConfig returned an empty list."
            )

        selected = None

        for item in data:
            if (
                isinstance(item, dict)
                and str(item.get("symbol", "")).upper() == SYMBOL
            ):
                selected = item
                break

        if selected is None:
            selected = data[0]

        data = selected

    # Defensive handling in case response is wrapped.
    elif isinstance(data, dict):

        if isinstance(data.get("data"), list):

            entries = data["data"]

            if not entries:
                raise RuntimeError(
                    "symbolConfig data list is empty."
                )

            selected = None

            for item in entries:
                if (
                    isinstance(item, dict)
                    and str(item.get("symbol", "")).upper() == SYMBOL
                ):
                    selected = item
                    break

            data = selected or entries[0]

        elif isinstance(data.get("data"), dict):
            data = data["data"]

    if not isinstance(data, dict):
        raise RuntimeError(
            "Unable to normalize symbolConfig response."
        )

    return data


# =============================================================================
# LIVE OBSERVATION
# =============================================================================

def build_live_observation(config):

    margin_type = str(
        config.get("marginType", "")
    ).strip().upper()

    long_leverage = normalize_int(
        config.get("isolatedLongLeverage")
    )

    short_leverage = normalize_int(
        config.get("isolatedShortLeverage")
    )

    observation = {
        "version": VERSION,
        "symbol": SYMBOL,
        "source": "WEEX_LIVE_AUTHENTICATED_READ_ONLY",
        "request_method": "GET",
        "request_path": SYMBOL_CONFIG_PATH,

        "marginType": margin_type,
        "isolatedLongLeverage": long_leverage,
        "isolatedShortLeverage": short_leverage,

        "network_write": False,
        "mutation": False,
    }

    return observation


# =============================================================================
# CORRECTION INTENT
# =============================================================================

def build_correction_intent(observation):

    global intent_creation_counter
    global intent_binding_counter

    correction_required = (
        observation["marginType"]
        != TARGET_MARGIN_TYPE

        or observation["isolatedLongLeverage"]
        != TARGET_LONG_LEVERAGE

        or observation["isolatedShortLeverage"]
        != TARGET_SHORT_LEVERAGE
    )

    observation_hash = sha256_object(observation)

    intent = {
        "version": VERSION,
        "intent_type": "LEVERAGE_CORRECTION",

        "symbol": SYMBOL,

        "observed": {
            "marginType":
                observation["marginType"],

            "isolatedLongLeverage":
                observation["isolatedLongLeverage"],

            "isolatedShortLeverage":
                observation["isolatedShortLeverage"],
        },

        "target": {
            "marginType":
                TARGET_MARGIN_TYPE,

            "isolatedLongLeverage":
                TARGET_LONG_LEVERAGE,

            "isolatedShortLeverage":
                TARGET_SHORT_LEVERAGE,
        },

        "correction_required":
            correction_required,

        "observation_hash":
            observation_hash,

        "authorization":
            "NOT_GRANTED",

        "transport_mode":
            "SYNTHETIC_ONLY",

        "network_transmission_permitted":
            False,

        "leverage_mutation_permitted":
            False,
    }

    intent_creation_counter += 1
    intent_binding_counter += 1

    return intent


# =============================================================================
# EXACT FUTURE PAYLOAD
# =============================================================================

def build_target_payload():

    return {
        "symbol": SYMBOL,
        "marginType": TARGET_MARGIN_TYPE,
        "isolatedLongLeverage":
            str(TARGET_LONG_LEVERAGE),
        "isolatedShortLeverage":
            str(TARGET_SHORT_LEVERAGE),
    }


# =============================================================================
# SYNTHETIC ENVELOPE
# =============================================================================

def build_synthetic_envelope(
    observation,
    intent,
    payload,
):

    return {
        "version": VERSION,

        "transport":
            "SYNTHETIC",

        "method":
            "POST",

        "path":
            LEVERAGE_MUTATION_PATH,

        "payload":
            payload,

        "observation_hash":
            sha256_object(observation),

        "intent_hash":
            sha256_object(intent),

        "payload_hash":
            sha256_object(payload),

        "authorization":
            "NOT_GRANTED",

        "network_write_enabled":
            False,

        "leverage_mutation_enabled":
            False,

        "exchange_contacted":
            False,
    }


# =============================================================================
# HARD WRITE FIREBREAK
# =============================================================================

def forbidden_network_write(*args, **kwargs):

    raise RuntimeError(
        f"{VERSION}: NETWORK WRITE FIREBREAK ACTIVATED. "
        "R34C does not permit POST/PUT/PATCH/DELETE."
    )


def forbidden_leverage_mutation(*args, **kwargs):

    raise RuntimeError(
        f"{VERSION}: LEVERAGE MUTATION FIREBREAK ACTIVATED."
    )


# =============================================================================
# SYNTHETIC DISPATCH
# =============================================================================

def synthetic_dispatch(envelope):

    global synthetic_dispatch_counter
    global duplicate_dispatch_block_counter

    if runtime_state["synthetic_dispatch_committed"]:
        duplicate_dispatch_block_counter += 1

        raise RuntimeError(
            "Duplicate synthetic dispatch rejected."
        )

    if envelope["transport"] != "SYNTHETIC":
        raise RuntimeError(
            "Non-synthetic envelope rejected."
        )

    if envelope["network_write_enabled"] is not False:
        raise RuntimeError(
            "Envelope attempts to enable network writes."
        )

    if envelope["leverage_mutation_enabled"] is not False:
        raise RuntimeError(
            "Envelope attempts leverage mutation."
        )

    if envelope["authorization"] != "NOT_GRANTED":
        raise RuntimeError(
            "Unexpected authorization state."
        )

    runtime_state["synthetic_dispatch_committed"] = True

    synthetic_dispatch_counter += 1

    receipt = {
        "version": VERSION,

        "transport":
            "SYNTHETIC",

        "dispatch":
            "INTERCEPTED",

        "method":
            envelope["method"],

        "path":
            envelope["path"],

        "envelope_hash":
            sha256_object(envelope),

        "network_transmission":
            False,

        "exchange_contacted":
            False,

        "leverage_mutated":
            False,

        "real_order_sent":
            False,

        "synthetic_dispatch_counter":
            synthetic_dispatch_counter,
    }

    return receipt


# =============================================================================
# PART 3 OF 4
# R34C VALIDATION SUITE
# =============================================================================

def run_validation():

    global real_order_counter
    global network_write_counter
    global leverage_mutation_counter

    banner(f"{VERSION}: MAIN.PY ENTERED")

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATION DISABLED",
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


    # =========================================================================
    section(
        "R34C TEST 1: STANDARD LIBRARY SAFETY CONFIGURATION"
    )
    # =========================================================================

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
    section(
        "R34C TEST 2: WRITE METHOD FIREBREAK"
    )
    # =========================================================================

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


    # =========================================================================
    section(
        "R34C TEST 3: AUTHENTICATED LIVE READ-ONLY OBSERVATION"
    )
    # =========================================================================

    config = authenticated_get_symbol_config()

    observation = build_live_observation(config)

    runtime_state["observed_margin_type"] = (
        observation["marginType"]
    )

    runtime_state["observed_long_leverage"] = (
        observation["isolatedLongLeverage"]
    )

    runtime_state["observed_short_leverage"] = (
        observation["isolatedShortLeverage"]
    )

    runtime_state["observation_hash"] = (
        sha256_object(observation)
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observation['marginType']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{observation['isolatedLongLeverage']}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{observation['isolatedShortLeverage']}x",
        flush=True,
    )

    check(
        "Exactly One Authenticated GET Was Performed",
        authenticated_get_counter == 1,
    )

    check(
        "Observed Symbol Is BTCUSDT",
        observation["symbol"] == SYMBOL,
    )

    check(
        "Observed Margin Type Is Present",
        bool(observation["marginType"]),
    )

    check(
        "Observed Long Leverage Is Present",
        observation["isolatedLongLeverage"] is not None,
    )

    check(
        "Observed Short Leverage Is Present",
        observation["isolatedShortLeverage"] is not None,
    )

    check(
        "Observation Confirms No Network Write",
        observation["network_write"] is False,
    )

    check(
        "Observation Confirms No Mutation",
        observation["mutation"] is False,
    )


    # =========================================================================
    section(
        "R34C TEST 4: LIVE OBSERVATION HASH BINDING"
    )
    # =========================================================================

    observation_hash_1 = sha256_object(observation)

    observation_hash_2 = sha256_object(
        json.loads(canonical_json(observation))
    )

    check(
        "Observation Hash Is Deterministic",
        observation_hash_1 == observation_hash_2,
    )

    check(
        "Observation Hash Is SHA256 Length",
        len(observation_hash_1) == 64,
    )


    # =========================================================================
    section(
        "R34C TEST 5: CORRECTION REQUIREMENT DETECTION"
    )
    # =========================================================================

    correction_required = (
        observation["marginType"]
        != TARGET_MARGIN_TYPE

        or observation["isolatedLongLeverage"]
        != TARGET_LONG_LEVERAGE

        or observation["isolatedShortLeverage"]
        != TARGET_SHORT_LEVERAGE
    )

    runtime_state["correction_required"] = (
        correction_required
    )

    check(
        "Target Margin Type Is ISOLATED",
        TARGET_MARGIN_TYPE == "ISOLATED",
    )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE == 100,
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE == 100,
    )

    if (
        observation["marginType"] == TARGET_MARGIN_TYPE
        and
        observation["isolatedLongLeverage"]
        == TARGET_LONG_LEVERAGE
        and
        observation["isolatedShortLeverage"]
        == TARGET_SHORT_LEVERAGE
    ):

        check(
            "Correction Correctly Identified As Not Required",
            correction_required is False,
        )

    else:

        check(
            "Correction Correctly Identified As Required",
            correction_required is True,
        )


    # =========================================================================
    section(
        "R34C TEST 6: CORRECTION INTENT CONSTRUCTION"
    )
    # =========================================================================

    intent = build_correction_intent(
        observation
    )

    runtime_state["intent_hash"] = (
        sha256_object(intent)
    )

    check(
        "Exactly One Correction Intent Was Created",
        intent_creation_counter == 1,
    )

    check(
        "Intent Symbol Matches Live Observation",
        intent["symbol"] == observation["symbol"],
    )

    check(
        "Intent Observed Margin Matches Live Observation",
        intent["observed"]["marginType"]
        == observation["marginType"],
    )

    check(
        "Intent Observed Long Leverage Matches Live Observation",
        intent["observed"]["isolatedLongLeverage"]
        == observation["isolatedLongLeverage"],
    )

    check(
        "Intent Observed Short Leverage Matches Live Observation",
        intent["observed"]["isolatedShortLeverage"]
        == observation["isolatedShortLeverage"],
    )

    check(
        "Intent Target Margin Is ISOLATED",
        intent["target"]["marginType"]
        == "ISOLATED",
    )

    check(
        "Intent Target Long Is 100x",
        intent["target"]["isolatedLongLeverage"]
        == 100,
    )

    check(
        "Intent Target Short Is 100x",
        intent["target"]["isolatedShortLeverage"]
        == 100,
    )

    check(
        "Intent Is Bound To Exact Observation Hash",
        intent["observation_hash"]
        == observation_hash_1,
    )

    check(
        "Intent Authorization Is Not Granted",
        intent["authorization"]
        == "NOT_GRANTED",
    )

    check(
        "Intent Prohibits Network Transmission",
        intent["network_transmission_permitted"]
        is False,
    )

    check(
        "Intent Prohibits Leverage Mutation",
        intent["leverage_mutation_permitted"]
        is False,
    )


    # =========================================================================
    section(
        "R34C TEST 7: EXACT 100x / 100x TARGET PAYLOAD"
    )
    # =========================================================================

    payload = build_target_payload()

    runtime_state["payload_hash"] = (
        sha256_object(payload)
    )

    print(
        f"{VERSION}: SYNTHETIC TARGET PAYLOAD="
        f"{canonical_json(payload)}",
        flush=True,
    )

    print(
        f"{VERSION}: PAYLOAD SHA256="
        f"{runtime_state['payload_hash']}",
        flush=True,
    )

    check(
        "Payload Symbol Is Exact",
        payload["symbol"] == SYMBOL,
    )

    check(
        "Payload Margin Type Is ISOLATED",
        payload["marginType"] == "ISOLATED",
    )

    check(
        "Payload Long Leverage Is Exactly 100",
        payload["isolatedLongLeverage"] == "100",
    )

    check(
        "Payload Short Leverage Is Exactly 100",
        payload["isolatedShortLeverage"] == "100",
    )


    # =========================================================================
    section(
        "R34C TEST 8: SYNTHETIC TRANSPORT ENVELOPE"
    )
    # =========================================================================

    envelope = build_synthetic_envelope(
        observation,
        intent,
        payload,
    )

    runtime_state["envelope_hash"] = (
        sha256_object(envelope)
    )

    check(
        "Envelope Transport Is Synthetic",
        envelope["transport"]
        == "SYNTHETIC",
    )

    check(
        "Envelope Method Is POST",
        envelope["method"]
        == "POST",
    )

    check(
        "Envelope Path Is Exact V3 Leverage Endpoint",
        envelope["path"]
        == "/capi/v3/account/leverage",
    )

    check(
        "Envelope Observation Hash Matches",
        envelope["observation_hash"]
        == observation_hash_1,
    )

    check(
        "Envelope Intent Hash Matches",
        envelope["intent_hash"]
        == sha256_object(intent),
    )

    check(
        "Envelope Payload Hash Matches",
        envelope["payload_hash"]
        == sha256_object(payload),
    )

    check(
        "Envelope Authorization Is Not Granted",
        envelope["authorization"]
        == "NOT_GRANTED",
    )

    check(
        "Envelope Network Write Remains Disabled",
        envelope["network_write_enabled"]
        is False,
    )

    check(
        "Envelope Leverage Mutation Remains Disabled",
        envelope["leverage_mutation_enabled"]
        is False,
    )

    check(
        "Envelope Confirms Exchange Not Contacted",
        envelope["exchange_contacted"]
        is False,
    )


    # =========================================================================
    section(
        "R34C TEST 9: SYNTHETIC DISPATCH"
    )
    # =========================================================================

    receipt = synthetic_dispatch(
        envelope
    )

    runtime_state["receipt_hash"] = (
        sha256_object(receipt)
    )

    check(
        "Exactly One Synthetic Dispatch Occurred",
        synthetic_dispatch_counter == 1,
    )

    check(
        "Synthetic Receipt Transport Is Synthetic",
        receipt["transport"]
        == "SYNTHETIC",
    )

    check(
        "Synthetic Dispatch Was Intercepted",
        receipt["dispatch"]
        == "INTERCEPTED",
    )

    check(
        "Receipt Preserves Exact Leverage Endpoint",
        receipt["path"]
        == LEVERAGE_MUTATION_PATH,
    )

    check(
        "Receipt Confirms No Network Transmission",
        receipt["network_transmission"]
        is False,
    )

    check(
        "Receipt Confirms Exchange Was Not Contacted",
        receipt["exchange_contacted"]
        is False,
    )

    check(
        "Receipt Confirms Leverage Was Not Mutated",
        receipt["leverage_mutated"]
        is False,
    )

    check(
        "Receipt Confirms No Real Order Was Sent",
        receipt["real_order_sent"]
        is False,
    )


    # =========================================================================
    section(
        "R34C TEST 10: DUPLICATE SYNTHETIC DISPATCH REJECTION"
    )
    # =========================================================================

    duplicate_rejected = False

    try:
        synthetic_dispatch(
            envelope
        )

    except RuntimeError:
        duplicate_rejected = True

    check(
        "Duplicate Synthetic Dispatch Is Rejected",
        duplicate_rejected is True,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        synthetic_dispatch_counter == 1,
    )

    check(
        "Duplicate Dispatch Block Counter Is One",
        duplicate_dispatch_block_counter == 1,
    )


    # =========================================================================
    section(
        "R34C TEST 11: LIVE OBSERVATION TAMPER DETECTION"
    )
    # =========================================================================

    tampered_observation = dict(
        observation
    )

    tampered_observation[
        "isolatedLongLeverage"
    ] = 999

    tampered_hash = sha256_object(
        tampered_observation
    )

    check(
        "Tampered Observation Changes Hash",
        tampered_hash != observation_hash_1,
    )

    check(
        "Intent Remains Bound To Original Observation",
        intent["observation_hash"]
        != tampered_hash,
    )


    # =========================================================================
    section(
        "R34C TEST 12: PAYLOAD TAMPER DETECTION"
    )
    # =========================================================================

    tampered_payload = dict(
        payload
    )

    tampered_payload[
        "isolatedLongLeverage"
    ] = "99"

    check(
        "Tampered Payload Changes Hash",
        sha256_object(tampered_payload)
        != runtime_state["payload_hash"],
    )

    check(
        "Envelope Remains Bound To Original Payload",
        envelope["payload_hash"]
        == runtime_state["payload_hash"],
    )


    # =========================================================================
    section(
        "R34C TEST 13: TERMINAL SAFETY COUNTERS"
    )
    # =========================================================================

    check(
        "Real Order Counter Is Zero",
        real_order_counter == 0,
    )

    check(
        "Network Write Counter Is Zero",
        network_write_counter == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        leverage_mutation_counter == 0,
    )

    check(
        "Authenticated GET Counter Is One",
        authenticated_get_counter == 1,
    )

    check(
        "Synthetic Dispatch Counter Is One",
        synthetic_dispatch_counter == 1,
    )


    # =========================================================================
    section(
        "R34C TEST 14: FINAL FIREBREAK VALIDATION"
    )
    # =========================================================================

    check(
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Writes Remain Disabled",
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
        "Synthetic-Only Mode Remains Enabled",
        SYNTHETIC_ONLY is True,
    )


    # =========================================================================
    # FINAL PHASE
    # =========================================================================

    runtime_state["phase"] = (
        "LIVE_OBSERVATION_INTENT_BOUND"
    )

    banner(
        "R34C VALIDATION COMPLETE"
    )

    print(
        f"{VERSION}: PHASE="
        f"{runtime_state['phase']}",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE OBSERVATION HASH="
        f"{runtime_state['observation_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION INTENT HASH="
        f"{runtime_state['intent_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET PAYLOAD HASH="
        f"{runtime_state['payload_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC ENVELOPE HASH="
        f"{runtime_state['envelope_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC RECEIPT HASH="
        f"{runtime_state['receipt_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED "
        f"MARGIN={runtime_state['observed_margin_type']} "
        f"LONG={runtime_state['observed_long_leverage']}x "
        f"SHORT={runtime_state['observed_short_leverage']}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET "
        f"MARGIN={TARGET_MARGIN_TYPE} "
        f"LONG={TARGET_LONG_LEVERAGE}x "
        f"SHORT={TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{runtime_state['correction_required']}",
        flush=True,
    )

    print(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{authenticated_get_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{synthetic_dispatch_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDERS="
        f"{real_order_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES="
        f"{network_write_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{leverage_mutation_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: NO REAL LEVERAGE CHANGE WAS SENT",
        flush=True,
    )


# =============================================================================
# PART 4 OF 4
# HEARTBEAT / ENTRYPOINT
# =============================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"phase={runtime_state['phase']} | "
            f"synthetic-only={SYNTHETIC_ONLY} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED} | "
            f"authenticated-get="
            f"{authenticated_get_counter} | "
            f"intent-bound="
            f"{runtime_state['intent_hash'] is not None} | "
            f"synthetic-dispatch="
            f"{synthetic_dispatch_counter} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"correction-required="
            f"{runtime_state['correction_required']} | "
            f"observed-margin="
            f"{runtime_state['observed_margin_type']} | "
            f"observed-long="
            f"{runtime_state['observed_long_leverage']}x | "
            f"observed-short="
            f"{runtime_state['observed_short_leverage']}x | "
            f"target-long="
            f"{TARGET_LONG_LEVERAGE}x | "
            f"target-short="
            f"{TARGET_SHORT_LEVERAGE}x",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


def main():

    start_health_server()

    run_validation()

    heartbeat_loop()


if __name__ == "__main__":
    main()
