import os
import json
import time
import uuid
import hashlib
import threading
import tempfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer


print("R28 UNIT N.12: MAIN.PY ENTERED", flush=True)


# ============================================================================
# R28 UNIT N.12
# CRASH-CONSISTENT DISPATCH RECOVERY
# SYNTHETIC TRANSPORT ONLY
# REAL NETWORK WRITES HARD-LOCKED
# ============================================================================


UNIT = "R28 UNIT N.12"
SYMBOL = "BTCUSDT"
MARGIN_MODE = "ISOLATED"
LEVERAGE = "100"

HEARTBEAT_SECONDS = 15

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
REAL_POST_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

SYNTHETIC_TRANSPORT_ENABLED = True


# ============================================================================
# GLOBAL COUNTERS
# ============================================================================

COUNTERS_LOCK = threading.RLock()

COUNTERS = {
    "network_posts": 0,
    "network_writes": 0,
    "leverage_transmissions": 0,
    "synthetic_dispatches": 0,
    "recovery_attempts": 0,
    "recovery_successes": 0,
    "recovery_rejections": 0,
    "crash_simulations": 0,
}


# ============================================================================
# TEST RESULTS
# ============================================================================

RESULTS_LOCK = threading.RLock()
TEST_RESULTS = []

STRUCTURAL_SAFETY_FAILURES = 0
READINESS_BLOCKERS = 0


def record_result(name, passed):
    global STRUCTURAL_SAFETY_FAILURES

    status = "✅ PASS" if passed else "❌ FAIL"

    with RESULTS_LOCK:
        TEST_RESULTS.append((name, bool(passed)))

    print(f"{name:<82} {status}", flush=True)

    if not passed:
        STRUCTURAL_SAFETY_FAILURES += 1

    return passed


def section(title):
    print("", flush=True)
    print(f"{UNIT} {title}", flush=True)
    print("-" * 92, flush=True)


def local_block(message):
    print(f"{UNIT} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


# ============================================================================
# HASH / CANONICAL SERIALIZATION
# ============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_object(value):
    return sha256_text(canonical_json(value))


# ============================================================================
# REQUEST
# ============================================================================

EXACT_PAYLOAD = {
    "leverage": LEVERAGE,
    "marginMode": MARGIN_MODE,
    "symbol": SYMBOL,
}

EXACT_PAYLOAD_JSON = canonical_json(EXACT_PAYLOAD)
EXACT_PAYLOAD_HASH = sha256_text(EXACT_PAYLOAD_JSON)

LEVERAGE_PATH = "/capi/v3/account/leverage"


def build_request_binding():
    return {
        "method": "POST",
        "path": LEVERAGE_PATH,
        "payload": EXACT_PAYLOAD,
        "payload_hash": EXACT_PAYLOAD_HASH,
    }


def request_binding_hash(binding):
    return sha256_object(binding)


# ============================================================================
# AUTHORIZATION
# ============================================================================

def create_authorization(auth_id, binding):
    return {
        "authorization_id": auth_id,
        "request_binding": binding,
        "request_binding_hash": request_binding_hash(binding),
        "consumed": False,
        "consumed_by": None,
        "consumed_at_ns": None,
    }


def validate_authorization_binding(auth, binding):
    if not isinstance(auth, dict):
        return False

    expected_hash = request_binding_hash(binding)

    if auth.get("request_binding_hash") != expected_hash:
        return False

    if auth.get("request_binding") != binding:
        return False

    return True


# ============================================================================
# STATE STORE
# ============================================================================

class PersistentStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

        self.snapshot_path = self.root / "n12_snapshot.json"
        self.journal_path = self.root / "n12_dispatch_journal.jsonl"

        self.lock = threading.RLock()

    def empty_state(self):
        return {
            "version": 1,
            "authorizations": {},
            "dispatches": {},
            "recoveries": {},
        }

    def seal_state(self, state_without_seal):
        clean = dict(state_without_seal)
        clean.pop("seal", None)

        seal = sha256_object(clean)

        output = dict(clean)
        output["seal"] = seal
        return output

    def verify_state(self, state):
        if not isinstance(state, dict):
            return False

        seal = state.get("seal")

        if not isinstance(seal, str):
            return False

        clean = dict(state)
        clean.pop("seal", None)

        return sha256_object(clean) == seal

    def save_state(self, state):
        with self.lock:
            sealed = self.seal_state(state)

            temp_path = self.snapshot_path.with_suffix(
                f".{uuid.uuid4().hex}.tmp"
            )

            with open(temp_path, "w", encoding="utf-8") as handle:
                json.dump(
                    sealed,
                    handle,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(temp_path, self.snapshot_path)

            return sealed

    def load_state(self):
        with self.lock:
            if not self.snapshot_path.exists():
                state = self.empty_state()
                return self.save_state(state)

            with open(self.snapshot_path, "r", encoding="utf-8") as handle:
                state = json.load(handle)

            if not self.verify_state(state):
                raise RuntimeError("snapshot integrity seal mismatch")

            state = dict(state)
            state.pop("seal", None)

            return state

    def append_journal(self, record):
        with self.lock:
            encoded = canonical_json(record)

            with open(self.journal_path, "a", encoding="utf-8") as handle:
                handle.write(encoded + "\n")
                handle.flush()
                os.fsync(handle.fileno())

    def read_journal(self):
        with self.lock:
            if not self.journal_path.exists():
                return []

            records = []

            with open(self.journal_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()

                    if not line:
                        continue

                    records.append(json.loads(line))

            return records


# ============================================================================
# SYNTHETIC TRANSPORT
# ============================================================================

class SyntheticTransport:
    def __init__(self):
        self.lock = threading.RLock()

    def dispatch(self, dispatch_id, binding):
        if not SYNTHETIC_TRANSPORT_ENABLED:
            raise RuntimeError("synthetic transport disabled")

        if binding.get("method") != "POST":
            raise RuntimeError("unexpected method")

        if binding.get("path") != LEVERAGE_PATH:
            raise RuntimeError("unexpected path")

        if binding.get("payload_hash") != EXACT_PAYLOAD_HASH:
            raise RuntimeError("payload hash mismatch")

        if binding.get("payload") != EXACT_PAYLOAD:
            raise RuntimeError("payload mismatch")

        with self.lock:
            with COUNTERS_LOCK:
                COUNTERS["synthetic_dispatches"] += 1

        return {
            "dispatch_id": dispatch_id,
            "transport": "synthetic",
            "transmitted": False,
            "status": "SYNTHETIC_DISPATCH_COMPLETE",
            "binding_hash": request_binding_hash(binding),
        }


# ============================================================================
# HARD NETWORK FIREBREAK
# ============================================================================

def real_network_post(*args, **kwargs):
    local_block(f"{UNIT} LOCAL BLOCK: real network POST is disabled.")
    raise RuntimeError("real network POST is disabled")


def leverage_mutation_transport(*args, **kwargs):
    local_block(
        f"{UNIT} LOCAL BLOCK: leverage mutation transport is disabled."
    )
    raise RuntimeError("leverage mutation transport is disabled")


# ============================================================================
# CRASH SIMULATION
# ============================================================================

class SimulatedCrash(RuntimeError):
    pass


CRASH_BEFORE_CONSUME = "CRASH_BEFORE_CONSUME"
CRASH_AFTER_CONSUME = "CRASH_AFTER_CONSUME"
CRASH_AFTER_PREPARE = "CRASH_AFTER_PREPARE"
CRASH_AFTER_SYNTHETIC_DISPATCH = "CRASH_AFTER_SYNTHETIC_DISPATCH"


def simulate_crash(point):
    with COUNTERS_LOCK:
        COUNTERS["crash_simulations"] += 1

    raise SimulatedCrash(point)


# ============================================================================
# DISPATCH COORDINATOR
# ============================================================================

class DispatchCoordinator:
    def __init__(self, store, transport):
        self.store = store
        self.transport = transport
        self.lock = threading.RLock()

    def install_authorization(self, authorization):
        with self.lock:
            state = self.store.load_state()

            auth_id = authorization["authorization_id"]

            state["authorizations"][auth_id] = authorization

            self.store.save_state(state)

    def get_authorization(self, auth_id):
        with self.lock:
            state = self.store.load_state()
            return state["authorizations"].get(auth_id)

    def dispatch(
        self,
        auth_id,
        binding,
        worker_id,
        crash_point=None,
    ):
        with self.lock:

            state = self.store.load_state()

            auth = state["authorizations"].get(auth_id)

            if auth is None:
                raise RuntimeError("authorization not found")

            if not validate_authorization_binding(auth, binding):
                raise RuntimeError("request binding mismatch")

            if auth.get("consumed"):
                raise RuntimeError("authorization already consumed")

            if crash_point == CRASH_BEFORE_CONSUME:
                simulate_crash(CRASH_BEFORE_CONSUME)

            # ------------------------------------------------------------
            # ATOMIC CONSUMPTION
            # ------------------------------------------------------------

            auth["consumed"] = True
            auth["consumed_by"] = worker_id
            auth["consumed_at_ns"] = time.time_ns()

            state["authorizations"][auth_id] = auth

            dispatch_id = sha256_text(
                f"{auth_id}|{auth['request_binding_hash']}"
            )[:32]

            state["dispatches"][dispatch_id] = {
                "dispatch_id": dispatch_id,
                "authorization_id": auth_id,
                "worker_id": worker_id,
                "binding_hash": request_binding_hash(binding),
                "status": "AUTHORIZATION_CONSUMED",
                "synthetic_dispatch_complete": False,
            }

            self.store.save_state(state)

            self.store.append_journal({
                "event": "AUTHORIZATION_CONSUMED",
                "authorization_id": auth_id,
                "dispatch_id": dispatch_id,
                "worker_id": worker_id,
                "binding_hash": request_binding_hash(binding),
            })

            if crash_point == CRASH_AFTER_CONSUME:
                simulate_crash(CRASH_AFTER_CONSUME)

            # ------------------------------------------------------------
            # PREPARE JOURNAL
            # ------------------------------------------------------------

            self.store.append_journal({
                "event": "DISPATCH_PREPARE",
                "authorization_id": auth_id,
                "dispatch_id": dispatch_id,
                "worker_id": worker_id,
                "binding_hash": request_binding_hash(binding),
            })

            state = self.store.load_state()

            state["dispatches"][dispatch_id]["status"] = "DISPATCH_PREPARED"

            self.store.save_state(state)

            if crash_point == CRASH_AFTER_PREPARE:
                simulate_crash(CRASH_AFTER_PREPARE)

            # ------------------------------------------------------------
            # SYNTHETIC DISPATCH
            # ------------------------------------------------------------

            receipt = self.transport.dispatch(
                dispatch_id,
                binding,
            )

            self.store.append_journal({
                "event": "SYNTHETIC_DISPATCH_COMPLETE",
                "authorization_id": auth_id,
                "dispatch_id": dispatch_id,
                "worker_id": worker_id,
                "binding_hash": request_binding_hash(binding),
                "transmitted": False,
            })

            state = self.store.load_state()

            dispatch_record = state["dispatches"][dispatch_id]
            dispatch_record["status"] = "SYNTHETIC_DISPATCH_COMPLETE"
            dispatch_record["synthetic_dispatch_complete"] = True
            dispatch_record["receipt"] = receipt

            state["dispatches"][dispatch_id] = dispatch_record

            self.store.save_state(state)

            if crash_point == CRASH_AFTER_SYNTHETIC_DISPATCH:
                simulate_crash(CRASH_AFTER_SYNTHETIC_DISPATCH)

            return receipt

    def recover(self, binding, recovery_worker):
        with self.lock:

            with COUNTERS_LOCK:
                COUNTERS["recovery_attempts"] += 1

            state = self.store.load_state()

            recovered = []

            for dispatch_id, dispatch in list(
                state["dispatches"].items()
            ):

                auth_id = dispatch["authorization_id"]

                auth = state["authorizations"].get(auth_id)

                if auth is None:
                    with COUNTERS_LOCK:
                        COUNTERS["recovery_rejections"] += 1
                    raise RuntimeError(
                        "dispatch references missing authorization"
                    )

                if not validate_authorization_binding(auth, binding):
                    with COUNTERS_LOCK:
                        COUNTERS["recovery_rejections"] += 1
                    raise RuntimeError(
                        "recovery request binding mismatch"
                    )

                expected_binding_hash = request_binding_hash(binding)

                if dispatch.get("binding_hash") != expected_binding_hash:
                    with COUNTERS_LOCK:
                        COUNTERS["recovery_rejections"] += 1
                    raise RuntimeError(
                        "dispatch binding mismatch"
                    )

                if not auth.get("consumed"):
                    continue

                if dispatch.get("synthetic_dispatch_complete"):
                    continue

                recovery_key = sha256_text(
                    f"{dispatch_id}|RECOVERY"
                )

                existing = state["recoveries"].get(recovery_key)

                if existing and existing.get("completed"):
                    continue

                state["recoveries"][recovery_key] = {
                    "dispatch_id": dispatch_id,
                    "authorization_id": auth_id,
                    "recovery_worker": recovery_worker,
                    "binding_hash": expected_binding_hash,
                    "completed": False,
                }

                self.store.save_state(state)

                self.store.append_journal({
                    "event": "RECOVERY_CLAIMED",
                    "authorization_id": auth_id,
                    "dispatch_id": dispatch_id,
                    "recovery_worker": recovery_worker,
                    "binding_hash": expected_binding_hash,
                })

                receipt = self.transport.dispatch(
                    dispatch_id,
                    binding,
                )

                self.store.append_journal({
                    "event": "RECOVERY_SYNTHETIC_DISPATCH_COMPLETE",
                    "authorization_id": auth_id,
                    "dispatch_id": dispatch_id,
                    "recovery_worker": recovery_worker,
                    "binding_hash": expected_binding_hash,
                    "transmitted": False,
                })

                state = self.store.load_state()

                state["dispatches"][dispatch_id][
                    "synthetic_dispatch_complete"
                ] = True

                state["dispatches"][dispatch_id][
                    "status"
                ] = "SYNTHETIC_DISPATCH_COMPLETE"

                state["dispatches"][dispatch_id][
                    "receipt"
                ] = receipt

                state["recoveries"][recovery_key][
                    "completed"
                ] = True

                self.store.save_state(state)

                recovered.append(dispatch_id)

                with COUNTERS_LOCK:
                    COUNTERS["recovery_successes"] += 1

            return recovered


# ============================================================================
# HEALTH SERVER
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/health"):
            body = (
                "R28 UNIT N.12 ACTIVE\n"
                "CRASH-CONSISTENT RECOVERY ACTIVE\n"
                "REAL NETWORK WRITES DISABLED\n"
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

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

    print(
        f"{UNIT}: HEALTH SERVER ACTIVE ON PORT {port}",
        flush=True,
    )

    return server


# ============================================================================
# TEST ENVIRONMENT
# ============================================================================

def new_environment():
    root = tempfile.mkdtemp(
        prefix="r28_n12_"
    )

    store = PersistentStore(root)
    transport = SyntheticTransport()
    coordinator = DispatchCoordinator(
        store,
        transport,
    )

    return root, store, transport, coordinator


# ============================================================================
# TEST 1
# CRASH BEFORE CONSUMPTION
# ============================================================================

def test_crash_before_consume():

    section("TEST 1: CRASH BEFORE AUTHORIZATION CONSUMPTION")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T1",
        binding,
    )

    coordinator.install_authorization(auth)

    crashed = False

    try:
        coordinator.dispatch(
            "AUTH-N12-T1",
            binding,
            "worker-t1",
            CRASH_BEFORE_CONSUME,
        )
    except SimulatedCrash:
        crashed = True

    state = store.load_state()

    persisted_auth = state["authorizations"]["AUTH-N12-T1"]

    record_result(
        "Crash Before Consume Was Simulated",
        crashed,
    )

    record_result(
        "Authorization Remains Unconsumed After Pre-Consume Crash",
        persisted_auth["consumed"] is False,
    )

    recovered = coordinator.recover(
        binding,
        "recovery-t1",
    )

    record_result(
        "Pre-Consume Crash Produces No Recovery Dispatch",
        recovered == [],
    )


# ============================================================================
# TEST 2
# CRASH AFTER CONSUMPTION
# ============================================================================

def test_crash_after_consume():

    section("TEST 2: CRASH AFTER CONSUMPTION BEFORE DISPATCH PREPARE")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T2",
        binding,
    )

    coordinator.install_authorization(auth)

    before = COUNTERS["synthetic_dispatches"]

    crashed = False

    try:
        coordinator.dispatch(
            "AUTH-N12-T2",
            binding,
            "worker-t2",
            CRASH_AFTER_CONSUME,
        )
    except SimulatedCrash:
        crashed = True

    record_result(
        "Crash After Consume Was Simulated",
        crashed,
    )

    state = store.load_state()

    auth_after = state["authorizations"]["AUTH-N12-T2"]

    record_result(
        "Consumed Authorization Persisted Across Crash",
        auth_after["consumed"] is True,
    )

    recovered = coordinator.recover(
        binding,
        "recovery-t2",
    )

    after = COUNTERS["synthetic_dispatches"]

    record_result(
        "Recovery Located Interrupted Dispatch",
        len(recovered) == 1,
    )

    record_result(
        "Recovery Produced Exactly One Synthetic Dispatch",
        after - before == 1,
    )


# ============================================================================
# TEST 3
# CRASH AFTER PREPARE
# ============================================================================

def test_crash_after_prepare():

    section("TEST 3: CRASH AFTER DISPATCH PREPARE JOURNAL")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T3",
        binding,
    )

    coordinator.install_authorization(auth)

    before = COUNTERS["synthetic_dispatches"]

    crashed = False

    try:
        coordinator.dispatch(
            "AUTH-N12-T3",
            binding,
            "worker-t3",
            CRASH_AFTER_PREPARE,
        )
    except SimulatedCrash:
        crashed = True

    record_result(
        "Crash After Prepare Was Simulated",
        crashed,
    )

    journal = store.read_journal()

    prepare_records = [
        record
        for record in journal
        if record.get("event") == "DISPATCH_PREPARE"
    ]

    record_result(
        "Exactly One Dispatch Prepare Journal Record Persisted",
        len(prepare_records) == 1,
    )

    recovered = coordinator.recover(
        binding,
        "recovery-t3",
    )

    after = COUNTERS["synthetic_dispatches"]

    record_result(
        "Prepared Dispatch Recovered",
        len(recovered) == 1,
    )

    record_result(
        "Prepared Dispatch Generated Exactly One Synthetic Recovery",
        after - before == 1,
    )


# ============================================================================
# TEST 4
# POST-DISPATCH CRASH
# ============================================================================

def test_post_dispatch_crash():

    section("TEST 4: CRASH AFTER SYNTHETIC DISPATCH COMMIT")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T4",
        binding,
    )

    coordinator.install_authorization(auth)

    before = COUNTERS["synthetic_dispatches"]

    crashed = False

    try:
        coordinator.dispatch(
            "AUTH-N12-T4",
            binding,
            "worker-t4",
            CRASH_AFTER_SYNTHETIC_DISPATCH,
        )
    except SimulatedCrash:
        crashed = True

    middle = COUNTERS["synthetic_dispatches"]

    record_result(
        "Crash After Synthetic Dispatch Was Simulated",
        crashed,
    )

    record_result(
        "Exactly One Synthetic Dispatch Occurred Before Crash",
        middle - before == 1,
    )

    recovered = coordinator.recover(
        binding,
        "recovery-t4",
    )

    after = COUNTERS["synthetic_dispatches"]

    record_result(
        "Completed Dispatch Requires No Recovery Redispatch",
        recovered == [],
    )

    record_result(
        "Restart Recovery Produced No Duplicate Synthetic Dispatch",
        after == middle,
    )


# ============================================================================
# TEST 5
# REPEATED RESTART IDEMPOTENCY
# ============================================================================

def test_repeated_restart_idempotency():

    section("TEST 5: REPEATED RESTART RECOVERY IDEMPOTENCY")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T5",
        binding,
    )

    coordinator.install_authorization(auth)

    try:
        coordinator.dispatch(
            "AUTH-N12-T5",
            binding,
            "worker-t5",
            CRASH_AFTER_CONSUME,
        )
    except SimulatedCrash:
        pass

    before = COUNTERS["synthetic_dispatches"]

    first = coordinator.recover(
        binding,
        "recovery-t5-a",
    )

    after_first = COUNTERS["synthetic_dispatches"]

    second = coordinator.recover(
        binding,
        "recovery-t5-b",
    )

    third = coordinator.recover(
        binding,
        "recovery-t5-c",
    )

    after_all = COUNTERS["synthetic_dispatches"]

    record_result(
        "First Restart Recovered Exactly One Dispatch",
        len(first) == 1,
    )

    record_result(
        "Second Restart Produced No Recovery Dispatch",
        second == [],
    )

    record_result(
        "Third Restart Produced No Recovery Dispatch",
        third == [],
    )

    record_result(
        "Repeated Restarts Preserve Exactly-Once Synthetic Dispatch",
        after_first - before == 1
        and after_all == after_first,
    )


# ============================================================================
# TEST 6
# REQUEST-BINDING TAMPER REJECTION
# ============================================================================

def test_recovery_binding_tamper():

    section("TEST 6: RECOVERY REQUEST-BINDING TAMPER REJECTION")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T6",
        binding,
    )

    coordinator.install_authorization(auth)

    try:
        coordinator.dispatch(
            "AUTH-N12-T6",
            binding,
            "worker-t6",
            CRASH_AFTER_CONSUME,
        )
    except SimulatedCrash:
        pass

    tampered = build_request_binding()
    tampered["payload"] = dict(tampered["payload"])
    tampered["payload"]["leverage"] = "99"
    tampered["payload_hash"] = sha256_object(
        tampered["payload"]
    )

    before = COUNTERS["synthetic_dispatches"]

    rejected = False

    try:
        coordinator.recover(
            tampered,
            "recovery-t6-tampered",
        )
    except RuntimeError:
        rejected = True

    after = COUNTERS["synthetic_dispatches"]

    record_result(
        "Tampered Recovery Binding Rejected",
        rejected,
    )

    record_result(
        "Tampered Recovery Produced No Synthetic Dispatch",
        before == after,
    )

    recovered = coordinator.recover(
        binding,
        "recovery-t6-valid",
    )

    record_result(
        "Original Exact Binding Still Recovers Successfully",
        len(recovered) == 1,
    )


# ============================================================================
# TEST 7
# CORRUPTED SNAPSHOT REJECTION
# ============================================================================

def test_corrupt_snapshot():

    section("TEST 7: CORRUPTED RECOVERY SNAPSHOT REJECTION")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T7",
        binding,
    )

    coordinator.install_authorization(auth)

    raw = json.loads(
        store.snapshot_path.read_text(
            encoding="utf-8"
        )
    )

    raw["authorizations"]["AUTH-N12-T7"][
        "consumed"
    ] = True

    store.snapshot_path.write_text(
        json.dumps(raw),
        encoding="utf-8",
    )

    rejected = False

    try:
        store.load_state()
    except RuntimeError:
        rejected = True

    record_result(
        "Corrupted Snapshot Integrity Seal Rejected",
        rejected,
    )


# ============================================================================
# TEST 8
# CONCURRENT RECOVERY SINGLE-WINNER
# ============================================================================

def test_concurrent_recovery():

    section("TEST 8: CONCURRENT RECOVERY SINGLE-WINNER")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T8",
        binding,
    )

    coordinator.install_authorization(auth)

    try:
        coordinator.dispatch(
            "AUTH-N12-T8",
            binding,
            "worker-t8",
            CRASH_AFTER_CONSUME,
        )
    except SimulatedCrash:
        pass

    before = COUNTERS["synthetic_dispatches"]

    outcomes = []
    outcomes_lock = threading.Lock()

    def recovery_worker(worker_number):
        try:
            recovered = coordinator.recover(
                binding,
                f"recovery-racer-{worker_number}",
            )

            with outcomes_lock:
                outcomes.append(
                    (
                        worker_number,
                        len(recovered),
                        None,
                    )
                )

        except Exception as exc:
            with outcomes_lock:
                outcomes.append(
                    (
                        worker_number,
                        0,
                        str(exc),
                    )
                )

    threads = []

    for number in range(8):
        thread = threading.Thread(
            target=recovery_worker,
            args=(number,),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    after = COUNTERS["synthetic_dispatches"]

    recovery_winners = sum(
        count
        for _, count, _ in outcomes
    )

    record_result(
        "All Eight Recovery Workers Completed",
        len(outcomes) == 8,
    )

    record_result(
        "Eight-Worker Recovery Race Produced Exactly One Winner",
        recovery_winners == 1,
    )

    record_result(
        "Concurrent Recovery Produced Exactly One Synthetic Dispatch",
        after - before == 1,
    )


# ============================================================================
# TEST 9
# AUTHORIZATION REPLAY AFTER RECOVERY
# ============================================================================

def test_post_recovery_replay():

    section("TEST 9: POST-RECOVERY AUTHORIZATION REPLAY REJECTION")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T9",
        binding,
    )

    coordinator.install_authorization(auth)

    try:
        coordinator.dispatch(
            "AUTH-N12-T9",
            binding,
            "worker-t9",
            CRASH_AFTER_CONSUME,
        )
    except SimulatedCrash:
        pass

    coordinator.recover(
        binding,
        "recovery-t9",
    )

    before = COUNTERS["synthetic_dispatches"]

    rejected = False

    try:
        coordinator.dispatch(
            "AUTH-N12-T9",
            binding,
            "worker-t9-replay",
        )
    except RuntimeError:
        rejected = True

    after = COUNTERS["synthetic_dispatches"]

    record_result(
        "Recovered Authorization Replay Rejected",
        rejected,
    )

    record_result(
        "Authorization Replay Produced No Second Synthetic Dispatch",
        before == after,
    )


# ============================================================================
# TEST 10
# JOURNAL CONSISTENCY
# ============================================================================

def test_journal_consistency():

    section("TEST 10: CRASH-RECOVERY JOURNAL CONSISTENCY")

    root, store, transport, coordinator = new_environment()

    binding = build_request_binding()

    auth = create_authorization(
        "AUTH-N12-T10",
        binding,
    )

    coordinator.install_authorization(auth)

    try:
        coordinator.dispatch(
            "AUTH-N12-T10",
            binding,
            "worker-t10",
            CRASH_AFTER_PREPARE,
        )
    except SimulatedCrash:
        pass

    coordinator.recover(
        binding,
        "recovery-t10",
    )

    journal = store.read_journal()

    consumed = [
        r for r in journal
        if r.get("event") == "AUTHORIZATION_CONSUMED"
    ]

    prepared = [
        r for r in journal
        if r.get("event") == "DISPATCH_PREPARE"
    ]

    recovered = [
        r for r in journal
        if r.get("event") ==
        "RECOVERY_SYNTHETIC_DISPATCH_COMPLETE"
    ]

    same_dispatch = (
        len(consumed) == 1
        and len(prepared) == 1
        and len(recovered) == 1
        and consumed[0]["dispatch_id"]
        == prepared[0]["dispatch_id"]
        == recovered[0]["dispatch_id"]
    )

    same_binding = (
        len(consumed) == 1
        and len(prepared) == 1
        and len(recovered) == 1
        and consumed[0]["binding_hash"]
        == prepared[0]["binding_hash"]
        == recovered[0]["binding_hash"]
    )

    record_result(
        "Exactly One Authorization Consumed Record",
        len(consumed) == 1,
    )

    record_result(
        "Exactly One Dispatch Prepare Record",
        len(prepared) == 1,
    )

    record_result(
        "Exactly One Recovery Completion Record",
        len(recovered) == 1,
    )

    record_result(
        "Crash-Recovery Journal Preserves Same Dispatch Identity",
        same_dispatch,
    )

    record_result(
        "Crash-Recovery Journal Preserves Exact Request Binding",
        same_binding,
    )


# ============================================================================
# TEST 11
# FINAL NETWORK WRITE FIREBREAK
# ============================================================================

def test_network_firebreak():

    section("TEST 11: FINAL NETWORK WRITE FIREBREAK")

    before_posts = COUNTERS["network_posts"]
    before_writes = COUNTERS["network_writes"]
    before_leverage = COUNTERS["leverage_transmissions"]

    post_blocked = False

    try:
        real_network_post(
            LEVERAGE_PATH,
            EXACT_PAYLOAD,
        )
    except RuntimeError:
        post_blocked = True

    record_result(
        "Real POST Rejected Locally",
        post_blocked,
    )

    leverage_blocked = False

    try:
        leverage_mutation_transport(
            EXACT_PAYLOAD,
        )
    except RuntimeError:
        leverage_blocked = True

    record_result(
        "Leverage Mutation Transport Rejected Locally",
        leverage_blocked,
    )

    record_result(
        "Real POST Block Produced No Network POST",
        COUNTERS["network_posts"] == before_posts,
    )

    record_result(
        "Real POST Block Produced No Network Write",
        COUNTERS["network_writes"] == before_writes,
    )

    record_result(
        "Leverage Block Produced No Transmission",
        COUNTERS["leverage_transmissions"] == before_leverage,
    )


# ============================================================================
# DIAGNOSTIC
# ============================================================================

def run_diagnostic():

    print("=" * 92, flush=True)
    print("0F-4H-R28-UNIT-N.12 STARTING", flush=True)
    print("CRASH-CONSISTENT DISPATCH RECOVERY", flush=True)
    print("EXACTLY-ONCE SYNTHETIC RECOVERY VALIDATION", flush=True)
    print("REAL NETWORK POST DISABLED", flush=True)
    print("LEVERAGE MUTATION TRANSPORT DISABLED", flush=True)
    print("=" * 92, flush=True)

    section("SAFETY GATES")

    record_result(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    record_result(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    record_result(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    record_result(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    record_result(
        "Leverage Mutation Transport Disabled",
        LEVERAGE_MUTATION_TRANSPORT_ENABLED is False,
    )

    record_result(
        "Synthetic Transport Enabled",
        SYNTHETIC_TRANSPORT_ENABLED is True,
    )

    section("EXACT REQUEST BINDING")

    print(
        f"Payload = {EXACT_PAYLOAD_JSON}",
        flush=True,
    )

    print(
        f"Payload SHA256 = {EXACT_PAYLOAD_HASH}",
        flush=True,
    )

    print(
        f"Method = POST",
        flush=True,
    )

    print(
        f"Path = {LEVERAGE_PATH}",
        flush=True,
    )

    record_result(
        "Exact Leverage Payload Preserved",
        EXACT_PAYLOAD == {
            "leverage": "100",
            "marginMode": "ISOLATED",
            "symbol": "BTCUSDT",
        },
    )

    test_crash_before_consume()
    test_crash_after_consume()
    test_crash_after_prepare()
    test_post_dispatch_crash()
    test_repeated_restart_idempotency()
    test_recovery_binding_tamper()
    test_corrupt_snapshot()
    test_concurrent_recovery()
    test_post_recovery_replay()
    test_journal_consistency()
    test_network_firebreak()

    section("WRITE-LOCK AUDIT")

    print(
        f"  Network POSTs = {COUNTERS['network_posts']}",
        flush=True,
    )

    print(
        f"  Network writes = {COUNTERS['network_writes']}",
        flush=True,
    )

    print(
        f"  Leverage transmissions = "
        f"{COUNTERS['leverage_transmissions']}",
        flush=True,
    )

    print(
        f"  Synthetic dispatches = "
        f"{COUNTERS['synthetic_dispatches']}",
        flush=True,
    )

    print(
        f"  Crash simulations = "
        f"{COUNTERS['crash_simulations']}",
        flush=True,
    )

    print(
        f"  Recovery attempts = "
        f"{COUNTERS['recovery_attempts']}",
        flush=True,
    )

    print(
        f"  Recovery successes = "
        f"{COUNTERS['recovery_successes']}",
        flush=True,
    )

    print(
        f"  Recovery rejections = "
        f"{COUNTERS['recovery_rejections']}",
        flush=True,
    )

    record_result(
        "Network POST Count Is Zero",
        COUNTERS["network_posts"] == 0,
    )

    record_result(
        "Network Write Count Is Zero",
        COUNTERS["network_writes"] == 0,
    )

    record_result(
        "Leverage Transmission Count Is Zero",
        COUNTERS["leverage_transmissions"] == 0,
    )

    section("EXECUTION-READINESS ASSESSMENT")

    failures = sum(
        1
        for _, passed in TEST_RESULTS
        if not passed
    )

    blockers = failures

    print(
        f"Structural Safety Failures = {failures}",
        flush=True,
    )

    print(
        f"Readiness Blockers = {blockers}",
        flush=True,
    )

    print(
        "Crash-Before-Consume Safety = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Consumed-State Durability = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Prepared-Dispatch Recovery = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Repeated Restart Idempotency = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Concurrent Recovery Single Winner = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Recovery Request Binding = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Snapshot Integrity = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Post-Recovery Replay Protection = "
        + ("✅ VERIFIED" if failures == 0 else "❌ FAILED"),
        flush=True,
    )

    print(
        "Final Network Dispatch = 🛡 BLOCKED LOCALLY",
        flush=True,
    )

    print(
        "Leverage Mutation Transmission = 🛡 BLOCKED LOCALLY",
        flush=True,
    )

    print("", flush=True)

    if failures == 0:

        print(
            "✅ R28 UNIT N.12 DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ CRASH-CONSISTENT DISPATCH RECOVERY VERIFIED",
            flush=True,
        )

        print(
            "✅ PRE-CONSUME CRASH PRESERVES AUTHORIZATION",
            flush=True,
        )

        print(
            "✅ POST-CONSUME CRASH RECOVERS DETERMINISTICALLY",
            flush=True,
        )

        print(
            "✅ PREPARED DISPATCH SURVIVES RESTART",
            flush=True,
        )

        print(
            "✅ COMPLETED SYNTHETIC DISPATCH IS NOT REPEATED",
            flush=True,
        )

        print(
            "✅ REPEATED RESTART RECOVERY IS IDEMPOTENT",
            flush=True,
        )

        print(
            "✅ CONCURRENT RECOVERY PRODUCES SINGLE WINNER",
            flush=True,
        )

        print(
            "✅ RECOVERY REQUEST BINDING PRESERVED",
            flush=True,
        )

        print(
            "✅ CORRUPTED RECOVERY SNAPSHOT REJECTED",
            flush=True,
        )

        print(
            "✅ POST-RECOVERY AUTHORIZATION REPLAY BLOCKED",
            flush=True,
        )

        print(
            "✅ CRASH-RECOVERY JOURNAL SERIALIZATION VERIFIED",
            flush=True,
        )

        print(
            "🛡 REAL NETWORK DISPATCH REMAINS DISABLED",
            flush=True,
        )

        print(
            "🛡 LEVERAGE MUTATION TRANSPORT REMAINS LOCKED",
            flush=True,
        )

        print(
            "🛡 NO NETWORK WRITE WAS TRANSMITTED",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT N.12 DIAGNOSTIC FAILED",
            flush=True,
        )

        print(
            "❌ DO NOT ADVANCE TO NEXT UNIT",
            flush=True,
        )

    print("=" * 92, flush=True)

    return failures == 0


# ============================================================================
# HEARTBEAT
# ============================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{UNIT}: HEARTBEAT {heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(HEARTBEAT_SECONDS)


# ============================================================================
# MAIN
# ============================================================================

def main():

    print(
        f"{UNIT}: IMPORTS COMPLETE",
        flush=True,
    )

    print(
        f"{UNIT}: CONSTANTS INITIALIZED",
        flush=True,
    )

    print(
        f"{UNIT}: RUNTIME STARTING",
        flush=True,
    )

    start_health_server()

    passed = run_diagnostic()

    print("=" * 92, flush=True)

    if passed:

        print(
            f"{UNIT}: PERSISTENT RUNTIME ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: CRASH-CONSISTENT RECOVERY GATE ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: AUTHORIZATION DURABILITY GATE ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: DISPATCH RECOVERY JOURNAL ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: RESTART IDEMPOTENCY LOCK ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: CONCURRENT RECOVERY LOCK ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: REQUEST-BINDING RECOVERY LOCK ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: SNAPSHOT INTEGRITY LOCK ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: SYNTHETIC TRANSPORT INTERCEPTOR ACTIVE",
            flush=True,
        )

        print(
            f"{UNIT}: NETWORK WRITE TRANSPORT LOCKED",
            flush=True,
        )

        print(
            f"{UNIT}: LEVERAGE MUTATION TRANSPORT LOCKED",
            flush=True,
        )

    else:

        print(
            f"{UNIT}: DIAGNOSTIC FAILURE — SAFETY LOCKS REMAIN ACTIVE",
            flush=True,
        )

    heartbeat_loop()


if __name__ == "__main__":
    main()
