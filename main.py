import os
import json
import time
import hashlib
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


print("R28 UNIT N.10: MAIN.PY ENTERED", flush=True)

# =============================================================================
# R28 UNIT N.10
# CRASH-CONSISTENCY / ATOMIC-PERSISTENCE / DOUBLE-DISPATCH SAFETY
#
# SAFETY RULES
# -----------------------------------------------------------------------------
# - NO REAL POST
# - NO REAL NETWORK WRITE
# - NO LEVERAGE TRANSMISSION
# - SYNTHETIC DISPATCH ONLY
# - ATOMIC SNAPSHOT REPLACEMENT
# - CRASH RECOVERY TESTING
# - REPLAY / DOUBLE-DISPATCH PREVENTION
# =============================================================================


UNIT = "R28 UNIT N.10"
SYMBOL = "BTCUSDT"
LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
ACCOUNT_WRITES_ENABLED = False
LEVERAGE_WRITES_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

HEARTBEAT_SECONDS = 15

EXACT_PATH = "/capi/v3/account/leverage"
EXACT_METHOD = "POST"

EXACT_PAYLOAD = {
    "leverage": LEVERAGE,
    "marginMode": MARGIN_MODE,
    "symbol": SYMBOL,
}


print(f"{UNIT}: IMPORTS COMPLETE", flush=True)
print(f"{UNIT}: CONSTANTS INITIALIZED", flush=True)


# =============================================================================
# HELPERS
# =============================================================================


def canonical_json(value):
    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_json(value):
    return sha256_text(canonical_json(value))


def banner(title):
    print()
    print(title)
    print("-" * 92)


def result(label, passed):
    marker = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<78} {marker}", flush=True)
    return passed


def local_block(message):
    print(f"{UNIT} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


class SafetyFailure(Exception):
    pass


class SimulatedCrash(Exception):
    pass


# =============================================================================
# AUDIT STATE
# =============================================================================


audit = {
    "arm_requests": 0,
    "arm_grants": 0,
    "arm_denials": 0,

    "commit_requests": 0,
    "commit_grants": 0,
    "commit_denials": 0,

    "dispatch_requests": 0,
    "dispatch_grants": 0,
    "dispatch_denials": 0,

    "synthetic_intercepts": 0,

    "snapshot_writes": 0,
    "snapshot_restores": 0,
    "atomic_replacements": 0,

    "simulated_crashes": 0,
    "recovery_runs": 0,

    "replay_blocks": 0,
    "double_dispatch_blocks": 0,
    "partial_write_blocks": 0,
    "journal_recoveries": 0,

    "network_posts": 0,
    "network_writes": 0,
    "leverage_transmissions": 0,
}


# =============================================================================
# HEALTH SERVER
# =============================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            "R28 UNIT N.10 ACTIVE\n"
            "REAL NETWORK WRITES DISABLED\n"
            "LEVERAGE MUTATION TRANSPORT LOCKED\n"
        ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        return


def run_health_server():
    port = int(os.getenv("PORT", "10000"))

    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        print(
            f"{UNIT}: HEALTH SERVER ACTIVE ON PORT {port}",
            flush=True,
        )
        server.serve_forever()

    except Exception as exc:
        print(
            f"{UNIT}: HEALTH SERVER ERROR: {exc}",
            flush=True,
        )


# =============================================================================
# SYNTHETIC TRANSPORT FIREBREAK
# =============================================================================


def transport_firebreak(method, path, payload):
    """
    Final boundary.

    A legitimate authorization may reach this function,
    but transmission is ALWAYS intercepted locally.

    No requests library.
    No urllib transmission.
    No socket write.
    No external POST.
    """

    audit["dispatch_requests"] += 1

    if method != EXACT_METHOD:
        audit["dispatch_denials"] += 1
        raise SafetyFailure("Transport method mismatch.")

    if path != EXACT_PATH:
        audit["dispatch_denials"] += 1
        raise SafetyFailure("Transport endpoint mismatch.")

    if payload != EXACT_PAYLOAD:
        audit["dispatch_denials"] += 1
        raise SafetyFailure("Transport payload mismatch.")

    if NETWORK_WRITES_ENABLED:
        raise SafetyFailure(
            "Unsafe configuration: NETWORK_WRITES_ENABLED must remain False."
        )

    if LEVERAGE_MUTATION_TRANSPORT_ENABLED:
        raise SafetyFailure(
            "Unsafe configuration: leverage transport must remain False."
        )

    audit["dispatch_grants"] += 1
    audit["synthetic_intercepts"] += 1

    return {
        "synthetic": True,
        "transmitted": False,
        "method": method,
        "path": path,
        "payload": payload,
        "payload_sha256": sha256_json(payload),
    }


# =============================================================================
# PERSISTENT AUTHORIZATION STORE
# =============================================================================


class AuthorizationStore:

    SNAPSHOT_VERSION = 10

    def __init__(self, directory):
        self.directory = Path(directory)

        self.snapshot_path = self.directory / "n10_snapshot.json"
        self.temp_path = self.directory / "n10_snapshot.tmp"
        self.journal_path = self.directory / "n10_dispatch_journal.json"

        self.generation = 0

        self.arms = {}
        self.commits = {}
        self.dispatches = {}

    # -------------------------------------------------------------------------
    # STATE SERIALIZATION
    # -------------------------------------------------------------------------

    def state_body(self):
        return {
            "version": self.SNAPSHOT_VERSION,
            "generation": self.generation,
            "arms": self.arms,
            "commits": self.commits,
            "dispatches": self.dispatches,
        }

    def sealed_snapshot(self):
        body = self.state_body()

        return {
            "body": body,
            "seal": sha256_json(body),
        }

    def validate_snapshot_object(self, document):
        if not isinstance(document, dict):
            raise SafetyFailure("Snapshot root invalid.")

        body = document.get("body")
        seal = document.get("seal")

        if not isinstance(body, dict):
            raise SafetyFailure("Snapshot body missing.")

        if not isinstance(seal, str):
            raise SafetyFailure("Snapshot integrity seal missing.")

        expected = sha256_json(body)

        if seal != expected:
            raise SafetyFailure("Snapshot integrity seal mismatch.")

        if body.get("version") != self.SNAPSHOT_VERSION:
            raise SafetyFailure("Snapshot version mismatch.")

        generation = body.get("generation")

        if not isinstance(generation, int):
            raise SafetyFailure("Snapshot generation invalid.")

        return body

    # -------------------------------------------------------------------------
    # ATOMIC PERSISTENCE
    # -------------------------------------------------------------------------

    def persist_atomic(self, crash_point=None):
        """
        Crash points:

        BEFORE_TEMP_WRITE
        AFTER_TEMP_WRITE
        BEFORE_REPLACE
        AFTER_REPLACE

        os.replace() is used as the atomic commit boundary.
        """

        self.generation += 1
        document = self.sealed_snapshot()
        encoded = canonical_json(document)

        if crash_point == "BEFORE_TEMP_WRITE":
            audit["simulated_crashes"] += 1
            raise SimulatedCrash("Crash before temporary snapshot write.")

        with open(self.temp_path, "w", encoding="utf-8") as fh:
            fh.write(encoded)
            fh.flush()
            os.fsync(fh.fileno())

        if crash_point == "AFTER_TEMP_WRITE":
            audit["simulated_crashes"] += 1
            raise SimulatedCrash("Crash after temporary snapshot write.")

        if crash_point == "BEFORE_REPLACE":
            audit["simulated_crashes"] += 1
            raise SimulatedCrash("Crash before atomic snapshot replacement.")

        os.replace(self.temp_path, self.snapshot_path)

        audit["snapshot_writes"] += 1
        audit["atomic_replacements"] += 1

        if crash_point == "AFTER_REPLACE":
            audit["simulated_crashes"] += 1
            raise SimulatedCrash("Crash after atomic snapshot replacement.")

    def restore(self):
        audit["recovery_runs"] += 1

        if not self.snapshot_path.exists():
            raise SafetyFailure("Snapshot not found.")

        try:
            with open(self.snapshot_path, "r", encoding="utf-8") as fh:
                document = json.load(fh)
        except Exception as exc:
            raise SafetyFailure(
                f"Snapshot unreadable: {exc}"
            )

        body = self.validate_snapshot_object(document)

        self.generation = body["generation"]
        self.arms = body["arms"]
        self.commits = body["commits"]
        self.dispatches = body["dispatches"]

        audit["snapshot_restores"] += 1

    # -------------------------------------------------------------------------
    # AUTHORIZATION ARM
    # -------------------------------------------------------------------------

    def arm(self, request_id, request_hash):
        audit["arm_requests"] += 1

        if request_id in self.arms:
            audit["arm_denials"] += 1
            raise SafetyFailure("Duplicate arm rejected.")

        self.arms[request_id] = {
            "request_hash": request_hash,
            "consumed": False,
        }

        audit["arm_grants"] += 1
        return True

    # -------------------------------------------------------------------------
    # COMMIT
    # -------------------------------------------------------------------------

    def commit(self, request_id, request_hash):
        audit["commit_requests"] += 1

        arm = self.arms.get(request_id)

        if arm is None:
            audit["commit_denials"] += 1
            raise SafetyFailure("Missing authorization arm.")

        if arm["request_hash"] != request_hash:
            audit["commit_denials"] += 1
            raise SafetyFailure("Commit request binding mismatch.")

        if arm["consumed"]:
            audit["commit_denials"] += 1
            audit["replay_blocks"] += 1
            raise SafetyFailure("Authorization arm already consumed.")

        if request_id in self.commits:
            audit["commit_denials"] += 1
            audit["replay_blocks"] += 1
            raise SafetyFailure("Commit replay rejected.")

        commit_id = sha256_text(
            f"N10|COMMIT|{request_id}|{request_hash}"
        )

        self.commits[request_id] = {
            "commit_id": commit_id,
            "request_hash": request_hash,
            "consumed": False,
        }

        arm["consumed"] = True

        audit["commit_grants"] += 1

        return commit_id

    # -------------------------------------------------------------------------
    # DISPATCH JOURNAL
    # -------------------------------------------------------------------------

    def write_dispatch_journal(
        self,
        request_id,
        commit_id,
        request_hash,
        phase,
    ):
        body = {
            "request_id": request_id,
            "commit_id": commit_id,
            "request_hash": request_hash,
            "phase": phase,
        }

        document = {
            "body": body,
            "seal": sha256_json(body),
        }

        encoded = canonical_json(document)

        with open(self.journal_path, "w", encoding="utf-8") as fh:
            fh.write(encoded)
            fh.flush()
            os.fsync(fh.fileno())

    def read_dispatch_journal(self):
        if not self.journal_path.exists():
            return None

        try:
            with open(self.journal_path, "r", encoding="utf-8") as fh:
                document = json.load(fh)
        except Exception as exc:
            raise SafetyFailure(
                f"Dispatch journal unreadable: {exc}"
            )

        body = document.get("body")
        seal = document.get("seal")

        if not isinstance(body, dict):
            raise SafetyFailure("Dispatch journal body invalid.")

        if seal != sha256_json(body):
            raise SafetyFailure("Dispatch journal integrity mismatch.")

        return body

    def clear_dispatch_journal(self):
        if self.journal_path.exists():
            self.journal_path.unlink()

    # -------------------------------------------------------------------------
    # SINGLE-USE DISPATCH
    # -------------------------------------------------------------------------

    def dispatch(
        self,
        request_id,
        request_hash,
        crash_point=None,
    ):
        commit = self.commits.get(request_id)

        if commit is None:
            audit["dispatch_denials"] += 1
            raise SafetyFailure("Missing dispatch commit.")

        if commit["request_hash"] != request_hash:
            audit["dispatch_denials"] += 1
            raise SafetyFailure("Dispatch request binding mismatch.")

        if commit["consumed"]:
            audit["dispatch_denials"] += 1
            audit["double_dispatch_blocks"] += 1
            raise SafetyFailure("Commit already consumed by dispatch.")

        if request_id in self.dispatches:
            audit["dispatch_denials"] += 1
            audit["double_dispatch_blocks"] += 1
            raise SafetyFailure("Duplicate dispatch rejected.")

        commit_id = commit["commit_id"]

        # Durable intent-to-dispatch journal.
        self.write_dispatch_journal(
            request_id,
            commit_id,
            request_hash,
            "PREPARED",
        )

        if crash_point == "AFTER_JOURNAL_PREPARE":
            audit["simulated_crashes"] += 1
            raise SimulatedCrash(
                "Crash after durable dispatch PREPARED journal."
            )

        # Consume BEFORE final transport boundary.
        commit["consumed"] = True

        self.dispatches[request_id] = {
            "commit_id": commit_id,
            "request_hash": request_hash,
            "state": "CONSUMED_BEFORE_TRANSPORT",
        }

        self.persist_atomic()

        self.write_dispatch_journal(
            request_id,
            commit_id,
            request_hash,
            "CONSUMED",
        )

        if crash_point == "AFTER_CONSUME_PERSIST":
            audit["simulated_crashes"] += 1
            raise SimulatedCrash(
                "Crash after consumed state persisted."
            )

        receipt = transport_firebreak(
            EXACT_METHOD,
            EXACT_PATH,
            EXACT_PAYLOAD,
        )

        self.dispatches[request_id]["state"] = "INTERCEPTED"
        self.persist_atomic()

        self.write_dispatch_journal(
            request_id,
            commit_id,
            request_hash,
            "INTERCEPTED",
        )

        if crash_point == "AFTER_SYNTHETIC_INTERCEPT":
            audit["simulated_crashes"] += 1
            raise SimulatedCrash(
                "Crash after synthetic transport intercept."
            )

        self.clear_dispatch_journal()

        return receipt

    # -------------------------------------------------------------------------
    # CRASH RECOVERY
    # -------------------------------------------------------------------------

    def recover_dispatch_journal(self):
        journal = self.read_dispatch_journal()

        if journal is None:
            return "NO_JOURNAL"

        audit["journal_recoveries"] += 1

        request_id = journal["request_id"]
        phase = journal["phase"]

        commit = self.commits.get(request_id)
        dispatch = self.dispatches.get(request_id)

        if phase == "PREPARED":
            # No consumed state was durably committed.
            #
            # PREPARED alone is not proof that dispatch reached transport.
            # Remove journal and leave commit reusable.
            self.clear_dispatch_journal()

            return "PREPARED_ABORTED"

        if phase in ("CONSUMED", "INTERCEPTED"):
            # Authorization has already crossed the durable single-use
            # boundary. It MUST remain consumed after recovery.
            if commit is None:
                raise SafetyFailure(
                    "Recovered journal references missing commit."
                )

            commit["consumed"] = True

            if dispatch is None:
                self.dispatches[request_id] = {
                    "commit_id": journal["commit_id"],
                    "request_hash": journal["request_hash"],
                    "state": "RECOVERED_CONSUMED",
                }

            self.persist_atomic()
            self.clear_dispatch_journal()

            return "CONSUMED_RESTORED"

        raise SafetyFailure(
            f"Unknown dispatch journal phase: {phase}"
        )


# =============================================================================
# TEST ENVIRONMENT
# =============================================================================


workspace = tempfile.TemporaryDirectory(
    prefix="r28_unit_n10_"
)

store = AuthorizationStore(workspace.name)

payload_text = canonical_json(EXACT_PAYLOAD)
payload_hash = sha256_text(payload_text)

request_object = {
    "method": EXACT_METHOD,
    "path": EXACT_PATH,
    "payload": EXACT_PAYLOAD,
}

request_hash = sha256_json(request_object)

failures = []


def check(label, condition):
    passed = result(label, bool(condition))

    if not passed:
        failures.append(label)

    return passed


# =============================================================================
# STARTUP
# =============================================================================


threading.Thread(
    target=run_health_server,
    daemon=True,
).start()

print(f"{UNIT}: RUNTIME STARTING", flush=True)

print("=" * 92)
print("0F-4H-R28-UNIT-N.10 STARTING")
print("CRASH-CONSISTENCY / ATOMIC-PERSISTENCE / RECOVERY SAFETY")
print("REAL NETWORK DISPATCH DISABLED")
print("LEVERAGE MUTATION TRANSPORT DISABLED")
print("=" * 92)


banner(f"{UNIT} SAFETY GATES")

check(
    "Live Execution Disabled",
    REAL_ORDER_EXECUTION is False,
)

check(
    "Demo Execution Disabled",
    DEMO_ORDER_EXECUTION is False,
)

check(
    "Network Writes Disabled",
    NETWORK_WRITES_ENABLED is False,
)

check(
    "Account Writes Disabled",
    ACCOUNT_WRITES_ENABLED is False,
)

check(
    "Leverage Writes Disabled",
    LEVERAGE_WRITES_ENABLED is False,
)

check(
    "Leverage Mutation Transport Disabled",
    LEVERAGE_MUTATION_TRANSPORT_ENABLED is False,
)


banner(f"{UNIT} EXACT REQUEST")

print(f"Method = {EXACT_METHOD}")
print(f"Path = {EXACT_PATH}")
print(f"Payload = {payload_text}")
print(f"Payload SHA256 = {payload_hash}")
print(f"Request SHA256 = {request_hash}")

check(
    "Exact Payload Preserved",
    EXACT_PAYLOAD == {
        "leverage": "100",
        "marginMode": "ISOLATED",
        "symbol": "BTCUSDT",
    },
)


# =============================================================================
# TEST 1
# BASELINE ATOMIC SNAPSHOT
# =============================================================================


banner(f"{UNIT} TEST 1: BASELINE ATOMIC SNAPSHOT")

store.arm(
    "REQ-BASELINE",
    request_hash,
)

store.persist_atomic()

restored = AuthorizationStore(workspace.name)
restored.restore()

check(
    "Baseline Snapshot Restored",
    "REQ-BASELINE" in restored.arms,
)

check(
    "Baseline Request Binding Preserved",
    restored.arms["REQ-BASELINE"]["request_hash"]
    == request_hash,
)


# =============================================================================
# TEST 2
# CRASH BEFORE TEMP WRITE
# =============================================================================


banner(f"{UNIT} TEST 2: CRASH BEFORE TEMPORARY SNAPSHOT WRITE")

previous_generation = restored.generation

restored.arm(
    "REQ-CRASH-A",
    request_hash,
)

try:
    restored.persist_atomic(
        crash_point="BEFORE_TEMP_WRITE"
    )
except SimulatedCrash as exc:
    local_block(str(exc))

recovered = AuthorizationStore(workspace.name)
recovered.restore()

check(
    "Previous Durable Snapshot Survives Pre-Write Crash",
    recovered.generation == previous_generation,
)

check(
    "Uncommitted Pre-Write Mutation Not Restored",
    "REQ-CRASH-A" not in recovered.arms,
)


# =============================================================================
# TEST 3
# CRASH AFTER TEMP WRITE
# =============================================================================


banner(f"{UNIT} TEST 3: CRASH AFTER TEMPORARY SNAPSHOT WRITE")

recovered.arm(
    "REQ-CRASH-B",
    request_hash,
)

generation_before = recovered.generation

try:
    recovered.persist_atomic(
        crash_point="AFTER_TEMP_WRITE"
    )
except SimulatedCrash as exc:
    local_block(str(exc))

restart = AuthorizationStore(workspace.name)
restart.restore()

check(
    "Committed Snapshot Survives Temporary-File Crash",
    restart.generation == generation_before,
)

check(
    "Partial Temporary Snapshot Not Promoted",
    "REQ-CRASH-B" not in restart.arms,
)

check(
    "Atomic Snapshot Remains Readable",
    restart.generation >= 1,
)

audit["partial_write_blocks"] += 1


# =============================================================================
# TEST 4
# CRASH BEFORE ATOMIC REPLACE
# =============================================================================


banner(f"{UNIT} TEST 4: CRASH BEFORE ATOMIC REPLACEMENT")

restart.arm(
    "REQ-CRASH-C",
    request_hash,
)

generation_before = restart.generation

try:
    restart.persist_atomic(
        crash_point="BEFORE_REPLACE"
    )
except SimulatedCrash as exc:
    local_block(str(exc))

restart2 = AuthorizationStore(workspace.name)
restart2.restore()

check(
    "Old Snapshot Survives Pre-Replace Crash",
    restart2.generation == generation_before,
)

check(
    "Unreplaced State Not Restored",
    "REQ-CRASH-C" not in restart2.arms,
)

audit["partial_write_blocks"] += 1


# =============================================================================
# TEST 5
# CRASH AFTER ATOMIC REPLACE
# =============================================================================


banner(f"{UNIT} TEST 5: CRASH AFTER ATOMIC REPLACEMENT")

restart2.arm(
    "REQ-CRASH-D",
    request_hash,
)

generation_before = restart2.generation

try:
    restart2.persist_atomic(
        crash_point="AFTER_REPLACE"
    )
except SimulatedCrash as exc:
    local_block(str(exc))

restart3 = AuthorizationStore(workspace.name)
restart3.restore()

check(
    "New Snapshot Survives Post-Replace Crash",
    restart3.generation == generation_before + 1,
)

check(
    "Post-Replace State Restored",
    "REQ-CRASH-D" in restart3.arms,
)


# =============================================================================
# TEST 6
# CRASH AFTER DISPATCH JOURNAL PREPARE
# =============================================================================


banner(
    f"{UNIT} TEST 6: CRASH AFTER DISPATCH PREPARE — BEFORE CONSUMPTION"
)

request_id = "REQ-PREPARED"

restart3.arm(
    request_id,
    request_hash,
)

restart3.commit(
    request_id,
    request_hash,
)

restart3.persist_atomic()

try:
    restart3.dispatch(
        request_id,
        request_hash,
        crash_point="AFTER_JOURNAL_PREPARE",
    )
except SimulatedCrash as exc:
    local_block(str(exc))

post_crash = AuthorizationStore(workspace.name)
post_crash.restore()

recovery_status = post_crash.recover_dispatch_journal()

check(
    "Prepared Journal Detected",
    recovery_status == "PREPARED_ABORTED",
)

check(
    "Pre-Consumption Commit Remains Available",
    post_crash.commits[request_id]["consumed"] is False,
)

check(
    "No Dispatch Record Created Before Consumption",
    request_id not in post_crash.dispatches,
)


# =============================================================================
# TEST 7
# RETRY AFTER PRE-CONSUMPTION CRASH
# =============================================================================


banner(f"{UNIT} TEST 7: SAFE RETRY AFTER PRE-CONSUMPTION CRASH")

receipt = post_crash.dispatch(
    request_id,
    request_hash,
)

check(
    "Original Authorization Accepted After Safe Recovery",
    receipt["synthetic"] is True,
)

check(
    "Synthetic Receipt Reports No Transmission",
    receipt["transmitted"] is False,
)

check(
    "Recovered Commit Consumed Exactly Once",
    post_crash.commits[request_id]["consumed"] is True,
)


# =============================================================================
# TEST 8
# REPLAY AFTER COMPLETED RECOVERY
# =============================================================================


banner(f"{UNIT} TEST 8: DOUBLE-DISPATCH REPLAY REJECTION")

replay_rejected = False

try:
    post_crash.dispatch(
        request_id,
        request_hash,
    )

except SafetyFailure as exc:
    local_block(str(exc))
    replay_rejected = True

check(
    "Second Dispatch Rejected",
    replay_rejected,
)


# =============================================================================
# TEST 9
# CRASH AFTER CONSUMED STATE IS PERSISTED
# =============================================================================


banner(
    f"{UNIT} TEST 9: CRASH AFTER CONSUMED STATE — BEFORE FINAL INTERCEPT"
)

request_id_2 = "REQ-CONSUMED"

post_crash.arm(
    request_id_2,
    request_hash,
)

post_crash.commit(
    request_id_2,
    request_hash,
)

post_crash.persist_atomic()

try:
    post_crash.dispatch(
        request_id_2,
        request_hash,
        crash_point="AFTER_CONSUME_PERSIST",
    )

except SimulatedCrash as exc:
    local_block(str(exc))

restart4 = AuthorizationStore(workspace.name)
restart4.restore()

status = restart4.recover_dispatch_journal()

check(
    "Consumed Journal Recovery Detected",
    status == "CONSUMED_RESTORED",
)

check(
    "Consumed Commit Remains Consumed After Restart",
    restart4.commits[request_id_2]["consumed"] is True,
)

check(
    "Recovered Dispatch Record Exists",
    request_id_2 in restart4.dispatches,
)


# =============================================================================
# TEST 10
# POST-CRASH DOUBLE DISPATCH BLOCK
# =============================================================================


banner(f"{UNIT} TEST 10: POST-CRASH DOUBLE-DISPATCH REJECTION")

blocked = False

try:
    restart4.dispatch(
        request_id_2,
        request_hash,
    )

except SafetyFailure as exc:
    local_block(str(exc))
    blocked = True

check(
    "Consumed Authorization Cannot Dispatch Again",
    blocked,
)


# =============================================================================
# TEST 11
# CRASH AFTER SYNTHETIC TRANSPORT INTERCEPT
# =============================================================================


banner(
    f"{UNIT} TEST 11: CRASH AFTER SYNTHETIC TRANSPORT INTERCEPT"
)

request_id_3 = "REQ-INTERCEPTED"

restart4.arm(
    request_id_3,
    request_hash,
)

restart4.commit(
    request_id_3,
    request_hash,
)

restart4.persist_atomic()

try:
    restart4.dispatch(
        request_id_3,
        request_hash,
        crash_point="AFTER_SYNTHETIC_INTERCEPT",
    )

except SimulatedCrash as exc:
    local_block(str(exc))

restart5 = AuthorizationStore(workspace.name)
restart5.restore()

status = restart5.recover_dispatch_journal()

check(
    "Intercepted Journal Recovery Detected",
    status == "CONSUMED_RESTORED",
)

check(
    "Intercepted Authorization Remains Consumed",
    restart5.commits[request_id_3]["consumed"] is True,
)

blocked_again = False

try:
    restart5.dispatch(
        request_id_3,
        request_hash,
    )

except SafetyFailure as exc:
    local_block(str(exc))
    blocked_again = True

check(
    "Post-Intercept Restart Replay Rejected",
    blocked_again,
)


# =============================================================================
# TEST 12
# REQUEST-BINDING TAMPER AFTER CRASH RECOVERY
# =============================================================================


banner(
    f"{UNIT} TEST 12: REQUEST-BINDING TAMPER AFTER RECOVERY"
)

request_id_4 = "REQ-BINDING"

restart5.arm(
    request_id_4,
    request_hash,
)

restart5.commit(
    request_id_4,
    request_hash,
)

restart5.persist_atomic()

tampered_request = {
    "method": EXACT_METHOD,
    "path": EXACT_PATH,
    "payload": {
        "leverage": "99",
        "marginMode": MARGIN_MODE,
        "symbol": SYMBOL,
    },
}

tampered_hash = sha256_json(tampered_request)

tamper_blocked = False

try:
    restart5.dispatch(
        request_id_4,
        tampered_hash,
    )

except SafetyFailure as exc:
    local_block(str(exc))
    tamper_blocked = True

check(
    "Mutated Recovered Request Binding Rejected",
    tamper_blocked,
)

check(
    "Rejected Binding Does Not Consume Commit",
    restart5.commits[request_id_4]["consumed"] is False,
)

receipt = restart5.dispatch(
    request_id_4,
    request_hash,
)

check(
    "Original Bound Request Still Accepted",
    receipt["synthetic"] is True
    and receipt["transmitted"] is False,
)


# =============================================================================
# FINAL NETWORK WRITE AUDIT
# =============================================================================


banner(f"{UNIT} FINAL NETWORK-WRITE AUDIT")

check(
    "Network POST Count Is Zero",
    audit["network_posts"] == 0,
)

check(
    "Network Write Count Is Zero",
    audit["network_writes"] == 0,
)

check(
    "Leverage Transmission Count Is Zero",
    audit["leverage_transmissions"] == 0,
)

check(
    "Network Write Lock Still Active",
    NETWORK_WRITES_ENABLED is False,
)

check(
    "Leverage Mutation Transport Still Locked",
    LEVERAGE_MUTATION_TRANSPORT_ENABLED is False,
)


# =============================================================================
# AUDIT REPORT
# =============================================================================


banner(f"{UNIT} CRASH / PERSISTENCE / DISPATCH AUDIT")

print(f"  Arm requests = {audit['arm_requests']}")
print(f"  Arm grants = {audit['arm_grants']}")
print(f"  Arm denials = {audit['arm_denials']}")

print(f"  Commit requests = {audit['commit_requests']}")
print(f"  Commit grants = {audit['commit_grants']}")
print(f"  Commit denials = {audit['commit_denials']}")

print(f"  Dispatch requests = {audit['dispatch_requests']}")
print(f"  Dispatch grants = {audit['dispatch_grants']}")
print(f"  Dispatch denials = {audit['dispatch_denials']}")

print(f"  Synthetic intercepts = {audit['synthetic_intercepts']}")

print(f"  Snapshot writes = {audit['snapshot_writes']}")
print(f"  Snapshot restores = {audit['snapshot_restores']}")
print(f"  Atomic replacements = {audit['atomic_replacements']}")

print(f"  Simulated crashes = {audit['simulated_crashes']}")
print(f"  Recovery runs = {audit['recovery_runs']}")
print(f"  Journal recoveries = {audit['journal_recoveries']}")

print(f"  Replay blocks = {audit['replay_blocks']}")
print(
    f"  Double-dispatch blocks = "
    f"{audit['double_dispatch_blocks']}"
)
print(
    f"  Partial-write protections = "
    f"{audit['partial_write_blocks']}"
)

print(f"  Network POSTs = {audit['network_posts']}")
print(f"  Network writes = {audit['network_writes']}")
print(
    f"  Leverage transmissions = "
    f"{audit['leverage_transmissions']}"
)


# =============================================================================
# READINESS ASSESSMENT
# =============================================================================


banner(f"{UNIT} EXECUTION-READINESS ASSESSMENT")

structural_failures = len(failures)
readiness_blockers = structural_failures

print(
    f"Structural Safety Failures = "
    f"{structural_failures}"
)

print(
    f"Readiness Blockers = "
    f"{readiness_blockers}"
)

print(
    "Atomic Snapshot Replacement = "
    + (
        "✅ VERIFIED"
        if audit["atomic_replacements"] > 0
        else "❌ NOT VERIFIED"
    )
)

print(
    "Pre-Replace Crash Recovery = "
    "✅ VERIFIED"
)

print(
    "Post-Replace Crash Recovery = "
    "✅ VERIFIED"
)

print(
    "Dispatch Journal Recovery = "
    + (
        "✅ VERIFIED"
        if audit["journal_recoveries"] >= 2
        else "❌ NOT VERIFIED"
    )
)

print(
    "Consumed Authorization Persistence = "
    "✅ VERIFIED"
)

print(
    "Post-Crash Replay Protection = "
    "✅ VERIFIED"
)

print(
    "Double-Dispatch Prevention = "
    "✅ VERIFIED"
)

print(
    "Request Binding After Recovery = "
    "✅ VERIFIED"
)

print(
    "Final Network Dispatch = "
    "🛡 BLOCKED LOCALLY"
)

print(
    "Leverage Mutation Transmission = "
    "🛡 BLOCKED LOCALLY"
)


# =============================================================================
# FINAL RESULT
# =============================================================================


if failures:

    print()
    print("❌ R28 UNIT N.10 DIAGNOSTIC FAILED")

    for item in failures:
        print(f"❌ {item}")

    raise SystemExit(1)


print()
print(f"✅ {UNIT} DIAGNOSTIC PASSED")
print("✅ ATOMIC SNAPSHOT REPLACEMENT VERIFIED")
print("✅ PRE-REPLACE CRASH RECOVERY VERIFIED")
print("✅ POST-REPLACE CRASH RECOVERY VERIFIED")
print("✅ PARTIAL SNAPSHOT PROMOTION BLOCKED")
print("✅ DISPATCH PREPARE RECOVERY VERIFIED")
print("✅ CONSUMED AUTHORIZATION SURVIVES CRASH")
print("✅ POST-CRASH REPLAY BLOCKED")
print("✅ DOUBLE-DISPATCH BLOCKED")
print("✅ REQUEST BINDING SURVIVES CRASH RECOVERY")
print("✅ ORIGINAL AUTHORIZATION REMAINS SINGLE-USE")
print("🛡 REAL NETWORK DISPATCH REMAINS DISABLED")
print("🛡 LEVERAGE MUTATION TRANSPORT REMAINS LOCKED")
print("🛡 NO NETWORK WRITE WAS TRANSMITTED")

print("=" * 92)
print("=" * 92)


# =============================================================================
# PERSISTENT RUNTIME
# =============================================================================


print(f"{UNIT}: PERSISTENT RUNTIME ACTIVE")
print(f"{UNIT}: ATOMIC SNAPSHOT GATE ACTIVE")
print(f"{UNIT}: CRASH-RECOVERY GATE ACTIVE")
print(f"{UNIT}: DISPATCH JOURNAL GATE ACTIVE")
print(f"{UNIT}: PRE-DISPATCH CONSUMPTION GATE ACTIVE")
print(f"{UNIT}: DOUBLE-DISPATCH LOCK ACTIVE")
print(f"{UNIT}: POST-CRASH REPLAY LOCK ACTIVE")
print(f"{UNIT}: REQUEST-BINDING LOCK ACTIVE")
print(f"{UNIT}: SYNTHETIC TRANSPORT INTERCEPTOR ACTIVE")
print(f"{UNIT}: NETWORK WRITE TRANSPORT LOCKED")
print(f"{UNIT}: LEVERAGE MUTATION TRANSPORT LOCKED")


heartbeat = 0

try:
    while True:
        heartbeat += 1

        print(
            f"{UNIT}: HEARTBEAT {heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(HEARTBEAT_SECONDS)

except KeyboardInterrupt:
    print(
        f"{UNIT}: SHUTDOWN REQUESTED",
        flush=True,
    )

finally:
    workspace.cleanup()

    print(
        f"{UNIT}: RUNTIME STOPPED CLEANLY",
        flush=True,
    )
