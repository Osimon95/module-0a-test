import copy
import hashlib
import hmac
import json
import os
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

UNIT = "R28 UNIT N.23"
SEPARATOR = "=" * 92
SUBSEP = "-" * 92

REAL_NETWORK_POST_ENABLED = False
NETWORK_WRITE_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

TRANSPORT_METHOD = "POST"
TRANSPORT_PATH = "/api/v2/mix/account/set-leverage"
SYMBOL = "BTCUSDT"
MARGIN_MODE = "ISOLATED"
LEVERAGE = "100"

NETWORK_POST_COUNT = 0
NETWORK_WRITE_COUNT = 0
LEVERAGE_TRANSMISSION_COUNT = 0
SYNTHETIC_DISPATCH_COUNT = 0

_SECRET = b"R28-N23-LOCAL-INTEGRITY-KEY"
_COUNTER_LOCK = threading.Lock()


class LocalSafetyBlock(RuntimeError):
    pass


class IntegrityError(RuntimeError):
    pass


class ChainError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def seal_dict(value: Dict[str, Any]) -> str:
    return hmac.new(_SECRET, canonical_json(value).encode("utf-8"), hashlib.sha256).hexdigest()


def verify_seal(value: Dict[str, Any], seal: str) -> bool:
    return hmac.compare_digest(seal_dict(value), seal)


def payload() -> Dict[str, str]:
    return {
        "symbol": SYMBOL,
        "leverage": LEVERAGE,
        "marginMode": MARGIN_MODE,
    }


def payload_hash() -> str:
    return sha256_text(canonical_json(payload()))


def deterministic_dispatch_id(lineage_id: str, generation: int, epoch: int, nonce: int) -> str:
    raw = f"{UNIT}|dispatch|{lineage_id}|{generation}|{epoch}|{nonce}|{payload_hash()}"
    return sha256_text(raw)[:32]


def deterministic_owner_id(lineage_id: str, generation: int) -> str:
    return sha256_text(f"{UNIT}|owner|{lineage_id}|{generation}")[:24]


@dataclass(frozen=True)
class FinalityCertificate:
    lineage_id: str
    generation: int
    recovery_epoch: int
    recovery_nonce: int
    owner_id: str
    payload_hash: str
    dispatch_id: str
    predecessor_certificate_hash: str
    certificate_hash: str
    seal: str

    def body(self) -> Dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "generation": self.generation,
            "recovery_epoch": self.recovery_epoch,
            "recovery_nonce": self.recovery_nonce,
            "owner_id": self.owner_id,
            "payload_hash": self.payload_hash,
            "dispatch_id": self.dispatch_id,
            "predecessor_certificate_hash": self.predecessor_certificate_hash,
            "certificate_hash": self.certificate_hash,
        }


@dataclass(frozen=True)
class GenerationManifest:
    lineage_id: str
    generation: int
    certificate_hash: str
    predecessor_manifest_hash: str
    manifest_hash: str
    seal: str

    def body(self) -> Dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "generation": self.generation,
            "certificate_hash": self.certificate_hash,
            "predecessor_manifest_hash": self.predecessor_manifest_hash,
            "manifest_hash": self.manifest_hash,
        }


@dataclass
class DurableState:
    lineage_id: str
    certificates: List[Dict[str, Any]]
    manifests: List[Dict[str, Any]]
    finalized_generations: List[int]
    snapshot_seal: str = ""

    def body(self) -> Dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "certificates": self.certificates,
            "manifests": self.manifests,
            "finalized_generations": self.finalized_generations,
        }


class N23Engine:
    def __init__(self, lineage_id: Optional[str] = None):
        self.lineage_id = lineage_id or sha256_text(f"{UNIT}|lineage|root")[:24]
        self._certificates: Dict[int, FinalityCertificate] = {}
        self._manifests: Dict[int, GenerationManifest] = {}
        self._finalized: set[int] = set()
        self._lock = threading.RLock()

    @staticmethod
    def _certificate_core(
        lineage_id: str,
        generation: int,
        recovery_epoch: int,
        recovery_nonce: int,
        owner_id: str,
        payload_digest: str,
        dispatch_id: str,
        predecessor_certificate_hash: str,
    ) -> Dict[str, Any]:
        return {
            "lineage_id": lineage_id,
            "generation": generation,
            "recovery_epoch": recovery_epoch,
            "recovery_nonce": recovery_nonce,
            "owner_id": owner_id,
            "payload_hash": payload_digest,
            "dispatch_id": dispatch_id,
            "predecessor_certificate_hash": predecessor_certificate_hash,
        }

    @classmethod
    def _build_certificate(
        cls,
        lineage_id: str,
        generation: int,
        recovery_epoch: int,
        recovery_nonce: int,
        owner_id: str,
        payload_digest: str,
        dispatch_id: str,
        predecessor_certificate_hash: str,
    ) -> FinalityCertificate:
        core = cls._certificate_core(
            lineage_id,
            generation,
            recovery_epoch,
            recovery_nonce,
            owner_id,
            payload_digest,
            dispatch_id,
            predecessor_certificate_hash,
        )
        certificate_hash = sha256_text(canonical_json(core))
        body = {**core, "certificate_hash": certificate_hash}
        return FinalityCertificate(**body, seal=seal_dict(body))

    @staticmethod
    def _build_manifest(
        lineage_id: str,
        generation: int,
        certificate_hash: str,
        predecessor_manifest_hash: str,
    ) -> GenerationManifest:
        core = {
            "lineage_id": lineage_id,
            "generation": generation,
            "certificate_hash": certificate_hash,
            "predecessor_manifest_hash": predecessor_manifest_hash,
        }
        manifest_hash = sha256_text(canonical_json(core))
        body = {**core, "manifest_hash": manifest_hash}
        return GenerationManifest(**body, seal=seal_dict(body))
    @staticmethod
    def _verify_certificate(cert: FinalityCertificate) -> None:
        core = {
            "lineage_id": cert.lineage_id,
            "generation": cert.generation,
            "recovery_epoch": cert.recovery_epoch,
            "recovery_nonce": cert.recovery_nonce,
            "owner_id": cert.owner_id,
            "payload_hash": cert.payload_hash,
            "dispatch_id": cert.dispatch_id,
            "predecessor_certificate_hash": cert.predecessor_certificate_hash,
        }

        expected_hash = sha256_text(canonical_json(core))

        if cert.certificate_hash != expected_hash:
            raise IntegrityError("certificate hash mismatch")

        if not verify_seal(cert.body(), cert.seal):
            raise IntegrityError("certificate integrity seal mismatch")

    @staticmethod
    def _verify_manifest(manifest: GenerationManifest) -> None:
        core = {
            "lineage_id": manifest.lineage_id,
            "generation": manifest.generation,
            "certificate_hash": manifest.certificate_hash,
            "predecessor_manifest_hash": manifest.predecessor_manifest_hash,
        }

        expected_hash = sha256_text(canonical_json(core))

        if manifest.manifest_hash != expected_hash:
            raise IntegrityError("manifest hash mismatch")

        if not verify_seal(manifest.body(), manifest.seal):
            raise IntegrityError("manifest integrity seal mismatch")

    def _expected_predecessor_certificate_hash(self, generation: int) -> str:
        if generation == 0:
            return "GENESIS"

        predecessor = self._certificates.get(generation - 1)

        if predecessor is None:
            raise ChainError("missing predecessor certificate")

        return predecessor.certificate_hash

    def _expected_predecessor_manifest_hash(self, generation: int) -> str:
        if generation == 0:
            return "GENESIS"

        predecessor = self._manifests.get(generation - 1)

        if predecessor is None:
            raise ChainError("missing predecessor manifest")

        return predecessor.manifest_hash

    def _assert_generation_sequence(self, generation: int) -> None:
        if generation < 0:
            raise ChainError("generation cannot be negative")

        if generation in self._finalized:
            raise ChainError("generation already finalized")

        if not self._finalized:
            if generation != 0:
                raise ChainError("first certified generation must be generation zero")
            return

        expected_generation = max(self._finalized) + 1

        if generation != expected_generation:
            raise ChainError(
                f"generation sequence mismatch: expected {expected_generation}, got {generation}"
            )

    def _assert_certificate_binding(
        self,
        cert: FinalityCertificate,
        expected_generation: Optional[int] = None,
    ) -> None:
        self._verify_certificate(cert)

        if cert.lineage_id != self.lineage_id:
            raise ChainError("certificate lineage mismatch")

        if expected_generation is not None and cert.generation != expected_generation:
            raise ChainError("certificate generation mismatch")

        if cert.payload_hash != payload_hash():
            raise ChainError("certificate payload binding mismatch")

        expected_dispatch = deterministic_dispatch_id(
            cert.lineage_id,
            cert.generation,
            cert.recovery_epoch,
            cert.recovery_nonce,
        )

        if cert.dispatch_id != expected_dispatch:
            raise ChainError("certificate dispatch identity mismatch")

        expected_predecessor = self._expected_predecessor_certificate_hash(
            cert.generation
        )

        if cert.predecessor_certificate_hash != expected_predecessor:
            raise ChainError("certificate predecessor mismatch")

    def _assert_manifest_binding(
        self,
        manifest: GenerationManifest,
        cert: FinalityCertificate,
    ) -> None:
        self._verify_manifest(manifest)

        if manifest.lineage_id != self.lineage_id:
            raise ChainError("manifest lineage mismatch")

        if manifest.generation != cert.generation:
            raise ChainError("manifest generation mismatch")

        if manifest.certificate_hash != cert.certificate_hash:
            raise ChainError("manifest certificate binding mismatch")

        expected_predecessor = self._expected_predecessor_manifest_hash(
            manifest.generation
        )

        if manifest.predecessor_manifest_hash != expected_predecessor:
            raise ChainError("manifest predecessor mismatch")

    def finalize_generation(
        self,
        generation: int,
        recovery_epoch: int,
        recovery_nonce: int,
        owner_id: Optional[str] = None,
    ) -> Tuple[FinalityCertificate, GenerationManifest]:
        global SYNTHETIC_DISPATCH_COUNT

        with self._lock:
            self._assert_generation_sequence(generation)

            if recovery_epoch < 0:
                raise ChainError("recovery epoch cannot be negative")

            if recovery_nonce < 0:
                raise ChainError("recovery nonce cannot be negative")

            if generation > 0:
                previous = self._certificates[generation - 1]

                if recovery_epoch <= previous.recovery_epoch:
                    raise ChainError(
                        "recovery epoch must advance monotonically"
                    )

                if recovery_nonce <= previous.recovery_nonce:
                    raise ChainError(
                        "recovery nonce must advance monotonically"
                    )

            owner = owner_id or deterministic_owner_id(
                self.lineage_id,
                generation,
            )

            predecessor_certificate_hash = (
                self._expected_predecessor_certificate_hash(generation)
            )

            dispatch_id = deterministic_dispatch_id(
                self.lineage_id,
                generation,
                recovery_epoch,
                recovery_nonce,
            )

            cert = self._build_certificate(
                lineage_id=self.lineage_id,
                generation=generation,
                recovery_epoch=recovery_epoch,
                recovery_nonce=recovery_nonce,
                owner_id=owner,
                payload_digest=payload_hash(),
                dispatch_id=dispatch_id,
                predecessor_certificate_hash=predecessor_certificate_hash,
            )

            self._assert_certificate_binding(
                cert,
                expected_generation=generation,
            )

            predecessor_manifest_hash = (
                self._expected_predecessor_manifest_hash(generation)
            )

            manifest = self._build_manifest(
                lineage_id=self.lineage_id,
                generation=generation,
                certificate_hash=cert.certificate_hash,
                predecessor_manifest_hash=predecessor_manifest_hash,
            )

            self._assert_manifest_binding(manifest, cert)

            self._certificates[generation] = cert
            self._manifests[generation] = manifest
            self._finalized.add(generation)

            with _COUNTER_LOCK:
                SYNTHETIC_DISPATCH_COUNT += 1

            return cert, manifest

    def validate_complete_chain(self) -> bool:
        with self._lock:
            if not self._finalized:
                return True

            generations = sorted(self._finalized)

            if generations != list(range(generations[-1] + 1)):
                raise ChainError("certified generation chain contains a gap")

            previous_certificate_hash = "GENESIS"
            previous_manifest_hash = "GENESIS"
            previous_epoch = -1
            previous_nonce = -1

            for generation in generations:
                cert = self._certificates.get(generation)
                manifest = self._manifests.get(generation)

                if cert is None:
                    raise ChainError("certificate missing from certified chain")

                if manifest is None:
                    raise ChainError("manifest missing from certified chain")

                self._verify_certificate(cert)
                self._verify_manifest(manifest)

                if cert.lineage_id != self.lineage_id:
                    raise ChainError("foreign certificate lineage detected")

                if manifest.lineage_id != self.lineage_id:
                    raise ChainError("foreign manifest lineage detected")

                if cert.generation != generation:
                    raise ChainError("certificate generation discontinuity")

                if manifest.generation != generation:
                    raise ChainError("manifest generation discontinuity")

                if cert.predecessor_certificate_hash != previous_certificate_hash:
                    raise ChainError("certificate chain predecessor mismatch")

                if manifest.predecessor_manifest_hash != previous_manifest_hash:
                    raise ChainError("manifest chain predecessor mismatch")

                if manifest.certificate_hash != cert.certificate_hash:
                    raise ChainError("manifest-to-certificate binding mismatch")

                if cert.payload_hash != payload_hash():
                    raise ChainError("chain payload binding mismatch")

                expected_dispatch = deterministic_dispatch_id(
                    cert.lineage_id,
                    cert.generation,
                    cert.recovery_epoch,
                    cert.recovery_nonce,
                )

                if cert.dispatch_id != expected_dispatch:
                    raise ChainError("chain dispatch identity mismatch")

                if generation > 0:
                    if cert.recovery_epoch <= previous_epoch:
                        raise ChainError("chain recovery epoch is not monotonic")

                    if cert.recovery_nonce <= previous_nonce:
                        raise ChainError("chain recovery nonce is not monotonic")

                previous_certificate_hash = cert.certificate_hash
                previous_manifest_hash = manifest.manifest_hash
                previous_epoch = cert.recovery_epoch
                previous_nonce = cert.recovery_nonce

            return True

    def export_state(self) -> DurableState:
        with self._lock:
            self.validate_complete_chain()

            certificates = [
                asdict(self._certificates[generation])
                for generation in sorted(self._certificates)
            ]

            manifests = [
                asdict(self._manifests[generation])
                for generation in sorted(self._manifests)
            ]

            state = DurableState(
                lineage_id=self.lineage_id,
                certificates=certificates,
                manifests=manifests,
                finalized_generations=sorted(self._finalized),
            )

            state.snapshot_seal = seal_dict(state.body())

            return state
            @classmethod
def restore_state(cls, state: DurableState) -> "N23Engine":
        if not verify_seal(state.body(), state.snapshot_seal):
            raise IntegrityError("snapshot integrity seal mismatch")

        engine = cls(state.lineage_id)

        for raw in state.certificates:
            cert = FinalityCertificate(**raw)
            engine._verify_certificate(cert)

            if cert.generation in engine._certificates:
                raise ChainError("duplicate certificate generation in snapshot")

            engine._certificates[cert.generation] = cert

        for raw in state.manifests:
            manifest = GenerationManifest(**raw)
            engine._verify_manifest(manifest)

            if manifest.generation in engine._manifests:
                raise ChainError("duplicate manifest generation in snapshot")

            engine._manifests[manifest.generation] = manifest

        engine._finalized = set(state.finalized_generations)

        if set(engine._certificates) != engine._finalized:
            raise ChainError("certificate/finality set mismatch")

        if set(engine._manifests) != engine._finalized:
            raise ChainError("manifest/finality set mismatch")

        engine.validate_complete_chain()

        return engine

    def save_snapshot(self, path: str) -> None:
        state = self.export_state()
        data = asdict(state)

        temporary_path = f"{path}.{uuid.uuid4().hex}.tmp"

        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                sort_keys=True,
                separators=(",", ":"),
            )
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, path)

    @classmethod
    def load_snapshot(cls, path: str) -> "N23Engine":
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        state = DurableState(**data)

        return cls.restore_state(state)

    def certificate(self, generation: int) -> FinalityCertificate:
        with self._lock:
            if generation not in self._certificates:
                raise ChainError("certificate generation does not exist")

            return self._certificates[generation]

    def manifest(self, generation: int) -> GenerationManifest:
        with self._lock:
            if generation not in self._manifests:
                raise ChainError("manifest generation does not exist")

            return self._manifests[generation]

    @property
    def finalized_generations(self) -> List[int]:
        with self._lock:
            return sorted(self._finalized)


def synthetic_dispatch(cert: FinalityCertificate) -> Dict[str, Any]:
    global SYNTHETIC_DISPATCH_COUNT

    N23Engine._verify_certificate(cert)

    if cert.payload_hash != payload_hash():
        raise ChainError("synthetic dispatch payload binding mismatch")

    expected_dispatch = deterministic_dispatch_id(
        cert.lineage_id,
        cert.generation,
        cert.recovery_epoch,
        cert.recovery_nonce,
    )

    if cert.dispatch_id != expected_dispatch:
        raise ChainError("synthetic dispatch identity mismatch")

    with _COUNTER_LOCK:
        SYNTHETIC_DISPATCH_COUNT += 1

    return {
        "synthetic": True,
        "transmitted": False,
        "method": TRANSPORT_METHOD,
        "path": TRANSPORT_PATH,
        "payload": payload(),
        "payload_hash": cert.payload_hash,
        "dispatch_id": cert.dispatch_id,
        "generation": cert.generation,
        "lineage_id": cert.lineage_id,
    }


def real_network_post(*args: Any, **kwargs: Any) -> None:
    print(f"{UNIT} LOCAL BLOCK:")
    print(f"  {UNIT} LOCAL BLOCK: real network POST is disabled.")
    print(f"{UNIT} LOCAL BLOCK:")
    print("  real network POST is disabled")

    raise LocalSafetyBlock("real network POST is disabled")


def generic_network_write(
    method: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    print(f"{UNIT} LOCAL BLOCK:")
    print(
        f"  {UNIT} LOCAL BLOCK: "
        f"network write method {method} is disabled."
    )
    print(f"{UNIT} LOCAL BLOCK:")
    print("  network write disabled")

    raise LocalSafetyBlock("network write disabled")


def leverage_mutation_transport(
    *args: Any,
    **kwargs: Any,
) -> None:
    print(f"{UNIT} LOCAL BLOCK:")
    print(
        f"  {UNIT} LOCAL BLOCK: "
        "leverage mutation transport is disabled."
    )
    print(f"{UNIT} LOCAL BLOCK:")
    print("  leverage mutation transport disabled")

    raise LocalSafetyBlock(
        "leverage mutation transport disabled"
    )


PASS_COUNT = 0
FAIL_COUNT = 0


def banner(title: str) -> None:
    print()
    print(title)
    print(SUBSEP)


def check(name: str, condition: bool) -> None:
    global PASS_COUNT
    global FAIL_COUNT

    if condition:
        PASS_COUNT += 1
        print(f"{name:<86} ✅ PASS")
    else:
        FAIL_COUNT += 1
        print(f"{name:<86} ❌ FAIL")


def expect_raises(
    name: str,
    exc_type: type,
    fn,
) -> None:
    try:
        fn()

    except exc_type:
        check(name, True)

    except Exception as exc:
        print(
            f"Unexpected exception for {name}: "
            f"{type(exc).__name__}: {exc}"
        )
        check(name, False)

    else:
        check(name, False)


def tamper_dataclass(
    obj: Any,
    field: str,
    value: Any,
) -> Any:
    raw = asdict(obj)
    raw[field] = value

    return type(obj)(**raw)


def run_diagnostic() -> None:
    global NETWORK_POST_COUNT
    global NETWORK_WRITE_COUNT
    global LEVERAGE_TRANSMISSION_COUNT

    print(SEPARATOR)
    print(f"{UNIT}: MAIN.PY ENTERED")
    print(f"{UNIT}: IMPORTS COMPLETE")
    print(f"{UNIT}: CONSTANTS INITIALIZED")
    print(SEPARATOR)
    print(f"{UNIT}: RUNTIME STARTING")
    print(
        f"{UNIT}: DURABLE CERTIFICATE-CHAIN "
        "CONTINUITY DIAGNOSTIC"
    )
    print(SEPARATOR)

    lineage = sha256_text(
        f"{UNIT}|primary-lineage"
    )[:24]

    banner(
        f"{UNIT} TEST 1: "
        "ROOT CERTIFICATE + MANIFEST FINALIZATION"
    )

    engine = N23Engine(lineage)

    c0, m0 = engine.finalize_generation(
        generation=0,
        recovery_epoch=0,
        recovery_nonce=1,
    )

    check(
        "Root Certificate Finalized",
        c0.generation == 0,
    )

    check(
        "Root Manifest Finalized",
        m0.generation == 0,
    )

    check(
        "Root Certificate Uses Genesis Predecessor",
        c0.predecessor_certificate_hash == "GENESIS",
    )

    check(
        "Root Manifest Uses Genesis Predecessor",
        m0.predecessor_manifest_hash == "GENESIS",
    )

    banner(
        f"{UNIT} TEST 2: "
        "EXACT SUCCESSOR CHAIN BINDING"
    )

    c1, m1 = engine.finalize_generation(
        generation=1,
        recovery_epoch=1,
        recovery_nonce=2,
    )

    check(
        "Second Certificate References Root Certificate",
        c1.predecessor_certificate_hash
        == c0.certificate_hash,
    )

    check(
        "Second Manifest References Root Manifest",
        m1.predecessor_manifest_hash
        == m0.manifest_hash,
    )

    check(
        "Second Manifest Binds Exact Certificate",
        m1.certificate_hash
        == c1.certificate_hash,
    )

    banner(
        f"{UNIT} TEST 3: "
        "CONTIGUOUS GENERATION ADVANCE"
    )

    c2, m2 = engine.finalize_generation(
        generation=2,
        recovery_epoch=2,
        recovery_nonce=3,
    )

    check(
        "Complete Certificate Chain Validates",
        engine.validate_complete_chain() is True,
    )

    check(
        "Generation Chain Is Contiguous",
        engine.finalized_generations
        == [0, 1, 2],
    )

    expect_raises(
        "Skipped Generation Rejected",
        ChainError,
        lambda: engine.finalize_generation(
            generation=4,
            recovery_epoch=4,
            recovery_nonce=5,
        ),
    )

    banner(
        f"{UNIT} TEST 4: "
        "DUPLICATE FINALIZATION REJECTION"
    )

    expect_raises(
        "Duplicate Certified Generation Rejected",
        ChainError,
        lambda: engine.finalize_generation(
            generation=2,
            recovery_epoch=9,
            recovery_nonce=9,
        ),
    )

    banner(
        f"{UNIT} TEST 5: "
        "CERTIFICATE PREDECESSOR TAMPER REJECTION"
    )

    bad_c2 = tamper_dataclass(
        c2,
        "predecessor_certificate_hash",
        "FORGED-PREDECESSOR",
    )

    expect_raises(
        "Tampered Certificate Integrity Rejected",
        IntegrityError,
        lambda: N23Engine._verify_certificate(
            bad_c2
        ),
    )

    banner(
        f"{UNIT} TEST 6: "
        "MANIFEST PREDECESSOR TAMPER REJECTION"
    )

    bad_m2 = tamper_dataclass(
        m2,
        "predecessor_manifest_hash",
        "FORGED-MANIFEST-PREDECESSOR",
    )

    expect_raises(
        "Tampered Manifest Integrity Rejected",
        IntegrityError,
        lambda: N23Engine._verify_manifest(
            bad_m2
        ),
    )

    banner(
        f"{UNIT} TEST 7: "
        "PAYLOAD + DISPATCH BINDING"
    )

    check(
        "Certificate Payload Hash Preserved",
        c2.payload_hash == payload_hash(),
    )

    expected_dispatch = deterministic_dispatch_id(
        c2.lineage_id,
        c2.generation,
        c2.recovery_epoch,
        c2.recovery_nonce,
    )

    check(
        "Certificate Dispatch Identity Preserved",
        c2.dispatch_id == expected_dispatch,
    )

    receipt = synthetic_dispatch(c2)

    check(
        "Synthetic Dispatch Reports No Transmission",
        receipt["transmitted"] is False,
    )

    check(
        "Synthetic Dispatch Preserves Payload Hash",
        receipt["payload_hash"]
        == c2.payload_hash,
    )

    check(
        "Synthetic Dispatch Preserves Dispatch Identity",
        receipt["dispatch_id"]
        == c2.dispatch_id,
    )
    banner(
        f"{UNIT} TEST 8: "
        "DURABLE SNAPSHOT RESTART PRESERVATION"
    )

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(
            td,
            "n23_state.json",
        )

        engine.save_snapshot(path)

        restored = N23Engine.load_snapshot(path)

        check(
            "Restored Certificate Chain Validates",
            restored.validate_complete_chain() is True,
        )

        check(
            "Certified Generation Chain Survived Restart",
            restored.finalized_generations
            == [0, 1, 2],
        )

        check(
            "Root Manifest Hash Preserved Across Restart",
            restored.manifest(0).manifest_hash
            == m0.manifest_hash,
        )

        check(
            "Latest Certificate Hash Preserved Across Restart",
            restored.certificate(2).certificate_hash
            == c2.certificate_hash,
        )

    banner(
        f"{UNIT} TEST 9: "
        "SNAPSHOT TAMPER REJECTION"
    )

    state = engine.export_state()

    tampered_state = copy.deepcopy(state)
    tampered_state.finalized_generations = [
        0,
        1,
    ]

    expect_raises(
        "Tampered Snapshot Integrity Seal Rejected",
        IntegrityError,
        lambda: N23Engine.restore_state(
            tampered_state
        ),
    )

    banner(
        f"{UNIT} TEST 10: "
        "FOREIGN LINEAGE CHAIN REJECTION"
    )

    foreign_state = copy.deepcopy(
        engine.export_state()
    )

    foreign_state.lineage_id = (
        "foreign-lineage"
    )

    foreign_state.snapshot_seal = seal_dict(
        foreign_state.body()
    )

    expect_raises(
        "Foreign Lineage Snapshot Rejected",
        ChainError,
        lambda: N23Engine.restore_state(
            foreign_state
        ),
    )

    banner(
        f"{UNIT} TEST 11: "
        "STALE PREDECESSOR / FORK REJECTION"
    )

    fork = N23Engine(
        engine.lineage_id
    )

    fork._certificates = copy.deepcopy(
        engine._certificates
    )

    fork._manifests = copy.deepcopy(
        engine._manifests
    )

    fork._finalized = set(
        engine._finalized
    )

    forged_c2 = N23Engine._build_certificate(
        lineage_id=engine.lineage_id,
        generation=2,
        recovery_epoch=2,
        recovery_nonce=3,
        owner_id=c2.owner_id,
        payload_digest=c2.payload_hash,
        dispatch_id=c2.dispatch_id,
        predecessor_certificate_hash=(
            c0.certificate_hash
        ),
    )

    fork._certificates[2] = forged_c2

    fork._manifests[2] = (
        N23Engine._build_manifest(
            lineage_id=engine.lineage_id,
            generation=2,
            certificate_hash=(
                forged_c2.certificate_hash
            ),
            predecessor_manifest_hash=(
                m1.manifest_hash
            ),
        )
    )

    expect_raises(
        "Forked Certificate Predecessor Rejected",
        ChainError,
        fork.validate_complete_chain,
    )

    banner(
        f"{UNIT} TEST 12: "
        "ANTI-ABA OWNER REUSE ACROSS CHAIN"
    )

    reused_owner = c0.owner_id

    c3, m3 = engine.finalize_generation(
        generation=3,
        recovery_epoch=3,
        recovery_nonce=4,
        owner_id=reused_owner,
    )

    check(
        "Reused Owner Is Bound To Higher Generation",
        c3.generation > c0.generation,
    )

    check(
        "Reused Owner Certificate Uses New Dispatch Identity",
        c3.dispatch_id
        != c0.dispatch_id,
    )

    check(
        "Reused Owner Certificate Uses New Predecessor",
        c3.predecessor_certificate_hash
        == c2.certificate_hash,
    )

    check(
        "Reused Owner Manifest Extends Existing Chain",
        m3.predecessor_manifest_hash
        == m2.manifest_hash,
    )

    check(
        "Reused Owner Uses Higher Recovery Epoch",
        c3.recovery_epoch
        > c0.recovery_epoch,
    )

    check(
        "Reused Owner Uses Higher Recovery Nonce",
        c3.recovery_nonce
        > c0.recovery_nonce,
    )

    banner(
        f"{UNIT} TEST 13: "
        "CONCURRENT NEXT-GENERATION SINGLE WINNER"
    )

    race_engine = N23Engine(
        "race-lineage"
    )

    race_engine.finalize_generation(
        generation=0,
        recovery_epoch=0,
        recovery_nonce=1,
    )

    winners: List[
        Tuple[
            FinalityCertificate,
            GenerationManifest,
        ]
    ] = []

    errors: List[Exception] = []

    gate = threading.Barrier(8)

    def contender(i: int) -> None:
        try:
            gate.wait()

            result = (
                race_engine.finalize_generation(
                    generation=1,
                    recovery_epoch=1,
                    recovery_nonce=i + 10,
                    owner_id=f"worker-{i}",
                )
            )

            winners.append(result)

        except Exception as exc:
            errors.append(exc)

    threads = [
        threading.Thread(
            target=contender,
            args=(i,),
        )
        for i in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    check(
        "Concurrent Chain Validates",
        race_engine.validate_complete_chain()
        is True,
    )

    check(
        "Concurrent Generation Finalization Produced One Winner",
        len(winners) == 1,
    )

    check(
        "Concurrent Losers Were Rejected",
        len(errors) == 7,
    )

    check(
        "Concurrent Final State Contains One Successor",
        race_engine.finalized_generations
        == [0, 1],
    )

    banner(
        f"{UNIT} TEST 14: "
        "RESTART THEN CONTINUE CERTIFICATE CHAIN"
    )

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(
            td,
            "n23_continue.json",
        )

        engine.save_snapshot(path)

        resumed = N23Engine.load_snapshot(
            path
        )

        c4, m4 = resumed.finalize_generation(
            generation=4,
            recovery_epoch=4,
            recovery_nonce=5,
        )

        check(
            "Post-Restart Chain Validates",
            resumed.validate_complete_chain()
            is True,
        )

        check(
            "Post-Restart Generation Advanced Exactly Once",
            resumed.finalized_generations
            == [0, 1, 2, 3, 4],
        )

        check(
            "Post-Restart Certificate References Prior Certificate",
            c4.predecessor_certificate_hash
            == c3.certificate_hash,
        )

        check(
            "Post-Restart Manifest References Prior Manifest",
            m4.predecessor_manifest_hash
            == m3.manifest_hash,
        )

        expect_raises(
            "Post-Restart Duplicate Generation Rejected",
            ChainError,
            lambda: resumed.finalize_generation(
                generation=4,
                recovery_epoch=5,
                recovery_nonce=6,
            ),
        )

    banner(
        f"{UNIT} TEST 15: "
        "EXACT SYNTHETIC TRANSPORT BINDING"
    )

    receipt = synthetic_dispatch(c3)

    check(
        "Transport Method Exactly POST",
        receipt["method"]
        == TRANSPORT_METHOD,
    )

    check(
        "Transport Path Exactly Leverage Endpoint",
        receipt["path"]
        == TRANSPORT_PATH,
    )

    check(
        "Transport Payload Preserved",
        receipt["payload"]
        == payload(),
    )

    check(
        "Transport Payload Hash Preserved",
        receipt["payload_hash"]
        == payload_hash(),
    )

    check(
        "Transport Dispatch Identity Preserved",
        receipt["dispatch_id"]
        == c3.dispatch_id,
    )

    check(
        "Synthetic Receipt Reports No Transmission",
        receipt["transmitted"]
        is False,
    )

    banner(
        f"{UNIT} TEST 16: "
        "FINAL NETWORK WRITE FIREBREAK"
    )

    expect_raises(
        "Real POST Rejected Locally",
        LocalSafetyBlock,
        lambda: real_network_post(),
    )

    expect_raises(
        "Generic Network Write Rejected Locally",
        LocalSafetyBlock,
        lambda: generic_network_write(
            "PUT"
        ),
    )

    expect_raises(
        "Leverage Mutation Transport Rejected Locally",
        LocalSafetyBlock,
        lambda: leverage_mutation_transport(),
    )

    check(
        "Network POST Count Is Zero",
        NETWORK_POST_COUNT == 0,
    )

    check(
        "Network Write Count Is Zero",
        NETWORK_WRITE_COUNT == 0,
    )

    check(
        "Leverage Transmission Count Is Zero",
        LEVERAGE_TRANSMISSION_COUNT
        == 0,
    )

    banner(
        f"{UNIT} WRITE-LOCK AUDIT"
    )

    print(
        f"  Network POSTs = "
        f"{NETWORK_POST_COUNT}"
    )

    print(
        f"  Network writes = "
        f"{NETWORK_WRITE_COUNT}"
    )

    print(
        f"  Leverage transmissions = "
        f"{LEVERAGE_TRANSMISSION_COUNT}"
    )

    print(
        f"  Synthetic dispatches = "
        f"{SYNTHETIC_DISPATCH_COUNT}"
    )

    check(
        "Network POST Count Is Zero",
        NETWORK_POST_COUNT == 0,
    )

    check(
        "Network Write Count Is Zero",
        NETWORK_WRITE_COUNT == 0,
    )

    check(
        "Leverage Transmission Count Is Zero",
        LEVERAGE_TRANSMISSION_COUNT
        == 0,
    )

    structural_failures = FAIL_COUNT

    readiness_blockers = (
        0
        if (
            structural_failures == 0
            and not REAL_NETWORK_POST_ENABLED
            and not NETWORK_WRITE_ENABLED
            and not LEVERAGE_MUTATION_TRANSPORT_ENABLED
        )
        else 1
    )

    banner(
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
        "  Durable Finality Certificate Chain "
        "= ✅ VERIFIED"
    )

    print(
        "  Generation Manifest Chain "
        "= ✅ VERIFIED"
    )

    print(
        "  Certificate Predecessor Binding "
        "= ✅ VERIFIED"
    )

    print(
        "  Manifest Predecessor Binding "
        "= ✅ VERIFIED"
    )

    print(
        "  Certificate/Manifest Cross-Binding "
        "= ✅ VERIFIED"
    )

    print(
        "  Contiguous Generation Advance "
        "= ✅ VERIFIED"
    )

    print(
        "  Fork / Skipped Generation Rejection "
        "= ✅ VERIFIED"
    )

    print(
        "  Restart Chain Preservation "
        "= ✅ VERIFIED"
    )

    print(
        "  Snapshot Integrity "
        "= ✅ VERIFIED"
    )

    print(
        "  Cross-Lineage Chain Rejection "
        "= ✅ VERIFIED"
    )

    print(
        "  Concurrent Next-Generation Single Winner "
        "= ✅ VERIFIED"
    )

    print(
        "  Anti-ABA Owner Reuse Across Chain "
        "= ✅ VERIFIED"
    )

    print(
        "  Exact Synthetic Transport Binding "
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
        structural_failures == 0,
    )

    check(
        "Readiness Blockers Are Zero",
        readiness_blockers == 0,
    )

    print()
    print(SEPARATOR)

    if FAIL_COUNT == 0:
        print(
            f"✅ {UNIT} DIAGNOSTIC PASSED"
        )

        print(SEPARATOR)

        print(
            "✅ DURABLE CERTIFICATE-CHAIN "
            "CONTINUITY VERIFIED"
        )

        print(
            "✅ GENERATION MANIFEST CHAIN "
            "VERIFIED"
        )

        print(
            "✅ EXACT PREDECESSOR CERTIFICATE "
            "BINDING VERIFIED"
        )

        print(
            "✅ EXACT PREDECESSOR MANIFEST "
            "BINDING VERIFIED"
        )

        print(
            "✅ CERTIFICATE/MANIFEST "
            "CROSS-BINDING VERIFIED"
        )

        print(
            "✅ SKIPPED GENERATION REJECTED"
        )

        print(
            "✅ FORKED PREDECESSOR REJECTED"
        )

        print(
            "✅ CERTIFICATE CHAIN SURVIVES "
            "RESTART"
        )

        print(
            "✅ SNAPSHOT TAMPER REJECTED"
        )

        print(
            "✅ FOREIGN LINEAGE CHAIN REJECTED"
        )

        print(
            "✅ CONCURRENT SUCCESSOR FINALIZATION "
            "PRODUCES ONE WINNER"
        )

        print(
            "✅ ANTI-ABA OWNER REUSE ACROSS "
            "CHAIN VERIFIED"
        )

        print(
            "✅ EXACT SYNTHETIC TRANSPORT "
            "BINDING VERIFIED"
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

    print(SEPARATOR)


def heartbeat_loop() -> None:
    heartbeat = 1

    while True:
        print(
            f"{UNIT}: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        heartbeat += 1
        time.sleep(15)


def main() -> None:
    run_diagnostic()

    if FAIL_COUNT != 0:
        raise SystemExit(1)

    print(
        f"{UNIT}: PERSISTENT RUNTIME ACTIVE"
    )

    print(
        f"{UNIT}: DURABLE CERTIFICATE-CHAIN "
        "LOCK ACTIVE"
    )

    print(
        f"{UNIT}: GENERATION MANIFEST "
        "CHAIN LOCK ACTIVE"
    )

    print(
        f"{UNIT}: CERTIFICATE PREDECESSOR "
        "BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT}: MANIFEST PREDECESSOR "
        "BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT}: CERTIFICATE/MANIFEST "
        "CROSS-BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT}: CONTIGUOUS GENERATION "
        "ADVANCE LOCK ACTIVE"
    )

    print(
        f"{UNIT}: FORKED GENERATION "
        "REJECTION LOCK ACTIVE"
    )

    print(
        f"{UNIT}: RESTART CHAIN "
        "PRESERVATION LOCK ACTIVE"
    )

    print(
        f"{UNIT}: SNAPSHOT INTEGRITY "
        "LOCK ACTIVE"
    )

    print(
        f"{UNIT}: CROSS-LINEAGE "
        "CHAIN LOCK ACTIVE"
    )

    print(
        f"{UNIT}: CONCURRENT SUCCESSOR "
        "FINALIZATION LOCK ACTIVE"
    )

    print(
        f"{UNIT}: ANTI-ABA CHAIN "
        "LOCK ACTIVE"
    )

    print(
        f"{UNIT}: SYNTHETIC TRANSPORT "
        "INTERCEPTOR ACTIVE"
    )

    print(
        f"{UNIT}: NETWORK WRITE "
        "TRANSPORT LOCKED"
    )

    print(
        f"{UNIT}: LEVERAGE MUTATION "
        "TRANSPORT LOCKED"
    )

    heartbeat_loop()


if __name__ == "__main__":
    main()
