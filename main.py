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
