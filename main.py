# ============================================================================
# R28 UNIT N.25
# DURABLE WAL + CHECKPOINT + EXACTLY-ONCE SYNTHETIC TRANSPORT
# + GENERATION LINEAGE + ANTI-ABA RECOVERY FENCING
#
# CORRECTED COMPLETE STANDALONE COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
# ============================================================================

print("R28 UNIT N.25: MAIN.PY ENTERED", flush=True)

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

print("R28 UNIT N.25: IMPORTS COMPLETE", flush=True)

# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.25"
UNIT_VERSION = "N.25"

SYMBOL = "BTCUSDT"
LEVERAGE = 100
MARGIN_MODE = "ISOLATED"
TRANSPORT_METHOD = "POST"
TRANSPORT_PATH = "/capi/v2/account/leverage"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

STATE_PREPARED = "PREPARED"
STATE_COMMITTED = "COMMITTED"
STATE_DISPATCHED = "DISPATCHED"
STATE_COMPLETED = "COMPLETED"

WAL_GENESIS = "0" * 64
SNAPSHOT_KEY = b"R28-N25-SNAPSHOT-INTEGRITY-KEY"

print("R28 UNIT N.25: CONSTANTS INITIALIZED", flush=True)

# ============================================================================
# HELPERS
# ============================================================================


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_sha256(key: bytes, value: str) -> str:
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()


def new_lineage_id() -> str:
    return uuid.uuid4().hex


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)
    raise RuntimeError(message)


def test_header(number: int, title: str) -> None:
    print("", flush=True)
    print(f"{UNIT_NAME} TEST {number}: {title}", flush=True)
    print("-" * 92, flush=True)


def passed(label: str) -> None:
    print(f"{label:<84} ✅ PASS", flush=True)


def expect_rejection(fn, label: str) -> str:
    rejected = False
    message = ""
    try:
        fn()
    except RuntimeError as exc:
        rejected = True
        message = str(exc)
    require(rejected, f"{label} was unexpectedly accepted")
    passed(label)
    return message


def payload_for_leverage() -> Dict[str, str]:
    return {
        "symbol": SYMBOL,
        "leverage": str(LEVERAGE),
        "marginMode": MARGIN_MODE,
    }


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass(frozen=True)
class RecoveryLease:
    owner: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    lease_nonce: int

    def identity(self) -> Tuple[Any, ...]:
        return (
            self.owner,
            self.generation,
            self.lineage_id,
            self.recovery_epoch,
            self.lease_nonce,
        )


@dataclass(frozen=True)
class DurableCommit:
    commit_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    payload: Dict[str, str]
    payload_hash: str
    transport_method: str
    transport_path: str

    def binding(self) -> Tuple[Any, ...]:
        return (
            self.commit_id,
            self.generation,
            self.lineage_id,
            self.recovery_epoch,
            self.payload_hash,
            self.transport_method,
            self.transport_path,
        )


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    commit_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    payload_hash: str
    transport_method: str
    transport_path: str
    transmitted: bool


@dataclass(frozen=True)
class WalRecord:
    sequence: int
    record_type: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    body: Dict[str, Any]
    prev_hash: str
    record_hash: str


@dataclass
class DurableState:
    generation: int = 1
    lineage_id: str = field(default_factory=new_lineage_id)
    recovery_epoch: int = 1
    lease_nonce_counter: int = 0
    state: str = STATE_PREPARED
    payload: Dict[str, str] = field(default_factory=payload_for_leverage)
    payload_hash: str = ""
    durable_commit: Optional[DurableCommit] = None
    receipt: Optional[SyntheticReceipt] = None
    finalized_commit_id: Optional[str] = None
    completed_dispatches: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    synthetic_transport_count: int = 0
    last_lease: Optional[RecoveryLease] = None
    wal: List[WalRecord] = field(default_factory=list)
    checkpoint_seal: str = ""

    def __post_init__(self) -> None:
        if not self.payload_hash:
            self.payload_hash = sha256_text(canonical_json(self.payload))
# ============================================================================
# N.25 ENGINE
# ============================================================================

class N25Engine:
    def __init__(self, state: Optional[DurableState] = None) -> None:
        self.lock = threading.RLock()
        self.state = copy.deepcopy(state) if state is not None else DurableState()
        self._validate_basic_state()

    # ------------------------------------------------------------------------
    # WAL
    # ------------------------------------------------------------------------

    def _append_wal(self, record_type: str, body: Dict[str, Any]) -> WalRecord:
        prev_hash = self.state.wal[-1].record_hash if self.state.wal else WAL_GENESIS
        sequence = len(self.state.wal) + 1
        unsigned = {
            "sequence": sequence,
            "record_type": record_type,
            "generation": self.state.generation,
            "lineage_id": self.state.lineage_id,
            "recovery_epoch": self.state.recovery_epoch,
            "body": copy.deepcopy(body),
            "prev_hash": prev_hash,
        }
        record_hash = sha256_text(canonical_json(unsigned))
        rec = WalRecord(record_hash=record_hash, **unsigned)
        self.state.wal.append(rec)
        return rec

    def validate_wal_chain(self, wal: Optional[List[WalRecord]] = None) -> bool:
        records = self.state.wal if wal is None else wal
        prev_hash = WAL_GENESIS
        for index, rec in enumerate(records, start=1):
            if rec.sequence != index:
                return False
            if rec.prev_hash != prev_hash:
                return False
            unsigned = {
                "sequence": rec.sequence,
                "record_type": rec.record_type,
                "generation": rec.generation,
                "lineage_id": rec.lineage_id,
                "recovery_epoch": rec.recovery_epoch,
                "body": rec.body,
                "prev_hash": rec.prev_hash,
            }
            expected = sha256_text(canonical_json(unsigned))
            if not hmac.compare_digest(expected, rec.record_hash):
                return False
            prev_hash = rec.record_hash
        return True

    # ------------------------------------------------------------------------
    # CHECKPOINT / SNAPSHOT
    # ------------------------------------------------------------------------

    def _snapshot_payload(self) -> Dict[str, Any]:
        return {
            "generation": self.state.generation,
            "lineage_id": self.state.lineage_id,
            "recovery_epoch": self.state.recovery_epoch,
            "lease_nonce_counter": self.state.lease_nonce_counter,
            "state": self.state.state,
            "payload": copy.deepcopy(self.state.payload),
            "payload_hash": self.state.payload_hash,
            "durable_commit": asdict(self.state.durable_commit) if self.state.durable_commit else None,
            "receipt": asdict(self.state.receipt) if self.state.receipt else None,
            "finalized_commit_id": self.state.finalized_commit_id,
            "completed_dispatches": copy.deepcopy(self.state.completed_dispatches),
            "synthetic_transport_count": self.state.synthetic_transport_count,
            "last_lease": asdict(self.state.last_lease) if self.state.last_lease else None,
            "wal": [asdict(r) for r in self.state.wal],
        }

    def create_checkpoint(self) -> Dict[str, Any]:
        with self.lock:
            snapshot = self._snapshot_payload()
            seal = hmac_sha256(SNAPSHOT_KEY, canonical_json(snapshot))
            self.state.checkpoint_seal = seal
            return {"snapshot": snapshot, "seal": seal}

    @classmethod
    def restore_checkpoint(cls, checkpoint: Dict[str, Any]) -> "N25Engine":
        if not isinstance(checkpoint, dict):
            local_block("invalid checkpoint structure")
        snapshot = checkpoint.get("snapshot")
        seal = checkpoint.get("seal")
        if not isinstance(snapshot, dict) or not isinstance(seal, str):
            local_block("invalid checkpoint structure")
        expected = hmac_sha256(SNAPSHOT_KEY, canonical_json(snapshot))
        if not hmac.compare_digest(expected, seal):
            local_block("snapshot integrity seal mismatch")

        wal = [WalRecord(**item) for item in snapshot.get("wal", [])]
        durable_commit = (
            DurableCommit(**snapshot["durable_commit"])
            if snapshot.get("durable_commit") is not None
            else None
        )
        receipt = (
            SyntheticReceipt(**snapshot["receipt"])
            if snapshot.get("receipt") is not None
            else None
        )
        last_lease = (
            RecoveryLease(**snapshot["last_lease"])
            if snapshot.get("last_lease") is not None
            else None
        )

        state = DurableState(
            generation=int(snapshot["generation"]),
            lineage_id=str(snapshot["lineage_id"]),
            recovery_epoch=int(snapshot["recovery_epoch"]),
            lease_nonce_counter=int(snapshot.get("lease_nonce_counter", 0)),
            state=str(snapshot["state"]),
            payload=copy.deepcopy(snapshot["payload"]),
            payload_hash=str(snapshot["payload_hash"]),
            durable_commit=durable_commit,
            receipt=receipt,
            finalized_commit_id=snapshot.get("finalized_commit_id"),
            completed_dispatches=copy.deepcopy(snapshot.get("completed_dispatches", {})),
            synthetic_transport_count=int(snapshot.get("synthetic_transport_count", 0)),
            last_lease=last_lease,
            wal=wal,
            checkpoint_seal=seal,
        )
        engine = cls(state)
        if not engine.validate_wal_chain():
            local_block("WAL hash chain mismatch")
        engine._validate_full_state()
        return engine

    # ------------------------------------------------------------------------
    # STATE VALIDATION
    # ------------------------------------------------------------------------

    def _validate_basic_state(self) -> None:
        if self.state.generation < 1:
            local_block("invalid generation")
        if self.state.recovery_epoch < 1:
            local_block("invalid recovery epoch")
        if not self.state.lineage_id:
            local_block("missing lineage id")
        expected_payload_hash = sha256_text(canonical_json(self.state.payload))
        if not hmac.compare_digest(expected_payload_hash, self.state.payload_hash):
            local_block("payload hash mismatch")

    def _validate_full_state(self) -> None:
        self._validate_basic_state()
        if not self.validate_wal_chain():
            local_block("WAL hash chain mismatch")
        c = self.state.durable_commit
        if c is not None:
            if c.payload_hash != sha256_text(canonical_json(c.payload)):
                local_block("durable commit payload hash mismatch")
            if c.generation != self.state.generation and self.state.state != STATE_PREPARED:
                local_block("durable commit generation mismatch")
        if self.state.state == STATE_COMPLETED:
            if self.state.receipt is None:
                local_block("completed state missing receipt")
            if self.state.finalized_commit_id is None:
                local_block("completed state missing finalized commit")

    # ------------------------------------------------------------------------
    # RECOVERY LEASES / GENERATIONS
    # ------------------------------------------------------------------------

    def acquire_recovery_lease(self, owner: str) -> RecoveryLease:
        with self.lock:
            if not owner:
                local_block("recovery lease owner required")
            if self.state.state == STATE_COMPLETED:
                local_block("terminal generation cannot acquire recovery lease")
            self.state.lease_nonce_counter += 1
            lease = RecoveryLease(
                owner=owner,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                lease_nonce=self.state.lease_nonce_counter,
            )
            self.state.last_lease = lease
            self._append_wal("RECOVERY_LEASE_ACQUIRED", asdict(lease))
            return lease

    def _require_current_lease(self, lease: RecoveryLease) -> None:
        current = self.state.last_lease
        if current is None:
            local_block("recovery lease required")
        if lease.identity() != current.identity():
            local_block("recovery lease identity mismatch")
        if lease.generation != self.state.generation:
            local_block("recovery lease generation mismatch")
        if lease.lineage_id != self.state.lineage_id:
            local_block("recovery lease lineage mismatch")
        if lease.recovery_epoch != self.state.recovery_epoch:
            local_block("recovery lease fence mismatch")

    def advance_generation(self) -> None:
        with self.lock:
            if self.state.state != STATE_COMPLETED:
                local_block("generation advancement requires completed state")
            prior_generation = self.state.generation
            prior_lineage = self.state.lineage_id
            prior_epoch = self.state.recovery_epoch
            prior_receipt = self.state.receipt
            if prior_receipt is not None:
                self.state.completed_dispatches[prior_receipt.commit_id] = asdict(prior_receipt)

            self.state.generation += 1
            self.state.recovery_epoch += 1
            self.state.lineage_id = new_lineage_id()
            self.state.state = STATE_PREPARED
            self.state.payload = payload_for_leverage()
            self.state.payload_hash = sha256_text(canonical_json(self.state.payload))
            self.state.durable_commit = None
            self.state.receipt = None
            self.state.finalized_commit_id = None
            self.state.last_lease = None
            self._append_wal(
                "GENERATION_ADVANCED",
                {
                    "prior_generation": prior_generation,
                    "prior_lineage_id": prior_lineage,
                    "prior_recovery_epoch": prior_epoch,
                    "new_generation": self.state.generation,
                    "new_lineage_id": self.state.lineage_id,
                    "new_recovery_epoch": self.state.recovery_epoch,
                },
            )

    # ------------------------------------------------------------------------
    # DURABLE COMMIT
    # ------------------------------------------------------------------------

    def durable_commit(self, lease: Optional[RecoveryLease] = None) -> DurableCommit:
        with self.lock:
            if self.state.state == STATE_COMPLETED:
                local_block("terminal generation cannot create durable commit")
            if lease is not None:
                self._require_current_lease(lease)

            if self.state.durable_commit is not None:
                return self.state.durable_commit

            body = {
                "generation": self.state.generation,
                "lineage_id": self.state.lineage_id,
                "recovery_epoch": self.state.recovery_epoch,
                "payload": copy.deepcopy(self.state.payload),
                "payload_hash": self.state.payload_hash,
                "transport_method": TRANSPORT_METHOD,
                "transport_path": TRANSPORT_PATH,
            }
            commit_id = sha256_text(canonical_json(body))
            commit = DurableCommit(commit_id=commit_id, **body)
            self.state.durable_commit = commit
            self.state.state = STATE_COMMITTED
            self._append_wal("DURABLE_COMMIT", asdict(commit))
            return commit

    # ------------------------------------------------------------------------
    # EXACT SYNTHETIC TRANSPORT BOUNDARY
    # ------------------------------------------------------------------------

    def synthetic_transport(self, commit: DurableCommit) -> SyntheticReceipt:
        with self.lock:
            durable = self.state.durable_commit
            if durable is None:
                local_block("durable commit required before transport")

            if commit.generation != self.state.generation:
                local_block("durable commit generation mismatch")
            if commit.lineage_id != self.state.lineage_id:
                local_block("durable commit lineage mismatch")
            if commit.recovery_epoch != self.state.recovery_epoch:
                local_block("durable commit recovery epoch mismatch")

            if commit.commit_id != durable.commit_id:
                local_block("durable commit identity mismatch")
            if commit.generation != durable.generation:
                local_block("durable commit generation binding mismatch")
            if commit.lineage_id != durable.lineage_id:
                local_block("durable commit lineage binding mismatch")
            if commit.recovery_epoch != durable.recovery_epoch:
                local_block("durable commit recovery epoch binding mismatch")
            if commit.payload_hash != durable.payload_hash:
                local_block("durable commit payload hash binding mismatch")
            if canonical_json(commit.payload) != canonical_json(durable.payload):
                local_block("durable commit payload binding mismatch")
            if commit.transport_method != durable.transport_method:
                local_block("durable commit transport method mismatch")
            if commit.transport_path != durable.transport_path:
                local_block("durable commit transport path mismatch")

            expected_hash = sha256_text(canonical_json(commit.payload))
            if commit.payload_hash != expected_hash:
                local_block("durable commit payload hash mismatch")
            if commit.transport_method != TRANSPORT_METHOD:
                local_block("synthetic transport method mismatch")
            if commit.transport_path != TRANSPORT_PATH:
                local_block("synthetic transport path mismatch")

            if self.state.finalized_commit_id == commit.commit_id:
                local_block("synthetic transport replay rejected")
            if self.state.receipt is not None and self.state.receipt.commit_id == commit.commit_id:
                local_block("synthetic transport replay rejected")
            if commit.commit_id in self.state.completed_dispatches:
                local_block("synthetic transport replay rejected")

            if REAL_POST_ENABLED or DEMO_POST_ENABLED or NETWORK_WRITES_ENABLED:
                local_block("network write firebreak configuration invalid")
            if not SYNTHETIC_TRANSPORT_ONLY:
                local_block("synthetic-only transport lock disabled")

            receipt_seed = {
                "commit_id": commit.commit_id,
                "generation": commit.generation,
                "lineage_id": commit.lineage_id,
                "recovery_epoch": commit.recovery_epoch,
                "payload_hash": commit.payload_hash,
                "transport_method": commit.transport_method,
                "transport_path": commit.transport_path,
            }
            receipt = SyntheticReceipt(
                receipt_id=sha256_text(canonical_json(receipt_seed)),
                commit_id=commit.commit_id,
                generation=commit.generation,
                lineage_id=commit.lineage_id,
                recovery_epoch=commit.recovery_epoch,
                payload_hash=commit.payload_hash,
                transport_method=commit.transport_method,
                transport_path=commit.transport_path,
                transmitted=False,
            )
            self.state.receipt = receipt
            self.state.synthetic_transport_count += 1
            self.state.state = STATE_DISPATCHED
            self._append_wal("SYNTHETIC_DISPATCH", asdict(receipt))
            return receipt

    # ------------------------------------------------------------------------
    # FINALIZATION / RECOVERY
    # ------------------------------------------------------------------------

    def finalize(self, receipt: SyntheticReceipt) -> SyntheticReceipt:
        with self.lock:
            if self.state.state == STATE_COMPLETED:
                if self.state.receipt is not None and self.state.receipt.receipt_id == receipt.receipt_id:
                    return self.state.receipt
                local_block("terminal generation immutable")
            if self.state.receipt is None:
                local_block("synthetic receipt required before finalization")
            if receipt.receipt_id != self.state.receipt.receipt_id:
                local_block("synthetic receipt identity mismatch")
            if self.state.durable_commit is None:
                local_block("durable commit required before finalization")
            if receipt.commit_id != self.state.durable_commit.commit_id:
                local_block("receipt commit binding mismatch")

            self.state.finalized_commit_id = receipt.commit_id
            self.state.state = STATE_COMPLETED
            self.state.completed_dispatches[receipt.commit_id] = asdict(receipt)
            self._append_wal(
                "FINALIZATION",
                {
                    "commit_id": receipt.commit_id,
                    "receipt_id": receipt.receipt_id,
                },
            )
            return receipt

    def recover(self) -> SyntheticReceipt:
        with self.lock:
            if self.state.state == STATE_COMPLETED:
                require(self.state.receipt is not None, "completed state missing receipt")
                return self.state.receipt
            if self.state.durable_commit is None:
                local_block("durable commit required before recovery")
            if self.state.receipt is None:
                receipt = self.synthetic_transport(self.state.durable_commit)
            else:
                receipt = self.state.receipt
            return self.finalize(receipt)

    # ------------------------------------------------------------------------
    # CORRUPTION HELPERS USED ONLY BY DIAGNOSTICS
    # ------------------------------------------------------------------------

    def export_state(self) -> DurableState:
        with self.lock:
            return copy.deepcopy(self.state)


print("R28 UNIT N.25: PART 1 DEFINITIONS LOADED", flush=True)
