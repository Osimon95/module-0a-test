print("R28 UNIT N.6: MAIN.PY ENTERED", flush=True)

import os
import json
import time
import hmac
import hashlib
import signal
import threading
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional, Dict, Any

print("R28 UNIT N.6: IMPORTS COMPLETE", flush=True)


# ============================================================================
# R28 UNIT N.6
# RESTART PERSISTENCE / AUTHORIZATION RECOVERY SAFETY
#
# PURPOSE
#   - Persist N.5 two-stage mutation authorization state.
#   - Verify consumed commits remain consumed after restart.
#   - Verify expired arms remain unusable after restart.
#   - Verify tampered persistence snapshots are rejected.
#   - Verify corrupted snapshots fail closed.
#   - Verify replay protection survives restart.
#   - Verify no network POST/write transmission occurs.
#
# THIS UNIT DOES NOT CHANGE LEVERAGE.
# THIS UNIT DOES NOT SEND A POST TO WEEX.
# ============================================================================


UNIT = "R28 UNIT N.6"

SYMBOL = "BTCUSDT"
TARGET_LEVERAGE = 100
MARGIN_MODE = "ISOLATED"

# ---------------------------------------------------------------------------
# HARD SAFETY FLAGS
# ---------------------------------------------------------------------------

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
ACCOUNT_WRITES_ENABLED = False
LEVERAGE_WRITES_ENABLED = False

ALLOW_REAL_POST = False
ALLOW_DEMO_POST = False

ARMING_GATE_ENABLED = True
COMMIT_GATE_ENABLED = True

TRANSPORT_WRITE_LOCK = True
LEVERAGE_TRANSPORT_LOCK = True

# Snapshot integrity must use a key that stays stable across a real process
# restart. For diagnostic purposes a deterministic default is provided.
#
# In later production integration this should be supplied as a Render
# environment variable:
#
#   R28_PERSISTENCE_KEY=<strong random secret>
#
PERSISTENCE_KEY = os.getenv(
    "R28_PERSISTENCE_KEY",
    "R28-N6-LOCAL-DIAGNOSTIC-PERSISTENCE-KEY"
).encode("utf-8")

SNAPSHOT_VERSION = 1
SNAPSHOT_FILE = Path(
    os.getenv("R28_N6_SNAPSHOT_FILE", "/tmp/r28_n6_state.json")
)

HEALTH_PORT = int(os.getenv("PORT", "10000"))

ARM_TTL_SECONDS = 3.0
COMMIT_TTL_SECONDS = 10.0

RUNNING = True


print("R28 UNIT N.6: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# UTILITIES
# ============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def now_s() -> float:
    return time.time()


def deterministic_id(prefix: str, *parts: str) -> str:
    material = "|".join(str(x) for x in parts)
    digest = sha256_text(material)
    return f"{prefix}-{digest[:24]}"


def pass_fail(value: bool) -> str:
    return "✅ PASS" if value else "❌ FAIL"


def print_test(name: str, result: bool):
    print(f"{name:<72} {pass_fail(result)}", flush=True)


def divider():
    print("-" * 76, flush=True)


def big_divider():
    print("=" * 76, flush=True)


# ============================================================================
# EXACT LEVERAGE PAYLOAD
# ============================================================================

def build_leverage_payload() -> Dict[str, str]:
    return {
        "symbol": SYMBOL,
        "leverage": str(TARGET_LEVERAGE),
        "marginMode": MARGIN_MODE,
    }


def payload_body(payload: Dict[str, Any]) -> str:
    return canonical_json(payload)


def payload_hash(payload: Dict[str, Any]) -> str:
    return sha256_text(payload_body(payload))


# ============================================================================
# AUTHORIZATION RECORDS
# ============================================================================

@dataclass
class ArmAuthorization:
    arm_id: str
    payload_hash: str
    symbol: str
    target_leverage: int
    created_at: float
    expires_at: float
    consumed: bool = False


@dataclass
class CommitAuthorization:
    commit_id: str
    arm_id: str
    payload_hash: str
    created_at: float
    expires_at: float
    consumed: bool = False


# ============================================================================
# AUDIT COUNTERS
# ============================================================================

@dataclass
class AuditCounters:
    arm_requests: int = 0
    arm_grants: int = 0
    arm_denials: int = 0

    commit_requests: int = 0
    commit_grants: int = 0
    commit_denials: int = 0

    expired_arms_rejected: int = 0
    expired_commits_rejected: int = 0

    tampered_commits_rejected: int = 0
    commit_replays_blocked: int = 0

    restart_loads: int = 0
    restart_restore_successes: int = 0
    restart_restore_failures: int = 0

    snapshot_writes: int = 0
    snapshot_integrity_failures: int = 0
    corrupted_snapshots_rejected: int = 0

    persisted_consumed_commits_rejected: int = 0
    persisted_expired_arms_rejected: int = 0

    local_post_attempts: int = 0
    local_post_blocks: int = 0

    network_posts: int = 0
    leverage_change_transmissions: int = 0


# ============================================================================
# SNAPSHOT INTEGRITY
# ============================================================================

def snapshot_signature(state: Dict[str, Any]) -> str:
    message = canonical_json(state).encode("utf-8")
    return hmac.new(
        PERSISTENCE_KEY,
        message,
        hashlib.sha256,
    ).hexdigest()


def secure_snapshot_document(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "state": state,
        "signature": snapshot_signature(state),
    }


def verify_snapshot_document(document: Dict[str, Any]) -> bool:
    if not isinstance(document, dict):
        return False

    state = document.get("state")
    signature_value = document.get("signature")

    if not isinstance(state, dict):
        return False

    if not isinstance(signature_value, str):
        return False

    expected = snapshot_signature(state)

    return hmac.compare_digest(
        expected,
        signature_value,
    )


# ============================================================================
# TWO-STAGE MUTATION AUTHORIZATION ENGINE
# ============================================================================

class MutationGate:

    def __init__(self):
        self.arms: Dict[str, ArmAuthorization] = {}
        self.commits: Dict[str, CommitAuthorization] = {}
        self.audit = AuditCounters()

    # -----------------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------------

    def export_state(self) -> Dict[str, Any]:
        return {
            "snapshot_version": SNAPSHOT_VERSION,
            "unit": UNIT,
            "symbol": SYMBOL,
            "target_leverage": TARGET_LEVERAGE,
            "margin_mode": MARGIN_MODE,
            "saved_at": now_s(),

            "arms": {
                key: asdict(value)
                for key, value in sorted(self.arms.items())
            },

            "commits": {
                key: asdict(value)
                for key, value in sorted(self.commits.items())
            },
        }

    def save_snapshot(self, path: Path = SNAPSHOT_FILE):
        state = self.export_state()
        document = secure_snapshot_document(state)

        temp_path = Path(str(path) + ".tmp")

        temp_path.write_text(
            canonical_json(document),
            encoding="utf-8",
        )

        os.replace(temp_path, path)

        self.audit.snapshot_writes += 1

    def load_snapshot(self, path: Path = SNAPSHOT_FILE) -> bool:
        self.audit.restart_loads += 1

        if not path.exists():
            self.audit.restart_restore_failures += 1
            return False

        try:
            raw = path.read_text(encoding="utf-8")
            document = json.loads(raw)
        except Exception:
            self.audit.corrupted_snapshots_rejected += 1
            self.audit.restart_restore_failures += 1
            return False

        if not verify_snapshot_document(document):
            self.audit.snapshot_integrity_failures += 1
            self.audit.restart_restore_failures += 1
            return False

        state = document.get("state", {})

        if state.get("snapshot_version") != SNAPSHOT_VERSION:
            self.audit.restart_restore_failures += 1
            return False

        if state.get("symbol") != SYMBOL:
            self.audit.restart_restore_failures += 1
            return False

        if state.get("target_leverage") != TARGET_LEVERAGE:
            self.audit.restart_restore_failures += 1
            return False

        if state.get("margin_mode") != MARGIN_MODE:
            self.audit.restart_restore_failures += 1
            return False

        try:
            restored_arms = {}

            for arm_id, arm_data in state.get("arms", {}).items():
                restored_arms[arm_id] = ArmAuthorization(
                    arm_id=str(arm_data["arm_id"]),
                    payload_hash=str(arm_data["payload_hash"]),
                    symbol=str(arm_data["symbol"]),
                    target_leverage=int(
                        arm_data["target_leverage"]
                    ),
                    created_at=float(arm_data["created_at"]),
                    expires_at=float(arm_data["expires_at"]),
                    consumed=bool(arm_data["consumed"]),
                )

            restored_commits = {}

            for commit_id, commit_data in state.get(
                "commits",
                {},
            ).items():

                restored_commits[commit_id] = (
                    CommitAuthorization(
                        commit_id=str(
                            commit_data["commit_id"]
                        ),
                        arm_id=str(
                            commit_data["arm_id"]
                        ),
                        payload_hash=str(
                            commit_data["payload_hash"]
                        ),
                        created_at=float(
                            commit_data["created_at"]
                        ),
                        expires_at=float(
                            commit_data["expires_at"]
                        ),
                        consumed=bool(
                            commit_data["consumed"]
                        ),
                    )
                )

        except Exception:
            self.audit.corrupted_snapshots_rejected += 1
            self.audit.restart_restore_failures += 1
            return False

        # Validate every restored arm.
        for arm_id, arm in restored_arms.items():

            if arm.arm_id != arm_id:
                self.audit.restart_restore_failures += 1
                return False

            if arm.symbol != SYMBOL:
                self.audit.restart_restore_failures += 1
                return False

            if arm.target_leverage != TARGET_LEVERAGE:
                self.audit.restart_restore_failures += 1
                return False

        # Validate every restored commit binding.
        for commit_id, commit in restored_commits.items():

            if commit.commit_id != commit_id:
                self.audit.restart_restore_failures += 1
                return False

            arm = restored_arms.get(commit.arm_id)

            if arm is None:
                self.audit.restart_restore_failures += 1
                return False

            if commit.payload_hash != arm.payload_hash:
                self.audit.restart_restore_failures += 1
                return False

        self.arms = restored_arms
        self.commits = restored_commits

        self.audit.restart_restore_successes += 1

        return True

    # -----------------------------------------------------------------------
    # Stage 1 - ARM
    # -----------------------------------------------------------------------

    def request_arm(
        self,
        payload: Dict[str, Any],
        ttl_seconds: float = ARM_TTL_SECONDS,
    ) -> Optional[ArmAuthorization]:

        self.audit.arm_requests += 1

        if not ARMING_GATE_ENABLED:
            self.audit.arm_denials += 1
            return None

        expected_payload = build_leverage_payload()

        if payload != expected_payload:
            self.audit.arm_denials += 1
            return None

        p_hash = payload_hash(payload)

        created = now_s()
        expires = created + ttl_seconds

        nonce = (
            f"{p_hash}|{created:.9f}|"
            f"{len(self.arms)}"
        )

        arm_id = deterministic_id(
            "ARM",
            nonce,
        )

        arm = ArmAuthorization(
            arm_id=arm_id,
            payload_hash=p_hash,
            symbol=SYMBOL,
            target_leverage=TARGET_LEVERAGE,
            created_at=created,
            expires_at=expires,
            consumed=False,
        )

        self.arms[arm_id] = arm

        self.audit.arm_grants += 1

        return arm

    # -----------------------------------------------------------------------
    # Stage 2 - COMMIT
    # -----------------------------------------------------------------------

    def request_commit(
        self,
        arm_id: str,
        payload: Dict[str, Any],
        ttl_seconds: float = COMMIT_TTL_SECONDS,
    ) -> Optional[CommitAuthorization]:

        self.audit.commit_requests += 1

        if not COMMIT_GATE_ENABLED:
            self.audit.commit_denials += 1
            return None

        arm = self.arms.get(arm_id)

        if arm is None:
            self.audit.commit_denials += 1
            return None

        current = now_s()

        if current > arm.expires_at:
            self.audit.expired_arms_rejected += 1
            self.audit.commit_denials += 1
            return None

        if arm.consumed:
            self.audit.commit_denials += 1
            return None

        supplied_hash = payload_hash(payload)

        if supplied_hash != arm.payload_hash:
            self.audit.tampered_commits_rejected += 1
            self.audit.commit_denials += 1
            return None

        created = current
        expires = created + ttl_seconds

        nonce = (
            f"{arm.arm_id}|"
            f"{arm.payload_hash}|"
            f"{created:.9f}|"
            f"{len(self.commits)}"
        )

        commit_id = deterministic_id(
            "COMMIT",
            nonce,
        )

        commit = CommitAuthorization(
            commit_id=commit_id,
            arm_id=arm.arm_id,
            payload_hash=arm.payload_hash,
            created_at=created,
            expires_at=expires,
            consumed=False,
        )

        self.commits[commit_id] = commit

        # An arm can authorize only one commit.
        arm.consumed = True

        self.audit.commit_grants += 1

        return commit

    # -----------------------------------------------------------------------
    # FINAL TRANSPORT BOUNDARY
    # -----------------------------------------------------------------------

    def transport_commit(
        self,
        commit_id: str,
        payload: Dict[str, Any],
    ) -> bool:

        self.audit.local_post_attempts += 1

        commit = self.commits.get(commit_id)

        if commit is None:
            self.audit.local_post_blocks += 1
            return False

        current = now_s()

        if current > commit.expires_at:
            self.audit.expired_commits_rejected += 1
            self.audit.local_post_blocks += 1
            return False

        supplied_hash = payload_hash(payload)

        if supplied_hash != commit.payload_hash:
            self.audit.tampered_commits_rejected += 1
            self.audit.local_post_blocks += 1
            return False

        if commit.consumed:
            self.audit.commit_replays_blocked += 1
            self.audit.local_post_blocks += 1
            return False

        # Consume before transport decision.
        #
        # This guarantees a commit cannot be replayed even though the
        # actual network transport below remains disabled.
        commit.consumed = True

        # Save consumed state before any hypothetical future transport.
        self.save_snapshot()

        # HARD LOCAL WRITE LOCK.
        if (
            not NETWORK_WRITES_ENABLED
            or not ACCOUNT_WRITES_ENABLED
            or not LEVERAGE_WRITES_ENABLED
            or not ALLOW_REAL_POST
            or TRANSPORT_WRITE_LOCK
            or LEVERAGE_TRANSPORT_LOCK
        ):
            self.audit.local_post_blocks += 1
            return False

        # -------------------------------------------------------------------
        # DELIBERATELY UNREACHABLE IN UNIT N.6
        #
        # No requests.post()
        # No httpx.post()
        # No urllib POST
        # No exchange write function
        # -------------------------------------------------------------------

        raise RuntimeError(
            "R28 UNIT N.6 SAFETY FAILURE: "
            "write transport became reachable."
        )


# ============================================================================
# LOCAL HEALTH SERVER
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = b"R28 UNIT N.6 ACTIVE\n"

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def health_server():
    try:
        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        print(
            f"R28 UNIT N.6: HEALTH SERVER ACTIVE "
            f"ON PORT {HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    except Exception as exc:
        print(
            "R28 UNIT N.6: HEALTH SERVER ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )


# ============================================================================
# CLEAN TEST SNAPSHOT
# ============================================================================

def reset_test_snapshot():
    try:
        if SNAPSHOT_FILE.exists():
            SNAPSHOT_FILE.unlink()
    except Exception:
        pass

    temp = Path(str(SNAPSHOT_FILE) + ".tmp")

    try:
        if temp.exists():
            temp.unlink()
    except Exception:
        pass


# ============================================================================
# DIAGNOSTIC
# ============================================================================

def run_diagnostic() -> bool:

    failures = []

    reset_test_snapshot()

    big_divider()

    print(
        "0F-4H-R28-UNIT-N.6 STARTING",
        flush=True,
    )

    print(
        "RESTART PERSISTENCE / AUTHORIZATION RECOVERY SAFETY",
        flush=True,
    )

    print(
        "TWO-STAGE MUTATION AUTHORIZATION PERSISTENCE",
        flush=True,
    )

    print(
        "ALL EXCHANGE WRITE TRANSPORT REMAINS DISABLED",
        flush=True,
    )

    big_divider()

    print(
        f"{UNIT} SYMBOL: {SYMBOL}",
        flush=True,
    )

    print(
        f"{UNIT} TARGET LEVERAGE: "
        f"{TARGET_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{UNIT} MARGIN MODE: {MARGIN_MODE}",
        flush=True,
    )

    print()

    # ========================================================================
    # SAFETY GATES
    # ========================================================================

    print(
        "R28 UNIT N.6 SAFETY GATES",
        flush=True,
    )

    divider()

    tests = {
        "Live Execution Disabled":
            LIVE_ORDER_EXECUTION is False,

        "Demo Execution Disabled":
            DEMO_ORDER_EXECUTION is False,

        "Network Writes Disabled":
            NETWORK_WRITES_ENABLED is False,

        "Account Writes Disabled":
            ACCOUNT_WRITES_ENABLED is False,

        "Leverage Writes Disabled":
            LEVERAGE_WRITES_ENABLED is False,

        "Real POST Disabled":
            ALLOW_REAL_POST is False,

        "Demo POST Disabled":
            ALLOW_DEMO_POST is False,

        "Transport Write Lock Active":
            TRANSPORT_WRITE_LOCK is True,

        "Leverage Transport Lock Active":
            LEVERAGE_TRANSPORT_LOCK is True,

        "Stage-1 Arming Gate Active":
            ARMING_GATE_ENABLED is True,

        "Stage-2 Commit Gate Active":
            COMMIT_GATE_ENABLED is True,
    }

    for name, result in tests.items():
        print_test(name, result)

        if not result:
            failures.append(name)

    # ========================================================================
    # EXACT PAYLOAD
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 EXACT PAYLOAD",
        flush=True,
    )

    divider()

    payload = build_leverage_payload()
    body = payload_body(payload)
    p_hash = payload_hash(payload)

    print(
        f"Payload = {body}",
        flush=True,
    )

    print(
        f"Payload SHA256 = {p_hash}",
        flush=True,
    )

    payload_exact = payload == {
        "symbol": "BTCUSDT",
        "leverage": "100",
        "marginMode": "ISOLATED",
    }

    print_test(
        "Exact Leverage Payload Preserved",
        payload_exact,
    )

    if not payload_exact:
        failures.append(
            "Exact Leverage Payload Preserved"
        )

    # ========================================================================
    # TEST 1
    # CONSUMED COMMIT MUST REMAIN CONSUMED AFTER RESTART
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 TEST 1: "
        "CONSUMED COMMIT RESTART PERSISTENCE",
        flush=True,
    )

    divider()

    gate1 = MutationGate()

    arm1 = gate1.request_arm(
        payload,
        ttl_seconds=30.0,
    )

    arm1_ok = arm1 is not None

    print_test(
        "Initial Arm Granted",
        arm1_ok,
    )

    if not arm1_ok:
        failures.append("Initial Arm Granted")
        return False

    commit1 = gate1.request_commit(
        arm1.arm_id,
        payload,
        ttl_seconds=30.0,
    )

    commit1_ok = commit1 is not None

    print_test(
        "Initial Commit Granted",
        commit1_ok,
    )

    if not commit1_ok:
        failures.append("Initial Commit Granted")
        return False

    # First transport reaches the LOCAL boundary only.
    first_transport = gate1.transport_commit(
        commit1.commit_id,
        payload,
    )

    first_transport_blocked = (
        first_transport is False
        and gate1.audit.network_posts == 0
        and gate1.audit.leverage_change_transmissions == 0
    )

    print_test(
        "Initial Commit Consumed At Local Boundary",
        first_transport_blocked,
    )

    if not first_transport_blocked:
        failures.append(
            "Initial Commit Consumed At Local Boundary"
        )

    snapshot_after_consumption = (
        SNAPSHOT_FILE.exists()
    )

    print_test(
        "Consumed State Snapshot Persisted",
        snapshot_after_consumption,
    )

    if not snapshot_after_consumption:
        failures.append(
            "Consumed State Snapshot Persisted"
        )

    # -----------------------------------------------------------------------
    # Simulated process restart:
    # create a brand-new authorization engine and restore state from disk.
    # -----------------------------------------------------------------------

    gate2 = MutationGate()

    restart_loaded = gate2.load_snapshot()

    print_test(
        "Snapshot Restored Into Fresh Runtime",
        restart_loaded,
    )

    if not restart_loaded:
        failures.append(
            "Snapshot Restored Into Fresh Runtime"
        )

    restored_commit = gate2.commits.get(
        commit1.commit_id
    )

    consumed_survived_restart = (
        restored_commit is not None
        and restored_commit.consumed is True
    )

    print_test(
        "Consumed Commit State Survived Restart",
        consumed_survived_restart,
    )

    if not consumed_survived_restart:
        failures.append(
            "Consumed Commit State Survived Restart"
        )

    replay_result = gate2.transport_commit(
        commit1.commit_id,
        payload,
    )

    replay_blocked = (
        replay_result is False
        and gate2.audit.commit_replays_blocked == 1
    )

    if replay_blocked:
        gate2.audit.persisted_consumed_commits_rejected += 1

    print_test(
        "Consumed Commit Replay After Restart Rejected",
        replay_blocked,
    )

    if not replay_blocked:
        failures.append(
            "Consumed Commit Replay After Restart Rejected"
        )

    # ========================================================================
    # TEST 2
    # EXPIRED ARM MUST REMAIN INVALID THROUGH RESTART
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 TEST 2: "
        "EXPIRED ARM RESTART PROTECTION",
        flush=True,
    )

    divider()

    gate3 = MutationGate()

    arm2 = gate3.request_arm(
        payload,
        ttl_seconds=0.30,
    )

    arm2_created = arm2 is not None

    print_test(
        "Short-Lived Arm Granted",
        arm2_created,
    )

    if not arm2_created:
        failures.append(
            "Short-Lived Arm Granted"
        )
        return False

    gate3.save_snapshot()

    time.sleep(0.45)

    gate4 = MutationGate()

    expired_snapshot_loaded = (
        gate4.load_snapshot()
    )

    print_test(
        "Expired-Arm Snapshot Restored",
        expired_snapshot_loaded,
    )

    if not expired_snapshot_loaded:
        failures.append(
            "Expired-Arm Snapshot Restored"
        )

    expired_commit = gate4.request_commit(
        arm2.arm_id,
        payload,
    )

    expired_arm_rejected = (
        expired_commit is None
        and gate4.audit.expired_arms_rejected == 1
    )

    if expired_arm_rejected:
        gate4.audit.persisted_expired_arms_rejected += 1

    print_test(
        "Expired Arm Rejected After Restart",
        expired_arm_rejected,
    )

    if not expired_arm_rejected:
        failures.append(
            "Expired Arm Rejected After Restart"
        )

    # ========================================================================
    # TEST 3
    # SNAPSHOT TAMPERING
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 TEST 3: "
        "PERSISTENCE TAMPER DETECTION",
        flush=True,
    )

    divider()

    gate5 = MutationGate()

    arm3 = gate5.request_arm(
        payload,
        ttl_seconds=30.0,
    )

    gate5.save_snapshot()

    original_snapshot = SNAPSHOT_FILE.read_text(
        encoding="utf-8"
    )

    snapshot_document = json.loads(
        original_snapshot
    )

    # Tamper with protected authorization data without
    # recomputing the HMAC signature.
    state = snapshot_document["state"]

    first_arm_id = next(
        iter(state["arms"])
    )

    state["arms"][first_arm_id][
        "target_leverage"
    ] = 400

    SNAPSHOT_FILE.write_text(
        canonical_json(snapshot_document),
        encoding="utf-8",
    )

    gate6 = MutationGate()

    tampered_loaded = gate6.load_snapshot()

    tampered_rejected = (
        tampered_loaded is False
        and gate6.audit.snapshot_integrity_failures == 1
    )

    print_test(
        "Tampered Snapshot Rejected",
        tampered_rejected,
    )

    if not tampered_rejected:
        failures.append(
            "Tampered Snapshot Rejected"
        )

    fail_closed_after_tamper = (
        len(gate6.arms) == 0
        and len(gate6.commits) == 0
    )

    print_test(
        "Tampered Snapshot Failed Closed",
        fail_closed_after_tamper,
    )

    if not fail_closed_after_tamper:
        failures.append(
            "Tampered Snapshot Failed Closed"
        )

    # ========================================================================
    # TEST 4
    # CORRUPTED SNAPSHOT
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 TEST 4: "
        "CORRUPTED SNAPSHOT RECOVERY",
        flush=True,
    )

    divider()

    SNAPSHOT_FILE.write_text(
        '{"state": THIS_IS_NOT_VALID_JSON',
        encoding="utf-8",
    )

    gate7 = MutationGate()

    corrupted_loaded = gate7.load_snapshot()

    corrupted_rejected = (
        corrupted_loaded is False
        and gate7.audit.corrupted_snapshots_rejected == 1
    )

    print_test(
        "Corrupted Snapshot Rejected",
        corrupted_rejected,
    )

    if not corrupted_rejected:
        failures.append(
            "Corrupted Snapshot Rejected"
        )

    corrupted_failed_closed = (
        len(gate7.arms) == 0
        and len(gate7.commits) == 0
    )

    print_test(
        "Corrupted Snapshot Failed Closed",
        corrupted_failed_closed,
    )

    if not corrupted_failed_closed:
        failures.append(
            "Corrupted Snapshot Failed Closed"
        )

    # ========================================================================
    # TEST 5
    # VALID SNAPSHOT WITH INVALID INTERNAL COMMIT BINDING
    #
    # Here we deliberately recompute the signature after modifying the
    # snapshot. This proves HMAC integrity alone is not enough:
    # structural authorization validation must also reject impossible state.
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 TEST 5: "
        "STRUCTURAL SNAPSHOT VALIDATION",
        flush=True,
    )

    divider()

    gate8 = MutationGate()

    arm4 = gate8.request_arm(
        payload,
        ttl_seconds=30.0,
    )

    commit4 = gate8.request_commit(
        arm4.arm_id,
        payload,
        ttl_seconds=30.0,
    )

    gate8.save_snapshot()

    structure_document = json.loads(
        SNAPSHOT_FILE.read_text(
            encoding="utf-8"
        )
    )

    structure_state = structure_document[
        "state"
    ]

    structure_state["commits"][
        commit4.commit_id
    ]["payload_hash"] = (
        "0" * 64
    )

    # Re-sign modified snapshot so cryptographic integrity
    # passes. Structural binding must still reject it.
    resigned_document = (
        secure_snapshot_document(
            structure_state
        )
    )

    SNAPSHOT_FILE.write_text(
        canonical_json(resigned_document),
        encoding="utf-8",
    )

    gate9 = MutationGate()

    structurally_invalid_loaded = (
        gate9.load_snapshot()
    )

    structurally_invalid_rejected = (
        structurally_invalid_loaded is False
    )

    print_test(
        "Invalid Commit/Arm Binding Rejected",
        structurally_invalid_rejected,
    )

    if not structurally_invalid_rejected:
        failures.append(
            "Invalid Commit/Arm Binding Rejected"
        )

    structural_fail_closed = (
        len(gate9.arms) == 0
        and len(gate9.commits) == 0
    )

    print_test(
        "Invalid Binding Failed Closed",
        structural_fail_closed,
    )

    if not structural_fail_closed:
        failures.append(
            "Invalid Binding Failed Closed"
        )

    # ========================================================================
    # FINAL TRANSPORT AUDIT
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 FINAL TRANSPORT-BOUNDARY AUDIT",
        flush=True,
    )

    divider()

    all_gates = [
        gate1,
        gate2,
        gate3,
        gate4,
        gate5,
        gate6,
        gate7,
        gate8,
        gate9,
    ]

    total_local_post_attempts = sum(
        gate.audit.local_post_attempts
        for gate in all_gates
    )

    total_local_post_blocks = sum(
        gate.audit.local_post_blocks
        for gate in all_gates
    )

    total_network_posts = sum(
        gate.audit.network_posts
        for gate in all_gates
    )

    total_leverage_transmissions = sum(
        gate.audit.leverage_change_transmissions
        for gate in all_gates
    )

    total_replays_blocked = sum(
        gate.audit.commit_replays_blocked
        for gate in all_gates
    )

    total_integrity_failures = sum(
        gate.audit.snapshot_integrity_failures
        for gate in all_gates
    )

    total_corruptions_rejected = sum(
        gate.audit.corrupted_snapshots_rejected
        for gate in all_gates
    )

    network_zero = (
        total_network_posts == 0
    )

    leverage_zero = (
        total_leverage_transmissions == 0
    )

    print_test(
        "Network POST Count Is Zero",
        network_zero,
    )

    if not network_zero:
        failures.append(
            "Network POST Count Is Zero"
        )

    print_test(
        "Leverage Transmission Count Is Zero",
        leverage_zero,
    )

    if not leverage_zero:
        failures.append(
            "Leverage Transmission Count Is Zero"
        )

    print_test(
        "Transport Write Lock Still Active",
        TRANSPORT_WRITE_LOCK is True,
    )

    print_test(
        "Leverage Mutation Transport Still Locked",
        LEVERAGE_TRANSPORT_LOCK is True,
    )

    # ========================================================================
    # AUDIT COUNTERS
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 PERSISTENCE AUDIT",
        flush=True,
    )

    divider()

    print(
        f"  Local POST attempts = "
        f"{total_local_post_attempts}",
        flush=True,
    )

    print(
        f"  Local POST blocks = "
        f"{total_local_post_blocks}",
        flush=True,
    )

    print(
        f"  Commit replays blocked = "
        f"{total_replays_blocked}",
        flush=True,
    )

    print(
        f"  Snapshot integrity failures = "
        f"{total_integrity_failures}",
        flush=True,
    )

    print(
        f"  Corrupted snapshots rejected = "
        f"{total_corruptions_rejected}",
        flush=True,
    )

    print(
        f"  Network POSTs = "
        f"{total_network_posts}",
        flush=True,
    )

    print(
        f"  Leverage change transmissions = "
        f"{total_leverage_transmissions}",
        flush=True,
    )

    # ========================================================================
    # FINAL ASSESSMENT
    # ========================================================================

    print()

    print(
        "R28 UNIT N.6 EXECUTION-READINESS ASSESSMENT",
        flush=True,
    )

    divider()

    structural_failures = len(
        failures
    )

    readiness_blockers = (
        structural_failures
    )

    print(
        f"Structural Safety Failures = "
        f"{structural_failures}",
        flush=True,
    )

    print(
        f"Readiness Blockers = "
        f"{readiness_blockers}",
        flush=True,
    )

    print(
        "Consumed Commit Persistence = "
        + (
            "✅ VERIFIED"
            if consumed_survived_restart
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Restart Replay Protection = "
        + (
            "✅ VERIFIED"
            if replay_blocked
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Expired Arm Persistence = "
        + (
            "✅ VERIFIED"
            if expired_arm_rejected
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Snapshot Integrity Protection = "
        + (
            "✅ VERIFIED"
            if tampered_rejected
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Corrupted Snapshot Rejection = "
        + (
            "✅ VERIFIED"
            if corrupted_rejected
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Structural State Validation = "
        + (
            "✅ VERIFIED"
            if structurally_invalid_rejected
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Transport Boundary = "
        + (
            "✅ VERIFIED"
            if network_zero
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Leverage Mutation Transmission = "
        + (
            "🛡 BLOCKED LOCALLY"
            if leverage_zero
            else "❌ TRANSMISSION DETECTED"
        ),
        flush=True,
    )

    print()

    if structural_failures == 0:

        print(
            "✅ R28 UNIT N.6 DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ AUTHORIZATION PERSISTENCE VERIFIED",
            flush=True,
        )

        print(
            "✅ CONSUMED COMMIT SURVIVES RESTART",
            flush=True,
        )

        print(
            "✅ COMMIT REPLAY AFTER RESTART BLOCKED",
            flush=True,
        )

        print(
            "✅ EXPIRED ARM AFTER RESTART REJECTED",
            flush=True,
        )

        print(
            "✅ SNAPSHOT TAMPER PROTECTION VERIFIED",
            flush=True,
        )

        print(
            "✅ CORRUPTED SNAPSHOT FAIL-CLOSED VERIFIED",
            flush=True,
        )

        print(
            "✅ STRUCTURAL SNAPSHOT VALIDATION VERIFIED",
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
            "❌ R28 UNIT N.6 DIAGNOSTIC FAILED",
            flush=True,
        )

        for failure in failures:
            print(
                f"  ❌ {failure}",
                flush=True,
            )

        print(
            "🛡 WRITE TRANSPORT REMAINS LOCKED",
            flush=True,
        )

    big_divider()

    # Remove diagnostic persistence state.
    # A future integrated unit may intentionally retain its own state.
    reset_test_snapshot()

    return structural_failures == 0


# ============================================================================
# SHUTDOWN
# ============================================================================

def shutdown_handler(signum, frame):
    global RUNNING

    print(
        "R28 UNIT N.6: SHUTDOWN REQUESTED",
        flush=True,
    )

    RUNNING = False


signal.signal(
    signal.SIGTERM,
    shutdown_handler,
)

signal.signal(
    signal.SIGINT,
    shutdown_handler,
)


# ============================================================================
# MAIN
# ============================================================================

def main():

    global RUNNING

    print(
        "R28 UNIT N.6: RUNTIME STARTING",
        flush=True,
    )

    health_thread = threading.Thread(
        target=health_server,
        daemon=True,
    )

    health_thread.start()

    time.sleep(0.20)

    diagnostic_passed = run_diagnostic()

    big_divider()

    if diagnostic_passed:
        print(
            "R28 UNIT N.6: PERSISTENT RUNTIME ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.6: RESTART PERSISTENCE GATE ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.6: SNAPSHOT INTEGRITY LOCK ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.6: COMMIT REPLAY LOCK ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.6: NETWORK WRITE TRANSPORT LOCKED",
            flush=True,
        )

        print(
            "R28 UNIT N.6: LEVERAGE MUTATION TRANSPORT LOCKED",
            flush=True,
        )

    else:
        print(
            "R28 UNIT N.6: DIAGNOSTIC FAILURE",
            flush=True,
        )

        print(
            "R28 UNIT N.6: FAIL-CLOSED MODE ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.6: NETWORK WRITE TRANSPORT LOCKED",
            flush=True,
        )

        print(
            "R28 UNIT N.6: LEVERAGE MUTATION TRANSPORT LOCKED",
            flush=True,
        )

    heartbeat = 0

    while RUNNING:

        heartbeat += 1

        print(
            f"R28 UNIT N.6: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(15)

    print(
        "R28 UNIT N.6: RUNTIME STOPPED CLEANLY",
        flush=True,
    )


if __name__ == "__main__":
    main()
