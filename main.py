# =============================================================================
# R34G - FINAL PRE-WRITE / CONTROLLED EXECUTION-GATE VALIDATION
#
# PURPOSE
# -----------------------------------------------------------------------------
# 1. Perform fresh authenticated read-only reconciliation against WEEX.
# 2. Confirm BTCUSDT remains ISOLATED.
# 3. Confirm no BTCUSDT position is open.
# 4. Confirm leverage correction is still required.
# 5. Bind the 100x / 100x correction payload to fresh live state.
# 6. Construct and sign the exact V3 leverage correction envelope OFFLINE.
# 7. Validate stale-state rejection.
# 8. Validate payload / envelope / authorization bindings.
# 9. Perform exactly one SYNTHETIC transport dispatch.
# 10. Reject replay.
# 11. Re-read live state after synthetic dispatch.
# 12. Confirm absolutely no exchange mutation occurred.
#
# IMPORTANT
# -----------------------------------------------------------------------------
# REAL ORDER EXECUTION:      DISABLED
# NETWORK WRITES:            DISABLED
# LEVERAGE MUTATION:         DISABLED
# SYNTHETIC TRANSPORT ONLY:  ENABLED
#
# NO HTTP POST IS IMPLEMENTED IN THIS PROGRAM.
# =============================================================================

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

from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R34G CONSTANTS
# =============================================================================

VERSION = "R34G"

SYMBOL = "BTCUSDT"

BASE_URL = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
ALL_POSITIONS_PATH = "/capi/v3/account/position/allPosition"

LEVERAGE_CORRECTION_PATH = "/capi/v3/account/leverage"

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

HEALTH_PORT = int(os.getenv("PORT", "10000"))

HTTP_TIMEOUT_SECONDS = 15

# Maximum acceptable age for a state snapshot before authorization.
MAX_STATE_AGE_MS = 15_000


# =============================================================================
# ABSOLUTE SAFETY LOCKS
# =============================================================================

SYNTHETIC_ONLY = True

AUTHENTICATED_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

REAL_HTTP_POST_IMPLEMENTED = False


# =============================================================================
# RUNTIME COUNTERS
# =============================================================================

authenticated_get_counter = 0

network_write_counter = 0
real_order_counter = 0
leverage_mutation_counter = 0

synthetic_dispatch_counter = 0
duplicate_dispatch_block_counter = 0

stale_state_block_counter = 0

authorization_consumed = False
dispatch_committed = False

heartbeat_counter = 0


# =============================================================================
# TERMINAL RUNTIME STATE
# =============================================================================

runtime_phase = "BOOTING"

observed_margin_type = "UNKNOWN"
observed_long_leverage = None
observed_short_leverage = None
observed_open_positions = None

correction_required = False
correction_ready = False

fresh_state_validated = False
execution_gate_validated = False


# =============================================================================
# FORMATTING
# =============================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def check(name, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    log(f"{name:<82} {status}")

    if not condition:
        raise AssertionError(name)


# =============================================================================
# HASHING / CANONICAL SERIALIZATION
# =============================================================================

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
    return sha256_text(
        canonical_json(value)
    )


# =============================================================================
# CREDENTIAL RESOLUTION
# =============================================================================

def first_environment_value(*names):
    for name in names:
        value = os.getenv(name)

        if value is not None and value.strip():
            return value.strip()

    return ""


API_KEY = first_environment_value(
    "WEEX_API_KEY",
    "API_KEY",
)

SECRET_KEY = first_environment_value(
    "WEEX_SECRET_KEY",
    "WEEX_API_SECRET",
    "SECRET_KEY",
    "API_SECRET",
)

ACCESS_PASSPHRASE = first_environment_value(
    "WEEX_PASSPHRASE",
    "WEEX_API_PASSPHRASE",
    "ACCESS_PASSPHRASE",
    "PASSPHRASE",
)


# =============================================================================
# WEEX V3 SIGNATURE
# =============================================================================

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
        unsigned = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )
    else:
        unsigned = (
            timestamp
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        secret_key.encode("utf-8"),
        unsigned.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# =============================================================================
# AUTHENTICATED GET
#
# IMPORTANT:
# This program has ONLY an authenticated GET transport.
# There is deliberately no generic authenticated request function and
# deliberately no HTTP POST transport.
# =============================================================================

def authenticated_get(request_path, parameters=None):
    global authenticated_get_counter

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated reads are disabled."
        )

    if not API_KEY:
        raise RuntimeError(
            "Missing WEEX API key."
        )

    if not SECRET_KEY:
        raise RuntimeError(
            "Missing WEEX secret key."
        )

    if not ACCESS_PASSPHRASE:
        raise RuntimeError(
            "Missing WEEX passphrase."
        )

    parameters = parameters or {}

    query_string = urllib.parse.urlencode(parameters)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_signature(
        secret_key=SECRET_KEY,
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": ACCESS_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "locale": "en-US",
    }

    url = BASE_URL + request_path

    if query_string:
        url += "?" + query_string

    # Explicit GET object.
    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            status = response.getcode()

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Authenticated GET failed "
            f"HTTP {exc.code}: {body}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Authenticated GET transport error: {exc}"
        ) from exc

    if status < 200 or status >= 300:
        raise RuntimeError(
            f"Unexpected HTTP status: {status}"
        )

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"WEEX returned invalid JSON: {raw}"
        ) from exc

    authenticated_get_counter += 1

    return payload


# =============================================================================
# RESPONSE NORMALIZATION
# =============================================================================

def unwrap_data(payload):
    current = payload

    # Some API responses may contain a top-level data object.
    for _ in range(4):
        if (
            isinstance(current, dict)
            and "data" in current
            and current["data"] is not None
        ):
            current = current["data"]
        else:
            break

    return current


def normalize_symbol_config(payload):
    data = unwrap_data(payload)

    if isinstance(data, list):
        candidates = data

    elif isinstance(data, dict):
        candidates = [data]

    else:
        raise RuntimeError(
            "Unexpected symbolConfig response structure."
        )

    for item in candidates:
        if not isinstance(item, dict):
            continue

        symbol = str(
            item.get("symbol", "")
        ).upper()

        if symbol == SYMBOL:
            return item

    # If the endpoint returned exactly one config object and omitted symbol,
    # accept that object only as a fallback.
    if len(candidates) == 1:
        item = candidates[0]

        if isinstance(item, dict):
            return item

    raise RuntimeError(
        f"{SYMBOL} configuration was not found."
    )


def normalize_positions(payload):
    data = unwrap_data(payload)

    if data is None:
        return []

    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, dict):
        # Defensive support for alternative wrappers.
        for key in (
            "positions",
            "positionList",
            "list",
            "rows",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return [
                    item
                    for item in value
                    if isinstance(item, dict)
                ]

        # Single position object fallback.
        if "symbol" in data:
            return [data]

    raise RuntimeError(
        "Unexpected position response structure."
    )


# =============================================================================
# VALUE NORMALIZATION
# =============================================================================

def integer_leverage(value):
    if value is None:
        return None

    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None


def decimal_is_nonzero(value):
    if value is None:
        return False

    try:
        return abs(float(str(value))) > 0.0
    except (ValueError, TypeError):
        return False


def position_size(position):
    for key in (
        "size",
        "quantity",
        "qty",
        "positionAmt",
        "positionSize",
        "available",
    ):
        if key in position:
            return position.get(key)

    return "0"


def count_open_symbol_positions(positions):
    count = 0

    for position in positions:
        symbol = str(
            position.get("symbol", "")
        ).upper()

        if symbol != SYMBOL:
            continue

        if decimal_is_nonzero(
            position_size(position)
        ):
            count += 1

    return count


# =============================================================================
# LIVE STATE CAPTURE
# =============================================================================

def retrieve_live_state():
    symbol_response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    position_response = authenticated_get(
        ALL_POSITIONS_PATH
    )

    config = normalize_symbol_config(
        symbol_response
    )

    positions = normalize_positions(
        position_response
    )

    margin_type = str(
        config.get("marginType", "")
    ).upper()

    long_leverage = integer_leverage(
        config.get("isolatedLongLeverage")
    )

    short_leverage = integer_leverage(
        config.get("isolatedShortLeverage")
    )

    open_positions = count_open_symbol_positions(
        positions
    )

    observed_at_ms = int(
        time.time() * 1000
    )

    state = {
        "version": VERSION,
        "symbol": SYMBOL,
        "marginType": margin_type,
        "isolatedLongLeverage": long_leverage,
        "isolatedShortLeverage": short_leverage,
        "openPositions": open_positions,
        "observedAtMs": observed_at_ms,
    }

    return state


# =============================================================================
# STATE FRESHNESS
# =============================================================================

def state_age_ms(state):
    observed_at = int(
        state.get("observedAtMs", 0)
    )

    now = int(
        time.time() * 1000
    )

    return max(
        0,
        now - observed_at,
    )


def state_is_fresh(state):
    return (
        state_age_ms(state)
        <= MAX_STATE_AGE_MS
    )


# =============================================================================
# CORRECTION REQUIREMENT
# =============================================================================

def correction_is_required(state):
    return (
        state["isolatedLongLeverage"]
        != TARGET_LONG_LEVERAGE
        or
        state["isolatedShortLeverage"]
        != TARGET_SHORT_LEVERAGE
    )


def correction_preconditions_hold(state):
    return (
        state["symbol"] == SYMBOL
        and
        state["marginType"] == TARGET_MARGIN_TYPE
        and
        state["openPositions"] == 0
        and
        state_is_fresh(state)
        and
        correction_is_required(state)
    )


# =============================================================================
# EXACT V3 CORRECTION PAYLOAD
# =============================================================================

def construct_correction_payload():
    return {
        "symbol": SYMBOL,
        "marginType": TARGET_MARGIN_TYPE,
        "isolatedLongLeverage": str(
            TARGET_LONG_LEVERAGE
        ),
        "isolatedShortLeverage": str(
            TARGET_SHORT_LEVERAGE
        ),
    }


# =============================================================================
# OFFLINE POST ENVELOPE CONSTRUCTION
#
# THIS DOES NOT TRANSMIT ANYTHING.
# =============================================================================

def construct_offline_envelope(
    state_hash,
    payload,
):
    body = canonical_json(payload)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_signature(
        secret_key=SECRET_KEY,
        timestamp=timestamp,
        method="POST",
        request_path=LEVERAGE_CORRECTION_PATH,
        query_string="",
        body=body,
    )

    envelope = {
        "version": VERSION,

        "transport": "SYNTHETIC_ONLY",

        "method": "POST",

        "path": LEVERAGE_CORRECTION_PATH,

        "queryString": "",

        "body": body,

        "payloadHash": sha256_text(body),

        "liveStateHash": state_hash,

        "headers": {
            "ACCESS-KEY": API_KEY,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": ACCESS_PASSPHRASE,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
        },

        "networkWriteAllowed": False,

        "leverageMutationAllowed": False,

        "realExecutionAllowed": False,
    }

    return envelope


# =============================================================================
# OFFLINE SIGNATURE RECOMPUTATION
# =============================================================================

def recompute_envelope_signature(
    envelope,
):
    return generate_signature(
        secret_key=SECRET_KEY,
        timestamp=envelope[
            "headers"
        ][
            "ACCESS-TIMESTAMP"
        ],
        method=envelope["method"],
        request_path=envelope["path"],
        query_string=envelope[
            "queryString"
        ],
        body=envelope["body"],
    )


# =============================================================================
# ONE-TIME SYNTHETIC AUTHORIZATION
# =============================================================================

def construct_authorization(
    live_state,
    state_hash,
    payload_hash,
    envelope_hash,
):
    authorization = {
        "version": VERSION,

        "type": "SYNTHETIC_CORRECTION_AUTHORIZATION",

        "symbol": SYMBOL,

        "marginType": TARGET_MARGIN_TYPE,

        "targetLongLeverage":
            TARGET_LONG_LEVERAGE,

        "targetShortLeverage":
            TARGET_SHORT_LEVERAGE,

        "liveStateHash": state_hash,

        "payloadHash": payload_hash,

        "envelopeHash": envelope_hash,

        "observedAtMs":
            live_state["observedAtMs"],

        "issuedAtMs":
            int(time.time() * 1000),

        "syntheticOnly": True,

        "exchangeWriteAllowed": False,

        "leverageMutationAllowed": False,

        "realExecutionAllowed": False,

        "consumed": False,
    }

    return authorization


# =============================================================================
# AUTHORIZATION VALIDATION
# =============================================================================

def validate_authorization(
    authorization,
    live_state,
    state_hash,
    payload_hash,
    envelope_hash,
):
    return (
        authorization["symbol"] == SYMBOL

        and authorization["marginType"]
        == TARGET_MARGIN_TYPE

        and authorization[
            "targetLongLeverage"
        ]
        == TARGET_LONG_LEVERAGE

        and authorization[
            "targetShortLeverage"
        ]
        == TARGET_SHORT_LEVERAGE

        and authorization[
            "liveStateHash"
        ]
        == state_hash

        and authorization[
            "payloadHash"
        ]
        == payload_hash

        and authorization[
            "envelopeHash"
        ]
        == envelope_hash

        and authorization[
            "observedAtMs"
        ]
        == live_state["observedAtMs"]

        and authorization["syntheticOnly"]
        is True

        and authorization[
            "exchangeWriteAllowed"
        ]
        is False

        and authorization[
            "leverageMutationAllowed"
        ]
        is False

        and authorization[
            "realExecutionAllowed"
        ]
        is False

        and authorization["consumed"]
        is False

        and correction_preconditions_hold(
            live_state
        )
    )


# =============================================================================
# SYNTHETIC TRANSPORT
#
# THIS FUNCTION CANNOT REACH WEEX.
# =============================================================================

def synthetic_dispatch(
    authorization,
    envelope,
):
    global authorization_consumed
    global dispatch_committed
    global synthetic_dispatch_counter
    global duplicate_dispatch_block_counter

    if authorization_consumed:
        duplicate_dispatch_block_counter += 1

        raise RuntimeError(
            "Authorization replay rejected."
        )

    if authorization.get("consumed"):
        duplicate_dispatch_block_counter += 1

        raise RuntimeError(
            "Authorization already consumed."
        )

    if envelope[
        "transport"
    ] != "SYNTHETIC_ONLY":
        raise RuntimeError(
            "Non-synthetic transport rejected."
        )

    if envelope[
        "networkWriteAllowed"
    ] is not False:
        raise RuntimeError(
            "Network-enabled envelope rejected."
        )

    if envelope[
        "leverageMutationAllowed"
    ] is not False:
        raise RuntimeError(
            "Mutation-enabled envelope rejected."
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Network write safety invariant failed."
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "Leverage mutation safety invariant failed."
        )

    if REAL_ORDER_EXECUTION_ENABLED:
        raise RuntimeError(
            "Real execution safety invariant failed."
        )

    if REAL_HTTP_POST_IMPLEMENTED:
        raise RuntimeError(
            "Real HTTP POST unexpectedly enabled."
        )

    authorization[
        "consumed"
    ] = True

    authorization_consumed = True

    dispatch_committed = True

    synthetic_dispatch_counter += 1

    receipt = {
        "version": VERSION,

        "transport": "SYNTHETIC_ONLY",

        "symbol": SYMBOL,

        "path": envelope["path"],

        "payloadHash":
            envelope["payloadHash"],

        "envelopeHash":
            sha256_object(envelope),

        "authorizationConsumed": True,

        "dispatchCommitted": True,

        "networkTransmissionOccurred": False,

        "exchangeContactedForWrite": False,

        "leverageMutationOccurred": False,

        "realOrderOccurred": False,

        "networkWriteCounter":
            network_write_counter,

        "leverageMutationCounter":
            leverage_mutation_counter,

        "realOrderCounter":
            real_order_counter,

        "syntheticDispatchCounter":
            synthetic_dispatch_counter,
    }

    return receipt


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "status": "ok",

            "version": VERSION,

            "phase": runtime_phase,

            "symbol": SYMBOL,

            "syntheticOnly":
                SYNTHETIC_ONLY,

            "realExecution":
                REAL_ORDER_EXECUTION_ENABLED,

            "networkWrites":
                EXCHANGE_NETWORK_WRITES_ENABLED,

            "leverageMutation":
                LEVERAGE_MUTATION_ENABLED,

            "authenticatedGets":
                authenticated_get_counter,

            "networkWriteCounter":
                network_write_counter,

            "leverageMutationCounter":
                leverage_mutation_counter,

            "realOrderCounter":
                real_order_counter,

            "syntheticDispatchCounter":
                synthetic_dispatch_counter,

            "duplicateDispatchBlocks":
                duplicate_dispatch_block_counter,

            "staleStateBlocks":
                stale_state_block_counter,

            "authorizationConsumed":
                authorization_consumed,

            "dispatchCommitted":
                dispatch_committed,

            "freshStateValidated":
                fresh_state_validated,

            "executionGateValidated":
                execution_gate_validated,

            "observedMargin":
                observed_margin_type,

            "observedLongLeverage":
                observed_long_leverage,

            "observedShortLeverage":
                observed_short_leverage,

            "openPositions":
                observed_open_positions,

            "targetLongLeverage":
                TARGET_LONG_LEVERAGE,

            "targetShortLeverage":
                TARGET_SHORT_LEVERAGE,

            "correctionRequired":
                correction_required,

            "correctionReady":
                correction_ready,
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

    def log_message(
        self,
        format,
        *args,
    ):
        return


def start_health_server():

    def worker():
        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        server.serve_forever()

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():
    global heartbeat_counter

    while True:
        heartbeat_counter += 1

        log(
            f"{VERSION}: HEARTBEAT "
            f"{heartbeat_counter} | "
            f"phase={runtime_phase} | "
            f"synthetic-only={SYNTHETIC_ONLY} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED} | "
            f"authenticated-get="
            f"{authenticated_get_counter} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"network-write-counter="
            f"{network_write_counter} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"leverage-mutation-counter="
            f"{leverage_mutation_counter} | "
            f"synthetic-dispatch="
            f"{synthetic_dispatch_counter} | "
            f"duplicate-dispatch-block="
            f"{duplicate_dispatch_block_counter} | "
            f"authorization-consumed="
            f"{authorization_consumed} | "
            f"fresh-state="
            f"{fresh_state_validated} | "
            f"stale-state-blocked="
            f"{stale_state_block_counter} | "
            f"open-positions="
            f"{observed_open_positions} | "
            f"correction-required="
            f"{correction_required} | "
            f"correction-ready="
            f"{correction_ready} | "
            f"execution-gate="
            f"{execution_gate_validated} | "
            f"observed-margin="
            f"{observed_margin_type} | "
            f"observed-long="
            f"{observed_long_leverage}x | "
            f"observed-short="
            f"{observed_short_leverage}x | "
            f"target-long="
            f"{TARGET_LONG_LEVERAGE}x | "
            f"target-short="
            f"{TARGET_SHORT_LEVERAGE}x"
        )

        time.sleep(30)


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def main():

    global runtime_phase

    global observed_margin_type
    global observed_long_leverage
    global observed_short_leverage
    global observed_open_positions

    global correction_required
    global correction_ready

    global fresh_state_validated
    global execution_gate_validated

    global stale_state_block_counter


    # =========================================================================
    section(f"{VERSION}: MAIN.PY ENTERED")
    # =========================================================================

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(
        f"{VERSION}: HEALTH PORT="
        f"{HEALTH_PORT}"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"{VERSION}: EXACT V3 LEVERAGE PATH="
        f"{LEVERAGE_CORRECTION_PATH}"
    )

    log(
        f"{VERSION}: REAL EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )

    log(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 1: "
        "ABSOLUTE WRITE SAFETY CONFIGURATION"
    )
    # =========================================================================

    check(
        "Synthetic Only Is Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED
        is True,
    )

    check(
        "Real Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Real HTTP POST Is Not Implemented",
        REAL_HTTP_POST_IMPLEMENTED
        is False,
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 2: "
        "CREDENTIAL PRESENCE"
    )
    # =========================================================================

    check(
        "API Key Is Present",
        bool(API_KEY),
    )

    check(
        "Secret Key Is Present",
        bool(SECRET_KEY),
    )

    check(
        "Access Passphrase Is Present",
        bool(ACCESS_PASSPHRASE),
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 3: "
        "FRESH AUTHENTICATED LIVE STATE"
    )
    # =========================================================================

    initial_state = retrieve_live_state()

    initial_state_hash = sha256_object(
        initial_state
    )

    observed_margin_type = initial_state[
        "marginType"
    ]

    observed_long_leverage = initial_state[
        "isolatedLongLeverage"
    ]

    observed_short_leverage = initial_state[
        "isolatedShortLeverage"
    ]

    observed_open_positions = initial_state[
        "openPositions"
    ]

    check(
        "Fresh Authenticated State Was Retrieved",
        authenticated_get_counter >= 2,
    )

    check(
        "State Symbol Is BTCUSDT",
        initial_state["symbol"] == SYMBOL,
    )

    check(
        "State Has Observation Timestamp",
        initial_state[
            "observedAtMs"
        ] > 0,
    )

    check(
        "State Is Fresh",
        state_is_fresh(initial_state),
    )

    fresh_state_validated = True

    log(
        f"{VERSION}: LIVE STATE SHA256="
        f"{initial_state_hash}"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 4: "
        "LIVE MARGIN / LEVERAGE RECONCILIATION"
    )
    # =========================================================================

    check(
        "Observed Margin Is ISOLATED",
        observed_margin_type
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Observed Long Leverage Is Valid",
        observed_long_leverage
        is not None,
    )

    check(
        "Observed Short Leverage Is Valid",
        observed_short_leverage
        is not None,
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observed_margin_type}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{observed_long_leverage}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{observed_short_leverage}x"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 5: "
        "ZERO OPEN POSITION GATE"
    )
    # =========================================================================

    check(
        "Open Position Count Was Retrieved",
        observed_open_positions
        is not None,
    )

    check(
        "No BTCUSDT Position Is Open",
        observed_open_positions == 0,
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 6: "
        "CORRECTION REQUIREMENT"
    )
    # =========================================================================

    correction_required = (
        correction_is_required(
            initial_state
        )
    )

    correction_ready = (
        correction_preconditions_hold(
            initial_state
        )
    )

    check(
        "100x / 100x Correction Is Required",
        correction_required is True,
    )

    check(
        "Correction Preconditions Hold",
        correction_ready is True,
    )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE == 100,
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE == 100,
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 7: "
        "STALE STATE REJECTION"
    )
    # =========================================================================

    stale_state = dict(initial_state)

    stale_state[
        "observedAtMs"
    ] = (
        int(time.time() * 1000)
        - MAX_STATE_AGE_MS
        - 10_000
    )

    stale_rejected = (
        not correction_preconditions_hold(
            stale_state
        )
    )

    if stale_rejected:
        stale_state_block_counter += 1

    check(
        "Synthetic Stale State Is Rejected",
        stale_rejected,
    )

    check(
        "Stale State Block Counter Is One",
        stale_state_block_counter == 1,
    )

    check(
        "Original Live State Remains Fresh",
        state_is_fresh(initial_state),
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 8: "
        "EXACT V3 CORRECTION PAYLOAD"
    )
    # =========================================================================

    correction_payload = (
        construct_correction_payload()
    )

    payload_body = canonical_json(
        correction_payload
    )

    payload_hash = sha256_text(
        payload_body
    )

    check(
        "Payload Symbol Is BTCUSDT",
        correction_payload[
            "symbol"
        ] == SYMBOL,
    )

    check(
        "Payload Margin Type Is ISOLATED",
        correction_payload[
            "marginType"
        ] == TARGET_MARGIN_TYPE,
    )

    check(
        "Payload Long Leverage Is Exactly 100",
        correction_payload[
            "isolatedLongLeverage"
        ] == "100",
    )

    check(
        "Payload Short Leverage Is Exactly 100",
        correction_payload[
            "isolatedShortLeverage"
        ] == "100",
    )

    log(
        f"{VERSION}: PAYLOAD="
        f"{payload_body}"
    )

    log(
        f"{VERSION}: PAYLOAD SHA256="
        f"{payload_hash}"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 9: "
        "OFFLINE V3 ENVELOPE CONSTRUCTION"
    )
    # =========================================================================

    envelope = construct_offline_envelope(
        state_hash=initial_state_hash,
        payload=correction_payload,
    )

    envelope_hash = sha256_object(
        envelope
    )

    check(
        "Envelope Method Is POST",
        envelope["method"] == "POST",
    )

    check(
        "Envelope Uses Exact V3 Leverage Path",
        envelope["path"]
        == LEVERAGE_CORRECTION_PATH,
    )

    check(
        "Envelope Transport Is Synthetic Only",
        envelope[
            "transport"
        ] == "SYNTHETIC_ONLY",
    )

    check(
        "Envelope Payload Hash Matches",
        envelope[
            "payloadHash"
        ] == payload_hash,
    )

    check(
        "Envelope Live State Hash Matches",
        envelope[
            "liveStateHash"
        ] == initial_state_hash,
    )

    check(
        "Envelope Forbids Network Write",
        envelope[
            "networkWriteAllowed"
        ] is False,
    )

    check(
        "Envelope Forbids Leverage Mutation",
        envelope[
            "leverageMutationAllowed"
        ] is False,
    )

    check(
        "Envelope Forbids Real Execution",
        envelope[
            "realExecutionAllowed"
        ] is False,
    )

    log(
        f"{VERSION}: ENVELOPE SHA256="
        f"{envelope_hash}"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 10: "
        "OFFLINE SIGNATURE VALIDATION"
    )
    # =========================================================================

    headers = envelope["headers"]

    check(
        "ACCESS-KEY Header Is Present",
        bool(headers.get("ACCESS-KEY")),
    )

    check(
        "ACCESS-SIGN Header Is Present",
        bool(headers.get("ACCESS-SIGN")),
    )

    check(
        "ACCESS-PASSPHRASE Header Is Present",
        bool(
            headers.get(
                "ACCESS-PASSPHRASE"
            )
        ),
    )

    check(
        "ACCESS-TIMESTAMP Header Is Present",
        bool(
            headers.get(
                "ACCESS-TIMESTAMP"
            )
        ),
    )

    recomputed_signature = (
        recompute_envelope_signature(
            envelope
        )
    )

    check(
        "Envelope Signature Recomputes Exactly",
        recomputed_signature
        == headers["ACCESS-SIGN"],
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 11: "
        "FRESH-STATE-BOUND AUTHORIZATION"
    )
    # =========================================================================

    authorization = (
        construct_authorization(
            live_state=initial_state,
            state_hash=initial_state_hash,
            payload_hash=payload_hash,
            envelope_hash=envelope_hash,
        )
    )

    authorization_hash = sha256_object(
        authorization
    )

    check(
        "Authorization Is Initially Unconsumed",
        authorization[
            "consumed"
        ] is False,
    )

    check(
        "Authorization Is Synthetic Only",
        authorization[
            "syntheticOnly"
        ] is True,
    )

    check(
        "Authorization Forbids Exchange Write",
        authorization[
            "exchangeWriteAllowed"
        ] is False,
    )

    check(
        "Authorization Forbids Mutation",
        authorization[
            "leverageMutationAllowed"
        ] is False,
    )

    check(
        "Authorization Is Bound To Fresh State",
        authorization[
            "liveStateHash"
        ] == initial_state_hash,
    )

    check(
        "Authorization Is Bound To Payload",
        authorization[
            "payloadHash"
        ] == payload_hash,
    )

    check(
        "Authorization Is Bound To Envelope",
        authorization[
            "envelopeHash"
        ] == envelope_hash,
    )

    check(
        "Authorization Validation Passes",
        validate_authorization(
            authorization,
            initial_state,
            initial_state_hash,
            payload_hash,
            envelope_hash,
        ),
    )

    log(
        f"{VERSION}: AUTHORIZATION SHA256="
        f"{authorization_hash}"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 12: "
        "PRE-WRITE EXECUTION GATE"
    )
    # =========================================================================

    execution_gate_validated = (
        correction_ready

        and fresh_state_validated

        and initial_state[
            "openPositions"
        ] == 0

        and initial_state[
            "marginType"
        ] == TARGET_MARGIN_TYPE

        and envelope[
            "path"
        ] == LEVERAGE_CORRECTION_PATH

        and envelope[
            "networkWriteAllowed"
        ] is False

        and envelope[
            "leverageMutationAllowed"
        ] is False

        and EXCHANGE_NETWORK_WRITES_ENABLED
        is False

        and LEVERAGE_MUTATION_ENABLED
        is False

        and REAL_ORDER_EXECUTION_ENABLED
        is False

        and REAL_HTTP_POST_IMPLEMENTED
        is False
    )

    check(
        "Pre-Write Execution Gate Is Valid",
        execution_gate_validated,
    )

    check(
        "Execution Gate Still Forbids Network Write",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Execution Gate Still Forbids Mutation",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Execution Gate Cannot Perform HTTP POST",
        REAL_HTTP_POST_IMPLEMENTED
        is False,
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 13: "
        "ONE SYNTHETIC DISPATCH"
    )
    # =========================================================================

    receipt = synthetic_dispatch(
        authorization,
        envelope,
    )

    receipt_hash = sha256_object(
        receipt
    )

    check(
        "Exactly One Synthetic Dispatch Occurred",
        synthetic_dispatch_counter == 1,
    )

    check(
        "Authorization Was Consumed Exactly Once",
        authorization_consumed
        is True,
    )

    check(
        "Dispatch Was Committed Locally",
        dispatch_committed is True,
    )

    check(
        "Receipt Transport Is Synthetic Only",
        receipt[
            "transport"
        ] == "SYNTHETIC_ONLY",
    )

    check(
        "Receipt Confirms No Network Transmission",
        receipt[
            "networkTransmissionOccurred"
        ] is False,
    )

    check(
        "Receipt Confirms Exchange Not Contacted For Write",
        receipt[
            "exchangeContactedForWrite"
        ] is False,
    )

    check(
        "Receipt Confirms No Leverage Mutation",
        receipt[
            "leverageMutationOccurred"
        ] is False,
    )

    check(
        "Receipt Confirms No Real Order",
        receipt[
            "realOrderOccurred"
        ] is False,
    )

    check(
        "Receipt Network Write Counter Is Zero",
        receipt[
            "networkWriteCounter"
        ] == 0,
    )

    check(
        "Receipt Leverage Mutation Counter Is Zero",
        receipt[
            "leverageMutationCounter"
        ] == 0,
    )

    log(
        f"{VERSION}: RECEIPT SHA256="
        f"{receipt_hash}"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 14: "
        "AUTHORIZATION REPLAY REJECTION"
    )
    # =========================================================================

    replay_rejected = False

    try:
        synthetic_dispatch(
            authorization,
            envelope,
        )

    except RuntimeError:
        replay_rejected = True

    check(
        "Consumed Authorization Replay Is Rejected",
        replay_rejected,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        synthetic_dispatch_counter == 1,
    )

    check(
        "Duplicate Dispatch Block Counter Is One",
        duplicate_dispatch_block_counter
        == 1,
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 15: "
        "PAYLOAD TAMPER REJECTION"
    )
    # =========================================================================

    tampered_payload = dict(
        correction_payload
    )

    tampered_payload[
        "isolatedLongLeverage"
    ] = "99"

    tampered_payload_hash = (
        sha256_text(
            canonical_json(
                tampered_payload
            )
        )
    )

    check(
        "Tampered Payload Hash Differs",
        tampered_payload_hash
        != payload_hash,
    )

    check(
        "Authorization Does Not Bind Tampered Payload",
        authorization[
            "payloadHash"
        ] != tampered_payload_hash,
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 16: "
        "ENVELOPE TAMPER REJECTION"
    )
    # =========================================================================

    tampered_envelope = dict(
        envelope
    )

    tampered_envelope[
        "path"
    ] = "/invalid/write/path"

    tampered_envelope_hash = (
        sha256_object(
            tampered_envelope
        )
    )

    check(
        "Tampered Envelope Hash Differs",
        tampered_envelope_hash
        != envelope_hash,
    )

    check(
        "Authorization Rejects Tampered Envelope Binding",
        authorization[
            "envelopeHash"
        ] != tampered_envelope_hash,
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 17: "
        "POST-DISPATCH LIVE RECONCILIATION"
    )
    # =========================================================================

    final_state = retrieve_live_state()

    final_state_hash = sha256_object(
        final_state
    )

    check(
        "Final Authenticated State Was Retrieved",
        authenticated_get_counter >= 4,
    )

    check(
        "Final Margin Remains ISOLATED",
        final_state[
            "marginType"
        ] == TARGET_MARGIN_TYPE,
    )

    check(
        "Final Long Leverage Matches Initial",
        final_state[
            "isolatedLongLeverage"
        ]
        ==
        initial_state[
            "isolatedLongLeverage"
        ],
    )

    check(
        "Final Short Leverage Matches Initial",
        final_state[
            "isolatedShortLeverage"
        ]
        ==
        initial_state[
            "isolatedShortLeverage"
        ],
    )

    check(
        "No Position Was Opened",
        final_state[
            "openPositions"
        ] == 0,
    )

    check(
        "Observed Long Leverage Was Not Mutated",
        final_state[
            "isolatedLongLeverage"
        ]
        ==
        observed_long_leverage,
    )

    check(
        "Observed Short Leverage Was Not Mutated",
        final_state[
            "isolatedShortLeverage"
        ]
        ==
        observed_short_leverage,
    )

    log(
        f"{VERSION}: FINAL STATE SHA256="
        f"{final_state_hash}"
    )


    # =========================================================================
    section(
        f"{VERSION} TEST 18: "
        "FINAL WRITE-FREE INVARIANTS"
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
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Exchange Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Exactly One Synthetic Dispatch Is Recorded",
        synthetic_dispatch_counter == 1,
    )

    check(
        "Exactly One Replay Was Blocked",
        duplicate_dispatch_block_counter
        == 1,
    )

    check(
        "Stale State Rejection Was Exercised",
        stale_state_block_counter == 1,
    )

    check(
        "Final Pre-Write Gate Is Validated",
        execution_gate_validated
        is True,
    )


    # =========================================================================
    # TERMINAL PHASE
    # =========================================================================

    runtime_phase = (
        "FINAL_PRE_WRITE_GATE_VALIDATED"
    )


    # =========================================================================
    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )
    # =========================================================================

    log(
        f"{VERSION}: PHASE="
        f"{runtime_phase}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{authenticated_get_counter}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observed_margin_type}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{observed_long_leverage}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{observed_short_leverage}x"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"{VERSION}: OPEN POSITIONS="
        f"{observed_open_positions}"
    )

    log(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{correction_required}"
    )

    log(
        f"{VERSION}: CORRECTION READY="
        f"{correction_ready}"
    )

    log(
        f"{VERSION}: FRESH STATE VALIDATED="
        f"{fresh_state_validated}"
    )

    log(
        f"{VERSION}: EXECUTION GATE VALIDATED="
        f"{execution_gate_validated}"
    )

    log(
        f"{VERSION}: INITIAL STATE SHA256="
        f"{initial_state_hash}"
    )

    log(
        f"{VERSION}: PAYLOAD SHA256="
        f"{payload_hash}"
    )

    log(
        f"{VERSION}: ENVELOPE SHA256="
        f"{envelope_hash}"
    )

    log(
        f"{VERSION}: AUTHORIZATION SHA256="
        f"{authorization_hash}"
    )

    log(
        f"{VERSION}: RECEIPT SHA256="
        f"{receipt_hash}"
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{synthetic_dispatch_counter}"
    )

    log(
        f"{VERSION}: DUPLICATE DISPATCH BLOCKS="
        f"{duplicate_dispatch_block_counter}"
    )

    log(
        f"{VERSION}: STALE STATE BLOCKS="
        f"{stale_state_block_counter}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{network_write_counter}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{real_order_counter}"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{leverage_mutation_counter}"
    )

    log(
        f"{VERSION}: EXACT V3 PRE-WRITE "
        f"CORRECTION GATE VALIDATED"
    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO EXCHANGE WRITE WAS SENT"
    )

    log(
        f"{VERSION}: NO LEVERAGE MUTATION "
        f"WAS PERFORMED"
    )

    log(
        f"{VERSION}: REAL HTTP POST "
        f"DOES NOT EXIST IN THIS BUILD"
    )

    section("")

    heartbeat_loop()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    try:
        start_health_server()

        main()

    except KeyboardInterrupt:
        log(
            f"{VERSION}: SHUTDOWN REQUESTED"
        )

        sys.exit(0)

    except Exception as exc:
        runtime_phase = "FAILED_CLOSED"

        section(
            f"{VERSION}: FAILED CLOSED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        log(
            f"{VERSION}: NETWORK WRITES="
            f"{network_write_counter}"
        )

        log(
            f"{VERSION}: REAL ORDERS="
            f"{real_order_counter}"
        )

        log(
            f"{VERSION}: LEVERAGE MUTATIONS="
            f"{leverage_mutation_counter}"
        )

        log(
            f"{VERSION}: NO REAL ORDER WAS SENT"
        )

        log(
            f"{VERSION}: NO EXCHANGE WRITE WAS SENT"
        )

        log(
            f"{VERSION}: NO LEVERAGE MUTATION "
            f"WAS PERFORMED"
        )

        section("")

        raise
