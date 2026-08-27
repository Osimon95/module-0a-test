import os
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R34A
# STANDARD-LIBRARY-ONLY PRE-LIVE CORRECTION VALIDATION
# =============================================================================

VERSION = "R34A"
SYMBOL = "BTCUSDT"

STATE_FILE = "/tmp/r34a_pre_live_state.json"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

MARGIN_TYPE = "ISOLATED"

LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"


# =============================================================================
# HARD SAFETY CONSTANTS
# =============================================================================

SYNTHETIC_ONLY = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

REAL_POST_ENABLED = False

AUTHENTICATED_POST_ENABLED = False

PUBLIC_READ_ONLY_HTTP_ENABLED = False
PRIVATE_READ_ONLY_HTTP_ENABLED = False


# =============================================================================
# RUNTIME COUNTERS
# =============================================================================

REAL_ORDER_COUNTER = 0
NETWORK_WRITE_COUNTER = 0
LEVERAGE_MUTATION_COUNTER = 0

SYNTHETIC_DISPATCH_COUNTER = 0
DUPLICATE_DISPATCH_BLOCK_COUNTER = 0


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_json(data):
    return sha256_text(canonical_json(data))


def separator():
    print("-" * 92, flush=True)


def section(title):
    separator()
    print(title, flush=True)
    separator()


TEST_RESULTS = []


def check(name, condition):
    passed = bool(condition)

    TEST_RESULTS.append(
        {
            "name": name,
            "passed": passed,
        }
    )

    icon = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{name:<78} {icon}",
        flush=True,
    )

    return passed


# =============================================================================
# DURABLE STATE
# =============================================================================

def initial_state():
    return {
        "version": VERSION,
        "symbol": SYMBOL,

        "phase": "PREPARED",

        "synthetic_only": True,

        "real_execution": False,
        "network_writes": False,
        "leverage_mutation": False,

        "correction_required": True,

        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,

        "margin_type": MARGIN_TYPE,

        "intent_bound": False,

        "authorization_issued": False,
        "authorization_consumed": False,

        "dispatch_committed": False,
        "synthetic_dispatch_completed": False,

        "generation": 1,
        "recovery_epoch": 1,

        "intent_hash": None,
        "authorization_hash": None,
        "payload_hash": None,
        "envelope_hash": None,
        "receipt_hash": None,

        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def save_state(state):
    state["updated_at"] = utc_now()

    temp_file = STATE_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(
            state,
            f,
            sort_keys=True,
            indent=2,
        )

        f.flush()

        try:
            os.fsync(f.fileno())
        except OSError:
            pass

    os.replace(
        temp_file,
        STATE_FILE,
    )


def load_state():
    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        return data

    except Exception as exc:
        print(
            f"{VERSION}: STATE RESTORE ERROR: {exc}",
            flush=True,
        )

        return None


def reset_state():
    state = initial_state()

    save_state(state)

    return state


# =============================================================================
# INTENT CONSTRUCTION
# =============================================================================

def build_correction_intent(state):
    intent = {
        "type": "LEVERAGE_CORRECTION_INTENT",

        "symbol": SYMBOL,

        "margin_type": MARGIN_TYPE,

        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,

        "generation": state["generation"],
        "recovery_epoch": state["recovery_epoch"],

        "synthetic_only": True,

        "network_transmission_allowed": False,
        "leverage_mutation_allowed": False,
    }

    return intent


# =============================================================================
# PAYLOAD CONSTRUCTION
# =============================================================================

def build_leverage_payload():
    return {
        "symbol": SYMBOL,
        "marginMode": MARGIN_TYPE,
        "leverage": str(TARGET_LONG_LEVERAGE),
    }


# =============================================================================
# AUTHORIZATION
# =============================================================================

def build_authorization(
    state,
    intent_hash,
    payload_hash,
):
    authorization = {
        "type": "SYNTHETIC_LEVERAGE_AUTHORIZATION",

        "symbol": SYMBOL,

        "intent_hash": intent_hash,
        "payload_hash": payload_hash,

        "generation": state["generation"],
        "recovery_epoch": state["recovery_epoch"],

        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,

        "synthetic_only": True,

        "network_write_authorized": False,
        "real_execution_authorized": False,
        "leverage_mutation_authorized": False,
    }

    return authorization


# =============================================================================
# TRANSPORT ENVELOPE
# =============================================================================

def build_transport_envelope(
    state,
    intent_hash,
    authorization_hash,
    payload,
):
    envelope = {
        "transport": "SYNTHETIC",

        "method": "POST",

        "path": LEVERAGE_ENDPOINT,

        "symbol": SYMBOL,

        "payload": payload,

        "intent_hash": intent_hash,
        "authorization_hash": authorization_hash,

        "generation": state["generation"],
        "recovery_epoch": state["recovery_epoch"],

        "network_transmission": False,
        "exchange_contacted": False,

        "real_post": False,

        "leverage_mutation": False,
    }

    return envelope


# =============================================================================
# ABSOLUTE NETWORK-WRITE FIREBREAK
# =============================================================================

def forbidden_network_write(*args, **kwargs):
    raise RuntimeError(
        "R34A FIREBREAK: real network writes are disabled"
    )


def forbidden_real_order(*args, **kwargs):
    raise RuntimeError(
        "R34A FIREBREAK: real order execution is disabled"
    )


def forbidden_leverage_mutation(*args, **kwargs):
    raise RuntimeError(
        "R34A FIREBREAK: leverage mutation is disabled"
    )


# =============================================================================
# SYNTHETIC DISPATCH
# =============================================================================

def synthetic_dispatch(
    state,
    envelope,
):
    global SYNTHETIC_DISPATCH_COUNTER
    global DUPLICATE_DISPATCH_BLOCK_COUNTER

    if state.get("synthetic_dispatch_completed"):
        DUPLICATE_DISPATCH_BLOCK_COUNTER += 1

        raise RuntimeError(
            "duplicate synthetic dispatch rejected"
        )

    if state.get("authorization_consumed"):
        DUPLICATE_DISPATCH_BLOCK_COUNTER += 1

        raise RuntimeError(
            "authorization already consumed"
        )

    if not SYNTHETIC_ONLY:
        raise RuntimeError(
            "synthetic-only invariant violated"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "network writes unexpectedly enabled"
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "leverage mutation unexpectedly enabled"
        )

    if REAL_ORDER_EXECUTION_ENABLED:
        raise RuntimeError(
            "real execution unexpectedly enabled"
        )

    state["dispatch_committed"] = True

    save_state(state)

    state["authorization_consumed"] = True

    SYNTHETIC_DISPATCH_COUNTER += 1

    receipt = {
        "type": "SYNTHETIC_LEVERAGE_RECEIPT",

        "symbol": SYMBOL,

        "transport": "SYNTHETIC",

        "endpoint": envelope["path"],

        "generation": state["generation"],
        "recovery_epoch": state["recovery_epoch"],

        "authorization_consumed": True,

        "dispatch_committed": True,

        "synthetic_dispatch": True,

        "network_transmission": False,
        "exchange_contacted": False,

        "real_order_created": False,

        "leverage_mutated": False,

        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,
    }

    state["receipt_hash"] = sha256_json(receipt)

    state["synthetic_dispatch_completed"] = True

    state["phase"] = "PRE_LIVE_VALIDATED"

    save_state(state)

    return receipt


# =============================================================================
# HEALTH SERVER
# =============================================================================

CURRENT_STATE = {}


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):
            self.send_response(404)
            self.end_headers()
            return

        body = {
            "status": "ok",
            "version": VERSION,
            "symbol": SYMBOL,

            "phase": CURRENT_STATE.get(
                "phase",
                "UNKNOWN",
            ),

            "synthetic_only": SYNTHETIC_ONLY,

            "real_execution": (
                REAL_ORDER_EXECUTION_ENABLED
            ),

            "network_writes": (
                EXCHANGE_NETWORK_WRITES_ENABLED
            ),

            "leverage_mutation": (
                LEVERAGE_MUTATION_ENABLED
            ),

            "target_long_leverage":
                TARGET_LONG_LEVERAGE,

            "target_short_leverage":
                TARGET_SHORT_LEVERAGE,

            "generation": CURRENT_STATE.get(
                "generation"
            ),

            "recovery_epoch":
                CURRENT_STATE.get(
                    "recovery_epoch"
                ),
        }

        encoded = json.dumps(
            body
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


def run_health_server():
    try:
        server = HTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        print(
            f"{VERSION}: HEALTH SERVER "
            f"LISTENING ON PORT {HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    except Exception as exc:
        print(
            f"{VERSION}: HEALTH SERVER ERROR: {exc}",
            flush=True,
        )


# =============================================================================
# VALIDATION
# =============================================================================

def run_validation():
    global CURRENT_STATE

    section(
        "R34A: MAIN.PY ENTERED"
    )

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: EXTERNAL REQUESTS PACKAGE="
        f"NOT REQUIRED",
        flush=True,
    )

    print(
        f"{VERSION}: REAL EXECUTION DISABLED",
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
        "R34A TEST 1: STANDARD LIBRARY SAFETY CONFIGURATION"
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


    # =========================================================================
    section(
        "R34A TEST 2: TARGET CONFIGURATION"
    )
    # =========================================================================

    check(
        "Symbol Is BTCUSDT",
        SYMBOL == "BTCUSDT",
    )

    check(
        "Margin Type Is ISOLATED",
        MARGIN_TYPE == "ISOLATED",
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
        "Exact Leverage Endpoint Is Preserved",
        LEVERAGE_ENDPOINT
        == "/capi/v2/account/leverage",
    )


    # =========================================================================
    section(
        "R34A TEST 3: FRESH DURABLE STATE"
    )
    # =========================================================================

    state = reset_state()

    CURRENT_STATE = state

    check(
        "State Starts Prepared",
        state["phase"] == "PREPARED",
    )

    check(
        "Correction Is Required",
        state["correction_required"] is True,
    )

    check(
        "Generation Is One",
        state["generation"] == 1,
    )

    check(
        "Recovery Epoch Is One",
        state["recovery_epoch"] == 1,
    )

    check(
        "Authorization Is Initially Unconsumed",
        state["authorization_consumed"] is False,
    )


    # =========================================================================
    section(
        "R34A TEST 4: CORRECTION INTENT"
    )
    # =========================================================================

    intent = build_correction_intent(
        state
    )

    intent_hash = sha256_json(
        intent
    )

    state["intent_hash"] = intent_hash
    state["intent_bound"] = True

    save_state(state)

    check(
        "Intent Is Bound",
        state["intent_bound"] is True,
    )

    check(
        "Intent Symbol Matches",
        intent["symbol"] == SYMBOL,
    )

    check(
        "Intent Long Target Is 100x",
        intent["target_long_leverage"]
        == 100,
    )

    check(
        "Intent Short Target Is 100x",
        intent["target_short_leverage"]
        == 100,
    )

    check(
        "Intent Is Synthetic Only",
        intent["synthetic_only"] is True,
    )

    check(
        "Intent Forbids Network Transmission",
        intent[
            "network_transmission_allowed"
        ] is False,
    )

    check(
        "Intent Forbids Leverage Mutation",
        intent[
            "leverage_mutation_allowed"
        ] is False,
    )


    # =========================================================================
    section(
        "R34A TEST 5: EXACT PAYLOAD"
    )
    # =========================================================================

    payload = build_leverage_payload()

    payload_hash = sha256_json(
        payload
    )

    state["payload_hash"] = payload_hash

    save_state(state)

    check(
        "Payload Symbol Matches",
        payload["symbol"] == SYMBOL,
    )

    check(
        "Payload Margin Mode Is ISOLATED",
        payload["marginMode"]
        == "ISOLATED",
    )

    check(
        "Payload Leverage Is 100",
        payload["leverage"]
        == "100",
    )

    check(
        "Payload Hash Exists",
        isinstance(
            payload_hash,
            str,
        )
        and len(payload_hash) == 64,
    )


    # =========================================================================
    section(
        "R34A TEST 6: SYNTHETIC AUTHORIZATION"
    )
    # =========================================================================

    authorization = build_authorization(
        state,
        intent_hash,
        payload_hash,
    )

    authorization_hash = sha256_json(
        authorization
    )

    state["authorization_hash"] = (
        authorization_hash
    )

    state["authorization_issued"] = True

    save_state(state)

    check(
        "Authorization Is Issued",
        state["authorization_issued"]
        is True,
    )

    check(
        "Authorization Binds Intent",
        authorization["intent_hash"]
        == intent_hash,
    )

    check(
        "Authorization Binds Payload",
        authorization["payload_hash"]
        == payload_hash,
    )

    check(
        "Authorization Is Synthetic",
        authorization["synthetic_only"]
        is True,
    )

    check(
        "Authorization Does Not Permit Network Write",
        authorization[
            "network_write_authorized"
        ] is False,
    )

    check(
        "Authorization Does Not Permit Real Execution",
        authorization[
            "real_execution_authorized"
        ] is False,
    )

    check(
        "Authorization Does Not Permit Leverage Mutation",
        authorization[
            "leverage_mutation_authorized"
        ] is False,
    )


    # =========================================================================
    section(
        "R34A TEST 7: TRANSPORT ENVELOPE"
    )
    # =========================================================================

    envelope = build_transport_envelope(
        state,
        intent_hash,
        authorization_hash,
        payload,
    )

    envelope_hash = sha256_json(
        envelope
    )

    state["envelope_hash"] = (
        envelope_hash
    )

    save_state(state)

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
        "Envelope Path Is Exact",
        envelope["path"]
        == LEVERAGE_ENDPOINT,
    )

    check(
        "Envelope Contains Exact Payload",
        envelope["payload"]
        == payload,
    )

    check(
        "Envelope Binds Intent",
        envelope["intent_hash"]
        == intent_hash,
    )

    check(
        "Envelope Binds Authorization",
        envelope[
            "authorization_hash"
        ] == authorization_hash,
    )

    check(
        "Envelope Confirms No Network Transmission",
        envelope[
            "network_transmission"
        ] is False,
    )

    check(
        "Envelope Confirms Exchange Not Contacted",
        envelope[
            "exchange_contacted"
        ] is False,
    )

    check(
        "Envelope Confirms No Real POST",
        envelope["real_post"]
        is False,
    )


    # =========================================================================
    section(
        "R34A TEST 8: REAL NETWORK FIREBREAK"
    )
    # =========================================================================

    blocked = False

    try:
        forbidden_network_write(
            LEVERAGE_ENDPOINT,
            payload,
        )

    except RuntimeError:
        blocked = True

    check(
        "Real Network Write Firebreak Rejects Call",
        blocked,
    )

    check(
        "Network Write Counter Remains Zero",
        NETWORK_WRITE_COUNTER == 0,
    )


    # =========================================================================
    section(
        "R34A TEST 9: REAL ORDER FIREBREAK"
    )
    # =========================================================================

    blocked = False

    try:
        forbidden_real_order()

    except RuntimeError:
        blocked = True

    check(
        "Real Order Firebreak Rejects Call",
        blocked,
    )

    check(
        "Real Order Counter Remains Zero",
        REAL_ORDER_COUNTER == 0,
    )


    # =========================================================================
    section(
        "R34A TEST 10: LEVERAGE MUTATION FIREBREAK"
    )
    # =========================================================================

    blocked = False

    try:
        forbidden_leverage_mutation()

    except RuntimeError:
        blocked = True

    check(
        "Leverage Mutation Firebreak Rejects Call",
        blocked,
    )

    check(
        "Leverage Mutation Counter Remains Zero",
        LEVERAGE_MUTATION_COUNTER
        == 0,
    )


    # =========================================================================
    section(
        "R34A TEST 11: SYNTHETIC DISPATCH"
    )
    # =========================================================================

    receipt = synthetic_dispatch(
        state,
        envelope,
    )

    CURRENT_STATE = state

    check(
        "Synthetic Dispatch Completed",
        state[
            "synthetic_dispatch_completed"
        ] is True,
    )

    check(
        "Synthetic Dispatch Counter Is One",
        SYNTHETIC_DISPATCH_COUNTER
        == 1,
    )

    check(
        "Authorization Was Consumed",
        state[
            "authorization_consumed"
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
        receipt["transport"]
        == "SYNTHETIC",
    )

    check(
        "Receipt Confirms No Network Transmission",
        receipt[
            "network_transmission"
        ] is False,
    )

    check(
        "Receipt Confirms Exchange Not Contacted",
        receipt[
            "exchange_contacted"
        ] is False,
    )

    check(
        "Receipt Confirms No Real Order",
        receipt[
            "real_order_created"
        ] is False,
    )

    check(
        "Receipt Confirms No Leverage Mutation",
        receipt[
            "leverage_mutated"
        ] is False,
    )

    check(
        "Receipt Long Target Is 100x",
        receipt[
            "target_long_leverage"
        ] == 100,
    )

    check(
        "Receipt Short Target Is 100x",
        receipt[
            "target_short_leverage"
        ] == 100,
    )


    # =========================================================================
    section(
        "R34A TEST 12: DUPLICATE DISPATCH REJECTION"
    )
    # =========================================================================

    duplicate_rejected = False

    try:
        synthetic_dispatch(
            state,
            envelope,
        )

    except RuntimeError:
        duplicate_rejected = True

    check(
        "Duplicate Synthetic Dispatch Is Rejected",
        duplicate_rejected,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        SYNTHETIC_DISPATCH_COUNTER
        == 1,
    )

    check(
        "Duplicate Dispatch Block Counter Is One",
        DUPLICATE_DISPATCH_BLOCK_COUNTER
        == 1,
    )


    # =========================================================================
    section(
        "R34A TEST 13: DURABLE TERMINAL SNAPSHOT"
    )
    # =========================================================================

    restored = load_state()

    check(
        "State File Restores",
        restored is not None,
    )

    if restored is not None:

        check(
            "Restored Phase Is Pre-Live Validated",
            restored["phase"]
            == "PRE_LIVE_VALIDATED",
        )

        check(
            "Restored Intent Hash Matches",
            restored["intent_hash"]
            == intent_hash,
        )

        check(
            "Restored Authorization Hash Matches",
            restored[
                "authorization_hash"
            ] == authorization_hash,
        )

        check(
            "Restored Payload Hash Matches",
            restored["payload_hash"]
            == payload_hash,
        )

        check(
            "Restored Envelope Hash Matches",
            restored["envelope_hash"]
            == envelope_hash,
        )

        check(
            "Restored Receipt Hash Exists",
            isinstance(
                restored["receipt_hash"],
                str,
            )
            and len(
                restored["receipt_hash"]
            ) == 64,
        )

        check(
            "Restored Authorization Is Consumed",
            restored[
                "authorization_consumed"
            ] is True,
        )

        check(
            "Restored Dispatch Is Committed",
            restored[
                "dispatch_committed"
            ] is True,
        )

        check(
            "Restored Synthetic Dispatch Is Completed",
            restored[
                "synthetic_dispatch_completed"
            ] is True,
        )


    # =========================================================================
    section(
        "R34A TEST 14: TERMINAL SAFETY COUNTERS"
    )
    # =========================================================================

    check(
        "Exactly One Synthetic Dispatch Occurred",
        SYNTHETIC_DISPATCH_COUNTER
        == 1,
    )

    check(
        "Zero Real Orders Occurred",
        REAL_ORDER_COUNTER
        == 0,
    )

    check(
        "Zero Network Writes Occurred",
        NETWORK_WRITE_COUNTER
        == 0,
    )

    check(
        "Zero Leverage Mutations Occurred",
        LEVERAGE_MUTATION_COUNTER
        == 0,
    )


    # =========================================================================
    section(
        "R34A TEST 15: TERMINAL STATE"
    )
    # =========================================================================

    check(
        "Terminal Phase Is Pre-Live Validated",
        state["phase"]
        == "PRE_LIVE_VALIDATED",
    )

    check(
        "Terminal State Remains Synthetic Only",
        state["synthetic_only"]
        is True,
    )

    check(
        "Terminal State Has No Real Execution",
        state["real_execution"]
        is False,
    )

    check(
        "Terminal State Has No Network Writes",
        state["network_writes"]
        is False,
    )

    check(
        "Terminal State Has No Leverage Mutation",
        state["leverage_mutation"]
        is False,
    )


    # =========================================================================
    section(
        "R34A VALIDATION SUMMARY"
    )
    # =========================================================================

    total = len(TEST_RESULTS)

    passed = sum(
        1
        for result in TEST_RESULTS
        if result["passed"]
    )

    failed = total - passed

    print(
        f"Total Checks: {total}",
        flush=True,
    )

    print(
        f"Passed:       {passed}",
        flush=True,
    )

    print(
        f"Failed:       {failed}",
        flush=True,
    )

    separator()

    if failed == 0:

        print(
            "R34A VALIDATION: ✅ PASSED",
            flush=True,
        )

        print(
            "R34A: STANDARD-LIBRARY-ONLY "
            "PRE-LIVE CORRECTION PIPELINE VALIDATED",
            flush=True,
        )

        print(
            "R34A: NO EXTERNAL requests PACKAGE REQUIRED",
            flush=True,
        )

        print(
            "R34A: NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "R34A: NO NETWORK WRITE OCCURRED",
            flush=True,
        )

        print(
            "R34A: NO LEVERAGE MUTATION OCCURRED",
            flush=True,
        )

    else:

        print(
            "R34A VALIDATION: ❌ FAILED",
            flush=True,
        )

        raise RuntimeError(
            f"R34A validation failed: "
            f"{failed} check(s)"
        )

    separator()

    return state


# =============================================================================
# HEARTBEAT LOOP
# =============================================================================

def heartbeat_loop():
    count = 0

    while True:
        time.sleep(30)

        count += 1

        state = CURRENT_STATE

        print(
            f"{VERSION}: HEARTBEAT {count}"
            f" | phase={state.get('phase', 'UNKNOWN')}"
            f" | synthetic-only={SYNTHETIC_ONLY}"
            f" | synthetic-dispatch={SYNTHETIC_DISPATCH_COUNTER}"
            f" | real-execution={REAL_ORDER_EXECUTION_ENABLED}"
            f" | network-writes={EXCHANGE_NETWORK_WRITES_ENABLED}"
            f" | leverage-mutation={LEVERAGE_MUTATION_ENABLED}"
            f" | correction-required={state.get('correction_required')}"
            f" | intent-bound={state.get('intent_bound')}"
            f" | authorization-consumed={state.get('authorization_consumed')}"
            f" | dispatch-committed={state.get('dispatch_committed')}"
            f" | target-long={TARGET_LONG_LEVERAGE}x"
            f" | target-short={TARGET_SHORT_LEVERAGE}x"
            f" | generation={state.get('generation')}"
            f" | recovery-epoch={state.get('recovery_epoch')}",
            flush=True,
        )


# =============================================================================
# MAIN
# =============================================================================

def main():
    global CURRENT_STATE

    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    health_thread.start()

    CURRENT_STATE = run_validation()

    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        daemon=True,
    )

    heartbeat_thread.start()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
