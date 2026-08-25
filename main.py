import copy
import hashlib
import json
import os
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Tuple


print("R28 UNIT N.22: MAIN.PY ENTERED")


# ============================================================================
# R28 UNIT N.22
# DURABLE RECOVERY-GENERATION FINALITY CERTIFICATES
#
# SAFETY:
#   - REAL NETWORK POST DISABLED
#   - GENERIC NETWORK WRITES DISABLED
#   - LEVERAGE MUTATION TRANSPORT DISABLED
#   - SYNTHETIC DISPATCH ONLY
# ============================================================================


UNIT_NAME = "R28 UNIT N.22"
SYMBOL = "BTCUSDT"
LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

LEVERAGE_ENDPOINT = "/capi/v3/account/leverage"

REAL_NETWORK_POST_ENABLED = False
NETWORK_WRITE_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

STATE_FILE = "/tmp/r28_unit_n22_state.json"

HEARTBEAT_SECONDS = 15

TERMINAL_STATES = {
    "COMPLETED",
    "FAILED",
    "CANCELED",
    "REJECTED",
    "EXPIRED",
}

ACTIVE_STATES = {
    "PREPARED",
    "AUTHORIZED",
    "RECOVERING",
}

ALL_STATES = ACTIVE_STATES | TERMINAL_STATES


# ============================================================================
# GLOBAL AUDIT COUNTERS
# ============================================================================

NETWORK_POST_COUNT = 0
NETWORK_WRITE_COUNT = 0
LEVERAGE_TRANSMISSION_COUNT = 0
SYNTHETIC_DISPATCH_COUNT = 0

STRUCTURAL_SAFETY_FAILURES = 0
READINESS_BLOCKERS = 0


# ============================================================================
# HELPERS
# ============================================================================


class LocalSafetyBlock(Exception):
    pass


class IntegrityError(Exception):
    pass


class RecoveryError(Exception):
    pass


class FinalityError(Exception):
    pass


class AssertionFailure(Exception):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_object(value: Any) -> str:
    return sha256_text(canonical_json(value))


def now_ms() -> int:
    return int(time.time() * 1000)


def separator():
    print("-" * 92)


def banner():
    print("=" * 92)


def passed(label: str):
    print(f"{label:<86} ✅ PASS")


def failed(label: str):
    global STRUCTURAL_SAFETY_FAILURES
    STRUCTURAL_SAFETY_FAILURES += 1
    print(f"{label:<86} ❌ FAIL")


def require(condition: bool, label: str):
    if condition:
        passed(label)
        return

    failed(label)
    raise AssertionFailure(label)


def local_block(message: str):
    print(f"{UNIT_NAME} LOCAL BLOCK:")
    print(f"  {message}")


# ============================================================================
# EXACT SYNTHETIC TRANSPORT PAYLOAD
# ============================================================================


def build_leverage_payload() -> Dict[str, str]:
    return {
        "leverage": LEVERAGE,
        "marginMode": MARGIN_MODE,
        "symbol": SYMBOL,
    }


EXPECTED_PAYLOAD = build_leverage_payload()
EXPECTED_PAYLOAD_HASH = sha256_object(EXPECTED_PAYLOAD)


# ============================================================================
# GENERATION / LEASE / FINALITY MODEL
# ============================================================================


@dataclass
class GenerationRecord:
    generation: int
    lineage_id: str
    state: str
    recovery_epoch: int
    recovery_nonce: int
    owner_id: Optional[str]
    lease_token: Optional[str]
    lease_expires_ms: int
    payload_hash: str
    dispatch_id: Optional[str]
    finality_certificate_id: Optional[str]
    finality_certificate_hash: Optional[str]


@dataclass
class FinalityCertificate:
    certificate_id: str
    generation: int
    lineage_id: str
    terminal_state: str
    recovery_epoch: int
    recovery_nonce: int
    payload_hash: str
    dispatch_id: str
    issued_at_ms: int
    predecessor_certificate_hash: Optional[str]
    certificate_hash: str


def unsigned_certificate_dict(cert: FinalityCertificate) -> Dict[str, Any]:
    data = asdict(cert)
    data.pop("certificate_hash", None)
    return data


def compute_certificate_hash(cert: FinalityCertificate) -> str:
    return sha256_object(unsigned_certificate_dict(cert))


def make_certificate(
    generation: GenerationRecord,
    predecessor_certificate_hash: Optional[str],
) -> FinalityCertificate:

    if generation.state not in TERMINAL_STATES:
        raise FinalityError(
            "finality certificate requires terminal generation"
        )

    if not generation.dispatch_id:
        raise FinalityError(
            "finality certificate requires dispatch identity"
        )

    cert = FinalityCertificate(
        certificate_id=str(uuid.uuid4()),
        generation=generation.generation,
        lineage_id=generation.lineage_id,
        terminal_state=generation.state,
        recovery_epoch=generation.recovery_epoch,
        recovery_nonce=generation.recovery_nonce,
        payload_hash=generation.payload_hash,
        dispatch_id=generation.dispatch_id,
        issued_at_ms=now_ms(),
        predecessor_certificate_hash=predecessor_certificate_hash,
        certificate_hash="",
    )

    cert.certificate_hash = compute_certificate_hash(cert)
    return cert


# ============================================================================
# DURABLE STORE
# ============================================================================


class DurableStore:

    def __init__(self, path: str):
        self.path = path
        self.lock = threading.RLock()

    def _seal(self, body: Dict[str, Any]) -> str:
        return sha256_object(body)

    def save(
        self,
        generation: GenerationRecord,
        certificate: Optional[FinalityCertificate],
    ):

        with self.lock:

            body = {
                "version": 22,
                "generation": asdict(generation),
                "certificate": (
                    asdict(certificate)
                    if certificate is not None
                    else None
                ),
            }

            wrapper = {
                "body": body,
                "integrity_seal": self._seal(body),
            }

            tmp_path = self.path + ".tmp"

            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(
                    wrapper,
                    handle,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(tmp_path, self.path)

    def load(
        self,
    ) -> Tuple[GenerationRecord, Optional[FinalityCertificate]]:

        with self.lock:

            with open(self.path, "r", encoding="utf-8") as handle:
                wrapper = json.load(handle)

            body = wrapper["body"]
            stored_seal = wrapper["integrity_seal"]

            expected_seal = self._seal(body)

            if stored_seal != expected_seal:
                raise IntegrityError(
                    "snapshot integrity seal mismatch"
                )

            generation = GenerationRecord(
                **body["generation"]
            )

            cert_data = body.get("certificate")

            certificate = (
                FinalityCertificate(**cert_data)
                if cert_data
                else None
            )

            if certificate:

                computed = compute_certificate_hash(certificate)

                if computed != certificate.certificate_hash:
                    raise IntegrityError(
                        "finality certificate hash mismatch"
                    )

                if (
                    generation.finality_certificate_id
                    != certificate.certificate_id
                ):
                    raise IntegrityError(
                        "generation certificate identity mismatch"
                    )

                if (
                    generation.finality_certificate_hash
                    != certificate.certificate_hash
                ):
                    raise IntegrityError(
                        "generation certificate hash mismatch"
                    )

            return generation, certificate


# ============================================================================
# RECOVERY ENGINE
# ============================================================================


class RecoveryEngine:

    def __init__(self, store: DurableStore):

        self.store = store
        self.lock = threading.RLock()

        self.current = GenerationRecord(
            generation=1,
            lineage_id=str(uuid.uuid4()),
            state="PREPARED",
            recovery_epoch=1,
            recovery_nonce=1,
            owner_id=None,
            lease_token=None,
            lease_expires_ms=0,
            payload_hash=EXPECTED_PAYLOAD_HASH,
            dispatch_id=None,
            finality_certificate_id=None,
            finality_certificate_hash=None,
        )

        self.certificate: Optional[FinalityCertificate] = None

        self.synthetic_dispatch_ids = set()

    def persist(self):
        self.store.save(
            self.current,
            self.certificate,
        )

    def acquire_recovery_lease(
        self,
        owner_id: str,
        ttl_ms: int = 5000,
    ) -> str:

        with self.lock:

            if self.current.state in TERMINAL_STATES:
                raise RecoveryError(
                    "terminal generation cannot acquire recovery lease"
                )

            now = now_ms()

            if (
                self.current.owner_id is not None
                and self.current.lease_token is not None
                and now < self.current.lease_expires_ms
            ):
                raise RecoveryError(
                    "recovery lease already owned"
                )

            self.current.recovery_epoch += 1
            self.current.recovery_nonce += 1
            self.current.owner_id = owner_id
            self.current.lease_token = str(uuid.uuid4())
            self.current.lease_expires_ms = now + ttl_ms
            self.current.state = "RECOVERING"

            self.persist()

            return self.current.lease_token

    def assert_lease(
        self,
        owner_id: str,
        lease_token: str,
        generation: int,
        lineage_id: str,
        epoch: int,
        nonce: int,
    ):

        current = self.current

        if generation != current.generation:
            raise RecoveryError(
                "recovery generation mismatch"
            )

        if lineage_id != current.lineage_id:
            raise RecoveryError(
                "recovery lineage mismatch"
            )

        if epoch != current.recovery_epoch:
            raise RecoveryError(
                "recovery lease epoch mismatch"
            )

        if nonce != current.recovery_nonce:
            raise RecoveryError(
                "recovery lease nonce mismatch"
            )

        if owner_id != current.owner_id:
            raise RecoveryError(
                "recovery lease owner mismatch"
            )

        if lease_token != current.lease_token:
            raise RecoveryError(
                "recovery lease fence mismatch"
            )

        if now_ms() >= current.lease_expires_ms:
            raise RecoveryError(
                "recovery lease expired"
            )

    def synthetic_dispatch(
        self,
        owner_id: str,
        lease_token: str,
        generation: int,
        lineage_id: str,
        epoch: int,
        nonce: int,
    ) -> str:

        global SYNTHETIC_DISPATCH_COUNT

        with self.lock:

            self.assert_lease(
                owner_id,
                lease_token,
                generation,
                lineage_id,
                epoch,
                nonce,
            )

            if self.current.dispatch_id:
                return self.current.dispatch_id

            dispatch_identity = sha256_object(
                {
                    "generation": generation,
                    "lineage_id": lineage_id,
                    "epoch": epoch,
                    "nonce": nonce,
                    "payload_hash": self.current.payload_hash,
                }
            )

            if dispatch_identity not in self.synthetic_dispatch_ids:
                self.synthetic_dispatch_ids.add(dispatch_identity)
                SYNTHETIC_DISPATCH_COUNT += 1

            self.current.dispatch_id = dispatch_identity

            self.persist()

            return dispatch_identity

    def complete_generation(
        self,
        owner_id: str,
        lease_token: str,
        generation: int,
        lineage_id: str,
        epoch: int,
        nonce: int,
    ) -> FinalityCertificate:

        with self.lock:

            if self.current.state in TERMINAL_STATES:
                if self.certificate is None:
                    raise FinalityError(
                        "terminal generation missing certificate"
                    )
                return self.certificate

            self.assert_lease(
                owner_id,
                lease_token,
                generation,
                lineage_id,
                epoch,
                nonce,
            )

            if not self.current.dispatch_id:
                raise FinalityError(
                    "generation cannot finalize without dispatch"
                )

            self.current.state = "COMPLETED"

            predecessor_hash = (
                self.certificate.certificate_hash
                if self.certificate
                else None
            )

            certificate = make_certificate(
                self.current,
                predecessor_hash,
            )

            self.current.finality_certificate_id = (
                certificate.certificate_id
            )

            self.current.finality_certificate_hash = (
                certificate.certificate_hash
            )

            self.certificate = certificate

            self.persist()

            return certificate

    def validate_certificate(
        self,
        certificate: FinalityCertificate,
    ):

        if (
            compute_certificate_hash(certificate)
            != certificate.certificate_hash
        ):
            raise FinalityError(
                "finality certificate integrity mismatch"
            )

        if certificate.generation != self.current.generation:
            raise FinalityError(
                "finality certificate generation mismatch"
            )

        if certificate.lineage_id != self.current.lineage_id:
            raise FinalityError(
                "finality certificate lineage mismatch"
            )

        if certificate.recovery_epoch != self.current.recovery_epoch:
            raise FinalityError(
                "finality certificate epoch mismatch"
            )

        if certificate.recovery_nonce != self.current.recovery_nonce:
            raise FinalityError(
                "finality certificate nonce mismatch"
            )

        if certificate.payload_hash != self.current.payload_hash:
            raise FinalityError(
                "finality certificate payload mismatch"
            )

        if certificate.dispatch_id != self.current.dispatch_id:
            raise FinalityError(
                "finality certificate dispatch mismatch"
            )

        if certificate.terminal_state != self.current.state:
            raise FinalityError(
                "finality certificate terminal state mismatch"
            )

        if (
            certificate.certificate_id
            != self.current.finality_certificate_id
        ):
            raise FinalityError(
                "finality certificate identity mismatch"
            )

        if (
            certificate.certificate_hash
            != self.current.finality_certificate_hash
        ):
            raise FinalityError(
                "finality certificate binding mismatch"
            )

    def advance_generation(
        self,
        certificate: FinalityCertificate,
    ):

        with self.lock:

            self.validate_certificate(certificate)

            if self.current.state not in TERMINAL_STATES:
                raise FinalityError(
                    "generation advance requires terminal predecessor"
                )

            old_generation = self.current.generation
            old_lineage = self.current.lineage_id
            old_epoch = self.current.recovery_epoch
            old_nonce = self.current.recovery_nonce

            predecessor_hash = certificate.certificate_hash

            self.current = GenerationRecord(
                generation=old_generation + 1,
                lineage_id=str(uuid.uuid4()),
                state="PREPARED",
                recovery_epoch=old_epoch + 1,
                recovery_nonce=old_nonce + 1,
                owner_id=None,
                lease_token=None,
                lease_expires_ms=0,
                payload_hash=EXPECTED_PAYLOAD_HASH,
                dispatch_id=None,
                finality_certificate_id=None,
                finality_certificate_hash=None,
            )

            self.certificate = None

            self.persist()

            return {
                "old_generation": old_generation,
                "new_generation": self.current.generation,
                "old_lineage": old_lineage,
                "new_lineage": self.current.lineage_id,
                "predecessor_certificate_hash": predecessor_hash,
            }


# ============================================================================
# HARD NETWORK FIREBREAK
# ============================================================================


def real_network_post(
    path: str,
    payload: Dict[str, Any],
):
    global NETWORK_POST_COUNT

    if not REAL_NETWORK_POST_ENABLED:
        message = (
            f"{UNIT_NAME} LOCAL BLOCK: "
            "real network POST is disabled."
        )
        local_block(message)
        raise LocalSafetyBlock(
            "real network POST is disabled"
        )

    NETWORK_POST_COUNT += 1
    raise RuntimeError(
        "network transmission intentionally unavailable"
    )


def generic_network_write(
    method: str,
    path: str,
    payload: Dict[str, Any],
):
    global NETWORK_WRITE_COUNT

    if not NETWORK_WRITE_ENABLED:
        message = (
            f"{UNIT_NAME} LOCAL BLOCK: "
            f"network write method {method} is disabled."
        )
        local_block(message)
        raise LocalSafetyBlock(
            "network write disabled"
        )

    NETWORK_WRITE_COUNT += 1
    raise RuntimeError(
        "network transmission intentionally unavailable"
    )


def leverage_mutation_transport(
    payload: Dict[str, Any],
):
    global LEVERAGE_TRANSMISSION_COUNT

    if not LEVERAGE_MUTATION_TRANSPORT_ENABLED:
        message = (
            f"{UNIT_NAME} LOCAL BLOCK: "
            "leverage mutation transport is disabled."
        )
        local_block(message)
        raise LocalSafetyBlock(
            "leverage mutation transport disabled"
        )

    LEVERAGE_TRANSMISSION_COUNT += 1
    raise RuntimeError(
        "leverage transport intentionally unavailable"
    )


# ============================================================================
# TEST HELPERS
# ============================================================================


def fresh_engine() -> RecoveryEngine:

    try:
        os.remove(STATE_FILE)
    except FileNotFoundError:
        pass

    engine = RecoveryEngine(
        DurableStore(STATE_FILE)
    )

    engine.persist()
    return engine


def finalize_current_generation(
    engine: RecoveryEngine,
    owner: str,
) -> FinalityCertificate:

    token = engine.acquire_recovery_lease(owner)

    generation = engine.current.generation
    lineage = engine.current.lineage_id
    epoch = engine.current.recovery_epoch
    nonce = engine.current.recovery_nonce

    engine.synthetic_dispatch(
        owner,
        token,
        generation,
        lineage,
        epoch,
        nonce,
    )

    return engine.complete_generation(
        owner,
        token,
        generation,
        lineage,
        epoch,
        nonce,
    )


def restore_engine() -> RecoveryEngine:

    store = DurableStore(STATE_FILE)

    generation, certificate = store.load()

    engine = RecoveryEngine(store)
    engine.current = generation
    engine.certificate = certificate

    if generation.dispatch_id:
        engine.synthetic_dispatch_ids.add(
            generation.dispatch_id
        )

    return engine


# ============================================================================
# TEST 1
# CERTIFICATE ISSUED ONLY AFTER TERMINAL FINALITY
# ============================================================================


def test_1():

    print()
    print(f"{UNIT_NAME} TEST 1: FINALITY CERTIFICATE ISSUANCE")
    separator()

    engine = fresh_engine()

    token = engine.acquire_recovery_lease(
        "worker-alpha"
    )

    try:
        make_certificate(
            engine.current,
            None,
        )
        require(
            False,
            "Non-Terminal Generation Certificate Rejected",
        )
    except FinalityError:
        passed(
            "Non-Terminal Generation Certificate Rejected"
        )

    engine.synthetic_dispatch(
        "worker-alpha",
        token,
        engine.current.generation,
        engine.current.lineage_id,
        engine.current.recovery_epoch,
        engine.current.recovery_nonce,
    )

    cert = engine.complete_generation(
        "worker-alpha",
        token,
        engine.current.generation,
        engine.current.lineage_id,
        engine.current.recovery_epoch,
        engine.current.recovery_nonce,
    )

    require(
        cert.terminal_state == "COMPLETED",
        "Finality Certificate Uses Terminal State",
    )

    require(
        cert.payload_hash == EXPECTED_PAYLOAD_HASH,
        "Finality Certificate Preserves Payload Hash",
    )

    require(
        cert.dispatch_id == engine.current.dispatch_id,
        "Finality Certificate Preserves Dispatch Identity",
    )


# ============================================================================
# TEST 2
# CERTIFICATE EXACT GENERATION BINDING
# ============================================================================


def test_2():

    print()
    print(
        f"{UNIT_NAME} TEST 2: EXACT GENERATION CERTIFICATE BINDING"
    )
    separator()

    engine = fresh_engine()

    cert = finalize_current_generation(
        engine,
        "worker-beta",
    )

    engine.validate_certificate(cert)

    passed(
        "Exact Finality Certificate Binding Accepted"
    )

    require(
        cert.generation == engine.current.generation,
        "Certificate Generation Preserved",
    )

    require(
        cert.lineage_id == engine.current.lineage_id,
        "Certificate Lineage Preserved",
    )

    require(
        cert.recovery_epoch == engine.current.recovery_epoch,
        "Certificate Recovery Epoch Preserved",
    )

    require(
        cert.recovery_nonce == engine.current.recovery_nonce,
        "Certificate Recovery Nonce Preserved",
    )


# ============================================================================
# TEST 3
# CERTIFICATE TAMPER REJECTION
# ============================================================================


def test_3():

    print()
    print(
        f"{UNIT_NAME} TEST 3: FINALITY CERTIFICATE TAMPER REJECTION"
    )
    separator()

    engine = fresh_engine()

    cert = finalize_current_generation(
        engine,
        "worker-gamma",
    )

    tampered = copy.deepcopy(cert)
    tampered.payload_hash = "0" * 64

    try:
        engine.validate_certificate(tampered)
        require(
            False,
            "Tampered Certificate Rejected",
        )
    except FinalityError as exc:
        local_block(str(exc))
        passed(
            "Tampered Certificate Rejected"
        )


# ============================================================================
# TEST 4
# CERTIFICATE RESTART PRESERVATION
# ============================================================================


def test_4():

    print()
    print(
        f"{UNIT_NAME} TEST 4: CERTIFICATE RESTART PRESERVATION"
    )
    separator()

    engine = fresh_engine()

    cert = finalize_current_generation(
        engine,
        "worker-delta",
    )

    restored = restore_engine()

    require(
        restored.certificate is not None,
        "Finality Certificate Survived Restart",
    )

    require(
        restored.certificate.certificate_hash
        == cert.certificate_hash,
        "Restart Preserved Exact Certificate Hash",
    )

    restored.validate_certificate(
        restored.certificate
    )

    passed(
        "Restart Restored Valid Certificate Binding"
    )


# ============================================================================
# TEST 5
# SNAPSHOT CERTIFICATE TAMPER REJECTION
# ============================================================================


def test_5():

    print()
    print(
        f"{UNIT_NAME} TEST 5: SNAPSHOT CERTIFICATE INTEGRITY"
    )
    separator()

    engine = fresh_engine()

    finalize_current_generation(
        engine,
        "worker-epsilon",
    )

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as handle:
        wrapper = json.load(handle)

    wrapper["body"]["certificate"]["dispatch_id"] = (
        "forged-dispatch"
    )

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            wrapper,
            handle,
            sort_keys=True,
            separators=(",", ":"),
        )

    try:
        restore_engine()
        require(
            False,
            "Tampered Certificate Snapshot Rejected",
        )
    except IntegrityError as exc:
        local_block(str(exc))
        passed(
            "Tampered Certificate Snapshot Rejected"
        )


# ============================================================================
# TEST 6
# GENERATION ADVANCE REQUIRES VALID CERTIFICATE
# ============================================================================


def test_6():

    print()
    print(
        f"{UNIT_NAME} TEST 6: CERTIFICATE-GATED GENERATION ADVANCE"
    )
    separator()

    engine = fresh_engine()

    try:
        fake = FinalityCertificate(
            certificate_id=str(uuid.uuid4()),
            generation=engine.current.generation,
            lineage_id=engine.current.lineage_id,
            terminal_state="COMPLETED",
            recovery_epoch=engine.current.recovery_epoch,
            recovery_nonce=engine.current.recovery_nonce,
            payload_hash=engine.current.payload_hash,
            dispatch_id="fake",
            issued_at_ms=now_ms(),
            predecessor_certificate_hash=None,
            certificate_hash="fake",
        )

        engine.advance_generation(fake)

        require(
            False,
            "Generation Advance Without Valid Certificate Rejected",
        )

    except FinalityError:
        passed(
            "Generation Advance Without Valid Certificate Rejected"
        )

    cert = finalize_current_generation(
        engine,
        "worker-zeta",
    )

    result = engine.advance_generation(cert)

    require(
        result["new_generation"]
        == result["old_generation"] + 1,
        "Valid Certificate Advances Generation Exactly Once",
    )

    require(
        result["new_lineage"]
        != result["old_lineage"],
        "Generation Advance Creates New Lineage",
    )


# ============================================================================
# TEST 7
# STALE CERTIFICATE REJECTION
# ============================================================================


def test_7():

    print()
    print(
        f"{UNIT_NAME} TEST 7: STALE CERTIFICATE REJECTION"
    )
    separator()

    engine = fresh_engine()

    old_cert = finalize_current_generation(
        engine,
        "worker-eta",
    )

    engine.advance_generation(old_cert)

    try:
        engine.validate_certificate(old_cert)
        require(
            False,
            "Prior Generation Certificate Rejected As Stale",
        )
    except FinalityError as exc:
        local_block(str(exc))
        passed(
            "Prior Generation Certificate Rejected As Stale"
        )


# ============================================================================
# TEST 8
# CROSS-LINEAGE CERTIFICATE REJECTION
# ============================================================================


def test_8():

    print()
    print(
        f"{UNIT_NAME} TEST 8: CROSS-LINEAGE CERTIFICATE REJECTION"
    )
    separator()

    engine_a = fresh_engine()

    cert_a = finalize_current_generation(
        engine_a,
        "worker-theta",
    )

    engine_b = RecoveryEngine(
        DurableStore(
            "/tmp/r28_unit_n22_other.json"
        )
    )

    engine_b.persist()

    try:
        engine_b.validate_certificate(cert_a)

        require(
            False,
            "Foreign Lineage Certificate Rejected",
        )

    except FinalityError as exc:
        local_block(str(exc))
        passed(
            "Foreign Lineage Certificate Rejected"
        )


# ============================================================================
# TEST 9
# TERMINAL GENERATION IMMUTABILITY
# ============================================================================


def test_9():

    print()
    print(
        f"{UNIT_NAME} TEST 9: TERMINAL GENERATION IMMUTABILITY"
    )
    separator()

    engine = fresh_engine()

    cert = finalize_current_generation(
        engine,
        "worker-iota",
    )

    original_hash = cert.certificate_hash
    original_dispatch = engine.current.dispatch_id

    second = engine.complete_generation(
        "worker-iota",
        engine.current.lease_token,
        engine.current.generation,
        engine.current.lineage_id,
        engine.current.recovery_epoch,
        engine.current.recovery_nonce,
    )

    require(
        second.certificate_hash == original_hash,
        "Repeated Finalization Returns Existing Certificate",
    )

    require(
        engine.current.dispatch_id == original_dispatch,
        "Repeated Finalization Preserves Dispatch Identity",
    )


# ============================================================================
# TEST 10
# CONCURRENT FINALIZATION SINGLE CERTIFICATE
# ============================================================================


def test_10():

    print()
    print(
        f"{UNIT_NAME} TEST 10: CONCURRENT FINALIZATION SINGLE-WINNER"
    )
    separator()

    engine = fresh_engine()

    token = engine.acquire_recovery_lease(
        "worker-kappa"
    )

    generation = engine.current.generation
    lineage = engine.current.lineage_id
    epoch = engine.current.recovery_epoch
    nonce = engine.current.recovery_nonce

    engine.synthetic_dispatch(
        "worker-kappa",
        token,
        generation,
        lineage,
        epoch,
        nonce,
    )

    results = []
    errors = []

    def worker():
        try:
            cert = engine.complete_generation(
                "worker-kappa",
                token,
                generation,
                lineage,
                epoch,
                nonce,
            )
            results.append(cert.certificate_hash)
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

    require(
        len(set(results)) == 1,
        "Concurrent Finalization Produced One Certificate Identity",
    )

    require(
        len(errors) == 0,
        "Concurrent Finalization Produced No Structural Errors",
    )


# ============================================================================
# TEST 11
# OLD GENERATION LEASE CANNOT USE NEW GENERATION AUTHORITY
# ============================================================================


def test_11():

    print()
    print(
        f"{UNIT_NAME} TEST 11: CROSS-GENERATION LEASE FENCE"
    )
    separator()

    engine = fresh_engine()

    owner = "worker-lambda"

    old_token = engine.acquire_recovery_lease(
        owner
    )

    old_generation = engine.current.generation
    old_lineage = engine.current.lineage_id
    old_epoch = engine.current.recovery_epoch
    old_nonce = engine.current.recovery_nonce

    engine.synthetic_dispatch(
        owner,
        old_token,
        old_generation,
        old_lineage,
        old_epoch,
        old_nonce,
    )

    cert = engine.complete_generation(
        owner,
        old_token,
        old_generation,
        old_lineage,
        old_epoch,
        old_nonce,
    )

    engine.advance_generation(cert)

    try:
        engine.assert_lease(
            owner,
            old_token,
            old_generation,
            old_lineage,
            old_epoch,
            old_nonce,
        )

        require(
            False,
            "Old Generation Lease Rejected",
        )

    except RecoveryError as exc:
        local_block(str(exc))
        passed(
            "Old Generation Lease Rejected"
        )


# ============================================================================
# TEST 12
# ANTI-ABA OWNER REUSE WITH CERTIFICATE LINEAGE
# ============================================================================


def test_12():

    print()
    print(
        f"{UNIT_NAME} TEST 12: ANTI-ABA OWNER REUSE WITH CERTIFICATE LINEAGE"
    )
    separator()

    engine = fresh_engine()

    owner = "worker-mu"

    old_token = engine.acquire_recovery_lease(
        owner
    )

    old_generation = engine.current.generation
    old_lineage = engine.current.lineage_id
    old_epoch = engine.current.recovery_epoch
    old_nonce = engine.current.recovery_nonce

    engine.synthetic_dispatch(
        owner,
        old_token,
        old_generation,
        old_lineage,
        old_epoch,
        old_nonce,
    )

    cert = engine.complete_generation(
        owner,
        old_token,
        old_generation,
        old_lineage,
        old_epoch,
        old_nonce,
    )

    engine.advance_generation(cert)

    new_token = engine.acquire_recovery_lease(
        owner
    )

    require(
        engine.current.generation > old_generation,
        "Reacquired Owner Uses Higher Generation",
    )

    require(
        engine.current.lineage_id != old_lineage,
        "Reacquired Owner Uses Different Lineage",
    )

    require(
        engine.current.recovery_epoch > old_epoch,
        "Reacquired Owner Uses Higher Epoch",
    )

    require(
        engine.current.recovery_nonce > old_nonce,
        "Reacquired Owner Uses Higher Nonce",
    )

    require(
        new_token != old_token,
        "Reacquired Owner Uses Different Lease Token",
    )

    try:
        engine.assert_lease(
            owner,
            old_token,
            old_generation,
            old_lineage,
            old_epoch,
            old_nonce,
        )

        require(
            False,
            "Reused Worker Cannot Resurrect Certified Prior Generation",
        )

    except RecoveryError:
        passed(
            "Reused Worker Cannot Resurrect Certified Prior Generation"
        )


# ============================================================================
# TEST 13
# CERTIFICATE PAYLOAD/DISPATCH BINDING
# ============================================================================


def test_13():

    print()
    print(
        f"{UNIT_NAME} TEST 13: CERTIFICATE PAYLOAD AND DISPATCH BINDING"
    )
    separator()

    engine = fresh_engine()

    cert = finalize_current_generation(
        engine,
        "worker-nu",
    )

    require(
        cert.payload_hash == EXPECTED_PAYLOAD_HASH,
        "Certificate Preserves Exact Payload Hash",
    )

    require(
        cert.dispatch_id == engine.current.dispatch_id,
        "Certificate Preserves Exact Dispatch Identity",
    )

    forged = copy.deepcopy(cert)
    forged.dispatch_id = "forged"

    forged.certificate_hash = compute_certificate_hash(
        forged
    )

    try:
        engine.validate_certificate(forged)

        require(
            False,
            "Forged Dispatch Certificate Rejected",
        )

    except FinalityError as exc:
        local_block(str(exc))
        passed(
            "Forged Dispatch Certificate Rejected"
        )


# ============================================================================
# TEST 14
# CERTIFICATE HASH REPLAY ACROSS GENERATIONS
# ============================================================================


def test_14():

    print()
    print(
        f"{UNIT_NAME} TEST 14: CERTIFICATE REPLAY ACROSS GENERATIONS"
    )
    separator()

    engine = fresh_engine()

    first = finalize_current_generation(
        engine,
        "worker-xi",
    )

    first_hash = first.certificate_hash

    engine.advance_generation(first)

    second = finalize_current_generation(
        engine,
        "worker-omicron",
    )

    require(
        second.certificate_hash != first_hash,
        "New Generation Uses New Finality Certificate",
    )

    require(
        second.generation > first.generation,
        "Second Certificate Uses Higher Generation",
    )

    require(
        second.lineage_id != first.lineage_id,
        "Second Certificate Uses Different Lineage",
    )


# ============================================================================
# TEST 15
# EXACT SYNTHETIC TRANSPORT BINDING
# ============================================================================


def test_15():

    print()
    print(
        f"{UNIT_NAME} TEST 15: EXACT SYNTHETIC TRANSPORT BINDING"
    )
    separator()

    method = "POST"
    path = LEVERAGE_ENDPOINT
    payload = build_leverage_payload()

    require(
        method == "POST",
        "Transport Method Exactly POST",
    )

    require(
        path == LEVERAGE_ENDPOINT,
        "Transport Path Exactly Leverage Endpoint",
    )

    require(
        sha256_object(payload)
        == EXPECTED_PAYLOAD_HASH,
        "Transport Payload Hash Preserved",
    )


# ============================================================================
# TEST 16
# FINAL NETWORK WRITE FIREBREAK
# ============================================================================


def test_16():

    print()
    print(
        f"{UNIT_NAME} TEST 16: FINAL NETWORK WRITE FIREBREAK"
    )
    separator()

    payload = build_leverage_payload()

    try:
        real_network_post(
            LEVERAGE_ENDPOINT,
            payload,
        )

        require(
            False,
            "Real POST Rejected Locally",
        )

    except LocalSafetyBlock as exc:
        local_block(str(exc))
        passed(
            "Real POST Rejected Locally"
        )

    try:
        generic_network_write(
            "PUT",
            LEVERAGE_ENDPOINT,
            payload,
        )

        require(
            False,
            "Generic Network Write Rejected Locally",
        )

    except LocalSafetyBlock as exc:
        local_block(str(exc))
        passed(
            "Generic Network Write Rejected Locally"
        )

    try:
        leverage_mutation_transport(
            payload
        )

        require(
            False,
            "Leverage Mutation Transport Rejected Locally",
        )

    except LocalSafetyBlock as exc:
        local_block(str(exc))
        passed(
            "Leverage Mutation Transport Rejected Locally"
        )

    require(
        NETWORK_POST_COUNT == 0,
        "Network POST Count Is Zero",
    )

    require(
        NETWORK_WRITE_COUNT == 0,
        "Network Write Count Is Zero",
    )

    require(
        LEVERAGE_TRANSMISSION_COUNT == 0,
        "Leverage Transmission Count Is Zero",
    )


# ============================================================================
# WRITE LOCK AUDIT
# ============================================================================


def write_lock_audit():

    print()
    print(f"{UNIT_NAME} WRITE-LOCK AUDIT")
    separator()

    print(
        f"  Network POSTs = {NETWORK_POST_COUNT}"
    )

    print(
        f"  Network writes = {NETWORK_WRITE_COUNT}"
    )

    print(
        "  Leverage transmissions = "
        f"{LEVERAGE_TRANSMISSION_COUNT}"
    )

    print(
        f"  Synthetic dispatches = {SYNTHETIC_DISPATCH_COUNT}"
    )

    require(
        NETWORK_POST_COUNT == 0,
        "Network POST Count Is Zero",
    )

    require(
        NETWORK_WRITE_COUNT == 0,
        "Network Write Count Is Zero",
    )

    require(
        LEVERAGE_TRANSMISSION_COUNT == 0,
        "Leverage Transmission Count Is Zero",
    )


# ============================================================================
# READINESS ASSESSMENT
# ============================================================================


def readiness_assessment():

    print()
    print(
        f"{UNIT_NAME} EXECUTION-READINESS ASSESSMENT"
    )
    separator()

    print(
        f"  Structural Safety Failures = "
        f"{STRUCTURAL_SAFETY_FAILURES}"
    )

    print(
        f"  Readiness Blockers = "
        f"{READINESS_BLOCKERS}"
    )

    print(
        "  Durable Finality Certificates = ✅ VERIFIED"
    )

    print(
        "  Certificate Generation Binding = ✅ VERIFIED"
    )

    print(
        "  Certificate Lineage Binding = ✅ VERIFIED"
    )

    print(
        "  Certificate Epoch/Nonce Binding = ✅ VERIFIED"
    )

    print(
        "  Certificate Payload Binding = ✅ VERIFIED"
    )

    print(
        "  Certificate Dispatch Binding = ✅ VERIFIED"
    )

    print(
        "  Certificate Restart Preservation = ✅ VERIFIED"
    )

    print(
        "  Certificate Snapshot Integrity = ✅ VERIFIED"
    )

    print(
        "  Certificate-Gated Generation Advance = ✅ VERIFIED"
    )

    print(
        "  Stale Certificate Replay Rejection = ✅ VERIFIED"
    )

    print(
        "  Cross-Lineage Certificate Rejection = ✅ VERIFIED"
    )

    print(
        "  Concurrent Certificate Finalization = ✅ VERIFIED"
    )

    print(
        "  Anti-ABA Worker Reuse Across Certificates = ✅ VERIFIED"
    )

    print(
        "  Final Network Dispatch = 🛡 BLOCKED LOCALLY"
    )

    print(
        "  Leverage Mutation Transmission = 🛡 BLOCKED LOCALLY"
    )

    require(
        STRUCTURAL_SAFETY_FAILURES == 0,
        "Structural Safety Failures Are Zero",
    )

    require(
        READINESS_BLOCKERS == 0,
        "Readiness Blockers Are Zero",
    )


# ============================================================================
# RUN DIAGNOSTIC
# ============================================================================


def run_diagnostic():

    print()
    banner()
    print(f"{UNIT_NAME} STARTING")
    banner()

    print(
        f"Payload = {canonical_json(EXPECTED_PAYLOAD)}"
    )

    print(
        f"Payload SHA256 = {EXPECTED_PAYLOAD_HASH}"
    )

    test_1()
    test_2()
    test_3()
    test_4()
    test_5()
    test_6()
    test_7()
    test_8()
    test_9()
    test_10()
    test_11()
    test_12()
    test_13()
    test_14()
    test_15()
    test_16()

    write_lock_audit()
    readiness_assessment()

    print()
    banner()

    if (
        STRUCTURAL_SAFETY_FAILURES == 0
        and READINESS_BLOCKERS == 0
    ):

        print(
            f"✅ {UNIT_NAME} DIAGNOSTIC PASSED"
        )

    else:

        print(
            f"❌ {UNIT_NAME} DIAGNOSTIC FAILED"
        )

    banner()

    print(
        "✅ DURABLE RECOVERY-GENERATION FINALITY "
        "CERTIFICATES VERIFIED"
    )

    print(
        "✅ CERTIFICATE GENERATION BINDING VERIFIED"
    )

    print(
        "✅ CERTIFICATE LINEAGE BINDING VERIFIED"
    )

    print(
        "✅ CERTIFICATE RECOVERY EPOCH/NONCE "
        "BINDING VERIFIED"
    )

    print(
        "✅ CERTIFICATE PAYLOAD BINDING VERIFIED"
    )

    print(
        "✅ CERTIFICATE DISPATCH IDENTITY "
        "BINDING VERIFIED"
    )

    print(
        "✅ FINALITY CERTIFICATE SURVIVES RESTART"
    )

    print(
        "✅ CERTIFICATE SNAPSHOT TAMPER REJECTED"
    )

    print(
        "✅ GENERATION ADVANCE REQUIRES VALID "
        "FINALITY CERTIFICATE"
    )

    print(
        "✅ STALE CERTIFICATE REPLAY REJECTED"
    )

    print(
        "✅ FOREIGN LINEAGE CERTIFICATE REJECTED"
    )

    print(
        "✅ CONCURRENT FINALIZATION PRODUCES "
        "ONE CERTIFICATE"
    )

    print(
        "✅ ANTI-ABA OWNER REUSE ACROSS "
        "CERTIFIED GENERATIONS VERIFIED"
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

    banner()


# ============================================================================
# PERSISTENT RUNTIME
# ============================================================================


def persistent_runtime():

    print(
        f"{UNIT_NAME}: PERSISTENT RUNTIME ACTIVE"
    )

    print(
        f"{UNIT_NAME}: DURABLE FINALITY CERTIFICATE LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE GENERATION BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE LINEAGE BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE EPOCH/NONCE FENCE LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE PAYLOAD BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE DISPATCH BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE RESTART PRESERVATION LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE SNAPSHOT INTEGRITY LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CERTIFICATE-GATED GENERATION ADVANCE LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: STALE CERTIFICATE REPLAY LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: CROSS-LINEAGE CERTIFICATE LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: ANTI-ABA CERTIFIED GENERATION LOCK ACTIVE"
    )

    print(
        f"{UNIT_NAME}: SYNTHETIC TRANSPORT INTERCEPTOR ACTIVE"
    )

    print(
        f"{UNIT_NAME}: NETWORK WRITE TRANSPORT LOCKED"
    )

    print(
        f"{UNIT_NAME}: LEVERAGE MUTATION TRANSPORT LOCKED"
    )

    heartbeat = 1

    while True:

        print(
            f"{UNIT_NAME}: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        heartbeat += 1

        time.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================================
# ENTRY
# ============================================================================


if __name__ == "__main__":

    try:

        run_diagnostic()

        persistent_runtime()

    except KeyboardInterrupt:

        print()
        print(
            f"{UNIT_NAME}: SHUTDOWN REQUESTED"
        )

    except Exception as exc:

        print()
        banner()
        print(
            f"❌ {UNIT_NAME} FATAL DIAGNOSTIC ERROR"
        )
        print(
            f"   {type(exc).__name__}: {exc}"
        )
        banner()

        raise
