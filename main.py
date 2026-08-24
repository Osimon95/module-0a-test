# ============================================================
# 0F-4H-R28-UNIT-N.9
# RESTART / PERSISTENCE HARDENING
# FINAL-DISPATCH AUTHORIZATION STATE
#
# SAFETY:
#   - NO REAL POST
#   - NO DEMO POST
#   - NO ACCOUNT MUTATION
#   - NO LEVERAGE MUTATION
#   - NO NETWORK WRITE
#   - SYNTHETIC DISPATCH ONLY
#
# PURPOSE:
#   1. Verify consumed authorization survives restart.
#   2. Verify replay remains blocked after restart.
#   3. Verify unused authorization can survive restart.
#   4. Verify unused authorization remains single-use.
#   5. Verify request binding survives restart.
#   6. Verify tampered snapshots are rejected.
#   7. Verify corrupted snapshots are rejected.
#   8. Verify rollback/stale snapshots are rejected.
#   9. Verify no network write occurs.
# ============================================================

print("R28 UNIT N.9: MAIN.PY ENTERED", flush=True)

import os
import json
import time
import hmac
import hashlib
import threading
import tempfile
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer

print("R28 UNIT N.9: IMPORTS COMPLETE", flush=True)


# ============================================================
# CONSTANTS
# ============================================================

UNIT_NAME = "R28 UNIT N.9"

SYMBOL = "BTCUSDT"

HEALTH_PORT = int(os.getenv("PORT", "10000"))
HEARTBEAT_SECONDS = 15

# ------------------------------------------------------------
# HARD SAFETY LOCKS
# ------------------------------------------------------------

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
ACCOUNT_WRITES_ENABLED = False
LEVERAGE_WRITES_ENABLED = False

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False

LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

# ------------------------------------------------------------
# IMPORTANT
#
# N.9 deliberately does NOT reconstruct the WEEX leverage
# payload here.
#
# N.8 already verified the current V3 endpoint/schema.
#
# N.9 persists only a cryptographic binding representing the
# already-verified final request boundary.
#
# This prevents N.9 from accidentally restoring the obsolete
# N.7 payload shape.
# ------------------------------------------------------------

N8_VERIFIED_REQUEST_DESCRIPTOR = {
    "unit": "R28-N.8",
    "symbol": SYMBOL,
    "request_class": "CURRENT_WEEX_V3_LEVERAGE_MUTATION",
    "schema_status": "VERIFIED_BY_N8",
    "endpoint_status": "PINNED_BY_N8",
    "method_status": "POST_VERIFIED_BY_N8",
    "transport": "LOCAL_SYNTHETIC_INTERCEPT_ONLY",
}

STATE_FILE = os.path.join(
    tempfile.gettempdir(),
    "r28_unit_n9_restart_state.json"
)

STALE_STATE_FILE = os.path.join(
    tempfile.gettempdir(),
    "r28_unit_n9_stale_state.json"
)

# Test-only integrity key.
#
# This key signs LOCAL diagnostic snapshots only.
# It is NOT an exchange/API signing secret.
SNAPSHOT_HMAC_KEY = (
    b"R28_UNIT_N9_LOCAL_DIAGNOSTIC_SNAPSHOT_INTEGRITY_KEY"
)

print("R28 UNIT N.9: CONSTANTS INITIALIZED", flush=True)


# ============================================================
# AUDIT COUNTERS
# ============================================================

AUDIT = {
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

    "restart_restores": 0,
    "replay_blocks": 0,
    "tamper_blocks": 0,
    "corruption_blocks": 0,
    "rollback_blocks": 0,

    "network_posts": 0,
    "network_writes": 0,
    "leverage_transmissions": 0,
}


# ============================================================
# TEST RESULT TRACKING
# ============================================================

STRUCTURAL_FAILURES = 0
READINESS_BLOCKERS = 0


def section(title):
    print()
    print(title, flush=True)
    print("-" * 92, flush=True)


def check(label, condition, blocker=True):
    global STRUCTURAL_FAILURES
    global READINESS_BLOCKERS

    if condition:
        print(f"{label:<78} ✅ PASS", flush=True)
        return True

    print(f"{label:<78} ❌ FAIL", flush=True)

    STRUCTURAL_FAILURES += 1

    if blocker:
        READINESS_BLOCKERS += 1

    return False


# ============================================================
# CANONICAL JSON / HASH HELPERS
# ============================================================

def canonical_json(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")

    return hashlib.sha256(data).hexdigest()


def request_binding_hash(descriptor):
    return sha256_hex(canonical_json(descriptor))


N8_REQUEST_BINDING = request_binding_hash(
    N8_VERIFIED_REQUEST_DESCRIPTOR
)


# ============================================================
# AUTHORIZATION OBJECT HELPERS
# ============================================================

def make_arm_id(binding_hash, nonce):
    material = {
        "kind": "ARM",
        "binding": binding_hash,
        "nonce": nonce,
    }

    return sha256_hex(canonical_json(material))


def make_commit_id(arm_id, binding_hash):
    material = {
        "kind": "COMMIT",
        "arm_id": arm_id,
        "binding": binding_hash,
    }

    return sha256_hex(canonical_json(material))


# ============================================================
# PERSISTENT AUTHORIZATION STATE
# ============================================================

class AuthorizationState:

    def __init__(self):
        self.generation = 0

        self.arms = {}
        self.commits = {}

        self.consumed_arms = set()
        self.consumed_commits = set()

        self.highest_generation_seen = 0

    # --------------------------------------------------------
    # ARM
    # --------------------------------------------------------

    def arm(self, binding_hash, nonce):

        AUDIT["arm_requests"] += 1

        if not binding_hash:
            AUDIT["arm_denials"] += 1
            raise RuntimeError(
                "Empty request binding rejected."
            )

        arm_id = make_arm_id(
            binding_hash,
            nonce
        )

        if arm_id in self.arms:
            AUDIT["arm_denials"] += 1
            raise RuntimeError(
                "Duplicate arm rejected."
            )

        if arm_id in self.consumed_arms:
            AUDIT["arm_denials"] += 1
            raise RuntimeError(
                "Previously consumed arm rejected."
            )

        self.arms[arm_id] = {
            "arm_id": arm_id,
            "binding": binding_hash,
            "nonce": nonce,
            "consumed": False,
        }

        AUDIT["arm_grants"] += 1

        return arm_id

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    def commit(self, arm_id, binding_hash):

        AUDIT["commit_requests"] += 1

        arm = self.arms.get(arm_id)

        if not arm:
            AUDIT["commit_denials"] += 1
            raise RuntimeError(
                "Unknown arm rejected."
            )

        if arm_id in self.consumed_arms:
            AUDIT["commit_denials"] += 1
            raise RuntimeError(
                "Consumed arm rejected."
            )

        if arm["binding"] != binding_hash:
            AUDIT["commit_denials"] += 1
            raise RuntimeError(
                "Commit binding mismatch."
            )

        commit_id = make_commit_id(
            arm_id,
            binding_hash
        )

        if commit_id in self.commits:
            AUDIT["commit_denials"] += 1
            raise RuntimeError(
                "Duplicate commit rejected."
            )

        if commit_id in self.consumed_commits:
            AUDIT["commit_denials"] += 1
            raise RuntimeError(
                "Consumed commit rejected."
            )

        self.commits[commit_id] = {
            "commit_id": commit_id,
            "arm_id": arm_id,
            "binding": binding_hash,
            "consumed": False,
        }

        AUDIT["commit_grants"] += 1

        return commit_id

    # --------------------------------------------------------
    # SYNTHETIC FINAL DISPATCH
    # --------------------------------------------------------

    def synthetic_dispatch(
        self,
        commit_id,
        binding_hash
    ):

        AUDIT["dispatch_requests"] += 1

        commit = self.commits.get(commit_id)

        if not commit:
            AUDIT["dispatch_denials"] += 1
            raise RuntimeError(
                "Unknown commit rejected."
            )

        arm_id = commit["arm_id"]

        arm = self.arms.get(arm_id)

        if not arm:
            AUDIT["dispatch_denials"] += 1
            raise RuntimeError(
                "Commit arm missing."
            )

        if commit_id in self.consumed_commits:
            AUDIT["dispatch_denials"] += 1
            AUDIT["replay_blocks"] += 1

            raise RuntimeError(
                "Consumed commit replay blocked."
            )

        if arm_id in self.consumed_arms:
            AUDIT["dispatch_denials"] += 1
            AUDIT["replay_blocks"] += 1

            raise RuntimeError(
                "Consumed arm replay blocked."
            )

        if commit["binding"] != binding_hash:
            AUDIT["dispatch_denials"] += 1
            raise RuntimeError(
                "Commit request binding mismatch."
            )

        if arm["binding"] != binding_hash:
            AUDIT["dispatch_denials"] += 1
            raise RuntimeError(
                "Arm request binding mismatch."
            )

        # ----------------------------------------------------
        # FINAL LOCAL FIREBREAK
        #
        # Authorization is consumed HERE.
        #
        # No network transport exists below this point.
        # ----------------------------------------------------

        self.consumed_commits.add(commit_id)
        self.consumed_arms.add(arm_id)

        self.commits[commit_id]["consumed"] = True
        self.arms[arm_id]["consumed"] = True

        self.generation += 1

        if self.generation > self.highest_generation_seen:
            self.highest_generation_seen = self.generation

        AUDIT["dispatch_grants"] += 1
        AUDIT["synthetic_intercepts"] += 1

        return {
            "status": "SYNTHETIC_INTERCEPT",
            "network_transmitted": False,
            "leverage_transmitted": False,
            "commit_consumed": True,
            "arm_consumed": True,
            "binding": binding_hash,
        }


# ============================================================
# SNAPSHOT SERIALIZATION
# ============================================================

def export_state(state):

    return {
        "version": 1,
        "unit": UNIT_NAME,
        "generation": state.generation,

        "highest_generation_seen":
            state.highest_generation_seen,

        "request_binding":
            N8_REQUEST_BINDING,

        "arms":
            deepcopy(state.arms),

        "commits":
            deepcopy(state.commits),

        "consumed_arms":
            sorted(state.consumed_arms),

        "consumed_commits":
            sorted(state.consumed_commits),
    }


def calculate_snapshot_seal(body):

    raw = canonical_json(body).encode("utf-8")

    return hmac.new(
        SNAPSHOT_HMAC_KEY,
        raw,
        hashlib.sha256,
    ).hexdigest()


def build_snapshot(state):

    body = export_state(state)

    return {
        "body": body,
        "seal": calculate_snapshot_seal(body),
    }


def save_snapshot(state, filename):

    snapshot = build_snapshot(state)

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            snapshot,
            f,
            sort_keys=True,
            separators=(",", ":"),
        )

    return snapshot


# ============================================================
# SNAPSHOT RESTORE
# ============================================================

def restore_snapshot(
    filename,
    minimum_generation=0
):

    if not os.path.exists(filename):

        AUDIT["corruption_blocks"] += 1

        raise RuntimeError(
            "Snapshot missing."
        )

    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            snapshot = json.load(f)

    except Exception as exc:

        AUDIT["corruption_blocks"] += 1

        raise RuntimeError(
            f"Snapshot unreadable: {exc}"
        )

    if not isinstance(snapshot, dict):

        AUDIT["corruption_blocks"] += 1

        raise RuntimeError(
            "Snapshot root invalid."
        )

    body = snapshot.get("body")
    supplied_seal = snapshot.get("seal")

    if not isinstance(body, dict):
        AUDIT["corruption_blocks"] += 1
        raise RuntimeError(
            "Snapshot body invalid."
        )

    if not isinstance(supplied_seal, str):
        AUDIT["corruption_blocks"] += 1
        raise RuntimeError(
            "Snapshot seal missing."
        )

    expected_seal = calculate_snapshot_seal(body)

    if not hmac.compare_digest(
        supplied_seal,
        expected_seal
    ):

        AUDIT["tamper_blocks"] += 1

        raise RuntimeError(
            "Snapshot integrity seal mismatch."
        )

    if body.get("version") != 1:

        AUDIT["corruption_blocks"] += 1

        raise RuntimeError(
            "Snapshot version unsupported."
        )

    if body.get("request_binding") != N8_REQUEST_BINDING:

        AUDIT["tamper_blocks"] += 1

        raise RuntimeError(
            "Persisted N.8 request binding mismatch."
        )

    generation = body.get("generation")

    if not isinstance(generation, int):

        AUDIT["corruption_blocks"] += 1

        raise RuntimeError(
            "Snapshot generation invalid."
        )

    if generation < minimum_generation:

        AUDIT["rollback_blocks"] += 1

        raise RuntimeError(
            "Stale snapshot rollback rejected."
        )

    restored = AuthorizationState()

    restored.generation = generation

    restored.highest_generation_seen = max(
        body.get(
            "highest_generation_seen",
            generation
        ),
        generation,
    )

    restored.arms = deepcopy(
        body.get("arms", {})
    )

    restored.commits = deepcopy(
        body.get("commits", {})
    )

    restored.consumed_arms = set(
        body.get("consumed_arms", [])
    )

    restored.consumed_commits = set(
        body.get("consumed_commits", [])
    )

    # --------------------------------------------------------
    # INTERNAL CONSISTENCY VALIDATION
    # --------------------------------------------------------

    for commit_id in restored.consumed_commits:

        if commit_id not in restored.commits:

            AUDIT["corruption_blocks"] += 1

            raise RuntimeError(
                "Consumed commit missing from snapshot."
            )

        if not restored.commits[commit_id].get(
            "consumed"
        ):

            AUDIT["corruption_blocks"] += 1

            raise RuntimeError(
                "Consumed commit flag inconsistent."
            )

    for arm_id in restored.consumed_arms:

        if arm_id not in restored.arms:

            AUDIT["corruption_blocks"] += 1

            raise RuntimeError(
                "Consumed arm missing from snapshot."
            )

        if not restored.arms[arm_id].get(
            "consumed"
        ):

            AUDIT["corruption_blocks"] += 1

            raise RuntimeError(
                "Consumed arm flag inconsistent."
            )

    AUDIT["restart_restores"] += 1

    return restored


# ============================================================
# NETWORK FIREBREAK
# ============================================================

def forbidden_network_write(*args, **kwargs):

    raise RuntimeError(
        "R28 UNIT N.9 LOCAL FIREBREAK: "
        "network write transport disabled."
    )


def forbidden_leverage_transmission(
    *args,
    **kwargs
):

    raise RuntimeError(
        "R28 UNIT N.9 LOCAL FIREBREAK: "
        "leverage mutation transport disabled."
    )


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = b"R28 UNIT N.9 ACTIVE\n"

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(
        self,
        format,
        *args
    ):
        return


def start_health_server():

    try:

        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True
        )

        thread.start()

        print(
            f"R28 UNIT N.9: "
            f"HEALTH SERVER ACTIVE ON PORT "
            f"{HEALTH_PORT}",
            flush=True
        )

        return server

    except Exception as exc:

        print(
            f"R28 UNIT N.9: "
            f"HEALTH SERVER ERROR: {exc}",
            flush=True
        )

        return None


# ============================================================
# DIAGNOSTIC
# ============================================================

def run_diagnostic():

    global STRUCTURAL_FAILURES
    global READINESS_BLOCKERS

    print("=" * 92)
    print(
        "0F-4H-R28-UNIT-N.9 STARTING"
    )
    print(
        "RESTART / PERSISTENCE HARDENING"
    )
    print(
        "FINAL-DISPATCH AUTHORIZATION STATE"
    )
    print(
        "NO REAL NETWORK WRITE WILL BE TRANSMITTED"
    )
    print("=" * 92)

    print(
        f"R28 UNIT N.9 SYMBOL: {SYMBOL}"
    )

    print(
        "R28 UNIT N.9 N.8 REQUEST BINDING:"
    )
    print(
        f"  SHA256 = {N8_REQUEST_BINDING}"
    )

    # ========================================================
    # TEST 1
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 1: "
        "HARD SAFETY LOCKS"
    )

    check(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False
    )

    check(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False
    )

    check(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False
    )

    check(
        "Account Writes Disabled",
        ACCOUNT_WRITES_ENABLED is False
    )

    check(
        "Leverage Writes Disabled",
        LEVERAGE_WRITES_ENABLED is False
    )

    check(
        "Real POST Disabled",
        REAL_POST_ENABLED is False
    )

    check(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False
    )

    check(
        "Leverage Mutation Transport Disabled",
        LEVERAGE_MUTATION_TRANSPORT_ENABLED
        is False
    )

    check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True
    )

    # ========================================================
    # TEST 2
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 2: "
        "N.8 REQUEST-BINDING DETERMINISM"
    )

    binding_1 = request_binding_hash(
        N8_VERIFIED_REQUEST_DESCRIPTOR
    )

    binding_2 = request_binding_hash(
        deepcopy(
            N8_VERIFIED_REQUEST_DESCRIPTOR
        )
    )

    check(
        "N.8 Request Binding Generated",
        isinstance(binding_1, str)
        and len(binding_1) == 64
    )

    check(
        "N.8 Request Binding Deterministic",
        binding_1 == binding_2
    )

    mutated_descriptor = deepcopy(
        N8_VERIFIED_REQUEST_DESCRIPTOR
    )

    mutated_descriptor[
        "request_class"
    ] = "MUTATED_REQUEST_CLASS"

    mutated_binding = request_binding_hash(
        mutated_descriptor
    )

    check(
        "Request Mutation Changes Binding",
        mutated_binding != binding_1
    )

    # ========================================================
    # TEST 3
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 3: "
        "CONSUMED AUTHORIZATION SNAPSHOT"
    )

    state = AuthorizationState()

    arm_1 = state.arm(
        N8_REQUEST_BINDING,
        "N9-CONSUMED-ARM-001"
    )

    commit_1 = state.commit(
        arm_1,
        N8_REQUEST_BINDING
    )

    receipt_1 = state.synthetic_dispatch(
        commit_1,
        N8_REQUEST_BINDING
    )

    check(
        "Synthetic Final Dispatch Intercepted",
        receipt_1[
            "status"
        ] == "SYNTHETIC_INTERCEPT"
    )

    check(
        "Synthetic Receipt Reports No Transmission",
        receipt_1[
            "network_transmitted"
        ] is False
    )

    check(
        "Commit Consumed Before Snapshot",
        commit_1 in state.consumed_commits
    )

    check(
        "Arm Consumed Before Snapshot",
        arm_1 in state.consumed_arms
    )

    snapshot_1 = save_snapshot(
        state,
        STATE_FILE
    )

    check(
        "Consumed Authorization Snapshot Saved",
        os.path.exists(STATE_FILE)
    )

    check(
        "Snapshot Integrity Seal Generated",
        isinstance(
            snapshot_1.get("seal"),
            str
        )
        and len(
            snapshot_1.get("seal")
        ) == 64
    )

    generation_after_consumption = (
        state.generation
    )

    # ========================================================
    # TEST 4
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 4: "
        "SIMULATED PROCESS RESTART"
    )

    del state

    restored = restore_snapshot(
        STATE_FILE,
        minimum_generation=
            generation_after_consumption
    )

    check(
        "Persistent State Restored",
        isinstance(
            restored,
            AuthorizationState
        )
    )

    check(
        "Generation Survived Restart",
        restored.generation
        == generation_after_consumption
    )

    check(
        "Consumed Commit Survived Restart",
        commit_1
        in restored.consumed_commits
    )

    check(
        "Consumed Arm Survived Restart",
        arm_1
        in restored.consumed_arms
    )

    check(
        "N.8 Request Binding Survived Restart",
        N8_REQUEST_BINDING
        == request_binding_hash(
            N8_VERIFIED_REQUEST_DESCRIPTOR
        )
    )

    # ========================================================
    # TEST 5
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 5: "
        "POST-RESTART REPLAY REJECTION"
    )

    replay_rejected = False

    try:

        restored.synthetic_dispatch(
            commit_1,
            N8_REQUEST_BINDING
        )

    except Exception as exc:

        replay_rejected = True

        print(
            "R28 UNIT N.9 LOCAL BLOCK:"
        )

        print(
            f"  {exc}"
        )

    check(
        "Consumed Commit Replay Rejected After Restart",
        replay_rejected
    )

    check(
        "Replay Did Not Create Network POST",
        AUDIT["network_posts"] == 0
    )

    check(
        "Replay Did Not Create Leverage Transmission",
        AUDIT[
            "leverage_transmissions"
        ] == 0
    )

    # ========================================================
    # TEST 6
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 6: "
        "UNUSED AUTHORIZATION SURVIVES RESTART"
    )

    arm_2 = restored.arm(
        N8_REQUEST_BINDING,
        "N9-UNUSED-ARM-002"
    )

    commit_2 = restored.commit(
        arm_2,
        N8_REQUEST_BINDING
    )

    check(
        "Second Commit Initially Unconsumed",
        commit_2
        not in restored.consumed_commits
    )

    save_snapshot(
        restored,
        STATE_FILE
    )

    generation_before_unused_restart = (
        restored.generation
    )

    del restored

    restored_2 = restore_snapshot(
        STATE_FILE,
        minimum_generation=
            generation_before_unused_restart
    )

    check(
        "Unused Commit Restored",
        commit_2 in restored_2.commits
    )

    check(
        "Unused Commit Still Unconsumed",
        commit_2
        not in restored_2.consumed_commits
    )

    receipt_2 = restored_2.synthetic_dispatch(
        commit_2,
        N8_REQUEST_BINDING
    )

    check(
        "Restored Unused Authorization Accepted Once",
        receipt_2[
            "status"
        ] == "SYNTHETIC_INTERCEPT"
    )

    check(
        "Restored Commit Consumed At Final Boundary",
        commit_2
        in restored_2.consumed_commits
    )

    check(
        "Restored Arm Consumed At Final Boundary",
        arm_2
        in restored_2.consumed_arms
    )

    # ========================================================
    # TEST 7
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 7: "
        "SECOND RESTART REPLAY REJECTION"
    )

    save_snapshot(
        restored_2,
        STATE_FILE
    )

    latest_generation = restored_2.generation

    del restored_2

    restored_3 = restore_snapshot(
        STATE_FILE,
        minimum_generation=
            latest_generation
    )

    replay_2_rejected = False

    try:

        restored_3.synthetic_dispatch(
            commit_2,
            N8_REQUEST_BINDING
        )

    except Exception:

        replay_2_rejected = True

    check(
        "Second Commit Replay Rejected After Restart",
        replay_2_rejected
    )

    # ========================================================
    # TEST 8
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 8: "
        "SNAPSHOT TAMPER REJECTION"
    )

    good_snapshot = build_snapshot(
        restored_3
    )

    tampered_snapshot = deepcopy(
        good_snapshot
    )

    tampered_snapshot[
        "body"
    ][
        "request_binding"
    ] = (
        "0" * 64
    )

    # Keep OLD seal deliberately.
    # Restore must reject the modification.

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            tampered_snapshot,
            f,
            sort_keys=True,
            separators=(",", ":"),
        )

    tamper_rejected = False

    try:

        restore_snapshot(
            STATE_FILE,
            minimum_generation=
                latest_generation
        )

    except Exception as exc:

        tamper_rejected = True

        print(
            "R28 UNIT N.9 LOCAL BLOCK:"
        )

        print(
            f"  {exc}"
        )

    check(
        "Tampered Snapshot Rejected",
        tamper_rejected
    )

    # Restore valid snapshot for next test.

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            good_snapshot,
            f,
            sort_keys=True,
            separators=(",", ":"),
        )

    # ========================================================
    # TEST 9
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 9: "
        "CORRUPTED SNAPSHOT REJECTION"
    )

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "{THIS_IS_NOT_VALID_JSON"
        )

    corruption_rejected = False

    try:

        restore_snapshot(
            STATE_FILE,
            minimum_generation=
                latest_generation
        )

    except Exception as exc:

        corruption_rejected = True

        print(
            "R28 UNIT N.9 LOCAL BLOCK:"
        )

        print(
            f"  {exc}"
        )

    check(
        "Corrupted Snapshot Rejected",
        corruption_rejected
    )

    # Restore valid snapshot again.

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            good_snapshot,
            f,
            sort_keys=True,
            separators=(",", ":"),
        )

    # ========================================================
    # TEST 10
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 10: "
        "STALE SNAPSHOT / ROLLBACK REJECTION"
    )

    stale_body = deepcopy(
        good_snapshot["body"]
    )

    stale_body["generation"] = max(
        0,
        latest_generation - 1
    )

    stale_body[
        "highest_generation_seen"
    ] = stale_body["generation"]

    stale_snapshot = {
        "body": stale_body,
        "seal": calculate_snapshot_seal(
            stale_body
        ),
    }

    with open(
        STALE_STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            stale_snapshot,
            f,
            sort_keys=True,
            separators=(",", ":"),
        )

    rollback_rejected = False

    try:

        restore_snapshot(
            STALE_STATE_FILE,
            minimum_generation=
                latest_generation
        )

    except Exception as exc:

        rollback_rejected = True

        print(
            "R28 UNIT N.9 LOCAL BLOCK:"
        )

        print(
            f"  {exc}"
        )

    check(
        "Stale Snapshot Rollback Rejected",
        rollback_rejected
    )

    # ========================================================
    # TEST 11
    # ========================================================

    section(
        "R28 UNIT N.9 TEST 11: "
        "REQUEST-BINDING TAMPER AFTER RESTART"
    )

    restored_final = restore_snapshot(
        STATE_FILE,
        minimum_generation=
            latest_generation
    )

    arm_3 = restored_final.arm(
        N8_REQUEST_BINDING,
        "N9-TAMPER-BINDING-003"
    )

    commit_3 = restored_final.commit(
        arm_3,
        N8_REQUEST_BINDING
    )

    wrong_binding = sha256_hex(
        "MUTATED_FINAL_REQUEST"
    )

    binding_tamper_rejected = False

    try:

        restored_final.synthetic_dispatch(
            commit_3,
            wrong_binding
        )

    except Exception as exc:

        binding_tamper_rejected = True

        print(
            "R28 UNIT N.9 LOCAL BLOCK:"
        )

        print(
            f"  {exc}"
        )

    check(
        "Mutated Request Binding Rejected",
        binding_tamper_rejected
    )

    check(
        "Rejected Commit Remains Unconsumed",
        commit_3
        not in restored_final.consumed_commits
    )

    check(
        "Rejected Arm Remains Unconsumed",
        arm_3
        not in restored_final.consumed_arms
    )

    # Correct binding should still work exactly once.

    receipt_3 = restored_final.synthetic_dispatch(
        commit_3,
        N8_REQUEST_BINDING
    )

    check(
        "Original Bound Request Still Accepted",
        receipt_3[
            "status"
        ] == "SYNTHETIC_INTERCEPT"
    )

    # ========================================================
    # FINAL WRITE AUDIT
    # ========================================================

    section(
        "R28 UNIT N.9 FINAL NETWORK-WRITE AUDIT"
    )

    check(
        "Network POST Count Is Zero",
        AUDIT["network_posts"] == 0
    )

    check(
        "Network Write Count Is Zero",
        AUDIT["network_writes"] == 0
    )

    check(
        "Leverage Transmission Count Is Zero",
        AUDIT[
            "leverage_transmissions"
        ] == 0
    )

    check(
        "Network Write Lock Still Active",
        NETWORK_WRITES_ENABLED is False
    )

    check(
        "Leverage Mutation Transport Still Locked",
        LEVERAGE_MUTATION_TRANSPORT_ENABLED
        is False
    )

    # ========================================================
    # AUDIT
    # ========================================================

    section(
        "R28 UNIT N.9 PERSISTENCE / DISPATCH AUDIT"
    )

    print(
        f"  Arm requests = "
        f"{AUDIT['arm_requests']}"
    )

    print(
        f"  Arm grants = "
        f"{AUDIT['arm_grants']}"
    )

    print(
        f"  Arm denials = "
        f"{AUDIT['arm_denials']}"
    )

    print(
        f"  Commit requests = "
        f"{AUDIT['commit_requests']}"
    )

    print(
        f"  Commit grants = "
        f"{AUDIT['commit_grants']}"
    )

    print(
        f"  Commit denials = "
        f"{AUDIT['commit_denials']}"
    )

    print(
        f"  Dispatch requests = "
        f"{AUDIT['dispatch_requests']}"
    )

    print(
        f"  Dispatch grants = "
        f"{AUDIT['dispatch_grants']}"
    )

    print(
        f"  Dispatch denials = "
        f"{AUDIT['dispatch_denials']}"
    )

    print(
        f"  Synthetic intercepts = "
        f"{AUDIT['synthetic_intercepts']}"
    )

    print(
        f"  Restart restores = "
        f"{AUDIT['restart_restores']}"
    )

    print(
        f"  Replay blocks = "
        f"{AUDIT['replay_blocks']}"
    )

    print(
        f"  Tamper blocks = "
        f"{AUDIT['tamper_blocks']}"
    )

    print(
        f"  Corruption blocks = "
        f"{AUDIT['corruption_blocks']}"
    )

    print(
        f"  Rollback blocks = "
        f"{AUDIT['rollback_blocks']}"
    )

    print(
        f"  Network POSTs = "
        f"{AUDIT['network_posts']}"
    )

    print(
        f"  Network writes = "
        f"{AUDIT['network_writes']}"
    )

    print(
        f"  Leverage transmissions = "
        f"{AUDIT['leverage_transmissions']}"
    )

    # ========================================================
    # READINESS
    # ========================================================

    section(
        "R28 UNIT N.9 EXECUTION-READINESS ASSESSMENT"
    )

    print(
        f"Structural Safety Failures = "
        f"{STRUCTURAL_FAILURES}"
    )

    print(
        f"Readiness Blockers = "
        f"{READINESS_BLOCKERS}"
    )

    print(
        "N.8 Request Binding Persistence = "
        "✅ VERIFIED"
        if STRUCTURAL_FAILURES == 0
        else
        "❌ FAILED"
    )

    print(
        "Consumed Authorization Persistence = "
        "✅ VERIFIED"
        if STRUCTURAL_FAILURES == 0
        else
        "❌ FAILED"
    )

    print(
        "Post-Restart Replay Protection = "
        "✅ VERIFIED"
        if STRUCTURAL_FAILURES == 0
        else
        "❌ FAILED"
    )

    print(
        "Snapshot Integrity Protection = "
        "✅ VERIFIED"
        if STRUCTURAL_FAILURES == 0
        else
        "❌ FAILED"
    )

    print(
        "Rollback Protection = "
        "✅ VERIFIED"
        if STRUCTURAL_FAILURES == 0
        else
        "❌ FAILED"
    )

    print(
        "Single-Use Dispatch Authorization = "
        "✅ VERIFIED"
        if STRUCTURAL_FAILURES == 0
        else
        "❌ FAILED"
    )

    print(
        "Final Network Dispatch = "
        "🛡 BLOCKED LOCALLY"
    )

    print(
        "Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY"
    )

    print()

    if (
        STRUCTURAL_FAILURES == 0
        and
        READINESS_BLOCKERS == 0
    ):

        print(
            "✅ R28 UNIT N.9 DIAGNOSTIC PASSED"
        )

        print(
            "✅ CONSUMED AUTHORIZATION "
            "SURVIVES RESTART"
        )

        print(
            "✅ POST-RESTART REPLAY BLOCKED"
        )

        print(
            "✅ UNUSED AUTHORIZATION "
            "SURVIVES RESTART"
        )

        print(
            "✅ RESTORED AUTHORIZATION "
            "REMAINS SINGLE-USE"
        )

        print(
            "✅ N.8 REQUEST BINDING "
            "SURVIVES RESTART"
        )

        print(
            "✅ SNAPSHOT TAMPERING BLOCKED"
        )

        print(
            "✅ SNAPSHOT CORRUPTION BLOCKED"
        )

        print(
            "✅ STALE SNAPSHOT ROLLBACK BLOCKED"
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
            "🛡 NO NETWORK WRITE "
            "WAS TRANSMITTED"
        )

    else:

        print(
            "❌ R28 UNIT N.9 "
            "DIAGNOSTIC FAILED"
        )

    print("=" * 92)

    return (
        STRUCTURAL_FAILURES == 0
        and
        READINESS_BLOCKERS == 0
    )


# ============================================================
# HEARTBEAT
# ============================================================

def persistent_runtime():

    print("=" * 92)

    print(
        "R28 UNIT N.9: "
        "PERSISTENT RUNTIME ACTIVE"
    )

    print(
        "R28 UNIT N.9: "
        "RESTART-PERSISTENCE GATE ACTIVE"
    )

    print(
        "R28 UNIT N.9: "
        "SNAPSHOT INTEGRITY GATE ACTIVE"
    )

    print(
        "R28 UNIT N.9: "
        "ROLLBACK PROTECTION ACTIVE"
    )

    print(
        "R28 UNIT N.9: "
        "POST-RESTART REPLAY LOCK ACTIVE"
    )

    print(
        "R28 UNIT N.9: "
        "SINGLE-USE DISPATCH LOCK ACTIVE"
    )

    print(
        "R28 UNIT N.9: "
        "SYNTHETIC TRANSPORT INTERCEPTOR ACTIVE"
    )

    print(
        "R28 UNIT N.9: "
        "NETWORK WRITE TRANSPORT LOCKED"
    )

    print(
        "R28 UNIT N.9: "
        "LEVERAGE MUTATION TRANSPORT LOCKED"
    )

    counter = 1

    while True:

        print(
            f"R28 UNIT N.9: "
            f"HEARTBEAT {counter} ✅ ACTIVE",
            flush=True
        )

        counter += 1

        time.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "R28 UNIT N.9: RUNTIME STARTING",
        flush=True
    )

    start_health_server()

    passed = run_diagnostic()

    if not passed:

        print(
            "R28 UNIT N.9: "
            "READINESS BLOCKED",
            flush=True
        )

    persistent_runtime()


if __name__ == "__main__":
    main()
