# ============================================================================
# R28 UNIT N.31
# TRANSACTIONAL CHECKPOINT PROMOTION + COMMITTED-MANIFEST ANCHORING
# + CRASH-WINDOW RECOVERY + ROLLBACK / STALE-INTENT FENCING
#
# COMPLETE COPY/PASTE VERSION
# SINGLE MAIN.PY
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.31 INCREMENT OVER N.30:
#   - DURABLE CHECKPOINT PROMOTION INTENT
#   - SEALED PROMOTION TRANSACTION
#   - PRE-PROMOTION / POST-PROMOTION CRASH RECOVERY
#   - EXACTLY-ONE AUTHORITATIVE PROMOTION
#   - COMMITTED MANIFEST ANCHOR
#   - STALE PROMOTION INTENT REJECTION
#   - CROSS-GENERATION PROMOTION FENCING
#   - MANIFEST SEQUENCE ROLLBACK REJECTION
#   - CHECKPOINT SEQUENCE ROLLBACK REJECTION
#   - PROMOTION INTENT TAMPER REJECTION
#   - MANIFEST HISTORY HASH-CHAIN VALIDATION
#   - WAL HASH-CHAIN VALIDATION
#   - EXACT SYNTHETIC TRANSPORT BINDING
# ============================================================================

print("R28 UNIT N.31: MAIN.PY ENTERED", flush=True)

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
from typing import Any, Dict, List, Optional, Tuple


print("R28 UNIT N.31: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.31"
UNIT_VERSION = "N.31"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

TARGET_LEVERAGE = "100"
TARGET_MARGIN_MODE = "ISOLATED"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
SYNTHETIC_TRANSPORT_ONLY = True

INTEGRITY_KEY = b"R28-N31-LOCAL-INTEGRITY-KEY"
CHECKPOINT_KEY = b"R28-N31-CHECKPOINT-INTEGRITY-KEY"
MANIFEST_KEY = b"R28-N31-MANIFEST-INTEGRITY-KEY"
PROMOTION_KEY = b"R28-N31-PROMOTION-INTEGRITY-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

SLOT_A = "A"
SLOT_B = "B"

PROMOTION_PENDING = "PENDING"
PROMOTION_COMMITTED = "COMMITTED"
PROMOTION_ABORTED = "ABORTED"

ZERO_HASH = "0" * 64

NETWORK_WRITE_COUNT = 0
REAL_POST_COUNT = 0
DEMO_POST_COUNT = 0

SEP = "=" * 92
SUBSEP = "-" * 92


print("R28 UNIT N.31: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# BASIC HELPERS
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


def sha256_object(value: Any) -> str:
    return sha256_text(canonical_json(value))


def hmac_hex(key: bytes, value: str) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def clone(value: Any) -> Any:
    return copy.deepcopy(value)


def print_test(number: int, title: str) -> None:
    print(SUBSEP, flush=True)
    print(f"{UNIT_NAME} TEST {number}: {title}", flush=True)
    print(SUBSEP, flush=True)


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


def result(label: str, passed: bool) -> None:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<78}{status}", flush=True)
    if not passed:
        raise AssertionError(label)


def expect_block(label: str, fn, contains: Optional[str] = None) -> None:
    try:
        fn()
    except Exception as exc:
        local_block(str(exc))

        if contains is not None:
            result(label, contains in str(exc))
        else:
            result(label, True)
        return

    result(label, False)


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class RecoveryLease:
    lease_id: str
    owner: str
    generation: int
    lineage: str
    recovery_epoch: int
    nonce: int
    active: bool = True


@dataclass
class Authorization:
    authorization_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    lease_id: str
    owner: str
    payload_hash: str
    consumed: bool = False


@dataclass
class WALRecord:
    index: int
    kind: str
    generation: int
    lineage: str
    payload: Dict[str, Any]
    previous_hash: str
    record_hash: str


@dataclass
class Checkpoint:
    slot: str
    sequence: int
    generation: int
    lineage: str
    recovery_epoch: int
    wal_length: int
    wal_final_hash: str
    phase: str
    dispatch_count: int
    payload_hash: str
    state_hash: str
    integrity_seal: str


@dataclass
class ManifestRecord:
    sequence: int
    generation: int
    lineage: str
    slot: str
    checkpoint_sequence: int
    checkpoint_hash: str
    previous_manifest_hash: str
    manifest_hash: str
    integrity_seal: str


@dataclass
class PromotionIntent:
    promotion_id: str
    status: str
    generation: int
    lineage: str
    recovery_epoch: int
    source_slot: Optional[str]
    target_slot: str
    checkpoint_sequence: int
    checkpoint_hash: str
    expected_manifest_sequence: int
    previous_manifest_hash: str
    intent_hash: str
    integrity_seal: str


@dataclass
class SyntheticReceipt:
    receipt_id: str
    method: str
    path: str
    payload: Dict[str, Any]
    payload_hash: str
    synthetic: bool
    transmitted: bool
    generation: int
    lineage: str


@dataclass
class DurableState:
    generation: int = 1
    lineage: str = field(default_factory=lambda: new_id("lineage"))
    recovery_epoch: int = 1
    owner_nonce: int = 0

    phase: str = PHASE_PREPARED

    payload: Dict[str, Any] = field(default_factory=dict)
    payload_hash: str = ""

    active_lease: Optional[RecoveryLease] = None
    authorization: Optional[Authorization] = None

    wal: List[WALRecord] = field(default_factory=list)

    checkpoint_slots: Dict[str, Optional[Checkpoint]] = field(
        default_factory=lambda: {
            SLOT_A: None,
            SLOT_B: None,
        }
    )

    manifest_history: List[ManifestRecord] = field(default_factory=list)
    promotion_intent: Optional[PromotionIntent] = None

    dispatch_receipts: List[SyntheticReceipt] = field(default_factory=list)
    dispatch_count: int = 0

    next_checkpoint_sequence: int = 1
    next_manifest_sequence: int = 1


# ============================================================================
# PAYLOAD CONSTRUCTION
# ============================================================================

def build_leverage_payload() -> Dict[str, Any]:
    return {
        "symbol": SYMBOL,
        "marginMode": TARGET_MARGIN_MODE,
        "leverage": TARGET_LEVERAGE,
    }


# ============================================================================
# WAL
# ============================================================================

def wal_record_material(
    index: int,
    kind: str,
    generation: int,
    lineage: str,
    payload: Dict[str, Any],
    previous_hash: str,
) -> Dict[str, Any]:
    return {
        "index": index,
        "kind": kind,
        "generation": generation,
        "lineage": lineage,
        "payload": payload,
        "previous_hash": previous_hash,
    }


def calculate_wal_record_hash(
    index: int,
    kind: str,
    generation: int,
    lineage: str,
    payload: Dict[str, Any],
    previous_hash: str,
) -> str:
    return sha256_object(
        wal_record_material(
            index=index,
            kind=kind,
            generation=generation,
            lineage=lineage,
            payload=payload,
            previous_hash=previous_hash,
        )
    )


def validate_wal(wal: List[WALRecord]) -> None:
    previous_hash = ZERO_HASH

    for expected_index, record in enumerate(wal, start=1):
        if record.index != expected_index:
            raise ValueError("WAL record index mismatch")

        if record.previous_hash != previous_hash:
            raise ValueError("WAL hash chain mismatch")

        calculated = calculate_wal_record_hash(
            index=record.index,
            kind=record.kind,
            generation=record.generation,
            lineage=record.lineage,
            payload=record.payload,
            previous_hash=record.previous_hash,
        )

        if not hmac.compare_digest(
            calculated,
            record.record_hash,
        ):
            raise ValueError("WAL record hash mismatch")

        previous_hash = record.record_hash


# ============================================================================
# CHECKPOINT INTEGRITY
# ============================================================================

def checkpoint_state_material(
    slot: str,
    sequence: int,
    generation: int,
    lineage: str,
    recovery_epoch: int,
    wal_length: int,
    wal_final_hash: str,
    phase: str,
    dispatch_count: int,
    payload_hash: str,
) -> Dict[str, Any]:
    return {
        "slot": slot,
        "sequence": sequence,
        "generation": generation,
        "lineage": lineage,
        "recovery_epoch": recovery_epoch,
        "wal_length": wal_length,
        "wal_final_hash": wal_final_hash,
        "phase": phase,
        "dispatch_count": dispatch_count,
        "payload_hash": payload_hash,
    }


def calculate_checkpoint_state_hash(
    slot: str,
    sequence: int,
    generation: int,
    lineage: str,
    recovery_epoch: int,
    wal_length: int,
    wal_final_hash: str,
    phase: str,
    dispatch_count: int,
    payload_hash: str,
) -> str:
    return sha256_object(
        checkpoint_state_material(
            slot=slot,
            sequence=sequence,
            generation=generation,
            lineage=lineage,
            recovery_epoch=recovery_epoch,
            wal_length=wal_length,
            wal_final_hash=wal_final_hash,
            phase=phase,
            dispatch_count=dispatch_count,
            payload_hash=payload_hash,
        )
    )


def checkpoint_seal_material(checkpoint: Checkpoint) -> str:
    return canonical_json(
        {
            "slot": checkpoint.slot,
            "sequence": checkpoint.sequence,
            "generation": checkpoint.generation,
            "lineage": checkpoint.lineage,
            "recovery_epoch": checkpoint.recovery_epoch,
            "wal_length": checkpoint.wal_length,
            "wal_final_hash": checkpoint.wal_final_hash,
            "phase": checkpoint.phase,
            "dispatch_count": checkpoint.dispatch_count,
            "payload_hash": checkpoint.payload_hash,
            "state_hash": checkpoint.state_hash,
        }
    )


def validate_checkpoint(
    checkpoint: Checkpoint,
    wal: List[WALRecord],
) -> None:
    calculated_state_hash = calculate_checkpoint_state_hash(
        slot=checkpoint.slot,
        sequence=checkpoint.sequence,
        generation=checkpoint.generation,
        lineage=checkpoint.lineage,
        recovery_epoch=checkpoint.recovery_epoch,
        wal_length=checkpoint.wal_length,
        wal_final_hash=checkpoint.wal_final_hash,
        phase=checkpoint.phase,
        dispatch_count=checkpoint.dispatch_count,
        payload_hash=checkpoint.payload_hash,
    )

    if not hmac.compare_digest(
        calculated_state_hash,
        checkpoint.state_hash,
    ):
        raise ValueError("checkpoint state hash mismatch")

    calculated_seal = hmac_hex(
        CHECKPOINT_KEY,
        checkpoint_seal_material(checkpoint),
    )

    if not hmac.compare_digest(
        calculated_seal,
        checkpoint.integrity_seal,
    ):
        raise ValueError("checkpoint integrity seal mismatch")

    if checkpoint.wal_length != len(wal):
        raise ValueError("checkpoint WAL length mismatch")

    expected_final_hash = (
        wal[-1].record_hash
        if wal
        else ZERO_HASH
    )

    if checkpoint.wal_final_hash != expected_final_hash:
        raise ValueError("checkpoint WAL final hash mismatch")


# ============================================================================
# MANIFEST INTEGRITY
# ============================================================================

def manifest_hash_material(
    sequence: int,
    generation: int,
    lineage: str,
    slot: str,
    checkpoint_sequence: int,
    checkpoint_hash: str,
    previous_manifest_hash: str,
) -> Dict[str, Any]:
    return {
        "sequence": sequence,
        "generation": generation,
        "lineage": lineage,
        "slot": slot,
        "checkpoint_sequence": checkpoint_sequence,
        "checkpoint_hash": checkpoint_hash,
        "previous_manifest_hash": previous_manifest_hash,
    }


def calculate_manifest_hash(
    sequence: int,
    generation: int,
    lineage: str,
    slot: str,
    checkpoint_sequence: int,
    checkpoint_hash: str,
    previous_manifest_hash: str,
) -> str:
    return sha256_object(
        manifest_hash_material(
            sequence=sequence,
            generation=generation,
            lineage=lineage,
            slot=slot,
            checkpoint_sequence=checkpoint_sequence,
            checkpoint_hash=checkpoint_hash,
            previous_manifest_hash=previous_manifest_hash,
        )
    )


def manifest_seal_material(record: ManifestRecord) -> str:
    return canonical_json(
        {
            "sequence": record.sequence,
            "generation": record.generation,
            "lineage": record.lineage,
            "slot": record.slot,
            "checkpoint_sequence": record.checkpoint_sequence,
            "checkpoint_hash": record.checkpoint_hash,
            "previous_manifest_hash": record.previous_manifest_hash,
            "manifest_hash": record.manifest_hash,
        }
    )


def validate_manifest_history(
    history: List[ManifestRecord],
    checkpoint_slots: Dict[str, Optional[Checkpoint]],
) -> None:
    previous_hash = ZERO_HASH
    previous_sequence = 0

    for record in history:
        if record.sequence <= previous_sequence:
            raise ValueError("manifest sequence rollback detected")

        if record.previous_manifest_hash != previous_hash:
            raise ValueError("manifest history chain mismatch")

        calculated_hash = calculate_manifest_hash(
            sequence=record.sequence,
            generation=record.generation,
            lineage=record.lineage,
            slot=record.slot,
            checkpoint_sequence=record.checkpoint_sequence,
            checkpoint_hash=record.checkpoint_hash,
            previous_manifest_hash=record.previous_manifest_hash,
        )

        if not hmac.compare_digest(
            calculated_hash,
            record.manifest_hash,
        ):
            raise ValueError("manifest record hash mismatch")

        calculated_seal = hmac_hex(
            MANIFEST_KEY,
            manifest_seal_material(record),
        )

        if not hmac.compare_digest(
            calculated_seal,
            record.integrity_seal,
        ):
            raise ValueError("manifest integrity seal mismatch")

        previous_hash = record.manifest_hash
        previous_sequence = record.sequence

    if history:
        latest = history[-1]
        checkpoint = checkpoint_slots.get(latest.slot)

        if checkpoint is None:
            raise ValueError("manifest references empty checkpoint slot")

        if checkpoint.sequence != latest.checkpoint_sequence:
            raise ValueError("manifest checkpoint sequence mismatch")

        if checkpoint.state_hash != latest.checkpoint_hash:
            raise ValueError("manifest checkpoint hash mismatch")


# ============================================================================
# PROMOTION INTENT INTEGRITY
# ============================================================================

def promotion_hash_material(
    promotion_id: str,
    status: str,
    generation: int,
    lineage: str,
    recovery_epoch: int,
    source_slot: Optional[str],
    target_slot: str,
    checkpoint_sequence: int,
    checkpoint_hash: str,
    expected_manifest_sequence: int,
    previous_manifest_hash: str,
) -> Dict[str, Any]:
    return {
        "promotion_id": promotion_id,
        "status": status,
        "generation": generation,
        "lineage": lineage,
        "recovery_epoch": recovery_epoch,
        "source_slot": source_slot,
        "target_slot": target_slot,
        "checkpoint_sequence": checkpoint_sequence,
        "checkpoint_hash": checkpoint_hash,
        "expected_manifest_sequence": expected_manifest_sequence,
        "previous_manifest_hash": previous_manifest_hash,
    }


def calculate_promotion_intent_hash(
    promotion_id: str,
    status: str,
    generation: int,
    lineage: str,
    recovery_epoch: int,
    source_slot: Optional[str],
    target_slot: str,
    checkpoint_sequence: int,
    checkpoint_hash: str,
    expected_manifest_sequence: int,
    previous_manifest_hash: str,
) -> str:
    return sha256_object(
        promotion_hash_material(
            promotion_id=promotion_id,
            status=status,
            generation=generation,
            lineage=lineage,
            recovery_epoch=recovery_epoch,
            source_slot=source_slot,
            target_slot=target_slot,
            checkpoint_sequence=checkpoint_sequence,
            checkpoint_hash=checkpoint_hash,
            expected_manifest_sequence=expected_manifest_sequence,
            previous_manifest_hash=previous_manifest_hash,
        )
    )


def promotion_seal_material(intent: PromotionIntent) -> str:
    return canonical_json(
        {
            "promotion_id": intent.promotion_id,
            "status": intent.status,
            "generation": intent.generation,
            "lineage": intent.lineage,
            "recovery_epoch": intent.recovery_epoch,
            "source_slot": intent.source_slot,
            "target_slot": intent.target_slot,
            "checkpoint_sequence": intent.checkpoint_sequence,
            "checkpoint_hash": intent.checkpoint_hash,
            "expected_manifest_sequence": intent.expected_manifest_sequence,
            "previous_manifest_hash": intent.previous_manifest_hash,
            "intent_hash": intent.intent_hash,
        }
    )


def validate_promotion_intent(intent: PromotionIntent) -> None:
    calculated_hash = calculate_promotion_intent_hash(
        promotion_id=intent.promotion_id,
        status=intent.status,
        generation=intent.generation,
        lineage=intent.lineage,
        recovery_epoch=intent.recovery_epoch,
        source_slot=intent.source_slot,
        target_slot=intent.target_slot,
        checkpoint_sequence=intent.checkpoint_sequence,
        checkpoint_hash=intent.checkpoint_hash,
        expected_manifest_sequence=intent.expected_manifest_sequence,
        previous_manifest_hash=intent.previous_manifest_hash,
    )

    if not hmac.compare_digest(
        calculated_hash,
        intent.intent_hash,
    ):
        raise ValueError("promotion intent hash mismatch")

    calculated_seal = hmac_hex(
        PROMOTION_KEY,
        promotion_seal_material(intent),
    )

    if not hmac.compare_digest(
        calculated_seal,
        intent.integrity_seal,
    ):
        raise ValueError("promotion intent integrity seal mismatch")


# ============================================================================
# ENGINE
# ============================================================================

class N31Engine:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.state = DurableState()

        self.state.payload = build_leverage_payload()
        self.state.payload_hash = sha256_object(self.state.payload)

        self.append_wal(
            "ENGINE_INITIALIZED",
            {
                "payload_hash": self.state.payload_hash,
                "phase": self.state.phase,
            },
        )

    # ------------------------------------------------------------------------
    # WAL
    # ------------------------------------------------------------------------

    def append_wal(
        self,
        kind: str,
        payload: Dict[str, Any],
    ) -> WALRecord:
        with self.lock:
            previous_hash = (
                self.state.wal[-1].record_hash
                if self.state.wal
                else ZERO_HASH
            )

            index = len(self.state.wal) + 1

            record_hash = calculate_wal_record_hash(
                index=index,
                kind=kind,
                generation=self.state.generation,
                lineage=self.state.lineage,
                payload=clone(payload),
                previous_hash=previous_hash,
            )

            record = WALRecord(
                index=index,
                kind=kind,
                generation=self.state.generation,
                lineage=self.state.lineage,
                payload=clone(payload),
                previous_hash=previous_hash,
                record_hash=record_hash,
            )

            self.state.wal.append(record)
            return record

    # ------------------------------------------------------------------------
    # LEASE
    # ------------------------------------------------------------------------

    def acquire_recovery_lease(
        self,
        owner: str,
    ) -> RecoveryLease:
        with self.lock:
            if self.state.active_lease is not None:
                if self.state.active_lease.active:
                    raise ValueError("recovery lease already active")

            self.state.owner_nonce += 1

            lease = RecoveryLease(
                lease_id=new_id("lease"),
                owner=owner,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                nonce=self.state.owner_nonce,
                active=True,
            )

            self.state.active_lease = lease

            self.append_wal(
                "RECOVERY_LEASE_ACQUIRED",
                {
                    "lease_id": lease.lease_id,
                    "owner": lease.owner,
                    "generation": lease.generation,
                    "lineage": lease.lineage,
                    "recovery_epoch": lease.recovery_epoch,
                    "nonce": lease.nonce,
                },
            )

            return clone(lease)

    def validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        active = self.state.active_lease

        if active is None or not active.active:
            raise ValueError("no active recovery lease")

        if lease.lease_id != active.lease_id:
            raise ValueError("recovery lease fence mismatch")

        if lease.generation != self.state.generation:
            raise ValueError("recovery lease generation mismatch")

        if lease.lineage != self.state.lineage:
            raise ValueError("recovery lease lineage mismatch")

        if lease.recovery_epoch != self.state.recovery_epoch:
            raise ValueError("recovery lease epoch mismatch")

        if lease.owner != active.owner:
            raise ValueError("recovery lease owner mismatch")

        if lease.nonce != active.nonce:
            raise ValueError("recovery lease nonce mismatch")

    # ------------------------------------------------------------------------
    # AUTHORIZATION
    # ------------------------------------------------------------------------

    def authorize(
        self,
        lease: RecoveryLease,
    ) -> Authorization:
        with self.lock:
            self.validate_lease(lease)

            authorization = Authorization(
                authorization_id=new_id("authorization"),
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                lease_id=lease.lease_id,
                owner=lease.owner,
                payload_hash=self.state.payload_hash,
                consumed=False,
            )

            self.state.authorization = authorization
            self.state.phase = PHASE_AUTHORIZED

            self.append_wal(
                "AUTHORIZED",
                {
                    "authorization_id": authorization.authorization_id,
                    "payload_hash": authorization.payload_hash,
                },
            )

            return clone(authorization)

    def consume_authorization(
        self,
        authorization: Authorization,
    ) -> None:
        with self.lock:
            current = self.state.authorization

            if current is None:
                raise ValueError("generation is not authorized")

            if authorization.authorization_id != current.authorization_id:
                raise ValueError("authorization identity mismatch")

            if current.consumed:
                raise ValueError("authorization already consumed")

            if authorization.generation != self.state.generation:
                raise ValueError("authorization generation mismatch")

            if authorization.lineage != self.state.lineage:
                raise ValueError("authorization lineage mismatch")

            if authorization.recovery_epoch != self.state.recovery_epoch:
                raise ValueError("authorization recovery epoch mismatch")

            if authorization.payload_hash != self.state.payload_hash:
                raise ValueError("authorization payload hash mismatch")

            current.consumed = True

            self.append_wal(
                "AUTHORIZATION_CONSUMED",
                {
                    "authorization_id": current.authorization_id,
                },
            )

    # ------------------------------------------------------------------------
    # SYNTHETIC DISPATCH
    # ------------------------------------------------------------------------

    def synthetic_dispatch(
        self,
        authorization: Authorization,
    ) -> SyntheticReceipt:
        with self.lock:
            self.consume_authorization(authorization)

            receipt = SyntheticReceipt(
                receipt_id=new_id("receipt"),
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload=clone(self.state.payload),
                payload_hash=self.state.payload_hash,
                synthetic=True,
                transmitted=False,
                generation=self.state.generation,
                lineage=self.state.lineage,
            )

            self.state.dispatch_receipts.append(receipt)
            self.state.dispatch_count += 1
            self.state.phase = PHASE_DISPATCHED

            self.append_wal(
                "SYNTHETIC_DISPATCH",
                {
                    "receipt_id": receipt.receipt_id,
                    "method": receipt.method,
                    "path": receipt.path,
                    "payload_hash": receipt.payload_hash,
                    "synthetic": True,
                    "transmitted": False,
                },
            )

            self.state.phase = PHASE_COMPLETED

            self.append_wal(
                "GENERATION_COMPLETED",
                {
                    "dispatch_count": self.state.dispatch_count,
                },
            )

            return clone(receipt)

    # ------------------------------------------------------------------------
    # CHECKPOINT
    # ------------------------------------------------------------------------

    def choose_inactive_slot(self) -> str:
        authoritative = self.authoritative_manifest()

        if authoritative is None:
            return SLOT_A

        if authoritative.slot == SLOT_A:
            return SLOT_B

        return SLOT_A

    def create_checkpoint(
        self,
        slot: Optional[str] = None,
    ) -> Checkpoint:
        with self.lock:
            validate_wal(self.state.wal)

            if slot is None:
                slot = self.choose_inactive_slot()

            if slot not in (SLOT_A, SLOT_B):
                raise ValueError("invalid checkpoint slot")

            sequence = self.state.next_checkpoint_sequence
            self.state.next_checkpoint_sequence += 1

            wal_length = len(self.state.wal)
            wal_final_hash = (
                self.state.wal[-1].record_hash
                if self.state.wal
                else ZERO_HASH
            )

            state_hash = calculate_checkpoint_state_hash(
                slot=slot,
                sequence=sequence,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                wal_length=wal_length,
                wal_final_hash=wal_final_hash,
                phase=self.state.phase,
                dispatch_count=self.state.dispatch_count,
                payload_hash=self.state.payload_hash,
            )

            checkpoint = Checkpoint(
                slot=slot,
                sequence=sequence,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                wal_length=wal_length,
                wal_final_hash=wal_final_hash,
                phase=self.state.phase,
                dispatch_count=self.state.dispatch_count,
                payload_hash=self.state.payload_hash,
                state_hash=state_hash,
                integrity_seal="",
            )

            checkpoint.integrity_seal = hmac_hex(
                CHECKPOINT_KEY,
                checkpoint_seal_material(checkpoint),
            )

            self.state.checkpoint_slots[slot] = checkpoint

            return clone(checkpoint)

    # ------------------------------------------------------------------------
    # MANIFEST
    # ------------------------------------------------------------------------

    def authoritative_manifest(self) -> Optional[ManifestRecord]:
        if not self.state.manifest_history:
            return None

        return self.state.manifest_history[-1]

    def authoritative_checkpoint(self) -> Optional[Checkpoint]:
        manifest = self.authoritative_manifest()

        if manifest is None:
            return None

        checkpoint = self.state.checkpoint_slots.get(manifest.slot)

        if checkpoint is None:
            raise ValueError("authoritative manifest references empty slot")

        return checkpoint

    # ------------------------------------------------------------------------
    # PROMOTION
    # ------------------------------------------------------------------------

    def prepare_checkpoint_promotion(
        self,
        checkpoint: Checkpoint,
    ) -> PromotionIntent:
        with self.lock:
            if self.state.promotion_intent is not None:
                if self.state.promotion_intent.status == PROMOTION_PENDING:
                    raise ValueError("checkpoint promotion already pending")

            current_checkpoint = self.state.checkpoint_slots.get(
                checkpoint.slot
            )

            if current_checkpoint is None:
                raise ValueError("checkpoint slot is empty")

            validate_checkpoint(
                current_checkpoint,
                self.state.wal,
            )

            if checkpoint.sequence != current_checkpoint.sequence:
                raise ValueError("checkpoint sequence mismatch")

            if checkpoint.state_hash != current_checkpoint.state_hash:
                raise ValueError("checkpoint hash mismatch")

            if checkpoint.generation != self.state.generation:
                raise ValueError("checkpoint generation mismatch")

            if checkpoint.lineage != self.state.lineage:
                raise ValueError("checkpoint lineage mismatch")

            authoritative = self.authoritative_manifest()

            source_slot = (
                authoritative.slot
                if authoritative is not None
                else None
            )

            previous_manifest_hash = (
                authoritative.manifest_hash
                if authoritative is not None
                else ZERO_HASH
            )

            expected_manifest_sequence = self.state.next_manifest_sequence

            promotion_id = new_id("promotion")

            intent_hash = calculate_promotion_intent_hash(
                promotion_id=promotion_id,
                status=PROMOTION_PENDING,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                source_slot=source_slot,
                target_slot=checkpoint.slot,
                checkpoint_sequence=checkpoint.sequence,
                checkpoint_hash=checkpoint.state_hash,
                expected_manifest_sequence=expected_manifest_sequence,
                previous_manifest_hash=previous_manifest_hash,
            )

            intent = PromotionIntent(
                promotion_id=promotion_id,
                status=PROMOTION_PENDING,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                source_slot=source_slot,
                target_slot=checkpoint.slot,
                checkpoint_sequence=checkpoint.sequence,
                checkpoint_hash=checkpoint.state_hash,
                expected_manifest_sequence=expected_manifest_sequence,
                previous_manifest_hash=previous_manifest_hash,
                intent_hash=intent_hash,
                integrity_seal="",
            )

            intent.integrity_seal = hmac_hex(
                PROMOTION_KEY,
                promotion_seal_material(intent),
            )

            self.state.promotion_intent = intent

            self.append_wal(
                "CHECKPOINT_PROMOTION_PREPARED",
                {
                    "promotion_id": intent.promotion_id,
                    "target_slot": intent.target_slot,
                    "checkpoint_sequence": intent.checkpoint_sequence,
                    "expected_manifest_sequence": (
                        intent.expected_manifest_sequence
                    ),
                },
            )

            return clone(intent)

    def commit_checkpoint_promotion(
        self,
        intent: PromotionIntent,
    ) -> ManifestRecord:
        with self.lock:
            current = self.state.promotion_intent

            if current is None:
                raise ValueError("no pending checkpoint promotion")

            validate_promotion_intent(current)

            if current.status != PROMOTION_PENDING:
                raise ValueError("checkpoint promotion is not pending")

            if intent.promotion_id != current.promotion_id:
                raise ValueError("promotion identity mismatch")

            if intent.intent_hash != current.intent_hash:
                raise ValueError("promotion intent hash mismatch")

            if current.generation != self.state.generation:
                raise ValueError("promotion generation mismatch")

            if current.lineage != self.state.lineage:
                raise ValueError("promotion lineage mismatch")

            if current.recovery_epoch != self.state.recovery_epoch:
                raise ValueError("promotion recovery epoch mismatch")

            checkpoint = self.state.checkpoint_slots.get(
                current.target_slot
            )

            if checkpoint is None:
                raise ValueError("promotion target checkpoint missing")

            validate_checkpoint(
                checkpoint,
                self.state.wal,
            )

            if checkpoint.sequence != current.checkpoint_sequence:
                raise ValueError("promotion checkpoint sequence mismatch")

            if checkpoint.state_hash != current.checkpoint_hash:
                raise ValueError("promotion checkpoint hash mismatch")

            authoritative = self.authoritative_manifest()

            actual_previous_hash = (
                authoritative.manifest_hash
                if authoritative is not None
                else ZERO_HASH
            )

            if current.previous_manifest_hash != actual_previous_hash:
                raise ValueError("promotion previous manifest mismatch")

            if (
                current.expected_manifest_sequence
                != self.state.next_manifest_sequence
            ):
                raise ValueError("promotion manifest sequence mismatch")

            sequence = self.state.next_manifest_sequence

            manifest_hash = calculate_manifest_hash(
                sequence=sequence,
                generation=self.state.generation,
                lineage=self.state.lineage,
                slot=current.target_slot,
                checkpoint_sequence=current.checkpoint_sequence,
                checkpoint_hash=current.checkpoint_hash,
                previous_manifest_hash=actual_previous_hash,
            )

            record = ManifestRecord(
                sequence=sequence,
                generation=self.state.generation,
                lineage=self.state.lineage,
                slot=current.target_slot,
                checkpoint_sequence=current.checkpoint_sequence,
                checkpoint_hash=current.checkpoint_hash,
                previous_manifest_hash=actual_previous_hash,
                manifest_hash=manifest_hash,
                integrity_seal="",
            )

            record.integrity_seal = hmac_hex(
                MANIFEST_KEY,
                manifest_seal_material(record),
            )

            self.state.manifest_history.append(record)
            self.state.next_manifest_sequence += 1

            current.status = PROMOTION_COMMITTED

            current.intent_hash = calculate_promotion_intent_hash(
                promotion_id=current.promotion_id,
                status=current.status,
                generation=current.generation,
                lineage=current.lineage,
                recovery_epoch=current.recovery_epoch,
                source_slot=current.source_slot,
                target_slot=current.target_slot,
                checkpoint_sequence=current.checkpoint_sequence,
                checkpoint_hash=current.checkpoint_hash,
                expected_manifest_sequence=current.expected_manifest_sequence,
                previous_manifest_hash=current.previous_manifest_hash,
            )

            current.integrity_seal = hmac_hex(
                PROMOTION_KEY,
                promotion_seal_material(current),
            )

            self.append_wal(
                "CHECKPOINT_PROMOTION_COMMITTED",
                {
                    "promotion_id": current.promotion_id,
                    "manifest_sequence": record.sequence,
                    "slot": record.slot,
                    "checkpoint_sequence": record.checkpoint_sequence,
                },
            )

            self.state.promotion_intent = None

            return clone(record)

    # ------------------------------------------------------------------------
    # RECOVERY
    # ------------------------------------------------------------------------

    def recover_pending_promotion(self) -> Optional[ManifestRecord]:
        with self.lock:
            intent = self.state.promotion_intent

            if intent is None:
                return None

            validate_promotion_intent(intent)

            if intent.status != PROMOTION_PENDING:
                raise ValueError(
                    "recoverable promotion must be pending"
                )

            checkpoint = self.state.checkpoint_slots.get(
                intent.target_slot
            )

            if checkpoint is None:
                raise ValueError(
                    "pending promotion target checkpoint missing"
                )

            validate_checkpoint(
                checkpoint,
                self.state.wal,
            )

            return self.commit_checkpoint_promotion(
                clone(intent)
            )

    def recover_authoritative_checkpoint(self) -> Checkpoint:
        with self.lock:
            validate_wal(self.state.wal)

            validate_manifest_history(
                self.state.manifest_history,
                self.state.checkpoint_slots,
            )

            manifest = self.authoritative_manifest()

            if manifest is None:
                raise ValueError("no committed checkpoint authority")

            checkpoint = self.state.checkpoint_slots.get(
                manifest.slot
            )

            if checkpoint is None:
                raise ValueError(
                    "authoritative checkpoint slot missing"
                )

            validate_checkpoint(
                checkpoint,
                self.state.wal,
            )

            if checkpoint.sequence != manifest.checkpoint_sequence:
                raise ValueError(
                    "authoritative checkpoint sequence mismatch"
                )

            if checkpoint.state_hash != manifest.checkpoint_hash:
                raise ValueError(
                    "authoritative checkpoint hash mismatch"
                )

            return clone(checkpoint)

    # ------------------------------------------------------------------------
    # GENERATION ADVANCE
    # ------------------------------------------------------------------------

    def advance_generation(self) -> None:
        with self.lock:
            if self.state.promotion_intent is not None:
                if (
                    self.state.promotion_intent.status
                    == PROMOTION_PENDING
                ):
                    raise ValueError(
                        "cannot advance generation with pending "
                        "checkpoint promotion"
                    )

            old_generation = self.state.generation
            old_lineage = self.state.lineage

            self.state.generation += 1
            self.state.recovery_epoch += 1
            self.state.lineage = new_id("lineage")

            self.state.phase = PHASE_PREPARED
            self.state.authorization = None
            self.state.active_lease = None
            self.state.dispatch_count = 0
            self.state.dispatch_receipts = []

            self.append_wal(
                "GENERATION_ADVANCED",
                {
                    "from_generation": old_generation,
                    "to_generation": self.state.generation,
                    "from_lineage": old_lineage,
                    "to_lineage": self.state.lineage,
                    "recovery_epoch": self.state.recovery_epoch,
                },
            )

    # ------------------------------------------------------------------------
    # SERIALIZATION / RESTART
    # ------------------------------------------------------------------------

    def export_state(self) -> DurableState:
        with self.lock:
            return clone(self.state)

    @classmethod
    def restore_state(
        cls,
        state: DurableState,
    ) -> "N31Engine":
        engine = cls.__new__(cls)
        engine.lock = threading.RLock()
        engine.state = clone(state)

        validate_wal(engine.state.wal)

        for checkpoint in engine.state.checkpoint_slots.values():
            if checkpoint is not None:
                validate_checkpoint(
                    checkpoint,
                    engine.state.wal,
                )

        validate_manifest_history(
            engine.state.manifest_history,
            engine.state.checkpoint_slots,
        )

        if engine.state.promotion_intent is not None:
            validate_promotion_intent(
                engine.state.promotion_intent
            )

        return engine


print("R28 UNIT N.31: ENGINE DEFINITIONS LOADED", flush=True)


# ============================================================================
# HARD NETWORK FIREBREAKS
# ============================================================================

def real_network_post(
    path: str,
    payload: Dict[str, Any],
) -> None:
    global NETWORK_WRITE_COUNT
    global REAL_POST_COUNT

    if not NETWORK_WRITES_ENABLED:
        raise RuntimeError("real network POST is disabled")

    if not REAL_POST_ENABLED:
        raise RuntimeError("real network POST is disabled")

    NETWORK_WRITE_COUNT += 1
    REAL_POST_COUNT += 1

    raise RuntimeError(
        "network transport intentionally unavailable in N.31"
    )


def demo_network_post(
    path: str,
    payload: Dict[str, Any],
) -> None:
    global NETWORK_WRITE_COUNT
    global DEMO_POST_COUNT

    if not NETWORK_WRITES_ENABLED:
        raise RuntimeError("demo network POST is disabled")

    if not DEMO_POST_ENABLED:
        raise RuntimeError("demo network POST is disabled")

    NETWORK_WRITE_COUNT += 1
    DEMO_POST_COUNT += 1

    raise RuntimeError(
        "network transport intentionally unavailable in N.31"
    )


# ============================================================================
# BASELINE BUILDER
# ============================================================================

def make_completed_engine() -> Tuple[
    N31Engine,
    RecoveryLease,
    Authorization,
    SyntheticReceipt,
]:
    engine = N31Engine()

    lease = engine.acquire_recovery_lease(
        "worker-alpha"
    )

    authorization = engine.authorize(
        lease
    )

    receipt = engine.synthetic_dispatch(
        authorization
    )

    return (
        engine,
        lease,
        authorization,
        receipt,
    )


def make_promoted_engine() -> Tuple[
    N31Engine,
    Checkpoint,
    PromotionIntent,
    ManifestRecord,
]:
    engine, _, _, _ = make_completed_engine()

    checkpoint = engine.create_checkpoint()

    intent = engine.prepare_checkpoint_promotion(
        checkpoint
    )

    manifest = engine.commit_checkpoint_promotion(
        intent
    )

    return (
        engine,
        checkpoint,
        intent,
        manifest,
    )


# ============================================================================
# DIAGNOSTIC SUITE
# ============================================================================

def run_diagnostics() -> None:
    global NETWORK_WRITE_COUNT
    global REAL_POST_COUNT
    global DEMO_POST_COUNT

    NETWORK_WRITE_COUNT = 0
    REAL_POST_COUNT = 0
    DEMO_POST_COUNT = 0

    print(SEP, flush=True)
    print(
        "R28 UNIT N.31 — TRANSACTIONAL CHECKPOINT PROMOTION "
        "+ COMMITTED-MANIFEST ANCHORING",
        flush=True,
    )
    print(SEP, flush=True)

    # ========================================================================
    # TEST 1
    # ========================================================================

    print_test(
        1,
        "ENGINE INITIALIZATION",
    )

    engine = N31Engine()

    result(
        "Engine Starts PREPARED",
        engine.state.phase == PHASE_PREPARED,
    )

    result(
        "Initial Generation Is One",
        engine.state.generation == 1,
    )

    result(
        "Initial Recovery Epoch Is One",
        engine.state.recovery_epoch == 1,
    )

    result(
        "Payload Hash Established",
        engine.state.payload_hash
        == sha256_object(build_leverage_payload()),
    )

    # ========================================================================
    # TEST 2
    # ========================================================================

    print_test(
        2,
        "RECOVERY LEASE BINDING",
    )

    lease = engine.acquire_recovery_lease(
        "worker-alpha"
    )

    result(
        "Lease Bound To Current Generation",
        lease.generation == engine.state.generation,
    )

    result(
        "Lease Bound To Current Lineage",
        lease.lineage == engine.state.lineage,
    )

    result(
        "Lease Bound To Current Recovery Epoch",
        lease.recovery_epoch
        == engine.state.recovery_epoch,
    )

    # ========================================================================
    # TEST 3
    # ========================================================================

    print_test(
        3,
        "AUTHORIZATION BINDING",
    )

    authorization = engine.authorize(
        lease
    )

    result(
        "Authorization Bound To Generation",
        authorization.generation
        == engine.state.generation,
    )

    result(
        "Authorization Bound To Lineage",
        authorization.lineage
        == engine.state.lineage,
    )

    result(
        "Authorization Payload Hash Preserved",
        authorization.payload_hash
        == engine.state.payload_hash,
    )

    # ========================================================================
    # TEST 4
    # ========================================================================

    print_test(
        4,
        "SYNTHETIC DISPATCH",
    )

    receipt = engine.synthetic_dispatch(
        authorization
    )

    result(
        "Synthetic Dispatch Completed",
        engine.state.phase == PHASE_COMPLETED,
    )

    result(
        "Exactly One Dispatch Produced",
        engine.state.dispatch_count == 1,
    )

    result(
        "Dispatch Is Synthetic",
        receipt.synthetic is True
        and receipt.transmitted is False,
    )

    # ========================================================================
    # TEST 5
    # ========================================================================

    print_test(
        5,
        "CHECKPOINT CREATION",
    )

    checkpoint = engine.create_checkpoint()

    result(
        "Checkpoint Created In Valid Slot",
        checkpoint.slot in (SLOT_A, SLOT_B),
    )

    result(
        "Checkpoint Bound To Current Generation",
        checkpoint.generation
        == engine.state.generation,
    )

    result(
        "Checkpoint Bound To Current Lineage",
        checkpoint.lineage
        == engine.state.lineage,
    )

    result(
        "Checkpoint WAL Length Preserved",
        checkpoint.wal_length
        == len(engine.state.wal),
    )

    # ========================================================================
    # TEST 6
    # ========================================================================

    print_test(
        6,
        "CHECKPOINT INTEGRITY VALIDATION",
    )

    validate_checkpoint(
        engine.state.checkpoint_slots[
            checkpoint.slot
        ],
        engine.state.wal,
    )

    result(
        "Checkpoint Integrity Validates",
        True,
    )

    # ========================================================================
    # TEST 7
    # ========================================================================

    print_test(
        7,
        "PROMOTION INTENT CREATION",
    )

    intent = engine.prepare_checkpoint_promotion(
        checkpoint
    )

    result(
        "Promotion Intent Is Pending",
        intent.status == PROMOTION_PENDING,
    )

    result(
        "Promotion Targets Correct Slot",
        intent.target_slot == checkpoint.slot,
    )

    result(
        "Promotion Targets Correct Checkpoint Sequence",
        intent.checkpoint_sequence
        == checkpoint.sequence,
    )

    result(
        "Promotion Bound To Current Generation",
        intent.generation
        == engine.state.generation,
    )

    # ========================================================================
    # TEST 8
    # ========================================================================

    print_test(
        8,
        "PROMOTION INTENT INTEGRITY",
    )

    validate_promotion_intent(
        engine.state.promotion_intent
    )

    result(
        "Promotion Intent Seal Validates",
        True,
    )

    # ========================================================================
    # TEST 9
    # ========================================================================

    print_test(
        9,
        "COMMITTED MANIFEST PROMOTION",
    )

    manifest = engine.commit_checkpoint_promotion(
        intent
    )

    result(
        "Manifest Promotion Committed",
        manifest.sequence == 1,
    )

    result(
        "Manifest References Promoted Slot",
        manifest.slot == checkpoint.slot,
    )

    result(
        "Manifest References Exact Checkpoint",
        manifest.checkpoint_sequence
        == checkpoint.sequence,
    )

    result(
        "Pending Promotion Cleared",
        engine.state.promotion_intent is None,
    )

    # ========================================================================
    # TEST 10
    # ========================================================================

    print_test(
        10,
        "AUTHORITATIVE CHECKPOINT RECOVERY",
    )

    recovered = engine.recover_authoritative_checkpoint()

    result(
        "Authoritative Checkpoint Recovered",
        recovered.state_hash
        == checkpoint.state_hash,
    )

    result(
        "Recovered Checkpoint Matches Manifest Slot",
        recovered.slot
        == manifest.slot,
    )

    result(
        "Recovered Checkpoint Matches Manifest Sequence",
        recovered.sequence
        == manifest.checkpoint_sequence,
    )

    # ========================================================================
    # TEST 11
    # ========================================================================

    print_test(
        11,
        "PRE-COMMIT PROMOTION CRASH RECOVERY",
    )

    crash_engine, _, _, _ = make_completed_engine()

    crash_checkpoint = crash_engine.create_checkpoint()

    crash_intent = (
        crash_engine.prepare_checkpoint_promotion(
            crash_checkpoint
        )
    )

    saved = crash_engine.export_state()

    restarted = N31Engine.restore_state(saved)

    recovered_manifest = (
        restarted.recover_pending_promotion()
    )

    result(
        "Pending Promotion Survives Restart",
        recovered_manifest is not None,
    )

    result(
        "Recovered Promotion Commits Exactly Once",
        len(restarted.state.manifest_history) == 1,
    )

    result(
        "Recovered Promotion Clears Pending Intent",
        restarted.state.promotion_intent is None,
    )

    # ========================================================================
    # TEST 12
    # ========================================================================

    print_test(
        12,
        "POST-COMMIT RESTART RECOVERY",
    )

    committed_engine, _, _, committed_manifest = (
        make_promoted_engine()
    )

    committed_saved = committed_engine.export_state()

    committed_restart = N31Engine.restore_state(
        committed_saved
    )

    committed_checkpoint = (
        committed_restart.recover_authoritative_checkpoint()
    )

    result(
        "Committed Manifest Survives Restart",
        len(
            committed_restart.state.manifest_history
        ) == 1,
    )

    result(
        "Committed Authority Remains Recoverable",
        committed_checkpoint.sequence
        == committed_manifest.checkpoint_sequence,
    )

    # ========================================================================
    # TEST 13
    # ========================================================================

    print_test(
        13,
        "DUPLICATE PROMOTION COMMIT REJECTION",
    )

    duplicate_engine, _, old_intent, _ = (
        make_promoted_engine()
    )

    expect_block(
        "Second Commit Of Same Promotion Rejected",
        lambda: duplicate_engine.commit_checkpoint_promotion(
            old_intent
        ),
        "no pending checkpoint promotion",
    )

    # ========================================================================
    # TEST 14
    # ========================================================================

    print_test(
        14,
        "SECOND CHECKPOINT PROMOTION",
    )

    second_engine, first_cp, _, first_manifest = (
        make_promoted_engine()
    )

    second_engine.append_wal(
        "SECOND_CHECKPOINT_MARKER",
        {
            "marker": 2,
        },
    )

    second_cp = second_engine.create_checkpoint()

    second_intent = (
        second_engine.prepare_checkpoint_promotion(
            second_cp
        )
    )

    second_manifest = (
        second_engine.commit_checkpoint_promotion(
            second_intent
        )
    )

    result(
        "Second Manifest Sequence Is Higher",
        second_manifest.sequence
        > first_manifest.sequence,
    )

    result(
        "Second Checkpoint Sequence Is Higher",
        second_cp.sequence
        > first_cp.sequence,
    )

    result(
        "Manifest History Contains Two Authorities",
        len(
            second_engine.state.manifest_history
        ) == 2,
    )

    # ========================================================================
    # TEST 15
    # ========================================================================

    print_test(
        15,
        "DUAL-SLOT ALTERNATION",
    )

    result(
        "Second Promotion Uses Opposite Slot",
        second_cp.slot != first_cp.slot,
    )

    result(
        "Authoritative Manifest Points To New Slot",
        second_engine.authoritative_manifest().slot
        == second_cp.slot,
    )

    # ========================================================================
    # TEST 16
    # ========================================================================

    print_test(
        16,
        "PROMOTION INTENT TAMPER REJECTION",
    )

    tamper_engine, _, _, _ = make_completed_engine()

    tamper_cp = tamper_engine.create_checkpoint()

    tamper_engine.prepare_checkpoint_promotion(
        tamper_cp
    )

    tampered_state = tamper_engine.export_state()

    tampered_state.promotion_intent.target_slot = (
        SLOT_B
        if tampered_state.promotion_intent.target_slot
        == SLOT_A
        else SLOT_A
    )

    expect_block(
        "Tampered Promotion Intent Rejected",
        lambda: N31Engine.restore_state(
            tampered_state
        ),
        "promotion intent hash mismatch",
    )

    # ========================================================================
    # TEST 17
    # ========================================================================

    print_test(
        17,
        "CHECKPOINT HASH TAMPER REJECTION",
    )

    cp_tamper_engine, cp_tamper, _, _ = (
        make_promoted_engine()
    )

    cp_tampered_state = (
        cp_tamper_engine.export_state()
    )

    cp_tampered_state.checkpoint_slots[
        cp_tamper.slot
    ].state_hash = "f" * 64

    expect_block(
        "Tampered Checkpoint Hash Rejected",
        lambda: N31Engine.restore_state(
            cp_tampered_state
        ),
        "checkpoint state hash mismatch",
    )

    # ========================================================================
    # TEST 18
    # ========================================================================

    print_test(
        18,
        "CHECKPOINT SEAL TAMPER REJECTION",
    )

    seal_engine, seal_cp, _, _ = (
        make_promoted_engine()
    )

    seal_state = seal_engine.export_state()

    seal_state.checkpoint_slots[
        seal_cp.slot
    ].integrity_seal = "0" * 64

    expect_block(
        "Tampered Checkpoint Seal Rejected",
        lambda: N31Engine.restore_state(
            seal_state
        ),
        "checkpoint integrity seal mismatch",
    )

    # ========================================================================
    # TEST 19
    # ========================================================================

    print_test(
        19,
        "MANIFEST HASH TAMPER REJECTION",
    )

    manifest_tamper_engine, _, _, _ = (
        make_promoted_engine()
    )

    manifest_tamper_state = (
        manifest_tamper_engine.export_state()
    )

    manifest_tamper_state.manifest_history[
        0
    ].manifest_hash = "1" * 64

    expect_block(
        "Tampered Manifest Hash Rejected",
        lambda: N31Engine.restore_state(
            manifest_tamper_state
        ),
        "manifest record hash mismatch",
    )

    # ========================================================================
    # TEST 20
    # ========================================================================

    print_test(
        20,
        "MANIFEST SEAL TAMPER REJECTION",
    )

    manifest_seal_engine, _, _, _ = (
        make_promoted_engine()
    )

    manifest_seal_state = (
        manifest_seal_engine.export_state()
    )

    manifest_seal_state.manifest_history[
        0
    ].integrity_seal = "2" * 64

    expect_block(
        "Tampered Manifest Seal Rejected",
        lambda: N31Engine.restore_state(
            manifest_seal_state
        ),
        "manifest integrity seal mismatch",
    )

    # ========================================================================
    # TEST 21
    # ========================================================================

    print_test(
        21,
        "MANIFEST HISTORY CHAIN TAMPER REJECTION",
    )

    chain_engine, _, _, _ = make_promoted_engine()

    chain_engine.append_wal(
        "CHAIN_SECOND_RECORD",
        {
            "value": 2,
        },
    )

    chain_cp = chain_engine.create_checkpoint()

    chain_intent = (
        chain_engine.prepare_checkpoint_promotion(
            chain_cp
        )
    )

    chain_engine.commit_checkpoint_promotion(
        chain_intent
    )

    chain_state = chain_engine.export_state()

    chain_state.manifest_history[
        1
    ].previous_manifest_hash = ZERO_HASH

    expect_block(
        "Tampered Manifest History Rejected",
        lambda: N31Engine.restore_state(
            chain_state
        ),
        "manifest history chain mismatch",
    )

    # ========================================================================
    # TEST 22
    # ========================================================================

    print_test(
        22,
        "MANIFEST SEQUENCE ROLLBACK REJECTION",
    )

    rollback_engine, _, _, _ = (
        make_promoted_engine()
    )

    rollback_engine.append_wal(
        "ROLLBACK_SECOND_MARKER",
        {
            "value": 2,
        },
    )

    rollback_cp = rollback_engine.create_checkpoint()

    rollback_intent = (
        rollback_engine.prepare_checkpoint_promotion(
            rollback_cp
        )
    )

    rollback_engine.commit_checkpoint_promotion(
        rollback_intent
    )

    rollback_state = rollback_engine.export_state()

    rollback_state.manifest_history[
        1
    ].sequence = 1

    expect_block(
        "Manifest Sequence Rollback Rejected",
        lambda: N31Engine.restore_state(
            rollback_state
        ),
        "manifest sequence rollback detected",
    )

    # ========================================================================
    # TEST 23
    # ========================================================================

    print_test(
        23,
        "PENDING PROMOTION BLOCKS GENERATION ADVANCE",
    )

    pending_engine, _, _, _ = make_completed_engine()

    pending_cp = pending_engine.create_checkpoint()

    pending_engine.prepare_checkpoint_promotion(
        pending_cp
    )

    expect_block(
        "Generation Advance With Pending Promotion Rejected",
        pending_engine.advance_generation,
        "cannot advance generation with pending checkpoint promotion",
    )

    # ========================================================================
    # TEST 24
    # ========================================================================

    print_test(
        24,
        "GENERATION ADVANCE + LINEAGE FENCING",
    )

    generation_engine, _, _, _ = (
        make_promoted_engine()
    )

    old_generation = generation_engine.state.generation
    old_lineage = generation_engine.state.lineage
    old_epoch = generation_engine.state.recovery_epoch

    generation_engine.advance_generation()

    result(
        "Generation Advanced Monotonically",
        generation_engine.state.generation
        > old_generation,
    )

    result(
        "Recovery Epoch Advanced Monotonically",
        generation_engine.state.recovery_epoch
        > old_epoch,
    )

    result(
        "New Generation Uses Different Lineage",
        generation_engine.state.lineage
        != old_lineage,
    )

    # ========================================================================
    # TEST 25
    # ========================================================================

    print_test(
        25,
        "OLD LEASE CANNOT CROSS GENERATION",
    )

    old_lease_engine, old_lease, _, _ = (
        make_completed_engine()
    )

    old_lease_engine.create_checkpoint()

    cp_for_manifest = (
        old_lease_engine.state.checkpoint_slots[
            SLOT_A
        ]
    )

    old_lease_intent = (
        old_lease_engine.prepare_checkpoint_promotion(
            clone(cp_for_manifest)
        )
    )

    old_lease_engine.commit_checkpoint_promotion(
        old_lease_intent
    )

    old_lease_engine.advance_generation()

    expect_block(
        "Prior Generation Lease Rejected",
        lambda: old_lease_engine.validate_lease(
            old_lease
        ),
        "recovery lease",
    )

    # ========================================================================
    # TEST 26
    # ========================================================================

    print_test(
        26,
        "OWNER REUSE GETS NEW GENERATION BINDING",
    )

    reuse_engine, first_lease, _, _ = (
        make_completed_engine()
    )

    reuse_cp = reuse_engine.create_checkpoint()

    reuse_intent = (
        reuse_engine.prepare_checkpoint_promotion(
            reuse_cp
        )
    )

    reuse_engine.commit_checkpoint_promotion(
        reuse_intent
    )

    reuse_engine.advance_generation()

    second_lease = (
        reuse_engine.acquire_recovery_lease(
            first_lease.owner
        )
    )

    result(
        "Reacquired Owner Uses Higher Generation",
        second_lease.generation
        > first_lease.generation,
    )

    result(
        "Reacquired Owner Uses Different Lineage",
        second_lease.lineage
        != first_lease.lineage,
    )

    result(
        "Reacquired Owner Uses Higher Epoch",
        second_lease.recovery_epoch
        > first_lease.recovery_epoch,
    )

    result(
        "Reacquired Owner Uses Higher Nonce",
        second_lease.nonce
        > first_lease.nonce,
    )

    # ========================================================================
    # TEST 27
    # ========================================================================

    print_test(
        27,
        "NEW GENERATION CHECKPOINT AUTHORITY",
    )

    newgen_engine, _, _, old_manifest = (
        make_promoted_engine()
    )

    newgen_engine.advance_generation()

    new_lease = (
        newgen_engine.acquire_recovery_lease(
            "worker-alpha"
        )
    )

    new_auth = newgen_engine.authorize(
        new_lease
    )

    newgen_engine.synthetic_dispatch(
        new_auth
    )

    new_cp = newgen_engine.create_checkpoint()

    new_intent = (
        newgen_engine.prepare_checkpoint_promotion(
            new_cp
        )
    )

    new_manifest = (
        newgen_engine.commit_checkpoint_promotion(
            new_intent
        )
    )

    result(
        "New Manifest Uses Higher Generation",
        new_manifest.generation
        > old_manifest.generation,
    )

    result(
        "New Manifest Uses New Lineage",
        new_manifest.lineage
        != old_manifest.lineage,
    )

    result(
        "Manifest Sequence Remains Monotonic Across Generation",
        new_manifest.sequence
        > old_manifest.sequence,
    )

    result(
        "New Checkpoint Bound To New Generation",
        new_cp.generation
        == newgen_engine.state.generation,
    )

    # ========================================================================
    # TEST 28
    # ========================================================================

    print_test(
        28,
        "STALE PROMOTION INTENT REJECTION",
    )

    stale_engine, _, _, _ = make_promoted_engine()

    stale_engine.advance_generation()

    stale_lease = (
        stale_engine.acquire_recovery_lease(
            "worker-stale"
        )
    )

    stale_auth = stale_engine.authorize(
        stale_lease
    )

    stale_engine.synthetic_dispatch(
        stale_auth
    )

    stale_cp = stale_engine.create_checkpoint()

    stale_intent = (
        stale_engine.prepare_checkpoint_promotion(
            stale_cp
        )
    )

    stale_snapshot = stale_engine.export_state()

    stale_snapshot.promotion_intent.generation -= 1

    expect_block(
        "Stale Promotion Intent Rejected",
        lambda: N31Engine.restore_state(
            stale_snapshot
        ),
        "promotion intent hash mismatch",
    )

    # ========================================================================
    # TEST 29
    # ========================================================================

    print_test(
        29,
        "TORN WAL TAIL REJECTION",
    )

    wal_engine, _, _, _ = make_promoted_engine()

    wal_state = wal_engine.export_state()

    wal_state.wal[-1].record_hash = "3" * 64

    expect_block(
        "Torn WAL Tail Rejected",
        lambda: N31Engine.restore_state(
            wal_state
        ),
        "WAL record hash mismatch",
    )

    # ========================================================================
    # TEST 30
    # ========================================================================

    print_test(
        30,
        "HISTORICAL WAL TAMPER REJECTION",
    )

    historical_engine, _, _, _ = (
        make_promoted_engine()
    )

    historical_state = (
        historical_engine.export_state()
    )

    historical_state.wal[
        0
    ].payload["payload_hash"] = "tampered"

    expect_block(
        "Historical WAL Tamper Rejected",
        lambda: N31Engine.restore_state(
            historical_state
        ),
        "WAL record hash mismatch",
    )

    # ========================================================================
    # TEST 31
    # ========================================================================

    print_test(
        31,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    transport_engine, _, _, transport_receipt = (
        make_completed_engine()
    )

    result(
        "Transport Method Exactly POST",
        transport_receipt.method
        == HTTP_METHOD,
    )

    result(
        "Transport Path Exactly Leverage Endpoint",
        transport_receipt.path
        == LEVERAGE_ENDPOINT,
    )

    result(
        "Transport Payload Hash Preserved",
        transport_receipt.payload_hash
        == transport_engine.state.payload_hash,
    )

    result(
        "Transport Payload Exactly Preserved",
        transport_receipt.payload
        == build_leverage_payload(),
    )

    result(
        "Dispatch Is Synthetic",
        transport_receipt.synthetic is True
        and transport_receipt.transmitted is False,
    )

    # ========================================================================
    # TEST 32
    # ========================================================================

    print_test(
        32,
        "FINAL NETWORK WRITE FIREBREAK",
    )

    result(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    result(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    result(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    result(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    result(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    result(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    expect_block(
        "Real Network POST Hard Blocked",
        lambda: real_network_post(
            LEVERAGE_ENDPOINT,
            build_leverage_payload(),
        ),
        "real network POST is disabled",
    )

    expect_block(
        "Demo Network POST Hard Blocked",
        lambda: demo_network_post(
            LEVERAGE_ENDPOINT,
            build_leverage_payload(),
        ),
        "demo network POST is disabled",
    )

    result(
        "Network Write Count Remains Zero",
        NETWORK_WRITE_COUNT == 0,
    )

    result(
        "Real POST Count Remains Zero",
        REAL_POST_COUNT == 0,
    )

    result(
        "Demo POST Count Remains Zero",
        DEMO_POST_COUNT == 0,
    )

    # ========================================================================
    # FINAL VALIDATION
    # ========================================================================

    print(SEP, flush=True)

    print(
        "✅ R28 UNIT N.31 PASSED — TRANSACTIONAL CHECKPOINT PROMOTION "
        "+ COMMITTED-MANIFEST AUTHORITY VALIDATED",
        flush=True,
    )

    print(
        "✅ PROMOTION INTENT IS SEALED, CRASH-RECOVERABLE, "
        "EXACTLY-ONCE, AND GENERATION-FENCED",
        flush=True,
    )

    print(
        "✅ MANIFEST AUTHORITY REMAINS MONOTONIC, HASH-CHAINED, "
        "ROLLBACK-RESISTANT, AND RESTART-SAFE",
        flush=True,
    )

    print(
        "✅ NO REAL ORDER WAS SENT — NO DEMO ORDER WAS SENT — "
        "NO NETWORK WRITE OCCURRED",
        flush=True,
    )

    print(SEP, flush=True)


# ============================================================================
# POST-DIAGNOSTIC SAFETY ASSERTIONS
# ============================================================================

def post_diagnostic_safety_assertions() -> None:
    assert REAL_POST_ENABLED is False
    assert DEMO_POST_ENABLED is False
    assert NETWORK_WRITES_ENABLED is False
    assert LIVE_ORDER_EXECUTION is False
    assert DEMO_ORDER_EXECUTION is False
    assert SYNTHETIC_TRANSPORT_ONLY is True

    assert NETWORK_WRITE_COUNT == 0
    assert REAL_POST_COUNT == 0
    assert DEMO_POST_COUNT == 0

    print(
        "R28 UNIT N.31: POST-DIAGNOSTIC SAFETY ASSERTIONS PASSED",
        flush=True,
    )


# ============================================================================
# OPTIONAL HEALTH SERVER
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
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
                    "real_post": REAL_POST_ENABLED,
                    "demo_post": DEMO_POST_ENABLED,
                    "network_writes": NETWORK_WRITES_ENABLED,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
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
                f"R28 UNIT N.31: HEALTH SERVER LISTENING ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"R28 UNIT N.31: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()

    print(
        "R28 UNIT N.31: HEALTH SERVER STARTED",
        flush=True,
    )


# ============================================================================
# PERSISTENT RUNTIME
# ============================================================================

def persistent_runtime() -> None:
    print(
        "R28 UNIT N.31: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT N.31: ✅ NO REAL POST — "
        "NO DEMO POST — NO NETWORK WRITE",
        flush=True,
    )

    print(SEP, flush=True)

    heartbeat = 0

    while True:
        heartbeat += 1

        print(
            f"R28 UNIT N.31: HEARTBEAT {heartbeat} — "
            f"synthetic-only safety envelope intact",
            flush=True,
        )

        time.sleep(60)


# ============================================================================
# MAIN ENTRY
# ============================================================================

def main() -> None:
    run_diagnostics()

    post_diagnostic_safety_assertions()

    start_health_server()

    persistent_runtime()


if __name__ == "__main__":
    main()
