#!/usr/bin/env python3
# ================================================================
# R35T MAIN.PY
# DURABLE CRASH-WINDOW + STALE-STATE RECOVERY VALIDATION
#
# SAFETY:
#   - NO REAL ORDERS
#   - NO DEMO ORDERS
#   - NO NETWORK WRITES
#   - NO LEVERAGE / MARGIN / POSITION / ACCOUNT MUTATIONS
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE:
#   Validate exactly-once synthetic execution across:
#       1. Durable authorization
#       2. Pre-consumption crash
#       3. Post-consumption / pre-receipt crash window
#       4. Recovery reconciliation
#       5. Stale-state rejection
#       6. Duplicate/replay rejection
#       7. Corrupted durable-state rejection
#       8. Terminal durable seal
# ================================================================

import copy
import hashlib
import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ================================================================
# CONFIGURATION
# ================================================================

VERSION = "R35T"
SYMBOL = "BTCUSDT"

HEALTH_PORT = int(os.environ.get("PORT", "10000"))

STATE_FILE = os.environ.get(
    "R35T_STATE_FILE",
    "/tmp/r35t_state.json"
)

TEST_STATE_FILE = STATE_FILE + ".test"
CORRUPT_STATE_FILE = STATE_FILE + ".corrupt"

HEARTBEAT_SECONDS = 30

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

AUTHORIZATION_TTL_SECONDS = 300

INITIAL_ENTRY_PERCENT = 5.0
MAX_FUND_EXPOSURE_PERCENT = 35.0
TARGET_LEVERAGE = 100
TARGET_MARGIN_TYPE = "ISOLATED"

QTY_STEP = 0.0001
MIN_QTY = 0.0001

LINE = "-" * 100


# ================================================================
# GLOBAL COUNTERS
# ================================================================

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
    "restart_replay_blocks": 0,
    "stale_state_blocks": 0,

    "preconsume_crash_simulations": 0,
    "postconsume_crash_simulations": 0,
    "recovery_reconciliations": 0,

    "corrupt_state_blocks": 0,

    "durable_writes": 0,
    "durable_reads": 0,
}


PHASE = "BOOT"


# ================================================================
# BASIC UTILITIES
# ================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_object(value):
    return sha256_text(canonical_json(value))


def log(message=""):
    print(f"{VERSION}: {message}", flush=True)


def separator():
    print(LINE, flush=True)


def pass_line(name):
    print(f"{name:<88} ✅ PASS", flush=True)


def fail_line(name):
    print(f"{name:<88} ❌ FAIL", flush=True)


def require(condition, name):
    if not condition:
        fail_line(name)
        raise AssertionError(name)

    pass_line(name)


def test_header(number, title):
    separator()
    print(f"{VERSION} TEST {number}: {title}", flush=True)
    separator()


# ================================================================
# ABSOLUTE WRITE FIREBREAKS
# ================================================================

def reject_network_write(*args, **kwargs):
    raise RuntimeError(
        "R35T safety firebreak: network write is permanently disabled"
    )


def reject_real_order(*args, **kwargs):
    raise RuntimeError(
        "R35T safety firebreak: real order execution is disabled"
    )


def reject_demo_order(*args, **kwargs):
    raise RuntimeError(
        "R35T safety firebreak: demo order execution is disabled"
    )


def reject_leverage_mutation(*args, **kwargs):
    raise RuntimeError(
        "R35T safety firebreak: leverage mutation is disabled"
    )


def reject_margin_mutation(*args, **kwargs):
    raise RuntimeError(
        "R35T safety firebreak: margin mutation is disabled"
    )


def reject_position_mutation(*args, **kwargs):
    raise RuntimeError(
        "R35T safety firebreak: position mutation is disabled"
    )


def reject_account_mutation(*args, **kwargs):
    raise RuntimeError(
        "R35T safety firebreak: account mutation is disabled"
    )


# ================================================================
# DURABLE STATE
# ================================================================

def make_state_body(state):
    body = copy.deepcopy(state)
    body.pop("state_sha256", None)
    return body


def calculate_state_hash(state):
    return hash_object(make_state_body(state))


def write_state(path, state):
    body = copy.deepcopy(state)
    body["state_sha256"] = calculate_state_hash(body)

    directory = os.path.dirname(path)

    if directory:
        os.makedirs(directory, exist_ok=True)

    temporary = path + ".tmp"

    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(
            body,
            handle,
            sort_keys=True,
            separators=(",", ":")
        )
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temporary, path)

    COUNTERS["durable_writes"] += 1

    return body


def read_state(path):
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)

    COUNTERS["durable_reads"] += 1

    expected = state.get("state_sha256")
    calculated = calculate_state_hash(state)

    if not expected or expected != calculated:
        raise RuntimeError(
            "Durable state integrity verification failed"
        )

    return state


def remove_test_files():
    for path in (
        TEST_STATE_FILE,
        TEST_STATE_FILE + ".tmp",
        CORRUPT_STATE_FILE,
        CORRUPT_STATE_FILE + ".tmp",
    ):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


# ================================================================
# SYNTHETIC EXECUTION OBJECTS
# ================================================================

def build_live_state():
    state = {
        "symbol": SYMBOL,
        "generation": 100,
        "epoch": 500,
        "margin_type": TARGET_MARGIN_TYPE,
        "long_leverage": TARGET_LEVERAGE,
        "short_leverage": TARGET_LEVERAGE,
        "open_positions": 0,
        "available_balance": "7.18945017",
        "market_price": "79950.1",
        "captured_at": utc_now(),
    }

    state["live_state_sha256"] = hash_object(state)

    return state


def build_intent(live_state):
    intent = {
        "intent_id": "intent-" + uuid.uuid4().hex,
        "version": VERSION,
        "symbol": SYMBOL,

        "action": "SYNTHETIC_INITIAL_LONG_ENTRY",

        "side": "BUY",
        "position_side": "LONG",
        "order_type": "MARKET",

        "quantity": "0.0004",

        "generation": live_state["generation"],
        "epoch": live_state["epoch"],

        "live_state_sha256": live_state["live_state_sha256"],

        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,
        "real_execution_allowed": False,
        "demo_execution_allowed": False,

        "created_at": utc_now(),
    }

    intent["intent_sha256"] = hash_object(intent)

    return intent


def build_payload(intent):
    payload = {
        "symbol": intent["symbol"],
        "side": intent["side"],
        "positionSide": intent["position_side"],
        "type": intent["order_type"],
        "quantity": intent["quantity"],
        "newClientOrderId": (
            "r35t-" + uuid.uuid4().hex[:20]
        ),
    }

    payload_hash = hash_object(payload)

    return payload, payload_hash


def build_envelope(intent, payload_hash, live_state):
    envelope = {
        "version": VERSION,

        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,

        "intent_sha256": intent["intent_sha256"],
        "payload_sha256": payload_hash,
        "live_state_sha256": live_state["live_state_sha256"],

        "generation": live_state["generation"],
        "epoch": live_state["epoch"],

        "created_at": utc_now(),
    }

    envelope["envelope_sha256"] = hash_object(envelope)

    return envelope


def authorization_integrity_body(auth):
    value = copy.deepcopy(auth)
    value.pop("authorization_sha256", None)
    return value


def authorization_hash(auth):
    return hash_object(authorization_integrity_body(auth))


def build_authorization(
    intent,
    payload_hash,
    envelope,
    live_state
):
    now = time.time()

    auth = {
        "authorization_id": "auth-" + uuid.uuid4().hex,

        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,

        "intent_sha256": intent["intent_sha256"],
        "payload_sha256": payload_hash,
        "envelope_sha256": envelope["envelope_sha256"],
        "live_state_sha256": live_state["live_state_sha256"],

        "generation": live_state["generation"],
        "epoch": live_state["epoch"],

        "issued_unix": now,
        "expires_unix": now + AUTHORIZATION_TTL_SECONDS,

        "consumed": False,
        "consumed_at": None,
        "dispatch_id": None,
    }

    auth["authorization_sha256"] = authorization_hash(auth)

    return auth


def verify_authorization_integrity(auth):
    expected = auth.get("authorization_sha256")

    if not expected:
        return False

    return expected == authorization_hash(auth)


def verify_live_binding(auth, live_state):
    return (
        auth["generation"] == live_state["generation"]
        and
        auth["epoch"] == live_state["epoch"]
        and
        auth["live_state_sha256"]
        == live_state["live_state_sha256"]
    )


def consume_authorization(auth):
    if auth["consumed"]:
        raise RuntimeError(
            "Synthetic authorization already consumed"
        )

    if time.time() >= auth["expires_unix"]:
        raise RuntimeError(
            "Synthetic authorization expired"
        )

    consumed = copy.deepcopy(auth)

    consumed["consumed"] = True
    consumed["consumed_at"] = utc_now()
    consumed["dispatch_id"] = "dispatch-" + uuid.uuid4().hex

    consumed["authorization_sha256"] = authorization_hash(
        consumed
    )

    return consumed


def build_receipt(
    authorization,
    intent,
    payload,
    payload_hash,
    envelope,
    live_state
):
    receipt = {
        "receipt_id": "receipt-" + uuid.uuid4().hex,

        "dispatch_id": authorization["dispatch_id"],
        "authorization_id": authorization["authorization_id"],

        "authorization_sha256":
            authorization["authorization_sha256"],

        "intent_sha256": intent["intent_sha256"],
        "payload_sha256": payload_hash,
        "envelope_sha256": envelope["envelope_sha256"],
        "live_state_sha256": live_state["live_state_sha256"],

        "client_order_id": payload["newClientOrderId"],

        "synthetic": True,
        "transmitted": False,
        "network_write": False,
        "real_execution": False,
        "demo_execution": False,

        "created_at": utc_now(),
    }

    receipt["receipt_sha256"] = hash_object(receipt)

    return receipt


# ================================================================
# SYNTHETIC DISPATCH
# ================================================================

def synthetic_dispatch(
    authorization,
    intent,
    payload,
    payload_hash,
    envelope,
    live_state
):
    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "Synthetic transport firebreak unexpectedly disabled"
        )

    if not verify_authorization_integrity(authorization):
        raise RuntimeError(
            "Authorization integrity failure"
        )

    if authorization["consumed"]:
        COUNTERS["duplicate_dispatch_blocks"] += 1
        raise RuntimeError(
            "Duplicate synthetic dispatch rejected"
        )

    if not verify_live_binding(
        authorization,
        live_state
    ):
        COUNTERS["stale_state_blocks"] += 1
        raise RuntimeError(
            "Stale live state rejected"
        )

    if authorization["intent_sha256"] != intent["intent_sha256"]:
        raise RuntimeError(
            "Authorization intent binding failure"
        )

    if authorization["payload_sha256"] != payload_hash:
        raise RuntimeError(
            "Authorization payload binding failure"
        )

    if (
        authorization["envelope_sha256"]
        != envelope["envelope_sha256"]
    ):
        raise RuntimeError(
            "Authorization envelope binding failure"
        )

    consumed_auth = consume_authorization(
        authorization
    )

    COUNTERS["synthetic_dispatches"] += 1

    receipt = build_receipt(
        consumed_auth,
        intent,
        payload,
        payload_hash,
        envelope,
        live_state
    )

    return consumed_auth, receipt


# ================================================================
# HEALTH SERVER
# ================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps({
            "ok": True,
            "version": VERSION,
            "phase": PHASE,

            "network_writes":
                COUNTERS["network_writes"],

            "real_orders":
                COUNTERS["real_orders"],

            "demo_orders":
                COUNTERS["demo_orders"],

            "synthetic_dispatches":
                COUNTERS["synthetic_dispatches"],

            "stale_state_blocks":
                COUNTERS["stale_state_blocks"],
        }).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    return server


# ================================================================
# MAIN VALIDATION
# ================================================================

def run_validation():

    global PHASE

    remove_test_files()

    separator()
    log("MAIN.PY ENTERED")
    separator()

    log(f"SYMBOL={SYMBOL}")
    log(f"VERSION={VERSION}")
    log(f"HEALTH PORT={HEALTH_PORT}")

    log("SYNTHETIC TRANSPORT ONLY")
    log("NETWORK WRITES DISABLED")
    log("REAL ORDER EXECUTION DISABLED")
    log("DEMO ORDER EXECUTION DISABLED")
    log("LEVERAGE MUTATION DISABLED")
    log("MARGIN MUTATION DISABLED")
    log("POSITION MUTATION DISABLED")
    log("ACCOUNT MUTATION DISABLED")

    # ============================================================
    # TEST 1
    # ============================================================

    test_header(
        1,
        "ABSOLUTE SAFETY FIREBREAK"
    )

    require(
        REAL_ORDER_EXECUTION is False,
        "Real Order Execution Is Disabled"
    )

    require(
        DEMO_ORDER_EXECUTION is False,
        "Demo Order Execution Is Disabled"
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "Network Writes Are Disabled"
    )

    require(
        LEVERAGE_MUTATION_ENABLED is False,
        "Leverage Mutation Is Disabled"
    )

    require(
        MARGIN_MUTATION_ENABLED is False,
        "Margin Mutation Is Disabled"
    )

    require(
        POSITION_MUTATION_ENABLED is False,
        "Position Mutation Is Disabled"
    )

    require(
        ACCOUNT_MUTATION_ENABLED is False,
        "Account Mutation Is Disabled"
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic Transport Only Is Enabled"
    )

    # ============================================================
    # TEST 2
    # ============================================================

    test_header(
        2,
        "SYNTHETIC LIVE STATE"
    )

    live_state = build_live_state()

    require(
        live_state["symbol"] == SYMBOL,
        "Live State Symbol Is Correct"
    )

    require(
        live_state["margin_type"]
        == TARGET_MARGIN_TYPE,
        "Live State Margin Type Is ISOLATED"
    )

    require(
        live_state["long_leverage"]
        == TARGET_LEVERAGE,
        "Live State Long Leverage Is 100x"
    )

    require(
        live_state["short_leverage"]
        == TARGET_LEVERAGE,
        "Live State Short Leverage Is 100x"
    )

    require(
        live_state["open_positions"] == 0,
        "Live State Is Flat"
    )

    require(
        bool(live_state["live_state_sha256"]),
        "Live State Hash Exists"
    )

    log(
        "LIVE STATE SHA256="
        + live_state["live_state_sha256"]
    )

    # ============================================================
    # TEST 3
    # ============================================================

    test_header(
        3,
        "SYNTHETIC INTENT AND PAYLOAD"
    )

    intent = build_intent(live_state)
    payload, payload_hash = build_payload(intent)

    require(
        intent["synthetic_only"] is True,
        "Intent Is Synthetic Only"
    )

    require(
        intent["transmission_allowed"] is False,
        "Intent Forbids Transmission"
    )

    require(
        intent["network_write_allowed"] is False,
        "Intent Forbids Network Write"
    )

    require(
        payload["symbol"] == SYMBOL,
        "Payload Symbol Is Correct"
    )

    require(
        payload["quantity"] == "0.0004",
        "Payload Quantity Is 0.0004"
    )

    require(
        bool(payload_hash),
        "Payload Hash Exists"
    )

    log(
        "SYNTHETIC PAYLOAD="
        + canonical_json(payload)
    )

    log(
        "SYNTHETIC PAYLOAD SHA256="
        + payload_hash
    )

    # ============================================================
    # TEST 4
    # ============================================================

    test_header(
        4,
        "SYNTHETIC EXECUTION ENVELOPE"
    )

    envelope = build_envelope(
        intent,
        payload_hash,
        live_state
    )

    require(
        envelope["synthetic_only"] is True,
        "Envelope Is Synthetic Only"
    )

    require(
        envelope["transmission_allowed"] is False,
        "Envelope Forbids Transmission"
    )

    require(
        envelope["network_write_allowed"] is False,
        "Envelope Forbids Network Write"
    )

    require(
        envelope["intent_sha256"]
        == intent["intent_sha256"],
        "Envelope Binds Exact Intent"
    )

    require(
        envelope["payload_sha256"]
        == payload_hash,
        "Envelope Binds Exact Payload"
    )

    require(
        envelope["live_state_sha256"]
        == live_state["live_state_sha256"],
        "Envelope Binds Exact Live State"
    )

    log(
        "ENVELOPE SHA256="
        + envelope["envelope_sha256"]
    )

    # ============================================================
    # TEST 5
    # ============================================================

    test_header(
        5,
        "ONE-TIME SYNTHETIC AUTHORIZATION"
    )

    authorization = build_authorization(
        intent,
        payload_hash,
        envelope,
        live_state
    )

    require(
        authorization["synthetic_only"] is True,
        "Authorization Is Synthetic Only"
    )

    require(
        authorization["consumed"] is False,
        "Authorization Is Initially Unconsumed"
    )

    require(
        authorization["expires_unix"]
        > time.time(),
        "Authorization Has Future Expiry"
    )

    require(
        verify_authorization_integrity(
            authorization
        ),
        "Authorization Integrity Recomputes Exactly"
    )

    log(
        "AUTHORIZATION ID="
        + authorization["authorization_id"]
    )

    log(
        "AUTHORIZATION SHA256="
        + authorization["authorization_sha256"]
    )

    # ============================================================
    # TEST 6
    # ============================================================

    test_header(
        6,
        "PRE-CONSUMPTION CRASH WINDOW"
    )

    initial_state = {
        "version": VERSION,
        "phase": "AUTHORIZED",

        "live_state": live_state,
        "intent": intent,
        "payload": payload,
        "payload_sha256": payload_hash,
        "envelope": envelope,
        "authorization": authorization,
        "receipt": None,

        "terminal": False,
        "updated_at": utc_now(),
    }

    written_initial = write_state(
        TEST_STATE_FILE,
        initial_state
    )

    COUNTERS[
        "preconsume_crash_simulations"
    ] += 1

    recovered_initial = read_state(
        TEST_STATE_FILE
    )

    require(
        recovered_initial["phase"]
        == "AUTHORIZED",
        "Pre-Crash Phase Recovers As Authorized"
    )

    require(
        recovered_initial[
            "authorization"
        ]["consumed"] is False,
        "Authorization Remains Unconsumed"
    )

    require(
        recovered_initial[
            "state_sha256"
        ] == written_initial[
            "state_sha256"
        ],
        "Recovered State Hash Matches"
    )

    # ============================================================
    # TEST 7
    # ============================================================

    test_header(
        7,
        "STALE STATE REJECTION"
    )

    stale_state = copy.deepcopy(live_state)

    stale_state["generation"] += 1

    stale_state.pop(
        "live_state_sha256",
        None
    )

    stale_state[
        "live_state_sha256"
    ] = hash_object(stale_state)

    stale_rejected = False

    try:
        synthetic_dispatch(
            recovered_initial["authorization"],
            intent,
            payload,
            payload_hash,
            envelope,
            stale_state
        )

    except RuntimeError as exc:
        stale_rejected = (
            "Stale live state rejected"
            in str(exc)
        )

    require(
        stale_rejected,
        "Synthetic Stale State Is Rejected"
    )

    require(
        COUNTERS["stale_state_blocks"] == 1,
        "Stale State Block Counter Is One"
    )

    require(
        COUNTERS["synthetic_dispatches"] == 0,
        "No Dispatch Occurred On Stale State"
    )

    # ============================================================
    # TEST 8
    # ============================================================

    test_header(
        8,
        "POST-CONSUMPTION PRE-RECEIPT CRASH WINDOW"
    )

    recovered_auth = recovered_initial[
        "authorization"
    ]

    require(
        verify_live_binding(
            recovered_auth,
            live_state
        ),
        "Recovered Authorization Matches Fresh State"
    )

    consumed_auth = consume_authorization(
        recovered_auth
    )

    crash_window_state = copy.deepcopy(
        recovered_initial
    )

    crash_window_state[
        "phase"
    ] = "AUTHORIZATION_CONSUMED"

    crash_window_state[
        "authorization"
    ] = consumed_auth

    crash_window_state[
        "receipt"
    ] = None

    crash_window_state[
        "updated_at"
    ] = utc_now()

    write_state(
        TEST_STATE_FILE,
        crash_window_state
    )

    COUNTERS[
        "postconsume_crash_simulations"
    ] += 1

    recovered_crash_window = read_state(
        TEST_STATE_FILE
    )

    require(
        recovered_crash_window[
            "authorization"
        ]["consumed"] is True,
        "Consumed Authorization Survives Crash"
    )

    require(
        recovered_crash_window[
            "receipt"
        ] is None,
        "Receipt Is Absent In Crash Window"
    )

    require(
        recovered_crash_window[
            "phase"
        ] == "AUTHORIZATION_CONSUMED",
        "Crash Window Phase Is Recovered"
    )

    # ============================================================
    # TEST 9
    # ============================================================

    test_header(
        9,
        "CRASH-WINDOW RECOVERY RECONCILIATION"
    )

    recovered_auth = recovered_crash_window[
        "authorization"
    ]

    require(
        verify_authorization_integrity(
            recovered_auth
        ),
        "Recovered Consumed Authorization Integrity Is Valid"
    )

    require(
        recovered_auth[
            "dispatch_id"
        ] is not None,
        "Recovered Authorization Has Dispatch ID"
    )

    recovered_receipt = build_receipt(
        recovered_auth,
        intent,
        payload,
        payload_hash,
        envelope,
        live_state
    )

    COUNTERS[
        "synthetic_dispatches"
    ] += 1

    COUNTERS[
        "recovery_reconciliations"
    ] += 1

    require(
        recovered_receipt[
            "synthetic"
        ] is True,
        "Recovered Receipt Is Synthetic"
    )

    require(
        recovered_receipt[
            "transmitted"
        ] is False,
        "Recovered Receipt Was Not Transmitted"
    )

    require(
        recovered_receipt[
            "network_write"
        ] is False,
        "Recovered Receipt Records No Network Write"
    )

    require(
        recovered_receipt[
            "dispatch_id"
        ] == recovered_auth[
            "dispatch_id"
        ],
        "Recovered Receipt Uses Existing Dispatch ID"
    )

    # ============================================================
    # TEST 10
    # ============================================================

    test_header(
        10,
        "RECOVERED COMMIT"
    )

    committed_state = copy.deepcopy(
        recovered_crash_window
    )

    committed_state[
        "phase"
    ] = "DISPATCH_COMMITTED"

    committed_state[
        "receipt"
    ] = recovered_receipt

    committed_state[
        "updated_at"
    ] = utc_now()

    written_committed = write_state(
        TEST_STATE_FILE,
        committed_state
    )

    committed_reload = read_state(
        TEST_STATE_FILE
    )

    require(
        committed_reload[
            "authorization"
        ]["consumed"] is True,
        "Committed Authorization Is Consumed"
    )

    require(
        committed_reload[
            "receipt"
        ] is not None,
        "Committed Receipt Exists"
    )

    require(
        committed_reload[
            "phase"
        ] == "DISPATCH_COMMITTED",
        "Committed Phase Is Correct"
    )

    require(
        committed_reload[
            "state_sha256"
        ] == written_committed[
            "state_sha256"
        ],
        "Committed State Integrity Is Valid"
    )

    # ============================================================
    # TEST 11
    # ============================================================

    test_header(
        11,
        "POST-RECOVERY DUPLICATE DISPATCH REJECTION"
    )

    duplicate_rejected = False

    try:
        synthetic_dispatch(
            committed_reload[
                "authorization"
            ],
            intent,
            payload,
            payload_hash,
            envelope,
            live_state
        )

    except RuntimeError as exc:
        duplicate_rejected = (
            "already consumed"
            in str(exc).lower()
            or
            "duplicate"
            in str(exc).lower()
        )

        if duplicate_rejected:
            COUNTERS[
                "restart_replay_blocks"
            ] += 1

    require(
        duplicate_rejected,
        "Recovered Duplicate Dispatch Is Rejected"
    )

    require(
        COUNTERS[
            "restart_replay_blocks"
        ] == 1,
        "Restart Replay Block Counter Is One"
    )

    require(
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
        "Synthetic Dispatch Count Remains One"
    )

    # ============================================================
    # TEST 12
    # ============================================================

    test_header(
        12,
        "CORRUPTED DURABLE STATE REJECTION"
    )

    with open(
        CORRUPT_STATE_FILE,
        "w",
        encoding="utf-8"
    ) as handle:
        corrupted = copy.deepcopy(
            committed_reload
        )

        corrupted["phase"] = "FAKE_PHASE"

        # Deliberately preserve old SHA256.
        json.dump(
            corrupted,
            handle,
            sort_keys=True,
            separators=(",", ":")
        )

    corrupt_rejected = False

    try:
        read_state(
            CORRUPT_STATE_FILE
        )

    except RuntimeError as exc:
        corrupt_rejected = (
            "integrity"
            in str(exc).lower()
        )

        if corrupt_rejected:
            COUNTERS[
                "corrupt_state_blocks"
            ] += 1

    require(
        corrupt_rejected,
        "Corrupted Durable State Is Rejected"
    )

    require(
        COUNTERS[
            "corrupt_state_blocks"
        ] == 1,
        "Corrupt State Block Counter Is One"
    )

    # ============================================================
    # TEST 13
    # ============================================================

    test_header(
        13,
        "RECEIPT CHAIN RECONCILIATION"
    )

    receipt = committed_reload[
        "receipt"
    ]

    auth = committed_reload[
        "authorization"
    ]

    require(
        receipt[
            "authorization_sha256"
        ] == auth[
            "authorization_sha256"
        ],
        "Receipt Binds Exact Authorization"
    )

    require(
        receipt[
            "intent_sha256"
        ] == intent[
            "intent_sha256"
        ],
        "Receipt Binds Exact Intent"
    )

    require(
        receipt[
            "payload_sha256"
        ] == payload_hash,
        "Receipt Binds Exact Payload"
    )

    require(
        receipt[
            "envelope_sha256"
        ] == envelope[
            "envelope_sha256"
        ],
        "Receipt Binds Exact Envelope"
    )

    require(
        receipt[
            "live_state_sha256"
        ] == live_state[
            "live_state_sha256"
        ],
        "Receipt Binds Exact Live State"
    )

    require(
        receipt[
            "dispatch_id"
        ] == auth[
            "dispatch_id"
        ],
        "Receipt Dispatch ID Matches Authorization"
    )

    # ============================================================
    # TEST 14
    # ============================================================

    test_header(
        14,
        "TERMINAL DURABLE SEAL"
    )

    terminal_state = copy.deepcopy(
        committed_reload
    )

    terminal_state[
        "phase"
    ] = "DURABLE_CRASH_WINDOW_VALIDATED"

    terminal_state[
        "terminal"
    ] = True

    terminal_state[
        "updated_at"
    ] = utc_now()

    terminal_written = write_state(
        TEST_STATE_FILE,
        terminal_state
    )

    terminal_reload = read_state(
        TEST_STATE_FILE
    )

    require(
        terminal_reload[
            "terminal"
        ] is True,
        "Terminal Flag Survives Reload"
    )

    require(
        terminal_reload[
            "phase"
        ] == "DURABLE_CRASH_WINDOW_VALIDATED",
        "Terminal Phase Survives Reload"
    )

    require(
        terminal_reload[
            "authorization"
        ]["consumed"] is True,
        "Terminal Authorization Remains Consumed"
    )

    require(
        terminal_reload[
            "receipt"
        ] is not None,
        "Terminal Receipt Survives Reload"
    )

    # ============================================================
    # TEST 15
    # ============================================================

    test_header(
        15,
        "FINAL SAFETY INVARIANTS"
    )

    require(
        COUNTERS[
            "synthetic_dispatches"
        ] == 1,
        "Exactly One Synthetic Dispatch Was Counted"
    )

    require(
        COUNTERS[
            "stale_state_blocks"
        ] == 1,
        "Exactly One Stale State Was Blocked"
    )

    require(
        COUNTERS[
            "restart_replay_blocks"
        ] == 1,
        "Exactly One Restart Replay Was Blocked"
    )

    require(
        COUNTERS[
            "preconsume_crash_simulations"
        ] == 1,
        "Pre-Consumption Crash Was Exercised"
    )

    require(
        COUNTERS[
            "postconsume_crash_simulations"
        ] == 1,
        "Post-Consumption Crash Was Exercised"
    )

    require(
        COUNTERS[
            "recovery_reconciliations"
        ] == 1,
        "Recovery Reconciliation Was Exercised"
    )

    require(
        COUNTERS[
            "corrupt_state_blocks"
        ] == 1,
        "Corrupted State Rejection Was Exercised"
    )

    require(
        COUNTERS["network_writes"] == 0,
        "Network Writes Remain Zero"
    )

    require(
        COUNTERS["leverage_mutations"] == 0,
        "Leverage Mutations Remain Zero"
    )

    require(
        COUNTERS["margin_mutations"] == 0,
        "Margin Mutations Remain Zero"
    )

    require(
        COUNTERS["position_mutations"] == 0,
        "Position Mutations Remain Zero"
    )

    require(
        COUNTERS["account_mutations"] == 0,
        "Account Mutations Remain Zero"
    )

    require(
        COUNTERS["real_orders"] == 0,
        "Real Orders Remain Zero"
    )

    require(
        COUNTERS["demo_orders"] == 0,
        "Demo Orders Remain Zero"
    )

    require(
        os.path.exists(TEST_STATE_FILE),
        "Terminal State File Exists"
    )

    # ============================================================
    # FINAL
    # ============================================================

    PHASE = "DURABLE_CRASH_WINDOW_VALIDATED"

    separator()
    log("VALIDATION COMPLETE")
    separator()

    log(f"PHASE={PHASE}")

    log(
        f"AUTHENTICATED GETS="
        f"{COUNTERS['authenticated_gets']}"
    )

    log(
        f"PUBLIC GETS="
        f"{COUNTERS['public_gets']}"
    )

    log(
        f"NETWORK WRITES="
        f"{COUNTERS['network_writes']}"
    )

    log(
        f"LEVERAGE MUTATIONS="
        f"{COUNTERS['leverage_mutations']}"
    )

    log(
        f"MARGIN MUTATIONS="
        f"{COUNTERS['margin_mutations']}"
    )

    log(
        f"POSITION MUTATIONS="
        f"{COUNTERS['position_mutations']}"
    )

    log(
        f"ACCOUNT MUTATIONS="
        f"{COUNTERS['account_mutations']}"
    )

    log(
        f"REAL ORDERS="
        f"{COUNTERS['real_orders']}"
    )

    log(
        f"DEMO ORDERS="
        f"{COUNTERS['demo_orders']}"
    )

    log(
        f"SYNTHETIC DISPATCHES="
        f"{COUNTERS['synthetic_dispatches']}"
    )

    log(
        f"DUPLICATE DISPATCH BLOCKS="
        f"{COUNTERS['duplicate_dispatch_blocks']}"
    )

    log(
        f"STALE STATE BLOCKS="
        f"{COUNTERS['stale_state_blocks']}"
    )

    log(
        f"RESTART REPLAY BLOCKS="
        f"{COUNTERS['restart_replay_blocks']}"
    )

    log(
        f"PRE-CONSUME CRASH SIMULATIONS="
        f"{COUNTERS['preconsume_crash_simulations']}"
    )

    log(
        f"POST-CONSUME CRASH SIMULATIONS="
        f"{COUNTERS['postconsume_crash_simulations']}"
    )

    log(
        f"RECOVERY RECONCILIATIONS="
        f"{COUNTERS['recovery_reconciliations']}"
    )

    log(
        f"CORRUPT STATE BLOCKS="
        f"{COUNTERS['corrupt_state_blocks']}"
    )

    log(
        f"DURABLE WRITES="
        f"{COUNTERS['durable_writes']}"
    )

    log(
        f"DURABLE READS="
        f"{COUNTERS['durable_reads']}"
    )

    log(
        "TERMINAL STATE SHA256="
        + terminal_written["state_sha256"]
    )

    log(
        "RECEIPT SHA256="
        + terminal_reload[
            "receipt"
        ]["receipt_sha256"]
    )

    log(
        "AUTHORIZATION ID="
        + terminal_reload[
            "authorization"
        ]["authorization_id"]
    )

    log(
        "AUTHORIZATION CONSUMED="
        + str(
            terminal_reload[
                "authorization"
            ]["consumed"]
        )
    )

    log("NO REAL OR DEMO ORDER WAS SENT")

    return terminal_reload


# ================================================================
# HEARTBEAT LOOP
# ================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:
        time.sleep(HEARTBEAT_SECONDS)

        heartbeat += 1

        log(
            f"HEARTBEAT {heartbeat}"
            f" | phase={PHASE}"
            f" | network-writes="
            f"{COUNTERS['network_writes']}"
            f" | real-orders="
            f"{COUNTERS['real_orders']}"
            f" | demo-orders="
            f"{COUNTERS['demo_orders']}"
            f" | synthetic-dispatches="
            f"{COUNTERS['synthetic_dispatches']}"
            f" | stale-blocks="
            f"{COUNTERS['stale_state_blocks']}"
            f" | restart-replay-blocks="
            f"{COUNTERS['restart_replay_blocks']}"
            f" | corrupt-state-blocks="
            f"{COUNTERS['corrupt_state_blocks']}"
            f" | durable-writes="
            f"{COUNTERS['durable_writes']}"
            f" | durable-reads="
            f"{COUNTERS['durable_reads']}"
        )


# ================================================================
# ENTRY POINT
# ================================================================

def main():

    start_health_server()

    try:
        run_validation()

    except Exception as exc:

        global PHASE

        PHASE = "VALIDATION_FAILED"

        separator()
        log("VALIDATION FAILED")
        separator()

        log(
            f"ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        raise

    heartbeat_loop()


if __name__ == "__main__":
    main()
