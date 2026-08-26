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
