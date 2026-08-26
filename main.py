# ============================================================================
# R28 UNIT N.39
# REPEATED COMPACTION + POST-COMPACTION TRANSACTION CONTINUITY
# + CHECKPOINT ANCESTRY + STALE-AUTHORITY FENCING
#
# COMPLETE SINGLE-FILE COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.39 INCREMENT OVER N.38:
#   - MULTIPLE CONSECUTIVE COMPACTION CYCLES
#   - CHECKPOINT ANCESTRY CHAIN
#   - POST-COMPACTION TRANSACTION CONTINUITY
#   - FINALIZED FENCE ACCUMULATION
#   - STALE CHECKPOINT / MANIFEST REJECTION
#   - STALE GENERATION / LINEAGE / EPOCH AUTHORITY REJECTION
#   - REPEATED RESTART VALIDATION
#   - CROSS-COMPACTION WAL SEQUENCE MONOTONICITY
#   - EXACTLY-ONCE SYNTHETIC DISPATCH PRESERVATION
#   - FINAL NETWORK WRITE FIREBREAK
# ============================================================================

print("R28 UNIT N.39: MAIN.PY ENTERED", flush=True)

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

print("R28 UNIT N.39: IMPORTS COMPLETE", flush=True)


# ============================================================================
# CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.39"
UNIT_VERSION = "N.39"

SYMBOL = "BTCUSDT"
HTTP_METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

TARGET_LEVERAGE = "100"
MARGIN_TYPE = "ISOLATED"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

INTEGRITY_KEY = b"R28-N39-LOCAL-INTEGRITY-KEY"
CERTIFICATE_KEY = b"R28-N39-CERTIFICATE-KEY"
CHECKPOINT_KEY = b"R28-N39-CHECKPOINT-KEY"
MANIFEST_KEY = b"R28-N39-MANIFEST-KEY"
SNAPSHOT_KEY = b"R28-N39-SNAPSHOT-KEY"

ZERO_HASH = "0" * 64

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_RECONCILED = "RECONCILED"
PHASE_FINALIZED = "FINALIZED"

COMPACTION_NONE = "NONE"
COMPACTION_PREPARED = "PREPARED"
COMPACTION_CHECKPOINTED = "CHECKPOINTED"
COMPACTION_REBASED = "REBASED"
COMPACTION_FINALIZED = "FINALIZED"

print("R28 UNIT N.39: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# GENERIC HELPERS
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


def keyed_digest(key: bytes, value: Any) -> str:
    if not isinstance(value, str):
        value = canonical_json(value)

    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def local_block(exc: Exception) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {exc}", flush=True)


TEST_GROUPS_EXECUTED = 0
PASS_ASSERTIONS = 0


def test_header(number: int, title: str) -> None:
    global TEST_GROUPS_EXECUTED

    TEST_GROUPS_EXECUTED += 1

    print("-" * 92, flush=True)
    print(
        f"{UNIT_NAME} TEST {number}: {title}",
        flush=True,
    )
    print("-" * 92, flush=True)


def pass_check(label: str, condition: bool) -> None:
    global PASS_ASSERTIONS

    require(condition, f"assertion failed: {label}")
    PASS_ASSERTIONS += 1

    print(
        f"{label:<84} ✅ PASS",
        flush=True,
    )


def expect_block(label: str, fn) -> None:
    try:
        fn()
    except Exception as exc:
        local_block(exc)
        pass_check(label, True)
        return

    raise RuntimeError(
        f"expected local rejection did not occur: {label}"
    )


# ============================================================================
# DURABLE OBJECTS
# ============================================================================

@dataclass
class WALRecord:
    sequence: int
    event_type: str
    payload: Dict[str, Any]
    previous_hash: str
    record_hash: str = ""

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
        }

    def calculate_hash(self) -> str:
        return sha256_text(
            canonical_json(self.signing_payload())
        )

    def seal(self) -> None:
        self.record_hash = self.calculate_hash()

    def validate(self) -> None:
        require(
            self.record_hash == self.calculate_hash(),
            "WAL record hash mismatch",
        )


@dataclass
class PromotionTransaction:
    transaction_id: str
    promotion_id: str
    receipt_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    method: str
    path: str
    payload: Dict[str, Any]
    payload_hash: str

    phase: str = PHASE_PREPARED

    synthetic_dispatch_count: int = 0
    network_transmission_count: int = 0

    reconciliation_certificate: Optional[str] = None


@dataclass
class CompactionCheckpoint:
    checkpoint_id: str
    checkpoint_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    compaction_cycle: int

    source_wal_final_hash: str
    parent_checkpoint_id: Optional[str]
    parent_checkpoint_hash: Optional[str]

    finalized_promotion_ids: List[str]
    finalized_receipt_ids: List[str]
    reconciled_transaction_ids: List[str]

    last_global_wal_sequence: int

    integrity_seal: str = ""

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_sequence": self.checkpoint_sequence,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "compaction_cycle": self.compaction_cycle,
            "source_wal_final_hash": self.source_wal_final_hash,
            "parent_checkpoint_id": self.parent_checkpoint_id,
            "parent_checkpoint_hash": self.parent_checkpoint_hash,
            "finalized_promotion_ids": sorted(
                self.finalized_promotion_ids
            ),
            "finalized_receipt_ids": sorted(
                self.finalized_receipt_ids
            ),
            "reconciled_transaction_ids": sorted(
                self.reconciled_transaction_ids
            ),
            "last_global_wal_sequence": self.last_global_wal_sequence,
        }

    def calculate_hash(self) -> str:
        return sha256_text(
            canonical_json(self.signing_payload())
        )

    def seal(self) -> None:
        self.integrity_seal = keyed_digest(
            CHECKPOINT_KEY,
            self.signing_payload(),
        )

    def validate_integrity(self) -> None:
        require(
            self.integrity_seal
            == keyed_digest(
                CHECKPOINT_KEY,
                self.signing_payload(),
            ),
            "checkpoint integrity seal mismatch",
        )


@dataclass
class CompactionManifest:
    manifest_id: str
    checkpoint_id: str
    checkpoint_hash: str
    checkpoint_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    compaction_cycle: int
    finalized: bool

    previous_manifest_id: Optional[str]
    integrity_seal: str = ""

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_hash": self.checkpoint_hash,
            "checkpoint_sequence": self.checkpoint_sequence,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "compaction_cycle": self.compaction_cycle,
            "finalized": self.finalized,
            "previous_manifest_id": self.previous_manifest_id,
        }

    def seal(self) -> None:
        self.integrity_seal = keyed_digest(
            MANIFEST_KEY,
            self.signing_payload(),
        )

    def validate_integrity(self) -> None:
        require(
            self.integrity_seal
            == keyed_digest(
                MANIFEST_KEY,
                self.signing_payload(),
            ),
            "manifest integrity seal mismatch",
        )


@dataclass
class DurableState:
    generation: int = 1
    lineage: str = field(
        default_factory=lambda: new_id("lineage")
    )
    recovery_epoch: int = 1

    global_wal_sequence: int = 0
    wal_records: List[WALRecord] = field(default_factory=list)
    wal_final_hash: str = ZERO_HASH

    transactions: Dict[str, PromotionTransaction] = field(
        default_factory=dict
    )

    finalized_promotion_ids: Set[str] = field(
        default_factory=set
    )
    finalized_receipt_ids: Set[str] = field(
        default_factory=set
    )
    reconciled_transaction_ids: Set[str] = field(
        default_factory=set
    )

    checkpoints: Dict[str, CompactionCheckpoint] = field(
        default_factory=dict
    )

    manifests: Dict[str, CompactionManifest] = field(
        default_factory=dict
    )

    active_checkpoint_id: Optional[str] = None
    active_manifest_id: Optional[str] = None

    compaction_cycle: int = 0
    compaction_phase: str = COMPACTION_NONE

    total_synthetic_dispatches: int = 0
    total_network_transmissions: int = 0


# ============================================================================
# ENGINE
# ============================================================================

class N39Engine:

    def __init__(
        self,
        state: Optional[DurableState] = None,
    ):
        self.state = state or DurableState()

    # ------------------------------------------------------------------------
    # WAL
    # ------------------------------------------------------------------------

    def append_wal(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> WALRecord:

        self.state.global_wal_sequence += 1

        record = WALRecord(
            sequence=self.state.global_wal_sequence,
            event_type=event_type,
            payload=copy.deepcopy(payload),
            previous_hash=self.state.wal_final_hash,
        )

        record.seal()

        self.state.wal_records.append(record)
        self.state.wal_final_hash = record.record_hash

        return record

    def validate_wal(self) -> None:
        previous_hash = ZERO_HASH
        previous_sequence = None

        for record in self.state.wal_records:
            record.validate()

            require(
                record.previous_hash == previous_hash,
                "WAL previous hash mismatch",
            )

            if previous_sequence is not None:
                require(
                    record.sequence == previous_sequence + 1,
                    "WAL sequence discontinuity",
                )

            previous_hash = record.record_hash
            previous_sequence = record.sequence

        expected_final = (
            self.state.wal_records[-1].record_hash
            if self.state.wal_records
            else ZERO_HASH
        )

        require(
            self.state.wal_final_hash == expected_final,
            "WAL final hash mismatch",
        )

    # ------------------------------------------------------------------------
    # TRANSACTIONS
    # ------------------------------------------------------------------------

    def create_transaction(
        self,
    ) -> PromotionTransaction:

        payload = {
            "symbol": SYMBOL,
            "marginType": MARGIN_TYPE,
            "leverage": TARGET_LEVERAGE,
        }

        payload_hash = sha256_text(
            canonical_json(payload)
        )

        tx = PromotionTransaction(
            transaction_id=new_id("tx"),
            promotion_id=new_id("promotion"),
            receipt_id=new_id("receipt"),
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            method=HTTP_METHOD,
            path=LEVERAGE_ENDPOINT,
            payload=payload,
            payload_hash=payload_hash,
        )

        self.state.transactions[tx.transaction_id] = tx

        self.append_wal(
            "PROMOTION_PREPARED",
            {
                "transaction_id": tx.transaction_id,
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
                "generation": tx.generation,
                "lineage": tx.lineage,
                "recovery_epoch": tx.recovery_epoch,
                "payload_hash": tx.payload_hash,
            },
        )

        return tx

    def validate_transaction_authority(
        self,
        tx: PromotionTransaction,
    ) -> None:

        require(
            tx.generation == self.state.generation,
            "transaction generation mismatch",
        )

        require(
            tx.lineage == self.state.lineage,
            "transaction lineage mismatch",
        )

        require(
            tx.recovery_epoch == self.state.recovery_epoch,
            "transaction recovery epoch mismatch",
        )

        require(
            tx.promotion_id
            not in self.state.finalized_promotion_ids,
            "promotion already finalized",
        )

        require(
            tx.receipt_id
            not in self.state.finalized_receipt_ids,
            "receipt already finalized",
        )

    def authorize_transaction(
        self,
        tx: PromotionTransaction,
    ) -> None:

        self.validate_transaction_authority(tx)

        require(
            tx.phase == PHASE_PREPARED,
            "transaction is not prepared",
        )

        tx.phase = PHASE_AUTHORIZED

        self.append_wal(
            "PROMOTION_AUTHORIZED",
            {
                "transaction_id": tx.transaction_id,
                "generation": tx.generation,
                "lineage": tx.lineage,
                "recovery_epoch": tx.recovery_epoch,
            },
        )

    def synthetic_dispatch(
        self,
        tx: PromotionTransaction,
    ) -> None:

        self.validate_transaction_authority(tx)

        require(
            SYNTHETIC_TRANSPORT_ONLY,
            "synthetic transport required",
        )

        require(
            not NETWORK_WRITES_ENABLED,
            "network writes unexpectedly enabled",
        )

        require(
            not REAL_POST_ENABLED,
            "real POST unexpectedly enabled",
        )

        require(
            not DEMO_POST_ENABLED,
            "demo POST unexpectedly enabled",
        )

        require(
            tx.phase == PHASE_AUTHORIZED,
            "transaction is not authorized",
        )

        require(
            tx.synthetic_dispatch_count == 0,
            "synthetic dispatch already occurred",
        )

        require(
            tx.method == HTTP_METHOD,
            "transport method mismatch",
        )

        require(
            tx.path == LEVERAGE_ENDPOINT,
            "transport path mismatch",
        )

        require(
            tx.payload_hash
            == sha256_text(canonical_json(tx.payload)),
            "transport payload hash mismatch",
        )

        tx.synthetic_dispatch_count += 1
        self.state.total_synthetic_dispatches += 1

        # Deliberately no network transport call exists here.
        tx.network_transmission_count = 0

        tx.phase = PHASE_DISPATCHED

        self.append_wal(
            "SYNTHETIC_DISPATCHED",
            {
                "transaction_id": tx.transaction_id,
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
                "payload_hash": tx.payload_hash,
                "method": tx.method,
                "path": tx.path,
                "synthetic": True,
                "network_transmitted": False,
            },
        )

    def reconcile_transaction(
        self,
        tx: PromotionTransaction,
    ) -> None:

        require(
            tx.phase == PHASE_DISPATCHED,
            "transaction is not dispatched",
        )

        certificate_payload = {
            "transaction_id": tx.transaction_id,
            "promotion_id": tx.promotion_id,
            "receipt_id": tx.receipt_id,
            "generation": tx.generation,
            "lineage": tx.lineage,
            "recovery_epoch": tx.recovery_epoch,
            "payload_hash": tx.payload_hash,
        }

        tx.reconciliation_certificate = keyed_digest(
            CERTIFICATE_KEY,
            certificate_payload,
        )

        tx.phase = PHASE_RECONCILED

        self.state.reconciled_transaction_ids.add(
            tx.transaction_id
        )

        self.append_wal(
            "PROMOTION_RECONCILED",
            certificate_payload,
        )

    def validate_reconciliation_certificate(
        self,
        tx: PromotionTransaction,
    ) -> None:

        require(
            tx.reconciliation_certificate is not None,
            "reconciliation certificate missing",
        )

        certificate_payload = {
            "transaction_id": tx.transaction_id,
            "promotion_id": tx.promotion_id,
            "receipt_id": tx.receipt_id,
            "generation": tx.generation,
            "lineage": tx.lineage,
            "recovery_epoch": tx.recovery_epoch,
            "payload_hash": tx.payload_hash,
        }

        expected = keyed_digest(
            CERTIFICATE_KEY,
            certificate_payload,
        )

        require(
            tx.reconciliation_certificate == expected,
            "reconciliation certificate mismatch",
        )

    def finalize_transaction(
        self,
        tx: PromotionTransaction,
    ) -> None:

        require(
            tx.phase == PHASE_RECONCILED,
            "transaction is not reconciled",
        )

        self.validate_reconciliation_certificate(tx)

        require(
            tx.promotion_id
            not in self.state.finalized_promotion_ids,
            "promotion already finalized",
        )

        require(
            tx.receipt_id
            not in self.state.finalized_receipt_ids,
            "receipt already finalized",
        )

        self.state.finalized_promotion_ids.add(
            tx.promotion_id
        )

        self.state.finalized_receipt_ids.add(
            tx.receipt_id
        )

        tx.phase = PHASE_FINALIZED

        self.append_wal(
            "PROMOTION_FINALIZED",
            {
                "transaction_id": tx.transaction_id,
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
            },
        )

    def clear_terminal_transaction(
        self,
        transaction_id: str,
    ) -> None:

        tx = self.state.transactions.get(transaction_id)

        require(
            tx is not None,
            "transaction missing",
        )

        require(
            tx.phase == PHASE_FINALIZED,
            "transaction is not terminal",
        )

        del self.state.transactions[transaction_id]

        self.append_wal(
            "TERMINAL_TRANSACTION_CLEARED",
            {
                "transaction_id": transaction_id,
            },
        )

    def execute_full_transaction(
        self,
    ) -> PromotionTransaction:

        tx = self.create_transaction()
        self.authorize_transaction(tx)
        self.synthetic_dispatch(tx)
        self.reconcile_transaction(tx)
        self.finalize_transaction(tx)

        return tx

    # ------------------------------------------------------------------------
    # CHECKPOINT / COMPACTION
    # ------------------------------------------------------------------------

    def active_checkpoint(
        self,
    ) -> Optional[CompactionCheckpoint]:

        if self.state.active_checkpoint_id is None:
            return None

        return self.state.checkpoints.get(
            self.state.active_checkpoint_id
        )

    def active_manifest(
        self,
    ) -> Optional[CompactionManifest]:

        if self.state.active_manifest_id is None:
            return None

        return self.state.manifests.get(
            self.state.active_manifest_id
        )

    def prepare_compaction(self) -> None:

        require(
            self.state.compaction_phase
            in (
                COMPACTION_NONE,
                COMPACTION_FINALIZED,
            ),
            "compaction already active",
        )

        self.validate_wal()

        self.state.compaction_cycle += 1
        self.state.compaction_phase = COMPACTION_PREPARED

        self.append_wal(
            "COMPACTION_PREPARED",
            {
                "compaction_cycle":
                    self.state.compaction_cycle,
                "generation":
                    self.state.generation,
                "source_wal_final_hash":
                    self.state.wal_final_hash,
            },
        )

    def create_checkpoint(
        self,
    ) -> CompactionCheckpoint:

        require(
            self.state.compaction_phase
            == COMPACTION_PREPARED,
            "compaction is not prepared",
        )

        self.validate_wal()

        parent = self.active_checkpoint()

        checkpoint = CompactionCheckpoint(
            checkpoint_id=new_id("checkpoint"),
            checkpoint_sequence=
                self.state.global_wal_sequence,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            compaction_cycle=self.state.compaction_cycle,
            source_wal_final_hash=
                self.state.wal_final_hash,
            parent_checkpoint_id=(
                parent.checkpoint_id
                if parent is not None
                else None
            ),
            parent_checkpoint_hash=(
                parent.calculate_hash()
                if parent is not None
                else None
            ),
            finalized_promotion_ids=sorted(
                self.state.finalized_promotion_ids
            ),
            finalized_receipt_ids=sorted(
                self.state.finalized_receipt_ids
            ),
            reconciled_transaction_ids=sorted(
                self.state.reconciled_transaction_ids
            ),
            last_global_wal_sequence=
                self.state.global_wal_sequence,
        )

        checkpoint.seal()

        self.state.checkpoints[
            checkpoint.checkpoint_id
        ] = checkpoint

        self.state.compaction_phase = COMPACTION_CHECKPOINTED

        return checkpoint

    def validate_checkpoint(
        self,
        checkpoint: CompactionCheckpoint,
        allow_historical_generation: bool = False,
    ) -> None:

        checkpoint.validate_integrity()

        if not allow_historical_generation:
            require(
                checkpoint.generation
                == self.state.generation,
                "checkpoint generation mismatch",
            )

            require(
                checkpoint.lineage
                == self.state.lineage,
                "checkpoint lineage mismatch",
            )

            require(
                checkpoint.recovery_epoch
                == self.state.recovery_epoch,
                "checkpoint recovery epoch mismatch",
            )

        require(
            checkpoint.compaction_cycle > 0,
            "checkpoint compaction cycle invalid",
        )

        if checkpoint.parent_checkpoint_id is not None:
            parent = self.state.checkpoints.get(
                checkpoint.parent_checkpoint_id
            )

            require(
                parent is not None,
                "checkpoint parent missing",
            )

            parent.validate_integrity()

            require(
                checkpoint.parent_checkpoint_hash
                == parent.calculate_hash(),
                "checkpoint parent hash mismatch",
            )

            require(
                checkpoint.compaction_cycle
                > parent.compaction_cycle,
                "checkpoint compaction cycle rollback",
            )

            require(
                checkpoint.checkpoint_sequence
                > parent.checkpoint_sequence,
                "checkpoint sequence rollback",
            )

    def create_manifest(
        self,
        checkpoint: CompactionCheckpoint,
    ) -> CompactionManifest:

        require(
            self.state.compaction_phase
            == COMPACTION_CHECKPOINTED,
            "compaction is not checkpointed",
        )

        self.validate_checkpoint(checkpoint)

        previous_manifest = self.active_manifest()

        manifest = CompactionManifest(
            manifest_id=new_id("manifest"),
            checkpoint_id=checkpoint.checkpoint_id,
            checkpoint_hash=checkpoint.calculate_hash(),
            checkpoint_sequence=
                checkpoint.checkpoint_sequence,
            generation=checkpoint.generation,
            lineage=checkpoint.lineage,
            recovery_epoch=checkpoint.recovery_epoch,
            compaction_cycle=
                checkpoint.compaction_cycle,
            finalized=False,
            previous_manifest_id=(
                previous_manifest.manifest_id
                if previous_manifest is not None
                else None
            ),
        )

        manifest.seal()

        self.state.manifests[
            manifest.manifest_id
        ] = manifest

        return manifest

    def validate_manifest(
        self,
        manifest: CompactionManifest,
        allow_historical_generation: bool = False,
    ) -> None:

        manifest.validate_integrity()

        checkpoint = self.state.checkpoints.get(
            manifest.checkpoint_id
        )

        require(
            checkpoint is not None,
            "manifest checkpoint missing",
        )

        self.validate_checkpoint(
            checkpoint,
            allow_historical_generation=
                allow_historical_generation,
        )

        require(
            manifest.checkpoint_hash
            == checkpoint.calculate_hash(),
            "manifest checkpoint mismatch",
        )

        require(
            manifest.checkpoint_sequence
            == checkpoint.checkpoint_sequence,
            "manifest checkpoint sequence mismatch",
        )

        require(
            manifest.generation
            == checkpoint.generation,
            "manifest generation mismatch",
        )

        require(
            manifest.lineage
            == checkpoint.lineage,
            "manifest lineage mismatch",
        )

        require(
            manifest.recovery_epoch
            == checkpoint.recovery_epoch,
            "manifest recovery epoch mismatch",
        )

        require(
            manifest.compaction_cycle
            == checkpoint.compaction_cycle,
            "manifest compaction cycle mismatch",
        )

    def rebase_wal(
        self,
        checkpoint: CompactionCheckpoint,
    ) -> None:

        require(
            self.state.compaction_phase
            == COMPACTION_CHECKPOINTED,
            "compaction is not checkpointed",
        )

        self.validate_checkpoint(checkpoint)

        self.state.wal_records = []
        self.state.wal_final_hash = ZERO_HASH

        self.state.compaction_phase = COMPACTION_REBASED

        self.append_wal(
            "WAL_REBASED",
            {
                "checkpoint_id":
                    checkpoint.checkpoint_id,
                "checkpoint_sequence":
                    checkpoint.checkpoint_sequence,
                "compaction_cycle":
                    checkpoint.compaction_cycle,
                "source_wal_final_hash":
                    checkpoint.source_wal_final_hash,
            },
        )

    def finalize_compaction(
        self,
        checkpoint: CompactionCheckpoint,
        manifest: CompactionManifest,
    ) -> None:

        require(
            self.state.compaction_phase
            == COMPACTION_REBASED,
            "compaction WAL is not rebased",
        )

        self.validate_checkpoint(checkpoint)
        self.validate_manifest(manifest)

        require(
            manifest.checkpoint_id
            == checkpoint.checkpoint_id,
            "manifest/checkpoint mismatch",
        )

        manifest.finalized = True
        manifest.seal()

        self.state.active_checkpoint_id = (
            checkpoint.checkpoint_id
        )

        self.state.active_manifest_id = (
            manifest.manifest_id
        )

        self.state.compaction_phase = COMPACTION_FINALIZED

        self.append_wal(
            "COMPACTION_FINALIZED",
            {
                "checkpoint_id":
                    checkpoint.checkpoint_id,
                "manifest_id":
                    manifest.manifest_id,
                "compaction_cycle":
                    checkpoint.compaction_cycle,
            },
        )

    def compact(
        self,
    ) -> Tuple[
        CompactionCheckpoint,
        CompactionManifest,
    ]:

        self.prepare_compaction()
        checkpoint = self.create_checkpoint()
        manifest = self.create_manifest(checkpoint)
        self.rebase_wal(checkpoint)
        self.finalize_compaction(
            checkpoint,
            manifest,
        )

        return checkpoint, manifest

    # ------------------------------------------------------------------------
    # GENERATION ADVANCE
    # ------------------------------------------------------------------------

    def advance_generation(self) -> None:

        require(
            self.state.compaction_phase
            in (
                COMPACTION_NONE,
                COMPACTION_FINALIZED,
            ),
            "cannot advance generation during compaction",
        )

        old_generation = self.state.generation
        old_lineage = self.state.lineage
        old_epoch = self.state.recovery_epoch

        self.state.generation += 1
        self.state.lineage = new_id("lineage")
        self.state.recovery_epoch += 1

        self.append_wal(
            "GENERATION_ADVANCED",
            {
                "old_generation": old_generation,
                "new_generation":
                    self.state.generation,
                "old_lineage": old_lineage,
                "new_lineage":
                    self.state.lineage,
                "old_recovery_epoch": old_epoch,
                "new_recovery_epoch":
                    self.state.recovery_epoch,
            },
        )

    # ------------------------------------------------------------------------
    # SNAPSHOT
    # ------------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:

        raw = {
            "state": copy.deepcopy(self.state),
        }

        serializable = self._state_to_dict(
            raw["state"]
        )

        envelope = {
            "payload": serializable,
        }

        envelope["integrity_seal"] = keyed_digest(
            SNAPSHOT_KEY,
            envelope["payload"],
        )

        return envelope

    def restore_snapshot(
        self,
        envelope: Dict[str, Any],
    ) -> None:

        payload = envelope.get("payload")
        integrity_seal = envelope.get(
            "integrity_seal"
        )

        require(
            payload is not None,
            "snapshot payload missing",
        )

        require(
            integrity_seal
            == keyed_digest(
                SNAPSHOT_KEY,
                payload,
            ),
            "snapshot integrity seal mismatch",
        )

        self.state = self._state_from_dict(
            copy.deepcopy(payload)
        )

        self.validate_complete_state()

    def _state_to_dict(
        self,
        state: DurableState,
    ) -> Dict[str, Any]:

        return {
            "generation": state.generation,
            "lineage": state.lineage,
            "recovery_epoch": state.recovery_epoch,
            "global_wal_sequence":
                state.global_wal_sequence,
            "wal_records": [
                asdict(record)
                for record in state.wal_records
            ],
            "wal_final_hash":
                state.wal_final_hash,
            "transactions": {
                key: asdict(value)
                for key, value
                in state.transactions.items()
            },
            "finalized_promotion_ids": sorted(
                state.finalized_promotion_ids
            ),
            "finalized_receipt_ids": sorted(
                state.finalized_receipt_ids
            ),
            "reconciled_transaction_ids": sorted(
                state.reconciled_transaction_ids
            ),
            "checkpoints": {
                key: asdict(value)
                for key, value
                in state.checkpoints.items()
            },
            "manifests": {
                key: asdict(value)
                for key, value
                in state.manifests.items()
            },
            "active_checkpoint_id":
                state.active_checkpoint_id,
            "active_manifest_id":
                state.active_manifest_id,
            "compaction_cycle":
                state.compaction_cycle,
            "compaction_phase":
                state.compaction_phase,
            "total_synthetic_dispatches":
                state.total_synthetic_dispatches,
            "total_network_transmissions":
                state.total_network_transmissions,
        }

    def _state_from_dict(
        self,
        payload: Dict[str, Any],
    ) -> DurableState:

        state = DurableState(
            generation=payload["generation"],
            lineage=payload["lineage"],
            recovery_epoch=
                payload["recovery_epoch"],
            global_wal_sequence=
                payload["global_wal_sequence"],
            wal_final_hash=
                payload["wal_final_hash"],
            active_checkpoint_id=
                payload["active_checkpoint_id"],
            active_manifest_id=
                payload["active_manifest_id"],
            compaction_cycle=
                payload["compaction_cycle"],
            compaction_phase=
                payload["compaction_phase"],
            total_synthetic_dispatches=
                payload[
                    "total_synthetic_dispatches"
                ],
            total_network_transmissions=
                payload[
                    "total_network_transmissions"
                ],
        )

        state.wal_records = [
            WALRecord(**item)
            for item in payload["wal_records"]
        ]

        state.transactions = {
            key: PromotionTransaction(**value)
            for key, value
            in payload["transactions"].items()
        }

        state.finalized_promotion_ids = set(
            payload["finalized_promotion_ids"]
        )

        state.finalized_receipt_ids = set(
            payload["finalized_receipt_ids"]
        )

        state.reconciled_transaction_ids = set(
            payload[
                "reconciled_transaction_ids"
            ]
        )

        state.checkpoints = {
            key: CompactionCheckpoint(**value)
            for key, value
            in payload["checkpoints"].items()
        }

        state.manifests = {
            key: CompactionManifest(**value)
            for key, value
            in payload["manifests"].items()
        }

        return state

    # ------------------------------------------------------------------------
    # COMPLETE STATE VALIDATION
    # ------------------------------------------------------------------------

    def validate_checkpoint_ancestry(self) -> None:

        checkpoint = self.active_checkpoint()
        seen = set()

        while checkpoint is not None:
            checkpoint.validate_integrity()

            require(
                checkpoint.checkpoint_id not in seen,
                "checkpoint ancestry cycle detected",
            )

            seen.add(checkpoint.checkpoint_id)

            if checkpoint.parent_checkpoint_id is None:
                break

            parent = self.state.checkpoints.get(
                checkpoint.parent_checkpoint_id
            )

            require(
                parent is not None,
                "checkpoint ancestry parent missing",
            )

            parent.validate_integrity()

            require(
                checkpoint.parent_checkpoint_hash
                == parent.calculate_hash(),
                "checkpoint ancestry hash mismatch",
            )

            require(
                parent.compaction_cycle
                < checkpoint.compaction_cycle,
                "checkpoint ancestry cycle rollback",
            )

            require(
                parent.checkpoint_sequence
                < checkpoint.checkpoint_sequence,
                "checkpoint ancestry sequence rollback",
            )

            checkpoint = parent

    def validate_complete_state(self) -> None:

        self.validate_wal()

        require(
            self.state.total_network_transmissions == 0,
            "network transmission counter is nonzero",
        )

        for tx in self.state.transactions.values():
            require(
                tx.network_transmission_count == 0,
                "transaction network transmission detected",
            )

            require(
                tx.synthetic_dispatch_count <= 1,
                "duplicate synthetic dispatch detected",
            )

        for checkpoint in self.state.checkpoints.values():
            checkpoint.validate_integrity()

        for manifest in self.state.manifests.values():
            manifest.validate_integrity()

            checkpoint = self.state.checkpoints.get(
                manifest.checkpoint_id
            )

            require(
                checkpoint is not None,
                "manifest checkpoint missing",
            )

            require(
                manifest.checkpoint_hash
                == checkpoint.calculate_hash(),
                "manifest checkpoint mismatch",
            )

        if self.state.active_checkpoint_id is not None:
            require(
                self.state.active_checkpoint_id
                in self.state.checkpoints,
                "active checkpoint missing",
            )

        if self.state.active_manifest_id is not None:
            require(
                self.state.active_manifest_id
                in self.state.manifests,
                "active manifest missing",
            )

        self.validate_checkpoint_ancestry()


print("R28 UNIT N.39: DEFINITIONS LOADED", flush=True)


# ============================================================================
# TEST SUITE
# ============================================================================

def run_diagnostics() -> None:

    engine = N39Engine()

    # ------------------------------------------------------------------------
    test_header(
        1,
        "INITIAL DURABLE STATE",
    )

    pass_check(
        "Initial Generation Is One",
        engine.state.generation == 1,
    )

    pass_check(
        "Initial Recovery Epoch Is One",
        engine.state.recovery_epoch == 1,
    )

    pass_check(
        "Initial WAL Is Empty",
        len(engine.state.wal_records) == 0,
    )

    pass_check(
        "Initial WAL Final Hash Is Zero",
        engine.state.wal_final_hash == ZERO_HASH,
    )

    # ------------------------------------------------------------------------
    test_header(
        2,
        "FIRST PROMOTION TRANSACTION",
    )

    tx1 = engine.execute_full_transaction()

    pass_check(
        "First Promotion Transaction Finalized",
        tx1.phase == PHASE_FINALIZED,
    )

    pass_check(
        "First Promotion Fence Established",
        tx1.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "First Receipt Fence Established",
        tx1.receipt_id
        in engine.state.finalized_receipt_ids,
    )

    pass_check(
        "First Transaction Reconciliation Fence Established",
        tx1.transaction_id
        in engine.state.reconciled_transaction_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        3,
        "FIRST TRANSACTION TERMINAL CLEAR",
    )

    engine.clear_terminal_transaction(
        tx1.transaction_id
    )

    pass_check(
        "First Terminal Transaction Cleared",
        tx1.transaction_id
        not in engine.state.transactions,
    )

    pass_check(
        "First Promotion Fence Survives Clear",
        tx1.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        4,
        "FIRST PRE-COMPACTION WAL VALIDATION",
    )

    engine.validate_wal()

    pass_check(
        "First Pre-Compaction WAL Records Validate",
        True,
    )

    pass_check(
        "First Pre-Compaction WAL Final Hash Validates",
        True,
    )

    first_pre_compaction_sequence = (
        engine.state.global_wal_sequence
    )

    # ------------------------------------------------------------------------
    test_header(
        5,
        "FIRST COMPACTION CYCLE",
    )

    cp1, mf1 = engine.compact()

    pass_check(
        "First Compaction Finalized",
        engine.state.compaction_phase
        == COMPACTION_FINALIZED,
    )

    pass_check(
        "First Checkpoint Is Active",
        engine.state.active_checkpoint_id
        == cp1.checkpoint_id,
    )

    pass_check(
        "First Manifest Is Active",
        engine.state.active_manifest_id
        == mf1.manifest_id,
    )

    pass_check(
        "First Manifest Finalized",
        mf1.finalized is True,
    )

    # ------------------------------------------------------------------------
    test_header(
        6,
        "FIRST CHECKPOINT CONTENT",
    )

    pass_check(
        "First Checkpoint Contains Promotion Fence",
        tx1.promotion_id
        in cp1.finalized_promotion_ids,
    )

    pass_check(
        "First Checkpoint Contains Receipt Fence",
        tx1.receipt_id
        in cp1.finalized_receipt_ids,
    )

    pass_check(
        "First Checkpoint Contains Reconciliation Fence",
        tx1.transaction_id
        in cp1.reconciled_transaction_ids,
    )

    pass_check(
        "First Checkpoint Has No Parent",
        cp1.parent_checkpoint_id is None,
    )

    # ------------------------------------------------------------------------
    test_header(
        7,
        "FIRST COMPACTION RESTART",
    )

    snapshot1 = engine.snapshot()

    restart1 = N39Engine()
    restart1.restore_snapshot(snapshot1)

    pass_check(
        "First Compacted State Restored",
        restart1.state.active_checkpoint_id
        == cp1.checkpoint_id,
    )

    pass_check(
        "First Promotion Fence Survives Restart",
        tx1.promotion_id
        in restart1.state.finalized_promotion_ids,
    )

    pass_check(
        "First Receipt Fence Survives Restart",
        tx1.receipt_id
        in restart1.state.finalized_receipt_ids,
    )

    engine = restart1

    # ------------------------------------------------------------------------
    test_header(
        8,
        "POST-COMPACTION TRANSACTION CONTINUITY",
    )

    tx2 = engine.execute_full_transaction()

    pass_check(
        "Second Promotion Transaction Finalized",
        tx2.phase == PHASE_FINALIZED,
    )

    pass_check(
        "Second Promotion Uses Current Generation",
        tx2.generation == engine.state.generation,
    )

    pass_check(
        "Second Promotion Uses Current Lineage",
        tx2.lineage == engine.state.lineage,
    )

    pass_check(
        "Second Promotion Uses Current Recovery Epoch",
        tx2.recovery_epoch
        == engine.state.recovery_epoch,
    )

    # ------------------------------------------------------------------------
    test_header(
        9,
        "FINALIZED FENCE ACCUMULATION",
    )

    pass_check(
        "First Promotion Fence Still Present",
        tx1.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "Second Promotion Fence Present",
        tx2.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "First Receipt Fence Still Present",
        tx1.receipt_id
        in engine.state.finalized_receipt_ids,
    )

    pass_check(
        "Second Receipt Fence Present",
        tx2.receipt_id
        in engine.state.finalized_receipt_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        10,
        "SECOND TRANSACTION TERMINAL CLEAR",
    )

    engine.clear_terminal_transaction(
        tx2.transaction_id
    )

    pass_check(
        "Second Terminal Transaction Cleared",
        tx2.transaction_id
        not in engine.state.transactions,
    )

    pass_check(
        "Second Promotion Fence Survives Clear",
        tx2.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        11,
        "SECOND PRE-COMPACTION WAL VALIDATION",
    )

    engine.validate_wal()

    pass_check(
        "Second Pre-Compaction WAL Records Validate",
        True,
    )

    pass_check(
        "Global WAL Sequence Advanced",
        engine.state.global_wal_sequence
        > first_pre_compaction_sequence,
    )

    sequence_before_second_compaction = (
        engine.state.global_wal_sequence
    )

    # ------------------------------------------------------------------------
    test_header(
        12,
        "SECOND COMPACTION CYCLE",
    )

    cp2, mf2 = engine.compact()

    pass_check(
        "Second Compaction Finalized",
        engine.state.compaction_phase
        == COMPACTION_FINALIZED,
    )

    pass_check(
        "Compaction Cycle Advanced",
        cp2.compaction_cycle
        > cp1.compaction_cycle,
    )

    pass_check(
        "Second Checkpoint Sequence Advanced",
        cp2.checkpoint_sequence
        > cp1.checkpoint_sequence,
    )

    # ------------------------------------------------------------------------
    test_header(
        13,
        "CHECKPOINT ANCESTRY",
    )

    pass_check(
        "Second Checkpoint References First Checkpoint",
        cp2.parent_checkpoint_id
        == cp1.checkpoint_id,
    )

    pass_check(
        "Second Checkpoint Parent Hash Matches First",
        cp2.parent_checkpoint_hash
        == cp1.calculate_hash(),
    )

    engine.validate_checkpoint_ancestry()

    pass_check(
        "Checkpoint Ancestry Validates",
        True,
    )

    # ------------------------------------------------------------------------
    test_header(
        14,
        "SECOND CHECKPOINT ACCUMULATED FENCES",
    )

    pass_check(
        "Second Checkpoint Contains First Promotion Fence",
        tx1.promotion_id
        in cp2.finalized_promotion_ids,
    )

    pass_check(
        "Second Checkpoint Contains Second Promotion Fence",
        tx2.promotion_id
        in cp2.finalized_promotion_ids,
    )

    pass_check(
        "Second Checkpoint Contains First Receipt Fence",
        tx1.receipt_id
        in cp2.finalized_receipt_ids,
    )

    pass_check(
        "Second Checkpoint Contains Second Receipt Fence",
        tx2.receipt_id
        in cp2.finalized_receipt_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        15,
        "SECOND MANIFEST CHAIN",
    )

    pass_check(
        "Second Manifest References Previous Manifest",
        mf2.previous_manifest_id
        == mf1.manifest_id,
    )

    pass_check(
        "Second Manifest References Second Checkpoint",
        mf2.checkpoint_id
        == cp2.checkpoint_id,
    )

    pass_check(
        "Second Manifest Finalized",
        mf2.finalized is True,
    )

    # ------------------------------------------------------------------------
    test_header(
        16,
        "SECOND COMPACTION RESTART",
    )

    snapshot2 = engine.snapshot()

    restart2 = N39Engine()
    restart2.restore_snapshot(snapshot2)

    pass_check(
        "Second Compacted State Restored",
        restart2.state.active_checkpoint_id
        == cp2.checkpoint_id,
    )

    pass_check(
        "Second Active Manifest Restored",
        restart2.state.active_manifest_id
        == mf2.manifest_id,
    )

    engine = restart2

    # ------------------------------------------------------------------------
    test_header(
        17,
        "MULTI-CYCLE FINALIZED FENCE SURVIVAL",
    )

    pass_check(
        "First Promotion Fence Survives Second Compaction",
        tx1.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "Second Promotion Fence Survives Second Compaction",
        tx2.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "First Receipt Fence Survives Second Compaction",
        tx1.receipt_id
        in engine.state.finalized_receipt_ids,
    )

    pass_check(
        "Second Receipt Fence Survives Second Compaction",
        tx2.receipt_id
        in engine.state.finalized_receipt_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        18,
        "STALE FINALIZED PROMOTION REJECTION",
    )

    stale_promotion_tx = engine.create_transaction()

    stale_promotion_tx.promotion_id = tx1.promotion_id

    expect_block(
        "Stale Finalized Promotion Rejected",
        lambda: engine.authorize_transaction(
            stale_promotion_tx
        ),
    )

    del engine.state.transactions[
        stale_promotion_tx.transaction_id
    ]

    # ------------------------------------------------------------------------
    test_header(
        19,
        "STALE FINALIZED RECEIPT REJECTION",
    )

    stale_receipt_tx = engine.create_transaction()

    stale_receipt_tx.receipt_id = tx2.receipt_id

    expect_block(
        "Stale Finalized Receipt Rejected",
        lambda: engine.authorize_transaction(
            stale_receipt_tx
        ),
    )

    del engine.state.transactions[
        stale_receipt_tx.transaction_id
    ]

    # ------------------------------------------------------------------------
    test_header(
        20,
        "CHECKPOINT PARENT HASH TAMPER REJECTION",
    )

    tampered_cp2 = copy.deepcopy(cp2)
    tampered_cp2.parent_checkpoint_hash = "f" * 64

    # Re-seal to prove ancestry binding, not merely seal binding.
    tampered_cp2.seal()

    expect_block(
        "Tampered Checkpoint Parent Hash Rejected",
        lambda: engine.validate_checkpoint(
            tampered_cp2,
            allow_historical_generation=True,
        ),
    )

    # ------------------------------------------------------------------------
    test_header(
        21,
        "CHECKPOINT ANCESTRY CYCLE REJECTION",
    )

    cycle_checkpoint = copy.deepcopy(cp2)

    cycle_checkpoint.parent_checkpoint_id = (
        cycle_checkpoint.checkpoint_id
    )

    cycle_checkpoint.parent_checkpoint_hash = (
        cycle_checkpoint.calculate_hash()
    )

    cycle_checkpoint.seal()

    temp_original = engine.state.checkpoints[
        cp2.checkpoint_id
    ]

    engine.state.checkpoints[
        cp2.checkpoint_id
    ] = cycle_checkpoint

    expect_block(
        "Checkpoint Ancestry Cycle Rejected",
        engine.validate_checkpoint_ancestry,
    )

    engine.state.checkpoints[
        cp2.checkpoint_id
    ] = temp_original

    # ------------------------------------------------------------------------
    test_header(
        22,
        "MANIFEST/CHECKPOINT HASH MISMATCH REJECTION",
    )

    bad_manifest = copy.deepcopy(mf2)
    bad_manifest.checkpoint_hash = "a" * 64
    bad_manifest.seal()

    expect_block(
        "Manifest Pointing To Wrong Checkpoint Hash Rejected",
        lambda: engine.validate_manifest(
            bad_manifest,
            allow_historical_generation=True,
        ),
    )

    # ------------------------------------------------------------------------
    test_header(
        23,
        "MANIFEST CHECKPOINT SEQUENCE MISMATCH REJECTION",
    )

    bad_sequence_manifest = copy.deepcopy(mf2)
    bad_sequence_manifest.checkpoint_sequence += 1
    bad_sequence_manifest.seal()

    expect_block(
        "Manifest Checkpoint Sequence Mismatch Rejected",
        lambda: engine.validate_manifest(
            bad_sequence_manifest,
            allow_historical_generation=True,
        ),
    )

    # ------------------------------------------------------------------------
    test_header(
        24,
        "CHECKPOINT INTEGRITY TAMPER REJECTION",
    )

    bad_checkpoint = copy.deepcopy(cp2)
    bad_checkpoint.finalized_promotion_ids.append(
        "forged-promotion"
    )

    expect_block(
        "Tampered Checkpoint Rejected",
        lambda: bad_checkpoint.validate_integrity(),
    )

    # ------------------------------------------------------------------------
    test_header(
        25,
        "MANIFEST INTEGRITY TAMPER REJECTION",
    )

    integrity_bad_manifest = copy.deepcopy(mf2)
    integrity_bad_manifest.compaction_cycle += 1

    expect_block(
        "Tampered Manifest Rejected",
        lambda:
            integrity_bad_manifest.validate_integrity(),
    )

    # ------------------------------------------------------------------------
    test_header(
        26,
        "SNAPSHOT INTEGRITY TAMPER REJECTION",
    )

    bad_snapshot = copy.deepcopy(snapshot2)

    bad_snapshot["payload"]["generation"] += 1

    expect_block(
        "Tampered Durable Snapshot Rejected",
        lambda: N39Engine().restore_snapshot(
            bad_snapshot
        ),
    )

    # ------------------------------------------------------------------------
    test_header(
        27,
        "POST-SECOND-COMPACTION TRANSACTION",
    )

    tx3 = engine.execute_full_transaction()

    pass_check(
        "Third Promotion Transaction Finalized",
        tx3.phase == PHASE_FINALIZED,
    )

    pass_check(
        "Third Promotion Fence Established",
        tx3.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "Third Synthetic Dispatch Exactly Once",
        tx3.synthetic_dispatch_count == 1,
    )

    pass_check(
        "Third Transaction Network Transmission Zero",
        tx3.network_transmission_count == 0,
    )

    # ------------------------------------------------------------------------
    test_header(
        28,
        "EXACTLY-ONCE SYNTHETIC DISPATCH FENCE",
    )

    expect_block(
        "Second Synthetic Dispatch Rejected",
        lambda: engine.synthetic_dispatch(tx3),
    )

    pass_check(
        "Synthetic Dispatch Count Remains One",
        tx3.synthetic_dispatch_count == 1,
    )

    # ------------------------------------------------------------------------
    test_header(
        29,
        "THIRD TERMINAL CLEAR",
    )

    engine.clear_terminal_transaction(
        tx3.transaction_id
    )

    pass_check(
        "Third Terminal Transaction Cleared",
        tx3.transaction_id
        not in engine.state.transactions,
    )

    pass_check(
        "Third Promotion Fence Preserved",
        tx3.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        30,
        "THIRD COMPACTION CYCLE",
    )

    cp3, mf3 = engine.compact()

    pass_check(
        "Third Compaction Finalized",
        engine.state.compaction_phase
        == COMPACTION_FINALIZED,
    )

    pass_check(
        "Third Checkpoint References Second",
        cp3.parent_checkpoint_id
        == cp2.checkpoint_id,
    )

    pass_check(
        "Third Checkpoint Sequence Advanced",
        cp3.checkpoint_sequence
        > cp2.checkpoint_sequence,
    )

    pass_check(
        "Third Compaction Cycle Advanced",
        cp3.compaction_cycle
        > cp2.compaction_cycle,
    )

    # ------------------------------------------------------------------------
    test_header(
        31,
        "THREE-LEVEL CHECKPOINT ANCESTRY",
    )

    engine.validate_checkpoint_ancestry()

    pass_check(
        "Three-Level Checkpoint Ancestry Validates",
        True,
    )

    pass_check(
        "Third Checkpoint Contains All Promotion Fences",
        all(
            promotion_id
            in cp3.finalized_promotion_ids
            for promotion_id in (
                tx1.promotion_id,
                tx2.promotion_id,
                tx3.promotion_id,
            )
        ),
    )

    pass_check(
        "Third Checkpoint Contains All Receipt Fences",
        all(
            receipt_id
            in cp3.finalized_receipt_ids
            for receipt_id in (
                tx1.receipt_id,
                tx2.receipt_id,
                tx3.receipt_id,
            )
        ),
    )

    # ------------------------------------------------------------------------
    test_header(
        32,
        "THIRD COMPACTION RESTART",
    )

    snapshot3 = engine.snapshot()

    restart3 = N39Engine()
    restart3.restore_snapshot(snapshot3)

    pass_check(
        "Third Compacted State Restored",
        restart3.state.active_checkpoint_id
        == cp3.checkpoint_id,
    )

    pass_check(
        "Third Manifest Restored",
        restart3.state.active_manifest_id
        == mf3.manifest_id,
    )

    pass_check(
        "Three Compaction Cycles Preserved",
        restart3.state.compaction_cycle == 3,
    )

    engine = restart3

    # ------------------------------------------------------------------------
    test_header(
        33,
        "GENERATION ADVANCE AFTER REPEATED COMPACTION",
    )

    old_generation = engine.state.generation
    old_lineage = engine.state.lineage
    old_epoch = engine.state.recovery_epoch

    engine.advance_generation()

    pass_check(
        "Generation Advanced Monotonically",
        engine.state.generation
        == old_generation + 1,
    )

    pass_check(
        "Lineage Changed On Generation Advance",
        engine.state.lineage != old_lineage,
    )

    pass_check(
        "Recovery Epoch Advanced Monotonically",
        engine.state.recovery_epoch
        == old_epoch + 1,
    )

    # ------------------------------------------------------------------------
    test_header(
        34,
        "FINALIZED FENCE CROSS-GENERATION PRESERVATION",
    )

    pass_check(
        "First Promotion Fence Preserved Across Generation",
        tx1.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "Second Promotion Fence Preserved Across Generation",
        tx2.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    pass_check(
        "Third Promotion Fence Preserved Across Generation",
        tx3.promotion_id
        in engine.state.finalized_promotion_ids,
    )

    # ------------------------------------------------------------------------
    test_header(
        35,
        "STALE TRANSACTION GENERATION REJECTION",
    )

    stale_generation_tx = engine.create_transaction()
    stale_generation_tx.generation = old_generation

    expect_block(
        "Stale Transaction Generation Rejected",
        lambda: engine.authorize_transaction(
            stale_generation_tx
        ),
    )

    del engine.state.transactions[
        stale_generation_tx.transaction_id
    ]

    # ------------------------------------------------------------------------
    test_header(
        36,
        "STALE TRANSACTION LINEAGE REJECTION",
    )

    stale_lineage_tx = engine.create_transaction()
    stale_lineage_tx.lineage = old_lineage

    expect_block(
        "Stale Transaction Lineage Rejected",
        lambda: engine.authorize_transaction(
            stale_lineage_tx
        ),
    )

    del engine.state.transactions[
        stale_lineage_tx.transaction_id
    ]

    # ------------------------------------------------------------------------
    test_header(
        37,
        "STALE TRANSACTION RECOVERY EPOCH REJECTION",
    )

    stale_epoch_tx = engine.create_transaction()
    stale_epoch_tx.recovery_epoch = old_epoch

    expect_block(
        "Stale Transaction Recovery Epoch Rejected",
        lambda: engine.authorize_transaction(
            stale_epoch_tx
        ),
    )

    del engine.state.transactions[
        stale_epoch_tx.transaction_id
    ]

    # ------------------------------------------------------------------------
    test_header(
        38,
        "STALE CROSS-GENERATION CHECKPOINT REJECTION",
    )

    expect_block(
        "Stale Cross-Generation Checkpoint Rejected",
        lambda: engine.validate_checkpoint(cp3),
    )

    # Historical ancestry remains cryptographically inspectable.
    engine.validate_checkpoint(
        cp3,
        allow_historical_generation=True,
    )

    pass_check(
        "Historical Checkpoint Remains Integrity Verifiable",
        True,
    )

    # ------------------------------------------------------------------------
    test_header(
        39,
        "STALE CROSS-GENERATION MANIFEST REJECTION",
    )

    expect_block(
        "Stale Cross-Generation Manifest Rejected",
        lambda: engine.validate_manifest(mf3),
    )

    engine.validate_manifest(
        mf3,
        allow_historical_generation=True,
    )

    pass_check(
        "Historical Manifest Remains Integrity Verifiable",
        True,
    )

    # ------------------------------------------------------------------------
    test_header(
        40,
        "GENERATION ADVANCE BLOCKED DURING COMPACTION",
    )

    blocker = N39Engine(
        copy.deepcopy(engine.state)
    )

    blocker.prepare_compaction()

    expect_block(
        "Generation Advance During Compaction Rejected",
        blocker.advance_generation,
    )

    # ------------------------------------------------------------------------
    test_header(
        41,
        "NEW-GENERATION TRANSACTION CONTINUITY",
    )

    tx4 = engine.execute_full_transaction()

    pass_check(
        "New Generation Transaction Finalized",
        tx4.phase == PHASE_FINALIZED,
    )

    pass_check(
        "New Transaction Bound To New Generation",
        tx4.generation
        == engine.state.generation,
    )

    pass_check(
        "New Transaction Bound To New Lineage",
        tx4.lineage
        == engine.state.lineage,
    )

    pass_check(
        "New Transaction Bound To New Recovery Epoch",
        tx4.recovery_epoch
        == engine.state.recovery_epoch,
    )

    # ------------------------------------------------------------------------
    test_header(
        42,
        "OLD FINALIZED FENCE REPLAY IN NEW GENERATION",
    )

    replay_tx = engine.create_transaction()
    replay_tx.promotion_id = tx1.promotion_id

    expect_block(
        "Cross-Generation Finalized Promotion Replay Rejected",
        lambda: engine.authorize_transaction(
            replay_tx
        ),
    )

    del engine.state.transactions[
        replay_tx.transaction_id
    ]

    # ------------------------------------------------------------------------
    test_header(
        43,
        "NEW-GENERATION COMPACTION",
    )

    engine.clear_terminal_transaction(
        tx4.transaction_id
    )

    cp4, mf4 = engine.compact()

    pass_check(
        "New Generation Compaction Finalized",
        engine.state.compaction_phase
        == COMPACTION_FINALIZED,
    )

    pass_check(
        "Fourth Checkpoint Uses New Generation",
        cp4.generation
        == engine.state.generation,
    )

    pass_check(
        "Fourth Checkpoint Uses New Lineage",
        cp4.lineage
        == engine.state.lineage,
    )

    pass_check(
        "Fourth Checkpoint Uses New Recovery Epoch",
        cp4.recovery_epoch
        == engine.state.recovery_epoch,
    )

    # ------------------------------------------------------------------------
    test_header(
        44,
        "CROSS-GENERATION CHECKPOINT ANCESTRY",
    )

    pass_check(
        "Fourth Checkpoint References Third Checkpoint",
        cp4.parent_checkpoint_id
        == cp3.checkpoint_id,
    )

    pass_check(
        "Fourth Checkpoint Parent Hash Preserved",
        cp4.parent_checkpoint_hash
        == cp3.calculate_hash(),
    )

    engine.validate_checkpoint_ancestry()

    pass_check(
        "Cross-Generation Checkpoint Ancestry Validates",
        True,
    )

    # ------------------------------------------------------------------------
    test_header(
        45,
        "ALL FINALIZED FENCES IN NEW CHECKPOINT",
    )

    expected_promotions = {
        tx1.promotion_id,
        tx2.promotion_id,
        tx3.promotion_id,
        tx4.promotion_id,
    }

    expected_receipts = {
        tx1.receipt_id,
        tx2.receipt_id,
        tx3.receipt_id,
        tx4.receipt_id,
    }

    pass_check(
        "All Promotion Fences Preserved",
        expected_promotions.issubset(
            set(cp4.finalized_promotion_ids)
        ),
    )

    pass_check(
        "All Receipt Fences Preserved",
        expected_receipts.issubset(
            set(cp4.finalized_receipt_ids)
        ),
    )

    # ------------------------------------------------------------------------
    test_header(
        46,
        "FINAL MULTI-CYCLE RESTART",
    )

    final_snapshot = engine.snapshot()

    final_restart = N39Engine()
    final_restart.restore_snapshot(
        final_snapshot
    )

    pass_check(
        "Final Durable Snapshot Restored",
        final_restart.state.active_checkpoint_id
        == cp4.checkpoint_id,
    )

    pass_check(
        "Final Manifest Restored",
        final_restart.state.active_manifest_id
        == mf4.manifest_id,
    )

    pass_check(
        "All Promotion Fences Survive Final Restart",
        expected_promotions.issubset(
            final_restart.state.finalized_promotion_ids
        ),
    )

    pass_check(
        "All Receipt Fences Survive Final Restart",
        expected_receipts.issubset(
            final_restart.state.finalized_receipt_ids
        ),
    )

    engine = final_restart

    # ------------------------------------------------------------------------
    test_header(
        47,
        "SECOND RESTART OF FINAL STATE",
    )

    second_final_snapshot = engine.snapshot()

    second_restart = N39Engine()
    second_restart.restore_snapshot(
        second_final_snapshot
    )

    pass_check(
        "Final State Survives Second Restart",
        second_restart.state.active_checkpoint_id
        == cp4.checkpoint_id,
    )

    pass_check(
        "Finalized Fences Survive Second Restart",
        expected_promotions.issubset(
            second_restart.state.finalized_promotion_ids
        ),
    )

    engine = second_restart

    # ------------------------------------------------------------------------
    test_header(
        48,
        "GLOBAL WAL SEQUENCE MONOTONICITY",
    )

    pass_check(
        "Global WAL Sequence Never Reset",
        engine.state.global_wal_sequence
        > sequence_before_second_compaction,
    )

    pass_check(
        "Active Checkpoint Sequence Is Monotonic",
        cp4.checkpoint_sequence
        > cp3.checkpoint_sequence
        > cp2.checkpoint_sequence
        > cp1.checkpoint_sequence,
    )

    # ------------------------------------------------------------------------
    test_header(
        49,
        "FINAL WAL INTEGRITY",
    )

    engine.validate_wal()

    pass_check(
        "WAL Records Validate",
        True,
    )

    expected_final_hash = (
        engine.state.wal_records[-1].record_hash
        if engine.state.wal_records
        else ZERO_HASH
    )

    pass_check(
        "WAL Final Hash Matches Journal",
        engine.state.wal_final_hash
        == expected_final_hash,
    )

    # ------------------------------------------------------------------------
    test_header(
        50,
        "COMPLETE DURABLE STATE VALIDATION",
    )

    engine.validate_complete_state()

    pass_check(
        "Complete Durable State Validates",
        True,
    )

    pass_check(
        "Checkpoint Ancestry Remains Valid",
        True,
    )

    # ------------------------------------------------------------------------
    test_header(
        51,
        "SYNTHETIC TRANSPORT EXACTNESS",
    )

    pass_check(
        "All Dispatches Are Synthetic",
        engine.state.total_synthetic_dispatches
        >= 4,
    )

    pass_check(
        "No Network Transmission Occurred",
        engine.state.total_network_transmissions == 0,
    )

    pass_check(
        "Transport Method Exactly POST",
        HTTP_METHOD == "POST",
    )

    pass_check(
        "Transport Path Exactly Leverage Endpoint",
        LEVERAGE_ENDPOINT
        == "/capi/v2/account/leverage",
    )

    # ------------------------------------------------------------------------
    test_header(
        52,
        "FINAL NETWORK WRITE POLICY",
    )

    pass_check(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    pass_check(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    pass_check(
        "All Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    pass_check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    print("", flush=True)
    print("-" * 92, flush=True)
    print(
        f"{UNIT_NAME}: ALL DIAGNOSTICS PASSED",
        flush=True,
    )
    print("-" * 92, flush=True)

    print("NO REAL ORDER WAS SENT", flush=True)
    print("NO DEMO ORDER WAS SENT", flush=True)
    print("NO NETWORK WRITE WAS ATTEMPTED", flush=True)

    print(
        f"{UNIT_NAME}: TEST GROUPS EXECUTED = "
        f"{TEST_GROUPS_EXECUTED}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: PASS ASSERTIONS = "
        f"{PASS_ASSERTIONS}",
        flush=True,
    )


# ============================================================================
# HEALTH SERVER
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/health"):
            body = json.dumps(
                {
                    "status": "ok",
                    "unit": UNIT_NAME,
                    "synthetic_only":
                        SYNTHETIC_TRANSPORT_ONLY,
                    "network_writes":
                        NETWORK_WRITES_ENABLED,
                }
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
        format,
        *args,
    ):
        return


def run_health_server() -> None:

    port = int(
        os.environ.get("PORT", "10000")
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler,
    )

    print(
        f"{UNIT_NAME}: HEALTH SERVER LISTENING "
        f"ON PORT {port}",
        flush=True,
    )

    server.serve_forever()


def heartbeat_loop() -> None:

    counter = 0

    while True:
        counter += 1

        print(
            f"{UNIT_NAME}: HEARTBEAT {counter} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes="
            f"{NETWORK_WRITES_ENABLED}",
            flush=True,
        )

        time.sleep(30)


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:

    run_diagnostics()

    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    health_thread.start()

    heartbeat_loop()


if __name__ == "__main__":
    main()
