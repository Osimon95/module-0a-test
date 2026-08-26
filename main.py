# ============================================================================
# R28 UNIT N.29
# TWO-PHASE CHECKPOINT PROMOTION + CRASH-SAFE SLOT ROTATION
# + PROMOTION FENCING + ROLLBACK-RESISTANT RECOVERY
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
# N.29 INCREMENT OVER N.28:
#   - PRESERVES DUAL CHECKPOINT RECOVERY
#   - PRESERVES CHECKPOINT MANIFEST INTEGRITY
#   - PRESERVES CHECKPOINT ROLLBACK REJECTION
#   - PRESERVES WAL HASH-CHAIN VALIDATION
#   - PRESERVES GENERATION / LINEAGE / EPOCH FENCING
#   - PRESERVES EXACTLY-ONCE SYNTHETIC DISPATCH
#   - ADDS TWO-PHASE CHECKPOINT STAGING
#   - ADDS CRASH-SAFE CHECKPOINT PROMOTION
#   - ADDS MONOTONIC PROMOTION SEQUENCE
#   - ADDS STAGED-CHECKPOINT NON-AUTHORITY RULE
#   - ADDS SLOT ROTATION FENCING
#   - ADDS PROMOTION RECORD INTEGRITY SEAL
#   - ADDS CRASH RECOVERY BEFORE PROMOTION
#   - ADDS CRASH RECOVERY AFTER PROMOTION
#   - ADDS ANTI-ROLLBACK PROMOTION FENCING
# ============================================================================

print("R28 UNIT N.29: MAIN.PY ENTERED", flush=True)

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


print("R28 UNIT N.29: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.29"
UNIT_VERSION = "N.29"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

INTEGRITY_KEY = b"R28-N29-LOCAL-INTEGRITY-KEY"
CERTIFICATE_KEY = b"R28-N29-RECOVERY-CERTIFICATE-KEY"
CHECKPOINT_KEY = b"R28-N29-CHECKPOINT-INTEGRITY-KEY"
MANIFEST_KEY = b"R28-N29-CHECKPOINT-MANIFEST-KEY"
PROMOTION_KEY = b"R28-N29-CHECKPOINT-PROMOTION-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

TERMINAL_PHASES = {
    PHASE_COMPLETED,
}

CHECKPOINT_SLOT_A = "A"
CHECKPOINT_SLOT_B = "B"

VALID_CHECKPOINT_SLOTS = {
    CHECKPOINT_SLOT_A,
    CHECKPOINT_SLOT_B,
}

PROMOTION_STAGED = "STAGED"
PROMOTION_COMMITTED = "COMMITTED"

VALID_PROMOTION_STATES = {
    PROMOTION_STAGED,
    PROMOTION_COMMITTED,
}

GENESIS_HASH = "0" * 64

NETWORK_WRITE_COUNT = 0
REAL_POST_COUNT = 0
DEMO_POST_COUNT = 0

GLOBAL_COUNTER_LOCK = threading.Lock()


print("R28 UNIT N.29: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# BASIC HELPERS
# ============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_hex(value: Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = canonical_json(value).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def hmac_hex(key: bytes, value: Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = canonical_json(value).encode("utf-8")

    return hmac.new(
        key,
        raw,
        hashlib.sha256,
    ).hexdigest()


def secure_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(
        str(left),
        str(right),
    )


def deep_copy(value: Any) -> Any:
    return copy.deepcopy(value)


def new_uuid() -> str:
    return str(uuid.uuid4())


def monotonic_ns() -> int:
    return time.monotonic_ns()


def utc_time_ns() -> int:
    return time.time_ns()


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        local_block(message)
        raise ValueError(message)


def opposite_checkpoint_slot(slot: str) -> str:
    require(
        slot in VALID_CHECKPOINT_SLOTS,
        "invalid checkpoint slot",
    )

    if slot == CHECKPOINT_SLOT_A:
        return CHECKPOINT_SLOT_B

    return CHECKPOINT_SLOT_A


# ============================================================================
# TEST OUTPUT HELPERS
# ============================================================================

TEST_WIDTH = 92


def separator() -> None:
    print("-" * TEST_WIDTH, flush=True)


def major_separator() -> None:
    print("=" * TEST_WIDTH, flush=True)


def test_header(
    number: int,
    title: str,
) -> None:
    separator()
    print(
        f"{UNIT_NAME} TEST {number}: {title}",
        flush=True,
    )
    separator()


def pass_line(
    label: str,
    passed: bool,
) -> None:
    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<76} {status}",
        flush=True,
    )

    if not passed:
        raise AssertionError(label)


# ============================================================================
# DURABLE WRITE-AHEAD LOG RECORD
# ============================================================================

@dataclass
class WALRecord:
    index: int
    record_type: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    payload: Dict[str, Any]
    previous_hash: str
    record_hash: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "record_type": self.record_type,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "payload": deep_copy(self.payload),
            "previous_hash": self.previous_hash,
        }

    def calculate_hash(self) -> str:
        return sha256_hex(
            self.unsigned_dict()
        )

    def seal(self) -> None:
        self.record_hash = self.calculate_hash()

    def validate(self) -> None:
        require(
            self.index >= 0,
            "WAL record index invalid",
        )

        require(
            bool(self.record_type),
            "WAL record type missing",
        )

        require(
            self.generation >= 1,
            "WAL record generation invalid",
        )

        require(
            bool(self.lineage_id),
            "WAL record lineage missing",
        )

        require(
            self.recovery_epoch >= 0,
            "WAL record recovery epoch invalid",
        )

        require(
            len(self.previous_hash) == 64,
            "WAL previous hash invalid",
        )

        require(
            secure_equal(
                self.record_hash,
                self.calculate_hash(),
            ),
            "WAL record hash mismatch",
        )


# ============================================================================
# RECOVERY LEASE
# ============================================================================

@dataclass
class RecoveryLease:
    owner_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    nonce: str
    issued_at_ns: int

    def identity_tuple(
        self,
    ) -> Tuple[str, int, str, int, str]:
        return (
            self.owner_id,
            self.generation,
            self.lineage_id,
            self.recovery_epoch,
            self.nonce,
        )


# ============================================================================
# RECOVERY AUTHORIZATION
# ============================================================================

@dataclass
class RecoveryAuthorization:
    authorization_id: str
    owner_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    lease_nonce: str
    payload_hash: str
    issued_at_ns: int
    consumed: bool = False
    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "owner_id": self.owner_id,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "lease_nonce": self.lease_nonce,
            "payload_hash": self.payload_hash,
            "issued_at_ns": self.issued_at_ns,
            "consumed": self.consumed,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            CERTIFICATE_KEY,
            self.unsigned_dict(),
        )

    def seal(self) -> None:
        self.integrity_seal = self.calculate_seal()

    def validate_integrity(self) -> None:
        require(
            secure_equal(
                self.integrity_seal,
                self.calculate_seal(),
            ),
            "authorization integrity seal mismatch",
        )


# ============================================================================
# DURABLE DISPATCH COMMIT
# ============================================================================

@dataclass
class DispatchCommit:
    commit_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    authorization_id: str
    payload_hash: str
    dispatch_identity: str
    committed_at_ns: int
    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "commit_id": self.commit_id,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "authorization_id": self.authorization_id,
            "payload_hash": self.payload_hash,
            "dispatch_identity": self.dispatch_identity,
            "committed_at_ns": self.committed_at_ns,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            INTEGRITY_KEY,
            self.unsigned_dict(),
        )

    def seal(self) -> None:
        self.integrity_seal = self.calculate_seal()

    def validate_integrity(self) -> None:
        require(
            secure_equal(
                self.integrity_seal,
                self.calculate_seal(),
            ),
            "dispatch commit integrity seal mismatch",
        )


# ============================================================================
# SYNTHETIC DISPATCH RECORD
# ============================================================================

@dataclass
class SyntheticDispatch:
    dispatch_identity: str
    commit_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    method: str
    path: str
    payload: Dict[str, Any]
    payload_hash: str
    synthetic: bool
    dispatched_at_ns: int

    def validate(self) -> None:
        require(
            self.synthetic is True,
            "dispatch is not synthetic",
        )

        require(
            self.method == HTTP_METHOD,
            "transport method mismatch",
        )

        require(
            self.path == LEVERAGE_ENDPOINT,
            "transport path mismatch",
        )

        require(
            secure_equal(
                self.payload_hash,
                sha256_hex(self.payload),
            ),
            "transport payload hash mismatch",
        )


# ============================================================================
# CHECKPOINT
# ============================================================================

@dataclass
class Checkpoint:
    checkpoint_id: str
    checkpoint_sequence: int
    slot: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    phase: str

    WAL_length: int
    WAL_final_hash: str

    state_hash: str

    created_at_ns: int

    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_sequence": self.checkpoint_sequence,
            "slot": self.slot,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "phase": self.phase,
            "WAL_length": self.WAL_length,
            "WAL_final_hash": self.WAL_final_hash,
            "state_hash": self.state_hash,
            "created_at_ns": self.created_at_ns,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            CHECKPOINT_KEY,
            self.unsigned_dict(),
        )

    def seal(self) -> None:
        self.integrity_seal = self.calculate_seal()

    def validate_integrity(self) -> None:
        require(
            self.slot in VALID_CHECKPOINT_SLOTS,
            "checkpoint slot invalid",
        )

        require(
            self.checkpoint_sequence >= 1,
            "checkpoint sequence invalid",
        )

        require(
            self.generation >= 1,
            "checkpoint generation invalid",
        )

        require(
            bool(self.lineage_id),
            "checkpoint lineage missing",
        )

        require(
            self.recovery_epoch >= 0,
            "checkpoint recovery epoch invalid",
        )

        require(
            len(self.WAL_final_hash) == 64,
            "checkpoint WAL final hash invalid",
        )

        require(
            len(self.state_hash) == 64,
            "checkpoint state hash invalid",
        )

        require(
            secure_equal(
                self.integrity_seal,
                self.calculate_seal(),
            ),
            "checkpoint integrity seal mismatch",
        )


# ============================================================================
# N.29 CHECKPOINT PROMOTION RECORD
#
# A checkpoint may exist physically in the staged slot while still being
# non-authoritative. Authority changes only when a valid COMMITTED promotion
# record is installed.
# ============================================================================

@dataclass
class CheckpointPromotion:
    promotion_id: str

    promotion_sequence: int

    source_slot: str
    target_slot: str

    prior_checkpoint_id: Optional[str]
    target_checkpoint_id: str

    target_checkpoint_sequence: int

    generation: int
    lineage_id: str
    recovery_epoch: int

    WAL_length: int
    WAL_final_hash: str

    state: str

    created_at_ns: int
    committed_at_ns: Optional[int] = None

    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "promotion_id": self.promotion_id,
            "promotion_sequence": self.promotion_sequence,
            "source_slot": self.source_slot,
            "target_slot": self.target_slot,
            "prior_checkpoint_id": self.prior_checkpoint_id,
            "target_checkpoint_id": self.target_checkpoint_id,
            "target_checkpoint_sequence": self.target_checkpoint_sequence,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "WAL_length": self.WAL_length,
            "WAL_final_hash": self.WAL_final_hash,
            "state": self.state,
            "created_at_ns": self.created_at_ns,
            "committed_at_ns": self.committed_at_ns,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            PROMOTION_KEY,
            self.unsigned_dict(),
        )

    def seal(self) -> None:
        self.integrity_seal = self.calculate_seal()

    def validate_integrity(self) -> None:
        require(
            self.promotion_sequence >= 1,
            "promotion sequence invalid",
        )

        require(
            self.source_slot in VALID_CHECKPOINT_SLOTS,
            "promotion source slot invalid",
        )

        require(
            self.target_slot in VALID_CHECKPOINT_SLOTS,
            "promotion target slot invalid",
        )

        require(
            self.source_slot != self.target_slot,
            "promotion source and target slots identical",
        )

        require(
            self.state in VALID_PROMOTION_STATES,
            "promotion state invalid",
        )

        require(
            self.target_checkpoint_sequence >= 1,
            "promotion checkpoint sequence invalid",
        )

        require(
            self.generation >= 1,
            "promotion generation invalid",
        )

        require(
            bool(self.lineage_id),
            "promotion lineage missing",
        )

        require(
            self.recovery_epoch >= 0,
            "promotion recovery epoch invalid",
        )

        require(
            len(self.WAL_final_hash) == 64,
            "promotion WAL final hash invalid",
        )

        if self.state == PROMOTION_COMMITTED:
            require(
                self.committed_at_ns is not None,
                "committed promotion missing commit timestamp",
            )

        require(
            secure_equal(
                self.integrity_seal,
                self.calculate_seal(),
            ),
            "checkpoint promotion integrity seal mismatch",
        )


# ============================================================================
# CHECKPOINT MANIFEST
# ============================================================================

@dataclass
class CheckpointManifest:
    manifest_sequence: int

    active_slot: str
    active_checkpoint_id: str
    active_checkpoint_sequence: int

    generation: int
    lineage_id: str
    recovery_epoch: int

    WAL_length: int
    WAL_final_hash: str

    last_promotion_sequence: int
    last_promotion_id: Optional[str]

    updated_at_ns: int

    integrity_seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "manifest_sequence": self.manifest_sequence,
            "active_slot": self.active_slot,
            "active_checkpoint_id": self.active_checkpoint_id,
            "active_checkpoint_sequence": self.active_checkpoint_sequence,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "WAL_length": self.WAL_length,
            "WAL_final_hash": self.WAL_final_hash,
            "last_promotion_sequence": self.last_promotion_sequence,
            "last_promotion_id": self.last_promotion_id,
            "updated_at_ns": self.updated_at_ns,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            MANIFEST_KEY,
            self.unsigned_dict(),
        )

    def seal(self) -> None:
        self.integrity_seal = self.calculate_seal()

    def validate_integrity(self) -> None:
        require(
            self.manifest_sequence >= 1,
            "checkpoint manifest sequence invalid",
        )

        require(
            self.active_slot in VALID_CHECKPOINT_SLOTS,
            "checkpoint manifest active slot invalid",
        )

        require(
            bool(self.active_checkpoint_id),
            "checkpoint manifest checkpoint ID missing",
        )

        require(
            self.active_checkpoint_sequence >= 1,
            "checkpoint manifest checkpoint sequence invalid",
        )

        require(
            self.generation >= 1,
            "checkpoint manifest generation invalid",
        )

        require(
            bool(self.lineage_id),
            "checkpoint manifest lineage missing",
        )

        require(
            self.recovery_epoch >= 0,
            "checkpoint manifest recovery epoch invalid",
        )

        require(
            len(self.WAL_final_hash) == 64,
            "checkpoint manifest WAL final hash invalid",
        )

        require(
            self.last_promotion_sequence >= 0,
            "checkpoint manifest promotion sequence invalid",
        )

        require(
            secure_equal(
                self.integrity_seal,
                self.calculate_seal(),
            ),
            "checkpoint manifest integrity seal mismatch",
        )


# ============================================================================
# DURABLE ENGINE STATE
# ============================================================================

@dataclass
class DurableState:
    generation: int = 1
    lineage_id: str = field(
        default_factory=new_uuid
    )
    recovery_epoch: int = 0

    phase: str = PHASE_PREPARED

    payload: Dict[str, Any] = field(
        default_factory=dict
    )
    payload_hash: str = ""

    current_lease: Optional[RecoveryLease] = None
    authorization: Optional[RecoveryAuthorization] = None
    dispatch_commit: Optional[DispatchCommit] = None

    synthetic_dispatches: List[SyntheticDispatch] = field(
        default_factory=list
    )

    WAL: List[WALRecord] = field(
        default_factory=list
    )

    checkpoint_slots: Dict[str, Optional[Checkpoint]] = field(
        default_factory=lambda: {
            CHECKPOINT_SLOT_A: None,
            CHECKPOINT_SLOT_B: None,
        }
    )

    checkpoint_state_images: Dict[str, Optional[Dict[str, Any]]] = field(
        default_factory=lambda: {
            CHECKPOINT_SLOT_A: None,
            CHECKPOINT_SLOT_B: None,
        }
    )

    checkpoint_manifest: Optional[CheckpointManifest] = None

    pending_promotion: Optional[CheckpointPromotion] = None
    committed_promotions: List[CheckpointPromotion] = field(
        default_factory=list
    )

    highest_checkpoint_sequence_seen: int = 0
    highest_manifest_sequence_seen: int = 0
    highest_promotion_sequence_seen: int = 0

    consumed_authorization_ids: Set[str] = field(
        default_factory=set
    )

    completed_dispatch_identities: Set[str] = field(
        default_factory=set
    )

    prior_completed_dispatches: List[SyntheticDispatch] = field(
        default_factory=list
    )


# ============================================================================
# STATE SERIALIZATION HELPERS
# ============================================================================

def lease_to_dict(
    lease: Optional[RecoveryLease],
) -> Optional[Dict[str, Any]]:
    if lease is None:
        return None

    return asdict(lease)


def authorization_to_dict(
    authorization: Optional[RecoveryAuthorization],
) -> Optional[Dict[str, Any]]:
    if authorization is None:
        return None

    return asdict(authorization)


def commit_to_dict(
    commit: Optional[DispatchCommit],
) -> Optional[Dict[str, Any]]:
    if commit is None:
        return None

    return asdict(commit)


def dispatch_to_dict(
    dispatch: SyntheticDispatch,
) -> Dict[str, Any]:
    return asdict(dispatch)


def durable_core_dict(
    state: DurableState,
) -> Dict[str, Any]:
    return {
        "generation": state.generation,
        "lineage_id": state.lineage_id,
        "recovery_epoch": state.recovery_epoch,
        "phase": state.phase,
        "payload": deep_copy(state.payload),
        "payload_hash": state.payload_hash,
        "current_lease": lease_to_dict(
            state.current_lease
        ),
        "authorization": authorization_to_dict(
            state.authorization
        ),
        "dispatch_commit": commit_to_dict(
            state.dispatch_commit
        ),
        "synthetic_dispatches": [
            dispatch_to_dict(item)
            for item in state.synthetic_dispatches
        ],
        "consumed_authorization_ids": sorted(
            state.consumed_authorization_ids
        ),
        "completed_dispatch_identities": sorted(
            state.completed_dispatch_identities
        ),
        "prior_completed_dispatches": [
            dispatch_to_dict(item)
            for item in state.prior_completed_dispatches
        ],
    }


def durable_core_hash(
    state: DurableState,
) -> str:
    return sha256_hex(
        durable_core_dict(state)
    )


# ============================================================================
# WAL HELPERS
# ============================================================================

def current_WAL_hash(
    state: DurableState,
) -> str:
    if not state.WAL:
        return GENESIS_HASH

    return state.WAL[-1].record_hash


def append_WAL(
    state: DurableState,
    record_type: str,
    payload: Dict[str, Any],
) -> WALRecord:
    record = WALRecord(
        index=len(state.WAL),
        record_type=record_type,
        generation=state.generation,
        lineage_id=state.lineage_id,
        recovery_epoch=state.recovery_epoch,
        payload=deep_copy(payload),
        previous_hash=current_WAL_hash(state),
    )

    record.seal()
    record.validate()

    state.WAL.append(record)

    return record


def validate_WAL(
    state: DurableState,
) -> None:
    expected_previous_hash = GENESIS_HASH

    for expected_index, record in enumerate(state.WAL):
        require(
            record.index == expected_index,
            "WAL record index mismatch",
        )

        require(
            secure_equal(
                record.previous_hash,
                expected_previous_hash,
            ),
            "WAL chain previous hash mismatch",
        )

        record.validate()

        expected_previous_hash = record.record_hash


# ============================================================================
# SYNTHETIC TRANSPORT FIREBREAK
# ============================================================================

def real_network_post(
    path: str,
    payload: Dict[str, Any],
) -> None:
    global NETWORK_WRITE_COUNT
    global REAL_POST_COUNT

    with GLOBAL_COUNTER_LOCK:
        if (
            not NETWORK_WRITES_ENABLED
            or not REAL_POST_ENABLED
            or SYNTHETIC_TRANSPORT_ONLY
        ):
            local_block(
                "real network POST is disabled"
            )
            raise RuntimeError(
                "real network POST is disabled"
            )

        NETWORK_WRITE_COUNT += 1
        REAL_POST_COUNT += 1

    raise RuntimeError(
        "real network transport must never execute in N.29"
    )


def demo_network_post(
    path: str,
    payload: Dict[str, Any],
) -> None:
    global NETWORK_WRITE_COUNT
    global DEMO_POST_COUNT

    with GLOBAL_COUNTER_LOCK:
        if (
            not NETWORK_WRITES_ENABLED
            or not DEMO_POST_ENABLED
            or SYNTHETIC_TRANSPORT_ONLY
        ):
            local_block(
                "demo network POST is disabled"
            )
            raise RuntimeError(
                "demo network POST is disabled"
            )

        NETWORK_WRITE_COUNT += 1
        DEMO_POST_COUNT += 1

    raise RuntimeError(
        "demo network transport must never execute in N.29"
    )


print(
    "R28 UNIT N.29: PART 1 DEFINITIONS LOADED",
    flush=True,
)

# ============================================================================
# END OF PART 1 OF 4
# ============================================================================
