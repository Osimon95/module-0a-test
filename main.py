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
