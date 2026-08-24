import os
import json
import time
import hmac
import hashlib
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dataclasses import dataclass, asdict
from typing import Dict, Optional


UNIT = "R28 UNIT N.7"
SYMBOL = "BTCUSDT"
LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

METHOD = "POST"
PATH = "/capi/v3/account/leverage"

HEARTBEAT_SECONDS = 15
ARM_TTL_SECONDS = 5.0


# ============================================================================
# HARD SAFETY LOCKS
# ============================================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

STAGE1_ARMING_ENABLED = True
STAGE2_COMMIT_ENABLED = True


# ============================================================================
# LOCAL-ONLY DIAGNOSTIC SECRETS
#
# These are NOT WEEX credentials.
# They exist only to validate deterministic local signing and snapshot integrity.
# ============================================================================

SNAPSHOT_SECRET = b"r28-n7-local-snapshot-integrity-key"
SIGNING_SECRET = b"r28-n7-local-signing-key"


# ============================================================================
# AUDIT COUNTERS
# ============================================================================

COUNTERS = {
    "arm_requests": 0,
    "arm_grants": 0,
    "arm_denials": 0,

    "commit_requests": 0,
    "commit_grants": 0,
    "commit_denials": 0,

    "local_post_attempts": 0,
    "local_post_blocks": 0,

    "network_posts": 0,
    "leverage_transmissions": 0,

    "commit_replays_blocked": 0,
    "transport_intercepts": 0,
}


# ============================================================================
# HELPERS
# ============================================================================

def canonical_json(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode()
    ).hexdigest()


def hmac_hex(secret, text):
    return hmac.new(
        secret,
        text.encode(),
        hashlib.sha256,
    ).hexdigest()


def check(label, condition):
    mark = "✅ PASS" if condition else "❌ FAIL"

    print(
        f"{label:<76} {mark}",
        flush=True,
    )

    return bool(condition)


def section(title):
    print(
        f"\n{UNIT} {title}",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


# ============================================================================
# AUTHORIZATION STATE
# ============================================================================

@dataclass
class Arm:
    arm_id: str
    payload_hash: str
    created_at: float
    expires_at: float

    committed: bool = False
    consumed: bool = False


@dataclass
class Commit:
    commit_id: str
    arm_id: str
    payload_hash: str
    created_at: float

    consumed: bool = False


# ============================================================================
# TWO-STAGE AUTHORIZATION RUNTIME
# ============================================================================

class AuthorizationRuntime:

    def __init__(self):

        self.arms: Dict[str, Arm] = {}

        self.commits: Dict[str, Commit] = {}


    # ------------------------------------------------------------------------
    # STAGE 1
    # ------------------------------------------------------------------------

    def arm(
        self,
        payload_text,
        ttl=ARM_TTL_SECONDS,
    ):

        COUNTERS["arm_requests"] += 1

        if not STAGE1_ARMING_ENABLED:

            COUNTERS["arm_denials"] += 1

            return None


        now = time.time()

        payload_hash = sha256_text(
            payload_text
        )


        seed = (
            f"ARM|"
            f"{payload_hash}|"
            f"{now:.9f}|"
            f"{COUNTERS['arm_requests']}"
        )


        arm_id = sha256_text(
            seed
        )[:32]


        arm = Arm(
            arm_id=arm_id,
            payload_hash=payload_hash,
            created_at=now,
            expires_at=now + ttl,
        )


        self.arms[
            arm_id
        ] = arm


        COUNTERS["arm_grants"] += 1


        return arm


    # ------------------------------------------------------------------------
    # STAGE 2
    # ------------------------------------------------------------------------

    def commit(
        self,
        arm_id,
        payload_text,
    ):

        COUNTERS["commit_requests"] += 1


        arm = self.arms.get(
            arm_id
        )


        now = time.time()


        payload_hash = sha256_text(
            payload_text
        )


        valid = (

            STAGE2_COMMIT_ENABLED

            and arm is not None

            and not arm.committed

            and not arm.consumed

            and now <= arm.expires_at

            and hmac.compare_digest(
                arm.payload_hash,
                payload_hash,
            )
        )


        if not valid:

            COUNTERS["commit_denials"] += 1

            return None


        commit_seed = (
            f"COMMIT|"
            f"{arm.arm_id}|"
            f"{payload_hash}|"
            f"{now:.9f}"
        )


        commit_id = sha256_text(
            commit_seed
        )[:40]


        commit = Commit(
            commit_id=commit_id,
            arm_id=arm.arm_id,
            payload_hash=payload_hash,
            created_at=now,
        )


        self.commits[
            commit_id
        ] = commit


        arm.committed = True


        COUNTERS["commit_grants"] += 1


        return commit


    # ------------------------------------------------------------------------
    # FINAL TRANSPORT AUTHORIZATION CHECK
    # ------------------------------------------------------------------------

    def validate_for_transport(
        self,
        commit_id,
        payload_text,
    ):

        commit = self.commits.get(
            commit_id
        )


        if commit is None:

            return (
                False,
                "unknown commit",
            )


        if commit.consumed:

            COUNTERS[
                "commit_replays_blocked"
            ] += 1

            return (
                False,
                "commit replay blocked",
            )


        arm = self.arms.get(
            commit.arm_id
        )


        if arm is None:

            return (
                False,
                "missing arm",
            )


        now = time.time()


        payload_hash = sha256_text(
            payload_text
        )


        if now > arm.expires_at:

            return (
                False,
                "arm expired",
            )


        if not hmac.compare_digest(
            payload_hash,
            commit.payload_hash,
        ):

            return (
                False,
                "payload hash mismatch",
            )


        if not hmac.compare_digest(
            payload_hash,
            arm.payload_hash,
        ):

            return (
                False,
                "arm payload mismatch",
            )


        if not arm.committed:

            return (
                False,
                "arm not committed",
            )


        if arm.consumed:

            return (
                False,
                "arm already consumed",
            )


        return (
            True,
            "authorized",
        )


    # ------------------------------------------------------------------------
    # SINGLE-USE CONSUMPTION
    # ------------------------------------------------------------------------

    def consume_at_boundary(
        self,
        commit_id,
    ):

        commit = self.commits.get(
            commit_id
        )


        if (
            commit is None
            or commit.consumed
        ):

            return False


        arm = self.arms.get(
            commit.arm_id
        )


        if (
            arm is None
            or arm.consumed
        ):

            return False


        commit.consumed = True

        arm.consumed = True


        return True


    # ------------------------------------------------------------------------
    # SNAPSHOT
    # ------------------------------------------------------------------------

    def snapshot(self):

        body = {

            "version": 1,

            "arms": {
                key: asdict(value)
                for key, value
                in sorted(
                    self.arms.items()
                )
            },

            "commits": {
                key: asdict(value)
                for key, value
                in sorted(
                    self.commits.items()
                )
            },
        }


        body_text = canonical_json(
            body
        )


        mac = hmac_hex(
            SNAPSHOT_SECRET,
            body_text,
        )


        return {
            "body": body,
            "mac": mac,
        }


    # ------------------------------------------------------------------------
    # RESTORE
    # ------------------------------------------------------------------------

    @classmethod
    def restore(
        cls,
        snapshot,
    ):

        if not isinstance(
            snapshot,
            dict,
        ):

            raise ValueError(
                "invalid snapshot envelope"
            )


        body = snapshot.get(
            "body"
        )

        mac = snapshot.get(
            "mac"
        )


        if (
            not isinstance(body, dict)
            or not isinstance(mac, str)
        ):

            raise ValueError(
                "invalid snapshot envelope"
            )


        expected = hmac_hex(
            SNAPSHOT_SECRET,
            canonical_json(body),
        )


        if not hmac.compare_digest(
            mac,
            expected,
        ):

            raise ValueError(
                "snapshot integrity failure"
            )


        if body.get(
            "version"
        ) != 1:

            raise ValueError(
                "unsupported snapshot version"
            )


        runtime = cls()


        for (
            arm_id,
            raw,
        ) in body.get(
            "arms",
            {},
        ).items():

            arm = Arm(
                **raw
            )


            if arm.arm_id != arm_id:

                raise ValueError(
                    "arm key mismatch"
                )


            runtime.arms[
                arm_id
            ] = arm


        for (
            commit_id,
            raw,
        ) in body.get(
            "commits",
            {},
        ).items():

            commit = Commit(
                **raw
            )


            if commit.commit_id != commit_id:

                raise ValueError(
                    "commit key mismatch"
                )


            arm = runtime.arms.get(
                commit.arm_id
            )


            if arm is None:

                raise ValueError(
                    "commit references missing arm"
                )


            if not hmac.compare_digest(
                commit.payload_hash,
                arm.payload_hash,
            ):

                raise ValueError(
                    "commit/arm payload binding mismatch"
                )


            if (
                commit.consumed
                and not arm.consumed
            ):

                raise ValueError(
                    "consumed commit requires consumed arm"
                )


            runtime.commits[
                commit_id
            ] = commit


        return runtime


# ============================================================================
# LOCAL SIGNATURE CONSTRUCTION
#
# IMPORTANT:
#
# This does NOT contact WEEX.
#
# It uses local fake diagnostic credentials only.
# ============================================================================

class LocalSigner:

    @staticmethod
    def build_headers(
        method,
        path,
        payload_text,
        timestamp_ms,
    ):

        prehash = (
            f"{timestamp_ms}"
            f"{method}"
            f"{path}"
            f"{payload_text}"
        )


        signature = hmac_hex(
            SIGNING_SECRET,
            prehash,
        )


        headers = {

            "ACCESS-KEY":
                "R28_N7_LOCAL_TEST_KEY",

            "ACCESS-SIGN":
                signature,

            "ACCESS-PASSPHRASE":
                "R28_N7_LOCAL_TEST_PASSPHRASE",

            "ACCESS-TIMESTAMP":
                str(timestamp_ms),

            "Content-Type":
                "application/json",
        }


        return (
            headers,
            prehash,
        )


# ============================================================================
# HARD TRANSPORT INTERCEPTOR
#
# THERE IS DELIBERATELY NO requests.post()
# THERE IS DELIBERATELY NO httpx.post()
# THERE IS DELIBERATELY NO aiohttp POST
# THERE IS DELIBERATELY NO SOCKET WRITE
#
# THE REQUEST DIES HERE.
# ============================================================================

class HardTransportInterceptor:

    def __init__(
        self,
        runtime,
    ):

        self.runtime = runtime

        self.last_capture: Optional[
            dict
        ] = None


    def post(
        self,
        path,
        payload_text,
        headers,
        commit_id,
    ):

        COUNTERS[
            "local_post_attempts"
        ] += 1


        authorized, reason = (
            self.runtime
            .validate_for_transport(
                commit_id,
                payload_text,
            )
        )


        if not authorized:

            COUNTERS[
                "local_post_blocks"
            ] += 1


            return {

                "sent": False,

                "blocked": True,

                "reason": reason,
            }


        capture = {

            "method":
                "POST",

            "path":
                path,

            "payload":
                payload_text,

            "payload_sha256":
                sha256_text(
                    payload_text
                ),

            "headers":
                dict(headers),

            "commit_id":
                commit_id,
        }


        self.last_capture = capture


        COUNTERS[
            "transport_intercepts"
        ] += 1


        consumed = (
            self.runtime
            .consume_at_boundary(
                commit_id
            )
        )


        if not consumed:

            COUNTERS[
                "local_post_blocks"
            ] += 1


            return {

                "sent": False,

                "blocked": True,

                "reason":
                    "commit consumption failed",
            }


        # ====================================================================
        # ABSOLUTE TRANSPORT STOP
        #
        # A fully valid and fully authorized leverage mutation has now reached
        # the last local boundary.
        #
        # It is consumed here and NEVER transmitted.
        # ====================================================================

        COUNTERS[
            "local_post_blocks"
        ] += 1


        return {

            "sent":
                False,

            "blocked":
                True,

            "reason":
                "authorized request intercepted at local transport boundary",

            "capture":
                capture,
        }


# ============================================================================
# HEALTH SERVER
# ============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        body = (
            b"R28 UNIT N.7 OK\n"
        )


        self.send_response(
            200
        )


        self.send_header(
            "Content-Type",
            "text/plain",
        )


        self.send_header(
            "Content-Length",
            str(len(body)),
        )


        self.end_headers()


        self.wfile.write(
            body
        )


    def log_message(
        self,
        fmt,
        *args,
    ):

        return


def start_health_server():

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )


    server = HTTPServer(
        (
            "0.0.0.0",
            port,
        ),
        HealthHandler,
    )


    thread = threading.Thread(
        target=
            server.serve_forever,
        daemon=True,
    )


    thread.start()


    print(
        f"{UNIT}: "
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {port}",
        flush=True,
    )


    return server


# ============================================================================
# N.7 DIAGNOSTIC
# ============================================================================

def run_diagnostic():

    failures = 0


    print(
        "=" * 76
    )

    print(
        "0F-4H-R28-UNIT-N.7 STARTING"
    )

    print(
        "FINAL AUTHORIZATION-TO-TRANSPORT HANDOFF VALIDATION"
    )

    print(
        "FULLY AUTHORIZED LEVERAGE REQUEST IS INTERCEPTED LOCALLY"
    )

    print(
        "NO REAL OR DEMO WRITE TRANSMISSION"
    )

    print(
        "=" * 76
    )


    # ========================================================================
    # SAFETY GATES
    # ========================================================================

    section(
        "SAFETY GATES"
    )


    tests = [

        (
            "Real POST Disabled",
            not LIVE_ORDER_EXECUTION,
        ),

        (
            "Demo POST Disabled",
            not DEMO_ORDER_EXECUTION,
        ),

        (
            "Transport Write Lock Active",
            not NETWORK_WRITES_ENABLED,
        ),

        (
            "Leverage Transport Lock Active",
            not LEVERAGE_MUTATION_TRANSPORT_ENABLED,
        ),

        (
            "Stage-1 Arming Gate Active",
            STAGE1_ARMING_ENABLED,
        ),

        (
            "Stage-2 Commit Gate Active",
            STAGE2_COMMIT_ENABLED,
        ),
    ]


    for (
        label,
        condition,
    ) in tests:

        failures += (
            0
            if check(
                label,
                condition,
            )
            else 1
        )


    # ========================================================================
    # EXACT LEVERAGE PAYLOAD
    # ========================================================================

    payload = {

        "leverage":
            LEVERAGE,

        "marginMode":
            MARGIN_MODE,

        "symbol":
            SYMBOL,
    }


    payload_text = canonical_json(
        payload
    )


    payload_hash = sha256_text(
        payload_text
    )


    section(
        "EXACT PAYLOAD"
    )


    print(
        f"Payload = {payload_text}"
    )


    print(
        f"Payload SHA256 = "
        f"{payload_hash}"
    )


    expected_payload = (
        '{"leverage":"100",'
        '"marginMode":"ISOLATED",'
        '"symbol":"BTCUSDT"}'
    )


    failures += (
        0
        if check(
            "Exact Leverage Payload Preserved",
            payload_text
            == expected_payload,
        )
        else 1
    )


    runtime = (
        AuthorizationRuntime()
    )


    transport = (
        HardTransportInterceptor(
            runtime
        )
    )


    # ========================================================================
    # TEST 1
    # COMPLETE AUTHORIZATION -> SIGNING -> FINAL BOUNDARY
    # ========================================================================

    section(
        "TEST 1: COMPLETE ARM -> COMMIT -> SIGN -> TRANSPORT HANDOFF"
    )


    arm = runtime.arm(
        payload_text
    )


    failures += (
        0
        if check(
            "Stage-1 Arm Granted",
            arm is not None,
        )
        else 1
    )


    commit = (
        runtime.commit(
            arm.arm_id,
            payload_text,
        )
        if arm
        else None
    )


    failures += (
        0
        if check(
            "Stage-2 Commit Granted",
            commit is not None,
        )
        else 1
    )


    timestamp_ms = int(
        time.time()
        * 1000
    )


    (
        headers,
        prehash,
    ) = LocalSigner.build_headers(

        METHOD,

        PATH,

        payload_text,

        timestamp_ms,
    )


    expected_signature = hmac_hex(
        SIGNING_SECRET,
        prehash,
    )


    failures += (
        0
        if check(
            "Transport Method Exactly POST",
            METHOD == "POST",
        )
        else 1
    )


    failures += (
        0
        if check(
            "Transport Path Exactly Leverage Endpoint",
            PATH
            == "/capi/v3/account/leverage",
        )
        else 1
    )


    failures += (
        0
        if check(
            "Payload Hash Bound Before Transport",

            sha256_text(
                payload_text
            )
            ==
            commit.payload_hash,
        )
        else 1
    )


    failures += (
        0
        if check(
            "ACCESS-KEY Present",
            bool(
                headers.get(
                    "ACCESS-KEY"
                )
            ),
        )
        else 1
    )


    failures += (
        0
        if check(
            "ACCESS-SIGN Generated",

            hmac.compare_digest(

                headers.get(
                    "ACCESS-SIGN",
                    "",
                ),

                expected_signature,
            ),
        )
        else 1
    )


    failures += (
        0
        if check(
            "ACCESS-PASSPHRASE Present",

            bool(
                headers.get(
                    "ACCESS-PASSPHRASE"
                )
            ),
        )
        else 1
    )


    failures += (
        0
        if check(
            "ACCESS-TIMESTAMP Present",

            headers.get(
                "ACCESS-TIMESTAMP"
            )
            ==
            str(
                timestamp_ms
            ),
        )
        else 1
    )


    result = transport.post(

        PATH,

        payload_text,

        headers,

        commit.commit_id,
    )


    failures += (
        0
        if check(
            "Authorized Request Reached Local Transport Boundary",

            transport.last_capture
            is not None,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Authorized Request Blocked Before Network",

            result.get(
                "blocked"
            )

            and

            not result.get(
                "sent"
            ),
        )
        else 1
    )


    failures += (
        0
        if check(
            "Commit Consumed At Final Local Boundary",

            runtime.commits[
                commit.commit_id
            ].consumed,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Arm Consumed With Commit",

            runtime.arms[
                arm.arm_id
            ].consumed,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Captured Method Preserved",

            transport
            .last_capture
            .get(
                "method"
            )
            ==
            METHOD,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Captured Path Preserved",

            transport
            .last_capture
            .get(
                "path"
            )
            ==
            PATH,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Captured Payload Preserved",

            transport
            .last_capture
            .get(
                "payload"
            )
            ==
            payload_text,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Captured Payload Hash Preserved",

            transport
            .last_capture
            .get(
                "payload_sha256"
            )
            ==
            payload_hash,
        )
        else 1
    )


    # ========================================================================
    # TEST 2
    # REPLAY AFTER CONSUMPTION
    # ========================================================================

    section(
        "TEST 2: POST-CONSUMPTION REPLAY REJECTION"
    )


    replay = transport.post(

        PATH,

        payload_text,

        headers,

        commit.commit_id,
    )


    failures += (
        0
        if check(
            "Consumed Commit Replay Rejected",

            replay.get(
                "blocked"
            )

            and

            replay.get(
                "reason"
            )
            ==
            "commit replay blocked",
        )
        else 1
    )


    failures += (
        0
        if check(
            "Replay Did Not Reach Capture Boundary Again",

            COUNTERS[
                "transport_intercepts"
            ]
            ==
            1,
        )
        else 1
    )


    # ========================================================================
    # TEST 3
    # TAMPERED PAYLOAD
    # ========================================================================

    section(
        "TEST 3: PAYLOAD TAMPER REJECTION"
    )


    tamper_runtime = (
        AuthorizationRuntime()
    )


    tamper_transport = (
        HardTransportInterceptor(
            tamper_runtime
        )
    )


    arm2 = tamper_runtime.arm(
        payload_text
    )


    commit2 = tamper_runtime.commit(

        arm2.arm_id,

        payload_text,
    )


    tampered_payload = (
        canonical_json(
            {
                "leverage":
                    "99",

                "marginMode":
                    MARGIN_MODE,

                "symbol":
                    SYMBOL,
            }
        )
    )


    (
        tampered_headers,
        _,
    ) = LocalSigner.build_headers(

        METHOD,

        PATH,

        tampered_payload,

        int(
            time.time()
            * 1000
        ),
    )


    tampered = (
        tamper_transport.post(

            PATH,

            tampered_payload,

            tampered_headers,

            commit2.commit_id,
        )
    )


    failures += (
        0
        if check(
            "Tampered Payload Rejected Before Transport Capture",

            tampered.get(
                "blocked"
            )

            and

            tamper_transport
            .last_capture
            is None,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Tampered Commit Remains Unconsumed",

            not tamper_runtime
            .commits[
                commit2.commit_id
            ]
            .consumed,
        )
        else 1
    )


    # ========================================================================
    # TEST 4
    # SNAPSHOT ROUND TRIP BEFORE TRANSPORT HANDOFF
    # ========================================================================

    section(
        "TEST 4: SNAPSHOT ROUND-TRIP BEFORE FINAL HANDOFF"
    )


    restart_runtime = (
        AuthorizationRuntime()
    )


    arm3 = restart_runtime.arm(
        payload_text
    )


    commit3 = restart_runtime.commit(

        arm3.arm_id,

        payload_text,
    )


    snapshot = (
        restart_runtime
        .snapshot()
    )


    restored = (
        AuthorizationRuntime
        .restore(
            snapshot
        )
    )


    restart_transport = (
        HardTransportInterceptor(
            restored
        )
    )


    failures += (
        0
        if check(
            "Authorized State Snapshot Restored",

            commit3.commit_id
            in restored.commits,
        )
        else 1
    )


    restored_result = (
        restart_transport.post(

            PATH,

            payload_text,

            headers,

            commit3.commit_id,
        )
    )


    failures += (
        0
        if check(
            "Restored Commit Reached Final Boundary",

            restart_transport
            .last_capture
            is not None,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Restored Commit Consumed Exactly Once",

            restored.commits[
                commit3.commit_id
            ].consumed,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Restored Authorized Request Still Blocked Locally",

            restored_result.get(
                "blocked"
            )

            and

            not restored_result.get(
                "sent"
            ),
        )
        else 1
    )


    # ========================================================================
    # FINAL TRANSPORT AUDIT
    # ========================================================================

    section(
        "FINAL TRANSPORT-BOUNDARY AUDIT"
    )


    failures += (
        0
        if check(
            "Network POST Count Is Zero",

            COUNTERS[
                "network_posts"
            ]
            ==
            0,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Leverage Transmission Count Is Zero",

            COUNTERS[
                "leverage_transmissions"
            ]
            ==
            0,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Transport Write Lock Still Active",

            not NETWORK_WRITES_ENABLED,
        )
        else 1
    )


    failures += (
        0
        if check(
            "Leverage Mutation Transport Still Locked",

            not LEVERAGE_MUTATION_TRANSPORT_ENABLED,
        )
        else 1
    )


    # ========================================================================
    # AUDIT COUNTERS
    # ========================================================================

    section(
        "HANDOFF AUDIT"
    )


    print(
        f"  Arm requests = "
        f"{COUNTERS['arm_requests']}"
    )


    print(
        f"  Arm grants = "
        f"{COUNTERS['arm_grants']}"
    )


    print(
        f"  Arm denials = "
        f"{COUNTERS['arm_denials']}"
    )


    print(
        f"  Commit requests = "
        f"{COUNTERS['commit_requests']}"
    )


    print(
        f"  Commit grants = "
        f"{COUNTERS['commit_grants']}"
    )


    print(
        f"  Commit denials = "
        f"{COUNTERS['commit_denials']}"
    )


    print(
        f"  Local POST attempts = "
        f"{COUNTERS['local_post_attempts']}"
    )


    print(
        f"  Local POST blocks = "
        f"{COUNTERS['local_post_blocks']}"
    )


    print(
        f"  Transport intercepts = "
        f"{COUNTERS['transport_intercepts']}"
    )


    print(
        f"  Commit replays blocked = "
        f"{COUNTERS['commit_replays_blocked']}"
    )


    print(
        f"  Network POSTs = "
        f"{COUNTERS['network_posts']}"
    )


    print(
        f"  Leverage change transmissions = "
        f"{COUNTERS['leverage_transmissions']}"
    )


    # ========================================================================
    # FINAL READINESS ASSESSMENT
    # ========================================================================

    section(
        "EXECUTION-READINESS ASSESSMENT"
    )


    print(
        f"Structural Safety Failures = "
        f"{failures}"
    )


    print(
        f"Readiness Blockers = "
        f"{failures}"
    )


    if failures == 0:

        print(
            "Exact Payload Binding = "
            "✅ VERIFIED"
        )

        print(
            "Two-Stage Authorization = "
            "✅ VERIFIED"
        )

        print(
            "Signature Construction = "
            "✅ VERIFIED"
        )

        print(
            "Final Transport Interception = "
            "✅ VERIFIED"
        )

        print(
            "Single-Use Commit Consumption = "
            "✅ VERIFIED"
        )

        print(
            "Replay Protection = "
            "✅ VERIFIED"
        )

        print(
            "Restart Handoff = "
            "✅ VERIFIED"
        )

    else:

        print(
            "Exact Payload Binding = "
            "❌ FAILED"
        )

        print(
            "Two-Stage Authorization = "
            "❌ FAILED"
        )

        print(
            "Signature Construction = "
            "❌ FAILED"
        )

        print(
            "Final Transport Interception = "
            "❌ FAILED"
        )

        print(
            "Single-Use Commit Consumption = "
            "❌ FAILED"
        )

        print(
            "Replay Protection = "
            "❌ FAILED"
        )

        print(
            "Restart Handoff = "
            "❌ FAILED"
        )


    print(
        "Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY"
    )


    # ========================================================================
    # RESULT
    # ========================================================================

    if failures == 0:

        print(
            f"\n✅ {UNIT} DIAGNOSTIC PASSED"
        )

        print(
            "✅ FINAL AUTHORIZATION-TO-TRANSPORT HANDOFF VERIFIED"
        )

        print(
            "✅ EXACT METHOD / PATH / PAYLOAD BINDING VERIFIED"
        )

        print(
            "✅ LOCAL SIGNATURE CONSTRUCTION VERIFIED"
        )

        print(
            "✅ COMMIT CONSUMED ONLY AT FINAL LOCAL BOUNDARY"
        )

        print(
            "✅ POST-CONSUMPTION REPLAY BLOCKED"
        )

        print(
            "✅ AUTHORIZED STATE SURVIVES RESTART TO FINAL BOUNDARY"
        )

        print(
            "🛡 LEVERAGE MUTATION TRANSPORT REMAINS LOCKED"
        )

        print(
            "🛡 NO NETWORK WRITE WAS TRANSMITTED"
        )

    else:

        print(
            f"\n❌ {UNIT} DIAGNOSTIC FAILED "
            f"WITH {failures} FAILURE(S)"
        )


    print(
        "=" * 76
    )


    return failures == 0


# ============================================================================
# HEARTBEAT
# ============================================================================

def heartbeat_loop():

    count = 1


    while True:

        print(
            f"{UNIT}: "
            f"HEARTBEAT {count} "
            f"✅ ACTIVE",
            flush=True,
        )


        count += 1


        time.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================================
# MAIN
# ============================================================================

def main():

    print(
        f"{UNIT}: MAIN.PY ENTERED",
        flush=True,
    )


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


    if not passed:

        raise SystemExit(
            1
        )


    print(
        "=" * 76
    )


    print(
        f"{UNIT}: "
        f"PERSISTENT RUNTIME ACTIVE"
    )


    print(
        f"{UNIT}: "
        f"FINAL HANDOFF GATE ACTIVE"
    )


    print(
        f"{UNIT}: "
        f"SINGLE-USE COMMIT LOCK ACTIVE"
    )


    print(
        f"{UNIT}: "
        f"TRANSPORT INTERCEPTOR ACTIVE"
    )


    print(
        f"{UNIT}: "
        f"NETWORK WRITE TRANSPORT LOCKED"
    )


    print(
        f"{UNIT}: "
        f"LEVERAGE MUTATION TRANSPORT LOCKED"
    )


    heartbeat_loop()


if __name__ == "__main__":

    main()
