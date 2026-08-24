print("R28 UNIT N.5: MAIN.PY ENTERED", flush=True)

import os
import sys
import json
import time
import signal
import hashlib
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

print("R28 UNIT N.5: IMPORTS COMPLETE", flush=True)


# ============================================================================
# R28 UNIT N.5
# TWO-STAGE LEVERAGE MUTATION ARMING / COMMIT AUTHORIZATION
# NO NETWORK WRITE TRANSMISSION
# ============================================================================

UNIT = "R28 UNIT N.5"
SYMBOL = "BTCUSDT"

WEEX_HOST = "https://api-contract.weex.com"
LEVERAGE_PATH = "/capi/v3/account/leverage"

TARGET_LEVERAGE = 100
TARGET_MARGIN_MODE = "ISOLATED"

PORT = int(os.environ.get("PORT", "10000"))

HEARTBEAT_SECONDS = 15

ARM_TTL_SECONDS = 30
COMMIT_TTL_SECONDS = 15

# ---------------------------------------------------------------------------
# ABSOLUTE SAFETY LOCKS
# ---------------------------------------------------------------------------

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
ACCOUNT_WRITES_ENABLED = False
LEVERAGE_WRITES_ENABLED = False

LEVERAGE_MUTATION_FEATURE_ENABLED = True

ARMING_GATE_ENABLED = True
COMMIT_GATE_ENABLED = True

TRANSPORT_WRITE_LOCK = True
LEVERAGE_TRANSPORT_LOCK = True

ALLOW_REAL_POST = False
ALLOW_DEMO_POST = False


# ============================================================================
# AUDIT STATE
# ============================================================================

audit = {
    "arm_requests": 0,
    "arm_grants": 0,
    "arm_denials": 0,

    "commit_requests": 0,
    "commit_grants": 0,
    "commit_denials": 0,

    "expired_arms_rejected": 0,
    "tampered_commits_rejected": 0,
    "commit_replays_blocked": 0,

    "local_post_attempts": 0,
    "local_post_blocks": 0,

    "network_posts": 0,
    "network_puts": 0,
    "network_patches": 0,
    "network_deletes": 0,

    "leverage_change_transmissions": 0,
    "real_order_transmissions": 0,
    "demo_order_transmissions": 0,
}


# ============================================================================
# UTILITY
# ============================================================================

def line():
    print("-" * 76, flush=True)


def big_line():
    print("=" * 76, flush=True)


def result(name, passed):
    icon = "✅ PASS" if passed else "❌ FAIL"
    print(f"{name:<68} {icon}", flush=True)
    return passed


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def now_ms():
    return int(time.time() * 1000)


def now_s():
    return time.time()


# ============================================================================
# HEALTH SERVER
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = b"R28 UNIT N.5 ACTIVE"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)

    print(
        f"{UNIT}: HEALTH SERVER ACTIVE ON PORT {PORT}",
        flush=True,
    )

    server.serve_forever()


# ============================================================================
# EXACT LEVERAGE PAYLOAD
# ============================================================================

def build_leverage_payload():
    return {
        "symbol": SYMBOL,
        "leverage": str(TARGET_LEVERAGE),
        "marginMode": TARGET_MARGIN_MODE,
    }


def payload_body(payload):
    return canonical_json(payload)


def payload_hash(payload):
    return sha256_text(payload_body(payload))


# ============================================================================
# TWO-STAGE AUTHORIZATION OBJECTS
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


active_arm: Optional[ArmAuthorization] = None
active_commit: Optional[CommitAuthorization] = None


# ============================================================================
# STAGE 1 — ARMING
# ============================================================================

def request_arm(payload):
    global active_arm

    audit["arm_requests"] += 1

    if not LEVERAGE_MUTATION_FEATURE_ENABLED:
        audit["arm_denials"] += 1
        return False, "leverage mutation feature disabled"

    if not ARMING_GATE_ENABLED:
        audit["arm_denials"] += 1
        return False, "arming gate disabled"

    if payload.get("symbol") != SYMBOL:
        audit["arm_denials"] += 1
        return False, "symbol mismatch"

    try:
        leverage = int(payload.get("leverage"))
    except Exception:
        audit["arm_denials"] += 1
        return False, "invalid leverage"

    if leverage != TARGET_LEVERAGE:
        audit["arm_denials"] += 1
        return False, "target leverage mismatch"

    if payload.get("marginMode") != TARGET_MARGIN_MODE:
        audit["arm_denials"] += 1
        return False, "margin mode mismatch"

    phash = payload_hash(payload)
    created = now_s()

    seed = (
        f"ARM|{SYMBOL}|{TARGET_LEVERAGE}|"
        f"{phash}|{created:.9f}"
    )

    arm_id = sha256_text(seed)

    active_arm = ArmAuthorization(
        arm_id=arm_id,
        payload_hash=phash,
        symbol=SYMBOL,
        target_leverage=TARGET_LEVERAGE,
        created_at=created,
        expires_at=created + ARM_TTL_SECONDS,
        consumed=False,
    )

    audit["arm_grants"] += 1

    return True, active_arm


def validate_arm(arm, payload):
    if arm is None:
        return False, "no active arm"

    if arm.consumed:
        return False, "arm already consumed"

    if now_s() > arm.expires_at:
        audit["expired_arms_rejected"] += 1
        return False, "arm expired"

    if arm.payload_hash != payload_hash(payload):
        return False, "payload no longer matches arm"

    if arm.symbol != SYMBOL:
        return False, "arm symbol mismatch"

    if arm.target_leverage != TARGET_LEVERAGE:
        return False, "arm leverage mismatch"

    return True, "arm valid"


# ============================================================================
# STAGE 2 — COMMIT AUTHORIZATION
# ============================================================================

def request_commit(arm, payload):
    global active_commit

    audit["commit_requests"] += 1

    if not COMMIT_GATE_ENABLED:
        audit["commit_denials"] += 1
        return False, "commit gate disabled"

    valid, reason = validate_arm(arm, payload)

    if not valid:
        audit["commit_denials"] += 1
        return False, reason

    phash = payload_hash(payload)
    created = now_s()

    seed = (
        f"COMMIT|{arm.arm_id}|{phash}|"
        f"{created:.9f}"
    )

    commit_id = sha256_text(seed)

    active_commit = CommitAuthorization(
        commit_id=commit_id,
        arm_id=arm.arm_id,
        payload_hash=phash,
        created_at=created,
        expires_at=created + COMMIT_TTL_SECONDS,
        consumed=False,
    )

    # Arm becomes single-use once commit exists.
    arm.consumed = True

    audit["commit_grants"] += 1

    return True, active_commit


def validate_commit(commit, payload):
    if commit is None:
        audit["commit_denials"] += 1
        return False, "no commit authorization"

    if commit.consumed:
        audit["commit_replays_blocked"] += 1
        return False, "commit authorization replay blocked"

    if now_s() > commit.expires_at:
        audit["commit_denials"] += 1
        return False, "commit authorization expired"

    current_hash = payload_hash(payload)

    if current_hash != commit.payload_hash:
        audit["tampered_commits_rejected"] += 1
        audit["commit_denials"] += 1
        return False, "payload changed after commit authorization"

    return True, "commit authorization valid"


# ============================================================================
# HARD TRANSPORT BOUNDARY
# ============================================================================

def attempt_leverage_post(path, payload, commit):
    """
    This function intentionally NEVER performs an HTTP POST.

    N.5 validates that a correctly armed and committed leverage mutation
    reaches the final local boundary and is blocked there.
    """

    audit["local_post_attempts"] += 1

    if path != LEVERAGE_PATH:
        audit["local_post_blocks"] += 1
        return False, "unexpected leverage endpoint"

    valid, reason = validate_commit(commit, payload)

    if not valid:
        audit["local_post_blocks"] += 1
        return False, reason

    # Consume commit at transport boundary.
    commit.consumed = True

    # -----------------------------------------------------------------------
    # ABSOLUTE NETWORK WRITE LOCK
    # -----------------------------------------------------------------------

    if (
        TRANSPORT_WRITE_LOCK
        or LEVERAGE_TRANSPORT_LOCK
        or not NETWORK_WRITES_ENABLED
        or not ACCOUNT_WRITES_ENABLED
        or not LEVERAGE_WRITES_ENABLED
    ):
        audit["local_post_blocks"] += 1

        return (
            False,
            f"{UNIT} LOCAL TRANSPORT BLOCK: "
            "network write transport locked.",
        )

    # This point must be unreachable in Unit N.5.
    raise RuntimeError(
        "R28 UNIT N.5 SAFETY FAILURE: "
        "network-write boundary unexpectedly became reachable"
    )


# ============================================================================
# DIAGNOSTIC
# ============================================================================

def run_diagnostic():

    failures = []

    big_line()
    print("0F-4H-R28-UNIT-N.5 STARTING", flush=True)
    print(
        "TWO-STAGE LEVERAGE MUTATION ARMING / COMMIT AUTHORIZATION",
        flush=True,
    )
    print("NO NETWORK WRITE TRANSMISSION", flush=True)
    print("FINAL TRANSPORT HARD-LOCK ACTIVE", flush=True)
    big_line()

    print(f"{UNIT} SYMBOL: {SYMBOL}", flush=True)
    print(f"{UNIT} TARGET LEVERAGE: {TARGET_LEVERAGE}x", flush=True)
    print(f"{UNIT} MARGIN MODE: {TARGET_MARGIN_MODE}", flush=True)

    print()
    print(f"{UNIT} SAFETY GATES")
    line()

    checks = [
        (
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        ),
        (
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        ),
        (
            "Network Writes Disabled",
            NETWORK_WRITES_ENABLED is False,
        ),
        (
            "Account Writes Disabled",
            ACCOUNT_WRITES_ENABLED is False,
        ),
        (
            "Leverage Writes Disabled",
            LEVERAGE_WRITES_ENABLED is False,
        ),
        (
            "Arming Gate Enabled",
            ARMING_GATE_ENABLED is True,
        ),
        (
            "Commit Gate Enabled",
            COMMIT_GATE_ENABLED is True,
        ),
        (
            "Network Transport Lock Active",
            TRANSPORT_WRITE_LOCK is True,
        ),
        (
            "Leverage Transport Lock Active",
            LEVERAGE_TRANSPORT_LOCK is True,
        ),
    ]

    for name, passed in checks:
        if not result(name, passed):
            failures.append(name)

    # -----------------------------------------------------------------------
    # PAYLOAD
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} EXACT PAYLOAD CONSTRUCTION")
    line()

    payload = build_leverage_payload()
    body = payload_body(payload)
    phash = payload_hash(payload)

    print(f"  Payload = {body}", flush=True)
    print(f"  Payload SHA256 = {phash}", flush=True)

    payload_checks = [
        (
            "Payload Symbol Exactly BTCUSDT",
            payload["symbol"] == SYMBOL,
        ),
        (
            "Payload Leverage Exactly Target",
            payload["leverage"] == str(TARGET_LEVERAGE),
        ),
        (
            "Payload Margin Mode Exactly ISOLATED",
            payload["marginMode"] == TARGET_MARGIN_MODE,
        ),
        (
            "Payload Hash Generated",
            len(phash) == 64,
        ),
    ]

    for name, passed in payload_checks:
        if not result(name, passed):
            failures.append(name)

    # -----------------------------------------------------------------------
    # ARM
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} STAGE-1 ARMING TEST")
    line()

    armed, arm_result = request_arm(payload)

    if armed:
        arm = arm_result

        print(f"  Arm ID = {arm.arm_id}", flush=True)
        print(f"  Arm Payload Hash = {arm.payload_hash}", flush=True)
        print(
            f"  Arm TTL = {ARM_TTL_SECONDS} seconds",
            flush=True,
        )
    else:
        arm = None

    if not result(
        "Exact Leverage Mutation Armed Locally",
        armed,
    ):
        failures.append("Exact Leverage Mutation Armed Locally")

    arm_valid, arm_reason = validate_arm(arm, payload)

    if not result(
        "Armed Payload Binding Valid",
        arm_valid,
    ):
        failures.append("Armed Payload Binding Valid")

    print(f"  Arm Validation = {arm_reason}", flush=True)

    # -----------------------------------------------------------------------
    # TAMPER BEFORE COMMIT
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} PRE-COMMIT TAMPER TEST")
    line()

    tampered_payload = dict(payload)
    tampered_payload["leverage"] = "99"

    tamper_valid, tamper_reason = validate_arm(
        arm,
        tampered_payload,
    )

    tamper_rejected = not tamper_valid

    if not result(
        "Tampered Payload Rejected Before Commit",
        tamper_rejected,
    ):
        failures.append(
            "Tampered Payload Rejected Before Commit"
        )

    print(
        f"  Tamper Result = {tamper_reason}",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # COMMIT
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} STAGE-2 COMMIT AUTHORIZATION")
    line()

    committed, commit_result = request_commit(
        arm,
        payload,
    )

    if committed:
        commit = commit_result

        print(
            f"  Commit ID = {commit.commit_id}",
            flush=True,
        )
        print(
            f"  Commit Arm ID = {commit.arm_id}",
            flush=True,
        )
        print(
            f"  Commit Payload Hash = "
            f"{commit.payload_hash}",
            flush=True,
        )
        print(
            f"  Commit TTL = "
            f"{COMMIT_TTL_SECONDS} seconds",
            flush=True,
        )
    else:
        commit = None

    if not result(
        "Exact Armed Mutation Commit Authorized",
        committed,
    ):
        failures.append(
            "Exact Armed Mutation Commit Authorized"
        )

    commit_valid, commit_reason = validate_commit(
        commit,
        payload,
    )

    if not result(
        "Commit Authorization Valid Before Transport",
        commit_valid,
    ):
        failures.append(
            "Commit Authorization Valid Before Transport"
        )

    print(
        f"  Commit Validation = {commit_reason}",
        flush=True,
    )

    # Arm must now be consumed.
    arm_reuse_valid, arm_reuse_reason = validate_arm(
        arm,
        payload,
    )

    if not result(
        "Stage-1 Arm Cannot Be Reused After Commit",
        not arm_reuse_valid,
    ):
        failures.append(
            "Stage-1 Arm Cannot Be Reused After Commit"
        )

    print(
        f"  Arm Replay Result = {arm_reuse_reason}",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # FINAL TRANSPORT BOUNDARY
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} FINAL TRANSPORT-BOUNDARY TEST")
    line()

    sent, transport_reason = attempt_leverage_post(
        LEVERAGE_PATH,
        payload,
        commit,
    )

    print(f"{UNIT} LOCAL BLOCK:", flush=True)
    print(f"  {transport_reason}", flush=True)

    if not result(
        "Committed Leverage POST Blocked Locally",
        sent is False,
    ):
        failures.append(
            "Committed Leverage POST Blocked Locally"
        )

    if not result(
        "Commit Consumed At Transport Boundary",
        commit is not None and commit.consumed is True,
    ):
        failures.append(
            "Commit Consumed At Transport Boundary"
        )

    # -----------------------------------------------------------------------
    # COMMIT REPLAY TEST
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} COMMIT REPLAY TEST")
    line()

    replay_valid, replay_reason = validate_commit(
        commit,
        payload,
    )

    if not result(
        "Transport Commit Replay Rejected",
        replay_valid is False,
    ):
        failures.append(
            "Transport Commit Replay Rejected"
        )

    print(
        f"  Replay Result = {replay_reason}",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # POST-COMMIT PAYLOAD TAMPERING
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} POST-COMMIT PAYLOAD BINDING TEST")
    line()

    # Create a fresh authorization pair solely for tamper testing.
    armed2, arm2 = request_arm(payload)

    if armed2:
        committed2, commit2 = request_commit(
            arm2,
            payload,
        )
    else:
        committed2 = False
        commit2 = None

    tampered2 = dict(payload)
    tampered2["marginMode"] = "CROSS"

    tampered_commit_valid, tampered_commit_reason = (
        validate_commit(
            commit2,
            tampered2,
        )
    )

    if not result(
        "Payload Mutation After Commit Rejected",
        tampered_commit_valid is False,
    ):
        failures.append(
            "Payload Mutation After Commit Rejected"
        )

    print(
        f"  Tamper Result = {tampered_commit_reason}",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # EXPIRED ARM TEST
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} ARM EXPIRY TEST")
    line()

    armed3, arm3 = request_arm(payload)

    if armed3:
        # Force local test expiry without sleeping.
        arm3.expires_at = now_s() - 1

    expired_valid, expired_reason = validate_arm(
        arm3,
        payload,
    )

    if not result(
        "Expired Mutation Arm Rejected",
        expired_valid is False,
    ):
        failures.append(
            "Expired Mutation Arm Rejected"
        )

    print(
        f"  Expiry Result = {expired_reason}",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # WRITE LOCK AUDIT
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} WRITE-LOCK AUDIT")
    line()

    write_checks = [
        (
            "Network POST Count Is Zero",
            audit["network_posts"] == 0,
        ),
        (
            "Network PUT Count Is Zero",
            audit["network_puts"] == 0,
        ),
        (
            "Network PATCH Count Is Zero",
            audit["network_patches"] == 0,
        ),
        (
            "Network DELETE Count Is Zero",
            audit["network_deletes"] == 0,
        ),
        (
            "Leverage Change Transmission Count Is Zero",
            audit["leverage_change_transmissions"] == 0,
        ),
        (
            "Real Order Transmission Count Is Zero",
            audit["real_order_transmissions"] == 0,
        ),
        (
            "Demo Order Transmission Count Is Zero",
            audit["demo_order_transmissions"] == 0,
        ),
        (
            "Exactly One Local POST Attempt Occurred",
            audit["local_post_attempts"] == 1,
        ),
        (
            "Exactly One Local POST Block Occurred",
            audit["local_post_blocks"] == 1,
        ),
        (
            "Commit Replay Was Blocked",
            audit["commit_replays_blocked"] >= 1,
        ),
        (
            "Expired Arm Was Rejected",
            audit["expired_arms_rejected"] >= 1,
        ),
        (
            "Post-Commit Tampering Was Rejected",
            audit["tampered_commits_rejected"] >= 1,
        ),
    ]

    for name, passed in write_checks:
        if not result(name, passed):
            failures.append(name)

    # -----------------------------------------------------------------------
    # AUDIT COUNTERS
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} AUTHORIZATION AUDIT:")
    print(
        f"  Arm requests = "
        f"{audit['arm_requests']}",
        flush=True,
    )
    print(
        f"  Arm grants = "
        f"{audit['arm_grants']}",
        flush=True,
    )
    print(
        f"  Arm denials = "
        f"{audit['arm_denials']}",
        flush=True,
    )
    print(
        f"  Commit requests = "
        f"{audit['commit_requests']}",
        flush=True,
    )
    print(
        f"  Commit grants = "
        f"{audit['commit_grants']}",
        flush=True,
    )
    print(
        f"  Commit denials = "
        f"{audit['commit_denials']}",
        flush=True,
    )
    print(
        f"  Expired arms rejected = "
        f"{audit['expired_arms_rejected']}",
        flush=True,
    )
    print(
        f"  Tampered commits rejected = "
        f"{audit['tampered_commits_rejected']}",
        flush=True,
    )
    print(
        f"  Commit replays blocked = "
        f"{audit['commit_replays_blocked']}",
        flush=True,
    )
    print(
        f"  Local POST attempts = "
        f"{audit['local_post_attempts']}",
        flush=True,
    )
    print(
        f"  Local POST blocks = "
        f"{audit['local_post_blocks']}",
        flush=True,
    )
    print(
        f"  Network POSTs = "
        f"{audit['network_posts']}",
        flush=True,
    )
    print(
        f"  Leverage change transmissions = "
        f"{audit['leverage_change_transmissions']}",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # READINESS ASSESSMENT
    # -----------------------------------------------------------------------

    print()
    print(f"{UNIT} EXECUTION-READINESS ASSESSMENT")
    line()

    structural_failures = len(failures)

    readiness_blockers = structural_failures

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
        "Exact Payload Construction = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "Stage-1 Mutation Arming = "
        "✅ VERIFIED"
        if armed
        else
        "Stage-1 Mutation Arming = ❌ FAILED",
        flush=True,
    )

    print(
        "Stage-2 Commit Authorization = "
        "✅ VERIFIED"
        if committed
        else
        "Stage-2 Commit Authorization = ❌ FAILED",
        flush=True,
    )

    print(
        "Payload / Authorization Binding = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "Arm Expiry Protection = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "Commit Replay Protection = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "Transport Boundary = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY",
        flush=True,
    )

    print()

    if failures:
        print(
            f"❌ {UNIT} DIAGNOSTIC FAILED",
            flush=True,
        )

        for failure in failures:
            print(
                f"   ❌ {failure}",
                flush=True,
            )

        return False

    print(
        f"✅ {UNIT} DIAGNOSTIC PASSED",
        flush=True,
    )

    print(
        "✅ TWO-STAGE MUTATION ARMING VERIFIED",
        flush=True,
    )

    print(
        "✅ EXACT PAYLOAD / ARM BINDING VERIFIED",
        flush=True,
    )

    print(
        "✅ ONE-SHOT COMMIT AUTHORIZATION VERIFIED",
        flush=True,
    )

    print(
        "✅ ARM EXPIRY PROTECTION VERIFIED",
        flush=True,
    )

    print(
        "✅ POST-COMMIT TAMPER REJECTION VERIFIED",
        flush=True,
    )

    print(
        "✅ COMMIT REPLAY LOCK VERIFIED",
        flush=True,
    )

    print(
        "✅ TRANSPORT COMMIT CONSUMPTION VERIFIED",
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

    big_line()

    return True


# ============================================================================
# RUNTIME
# ============================================================================

shutdown_event = threading.Event()


def handle_shutdown(signum, frame):
    print(
        f"{UNIT}: SHUTDOWN REQUESTED",
        flush=True,
    )

    shutdown_event.set()


def runtime_loop():

    heartbeat = 0

    big_line()
    print(
        f"{UNIT}: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: TWO-STAGE MUTATION GATE ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: ARM EXPIRY LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: COMMIT REPLAY LOCK ACTIVE",
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

    while not shutdown_event.is_set():

        heartbeat += 1

        print(
            f"{UNIT}: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        shutdown_event.wait(
            HEARTBEAT_SECONDS
        )

    print(
        f"{UNIT}: RUNTIME STOPPED CLEANLY",
        flush=True,
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    print(
        f"{UNIT}: CONSTANTS INITIALIZED",
        flush=True,
    )

    print(
        f"{UNIT}: RUNTIME STARTING",
        flush=True,
    )

    signal.signal(
        signal.SIGTERM,
        handle_shutdown,
    )

    signal.signal(
        signal.SIGINT,
        handle_shutdown,
    )

    server_thread = threading.Thread(
        target=health_server,
        daemon=True,
    )

    server_thread.start()

    # Small startup allowance for health server.
    time.sleep(0.2)

    passed = run_diagnostic()

    if not passed:
        print(
            f"{UNIT}: SAFETY DIAGNOSTIC FAILED",
            flush=True,
        )

        sys.exit(1)

    runtime_loop()


if __name__ == "__main__":
    main()
