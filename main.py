# ============================================================================
# R28 UNIT N.32
# ATOMIC DUAL-SLOT CHECKPOINT ROTATION
# + COMMITTED-MANIFEST FALLBACK
# + MANIFEST ROLLBACK REJECTION
# + CRASH-SAFE CHECKPOINT PROMOTION
#
# CORRECTED COPY/PASTE VERSION
# PART 1 OF 4
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.32 INCREMENT OVER N.31:
#   - DUAL CHECKPOINT SLOT ROTATION (A/B)
#   - LAST-KNOWN-GOOD COMMITTED MANIFEST RETENTION
#   - CORRUPTED NEW MANIFEST FALLBACK
#   - CORRUPTED NEW CHECKPOINT FALLBACK
#   - INCOMPLETE PROMOTION CANNOT REPLACE COMMITTED AUTHORITY
#   - MANIFEST SEQUENCE ROLLBACK REJECTED
#   - CHECKPOINT SEQUENCE ROLLBACK REJECTED
#   - CROSS-SLOT CHECKPOINT IDENTITY VALIDATION
#   - WAL PREFIX AUTHORITY PRESERVED ACROSS ROTATION
#   - RESTART DURING SLOT ROTATION RECOVERS LAST VALID AUTHORITY
#
# IMPORTANT:
#   THIS UNIT DOES NOT TRANSMIT ANY REAL OR DEMO NETWORK WRITE.
#   ALL DISPATCH ACTIVITY IS SYNTHETIC AND LOCAL ONLY.
# ============================================================================


print("R28 UNIT N.32: MAIN.PY ENTERED", flush=True)


# ============================================================================
# IMPORTS
# ============================================================================

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


print("R28 UNIT N.32: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.32"
UNIT_VERSION = "N.32"

SYMBOL = "BTCUSDT"

HTTP_METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TARGET_LEVERAGE = "100"
TARGET_MARGIN_MODE = "ISOLATED"

INTEGRITY_KEY = b"R28-N32-LOCAL-INTEGRITY-KEY"
AUTHORIZATION_KEY = b"R28-N32-AUTHORIZATION-KEY"
CHECKPOINT_KEY = b"R28-N32-CHECKPOINT-KEY"
MANIFEST_KEY = b"R28-N32-MANIFEST-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

CHECKPOINT_SLOT_A = "A"
CHECKPOINT_SLOT_B = "B"

VALID_CHECKPOINT_SLOTS = {
    CHECKPOINT_SLOT_A,
    CHECKPOINT_SLOT_B,
}

ZERO_HASH = "0" * 64

HEARTBEAT_INTERVAL_SECONDS = 30


print("R28 UNIT N.32: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# LOCAL EXCEPTION TYPES
# ============================================================================

class N32Error(Exception):
    pass


class IntegrityError(N32Error):
    pass


class AuthorizationError(N32Error):
    pass


class ReplayError(N32Error):
    pass


class RecoveryError(N32Error):
    pass


class CheckpointError(N32Error):
    pass


class ManifestError(N32Error):
    pass


class NetworkWriteBlocked(N32Error):
    pass


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
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_object(value: Any) -> str:
    return sha256_text(
        canonical_json(value)
    )


def hmac_hex(
    key: bytes,
    value: str,
) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def secure_equal(
    left: str,
    right: str,
) -> bool:
    return hmac.compare_digest(
        str(left),
        str(right),
    )


def new_id(prefix: str) -> str:
    return "{}-{}".format(
        prefix,
        uuid.uuid4().hex,
    )


def now_ms() -> int:
    return int(time.time() * 1000)


def deep_copy(value: Any) -> Any:
    return copy.deepcopy(value)


def opposite_slot(slot: str) -> str:
    if slot == CHECKPOINT_SLOT_A:
        return CHECKPOINT_SLOT_B

    if slot == CHECKPOINT_SLOT_B:
        return CHECKPOINT_SLOT_A

    raise CheckpointError(
        "invalid checkpoint slot"
    )


def separator() -> None:
    print(
        "-" * 92,
        flush=True,
    )


def diagnostic_header(
    number: int,
    name: str,
) -> None:
    separator()

    print(
        "{} TEST {}: {}".format(
            UNIT_NAME,
            number,
            name,
        ),
        flush=True,
    )

    separator()


def local_block(
    message: str,
) -> None:
    print(
        "{} LOCAL BLOCK:".format(
            UNIT_NAME
        ),
        flush=True,
    )

    print(
        "  {}".format(
            message
        ),
        flush=True,
    )


def check(
    condition: bool,
    label: str,
) -> None:
    if not condition:
        print(
            "{:<76} ❌ FAIL".format(
                label
            ),
            flush=True,
        )

        raise AssertionError(label)

    print(
        "{:<76} ✅ PASS".format(
            label
        ),
        flush=True,
    )


def expect_rejection(
    function: Any,
    label: str,
    expected_text: Optional[str] = None,
) -> None:
    try:
        function()

    except Exception as exc:
        message = str(exc)

        local_block(message)

        if expected_text is not None:
            if expected_text not in message:
                raise AssertionError(
                    "{}: expected {!r} in {!r}".format(
                        label,
                        expected_text,
                        message,
                    )
                )

        check(
            True,
            label,
        )

        return

    check(
        False,
        label,
    )


# ============================================================================
# PAYLOAD
# ============================================================================

def build_leverage_payload() -> Dict[str, str]:
    return {
        "leverage": TARGET_LEVERAGE,
        "marginMode": TARGET_MARGIN_MODE,
        "symbol": SYMBOL,
    }


def payload_hash(
    payload: Dict[str, Any],
) -> str:
    return sha256_object(payload)


# ============================================================================
# WAL RECORD
# ============================================================================

@dataclass
class WALRecord:
    index: int
    event: str
    generation: int
    recovery_epoch: int
    lineage_id: str
    payload_hash: str
    previous_hash: str
    timestamp_ms: int
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
    record_hash: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "event": self.event,
            "generation": self.generation,
            "recovery_epoch": self.recovery_epoch,
            "lineage_id": self.lineage_id,
            "payload_hash": self.payload_hash,
            "previous_hash": self.previous_hash,
            "timestamp_ms": self.timestamp_ms,
            "metadata": deep_copy(
                self.metadata
            ),
        }

    def calculate_hash(self) -> str:
        return sha256_object(
            self.unsigned_dict()
        )

    def seal(self) -> None:
        self.record_hash = self.calculate_hash()

    def validate(self) -> None:
        expected = self.calculate_hash()

        if not secure_equal(
            self.record_hash,
            expected,
        ):
            raise IntegrityError(
                "WAL record hash mismatch"
            )


# ============================================================================
# RECOVERY LEASE
# ============================================================================

@dataclass
class RecoveryLease:
    lease_id: str
    owner_id: str
    generation: int
    recovery_epoch: int
    lineage_id: str
    nonce: int
    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "owner_id": self.owner_id,
            "generation": self.generation,
            "recovery_epoch": self.recovery_epoch,
            "lineage_id": self.lineage_id,
            "nonce": self.nonce,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            INTEGRITY_KEY,
            canonical_json(
                self.unsigned_dict()
            ),
        )

    def seal(self) -> None:
        self.integrity_seal = (
            self.calculate_seal()
        )

    def validate_integrity(self) -> None:
        expected = self.calculate_seal()

        if not secure_equal(
            self.integrity_seal,
            expected,
        ):
            raise IntegrityError(
                "recovery lease integrity seal mismatch"
            )


# ============================================================================
# AUTHORIZATION
# ============================================================================

@dataclass
class Authorization:
    authorization_id: str
    generation: int
    recovery_epoch: int
    lineage_id: str
    lease_id: str
    owner_id: str
    payload_hash: str
    nonce: int
    consumed: bool = False
    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "generation": self.generation,
            "recovery_epoch": self.recovery_epoch,
            "lineage_id": self.lineage_id,
            "lease_id": self.lease_id,
            "owner_id": self.owner_id,
            "payload_hash": self.payload_hash,
            "nonce": self.nonce,
            "consumed": self.consumed,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            AUTHORIZATION_KEY,
            canonical_json(
                self.unsigned_dict()
            ),
        )

    def seal(self) -> None:
        self.integrity_seal = (
            self.calculate_seal()
        )

    def validate_integrity(self) -> None:
        expected = self.calculate_seal()

        if not secure_equal(
            self.integrity_seal,
            expected,
        ):
            raise IntegrityError(
                "authorization integrity seal mismatch"
            )


# ============================================================================
# SYNTHETIC TRANSPORT RECEIPT
# ============================================================================

@dataclass
class SyntheticDispatchReceipt:
    dispatch_id: str
    method: str
    path: str
    payload_hash: str
    generation: int
    recovery_epoch: int
    lineage_id: str
    transmitted: bool
    timestamp_ms: int

    def validate_synthetic(self) -> None:
        if self.transmitted:
            raise NetworkWriteBlocked(
                "synthetic receipt unexpectedly marked transmitted"
            )

        if self.method != HTTP_METHOD:
            raise RecoveryError(
                "transport method mismatch"
            )

        if self.path != LEVERAGE_ENDPOINT:
            raise RecoveryError(
                "transport path mismatch"
            )


# ============================================================================
# CHECKPOINT
# ============================================================================

@dataclass
class Checkpoint:
    slot: str
    checkpoint_sequence: int
    checkpoint_id: str
    generation: int
    recovery_epoch: int
    lineage_id: str
    phase: str
    payload_hash: str

    wal_length: int
    wal_final_hash: str

    authorization_consumed: bool
    dispatch_count: int

    created_ms: int

    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "slot": self.slot,
            "checkpoint_sequence": (
                self.checkpoint_sequence
            ),
            "checkpoint_id": self.checkpoint_id,
            "generation": self.generation,
            "recovery_epoch": self.recovery_epoch,
            "lineage_id": self.lineage_id,
            "phase": self.phase,
            "payload_hash": self.payload_hash,
            "wal_length": self.wal_length,
            "wal_final_hash": self.wal_final_hash,
            "authorization_consumed": (
                self.authorization_consumed
            ),
            "dispatch_count": self.dispatch_count,
            "created_ms": self.created_ms,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            CHECKPOINT_KEY,
            canonical_json(
                self.unsigned_dict()
            ),
        )

    def seal(self) -> None:
        self.integrity_seal = (
            self.calculate_seal()
        )

    def validate_integrity(self) -> None:
        if self.slot not in VALID_CHECKPOINT_SLOTS:
            raise CheckpointError(
                "invalid checkpoint slot"
            )

        expected = self.calculate_seal()

        if not secure_equal(
            self.integrity_seal,
            expected,
        ):
            raise IntegrityError(
                "checkpoint integrity seal mismatch"
            )


# ============================================================================
# COMMITTED MANIFEST
# ============================================================================

@dataclass
class CommittedManifest:
    manifest_sequence: int
    manifest_id: str

    checkpoint_slot: str
    checkpoint_sequence: int
    checkpoint_id: str

    generation: int
    recovery_epoch: int
    lineage_id: str

    checkpoint_wal_length: int
    checkpoint_wal_final_hash: str

    previous_manifest_sequence: Optional[int]
    previous_manifest_id: Optional[str]

    committed_ms: int

    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "manifest_sequence": (
                self.manifest_sequence
            ),
            "manifest_id": self.manifest_id,

            "checkpoint_slot": (
                self.checkpoint_slot
            ),
            "checkpoint_sequence": (
                self.checkpoint_sequence
            ),
            "checkpoint_id": (
                self.checkpoint_id
            ),

            "generation": self.generation,
            "recovery_epoch": (
                self.recovery_epoch
            ),
            "lineage_id": self.lineage_id,

            "checkpoint_wal_length": (
                self.checkpoint_wal_length
            ),
            "checkpoint_wal_final_hash": (
                self.checkpoint_wal_final_hash
            ),

            "previous_manifest_sequence": (
                self.previous_manifest_sequence
            ),
            "previous_manifest_id": (
                self.previous_manifest_id
            ),

            "committed_ms": self.committed_ms,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            MANIFEST_KEY,
            canonical_json(
                self.unsigned_dict()
            ),
        )

    def seal(self) -> None:
        self.integrity_seal = (
            self.calculate_seal()
        )

    def validate_integrity(self) -> None:
        if (
            self.checkpoint_slot
            not in VALID_CHECKPOINT_SLOTS
        ):
            raise ManifestError(
                "manifest checkpoint slot invalid"
            )

        expected = self.calculate_seal()

        if not secure_equal(
            self.integrity_seal,
            expected,
        ):
            raise IntegrityError(
                "committed manifest integrity seal mismatch"
            )


# ============================================================================
# PENDING CHECKPOINT PROMOTION
# ============================================================================

@dataclass
class PendingPromotion:
    promotion_id: str

    target_slot: str
    target_checkpoint_sequence: int
    target_checkpoint_id: str

    expected_generation: int
    expected_recovery_epoch: int
    expected_lineage_id: str

    base_manifest_sequence: Optional[int]
    base_manifest_id: Optional[str]

    checkpoint_wal_length: int
    checkpoint_wal_final_hash: str

    created_ms: int

    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "promotion_id": (
                self.promotion_id
            ),

            "target_slot": (
                self.target_slot
            ),
            "target_checkpoint_sequence": (
                self.target_checkpoint_sequence
            ),
            "target_checkpoint_id": (
                self.target_checkpoint_id
            ),

            "expected_generation": (
                self.expected_generation
            ),
            "expected_recovery_epoch": (
                self.expected_recovery_epoch
            ),
            "expected_lineage_id": (
                self.expected_lineage_id
            ),

            "base_manifest_sequence": (
                self.base_manifest_sequence
            ),
            "base_manifest_id": (
                self.base_manifest_id
            ),

            "checkpoint_wal_length": (
                self.checkpoint_wal_length
            ),
            "checkpoint_wal_final_hash": (
                self.checkpoint_wal_final_hash
            ),

            "created_ms": self.created_ms,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            MANIFEST_KEY,
            canonical_json(
                self.unsigned_dict()
            ),
        )

    def seal(self) -> None:
        self.integrity_seal = (
            self.calculate_seal()
        )

    def validate_integrity(self) -> None:
        if (
            self.target_slot
            not in VALID_CHECKPOINT_SLOTS
        ):
            raise ManifestError(
                "pending promotion target slot invalid"
            )

        expected = self.calculate_seal()

        if not secure_equal(
            self.integrity_seal,
            expected,
        ):
            raise IntegrityError(
                "pending promotion integrity seal mismatch"
            )


# ============================================================================
# DURABLE STATE
# ============================================================================

@dataclass
class DurableState:
    generation: int
    recovery_epoch: int
    lineage_id: str
    phase: str

    payload: Dict[str, Any]
    payload_hash: str

    lease_nonce: int = 0
    authorization_nonce: int = 0

    recovery_lease: Optional[RecoveryLease] = None
    authorization: Optional[Authorization] = None

    wal: List[WALRecord] = field(
        default_factory=list
    )

    checkpoint_slots: Dict[
        str,
        Optional[Checkpoint],
    ] = field(
        default_factory=lambda: {
            CHECKPOINT_SLOT_A: None,
            CHECKPOINT_SLOT_B: None,
        }
    )

    committed_manifest: Optional[
        CommittedManifest
    ] = None

    fallback_manifest: Optional[
        CommittedManifest
    ] = None

    pending_promotion: Optional[
        PendingPromotion
    ] = None

    dispatch_receipts: List[
        SyntheticDispatchReceipt
    ] = field(
        default_factory=list
    )

    highest_manifest_sequence_seen: int = 0

    def clone(self) -> "DurableState":
        return deep_copy(self)


# ============================================================================
# STATE SERIALIZATION HELPERS
# ============================================================================

def recovery_lease_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[RecoveryLease]:
    if value is None:
        return None

    return RecoveryLease(**value)


def authorization_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[Authorization]:
    if value is None:
        return None

    return Authorization(**value)


def wal_record_from_dict(
    value: Dict[str, Any],
) -> WALRecord:
    return WALRecord(**value)


def checkpoint_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[Checkpoint]:
    if value is None:
        return None

    return Checkpoint(**value)


def manifest_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[CommittedManifest]:
    if value is None:
        return None

    return CommittedManifest(**value)


def pending_promotion_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[PendingPromotion]:
    if value is None:
        return None

    return PendingPromotion(**value)


def receipt_from_dict(
    value: Dict[str, Any],
) -> SyntheticDispatchReceipt:
    return SyntheticDispatchReceipt(
        **value
    )


def serialize_state(
    state: DurableState,
) -> Dict[str, Any]:
    return {
        "generation": state.generation,
        "recovery_epoch": (
            state.recovery_epoch
        ),
        "lineage_id": state.lineage_id,
        "phase": state.phase,

        "payload": deep_copy(
            state.payload
        ),
        "payload_hash": (
            state.payload_hash
        ),

        "lease_nonce": (
            state.lease_nonce
        ),
        "authorization_nonce": (
            state.authorization_nonce
        ),

        "recovery_lease": (
            asdict(state.recovery_lease)
            if state.recovery_lease
            is not None
            else None
        ),

        "authorization": (
            asdict(state.authorization)
            if state.authorization
            is not None
            else None
        ),

        "wal": [
            asdict(record)
            for record in state.wal
        ],

        "checkpoint_slots": {
            slot: (
                asdict(checkpoint)
                if checkpoint
                is not None
                else None
            )
            for (
                slot,
                checkpoint
            ) in state.checkpoint_slots.items()
        },

        "committed_manifest": (
            asdict(
                state.committed_manifest
            )
            if state.committed_manifest
            is not None
            else None
        ),

        "fallback_manifest": (
            asdict(
                state.fallback_manifest
            )
            if state.fallback_manifest
            is not None
            else None
        ),

        "pending_promotion": (
            asdict(
                state.pending_promotion
            )
            if state.pending_promotion
            is not None
            else None
        ),

        "dispatch_receipts": [
            asdict(receipt)
            for receipt
            in state.dispatch_receipts
        ],

        "highest_manifest_sequence_seen": (
            state.highest_manifest_sequence_seen
        ),
    }


def restore_state_from_dict(
    value: Dict[str, Any],
) -> DurableState:
    checkpoint_slots_raw = value.get(
        "checkpoint_slots",
        {},
    )

    checkpoint_slots = {
        CHECKPOINT_SLOT_A: checkpoint_from_dict(
            checkpoint_slots_raw.get(
                CHECKPOINT_SLOT_A
            )
        ),
        CHECKPOINT_SLOT_B: checkpoint_from_dict(
            checkpoint_slots_raw.get(
                CHECKPOINT_SLOT_B
            )
        ),
    }

    return DurableState(
        generation=value["generation"],
        recovery_epoch=value[
            "recovery_epoch"
        ],
        lineage_id=value["lineage_id"],
        phase=value["phase"],

        payload=deep_copy(
            value["payload"]
        ),
        payload_hash=value[
            "payload_hash"
        ],

        lease_nonce=value.get(
            "lease_nonce",
            0,
        ),
        authorization_nonce=value.get(
            "authorization_nonce",
            0,
        ),

        recovery_lease=(
            recovery_lease_from_dict(
                value.get(
                    "recovery_lease"
                )
            )
        ),

        authorization=(
            authorization_from_dict(
                value.get(
                    "authorization"
                )
            )
        ),

        wal=[
            wal_record_from_dict(
                record
            )
            for record
            in value.get(
                "wal",
                [],
            )
        ],

        checkpoint_slots=(
            checkpoint_slots
        ),

        committed_manifest=(
            manifest_from_dict(
                value.get(
                    "committed_manifest"
                )
            )
        ),

        fallback_manifest=(
            manifest_from_dict(
                value.get(
                    "fallback_manifest"
                )
            )
        ),

        pending_promotion=(
            pending_promotion_from_dict(
                value.get(
                    "pending_promotion"
                )
            )
        ),

        dispatch_receipts=[
            receipt_from_dict(receipt)
            for receipt
            in value.get(
                "dispatch_receipts",
                [],
            )
        ],

        highest_manifest_sequence_seen=(
            value.get(
                "highest_manifest_sequence_seen",
                0,
            )
        ),
    )


# ============================================================================
# WAL HELPERS
# ============================================================================

def wal_final_hash(
    wal: List[WALRecord],
    length: Optional[int] = None,
) -> str:
    if length is None:
        length = len(wal)

    if length == 0:
        return ZERO_HASH

    if length < 0:
        raise RecoveryError(
            "invalid WAL length"
        )

    if length > len(wal):
        raise RecoveryError(
            "requested WAL prefix exceeds WAL length"
        )

    return wal[length - 1].record_hash


def validate_wal(
    wal: List[WALRecord],
) -> None:
    previous_hash = ZERO_HASH

    for expected_index, record in enumerate(
        wal,
        start=1,
    ):
        record.validate()

        if record.index != expected_index:
            raise IntegrityError(
                "WAL index mismatch"
            )

        if record.previous_hash != previous_hash:
            raise IntegrityError(
                "WAL chain mismatch"
            )

        previous_hash = record.record_hash


def validate_wal_prefix(
    wal: List[WALRecord],
    required_length: int,
    required_final_hash: str,
) -> None:
    validate_wal(wal)

    if len(wal) < required_length:
        raise CheckpointError(
            "checkpoint WAL length mismatch"
        )

    actual_final_hash = wal_final_hash(
        wal,
        required_length,
    )

    if not secure_equal(
        actual_final_hash,
        required_final_hash,
    ):
        raise CheckpointError(
            "checkpoint WAL final hash mismatch"
        )


# ============================================================================
# END PART 1 OF 4
# ============================================================================

print(
    "R28 UNIT N.32: PART 1 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.32
# ATOMIC DUAL-SLOT CHECKPOINT ROTATION
# + COMMITTED-MANIFEST FALLBACK
#
# CORRECTED COPY/PASTE VERSION
# PART 2 OF 4
# ============================================================================


# ============================================================================
# N32 ENGINE
# ============================================================================

class N32Engine:
    def __init__(
        self,
        state: Optional[DurableState] = None,
    ) -> None:
        if state is None:
            payload = build_leverage_payload()

            self.state = DurableState(
                generation=1,
                recovery_epoch=1,
                lineage_id=new_id(
                    "lineage"
                ),
                phase=PHASE_PREPARED,
                payload=payload,
                payload_hash=payload_hash(
                    payload
                ),
            )

            self.append_wal(
                "GENERATION_CREATED",
                {
                    "generation": (
                        self.state.generation
                    ),
                    "recovery_epoch": (
                        self.state.recovery_epoch
                    ),
                    "lineage_id": (
                        self.state.lineage_id
                    ),
                },
            )

        else:
            self.state = state.clone()

        self._lock = threading.RLock()


# ============================================================================
# WAL APPEND
# ============================================================================

    def append_wal(
        self,
        event: str,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> WALRecord:
        if metadata is None:
            metadata = {}

        previous_hash = wal_final_hash(
            self.state.wal
        )

        record = WALRecord(
            index=len(
                self.state.wal
            ) + 1,
            event=event,
            generation=(
                self.state.generation
            ),
            recovery_epoch=(
                self.state.recovery_epoch
            ),
            lineage_id=(
                self.state.lineage_id
            ),
            payload_hash=(
                self.state.payload_hash
            ),
            previous_hash=(
                previous_hash
            ),
            timestamp_ms=now_ms(),
            metadata=deep_copy(
                metadata
            ),
        )

        record.seal()

        self.state.wal.append(
            record
        )

        return record


# ============================================================================
# CORE STATE VALIDATION
# ============================================================================

    def validate_core_state(
        self,
    ) -> None:
        calculated_payload_hash = (
            payload_hash(
                self.state.payload
            )
        )

        if not secure_equal(
            calculated_payload_hash,
            self.state.payload_hash,
        ):
            raise IntegrityError(
                "payload hash mismatch"
            )

        if self.state.generation < 1:
            raise RecoveryError(
                "invalid generation"
            )

        if (
            self.state.recovery_epoch
            < 1
        ):
            raise RecoveryError(
                "invalid recovery epoch"
            )

        if not self.state.lineage_id:
            raise RecoveryError(
                "missing lineage"
            )

        validate_wal(
            self.state.wal
        )


# ============================================================================
# RECOVERY LEASE
# ============================================================================

    def acquire_recovery_lease(
        self,
        owner_id: str,
    ) -> RecoveryLease:
        with self._lock:
            if (
                self.state.phase
                == PHASE_COMPLETED
            ):
                raise RecoveryError(
                    "terminal generation cannot acquire recovery lease"
                )

            self.state.lease_nonce += 1

            lease = RecoveryLease(
                lease_id=new_id(
                    "lease"
                ),
                owner_id=owner_id,
                generation=(
                    self.state.generation
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                nonce=(
                    self.state.lease_nonce
                ),
            )

            lease.seal()

            self.state.recovery_lease = (
                lease
            )

            self.append_wal(
                "RECOVERY_LEASE_ACQUIRED",
                {
                    "lease_id": (
                        lease.lease_id
                    ),
                    "owner_id": (
                        lease.owner_id
                    ),
                    "nonce": (
                        lease.nonce
                    ),
                },
            )

            return deep_copy(
                lease
            )


    def validate_recovery_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        lease.validate_integrity()

        if (
            lease.generation
            != self.state.generation
        ):
            raise RecoveryError(
                "recovery lease generation mismatch"
            )

        if (
            lease.recovery_epoch
            != self.state.recovery_epoch
        ):
            raise RecoveryError(
                "recovery lease recovery epoch mismatch"
            )

        if (
            lease.lineage_id
            != self.state.lineage_id
        ):
            raise RecoveryError(
                "recovery lease lineage mismatch"
            )

        current = (
            self.state.recovery_lease
        )

        if current is None:
            raise RecoveryError(
                "recovery lease missing"
            )

        current.validate_integrity()

        if (
            lease.lease_id
            != current.lease_id
        ):
            raise RecoveryError(
                "recovery lease identity mismatch"
            )

        if (
            lease.owner_id
            != current.owner_id
        ):
            raise RecoveryError(
                "recovery lease owner mismatch"
            )

        if (
            lease.nonce
            != current.nonce
        ):
            raise RecoveryError(
                "recovery lease nonce mismatch"
            )


# ============================================================================
# AUTHORIZATION
# ============================================================================

    def issue_authorization(
        self,
        lease: RecoveryLease,
    ) -> Authorization:
        with self._lock:
            self.validate_recovery_lease(
                lease
            )

            if (
                self.state.phase
                not in (
                    PHASE_PREPARED,
                    PHASE_AUTHORIZED,
                )
            ):
                raise AuthorizationError(
                    "generation is not authorizable"
                )

            if (
                self.state.authorization
                is not None
                and not self.state.authorization.consumed
            ):
                raise AuthorizationError(
                    "active authorization already exists"
                )

            self.state.authorization_nonce += 1

            authorization = Authorization(
                authorization_id=new_id(
                    "authorization"
                ),
                generation=(
                    self.state.generation
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                lease_id=(
                    lease.lease_id
                ),
                owner_id=(
                    lease.owner_id
                ),
                payload_hash=(
                    self.state.payload_hash
                ),
                nonce=(
                    self.state.authorization_nonce
                ),
                consumed=False,
            )

            authorization.seal()

            self.state.authorization = (
                authorization
            )

            self.state.phase = (
                PHASE_AUTHORIZED
            )

            self.append_wal(
                "AUTHORIZATION_ISSUED",
                {
                    "authorization_id": (
                        authorization.authorization_id
                    ),
                    "lease_id": (
                        authorization.lease_id
                    ),
                    "nonce": (
                        authorization.nonce
                    ),
                },
            )

            return deep_copy(
                authorization
            )


    def validate_authorization(
        self,
        authorization: Authorization,
    ) -> None:
        authorization.validate_integrity()

        if (
            authorization.generation
            != self.state.generation
        ):
            raise AuthorizationError(
                "authorization generation mismatch"
            )

        if (
            authorization.recovery_epoch
            != self.state.recovery_epoch
        ):
            raise AuthorizationError(
                "authorization recovery epoch mismatch"
            )

        if (
            authorization.lineage_id
            != self.state.lineage_id
        ):
            raise AuthorizationError(
                "authorization lineage mismatch"
            )

        if (
            authorization.payload_hash
            != self.state.payload_hash
        ):
            raise AuthorizationError(
                "authorization payload hash mismatch"
            )

        current = (
            self.state.authorization
        )

        if current is None:
            raise AuthorizationError(
                "authorization missing"
            )

        current.validate_integrity()

        if (
            authorization.authorization_id
            != current.authorization_id
        ):
            raise AuthorizationError(
                "authorization identity mismatch"
            )

        if (
            authorization.lease_id
            != current.lease_id
        ):
            raise AuthorizationError(
                "authorization lease mismatch"
            )

        if (
            authorization.owner_id
            != current.owner_id
        ):
            raise AuthorizationError(
                "authorization owner mismatch"
            )

        if (
            authorization.nonce
            != current.nonce
        ):
            raise AuthorizationError(
                "authorization nonce mismatch"
            )

        if current.consumed:
            raise ReplayError(
                "authorization already consumed"
            )


    def consume_authorization(
        self,
        authorization: Authorization,
    ) -> None:
        with self._lock:
            self.validate_authorization(
                authorization
            )

            current = (
                self.state.authorization
            )

            if current is None:
                raise AuthorizationError(
                    "authorization missing"
                )

            current.consumed = True
            current.seal()

            self.append_wal(
                "AUTHORIZATION_CONSUMED",
                {
                    "authorization_id": (
                        current.authorization_id
                    ),
                    "nonce": (
                        current.nonce
                    ),
                },
            )


# ============================================================================
# SYNTHETIC TRANSPORT
# ============================================================================

    def synthetic_dispatch(
        self,
        authorization: Authorization,
    ) -> SyntheticDispatchReceipt:
        with self._lock:
            self.validate_authorization(
                authorization
            )

            self.consume_authorization(
                authorization
            )

            receipt = (
                SyntheticDispatchReceipt(
                    dispatch_id=new_id(
                        "dispatch"
                    ),
                    method=HTTP_METHOD,
                    path=(
                        LEVERAGE_ENDPOINT
                    ),
                    payload_hash=(
                        self.state.payload_hash
                    ),
                    generation=(
                        self.state.generation
                    ),
                    recovery_epoch=(
                        self.state.recovery_epoch
                    ),
                    lineage_id=(
                        self.state.lineage_id
                    ),
                    transmitted=False,
                    timestamp_ms=now_ms(),
                )
            )

            receipt.validate_synthetic()

            self.state.dispatch_receipts.append(
                receipt
            )

            self.state.phase = (
                PHASE_DISPATCHED
            )

            self.append_wal(
                "SYNTHETIC_DISPATCH",
                {
                    "dispatch_id": (
                        receipt.dispatch_id
                    ),
                    "method": (
                        receipt.method
                    ),
                    "path": (
                        receipt.path
                    ),
                    "transmitted": (
                        receipt.transmitted
                    ),
                },
            )

            return deep_copy(
                receipt
            )


# ============================================================================
# FINALIZATION
# ============================================================================

    def finalize_generation(
        self,
    ) -> None:
        with self._lock:
            if (
                self.state.phase
                == PHASE_COMPLETED
            ):
                return

            if (
                self.state.phase
                != PHASE_DISPATCHED
            ):
                raise RecoveryError(
                    "generation is not dispatched"
                )

            if (
                len(
                    self.state.dispatch_receipts
                )
                != 1
            ):
                raise RecoveryError(
                    "generation does not contain exactly one synthetic dispatch"
                )

            self.state.phase = (
                PHASE_COMPLETED
            )

            self.append_wal(
                "GENERATION_COMPLETED",
                {
                    "dispatch_count": len(
                        self.state.dispatch_receipts
                    ),
                },
            )


# ============================================================================
# CHECKPOINT VALIDATION
# ============================================================================

    def validate_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> None:
        checkpoint.validate_integrity()

        if (
            checkpoint.generation
            != self.state.generation
        ):
            raise CheckpointError(
                "checkpoint generation mismatch"
            )

        if (
            checkpoint.recovery_epoch
            != self.state.recovery_epoch
        ):
            raise CheckpointError(
                "checkpoint recovery epoch mismatch"
            )

        if (
            checkpoint.lineage_id
            != self.state.lineage_id
        ):
            raise CheckpointError(
                "checkpoint lineage mismatch"
            )

        if (
            checkpoint.payload_hash
            != self.state.payload_hash
        ):
            raise CheckpointError(
                "checkpoint payload hash mismatch"
            )

        validate_wal_prefix(
            self.state.wal,
            checkpoint.wal_length,
            checkpoint.wal_final_hash,
        )


# ============================================================================
# CHECKPOINT CREATION
# ============================================================================

    def create_checkpoint(
        self,
        slot: str,
        checkpoint_sequence: int,
    ) -> Checkpoint:
        with self._lock:
            if (
                slot
                not in VALID_CHECKPOINT_SLOTS
            ):
                raise CheckpointError(
                    "invalid checkpoint slot"
                )

            if (
                checkpoint_sequence
                < 1
            ):
                raise CheckpointError(
                    "invalid checkpoint sequence"
                )

            authorization_consumed = False

            if (
                self.state.authorization
                is not None
            ):
                authorization_consumed = (
                    self.state.authorization.consumed
                )

            checkpoint = Checkpoint(
                slot=slot,
                checkpoint_sequence=(
                    checkpoint_sequence
                ),
                checkpoint_id=new_id(
                    "checkpoint"
                ),
                generation=(
                    self.state.generation
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                phase=(
                    self.state.phase
                ),
                payload_hash=(
                    self.state.payload_hash
                ),
                wal_length=len(
                    self.state.wal
                ),
                wal_final_hash=(
                    wal_final_hash(
                        self.state.wal
                    )
                ),
                authorization_consumed=(
                    authorization_consumed
                ),
                dispatch_count=len(
                    self.state.dispatch_receipts
                ),
                created_ms=now_ms(),
            )

            checkpoint.seal()

            self.state.checkpoint_slots[
                slot
            ] = checkpoint

            return deep_copy(
                checkpoint
            )


# ============================================================================
# CHECKPOINT SLOT LOOKUP
# ============================================================================

    def get_checkpoint(
        self,
        slot: str,
    ) -> Checkpoint:
        if (
            slot
            not in VALID_CHECKPOINT_SLOTS
        ):
            raise CheckpointError(
                "invalid checkpoint slot"
            )

        checkpoint = (
            self.state.checkpoint_slots.get(
                slot
            )
        )

        if checkpoint is None:
            raise CheckpointError(
                "checkpoint missing"
            )

        return checkpoint


# ============================================================================
# MANIFEST VALIDATION
# ============================================================================

    def validate_manifest(
        self,
        manifest: CommittedManifest,
        enforce_highest_sequence: bool = True,
    ) -> Checkpoint:
        manifest.validate_integrity()

        if (
            enforce_highest_sequence
            and
            self.state.highest_manifest_sequence_seen
            > 0
            and
            manifest.manifest_sequence
            < self.state.highest_manifest_sequence_seen
        ):
            raise ManifestError(
                "committed manifest sequence rollback detected"
            )

        checkpoint = (
            self.state.checkpoint_slots.get(
                manifest.checkpoint_slot
            )
        )

        if checkpoint is None:
            raise ManifestError(
                "manifest checkpoint missing"
            )

        checkpoint.validate_integrity()

        if (
            checkpoint.checkpoint_sequence
            != manifest.checkpoint_sequence
        ):
            raise ManifestError(
                "manifest checkpoint sequence mismatch"
            )

        if (
            checkpoint.checkpoint_id
            != manifest.checkpoint_id
        ):
            raise ManifestError(
                "manifest checkpoint identity mismatch"
            )

        if (
            checkpoint.generation
            != manifest.generation
        ):
            raise ManifestError(
                "manifest generation mismatch"
            )

        if (
            checkpoint.recovery_epoch
            != manifest.recovery_epoch
        ):
            raise ManifestError(
                "manifest recovery epoch mismatch"
            )

        if (
            checkpoint.lineage_id
            != manifest.lineage_id
        ):
            raise ManifestError(
                "manifest lineage mismatch"
            )

        if (
            checkpoint.wal_length
            != manifest.checkpoint_wal_length
        ):
            raise ManifestError(
                "manifest checkpoint WAL length mismatch"
            )

        if (
            checkpoint.wal_final_hash
            != manifest.checkpoint_wal_final_hash
        ):
            raise ManifestError(
                "manifest checkpoint WAL final hash mismatch"
            )

        self.validate_checkpoint(
            checkpoint
        )

        return checkpoint


# ============================================================================
# INITIAL MANIFEST COMMIT
# ============================================================================

    def commit_initial_manifest(
        self,
        checkpoint: Checkpoint,
    ) -> CommittedManifest:
        with self._lock:
            if (
                self.state.committed_manifest
                is not None
            ):
                raise ManifestError(
                    "committed manifest already exists"
                )

            self.validate_checkpoint(
                checkpoint
            )

            stored_checkpoint = (
                self.state.checkpoint_slots.get(
                    checkpoint.slot
                )
            )

            if stored_checkpoint is None:
                raise ManifestError(
                    "checkpoint missing"
                )

            if (
                stored_checkpoint.checkpoint_id
                != checkpoint.checkpoint_id
            ):
                raise ManifestError(
                    "checkpoint identity mismatch"
                )

            manifest = CommittedManifest(
                manifest_sequence=1,
                manifest_id=new_id(
                    "manifest"
                ),

                checkpoint_slot=(
                    checkpoint.slot
                ),
                checkpoint_sequence=(
                    checkpoint.checkpoint_sequence
                ),
                checkpoint_id=(
                    checkpoint.checkpoint_id
                ),

                generation=(
                    checkpoint.generation
                ),
                recovery_epoch=(
                    checkpoint.recovery_epoch
                ),
                lineage_id=(
                    checkpoint.lineage_id
                ),

                checkpoint_wal_length=(
                    checkpoint.wal_length
                ),
                checkpoint_wal_final_hash=(
                    checkpoint.wal_final_hash
                ),

                previous_manifest_sequence=None,
                previous_manifest_id=None,

                committed_ms=now_ms(),
            )

            manifest.seal()

            self.state.committed_manifest = (
                manifest
            )

            self.state.fallback_manifest = (
                None
            )

            self.state.highest_manifest_sequence_seen = (
                manifest.manifest_sequence
            )

            self.append_wal(
                "INITIAL_MANIFEST_COMMITTED",
                {
                    "manifest_sequence": (
                        manifest.manifest_sequence
                    ),
                    "manifest_id": (
                        manifest.manifest_id
                    ),
                    "checkpoint_slot": (
                        manifest.checkpoint_slot
                    ),
                    "checkpoint_sequence": (
                        manifest.checkpoint_sequence
                    ),
                },
            )

            return deep_copy(
                manifest
            )


# ============================================================================
# PREPARE SLOT ROTATION
# ============================================================================

    def prepare_checkpoint_rotation(
        self,
    ) -> PendingPromotion:
        with self._lock:
            current_manifest = (
                self.state.committed_manifest
            )

            if current_manifest is None:
                raise ManifestError(
                    "committed manifest missing"
                )

            current_checkpoint = (
                self.validate_manifest(
                    current_manifest
                )
            )

            target_slot = opposite_slot(
                current_manifest.checkpoint_slot
            )

            target_sequence = (
                current_checkpoint.checkpoint_sequence
                + 1
            )

            new_checkpoint = (
                self.create_checkpoint(
                    target_slot,
                    target_sequence,
                )
            )

            pending = PendingPromotion(
                promotion_id=new_id(
                    "promotion"
                ),

                target_slot=(
                    target_slot
                ),
                target_checkpoint_sequence=(
                    target_sequence
                ),
                target_checkpoint_id=(
                    new_checkpoint.checkpoint_id
                ),

                expected_generation=(
                    self.state.generation
                ),
                expected_recovery_epoch=(
                    self.state.recovery_epoch
                ),
                expected_lineage_id=(
                    self.state.lineage_id
                ),

                base_manifest_sequence=(
                    current_manifest.manifest_sequence
                ),
                base_manifest_id=(
                    current_manifest.manifest_id
                ),

                checkpoint_wal_length=(
                    new_checkpoint.wal_length
                ),
                checkpoint_wal_final_hash=(
                    new_checkpoint.wal_final_hash
                ),

                created_ms=now_ms(),
            )

            pending.seal()

            self.state.pending_promotion = (
                pending
            )

            self.append_wal(
                "CHECKPOINT_ROTATION_PREPARED",
                {
                    "promotion_id": (
                        pending.promotion_id
                    ),
                    "target_slot": (
                        pending.target_slot
                    ),
                    "target_checkpoint_sequence": (
                        pending.target_checkpoint_sequence
                    ),
                    "base_manifest_sequence": (
                        pending.base_manifest_sequence
                    ),
                },
            )

            return deep_copy(
                pending
            )


# ============================================================================
# PENDING PROMOTION VALIDATION
# ============================================================================

    def validate_pending_promotion(
        self,
        pending: PendingPromotion,
    ) -> Checkpoint:
        pending.validate_integrity()

        if (
            pending.expected_generation
            != self.state.generation
        ):
            raise ManifestError(
                "pending promotion generation mismatch"
            )

        if (
            pending.expected_recovery_epoch
            != self.state.recovery_epoch
        ):
            raise ManifestError(
                "pending promotion recovery epoch mismatch"
            )

        if (
            pending.expected_lineage_id
            != self.state.lineage_id
        ):
            raise ManifestError(
                "pending promotion lineage mismatch"
            )

        current_pending = (
            self.state.pending_promotion
        )

        if current_pending is None:
            raise ManifestError(
                "pending promotion missing"
            )

        current_pending.validate_integrity()

        if (
            pending.promotion_id
            != current_pending.promotion_id
        ):
            raise ManifestError(
                "pending promotion identity mismatch"
            )

        manifest = (
            self.state.committed_manifest
        )

        if manifest is None:
            raise ManifestError(
                "committed manifest missing"
            )

        manifest.validate_integrity()

        if (
            manifest.manifest_sequence
            != pending.base_manifest_sequence
        ):
            raise ManifestError(
                "pending promotion base manifest sequence mismatch"
            )

        if (
            manifest.manifest_id
            != pending.base_manifest_id
        ):
            raise ManifestError(
                "pending promotion base manifest identity mismatch"
            )

        checkpoint = (
            self.state.checkpoint_slots.get(
                pending.target_slot
            )
        )

        if checkpoint is None:
            raise ManifestError(
                "pending promotion checkpoint missing"
            )

        checkpoint.validate_integrity()

        if (
            checkpoint.checkpoint_sequence
            != pending.target_checkpoint_sequence
        ):
            raise ManifestError(
                "pending promotion checkpoint sequence mismatch"
            )

        if (
            checkpoint.checkpoint_id
            != pending.target_checkpoint_id
        ):
            raise ManifestError(
                "pending promotion checkpoint identity mismatch"
            )

        if (
            checkpoint.wal_length
            != pending.checkpoint_wal_length
        ):
            raise ManifestError(
                "pending promotion WAL length mismatch"
            )

        if (
            checkpoint.wal_final_hash
            != pending.checkpoint_wal_final_hash
        ):
            raise ManifestError(
                "pending promotion WAL final hash mismatch"
            )

        self.validate_checkpoint(
            checkpoint
        )

        return checkpoint


# ============================================================================
# COMMIT SLOT ROTATION
# ============================================================================

    def commit_checkpoint_rotation(
        self,
        pending: PendingPromotion,
    ) -> CommittedManifest:
        with self._lock:
            checkpoint = (
                self.validate_pending_promotion(
                    pending
                )
            )

            previous_manifest = (
                self.state.committed_manifest
            )

            if previous_manifest is None:
                raise ManifestError(
                    "committed manifest missing"
                )

            next_manifest_sequence = (
                previous_manifest.manifest_sequence
                + 1
            )

            if (
                next_manifest_sequence
                <= self.state.highest_manifest_sequence_seen
            ):
                raise ManifestError(
                    "manifest sequence is not monotonic"
                )

            new_manifest = (
                CommittedManifest(
                    manifest_sequence=(
                        next_manifest_sequence
                    ),
                    manifest_id=new_id(
                        "manifest"
                    ),

                    checkpoint_slot=(
                        checkpoint.slot
                    ),
                    checkpoint_sequence=(
                        checkpoint.checkpoint_sequence
                    ),
                    checkpoint_id=(
                        checkpoint.checkpoint_id
                    ),

                    generation=(
                        checkpoint.generation
                    ),
                    recovery_epoch=(
                        checkpoint.recovery_epoch
                    ),
                    lineage_id=(
                        checkpoint.lineage_id
                    ),

                    checkpoint_wal_length=(
                        checkpoint.wal_length
                    ),
                    checkpoint_wal_final_hash=(
                        checkpoint.wal_final_hash
                    ),

                    previous_manifest_sequence=(
                        previous_manifest.manifest_sequence
                    ),
                    previous_manifest_id=(
                        previous_manifest.manifest_id
                    ),

                    committed_ms=now_ms(),
                )
            )

            new_manifest.seal()

            self.state.fallback_manifest = (
                deep_copy(
                    previous_manifest
                )
            )

            self.state.committed_manifest = (
                new_manifest
            )

            self.state.pending_promotion = (
                None
            )

            self.state.highest_manifest_sequence_seen = (
                new_manifest.manifest_sequence
            )

            self.append_wal(
                "CHECKPOINT_ROTATION_COMMITTED",
                {
                    "manifest_sequence": (
                        new_manifest.manifest_sequence
                    ),
                    "manifest_id": (
                        new_manifest.manifest_id
                    ),
                    "checkpoint_slot": (
                        new_manifest.checkpoint_slot
                    ),
                    "checkpoint_sequence": (
                        new_manifest.checkpoint_sequence
                    ),
                    "previous_manifest_sequence": (
                        new_manifest.previous_manifest_sequence
                    ),
                },
            )

            return deep_copy(
                new_manifest
            )


# ============================================================================
# COMMITTED AUTHORITY RECOVERY
# ============================================================================

    def recover_committed_authority(
        self,
    ) -> Tuple[
        CommittedManifest,
        Checkpoint,
    ]:
        with self._lock:
            current_manifest = (
                self.state.committed_manifest
            )

            if current_manifest is None:
                raise ManifestError(
                    "committed manifest missing"
                )

            try:
                checkpoint = (
                    self.validate_manifest(
                        current_manifest,
                        enforce_highest_sequence=True,
                    )
                )

                return (
                    deep_copy(
                        current_manifest
                    ),
                    deep_copy(
                        checkpoint
                    ),
                )

            except (
                IntegrityError,
                CheckpointError,
            ):
                fallback = (
                    self.state.fallback_manifest
                )

                if fallback is None:
                    raise

                checkpoint = (
                    self.validate_manifest(
                        fallback,
                        enforce_highest_sequence=False,
                    )
                )

                return (
                    deep_copy(
                        fallback
                    ),
                    deep_copy(
                        checkpoint
                    ),
                )


# ============================================================================
# RESTART
# ============================================================================

    def restart(
        self,
    ) -> "N32Engine":
        serialized = serialize_state(
            self.state
        )

        restored = (
            restore_state_from_dict(
                deep_copy(
                    serialized
                )
            )
        )

        engine = N32Engine(
            restored
        )

        engine.validate_core_state()

        return engine


# ============================================================================
# COMPLETE PENDING PROMOTION AFTER RESTART
# ============================================================================

    def recover_pending_promotion(
        self,
    ) -> Optional[CommittedManifest]:
        with self._lock:
            pending = (
                self.state.pending_promotion
            )

            if pending is None:
                return None

            pending.validate_integrity()

            return (
                self.commit_checkpoint_rotation(
                    deep_copy(
                        pending
                    )
                )
            )


# ============================================================================
# GENERATION ADVANCE
# ============================================================================

    def advance_generation(
        self,
    ) -> None:
        with self._lock:
            prior_generation = (
                self.state.generation
            )

            prior_epoch = (
                self.state.recovery_epoch
            )

            prior_lineage = (
                self.state.lineage_id
            )

            self.state.generation += 1
            self.state.recovery_epoch += 1

            self.state.lineage_id = (
                new_id(
                    "lineage"
                )
            )

            self.state.phase = (
                PHASE_PREPARED
            )

            self.state.recovery_lease = (
                None
            )

            self.state.authorization = (
                None
            )

            self.state.pending_promotion = (
                None
            )

            self.state.dispatch_receipts = (
                []
            )

            self.append_wal(
                "GENERATION_ADVANCED",
                {
                    "prior_generation": (
                        prior_generation
                    ),
                    "new_generation": (
                        self.state.generation
                    ),
                    "prior_recovery_epoch": (
                        prior_epoch
                    ),
                    "new_recovery_epoch": (
                        self.state.recovery_epoch
                    ),
                    "prior_lineage_id": (
                        prior_lineage
                    ),
                    "new_lineage_id": (
                        self.state.lineage_id
                    ),
                },
            )


# ============================================================================
# NETWORK WRITE FIREBREAK
# ============================================================================

    def real_post(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        raise NetworkWriteBlocked(
            "real network POST is disabled"
        )


    def demo_post(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        raise NetworkWriteBlocked(
            "demo network POST is disabled"
        )


# ============================================================================
# AUTHORITY CONSISTENCY
# ============================================================================

    def validate_committed_authority(
        self,
    ) -> Checkpoint:
        manifest = (
            self.state.committed_manifest
        )

        if manifest is None:
            raise ManifestError(
                "committed manifest missing"
            )

        checkpoint = (
            self.validate_manifest(
                manifest
            )
        )

        if (
            checkpoint.phase
            != PHASE_COMPLETED
        ):
            raise CheckpointError(
                "committed checkpoint is not completed"
            )

        if (
            checkpoint.dispatch_count
            != 1
        ):
            raise CheckpointError(
                "committed checkpoint dispatch count mismatch"
            )

        if (
            not checkpoint.authorization_consumed
        ):
            raise CheckpointError(
                "committed checkpoint authorization is not consumed"
            )

        return checkpoint


# ============================================================================
# END PART 2 OF 4
# ============================================================================

print(
    "R28 UNIT N.32: PART 2 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.32
# ATOMIC DUAL-SLOT CHECKPOINT ROTATION
# + COMMITTED-MANIFEST FALLBACK
#
# CORRECTED COPY/PASTE VERSION
# PART 3 OF 4
# ============================================================================


# ============================================================================
# TEST FIXTURE BUILDERS
# ============================================================================

def build_completed_engine() -> Tuple[
    N32Engine,
    RecoveryLease,
    Authorization,
    SyntheticDispatchReceipt,
]:
    engine = N32Engine()

    lease = engine.acquire_recovery_lease(
        "worker-primary"
    )

    authorization = (
        engine.issue_authorization(
            lease
        )
    )

    receipt = (
        engine.synthetic_dispatch(
            authorization
        )
    )

    engine.finalize_generation()

    return (
        engine,
        lease,
        authorization,
        receipt,
    )


def build_initial_committed_engine() -> Tuple[
    N32Engine,
    Checkpoint,
    CommittedManifest,
]:
    (
        engine,
        _lease,
        _authorization,
        _receipt,
    ) = build_completed_engine()

    checkpoint = (
        engine.create_checkpoint(
            CHECKPOINT_SLOT_A,
            1,
        )
    )

    manifest = (
        engine.commit_initial_manifest(
            checkpoint
        )
    )

    return (
        engine,
        checkpoint,
        manifest,
    )


def build_rotated_engine() -> Tuple[
    N32Engine,
    Checkpoint,
    CommittedManifest,
    PendingPromotion,
    Checkpoint,
    CommittedManifest,
]:
    (
        engine,
        checkpoint_a,
        manifest_1,
    ) = build_initial_committed_engine()

    pending = (
        engine.prepare_checkpoint_rotation()
    )

    checkpoint_b = (
        engine.get_checkpoint(
            CHECKPOINT_SLOT_B
        )
    )

    manifest_2 = (
        engine.commit_checkpoint_rotation(
            pending
        )
    )

    return (
        engine,
        checkpoint_a,
        manifest_1,
        pending,
        checkpoint_b,
        manifest_2,
    )


# ============================================================================
# DIAGNOSTIC TESTS
# ============================================================================

def run_diagnostics() -> N32Engine:
    separator()

    print(
        "{} DIAGNOSTIC START".format(
            UNIT_NAME
        ),
        flush=True,
    )

    separator()


# ============================================================================
# TEST 1
# ============================================================================

    diagnostic_header(
        1,
        "INITIAL STATE",
    )

    engine = N32Engine()

    check(
        engine.state.generation == 1,
        "Initial Generation Is One",
    )

    check(
        engine.state.recovery_epoch == 1,
        "Initial Recovery Epoch Is One",
    )

    check(
        engine.state.phase
        == PHASE_PREPARED,
        "Initial Phase Is PREPARED",
    )

    check(
        bool(
            engine.state.lineage_id
        ),
        "Initial Lineage Established",
    )

    check(
        engine.state.payload_hash
        == payload_hash(
            engine.state.payload
        ),
        "Payload Hash Established",
    )


# ============================================================================
# TEST 2
# ============================================================================

    diagnostic_header(
        2,
        "RECOVERY LEASE BINDING",
    )

    lease = (
        engine.acquire_recovery_lease(
            "worker-primary"
        )
    )

    check(
        lease.generation
        == engine.state.generation,
        "Lease Bound To Current Generation",
    )

    check(
        lease.lineage_id
        == engine.state.lineage_id,
        "Lease Bound To Current Lineage",
    )

    check(
        lease.recovery_epoch
        == engine.state.recovery_epoch,
        "Lease Bound To Current Recovery Epoch",
    )

    check(
        lease.owner_id
        == "worker-primary",
        "Lease Bound To Worker",
    )


# ============================================================================
# TEST 3
# ============================================================================

    diagnostic_header(
        3,
        "AUTHORIZATION BINDING",
    )

    authorization = (
        engine.issue_authorization(
            lease
        )
    )

    check(
        authorization.generation
        == engine.state.generation,
        "Authorization Bound To Generation",
    )

    check(
        authorization.recovery_epoch
        == engine.state.recovery_epoch,
        "Authorization Bound To Recovery Epoch",
    )

    check(
        authorization.lineage_id
        == engine.state.lineage_id,
        "Authorization Bound To Lineage",
    )

    check(
        authorization.lease_id
        == lease.lease_id,
        "Authorization Bound To Recovery Lease",
    )

    check(
        authorization.payload_hash
        == engine.state.payload_hash,
        "Authorization Bound To Payload Hash",
    )


# ============================================================================
# TEST 4
# ============================================================================

    diagnostic_header(
        4,
        "SYNTHETIC DISPATCH",
    )

    receipt = (
        engine.synthetic_dispatch(
            authorization
        )
    )

    check(
        receipt.method
        == HTTP_METHOD,
        "Synthetic Dispatch Method Is POST",
    )

    check(
        receipt.path
        == LEVERAGE_ENDPOINT,
        "Synthetic Dispatch Path Is Leverage Endpoint",
    )

    check(
        receipt.payload_hash
        == engine.state.payload_hash,
        "Synthetic Dispatch Payload Hash Preserved",
    )

    check(
        receipt.transmitted is False,
        "Synthetic Dispatch Was Not Transmitted",
    )

    check(
        len(
            engine.state.dispatch_receipts
        ) == 1,
        "Exactly One Synthetic Dispatch Recorded",
    )


# ============================================================================
# TEST 5
# ============================================================================

    diagnostic_header(
        5,
        "FINALIZATION",
    )

    engine.finalize_generation()

    check(
        engine.state.phase
        == PHASE_COMPLETED,
        "Generation Reaches COMPLETED",
    )

    check(
        engine.state.authorization
        is not None
        and
        engine.state.authorization.consumed,
        "Authorization Consumed Exactly Once",
    )


# ============================================================================
# TEST 6
# ============================================================================

    diagnostic_header(
        6,
        "INITIAL CHECKPOINT SLOT A",
    )

    checkpoint_a = (
        engine.create_checkpoint(
            CHECKPOINT_SLOT_A,
            1,
        )
    )

    check(
        checkpoint_a.slot
        == CHECKPOINT_SLOT_A,
        "Initial Checkpoint Uses Slot A",
    )

    check(
        checkpoint_a.checkpoint_sequence
        == 1,
        "Initial Checkpoint Sequence Is One",
    )

    check(
        checkpoint_a.phase
        == PHASE_COMPLETED,
        "Checkpoint Captures COMPLETED Phase",
    )

    check(
        checkpoint_a.dispatch_count
        == 1,
        "Checkpoint Captures One Dispatch",
    )

    check(
        checkpoint_a.authorization_consumed,
        "Checkpoint Captures Consumed Authorization",
    )


# ============================================================================
# TEST 7
# ============================================================================

    diagnostic_header(
        7,
        "INITIAL MANIFEST COMMIT",
    )

    manifest_1 = (
        engine.commit_initial_manifest(
            checkpoint_a
        )
    )

    check(
        manifest_1.manifest_sequence
        == 1,
        "Initial Manifest Sequence Is One",
    )

    check(
        manifest_1.checkpoint_slot
        == CHECKPOINT_SLOT_A,
        "Initial Manifest Points To Slot A",
    )

    check(
        manifest_1.checkpoint_sequence
        == 1,
        "Initial Manifest Points To Checkpoint Sequence One",
    )

    check(
        engine.state.highest_manifest_sequence_seen
        == 1,
        "Highest Manifest Sequence Established",
    )


# ============================================================================
# TEST 8
# ============================================================================

    diagnostic_header(
        8,
        "INITIAL COMMITTED AUTHORITY RECOVERY",
    )

    (
        recovered_manifest,
        recovered_checkpoint,
    ) = (
        engine.recover_committed_authority()
    )

    check(
        recovered_manifest.manifest_id
        == manifest_1.manifest_id,
        "Committed Manifest Recovered",
    )

    check(
        recovered_checkpoint.checkpoint_id
        == checkpoint_a.checkpoint_id,
        "Committed Checkpoint Recovered",
    )

    check(
        recovered_checkpoint.wal_length
        <= len(
            engine.state.wal
        ),
        "Checkpoint Historical WAL Prefix Available",
    )


# ============================================================================
# TEST 9
# ============================================================================

    diagnostic_header(
        9,
        "DUAL-SLOT ROTATION PREPARATION",
    )

    pending = (
        engine.prepare_checkpoint_rotation()
    )

    checkpoint_b = (
        engine.get_checkpoint(
            CHECKPOINT_SLOT_B
        )
    )

    check(
        pending.target_slot
        == CHECKPOINT_SLOT_B,
        "Rotation Targets Opposite Slot B",
    )

    check(
        checkpoint_b.slot
        == CHECKPOINT_SLOT_B,
        "New Checkpoint Stored In Slot B",
    )

    check(
        checkpoint_b.checkpoint_sequence
        == 2,
        "Rotated Checkpoint Sequence Is Two",
    )

    check(
        engine.state.committed_manifest
        is not None
        and
        engine.state.committed_manifest.manifest_sequence
        == 1,
        "Old Manifest Remains Authority Before Promotion Commit",
    )


# ============================================================================
# TEST 10
# ============================================================================

    diagnostic_header(
        10,
        "PENDING PROMOTION BINDING",
    )

    check(
        pending.base_manifest_sequence
        == manifest_1.manifest_sequence,
        "Promotion Anchors Base Manifest Sequence",
    )

    check(
        pending.base_manifest_id
        == manifest_1.manifest_id,
        "Promotion Anchors Base Manifest Identity",
    )

    check(
        pending.target_checkpoint_id
        == checkpoint_b.checkpoint_id,
        "Promotion Anchors Target Checkpoint Identity",
    )

    check(
        pending.checkpoint_wal_length
        == checkpoint_b.wal_length,
        "Promotion Preserves Checkpoint WAL Boundary",
    )

    check(
        pending.checkpoint_wal_final_hash
        == checkpoint_b.wal_final_hash,
        "Promotion Preserves Checkpoint WAL Final Hash",
    )


# ============================================================================
# TEST 11
# ============================================================================

    diagnostic_header(
        11,
        "ATOMIC CHECKPOINT ROTATION COMMIT",
    )

    manifest_2 = (
        engine.commit_checkpoint_rotation(
            pending
        )
    )

    check(
        manifest_2.manifest_sequence
        == 2,
        "Manifest Sequence Advanced To Two",
    )

    check(
        manifest_2.checkpoint_slot
        == CHECKPOINT_SLOT_B,
        "Committed Manifest Rotated To Slot B",
    )

    check(
        manifest_2.checkpoint_sequence
        == 2,
        "Committed Checkpoint Sequence Advanced To Two",
    )

    check(
        manifest_2.previous_manifest_sequence
        == 1,
        "New Manifest Links Prior Manifest Sequence",
    )

    check(
        manifest_2.previous_manifest_id
        == manifest_1.manifest_id,
        "New Manifest Links Prior Manifest Identity",
    )

    check(
        engine.state.pending_promotion
        is None,
        "Pending Promotion Cleared After Commit",
    )


# ============================================================================
# TEST 12
# ============================================================================

    diagnostic_header(
        12,
        "LAST-KNOWN-GOOD FALLBACK RETENTION",
    )

    fallback = (
        engine.state.fallback_manifest
    )

    check(
        fallback is not None,
        "Fallback Manifest Retained",
    )

    check(
        fallback is not None
        and
        fallback.manifest_sequence
        == 1,
        "Fallback Manifest Sequence Is One",
    )

    check(
        fallback is not None
        and
        fallback.manifest_id
        == manifest_1.manifest_id,
        "Fallback Manifest Is Prior Committed Authority",
    )


# ============================================================================
# TEST 13
# ============================================================================

    diagnostic_header(
        13,
        "ROTATED AUTHORITY RECOVERY",
    )

    (
        authoritative_manifest,
        authoritative_checkpoint,
    ) = (
        engine.recover_committed_authority()
    )

    check(
        authoritative_manifest.manifest_sequence
        == 2,
        "Newest Committed Manifest Is Authoritative",
    )

    check(
        authoritative_checkpoint.slot
        == CHECKPOINT_SLOT_B,
        "Newest Committed Checkpoint Is Slot B",
    )

    check(
        authoritative_checkpoint.checkpoint_sequence
        == 2,
        "Newest Checkpoint Sequence Is Two",
    )


# ============================================================================
# TEST 14
# ============================================================================

    diagnostic_header(
        14,
        "WAL EXTENSION AFTER CHECKPOINT",
    )

    committed_boundary = (
        authoritative_checkpoint.wal_length
    )

    committed_hash = (
        authoritative_checkpoint.wal_final_hash
    )

    engine.append_wal(
        "POST_CHECKPOINT_METADATA",
        {
            "reason": (
                "verify historical prefix authority"
            ),
        },
    )

    check(
        len(
            engine.state.wal
        ) > committed_boundary,
        "WAL Extends Beyond Committed Checkpoint",
    )

    validate_wal_prefix(
        engine.state.wal,
        committed_boundary,
        committed_hash,
    )

    check(
        True,
        "Historical Checkpoint WAL Prefix Remains Valid",
    )


# ============================================================================
# TEST 15
# ============================================================================

    diagnostic_header(
        15,
        "RESTART WITH ROTATED AUTHORITY",
    )

    restarted = (
        engine.restart()
    )

    (
        restart_manifest,
        restart_checkpoint,
    ) = (
        restarted.recover_committed_authority()
    )

    check(
        restart_manifest.manifest_sequence
        == 2,
        "Rotated Manifest Survives Restart",
    )

    check(
        restart_checkpoint.checkpoint_sequence
        == 2,
        "Rotated Checkpoint Survives Restart",
    )

    check(
        restart_checkpoint.slot
        == CHECKPOINT_SLOT_B,
        "Restart Preserves Active Slot B",
    )


# ============================================================================
# TEST 16
# ============================================================================

    diagnostic_header(
        16,
        "CRASH BEFORE PROMOTION COMMIT",
    )

    (
        crash_engine,
        _crash_checkpoint_a,
        crash_manifest_1,
    ) = (
        build_initial_committed_engine()
    )

    crash_pending = (
        crash_engine.prepare_checkpoint_rotation()
    )

    crash_restarted = (
        crash_engine.restart()
    )

    check(
        crash_restarted.state.committed_manifest
        is not None
        and
        crash_restarted.state.committed_manifest.manifest_sequence
        == 1,
        "Pre-Commit Crash Preserves Old Committed Manifest",
    )

    check(
        crash_restarted.state.pending_promotion
        is not None,
        "Pending Promotion Survives Restart",
    )

    crash_manifest_2 = (
        crash_restarted.recover_pending_promotion()
    )

    check(
        crash_manifest_2 is not None
        and
        crash_manifest_2.manifest_sequence
        == 2,
        "Pending Promotion Commits After Restart",
    )

    check(
        crash_manifest_2 is not None
        and
        crash_manifest_2.previous_manifest_id
        == crash_manifest_1.manifest_id,
        "Recovered Promotion Anchors Original Manifest",
    )


# ============================================================================
# TEST 17
# ============================================================================

    diagnostic_header(
        17,
        "CORRUPTED ACTIVE MANIFEST FALLBACK",
    )

    corruption_engine = (
        engine.restart()
    )

    if (
        corruption_engine.state.committed_manifest
        is None
    ):
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    corruption_engine.state.committed_manifest.integrity_seal = (
        "f" * 64
    )

    (
        fallback_recovered_manifest,
        fallback_recovered_checkpoint,
    ) = (
        corruption_engine.recover_committed_authority()
    )

    check(
        fallback_recovered_manifest.manifest_sequence
        == 1,
        "Corrupted Active Manifest Falls Back To Prior Authority",
    )

    check(
        fallback_recovered_checkpoint.slot
        == CHECKPOINT_SLOT_A,
        "Fallback Authority Uses Prior Checkpoint Slot A",
    )


# ============================================================================
# TEST 18
# ============================================================================

    diagnostic_header(
        18,
        "CORRUPTED ACTIVE CHECKPOINT FALLBACK",
    )

    checkpoint_corruption_engine = (
        engine.restart()
    )

    active_manifest = (
        checkpoint_corruption_engine.state.committed_manifest
    )

    if active_manifest is None:
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    active_checkpoint = (
        checkpoint_corruption_engine.state.checkpoint_slots[
            active_manifest.checkpoint_slot
        ]
    )

    if active_checkpoint is None:
        raise AssertionError(
            "active checkpoint unexpectedly missing"
        )

    active_checkpoint.integrity_seal = (
        "e" * 64
    )

    (
        checkpoint_fallback_manifest,
        checkpoint_fallback_checkpoint,
    ) = (
        checkpoint_corruption_engine.recover_committed_authority()
    )

    check(
        checkpoint_fallback_manifest.manifest_sequence
        == 1,
        "Corrupted Active Checkpoint Falls Back To Prior Manifest",
    )

    check(
        checkpoint_fallback_checkpoint.checkpoint_sequence
        == 1,
        "Fallback Recovers Prior Checkpoint Sequence",
    )


# ============================================================================
# TEST 19
# ============================================================================

    diagnostic_header(
        19,
        "TAMPERED COMMITTED MANIFEST REJECTION WITHOUT FALLBACK",
    )

    (
        tamper_engine,
        _tamper_checkpoint,
        _tamper_manifest,
    ) = (
        build_initial_committed_engine()
    )

    if (
        tamper_engine.state.committed_manifest
        is None
    ):
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    tamper_engine.state.committed_manifest.integrity_seal = (
        "0" * 64
    )

    expect_rejection(
        lambda: (
            tamper_engine.recover_committed_authority()
        ),
        "Tampered Committed Manifest Rejected",
        "committed manifest integrity seal mismatch",
    )


# ============================================================================
# TEST 20
# ============================================================================

    diagnostic_header(
        20,
        "PENDING PROMOTION SURVIVES RESTART",
    )

    (
        pending_engine,
        pending_checkpoint_a,
        pending_manifest_1,
    ) = (
        build_initial_committed_engine()
    )

    pending_before_restart = (
        pending_engine.prepare_checkpoint_rotation()
    )

    pending_restart = (
        pending_engine.restart()
    )

    check(
        pending_restart.state.pending_promotion
        is not None,
        "Pending Promotion Intent Survives Restart",
    )

    promoted_after_restart = (
        pending_restart.recover_pending_promotion()
    )

    check(
        promoted_after_restart is not None
        and
        promoted_after_restart.manifest_sequence
        == 2,
        "Pending Promotion Commits After Restart",
    )

    check(
        promoted_after_restart is not None
        and
        promoted_after_restart.previous_manifest_id
        == pending_manifest_1.manifest_id,
        "Recovered Promotion Anchors Original Checkpoint Authority",
    )


# ============================================================================
# TEST 21
# ============================================================================

    diagnostic_header(
        21,
        "STALE CHECKPOINT REJECTION AFTER PREFIX LOSS",
    )

    prefix_engine = (
        engine.restart()
    )

    prefix_manifest = (
        prefix_engine.state.committed_manifest
    )

    if prefix_manifest is None:
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    prefix_checkpoint = (
        prefix_engine.state.checkpoint_slots[
            prefix_manifest.checkpoint_slot
        ]
    )

    if prefix_checkpoint is None:
        raise AssertionError(
            "checkpoint unexpectedly missing"
        )

    required_length = (
        prefix_checkpoint.wal_length
    )

    if required_length < 1:
        raise AssertionError(
            "checkpoint WAL length unexpectedly zero"
        )

    prefix_engine.state.wal = (
        prefix_engine.state.wal[
            : required_length - 1
        ]
    )

    expect_rejection(
        lambda: (
            prefix_engine.validate_checkpoint(
                prefix_checkpoint
            )
        ),
        "Stale Checkpoint Without Full WAL Prefix Rejected",
        "checkpoint WAL length mismatch",
    )


# ============================================================================
# TEST 22
# ============================================================================

    diagnostic_header(
        22,
        "CHECKPOINT FINAL HASH MISMATCH",
    )

    hash_engine = (
        engine.restart()
    )

    hash_manifest = (
        hash_engine.state.committed_manifest
    )

    if hash_manifest is None:
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    hash_checkpoint = (
        hash_engine.state.checkpoint_slots[
            hash_manifest.checkpoint_slot
        ]
    )

    if hash_checkpoint is None:
        raise AssertionError(
            "checkpoint unexpectedly missing"
        )

    if (
        hash_checkpoint.wal_length
        < 1
    ):
        raise AssertionError(
            "checkpoint WAL prefix unexpectedly empty"
        )

    target_index = (
        hash_checkpoint.wal_length - 1
    )

    hash_engine.state.wal[
        target_index
    ].record_hash = (
        "a" * 64
    )

    expect_rejection(
        lambda: (
            hash_engine.validate_checkpoint(
                hash_checkpoint
            )
        ),
        "Checkpoint To WAL Final Hash Mismatch Rejected",
        "WAL record hash mismatch",
    )


# ============================================================================
# TEST 23
# ============================================================================

    diagnostic_header(
        23,
        "MANIFEST/CHECKPOINT SLOT MISMATCH",
    )

    missing_slot_engine = (
        engine.restart()
    )

    missing_manifest = (
        missing_slot_engine.state.committed_manifest
    )

    if missing_manifest is None:
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    missing_slot_engine.state.checkpoint_slots[
        missing_manifest.checkpoint_slot
    ] = None

    expect_rejection(
        lambda: (
            missing_slot_engine.validate_manifest(
                missing_manifest
            )
        ),
        "Manifest Pointing To Missing Checkpoint Slot Rejected",
        "manifest checkpoint missing",
    )


# ============================================================================
# TEST 24
# ============================================================================

    diagnostic_header(
        24,
        "MANIFEST SEQUENCE ROLLBACK REJECTION",
    )

    rollback_engine = (
        engine.restart()
    )

    rollback_fallback = (
        rollback_engine.state.fallback_manifest
    )

    if rollback_fallback is None:
        raise AssertionError(
            "fallback manifest unexpectedly missing"
        )

    rollback_engine.state.committed_manifest = (
        deep_copy(
            rollback_fallback
        )
    )

    expect_rejection(
        lambda: (
            rollback_engine.recover_committed_authority()
        ),
        "Valid But Rolled-Back Manifest Sequence Rejected",
        "committed manifest sequence rollback detected",
    )


# ============================================================================
# TEST 25
# ============================================================================

    diagnostic_header(
        25,
        "CHECKPOINT SEQUENCE ROLLBACK REJECTION",
    )

    checkpoint_rollback_engine = (
        engine.restart()
    )

    current_manifest = (
        checkpoint_rollback_engine.state.committed_manifest
    )

    if current_manifest is None:
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    current_checkpoint = (
        checkpoint_rollback_engine.state.checkpoint_slots[
            current_manifest.checkpoint_slot
        ]
    )

    if current_checkpoint is None:
        raise AssertionError(
            "checkpoint unexpectedly missing"
        )

    current_checkpoint.checkpoint_sequence = 1
    current_checkpoint.seal()

    expect_rejection(
        lambda: (
            checkpoint_rollback_engine.validate_manifest(
                current_manifest
            )
        ),
        "Checkpoint Sequence Rollback Rejected",
        "manifest checkpoint sequence mismatch",
    )


# ============================================================================
# TEST 26
# ============================================================================

    diagnostic_header(
        26,
        "CROSS-SLOT CHECKPOINT IDENTITY REJECTION",
    )

    cross_slot_engine = (
        engine.restart()
    )

    cross_manifest = (
        cross_slot_engine.state.committed_manifest
    )

    if cross_manifest is None:
        raise AssertionError(
            "committed manifest unexpectedly missing"
        )

    wrong_checkpoint = (
        cross_slot_engine.state.checkpoint_slots[
            CHECKPOINT_SLOT_A
        ]
    )

    if wrong_checkpoint is None:
        raise AssertionError(
            "slot A checkpoint unexpectedly missing"
        )

    cross_slot_engine.state.checkpoint_slots[
        CHECKPOINT_SLOT_B
    ] = deep_copy(
        wrong_checkpoint
    )

    cross_slot_engine.state.checkpoint_slots[
        CHECKPOINT_SLOT_B
    ].slot = CHECKPOINT_SLOT_B

    cross_slot_engine.state.checkpoint_slots[
        CHECKPOINT_SLOT_B
    ].seal()

    expect_rejection(
        lambda: (
            cross_slot_engine.validate_manifest(
                cross_manifest
            )
        ),
        "Cross-Slot Checkpoint Identity Mismatch Rejected",
        "manifest checkpoint sequence mismatch",
    )


# ============================================================================
# TEST 27
# ============================================================================

    diagnostic_header(
        27,
        "GENERATION ADVANCE",
    )

    generation_engine = (
        engine.restart()
    )

    prior_generation = (
        generation_engine.state.generation
    )

    prior_epoch = (
        generation_engine.state.recovery_epoch
    )

    prior_lineage = (
        generation_engine.state.lineage_id
    )

    generation_engine.advance_generation()

    check(
        generation_engine.state.generation
        > prior_generation,
        "Generation Advanced Monotonically",
    )

    check(
        generation_engine.state.recovery_epoch
        > prior_epoch,
        "Recovery Epoch Advanced Monotonically",
    )

    check(
        generation_engine.state.lineage_id
        != prior_lineage,
        "New Generation Uses Different Lineage",
    )

    check(
        generation_engine.state.phase
        == PHASE_PREPARED,
        "New Generation Returns To PREPARED",
    )


# ============================================================================
# TEST 28
# ============================================================================

    diagnostic_header(
        28,
        "ANTI-ABA STALE LEASE REJECTION",
    )

    stale_engine = N32Engine()

    stale_lease = (
        stale_engine.acquire_recovery_lease(
            "worker-aba"
        )
    )

    stale_engine.advance_generation()

    expect_rejection(
        lambda: (
            stale_engine.validate_recovery_lease(
                stale_lease
            )
        ),
        "Prior Generation Lease Rejected",
        "recovery lease generation mismatch",
    )


# ============================================================================
# TEST 29
# ============================================================================

    diagnostic_header(
        29,
        "AUTHORIZATION REPLAY REJECTION",
    )

    replay_engine = N32Engine()

    replay_lease = (
        replay_engine.acquire_recovery_lease(
            "worker-replay"
        )
    )

    replay_authorization = (
        replay_engine.issue_authorization(
            replay_lease
        )
    )

    replay_engine.synthetic_dispatch(
        replay_authorization
    )

    expect_rejection(
        lambda: (
            replay_engine.synthetic_dispatch(
                replay_authorization
            )
        ),
        "Consumed Authorization Replay Rejected",
        "authorization already consumed",
    )


# ============================================================================
# TEST 30
# ============================================================================

    diagnostic_header(
        30,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    final_receipt = (
        engine.state.dispatch_receipts[
            0
        ]
    )

    check(
        final_receipt.method
        == HTTP_METHOD,
        "Transport Method Exactly POST",
    )

    check(
        final_receipt.path
        == LEVERAGE_ENDPOINT,
        "Transport Path Exactly Leverage Endpoint",
    )

    check(
        final_receipt.payload_hash
        == engine.state.payload_hash,
        "Transport Payload Hash Preserved",
    )

    check(
        final_receipt.transmitted
        is False,
        "Dispatch Was Never Transmitted",
    )


# ============================================================================
# TEST 31
# ============================================================================

    diagnostic_header(
        31,
        "FINAL NETWORK WRITE FIREBREAK",
    )

    check(
        REAL_POST_ENABLED
        is False,
        "Real POST Disabled",
    )

    check(
        DEMO_POST_ENABLED
        is False,
        "Demo POST Disabled",
    )

    check(
        NETWORK_WRITES_ENABLED
        is False,
        "All Network Writes Disabled",
    )

    check(
        SYNTHETIC_TRANSPORT_ONLY
        is True,
        "Synthetic Transport Only",
    )

    expect_rejection(
        lambda: (
            engine.real_post()
        ),
        "Real POST Firebreak Enforced",
        "real network POST is disabled",
    )

    expect_rejection(
        lambda: (
            engine.demo_post()
        ),
        "Demo POST Firebreak Enforced",
        "demo network POST is disabled",
    )


# ============================================================================
# TEST 32
# ============================================================================

    diagnostic_header(
        32,
        "FINAL COMMITTED AUTHORITY",
    )

    final_checkpoint = (
        engine.validate_committed_authority()
    )

    final_manifest = (
        engine.state.committed_manifest
    )

    check(
        final_manifest is not None,
        "Committed Manifest Exists",
    )

    check(
        final_manifest is not None
        and
        final_manifest.manifest_sequence
        == 2,
        "Committed Manifest Sequence Preserved",
    )

    check(
        final_checkpoint.slot
        == CHECKPOINT_SLOT_B,
        "Committed Authority Uses Rotated Slot B",
    )

    check(
        final_checkpoint.checkpoint_sequence
        == 2,
        "Committed Checkpoint Sequence Preserved",
    )

    check(
        final_checkpoint.generation
        == engine.state.generation,
        "Committed Authority Generation Preserved",
    )

    check(
        final_checkpoint.lineage_id
        == engine.state.lineage_id,
        "Committed Authority Lineage Preserved",
    )

    check(
        final_checkpoint.wal_length
        <= len(
            engine.state.wal
        ),
        "Committed Authority WAL Boundary Preserved",
    )

    validate_wal_prefix(
        engine.state.wal,
        final_checkpoint.wal_length,
        final_checkpoint.wal_final_hash,
    )

    check(
        True,
        "Committed Authority Historical WAL Prefix Validates",
    )


# ============================================================================
# DIAGNOSTIC SUMMARY
# ============================================================================

    separator()

    print(
        "{} DIAGNOSTIC SUMMARY".format(
            UNIT_NAME
        ),
        flush=True,
    )

    separator()

    final_manifest = (
        engine.state.committed_manifest
    )

    fallback_manifest = (
        engine.state.fallback_manifest
    )

    active_checkpoint = None

    if final_manifest is not None:
        active_checkpoint = (
            engine.state.checkpoint_slots.get(
                final_manifest.checkpoint_slot
            )
        )

    print(
        "Generation:              {}".format(
            engine.state.generation
        ),
        flush=True,
    )

    print(
        "Recovery Epoch:          {}".format(
            engine.state.recovery_epoch
        ),
        flush=True,
    )

    print(
        "Phase:                   {}".format(
            engine.state.phase
        ),
        flush=True,
    )

    print(
        "WAL Records:             {}".format(
            len(
                engine.state.wal
            )
        ),
        flush=True,
    )

    print(
        "Checkpoint Slot:         {}".format(
            (
                active_checkpoint.slot
                if active_checkpoint
                is not None
                else None
            )
        ),
        flush=True,
    )

    print(
        "Checkpoint Sequence:     {}".format(
            (
                active_checkpoint.checkpoint_sequence
                if active_checkpoint
                is not None
                else None
            )
        ),
        flush=True,
    )

    print(
        "Checkpoint WAL Length:   {}".format(
            (
                active_checkpoint.wal_length
                if active_checkpoint
                is not None
                else None
            )
        ),
        flush=True,
    )

    print(
        "Current WAL Length:      {}".format(
            len(
                engine.state.wal
            )
        ),
        flush=True,
    )

    print(
        "Manifest Sequence:       {}".format(
            (
                final_manifest.manifest_sequence
                if final_manifest
                is not None
                else None
            )
        ),
        flush=True,
    )

    print(
        "Fallback Manifest:       {}".format(
            (
                fallback_manifest.manifest_sequence
                if fallback_manifest
                is not None
                else None
            )
        ),
        flush=True,
    )

    print(
        "Synthetic Dispatches:    {}".format(
            len(
                engine.state.dispatch_receipts
            )
        ),
        flush=True,
    )

    print(
        "Real POST Enabled:       {}".format(
            REAL_POST_ENABLED
        ),
        flush=True,
    )

    print(
        "Demo POST Enabled:       {}".format(
            DEMO_POST_ENABLED
        ),
        flush=True,
    )

    print(
        "Network Writes Enabled:  {}".format(
            NETWORK_WRITES_ENABLED
        ),
        flush=True,
    )

    print(
        "Synthetic Only:          {}".format(
            SYNTHETIC_TRANSPORT_ONLY
        ),
        flush=True,
    )

    separator()

    print(
        "{}: ALL DIAGNOSTICS PASSED".format(
            UNIT_NAME
        ),
        flush=True,
    )

    print(
        "{}: NO REAL ORDER OR ACCOUNT MUTATION WAS SENT".format(
            UNIT_NAME
        ),
        flush=True,
    )

    separator()

    return engine


# ============================================================================
# END PART 3 OF 4
# ============================================================================

print(
    "R28 UNIT N.32: PART 3 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.32
# ATOMIC DUAL-SLOT CHECKPOINT ROTATION
# + COMMITTED-MANIFEST FALLBACK
#
# CORRECTED COPY/PASTE VERSION
# PART 4 OF 4
# ============================================================================


# ============================================================================
# HEALTH SERVER
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):
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

                    "real_post_enabled": (
                        REAL_POST_ENABLED
                    ),

                    "demo_post_enabled": (
                        DEMO_POST_ENABLED
                    ),

                    "network_writes_enabled": (
                        NETWORK_WRITES_ENABLED
                    ),

                    "synthetic_transport_only": (
                        SYNTHETIC_TRANSPORT_ONLY
                    ),
                },
                sort_keys=True,
            ).encode(
                "utf-8"
            )

            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                "application/json",
            )

            self.send_header(
                "Content-Length",
                str(
                    len(
                        body
                    )
                ),
            )

            self.end_headers()

            self.wfile.write(
                body
            )

            return

        self.send_response(
            404
        )

        self.end_headers()


    def log_message(
        self,
        _format: str,
        *_args: Any,
    ) -> None:
        return


# ============================================================================
# HEALTH SERVER START
# ============================================================================

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
                "{}: HEALTH SERVER LISTENING ON PORT {}".format(
                    UNIT_NAME,
                    port,
                ),
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                "{}: HEALTH SERVER ERROR: {}".format(
                    UNIT_NAME,
                    exc,
                ),
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        name="n32-health-server",
        daemon=True,
    )

    thread.start()


# ============================================================================
# FINAL STARTUP SAFETY VALIDATION
# ============================================================================

def validate_startup_firebreak() -> None:
    if REAL_POST_ENABLED:
        raise NetworkWriteBlocked(
            "REAL_POST_ENABLED must remain False"
        )

    if DEMO_POST_ENABLED:
        raise NetworkWriteBlocked(
            "DEMO_POST_ENABLED must remain False"
        )

    if NETWORK_WRITES_ENABLED:
        raise NetworkWriteBlocked(
            "NETWORK_WRITES_ENABLED must remain False"
        )

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise NetworkWriteBlocked(
            "SYNTHETIC_TRANSPORT_ONLY must remain True"
        )


# ============================================================================
# FINAL ENGINE VALIDATION
# ============================================================================

def validate_final_engine(
    engine: N32Engine,
) -> None:
    engine.validate_core_state()

    checkpoint = (
        engine.validate_committed_authority()
    )

    manifest = (
        engine.state.committed_manifest
    )

    if manifest is None:
        raise ManifestError(
            "final committed manifest missing"
        )

    if (
        manifest.manifest_sequence
        != 2
    ):
        raise ManifestError(
            "final committed manifest sequence mismatch"
        )

    if (
        manifest.checkpoint_slot
        != CHECKPOINT_SLOT_B
    ):
        raise ManifestError(
            "final committed manifest slot mismatch"
        )

    if (
        checkpoint.checkpoint_sequence
        != 2
    ):
        raise CheckpointError(
            "final checkpoint sequence mismatch"
        )

    if (
        checkpoint.phase
        != PHASE_COMPLETED
    ):
        raise CheckpointError(
            "final checkpoint phase mismatch"
        )

    if (
        checkpoint.dispatch_count
        != 1
    ):
        raise CheckpointError(
            "final checkpoint dispatch count mismatch"
        )

    if (
        not checkpoint.authorization_consumed
    ):
        raise CheckpointError(
            "final checkpoint authorization state mismatch"
        )

    if (
        len(
            engine.state.dispatch_receipts
        )
        != 1
    ):
        raise RecoveryError(
            "final synthetic dispatch count mismatch"
        )

    receipt = (
        engine.state.dispatch_receipts[
            0
        ]
    )

    receipt.validate_synthetic()

    if (
        receipt.payload_hash
        != engine.state.payload_hash
    ):
        raise RecoveryError(
            "final transport payload hash mismatch"
        )

    validate_wal_prefix(
        engine.state.wal,
        checkpoint.wal_length,
        checkpoint.wal_final_hash,
    )


# ============================================================================
# PERSISTENT SAFE RUNTIME
# ============================================================================

def persistent_safe_runtime(
    engine: N32Engine,
) -> None:
    heartbeat = 1

    print(
        "{}: ENTERING PERSISTENT SAFE RUNTIME".format(
            UNIT_NAME
        ),
        flush=True,
    )

    while True:
        validate_startup_firebreak()

        engine.validate_core_state()

        print(
            "{}: HEARTBEAT {}".format(
                UNIT_NAME,
                heartbeat,
            ),
            flush=True,
        )

        heartbeat += 1

        time.sleep(
            HEARTBEAT_INTERVAL_SECONDS
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    validate_startup_firebreak()

    start_health_server()

    engine = (
        run_diagnostics()
    )

    validate_final_engine(
        engine
    )

    persistent_safe_runtime(
        engine
    )


# ============================================================================
# PROGRAM ENTRY
# ============================================================================

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print(
            "{}: STOPPED BY OPERATOR".format(
                UNIT_NAME
            ),
            flush=True,
        )

    except Exception as exc:
        separator()

        print(
            "{}: FATAL DIAGNOSTIC FAILURE".format(
                UNIT_NAME
            ),
            flush=True,
        )

        print(
            "{}: {}".format(
                type(exc).__name__,
                exc,
            ),
            flush=True,
        )

        separator()

        raise


# ============================================================================
# END R28 UNIT N.32
# END PART 4 OF 4
#
# EXPECTED SUCCESS ENDING:
#
# R28 UNIT N.32: ALL DIAGNOSTICS PASSED
# R28 UNIT N.32: NO REAL ORDER OR ACCOUNT MUTATION WAS SENT
# --------------------------------------------------------------------------------------------
# R28 UNIT N.32: ENTERING PERSISTENT SAFE RUNTIME
# R28 UNIT N.32: HEARTBEAT 1
# R28 UNIT N.32: HEARTBEAT 2
# ...
#
# EXPECTED FINAL AUTHORITY:
#   Generation:              1
#   Recovery Epoch:          1
#   Phase:                   COMPLETED
#   Checkpoint Slot:         B
#   Checkpoint Sequence:     2
#   Manifest Sequence:       2
#   Fallback Manifest:       1
#   Synthetic Dispatches:    1
#
# SAFETY:
#   REAL POST DISABLED
#   DEMO POST DISABLED
#   ALL NETWORK WRITES DISABLED
#   SYNTHETIC TRANSPORT ONLY
# ============================================================================
