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
# ============================================================================
# R28 UNIT N.29
# TWO-PHASE CHECKPOINT PROMOTION + CRASH-SAFE SLOT ROTATION
# + PROMOTION FENCING + ROLLBACK-RESISTANT RECOVERY
#
# CORRECTED COPY/PASTE VERSION
# PART 2 OF 4
# ============================================================================


# ============================================================================
# ENGINE
# ============================================================================

class N29Engine:
    def __init__(
        self,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.lock = threading.RLock()

        self.state = DurableState()

        if payload is None:
            payload = {
                "symbol": SYMBOL,
                "leverage": 100,
            }

        self.state.payload = deep_copy(payload)
        self.state.payload_hash = sha256_hex(
            self.state.payload
        )

        append_WAL(
            self.state,
            "ENGINE_INITIALIZED",
            {
                "generation": self.state.generation,
                "lineage_id": self.state.lineage_id,
                "payload_hash": self.state.payload_hash,
                "phase": self.state.phase,
            },
        )

    # ========================================================================
    # GENERAL STATE VALIDATION
    # ========================================================================

    def validate_state(
        self,
    ) -> None:
        with self.lock:
            state = self.state

            require(
                state.generation >= 1,
                "generation invalid",
            )

            require(
                bool(state.lineage_id),
                "lineage missing",
            )

            require(
                state.recovery_epoch >= 0,
                "recovery epoch invalid",
            )

            require(
                state.phase in {
                    PHASE_PREPARED,
                    PHASE_AUTHORIZED,
                    PHASE_COMMITTED,
                    PHASE_DISPATCHED,
                    PHASE_COMPLETED,
                },
                "phase invalid",
            )

            require(
                bool(state.payload),
                "payload missing",
            )

            require(
                secure_equal(
                    state.payload_hash,
                    sha256_hex(state.payload),
                ),
                "payload hash mismatch",
            )

            validate_WAL(state)

            for dispatch in state.synthetic_dispatches:
                dispatch.validate()

            for dispatch in state.prior_completed_dispatches:
                dispatch.validate()

            if state.current_lease is not None:
                self._validate_lease_structure(
                    state.current_lease
                )

            if state.authorization is not None:
                state.authorization.validate_integrity()

            if state.dispatch_commit is not None:
                state.dispatch_commit.validate_integrity()

            for slot in VALID_CHECKPOINT_SLOTS:
                checkpoint = state.checkpoint_slots.get(slot)

                image = state.checkpoint_state_images.get(slot)

                if checkpoint is None:
                    require(
                        image is None,
                        "checkpoint image exists without checkpoint",
                    )
                else:
                    checkpoint.validate_integrity()

                    require(
                        checkpoint.slot == slot,
                        "checkpoint stored in wrong slot",
                    )

                    require(
                        image is not None,
                        "checkpoint state image missing",
                    )

                    require(
                        secure_equal(
                            checkpoint.state_hash,
                            sha256_hex(image),
                        ),
                        "checkpoint state image hash mismatch",
                    )

            if state.checkpoint_manifest is not None:
                state.checkpoint_manifest.validate_integrity()

            if state.pending_promotion is not None:
                state.pending_promotion.validate_integrity()

            for promotion in state.committed_promotions:
                promotion.validate_integrity()

                require(
                    promotion.state == PROMOTION_COMMITTED,
                    "committed promotion list contains non-committed promotion",
                )

            require(
                state.highest_checkpoint_sequence_seen >= 0,
                "highest checkpoint sequence invalid",
            )

            require(
                state.highest_manifest_sequence_seen >= 0,
                "highest manifest sequence invalid",
            )

            require(
                state.highest_promotion_sequence_seen >= 0,
                "highest promotion sequence invalid",
            )

    # ========================================================================
    # LEASE VALIDATION
    # ========================================================================

    def _validate_lease_structure(
        self,
        lease: RecoveryLease,
    ) -> None:
        require(
            bool(lease.owner_id),
            "recovery lease owner missing",
        )

        require(
            lease.generation >= 1,
            "recovery lease generation invalid",
        )

        require(
            bool(lease.lineage_id),
            "recovery lease lineage missing",
        )

        require(
            lease.recovery_epoch >= 1,
            "recovery lease epoch invalid",
        )

        require(
            bool(lease.nonce),
            "recovery lease nonce missing",
        )

    def validate_recovery_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        with self.lock:
            self._validate_lease_structure(lease)

            state = self.state

            require(
                state.current_lease is not None,
                "no recovery lease exists",
            )

            current = state.current_lease

            require(
                lease.owner_id == current.owner_id,
                "recovery lease owner mismatch",
            )

            require(
                lease.generation == current.generation,
                "recovery lease generation mismatch",
            )

            require(
                lease.generation == state.generation,
                "recovery lease stale generation",
            )

            require(
                lease.lineage_id == current.lineage_id,
                "recovery lease lineage mismatch",
            )

            require(
                lease.lineage_id == state.lineage_id,
                "recovery lease stale lineage",
            )

            require(
                lease.recovery_epoch == current.recovery_epoch,
                "recovery lease epoch mismatch",
            )

            require(
                lease.recovery_epoch == state.recovery_epoch,
                "recovery lease stale epoch",
            )

            require(
                lease.nonce == current.nonce,
                "recovery lease nonce mismatch",
            )

    # ========================================================================
    # RECOVERY LEASE ACQUISITION
    # ========================================================================

    def acquire_recovery_lease(
        self,
        owner_id: str,
    ) -> RecoveryLease:
        with self.lock:
            require(
                bool(owner_id),
                "recovery owner ID missing",
            )

            require(
                self.state.phase not in TERMINAL_PHASES,
                "terminal generation cannot acquire recovery lease",
            )

            self.state.recovery_epoch += 1

            lease = RecoveryLease(
                owner_id=owner_id,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                nonce=new_uuid(),
                issued_at_ns=utc_time_ns(),
            )

            self.state.current_lease = lease

            self.state.authorization = None

            append_WAL(
                self.state,
                "RECOVERY_LEASE_ACQUIRED",
                {
                    "owner_id": lease.owner_id,
                    "generation": lease.generation,
                    "lineage_id": lease.lineage_id,
                    "recovery_epoch": lease.recovery_epoch,
                    "nonce": lease.nonce,
                },
            )

            return deep_copy(lease)

    # ========================================================================
    # AUTHORIZATION
    # ========================================================================

    def authorize(
        self,
        lease: RecoveryLease,
    ) -> RecoveryAuthorization:
        with self.lock:
            self.validate_recovery_lease(lease)

            require(
                self.state.phase == PHASE_PREPARED,
                "generation is not prepared",
            )

            authorization = RecoveryAuthorization(
                authorization_id=new_uuid(),
                owner_id=lease.owner_id,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                lease_nonce=lease.nonce,
                payload_hash=self.state.payload_hash,
                issued_at_ns=utc_time_ns(),
                consumed=False,
            )

            authorization.seal()
            authorization.validate_integrity()

            self.state.authorization = authorization
            self.state.phase = PHASE_AUTHORIZED

            append_WAL(
                self.state,
                "RECOVERY_AUTHORIZED",
                {
                    "authorization_id": authorization.authorization_id,
                    "owner_id": authorization.owner_id,
                    "generation": authorization.generation,
                    "lineage_id": authorization.lineage_id,
                    "recovery_epoch": authorization.recovery_epoch,
                    "lease_nonce": authorization.lease_nonce,
                    "payload_hash": authorization.payload_hash,
                },
            )

            return deep_copy(authorization)

    def validate_authorization(
        self,
        authorization: RecoveryAuthorization,
        lease: RecoveryLease,
    ) -> None:
        with self.lock:
            self.validate_recovery_lease(lease)

            authorization.validate_integrity()

            state = self.state

            require(
                state.authorization is not None,
                "generation has no authorization",
            )

            current = state.authorization

            require(
                authorization.authorization_id
                == current.authorization_id,
                "authorization ID mismatch",
            )

            require(
                authorization.authorization_id
                not in state.consumed_authorization_ids,
                "authorization already consumed",
            )

            require(
                not authorization.consumed,
                "authorization marked consumed",
            )

            require(
                authorization.owner_id == lease.owner_id,
                "authorization owner mismatch",
            )

            require(
                authorization.generation
                == state.generation,
                "authorization generation mismatch",
            )

            require(
                authorization.lineage_id
                == state.lineage_id,
                "authorization lineage mismatch",
            )

            require(
                authorization.recovery_epoch
                == state.recovery_epoch,
                "authorization recovery epoch mismatch",
            )

            require(
                authorization.lease_nonce
                == lease.nonce,
                "authorization lease nonce mismatch",
            )

            require(
                secure_equal(
                    authorization.payload_hash,
                    state.payload_hash,
                ),
                "authorization payload hash mismatch",
            )

    # ========================================================================
    # DURABLE DISPATCH COMMIT
    # ========================================================================

    def commit_dispatch(
        self,
        lease: RecoveryLease,
        authorization: RecoveryAuthorization,
    ) -> DispatchCommit:
        with self.lock:
            self.validate_authorization(
                authorization,
                lease,
            )

            require(
                self.state.phase == PHASE_AUTHORIZED,
                "generation is not authorized",
            )

            dispatch_identity = sha256_hex(
                {
                    "unit": UNIT_VERSION,
                    "generation": self.state.generation,
                    "lineage_id": self.state.lineage_id,
                    "recovery_epoch": self.state.recovery_epoch,
                    "authorization_id": authorization.authorization_id,
                    "payload_hash": self.state.payload_hash,
                }
            )

            require(
                dispatch_identity
                not in self.state.completed_dispatch_identities,
                "dispatch identity already completed",
            )

            commit = DispatchCommit(
                commit_id=new_uuid(),
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                authorization_id=authorization.authorization_id,
                payload_hash=self.state.payload_hash,
                dispatch_identity=dispatch_identity,
                committed_at_ns=utc_time_ns(),
            )

            commit.seal()
            commit.validate_integrity()

            self.state.dispatch_commit = commit

            self.state.authorization.consumed = True
            self.state.authorization.seal()

            self.state.consumed_authorization_ids.add(
                authorization.authorization_id
            )

            self.state.phase = PHASE_COMMITTED

            append_WAL(
                self.state,
                "DISPATCH_COMMITTED",
                {
                    "commit_id": commit.commit_id,
                    "authorization_id": commit.authorization_id,
                    "generation": commit.generation,
                    "lineage_id": commit.lineage_id,
                    "recovery_epoch": commit.recovery_epoch,
                    "payload_hash": commit.payload_hash,
                    "dispatch_identity": commit.dispatch_identity,
                },
            )

            return deep_copy(commit)

    def validate_dispatch_commit(
        self,
        commit: DispatchCommit,
    ) -> None:
        with self.lock:
            commit.validate_integrity()

            state = self.state

            require(
                state.dispatch_commit is not None,
                "generation has no dispatch commit",
            )

            current = state.dispatch_commit

            require(
                commit.commit_id == current.commit_id,
                "dispatch commit ID mismatch",
            )

            require(
                commit.generation == state.generation,
                "dispatch commit generation mismatch",
            )

            require(
                commit.lineage_id == state.lineage_id,
                "dispatch commit lineage mismatch",
            )

            require(
                commit.recovery_epoch
                == state.recovery_epoch,
                "dispatch commit recovery epoch mismatch",
            )

            require(
                secure_equal(
                    commit.payload_hash,
                    state.payload_hash,
                ),
                "dispatch commit payload hash mismatch",
            )

            require(
                commit.authorization_id
                in state.consumed_authorization_ids,
                "dispatch commit authorization not consumed",
            )

    # ========================================================================
    # EXACTLY-ONCE SYNTHETIC DISPATCH
    # ========================================================================

    def synthetic_dispatch(
        self,
        commit: DispatchCommit,
    ) -> SyntheticDispatch:
        with self.lock:
            self.validate_dispatch_commit(commit)

            require(
                self.state.phase == PHASE_COMMITTED,
                "generation is not committed",
            )

            require(
                commit.dispatch_identity
                not in self.state.completed_dispatch_identities,
                "dispatch identity already completed",
            )

            existing = [
                item
                for item in self.state.synthetic_dispatches
                if item.dispatch_identity
                == commit.dispatch_identity
            ]

            require(
                not existing,
                "synthetic dispatch already exists",
            )

            dispatch = SyntheticDispatch(
                dispatch_identity=commit.dispatch_identity,
                commit_id=commit.commit_id,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload=deep_copy(self.state.payload),
                payload_hash=self.state.payload_hash,
                synthetic=True,
                dispatched_at_ns=utc_time_ns(),
            )

            dispatch.validate()

            self.state.synthetic_dispatches.append(
                dispatch
            )

            self.state.phase = PHASE_DISPATCHED

            append_WAL(
                self.state,
                "SYNTHETIC_DISPATCHED",
                {
                    "dispatch_identity": dispatch.dispatch_identity,
                    "commit_id": dispatch.commit_id,
                    "generation": dispatch.generation,
                    "lineage_id": dispatch.lineage_id,
                    "recovery_epoch": dispatch.recovery_epoch,
                    "method": dispatch.method,
                    "path": dispatch.path,
                    "payload_hash": dispatch.payload_hash,
                },
            )

            return deep_copy(dispatch)

    # ========================================================================
    # FINALIZATION
    # ========================================================================

    def finalize(
        self,
    ) -> None:
        with self.lock:
            require(
                self.state.phase == PHASE_DISPATCHED,
                "generation is not dispatched",
            )

            require(
                self.state.dispatch_commit is not None,
                "dispatch commit missing",
            )

            identity = (
                self.state.dispatch_commit.dispatch_identity
            )

            require(
                identity
                not in self.state.completed_dispatch_identities,
                "dispatch already finalized",
            )

            matching_dispatches = [
                item
                for item in self.state.synthetic_dispatches
                if item.dispatch_identity == identity
            ]

            require(
                len(matching_dispatches) == 1,
                "completed generation must contain exactly one dispatch",
            )

            self.state.completed_dispatch_identities.add(
                identity
            )

            self.state.phase = PHASE_COMPLETED

            append_WAL(
                self.state,
                "GENERATION_COMPLETED",
                {
                    "generation": self.state.generation,
                    "lineage_id": self.state.lineage_id,
                    "recovery_epoch": self.state.recovery_epoch,
                    "dispatch_identity": identity,
                },
            )

    # ========================================================================
    # FULL SYNTHETIC COMPLETION
    # ========================================================================

    def complete_generation(
        self,
        owner_id: str,
    ) -> SyntheticDispatch:
        with self.lock:
            lease = self.acquire_recovery_lease(
                owner_id
            )

            authorization = self.authorize(
                lease
            )

            commit = self.commit_dispatch(
                lease,
                authorization,
            )

            dispatch = self.synthetic_dispatch(
                commit
            )

            self.finalize()

            return dispatch

    # ========================================================================
    # CHECKPOINT STATE IMAGE
    # ========================================================================

    def build_checkpoint_state_image(
        self,
    ) -> Dict[str, Any]:
        with self.lock:
            return durable_core_dict(
                self.state
            )

    # ========================================================================
    # CHECKPOINT STRUCTURAL VALIDATION
    # ========================================================================

    def validate_checkpoint(
        self,
        checkpoint: Checkpoint,
        state_image: Dict[str, Any],
    ) -> None:
        with self.lock:
            checkpoint.validate_integrity()

            require(
                secure_equal(
                    checkpoint.state_hash,
                    sha256_hex(state_image),
                ),
                "checkpoint state image hash mismatch",
            )

            require(
                checkpoint.WAL_length
                <= len(self.state.WAL),
                "checkpoint WAL length exceeds journal",
            )

            if checkpoint.WAL_length == 0:
                expected_final_hash = GENESIS_HASH
            else:
                expected_final_hash = (
                    self.state.WAL[
                        checkpoint.WAL_length - 1
                    ].record_hash
                )

            require(
                secure_equal(
                    checkpoint.WAL_final_hash,
                    expected_final_hash,
                ),
                "checkpoint WAL final hash mismatch",
            )

    # ========================================================================
    # INITIAL CHECKPOINT
    # ========================================================================

    def create_initial_checkpoint(
        self,
    ) -> Checkpoint:
        with self.lock:
            require(
                self.state.checkpoint_manifest is None,
                "initial checkpoint already exists",
            )

            require(
                self.state.highest_checkpoint_sequence_seen == 0,
                "checkpoint sequence already initialized",
            )

            checkpoint_sequence = 1
            slot = CHECKPOINT_SLOT_A

            image = self.build_checkpoint_state_image()

            checkpoint = Checkpoint(
                checkpoint_id=new_uuid(),
                checkpoint_sequence=checkpoint_sequence,
                slot=slot,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                phase=self.state.phase,
                WAL_length=len(self.state.WAL),
                WAL_final_hash=current_WAL_hash(
                    self.state
                ),
                state_hash=sha256_hex(image),
                created_at_ns=utc_time_ns(),
            )

            checkpoint.seal()
            checkpoint.validate_integrity()

            self.state.checkpoint_slots[
                slot
            ] = checkpoint

            self.state.checkpoint_state_images[
                slot
            ] = deep_copy(image)

            self.state.highest_checkpoint_sequence_seen = (
                checkpoint_sequence
            )

            manifest = CheckpointManifest(
                manifest_sequence=1,
                active_slot=slot,
                active_checkpoint_id=checkpoint.checkpoint_id,
                active_checkpoint_sequence=checkpoint.checkpoint_sequence,
                generation=checkpoint.generation,
                lineage_id=checkpoint.lineage_id,
                recovery_epoch=checkpoint.recovery_epoch,
                WAL_length=checkpoint.WAL_length,
                WAL_final_hash=checkpoint.WAL_final_hash,
                last_promotion_sequence=0,
                last_promotion_id=None,
                updated_at_ns=utc_time_ns(),
            )

            manifest.seal()
            manifest.validate_integrity()

            self.state.checkpoint_manifest = manifest
            self.state.highest_manifest_sequence_seen = 1

            append_WAL(
                self.state,
                "INITIAL_CHECKPOINT_CREATED",
                {
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "checkpoint_sequence": checkpoint.checkpoint_sequence,
                    "slot": checkpoint.slot,
                    "manifest_sequence": manifest.manifest_sequence,
                },
            )

            return deep_copy(checkpoint)

    # ========================================================================
    # ACTIVE CHECKPOINT ACCESS
    # ========================================================================

    def get_active_checkpoint(
        self,
    ) -> Checkpoint:
        with self.lock:
            manifest = self.state.checkpoint_manifest

            require(
                manifest is not None,
                "checkpoint manifest missing",
            )

            manifest.validate_integrity()

            checkpoint = self.state.checkpoint_slots.get(
                manifest.active_slot
            )

            require(
                checkpoint is not None,
                "active checkpoint missing",
            )

            checkpoint.validate_integrity()

            require(
                checkpoint.checkpoint_id
                == manifest.active_checkpoint_id,
                "manifest checkpoint ID mismatch",
            )

            require(
                checkpoint.checkpoint_sequence
                == manifest.active_checkpoint_sequence,
                "manifest checkpoint sequence mismatch",
            )

            require(
                checkpoint.generation
                == manifest.generation,
                "manifest generation mismatch",
            )

            require(
                checkpoint.lineage_id
                == manifest.lineage_id,
                "manifest lineage mismatch",
            )

            require(
                checkpoint.recovery_epoch
                == manifest.recovery_epoch,
                "manifest recovery epoch mismatch",
            )

            require(
                checkpoint.WAL_length
                == manifest.WAL_length,
                "manifest WAL length mismatch",
            )

            require(
                secure_equal(
                    checkpoint.WAL_final_hash,
                    manifest.WAL_final_hash,
                ),
                "manifest WAL final hash mismatch",
            )

            return deep_copy(checkpoint)

    # ========================================================================
    # N.29 STAGE NEXT CHECKPOINT
    #
    # This writes the candidate checkpoint into the inactive slot.
    # It does NOT change the manifest and therefore does NOT make the
    # checkpoint authoritative.
    # ========================================================================

    def stage_checkpoint(
        self,
    ) -> CheckpointPromotion:
        with self.lock:
            manifest = self.state.checkpoint_manifest

            require(
                manifest is not None,
                "checkpoint manifest missing",
            )

            manifest.validate_integrity()

            require(
                self.state.pending_promotion is None,
                "checkpoint promotion already pending",
            )

            active_checkpoint = self.get_active_checkpoint()

            source_slot = manifest.active_slot
            target_slot = opposite_checkpoint_slot(
                source_slot
            )

            next_checkpoint_sequence = (
                self.state.highest_checkpoint_sequence_seen
                + 1
            )

            require(
                next_checkpoint_sequence
                > active_checkpoint.checkpoint_sequence,
                "checkpoint sequence did not advance",
            )

            image = self.build_checkpoint_state_image()

            staged_checkpoint = Checkpoint(
                checkpoint_id=new_uuid(),
                checkpoint_sequence=next_checkpoint_sequence,
                slot=target_slot,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                phase=self.state.phase,
                WAL_length=len(self.state.WAL),
                WAL_final_hash=current_WAL_hash(
                    self.state
                ),
                state_hash=sha256_hex(image),
                created_at_ns=utc_time_ns(),
            )

            staged_checkpoint.seal()
            staged_checkpoint.validate_integrity()

            self.state.checkpoint_slots[
                target_slot
            ] = staged_checkpoint

            self.state.checkpoint_state_images[
                target_slot
            ] = deep_copy(image)

            self.state.highest_checkpoint_sequence_seen = (
                next_checkpoint_sequence
            )

            next_promotion_sequence = (
                self.state.highest_promotion_sequence_seen
                + 1
            )

            promotion = CheckpointPromotion(
                promotion_id=new_uuid(),
                promotion_sequence=next_promotion_sequence,
                source_slot=source_slot,
                target_slot=target_slot,
                prior_checkpoint_id=active_checkpoint.checkpoint_id,
                target_checkpoint_id=staged_checkpoint.checkpoint_id,
                target_checkpoint_sequence=staged_checkpoint.checkpoint_sequence,
                generation=staged_checkpoint.generation,
                lineage_id=staged_checkpoint.lineage_id,
                recovery_epoch=staged_checkpoint.recovery_epoch,
                WAL_length=staged_checkpoint.WAL_length,
                WAL_final_hash=staged_checkpoint.WAL_final_hash,
                state=PROMOTION_STAGED,
                created_at_ns=utc_time_ns(),
                committed_at_ns=None,
            )

            promotion.seal()
            promotion.validate_integrity()

            self.state.pending_promotion = promotion
            self.state.highest_promotion_sequence_seen = (
                next_promotion_sequence
            )

            append_WAL(
                self.state,
                "CHECKPOINT_STAGED",
                {
                    "promotion_id": promotion.promotion_id,
                    "promotion_sequence": promotion.promotion_sequence,
                    "source_slot": source_slot,
                    "target_slot": target_slot,
                    "target_checkpoint_id": staged_checkpoint.checkpoint_id,
                    "target_checkpoint_sequence": staged_checkpoint.checkpoint_sequence,
                },
            )

            return deep_copy(promotion)

    # ========================================================================
    # VALIDATE STAGED PROMOTION
    # ========================================================================

    def validate_staged_promotion(
        self,
        promotion: CheckpointPromotion,
    ) -> Checkpoint:
        with self.lock:
            promotion.validate_integrity()

            require(
                promotion.state == PROMOTION_STAGED,
                "promotion is not staged",
            )

            require(
                self.state.pending_promotion is not None,
                "no pending checkpoint promotion",
            )

            current = self.state.pending_promotion

            require(
                promotion.promotion_id
                == current.promotion_id,
                "checkpoint promotion ID mismatch",
            )

            require(
                promotion.promotion_sequence
                == current.promotion_sequence,
                "checkpoint promotion sequence mismatch",
            )

            manifest = self.state.checkpoint_manifest

            require(
                manifest is not None,
                "checkpoint manifest missing",
            )

            manifest.validate_integrity()

            require(
                manifest.active_slot
                == promotion.source_slot,
                "promotion source slot is no longer active",
            )

            require(
                manifest.active_checkpoint_id
                == promotion.prior_checkpoint_id,
                "promotion prior checkpoint mismatch",
            )

            require(
                promotion.target_slot
                == opposite_checkpoint_slot(
                    promotion.source_slot
                ),
                "promotion target slot invalid",
            )

            checkpoint = self.state.checkpoint_slots.get(
                promotion.target_slot
            )

            require(
                checkpoint is not None,
                "staged checkpoint missing",
            )

            checkpoint.validate_integrity()

            require(
                checkpoint.checkpoint_id
                == promotion.target_checkpoint_id,
                "promotion target checkpoint ID mismatch",
            )

            require(
                checkpoint.checkpoint_sequence
                == promotion.target_checkpoint_sequence,
                "promotion checkpoint sequence mismatch",
            )

            require(
                checkpoint.checkpoint_sequence
                > manifest.active_checkpoint_sequence,
                "checkpoint rollback detected",
            )

            require(
                checkpoint.generation
                == promotion.generation,
                "promotion checkpoint generation mismatch",
            )

            require(
                checkpoint.lineage_id
                == promotion.lineage_id,
                "promotion checkpoint lineage mismatch",
            )

            require(
                checkpoint.recovery_epoch
                == promotion.recovery_epoch,
                "promotion checkpoint recovery epoch mismatch",
            )

            require(
                checkpoint.WAL_length
                == promotion.WAL_length,
                "promotion checkpoint WAL length mismatch",
            )

            require(
                secure_equal(
                    checkpoint.WAL_final_hash,
                    promotion.WAL_final_hash,
                ),
                "promotion checkpoint WAL hash mismatch",
            )

            image = self.state.checkpoint_state_images.get(
                promotion.target_slot
            )

            require(
                image is not None,
                "staged checkpoint state image missing",
            )

            self.validate_checkpoint(
                checkpoint,
                image,
            )

            return deep_copy(checkpoint)

    # ========================================================================
    # N.29 PROMOTION COMMIT
    #
    # Only this operation changes checkpoint authority.
    # ========================================================================

    def commit_checkpoint_promotion(
        self,
        promotion: CheckpointPromotion,
    ) -> CheckpointManifest:
        with self.lock:
            staged_checkpoint = (
                self.validate_staged_promotion(
                    promotion
                )
            )

            old_manifest = self.state.checkpoint_manifest

            require(
                old_manifest is not None,
                "checkpoint manifest missing",
            )

            next_manifest_sequence = (
                self.state.highest_manifest_sequence_seen
                + 1
            )

            require(
                next_manifest_sequence
                > old_manifest.manifest_sequence,
                "checkpoint manifest sequence did not advance",
            )

            committed_promotion = deep_copy(
                self.state.pending_promotion
            )

            require(
                committed_promotion is not None,
                "pending promotion disappeared",
            )

            committed_promotion.state = PROMOTION_COMMITTED
            committed_promotion.committed_at_ns = utc_time_ns()
            committed_promotion.seal()
            committed_promotion.validate_integrity()

            new_manifest = CheckpointManifest(
                manifest_sequence=next_manifest_sequence,
                active_slot=committed_promotion.target_slot,
                active_checkpoint_id=staged_checkpoint.checkpoint_id,
                active_checkpoint_sequence=staged_checkpoint.checkpoint_sequence,
                generation=staged_checkpoint.generation,
                lineage_id=staged_checkpoint.lineage_id,
                recovery_epoch=staged_checkpoint.recovery_epoch,
                WAL_length=staged_checkpoint.WAL_length,
                WAL_final_hash=staged_checkpoint.WAL_final_hash,
                last_promotion_sequence=committed_promotion.promotion_sequence,
                last_promotion_id=committed_promotion.promotion_id,
                updated_at_ns=utc_time_ns(),
            )

            new_manifest.seal()
            new_manifest.validate_integrity()

            require(
                new_manifest.active_checkpoint_sequence
                > old_manifest.active_checkpoint_sequence,
                "checkpoint rollback detected",
            )

            require(
                new_manifest.last_promotion_sequence
                > old_manifest.last_promotion_sequence,
                "promotion sequence rollback detected",
            )

            self.state.committed_promotions.append(
                committed_promotion
            )

            self.state.checkpoint_manifest = new_manifest

            self.state.highest_manifest_sequence_seen = (
                next_manifest_sequence
            )

            self.state.pending_promotion = None

            append_WAL(
                self.state,
                "CHECKPOINT_PROMOTED",
                {
                    "promotion_id": committed_promotion.promotion_id,
                    "promotion_sequence": committed_promotion.promotion_sequence,
                    "manifest_sequence": new_manifest.manifest_sequence,
                    "active_slot": new_manifest.active_slot,
                    "active_checkpoint_id": new_manifest.active_checkpoint_id,
                    "active_checkpoint_sequence": new_manifest.active_checkpoint_sequence,
                },
            )

            return deep_copy(new_manifest)

    # ========================================================================
    # COMPLETE CHECKPOINT ROTATION
    # ========================================================================

    def rotate_checkpoint(
        self,
    ) -> CheckpointManifest:
        with self.lock:
            promotion = self.stage_checkpoint()

            return self.commit_checkpoint_promotion(
                promotion
            )

    # ========================================================================
    # ABORT NON-AUTHORITATIVE STAGED CHECKPOINT
    #
    # Models recovery after a crash before promotion commit.
    # The manifest remains authoritative and the staged slot is discarded.
    # ========================================================================

    def discard_uncommitted_promotion(
        self,
    ) -> bool:
        with self.lock:
            promotion = self.state.pending_promotion

            if promotion is None:
                return False

            promotion.validate_integrity()

            require(
                promotion.state == PROMOTION_STAGED,
                "cannot discard committed promotion",
            )

            manifest = self.state.checkpoint_manifest

            require(
                manifest is not None,
                "checkpoint manifest missing",
            )

            require(
                manifest.active_slot
                == promotion.source_slot,
                "staged checkpoint became authoritative unexpectedly",
            )

            self.state.checkpoint_slots[
                promotion.target_slot
            ] = None

            self.state.checkpoint_state_images[
                promotion.target_slot
            ] = None

            append_WAL(
                self.state,
                "CHECKPOINT_STAGING_DISCARDED",
                {
                    "promotion_id": promotion.promotion_id,
                    "promotion_sequence": promotion.promotion_sequence,
                    "target_slot": promotion.target_slot,
                },
            )

            self.state.pending_promotion = None

            return True

    # ========================================================================
    # PROMOTION HISTORY VALIDATION
    # ========================================================================

    def validate_promotion_history(
        self,
    ) -> None:
        with self.lock:
            previous_sequence = 0
            previous_checkpoint_sequence = 0

            for promotion in self.state.committed_promotions:
                promotion.validate_integrity()

                require(
                    promotion.state == PROMOTION_COMMITTED,
                    "promotion history contains staged record",
                )

                require(
                    promotion.promotion_sequence
                    > previous_sequence,
                    "promotion history sequence rollback detected",
                )

                require(
                    promotion.target_checkpoint_sequence
                    > previous_checkpoint_sequence,
                    "promotion history checkpoint rollback detected",
                )

                previous_sequence = (
                    promotion.promotion_sequence
                )

                previous_checkpoint_sequence = (
                    promotion.target_checkpoint_sequence
                )

            manifest = self.state.checkpoint_manifest

            if manifest is not None:
                manifest.validate_integrity()

                if self.state.committed_promotions:
                    latest = (
                        self.state.committed_promotions[-1]
                    )

                    require(
                        manifest.last_promotion_sequence
                        == latest.promotion_sequence,
                        "manifest latest promotion sequence mismatch",
                    )

                    require(
                        manifest.last_promotion_id
                        == latest.promotion_id,
                        "manifest latest promotion ID mismatch",
                    )

    # ========================================================================
    # MANIFEST ROLLBACK FENCE
    # ========================================================================

    def validate_manifest_not_rolled_back(
        self,
        candidate: CheckpointManifest,
    ) -> None:
        with self.lock:
            candidate.validate_integrity()

            require(
                candidate.manifest_sequence
                >= self.state.highest_manifest_sequence_seen,
                "checkpoint manifest rollback detected",
            )

            require(
                candidate.active_checkpoint_sequence
                >= (
                    self.state.checkpoint_manifest.active_checkpoint_sequence
                    if self.state.checkpoint_manifest is not None
                    else 0
                ),
                "checkpoint rollback detected",
            )

            require(
                candidate.last_promotion_sequence
                >= (
                    self.state.checkpoint_manifest.last_promotion_sequence
                    if self.state.checkpoint_manifest is not None
                    else 0
                ),
                "promotion sequence rollback detected",
            )

    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(
        self,
    ) -> None:
        with self.lock:
            require(
                self.state.phase == PHASE_COMPLETED,
                "current generation is not completed",
            )

            require(
                self.state.pending_promotion is None,
                "cannot advance generation with pending checkpoint promotion",
            )

            self.state.prior_completed_dispatches.extend(
                deep_copy(
                    self.state.synthetic_dispatches
                )
            )

            prior_generation = self.state.generation
            prior_lineage = self.state.lineage_id
            prior_epoch = self.state.recovery_epoch

            self.state.generation += 1
            self.state.lineage_id = new_uuid()
            self.state.recovery_epoch += 1

            self.state.phase = PHASE_PREPARED

            self.state.current_lease = None
            self.state.authorization = None
            self.state.dispatch_commit = None
            self.state.synthetic_dispatches = []

            append_WAL(
                self.state,
                "GENERATION_ADVANCED",
                {
                    "prior_generation": prior_generation,
                    "new_generation": self.state.generation,
                    "prior_lineage_id": prior_lineage,
                    "new_lineage_id": self.state.lineage_id,
                    "prior_recovery_epoch": prior_epoch,
                    "new_recovery_epoch": self.state.recovery_epoch,
                },
            )

    # ========================================================================
    # SNAPSHOT FOR CRASH / RESTART TESTING
    # ========================================================================

    def snapshot_state(
        self,
    ) -> DurableState:
        with self.lock:
            return deep_copy(
                self.state
            )

    # ========================================================================
    # RESTORE FROM DURABLE STATE
    # ========================================================================

    @classmethod
    def restore_state(
        cls,
        durable_state: DurableState,
    ) -> "N29Engine":
        engine = cls.__new__(cls)

        engine.lock = threading.RLock()
        engine.state = deep_copy(
            durable_state
        )

        engine.validate_state()
        engine.validate_promotion_history()

        return engine

    # ========================================================================
    # RECOVERY OF INTERRUPTED CHECKPOINT PROMOTION
    #
    # STAGED:
    #   Target checkpoint never became authoritative.
    #   Keep manifest authority and discard staging.
    #
    # COMMITTED:
    #   Manifest already determines authority.
    #   No second promotion may occur.
    # ========================================================================

    def recover_checkpoint_promotion(
        self,
    ) -> str:
        with self.lock:
            manifest = self.state.checkpoint_manifest

            require(
                manifest is not None,
                "checkpoint manifest missing",
            )

            manifest.validate_integrity()

            pending = self.state.pending_promotion

            if pending is None:
                return "NO_PENDING_PROMOTION"

            pending.validate_integrity()

            require(
                pending.state == PROMOTION_STAGED,
                "pending
# ============================================================================
# R28 UNIT N.29
# TWO-PHASE CHECKPOINT PROMOTION + CRASH-SAFE SLOT ROTATION
# + PROMOTION FENCING + ROLLBACK-RESISTANT RECOVERY
#
# CORRECTED COPY/PASTE VERSION
# PART 3 OF 4
# ============================================================================


# ============================================================================
# TEST HELPERS
# ============================================================================

def expect_rejection(
    label: str,
    operation: Any,
) -> None:
    rejected = False

    try:
        operation()
    except (
        ValueError,
        RuntimeError,
        AssertionError,
    ):
        rejected = True

    pass_line(
        label,
        rejected,
    )


def make_engine_with_initial_checkpoint(
) -> N29Engine:
    engine = N29Engine()

    engine.create_initial_checkpoint()

    return engine


def make_completed_engine(
    owner_id: str = "worker-primary",
) -> N29Engine:
    engine = N29Engine()

    engine.complete_generation(
        owner_id
    )

    return engine


def make_completed_checkpointed_engine(
    owner_id: str = "worker-primary",
) -> N29Engine:
    engine = make_completed_engine(
        owner_id
    )

    engine.create_initial_checkpoint()

    return engine


# ============================================================================
# TEST 1
# BASELINE ENGINE + WAL INTEGRITY
# ============================================================================

def test_01_baseline_engine_and_WAL(
) -> None:
    test_header(
        1,
        "BASELINE ENGINE + WAL INTEGRITY",
    )

    engine = N29Engine()

    engine.validate_state()

    pass_line(
        "Initial Generation Is 1",
        engine.state.generation == 1,
    )

    pass_line(
        "Initial Recovery Epoch Is 0",
        engine.state.recovery_epoch == 0,
    )

    pass_line(
        "Initial Phase Is PREPARED",
        engine.state.phase == PHASE_PREPARED,
    )

    pass_line(
        "Payload Hash Valid",
        secure_equal(
            engine.state.payload_hash,
            sha256_hex(
                engine.state.payload
            ),
        ),
    )

    pass_line(
        "WAL Contains Initialization Record",
        len(engine.state.WAL) == 1,
    )

    validate_WAL(
        engine.state
    )

    pass_line(
        "WAL Hash Chain Valid",
        True,
    )


# ============================================================================
# TEST 2
# EXACTLY-ONCE SYNTHETIC GENERATION
# ============================================================================

def test_02_exactly_once_synthetic_generation(
) -> None:
    test_header(
        2,
        "EXACTLY-ONCE SYNTHETIC GENERATION",
    )

    engine = N29Engine()

    dispatch = engine.complete_generation(
        "worker-alpha"
    )

    pass_line(
        "Generation Reaches COMPLETED",
        engine.state.phase == PHASE_COMPLETED,
    )

    pass_line(
        "Exactly One Synthetic Dispatch Produced",
        len(
            engine.state.synthetic_dispatches
        ) == 1,
    )

    pass_line(
        "Dispatch Is Synthetic",
        dispatch.synthetic is True,
    )

    pass_line(
        "Authorization Consumed Exactly Once",
        len(
            engine.state.consumed_authorization_ids
        ) == 1,
    )

    pass_line(
        "Dispatch Identity Finalized",
        dispatch.dispatch_identity
        in engine.state.completed_dispatch_identities,
    )

    dispatch.validate()

    pass_line(
        "Synthetic Dispatch Validates",
        True,
    )


# ============================================================================
# TEST 3
# INITIAL CHECKPOINT + MANIFEST AUTHORITY
# ============================================================================

def test_03_initial_checkpoint_manifest(
) -> None:
    test_header(
        3,
        "INITIAL CHECKPOINT + MANIFEST AUTHORITY",
    )

    engine = make_engine_with_initial_checkpoint()

    checkpoint = engine.get_active_checkpoint()
    manifest = engine.state.checkpoint_manifest

    pass_line(
        "Initial Checkpoint Uses Slot A",
        checkpoint.slot == CHECKPOINT_SLOT_A,
    )

    pass_line(
        "Initial Checkpoint Sequence Is 1",
        checkpoint.checkpoint_sequence == 1,
    )

    pass_line(
        "Initial Manifest Exists",
        manifest is not None,
    )

    pass_line(
        "Manifest Uses Slot A",
        manifest is not None
        and manifest.active_slot == CHECKPOINT_SLOT_A,
    )

    pass_line(
        "Manifest Binds Active Checkpoint ID",
        manifest is not None
        and manifest.active_checkpoint_id
        == checkpoint.checkpoint_id,
    )

    pass_line(
        "Manifest Promotion Sequence Starts At Zero",
        manifest is not None
        and manifest.last_promotion_sequence == 0,
    )

    checkpoint.validate_integrity()

    if manifest is not None:
        manifest.validate_integrity()

    pass_line(
        "Initial Checkpoint + Manifest Integrity Valid",
        True,
    )


# ============================================================================
# TEST 4
# STAGED CHECKPOINT IS NON-AUTHORITATIVE
# ============================================================================

def test_04_staged_checkpoint_non_authority(
) -> None:
    test_header(
        4,
        "STAGED CHECKPOINT IS NON-AUTHORITATIVE",
    )

    engine = make_engine_with_initial_checkpoint()

    original_manifest = deep_copy(
        engine.state.checkpoint_manifest
    )

    original_active = engine.get_active_checkpoint()

    promotion = engine.stage_checkpoint()

    staged = engine.state.checkpoint_slots[
        promotion.target_slot
    ]

    active_after_stage = (
        engine.get_active_checkpoint()
    )

    pass_line(
        "Promotion State Is STAGED",
        promotion.state == PROMOTION_STAGED,
    )

    pass_line(
        "Staged Checkpoint Exists",
        staged is not None,
    )

    pass_line(
        "Staged Slot Is Opposite Active Slot",
        promotion.target_slot
        == opposite_checkpoint_slot(
            promotion.source_slot
        ),
    )

    pass_line(
        "Manifest Did Not Change During Staging",
        engine.state.checkpoint_manifest
        == original_manifest,
    )

    pass_line(
        "Old Checkpoint Remains Authoritative",
        active_after_stage.checkpoint_id
        == original_active.checkpoint_id,
    )

    pass_line(
        "Staged Checkpoint Is Not Authoritative",
        staged is not None
        and staged.checkpoint_id
        != active_after_stage.checkpoint_id,
    )


# ============================================================================
# TEST 5
# CHECKPOINT PROMOTION COMMIT
# ============================================================================

def test_05_checkpoint_promotion_commit(
) -> None:
    test_header(
        5,
        "CHECKPOINT PROMOTION COMMIT",
    )

    engine = make_engine_with_initial_checkpoint()

    old_manifest = deep_copy(
        engine.state.checkpoint_manifest
    )

    promotion = engine.stage_checkpoint()

    target_checkpoint = deep_copy(
        engine.state.checkpoint_slots[
            promotion.target_slot
        ]
    )

    new_manifest = (
        engine.commit_checkpoint_promotion(
            promotion
        )
    )

    pass_line(
        "Pending Promotion Cleared",
        engine.state.pending_promotion is None,
    )

    pass_line(
        "Promotion Added To Committed History",
        len(
            engine.state.committed_promotions
        ) == 1,
    )

    pass_line(
        "Committed Promotion State Is COMMITTED",
        engine.state.committed_promotions[
            -1
        ].state == PROMOTION_COMMITTED,
    )

    pass_line(
        "Manifest Sequence Advanced",
        old_manifest is not None
        and new_manifest.manifest_sequence
        > old_manifest.manifest_sequence,
    )

    pass_line(
        "Manifest Active Slot Rotated",
        old_manifest is not None
        and new_manifest.active_slot
        != old_manifest.active_slot,
    )

    pass_line(
        "Promoted Checkpoint Became Authoritative",
        target_checkpoint is not None
        and new_manifest.active_checkpoint_id
        == target_checkpoint.checkpoint_id,
    )

    pass_line(
        "Checkpoint Sequence Advanced",
        target_checkpoint is not None
        and old_manifest is not None
        and target_checkpoint.checkpoint_sequence
        > old_manifest.active_checkpoint_sequence,
    )

    engine.validate_promotion_history()

    pass_line(
        "Promotion History Valid",
        True,
    )


# ============================================================================
# TEST 6
# PRE-PROMOTION CRASH RECOVERY
# ============================================================================

def test_06_pre_promotion_crash_recovery(
) -> None:
    test_header(
        6,
        "PRE-PROMOTION CRASH RECOVERY",
    )

    engine = make_engine_with_initial_checkpoint()

    original_checkpoint = (
        engine.get_active_checkpoint()
    )

    promotion = engine.stage_checkpoint()

    snapshot = engine.snapshot_state()

    restored = N29Engine.restore_state(
        snapshot
    )

    result = (
        restored.recover_checkpoint_promotion()
    )

    recovered_active = (
        restored.get_active_checkpoint()
    )

    pass_line(
        "Interrupted Promotion Detected",
        result
        == "STAGED_PROMOTION_DISCARDED",
    )

    pass_line(
        "Pending Promotion Cleared After Recovery",
        restored.state.pending_promotion
        is None,
    )

    pass_line(
        "Pre-Promotion Active Checkpoint Preserved",
        recovered_active.checkpoint_id
        == original_checkpoint.checkpoint_id,
    )

    pass_line(
        "Staged Target Slot Discarded",
        restored.state.checkpoint_slots[
            promotion.target_slot
        ] is None,
    )

    pass_line(
        "Staged State Image Discarded",
        restored.state.checkpoint_state_images[
            promotion.target_slot
        ] is None,
    )


# ============================================================================
# TEST 7
# POST-PROMOTION CRASH RECOVERY
# ============================================================================

def test_07_post_promotion_crash_recovery(
) -> None:
    test_header(
        7,
        "POST-PROMOTION CRASH RECOVERY",
    )

    engine = make_engine_with_initial_checkpoint()

    promotion = engine.stage_checkpoint()

    manifest = (
        engine.commit_checkpoint_promotion(
            promotion
        )
    )

    snapshot = engine.snapshot_state()

    restored = N29Engine.restore_state(
        snapshot
    )

    result = (
        restored.recover_checkpoint_promotion()
    )

    active = restored.get_active_checkpoint()

    pass_line(
        "No Pending Promotion After Committed Restart",
        result == "NO_PENDING_PROMOTION",
    )

    pass_line(
        "Committed Active Slot Preserved",
        active.slot == manifest.active_slot,
    )

    pass_line(
        "Committed Checkpoint ID Preserved",
        active.checkpoint_id
        == manifest.active_checkpoint_id,
    )

    pass_line(
        "Exactly One Promotion Preserved",
        len(
            restored.state.committed_promotions
        ) == 1,
    )


# ============================================================================
# TEST 8
# MULTIPLE SLOT ROTATIONS ARE MONOTONIC
# ============================================================================

def test_08_multiple_slot_rotations(
) -> None:
    test_header(
        8,
        "MULTIPLE SLOT ROTATIONS ARE MONOTONIC",
    )

    engine = make_engine_with_initial_checkpoint()

    first_manifest = engine.rotate_checkpoint()
    second_manifest = engine.rotate_checkpoint()
    third_manifest = engine.rotate_checkpoint()

    sequences = [
        item.promotion_sequence
        for item in engine.state.committed_promotions
    ]

    checkpoint_sequences = [
        item.target_checkpoint_sequence
        for item in engine.state.committed_promotions
    ]

    pass_line(
        "Three Promotions Committed",
        len(sequences) == 3,
    )

    pass_line(
        "Promotion Sequence Strictly Monotonic",
        sequences
        == sorted(sequences)
        and len(set(sequences))
        == len(sequences),
    )

    pass_line(
        "Checkpoint Sequence Strictly Monotonic",
        checkpoint_sequences
        == sorted(checkpoint_sequences)
        and len(
            set(checkpoint_sequences)
        ) == len(checkpoint_sequences),
    )

    pass_line(
        "Checkpoint Slots Rotate",
        first_manifest.active_slot
        != second_manifest.active_slot
        and second_manifest.active_slot
        != third_manifest.active_slot,
    )

    pass_line(
        "Manifest Sequence Advanced Monotonically",
        first_manifest.manifest_sequence
        < second_manifest.manifest_sequence
        < third_manifest.manifest_sequence,
    )

    engine.validate_promotion_history()

    pass_line(
        "Multi-Rotation Promotion History Valid",
        True,
    )


# ============================================================================
# TEST 9
# PENDING PROMOTION REPLAY REJECTION
# ============================================================================

def test_09_pending_promotion_replay_rejection(
) -> None:
    test_header(
        9,
        "PENDING PROMOTION REPLAY REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    first = engine.stage_checkpoint()

    expect_rejection(
        "Second Concurrent Staging Rejected",
        lambda: engine.stage_checkpoint(),
    )

    engine.commit_checkpoint_promotion(
        first
    )

    expect_rejection(
        "Committed Promotion Replay Rejected",
        lambda: engine.commit_checkpoint_promotion(
            first
        ),
    )


# ============================================================================
# TEST 10
# PROMOTION INTEGRITY SEAL TAMPER REJECTION
# ============================================================================

def test_10_promotion_integrity_tamper(
) -> None:
    test_header(
        10,
        "PROMOTION INTEGRITY SEAL TAMPER REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    promotion = engine.stage_checkpoint()

    tampered = deep_copy(
        promotion
    )

    tampered.target_checkpoint_sequence += 100

    expect_rejection(
        "Tampered Promotion Rejected",
        lambda: engine.commit_checkpoint_promotion(
            tampered
        ),
    )


# ============================================================================
# TEST 11
# PROMOTION SOURCE SLOT TAMPER REJECTION
# ============================================================================

def test_11_promotion_source_slot_tamper(
) -> None:
    test_header(
        11,
        "PROMOTION SOURCE SLOT TAMPER REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    promotion = engine.stage_checkpoint()

    tampered = deep_copy(
        promotion
    )

    tampered.source_slot = tampered.target_slot
    tampered.seal()

    expect_rejection(
        "Forged Promotion Source Slot Rejected",
        lambda: engine.commit_checkpoint_promotion(
            tampered
        ),
    )


# ============================================================================
# TEST 12
# STAGED CHECKPOINT TAMPER REJECTION
# ============================================================================

def test_12_staged_checkpoint_tamper(
) -> None:
    test_header(
        12,
        "STAGED CHECKPOINT TAMPER REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    promotion = engine.stage_checkpoint()

    checkpoint = engine.state.checkpoint_slots[
        promotion.target_slot
    ]

    require(
        checkpoint is not None,
        "staged checkpoint missing",
    )

    checkpoint.generation += 1

    expect_rejection(
        "Tampered Staged Checkpoint Rejected",
        lambda: engine.commit_checkpoint_promotion(
            promotion
        ),
    )


# ============================================================================
# TEST 13
# STAGED STATE IMAGE TAMPER REJECTION
# ============================================================================

def test_13_staged_state_image_tamper(
) -> None:
    test_header(
        13,
        "STAGED STATE IMAGE TAMPER REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    promotion = engine.stage_checkpoint()

    image = (
        engine.state.checkpoint_state_images[
            promotion.target_slot
        ]
    )

    require(
        image is not None,
        "staged state image missing",
    )

    image["generation"] = 999999

    expect_rejection(
        "Tampered Staged State Image Rejected",
        lambda: engine.commit_checkpoint_promotion(
            promotion
        ),
    )


# ============================================================================
# TEST 14
# MANIFEST INTEGRITY TAMPER REJECTION
# ============================================================================

def test_14_manifest_tamper(
) -> None:
    test_header(
        14,
        "CHECKPOINT MANIFEST TAMPER REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    manifest = engine.state.checkpoint_manifest

    require(
        manifest is not None,
        "checkpoint manifest missing",
    )

    manifest.active_checkpoint_sequence += 1

    expect_rejection(
        "Tampered Checkpoint Manifest Rejected",
        lambda: engine.get_active_checkpoint(),
    )


# ============================================================================
# TEST 15
# MANIFEST ROLLBACK REJECTION
# ============================================================================

def test_15_manifest_rollback_rejection(
) -> None:
    test_header(
        15,
        "CHECKPOINT MANIFEST ROLLBACK REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    old_manifest = deep_copy(
        engine.state.checkpoint_manifest
    )

    engine.rotate_checkpoint()
    newer_manifest = deep_copy(
        engine.state.checkpoint_manifest
    )

    require(
        old_manifest is not None,
        "old manifest missing",
    )

    require(
        newer_manifest is not None,
        "new manifest missing",
    )

    expect_rejection(
        "Checkpoint Manifest Rollback Rejected",
        lambda: engine.validate_manifest_not_rolled_back(
            old_manifest
        ),
    )

    pass_line(
        "Newer Manifest Existed During Rollback Test",
        newer_manifest.manifest_sequence
        > old_manifest.manifest_sequence,
    )


# ============================================================================
# TEST 16
# PROMOTION SEQUENCE ROLLBACK REJECTION
# ============================================================================

def test_16_promotion_sequence_rollback(
) -> None:
    test_header(
        16,
        "PROMOTION SEQUENCE ROLLBACK REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    engine.rotate_checkpoint()
    engine.rotate_checkpoint()

    current_manifest = deep_copy(
        engine.state.checkpoint_manifest
    )

    require(
        current_manifest is not None,
        "current manifest missing",
    )

    forged = deep_copy(
        current_manifest
    )

    forged.manifest_sequence = (
        engine.state.highest_manifest_sequence_seen
    )

    forged.last_promotion_sequence -= 1
    forged.seal()

    expect_rejection(
        "Promotion Sequence Rollback Rejected",
        lambda: engine.validate_manifest_not_rolled_back(
            forged
        ),
    )


# ============================================================================
# TEST 17
# AUTHORITATIVE CHECKPOINT RECOVERY
# ============================================================================

def test_17_authoritative_checkpoint_recovery(
) -> None:
    test_header(
        17,
        "AUTHORITATIVE CHECKPOINT RECOVERY",
    )

    engine = make_completed_checkpointed_engine()

    engine.rotate_checkpoint()

    active = engine.get_active_checkpoint()

    image = (
        engine.recover_from_authoritative_checkpoint()
    )

    pass_line(
        "Recovered Image Uses Current Generation",
        image["generation"]
        == engine.state.generation,
    )

    pass_line(
        "Recovered Image Uses Current Lineage",
        image["lineage_id"]
        == engine.state.lineage_id,
    )

    pass_line(
        "Recovered Image Preserves COMPLETED Phase",
        image["phase"]
        == PHASE_COMPLETED,
    )

    pass_line(
        "Recovered Image Hash Matches Active Checkpoint",
        secure_equal(
            active.state_hash,
            sha256_hex(image),
        ),
    )


# ============================================================================
# TEST 18
# STALE CHECKPOINT WAL LENGTH REJECTION
# ============================================================================

def test_18_stale_checkpoint_rejection(
) -> None:
    test_header(
        18,
        "STALE CHECKPOINT REJECTION",
    )

    engine = make_engine_with_initial_checkpoint()

    manifest = engine.state.checkpoint_manifest

    require(
        manifest is not None,
        "checkpoint manifest missing",
    )

    active = engine.state.checkpoint_slots[
        manifest.active_slot
    ]

    require(
        active is not None,
        "active checkpoint missing",
    )

    active.WAL_length += 1
    active.seal()

    expect_rejection(
        "Stale Checkpoint Rejected",
        lambda: engine.recover_from_authoritative_checkpoint(),
    )


# ============================================================================
# TEST 19
# CHECKPOINT TO WAL FINAL HASH MISMATCH
# ============================================================================

def test_19_checkpoint_WAL_hash_mismatch(
) -> None:
    test_header(
        19,
        "CHECKPOINT TO WAL FINAL HASH MISMATCH",
    )

    engine = make_engine_with_initial_checkpoint()

    manifest = engine.state.checkpoint_manifest

    require(
        manifest is not None,
        "checkpoint manifest missing",
    )

    checkpoint = engine.state.checkpoint_slots[
        manifest.active_slot
    ]

    require(
        checkpoint is not None,
        "active checkpoint missing",
    )

    checkpoint.WAL_final_hash = "f" * 64
    checkpoint.seal()

    expect_rejection(
        "Checkpoint WAL Hash Mismatch Rejected",
        lambda: engine.recover_from_authoritative_checkpoint(),
    )


# ============================================================================
# TEST 20
# GENERATION ADVANCE + CHECKPOINT FENCING
# ============================================================================

def test_20_generation_advance_checkpoint_fencing(
) -> None:
    test_header(
        20,
        "GENERATION ADVANCE + CHECKPOINT GENERATION FENCING",
    )

    engine = make_completed_checkpointed_engine(
        "worker-generation-1"
    )

    first_generation = engine.state.generation
    first_lineage = engine.state.lineage_id
    first_epoch = engine.state.recovery_epoch

    first_dispatches = deep_copy(
        engine.state.synthetic_dispatches
    )

    engine.rotate_checkpoint()

    old_checkpoint = engine.get_active_checkpoint()

    engine.advance_generation()

    pass_line(
        "Generation Advanced Monotonically",
        engine.state.generation
        > first_generation,
    )

    pass_line(
        "Recovery Epoch Advanced Monotonically",
        engine.state.recovery_epoch
        > first_epoch,
    )

    pass_line(
        "New Generation Uses Different Lineage",
        engine.state.lineage_id
        != first_lineage,
    )

    pass_line(
        "New Generation Returns To PREPARED",
        engine.state.phase
        == PHASE_PREPARED,
    )

    pass_line(
        "Prior Completed Dispatch Preserved",
        len(
            engine.state.prior_completed_dispatches
        ) == len(first_dispatches),
    )

    new_manifest = engine.rotate_checkpoint()

    new_checkpoint = engine.get_active_checkpoint()

    pass_line(
        "New Checkpoint Uses Higher Generation",
        new_checkpoint.generation
        > old_checkpoint.generation,
    )

    pass_line(
        "New Checkpoint Uses New Lineage",
        new_checkpoint.lineage_id
        != old_checkpoint.lineage_id,
    )

    pass_line(
        "New Checkpoint Sequence Advanced",
        new_checkpoint.checkpoint_sequence
        > old_checkpoint.checkpoint_sequence,
    )

    pass_line(
        "New Promotion Sequence Advanced",
        new_manifest.last_promotion_sequence
        > 0,
    )


# ============================================================================
# TEST 21
# OWNER REUSE ACROSS GENERATION LINEAGE
# ============================================================================

def test_21_owner_reuse_across_generation(
) -> None:
    test_header(
        21,
        "OWNER REUSE ACROSS GENERATION LINEAGE",
    )

    engine = N29Engine()

    old_lease = engine.acquire_recovery_lease(
        "worker-reused"
    )

    authorization = engine.authorize(
        old_lease
    )

    commit = engine.commit_dispatch(
        old_lease,
        authorization,
    )

    engine.synthetic_dispatch(
        commit
    )

    engine.finalize()

    old_generation = old_lease.generation
    old_lineage = old_lease.lineage_id
    old_epoch = old_lease.recovery_epoch

    engine.advance_generation()

    new_lease = engine.acquire_recovery_lease(
        "worker-reused"
    )

    pass_line(
        "Reacquired Owner Uses Higher Generation",
        new_lease.generation
        > old_generation,
    )

    pass_line(
        "Reacquired Owner Uses Different Lineage",
        new_lease.lineage_id
        != old_lineage,
    )

    pass_line(
        "Reacquired Owner Uses Higher Epoch",
        new_lease.recovery_epoch
        > old_epoch,
    )

    expect_rejection(
        "Reused Owner Cannot Resurrect Prior Lease",
        lambda: engine.validate_recovery_lease(
            old_lease
        ),
    )


# ============================================================================
# TEST 22
# EXACT SYNTHETIC TRANSPORT BINDING
# ============================================================================

def test_22_exact_synthetic_transport_binding(
) -> None:
    test_header(
        22,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    engine = N29Engine()

    dispatch = engine.complete_generation(
        "worker-transport"
    )

    pass_line(
        "Transport Method Exactly POST",
        dispatch.method == HTTP_METHOD,
    )

    pass_line(
        "Transport Path Exactly Leverage Endpoint",
        dispatch.path == LEVERAGE_ENDPOINT,
    )

    pass_line(
        "Transport Payload Hash Preserved",
        secure_equal(
            dispatch.payload_hash,
            engine.state.payload_hash,
        ),
    )

    pass_line(
        "Transport Payload Exactly Preserved",
        dispatch.payload
        == engine.state.payload,
    )

    pass_line(
        "Dispatch Remains Synthetic",
        dispatch.synthetic is True,
    )


# ============================================================================
# TEST 23
# TORN WAL TAIL REJECTION
# ============================================================================

def test_23_torn_WAL_tail_rejection(
) -> None:
    test_header(
        23,
        "TORN WAL TAIL REJECTION",
    )

    engine = make_completed_checkpointed_engine()

    corrupted = engine.snapshot_state()

    require(
        bool(corrupted.WAL),
        "WAL unexpectedly empty",
    )

    corrupted.WAL[-1].record_hash = (
        "0" * 64
    )

    expect_rejection(
        "Torn WAL Tail Rejected",
        lambda: N29Engine.restore_state(
            corrupted
        ),
    )


# ============================================================================
# TEST 24
# HISTORICAL WAL TAMPER REJECTION
# ============================================================================

def test_24_historical_WAL_tamper(
) -> None:
    test_header(
        24,
        "HISTORICAL WAL RECORD TAMPER REJECTION",
    )

    engine = make_completed_checkpointed_engine()

    corrupted = engine.snapshot_state()

    require(
        len(corrupted.WAL) >= 2,
        "insufficient WAL records",
    )

    corrupted.WAL[0].record_type = (
        "FORGED_INITIAL_RECORD"
    )

    expect_rejection(
        "Historical WAL Tamper Rejected",
        lambda: N29Engine.restore_state(
            corrupted
        ),
    )


# ============================================================================
# TEST 25
# CRASH AFTER STAGING CANNOT CHANGE AUTHORITY
# ============================================================================

def test_25_crash_after_staging_authority_fence(
) -> None:
    test_header(
        25,
        "CRASH AFTER STAGING CANNOT CHANGE AUTHORITY",
    )

    engine = make_engine_with_initial_checkpoint()

    before = engine.get_active_checkpoint()

    promotion = engine.stage_checkpoint()

    snapshot = engine.snapshot_state()

    restored = N29Engine.restore_state(
        snapshot
    )

    before_recovery = (
        restored.get_active_checkpoint()
    )

    pass_line(
        "Manifest Still Points To Pre-Crash Checkpoint",
        before_recovery.checkpoint_id
        == before.checkpoint_id,
    )

    pass_line(
        "Staged Slot Cannot Self-Promote",
        before_recovery.slot
        == promotion.source_slot,
    )

    restored.recover_checkpoint_promotion()

    after_recovery = (
        restored.get_active_checkpoint()
    )

    pass_line(
        "Authority Preserved After Crash Recovery",
        after_recovery.checkpoint_id
        == before.checkpoint_id,
    )


# ============================================================================
# TEST 26
# COMMITTED PROMOTION CANNOT BE DISCARDED
# ============================================================================

def test_26_committed_promotion_non_discardable(
) -> None:
    test_header(
        26,
        "COMMITTED PROMOTION CANNOT BE DISCARDED",
    )

    engine = make_engine_with_initial_checkpoint()

    promotion = engine.stage_checkpoint()

    manifest = engine.commit_checkpoint_promotion(
        promotion
    )

    discarded = (
        engine.discard_uncommitted_promotion()
    )

    active = engine.get_active_checkpoint()

    pass_line(
        "No Pending Promotion Exists",
        engine.state.pending_promotion
        is None,
    )

    pass_line(
        "Committed Promotion Was Not Discarded",
        discarded is False,
    )

    pass_line(
        "Committed Checkpoint Remains Authoritative",
        active.checkpoint_id
        == manifest.active_checkpoint_id,
    )


# ============================================================================
# TEST 27
# PENDING PROMOTION BLOCKS GENERATION ADVANCE
# ============================================================================

def test_27_pending_promotion_generation_fence(
) -> None:
    test_header(
        27,
        "PENDING PROMOTION BLOCKS GENERATION ADVANCE",
    )

    engine = make_completed_checkpointed_engine()

    engine.stage_checkpoint()

    expect_rejection(
        "Generation Advance With Pending Promotion Rejected",
        lambda: engine.advance_generation(),
    )


# ============================================================================
# TEST 28
# CHECKPOINT SLOT STRUCTURAL FENCING
# ============================================================================

def test_28_checkpoint_slot_structural_fencing(
) -> None:
    test_header(
        28,
        "CHECKPOINT SLOT STRUCTURAL FENCING",
    )

    engine = make_engine_with_initial_checkpoint()

    promotion = engine.stage_checkpoint()

    checkpoint = engine.state.checkpoint_slots[
        promotion.target_slot
    ]

    require(
        checkpoint is not None,
        "staged checkpoint missing",
    )

    checkpoint.slot = promotion.source_slot
    checkpoint.seal()

    expect_rejection(
        "Checkpoint Stored In Wrong Slot Rejected",
        lambda: engine.validate_state(),
    )


# ============================================================================
# TEST 29
# FINAL NETWORK WRITE FIREBREAK
# ============================================================================

def test_29_final_network_write_firebreak(
) -> None:
    test_header(
        29,
        "FINAL NETWORK WRITE FIREBREAK",
    )

    pass_line(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    pass_line(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    pass_line
# ============================================================================
# R28 UNIT N.29
# TWO-PHASE CHECKPOINT PROMOTION + CRASH-SAFE SLOT ROTATION
# + PROMOTION FENCING + ROLLBACK-RESISTANT RECOVERY
#
# CORRECTED COPY/PASTE VERSION
# PART 4 OF 4
# ============================================================================


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
                    "live_execution": LIVE_ORDER_EXECUTION,
                    "demo_execution": DEMO_ORDER_EXECUTION,
                    "real_post": REAL_POST_ENABLED,
                    "demo_post": DEMO_POST_ENABLED,
                    "network_writes": NETWORK_WRITES_ENABLED,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                },
                sort_keys=True,
            ).encode(
                "utf-8"
            )

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

            self.wfile.write(
                body
            )

            return

        self.send_response(404)
        self.end_headers()

    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:
        return


# ============================================================================
# HEALTH SERVER STARTUP
# ============================================================================

def start_health_server(
) -> None:
    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )

    def runner(
    ) -> None:
        try:
            server = HTTPServer(
                (
                    "0.0.0.0",
                    port,
                ),
                HealthHandler,
            )

            print(
                f"{UNIT_NAME}: HEALTH SERVER LISTENING ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"{UNIT_NAME}: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        name="n29-health-server",
        daemon=True,
    )

    thread.start()


# ============================================================================
# POST-DIAGNOSTIC SAFETY ASSERTIONS
# ============================================================================

def post_diagnostic_safety_assertions(
) -> None:
    require(
        LIVE_ORDER_EXECUTION is False,
        "live execution unexpectedly enabled",
    )

    require(
        DEMO_ORDER_EXECUTION is False,
        "demo execution unexpectedly enabled",
    )

    require(
        REAL_POST_ENABLED is False,
        "real POST unexpectedly enabled",
    )

    require(
        DEMO_POST_ENABLED is False,
        "demo POST unexpectedly enabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "network writes unexpectedly enabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "synthetic transport-only gate disabled",
    )

    require(
        NETWORK_WRITE_COUNT == 0,
        "network write count is non-zero",
    )

    require(
        REAL_POST_COUNT == 0,
        "real POST count is non-zero",
    )

    require(
        DEMO_POST_COUNT == 0,
        "demo POST count is non-zero",
    )

    print(
        f"{UNIT_NAME}: POST-DIAGNOSTIC SAFETY ASSERTIONS PASSED",
        flush=True,
    )


# ============================================================================
# PERSISTENT RUNTIME
# ============================================================================

def persistent_runtime(
) -> None:
    print(
        f"{UNIT_NAME}: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: ✅ NO REAL POST — NO DEMO POST — NO NETWORK WRITE",
        flush=True,
    )

    major_separator()

    while True:
        time.sleep(
            60
        )


# ============================================================================
# MAIN
# ============================================================================

def main(
) -> None:
    run_N29_diagnostic()

    post_diagnostic_safety_assertions()

    start_health_server()

    print(
        f"{UNIT_NAME}: HEALTH SERVER STARTED",
        flush=True,
    )

    persistent_runtime()


print(
    "R28 UNIT N.29: PART 4 DEFINITIONS LOADED",
    flush=True,
)


# ============================================================================
# ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    main()


# ============================================================================
# END OF R28 UNIT N.29
#
# EXPECTED FINAL RESULT:
#
# ✅ R28 UNIT N.29 PASSED — TWO-PHASE CHECKPOINT PROMOTION
#    + CRASH-SAFE SLOT ROTATION VALIDATED
#
# ✅ STAGED CHECKPOINTS CANNOT BECOME AUTHORITATIVE WITHOUT
#    A COMMITTED PROMOTION
#
# ✅ PROMOTION / CHECKPOINT / MANIFEST ROLLBACK FENCING ACTIVE
#
# ✅ NO REAL ORDER WAS SENT
# ✅ NO DEMO ORDER WAS SENT
# ✅ NO NETWORK WRITE OCCURRED
#
# HEALTH SERVER:
#   /
#   /health
#   /healthz
#
# DEFAULT PORT:
#   10000
# ============================================================================
