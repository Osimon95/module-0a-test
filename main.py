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
