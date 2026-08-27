# =============================================================================
# R34B MAIN.PY
# AUTHENTICATED READ-ONLY LIVE-READINESS RECONCILIATION
# =============================================================================
#
# PURPOSE
# -------
# R34B advances from R34A's fully synthetic PRE_LIVE_VALIDATED state to an
# authenticated READ-ONLY reconciliation against the real WEEX account.
#
# THIS STAGE:
#
#   ✅ Reads BTCUSDT symbol configuration from WEEX
#   ✅ Observes current margin mode
#   ✅ Observes current isolated long leverage
#   ✅ Observes current isolated short leverage
#   ✅ Determines whether 100x correction is still required
#   ✅ Builds a correction intent bound to observed account state
#   ✅ Builds the exact proposed leverage payload
#   ✅ Creates a synthetic authorization
#   ✅ Creates a synthetic transport envelope
#   ✅ Creates a synthetic receipt
#   ✅ Persists a durable readiness snapshot
#   ✅ Rejects duplicate synthetic dispatch
#
# THIS STAGE DOES NOT:
#
#   ❌ Send a leverage POST
#   ❌ Place a real order
#   ❌ Place a demo order
#   ❌ Change leverage
#   ❌ Change margin mode
#   ❌ Change position state
#   ❌ Change account state
#
# NETWORK POLICY:
#
#   Allowed:
#       GET /capi/v3/account/symbolConfig?symbol=BTCUSDT
#
#   Forbidden:
#       ALL POST
#       ALL PUT
#       ALL PATCH
#       ALL DELETE
#
# =============================================================================

import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import traceback
import urllib.parse
import urllib.request
import urllib.error

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


# =============================================================================
# PART 1
# CONSTANTS / SAFETY CONFIGURATION / UTILITIES
# =============================================================================

VERSION = "R34B"

SYMBOL = "BTCUSDT"

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

BASE_URL = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

# This remains the proposed future mutation endpoint.
# R34B DOES NOT CALL IT.
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_FILE = Path(
    os.getenv(
        "R34B_STATE_FILE",
        "/tmp/r34b_live_readiness_state.json",
    )
)

# -----------------------------------------------------------------------------
# ABSOLUTE SAFETY LOCKS
# -----------------------------------------------------------------------------

SYNTHETIC_ONLY = True

AUTHENTICATED_GET_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

REAL_POST_ENABLED = False
AUTHENTICATED_POST_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# -----------------------------------------------------------------------------
# RUNTIME COUNTERS
# -----------------------------------------------------------------------------

COUNTERS = {
    "authenticated_gets": 0,
    "authenticated_get_failures": 0,
    "synthetic_dispatches": 0,
    "duplicate_dispatch_blocks": 0,
    "real_orders": 0,
    "demo_orders": 0,
    "network_writes": 0,
    "real_posts": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,
}


# -----------------------------------------------------------------------------
# TEST COUNTERS
# -----------------------------------------------------------------------------

TOTAL_CHECKS = 0
PASSED_CHECKS = 0
FAILED_CHECKS = 0


# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------

LINE = "-" * 92


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def check(label, condition):
    global TOTAL_CHECKS
    global PASSED_CHECKS
    global FAILED_CHECKS

    TOTAL_CHECKS += 1

    if bool(condition):
        PASSED_CHECKS += 1
        status = "✅ PASS"
    else:
        FAILED_CHECKS += 1
        status = "❌ FAIL"

    log(f"{label:<78} {status}")

    return bool(condition)


# -----------------------------------------------------------------------------
# CANONICAL JSON / HASHING
# -----------------------------------------------------------------------------

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


def hash_object(value):
    return sha256_text(
        canonical_json(value)
    )


# -----------------------------------------------------------------------------
# DURABLE STATE WRITING
# -----------------------------------------------------------------------------

def atomic_write_json(path, data):
    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = Path(
        str(path) + ".tmp"
    )

    encoded = json.dumps(
        data,
        indent=2,
        sort_keys=True,
    )

    with open(
        temporary,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(
        temporary,
        path,
    )


def load_json(path):
    path = Path(path)

    if not path.exists():
        return None

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as handle:
            return json.load(handle)

    except Exception:
        return None


# -----------------------------------------------------------------------------
# CREDENTIAL RESOLUTION
# -----------------------------------------------------------------------------

def first_environment_value(*names):
    for name in names:

        value = os.getenv(
            name,
            "",
        ).strip()

        if value:
            return value

    return ""


API_KEY = first_environment_value(
    "WEEX_API_KEY",
    "API_KEY",
    "WEEX_KEY",
)

SECRET_KEY = first_environment_value(
    "WEEX_SECRET_KEY",
    "WEEX_API_SECRET",
    "API_SECRET",
    "SECRET_KEY",
)

PASSPHRASE = first_environment_value(
    "WEEX_PASSPHRASE",
    "WEEX_API_PASSPHRASE",
    "API_PASSPHRASE",
    "PASSPHRASE",
)


# =============================================================================
# PART 2
# AUTHENTICATED READ-ONLY TRANSPORT
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

        prehash = (
            str(timestamp)
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        prehash = (
            str(timestamp)
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        secret_key.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def authenticated_read_only_get(
    request_path,
    query_parameters=None,
):
    """
    R34B READ-ONLY NETWORK BOUNDARY.

    This function permits exactly:

        GET /capi/v3/account/symbolConfig

    It cannot perform POST/PUT/PATCH/DELETE.
    """

    if not AUTHENTICATED_GET_ENABLED:
        raise RuntimeError(
            "Authenticated GET is disabled."
        )

    if request_path != SYMBOL_CONFIG_PATH:
        raise RuntimeError(
            "R34B read-only allowlist rejected endpoint."
        )

    if not API_KEY:
        raise RuntimeError(
            "WEEX API key is missing."
        )

    if not SECRET_KEY:
        raise RuntimeError(
            "WEEX secret key is missing."
        )

    if not PASSPHRASE:
        raise RuntimeError(
            "WEEX passphrase is missing."
        )

    query_parameters = (
        query_parameters or {}
    )

    query_string = urllib.parse.urlencode(
        query_parameters
    )

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
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "R34B-ReadOnly-Reconciliation/1.0",
    }

    url = (
        BASE_URL
        + request_path
    )

    if query_string:
        url += "?" + query_string

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
                "utf-8"
            )

            status_code = response.status

        COUNTERS[
            "authenticated_gets"
        ] += 1

        parsed = json.loads(raw)

        return {
            "ok": True,
            "status_code": status_code,
            "data": parsed,
            "method": "GET",
            "request_path": request_path,
            "query_string": query_string,
        }

    except urllib.error.HTTPError as error:

        COUNTERS[
            "authenticated_get_failures"
        ] += 1

        try:
            body = error.read().decode(
                "utf-8"
            )

        except Exception:
            body = str(error)

        return {
            "ok": False,
            "status_code": error.code,
            "error": body,
            "method": "GET",
            "request_path": request_path,
            "query_string": query_string,
        }

    except Exception as error:

        COUNTERS[
            "authenticated_get_failures"
        ] += 1

        return {
            "ok": False,
            "status_code": None,
            "error": str(error),
            "method": "GET",
            "request_path": request_path,
            "query_string": query_string,
        }


# -----------------------------------------------------------------------------
# HARD WRITE FIREBREAKS
# -----------------------------------------------------------------------------

def real_network_write_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: ALL NETWORK WRITES ARE DISABLED."
    )


def authenticated_post_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: AUTHENTICATED POST IS DISABLED."
    )


def real_order_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: REAL ORDER EXECUTION IS DISABLED."
    )


def demo_order_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: DEMO ORDER EXECUTION IS DISABLED."
    )


def leverage_mutation_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: LEVERAGE MUTATION IS DISABLED."
    )


def margin_mutation_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: MARGIN MUTATION IS DISABLED."
    )


def position_mutation_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: POSITION MUTATION IS DISABLED."
    )


def account_mutation_firebreak(*args, **kwargs):
    raise RuntimeError(
        "R34B FIREBREAK: ACCOUNT MUTATION IS DISABLED."
    )


def firebreak_rejects(function):
    try:
        function()
        return False

    except RuntimeError:
        return True


# -----------------------------------------------------------------------------
# RESPONSE NORMALIZATION
# -----------------------------------------------------------------------------

def unwrap_symbol_configuration(data):
    """
    WEEX normally returns a list for symbolConfig.

    This function also tolerates wrappers such as:
        {"data": [...]}
    """

    candidate = data

    if isinstance(
        candidate,
        dict,
    ):

        if "data" in candidate:
            candidate = candidate[
                "data"
            ]

    if isinstance(
        candidate,
        list,
    ):

        for item in candidate:

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

            if symbol == SYMBOL:
                return item

        if len(candidate) == 1:

            if isinstance(
                candidate[0],
                dict,
            ):
                return candidate[0]

    if isinstance(
        candidate,
        dict,
    ):
        return candidate

    return None


def safe_int(value):
    try:
        return int(
            float(
                str(value)
            )
        )

    except Exception:
        return None


# =============================================================================
# PART 3
# RECONCILIATION / INTENT / SYNTHETIC AUTHORIZATION / DISPATCH
# =============================================================================

def build_observed_snapshot(
    symbol_config,
):
    observed = {
        "symbol": str(
            symbol_config.get(
                "symbol",
                "",
            )
        ).upper(),

        "margin_type": str(
            symbol_config.get(
                "marginType",
                "",
            )
        ).upper(),

        "position_mode": str(
            symbol_config.get(
                "separatedType",
                "",
            )
        ).upper(),

        "cross_leverage": safe_int(
            symbol_config.get(
                "crossLeverage"
            )
        ),

        "isolated_long_leverage": safe_int(
            symbol_config.get(
                "isolatedLongLeverage"
            )
        ),

        "isolated_short_leverage": safe_int(
            symbol_config.get(
                "isolatedShortLeverage"
            )
        ),
    }

    observed[
        "snapshot_hash"
    ] = hash_object(
        observed
    )

    return observed


def correction_required(
    observed,
):
    return not (
        observed[
            "margin_type"
        ] == TARGET_MARGIN_TYPE

        and observed[
            "isolated_long_leverage"
        ] == TARGET_LONG_LEVERAGE

        and observed[
            "isolated_short_leverage"
        ] == TARGET_SHORT_LEVERAGE
    )


def build_correction_intent(
    observed,
    generation,
    recovery_epoch,
):
    intent = {
        "version": VERSION,
        "kind": "LEVERAGE_CORRECTION_INTENT",

        "symbol": SYMBOL,

        "target_margin_type":
            TARGET_MARGIN_TYPE,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "observed_snapshot_hash":
            observed[
                "snapshot_hash"
            ],

        "observed_margin_type":
            observed[
                "margin_type"
            ],

        "observed_long_leverage":
            observed[
                "isolated_long_leverage"
            ],

        "observed_short_leverage":
            observed[
                "isolated_short_leverage"
            ],

        "correction_required":
            correction_required(
                observed
            ),

        "generation":
            generation,

        "recovery_epoch":
            recovery_epoch,

        "synthetic_only":
            True,

        "network_write_permitted":
            False,

        "real_execution_permitted":
            False,

        "leverage_mutation_permitted":
            False,
    }

    intent[
        "intent_hash"
    ] = hash_object(
        intent
    )

    return intent


def build_proposed_payload():
    """
    This payload is constructed for validation only.

    R34B NEVER SENDS IT.
    """

    payload = {
        "leverage": str(
            TARGET_LONG_LEVERAGE
        ),

        "marginMode":
            TARGET_MARGIN_TYPE,

        "symbol":
            SYMBOL,
    }

    return {
        "payload": payload,
        "payload_hash": hash_object(
            payload
        ),
    }


def issue_synthetic_authorization(
    intent,
    payload_hash,
    observed,
    generation,
    recovery_epoch,
):
    authorization = {
        "kind":
            "SYNTHETIC_LEVERAGE_AUTHORIZATION",

        "symbol":
            SYMBOL,

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "payload_hash":
            payload_hash,

        "observed_snapshot_hash":
            observed[
                "snapshot_hash"
            ],

        "generation":
            generation,

        "recovery_epoch":
            recovery_epoch,

        "synthetic":
            True,

        "network_write_permitted":
            False,

        "real_execution_permitted":
            False,

        "leverage_mutation_permitted":
            False,

        "consumed":
            False,
    }

    authorization[
        "authorization_hash"
    ] = hash_object(
        authorization
    )

    return authorization


def build_transport_envelope(
    intent,
    authorization,
    payload_data,
    observed,
):
    envelope = {
        "kind":
            "SYNTHETIC_TRANSPORT_ENVELOPE",

        "transport":
            "SYNTHETIC",

        "method":
            "POST",

        "path":
            LEVERAGE_ENDPOINT,

        "payload":
            payload_data[
                "payload"
            ],

        "payload_hash":
            payload_data[
                "payload_hash"
            ],

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "authorization_hash":
            authorization[
                "authorization_hash"
            ],

        "observed_snapshot_hash":
            observed[
                "snapshot_hash"
            ],

        "network_transmitted":
            False,

        "exchange_contacted":
            False,

        "real_post":
            False,

        "leverage_mutated":
            False,
    }

    envelope[
        "envelope_hash"
    ] = hash_object(
        envelope
    )

    return envelope


def synthetic_dispatch(
    state,
    observed,
    intent,
    authorization,
    envelope,
):
    if state.get(
        "dispatch_committed",
        False,
    ):

        COUNTERS[
            "duplicate_dispatch_blocks"
        ] += 1

        raise RuntimeError(
            "Duplicate synthetic dispatch rejected."
        )

    if authorization.get(
        "consumed",
        False,
    ):
        COUNTERS[
            "duplicate_dispatch_blocks"
        ] += 1

        raise RuntimeError(
            "Authorization has already been consumed."
        )

    if authorization[
        "network_write_permitted"
    ]:
        raise RuntimeError(
            "Unsafe authorization."
        )

    if authorization[
        "leverage_mutation_permitted"
    ]:
        raise RuntimeError(
            "Unsafe leverage authorization."
        )

    if envelope[
        "transport"
    ] != "SYNTHETIC":
        raise RuntimeError(
            "Non-synthetic transport rejected."
        )

    if envelope[
        "network_transmitted"
    ]:
        raise RuntimeError(
            "Network transmission rejected."
        )

    COUNTERS[
        "synthetic_dispatches"
    ] += 1

    authorization[
        "consumed"
    ] = True

    state[
        "dispatch_committed"
    ] = True

    state[
        "authorization_consumed"
    ] = True

    state[
        "synthetic_dispatch_completed"
    ] = True

    receipt = {
        "kind":
            "R34B_SYNTHETIC_READINESS_RECEIPT",

        "transport":
            "SYNTHETIC",

        "symbol":
            SYMBOL,

        "target_margin_type":
            TARGET_MARGIN_TYPE,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "observed_margin_type":
            observed[
                "margin_type"
            ],

        "observed_long_leverage":
            observed[
                "isolated_long_leverage"
            ],

        "observed_short_leverage":
            observed[
                "isolated_short_leverage"
            ],

        "correction_required":
            correction_required(
                observed
            ),

        "observed_snapshot_hash":
            observed[
                "snapshot_hash"
            ],

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "authorization_hash":
            authorization[
                "authorization_hash"
            ],

        "envelope_hash":
            envelope[
                "envelope_hash"
            ],

        "authorization_consumed":
            True,

        "dispatch_committed":
            True,

        "network_transmitted":
            False,

        "exchange_contacted_for_mutation":
            False,

        "real_order_sent":
            False,

        "real_post_sent":
            False,

        "leverage_mutated":
            False,
    }

    receipt[
        "receipt_hash"
    ] = hash_object(
        receipt
    )

    return receipt


# =============================================================================
# HEALTH SERVER
# =============================================================================

RUNTIME_STATUS = {
    "version": VERSION,
    "phase": "BOOTING",
    "synthetic_only": True,
    "read_only_network": True,
    "correction_required": None,
    "observed_long": None,
    "observed_short": None,
    "target_long": TARGET_LONG_LEVERAGE,
    "target_short": TARGET_SHORT_LEVERAGE,
}


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        body = json.dumps(
            RUNTIME_STATUS,
            sort_keys=True,
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

        self.wfile.write(body)

    def log_message(
        self,
        format,
        *args,
    ):
        return


def health_server():
    try:

        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        log(
            f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}"
        )

        server.serve_forever()

    except Exception as error:

        log(
            f"{VERSION}: HEALTH SERVER ERROR: {error}"
        )


# =============================================================================
# PART 4
# VALIDATION
# =============================================================================

def main():
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
        f"{VERSION}: STATE FILE={STATE_FILE}"
    )

    log(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GET ENABLED"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: REAL POST DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )

    log(
        f"{VERSION}: TARGET LONG={TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"{VERSION}: TARGET SHORT={TARGET_SHORT_LEVERAGE}x"
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 1: SAFETY CONFIGURATION"
    )
    # -------------------------------------------------------------------------

    check(
        "Synthetic Only Is Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Authenticated GET Is Enabled",
        AUTHENTICATED_GET_ENABLED is True,
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
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Real POST Is Disabled",
        REAL_POST_ENABLED is False,
    )

    check(
        "Authenticated POST Is Disabled",
        AUTHENTICATED_POST_ENABLED is False,
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


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 2: TARGET CONFIGURATION"
    )
    # -------------------------------------------------------------------------

    check(
        "Symbol Is BTCUSDT",
        SYMBOL == "BTCUSDT",
    )

    check(
        "Target Margin Type Is ISOLATED",
        TARGET_MARGIN_TYPE == "ISOLATED",
    )

    check(
        "Long Target Is 100x",
        TARGET_LONG_LEVERAGE == 100,
    )

    check(
        "Short Target Is 100x",
        TARGET_SHORT_LEVERAGE == 100,
    )

    check(
        "Read Endpoint Is Exact",
        SYMBOL_CONFIG_PATH
        == "/capi/v3/account/symbolConfig",
    )

    check(
        "Proposed Leverage Endpoint Is Preserved",
        LEVERAGE_ENDPOINT
        == "/capi/v2/account/leverage",
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 3: CREDENTIAL READINESS"
    )
    # -------------------------------------------------------------------------

    check(
        "API Key Is Present",
        bool(API_KEY),
    )

    check(
        "Secret Key Is Present",
        bool(SECRET_KEY),
    )

    check(
        "Passphrase Is Present",
        bool(PASSPHRASE),
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 4: WRITE FIREBREAKS"
    )
    # -------------------------------------------------------------------------

    check(
        "Network Write Firebreak Rejects Call",
        firebreak_rejects(
            real_network_write_firebreak
        ),
    )

    check(
        "Authenticated POST Firebreak Rejects Call",
        firebreak_rejects(
            authenticated_post_firebreak
        ),
    )

    check(
        "Real Order Firebreak Rejects Call",
        firebreak_rejects(
            real_order_firebreak
        ),
    )

    check(
        "Demo Order Firebreak Rejects Call",
        firebreak_rejects(
            demo_order_firebreak
        ),
    )

    check(
        "Leverage Mutation Firebreak Rejects Call",
        firebreak_rejects(
            leverage_mutation_firebreak
        ),
    )

    check(
        "Margin Mutation Firebreak Rejects Call",
        firebreak_rejects(
            margin_mutation_firebreak
        ),
    )

    check(
        "Position Mutation Firebreak Rejects Call",
        firebreak_rejects(
            position_mutation_firebreak
        ),
    )

    check(
        "Account Mutation Firebreak Rejects Call",
        firebreak_rejects(
            account_mutation_firebreak
        ),
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 5: AUTHENTICATED READ-ONLY RECONCILIATION"
    )
    # -------------------------------------------------------------------------

    read_result = authenticated_read_only_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    check(
        "Authenticated Symbol Config GET Succeeded",
        read_result.get(
            "ok"
        ) is True,
    )

    check(
        "Authenticated Transport Method Is GET",
        read_result.get(
            "method"
        ) == "GET",
    )

    check(
        "Authenticated Read Path Is Exact",
        read_result.get(
            "request_path"
        ) == SYMBOL_CONFIG_PATH,
    )

    check(
        "Authenticated Query Contains BTCUSDT",
        "symbol=BTCUSDT"
        in read_result.get(
            "query_string",
            "",
        ),
    )

    if not read_result.get(
        "ok"
    ):

        log(LINE)
        log(
            f"{VERSION}: AUTHENTICATED READ FAILED"
        )
        log(
            f"{VERSION}: HTTP STATUS={read_result.get('status_code')}"
        )
        log(
            f"{VERSION}: ERROR={read_result.get('error')}"
        )
        log(LINE)

        RUNTIME_STATUS[
            "phase"
        ] = "READ_ONLY_RECONCILIATION_FAILED"

        show_summary()

        heartbeat_loop()

        return


    symbol_config = unwrap_symbol_configuration(
        read_result[
            "data"
        ]
    )

    check(
        "Symbol Configuration Was Returned",
        symbol_config is not None,
    )

    if symbol_config is None:

        RUNTIME_STATUS[
            "phase"
        ] = "READ_ONLY_RECONCILIATION_FAILED"

        show_summary()

        heartbeat_loop()

        return


    observed = build_observed_snapshot(
        symbol_config
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 6: OBSERVED ACCOUNT STATE"
    )
    # -------------------------------------------------------------------------

    log(
        f"{VERSION}: OBSERVED SYMBOL={observed['symbol']}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN TYPE={observed['margin_type']}"
    )

    log(
        f"{VERSION}: OBSERVED POSITION MODE={observed['position_mode']}"
    )

    log(
        f"{VERSION}: OBSERVED CROSS LEVERAGE={observed['cross_leverage']}x"
    )

    log(
        f"{VERSION}: OBSERVED LONG LEVERAGE={observed['isolated_long_leverage']}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT LEVERAGE={observed['isolated_short_leverage']}x"
    )

    check(
        "Observed Symbol Matches BTCUSDT",
        observed[
            "symbol"
        ] == SYMBOL,
    )

    check(
        "Observed Margin Type Exists",
        bool(
            observed[
                "margin_type"
            ]
        ),
    )

    check(
        "Observed Long Leverage Exists",
        observed[
            "isolated_long_leverage"
        ] is not None,
    )

    check(
        "Observed Short Leverage Exists",
        observed[
            "isolated_short_leverage"
        ] is not None,
    )

    check(
        "Observed Snapshot Hash Exists",
        bool(
            observed[
                "snapshot_hash"
            ]
        ),
    )


    requires_correction = correction_required(
        observed
    )

    log(
        f"{VERSION}: CORRECTION REQUIRED={requires_correction}"
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 7: LIVE-READINESS DECISION"
    )
    # -------------------------------------------------------------------------

    long_needs_correction = (
        observed[
            "isolated_long_leverage"
        ]
        != TARGET_LONG_LEVERAGE
    )

    short_needs_correction = (
        observed[
            "isolated_short_leverage"
        ]
        != TARGET_SHORT_LEVERAGE
    )

    margin_needs_correction = (
        observed[
            "margin_type"
        ]
        != TARGET_MARGIN_TYPE
    )

    check(
        "Correction Decision Is Boolean",
        isinstance(
            requires_correction,
            bool,
        ),
    )

    check(
        "Long Comparison Completed",
        isinstance(
            long_needs_correction,
            bool,
        ),
    )

    check(
        "Short Comparison Completed",
        isinstance(
            short_needs_correction,
            bool,
        ),
    )

    check(
        "Margin Comparison Completed",
        isinstance(
            margin_needs_correction,
            bool,
        ),
    )

    log(
        f"{VERSION}: LONG CORRECTION REQUIRED={long_needs_correction}"
    )

    log(
        f"{VERSION}: SHORT CORRECTION REQUIRED={short_needs_correction}"
    )

    log(
        f"{VERSION}: MARGIN CORRECTION REQUIRED={margin_needs_correction}"
    )


    # -------------------------------------------------------------------------
    # Fresh R34B generation intentionally starts a new stage lineage.
    # -------------------------------------------------------------------------

    generation = 1
    recovery_epoch = 1

    state = {
        "version": VERSION,

        "phase":
            "LIVE_STATE_RECONCILED",

        "symbol":
            SYMBOL,

        "generation":
            generation,

        "recovery_epoch":
            recovery_epoch,

        "synthetic_only":
            True,

        "authenticated_read_only":
            True,

        "network_writes_enabled":
            False,

        "real_execution_enabled":
            False,

        "leverage_mutation_enabled":
            False,

        "correction_required":
            requires_correction,

        "dispatch_committed":
            False,

        "authorization_consumed":
            False,

        "synthetic_dispatch_completed":
            False,
    }


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 8: OBSERVED-STATE-BOUND CORRECTION INTENT"
    )
    # -------------------------------------------------------------------------

    intent = build_correction_intent(
        observed=observed,
        generation=generation,
        recovery_epoch=recovery_epoch,
    )

    check(
        "Intent Symbol Matches",
        intent[
            "symbol"
        ] == SYMBOL,
    )

    check(
        "Intent Binds Observed Snapshot",
        intent[
            "observed_snapshot_hash"
        ]
        == observed[
            "snapshot_hash"
        ],
    )

    check(
        "Intent Observed Long Matches",
        intent[
            "observed_long_leverage"
        ]
        == observed[
            "isolated_long_leverage"
        ],
    )

    check(
        "Intent Observed Short Matches",
        intent[
            "observed_short_leverage"
        ]
        == observed[
            "isolated_short_leverage"
        ],
    )

    check(
        "Intent Long Target Is 100x",
        intent[
            "target_long_leverage"
        ] == 100,
    )

    check(
        "Intent Short Target Is 100x",
        intent[
            "target_short_leverage"
        ] == 100,
    )

    check(
        "Intent Is Synthetic Only",
        intent[
            "synthetic_only"
        ] is True,
    )

    check(
        "Intent Forbids Network Write",
        intent[
            "network_write_permitted"
        ] is False,
    )

    check(
        "Intent Forbids Real Execution",
        intent[
            "real_execution_permitted"
        ] is False,
    )

    check(
        "Intent Forbids Leverage Mutation",
        intent[
            "leverage_mutation_permitted"
        ] is False,
    )

    check(
        "Intent Hash Exists",
        bool(
            intent[
                "intent_hash"
            ]
        ),
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 9: PROPOSED EXACT PAYLOAD"
    )
    # -------------------------------------------------------------------------

    payload_data = build_proposed_payload()

    payload = payload_data[
        "payload"
    ]

    check(
        "Payload Symbol Matches",
        payload[
            "symbol"
        ] == SYMBOL,
    )

    check(
        "Payload Margin Mode Is ISOLATED",
        payload[
            "marginMode"
        ] == "ISOLATED",
    )

    check(
        "Payload Leverage Is 100",
        payload[
            "leverage"
        ] == "100",
    )

    check(
        "Payload Hash Exists",
        bool(
            payload_data[
                "payload_hash"
            ]
        ),
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 10: SYNTHETIC AUTHORIZATION"
    )
    # -------------------------------------------------------------------------

    authorization = issue_synthetic_authorization(
        intent=intent,
        payload_hash=payload_data[
            "payload_hash"
        ],
        observed=observed,
        generation=generation,
        recovery_epoch=recovery_epoch,
    )

    check(
        "Authorization Binds Intent",
        authorization[
            "intent_hash"
        ]
        == intent[
            "intent_hash"
        ],
    )

    check(
        "Authorization Binds Payload",
        authorization[
            "payload_hash"
        ]
        == payload_data[
            "payload_hash"
        ],
    )

    check(
        "Authorization Binds Observed Snapshot",
        authorization[
            "observed_snapshot_hash"
        ]
        == observed[
            "snapshot_hash"
        ],
    )

    check(
        "Authorization Is Synthetic",
        authorization[
            "synthetic"
        ] is True,
    )

    check(
        "Authorization Forbids Network Write",
        authorization[
            "network_write_permitted"
        ] is False,
    )

    check(
        "Authorization Forbids Real Execution",
        authorization[
            "real_execution_permitted"
        ] is False,
    )

    check(
        "Authorization Forbids Leverage Mutation",
        authorization[
            "leverage_mutation_permitted"
        ] is False,
    )

    check(
        "Authorization Initially Unconsumed",
        authorization[
            "consumed"
        ] is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 11: SYNTHETIC TRANSPORT ENVELOPE"
    )
    # -------------------------------------------------------------------------

    envelope = build_transport_envelope(
        intent=intent,
        authorization=authorization,
        payload_data=payload_data,
        observed=observed,
    )

    check(
        "Envelope Transport Is Synthetic",
        envelope[
            "transport"
        ] == "SYNTHETIC",
    )

    check(
        "Envelope Method Is POST",
        envelope[
            "method"
        ] == "POST",
    )

    check(
        "Envelope Path Is Exact",
        envelope[
            "path"
        ] == LEVERAGE_ENDPOINT,
    )

    check(
        "Envelope Contains Exact Payload",
        envelope[
            "payload"
        ] == payload,
    )

    check(
        "Envelope Binds Observed Snapshot",
        envelope[
            "observed_snapshot_hash"
        ]
        == observed[
            "snapshot_hash"
        ],
    )

    check(
        "Envelope Confirms No Transmission",
        envelope[
            "network_transmitted"
        ] is False,
    )

    check(
        "Envelope Confirms Exchange Not Contacted For Mutation",
        envelope[
            "exchange_contacted"
        ] is False,
    )

    check(
        "Envelope Confirms No Real POST",
        envelope[
            "real_post"
        ] is False,
    )

    check(
        "Envelope Confirms No Leverage Mutation",
        envelope[
            "leverage_mutated"
        ] is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 12: SYNTHETIC READINESS DISPATCH"
    )
    # -------------------------------------------------------------------------

    receipt = synthetic_dispatch(
        state=state,
        observed=observed,
        intent=intent,
        authorization=authorization,
        envelope=envelope,
    )

    check(
        "Synthetic Dispatch Completed",
        state[
            "synthetic_dispatch_completed"
        ] is True,
    )

    check(
        "Synthetic Dispatch Counter Is One",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    check(
        "Authorization Was Consumed",
        authorization[
            "consumed"
        ] is True,
    )

    check(
        "Dispatch Was Committed",
        state[
            "dispatch_committed"
        ] is True,
    )

    check(
        "Receipt Transport Is Synthetic",
        receipt[
            "transport"
        ] == "SYNTHETIC",
    )

    check(
        "Receipt Binds Observed Snapshot",
        receipt[
            "observed_snapshot_hash"
        ]
        == observed[
            "snapshot_hash"
        ],
    )

    check(
        "Receipt Confirms No Network Transmission",
        receipt[
            "network_transmitted"
        ] is False,
    )

    check(
        "Receipt Confirms No Real Order",
        receipt[
            "real_order_sent"
        ] is False,
    )

    check(
        "Receipt Confirms No Real POST",
        receipt[
            "real_post_sent"
        ] is False,
    )

    check(
        "Receipt Confirms No Leverage Mutation",
        receipt[
            "leverage_mutated"
        ] is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 13: DUPLICATE DISPATCH REJECTION"
    )
    # -------------------------------------------------------------------------

    duplicate_rejected = False

    try:

        synthetic_dispatch(
            state=state,
            observed=observed,
            intent=intent,
            authorization=authorization,
            envelope=envelope,
        )

    except RuntimeError:
        duplicate_rejected = True

    check(
        "Duplicate Synthetic Dispatch Is Rejected",
        duplicate_rejected,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    check(
        "Duplicate Dispatch Block Counter Is One",
        COUNTERS[
            "duplicate_dispatch_blocks"
        ] == 1,
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 14: DURABLE LIVE-READINESS SNAPSHOT"
    )
    # -------------------------------------------------------------------------

    state[
        "phase"
    ] = "LIVE_READ_ONLY_VALIDATED"

    state[
        "observed"
    ] = observed

    state[
        "intent"
    ] = intent

    state[
        "payload"
    ] = payload_data

    state[
        "authorization"
    ] = authorization

    state[
        "envelope"
    ] = envelope

    state[
        "receipt"
    ] = receipt

    state[
        "counters"
    ] = dict(
        COUNTERS
    )

    state[
        "snapshot_hash"
    ] = hash_object(
        {
            "observed_hash":
                observed[
                    "snapshot_hash"
                ],

            "intent_hash":
                intent[
                    "intent_hash"
                ],

            "payload_hash":
                payload_data[
                    "payload_hash"
                ],

            "authorization_hash":
                authorization[
                    "authorization_hash"
                ],

            "envelope_hash":
                envelope[
                    "envelope_hash"
                ],

            "receipt_hash":
                receipt[
                    "receipt_hash"
                ],

            "generation":
                generation,

            "recovery_epoch":
                recovery_epoch,
        }
    )

    atomic_write_json(
        STATE_FILE,
        state,
    )

    restored = load_json(
        STATE_FILE
    )

    check(
        "State File Restores",
        restored is not None,
    )

    check(
        "Restored Phase Is Live Read-Only Validated",
        restored is not None
        and restored.get(
            "phase"
        ) == "LIVE_READ_ONLY_VALIDATED",
    )

    check(
        "Restored Observed Snapshot Hash Matches",
        restored is not None
        and restored[
            "observed"
        ][
            "snapshot_hash"
        ]
        == observed[
            "snapshot_hash"
        ],
    )

    check(
        "Restored Intent Hash Matches",
        restored is not None
        and restored[
            "intent"
        ][
            "intent_hash"
        ]
        == intent[
            "intent_hash"
        ],
    )

    check(
        "Restored Payload Hash Matches",
        restored is not None
        and restored[
            "payload"
        ][
            "payload_hash"
        ]
        == payload_data[
            "payload_hash"
        ],
    )

    check(
        "Restored Authorization Hash Matches",
        restored is not None
        and restored[
            "authorization"
        ][
            "authorization_hash"
        ]
        == authorization[
            "authorization_hash"
        ],
    )

    check(
        "Restored Envelope Hash Matches",
        restored is not None
        and restored[
            "envelope"
        ][
            "envelope_hash"
        ]
        == envelope[
            "envelope_hash"
        ],
    )

    check(
        "Restored Receipt Hash Matches",
        restored is not None
        and restored[
            "receipt"
        ][
            "receipt_hash"
        ]
        == receipt[
            "receipt_hash"
        ],
    )

    check(
        "Restored Authorization Is Consumed",
        restored is not None
        and restored[
            "authorization_consumed"
        ] is True,
    )

    check(
        "Restored Dispatch Is Committed",
        restored is not None
        and restored[
            "dispatch_committed"
        ] is True,
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 15: TERMINAL SAFETY COUNTERS"
    )
    # -------------------------------------------------------------------------

    check(
        "Exactly One Authenticated GET Occurred",
        COUNTERS[
            "authenticated_gets"
        ] == 1,
    )

    check(
        "Exactly One Synthetic Dispatch Occurred",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    check(
        "Zero Real Orders Occurred",
        COUNTERS[
            "real_orders"
        ] == 0,
    )

    check(
        "Zero Demo Orders Occurred",
        COUNTERS[
            "demo_orders"
        ] == 0,
    )

    check(
        "Zero Network Writes Occurred",
        COUNTERS[
            "network_writes"
        ] == 0,
    )

    check(
        "Zero Real POSTs Occurred",
        COUNTERS[
            "real_posts"
        ] == 0,
    )

    check(
        "Zero Leverage Mutations Occurred",
        COUNTERS[
            "leverage_mutations"
        ] == 0,
    )

    check(
        "Zero Margin Mutations Occurred",
        COUNTERS[
            "margin_mutations"
        ] == 0,
    )

    check(
        "Zero Position Mutations Occurred",
        COUNTERS[
            "position_mutations"
        ] == 0,
    )

    check(
        "Zero Account Mutations Occurred",
        COUNTERS[
            "account_mutations"
        ] == 0,
    )


    # -------------------------------------------------------------------------
    section(
        "R34B TEST 16: TERMINAL LIVE-READINESS STATE"
    )
    # -------------------------------------------------------------------------

    check(
        "Terminal Phase Is Live Read-Only Validated",
        state[
            "phase"
        ] == "LIVE_READ_ONLY_VALIDATED",
    )

    check(
        "Terminal State Remains Synthetic Only",
        state[
            "synthetic_only"
        ] is True,
    )

    check(
        "Terminal State Is Authenticated Read-Only",
        state[
            "authenticated_read_only"
        ] is True,
    )

    check(
        "Terminal State Has No Real Execution",
        state[
            "real_execution_enabled"
        ] is False,
    )

    check(
        "Terminal State Has No Network Writes",
        state[
            "network_writes_enabled"
        ] is False,
    )

    check(
        "Terminal State Has No Leverage Mutation",
        state[
            "leverage_mutation_enabled"
        ] is False,
    )


    RUNTIME_STATUS[
        "phase"
    ] = "LIVE_READ_ONLY_VALIDATED"

    RUNTIME_STATUS[
        "correction_required"
    ] = requires_correction

    RUNTIME_STATUS[
        "observed_long"
    ] = observed[
        "isolated_long_leverage"
    ]

    RUNTIME_STATUS[
        "observed_short"
    ] = observed[
        "isolated_short_leverage"
    ]


    show_summary(
        observed=observed,
        requires_correction=requires_correction,
    )

    heartbeat_loop(
        observed=observed,
        requires_correction=requires_correction,
    )


# =============================================================================
# SUMMARY
# =============================================================================

def show_summary(
    observed=None,
    requires_correction=None,
):
    section(
        "R34B VALIDATION SUMMARY"
    )

    log(
        f"Total Checks: {TOTAL_CHECKS}"
    )

    log(
        f"Passed:       {PASSED_CHECKS}"
    )

    log(
        f"Failed:       {FAILED_CHECKS}"
    )

    log(LINE)

    if (
        FAILED_CHECKS == 0
        and observed is not None
    ):

        log(
            "R34B VALIDATION: ✅ PASSED"
        )

        log(
            "R34B: AUTHENTICATED READ-ONLY LIVE ACCOUNT RECONCILIATION VALIDATED"
        )

        log(
            f"R34B: OBSERVED MARGIN TYPE={observed['margin_type']}"
        )

        log(
            f"R34B: OBSERVED LONG={observed['isolated_long_leverage']}x"
        )

        log(
            f"R34B: OBSERVED SHORT={observed['isolated_short_leverage']}x"
        )

        log(
            f"R34B: TARGET LONG={TARGET_LONG_LEVERAGE}x"
        )

        log(
            f"R34B: TARGET SHORT={TARGET_SHORT_LEVERAGE}x"
        )

        log(
            f"R34B: CORRECTION REQUIRED={requires_correction}"
        )

        if requires_correction:

            log(
                "R34B: LIVE ACCOUNT DOES NOT YET MATCH 100x TARGET"
            )

        else:

            log(
                "R34B: LIVE ACCOUNT ALREADY MATCHES TARGET"
            )

    else:

        log(
            "R34B VALIDATION: ❌ NOT PASSED"
        )

    log(
        "R34B: AUTHENTICATED GET WAS READ-ONLY"
    )

    log(
        "R34B: NO REAL ORDER WAS SENT"
    )

    log(
        "R34B: NO DEMO ORDER WAS SENT"
    )

    log(
        "R34B: NO NETWORK WRITE OCCURRED"
    )

    log(
        "R34B: NO REAL POST OCCURRED"
    )

    log(
        "R34B: NO LEVERAGE MUTATION OCCURRED"
    )

    log(LINE)


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop(
    observed=None,
    requires_correction=None,
):
    heartbeat = 0

    while True:

        time.sleep(30)

        heartbeat += 1

        if observed is None:

            observed_long = "unknown"
            observed_short = "unknown"
            observed_margin = "unknown"

        else:

            observed_long = (
                observed[
                    "isolated_long_leverage"
                ]
            )

            observed_short = (
                observed[
                    "isolated_short_leverage"
                ]
            )

            observed_margin = (
                observed[
                    "margin_type"
                ]
            )

        log(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"phase={RUNTIME_STATUS['phase']} | "
            f"synthetic-only={SYNTHETIC_ONLY} | "
            f"authenticated-read-only=True | "
            f"authenticated-get={COUNTERS['authenticated_gets']} | "
            f"synthetic-dispatch={COUNTERS['synthetic_dispatches']} | "
            f"real-execution={REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes={EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"correction-required={requires_correction} | "
            f"observed-margin={observed_margin} | "
            f"observed-long={observed_long}x | "
            f"observed-short={observed_short}x | "
            f"target-long={TARGET_LONG_LEVERAGE}x | "
            f"target-short={TARGET_SHORT_LEVERAGE}x"
        )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    health_thread = threading.Thread(
        target=health_server,
        daemon=True,
    )

    health_thread.start()

    try:

        main()

    except KeyboardInterrupt:

        log(
            f"{VERSION}: SHUTDOWN REQUESTED"
        )

        sys.exit(0)

    except Exception as error:

        log(LINE)

        log(
            f"{VERSION}: FATAL ERROR"
        )

        log(
            f"{VERSION}: {type(error).__name__}: {error}"
        )

        traceback.print_exc()

        log(LINE)

        RUNTIME_STATUS[
            "phase"
        ] = "FATAL_ERROR"

        # Keep Render service alive for diagnostics.
        while True:

            time.sleep(30)

            log(
                f"{VERSION}: HEARTBEAT | "
                f"phase=FATAL_ERROR | "
                f"real-execution=False | "
                f"network-writes=False | "
                f"leverage-mutation=False"
            )
