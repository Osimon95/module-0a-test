import copy
import hashlib
import hmac
import json
import os
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


print("R28 UNIT N.13: MAIN.PY ENTERED")

# =============================================================================
# R28 UNIT N.13
# FINAL EXECUTION-BOUNDARY RECONCILIATION
#
# PURPOSE
# -----------------------------------------------------------------------------
# Verify that a crash-consistent, durable authorization/dispatch state can be
# reconciled immediately before transport without allowing stale state,
# tampering, replay, concurrent duplicate finalization, or network writes.
#
# IMPORTANT
# -----------------------------------------------------------------------------
# THIS UNIT DOES NOT SEND REAL ORDERS.
# THIS UNIT DOES NOT TRANSMIT LEVERAGE MUTATIONS.
# THIS UNIT DOES NOT PERFORM NETWORK POST/PUT/PATCH/DELETE.
#
# All execution handoffs terminate inside a synthetic transport interceptor.
# =============================================================================


UNIT = "R28 UNIT N.13"
SYMBOL = "BTCUSDT"
TARGET_LEVERAGE = 100
MARGIN_MODE = "ISOLATED"

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False

HEALTH_PORT = int(os.getenv("PORT", "10000"))
HEARTBEAT_SECONDS = 15

MAX_STATE_AGE_SECONDS = 120
SNAPSHOT_VERSION = 13

print("R28 UNIT N.13: IMPORTS COMPLETE")
print("R28 UNIT N.13: CONSTANTS INITIALIZED")


# =============================================================================
# GLOBAL AUDIT COUNTERS
# =============================================================================

audit_lock = threading.Lock()

AUDIT = {
    "network_posts": 0,
    "network_writes": 0,
    "leverage_transmissions": 0,
    "synthetic_dispatches": 0,
    "reconciliation_attempts": 0,
    "reconciliation_successes": 0,
    "reconciliation_rejections": 0,
    "finalization_attempts": 0,
    "finalization_successes": 0,
    "finalization_rejections": 0,
}


def bump(name, amount=1):
    with audit_lock:
        AUDIT[name] += amount


def audit_value(name):
    with audit_lock:
        return AUDIT[name]


# =============================================================================
# PRINT HELPERS
# =============================================================================

LINE = "-" * 92
DOUBLE_LINE = "=" * 92


def section(title):
    print()
    print(f"{UNIT} {title}")
    print(LINE)


def status(label, passed):
    marker = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<82} {marker}")
    return passed


def info(label, value):
    print(f"  {label} = {value}")


# =============================================================================
# CANONICAL SERIALIZATION / HASHING
# =============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_object(value):
    return sha256_text(canonical_json(value))


# =============================================================================
# LOCAL INTEGRITY KEY
# =============================================================================

# Diagnostic-only local sealing key.
#
# A fresh key per process is acceptable because each individual test constructs
# and consumes its own artifacts within the same process. Restart simulations
# copy the same diagnostic key into the simulated restarted runtime.
INTEGRITY_KEY = os.urandom(32)


def seal_payload(payload, key=INTEGRITY_KEY):
    body = canonical_json(payload).encode("utf-8")
    return hmac.new(key, body, hashlib.sha256).hexdigest()


def verify_seal(payload, seal, key=INTEGRITY_KEY):
    expected = seal_payload(payload, key)
    return hmac.compare_digest(expected, seal)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class LocalSafetyBlock(Exception):
    pass


class ReconciliationRejected(Exception):
    pass


class SnapshotRejected(Exception):
    pass


class ReplayRejected(Exception):
    pass


# =============================================================================
# EXECUTION REQUEST MODEL
# =============================================================================

def build_request(symbol=SYMBOL, leverage=TARGET_LEVERAGE, margin_mode=MARGIN_MODE):
    request = {
        "method": "POST",
        "path": "/capi/v3/account/leverage",
        "body": {
            "symbol": str(symbol),
            "leverage": str(leverage),
            "marginMode": str(margin_mode),
        },
    }

    request["body_hash"] = hash_object(request["body"])
    request["request_hash"] = hash_object(
        {
            "method": request["method"],
            "path": request["path"],
            "body": request["body"],
        }
    )

    return request


def build_dispatch_identity(request, authorization_id):
    material = {
        "authorization_id": authorization_id,
        "request_hash": request["request_hash"],
    }
    return "dispatch-" + hash_object(material)[:32]


# =============================================================================
# DURABLE EXECUTION STATE
# =============================================================================

def new_execution_state(
    request,
    account_epoch=1,
    symbol_epoch=1,
    position_epoch=1,
    now=None,
):
    now = time.time() if now is None else float(now)

    authorization_id = "auth-" + uuid.uuid4().hex
    dispatch_id = build_dispatch_identity(request, authorization_id)

    state = {
        "snapshot_version": SNAPSHOT_VERSION,
        "authorization_id": authorization_id,
        "authorization_status": "CONSUMED",
        "dispatch_id": dispatch_id,
        "dispatch_status": "PREPARED",
        "request": copy.deepcopy(request),
        "request_hash": request["request_hash"],
        "body_hash": request["body_hash"],
        "symbol": request["body"]["symbol"],
        "target_leverage": request["body"]["leverage"],
        "margin_mode": request["body"]["marginMode"],
        "account_epoch": int(account_epoch),
        "symbol_epoch": int(symbol_epoch),
        "position_epoch": int(position_epoch),
        "prepared_at": now,
        "finalization_status": "PENDING",
        "finalized_at": None,
        "completion_id": None,
        "journal": [
            {
                "event": "AUTHORIZATION_CONSUMED",
                "authorization_id": authorization_id,
                "dispatch_id": dispatch_id,
                "request_hash": request["request_hash"],
                "ts": now,
            },
            {
                "event": "DISPATCH_PREPARED",
                "authorization_id": authorization_id,
                "dispatch_id": dispatch_id,
                "request_hash": request["request_hash"],
                "ts": now,
            },
        ],
    }

    return state


# =============================================================================
# SNAPSHOT STORE
# =============================================================================

class SnapshotStore:
    def __init__(self, path, integrity_key=INTEGRITY_KEY):
        self.path = Path(path)
        self.integrity_key = integrity_key
        self.lock = threading.RLock()

    def _envelope(self, state):
        payload = copy.deepcopy(state)
        return {
            "payload": payload,
            "seal": seal_payload(payload, self.integrity_key),
        }

    def save(self, state):
        envelope = self._envelope(state)

        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            temp_path = self.path.with_suffix(
                self.path.suffix + "." + uuid.uuid4().hex + ".tmp"
            )

            with open(temp_path, "w", encoding="utf-8") as fh:
                json.dump(
                    envelope,
                    fh,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                fh.flush()
                os.fsync(fh.fileno())

            os.replace(temp_path, self.path)

    def load(self):
        with self.lock:
            if not self.path.exists():
                raise SnapshotRejected("snapshot does not exist")

            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    envelope = json.load(fh)
            except Exception as exc:
                raise SnapshotRejected(
                    f"snapshot unreadable: {exc}"
                ) from exc

            if not isinstance(envelope, dict):
                raise SnapshotRejected("snapshot envelope invalid")

            payload = envelope.get("payload")
            seal = envelope.get("seal")

            if not isinstance(payload, dict):
                raise SnapshotRejected("snapshot payload invalid")

            if not isinstance(seal, str):
                raise SnapshotRejected("snapshot seal missing")

            if not verify_seal(payload, seal, self.integrity_key):
                raise SnapshotRejected("snapshot integrity seal mismatch")

            return payload

    def corrupt_raw(self):
        with self.lock:
            with open(self.path, "w", encoding="utf-8") as fh:
                fh.write('{"payload":')


# =============================================================================
# OBSERVED EXECUTION BOUNDARY
# =============================================================================

def observed_boundary_state(
    account_epoch=1,
    symbol_epoch=1,
    position_epoch=1,
    symbol=SYMBOL,
    margin_mode=MARGIN_MODE,
    execution_permitted=True,
):
    return {
        "account_epoch": int(account_epoch),
        "symbol_epoch": int(symbol_epoch),
        "position_epoch": int(position_epoch),
        "symbol": str(symbol),
        "margin_mode": str(margin_mode),
        "execution_permitted": bool(execution_permitted),
    }


# =============================================================================
# NETWORK FIREBREAKS
# =============================================================================

def real_network_post(*args, **kwargs):
    print(f"{UNIT} LOCAL BLOCK:")
    print(f"  {UNIT} LOCAL BLOCK: real network POST is disabled.")
    raise LocalSafetyBlock("real network POST is disabled")


def generic_network_write(method, *args, **kwargs):
    print(f"{UNIT} LOCAL BLOCK:")
    print(
        f"  {UNIT} LOCAL BLOCK: network write method "
        f"{str(method).upper()} is disabled."
    )
    raise LocalSafetyBlock("network writes are disabled")


def leverage_mutation_transport(*args, **kwargs):
    print(f"{UNIT} LOCAL BLOCK:")
    print(
        f"  {UNIT} LOCAL BLOCK: leverage mutation transport is disabled."
    )
    raise LocalSafetyBlock("leverage mutation transport is disabled")


# =============================================================================
# SYNTHETIC TRANSPORT
# =============================================================================

class SyntheticTransport:
    def __init__(self):
        self.lock = threading.Lock()
        self.dispatches = []

    def dispatch(self, state):
        with self.lock:
            record = {
                "dispatch_id": state["dispatch_id"],
                "authorization_id": state["authorization_id"],
                "request_hash": state["request_hash"],
                "body_hash": state["body_hash"],
                "method": state["request"]["method"],
                "path": state["request"]["path"],
                "body": copy.deepcopy(state["request"]["body"]),
                "synthetic": True,
                "network_transmitted": False,
            }

            self.dispatches.append(record)
            bump("synthetic_dispatches")

            return copy.deepcopy(record)


# =============================================================================
# FINAL EXECUTION-BOUNDARY RECONCILER
# =============================================================================

class FinalBoundaryReconciler:
    def __init__(self, store, transport):
        self.store = store
        self.transport = transport
        self.finalization_lock = threading.Lock()

    def validate_snapshot_structure(self, state):
        required = [
            "snapshot_version",
            "authorization_id",
            "authorization_status",
            "dispatch_id",
            "dispatch_status",
            "request",
            "request_hash",
            "body_hash",
            "symbol",
            "target_leverage",
            "margin_mode",
            "account_epoch",
            "symbol_epoch",
            "position_epoch",
            "prepared_at",
            "finalization_status",
            "journal",
        ]

        for key in required:
            if key not in state:
                raise ReconciliationRejected(
                    f"required snapshot field missing: {key}"
                )

        if state["snapshot_version"] != SNAPSHOT_VERSION:
            raise ReconciliationRejected("snapshot version mismatch")

    def validate_request_binding(self, state):
        request = state["request"]

        if request.get("method") != "POST":
            raise ReconciliationRejected("request method binding mismatch")

        if request.get("path") != "/capi/v3/account/leverage":
            raise ReconciliationRejected("request path binding mismatch")

        body = request.get("body")

        if not isinstance(body, dict):
            raise ReconciliationRejected("request body invalid")

        calculated_body_hash = hash_object(body)

        if calculated_body_hash != state["body_hash"]:
            raise ReconciliationRejected("body hash binding mismatch")

        calculated_request_hash = hash_object(
            {
                "method": request["method"],
                "path": request["path"],
                "body": body,
            }
        )

        if calculated_request_hash != state["request_hash"]:
            raise ReconciliationRejected("request hash binding mismatch")

        if request.get("body_hash") != state["body_hash"]:
            raise ReconciliationRejected(
                "embedded body hash binding mismatch"
            )

        if request.get("request_hash") != state["request_hash"]:
            raise ReconciliationRejected(
                "embedded request hash binding mismatch"
            )

        expected_dispatch_id = build_dispatch_identity(
            request,
            state["authorization_id"],
        )

        if expected_dispatch_id != state["dispatch_id"]:
            raise ReconciliationRejected(
                "dispatch identity binding mismatch"
            )

        if body.get("symbol") != state["symbol"]:
            raise ReconciliationRejected("symbol binding mismatch")

        if body.get("leverage") != state["target_leverage"]:
            raise ReconciliationRejected("leverage binding mismatch")

        if body.get("marginMode") != state["margin_mode"]:
            raise ReconciliationRejected("margin mode binding mismatch")

    def validate_authorization_and_dispatch(self, state):
        if state["authorization_status"] != "CONSUMED":
            raise ReconciliationRejected(
                "authorization is not durably consumed"
            )

        if state["dispatch_status"] not in ("PREPARED", "COMPLETED"):
            raise ReconciliationRejected(
                "dispatch is not in a valid durable state"
            )

    def validate_freshness(self, state, now=None):
        now = time.time() if now is None else float(now)
        age = now - float(state["prepared_at"])

        if age < 0:
            raise ReconciliationRejected(
                "prepared dispatch timestamp is in the future"
            )

        if age > MAX_STATE_AGE_SECONDS:
            raise ReconciliationRejected(
                "prepared execution state is stale"
            )

    def validate_observed_state(self, state, observed):
        if not observed.get("execution_permitted"):
            raise ReconciliationRejected(
                "current execution boundary is not permitted"
            )

        if observed.get("symbol") != state["symbol"]:
            raise ReconciliationRejected(
                "observed symbol no longer matches prepared state"
            )

        if observed.get("margin_mode") != state["margin_mode"]:
            raise ReconciliationRejected(
                "observed margin mode changed before finalization"
            )

        if observed.get("account_epoch") != state["account_epoch"]:
            raise ReconciliationRejected(
                "account state changed before finalization"
            )

        if observed.get("symbol_epoch") != state["symbol_epoch"]:
            raise ReconciliationRejected(
                "symbol state changed before finalization"
            )

        if observed.get("position_epoch") != state["position_epoch"]:
            raise ReconciliationRejected(
                "position state changed before finalization"
            )

    def reconcile(self, state, observed, now=None):
        bump("reconciliation_attempts")

        try:
            self.validate_snapshot_structure(state)
            self.validate_authorization_and_dispatch(state)
            self.validate_request_binding(state)
            self.validate_freshness(state, now=now)
            self.validate_observed_state(state, observed)

            bump("reconciliation_successes")

            return {
                "dispatch_id": state["dispatch_id"],
                "authorization_id": state["authorization_id"],
                "request_hash": state["request_hash"],
                "body_hash": state["body_hash"],
                "reconciled": True,
            }

        except Exception:
            bump("reconciliation_rejections")
            raise

    def finalize(self, observed, now=None):
        bump("finalization_attempts")

        with self.finalization_lock:
            state = self.store.load()

            if state["finalization_status"] == "COMPLETED":
                bump("finalization_rejections")
                raise ReplayRejected(
                    "dispatch finalization replay blocked"
                )

            if state["finalization_status"] == "FINALIZING":
                bump("finalization_rejections")
                raise ReplayRejected(
                    "dispatch already finalizing"
                )

            try:
                reconciliation = self.reconcile(
                    state,
                    observed,
                    now=now,
                )
            except Exception:
                bump("finalization_rejections")
                raise

            state["finalization_status"] = "FINALIZING"
            state["journal"].append(
                {
                    "event": "FINAL_RECONCILIATION_ACCEPTED",
                    "dispatch_id": state["dispatch_id"],
                    "authorization_id": state["authorization_id"],
                    "request_hash": state["request_hash"],
                    "ts": time.time(),
                }
            )

            # Persist FINALIZING before synthetic handoff.
            self.store.save(state)

            dispatch_record = self.transport.dispatch(state)

            completion_id = (
                "completion-"
                + hash_object(
                    {
                        "dispatch_id": state["dispatch_id"],
                        "request_hash": state["request_hash"],
                    }
                )[:32]
            )

            state["finalization_status"] = "COMPLETED"
            state["dispatch_status"] = "COMPLETED"
            state["completion_id"] = completion_id
            state["finalized_at"] = time.time()

            state["journal"].append(
                {
                    "event": "DISPATCH_COMPLETED",
                    "dispatch_id": state["dispatch_id"],
                    "authorization_id": state["authorization_id"],
                    "request_hash": state["request_hash"],
                    "completion_id": completion_id,
                    "ts": state["finalized_at"],
                }
            )

            self.store.save(state)

            bump("finalization_successes")

            return {
                "reconciliation": reconciliation,
                "dispatch": dispatch_record,
                "completion_id": completion_id,
            }


# =============================================================================
# TEST ENVIRONMENT
# =============================================================================

class DiagnosticEnvironment:
    def __init__(self):
        self.tempdir = tempfile.TemporaryDirectory(
            prefix="r28-n13-"
        )

        self.snapshot_path = os.path.join(
            self.tempdir.name,
            "execution_snapshot.json",
        )

        self.store = SnapshotStore(self.snapshot_path)
        self.transport = SyntheticTransport()

    def close(self):
        self.tempdir.cleanup()


def make_ready_environment(
    prepared_at=None,
    account_epoch=1,
    symbol_epoch=1,
    position_epoch=1,
):
    env = DiagnosticEnvironment()

    request = build_request()

    state = new_execution_state(
        request,
        account_epoch=account_epoch,
        symbol_epoch=symbol_epoch,
        position_epoch=position_epoch,
        now=prepared_at,
    )

    env.store.save(state)

    reconciler = FinalBoundaryReconciler(
        env.store,
        env.transport,
    )

    return env, state, reconciler


# =============================================================================
# TEST 1
# COMPLETE FINAL EXECUTION-BOUNDARY RECONCILIATION
# =============================================================================

def test_complete_reconciliation():
    section("TEST 1: COMPLETE FINAL EXECUTION-BOUNDARY RECONCILIATION")

    env, state, reconciler = make_ready_environment()

    try:
        observed = observed_boundary_state()

        result = reconciler.finalize(observed)

        saved = env.store.load()

        checks = []

        checks.append(
            status(
                "Durable Authorization Was Consumed",
                saved["authorization_status"] == "CONSUMED",
            )
        )

        checks.append(
            status(
                "Prepared Dispatch Reconciled Successfully",
                result["reconciliation"]["reconciled"] is True,
            )
        )

        checks.append(
            status(
                "Synthetic Final Transport Handoff Completed",
                result["dispatch"]["synthetic"] is True,
            )
        )

        checks.append(
            status(
                "Synthetic Handoff Reports No Network Transmission",
                result["dispatch"]["network_transmitted"] is False,
            )
        )

        checks.append(
            status(
                "Finalization Persisted As Completed",
                saved["finalization_status"] == "COMPLETED",
            )
        )

        checks.append(
            status(
                "Dispatch Persisted As Completed",
                saved["dispatch_status"] == "COMPLETED",
            )
        )

        checks.append(
            status(
                "Completion Identity Persisted",
                bool(saved["completion_id"]),
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 2
# EXACT REQUEST BINDING PRESERVATION
# =============================================================================

def test_exact_request_binding():
    section("TEST 2: EXACT REQUEST BINDING PRESERVATION")

    env, original, reconciler = make_ready_environment()

    try:
        observed = observed_boundary_state()
        result = reconciler.finalize(observed)

        dispatch = result["dispatch"]

        checks = []

        checks.append(
            status(
                "Exact Request Hash Preserved",
                dispatch["request_hash"] == original["request_hash"],
            )
        )

        checks.append(
            status(
                "Exact Body Hash Preserved",
                dispatch["body_hash"] == original["body_hash"],
            )
        )

        checks.append(
            status(
                "Exact Dispatch Identity Preserved",
                dispatch["dispatch_id"] == original["dispatch_id"],
            )
        )

        checks.append(
            status(
                "Exact Authorization Identity Preserved",
                dispatch["authorization_id"]
                == original["authorization_id"],
            )
        )

        checks.append(
            status(
                "Exact V3 Endpoint Preserved",
                dispatch["path"]
                == "/capi/v3/account/leverage",
            )
        )

        checks.append(
            status(
                "Exact POST Method Preserved",
                dispatch["method"] == "POST",
            )
        )

        checks.append(
            status(
                "Exact Leverage Payload Preserved",
                dispatch["body"] == original["request"]["body"],
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 3
# STALE PREPARED STATE REJECTION
# =============================================================================

def test_stale_state_rejection():
    section("TEST 3: STALE PREPARED STATE REJECTION")

    old_time = time.time() - MAX_STATE_AGE_SECONDS - 5

    env, state, reconciler = make_ready_environment(
        prepared_at=old_time
    )

    try:
        before = len(env.transport.dispatches)

        rejected = False

        try:
            reconciler.finalize(
                observed_boundary_state(),
                now=time.time(),
            )
        except ReconciliationRejected:
            rejected = True

        after = len(env.transport.dispatches)

        checks = []

        checks.append(
            status(
                "Stale Prepared State Rejected",
                rejected,
            )
        )

        checks.append(
            status(
                "Stale State Produced No Synthetic Dispatch",
                after == before,
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 4
# CHANGED ACCOUNT / SYMBOL / POSITION STATE REJECTION
# =============================================================================

def test_changed_boundary_state_rejection():
    section("TEST 4: CHANGED EXECUTION-BOUNDARY STATE REJECTION")

    variants = [
        (
            "Changed Account Epoch Rejected",
            observed_boundary_state(account_epoch=2),
        ),
        (
            "Changed Symbol Epoch Rejected",
            observed_boundary_state(symbol_epoch=2),
        ),
        (
            "Changed Position Epoch Rejected",
            observed_boundary_state(position_epoch=2),
        ),
        (
            "Changed Symbol Rejected",
            observed_boundary_state(symbol="ETHUSDT"),
        ),
        (
            "Changed Margin Mode Rejected",
            observed_boundary_state(margin_mode="CROSS"),
        ),
        (
            "Execution Permission Revocation Rejected",
            observed_boundary_state(execution_permitted=False),
        ),
    ]

    all_checks = []

    for label, observed in variants:
        env, state, reconciler = make_ready_environment()

        try:
            before = len(env.transport.dispatches)

            rejected = False

            try:
                reconciler.finalize(observed)
            except ReconciliationRejected:
                rejected = True

            after = len(env.transport.dispatches)

            all_checks.append(
                status(
                    label,
                    rejected,
                )
            )

            all_checks.append(
                status(
                    f"{label} Produced No Synthetic Dispatch",
                    after == before,
                )
            )

        finally:
            env.close()

    return all(all_checks)


# =============================================================================
# TEST 5
# TAMPERED FINAL REQUEST REJECTION
# =============================================================================

def test_tampered_request_rejection():
    section("TEST 5: TAMPERED FINAL REQUEST BINDING REJECTION")

    env, state, reconciler = make_ready_environment()

    try:
        tampered = env.store.load()

        tampered["request"]["body"]["leverage"] = "101"

        # Intentionally reseal the snapshot at the storage level to model a
        # logically modified but structurally valid state. The immutable
        # request/body bindings must still reject it.
        env.store.save(tampered)

        before = len(env.transport.dispatches)

        rejected = False

        try:
            reconciler.finalize(
                observed_boundary_state()
            )
        except ReconciliationRejected:
            rejected = True

        after = len(env.transport.dispatches)

        checks = []

        checks.append(
            status(
                "Tampered Final Request Binding Rejected",
                rejected,
            )
        )

        checks.append(
            status(
                "Tampered Request Produced No Synthetic Dispatch",
                after == before,
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 6
# CORRUPTED SNAPSHOT INTEGRITY REJECTION
# =============================================================================

def test_corrupted_snapshot_rejection():
    section("TEST 6: CORRUPTED FINALIZATION SNAPSHOT REJECTION")

    env, state, reconciler = make_ready_environment()

    try:
        envelope = None

        with open(env.snapshot_path, "r", encoding="utf-8") as fh:
            envelope = json.load(fh)

        envelope["payload"]["request"]["body"]["leverage"] = "400"

        # Do NOT update the integrity seal.
        with open(env.snapshot_path, "w", encoding="utf-8") as fh:
            json.dump(
                envelope,
                fh,
                sort_keys=True,
                separators=(",", ":"),
            )

        before = len(env.transport.dispatches)

        rejected = False

        try:
            reconciler.finalize(
                observed_boundary_state()
            )
        except SnapshotRejected:
            rejected = True

        after = len(env.transport.dispatches)

        checks = []

        checks.append(
            status(
                "Corrupted Snapshot Integrity Seal Rejected",
                rejected,
            )
        )

        checks.append(
            status(
                "Corrupted Snapshot Produced No Synthetic Dispatch",
                after == before,
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 7
# DUPLICATE FINALIZATION REPLAY REJECTION
# =============================================================================

def test_finalization_replay_rejection():
    section("TEST 7: POST-FINALIZATION REPLAY REJECTION")

    env, state, reconciler = make_ready_environment()

    try:
        observed = observed_boundary_state()

        reconciler.finalize(observed)

        first_count = len(env.transport.dispatches)

        rejected = False

        try:
            reconciler.finalize(observed)
        except ReplayRejected:
            rejected = True

        second_count = len(env.transport.dispatches)

        checks = []

        checks.append(
            status(
                "Second Finalization Replay Rejected",
                rejected,
            )
        )

        checks.append(
            status(
                "Replay Produced No Second Synthetic Dispatch",
                second_count == first_count,
            )
        )

        checks.append(
            status(
                "Exactly One Synthetic Dispatch Exists",
                second_count == 1,
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 8
# CONCURRENT FINALIZATION SINGLE WINNER
# =============================================================================

def test_concurrent_finalization():
    section("TEST 8: CONCURRENT FINALIZATION SINGLE-WINNER")

    env, state, reconciler = make_ready_environment()

    try:
        observed = observed_boundary_state()

        workers = 8
        barrier = threading.Barrier(workers)

        results_lock = threading.Lock()
        winners = []
        losers = []

        def worker(worker_id):
            try:
                barrier.wait()

                result = reconciler.finalize(observed)

                with results_lock:
                    winners.append(
                        (
                            worker_id,
                            result["dispatch"]["dispatch_id"],
                        )
                    )

            except Exception as exc:
                with results_lock:
                    losers.append(
                        (
                            worker_id,
                            type(exc).__name__,
                        )
                    )

        threads = []

        for worker_id in range(workers):
            thread = threading.Thread(
                target=worker,
                args=(worker_id,),
                daemon=True,
            )

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        checks = []

        checks.append(
            status(
                "All Eight Finalization Workers Completed",
                len(winners) + len(losers) == workers,
            )
        )

        checks.append(
            status(
                "Eight-Worker Finalization Race Produced Exactly One Winner",
                len(winners) == 1,
            )
        )

        checks.append(
            status(
                "Concurrent Finalization Produced Exactly One Synthetic Dispatch",
                len(env.transport.dispatches) == 1,
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 9
# RESTART AFTER COMPLETION PRESERVES IDEMPOTENCY
# =============================================================================

def test_restart_after_completion():
    section("TEST 9: RESTART AFTER COMPLETION IDEMPOTENCY")

    env, state, reconciler = make_ready_environment()

    try:
        observed = observed_boundary_state()

        first = reconciler.finalize(observed)

        dispatch_count_before = len(env.transport.dispatches)

        # Simulated restart:
        #
        # - create a new reconciler instance
        # - preserve the durable snapshot
        # - preserve the synthetic transport audit stream
        restarted_reconciler = FinalBoundaryReconciler(
            env.store,
            env.transport,
        )

        replay_rejected = False

        try:
            restarted_reconciler.finalize(observed)
        except ReplayRejected:
            replay_rejected = True

        dispatch_count_after = len(env.transport.dispatches)

        restored = env.store.load()

        checks = []

        checks.append(
            status(
                "Completed State Survived Restart",
                restored["finalization_status"] == "COMPLETED",
            )
        )

        checks.append(
            status(
                "Completion Identity Survived Restart",
                restored["completion_id"]
                == first["completion_id"],
            )
        )

        checks.append(
            status(
                "Post-Restart Finalization Replay Rejected",
                replay_rejected,
            )
        )

        checks.append(
            status(
                "Restart Replay Produced No Second Synthetic Dispatch",
                dispatch_count_after == dispatch_count_before,
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 10
# FINALIZATION JOURNAL CONSISTENCY
# =============================================================================

def test_journal_consistency():
    section("TEST 10: FINALIZATION JOURNAL CONSISTENCY")

    env, original, reconciler = make_ready_environment()

    try:
        reconciler.finalize(
            observed_boundary_state()
        )

        state = env.store.load()

        consumed = [
            item
            for item in state["journal"]
            if item.get("event") == "AUTHORIZATION_CONSUMED"
        ]

        prepared = [
            item
            for item in state["journal"]
            if item.get("event") == "DISPATCH_PREPARED"
        ]

        reconciled = [
            item
            for item in state["journal"]
            if item.get("event")
            == "FINAL_RECONCILIATION_ACCEPTED"
        ]

        completed = [
            item
            for item in state["journal"]
            if item.get("event") == "DISPATCH_COMPLETED"
        ]

        checks = []

        checks.append(
            status(
                "Exactly One Authorization Consumed Record",
                len(consumed) == 1,
            )
        )

        checks.append(
            status(
                "Exactly One Dispatch Prepare Record",
                len(prepared) == 1,
            )
        )

        checks.append(
            status(
                "Exactly One Final Reconciliation Record",
                len(reconciled) == 1,
            )
        )

        checks.append(
            status(
                "Exactly One Dispatch Completion Record",
                len(completed) == 1,
            )
        )

        identities = {
            consumed[0]["dispatch_id"],
            prepared[0]["dispatch_id"],
            reconciled[0]["dispatch_id"],
            completed[0]["dispatch_id"],
        }

        checks.append(
            status(
                "Finalization Journal Preserves Same Dispatch Identity",
                identities == {original["dispatch_id"]},
            )
        )

        request_hashes = {
            consumed[0]["request_hash"],
            prepared[0]["request_hash"],
            reconciled[0]["request_hash"],
            completed[0]["request_hash"],
        }

        checks.append(
            status(
                "Finalization Journal Preserves Exact Request Binding",
                request_hashes == {original["request_hash"]},
            )
        )

        return all(checks)

    finally:
        env.close()


# =============================================================================
# TEST 11
# REAL NETWORK WRITE FIREBREAK
# =============================================================================

def test_network_firebreak():
    section("TEST 11: FINAL NETWORK WRITE FIREBREAK")

    checks = []

    before_posts = audit_value("network_posts")
    before_writes = audit_value("network_writes")
    before_leverage = audit_value("leverage_transmissions")

    blocked_post = False

    try:
        real_network_post(
            "/capi/v3/account/leverage",
            {"leverage": "100"},
        )
    except LocalSafetyBlock:
        blocked_post = True

    checks.append(
        status(
            "Real POST Rejected Locally",
            blocked_post,
        )
    )

    blocked_put = False

    try:
        generic_network_write(
            "PUT",
            "/unsafe/write",
        )
    except LocalSafetyBlock:
        blocked_put = True

    checks.append(
        status(
            "Generic Network Write Rejected Locally",
            blocked_put,
        )
    )

    blocked_leverage = False

    try:
        leverage_mutation_transport(
            {
                "symbol": SYMBOL,
                "leverage": str(TARGET_LEVERAGE),
                "marginMode": MARGIN_MODE,
            }
        )
    except LocalSafetyBlock:
        blocked_leverage = True

    checks.append(
        status(
            "Leverage Mutation Transport Rejected Locally",
            blocked_leverage,
        )
    )

    checks.append(
        status(
            "Real POST Block Produced No Network POST",
            audit_value("network_posts") == before_posts,
        )
    )

    checks.append(
        status(
            "Write Firebreak Produced No Network Write",
            audit_value("network_writes") == before_writes,
        )
    )

    checks.append(
        status(
            "Leverage Firebreak Produced No Transmission",
            audit_value("leverage_transmissions") == before_leverage,
        )
    )

    return all(checks)


# =============================================================================
# TEST 12
# EXACT PAYLOAD VALIDATION
# =============================================================================

def test_exact_payload():
    section("TEST 12: EXACT PAYLOAD / ENDPOINT IMMUTABILITY")

    request = build_request()

    expected_body = {
        "leverage": "100",
        "marginMode": "ISOLATED",
        "symbol": "BTCUSDT",
    }

    expected_canonical = (
        '{"leverage":"100","marginMode":"ISOLATED","symbol":"BTCUSDT"}'
    )

    print(
        f"Payload = {canonical_json(request['body'])}"
    )
    print(
        f"Payload SHA256 = {request['body_hash']}"
    )

    checks = []

    checks.append(
        status(
            "Exact Leverage Payload Preserved",
            request["body"] == expected_body,
        )
    )

    checks.append(
        status(
            "Canonical Payload Serialization Preserved",
            canonical_json(request["body"])
            == expected_canonical,
        )
    )

    checks.append(
        status(
            "Transport Method Exactly POST",
            request["method"] == "POST",
        )
    )

    checks.append(
        status(
            "Transport Path Exactly Leverage Endpoint",
            request["path"]
            == "/capi/v3/account/leverage",
        )
    )

    return all(checks)


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(
            {
                "status": "ok",
                "unit": "R28-N.13",
                "runtime": "active",
                "network_writes": False,
                "real_post": False,
                "leverage_transport": False,
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
    try:
        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        print(
            f"R28 UNIT N.13: HEALTH SERVER ACTIVE "
            f"ON PORT {HEALTH_PORT}"
        )

        return server

    except Exception as exc:
        print(
            f"R28 UNIT N.13: HEALTH SERVER WARNING: {exc}"
        )

        return None


# =============================================================================
# DIAGNOSTIC RUNNER
# =============================================================================

def run_diagnostic():
    print("R28 UNIT N.13: RUNTIME STARTING")

    health_server = start_health_server()

    print(DOUBLE_LINE)
    print("0F-4H-R28-UNIT-N.13 STARTING")
    print("FINAL EXECUTION-BOUNDARY RECONCILIATION")
    print("CRASH-CONSISTENT FINALIZATION / REPLAY SAFETY")
    print("SYNTHETIC TRANSPORT ONLY")
    print("REAL NETWORK POST DISABLED")
    print("NETWORK WRITES DISABLED")
    print("LEVERAGE MUTATION TRANSPORT DISABLED")
    print(DOUBLE_LINE)

    section("NETWORK POLICY")

    policy_checks = []

    policy_checks.append(
        status(
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        )
    )

    policy_checks.append(
        status(
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    policy_checks.append(
        status(
            "Network Writes Disabled",
            NETWORK_WRITES_ENABLED is False,
        )
    )

    policy_checks.append(
        status(
            "Leverage Mutation Transport Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        )
    )

    tests = [
        test_complete_reconciliation,
        test_exact_request_binding,
        test_stale_state_rejection,
        test_changed_boundary_state_rejection,
        test_tampered_request_rejection,
        test_corrupted_snapshot_rejection,
        test_finalization_replay_rejection,
        test_concurrent_finalization,
        test_restart_after_completion,
        test_journal_consistency,
        test_network_firebreak,
        test_exact_payload,
    ]

    results = list(policy_checks)

    for test in tests:
        try:
            results.append(bool(test()))

        except Exception as exc:
            print()
            print(
                f"{UNIT}: UNEXPECTED TEST ERROR: "
                f"{type(exc).__name__}: {exc}"
            )
            results.append(False)

    section("WRITE-LOCK AUDIT")

    info(
        "Network POSTs",
        audit_value("network_posts"),
    )

    info(
        "Network writes",
        audit_value("network_writes"),
    )

    info(
        "Leverage transmissions",
        audit_value("leverage_transmissions"),
    )

    info(
        "Synthetic dispatches",
        audit_value("synthetic_dispatches"),
    )

    info(
        "Reconciliation attempts",
        audit_value("reconciliation_attempts"),
    )

    info(
        "Reconciliation successes",
        audit_value("reconciliation_successes"),
    )

    info(
        "Reconciliation rejections",
        audit_value("reconciliation_rejections"),
    )

    info(
        "Finalization attempts",
        audit_value("finalization_attempts"),
    )

    info(
        "Finalization successes",
        audit_value("finalization_successes"),
    )

    info(
        "Finalization rejections",
        audit_value("finalization_rejections"),
    )

    audit_checks = []

    audit_checks.append(
        status(
            "Network POST Count Is Zero",
            audit_value("network_posts") == 0,
        )
    )

    audit_checks.append(
        status(
            "Network Write Count Is Zero",
            audit_value("network_writes") == 0,
        )
    )

    audit_checks.append(
        status(
            "Leverage Transmission Count Is Zero",
            audit_value("leverage_transmissions") == 0,
        )
    )

    results.extend(audit_checks)

    failures = sum(
        1
        for result in results
        if result is not True
    )

    blockers = failures

    section("EXECUTION-READINESS ASSESSMENT")

    info(
        "Structural Safety Failures",
        failures,
    )

    info(
        "Readiness Blockers",
        blockers,
    )

    readiness = {
        "Final Boundary Reconciliation":
            "✅ VERIFIED",
        "Exact Request Binding":
            "✅ VERIFIED",
        "Stale State Rejection":
            "✅ VERIFIED",
        "Account State Drift Rejection":
            "✅ VERIFIED",
        "Symbol State Drift Rejection":
            "✅ VERIFIED",
        "Position State Drift Rejection":
            "✅ VERIFIED",
        "Request Tamper Rejection":
            "✅ VERIFIED",
        "Snapshot Integrity":
            "✅ VERIFIED",
        "Finalization Replay Protection":
            "✅ VERIFIED",
        "Concurrent Finalization Single Winner":
            "✅ VERIFIED",
        "Restart Finalization Idempotency":
            "✅ VERIFIED",
        "Finalization Journal Serialization":
            "✅ VERIFIED",
        "Final Network Dispatch":
            "🛡 BLOCKED LOCALLY",
        "Leverage Mutation Transmission":
            "🛡 BLOCKED LOCALLY",
    }

    if failures != 0:
        # Do not falsely advertise VERIFIED if an assertion failed.
        for key in list(readiness.keys()):
            if readiness[key] == "✅ VERIFIED":
                readiness[key] = "❌ NOT VERIFIED"

    for key, value in readiness.items():
        info(key, value)

    print()

    if failures == 0:
        print("✅ R28 UNIT N.13 DIAGNOSTIC PASSED")
        print(
            "✅ FINAL EXECUTION-BOUNDARY "
            "RECONCILIATION VERIFIED"
        )
        print(
            "✅ DURABLE AUTHORIZATION RECONCILES "
            "AT FINAL BOUNDARY"
        )
        print(
            "✅ EXACT REQUEST IDENTITY AND HASH "
            "PRESERVED"
        )
        print(
            "✅ STALE EXECUTION STATE REJECTED"
        )
        print(
            "✅ ACCOUNT / SYMBOL / POSITION "
            "STATE DRIFT REJECTED"
        )
        print(
            "✅ TAMPERED FINAL REQUEST REJECTED"
        )
        print(
            "✅ CORRUPTED FINALIZATION SNAPSHOT "
            "REJECTED"
        )
        print(
            "✅ COMPLETED FINALIZATION IS NOT "
            "REPEATED"
        )
        print(
            "✅ CONCURRENT FINALIZATION PRODUCES "
            "SINGLE WINNER"
        )
        print(
            "✅ POST-RESTART FINALIZATION "
            "REMAINS IDEMPOTENT"
        )
        print(
            "✅ FINALIZATION JOURNAL "
            "SERIALIZATION VERIFIED"
        )
        print(
            "🛡 REAL NETWORK DISPATCH "
            "REMAINS DISABLED"
        )
        print(
            "🛡 LEVERAGE MUTATION TRANSPORT "
            "REMAINS LOCKED"
        )
        print(
            "🛡 NO NETWORK WRITE WAS TRANSMITTED"
        )

    else:
        print("❌ R28 UNIT N.13 DIAGNOSTIC FAILED")
        print(
            "❌ DO NOT ADVANCE PAST UNIT N.13"
        )

    print(DOUBLE_LINE)
    print(DOUBLE_LINE)

    return failures == 0, health_server


# =============================================================================
# PERSISTENT RUNTIME
# =============================================================================

def persistent_runtime():
    passed, health_server = run_diagnostic()

    if not passed:
        print(
            "R28 UNIT N.13: PERSISTENT RUNTIME "
            "NOT STARTED BECAUSE DIAGNOSTIC FAILED"
        )

        while True:
            time.sleep(60)

    print(
        "R28 UNIT N.13: PERSISTENT RUNTIME ACTIVE"
    )
    print(
        "R28 UNIT N.13: FINAL RECONCILIATION "
        "GATE ACTIVE"
    )
    print(
        "R28 UNIT N.13: STALE-STATE "
        "REJECTION GATE ACTIVE"
    )
    print(
        "R28 UNIT N.13: ACCOUNT-STATE "
        "BINDING LOCK ACTIVE"
    )
    print(
        "R28 UNIT N.13: SYMBOL-STATE "
        "BINDING LOCK ACTIVE"
    )
    print(
        "R28 UNIT N.13: POSITION-STATE "
        "BINDING LOCK ACTIVE"
    )
    print(
        "R28 UNIT N.13: REQUEST-BINDING "
        "FINALIZATION LOCK ACTIVE"
    )
    print(
        "R28 UNIT N.13: SNAPSHOT INTEGRITY "
        "LOCK ACTIVE"
    )
    print(
        "R28 UNIT N.13: FINALIZATION REPLAY "
        "LOCK ACTIVE"
    )
    print(
        "R28 UNIT N.13: CONCURRENT FINALIZATION "
        "LOCK ACTIVE"
    )
    print(
        "R28 UNIT N.13: SYNTHETIC TRANSPORT "
        "INTERCEPTOR ACTIVE"
    )
    print(
        "R28 UNIT N.13: NETWORK WRITE "
        "TRANSPORT LOCKED"
    )
    print(
        "R28 UNIT N.13: LEVERAGE MUTATION "
        "TRANSPORT LOCKED"
    )

    heartbeat = 0

    while True:
        heartbeat += 1

        print(
            f"R28 UNIT N.13: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(HEARTBEAT_SECONDS)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    persistent_runtime()
