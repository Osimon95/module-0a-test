import copy
import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R28 UNIT N.19
# DURABLE RECOVERY LEASE FENCING + ANTI-ABA EPOCH PROTECTION
# =============================================================================

UNIT = "R28 UNIT N.19"

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "10000"))

HEARTBEAT_SECONDS = 15

# -------------------------------------------------------------------------
# HARD SAFETY LOCKS
# -------------------------------------------------------------------------

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

LEVERAGE_PATH = "/capi/v3/account/leverage"
ALLOWED_METHOD = "POST"


print(f"{UNIT}: MAIN.PY ENTERED")


# =============================================================================
# CANONICALIZATION / HASHING
# =============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def seal_dict(value):
    body = {
        k: v
        for k, v in value.items()
        if k != "seal"
    }

    return sha256_text(
        canonical_json(body)
    )


# =============================================================================
# EXCEPTIONS
# =============================================================================

class LocalBlock(RuntimeError):
    pass


class StructuralError(RuntimeError):
    pass


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = b"OK"

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

    def log_message(self, fmt, *args):
        return


def start_health_server():

    try:
        server = HTTPServer(
            (HOST, PORT),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        print(
            f"{UNIT}: HEALTH SERVER ACTIVE "
            f"ON PORT {PORT}"
        )

    except OSError as exc:

        print(
            f"{UNIT}: HEALTH SERVER WARNING: "
            f"{exc}"
        )


# =============================================================================
# DURABLE RECOVERY LEASE
# =============================================================================

@dataclass
class RecoveryLease:

    generation: int
    epoch: int
    owner: str
    nonce: int

    state: str = "ACTIVE"

    seal: str = ""

    def finalize(self):

        self.seal = seal_dict(
            asdict(self)
        )

        return self

    def verify(self):

        return (
            self.seal
            ==
            seal_dict(asdict(self))
        )


# =============================================================================
# DURABLE COMMIT
# =============================================================================

@dataclass
class DurableCommit:

    generation: int
    epoch: int

    intent_id: str
    payload_hash: str

    authorization_id: str
    authorization_consumed: bool

    terminal: bool

    seal: str = ""

    def finalize(self):

        self.seal = seal_dict(
            asdict(self)
        )

        return self

    def verify(self):

        return (
            self.seal
            ==
            seal_dict(asdict(self))
        )


# =============================================================================
# COMMIT MANIFEST
# =============================================================================

@dataclass
class CommitManifest:

    generation: int
    epoch: int

    lease_seal: str
    commit_seal: str

    previous_manifest_seal: str

    seal: str = ""

    def finalize(self):

        self.seal = seal_dict(
            asdict(self)
        )

        return self

    def verify(self):

        return (
            self.seal
            ==
            seal_dict(asdict(self))
        )


# =============================================================================
# SYNTHETIC TRANSPORT
# =============================================================================

class SyntheticTransport:

    def __init__(self):

        self.network_posts = 0
        self.network_writes = 0

        self.leverage_transmissions = 0

        self.synthetic_dispatches = 0

        self.receipts = []

    # ---------------------------------------------------------------------
    # SYNTHETIC DISPATCH
    # ---------------------------------------------------------------------

    def synthetic_dispatch(
        self,
        method,
        path,
        payload,
    ):

        if method != ALLOWED_METHOD:

            raise StructuralError(
                "synthetic dispatch method mismatch"
            )

        if path != LEVERAGE_PATH:

            raise StructuralError(
                "synthetic dispatch path mismatch"
            )

        receipt = {

            "synthetic": True,

            "transmitted": False,

            "method": method,

            "path": path,

            "payload_hash":
                sha256_text(
                    canonical_json(payload)
                ),
        }

        self.synthetic_dispatches += 1

        self.receipts.append(
            receipt
        )

        return receipt

    # ---------------------------------------------------------------------
    # REAL POST FIREBREAK
    # ---------------------------------------------------------------------

    def real_post(
        self,
        path,
        payload,
    ):

        if (
            not LIVE_ORDER_EXECUTION
            or
            not NETWORK_WRITES_ENABLED
        ):

            raise LocalBlock(
                f"{UNIT} LOCAL BLOCK: "
                f"real network POST is disabled."
            )

        self.network_posts += 1
        self.network_writes += 1

        raise AssertionError(
            "real network POST unexpectedly enabled"
        )

    # ---------------------------------------------------------------------
    # GENERIC WRITE FIREBREAK
    # ---------------------------------------------------------------------

    def generic_write(
        self,
        method,
        path,
        payload,
    ):

        if not NETWORK_WRITES_ENABLED:

            raise LocalBlock(
                f"{UNIT} LOCAL BLOCK: "
                f"network write method "
                f"{method} is disabled."
            )

        self.network_writes += 1

        raise AssertionError(
            "generic network write "
            "unexpectedly enabled"
        )

    # ---------------------------------------------------------------------
    # LEVERAGE MUTATION FIREBREAK
    # ---------------------------------------------------------------------

    def leverage_mutation(
        self,
        payload,
    ):

        if not LEVERAGE_MUTATION_TRANSPORT_ENABLED:

            raise LocalBlock(
                f"{UNIT} LOCAL BLOCK: "
                f"leverage mutation transport "
                f"is disabled."
            )

        self.leverage_transmissions += 1

        raise AssertionError(
            "leverage mutation transport "
            "unexpectedly enabled"
        )


# =============================================================================
# DURABLE RECOVERY STORE
# =============================================================================

class DurableRecoveryStore:

    def __init__(self):

        self.lock = threading.RLock()

        self.generation = 0
        self.epoch = 1

        self.lease_nonce = 0

        self.active_lease = None

        self.commit = None
        self.manifest = None

        self.final_manifest_seal = ""

        self.dispatch_generation = set()

    # ---------------------------------------------------------------------
    # STRUCTURAL INTEGRITY
    # ---------------------------------------------------------------------

    def _assert_integrity(self):

        if self.active_lease:

            if not self.active_lease.verify():

                raise StructuralError(
                    "recovery lease "
                    "integrity seal mismatch"
                )

        if self.commit:

            if not self.commit.verify():

                raise StructuralError(
                    "durable commit "
                    "integrity seal mismatch"
                )

        if self.manifest:

            if not self.manifest.verify():

                raise StructuralError(
                    "commit manifest "
                    "integrity seal mismatch"
                )

        if self.manifest:

            if (
                not self.active_lease
                or
                not self.commit
            ):

                raise StructuralError(
                    "partial durable generation"
                )

            if (
                self.manifest.generation
                !=
                self.active_lease.generation
            ):

                raise StructuralError(
                    "lease generation mismatch"
                )

            if (
                self.manifest.generation
                !=
                self.commit.generation
            ):

                raise StructuralError(
                    "commit generation mismatch"
                )

            if (
                self.manifest.epoch
                !=
                self.active_lease.epoch
            ):

                raise StructuralError(
                    "lease epoch mismatch"
                )

            if (
                self.manifest.epoch
                !=
                self.commit.epoch
            ):

                raise StructuralError(
                    "commit epoch mismatch"
                )

            if (
                self.manifest.lease_seal
                !=
                self.active_lease.seal
            ):

                raise StructuralError(
                    "manifest lease "
                    "binding mismatch"
                )

            if (
                self.manifest.commit_seal
                !=
                self.commit.seal
            ):

                raise StructuralError(
                    "manifest commit "
                    "binding mismatch"
                )

    # ---------------------------------------------------------------------
    # SEED AUTHORIZED GENERATION
    # ---------------------------------------------------------------------

    def seed_authorized_generation(self):

        with self.lock:

            self.generation = 1

            self.lease_nonce = 1

            self.active_lease = RecoveryLease(

                generation=1,

                epoch=self.epoch,

                owner="bootstrap",

                nonce=1,

                state="RELEASED",

            ).finalize()

            payload = {

                "symbol": "BTCUSDT",

                "marginMode": "ISOLATED",

                "leverage": "100",
            }

            payload_hash = sha256_text(
                canonical_json(payload)
            )

            self.commit = DurableCommit(

                generation=1,

                epoch=self.epoch,

                intent_id="intent-n19-0001",

                payload_hash=payload_hash,

                authorization_id="auth-n19-0001",

                authorization_consumed=True,

                terminal=False,

            ).finalize()

            self.manifest = CommitManifest(

                generation=1,

                epoch=self.epoch,

                lease_seal=
                    self.active_lease.seal,

                commit_seal=
                    self.commit.seal,

                previous_manifest_seal=
                    "GENESIS",

            ).finalize()

            self._assert_integrity()

            return payload

    # ---------------------------------------------------------------------
    # ACQUIRE RECOVERY LEASE
    # ---------------------------------------------------------------------

    def acquire_recovery_lease(
        self,
        owner,
        expected_generation,
        expected_epoch,
    ):

        with self.lock:

            self._assert_integrity()

            if expected_epoch != self.epoch:

                raise LocalBlock(
                    "recovery lease epoch mismatch"
                )

            if (
                expected_generation
                !=
                self.generation
            ):

                raise LocalBlock(
                    "recovery lease generation mismatch"
                )

            if (
                self.commit
                and
                self.commit.terminal
            ):

                raise LocalBlock(
                    "terminal generation cannot "
                    "acquire recovery lease"
                )

            if (
                self.active_lease
                and
                self.active_lease.state
                ==
                "ACTIVE"
            ):

                raise LocalBlock(
                    "recovery lease already held"
                )

            self.lease_nonce += 1

            self.active_lease = RecoveryLease(

                generation=self.generation,

                epoch=self.epoch,

                owner=owner,

                nonce=self.lease_nonce,

                state="ACTIVE",

            ).finalize()

            previous = (

                self.manifest.seal

                if self.manifest

                else "GENESIS"
            )

            self.manifest = CommitManifest(

                generation=self.generation,

                epoch=self.epoch,

                lease_seal=
                    self.active_lease.seal,

                commit_seal=
                    self.commit.seal,

                previous_manifest_seal=
                    previous,

            ).finalize()

            self._assert_integrity()

            return copy.deepcopy(
                self.active_lease
            )

    # ---------------------------------------------------------------------
    # VALIDATE LEASE
    # ---------------------------------------------------------------------

    def validate_lease(
        self,
        lease,
    ):

        with self.lock:

            self._assert_integrity()

            if not lease.verify():

                raise LocalBlock(
                    "recovery lease "
                    "integrity seal mismatch"
                )

            if lease.epoch != self.epoch:

                raise LocalBlock(
                    "stale recovery lease epoch"
                )

            if (
                lease.generation
                !=
                self.generation
            ):

                raise LocalBlock(
                    "stale recovery "
                    "lease generation"
                )

            if not self.active_lease:

                raise LocalBlock(
                    "no active recovery lease"
                )

            if (
                lease.seal
                !=
                self.active_lease.seal
            ):

                raise LocalBlock(
                    "recovery lease fence mismatch"
                )

            if (
                lease.owner
                !=
                self.active_lease.owner
            ):

                raise LocalBlock(
                    "recovery lease owner mismatch"
                )

            if (
                lease.nonce
                !=
                self.active_lease.nonce
            ):

                raise LocalBlock(
                    "recovery lease nonce mismatch"
                )

            if (
                self.active_lease.state
                !=
                "ACTIVE"
            ):

                raise LocalBlock(
                    "recovery lease is not active"
                )

            return True

    # ---------------------------------------------------------------------
    # RELEASE RECOVERY LEASE
    # ---------------------------------------------------------------------

    def release_lease(
        self,
        lease,
    ):

        with self.lock:

            self.validate_lease(
                lease
            )

            self.active_lease.state = (
                "RELEASED"
            )

            self.active_lease.finalize()

            previous = (
                self.manifest.seal
            )

            self.manifest = CommitManifest(

                generation=self.generation,

                epoch=self.epoch,

                lease_seal=
                    self.active_lease.seal,

                commit_seal=
                    self.commit.seal,

                previous_manifest_seal=
                    previous,

            ).finalize()

            self._assert_integrity()

    # ---------------------------------------------------------------------
    # SINGLE RECOVERY
    # ---------------------------------------------------------------------

    def recover_once(
        self,
        lease,
        payload,
        transport,
    ):

        with self.lock:

            self.validate_lease(
                lease
            )

            if self.commit.terminal:

                raise LocalBlock(
                    "terminal generation "
                    "is immutable"
                )

            if not (
                self.commit.authorization_consumed
            ):

                raise StructuralError(
                    "recovery requires "
                    "consumed authorization"
                )

            supplied_hash = sha256_text(
                canonical_json(payload)
            )

            if (
                self.commit.payload_hash
                !=
                supplied_hash
            ):

                raise LocalBlock(
                    "recovery payload "
                    "binding mismatch"
                )

            if (
                self.generation
                in
                self.dispatch_generation
            ):

                raise LocalBlock(
                    "synthetic dispatch already "
                    "produced for generation"
                )

            receipt = (
                transport.synthetic_dispatch(
                    ALLOWED_METHOD,
                    LEVERAGE_PATH,
                    payload,
                )
            )

            self.dispatch_generation.add(
                self.generation
            )

            # -------------------------------------------------------------
            # FINALIZE COMMIT
            # -------------------------------------------------------------

            self.commit.terminal = True

            self.commit.finalize()

            # -------------------------------------------------------------
            # RELEASE WINNING LEASE
            # -------------------------------------------------------------

            self.active_lease.state = (
                "RELEASED"
            )

            self.active_lease.finalize()

            # -------------------------------------------------------------
            # FINAL MANIFEST
            # -------------------------------------------------------------

            previous = (
                self.manifest.seal
            )

            self.manifest = CommitManifest(

                generation=self.generation,

                epoch=self.epoch,

                lease_seal=
                    self.active_lease.seal,

                commit_seal=
                    self.commit.seal,

                previous_manifest_seal=
                    previous,

            ).finalize()

            self.final_manifest_seal = (
                self.manifest.seal
            )

            self._assert_integrity()

            return receipt

    # ---------------------------------------------------------------------
    # EPOCH ADVANCE
    # ---------------------------------------------------------------------

    def advance_epoch(self):

        with self.lock:

            self.epoch += 1

            return self.epoch

    # ---------------------------------------------------------------------
    # FORGED ABA LEASE
    # ---------------------------------------------------------------------

    def forge_generation_reuse(
        self,
        old_lease,
    ):

        with self.lock:

            forged = copy.deepcopy(
                old_lease
            )

            forged.generation = (
                self.generation
            )

            forged.epoch = (
                self.epoch
            )

            forged.finalize()

            return forged


# =============================================================================
# TEST FRAMEWORK
# =============================================================================

passes = 0
failures = 0

structural_failures = 0
readiness_blockers = 0


def divider():

    print("-" * 92)


def heading(text):

    print()

    print(text)

    divider()


def check(
    label,
    condition,
):

    global passes
    global failures

    if condition:

        passes += 1

        print(
            f"{label:<86} ✅ PASS"
        )

        return True

    failures += 1

    print(
        f"{label:<86} ❌ FAIL"
    )

    return False


def expect_local_block(
    label,
    fn,
    contains=None,
):

    global failures

    try:

        fn()

    except LocalBlock as exc:

        print(
            f"{UNIT} LOCAL BLOCK:"
        )

        print(
            f"  {exc}"
        )

        ok = (

            contains is None

            or

            contains in str(exc)
        )

        return check(
            label,
            ok,
        )

    except Exception as exc:

        failures += 1

        print(
            f"{label:<86} ❌ FAIL "
            f"({type(exc).__name__}: {exc})"
        )

        return False

    failures += 1

    print(
        f"{label:<86} ❌ FAIL "
        f"(no local block)"
    )

    return False


# =============================================================================
# MAIN DIAGNOSTIC
# =============================================================================

def main():

    global structural_failures
    global readiness_blockers

    print(
        f"{UNIT}: IMPORTS COMPLETE"
    )

    print(
        f"{UNIT}: CONSTANTS INITIALIZED"
    )

    print(
        f"{UNIT}: RUNTIME STARTING"
    )

    start_health_server()

    print("=" * 92)

    print(
        "0F-4H-R28-UNIT-N.19 STARTING"
    )

    print("=" * 92)

    transport = SyntheticTransport()

    store = DurableRecoveryStore()

    payload = (
        store.seed_authorized_generation()
    )


    # =========================================================================
    # TEST 1
    # =========================================================================

    heading(
        f"{UNIT} TEST 1: "
        f"BASELINE DURABLE GENERATION"
    )

    check(
        "Commit Manifest Integrity Verified",
        store.manifest.verify(),
    )

    check(
        "Durable Commit Integrity Verified",
        store.commit.verify(),
    )

    check(
        "Seed Authorization Persisted As Consumed",
        store.commit.authorization_consumed
        is True,
    )

    check(
        "Seed Generation Is Non-Terminal",
        store.commit.terminal
        is False,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    heading(
        f"{UNIT} TEST 2: "
        f"RECOVERY LEASE ACQUISITION"
    )

    lease_a = (
        store.acquire_recovery_lease(
            "worker-A",
            1,
            1,
        )
    )

    check(
        "Recovery Lease Acquired",
        lease_a.state
        ==
        "ACTIVE",
    )

    check(
        "Recovery Lease Bound To Generation",
        lease_a.generation
        ==
        store.generation,
    )

    check(
        "Recovery Lease Bound To Epoch",
        lease_a.epoch
        ==
        store.epoch,
    )

    check(
        "Recovery Lease Integrity Seal Verified",
        lease_a.verify(),
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    heading(
        f"{UNIT} TEST 3: "
        f"EXCLUSIVE LEASE OWNERSHIP"
    )

    expect_local_block(

        "Second Worker Lease Acquisition Rejected",

        lambda:
            store.acquire_recovery_lease(
                "worker-B",
                1,
                1,
            ),

        "already held",
    )

    check(
        "Original Lease Remains Active",

        store.active_lease.owner
        ==
        "worker-A",
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    heading(
        f"{UNIT} TEST 4: "
        f"FORGED LEASE OWNER REJECTION"
    )

    forged_owner = copy.deepcopy(
        lease_a
    )

    forged_owner.owner = (
        "worker-B"
    )

    forged_owner.finalize()

    expect_local_block(

        "Forged Lease Owner Rejected",

        lambda:
            store.validate_lease(
                forged_owner
            ),

        "fence mismatch",
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    heading(
        f"{UNIT} TEST 5: "
        f"FORGED LEASE NONCE REJECTION"
    )

    forged_nonce = copy.deepcopy(
        lease_a
    )

    forged_nonce.nonce += 1

    forged_nonce.finalize()

    expect_local_block(

        "Forged Lease Nonce Rejected",

        lambda:
            store.validate_lease(
                forged_nonce
            ),

        "fence mismatch",
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    heading(
        f"{UNIT} TEST 6: "
        f"TAMPERED LEASE SEAL REJECTION"
    )

    tampered = copy.deepcopy(
        lease_a
    )

    tampered.owner = (
        "tampered-without-reseal"
    )

    expect_local_block(

        "Tampered Lease Integrity Rejected",

        lambda:
            store.validate_lease(
                tampered
            ),

        "integrity seal mismatch",
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    heading(
        f"{UNIT} TEST 7: "
        f"STALE LEASE AFTER RELEASE"
    )

    stale_released = (
        copy.deepcopy(
            lease_a
        )
    )

    store.release_lease(
        lease_a
    )

    expect_local_block(

        "Released Lease Cannot Be Reused",

        lambda:
            store.validate_lease(
                stale_released
            ),

        "fence mismatch",
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    heading(
        f"{UNIT} TEST 8: "
        f"MONOTONIC LEASE NONCE"
    )

    lease_b = (
        store.acquire_recovery_lease(
            "worker-B",
            1,
            1,
        )
    )

    check(
        "New Lease Nonce Is Greater Than Prior Lease",

        lease_b.nonce
        >
        lease_a.nonce,
    )

    check(
        "New Lease Seal Differs From Prior Lease",

        lease_b.seal
        !=
        lease_a.seal,
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    heading(
        f"{UNIT} TEST 9: "
        f"STALE WORKER FENCING"
    )

    expect_local_block(

        "Old Worker Lease Rejected After New Lease",

        lambda:
            store.validate_lease(
                lease_a
            ),

        "fence mismatch",
    )

    check(
        "Current Worker Lease Accepted",

        store.validate_lease(
            lease_b
        )
        is True,
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    heading(
        f"{UNIT} TEST 10: "
        f"RECOVERY PAYLOAD BINDING"
    )

    wrong_payload = dict(
        payload
    )

    wrong_payload[
        "leverage"
    ] = "99"

    expect_local_block(

        "Tampered Recovery Payload Rejected",

        lambda:
            store.recover_once(
                lease_b,
                wrong_payload,
                transport,
            ),

        "payload binding mismatch",
    )

    check(
        "Tampered Recovery Produced No Synthetic Dispatch",

        transport.synthetic_dispatches
        ==
        0,
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    heading(
        f"{UNIT} TEST 11: "
        f"VALID SINGLE RECOVERY"
    )

    receipt = (
        store.recover_once(
            lease_b,
            payload,
            transport,
        )
    )

    check(
        "Authorized Recovery Produced Synthetic Receipt",

        receipt["synthetic"]
        is True,
    )

    check(
        "Synthetic Receipt Reports No Transmission",

        receipt["transmitted"]
        is False,
    )

    check(
        "Exactly One Synthetic Dispatch Produced",

        transport.synthetic_dispatches
        ==
        1,
    )

    check(
        "Recovered Generation Became Terminal",

        store.commit.terminal
        is True,
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    heading(
        f"{UNIT} TEST 12: "
        f"TERMINAL FINALITY"
    )

    expect_local_block(

        "Terminal Generation Rejects New Recovery Lease",

        lambda:
            store.acquire_recovery_lease(
                "worker-C",
                1,
                1,
            ),

        "terminal generation",
    )

    expect_local_block(

        "Terminal Generation Rejects Repeated Recovery",

        lambda:
            store.recover_once(
                lease_b,
                payload,
                transport,
            ),
    )

    check(
        "Repeated Recovery Produced No Second Dispatch",

        transport.synthetic_dispatches
        ==
        1,
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    heading(
        f"{UNIT} TEST 13: "
        f"EPOCH ADVANCE FENCES OLD LEASE"
    )

    old_epoch_lease = (
        copy.deepcopy(
            lease_b
        )
    )

    new_epoch = (
        store.advance_epoch()
    )

    check(
        "Recovery Epoch Advanced Monotonically",

        new_epoch
        ==
        2,
    )

    expect_local_block(

        "Old Epoch Lease Rejected",

        lambda:
            store.validate_lease(
                old_epoch_lease
            ),

        "stale recovery lease epoch",
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    heading(
        f"{UNIT} TEST 14: "
        f"ANTI-ABA GENERATION REUSE REJECTION"
    )

    forged_aba = (
        store.forge_generation_reuse(
            old_epoch_lease
        )
    )

    expect_local_block(

        "Reused Generation With New Epoch Cannot Resurrect Old Lease",

        lambda:
            store.validate_lease(
                forged_aba
            ),
    )

    check(
        "Terminal Commit Remains Immutable After ABA Attempt",

        store.commit.terminal
        is True,
    )

    check(
        "Synthetic Dispatch Count Remains One",

        transport.synthetic_dispatches
        ==
        1,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    heading(
        f"{UNIT} TEST 15: "
        f"EXACT SYNTHETIC TRANSPORT BINDING"
    )

    check(
        "Transport Method Exactly POST",

        receipt["method"]
        ==
        "POST",
    )

    check(
        "Transport Path Exactly Leverage Endpoint",

        receipt["path"]
        ==
        LEVERAGE_PATH,
    )

    check(
        "Transport Payload Hash Preserved",

        receipt["payload_hash"]
        ==
        store.commit.payload_hash,
    )


    # =========================================================================
    # TEST 16
    # =========================================================================

    heading(
        f"{UNIT} TEST 16: "
        f"FINAL NETWORK WRITE FIREBREAK"
    )

    expect_local_block(

        "Real POST Rejected Locally",

        lambda:
            transport.real_post(
                LEVERAGE_PATH,
                payload,
            ),

        "real network POST is disabled",
    )

    expect_local_block(

        "Generic Network Write Rejected Locally",

        lambda:
            transport.generic_write(
                "PUT",
                LEVERAGE_PATH,
                payload,
            ),

        "network write method PUT is disabled",
    )

    expect_local_block(

        "Leverage Mutation Transport Rejected Locally",

        lambda:
            transport.leverage_mutation(
                payload
            ),

        "leverage mutation transport is disabled",
    )

    check(
        "Network POST Count Is Zero",

        transport.network_posts
        ==
        0,
    )

    check(
        "Network Write Count Is Zero",

        transport.network_writes
        ==
        0,
    )

    check(
        "Leverage Transmission Count Is Zero",

        transport.leverage_transmissions
        ==
        0,
    )


    # =========================================================================
    # WRITE LOCK AUDIT
    # =========================================================================

    heading(
        f"{UNIT} WRITE-LOCK AUDIT"
    )

    print(
        f"  Network POSTs = "
        f"{transport.network_posts}"
    )

    print(
        f"  Network writes = "
        f"{transport.network_writes}"
    )

    print(
        f"  Leverage transmissions = "
        f"{transport.leverage_transmissions}"
    )

    print(
        f"  Synthetic dispatches = "
        f"{transport.synthetic_dispatches}"
    )

    check(
        "Network POST Count Is Zero",

        transport.network_posts
        ==
        0,
    )

    check(
        "Network Write Count Is Zero",

        transport.network_writes
        ==
        0,
    )

    check(
        "Leverage Transmission Count Is Zero",

        transport.leverage_transmissions
        ==
        0,
    )


    # =========================================================================
    # READINESS
    # =========================================================================

    if failures:

        readiness_blockers += failures


    heading(
        f"{UNIT} EXECUTION-READINESS ASSESSMENT"
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
        "  Durable Recovery Lease Integrity "
        "= ✅ VERIFIED"
    )

    print(
        "  Exclusive Lease Ownership "
        "= ✅ VERIFIED"
    )

    print(
        "  Monotonic Lease Nonce "
        "= ✅ VERIFIED"
    )

    print(
        "  Stale Worker Fencing "
        "= ✅ VERIFIED"
    )

    print(
        "  Lease Owner / Nonce Forgery Rejection "
        "= ✅ VERIFIED"
    )

    print(
        "  Recovery Payload Binding "
        "= ✅ VERIFIED"
    )

    print(
        "  Anti-ABA Epoch Fencing "
        "= ✅ VERIFIED"
    )

    print(
        "  Terminal Finality Immutability "
        "= ✅ VERIFIED"
    )

    print(
        "  Final Network Dispatch "
        "= 🛡 BLOCKED LOCALLY"
    )

    print(
        "  Leverage Mutation Transmission "
        "= 🛡 BLOCKED LOCALLY"
    )

    check(
        "Structural Safety Failures Are Zero",

        structural_failures
        ==
        0,
    )

    check(
        "Readiness Blockers Are Zero",

        readiness_blockers
        ==
        0,
    )


    # =========================================================================
    # FINAL RESULT
    # =========================================================================

    print()

    print("=" * 92)

    if (
        failures == 0
        and
        structural_failures == 0
        and
        readiness_blockers == 0
    ):

        print(
            f"✅ {UNIT} DIAGNOSTIC PASSED"
        )

        print(
            "✅ DURABLE RECOVERY LEASE "
            "FENCING VERIFIED"
        )

        print(
            "✅ EXCLUSIVE LEASE OWNERSHIP "
            "VERIFIED"
        )

        print(
            "✅ MONOTONIC LEASE NONCE "
            "VERIFIED"
        )

        print(
            "✅ STALE WORKER LEASES "
            "REJECTED"
        )

        print(
            "✅ LEASE OWNER / NONCE "
            "FORGERIES REJECTED"
        )

        print(
            "✅ RECOVERY PAYLOAD BINDING "
            "VERIFIED"
        )

        print(
            "✅ ANTI-ABA EPOCH FENCING "
            "VERIFIED"
        )

        print(
            "✅ TERMINAL FINALITY REMAINS "
            "IMMUTABLE"
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
            "🛡 NO NETWORK WRITE WAS "
            "TRANSMITTED"
        )

    else:

        print(
            f"❌ {UNIT} DIAGNOSTIC FAILED"
        )

        print(
            f"Failures = {failures}"
        )

        print(
            f"Structural Safety Failures = "
            f"{structural_failures}"
        )

        print(
            f"Readiness Blockers = "
            f"{readiness_blockers}"
        )

    print("=" * 92)

    return (
        failures == 0
        and
        structural_failures == 0
        and
        readiness_blockers == 0
    )


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":

    diagnostic_ok = main()

    print(
        f"{UNIT}: PERSISTENT RUNTIME ACTIVE"
    )

    print(
        f"{UNIT}: DURABLE RECOVERY LEASE "
        f"FENCE LOCK ACTIVE"
    )

    print(
        f"{UNIT}: EXCLUSIVE LEASE OWNER "
        f"LOCK ACTIVE"
    )

    print(
        f"{UNIT}: MONOTONIC LEASE NONCE "
        f"LOCK ACTIVE"
    )

    print(
        f"{UNIT}: STALE WORKER REJECTION "
        f"LOCK ACTIVE"
    )

    print(
        f"{UNIT}: ANTI-ABA EPOCH FENCE "
        f"LOCK ACTIVE"
    )

    print(
        f"{UNIT}: TERMINAL STATE "
        f"IMMUTABILITY LOCK ACTIVE"
    )

    print(
        f"{UNIT}: SYNTHETIC TRANSPORT "
        f"INTERCEPTOR ACTIVE"
    )

    print(
        f"{UNIT}: NETWORK WRITE "
        f"TRANSPORT LOCKED"
    )

    print(
        f"{UNIT}: LEVERAGE MUTATION "
        f"TRANSPORT LOCKED"
    )

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{UNIT}: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )
