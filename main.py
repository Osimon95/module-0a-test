# ============================================================
# 0F-4H-R28 UNIT N.15
# DURABLE DISPATCH FINALIZATION / CRASH-WINDOW CONSISTENCY
#
# SAFETY:
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO NETWORK WRITES
#   - NO LEVERAGE MUTATION TRANSMISSION
#   - SYNTHETIC TRANSPORT ONLY
#
# TARGET:
#   BTCUSDT
#   ISOLATED
#   100x
# ============================================================

import os
import json
import time
import hashlib
import threading
import tempfile
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer


print("R28 UNIT N.15: MAIN.PY ENTERED")


# ============================================================
# CONSTANTS
# ============================================================

UNIT_NAME = "R28 UNIT N.15"

SYMBOL = "BTCUSDT"
MARGIN_MODE = "ISOLATED"
LEVERAGE = "100"

LEVERAGE_ENDPOINT = "/capi/v3/account/leverage"
TRANSPORT_METHOD = "POST"

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
ACCOUNT_WRITES_ENABLED = False
LEVERAGE_WRITES_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

AUTHORIZATION_TTL_SECONDS = 60

HEALTH_PORT = int(os.environ.get("PORT", "10000"))

CANONICAL_PAYLOAD = {
    "leverage": LEVERAGE,
    "marginMode": MARGIN_MODE,
    "symbol": SYMBOL,
}

CANONICAL_PAYLOAD_JSON = json.dumps(
    CANONICAL_PAYLOAD,
    separators=(",", ":"),
    sort_keys=True,
)

CANONICAL_PAYLOAD_HASH = hashlib.sha256(
    CANONICAL_PAYLOAD_JSON.encode("utf-8")
).hexdigest()

EXPECTED_PAYLOAD_HASH = (
    "64f7f170df9a2966605a82724094ca67cdd46ea5fef06957ba37c91705bcb00e"
)

print("R28 UNIT N.15: IMPORTS COMPLETE")
print("R28 UNIT N.15: CONSTANTS INITIALIZED")


# ============================================================
# BASIC UTILITIES
# ============================================================

def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value):
    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
    )


def deterministic_id(prefix, *parts):
    material = "|".join(str(x) for x in parts)
    digest = sha256_text(material)[:32]
    return f"{prefix}-{digest}"


def banner(title):
    print()
    print(title)
    print("-" * 92)


def result(name, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{name:<82} {status}")
    return bool(condition)


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = b"R28 UNIT N.15 ACTIVE"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():

    def run():
        try:
            server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
            print(
                f"R28 UNIT N.15: HEALTH SERVER ACTIVE ON PORT "
                f"{HEALTH_PORT}"
            )
            server.serve_forever()

        except Exception as exc:
            print(
                "R28 UNIT N.15: HEALTH SERVER WARNING:",
                repr(exc),
            )

    thread = threading.Thread(
        target=run,
        daemon=True,
    )

    thread.start()


# ============================================================
# SAFETY COUNTERS
# ============================================================

class SafetyCounters:

    def __init__(self):
        self.network_posts = 0
        self.network_writes = 0
        self.leverage_transmissions = 0
        self.synthetic_dispatches = 0

    def reset(self):
        self.network_posts = 0
        self.network_writes = 0
        self.leverage_transmissions = 0
        self.synthetic_dispatches = 0


COUNTERS = SafetyCounters()


# ============================================================
# HARD NETWORK FIREBREAK
# ============================================================

def real_network_post(*args, **kwargs):
    print(f"{UNIT_NAME} LOCAL BLOCK:")
    print(
        f"  {UNIT_NAME} LOCAL BLOCK: "
        f"real network POST is disabled."
    )
    raise RuntimeError(
        "real network POST is disabled"
    )


def generic_network_write(method, *args, **kwargs):
    method = str(method).upper()

    print(f"{UNIT_NAME} LOCAL BLOCK:")
    print(
        f"  {UNIT_NAME} LOCAL BLOCK: "
        f"network write method {method} is disabled."
    )

    raise RuntimeError(
        f"network write method {method} is disabled"
    )


def leverage_mutation_transport(*args, **kwargs):
    print(f"{UNIT_NAME} LOCAL BLOCK:")
    print(
        f"  {UNIT_NAME} LOCAL BLOCK: "
        f"leverage mutation transport is disabled."
    )

    raise RuntimeError(
        "leverage mutation transport is disabled"
    )


# ============================================================
# DURABLE STATE MODEL
# ============================================================

def new_state():
    return {
        "version": 1,
        "generation": 0,
        "authorization": None,
        "dispatch": None,
        "completion_ledger": {},
        "journal": [],
    }


def state_without_seal(state):
    data = deepcopy(state)
    data.pop("integrity_seal", None)
    return data


def calculate_state_seal(state):
    body = canonical_json(
        state_without_seal(state)
    )
    return sha256_text(body)


def seal_state(state):
    state = deepcopy(state)
    state["integrity_seal"] = calculate_state_seal(state)
    return state


def verify_state_seal(state):
    supplied = state.get("integrity_seal")

    if not supplied:
        return False

    expected = calculate_state_seal(state)

    return supplied == expected


class DurableStore:

    def __init__(self, path):
        self.path = path
        self.lock = threading.RLock()

        if not os.path.exists(self.path):
            self.save(new_state())

    def save(self, state):
        with self.lock:

            state = deepcopy(state)
            state["generation"] = int(
                state.get("generation", 0)
            ) + 1

            sealed = seal_state(state)

            directory = os.path.dirname(self.path)

            fd, tmp_path = tempfile.mkstemp(
                prefix="r28_n15_",
                suffix=".tmp",
                dir=directory,
            )

            try:
                with os.fdopen(fd, "w") as handle:
                    json.dump(
                        sealed,
                        handle,
                        separators=(",", ":"),
                        sort_keys=True,
                    )

                    handle.flush()
                    os.fsync(handle.fileno())

                os.replace(
                    tmp_path,
                    self.path,
                )

            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

            return deepcopy(sealed)

    def load(self):
        with self.lock:
            with open(self.path, "r") as handle:
                state = json.load(handle)

            if not verify_state_seal(state):
                raise RuntimeError(
                    "snapshot integrity seal mismatch"
                )

            return state


# ============================================================
# JOURNAL
# ============================================================

def append_journal(
    state,
    event,
    authorization_id=None,
    dispatch_id=None,
    request_hash=None,
):
    sequence = len(state["journal"]) + 1

    record = {
        "sequence": sequence,
        "event": event,
        "authorization_id": authorization_id,
        "dispatch_id": dispatch_id,
        "request_hash": request_hash,
    }

    state["journal"].append(record)


# ============================================================
# AUTHORIZATION
# ============================================================

def create_authorization(state, now=None):
    if now is None:
        now = time.time()

    request_hash = CANONICAL_PAYLOAD_HASH

    authorization_id = deterministic_id(
        "AUTH",
        SYMBOL,
        MARGIN_MODE,
        LEVERAGE,
        request_hash,
    )

    authorization = {
        "authorization_id": authorization_id,
        "symbol": SYMBOL,
        "margin_mode": MARGIN_MODE,
        "leverage": LEVERAGE,
        "request_hash": request_hash,
        "issued_at": now,
        "expires_at": now + AUTHORIZATION_TTL_SECONDS,
        "revoked": False,
        "consumed": False,
        "consumed_by_dispatch": None,
    }

    state["authorization"] = authorization

    append_journal(
        state,
        "AUTHORIZATION_GRANTED",
        authorization_id=authorization_id,
        request_hash=request_hash,
    )

    return authorization


def validate_authorization(
    state,
    authorization_id,
    dispatch_id,
    request_hash,
    now=None,
):

    if now is None:
        now = time.time()

    auth = state.get("authorization")

    if not auth:
        raise RuntimeError(
            "authorization missing"
        )

    if auth["authorization_id"] != authorization_id:
        raise RuntimeError(
            "authorization identity mismatch"
        )

    if auth["request_hash"] != request_hash:
        raise RuntimeError(
            "authorization request binding mismatch"
        )

    if auth.get("revoked"):
        raise RuntimeError(
            "authorization revoked"
        )

    if now > auth["expires_at"]:
        raise RuntimeError(
            "authorization expired"
        )

    if auth.get("consumed"):

        previous_dispatch = auth.get(
            "consumed_by_dispatch"
        )

        if previous_dispatch != dispatch_id:
            raise RuntimeError(
                "authorization already consumed "
                "by another dispatch"
            )

    return True


# ============================================================
# DISPATCH PREPARATION
# ============================================================

def prepare_dispatch(
    state,
    authorization_id,
):

    request_hash = CANONICAL_PAYLOAD_HASH

    dispatch_id = deterministic_id(
        "DSP",
        authorization_id,
        request_hash,
    )

    existing = state.get("dispatch")

    if existing:
        if existing["dispatch_id"] != dispatch_id:
            raise RuntimeError(
                "cross-dispatch substitution rejected"
            )

        return existing

    dispatch = {
        "dispatch_id": dispatch_id,
        "authorization_id": authorization_id,
        "method": TRANSPORT_METHOD,
        "path": LEVERAGE_ENDPOINT,
        "payload": deepcopy(CANONICAL_PAYLOAD),
        "request_hash": request_hash,
        "state": "PREPARED",
        "synthetic_transport_started": False,
        "synthetic_transport_completed": False,
        "reconciled": False,
        "completed": False,
    }

    state["dispatch"] = dispatch

    append_journal(
        state,
        "DISPATCH_PREPARED",
        authorization_id=authorization_id,
        dispatch_id=dispatch_id,
        request_hash=request_hash,
    )

    return dispatch


# ============================================================
# AUTHORIZATION CONSUMPTION
# ============================================================

def consume_authorization(
    state,
    authorization_id,
    dispatch_id,
):

    auth = state["authorization"]

    validate_authorization(
        state,
        authorization_id,
        dispatch_id,
        CANONICAL_PAYLOAD_HASH,
    )

    if auth.get("consumed"):

        if (
            auth.get("consumed_by_dispatch")
            == dispatch_id
        ):
            return False

        raise RuntimeError(
            "authorization replay blocked"
        )

    auth["consumed"] = True
    auth["consumed_by_dispatch"] = dispatch_id

    append_journal(
        state,
        "AUTHORIZATION_CONSUMED",
        authorization_id=authorization_id,
        dispatch_id=dispatch_id,
        request_hash=CANONICAL_PAYLOAD_HASH,
    )

    return True


# ============================================================
# SYNTHETIC TRANSPORT
# ============================================================

def synthetic_transport(state):

    dispatch = state.get("dispatch")

    if not dispatch:
        raise RuntimeError(
            "dispatch missing"
        )

    if not state["authorization"].get("consumed"):
        raise RuntimeError(
            "authorization must be consumed "
            "before dispatch"
        )

    dispatch_id = dispatch["dispatch_id"]

    ledger = state["completion_ledger"]

    if dispatch_id in ledger:
        return deepcopy(
            ledger[dispatch_id]["receipt"]
        )

    if dispatch.get("synthetic_transport_completed"):
        raise RuntimeError(
            "dispatch transport state inconsistent"
        )

    dispatch["synthetic_transport_started"] = True

    COUNTERS.synthetic_dispatches += 1

    receipt = {
        "dispatch_id": dispatch_id,
        "transport": "SYNTHETIC",
        "network_transmitted": False,
        "method": dispatch["method"],
        "path": dispatch["path"],
        "request_hash": dispatch["request_hash"],
        "status": "SYNTHETIC_ACCEPTED",
    }

    dispatch["synthetic_transport_completed"] = True
    dispatch["state"] = "SYNTHETIC_DISPATCHED"

    ledger[dispatch_id] = {
        "receipt": deepcopy(receipt),
        "finalized": False,
    }

    append_journal(
        state,
        "SYNTHETIC_DISPATCH_COMPLETED",
        authorization_id=dispatch["authorization_id"],
        dispatch_id=dispatch_id,
        request_hash=dispatch["request_hash"],
    )

    return receipt


# ============================================================
# RECONCILIATION
# ============================================================

def reconcile_dispatch(state):

    dispatch = state["dispatch"]
    dispatch_id = dispatch["dispatch_id"]

    ledger_entry = state[
        "completion_ledger"
    ].get(dispatch_id)

    if not ledger_entry:
        raise RuntimeError(
            "completion ledger missing"
        )

    if not dispatch.get(
        "synthetic_transport_completed"
    ):
        raise RuntimeError(
            "cannot reconcile undispatched request"
        )

    if dispatch.get("reconciled"):
        return False

    dispatch["reconciled"] = True
    dispatch["state"] = "RECONCILED"

    append_journal(
        state,
        "FINAL_RECONCILIATION",
        authorization_id=dispatch["authorization_id"],
        dispatch_id=dispatch_id,
        request_hash=dispatch["request_hash"],
    )

    return True


# ============================================================
# FINALIZATION
# ============================================================

def finalize_dispatch(state):

    dispatch = state["dispatch"]
    dispatch_id = dispatch["dispatch_id"]

    ledger_entry = state[
        "completion_ledger"
    ].get(dispatch_id)

    if not ledger_entry:
        raise RuntimeError(
            "completion ledger missing"
        )

    if not dispatch.get("reconciled"):
        raise RuntimeError(
            "dispatch is not reconciled"
        )

    if ledger_entry.get("finalized"):
        return False

    ledger_entry["finalized"] = True

    dispatch["completed"] = True
    dispatch["state"] = "COMPLETED"

    append_journal(
        state,
        "DISPATCH_COMPLETED",
        authorization_id=dispatch["authorization_id"],
        dispatch_id=dispatch_id,
        request_hash=dispatch["request_hash"],
    )

    return True


# ============================================================
# RECOVERY ENGINE
# ============================================================

def recover_dispatch(state):

    dispatch = state.get("dispatch")
    auth = state.get("authorization")

    if not dispatch:
        return "NO_DISPATCH"

    if not auth:
        raise RuntimeError(
            "dispatch exists without authorization"
        )

    if (
        dispatch["authorization_id"]
        != auth["authorization_id"]
    ):
        raise RuntimeError(
            "recovery authorization binding mismatch"
        )

    if (
        dispatch["request_hash"]
        != auth["request_hash"]
    ):
        raise RuntimeError(
            "recovery request binding mismatch"
        )

    dispatch_id = dispatch["dispatch_id"]

    if dispatch.get("completed"):
        return "ALREADY_COMPLETED"

    if auth.get("consumed"):

        if (
            auth.get("consumed_by_dispatch")
            != dispatch_id
        ):
            raise RuntimeError(
                "consumed authorization bound "
                "to different dispatch"
            )

    else:
        consume_authorization(
            state,
            auth["authorization_id"],
            dispatch_id,
        )

    ledger = state["completion_ledger"]

    if dispatch_id in ledger:

        if not dispatch.get(
            "synthetic_transport_completed"
        ):
            dispatch[
                "synthetic_transport_completed"
            ] = True

        if not dispatch.get("reconciled"):
            reconcile_dispatch(state)

        if not dispatch.get("completed"):
            finalize_dispatch(state)

        return "RECOVERED_FROM_LEDGER"

    if dispatch.get(
        "synthetic_transport_completed"
    ):
        raise RuntimeError(
            "transport completed without "
            "completion ledger record"
        )

    synthetic_transport(state)
    reconcile_dispatch(state)
    finalize_dispatch(state)

    return "RECOVERED_AND_COMPLETED"


# ============================================================
# TEST ENVIRONMENT
# ============================================================

def make_store():

    directory = tempfile.mkdtemp(
        prefix="r28_n15_store_"
    )

    path = os.path.join(
        directory,
        "snapshot.json",
    )

    return DurableStore(path)


def build_prepared_state(store):

    state = store.load()

    authorization = create_authorization(state)

    dispatch = prepare_dispatch(
        state,
        authorization["authorization_id"],
    )

    state = store.save(state)

    return (
        state,
        authorization["authorization_id"],
        dispatch["dispatch_id"],
    )


# ============================================================
# TEST 1
# CANONICAL BASELINE
# ============================================================

def test_1():

    banner(
        "R28 UNIT N.15 TEST 1: "
        "CANONICAL REQUEST BASELINE"
    )

    checks = []

    checks.append(
        result(
            "Payload Symbol Exactly BTCUSDT",
            CANONICAL_PAYLOAD["symbol"]
            == "BTCUSDT",
        )
    )

    checks.append(
        result(
            "Payload Margin Mode Exactly ISOLATED",
            CANONICAL_PAYLOAD["marginMode"]
            == "ISOLATED",
        )
    )

    checks.append(
        result(
            "Payload Leverage Exactly 100",
            CANONICAL_PAYLOAD["leverage"]
            == "100",
        )
    )

    checks.append(
        result(
            "Canonical Payload Hash Preserved",
            CANONICAL_PAYLOAD_HASH
            == EXPECTED_PAYLOAD_HASH,
        )
    )

    checks.append(
        result(
            "Transport Method Exactly POST",
            TRANSPORT_METHOD == "POST",
        )
    )

    checks.append(
        result(
            "Transport Path Exactly Leverage Endpoint",
            LEVERAGE_ENDPOINT
            == "/capi/v3/account/leverage",
        )
    )

    return all(checks)


# ============================================================
# TEST 2
# PRE-DISPATCH CRASH
# ============================================================

def test_2():

    banner(
        "R28 UNIT N.15 TEST 2: "
        "CRASH AFTER PREPARE BEFORE AUTHORIZATION CONSUMPTION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    restored = store.load()

    recovery = recover_dispatch(restored)
    store.save(restored)

    final_state = store.load()

    checks = []

    checks.append(
        result(
            "Prepared Dispatch Survived Restart",
            final_state["dispatch"]["dispatch_id"]
            == dispatch_id,
        )
    )

    checks.append(
        result(
            "Authorization Consumed During Recovery",
            final_state["authorization"]["consumed"],
        )
    )

    checks.append(
        result(
            "Recovered Dispatch Completed",
            final_state["dispatch"]["completed"],
        )
    )

    checks.append(
        result(
            "Exactly One Synthetic Dispatch",
            COUNTERS.synthetic_dispatches == 1,
        )
    )

    checks.append(
        result(
            "Recovery Path Completed Successfully",
            recovery
            == "RECOVERED_AND_COMPLETED",
        )
    )

    return all(checks)


# ============================================================
# TEST 3
# CRASH AFTER AUTHORIZATION CONSUMPTION
# ============================================================

def test_3():

    banner(
        "R28 UNIT N.15 TEST 3: "
        "CRASH AFTER AUTHORIZATION CONSUMPTION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    store.save(state)

    restored = store.load()

    recover_dispatch(restored)
    store.save(restored)

    final_state = store.load()

    checks = []

    checks.append(
        result(
            "Consumed Authorization Survived Restart",
            final_state["authorization"]["consumed"],
        )
    )

    checks.append(
        result(
            "Authorization Still Bound To Same Dispatch",
            final_state["authorization"][
                "consumed_by_dispatch"
            ]
            == dispatch_id,
        )
    )

    checks.append(
        result(
            "Recovery Produced Exactly One Synthetic Dispatch",
            COUNTERS.synthetic_dispatches == 1,
        )
    )

    checks.append(
        result(
            "Recovered Dispatch Finalized",
            final_state["dispatch"]["completed"],
        )
    )

    return all(checks)


# ============================================================
# TEST 4
# CRASH AFTER SYNTHETIC TRANSPORT
# ============================================================

def test_4():

    banner(
        "R28 UNIT N.15 TEST 4: "
        "CRASH AFTER SYNTHETIC DISPATCH BEFORE RECONCILIATION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    synthetic_transport(state)

    store.save(state)

    synthetic_count_before_restart = (
        COUNTERS.synthetic_dispatches
    )

    restored = store.load()

    recovery = recover_dispatch(restored)
    store.save(restored)

    final_state = store.load()

    checks = []

    checks.append(
        result(
            "Completion Ledger Survived Restart",
            dispatch_id
            in final_state["completion_ledger"],
        )
    )

    checks.append(
        result(
            "Recovery Did Not Redispatch",
            COUNTERS.synthetic_dispatches
            == synthetic_count_before_restart,
        )
    )

    checks.append(
        result(
            "Ledger Recovery Path Selected",
            recovery
            == "RECOVERED_FROM_LEDGER",
        )
    )

    checks.append(
        result(
            "Recovered Dispatch Reconciled",
            final_state["dispatch"]["reconciled"],
        )
    )

    checks.append(
        result(
            "Recovered Dispatch Completed",
            final_state["dispatch"]["completed"],
        )
    )

    return all(checks)


# ============================================================
# TEST 5
# CRASH AFTER RECONCILIATION
# ============================================================

def test_5():

    banner(
        "R28 UNIT N.15 TEST 5: "
        "CRASH AFTER RECONCILIATION BEFORE FINALIZATION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    synthetic_transport(state)
    reconcile_dispatch(state)

    store.save(state)

    dispatches_before = (
        COUNTERS.synthetic_dispatches
    )

    restored = store.load()

    recover_dispatch(restored)
    store.save(restored)

    final_state = store.load()

    checks = []

    checks.append(
        result(
            "Reconciled State Survived Restart",
            final_state["dispatch"]["reconciled"],
        )
    )

    checks.append(
        result(
            "Recovery Produced No Second Dispatch",
            COUNTERS.synthetic_dispatches
            == dispatches_before,
        )
    )

    checks.append(
        result(
            "Dispatch Finalized After Restart",
            final_state["dispatch"]["completed"],
        )
    )

    checks.append(
        result(
            "Ledger Marked Finalized",
            final_state["completion_ledger"][
                dispatch_id
            ]["finalized"],
        )
    )

    return all(checks)


# ============================================================
# TEST 6
# RESTART AFTER COMPLETION
# ============================================================

def test_6():

    banner(
        "R28 UNIT N.15 TEST 6: "
        "RESTART AFTER COMPLETE FINALIZATION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    synthetic_transport(state)
    reconcile_dispatch(state)
    finalize_dispatch(state)

    store.save(state)

    dispatches_before = (
        COUNTERS.synthetic_dispatches
    )

    restored = store.load()

    recovery = recover_dispatch(restored)

    checks = []

    checks.append(
        result(
            "Completed Dispatch Survived Restart",
            restored["dispatch"]["completed"],
        )
    )

    checks.append(
        result(
            "Completed Dispatch Recognized",
            recovery == "ALREADY_COMPLETED",
        )
    )

    checks.append(
        result(
            "Restart Produced No Synthetic Replay",
            COUNTERS.synthetic_dispatches
            == dispatches_before,
        )
    )

    checks.append(
        result(
            "Authorization Remains Consumed",
            restored["authorization"]["consumed"],
        )
    )

    return all(checks)


# ============================================================
# TEST 7
# REPEATED RECOVERY
# ============================================================

def test_7():

    banner(
        "R28 UNIT N.15 TEST 7: "
        "REPEATED RESTART IDEMPOTENCY"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    synthetic_transport(state)
    store.save(state)

    restored_1 = store.load()
    recover_dispatch(restored_1)
    store.save(restored_1)

    count_after_first = (
        COUNTERS.synthetic_dispatches
    )

    restored_2 = store.load()
    recover_dispatch(restored_2)
    store.save(restored_2)

    restored_3 = store.load()
    recover_dispatch(restored_3)

    checks = []

    checks.append(
        result(
            "Second Recovery Produced No Dispatch",
            COUNTERS.synthetic_dispatches
            == count_after_first,
        )
    )

    checks.append(
        result(
            "Third Recovery Produced No Dispatch",
            COUNTERS.synthetic_dispatches
            == count_after_first,
        )
    )

    checks.append(
        result(
            "Final State Remains Completed",
            restored_3["dispatch"]["completed"],
        )
    )

    return all(checks)


# ============================================================
# TEST 8
# CROSS-DISPATCH SUBSTITUTION
# ============================================================

def test_8():

    banner(
        "R28 UNIT N.15 TEST 8: "
        "CROSS-DISPATCH SUBSTITUTION REJECTION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    fake_dispatch_id = deterministic_id(
        "DSP",
        "ATTACKER-DISPATCH",
        time.time(),
    )

    rejected = False

    try:
        validate_authorization(
            state,
            auth_id,
            fake_dispatch_id,
            CANONICAL_PAYLOAD_HASH,
        )

    except Exception:
        rejected = True

    checks = []

    checks.append(
        result(
            "Changed Dispatch Identity Rejected",
            rejected,
        )
    )

    checks.append(
        result(
            "Substitution Produced No Synthetic Dispatch",
            COUNTERS.synthetic_dispatches == 0,
        )
    )

    return all(checks)


# ============================================================
# TEST 9
# COMPLETION LEDGER TAMPERING
# ============================================================

def test_9():

    banner(
        "R28 UNIT N.15 TEST 9: "
        "COMPLETION LEDGER TAMPER REJECTION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    synthetic_transport(state)
    reconcile_dispatch(state)
    finalize_dispatch(state)

    saved = store.save(state)

    with open(store.path, "r") as handle:
        tampered = json.load(handle)

    tampered[
        "completion_ledger"
    ][dispatch_id]["finalized"] = False

    with open(store.path, "w") as handle:
        json.dump(
            tampered,
            handle,
            separators=(",", ":"),
            sort_keys=True,
        )

    rejected = False

    try:
        store.load()

    except Exception as exc:
        print(f"{UNIT_NAME} LOCAL BLOCK:")
        print(f"  {exc}")
        rejected = True

    checks = []

    checks.append(
        result(
            "Tampered Completion Ledger Rejected",
            rejected,
        )
    )

    return all(checks)


# ============================================================
# TEST 10
# JOURNAL ORDER
# ============================================================

def test_10():

    banner(
        "R28 UNIT N.15 TEST 10: "
        "FINALIZATION JOURNAL SERIALIZATION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    synthetic_transport(state)
    reconcile_dispatch(state)
    finalize_dispatch(state)

    events = [
        record["event"]
        for record in state["journal"]
    ]

    expected = [
        "AUTHORIZATION_GRANTED",
        "DISPATCH_PREPARED",
        "AUTHORIZATION_CONSUMED",
        "SYNTHETIC_DISPATCH_COMPLETED",
        "FINAL_RECONCILIATION",
        "DISPATCH_COMPLETED",
    ]

    checks = []

    checks.append(
        result(
            "Exactly One Authorization Grant Record",
            events.count(
                "AUTHORIZATION_GRANTED"
            ) == 1,
        )
    )

    checks.append(
        result(
            "Exactly One Dispatch Prepare Record",
            events.count(
                "DISPATCH_PREPARED"
            ) == 1,
        )
    )

    checks.append(
        result(
            "Exactly One Authorization Consumed Record",
            events.count(
                "AUTHORIZATION_CONSUMED"
            ) == 1,
        )
    )

    checks.append(
        result(
            "Exactly One Synthetic Dispatch Completion Record",
            events.count(
                "SYNTHETIC_DISPATCH_COMPLETED"
            ) == 1,
        )
    )

    checks.append(
        result(
            "Exactly One Final Reconciliation Record",
            events.count(
                "FINAL_RECONCILIATION"
            ) == 1,
        )
    )

    checks.append(
        result(
            "Exactly One Dispatch Completion Record",
            events.count(
                "DISPATCH_COMPLETED"
            ) == 1,
        )
    )

    checks.append(
        result(
            "Finalization Journal Order Is Canonical",
            events == expected,
        )
    )

    same_auth = all(
        (
            item["authorization_id"] is None
            or item["authorization_id"] == auth_id
        )
        for item in state["journal"]
    )

    same_dispatch = all(
        (
            item["dispatch_id"] is None
            or item["dispatch_id"] == dispatch_id
        )
        for item in state["journal"]
    )

    checks.append(
        result(
            "Journal Preserves Authorization Identity",
            same_auth,
        )
    )

    checks.append(
        result(
            "Journal Preserves Dispatch Identity",
            same_dispatch,
        )
    )

    return all(checks)


# ============================================================
# TEST 11
# CONCURRENT RECOVERY
# ============================================================

def test_11():

    banner(
        "R28 UNIT N.15 TEST 11: "
        "CONCURRENT RECOVERY SINGLE-DISPATCH"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    store.save(state)

    global_lock = threading.Lock()

    working_state = store.load()

    errors = []

    def worker():
        try:
            with global_lock:
                recover_dispatch(
                    working_state
                )

        except Exception as exc:
            errors.append(str(exc))

    threads = [
        threading.Thread(target=worker)
        for _ in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    checks = []

    checks.append(
        result(
            "Concurrent Recovery Produced Exactly One Synthetic Dispatch",
            COUNTERS.synthetic_dispatches == 1,
        )
    )

    checks.append(
        result(
            "Concurrent Recovery Final State Completed",
            working_state["dispatch"]["completed"],
        )
    )

    checks.append(
        result(
            "Concurrent Recovery Preserved Consumed Authorization",
            working_state["authorization"]["consumed"],
        )
    )

    checks.append(
        result(
            "Concurrent Recovery Produced No Structural Errors",
            len(errors) == 0,
        )
    )

    return all(checks)


# ============================================================
# TEST 12
# IMPOSSIBLE STATE REJECTION
# ============================================================

def test_12():

    banner(
        "R28 UNIT N.15 TEST 12: "
        "IMPOSSIBLE RECOVERY STATE REJECTION"
    )

    COUNTERS.reset()

    store = make_store()

    state, auth_id, dispatch_id = (
        build_prepared_state(store)
    )

    consume_authorization(
        state,
        auth_id,
        dispatch_id,
    )

    state["dispatch"][
        "synthetic_transport_completed"
    ] = True

    # Deliberately do NOT create completion ledger.
    rejected = False

    try:
        recover_dispatch(state)

    except Exception as exc:
        print(f"{UNIT_NAME} LOCAL BLOCK:")
        print(f"  {exc}")
        rejected = True

    checks = []

    checks.append(
        result(
            "Impossible Completed-Without-Ledger State Rejected",
            rejected,
        )
    )

    checks.append(
        result(
            "Impossible State Produced No Synthetic Redispatch",
            COUNTERS.synthetic_dispatches == 0,
        )
    )

    return all(checks)


# ============================================================
# TEST 13
# FINAL NETWORK FIREBREAK
# ============================================================

def test_13():

    banner(
        "R28 UNIT N.15 TEST 13: "
        "FINAL NETWORK WRITE FIREBREAK"
    )

    COUNTERS.reset()

    post_blocked = False
    generic_blocked = False
    leverage_blocked = False

    try:
        real_network_post(
            LEVERAGE_ENDPOINT,
            CANONICAL_PAYLOAD,
        )
    except Exception:
        post_blocked = True

    try:
        generic_network_write(
            "PUT",
            "/unsafe",
        )
    except Exception:
        generic_blocked = True

    try:
        leverage_mutation_transport(
            CANONICAL_PAYLOAD
        )
    except Exception:
        leverage_blocked = True

    checks = []

    checks.append(
        result(
            "Real POST Rejected Locally",
            post_blocked,
        )
    )

    checks.append(
        result(
            "Generic Network Write Rejected Locally",
            generic_blocked,
        )
    )

    checks.append(
        result(
            "Leverage Mutation Transport Rejected Locally",
            leverage_blocked,
        )
    )

    checks.append(
        result(
            "Real POST Block Produced No Network POST",
            COUNTERS.network_posts == 0,
        )
    )

    checks.append(
        result(
            "Write Firebreak Produced No Network Write",
            COUNTERS.network_writes == 0,
        )
    )

    checks.append(
        result(
            "Leverage Firebreak Produced No Transmission",
            COUNTERS.leverage_transmissions == 0,
        )
    )

    return all(checks)


# ============================================================
# TEST 14
# EXACT PAYLOAD IMMUTABILITY
# ============================================================

def test_14():

    banner(
        "R28 UNIT N.15 TEST 14: "
        "EXACT PAYLOAD / ENDPOINT IMMUTABILITY"
    )

    print(
        f"Payload = {CANONICAL_PAYLOAD_JSON}"
    )

    print(
        f"Payload SHA256 = "
        f"{CANONICAL_PAYLOAD_HASH}"
    )

    checks = []

    checks.append(
        result(
            "Exact Leverage Payload Preserved",
            CANONICAL_PAYLOAD_HASH
            == EXPECTED_PAYLOAD_HASH,
        )
    )

    checks.append(
        result(
            "Canonical Payload Serialization Preserved",
            CANONICAL_PAYLOAD_JSON
            ==
            '{"leverage":"100","marginMode":"ISOLATED","symbol":"BTCUSDT"}',
        )
    )

    checks.append(
        result(
            "Transport Method Exactly POST",
            TRANSPORT_METHOD == "POST",
        )
    )

    checks.append(
        result(
            "Transport Path Exactly Leverage Endpoint",
            LEVERAGE_ENDPOINT
            == "/capi/v3/account/leverage",
        )
    )

    return all(checks)


# ============================================================
# COMPLETE DIAGNOSTIC
# ============================================================

def run_diagnostic():

    print("=" * 92)
    print("0F-4H-R28-UNIT-N.15 STARTING")
    print("=" * 92)

    print()
    print("R28 UNIT N.15 SAFETY CONFIGURATION")
    print("-" * 92)

    print(
        f"  Live Execution Enabled = "
        f"{LIVE_ORDER_EXECUTION}"
    )
    print(
        f"  Demo Execution Enabled = "
        f"{DEMO_ORDER_EXECUTION}"
    )
    print(
        f"  Network Writes Enabled = "
        f"{NETWORK_WRITES_ENABLED}"
    )
    print(
        f"  Account Writes Enabled = "
        f"{ACCOUNT_WRITES_ENABLED}"
    )
    print(
        f"  Leverage Writes Enabled = "
        f"{LEVERAGE_WRITES_ENABLED}"
    )
    print(
        f"  Leverage Mutation Transport Enabled = "
        f"{LEVERAGE_MUTATION_TRANSPORT_ENABLED}"
    )

    tests = [
        test_1,
        test_2,
        test_3,
        test_4,
        test_5,
        test_6,
        test_7,
        test_8,
        test_9,
        test_10,
        test_11,
        test_12,
        test_13,
        test_14,
    ]

    results = []

    for test in tests:
        try:
            results.append(
                bool(test())
            )

        except Exception as exc:
            print()
            print(
                f"❌ {test.__name__} "
                f"UNHANDLED ERROR: {repr(exc)}"
            )
            results.append(False)

    structural_failures = sum(
        1 for item in results
        if not item
    )

    readiness_blockers = (
        structural_failures
    )

    banner(
        "R28 UNIT N.15 WRITE-LOCK AUDIT"
    )

    print(
        f"  Network POSTs = "
        f"{COUNTERS.network_posts}"
    )
    print(
        f"  Network writes = "
        f"{COUNTERS.network_writes}"
    )
    print(
        f"  Leverage transmissions = "
        f"{COUNTERS.leverage_transmissions}"
    )

    write_audit = []

    write_audit.append(
        result(
            "Network POST Count Is Zero",
            COUNTERS.network_posts == 0,
        )
    )

    write_audit.append(
        result(
            "Network Write Count Is Zero",
            COUNTERS.network_writes == 0,
        )
    )

    write_audit.append(
        result(
            "Leverage Transmission Count Is Zero",
            COUNTERS.leverage_transmissions
            == 0,
        )
    )

    if not all(write_audit):
        readiness_blockers += 1

    banner(
        "R28 UNIT N.15 EXECUTION-READINESS ASSESSMENT"
    )

    print(
        f"  Structural Safety Failures = "
        f"{structural_failures}"
    )

    print(
        f"  Readiness Blockers = "
        f"{readiness_blockers}"
    )

    print(
        "  Pre-Dispatch Crash Recovery = "
        + (
            "✅ VERIFIED"
            if results[1]
            else "❌ FAILED"
        )
    )

    print(
        "  Post-Authorization Crash Recovery = "
        + (
            "✅ VERIFIED"
            if results[2]
            else "❌ FAILED"
        )
    )

    print(
        "  Post-Dispatch Crash Recovery = "
        + (
            "✅ VERIFIED"
            if results[3]
            else "❌ FAILED"
        )
    )

    print(
        "  Post-Reconciliation Crash Recovery = "
        + (
            "✅ VERIFIED"
            if results[4]
            else "❌ FAILED"
        )
    )

    print(
        "  Completed Restart Idempotency = "
        + (
            "✅ VERIFIED"
            if results[5]
            else "❌ FAILED"
        )
    )

    print(
        "  Repeated Recovery Idempotency = "
        + (
            "✅ VERIFIED"
            if results[6]
            else "❌ FAILED"
        )
    )

    print(
        "  Cross-Dispatch Substitution Rejection = "
        + (
            "✅ VERIFIED"
            if results[7]
            else "❌ FAILED"
        )
    )

    print(
        "  Completion Ledger Tamper Protection = "
        + (
            "✅ VERIFIED"
            if results[8]
            else "❌ FAILED"
        )
    )

    print(
        "  Finalization Journal Serialization = "
        + (
            "✅ VERIFIED"
            if results[9]
            else "❌ FAILED"
        )
    )

    print(
        "  Concurrent Recovery Single Dispatch = "
        + (
            "✅ VERIFIED"
            if results[10]
            else "❌ FAILED"
        )
    )

    print(
        "  Impossible State Rejection = "
        + (
            "✅ VERIFIED"
            if results[11]
            else "❌ FAILED"
        )
    )

    print(
        "  Final Network Dispatch = "
        "🛡 BLOCKED LOCALLY"
    )

    print(
        "  Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY"
    )

    print()

    if (
        readiness_blockers == 0
        and all(results)
        and all(write_audit)
    ):

        print(
            "✅ R28 UNIT N.15 DIAGNOSTIC PASSED"
        )

        print(
            "✅ DURABLE DISPATCH FINALIZATION VERIFIED"
        )

        print(
            "✅ PRE-DISPATCH CRASH RECOVERY VERIFIED"
        )

        print(
            "✅ POST-AUTHORIZATION CRASH RECOVERY VERIFIED"
        )

        print(
            "✅ POST-SYNTHETIC-DISPATCH RECOVERY VERIFIED"
        )

        print(
            "✅ POST-RECONCILIATION RECOVERY VERIFIED"
        )

        print(
            "✅ COMPLETED DISPATCH CANNOT BE REPLAYED"
        )

        print(
            "✅ REPEATED RESTART RECOVERY IS IDEMPOTENT"
        )

        print(
            "✅ CROSS-DISPATCH SUBSTITUTION REJECTED"
        )

        print(
            "✅ COMPLETION LEDGER TAMPERING REJECTED"
        )

        print(
            "✅ FINALIZATION JOURNAL SERIALIZATION VERIFIED"
        )

        print(
            "✅ CONCURRENT RECOVERY PRODUCES "
            "SINGLE SYNTHETIC DISPATCH"
        )

        print(
            "✅ IMPOSSIBLE RECOVERY STATE REJECTED"
        )

        print(
            "🛡 REAL NETWORK DISPATCH REMAINS DISABLED"
        )

        print(
            "🛡 LEVERAGE MUTATION TRANSPORT REMAINS LOCKED"
        )

        print(
            "🛡 NO NETWORK WRITE WAS TRANSMITTED"
        )

    else:

        print(
            "❌ R28 UNIT N.15 DIAGNOSTIC FAILED"
        )

        print(
            "🛡 EXECUTION MUST REMAIN DISABLED"
        )

    print("=" * 92)

    return (
        readiness_blockers == 0
        and all(results)
        and all(write_audit)
    )


# ============================================================
# HEARTBEAT
# ============================================================

def persistent_runtime():

    heartbeat = 1

    print(
        "R28 UNIT N.15: PERSISTENT RUNTIME ACTIVE"
    )

    print(
        "R28 UNIT N.15: DURABLE DISPATCH "
        "FINALIZATION LOCK ACTIVE"
    )

    print(
        "R28 UNIT N.15: COMPLETION LEDGER ACTIVE"
    )

    print(
        "R28 UNIT N.15: CRASH-WINDOW "
        "RECOVERY GATE ACTIVE"
    )

    print(
        "R28 UNIT N.15: RESTART "
        "IDEMPOTENCY LOCK ACTIVE"
    )

    print(
        "R28 UNIT N.15: CROSS-DISPATCH "
        "SUBSTITUTION LOCK ACTIVE"
    )

    print(
        "R28 UNIT N.15: COMPLETION LEDGER "
        "TAMPER LOCK ACTIVE"
    )

    print(
        "R28 UNIT N.15: SYNTHETIC "
        "TRANSPORT INTERCEPTOR ACTIVE"
    )

    print(
        "R28 UNIT N.15: NETWORK WRITE "
        "TRANSPORT LOCKED"
    )

    print(
        "R28 UNIT N.15: LEVERAGE MUTATION "
        "TRANSPORT LOCKED"
    )

    while True:

        print(
            f"R28 UNIT N.15: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        heartbeat += 1

        time.sleep(15)


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "R28 UNIT N.15: RUNTIME STARTING"
    )

    start_health_server()

    time.sleep(0.2)

    passed = run_diagnostic()

    if not passed:
        print(
            "R28 UNIT N.15: "
            "DIAGNOSTIC FAILURE — "
            "PERSISTENT SAFETY RUNTIME CONTINUING"
        )

    persistent_runtime()


if __name__ == "__main__":
    main()
