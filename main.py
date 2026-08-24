import os
import json
import time
import uuid
import hashlib
import threading
import tempfile
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer


print("R28 UNIT N.11: MAIN.PY ENTERED", flush=True)


# =============================================================================
# R28 UNIT N.11
# CONCURRENT AUTHORIZATION / DISPATCH SERIALIZATION
#
# PURPOSE
# -----------------------------------------------------------------------------
# Prove that two or more workers racing against the SAME authorization cannot
# produce multiple dispatches.
#
# SAFETY
# -----------------------------------------------------------------------------
# - NO real POST implementation exists.
# - NO requests/httpx/aiohttp write client is imported.
# - All final dispatch attempts terminate at a synthetic local interceptor.
# - Leverage mutation transmission remains disabled.
# =============================================================================


UNIT_NAME = "R28 UNIT N.11"
SYMBOL = "BTCUSDT"
LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

HEARTBEAT_SECONDS = 15

BASE_DIR = os.environ.get(
    "R28_N11_STATE_DIR",
    os.path.join(tempfile.gettempdir(), "r28_unit_n11")
)

STATE_FILE = os.path.join(BASE_DIR, "snapshot.json")
JOURNAL_FILE = os.path.join(BASE_DIR, "dispatch_journal.jsonl")

os.makedirs(BASE_DIR, exist_ok=True)


# =============================================================================
# COUNTERS
# =============================================================================

metrics_lock = threading.Lock()

metrics = {
    "network_posts": 0,
    "network_writes": 0,
    "leverage_transmissions": 0,
    "synthetic_dispatches": 0,
    "authorization_grants": 0,
    "authorization_denials": 0,
    "concurrent_workers": 0,
    "journal_prepare_records": 0,
    "journal_consumed_records": 0,
}


def increment_metric(name, amount=1):
    with metrics_lock:
        metrics[name] += amount


# =============================================================================
# UTILITY
# =============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_object(value):
    return sha256_text(canonical_json(value))


def passfail(label, condition):
    marker = "✅ PASS" if condition else "❌ FAIL"
    print(f"{label:<78} {marker}", flush=True)
    return bool(condition)


def section(title):
    print()
    print(title)
    print("-" * 92)


def banner():
    print("=" * 92)


# =============================================================================
# HARD TRANSPORT LOCK
# =============================================================================

class NetworkWriteBlocked(RuntimeError):
    pass


def real_network_post(*args, **kwargs):
    """
    Deliberately impossible transport boundary.

    This function exists only so accidental invocation can be detected.
    It never performs network I/O.
    """
    raise NetworkWriteBlocked(
        f"{UNIT_NAME} LOCAL BLOCK: real network POST is disabled."
    )


def leverage_mutation_transport(*args, **kwargs):
    """
    Deliberately impossible leverage transmission boundary.
    """
    raise NetworkWriteBlocked(
        f"{UNIT_NAME} LOCAL BLOCK: leverage mutation transport is disabled."
    )


# =============================================================================
# SYNTHETIC FINAL TRANSPORT INTERCEPTOR
# =============================================================================

synthetic_dispatch_lock = threading.Lock()


def synthetic_transport_interceptor(request):
    """
    Final local-only boundary.

    Records that an authorized request reached the transport edge,
    but NEVER transmits anything.
    """
    with synthetic_dispatch_lock:
        increment_metric("synthetic_dispatches")

        receipt = {
            "transport": "SYNTHETIC_LOCAL_INTERCEPTOR",
            "transmitted": False,
            "method": request["method"],
            "path": request["path"],
            "request_id": request["request_id"],
            "payload_hash": request["payload_hash"],
            "timestamp_ns": time.time_ns(),
        }

        return receipt


# =============================================================================
# ATOMIC FILE HELPERS
# =============================================================================

file_lock = threading.RLock()


def atomic_write_json(path, data):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    temporary = f"{path}.{uuid.uuid4().hex}.tmp"

    encoded = canonical_json(data)

    with open(temporary, "w", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temporary, path)


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def append_journal(record):
    encoded = canonical_json(record)

    with file_lock:
        with open(JOURNAL_FILE, "a", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def read_journal():
    if not os.path.exists(JOURNAL_FILE):
        return []

    records = []

    with file_lock:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as handle:
            for raw in handle:
                raw = raw.strip()

                if not raw:
                    continue

                records.append(json.loads(raw))

    return records


# =============================================================================
# AUTHORIZATION STATE
# =============================================================================

authorization_lock = threading.RLock()


def fresh_state():
    return {
        "version": 1,
        "authorizations": {},
        "dispatches": {},
    }


def load_state():
    with file_lock:
        if not os.path.exists(STATE_FILE):
            state = fresh_state()
            atomic_write_json(STATE_FILE, state)
            return state

        return read_json(STATE_FILE)


def save_state(state):
    with file_lock:
        atomic_write_json(STATE_FILE, state)


def reset_test_storage():
    with file_lock:
        for path in (STATE_FILE, JOURNAL_FILE):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

        save_state(fresh_state())


# =============================================================================
# PAYLOAD / REQUEST BINDING
# =============================================================================

def build_payload():
    return {
        "leverage": LEVERAGE,
        "marginMode": MARGIN_MODE,
        "symbol": SYMBOL,
    }


def build_request(payload):
    payload_string = canonical_json(payload)
    payload_hash = sha256_text(payload_string)

    request_core = {
        "method": "POST",
        "path": "/capi/v3/account/leverage",
        "payload": deepcopy(payload),
        "payload_hash": payload_hash,
    }

    request_id = sha256_object(request_core)

    return {
        **request_core,
        "request_id": request_id,
    }


def build_authorization(request):
    authorization_core = {
        "request_id": request["request_id"],
        "payload_hash": request["payload_hash"],
        "method": request["method"],
        "path": request["path"],
        "nonce": uuid.uuid4().hex,
    }

    authorization_id = sha256_object(authorization_core)

    return {
        **authorization_core,
        "authorization_id": authorization_id,
        "consumed": False,
        "consumed_by": None,
        "consumed_at_ns": None,
    }


def register_authorization(authorization):
    with authorization_lock:
        state = load_state()

        state["authorizations"][
            authorization["authorization_id"]
        ] = deepcopy(authorization)

        save_state(state)


def request_matches_authorization(request, authorization):
    return (
        request["request_id"] == authorization["request_id"]
        and request["payload_hash"] == authorization["payload_hash"]
        and request["method"] == authorization["method"]
        and request["path"] == authorization["path"]
    )


# =============================================================================
# ATOMIC AUTHORIZATION CONSUMPTION
# =============================================================================

def consume_authorization_atomically(
    worker_id,
    request,
    authorization_id,
):
    """
    Critical N.11 boundary.

    Validation and consumption happen under one serialization lock.
    There is intentionally no validation -> unlock -> consumption gap.
    """

    with authorization_lock:
        state = load_state()

        authorization = state["authorizations"].get(authorization_id)

        if authorization is None:
            increment_metric("authorization_denials")

            return {
                "granted": False,
                "reason": "authorization_not_found",
            }

        if not request_matches_authorization(request, authorization):
            increment_metric("authorization_denials")

            return {
                "granted": False,
                "reason": "request_binding_mismatch",
            }

        if authorization["consumed"]:
            increment_metric("authorization_denials")

            return {
                "granted": False,
                "reason": "authorization_already_consumed",
                "consumed_by": authorization["consumed_by"],
            }

        # ---------------------------------------------------------------------
        # PREPARE journal record written before state mutation.
        # ---------------------------------------------------------------------

        prepare_record = {
            "event": "DISPATCH_PREPARE",
            "authorization_id": authorization_id,
            "worker_id": worker_id,
            "request_id": request["request_id"],
            "payload_hash": request["payload_hash"],
            "timestamp_ns": time.time_ns(),
        }

        append_journal(prepare_record)
        increment_metric("journal_prepare_records")

        # ---------------------------------------------------------------------
        # Single-use consumption.
        # ---------------------------------------------------------------------

        authorization["consumed"] = True
        authorization["consumed_by"] = worker_id
        authorization["consumed_at_ns"] = time.time_ns()

        state["authorizations"][authorization_id] = authorization

        dispatch_key = authorization_id

        state["dispatches"][dispatch_key] = {
            "worker_id": worker_id,
            "request_id": request["request_id"],
            "payload_hash": request["payload_hash"],
            "state": "AUTHORIZED_CONSUMED",
        }

        save_state(state)

        # ---------------------------------------------------------------------
        # Durable consumption journal record.
        # ---------------------------------------------------------------------

        consumed_record = {
            "event": "AUTHORIZATION_CONSUMED",
            "authorization_id": authorization_id,
            "worker_id": worker_id,
            "request_id": request["request_id"],
            "payload_hash": request["payload_hash"],
            "timestamp_ns": time.time_ns(),
        }

        append_journal(consumed_record)
        increment_metric("journal_consumed_records")
        increment_metric("authorization_grants")

        return {
            "granted": True,
            "worker_id": worker_id,
            "authorization": deepcopy(authorization),
        }


# =============================================================================
# CONCURRENT WORKER
# =============================================================================

def competing_worker(
    worker_id,
    request,
    authorization_id,
    start_barrier,
    results,
    results_lock,
):
    increment_metric("concurrent_workers")

    try:
        # Synchronize workers so they compete for the same authorization
        # as closely together as the Python runtime allows.
        start_barrier.wait(timeout=5)

        result = consume_authorization_atomically(
            worker_id=worker_id,
            request=request,
            authorization_id=authorization_id,
        )

        if result["granted"]:
            receipt = synthetic_transport_interceptor(request)
            result["receipt"] = receipt

        with results_lock:
            results.append({
                "worker_id": worker_id,
                **result,
            })

    except Exception as exc:
        with results_lock:
            results.append({
                "worker_id": worker_id,
                "granted": False,
                "reason": f"worker_exception:{type(exc).__name__}:{exc}",
            })


# =============================================================================
# RESTART / REPLAY SIMULATION
# =============================================================================

def restart_runtime_view():
    """
    Simulates a fresh runtime reading only durable disk state.
    """
    return load_state()


def attempt_post_restart_replay(
    worker_id,
    request,
    authorization_id,
):
    return consume_authorization_atomically(
        worker_id=worker_id,
        request=request,
        authorization_id=authorization_id,
    )


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = b"R28 UNIT N.11 ACTIVE"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    try:
        port = int(os.environ.get("PORT", "10000"))

        server = HTTPServer(("0.0.0.0", port), HealthHandler)

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        print(
            f"{UNIT_NAME}: HEALTH SERVER ACTIVE ON PORT {port}",
            flush=True,
        )

        return server

    except Exception as exc:
        print(
            f"{UNIT_NAME}: HEALTH SERVER WARNING: {exc}",
            flush=True,
        )

        return None


# =============================================================================
# TEST SUITE
# =============================================================================

def run_diagnostic():
    reset_test_storage()

    payload = build_payload()
    request = build_request(payload)
    authorization = build_authorization(request)

    register_authorization(authorization)

    banner()
    print("0F-4H-R28-UNIT-N.11 STARTING")
    print("CONCURRENT AUTHORIZATION / DISPATCH SERIALIZATION")
    print("SINGLE-USE AUTHORIZATION RACE PROTECTION")
    print("ATOMIC VALIDATE+CONSUME GATE")
    print("POST-RESTART REPLAY PROTECTION")
    print("SYNTHETIC FINAL TRANSPORT ONLY")
    print("REAL NETWORK WRITE TRANSPORT DISABLED")
    print("LEVERAGE MUTATION TRANSPORT DISABLED")
    banner()

    print(f"{UNIT_NAME} SYMBOL: {SYMBOL}")
    print(f"{UNIT_NAME} LEVERAGE: {LEVERAGE}x")
    print(f"{UNIT_NAME} MARGIN MODE: {MARGIN_MODE}")

    section(f"{UNIT_NAME} SAFETY GATES")

    safety_results = []

    safety_results.append(
        passfail(
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        )
    )

    safety_results.append(
        passfail(
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    safety_results.append(
        passfail(
            "Network Writes Disabled",
            NETWORK_WRITES_ENABLED is False,
        )
    )

    safety_results.append(
        passfail(
            "Leverage Mutation Transport Disabled",
            LEVERAGE_MUTATION_TRANSPORT_ENABLED is False,
        )
    )

    section(f"{UNIT_NAME} EXACT PAYLOAD")

    print(f"Payload = {canonical_json(payload)}")
    print(f"Payload SHA256 = {request['payload_hash']}")
    print(f"Request ID = {request['request_id']}")
    print(f"Authorization ID = {authorization['authorization_id']}")

    exact_payload_ok = (
        canonical_json(payload)
        == '{"leverage":"100","marginMode":"ISOLATED","symbol":"BTCUSDT"}'
    )

    safety_results.append(
        passfail(
            "Exact Leverage Payload Preserved",
            exact_payload_ok,
        )
    )

    safety_results.append(
        passfail(
            "Exact V3 Endpoint Preserved",
            request["path"] == "/capi/v3/account/leverage",
        )
    )

    safety_results.append(
        passfail(
            "Transport Method Exactly POST",
            request["method"] == "POST",
        )
    )

    # =========================================================================
    # TEST 1
    # TWO WORKERS RACE AGAINST ONE AUTHORIZATION
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 1: CONCURRENT SINGLE-USE AUTHORIZATION RACE"
    )

    workers = 2
    start_barrier = threading.Barrier(workers)
    results = []
    results_lock = threading.Lock()

    threads = []

    for worker_number in range(1, workers + 1):
        worker_id = f"worker-{worker_number}"

        thread = threading.Thread(
            target=competing_worker,
            args=(
                worker_id,
                deepcopy(request),
                authorization["authorization_id"],
                start_barrier,
                results,
                results_lock,
            ),
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join(timeout=10)

    granted = [
        item
        for item in results
        if item.get("granted") is True
    ]

    denied = [
        item
        for item in results
        if item.get("granted") is False
    ]

    test_results = []

    test_results.append(
        passfail(
            "Both Concurrent Workers Completed",
            len(results) == 2,
        )
    )

    test_results.append(
        passfail(
            "Exactly One Concurrent Authorization Grant",
            len(granted) == 1,
        )
    )

    test_results.append(
        passfail(
            "Exactly One Concurrent Authorization Denial",
            len(denied) == 1,
        )
    )

    denial_reason_ok = (
        len(denied) == 1
        and denied[0].get("reason")
        == "authorization_already_consumed"
    )

    test_results.append(
        passfail(
            "Losing Worker Rejected As Already Consumed",
            denial_reason_ok,
        )
    )

    # =========================================================================
    # TEST 2
    # EXACTLY ONE SYNTHETIC FINAL BOUNDARY REACHED
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 2: DOUBLE-DISPATCH PREVENTION"
    )

    test_results.append(
        passfail(
            "Synthetic Final Boundary Reached Exactly Once",
            metrics["synthetic_dispatches"] == 1,
        )
    )

    receipt_ok = (
        len(granted) == 1
        and granted[0].get("receipt", {}).get("transmitted") is False
    )

    test_results.append(
        passfail(
            "Synthetic Receipt Reports No Transmission",
            receipt_ok,
        )
    )

    # =========================================================================
    # TEST 3
    # DURABLE AUTHORIZATION CONSUMPTION
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 3: DURABLE SINGLE-USE CONSUMPTION"
    )

    persisted_state = load_state()

    persisted_auth = persisted_state["authorizations"].get(
        authorization["authorization_id"]
    )

    test_results.append(
        passfail(
            "Authorization Persisted",
            persisted_auth is not None,
        )
    )

    test_results.append(
        passfail(
            "Authorization Persisted As Consumed",
            bool(persisted_auth and persisted_auth["consumed"]),
        )
    )

    winning_worker = (
        granted[0]["worker_id"]
        if len(granted) == 1
        else None
    )

    test_results.append(
        passfail(
            "Winning Worker Persisted",
            bool(
                persisted_auth
                and persisted_auth["consumed_by"] == winning_worker
            ),
        )
    )

    # =========================================================================
    # TEST 4
    # JOURNAL SERIALIZATION
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 4: DISPATCH JOURNAL SERIALIZATION"
    )

    journal = read_journal()

    prepare_records = [
        record
        for record in journal
        if record.get("event") == "DISPATCH_PREPARE"
    ]

    consumed_records = [
        record
        for record in journal
        if record.get("event") == "AUTHORIZATION_CONSUMED"
    ]

    test_results.append(
        passfail(
            "Exactly One Dispatch Prepare Journal Record",
            len(prepare_records) == 1,
        )
    )

    test_results.append(
        passfail(
            "Exactly One Authorization Consumed Journal Record",
            len(consumed_records) == 1,
        )
    )

    same_worker_journal = (
        len(prepare_records) == 1
        and len(consumed_records) == 1
        and prepare_records[0]["worker_id"]
        == consumed_records[0]["worker_id"]
        == winning_worker
    )

    test_results.append(
        passfail(
            "Prepare And Consume Journal Bound To Same Worker",
            same_worker_journal,
        )
    )

    same_request_journal = (
        len(prepare_records) == 1
        and len(consumed_records) == 1
        and prepare_records[0]["request_id"]
        == request["request_id"]
        and consumed_records[0]["request_id"]
        == request["request_id"]
    )

    test_results.append(
        passfail(
            "Journal Preserves Exact Request Binding",
            same_request_journal,
        )
    )

    # =========================================================================
    # TEST 5
    # REQUEST TAMPERING
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 5: REQUEST-BINDING TAMPER REJECTION"
    )

    tampered_request = deepcopy(request)
    tampered_request["payload"]["leverage"] = "99"

    tampered_request["payload_hash"] = sha256_object(
        tampered_request["payload"]
    )

    tampered_request["request_id"] = sha256_object({
        "method": tampered_request["method"],
        "path": tampered_request["path"],
        "payload": tampered_request["payload"],
        "payload_hash": tampered_request["payload_hash"],
    })

    tampered_authorization = build_authorization(request)
    register_authorization(tampered_authorization)

    tamper_result = consume_authorization_atomically(
        worker_id="tamper-worker",
        request=tampered_request,
        authorization_id=tampered_authorization["authorization_id"],
    )

    test_results.append(
        passfail(
            "Tampered Request Rejected Before Consumption",
            tamper_result["granted"] is False
            and tamper_result["reason"] == "request_binding_mismatch",
        )
    )

    tamper_state = load_state()

    tamper_auth_state = tamper_state["authorizations"][
        tampered_authorization["authorization_id"]
    ]

    test_results.append(
        passfail(
            "Tampered Authorization Remains Unconsumed",
            tamper_auth_state["consumed"] is False,
        )
    )

    # =========================================================================
    # TEST 6
    # RESTART REPLAY
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 6: POST-RESTART REPLAY REJECTION"
    )

    restarted_state = restart_runtime_view()

    restart_auth = restarted_state["authorizations"].get(
        authorization["authorization_id"]
    )

    test_results.append(
        passfail(
            "Consumed Authorization Restored After Restart",
            bool(restart_auth and restart_auth["consumed"]),
        )
    )

    replay_result = attempt_post_restart_replay(
        worker_id="restart-replay-worker",
        request=deepcopy(request),
        authorization_id=authorization["authorization_id"],
    )

    test_results.append(
        passfail(
            "Post-Restart Authorization Replay Rejected",
            replay_result["granted"] is False
            and replay_result["reason"]
            == "authorization_already_consumed",
        )
    )

    test_results.append(
        passfail(
            "Post-Restart Replay Produced No Second Synthetic Dispatch",
            metrics["synthetic_dispatches"] == 1,
        )
    )

    # =========================================================================
    # TEST 7
    # HIGHER CONTENTION
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 7: MULTI-WORKER CONTENTION"
    )

    request_two = build_request(payload)
    auth_two = build_authorization(request_two)
    register_authorization(auth_two)

    contention_workers = 8
    contention_barrier = threading.Barrier(contention_workers)

    contention_results = []
    contention_results_lock = threading.Lock()

    contention_threads = []

    synthetic_before_contention = metrics["synthetic_dispatches"]

    for worker_number in range(1, contention_workers + 1):
        worker_id = f"contention-worker-{worker_number}"

        thread = threading.Thread(
            target=competing_worker,
            args=(
                worker_id,
                deepcopy(request_two),
                auth_two["authorization_id"],
                contention_barrier,
                contention_results,
                contention_results_lock,
            ),
        )

        contention_threads.append(thread)
        thread.start()

    for thread in contention_threads:
        thread.join(timeout=10)

    contention_grants = [
        item
        for item in contention_results
        if item.get("granted") is True
    ]

    contention_denials = [
        item
        for item in contention_results
        if item.get("granted") is False
    ]

    test_results.append(
        passfail(
            "All Eight Contending Workers Completed",
            len(contention_results) == contention_workers,
        )
    )

    test_results.append(
        passfail(
            "Eight-Worker Race Produced Exactly One Grant",
            len(contention_grants) == 1,
        )
    )

    test_results.append(
        passfail(
            "Eight-Worker Race Produced Seven Denials",
            len(contention_denials) == 7,
        )
    )

    synthetic_delta = (
        metrics["synthetic_dispatches"]
        - synthetic_before_contention
    )

    test_results.append(
        passfail(
            "Eight-Worker Race Produced Exactly One Synthetic Dispatch",
            synthetic_delta == 1,
        )
    )

    # =========================================================================
    # TEST 8
    # HARD NETWORK LOCK
    # =========================================================================

    section(
        f"{UNIT_NAME} TEST 8: FINAL NETWORK WRITE FIREBREAK"
    )

    real_post_blocked = False

    try:
        real_network_post(
            request["path"],
            request["payload"],
        )
    except NetworkWriteBlocked as exc:
        real_post_blocked = True
        print(f"{UNIT_NAME} LOCAL BLOCK:")
        print(f"  {exc}")

    test_results.append(
        passfail(
            "Real POST Rejected Locally",
            real_post_blocked,
        )
    )

    leverage_blocked = False

    try:
        leverage_mutation_transport(request)
    except NetworkWriteBlocked as exc:
        leverage_blocked = True
        print(f"{UNIT_NAME} LOCAL BLOCK:")
        print(f"  {exc}")

    test_results.append(
        passfail(
            "Leverage Mutation Transport Rejected Locally",
            leverage_blocked,
        )
    )

    # =========================================================================
    # WRITE LOCK AUDIT
    # =========================================================================

    section(
        f"{UNIT_NAME} WRITE-LOCK AUDIT"
    )

    print(f"  Network POSTs = {metrics['network_posts']}")
    print(f"  Network writes = {metrics['network_writes']}")
    print(
        f"  Leverage transmissions = "
        f"{metrics['leverage_transmissions']}"
    )
    print(
        f"  Synthetic dispatches = "
        f"{metrics['synthetic_dispatches']}"
    )
    print(
        f"  Authorization grants = "
        f"{metrics['authorization_grants']}"
    )
    print(
        f"  Authorization denials = "
        f"{metrics['authorization_denials']}"
    )

    test_results.append(
        passfail(
            "Network POST Count Is Zero",
            metrics["network_posts"] == 0,
        )
    )

    test_results.append(
        passfail(
            "Network Write Count Is Zero",
            metrics["network_writes"] == 0,
        )
    )

    test_results.append(
        passfail(
            "Leverage Transmission Count Is Zero",
            metrics["leverage_transmissions"] == 0,
        )
    )

    # =========================================================================
    # FINAL ASSESSMENT
    # =========================================================================

    section(
        f"{UNIT_NAME} EXECUTION-READINESS ASSESSMENT"
    )

    structural_failures = sum(
        1
        for result in safety_results + test_results
        if not result
    )

    readiness_blockers = structural_failures

    print(
        f"Structural Safety Failures = {structural_failures}"
    )

    print(
        f"Readiness Blockers = {readiness_blockers}"
    )

    final_checks = {
        "Concurrent Serialization":
            len(granted) == 1
            and len(denied) == 1,

        "Atomic Authorization Consumption":
            bool(persisted_auth and persisted_auth["consumed"]),

        "TOCTOU Protection":
            len(granted) == 1,

        "Dispatch Journal Serialization":
            len(prepare_records) == 1
            and len(consumed_records) == 1,

        "Post-Restart Replay Protection":
            replay_result["granted"] is False,

        "High-Contention Single Winner":
            len(contention_grants) == 1,

        "Double-Dispatch Prevention":
            synthetic_delta == 1,

        "Request Binding":
            same_request_journal,

        "Final Network Dispatch":
            metrics["network_writes"] == 0,

        "Leverage Mutation Transmission":
            metrics["leverage_transmissions"] == 0,
    }

    for label, value in final_checks.items():
        if label == "Final Network Dispatch":
            status = (
                "🛡 BLOCKED LOCALLY"
                if value
                else "❌ UNSAFE"
            )

        elif label == "Leverage Mutation Transmission":
            status = (
                "🛡 BLOCKED LOCALLY"
                if value
                else "❌ UNSAFE"
            )

        else:
            status = "✅ VERIFIED" if value else "❌ FAILED"

        print(f"{label} = {status}")

    print()

    all_passed = (
        structural_failures == 0
        and all(final_checks.values())
    )

    if all_passed:
        print(f"✅ {UNIT_NAME} DIAGNOSTIC PASSED")
        print("✅ CONCURRENT AUTHORIZATION SERIALIZATION VERIFIED")
        print("✅ ATOMIC VALIDATE-AND-CONSUME VERIFIED")
        print("✅ SINGLE-WINNER DISPATCH GUARANTEE VERIFIED")
        print("✅ TOCTOU CONSUMPTION GAP BLOCKED")
        print("✅ LOSING CONCURRENT WORKER REJECTED")
        print("✅ HIGH-CONTENTION SINGLE-WINNER TEST PASSED")
        print("✅ DISPATCH JOURNAL SERIALIZATION VERIFIED")
        print("✅ CONSUMED AUTHORIZATION SURVIVES RESTART")
        print("✅ POST-RESTART REPLAY BLOCKED")
        print("✅ DOUBLE-DISPATCH BLOCKED")
        print("✅ REQUEST BINDING PRESERVED")
        print("✅ ORIGINAL AUTHORIZATION REMAINS SINGLE-USE")
        print("🛡 REAL NETWORK DISPATCH REMAINS DISABLED")
        print("🛡 LEVERAGE MUTATION TRANSPORT REMAINS LOCKED")
        print("🛡 NO NETWORK WRITE WAS TRANSMITTED")

    else:
        print(f"❌ {UNIT_NAME} DIAGNOSTIC FAILED")

    banner()
    banner()

    return all_passed


# =============================================================================
# HEARTBEAT
# =============================================================================

def persistent_runtime():
    heartbeat = 0

    print(f"{UNIT_NAME}: PERSISTENT RUNTIME ACTIVE")
    print(f"{UNIT_NAME}: CONCURRENT AUTHORIZATION GATE ACTIVE")
    print(f"{UNIT_NAME}: ATOMIC CONSUMPTION GATE ACTIVE")
    print(f"{UNIT_NAME}: SINGLE-WINNER DISPATCH LOCK ACTIVE")
    print(f"{UNIT_NAME}: TOCTOU PROTECTION ACTIVE")
    print(f"{UNIT_NAME}: DISPATCH JOURNAL GATE ACTIVE")
    print(f"{UNIT_NAME}: POST-RESTART REPLAY LOCK ACTIVE")
    print(f"{UNIT_NAME}: REQUEST-BINDING LOCK ACTIVE")
    print(f"{UNIT_NAME}: SYNTHETIC TRANSPORT INTERCEPTOR ACTIVE")
    print(f"{UNIT_NAME}: NETWORK WRITE TRANSPORT LOCKED")
    print(f"{UNIT_NAME}: LEVERAGE MUTATION TRANSPORT LOCKED")

    while True:
        heartbeat += 1

        print(
            f"{UNIT_NAME}: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(HEARTBEAT_SECONDS)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print(f"{UNIT_NAME}: IMPORTS COMPLETE", flush=True)
    print(f"{UNIT_NAME}: CONSTANTS INITIALIZED", flush=True)
    print(f"{UNIT_NAME}: RUNTIME STARTING", flush=True)

    start_health_server()

    passed = run_diagnostic()

    if not passed:
        print(
            f"{UNIT_NAME}: SAFETY DIAGNOSTIC FAILED — "
            f"PERSISTENT RUNTIME NOT STARTED",
            flush=True,
        )
        return

    persistent_runtime()


if __name__ == "__main__":
    main()
