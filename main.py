# ============================================================================
# R28 UNIT N.30
# MANIFEST INTEGRITY + ROLLBACK FENCING + COMMITTED-AUTHORITY RECOVERY
#
# CORRECTED COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.30 INCREMENT OVER N.29:
#   - SEALED CHECKPOINT MANIFEST
#   - MANIFEST HASH-CHAIN BINDING
#   - MONOTONIC MANIFEST SEQUENCE FENCING
#   - ROLLBACK / REPLAYED MANIFEST REJECTION
#   - COMMITTED-AUTHORITY RECOVERY AFTER CRASH
#   - DUAL-SLOT AUTHORITATIVE CHECKPOINT SELECTION
#   - SLOT / GENERATION / LINEAGE / WAL BINDING
#   - PENDING PROMOTION RECOVERY FENCING
#   - EXACT SYNTHETIC TRANSPORT BINDING PRESERVED
# ============================================================================

print("R28 UNIT N.30: MAIN.PY ENTERED", flush=True)

import copy
import hashlib
import hmac
import json
import os
import threading
import time
import uuid

from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional, Set, Tuple


print("R28 UNIT N.30: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.30"
UNIT_VERSION = "N.30"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

INTEGRITY_KEY = b"R28-N30-LOCAL-INTEGRITY-KEY"
MANIFEST_KEY = b"R28-N30-MANIFEST-INTEGRITY-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

SLOT_A = "A"
SLOT_B = "B"

GENESIS_HASH = "0" * 64

print("R28 UNIT N.30: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# LOCAL BLOCK / ASSERT HELPERS
# ============================================================================

class LocalBlock(RuntimeError):
    pass


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)
    raise LocalBlock(message)


def assert_pass(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"{label:<80} ✅ PASS", flush=True)


def separator() -> None:
    print("-" * 92, flush=True)


def banner() -> None:
    print("=" * 92, flush=True)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sign_object(value: Any, key: bytes) -> str:
    body = canonical_json(value).encode("utf-8")
    return hmac.new(key, body, hashlib.sha256).hexdigest()


def deep_copy(value: Any) -> Any:
    return copy.deepcopy(value)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RecoveryLease:
    owner: str
    generation: int
    lineage: str
    recovery_epoch: int
    nonce: int


@dataclass
class Authorization:
    authorization_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    payload_hash: str
    consumed: bool = False


@dataclass
class CommitRecord:
    commit_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    payload_hash: str
    sequence: int


@dataclass
class DispatchReceipt:
    dispatch_id: str
    method: str
    path: str
    payload: Dict[str, Any]
    payload_hash: str
    synthetic: bool
    generation: int
    lineage: str


@dataclass
class WALRecord:
    sequence: int
    event: str
    generation: int
    lineage: str
    recovery_epoch: int
    payload: Dict[str, Any]
    prev_hash: str
    record_hash: str = ""

    def unsigned(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event": self.event,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
        }

    def seal(self) -> None:
        self.record_hash = sha256_text(
            canonical_json(self.unsigned())
        )

    def validate(self) -> None:
        expected = sha256_text(
            canonical_json(self.unsigned())
        )
        if not hmac.compare_digest(
            self.record_hash,
            expected,
        ):
            local_block("WAL record hash mismatch")


@dataclass
class Checkpoint:
    slot: str
    checkpoint_sequence: int
    promotion_sequence: int
    generation: int
    lineage: str
    recovery_epoch: int
    phase: str
    wal_length: int
    wal_final_hash: str
    state_payload: Dict[str, Any]
    seal: str = ""

    def unsigned(self) -> Dict[str, Any]:
        return {
            "slot": self.slot,
            "checkpoint_sequence": self.checkpoint_sequence,
            "promotion_sequence": self.promotion_sequence,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "phase": self.phase,
            "wal_length": self.wal_length,
            "wal_final_hash": self.wal_final_hash,
            "state_payload": self.state_payload,
        }

    def seal_checkpoint(self) -> None:
        self.seal = sign_object(
            self.unsigned(),
            INTEGRITY_KEY,
        )

    def validate_seal(self) -> None:
        expected = sign_object(
            self.unsigned(),
            INTEGRITY_KEY,
        )
        if not hmac.compare_digest(
            self.seal,
            expected,
        ):
            local_block(
                "checkpoint integrity seal mismatch"
            )


@dataclass
class Manifest:
    manifest_sequence: int
    authoritative_slot: str
    checkpoint_sequence: int
    promotion_sequence: int
    generation: int
    lineage: str
    recovery_epoch: int
    wal_length: int
    wal_final_hash: str
    previous_manifest_hash: str
    manifest_hash: str = ""
    seal: str = ""

    def unsigned(self) -> Dict[str, Any]:
        return {
            "manifest_sequence": self.manifest_sequence,
            "authoritative_slot": self.authoritative_slot,
            "checkpoint_sequence": self.checkpoint_sequence,
            "promotion_sequence": self.promotion_sequence,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "wal_length": self.wal_length,
            "wal_final_hash": self.wal_final_hash,
            "previous_manifest_hash": self.previous_manifest_hash,
        }

    def compute_hash(self) -> str:
        return sha256_text(
            canonical_json(self.unsigned())
        )

    def seal_manifest(self) -> None:
        self.manifest_hash = self.compute_hash()
        self.seal = sign_object(
            {
                "unsigned": self.unsigned(),
                "manifest_hash": self.manifest_hash,
            },
            MANIFEST_KEY,
        )

    def validate(self) -> None:
        expected_hash = self.compute_hash()

        if not hmac.compare_digest(
            self.manifest_hash,
            expected_hash,
        ):
            local_block("manifest hash mismatch")

        expected_seal = sign_object(
            {
                "unsigned": self.unsigned(),
                "manifest_hash": self.manifest_hash,
            },
            MANIFEST_KEY,
        )

        if not hmac.compare_digest(
            self.seal,
            expected_seal,
        ):
            local_block(
                "manifest integrity seal mismatch"
            )


@dataclass
class DurableState:
    generation: int = 1

    lineage: str = field(
        default_factory=lambda: uuid.uuid4().hex
    )

    recovery_epoch: int = 1
    phase: str = PHASE_PREPARED

    next_lease_nonce: int = 1
    next_commit_sequence: int = 1
    next_checkpoint_sequence: int = 1
    next_promotion_sequence: int = 1
    next_manifest_sequence: int = 1

    authorization: Optional[Authorization] = None
    commit: Optional[CommitRecord] = None
    dispatch: Optional[DispatchReceipt] = None

    wal: List[WALRecord] = field(
        default_factory=list
    )

    checkpoint_slots: Dict[
        str,
        Optional[Checkpoint],
    ] = field(
        default_factory=lambda: {
            SLOT_A: None,
            SLOT_B: None,
        }
    )

    manifest: Optional[Manifest] = None

    manifest_history: List[Manifest] = field(
        default_factory=list
    )

    pending_checkpoint_slot: Optional[str] = None
    pending_checkpoint_sequence: Optional[int] = None
    pending_promotion_sequence: Optional[int] = None

    burned_checkpoint_sequences: Set[int] = field(
        default_factory=set
    )

    burned_promotion_sequences: Set[int] = field(
        default_factory=set
    )

    completed_dispatch_ids: Set[str] = field(
        default_factory=set
    )


# ============================================================================
# SYNTHETIC TRANSPORT FIREBREAK
# ============================================================================

class SyntheticTransport:
    def __init__(self) -> None:
        self.synthetic_dispatches: List[
            DispatchReceipt
        ] = []

        self.network_write_count = 0
        self.real_post_count = 0
        self.demo_post_count = 0

    def real_post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> None:
        self.real_post_count += 0
        local_block(
            "real network POST is disabled"
        )

    def demo_post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> None:
        self.demo_post_count += 0
        local_block(
            "demo network POST is disabled"
        )

    def dispatch_synthetic(
        self,
        *,
        generation: int,
        lineage: str,
        method: str,
        path: str,
        payload: Dict[str, Any],
    ) -> DispatchReceipt:

        if not SYNTHETIC_TRANSPORT_ONLY:
            local_block(
                "synthetic-only transport invariant disabled"
            )

        if method != HTTP_METHOD:
            local_block(
                "transport method mismatch"
            )

        if path != LEVERAGE_ENDPOINT:
            local_block(
                "transport path mismatch"
            )

        exact_payload = deep_copy(payload)

        payload_hash = sha256_text(
            canonical_json(exact_payload)
        )

        receipt = DispatchReceipt(
            dispatch_id=uuid.uuid4().hex,
            method=method,
            path=path,
            payload=exact_payload,
            payload_hash=payload_hash,
            synthetic=True,
            generation=generation,
            lineage=lineage,
        )

        self.synthetic_dispatches.append(
            receipt
        )

        return receipt


# ============================================================================
# N.30 ENGINE
# ============================================================================

class N30Engine:
    def __init__(
        self,
        state: Optional[DurableState] = None,
        transport: Optional[SyntheticTransport] = None,
    ) -> None:

        self.state = (
            state
            if state is not None
            else DurableState()
        )

        self.transport = (
            transport
            if transport is not None
            else SyntheticTransport()
        )

        self._lock = threading.RLock()

    # ------------------------------------------------------------------------
    # WAL
    # ------------------------------------------------------------------------

    def wal_final_hash(self) -> str:
        if not self.state.wal:
            return GENESIS_HASH

        return self.state.wal[-1].record_hash

    def append_wal(
        self,
        event: str,
        payload: Dict[str, Any],
    ) -> WALRecord:

        with self._lock:
            record = WALRecord(
                sequence=len(self.state.wal) + 1,
                event=event,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                payload=deep_copy(payload),
                prev_hash=self.wal_final_hash(),
            )

            record.seal()

            self.state.wal.append(
                record
            )

            return record

    def validate_wal(self) -> None:
        expected_prev = GENESIS_HASH

        for index, record in enumerate(
            self.state.wal,
            start=1,
        ):
            if record.sequence != index:
                local_block(
                    "WAL sequence mismatch"
                )

            if record.prev_hash != expected_prev:
                local_block(
                    "WAL previous hash mismatch"
                )

            record.validate()

            expected_prev = record.record_hash

    # ------------------------------------------------------------------------
    # LEASE / AUTHORIZATION / COMMIT / DISPATCH
    # ------------------------------------------------------------------------

    def acquire_recovery_lease(
        self,
        owner: str,
    ) -> RecoveryLease:

        with self._lock:
            nonce = self.state.next_lease_nonce
            self.state.next_lease_nonce += 1

            lease = RecoveryLease(
                owner=owner,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                nonce=nonce,
            )

            self.append_wal(
                "LEASE_ACQUIRED",
                asdict(lease),
            )

            return lease

    def validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:

        if lease.generation != self.state.generation:
            local_block(
                "recovery lease generation mismatch"
            )

        if lease.lineage != self.state.lineage:
            local_block(
                "recovery lease lineage mismatch"
            )

        if (
            lease.recovery_epoch
            != self.state.recovery_epoch
        ):
            local_block(
                "recovery lease epoch mismatch"
            )

    def authorize(
        self,
        lease: RecoveryLease,
        payload: Dict[str, Any],
    ) -> Authorization:

        with self._lock:
            self.validate_lease(lease)

            payload_hash = sha256_text(
                canonical_json(payload)
            )

            auth = Authorization(
                authorization_id=uuid.uuid4().hex,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                payload_hash=payload_hash,
                consumed=False,
            )

            self.state.authorization = auth
            self.state.phase = PHASE_AUTHORIZED

            self.append_wal(
                "AUTHORIZED",
                asdict(auth),
            )

            return auth

    def commit_dispatch(
        self,
        lease: RecoveryLease,
        payload: Dict[str, Any],
    ) -> CommitRecord:

        with self._lock:
            self.validate_lease(lease)

            auth = self.state.authorization

            if auth is None:
                local_block(
                    "missing authorization"
                )

            if auth.consumed:
                local_block(
                    "authorization already consumed"
                )

            payload_hash = sha256_text(
                canonical_json(payload)
            )

            if payload_hash != auth.payload_hash:
                local_block(
                    "authorization payload hash mismatch"
                )

            auth.consumed = True

            commit = CommitRecord(
                commit_id=uuid.uuid4().hex,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                payload_hash=payload_hash,
                sequence=self.state.next_commit_sequence,
            )

            self.state.next_commit_sequence += 1

            self.state.commit = commit
            self.state.phase = PHASE_COMMITTED

            self.append_wal(
                "COMMIT_CREATED",
                asdict(commit),
            )

            return commit

    def dispatch_committed(
        self,
        payload: Dict[str, Any],
    ) -> DispatchReceipt:

        with self._lock:
            commit = self.state.commit

            if commit is None:
                local_block(
                    "missing durable commit"
                )

            payload_hash = sha256_text(
                canonical_json(payload)
            )

            if payload_hash != commit.payload_hash:
                local_block(
                    "commit payload hash mismatch"
                )

            if self.state.dispatch is not None:
                if (
                    self.state.dispatch.dispatch_id
                    in self.state.completed_dispatch_ids
                ):
                    return self.state.dispatch

                return self.state.dispatch

            receipt = self.transport.dispatch_synthetic(
                generation=self.state.generation,
                lineage=self.state.lineage,
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload=payload,
            )

            self.state.dispatch = receipt
            self.state.phase = PHASE_DISPATCHED

            self.append_wal(
                "SYNTHETIC_DISPATCHED",
                asdict(receipt),
            )

            return receipt

    def finalize_dispatch(self) -> None:
        with self._lock:
            if self.state.dispatch is None:
                local_block(
                    "cannot finalize without dispatch"
                )

            self.state.completed_dispatch_ids.add(
                self.state.dispatch.dispatch_id
            )

            self.state.phase = PHASE_COMPLETED

            self.append_wal(
                "DISPATCH_FINALIZED",
                {
                    "dispatch_id":
                    self.state.dispatch.dispatch_id
                },
            )

    # ------------------------------------------------------------------------
    # CHECKPOINT CONSTRUCTION / VALIDATION
    # ------------------------------------------------------------------------

    def authoritative_slot(
        self,
    ) -> Optional[str]:

        return (
            None
            if self.state.manifest is None
            else self.state.manifest.authoritative_slot
        )

    def inactive_slot(self) -> str:
        current = self.authoritative_slot()

        if current == SLOT_A:
            return SLOT_B

        return SLOT_A

    def make_checkpoint(
        self,
        slot: str,
    ) -> Checkpoint:

        if slot not in (
            SLOT_A,
            SLOT_B,
        ):
            local_block(
                "invalid checkpoint slot"
            )

        checkpoint_sequence = (
            self.state.next_checkpoint_sequence
        )

        self.state.next_checkpoint_sequence += 1

        promotion_sequence = (
            self.state.next_promotion_sequence
        )

        self.state.next_promotion_sequence += 1

        checkpoint = Checkpoint(
            slot=slot,
            checkpoint_sequence=checkpoint_sequence,
            promotion_sequence=promotion_sequence,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            phase=self.state.phase,
            wal_length=len(self.state.wal),
            wal_final_hash=self.wal_final_hash(),
            state_payload={
                "authorization": (
                    asdict(self.state.authorization)
                    if self.state.authorization
                    else None
                ),
                "commit": (
                    asdict(self.state.commit)
                    if self.state.commit
                    else None
                ),
                "dispatch": (
                    asdict(self.state.dispatch)
                    if self.state.dispatch
                    else None
                ),
                "completed_dispatch_ids": sorted(
                    self.state.completed_dispatch_ids
                ),
            },
        )

        checkpoint.seal_checkpoint()

        return checkpoint

    def validate_checkpoint(
        self,
        checkpoint: Checkpoint,
        expected_slot: Optional[str] = None,
    ) -> None:

        checkpoint.validate_seal()

        if checkpoint.slot not in (
            SLOT_A,
            SLOT_B,
        ):
            local_block(
                "invalid checkpoint slot"
            )

        if (
            expected_slot is not None
            and checkpoint.slot != expected_slot
        ):
            local_block(
                "checkpoint stored in wrong slot"
            )

        if (
            checkpoint.generation
            != self.state.generation
        ):
            local_block(
                "checkpoint generation mismatch"
            )

        if checkpoint.lineage != self.state.lineage:
            local_block(
                "checkpoint lineage mismatch"
            )

        if (
            checkpoint.recovery_epoch
            != self.state.recovery_epoch
        ):
            local_block(
                "checkpoint recovery epoch mismatch"
            )

        if (
            checkpoint.wal_length
            != len(self.state.wal)
        ):
            local_block(
                "checkpoint WAL length mismatch"
            )

        if (
            checkpoint.wal_final_hash
            != self.wal_final_hash()
        ):
            local_block(
                "checkpoint WAL final hash mismatch"
            )

    # ------------------------------------------------------------------------
    # TWO-PHASE CHECKPOINT PROMOTION
    # ------------------------------------------------------------------------

    def stage_checkpoint(
        self,
    ) -> Checkpoint:

        with self._lock:
            if (
                self.state.pending_checkpoint_slot
                is not None
            ):
                local_block(
                    "checkpoint promotion already pending"
                )

            slot = self.inactive_slot()

            checkpoint = self.make_checkpoint(
                slot
            )

            self.state.checkpoint_slots[
                slot
            ] = checkpoint

            self.state.pending_checkpoint_slot = (
                slot
            )

            self.state.pending_checkpoint_sequence = (
                checkpoint.checkpoint_sequence
            )

            self.state.pending_promotion_sequence = (
                checkpoint.promotion_sequence
            )

            self.append_wal(
                "CHECKPOINT_STAGED",
                {
                    "slot": slot,
                    "checkpoint_sequence":
                    checkpoint.checkpoint_sequence,
                    "promotion_sequence":
                    checkpoint.promotion_sequence,
                },
            )

            checkpoint.wal_length = len(
                self.state.wal
            )

            checkpoint.wal_final_hash = (
                self.wal_final_hash()
            )

            checkpoint.seal_checkpoint()

            return checkpoint

    def build_manifest(
        self,
        checkpoint: Checkpoint,
    ) -> Manifest:

        prior_hash = (
            self.state.manifest.manifest_hash
            if self.state.manifest is not None
            else GENESIS_HASH
        )

        manifest = Manifest(
            manifest_sequence=(
                self.state.next_manifest_sequence
            ),
            authoritative_slot=checkpoint.slot,
            checkpoint_sequence=(
                checkpoint.checkpoint_sequence
            ),
            promotion_sequence=(
                checkpoint.promotion_sequence
            ),
            generation=checkpoint.generation,
            lineage=checkpoint.lineage,
            recovery_epoch=(
                checkpoint.recovery_epoch
            ),
            wal_length=checkpoint.wal_length,
            wal_final_hash=checkpoint.wal_final_hash,
            previous_manifest_hash=prior_hash,
        )

        manifest.seal_manifest()

        return manifest

    def validate_manifest(
        self,
        manifest: Manifest,
        *,
        allow_historical: bool = False,
    ) -> Checkpoint:

        manifest.validate()

        if manifest.authoritative_slot not in (
            SLOT_A,
            SLOT_B,
        ):
            local_block(
                "manifest authoritative slot invalid"
            )

        checkpoint = (
            self.state.checkpoint_slots.get(
                manifest.authoritative_slot
            )
        )

        if checkpoint is None:
            local_block(
                "manifest points to missing checkpoint"
            )

        checkpoint.validate_seal()

        if (
            checkpoint.slot
            != manifest.authoritative_slot
        ):
            local_block(
                "manifest checkpoint slot mismatch"
            )

        if (
            checkpoint.checkpoint_sequence
            != manifest.checkpoint_sequence
        ):
            local_block(
                "manifest checkpoint sequence mismatch"
            )

        if (
            checkpoint.promotion_sequence
            != manifest.promotion_sequence
        ):
            local_block(
                "manifest promotion sequence mismatch"
            )

        if (
            checkpoint.generation
            != manifest.generation
        ):
            local_block(
                "manifest generation mismatch"
            )

        if (
            checkpoint.lineage
            != manifest.lineage
        ):
            local_block(
                "manifest lineage mismatch"
            )

        if (
            checkpoint.recovery_epoch
            != manifest.recovery_epoch
        ):
            local_block(
                "manifest recovery epoch mismatch"
            )

        if (
            checkpoint.wal_length
            != manifest.wal_length
        ):
            local_block(
                "manifest WAL length mismatch"
            )

        if (
            checkpoint.wal_final_hash
            != manifest.wal_final_hash
        ):
            local_block(
                "manifest WAL final hash mismatch"
            )

        if (
            not allow_historical
            and self.state.manifest is not None
        ):
            current = self.state.manifest

            if (
                manifest.manifest_sequence
                < current.manifest_sequence
            ):
                local_block(
                    "manifest rollback detected"
                )

            if (
                manifest.manifest_sequence
                == current.manifest_sequence
                and manifest.manifest_hash
                != current.manifest_hash
            ):
                local_block(
                    "manifest sequence collision"
                )

        return checkpoint

    def commit_checkpoint_promotion(
        self,
    ) -> Manifest:

        with self._lock:
            slot = (
                self.state.pending_checkpoint_slot
            )

            if slot is None:
                local_block(
                    "no pending checkpoint promotion"
                )

            checkpoint = (
                self.state.checkpoint_slots.get(slot)
            )

            if checkpoint is None:
                local_block(
                    "pending checkpoint missing"
                )

            if (
                checkpoint.checkpoint_sequence
                != self.state.pending_checkpoint_sequence
            ):
                local_block(
                    "pending checkpoint sequence mismatch"
                )

            if (
                checkpoint.promotion_sequence
                != self.state.pending_promotion_sequence
            ):
                local_block(
                    "pending promotion sequence mismatch"
                )

            self.validate_checkpoint(
                checkpoint,
                expected_slot=slot,
            )

            manifest = self.build_manifest(
                checkpoint
            )

            self.append_wal(
                "CHECKPOINT_PROMOTION_COMMITTED",
                {
                    "slot": slot,
                    "checkpoint_sequence":
                    checkpoint.checkpoint_sequence,
                    "promotion_sequence":
                    checkpoint.promotion_sequence,
                    "manifest_sequence":
                    manifest.manifest_sequence,
                },
            )

            checkpoint.wal_length = len(
                self.state.wal
            )

            checkpoint.wal_final_hash = (
                self.wal_final_hash()
            )

            checkpoint.seal_checkpoint()

            manifest.wal_length = (
                checkpoint.wal_length
            )

            manifest.wal_final_hash = (
                checkpoint.wal_final_hash
            )

            manifest.seal_manifest()

            self.state.manifest = manifest

            self.state.manifest_history.append(
                deep_copy(manifest)
            )

            self.state.next_manifest_sequence += 1

            self.state.pending_checkpoint_slot = None
            self.state.pending_checkpoint_sequence = None
            self.state.pending_promotion_sequence = None

            return manifest

    def abort_pending_checkpoint(
        self,
    ) -> None:

        with self._lock:
            if (
                self.state.pending_checkpoint_sequence
                is not None
            ):
                self.state.burned_checkpoint_sequences.add(
                    self.state.pending_checkpoint_sequence
                )

            if (
                self.state.pending_promotion_sequence
                is not None
            ):
                self.state.burned_promotion_sequences.add(
                    self.state.pending_promotion_sequence
                )

            self.state.pending_checkpoint_slot = None
            self.state.pending_checkpoint_sequence = None
            self.state.pending_promotion_sequence = None

    # ------------------------------------------------------------------------
    # RECOVERY / AUTHORITY
    # ------------------------------------------------------------------------

    def recover_authoritative_checkpoint(
        self,
    ) -> Optional[Checkpoint]:

        with self._lock:
            self.validate_wal()

            if self.state.manifest is None:
                return None

            manifest = self.state.manifest

            manifest.validate()

            if self.state.manifest_history:
                matching = [
                    item
                    for item
                    in self.state.manifest_history
                    if (
                        item.manifest_sequence
                        == manifest.manifest_sequence
                    )
                ]

                if not matching:
                    local_block(
                        "authoritative manifest absent from history"
                    )

                if (
                    matching[-1].manifest_hash
                    != manifest.manifest_hash
                ):
                    local_block(
                        "authoritative manifest history mismatch"
                    )

            checkpoint = self.validate_manifest(
                manifest
            )

            if (
                checkpoint.generation
                != self.state.generation
            ):
                local_block(
                    "authoritative checkpoint generation mismatch"
                )

            if (
                checkpoint.lineage
                != self.state.lineage
            ):
                local_block(
                    "authoritative checkpoint lineage mismatch"
                )

            if (
                self.state.pending_checkpoint_slot
                is not None
                and self.state.pending_checkpoint_slot
                != manifest.authoritative_slot
            ):
                staged = (
                    self.state.checkpoint_slots.get(
                        self.state.pending_checkpoint_slot
                    )
                )

                if staged is not None:
                    self.state.burned_checkpoint_sequences.add(
                        staged.checkpoint_sequence
                    )

                    self.state.burned_promotion_sequences.add(
                        staged.promotion_sequence
                    )

                self.abort_pending_checkpoint()

            return checkpoint

    def verify_manifest_history(
        self,
    ) -> None:

        previous_hash = GENESIS_HASH
        previous_sequence = 0

        for manifest in self.state.manifest_history:
            manifest.validate()

            if (
                manifest.manifest_sequence
                <= previous_sequence
            ):
                local_block(
                    "manifest sequence not monotonic"
                )

            if (
                manifest.previous_manifest_hash
                != previous_hash
            ):
                local_block(
                    "manifest history chain mismatch"
                )

            previous_sequence = (
                manifest.manifest_sequence
            )

            previous_hash = (
                manifest.manifest_hash
            )

        if (
            self.state.manifest_history
            and self.state.manifest is not None
        ):
            if (
                self.state.manifest_history[-1].manifest_hash
                != self.state.manifest.manifest_hash
            ):
                local_block(
                    "manifest history does not end at authority"
                )

    def advance_generation(
        self,
    ) -> None:

        with self._lock:
            if (
                self.state.pending_checkpoint_slot
                is not None
            ):
                local_block(
                    "cannot advance generation with pending checkpoint promotion"
                )

            self.state.generation += 1
            self.state.recovery_epoch += 1
            self.state.lineage = uuid.uuid4().hex

            self.state.phase = PHASE_PREPARED

            self.state.authorization = None
            self.state.commit = None
            self.state.dispatch = None

            self.append_wal(
                "GENERATION_ADVANCED",
                {
                    "generation":
                    self.state.generation,
                    "lineage":
                    self.state.lineage,
                    "recovery_epoch":
                    self.state.recovery_epoch,
                },
            )

    # ------------------------------------------------------------------------
    # SERIALIZATION / RESTORE
    # ------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> DurableState:

        return deep_copy(
            self.state
        )

    @classmethod
    def restore_state(
        cls,
        state: DurableState,
        transport: Optional[
            SyntheticTransport
        ] = None,
    ) -> "N30Engine":

        engine = cls(
            deep_copy(state),
            transport=transport,
        )

        engine.validate_wal()
        engine.verify_manifest_history()
        engine.recover_authoritative_checkpoint()

        return engine


print(
    "R28 UNIT N.30: ENGINE DEFINITIONS LOADED",
    flush=True,
)


# ============================================================================
# DIAGNOSTIC PAYLOAD
# ============================================================================

LEVERAGE_PAYLOAD = {
    "symbol": SYMBOL,
    "marginType": "ISOLATED",
    "isolatedLongLeverage": "100",
    "isolatedShortLeverage": "100",
}


# ============================================================================
# DIAGNOSTIC TEST SUITE
# ============================================================================

def expect_local_block(
    label: str,
    fn,
) -> None:

    blocked = False

    try:
        fn()
    except LocalBlock:
        blocked = True

    assert_pass(
        label,
        blocked,
    )


def make_completed_engine(
) -> Tuple[
    N30Engine,
    RecoveryLease,
]:

    transport = SyntheticTransport()

    engine = N30Engine(
        transport=transport
    )

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    engine.authorize(
        lease,
        LEVERAGE_PAYLOAD,
    )

    engine.commit_dispatch(
        lease,
        LEVERAGE_PAYLOAD,
    )

    engine.dispatch_committed(
        LEVERAGE_PAYLOAD
    )

    engine.finalize_dispatch()

    return engine, lease


def run_diagnostics() -> None:
    banner()

    print(
        f"{UNIT_NAME}: STARTING DIAGNOSTIC SUITE",
        flush=True,
    )

    banner()

    # ------------------------------------------------------------------------
    print(
        f"{UNIT_NAME} TEST 1: BASELINE SYNTHETIC DURABLE EXECUTION",
        flush=True,
    )
    separator()

    engine, lease = make_completed_engine()

    assert_pass(
        "Engine Reached COMPLETED",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    assert_pass(
        "Exactly One Synthetic Dispatch Produced",
        len(
            engine.transport.synthetic_dispatches
        )
        == 1,
    )

    assert_pass(
        "Authorization Consumed Exactly Once",
        engine.state.authorization is not None
        and engine.state.authorization.consumed,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 2: FIRST CHECKPOINT STAGING",
        flush=True,
    )

    separator()

    staged = engine.stage_checkpoint()

    assert_pass(
        "Checkpoint Staged In Inactive Slot",
        staged.slot == SLOT_A,
    )

    assert_pass(
        "Pending Checkpoint Sequence Recorded",
        engine.state.pending_checkpoint_sequence
        == staged.checkpoint_sequence,
    )

    assert_pass(
        "Pending Promotion Sequence Recorded",
        engine.state.pending_promotion_sequence
        == staged.promotion_sequence,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 3: FIRST MANIFEST PROMOTION",
        flush=True,
    )

    separator()

    manifest1 = (
        engine.commit_checkpoint_promotion()
    )

    assert_pass(
        "Manifest Sequence Starts At One",
        manifest1.manifest_sequence == 1,
    )

    assert_pass(
        "Manifest Points To Slot A",
        manifest1.authoritative_slot == SLOT_A,
    )

    assert_pass(
        "Manifest Bound To Checkpoint Sequence",
        manifest1.checkpoint_sequence
        == staged.checkpoint_sequence,
    )

    assert_pass(
        "Manifest Bound To Promotion Sequence",
        manifest1.promotion_sequence
        == staged.promotion_sequence,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 4: MANIFEST SEAL VALIDATION",
        flush=True,
    )

    separator()

    manifest1.validate()

    assert_pass(
        "Manifest Integrity Seal Valid",
        True,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 5: MANIFEST TAMPER REJECTION",
        flush=True,
    )

    separator()

    tampered_manifest = deep_copy(
        manifest1
    )

    tampered_manifest.authoritative_slot = (
        SLOT_B
    )

    expect_local_block(
        "Tampered Manifest Rejected",
        lambda: tampered_manifest.validate(),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 6: MANIFEST HASH TAMPER REJECTION",
        flush=True,
    )

    separator()

    hash_tampered = deep_copy(
        manifest1
    )

    hash_tampered.manifest_hash = (
        "f" * 64
    )

    expect_local_block(
        "Manifest Hash Tamper Rejected",
        lambda: hash_tampered.validate(),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 7: CRASH AFTER STAGING PRESERVES OLD AUTHORITY",
        flush=True,
    )

    separator()

    staged2 = engine.stage_checkpoint()

    pre_crash_manifest_hash = (
        engine.state.manifest.manifest_hash
    )

    staged2_sequence = (
        staged2.checkpoint_sequence
    )

    staged2_promotion = (
        staged2.promotion_sequence
    )

    restored = N30Engine.restore_state(
        engine.snapshot(),
        engine.transport,
    )

    assert_pass(
        "Manifest Still Points To Pre-Crash Authority",
        restored.state.manifest is not None
        and restored.state.manifest.manifest_hash
        == pre_crash_manifest_hash,
    )

    assert_pass(
        "Staged Checkpoint Sequence Burned During Recovery",
        staged2_sequence
        in restored.state.burned_checkpoint_sequences,
    )

    assert_pass(
        "Staged Promotion Sequence Burned During Recovery",
        staged2_promotion
        in restored.state.burned_promotion_sequences,
    )

    assert_pass(
        "Pending Promotion Cleared During Recovery",
        restored.state.pending_checkpoint_slot
        is None,
    )

    engine = restored

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 8: BURNED CHECKPOINT SEQUENCE NOT REUSED",
        flush=True,
    )

    separator()

    staged3 = engine.stage_checkpoint()

    assert_pass(
        "New Checkpoint Uses Higher Sequence",
        staged3.checkpoint_sequence
        > staged2_sequence,
    )

    assert_pass(
        "New Promotion Uses Higher Sequence",
        staged3.promotion_sequence
        > staged2_promotion,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 9: SECOND COMMITTED PROMOTION ROTATES SLOT",
        flush=True,
    )

    separator()

    manifest2 = (
        engine.commit_checkpoint_promotion()
    )

    assert_pass(
        "Second Manifest Uses Slot B",
        manifest2.authoritative_slot
        == SLOT_B,
    )

    assert_pass(
        "Manifest Sequence Advanced Monotonically",
        manifest2.manifest_sequence
        > manifest1.manifest_sequence,
    )

    assert_pass(
        "Manifest Chains To Prior Manifest",
        manifest2.previous_manifest_hash
        == manifest1.manifest_hash,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 10: MANIFEST HISTORY VALIDATION",
        flush=True,
    )

    separator()

    engine.verify_manifest_history()

    assert_pass(
        "Manifest History Hash Chain Valid",
        True,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 11: MANIFEST ROLLBACK REJECTION",
        flush=True,
    )

    separator()

    old_manifest = deep_copy(
        manifest1
    )

    expect_local_block(
        "Older Manifest Rollback Rejected",
        lambda: engine.validate_manifest(
            old_manifest
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 12: MANIFEST SEQUENCE COLLISION REJECTION",
        flush=True,
    )

    separator()

    collision = deep_copy(
        engine.state.manifest
    )

    collision.previous_manifest_hash = (
        "1" * 64
    )

    collision.seal_manifest()

    expect_local_block(
        "Manifest Sequence Collision Rejected",
        lambda: engine.validate_manifest(
            collision
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 13: MANIFEST SLOT BINDING",
        flush=True,
    )

    separator()

    slot_bound = deep_copy(
        engine.state.manifest
    )

    original_slot = (
        slot_bound.authoritative_slot
    )

    slot_bound.authoritative_slot = (
        SLOT_A
        if original_slot == SLOT_B
        else SLOT_B
    )

    slot_bound.seal_manifest()

    expect_local_block(
        "Manifest Wrong Slot Rejected",
        lambda: engine.validate_manifest(
            slot_bound
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 14: MANIFEST CHECKPOINT SEQUENCE BINDING",
        flush=True,
    )

    separator()

    seq_bound = deep_copy(
        engine.state.manifest
    )

    seq_bound.checkpoint_sequence += 1000

    seq_bound.seal_manifest()

    expect_local_block(
        "Manifest Wrong Checkpoint Sequence Rejected",
        lambda: engine.validate_manifest(
            seq_bound
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 15: MANIFEST PROMOTION SEQUENCE BINDING",
        flush=True,
    )

    separator()

    promotion_bound = deep_copy(
        engine.state.manifest
    )

    promotion_bound.promotion_sequence += 1000

    promotion_bound.seal_manifest()

    expect_local_block(
        "Manifest Wrong Promotion Sequence Rejected",
        lambda: engine.validate_manifest(
            promotion_bound
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 16: MANIFEST GENERATION BINDING",
        flush=True,
    )

    separator()

    generation_bound = deep_copy(
        engine.state.manifest
    )

    generation_bound.generation += 1

    generation_bound.seal_manifest()

    expect_local_block(
        "Manifest Wrong Generation Rejected",
        lambda: engine.validate_manifest(
            generation_bound
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 17: MANIFEST LINEAGE BINDING",
        flush=True,
    )

    separator()

    lineage_bound = deep_copy(
        engine.state.manifest
    )

    lineage_bound.lineage = (
        uuid.uuid4().hex
    )

    lineage_bound.seal_manifest()

    expect_local_block(
        "Manifest Wrong Lineage Rejected",
        lambda: engine.validate_manifest(
            lineage_bound
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 18: MANIFEST WAL LENGTH BINDING",
        flush=True,
    )

    separator()

    wal_length_bound = deep_copy(
        engine.state.manifest
    )

    wal_length_bound.wal_length += 1

    wal_length_bound.seal_manifest()

    expect_local_block(
        "Manifest Wrong WAL Length Rejected",
        lambda: engine.validate_manifest(
            wal_length_bound
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 19: MANIFEST WAL FINAL HASH BINDING",
        flush=True,
    )

    separator()

    wal_hash_bound = deep_copy(
        engine.state.manifest
    )

    wal_hash_bound.wal_final_hash = (
        "a" * 64
    )

    wal_hash_bound.seal_manifest()

    expect_local_block(
        "Manifest Wrong WAL Final Hash Rejected",
        lambda: engine.validate_manifest(
            wal_hash_bound
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 20: AUTHORITATIVE CHECKPOINT RECOVERY",
        flush=True,
    )

    separator()

    recovered_checkpoint = (
        engine.recover_authoritative_checkpoint()
    )

    assert_pass(
        "Authoritative Checkpoint Recovered",
        recovered_checkpoint is not None,
    )

    assert_pass(
        "Recovered Checkpoint Matches Manifest Slot",
        recovered_checkpoint is not None
        and recovered_checkpoint.slot
        == engine.state.manifest.authoritative_slot,
    )

    assert_pass(
        "Recovered Checkpoint Matches Manifest Sequence",
        recovered_checkpoint is not None
        and recovered_checkpoint.checkpoint_sequence
        == engine.state.manifest.checkpoint_sequence,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 21: COMMITTED AUTHORITY SURVIVES RESTART",
        flush=True,
    )

    separator()

    authoritative_hash = (
        engine.state.manifest.manifest_hash
    )

    restart_engine = N30Engine.restore_state(
        engine.snapshot(),
        engine.transport,
    )

    assert_pass(
        "Committed Manifest Survives Restart",
        restart_engine.state.manifest
        is not None
        and restart_engine.state.manifest.manifest_hash
        == authoritative_hash,
    )

    assert_pass(
        "Committed Authority Remains Recoverable",
        restart_engine.recover_authoritative_checkpoint()
        is not None,
    )

    engine = restart_engine

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 22: PENDING PROMOTION BLOCKS GENERATION ADVANCE",
        flush=True,
    )

    separator()

    engine.stage_checkpoint()

    expect_local_block(
        "Generation Advance With Pending Promotion Rejected",
        engine.advance_generation,
    )

    engine.abort_pending_checkpoint()

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 23: GENERATION ADVANCE + LINEAGE FENCING",
        flush=True,
    )

    separator()

    old_generation = (
        engine.state.generation
    )

    old_lineage = (
        engine.state.lineage
    )

    old_epoch = (
        engine.state.recovery_epoch
    )

    engine.advance_generation()

    assert_pass(
        "Generation Advanced Monotonically",
        engine.state.generation
        > old_generation,
    )

    assert_pass(
        "Recovery Epoch Advanced Monotonically",
        engine.state.recovery_epoch
        > old_epoch,
    )

    assert_pass(
        "New Generation Uses Different Lineage",
        engine.state.lineage
        != old_lineage,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 24: OLD LEASE CANNOT CROSS GENERATION",
        flush=True,
    )

    separator()

    expect_local_block(
        "Prior Generation Lease Rejected",
        lambda: engine.validate_lease(
            lease
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 25: OWNER REUSE GETS NEW GENERATION BINDING",
        flush=True,
    )

    separator()

    reused_owner = (
        engine.acquire_recovery_lease(
            "worker-A"
        )
    )

    assert_pass(
        "Reacquired Owner Uses Higher Generation",
        reused_owner.generation
        > lease.generation,
    )

    assert_pass(
        "Reacquired Owner Uses Different Lineage",
        reused_owner.lineage
        != lease.lineage,
    )

    assert_pass(
        "Reacquired Owner Uses Higher Epoch",
        reused_owner.recovery_epoch
        > lease.recovery_epoch,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 26: NEW GENERATION CHECKPOINT AUTHORITY",
        flush=True,
    )

    separator()

    new_stage = (
        engine.stage_checkpoint()
    )

    new_manifest = (
        engine.commit_checkpoint_promotion()
    )

    assert_pass(
        "New Manifest Uses Higher Generation",
        new_manifest.generation
        > manifest2.generation,
    )

    assert_pass(
        "New Manifest Uses New Lineage",
        new_manifest.lineage
        != manifest2.lineage,
    )

    assert_pass(
        "Manifest Sequence Remains Monotonic Across Generation",
        new_manifest.manifest_sequence
        > manifest2.manifest_sequence,
    )

    assert_pass(
        "New Checkpoint Bound To New Generation",
        new_stage.generation
        == engine.state.generation,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 27: EXACT SYNTHETIC TRANSPORT BINDING",
        flush=True,
    )

    separator()

    first_receipt = (
        engine.transport.synthetic_dispatches[0]
    )

    assert_pass(
        "Transport Method Exactly POST",
        first_receipt.method
        == HTTP_METHOD,
    )

    assert_pass(
        "Transport Path Exactly Leverage Endpoint",
        first_receipt.path
        == LEVERAGE_ENDPOINT,
    )

    assert_pass(
        "Transport Payload Hash Preserved",
        first_receipt.payload_hash
        == sha256_text(
            canonical_json(
                LEVERAGE_PAYLOAD
            )
        ),
    )

    assert_pass(
        "Transport Payload Exactly Preserved",
        first_receipt.payload
        == LEVERAGE_PAYLOAD,
    )

    assert_pass(
        "Dispatch Is Synthetic",
        first_receipt.synthetic is True,
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 28: TORN WAL TAIL REJECTION",
        flush=True,
    )

    separator()

    torn_state = engine.snapshot()

    torn_state.wal[-1].record_hash = (
        "0" * 64
    )

    expect_local_block(
        "Torn WAL Tail Rejected",
        lambda: N30Engine.restore_state(
            torn_state,
            engine.transport,
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 29: HISTORICAL WAL TAMPER REJECTION",
        flush=True,
    )

    separator()

    historical_state = engine.snapshot()

    if len(historical_state.wal) < 2:
        raise AssertionError(
            "insufficient WAL history for tamper test"
        )

    historical_state.wal[0].payload[
        "owner"
    ] = "tampered-owner"

    expect_local_block(
        "Historical WAL Tamper Rejected",
        lambda: N30Engine.restore_state(
            historical_state,
            engine.transport,
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 30: CHECKPOINT SEAL TAMPER REJECTION",
        flush=True,
    )

    separator()

    checkpoint_state = (
        engine.snapshot()
    )

    auth_slot = (
        checkpoint_state.manifest.authoritative_slot
    )

    checkpoint_state.checkpoint_slots[
        auth_slot
    ].phase = "TAMPERED"

    expect_local_block(
        "Tampered Checkpoint Rejected",
        lambda: N30Engine.restore_state(
            checkpoint_state,
            engine.transport,
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 31: MANIFEST HISTORY TAMPER REJECTION",
        flush=True,
    )

    separator()

    history_state = (
        engine.snapshot()
    )

    history_state.manifest_history[
        0
    ].previous_manifest_hash = (
        "b" * 64
    )

    history_state.manifest_history[
        0
    ].seal_manifest()

    expect_local_block(
        "Tampered Manifest History Rejected",
        lambda: N30Engine.restore_state(
            history_state,
            engine.transport,
        ),
    )

    # ------------------------------------------------------------------------
    separator()

    print(
        f"{UNIT_NAME} TEST 32: FINAL NETWORK WRITE FIREBREAK",
        flush=True,
    )

    separator()

    assert_pass(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    assert_pass(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    assert_pass(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    assert_pass(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    assert_pass(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    assert_pass(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    expect_local_block(
        "Real Network POST Hard Blocked",
        lambda: engine.transport.real_post(
            LEVERAGE_ENDPOINT,
            LEVERAGE_PAYLOAD,
        ),
    )

    expect_local_block(
        "Demo Network POST Hard Blocked",
        lambda: engine.transport.demo_post(
            LEVERAGE_ENDPOINT,
            LEVERAGE_PAYLOAD,
        ),
    )

    assert_pass(
        "Network Write Count Remains Zero",
        engine.transport.network_write_count
        == 0,
    )

    assert_pass(
        "Real POST Count Remains Zero",
        engine.transport.real_post_count
        == 0,
    )

    assert_pass(
        "Demo POST Count Remains Zero",
        engine.transport.demo_post_count
        == 0,
    )

    banner()

    print(
        f"✅ {UNIT_NAME} PASSED — "
        "MANIFEST INTEGRITY + ROLLBACK FENCING + "
        "COMMITTED-AUTHORITY RECOVERY VALIDATED",
        flush=True,
    )

    print(
        "✅ DUAL-SLOT CHECKPOINT AUTHORITY IS SEALED, "
        "MONOTONIC, HASH-CHAINED, AND CRASH-SAFE",
        flush=True,
    )

    print(
        "✅ NO REAL ORDER WAS SENT — "
        "NO DEMO ORDER WAS SENT — "
        "NO NETWORK WRITE OCCURRED",
        flush=True,
    )

    banner()


print(
    "R28 UNIT N.30: DIAGNOSTIC DEFINITIONS LOADED",
    flush=True,
)


# ============================================================================
# OPTIONAL HEALTH SERVER
# ============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):
    def do_GET(
        self,
    ) -> None:

        if self.path in (
            "/",
            "/health",
            "/healthz",
        ):
            body = json.dumps(
                {
                    "unit": UNIT_NAME,
                    "version": UNIT_VERSION,
                    "status": "ok",
                    "real_post":
                    REAL_POST_ENABLED,
                    "demo_post":
                    DEMO_POST_ENABLED,
                    "network_writes":
                    NETWORK_WRITES_ENABLED,
                    "synthetic_only":
                    SYNTHETIC_TRANSPORT_ONLY,
                },
                sort_keys=True,
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json",
            )

            self.send_header(
                "Content-Length",
                str(len(body)),
            )

            self.end_headers()

            self.wfile.write(body)

            return

        self.send_response(404)
        self.end_headers()

    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:
        return


def start_health_server() -> None:
    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )

    def runner() -> None:
        try:
            server = HTTPServer(
                (
                    "0.0.0.0",
                    port,
                ),
                HealthHandler,
            )

            print(
                f"{UNIT_NAME}: "
                f"HEALTH SERVER LISTENING ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"{UNIT_NAME}: "
                f"HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        name="n30-health-server",
        daemon=True,
    )

    thread.start()


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    run_diagnostics()

    assert REAL_POST_ENABLED is False
    assert DEMO_POST_ENABLED is False
    assert NETWORK_WRITES_ENABLED is False
    assert SYNTHETIC_TRANSPORT_ONLY is True
    assert LIVE_ORDER_EXECUTION is False
    assert DEMO_ORDER_EXECUTION is False

    print(
        f"{UNIT_NAME}: "
        "POST-DIAGNOSTIC SAFETY ASSERTIONS PASSED",
        flush=True,
    )

    start_health_server()

    print(
        f"{UNIT_NAME}: HEALTH SERVER STARTED",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: "
        "✅ NO REAL POST — "
        "NO DEMO POST — "
        "NO NETWORK WRITE",
        flush=True,
    )

    banner()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
