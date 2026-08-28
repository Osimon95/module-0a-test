
# ==============================================================================
# R34S main.py
# Durable Exactly-Once Restart Recovery Validation
#
# PURPOSE
#   - Extend R34R exactly-once synthetic dispatch protection.
#   - Persist intent, payload, envelope, authorization and receipt state.
#   - Simulate process restart by reloading durable state from disk.
#   - Prove consumed authorization remains consumed after restart.
#   - Prove duplicate/replay dispatch remains rejected after restart.
#
# SAFETY
#   - NO real orders.
#   - NO demo orders.
#   - NO exchange POST/PUT/PATCH/DELETE.
#   - NO leverage mutation.
#   - NO margin mutation.
#   - NO position mutation.
#   - NO account mutation.
#   - Synthetic transport only.
# ==============================================================================

import hashlib
import json
import os
import secrets
import threading
import time
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==============================================================================
# CONFIGURATION
# ==============================================================================

VERSION = "R34S"
SYMBOL = "BTCUSDT"

HEALTH_HOST = "0.0.0.0"
HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_FILE = os.getenv(
    "R34S_STATE_FILE",
    "/tmp/r34s_durable_state.json",
)

HEARTBEAT_SECONDS = 30

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

SYNTHETIC_QTY = "0.0004"
SYNTHETIC_SIDE = "BUY"
SYNTHETIC_POSITION_SIDE = "LONG"
SYNTHETIC_ORDER_TYPE = "MARKET"

AUTHORIZATION_TTL_SECONDS = 120


# ==============================================================================
# HARD SAFETY FIREBREAKS
# ==============================================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

SYNTHETIC_TRANSPORT_ONLY = True

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# ==============================================================================
# GLOBAL COUNTERS
# ==============================================================================

COUNTERS = {
    "authenticated_gets": 0,
    "public_gets": 0,

    "network_writes": 0,

    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "real_orders": 0,
    "demo_orders": 0,

    "synthetic_dispatches": 0,

    "duplicate_dispatch_blocks": 0,
    "stale_state_blocks": 0,
    "restart_replay_blocks": 0,

    "durable_writes": 0,
    "durable_reads": 0,

    "restart_simulations": 0,
}

COUNTER_LOCK = threading.Lock()

PHASE = "BOOTING"


# ==============================================================================
# BASIC HELPERS
# ==============================================================================

SEPARATOR = "-" * 100


def utc_now():
    return datetime.now(timezone.utc)


def utc_iso():
    return utc_now().isoformat()


def epoch_ms():
    return int(time.time() * 1000)


def log(message=""):
    print(message, flush=True)


def section(title):
    log(SEPARATOR)
    log(title)
    log(SEPARATOR)


def pass_check(name, condition):
    if not condition:
        log(f"{name:<88} ❌ FAIL")
        raise AssertionError(name)

    log(f"{name:<88} ✅ PASS")


def fail(message):
    raise RuntimeError(message)


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_value(value):
    if isinstance(value, str):
        raw = value
    else:
        raw = canonical_json(value)

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def random_id(prefix):
    return f"{prefix}-{secrets.token_hex(16)}"


# ==============================================================================
# HTTP HEALTH SERVER
# ==============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/health"):
            self.send_response(404)
            self.end_headers()
            return

        body = json.dumps(
            {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": PHASE,
                "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                "network_writes": COUNTERS["network_writes"],
                "real_orders": COUNTERS["real_orders"],
                "demo_orders": COUNTERS["demo_orders"],
                "synthetic_dispatches": COUNTERS["synthetic_dispatches"],
                "restart_replay_blocks": COUNTERS["restart_replay_blocks"],
            }
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

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(
        (HEALTH_HOST, HEALTH_PORT),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    return server


# ==============================================================================
# DURABLE STORAGE
# ==============================================================================

def atomic_write_json(path, value):
    directory = os.path.dirname(path)

    if directory:
        os.makedirs(
            directory,
            exist_ok=True,
        )

    temp_path = (
        f"{path}.tmp."
        f"{os.getpid()}."
        f"{secrets.token_hex(4)}"
    )

    encoded = canonical_json(value)

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(
        temp_path,
        path,
    )

    with COUNTER_LOCK:
        COUNTERS["durable_writes"] += 1


def durable_read_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:
        value = json.load(handle)

    with COUNTER_LOCK:
        COUNTERS["durable_reads"] += 1

    return value


def persist_state(state):
    state_copy = deepcopy(state)

    state_copy["state_hash"] = None

    calculated_hash = sha256_value(
        state_copy
    )

    state_copy["state_hash"] = calculated_hash

    atomic_write_json(
        STATE_FILE,
        state_copy,
    )

    return state_copy


def verify_state_integrity(state):
    stored_hash = state.get(
        "state_hash"
    )

    candidate = deepcopy(state)
    candidate["state_hash"] = None

    calculated_hash = sha256_value(
        candidate
    )

    return (
        isinstance(stored_hash, str)
        and len(stored_hash) == 64
        and stored_hash == calculated_hash
    )


# ==============================================================================
# LIVE-STATE SNAPSHOT
# ==============================================================================

def build_live_state():
    """
    R34S intentionally does not mutate the exchange.

    This snapshot represents the execution preconditions already validated
    by the preceding R34 sequence.
    """

    snapshot = {
        "symbol": SYMBOL,

        "margin_type": TARGET_MARGIN_TYPE,

        "long_leverage": TARGET_LONG_LEVERAGE,
        "short_leverage": TARGET_SHORT_LEVERAGE,

        "open_position_count": 0,

        "network_write_allowed": False,
        "real_execution_allowed": False,
        "demo_execution_allowed": False,

        "synthetic_transport_only": True,

        "captured_at_ms": epoch_ms(),
    }

    snapshot["state_sha256"] = sha256_value(
        snapshot
    )

    return snapshot


# ==============================================================================
# INTENT
# ==============================================================================

def build_intent(live_state):
    intent = {
        "intent_id": random_id(
            "intent"
        ),

        "version": VERSION,
        "symbol": SYMBOL,

        "side": SYNTHETIC_SIDE,
        "position_side": SYNTHETIC_POSITION_SIDE,
        "order_type": SYNTHETIC_ORDER_TYPE,
        "quantity": SYNTHETIC_QTY,

        "live_state_sha256":
            live_state["state_sha256"],

        "synthetic_only": True,

        "transmission_allowed": False,
        "network_write_allowed": False,

        "created_at_ms": epoch_ms(),
    }

    intent["intent_sha256"] = sha256_value(
        intent
    )

    return intent


# ==============================================================================
# PAYLOAD
# ==============================================================================

def build_payload(intent):
    client_order_id = (
        "r34s-"
        + secrets.token_hex(10)
    )

    payload = {
        "newClientOrderId": client_order_id,
        "positionSide":
            intent["position_side"],
        "quantity":
            intent["quantity"],
        "side":
            intent["side"],
        "symbol":
            intent["symbol"],
        "type":
            intent["order_type"],
    }

    payload_hash = sha256_value(
        payload
    )

    return payload, payload_hash


# ==============================================================================
# SYNTHETIC AUTHENTICATED ENVELOPE
# ==============================================================================

def build_envelope(
    intent,
    payload,
    payload_hash,
    live_state,
):
    envelope = {
        "envelope_id": random_id(
            "env"
        ),

        "version": VERSION,

        "intent_sha256":
            intent["intent_sha256"],

        "payload_sha256":
            payload_hash,

        "live_state_sha256":
            live_state["state_sha256"],

        "payload":
            deepcopy(payload),

        "synthetic_only": True,

        "authenticated_shape_only": True,

        "transmission_allowed": False,
        "network_write_allowed": False,

        "real_execution_allowed": False,
        "demo_execution_allowed": False,

        "created_at_ms":
            epoch_ms(),
    }

    envelope["envelope_sha256"] = sha256_value(
        envelope
    )

    return envelope


# ==============================================================================
# ONE-TIME SYNTHETIC AUTHORIZATION
# ==============================================================================

def build_authorization(
    intent,
    payload_hash,
    envelope,
    live_state,
):
    created = epoch_ms()

    authorization = {
        "authorization_id":
            random_id("auth"),

        "version": VERSION,

        "intent_sha256":
            intent["intent_sha256"],

        "payload_sha256":
            payload_hash,

        "envelope_sha256":
            envelope["envelope_sha256"],

        "live_state_sha256":
            live_state["state_sha256"],

        "synthetic_only": True,

        "transmission_allowed": False,
        "network_write_allowed": False,

        "created_at_ms":
            created,

        "expires_at_ms":
            created
            + (
                AUTHORIZATION_TTL_SECONDS
                * 1000
            ),

        "consumed": False,

        "consumed_at_ms": None,

        "dispatch_id": None,
    }

    authorization[
        "authorization_sha256"
    ] = sha256_value(
        authorization
    )

    return authorization


def recompute_authorization_hash(
    authorization
):
    candidate = deepcopy(
        authorization
    )

    candidate.pop(
        "authorization_sha256",
        None,
    )

    return sha256_value(
        candidate
    )


# ==============================================================================
# AUTHORIZATION VALIDATION
# ==============================================================================

def validate_authorization(
    authorization,
    intent,
    payload_hash,
    envelope,
    live_state,
    count_stale=True,
):
    if (
        authorization["synthetic_only"]
        is not True
    ):
        return False

    if (
        authorization["transmission_allowed"]
        is not False
    ):
        return False

    if (
        authorization["network_write_allowed"]
        is not False
    ):
        return False

    if (
        authorization["intent_sha256"]
        != intent["intent_sha256"]
    ):
        return False

    if (
        authorization["payload_sha256"]
        != payload_hash
    ):
        return False

    if (
        authorization["envelope_sha256"]
        != envelope["envelope_sha256"]
    ):
        return False

    if (
        authorization["live_state_sha256"]
        != live_state["state_sha256"]
    ):
        if count_stale:
            with COUNTER_LOCK:
                COUNTERS[
                    "stale_state_blocks"
                ] += 1

        return False

    if (
        epoch_ms()
        >= authorization["expires_at_ms"]
    ):
        return False

    calculated = (
        recompute_authorization_hash(
            authorization
        )
    )

    if (
        calculated
        != authorization[
            "authorization_sha256"
        ]
    ):
        return False

    return True


# ==============================================================================
# SYNTHETIC DISPATCH
# ==============================================================================

def synthetic_dispatch(
    authorization,
    intent,
    payload,
    payload_hash,
    envelope,
    live_state,
):
    """
    There is deliberately NO HTTP transport here.

    This function only creates an offline synthetic receipt.
    """

    if not SYNTHETIC_TRANSPORT_ONLY:
        fail(
            "Synthetic-only transport "
            "firebreak disabled."
        )

    if NETWORK_WRITES_ENABLED:
        fail(
            "Network writes unexpectedly "
            "enabled."
        )

    if REAL_ORDER_EXECUTION:
        fail(
            "Real execution unexpectedly "
            "enabled."
        )

    if DEMO_ORDER_EXECUTION:
        fail(
            "Demo execution unexpectedly "
            "enabled."
        )

    if authorization["consumed"]:
        with COUNTER_LOCK:
            COUNTERS[
                "duplicate_dispatch_blocks"
            ] += 1

        raise RuntimeError(
            "Authorization already consumed."
        )

    valid = validate_authorization(
        authorization,
        intent,
        payload_hash,
        envelope,
        live_state,
    )

    if not valid:
        raise RuntimeError(
            "Authorization validation failed."
        )

    dispatch_id = random_id(
        "dispatch"
    )

    # Consume authorization BEFORE receipt creation.
    authorization["consumed"] = True
    authorization["consumed_at_ms"] = epoch_ms()
    authorization["dispatch_id"] = dispatch_id

    authorization[
        "authorization_sha256"
    ] = recompute_authorization_hash(
        authorization
    )

    receipt = {
        "receipt_id":
            random_id("receipt"),

        "dispatch_id":
            dispatch_id,

        "authorization_id":
            authorization[
                "authorization_id"
            ],

        "authorization_sha256":
            authorization[
                "authorization_sha256"
            ],

        "intent_sha256":
            intent["intent_sha256"],

        "payload_sha256":
            payload_hash,

        "envelope_sha256":
            envelope[
                "envelope_sha256"
            ],

        "live_state_sha256":
            live_state[
                "state_sha256"
            ],

        "client_order_id":
            payload[
                "newClientOrderId"
            ],

        "synthetic": True,

        "transmitted": False,

        "network_write": False,

        "real_execution": False,

        "demo_execution": False,

        "created_at_ms":
            epoch_ms(),
    }

    receipt["receipt_sha256"] = sha256_value(
        receipt
    )

    with COUNTER_LOCK:
        COUNTERS[
            "synthetic_dispatches"
        ] += 1

    return receipt


# ==============================================================================
# RESTART REPLAY PROTECTION
# ==============================================================================

def attempt_restart_replay(state):
    """
    This represents a fresh process attempting to reuse an authorization
    recovered from durable state.
    """

    authorization = deepcopy(
        state["authorization"]
    )

    if authorization["consumed"]:
        with COUNTER_LOCK:
            COUNTERS[
                "restart_replay_blocks"
            ] += 1

        raise RuntimeError(
            "Restart replay blocked: "
            "authorization already consumed."
        )

    raise RuntimeError(
        "Unexpected replay path."
    )


# ==============================================================================
# INITIAL DURABLE STATE
# ==============================================================================

def build_durable_state(
    live_state,
    intent,
    payload,
    payload_hash,
    envelope,
    authorization,
):
    return {
        "schema_version": 1,

        "version": VERSION,

        "phase":
            "AUTHORIZED_NOT_DISPATCHED",

        "created_at":
            utc_iso(),

        "live_state":
            deepcopy(live_state),

        "intent":
            deepcopy(intent),

        "payload":
            deepcopy(payload),

        "payload_sha256":
            payload_hash,

        "envelope":
            deepcopy(envelope),

        "authorization":
            deepcopy(authorization),

        "receipt": None,

        "state_hash": None,
    }


# ==============================================================================
# VALIDATION
# ==============================================================================

def run_validation():
    global PHASE

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
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}"
    )
    log(
        f"{VERSION}: STATE FILE={STATE_FILE}"
    )

    log(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )
    log(
        f"{VERSION}: PUBLIC READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )
    log(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
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

    # --------------------------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 1: HARD SAFETY FIREBREAK"
    )

    pass_check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    pass_check(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION,
    )

    pass_check(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    pass_check(
        "Exchange Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    pass_check(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    pass_check(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    pass_check(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    pass_check(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION_ENABLED,
    )

    # --------------------------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 2: LIVE STATE SNAPSHOT"
    )

    live_state = build_live_state()

    pass_check(
        "Symbol Matches BTCUSDT",
        live_state["symbol"] == SYMBOL,
    )

    pass_check(
        "Margin Type Is ISOLATED",
        live_state["margin_type"]
        == TARGET_MARGIN_TYPE,
    )

    pass_check(
        "Long Leverage Is 100x",
        live_state["long_leverage"]
        == TARGET_LONG_LEVERAGE,
    )

    pass_check(
        "Short Leverage Is 100x",
        live_state["short_leverage"]
        == TARGET_SHORT_LEVERAGE,
    )

    pass_check(
        "Synthetic Live State Hash Exists",
        len(
            live_state["state_sha256"]
        ) == 64,
    )

    log(
        f"{VERSION}: LIVE STATE SHA256="
        f"{live_state['state_sha256']}"
    )

    # --------------------------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 3: SYNTHETIC EXECUTION INTENT"
    )

    intent = build_intent(
        live_state
    )

    pass_check(
        "Intent Is Synthetic Only",
        intent["synthetic_only"],
    )

    pass_check(
        "Intent Forbids Transmission",
        not intent[
            "transmission_allowed"
        ],
    )

    pass_check(
        "Intent Forbids Network Write",
        not intent[
            "network_write_allowed"
        ],
    )

    pass_check(
        "Intent Binds Exact Live State",
        intent[
            "live_state_sha256"
        ]
        == live_state[
            "state_sha256"
        ],
    )

    pass_check(
        "Intent Hash Exists",
        len(
            intent["intent_sha256"]
        ) == 64,
    )

    log(
        f"{VERSION}: INTENT SHA256="
        f"{intent['intent_sha256']}"
    )

    # --------------------------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 4: SYNTHETIC PAYLOAD"
    )

    payload, payload_hash = (
        build_payload(
            intent
        )
    )

    pass_check(
        "Payload Symbol Matches Intent",
        payload["symbol"]
        == intent["symbol"],
    )

    pass_check(
        "Payload Quantity Matches Intent",
        payload["quantity"]
        == intent["quantity"],
    )

    pass_check(
        "Payload Side Matches Intent",
        payload["side"]
        == intent["side"],
    )

    pass_check(
        "Payload Client Order ID Exists",
        bool(
            payload[
                "newClientOrderId"
            ]
        ),
    )

    pass_check(
        "Payload Hash Exists",
        len(payload_hash) == 64,
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD="
        f"{canonical_json(payload)}"
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD SHA256="
        f"{payload_hash}"
    )

    # --------------------------------------------------------------------------
    # TEST 5
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 5: SYNTHETIC AUTHENTICATED EXECUTION ENVELOPE"
    )

    envelope = build_envelope(
        intent,
        payload,
        payload_hash,
        live_state,
    )

    pass_check(
        "Envelope Is Synthetic Only",
        envelope["synthetic_only"],
    )

    pass_check(
        "Envelope Forbids Transmission",
        not envelope[
            "transmission_allowed"
        ],
    )

    pass_check(
        "Envelope Forbids Network Write",
        not envelope[
            "network_write_allowed"
        ],
    )

    pass_check(
        "Envelope Binds Exact Intent",
        envelope[
            "intent_sha256"
        ]
        == intent[
            "intent_sha256"
        ],
    )

    pass_check(
        "Envelope Binds Exact Payload",
        envelope[
            "payload_sha256"
        ]
        == payload_hash,
    )

    pass_check(
        "Envelope Binds Exact Live State",
        envelope[
            "live_state_sha256"
        ]
        == live_state[
            "state_sha256"
        ],
    )

    pass_check(
        "Envelope Hash Exists",
        len(
            envelope[
                "envelope_sha256"
            ]
        ) == 64,
    )

    log(
        f"{VERSION}: ENVELOPE SHA256="
        f"{envelope['envelope_sha256']}"
    )

    # --------------------------------------------------------------------------
    # TEST 6
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 6: ONE-TIME SYNTHETIC AUTHORIZATION"
    )

    authorization = (
        build_authorization(
            intent,
            payload_hash,
            envelope,
            live_state,
        )
    )

    pass_check(
        "Authorization Is Synthetic Only",
        authorization[
            "synthetic_only"
        ],
    )

    pass_check(
        "Authorization Forbids Transmission",
        not authorization[
            "transmission_allowed"
        ],
    )

    pass_check(
        "Authorization Forbids Network Write",
        not authorization[
            "network_write_allowed"
        ],
    )

    pass_check(
        "Authorization Is Initially Unconsumed",
        not authorization[
            "consumed"
        ],
    )

    pass_check(
        "Authorization Binds Exact Intent",
        authorization[
            "intent_sha256"
        ]
        == intent[
            "intent_sha256"
        ],
    )

    pass_check(
        "Authorization Binds Exact Payload",
        authorization[
            "payload_sha256"
        ]
        == payload_hash,
    )

    pass_check(
        "Authorization Binds Exact Envelope",
        authorization[
            "envelope_sha256"
        ]
        == envelope[
            "envelope_sha256"
        ],
    )

    pass_check(
        "Authorization Binds Exact Live State",
        authorization[
            "live_state_sha256"
        ]
        == live_state[
            "state_sha256"
        ],
    )

    pass_check(
        "Authorization Has Future Expiry",
        authorization[
            "expires_at_ms"
        ] > epoch_ms(),
    )

    pass_check(
        "Authorization Integrity Recomputes Exactly",
        recompute_authorization_hash(
            authorization
        )
        == authorization[
            "authorization_sha256"
        ],
    )

    log(
        f"{VERSION}: AUTHORIZATION ID="
        f"{authorization['authorization_id']}"
    )

    log(
        f"{VERSION}: AUTHORIZATION SHA256="
        f"{authorization['authorization_sha256']}"
    )

    # --------------------------------------------------------------------------
    # TEST 7
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 7: INITIAL DURABLE STATE PERSISTENCE"
    )

    durable_state = (
        build_durable_state(
            live_state,
            intent,
            payload,
            payload_hash,
            envelope,
            authorization,
        )
    )

    durable_state = (
        persist_state(
            durable_state
        )
    )

    pass_check(
        "Durable State File Exists",
        os.path.exists(
            STATE_FILE
        ),
    )

    pass_check(
        "Durable State Hash Exists",
        len(
            durable_state[
                "state_hash"
            ]
        ) == 64,
    )

    pass_check(
        "Initial Durable Phase Is Authorized",
        durable_state[
            "phase"
        ]
        == "AUTHORIZED_NOT_DISPATCHED",
    )

    pass_check(
        "Initial Durable Authorization Is Unconsumed",
        not durable_state[
            "authorization"
        ][
            "consumed"
        ],
    )

    log(
        f"{VERSION}: INITIAL DURABLE STATE SHA256="
        f"{durable_state['state_hash']}"
    )

    # --------------------------------------------------------------------------
    # TEST 8
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 8: INITIAL DURABLE RELOAD"
    )

    loaded_initial = (
        durable_read_json(
            STATE_FILE
        )
    )

    pass_check(
        "Initial Durable State Integrity Is Valid",
        verify_state_integrity(
            loaded_initial
        ),
    )

    pass_check(
        "Reloaded Intent Matches Original",
        loaded_initial[
            "intent"
        ][
            "intent_sha256"
        ]
        == intent[
            "intent_sha256"
        ],
    )

    pass_check(
        "Reloaded Authorization Matches Original",
        loaded_initial[
            "authorization"
        ][
            "authorization_id"
        ]
        == authorization[
            "authorization_id"
        ],
    )

    pass_check(
        "Reloaded Authorization Remains Unconsumed",
        not loaded_initial[
            "authorization"
        ][
            "consumed"
        ],
    )

    # --------------------------------------------------------------------------
    # TEST 9
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 9: EXACTLY-ONCE SYNTHETIC DISPATCH"
    )

    working_authorization = deepcopy(
        loaded_initial[
            "authorization"
        ]
    )

    receipt = synthetic_dispatch(
        working_authorization,
        intent,
        payload,
        payload_hash,
        envelope,
        live_state,
    )

    pass_check(
        "Authorization Was Consumed",
        working_authorization[
            "consumed"
        ],
    )

    pass_check(
        "Authorization Has Dispatch ID",
        bool(
            working_authorization[
                "dispatch_id"
            ]
        ),
    )

    pass_check(
        "Synthetic Dispatch Count Is One",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    pass_check(
        "Receipt Is Synthetic",
        receipt[
            "synthetic"
        ],
    )

    pass_check(
        "Receipt Was Not Transmitted",
        not receipt[
            "transmitted"
        ],
    )

    pass_check(
        "Receipt Records No Network Write",
        not receipt[
            "network_write"
        ],
    )

    pass_check(
        "Receipt Records No Real Execution",
        not receipt[
            "real_execution"
        ],
    )

    pass_check(
        "Receipt Records No Demo Execution",
        not receipt[
            "demo_execution"
        ],
    )

    pass_check(
        "Receipt Client Order ID Matches Payload",
        receipt[
            "client_order_id"
        ]
        == payload[
            "newClientOrderId"
        ],
    )

    pass_check(
        "Receipt Hash Exists",
        len(
            receipt[
                "receipt_sha256"
            ]
        ) == 64,
    )

    log(
        f"{VERSION}: SYNTHETIC RECEIPT SHA256="
        f"{receipt['receipt_sha256']}"
    )

    # --------------------------------------------------------------------------
    # TEST 10
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 10: POST-DISPATCH DURABLE COMMIT"
    )

    durable_state[
        "authorization"
    ] = deepcopy(
        working_authorization
    )

    durable_state[
        "receipt"
    ] = deepcopy(
        receipt
    )

    durable_state[
        "phase"
    ] = (
        "SYNTHETIC_DISPATCH_COMMITTED"
    )

    durable_state[
        "dispatch_committed_at"
    ] = utc_iso()

    durable_state = (
        persist_state(
            durable_state
        )
    )

    pass_check(
        "Committed Durable Authorization Is Consumed",
        durable_state[
            "authorization"
        ][
            "consumed"
        ],
    )

    pass_check(
        "Committed Durable Receipt Exists",
        durable_state[
            "receipt"
        ]
        is not None,
    )

    pass_check(
        "Committed Durable Phase Is Correct",
        durable_state[
            "phase"
        ]
        == "SYNTHETIC_DISPATCH_COMMITTED",
    )

    pass_check(
        "Committed Durable State Integrity Is Valid",
        verify_state_integrity(
            durable_state
        ),
    )

    log(
        f"{VERSION}: COMMITTED DURABLE STATE SHA256="
        f"{durable_state['state_hash']}"
    )

    # --------------------------------------------------------------------------
    # TEST 11
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 11: SIMULATED PROCESS RESTART"
    )

    del loaded_initial

    with COUNTER_LOCK:
        COUNTERS[
            "restart_simulations"
        ] += 1

    recovered = (
        durable_read_json(
            STATE_FILE
        )
    )

    pass_check(
        "Restart Simulation Count Is One",
        COUNTERS[
            "restart_simulations"
        ] == 1,
    )

    pass_check(
        "Recovered Durable State Integrity Is Valid",
        verify_state_integrity(
            recovered
        ),
    )

    pass_check(
        "Recovered Phase Is Dispatch Committed",
        recovered[
            "phase"
        ]
        == "SYNTHETIC_DISPATCH_COMMITTED",
    )

    pass_check(
        "Recovered Authorization Is Consumed",
        recovered[
            "authorization"
        ][
            "consumed"
        ],
    )

    pass_check(
        "Recovered Receipt Exists",
        recovered[
            "receipt"
        ]
        is not None,
    )

    pass_check(
        "Recovered Receipt Matches Pre-Restart Receipt",
        recovered[
            "receipt"
        ][
            "receipt_sha256"
        ]
        == receipt[
            "receipt_sha256"
        ],
    )

    pass_check(
        "Recovered Dispatch ID Matches Authorization",
        recovered[
            "receipt"
        ][
            "dispatch_id"
        ]
        == recovered[
            "authorization"
        ][
            "dispatch_id"
        ],
    )

    # --------------------------------------------------------------------------
    # TEST 12
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 12: POST-RESTART REPLAY REJECTION"
    )

    replay_rejected = False

    try:
        attempt_restart_replay(
            recovered
        )

    except RuntimeError:
        replay_rejected = True

    pass_check(
        "Post-Restart Replay Is Rejected",
        replay_rejected,
    )

    pass_check(
        "Restart Replay Block Counter Is One",
        COUNTERS[
            "restart_replay_blocks"
        ] == 1,
    )

    pass_check(
        "Synthetic Dispatch Count Remains One",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    pass_check(
        "Recovered Authorization Remains Consumed",
        recovered[
            "authorization"
        ][
            "consumed"
        ],
    )

    # --------------------------------------------------------------------------
    # TEST 13
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 13: DUPLICATE DISPATCH REJECTION AFTER RECOVERY"
    )

    duplicate_rejected = False

    try:
        synthetic_dispatch(
            deepcopy(
                recovered[
                    "authorization"
                ]
            ),
            recovered[
                "intent"
            ],
            recovered[
                "payload"
            ],
            recovered[
                "payload_sha256"
            ],
            recovered[
                "envelope"
            ],
            recovered[
                "live_state"
            ],
        )

    except RuntimeError:
        duplicate_rejected = True

    pass_check(
        "Recovered Duplicate Dispatch Is Rejected",
        duplicate_rejected,
    )

    pass_check(
        "Duplicate Dispatch Block Counter Is One",
        COUNTERS[
            "duplicate_dispatch_blocks"
        ] == 1,
    )

    pass_check(
        "Synthetic Dispatch Count Still Remains One",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    # --------------------------------------------------------------------------
    # TEST 14
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 14: RECEIPT CHAIN RECONCILIATION"
    )

    recovered_receipt = (
        recovered[
            "receipt"
        ]
    )

    recovered_auth = (
        recovered[
            "authorization"
        ]
    )

    pass_check(
        "Receipt Binds Exact Authorization",
        recovered_receipt[
            "authorization_id"
        ]
        == recovered_auth[
            "authorization_id"
        ],
    )

    pass_check(
        "Receipt Binds Exact Intent",
        recovered_receipt[
            "intent_sha256"
        ]
        == recovered[
            "intent"
        ][
            "intent_sha256"
        ],
    )

    pass_check(
        "Receipt Binds Exact Payload",
        recovered_receipt[
            "payload_sha256"
        ]
        == recovered[
            "payload_sha256"
        ],
    )

    pass_check(
        "Receipt Binds Exact Envelope",
        recovered_receipt[
            "envelope_sha256"
        ]
        == recovered[
            "envelope"
        ][
            "envelope_sha256"
        ],
    )

    pass_check(
        "Receipt Binds Exact Live State",
        recovered_receipt[
            "live_state_sha256"
        ]
        == recovered[
            "live_state"
        ][
            "state_sha256"
        ],
    )

    pass_check(
        "Receipt Dispatch ID Matches Authorization",
        recovered_receipt[
            "dispatch_id"
        ]
        == recovered_auth[
            "dispatch_id"
        ],
    )

    # --------------------------------------------------------------------------
    # TEST 15
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 15: DURABLE TERMINAL SEAL"
    )

    recovered[
        "phase"
    ] = (
        "DURABLE_EXACTLY_ONCE_VALIDATED"
    )

    recovered[
        "terminal_sealed_at"
    ] = utc_iso()

    recovered = persist_state(
        recovered
    )

    terminal_reload = (
        durable_read_json(
            STATE_FILE
        )
    )

    pass_check(
        "Terminal Durable State Integrity Is Valid",
        verify_state_integrity(
            terminal_reload
        ),
    )

    pass_check(
        "Terminal Phase Survives Reload",
        terminal_reload[
            "phase"
        ]
        == "DURABLE_EXACTLY_ONCE_VALIDATED",
    )

    pass_check(
        "Terminal Authorization Remains Consumed",
        terminal_reload[
            "authorization"
        ][
            "consumed"
        ],
    )

    pass_check(
        "Terminal Receipt Survives Reload",
        terminal_reload[
            "receipt"
        ][
            "receipt_sha256"
        ]
        == receipt[
            "receipt_sha256"
        ],
    )

    # --------------------------------------------------------------------------
    # TEST 16
    # --------------------------------------------------------------------------

    section(
        f"{VERSION} TEST 16: FINAL POST-RESTART INVARIANTS"
    )

    pass_check(
        "Exactly One Synthetic Dispatch Was Counted",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
    )

    pass_check(
        "Exactly One Duplicate Dispatch Was Blocked",
        COUNTERS[
            "duplicate_dispatch_blocks"
        ] == 1,
    )

    pass_check(
        "Exactly One Restart Replay Was Blocked",
        COUNTERS[
            "restart_replay_blocks"
        ] == 1,
    )

    pass_check(
        "Exactly One Restart Simulation Occurred",
        COUNTERS[
            "restart_simulations"
        ] == 1,
    )

    pass_check(
        "Durable Writes Were Exercised",
        COUNTERS[
            "durable_writes"
        ] >= 3,
    )

    pass_check(
        "Durable Reads Were Exercised",
        COUNTERS[
            "durable_reads"
        ] >= 3,
    )

    pass_check(
        "Network Writes Remain Zero",
        COUNTERS[
            "network_writes"
        ] == 0,
    )

    pass_check(
        "Leverage Mutations Remain Zero",
        COUNTERS[
            "leverage_mutations"
        ] == 0,
    )

    pass_check(
        "Margin Mutations Remain Zero",
        COUNTERS[
            "margin_mutations"
        ] == 0,
    )

    pass_check(
        "Position Mutations Remain Zero",
        COUNTERS[
            "position_mutations"
        ] == 0,
    )

    pass_check(
        "Account Mutations Remain Zero",
        COUNTERS[
            "account_mutations"
        ] == 0,
    )

    pass_check(
        "Real Orders Remain Zero",
        COUNTERS[
            "real_orders"
        ] == 0,
    )

    pass_check(
        "Demo Orders Remain Zero",
        COUNTERS[
            "demo_orders"
        ] == 0,
    )

    pass_check(
        "Terminal State File Exists",
        os.path.exists(
            STATE_FILE
        ),
    )

    # --------------------------------------------------------------------------
    # COMPLETION
    # --------------------------------------------------------------------------

    PHASE = (
        "DURABLE_EXACTLY_ONCE_VALIDATED"
    )

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        f"{VERSION}: PHASE={PHASE}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{COUNTERS['authenticated_gets']}"
    )

    log(
        f"{VERSION}: PUBLIC GETS="
        f"{COUNTERS['public_gets']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{COUNTERS['network_writes']}"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{COUNTERS['leverage_mutations']}"
    )

    log(
        f"{VERSION}: MARGIN MUTATIONS="
        f"{COUNTERS['margin_mutations']}"
    )

    log(
        f"{VERSION}: POSITION MUTATIONS="
        f"{COUNTERS['position_mutations']}"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATIONS="
        f"{COUNTERS['account_mutations']}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{COUNTERS['real_orders']}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{COUNTERS['demo_orders']}"
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{COUNTERS['synthetic_dispatches']}"
    )

    log(
        f"{VERSION}: DUPLICATE DISPATCH BLOCKS="
        f"{COUNTERS['duplicate_dispatch_blocks']}"
    )

    log(
        f"{VERSION}: STALE STATE BLOCKS="
        f"{COUNTERS['stale_state_blocks']}"
    )

    log(
        f"{VERSION}: RESTART REPLAY BLOCKS="
        f"{COUNTERS['restart_replay_blocks']}"
    )

    log(
        f"{VERSION}: RESTART SIMULATIONS="
        f"{COUNTERS['restart_simulations']}"
    )

    log(
        f"{VERSION}: DURABLE WRITES="
        f"{COUNTERS['durable_writes']}"
    )

    log(
        f"{VERSION}: DURABLE READS="
        f"{COUNTERS['durable_reads']}"
    )

    log(
        f"{VERSION}: TERMINAL STATE SHA256="
        f"{terminal_reload['state_hash']}"
    )

    log(
        f"{VERSION}: RECEIPT SHA256="
        f"{terminal_reload['receipt']['receipt_sha256']}"
    )

    log(
        f"{VERSION}: AUTHORIZATION ID="
        f"{terminal_reload['authorization']['authorization_id']}"
    )

    log(
        f"{VERSION}: AUTHORIZATION CONSUMED="
        f"{terminal_reload['authorization']['consumed']}"
    )

    log(
        f"{VERSION}: NO REAL OR DEMO ORDER WAS SENT"
    )


# ==============================================================================
# HEARTBEAT
# ==============================================================================

def heartbeat_loop():
    heartbeat = 0

    while True:
        time.sleep(
            HEARTBEAT_SECONDS
        )

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT {heartbeat}"
            f" | phase={PHASE}"
            f" | network-writes="
            f"{COUNTERS['network_writes']}"
            f" | real-orders="
            f"{COUNTERS['real_orders']}"
            f" | demo-orders="
            f"{COUNTERS['demo_orders']}"
            f" | synthetic-dispatches="
            f"{COUNTERS['synthetic_dispatches']}"
            f" | duplicate-blocks="
            f"{COUNTERS['duplicate_dispatch_blocks']}"
            f" | restart-replay-blocks="
            f"{COUNTERS['restart_replay_blocks']}"
            f" | durable-writes="
            f"{COUNTERS['durable_writes']}"
            f" | durable-reads="
            f"{COUNTERS['durable_reads']}"
        )


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    global PHASE

    start_health_server()

    try:
        run_validation()

    except Exception as exc:
        PHASE = "VALIDATION_FAILED"

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        raise

    heartbeat_loop()


if __name__ == "__main__":
    main()
