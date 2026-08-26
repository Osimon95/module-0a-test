# ============================================================================
# R28 UNIT N.28
# DUAL CHECKPOINT RECOVERY + ROLLBACK-RESISTANT CHECKPOINT SELECTION
# + DURABLE WAL + EXACTLY-ONCE SYNTHETIC DISPATCH
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
# N.28 INCREMENT OVER N.27:
#   - DUAL CHECKPOINT SLOTS A/B
#   - MONOTONIC CHECKPOINT SEQUENCE
#   - CHECKPOINT GENERATION FENCING
#   - CHECKPOINT RECOVERY EPOCH FENCING
#   - ROLLBACK / STALE CHECKPOINT REJECTION
#   - NEWEST VALID CHECKPOINT SELECTION
#   - SINGLE-SLOT CORRUPTION RECOVERY
#   - DUAL-SLOT CORRUPTION REJECTION
#   - CHECKPOINT MANIFEST INTEGRITY SEAL
#   - CHECKPOINT / WAL FINAL-HASH BINDING
#   - DURABLE DISPATCH COMMIT PRESERVED
#   - PRE-COMMIT CRASH RECOVERY
#   - POST-COMMIT / PRE-DISPATCH CRASH RECOVERY
#   - POST-DISPATCH / PRE-FINALIZATION CRASH RECOVERY
#   - EXACTLY-ONCE SYNTHETIC DISPATCH FENCING
#   - GENERATION / LINEAGE / EPOCH ANTI-ABA FENCING
# ============================================================================

print("R28 UNIT N.28: MAIN.PY ENTERED", flush=True)

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


print("R28 UNIT N.28: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.28"
UNIT_VERSION = "N.28"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

TARGET_LEVERAGE = 100

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True


# ============================================================================
# CRYPTOGRAPHIC / INTEGRITY KEYS
# ============================================================================

INTEGRITY_KEY = b"R28-N28-LOCAL-INTEGRITY-KEY"
CERTIFICATE_KEY = b"R28-N28-RECOVERY-CERTIFICATE-KEY"
CHECKPOINT_KEY = b"R28-N28-DUAL-CHECKPOINT-KEY"
MANIFEST_KEY = b"R28-N28-CHECKPOINT-MANIFEST-KEY"


# ============================================================================
# STATE MACHINE PHASES
# ============================================================================

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

VALID_PHASES: Set[str] = {
    PHASE_PREPARED,
    PHASE_AUTHORIZED,
    PHASE_COMMITTED,
    PHASE_DISPATCHED,
    PHASE_COMPLETED,
}

TERMINAL_PHASES: Set[str] = {
    PHASE_COMPLETED,
}


# ============================================================================
# WAL EVENT TYPES
# ============================================================================

EVENT_PREPARED = "PREPARED"
EVENT_AUTHORIZED = "AUTHORIZED"
EVENT_DISPATCH_COMMITTED = "DISPATCH_COMMITTED"
EVENT_SYNTHETIC_DISPATCHED = "SYNTHETIC_DISPATCHED"
EVENT_COMPLETED = "COMPLETED"
EVENT_GENERATION_ADVANCED = "GENERATION_ADVANCED"
EVENT_RECOVERY_LEASE_ACQUIRED = "RECOVERY_LEASE_ACQUIRED"
EVENT_AUTHORIZATION_CONSUMED = "AUTHORIZATION_CONSUMED"

VALID_EVENT_TYPES: Set[str] = {
    EVENT_PREPARED,
    EVENT_AUTHORIZED,
    EVENT_DISPATCH_COMMITTED,
    EVENT_SYNTHETIC_DISPATCHED,
    EVENT_COMPLETED,
    EVENT_GENERATION_ADVANCED,
    EVENT_RECOVERY_LEASE_ACQUIRED,
    EVENT_AUTHORIZATION_CONSUMED,
}


# ============================================================================
# CHECKPOINT CONSTANTS
# ============================================================================

CHECKPOINT_SLOT_A = "A"
CHECKPOINT_SLOT_B = "B"

VALID_CHECKPOINT_SLOTS: Set[str] = {
    CHECKPOINT_SLOT_A,
    CHECKPOINT_SLOT_B,
}


# ============================================================================
# COUNTERS — MUST REMAIN ZERO FOR REAL/DEMO NETWORK WRITES
# ============================================================================

NETWORK_WRITE_COUNT = 0
REAL_POST_COUNT = 0
DEMO_POST_COUNT = 0


print("R28 UNIT N.28: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# LOCAL BLOCK / ASSERTION HELPERS
# ============================================================================

class LocalSafetyBlock(RuntimeError):
    pass


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)
    raise LocalSafetyBlock(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        local_block(message)


def check(condition: bool, label: str) -> None:
    if not condition:
        print(f"{label:<80} ❌ FAIL", flush=True)
        raise AssertionError(label)

    print(f"{label:<80} ✅ PASS", flush=True)


def separator() -> None:
    print("-" * 92, flush=True)


def banner() -> None:
    print("=" * 92, flush=True)


# ============================================================================
# CANONICAL SERIALIZATION
# ============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
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


# ============================================================================
# IDENTIFIERS
# ============================================================================

def new_lineage_id() -> str:
    return uuid.uuid4().hex


def new_owner_nonce() -> str:
    return uuid.uuid4().hex


def deterministic_dispatch_id(
    generation: int,
    lineage_id: str,
    payload_hash: str,
) -> str:
    material = {
        "unit": UNIT_VERSION,
        "generation": generation,
        "lineage_id": lineage_id,
        "payload_hash": payload_hash,
        "transport_method": HTTP_METHOD,
        "transport_path": LEVERAGE_ENDPOINT,
    }

    return sha256_hex(material)[:32]


def deterministic_commit_id(
    generation: int,
    lineage_id: str,
    recovery_epoch: int,
    dispatch_id: str,
    payload_hash: str,
) -> str:
    material = {
        "unit": UNIT_VERSION,
        "generation": generation,
        "lineage_id": lineage_id,
        "recovery_epoch": recovery_epoch,
        "dispatch_id": dispatch_id,
        "payload_hash": payload_hash,
    }

    return sha256_hex(material)[:40]


# ============================================================================
# LEVERAGE PAYLOAD
# ============================================================================

def build_leverage_payload(
    symbol: str = SYMBOL,
    leverage: int = TARGET_LEVERAGE,
) -> Dict[str, Any]:
    require(
        isinstance(symbol, str) and bool(symbol.strip()),
        "symbol is empty",
    )

    require(
        isinstance(leverage, int),
        "leverage must be integer",
    )

    require(
        1 <= leverage <= 100,
        "leverage outside local safety range",
    )

    return {
        "symbol": symbol.strip().upper(),
        "leverage": leverage,
    }


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class RecoveryLease:
    owner_id: str
    owner_nonce: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    issued_at_ns: int

    consumed: bool = False


@dataclass
class RecoveryAuthorization:
    authorization_id: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    payload_hash: str
    dispatch_id: str

    issued_at_ns: int

    consumed: bool = False

    seal: str = ""


@dataclass
class DispatchCommit:
    commit_id: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    dispatch_id: str

    method: str
    path: str

    payload: Dict[str, Any]
    payload_hash: str

    committed_at_ns: int

    dispatched: bool = False
    finalized: bool = False

    seal: str = ""


@dataclass
class SyntheticDispatch:
    dispatch_id: str
    commit_id: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    method: str
    path: str

    payload: Dict[str, Any]
    payload_hash: str

    dispatched_at_ns: int


@dataclass
class WALRecord:
    index: int

    event_type: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    timestamp_ns: int

    data: Dict[str, Any]

    previous_hash: str
    record_hash: str


@dataclass
class DurableState:
    generation: int = 1
    lineage_id: str = field(default_factory=new_lineage_id)
    recovery_epoch: int = 0

    phase: str = PHASE_PREPARED

    payload: Dict[str, Any] = field(
        default_factory=lambda: build_leverage_payload()
    )

    payload_hash: str = ""

    active_lease: Optional[RecoveryLease] = None
    authorization: Optional[RecoveryAuthorization] = None
    dispatch_commit: Optional[DispatchCommit] = None

    synthetic_dispatches: List[SyntheticDispatch] = field(
        default_factory=list
    )

    completed_dispatch_ids: Set[str] = field(
        default_factory=set
    )

    checkpoint_sequence: int = 0

    def __post_init__(self) -> None:
        if not self.payload_hash:
            self.payload_hash = sha256_hex(self.payload)


@dataclass
class Checkpoint:
    slot: str

    sequence: int

    generation: int
    lineage_id: str
    recovery_epoch: int

    wal_length: int
    wal_final_hash: str

    created_at_ns: int

    state: Dict[str, Any]

    integrity_seal: str = ""


@dataclass
class CheckpointManifest:
    active_slot: str

    highest_sequence: int

    generation: int
    lineage_id: str
    recovery_epoch: int

    slot_a_sequence: int
    slot_b_sequence: int

    updated_at_ns: int

    seal: str = ""


# ============================================================================
# DATACLASS SERIALIZATION HELPERS
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

    return copy.deepcopy(asdict(commit))


def dispatch_to_dict(
    dispatch: SyntheticDispatch,
) -> Dict[str, Any]:
    return copy.deepcopy(asdict(dispatch))


def durable_state_to_dict(
    state: DurableState,
) -> Dict[str, Any]:
    return {
        "generation": state.generation,
        "lineage_id": state.lineage_id,
        "recovery_epoch": state.recovery_epoch,
        "phase": state.phase,
        "payload": copy.deepcopy(state.payload),
        "payload_hash": state.payload_hash,
        "active_lease": lease_to_dict(state.active_lease),
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
        "completed_dispatch_ids": sorted(
            state.completed_dispatch_ids
        ),
        "checkpoint_sequence": state.checkpoint_sequence,
    }


def recovery_lease_from_dict(
    data: Optional[Dict[str, Any]],
) -> Optional[RecoveryLease]:
    if data is None:
        return None

    return RecoveryLease(
        owner_id=str(data["owner_id"]),
        owner_nonce=str(data["owner_nonce"]),
        generation=int(data["generation"]),
        lineage_id=str(data["lineage_id"]),
        recovery_epoch=int(data["recovery_epoch"]),
        issued_at_ns=int(data["issued_at_ns"]),
        consumed=bool(data.get("consumed", False)),
    )


def recovery_authorization_from_dict(
    data: Optional[Dict[str, Any]],
) -> Optional[RecoveryAuthorization]:
    if data is None:
        return None

    return RecoveryAuthorization(
        authorization_id=str(
            data["authorization_id"]
        ),
        generation=int(data["generation"]),
        lineage_id=str(data["lineage_id"]),
        recovery_epoch=int(data["recovery_epoch"]),
        payload_hash=str(data["payload_hash"]),
        dispatch_id=str(data["dispatch_id"]),
        issued_at_ns=int(data["issued_at_ns"]),
        consumed=bool(data.get("consumed", False)),
        seal=str(data["seal"]),
    )


def dispatch_commit_from_dict(
    data: Optional[Dict[str, Any]],
) -> Optional[DispatchCommit]:
    if data is None:
        return None

    return DispatchCommit(
        commit_id=str(data["commit_id"]),
        generation=int(data["generation"]),
        lineage_id=str(data["lineage_id"]),
        recovery_epoch=int(data["recovery_epoch"]),
        dispatch_id=str(data["dispatch_id"]),
        method=str(data["method"]),
        path=str(data["path"]),
        payload=copy.deepcopy(data["payload"]),
        payload_hash=str(data["payload_hash"]),
        committed_at_ns=int(data["committed_at_ns"]),
        dispatched=bool(data.get("dispatched", False)),
        finalized=bool(data.get("finalized", False)),
        seal=str(data["seal"]),
    )


def synthetic_dispatch_from_dict(
    data: Dict[str, Any],
) -> SyntheticDispatch:
    return SyntheticDispatch(
        dispatch_id=str(data["dispatch_id"]),
        commit_id=str(data["commit_id"]),
        generation=int(data["generation"]),
        lineage_id=str(data["lineage_id"]),
        recovery_epoch=int(data["recovery_epoch"]),
        method=str(data["method"]),
        path=str(data["path"]),
        payload=copy.deepcopy(data["payload"]),
        payload_hash=str(data["payload_hash"]),
        dispatched_at_ns=int(data["dispatched_at_ns"]),
    )


def durable_state_from_dict(
    data: Dict[str, Any],
) -> DurableState:
    state = DurableState(
        generation=int(data["generation"]),
        lineage_id=str(data["lineage_id"]),
        recovery_epoch=int(data["recovery_epoch"]),
        phase=str(data["phase"]),
        payload=copy.deepcopy(data["payload"]),
        payload_hash=str(data["payload_hash"]),
        active_lease=recovery_lease_from_dict(
            data.get("active_lease")
        ),
        authorization=recovery_authorization_from_dict(
            data.get("authorization")
        ),
        dispatch_commit=dispatch_commit_from_dict(
            data.get("dispatch_commit")
        ),
        synthetic_dispatches=[
            synthetic_dispatch_from_dict(item)
            for item in data.get(
                "synthetic_dispatches",
                [],
            )
        ],
        completed_dispatch_ids=set(
            data.get(
                "completed_dispatch_ids",
                [],
            )
        ),
        checkpoint_sequence=int(
            data.get(
                "checkpoint_sequence",
                0,
            )
        ),
    )

    return state


# ============================================================================
# AUTHORIZATION SEAL
# ============================================================================

def authorization_seal_material(
    authorization: RecoveryAuthorization,
) -> Dict[str, Any]:
    return {
        "authorization_id": authorization.authorization_id,
        "generation": authorization.generation,
        "lineage_id": authorization.lineage_id,
        "recovery_epoch": authorization.recovery_epoch,
        "payload_hash": authorization.payload_hash,
        "dispatch_id": authorization.dispatch_id,
        "issued_at_ns": authorization.issued_at_ns,
        "consumed": authorization.consumed,
    }


def seal_authorization(
    authorization: RecoveryAuthorization,
) -> str:
    return hmac_hex(
        CERTIFICATE_KEY,
        authorization_seal_material(
            authorization
        ),
    )


def validate_authorization_seal(
    authorization: RecoveryAuthorization,
) -> None:
    expected = seal_authorization(
        authorization
    )

    require(
        secure_equal(
            authorization.seal,
            expected,
        ),
        "authorization integrity seal mismatch",
    )


# ============================================================================
# DISPATCH COMMIT SEAL
# ============================================================================

def commit_seal_material(
    commit: DispatchCommit,
) -> Dict[str, Any]:
    return {
        "commit_id": commit.commit_id,
        "generation": commit.generation,
        "lineage_id": commit.lineage_id,
        "recovery_epoch": commit.recovery_epoch,
        "dispatch_id": commit.dispatch_id,
        "method": commit.method,
        "path": commit.path,
        "payload": copy.deepcopy(commit.payload),
        "payload_hash": commit.payload_hash,
        "committed_at_ns": commit.committed_at_ns,
        "dispatched": commit.dispatched,
        "finalized": commit.finalized,
    }


def seal_dispatch_commit(
    commit: DispatchCommit,
) -> str:
    return hmac_hex(
        INTEGRITY_KEY,
        commit_seal_material(
            commit
        ),
    )


def validate_dispatch_commit_seal(
    commit: DispatchCommit,
) -> None:
    expected = seal_dispatch_commit(
        commit
    )

    require(
        secure_equal(
            commit.seal,
            expected,
        ),
        "dispatch commit integrity seal mismatch",
    )


# ============================================================================
# WAL
# ============================================================================

class DurableWAL:
    def __init__(self) -> None:
        self.records: List[WALRecord] = []
        self._lock = threading.RLock()

    @staticmethod
    def _record_material(
        index: int,
        event_type: str,
        generation: int,
        lineage_id: str,
        recovery_epoch: int,
        timestamp_ns: int,
        data: Dict[str, Any],
        previous_hash: str,
    ) -> Dict[str, Any]:
        return {
            "index": index,
            "event_type": event_type,
            "generation": generation,
            "lineage_id": lineage_id,
            "recovery_epoch": recovery_epoch,
            "timestamp_ns": timestamp_ns,
            "data": copy.deepcopy(data),
            "previous_hash": previous_hash,
        }

    @staticmethod
    def calculate_record_hash(
        index: int,
        event_type: str,
        generation: int,
        lineage_id: str,
        recovery_epoch: int,
        timestamp_ns: int,
        data: Dict[str, Any],
        previous_hash: str,
    ) -> str:
        material = DurableWAL._record_material(
            index=index,
            event_type=event_type,
            generation=generation,
            lineage_id=lineage_id,
            recovery_epoch=recovery_epoch,
            timestamp_ns=timestamp_ns,
            data=data,
            previous_hash=previous_hash,
        )

        return hmac_hex(
            INTEGRITY_KEY,
            material,
        )

    def append(
        self,
        event_type: str,
        generation: int,
        lineage_id: str,
        recovery_epoch: int,
        data: Dict[str, Any],
    ) -> WALRecord:
        with self._lock:
            require(
                event_type in VALID_EVENT_TYPES,
                "invalid WAL event type",
            )

            require(
                generation >= 1,
                "invalid WAL generation",
            )

            require(
                bool(lineage_id),
                "invalid WAL lineage",
            )

            require(
                recovery_epoch >= 0,
                "invalid WAL recovery epoch",
            )

            index = len(self.records)

            previous_hash = (
                self.records[-1].record_hash
                if self.records
                else "GENESIS"
            )

            timestamp_ns = time.time_ns()

            record_hash = self.calculate_record_hash(
                index=index,
                event_type=event_type,
                generation=generation,
                lineage_id=lineage_id,
                recovery_epoch=recovery_epoch,
                timestamp_ns=timestamp_ns,
                data=data,
                previous_hash=previous_hash,
            )

            record = WALRecord(
                index=index,
                event_type=event_type,
                generation=generation,
                lineage_id=lineage_id,
                recovery_epoch=recovery_epoch,
                timestamp_ns=timestamp_ns,
                data=copy.deepcopy(data),
                previous_hash=previous_hash,
                record_hash=record_hash,
            )

            self.records.append(record)

            return copy.deepcopy(record)

    def final_hash(self) -> str:
        with self._lock:
            if not self.records:
                return "GENESIS"

            return self.records[-1].record_hash

    def length(self) -> int:
        with self._lock:
            return len(self.records)

    def clone(self) -> "DurableWAL":
        cloned = DurableWAL()

        with self._lock:
            cloned.records = copy.deepcopy(
                self.records
            )

        return cloned

    def validate(self) -> None:
        with self._lock:
            previous_hash = "GENESIS"

            for expected_index, record in enumerate(
                self.records
            ):
                require(
                    record.index == expected_index,
                    "WAL index sequence mismatch",
                )

                require(
                    record.event_type
                    in VALID_EVENT_TYPES,
                    "invalid WAL event type",
                )

                require(
                    record.previous_hash
                    == previous_hash,
                    "WAL previous hash mismatch",
                )

                expected_hash = (
                    self.calculate_record_hash(
                        index=record.index,
                        event_type=record.event_type,
                        generation=record.generation,
                        lineage_id=record.lineage_id,
                        recovery_epoch=record.recovery_epoch,
                        timestamp_ns=record.timestamp_ns,
                        data=record.data,
                        previous_hash=record.previous_hash,
                    )
                )

                require(
                    secure_equal(
                        record.record_hash,
                        expected_hash,
                    ),
                    "WAL record hash mismatch",
                )

                previous_hash = record.record_hash


# ============================================================================
# CHECKPOINT INTEGRITY
# ============================================================================

def checkpoint_seal_material(
    checkpoint: Checkpoint,
) -> Dict[str, Any]:
    return {
        "slot": checkpoint.slot,
        "sequence": checkpoint.sequence,
        "generation": checkpoint.generation,
        "lineage_id": checkpoint.lineage_id,
        "recovery_epoch": checkpoint.recovery_epoch,
        "wal_length": checkpoint.wal_length,
        "wal_final_hash": checkpoint.wal_final_hash,
        "created_at_ns": checkpoint.created_at_ns,
        "state": copy.deepcopy(checkpoint.state),
    }


def seal_checkpoint(
    checkpoint: Checkpoint,
) -> str:
    return hmac_hex(
        CHECKPOINT_KEY,
        checkpoint_seal_material(
            checkpoint
        ),
    )


def validate_checkpoint_integrity(
    checkpoint: Checkpoint,
) -> None:
    require(
        checkpoint.slot
        in VALID_CHECKPOINT_SLOTS,
        "invalid checkpoint slot",
    )

    require(
        checkpoint.sequence >= 1,
        "invalid checkpoint sequence",
    )

    require(
        checkpoint.generation >= 1,
        "invalid checkpoint generation",
    )

    require(
        bool(checkpoint.lineage_id),
        "invalid checkpoint lineage",
    )

    require(
        checkpoint.recovery_epoch >= 0,
        "invalid checkpoint recovery epoch",
    )

    expected = seal_checkpoint(
        checkpoint
    )

    require(
        secure_equal(
            checkpoint.integrity_seal,
            expected,
        ),
        "checkpoint integrity seal mismatch",
    )


# ============================================================================
# CHECKPOINT MANIFEST INTEGRITY
# ============================================================================

def manifest_seal_material(
    manifest: CheckpointManifest,
) -> Dict[str, Any]:
    return {
        "active_slot": manifest.active_slot,
        "highest_sequence": manifest.highest_sequence,
        "generation": manifest.generation,
        "lineage_id": manifest.lineage_id,
        "recovery_epoch": manifest.recovery_epoch,
        "slot_a_sequence": manifest.slot_a_sequence,
        "slot_b_sequence": manifest.slot_b_sequence,
        "updated_at_ns": manifest.updated_at_ns,
    }


def seal_manifest(
    manifest: CheckpointManifest,
) -> str:
    return hmac_hex(
        MANIFEST_KEY,
        manifest_seal_material(
            manifest
        ),
    )


def validate_manifest_integrity(
    manifest: CheckpointManifest,
) -> None:
    require(
        manifest.active_slot
        in VALID_CHECKPOINT_SLOTS,
        "invalid checkpoint manifest active slot",
    )

    require(
        manifest.highest_sequence >= 1,
        "invalid checkpoint manifest sequence",
    )

    require(
        manifest.generation >= 1,
        "invalid checkpoint manifest generation",
    )

    require(
        bool(manifest.lineage_id),
        "invalid checkpoint manifest lineage",
    )

    require(
        manifest.recovery_epoch >= 0,
        "invalid checkpoint manifest recovery epoch",
    )

    expected = seal_manifest(
        manifest
    )

    require(
        secure_equal(
            manifest.seal,
            expected,
        ),
        "checkpoint manifest integrity seal mismatch",
    )


# ============================================================================
# DUAL CHECKPOINT STORE
# ============================================================================

class DualCheckpointStore:
    def __init__(self) -> None:
        self.slot_a: Optional[Checkpoint] = None
        self.slot_b: Optional[Checkpoint] = None
        self.manifest: Optional[CheckpointManifest] = None

        self._lock = threading.RLock()

    def clone(self) -> "DualCheckpointStore":
        cloned = DualCheckpointStore()

        with self._lock:
            cloned.slot_a = copy.deepcopy(
                self.slot_a
            )

            cloned.slot_b = copy.deepcopy(
                self.slot_b
            )

            cloned.manifest = copy.deepcopy(
                self.manifest
            )

        return cloned

    def get_slot(
        self,
        slot: str,
    ) -> Optional[Checkpoint]:
        require(
            slot in VALID_CHECKPOINT_SLOTS,
            "invalid checkpoint slot",
        )

        if slot == CHECKPOINT_SLOT_A:
            return copy.deepcopy(
                self.slot_a
            )

        return copy.deepcopy(
            self.slot_b
        )

    def set_slot(
        self,
        slot: str,
        checkpoint: Checkpoint,
    ) -> None:
        require(
            slot in VALID_CHECKPOINT_SLOTS,
            "invalid checkpoint slot",
        )

        require(
            checkpoint.slot == slot,
            "checkpoint slot binding mismatch",
        )

        if slot == CHECKPOINT_SLOT_A:
            self.slot_a = copy.deepcopy(
                checkpoint
            )
        else:
            self.slot_b = copy.deepcopy(
                checkpoint
            )

    def next_slot(self) -> str:
        if self.manifest is None:
            return CHECKPOINT_SLOT_A

        if (
            self.manifest.active_slot
            == CHECKPOINT_SLOT_A
        ):
            return CHECKPOINT_SLOT_B

        return CHECKPOINT_SLOT_A

    def highest_known_sequence(self) -> int:
        sequences = [0]

        if self.slot_a is not None:
            sequences.append(
                self.slot_a.sequence
            )

        if self.slot_b is not None:
            sequences.append(
                self.slot_b.sequence
            )

        if self.manifest is not None:
            sequences.append(
                self.manifest.highest_sequence
            )

        return max(sequences)

    def checkpoint_sequences(
        self,
    ) -> Tuple[int, int]:
        slot_a_sequence = (
            self.slot_a.sequence
            if self.slot_a is not None
            else 0
        )

        slot_b_sequence = (
            self.slot_b.sequence
            if self.slot_b is not None
            else 0
        )

        return (
            slot_a_sequence,
            slot_b_sequence,
        )


# ============================================================================
# PART 1 LOAD MARKER
# ============================================================================

print(
    "R28 UNIT N.28: PART 1 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.28
# PART 2 OF 4
#
# ENGINE + CHECKPOINT CREATION + RECOVERY VALIDATION
# ============================================================================


# ============================================================================
# CHECKPOINT VALIDATION AGAINST WAL / STATE
# ============================================================================

def validate_checkpoint_against_wal(
    checkpoint: Checkpoint,
    wal: DurableWAL,
) -> None:
    validate_checkpoint_integrity(
        checkpoint
    )

    wal.validate()

    require(
        checkpoint.wal_length
        == wal.length(),
        "checkpoint WAL length mismatch",
    )

    require(
        secure_equal(
            checkpoint.wal_final_hash,
            wal.final_hash(),
        ),
        "checkpoint WAL final hash mismatch",
    )


def validate_checkpoint_state_binding(
    checkpoint: Checkpoint,
) -> None:
    state = durable_state_from_dict(
        checkpoint.state
    )

    require(
        checkpoint.generation
        == state.generation,
        "checkpoint generation mismatch",
    )

    require(
        checkpoint.lineage_id
        == state.lineage_id,
        "checkpoint lineage mismatch",
    )

    require(
        checkpoint.recovery_epoch
        == state.recovery_epoch,
        "checkpoint recovery epoch mismatch",
    )

    require(
        checkpoint.sequence
        == state.checkpoint_sequence,
        "checkpoint sequence/state mismatch",
    )

    require(
        state.phase in VALID_PHASES,
        "checkpoint contains invalid phase",
    )

    require(
        secure_equal(
            state.payload_hash,
            sha256_hex(state.payload),
        ),
        "checkpoint payload hash mismatch",
    )


def validate_checkpoint_candidate(
    checkpoint: Checkpoint,
    wal: DurableWAL,
) -> DurableState:
    validate_checkpoint_against_wal(
        checkpoint,
        wal,
    )

    validate_checkpoint_state_binding(
        checkpoint
    )

    return durable_state_from_dict(
        checkpoint.state
    )


# ============================================================================
# MANIFEST / SLOT CROSS-CHECK
# ============================================================================

def validate_manifest_slot_sequences(
    store: DualCheckpointStore,
) -> None:
    require(
        store.manifest is not None,
        "checkpoint manifest missing",
    )

    manifest = store.manifest

    validate_manifest_integrity(
        manifest
    )

    slot_a_sequence, slot_b_sequence = (
        store.checkpoint_sequences()
    )

    require(
        manifest.slot_a_sequence
        == slot_a_sequence,
        "checkpoint manifest slot A sequence mismatch",
    )

    require(
        manifest.slot_b_sequence
        == slot_b_sequence,
        "checkpoint manifest slot B sequence mismatch",
    )

    require(
        manifest.highest_sequence
        == max(
            slot_a_sequence,
            slot_b_sequence,
        ),
        "checkpoint manifest highest sequence mismatch",
    )

    active_checkpoint = store.get_slot(
        manifest.active_slot
    )

    require(
        active_checkpoint is not None,
        "checkpoint manifest active slot missing",
    )

    require(
        active_checkpoint.sequence
        == manifest.highest_sequence,
        "checkpoint manifest active sequence mismatch",
    )

    require(
        active_checkpoint.generation
        == manifest.generation,
        "checkpoint manifest generation mismatch",
    )

    require(
        active_checkpoint.lineage_id
        == manifest.lineage_id,
        "checkpoint manifest lineage mismatch",
    )

    require(
        active_checkpoint.recovery_epoch
        == manifest.recovery_epoch,
        "checkpoint manifest recovery epoch mismatch",
    )


# ============================================================================
# CHECKPOINT SELECTION
# ============================================================================

def select_newest_valid_checkpoint(
    store: DualCheckpointStore,
    wal: DurableWAL,
) -> Checkpoint:
    candidates: List[Checkpoint] = []

    for slot in (
        CHECKPOINT_SLOT_A,
        CHECKPOINT_SLOT_B,
    ):
        checkpoint = store.get_slot(
            slot
        )

        if checkpoint is None:
            continue

        try:
            validate_checkpoint_candidate(
                checkpoint,
                wal,
            )

            candidates.append(
                checkpoint
            )

        except LocalSafetyBlock:
            continue

    require(
        bool(candidates),
        "no valid checkpoint available",
    )

    candidates.sort(
        key=lambda item: item.sequence,
        reverse=True,
    )

    newest = candidates[0]

    if len(candidates) >= 2:
        second = candidates[1]

        require(
            newest.sequence
            != second.sequence,
            "duplicate checkpoint sequence detected",
        )

    return newest


def select_checkpoint_with_manifest(
    store: DualCheckpointStore,
    wal: DurableWAL,
) -> Checkpoint:
    require(
        store.manifest is not None,
        "checkpoint manifest missing",
    )

    validate_manifest_integrity(
        store.manifest
    )

    newest = select_newest_valid_checkpoint(
        store,
        wal,
    )

    require(
        newest.sequence
        == store.manifest.highest_sequence,
        "checkpoint rollback detected",
    )

    require(
        newest.slot
        == store.manifest.active_slot,
        "checkpoint manifest active slot mismatch",
    )

    require(
        newest.generation
        == store.manifest.generation,
        "checkpoint manifest generation mismatch",
    )

    require(
        newest.lineage_id
        == store.manifest.lineage_id,
        "checkpoint manifest lineage mismatch",
    )

    require(
        newest.recovery_epoch
        == store.manifest.recovery_epoch,
        "checkpoint manifest recovery epoch mismatch",
    )

    return newest


# ============================================================================
# ENGINE
# ============================================================================

class N28Engine:
    def __init__(
        self,
        state: Optional[DurableState] = None,
        wal: Optional[DurableWAL] = None,
        checkpoints: Optional[DualCheckpointStore] = None,
    ) -> None:
        self.state = (
            copy.deepcopy(state)
            if state is not None
            else DurableState()
        )

        self.wal = (
            wal.clone()
            if wal is not None
            else DurableWAL()
        )

        self.checkpoints = (
            checkpoints.clone()
            if checkpoints is not None
            else DualCheckpointStore()
        )

        self._lock = threading.RLock()

        if self.wal.length() == 0:
            self._append_prepared_record()

        self.validate_runtime_state()

    # ========================================================================
    # INTERNAL STATE VALIDATION
    # ========================================================================

    def validate_runtime_state(self) -> None:
        self.wal.validate()

        require(
            self.state.generation >= 1,
            "invalid state generation",
        )

        require(
            bool(self.state.lineage_id),
            "invalid state lineage",
        )

        require(
            self.state.recovery_epoch >= 0,
            "invalid state recovery epoch",
        )

        require(
            self.state.phase in VALID_PHASES,
            "invalid runtime phase",
        )

        require(
            secure_equal(
                self.state.payload_hash,
                sha256_hex(
                    self.state.payload
                ),
            ),
            "runtime payload hash mismatch",
        )

        if self.state.authorization is not None:
            validate_authorization_seal(
                self.state.authorization
            )

        if self.state.dispatch_commit is not None:
            validate_dispatch_commit_seal(
                self.state.dispatch_commit
            )

        dispatch_ids = [
            item.dispatch_id
            for item in self.state.synthetic_dispatches
        ]

        require(
            len(dispatch_ids)
            == len(set(dispatch_ids)),
            "duplicate synthetic dispatch detected",
        )

        for dispatch in self.state.synthetic_dispatches:
            require(
                dispatch.method
                == HTTP_METHOD,
                "synthetic dispatch method mismatch",
            )

            require(
                dispatch.path
                == LEVERAGE_ENDPOINT,
                "synthetic dispatch path mismatch",
            )

            require(
                secure_equal(
                    dispatch.payload_hash,
                    sha256_hex(
                        dispatch.payload
                    ),
                ),
                "synthetic dispatch payload hash mismatch",
            )

    # ========================================================================
    # WAL HELPERS
    # ========================================================================

    def _append_event(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> WALRecord:
        return self.wal.append(
            event_type=event_type,
            generation=self.state.generation,
            lineage_id=self.state.lineage_id,
            recovery_epoch=self.state.recovery_epoch,
            data=data,
        )

    def _append_prepared_record(self) -> None:
        self._append_event(
            EVENT_PREPARED,
            {
                "phase": PHASE_PREPARED,
                "payload": copy.deepcopy(
                    self.state.payload
                ),
                "payload_hash": self.state.payload_hash,
            },
        )

    # ========================================================================
    # RECOVERY LEASE
    # ========================================================================

    def acquire_recovery_lease(
        self,
        owner_id: str,
    ) -> RecoveryLease:
        with self._lock:
            require(
                bool(owner_id),
                "recovery owner is empty",
            )

            require(
                self.state.phase
                not in TERMINAL_PHASES,
                "terminal generation cannot acquire recovery lease",
            )

            self.state.recovery_epoch += 1

            lease = RecoveryLease(
                owner_id=owner_id,
                owner_nonce=new_owner_nonce(),
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                issued_at_ns=time.time_ns(),
                consumed=False,
            )

            self.state.active_lease = copy.deepcopy(
                lease
            )

            self._append_event(
                EVENT_RECOVERY_LEASE_ACQUIRED,
                {
                    "owner_id": lease.owner_id,
                    "owner_nonce": lease.owner_nonce,
                    "generation": lease.generation,
                    "lineage_id": lease.lineage_id,
                    "recovery_epoch": lease.recovery_epoch,
                },
            )

            return copy.deepcopy(
                lease
            )

    def validate_recovery_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        active = self.state.active_lease

        require(
            active is not None,
            "no active recovery lease",
        )

        require(
            not active.consumed,
            "recovery lease already consumed",
        )

        require(
            lease.owner_id
            == active.owner_id,
            "recovery lease owner mismatch",
        )

        require(
            lease.owner_nonce
            == active.owner_nonce,
            "recovery lease nonce mismatch",
        )

        require(
            lease.generation
            == self.state.generation,
            "recovery lease generation mismatch",
        )

        require(
            lease.lineage_id
            == self.state.lineage_id,
            "recovery lease lineage mismatch",
        )

        require(
            lease.recovery_epoch
            == self.state.recovery_epoch,
            "recovery lease fence mismatch",
        )

    # ========================================================================
    # AUTHORIZATION
    # ========================================================================

    def authorize_recovery(
        self,
        lease: RecoveryLease,
    ) -> RecoveryAuthorization:
        with self._lock:
            self.validate_recovery_lease(
                lease
            )

            dispatch_id = deterministic_dispatch_id(
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                payload_hash=self.state.payload_hash,
            )

            authorization = RecoveryAuthorization(
                authorization_id=uuid.uuid4().hex,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                payload_hash=self.state.payload_hash,
                dispatch_id=dispatch_id,
                issued_at_ns=time.time_ns(),
                consumed=False,
            )

            authorization.seal = seal_authorization(
                authorization
            )

            self.state.authorization = copy.deepcopy(
                authorization
            )

            self.state.phase = PHASE_AUTHORIZED

            self._append_event(
                EVENT_AUTHORIZED,
                {
                    "authorization": authorization_to_dict(
                        authorization
                    ),
                    "phase": self.state.phase,
                },
            )

            return copy.deepcopy(
                authorization
            )

    def validate_authorization(
        self,
        authorization: RecoveryAuthorization,
    ) -> None:
        stored = self.state.authorization

        require(
            stored is not None,
            "generation is not authorized",
        )

        validate_authorization_seal(
            stored
        )

        validate_authorization_seal(
            authorization
        )

        require(
            authorization.authorization_id
            == stored.authorization_id,
            "authorization identity mismatch",
        )

        require(
            authorization.generation
            == self.state.generation,
            "authorization generation mismatch",
        )

        require(
            authorization.lineage_id
            == self.state.lineage_id,
            "authorization lineage mismatch",
        )

        require(
            authorization.recovery_epoch
            == self.state.recovery_epoch,
            "authorization recovery epoch mismatch",
        )

        require(
            authorization.payload_hash
            == self.state.payload_hash,
            "authorization payload hash mismatch",
        )

        require(
            not stored.consumed,
            "authorization already consumed",
        )

    # ========================================================================
    # DURABLE DISPATCH COMMIT
    # ========================================================================

    def commit_dispatch(
        self,
        authorization: RecoveryAuthorization,
    ) -> DispatchCommit:
        with self._lock:
            self.validate_authorization(
                authorization
            )

            commit_id = deterministic_commit_id(
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                dispatch_id=authorization.dispatch_id,
                payload_hash=self.state.payload_hash,
            )

            commit = DispatchCommit(
                commit_id=commit_id,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                dispatch_id=authorization.dispatch_id,
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload=copy.deepcopy(
                    self.state.payload
                ),
                payload_hash=self.state.payload_hash,
                committed_at_ns=time.time_ns(),
                dispatched=False,
                finalized=False,
            )

            commit.seal = seal_dispatch_commit(
                commit
            )

            self.state.dispatch_commit = copy.deepcopy(
                commit
            )

            self.state.phase = PHASE_COMMITTED

            self._append_event(
                EVENT_DISPATCH_COMMITTED,
                {
                    "commit": commit_to_dict(
                        commit
                    ),
                    "phase": self.state.phase,
                },
            )

            return copy.deepcopy(
                commit
            )

    # ========================================================================
    # SYNTHETIC TRANSPORT
    # ========================================================================

    def synthetic_dispatch(
        self,
    ) -> SyntheticDispatch:
        with self._lock:
            require(
                SYNTHETIC_TRANSPORT_ONLY,
                "synthetic transport disabled",
            )

            require(
                not NETWORK_WRITES_ENABLED,
                "network writes unexpectedly enabled",
            )

            commit = self.state.dispatch_commit

            require(
                commit is not None,
                "dispatch commit missing",
            )

            validate_dispatch_commit_seal(
                commit
            )

            for existing in self.state.synthetic_dispatches:
                if (
                    existing.dispatch_id
                    == commit.dispatch_id
                ):
                    return copy.deepcopy(
                        existing
                    )

            dispatch = SyntheticDispatch(
                dispatch_id=commit.dispatch_id,
                commit_id=commit.commit_id,
                generation=commit.generation,
                lineage_id=commit.lineage_id,
                recovery_epoch=commit.recovery_epoch,
                method=commit.method,
                path=commit.path,
                payload=copy.deepcopy(
                    commit.payload
                ),
                payload_hash=commit.payload_hash,
                dispatched_at_ns=time.time_ns(),
            )

            self.state.synthetic_dispatches.append(
                copy.deepcopy(dispatch)
            )

            commit.dispatched = True
            commit.seal = seal_dispatch_commit(
                commit
            )

            self.state.dispatch_commit = copy.deepcopy(
                commit
            )

            self.state.phase = PHASE_DISPATCHED

            self._append_event(
                EVENT_SYNTHETIC_DISPATCHED,
                {
                    "dispatch": dispatch_to_dict(
                        dispatch
                    ),
                    "phase": self.state.phase,
                },
            )

            return copy.deepcopy(
                dispatch
            )

    # ========================================================================
    # FINALIZATION
    # ========================================================================

    def finalize_dispatch(self) -> None:
        with self._lock:
            commit = self.state.dispatch_commit

            require(
                commit is not None,
                "dispatch commit missing",
            )

            validate_dispatch_commit_seal(
                commit
            )

            require(
                commit.dispatched,
                "cannot finalize undispatched commit",
            )

            commit.finalized = True
            commit.seal = seal_dispatch_commit(
                commit
            )

            self.state.dispatch_commit = copy.deepcopy(
                commit
            )

            self.state.completed_dispatch_ids.add(
                commit.dispatch_id
            )

            if self.state.authorization is not None:
                self.state.authorization.consumed = True
                self.state.authorization.seal = (
                    seal_authorization(
                        self.state.authorization
                    )
                )

            if self.state.active_lease is not None:
                self.state.active_lease.consumed = True

            self.state.phase = PHASE_COMPLETED

            self._append_event(
                EVENT_AUTHORIZATION_CONSUMED,
                {
                    "authorization_id": (
                        self.state.authorization.authorization_id
                        if self.state.authorization is not None
                        else None
                    ),
                    "dispatch_id": commit.dispatch_id,
                },
            )

            self._append_event(
                EVENT_COMPLETED,
                {
                    "dispatch_id": commit.dispatch_id,
                    "phase": self.state.phase,
                },
            )

    # ========================================================================
    # EXACT RECOVERY
    # ========================================================================

    def recover(
        self,
    ) -> str:
        with self._lock:
            self.validate_runtime_state()

            if self.state.phase == PHASE_COMPLETED:
                return PHASE_COMPLETED

            if self.state.phase == PHASE_PREPARED:
                lease = self.acquire_recovery_lease(
                    "recovery-worker"
                )

                authorization = self.authorize_recovery(
                    lease
                )

                self.commit_dispatch(
                    authorization
                )

                self.synthetic_dispatch()
                self.finalize_dispatch()

                return self.state.phase

            if self.state.phase == PHASE_AUTHORIZED:
                require(
                    self.state.authorization is not None,
                    "authorized phase missing authorization",
                )

                self.commit_dispatch(
                    copy.deepcopy(
                        self.state.authorization
                    )
                )

                self.synthetic_dispatch()
                self.finalize_dispatch()

                return self.state.phase

            if self.state.phase == PHASE_COMMITTED:
                self.synthetic_dispatch()
                self.finalize_dispatch()

                return self.state.phase

            if self.state.phase == PHASE_DISPATCHED:
                self.finalize_dispatch()

                return self.state.phase

            local_block(
                "unsupported recovery phase"
            )

    # ========================================================================
    # CHECKPOINT CREATION
    # ========================================================================

    def create_checkpoint(
        self,
    ) -> Checkpoint:
        with self._lock:
            self.validate_runtime_state()

            slot = self.checkpoints.next_slot()

            sequence = (
                self.checkpoints.highest_known_sequence()
                + 1
            )

            self.state.checkpoint_sequence = sequence

            checkpoint = Checkpoint(
                slot=slot,
                sequence=sequence,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                wal_length=self.wal.length(),
                wal_final_hash=self.wal.final_hash(),
                created_at_ns=time.time_ns(),
                state=durable_state_to_dict(
                    self.state
                ),
            )

            checkpoint.integrity_seal = (
                seal_checkpoint(
                    checkpoint
                )
            )

            self.checkpoints.set_slot(
                slot,
                checkpoint,
            )

            slot_a_sequence, slot_b_sequence = (
                self.checkpoints.checkpoint_sequences()
            )

            manifest = CheckpointManifest(
                active_slot=slot,
                highest_sequence=sequence,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                slot_a_sequence=slot_a_sequence,
                slot_b_sequence=slot_b_sequence,
                updated_at_ns=time.time_ns(),
            )

            manifest.seal = seal_manifest(
                manifest
            )

            self.checkpoints.manifest = copy.deepcopy(
                manifest
            )

            return copy.deepcopy(
                checkpoint
            )

    # ========================================================================
    # CHECKPOINT RESTORE
    # ========================================================================

    @classmethod
    def restore_from_checkpoint(
        cls,
        wal: DurableWAL,
        checkpoints: DualCheckpointStore,
    ) -> "N28Engine":
        wal.validate()

        selected = select_checkpoint_with_manifest(
            checkpoints,
            wal,
        )

        state = validate_checkpoint_candidate(
            selected,
            wal,
        )

        require(
            selected.sequence
            == checkpoints.manifest.highest_sequence,
            "checkpoint rollback detected",
        )

        engine = cls(
            state=state,
            wal=wal,
            checkpoints=checkpoints,
        )

        engine.validate_runtime_state()

        return engine

    # ========================================================================
    # FALLBACK RESTORE WHEN MANIFEST SLOT IS CORRUPT
    # ========================================================================

    @classmethod
    def restore_from_newest_valid_slot(
        cls,
        wal: DurableWAL,
        checkpoints: DualCheckpointStore,
    ) -> "N28Engine":
        wal.validate()

        selected = select_newest_valid_checkpoint(
            checkpoints,
            wal,
        )

        state = validate_checkpoint_candidate(
            selected,
            wal,
        )

        engine = cls(
            state=state,
            wal=wal,
            checkpoints=checkpoints,
        )

        engine.validate_runtime_state()

        return engine

    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(
        self,
    ) -> None:
        with self._lock:
            require(
                self.state.phase
                == PHASE_COMPLETED,
                "generation can advance only from completed state",
            )

            prior_generation = self.state.generation
            prior_lineage = self.state.lineage_id
            prior_dispatch_ids = set(
                self.state.completed_dispatch_ids
            )

            self.state.generation += 1
            self.state.lineage_id = new_lineage_id()
            self.state.recovery_epoch += 1

            self.state.phase = PHASE_PREPARED

            self.state.active_lease = None
            self.state.authorization = None
            self.state.dispatch_commit = None

            self.state.payload = (
                build_leverage_payload()
            )

            self.state.payload_hash = sha256_hex(
                self.state.payload
            )

            self.state.completed_dispatch_ids = (
                prior_dispatch_ids
            )

            self._append_event(
                EVENT_GENERATION_ADVANCED,
                {
                    "prior_generation": prior_generation,
                    "prior_lineage_id": prior_lineage,
                    "new_generation": self.state.generation,
                    "new_lineage_id": self.state.lineage_id,
                    "recovery_epoch": self.state.recovery_epoch,
                },
            )

            self._append_prepared_record()

    # ========================================================================
    # CLONE / CRASH SNAPSHOT
    # ========================================================================

    def clone_runtime(
        self,
    ) -> "N28Engine":
        with self._lock:
            return N28Engine(
                state=copy.deepcopy(
                    self.state
                ),
                wal=self.wal.clone(),
                checkpoints=self.checkpoints.clone(),
            )


# ============================================================================
# CHECKPOINT TAMPER HELPERS FOR DIAGNOSTICS
# ============================================================================

def tamper_checkpoint_state(
    checkpoint: Checkpoint,
) -> Checkpoint:
    damaged = copy.deepcopy(
        checkpoint
    )

    damaged.state["phase"] = "TAMPERED"

    return damaged


def tamper_checkpoint_sequence(
    checkpoint: Checkpoint,
    new_sequence: int,
) -> Checkpoint:
    damaged = copy.deepcopy(
        checkpoint
    )

    damaged.sequence = new_sequence

    return damaged


def tamper_checkpoint_wal_hash(
    checkpoint: Checkpoint,
) -> Checkpoint:
    damaged = copy.deepcopy(
        checkpoint
    )

    damaged.wal_final_hash = (
        "0" * 64
    )

    return damaged


def tamper_manifest_sequence(
    manifest: CheckpointManifest,
    new_sequence: int,
) -> CheckpointManifest:
    damaged = copy.deepcopy(
        manifest
    )

    damaged.highest_sequence = (
        new_sequence
    )

    return damaged


# ============================================================================
# EXPECT LOCAL BLOCK HELPER
# ============================================================================

def expect_local_block(
    fn: Any,
) -> bool:
    try:
        fn()

    except LocalSafetyBlock:
        return True

    return False


# ============================================================================
# SAFETY FIREBREAKS
# ============================================================================

def real_post(
    *args: Any,
    **kwargs: Any,
) -> None:
    global NETWORK_WRITE_COUNT
    global REAL_POST_COUNT

    local_block(
        f"{UNIT_NAME} LOCAL BLOCK: real network POST is disabled."
    )


def demo_post(
    *args: Any,
    **kwargs: Any,
) -> None:
    global NETWORK_WRITE_COUNT
    global DEMO_POST_COUNT

    local_block(
        f"{UNIT_NAME} LOCAL BLOCK: demo network POST is disabled."
    )


def assert_final_network_firebreak() -> None:
    check(
        LIVE_ORDER_EXECUTION is False,
        "Live Execution Disabled",
    )

    check(
        DEMO_ORDER_EXECUTION is False,
        "Demo Execution Disabled",
    )

    check(
        NETWORK_WRITES_ENABLED is False,
        "Network Writes Disabled",
    )

    check(
        REAL_POST_ENABLED is False,
        "Real POST Disabled",
    )

    check(
        DEMO_POST_ENABLED is False,
        "Demo POST Disabled",
    )

    check(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic Transport Only",
    )

    check(
        NETWORK_WRITE_COUNT == 0,
        "Network Write Count Remains Zero",
    )

    check(
        REAL_POST_COUNT == 0,
        "Real POST Count Remains Zero",
    )

    check(
        DEMO_POST_COUNT == 0,
        "Demo POST Count Remains Zero",
    )


# ============================================================================
# PART 2 LOAD MARKER
# ============================================================================

print(
    "R28 UNIT N.28: PART 2 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.28
# PART 3 OF 4
#
# DIAGNOSTIC TEST SUITE
# ============================================================================


# ============================================================================
# TEST 1 — BASELINE PREPARED STATE + INITIAL CHECKPOINT
# ============================================================================

def test_01_baseline_prepared_state() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 1: BASELINE PREPARED STATE + INITIAL CHECKPOINT",
        flush=True,
    )
    separator()

    engine = N28Engine()

    check(
        engine.state.phase == PHASE_PREPARED,
        "Initial Phase Is PREPARED",
    )

    check(
        engine.state.generation == 1,
        "Initial Generation Is One",
    )

    check(
        engine.state.recovery_epoch == 0,
        "Initial Recovery Epoch Is Zero",
    )

    check(
        engine.wal.length() == 1,
        "Initial WAL Contains Prepared Record",
    )

    checkpoint = engine.create_checkpoint()

    check(
        checkpoint.sequence == 1,
        "Initial Checkpoint Sequence Is One",
    )

    check(
        checkpoint.slot == CHECKPOINT_SLOT_A,
        "Initial Checkpoint Uses Slot A",
    )

    check(
        engine.checkpoints.manifest is not None,
        "Initial Checkpoint Manifest Created",
    )

    check(
        engine.checkpoints.manifest.active_slot
        == CHECKPOINT_SLOT_A,
        "Initial Manifest Points To Slot A",
    )


# ============================================================================
# TEST 2 — DUAL CHECKPOINT SLOT ALTERNATION
# ============================================================================

def test_02_dual_checkpoint_slot_alternation() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 2: DUAL CHECKPOINT SLOT ALTERNATION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    first = engine.create_checkpoint()
    second = engine.create_checkpoint()
    third = engine.create_checkpoint()

    check(
        first.slot == CHECKPOINT_SLOT_A,
        "Checkpoint One Uses Slot A",
    )

    check(
        second.slot == CHECKPOINT_SLOT_B,
        "Checkpoint Two Uses Slot B",
    )

    check(
        third.slot == CHECKPOINT_SLOT_A,
        "Checkpoint Three Returns To Slot A",
    )

    check(
        first.sequence < second.sequence < third.sequence,
        "Checkpoint Sequences Advance Monotonically",
    )

    check(
        engine.checkpoints.manifest.highest_sequence
        == third.sequence,
        "Manifest Tracks Highest Checkpoint Sequence",
    )


# ============================================================================
# TEST 3 — MANIFEST INTEGRITY + ACTIVE SLOT BINDING
# ============================================================================

def test_03_manifest_integrity_and_binding() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 3: MANIFEST INTEGRITY + ACTIVE SLOT BINDING",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.create_checkpoint()
    latest = engine.create_checkpoint()

    validate_manifest_slot_sequences(
        engine.checkpoints
    )

    check(
        engine.checkpoints.manifest.active_slot
        == latest.slot,
        "Manifest Active Slot Matches Latest Checkpoint",
    )

    check(
        engine.checkpoints.manifest.highest_sequence
        == latest.sequence,
        "Manifest Highest Sequence Matches Latest Checkpoint",
    )

    check(
        engine.checkpoints.manifest.generation
        == latest.generation,
        "Manifest Generation Matches Latest Checkpoint",
    )

    check(
        engine.checkpoints.manifest.lineage_id
        == latest.lineage_id,
        "Manifest Lineage Matches Latest Checkpoint",
    )

    check(
        engine.checkpoints.manifest.recovery_epoch
        == latest.recovery_epoch,
        "Manifest Recovery Epoch Matches Latest Checkpoint",
    )


# ============================================================================
# TEST 4 — NORMAL CHECKPOINT RESTORE
# ============================================================================

def test_04_normal_checkpoint_restore() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 4: NORMAL CHECKPOINT RESTORE",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.create_checkpoint()

    restored = N28Engine.restore_from_checkpoint(
        engine.wal.clone(),
        engine.checkpoints.clone(),
    )

    check(
        restored.state.phase
        == engine.state.phase,
        "Restored Phase Preserved",
    )

    check(
        restored.state.generation
        == engine.state.generation,
        "Restored Generation Preserved",
    )

    check(
        restored.state.lineage_id
        == engine.state.lineage_id,
        "Restored Lineage Preserved",
    )

    check(
        restored.state.recovery_epoch
        == engine.state.recovery_epoch,
        "Restored Recovery Epoch Preserved",
    )

    check(
        restored.state.payload_hash
        == engine.state.payload_hash,
        "Restored Payload Hash Preserved",
    )


# ============================================================================
# TEST 5 — AUTHORIZED RECOVERY + CHECKPOINT RESTART
# ============================================================================

def test_05_authorized_recovery_checkpoint_restart() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 5: AUTHORIZED RECOVERY + CHECKPOINT RESTART",
        flush=True,
    )
    separator()

    engine = N28Engine()

    lease = engine.acquire_recovery_lease(
        "worker-authorized"
    )

    engine.authorize_recovery(
        lease
    )

    engine.create_checkpoint()

    restored = N28Engine.restore_from_checkpoint(
        engine.wal.clone(),
        engine.checkpoints.clone(),
    )

    before_dispatches = len(
        restored.state.synthetic_dispatches
    )

    result = restored.recover()

    after_dispatches = len(
        restored.state.synthetic_dispatches
    )

    check(
        result == PHASE_COMPLETED,
        "Authorized Recovery Completed",
    )

    check(
        after_dispatches - before_dispatches == 1,
        "Authorized Recovery Produced Exactly One Dispatch",
    )

    check(
        restored.state.authorization is not None
        and restored.state.authorization.consumed,
        "Authorization Consumed Exactly Once",
    )


# ============================================================================
# TEST 6 — RESTART AFTER COMMIT BEFORE SYNTHETIC DISPATCH
# ============================================================================

def test_06_restart_after_commit() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 6: RESTART AFTER COMMIT BEFORE SYNTHETIC DISPATCH",
        flush=True,
    )
    separator()

    engine = N28Engine()

    lease = engine.acquire_recovery_lease(
        "worker-commit"
    )

    authorization = engine.authorize_recovery(
        lease
    )

    engine.commit_dispatch(
        authorization
    )

    engine.create_checkpoint()

    restored = N28Engine.restore_from_checkpoint(
        engine.wal.clone(),
        engine.checkpoints.clone(),
    )

    before = len(
        restored.state.synthetic_dispatches
    )

    result = restored.recover()

    after = len(
        restored.state.synthetic_dispatches
    )

    check(
        result == PHASE_COMPLETED,
        "Committed Recovery Completed",
    )

    check(
        after - before == 1,
        "Committed Recovery Produced Exactly One Dispatch",
    )


# ============================================================================
# TEST 7 — RESTART AFTER DISPATCH BEFORE FINALIZATION
# ============================================================================

def test_07_restart_after_dispatch() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 7: RESTART AFTER DISPATCH BEFORE FINALIZATION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    lease = engine.acquire_recovery_lease(
        "worker-dispatch"
    )

    authorization = engine.authorize_recovery(
        lease
    )

    engine.commit_dispatch(
        authorization
    )

    engine.synthetic_dispatch()

    check(
        len(engine.state.synthetic_dispatches) == 1,
        "Pre-Crash Synthetic Dispatch Count Is One",
    )

    engine.create_checkpoint()

    restored = N28Engine.restore_from_checkpoint(
        engine.wal.clone(),
        engine.checkpoints.clone(),
    )

    before = len(
        restored.state.synthetic_dispatches
    )

    result = restored.recover()

    after = len(
        restored.state.synthetic_dispatches
    )

    check(
        result == PHASE_COMPLETED,
        "Dispatched Recovery Completed",
    )

    check(
        after == before,
        "Dispatched Recovery Produced No Second Dispatch",
    )


# ============================================================================
# TEST 8 — TERMINAL RESTART IDEMPOTENCY
# ============================================================================

def test_08_terminal_restart_idempotency() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 8: TERMINAL RESTART IDEMPOTENCY",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.recover()
    engine.create_checkpoint()

    restored = N28Engine.restore_from_checkpoint(
        engine.wal.clone(),
        engine.checkpoints.clone(),
    )

    before = len(
        restored.state.synthetic_dispatches
    )

    result = restored.recover()

    after = len(
        restored.state.synthetic_dispatches
    )

    check(
        result == PHASE_COMPLETED,
        "Terminal Recovery Remains COMPLETED",
    )

    check(
        after == before,
        "Terminal Recovery Produced No Second Dispatch",
    )

    check(
        len(restored.state.completed_dispatch_ids) == 1,
        "Terminal Dispatch Finality Preserved",
    )


# ============================================================================
# TEST 9 — SINGLE ACTIVE SLOT CORRUPTION + FALLBACK
# ============================================================================

def test_09_single_slot_corruption_fallback() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 9: SINGLE ACTIVE SLOT CORRUPTION FALLBACK",
        flush=True,
    )
    separator()

    engine = N28Engine()

    first = engine.create_checkpoint()
    second = engine.create_checkpoint()

    check(
        second.sequence > first.sequence,
        "Second Checkpoint Is Newer",
    )

    corrupted_store = engine.checkpoints.clone()

    if second.slot == CHECKPOINT_SLOT_A:
        corrupted_store.slot_a = tamper_checkpoint_state(
            corrupted_store.slot_a
        )
    else:
        corrupted_store.slot_b = tamper_checkpoint_state(
            corrupted_store.slot_b
        )

    restored = N28Engine.restore_from_newest_valid_slot(
        engine.wal.clone(),
        corrupted_store,
    )

    check(
        restored.state.generation
        == engine.state.generation,
        "Fallback Restore Preserved Generation",
    )

    check(
        restored.state.lineage_id
        == engine.state.lineage_id,
        "Fallback Restore Preserved Lineage",
    )

    check(
        restored.state.phase
        == engine.state.phase,
        "Fallback Restore Preserved State",
    )


# ============================================================================
# TEST 10 — DUAL SLOT CORRUPTION REJECTION
# ============================================================================

def test_10_dual_slot_corruption_rejection() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 10: DUAL SLOT CORRUPTION REJECTION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.create_checkpoint()
    engine.create_checkpoint()

    corrupted_store = engine.checkpoints.clone()

    corrupted_store.slot_a = tamper_checkpoint_state(
        corrupted_store.slot_a
    )

    corrupted_store.slot_b = tamper_checkpoint_state(
        corrupted_store.slot_b
    )

    blocked = expect_local_block(
        lambda: N28Engine.restore_from_newest_valid_slot(
            engine.wal.clone(),
            corrupted_store,
        )
    )

    check(
        blocked,
        "Dual Corrupted Checkpoints Rejected",
    )


# ============================================================================
# TEST 11 — CHECKPOINT INTEGRITY SEAL TAMPER REJECTION
# ============================================================================

def test_11_checkpoint_integrity_tamper() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 11: CHECKPOINT INTEGRITY SEAL TAMPER REJECTION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    checkpoint = engine.create_checkpoint()

    damaged = tamper_checkpoint_state(
        checkpoint
    )

    blocked = expect_local_block(
        lambda: validate_checkpoint_integrity(
            damaged
        )
    )

    check(
        blocked,
        "Tampered Checkpoint Rejected",
    )


# ============================================================================
# TEST 12 — STALE CHECKPOINT WAL LENGTH REJECTION
# ============================================================================

def test_12_stale_checkpoint_rejection() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 12: STALE CHECKPOINT REJECTION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    checkpoint = engine.create_checkpoint()

    engine.acquire_recovery_lease(
        "worker-stale"
    )

    blocked = expect_local_block(
        lambda: validate_checkpoint_against_wal(
            checkpoint,
            engine.wal,
        )
    )

    check(
        blocked,
        "Stale Checkpoint Rejected",
    )


# ============================================================================
# TEST 13 — CHECKPOINT WAL FINAL HASH MISMATCH
# ============================================================================

def test_13_checkpoint_wal_hash_mismatch() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 13: CHECKPOINT TO WAL FINAL HASH MISMATCH",
        flush=True,
    )
    separator()

    engine = N28Engine()

    checkpoint = engine.create_checkpoint()

    damaged = tamper_checkpoint_wal_hash(
        checkpoint
    )

    damaged.integrity_seal = seal_checkpoint(
        damaged
    )

    blocked = expect_local_block(
        lambda: validate_checkpoint_against_wal(
            damaged,
            engine.wal,
        )
    )

    check(
        blocked,
        "Checkpoint WAL Hash Mismatch Rejected",
    )


# ============================================================================
# TEST 14 — MANIFEST TAMPER REJECTION
# ============================================================================

def test_14_manifest_tamper_rejection() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 14: CHECKPOINT MANIFEST TAMPER REJECTION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.create_checkpoint()

    damaged_store = engine.checkpoints.clone()

    damaged_store.manifest.highest_sequence += 1

    blocked = expect_local_block(
        lambda: validate_manifest_integrity(
            damaged_store.manifest
        )
    )

    check(
        blocked,
        "Tampered Checkpoint Manifest Rejected",
    )


# ============================================================================
# TEST 15 — CHECKPOINT ROLLBACK REJECTION
# ============================================================================

def test_15_checkpoint_rollback_rejection() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 15: CHECKPOINT ROLLBACK REJECTION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    first = engine.create_checkpoint()
    second = engine.create_checkpoint()

    rollback_store = engine.checkpoints.clone()

    rollback_store.manifest.active_slot = first.slot
    rollback_store.manifest.highest_sequence = first.sequence
    rollback_store.manifest.generation = first.generation
    rollback_store.manifest.lineage_id = first.lineage_id
    rollback_store.manifest.recovery_epoch = (
        first.recovery_epoch
    )

    rollback_store.manifest.seal = seal_manifest(
        rollback_store.manifest
    )

    blocked = expect_local_block(
        lambda: N28Engine.restore_from_checkpoint(
            engine.wal.clone(),
            rollback_store,
        )
    )

    check(
        blocked,
        "Checkpoint Rollback Rejected",
    )

    check(
        second.sequence > first.sequence,
        "Newer Checkpoint Existed During Rollback Test",
    )


# ============================================================================
# TEST 16 — GENERATION ADVANCE + CHECKPOINT GENERATION FENCING
# ============================================================================

def test_16_generation_checkpoint_fencing() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 16: GENERATION ADVANCE + CHECKPOINT GENERATION FENCING",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.recover()

    old_generation = engine.state.generation
    old_lineage = engine.state.lineage_id
    old_epoch = engine.state.recovery_epoch
    old_completed = set(
        engine.state.completed_dispatch_ids
    )

    old_checkpoint = engine.create_checkpoint()

    engine.advance_generation()

    new_checkpoint = engine.create_checkpoint()

    check(
        engine.state.generation
        > old_generation,
        "Generation Advanced Monotonically",
    )

    check(
        engine.state.recovery_epoch
        > old_epoch,
        "Recovery Epoch Advanced Monotonically",
    )

    check(
        engine.state.lineage_id
        != old_lineage,
        "New Generation Uses Different Lineage",
    )

    check(
        engine.state.phase
        == PHASE_PREPARED,
        "New Generation Returns To PREPARED",
    )

    check(
        old_completed.issubset(
            engine.state.completed_dispatch_ids
        ),
        "Prior Completed Dispatch Preserved",
    )

    check(
        new_checkpoint.generation
        > old_checkpoint.generation,
        "New Checkpoint Uses Higher Generation",
    )

    check(
        new_checkpoint.lineage_id
        != old_checkpoint.lineage_id,
        "New Checkpoint Uses New Lineage",
    )


# ============================================================================
# TEST 17 — OWNER REUSE ACROSS GENERATION LINEAGE
# ============================================================================

def test_17_owner_reuse_across_generation() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 17: OWNER REUSE ACROSS GENERATION LINEAGE",
        flush=True,
    )
    separator()

    engine = N28Engine()

    first_lease = engine.acquire_recovery_lease(
        "same-owner"
    )

    engine.authorize_recovery(
        first_lease
    )

    engine.commit_dispatch(
        engine.state.authorization
    )

    engine.synthetic_dispatch()
    engine.finalize_dispatch()

    engine.advance_generation()

    second_lease = engine.acquire_recovery_lease(
        "same-owner"
    )

    check(
        second_lease.generation
        > first_lease.generation,
        "Reacquired Owner Uses Higher Generation",
    )

    check(
        second_lease.lineage_id
        != first_lease.lineage_id,
        "Reacquired Owner Uses Different Lineage",
    )

    check(
        second_lease.recovery_epoch
        > first_lease.recovery_epoch,
        "Reacquired Owner Uses Higher Epoch",
    )

    blocked = expect_local_block(
        lambda: engine.validate_recovery_lease(
            first_lease
        )
    )

    check(
        blocked,
        "Reused Owner Cannot Resurrect Prior Lease",
    )


# ============================================================================
# TEST 18 — EXACT SYNTHETIC TRANSPORT BINDING
# ============================================================================

def test_18_exact_synthetic_transport_binding() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 18: EXACT SYNTHETIC TRANSPORT BINDING",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.recover()

    require(
        len(engine.state.synthetic_dispatches) == 1,
        "expected exactly one synthetic dispatch",
    )

    dispatch = engine.state.synthetic_dispatches[0]

    check(
        dispatch.method == HTTP_METHOD,
        "Transport Method Exactly POST",
    )

    check(
        dispatch.path == LEVERAGE_ENDPOINT,
        "Transport Path Exactly Leverage Endpoint",
    )

    check(
        dispatch.payload_hash
        == engine.state.payload_hash,
        "Transport Payload Hash Preserved",
    )

    check(
        dispatch.payload
        == engine.state.payload,
        "Transport Payload Exactly Preserved",
    )


# ============================================================================
# TEST 19 — WAL TORN TAIL REJECTION
# ============================================================================

def test_19_torn_wal_tail_rejection() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 19: TORN WAL TAIL REJECTION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.recover()

    damaged_wal = engine.wal.clone()

    require(
        bool(damaged_wal.records),
        "WAL unexpectedly empty",
    )

    damaged_wal.records[-1].record_hash = (
        "f" * 64
    )

    blocked = expect_local_block(
        damaged_wal.validate
    )

    check(
        blocked,
        "Torn WAL Tail Rejected",
    )


# ============================================================================
# TEST 20 — HISTORICAL WAL TAMPER REJECTION
# ============================================================================

def test_20_historical_wal_tamper_rejection() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 20: HISTORICAL WAL RECORD TAMPER REJECTION",
        flush=True,
    )
    separator()

    engine = N28Engine()

    engine.recover()

    damaged_wal = engine.wal.clone()

    require(
        len(damaged_wal.records) >= 2,
        "insufficient WAL records for historical tamper test",
    )

    damaged_wal.records[0].data["payload_hash"] = (
        "0" * 64
    )

    blocked = expect_local_block(
        damaged_wal.validate
    )

    check(
        blocked,
        "Historical WAL Tamper Rejected",
    )


# ============================================================================
# TEST 21 — FINAL NETWORK WRITE FIREBREAK
# ============================================================================

def test_21_final_network_write_firebreak() -> None:
    separator()
    print(
        "R28 UNIT N.28 TEST 21: FINAL NETWORK WRITE FIREBREAK",
        flush=True,
    )
    separator()

    assert_final_network_firebreak()


# ============================================================================
# DIAGNOSTIC RUNNER
# ============================================================================

def run_diagnostic() -> None:
    banner()
    print(
        "R28 UNIT N.28 DIAGNOSTIC START",
        flush=True,
    )
    banner()

    test_01_baseline_prepared_state()
    test_02_dual_checkpoint_slot_alternation()
    test_03_manifest_integrity_and_binding()
    test_04_normal_checkpoint_restore()
    test_05_authorized_recovery_checkpoint_restart()
    test_06_restart_after_commit()
    test_07_restart_after_dispatch()
    test_08_terminal_restart_idempotency()
    test_09_single_slot_corruption_fallback()
    test_10_dual_slot_corruption_rejection()
    test_11_checkpoint_integrity_tamper()
    test_12_stale_checkpoint_rejection()
    test_13_checkpoint_wal_hash_mismatch()
    test_14_manifest_tamper_rejection()
    test_15_checkpoint_rollback_rejection()
    test_16_generation_checkpoint_fencing()
    test_17_owner_reuse_across_generation()
    test_18_exact_synthetic_transport_binding()
    test_19_torn_wal_tail_rejection()
    test_20_historical_wal_tamper_rejection()
    test_21_final_network_write_firebreak()

    print("", flush=True)
    banner()
    print(
        "✅ R28 UNIT N.28 PASSED — DUAL CHECKPOINT + ROLLBACK-RESISTANT RECOVERY VALIDATED",
        flush=True,
    )
    print(
        "✅ NO REAL ORDER WAS SENT — NO DEMO ORDER WAS SENT — NO NETWORK WRITE OCCURRED",
        flush=True,
    )
    banner()


# ============================================================================
# PART 3 LOAD MARKER
# ============================================================================

print(
    "R28 UNIT N.28: PART 3 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.28
# PART 4 OF 4
#
# POST-DIAGNOSTIC SAFETY ASSERTIONS
# + HEALTH SERVER
# + PERSISTENT RUNTIME
# + MAIN ENTRY POINT
# ============================================================================


# ============================================================================
# POST-DIAGNOSTIC SAFETY ASSERTIONS
# ============================================================================

def post_diagnostic_safety_assertions() -> None:
    require(
        LIVE_ORDER_EXECUTION is False,
        "live execution unexpectedly enabled",
    )

    require(
        DEMO_ORDER_EXECUTION is False,
        "demo execution unexpectedly enabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "network writes unexpectedly enabled",
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
        SYNTHETIC_TRANSPORT_ONLY is True,
        "synthetic transport only flag disabled",
    )

    require(
        NETWORK_WRITE_COUNT == 0,
        "network write count is not zero",
    )

    require(
        REAL_POST_COUNT == 0,
        "real POST count is not zero",
    )

    require(
        DEMO_POST_COUNT == 0,
        "demo POST count is not zero",
    )

    print(
        "R28 UNIT N.28: POST-DIAGNOSTIC SAFETY ASSERTIONS PASSED",
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
                    "live_execution": LIVE_ORDER_EXECUTION,
                    "demo_execution": DEMO_ORDER_EXECUTION,
                    "real_post": REAL_POST_ENABLED,
                    "demo_post": DEMO_POST_ENABLED,
                    "network_writes": NETWORK_WRITES_ENABLED,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                    "network_write_count": NETWORK_WRITE_COUNT,
                    "real_post_count": REAL_POST_COUNT,
                    "demo_post_count": DEMO_POST_COUNT,
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


# ============================================================================
# HEALTH SERVER STARTUP
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
                f"R28 UNIT N.28: HEALTH SERVER LISTENING ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                "R28 UNIT N.28: HEALTH SERVER ERROR:",
                flush=True,
            )

            print(
                f"  {type(exc).__name__}: {exc}",
                flush=True,
            )

            raise

    thread = threading.Thread(
        target=runner,
        name="r28-n28-health-server",
        daemon=True,
    )

    thread.start()

    print(
        "R28 UNIT N.28: HEALTH SERVER STARTED",
        flush=True,
    )


# ============================================================================
# PERSISTENT RUNTIME
# ============================================================================

def persistent_runtime() -> None:
    print(
        "R28 UNIT N.28: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT N.28: ✅ NO REAL POST — NO DEMO POST — NO NETWORK WRITE",
        flush=True,
    )

    banner()

    while True:
        time.sleep(60)

        require(
            LIVE_ORDER_EXECUTION is False,
            "persistent runtime detected live execution enabled",
        )

        require(
            DEMO_ORDER_EXECUTION is False,
            "persistent runtime detected demo execution enabled",
        )

        require(
            NETWORK_WRITES_ENABLED is False,
            "persistent runtime detected network writes enabled",
        )

        require(
            REAL_POST_ENABLED is False,
            "persistent runtime detected real POST enabled",
        )

        require(
            DEMO_POST_ENABLED is False,
            "persistent runtime detected demo POST enabled",
        )

        require(
            SYNTHETIC_TRANSPORT_ONLY is True,
            "persistent runtime detected synthetic-only disabled",
        )

        require(
            NETWORK_WRITE_COUNT == 0,
            "persistent runtime detected network write",
        )

        require(
            REAL_POST_COUNT == 0,
            "persistent runtime detected real POST",
        )

        require(
            DEMO_POST_COUNT == 0,
            "persistent runtime detected demo POST",
        )


# ============================================================================
# COMPLETE RUNTIME
# ============================================================================

def main() -> None:
    run_diagnostic()

    post_diagnostic_safety_assertions()

    start_health_server()

    persistent_runtime()


# ============================================================================
# PART 4 LOAD MARKER
# ============================================================================

print(
    "R28 UNIT N.28: PART 4 DEFINITIONS LOADED",
    flush=True,
)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
