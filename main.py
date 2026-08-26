# ============================================================================
# R28 UNIT N.38
# DURABLE WAL COMPACTION + CHECKPOINT HANDOFF + CRASH-WINDOW RECOVERY
# + FINALIZED-FENCE PRESERVATION
#
# COMPLETE SINGLE-FILE COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.38 INCREMENT OVER N.37:
#   - DURABLE WAL COMPACTION CHECKPOINT
#   - COMPACTION MANIFEST
#   - CHECKPOINT/WAL HANDOFF VALIDATION
#   - PRE-COMPACTION CRASH RECOVERY
#   - POST-CHECKPOINT / PRE-WAL-TRUNCATION RECOVERY
#   - POST-WAL-TRUNCATION / PRE-MANIFEST-FINALIZATION RECOVERY
#   - IDEMPOTENT COMPACTION REPLAY
#   - FINALIZED PROMOTION/RECEIPT FENCE PRESERVATION
#   - RECONCILIATION FENCE PRESERVATION
#   - GENERATION/LINEAGE/EPOCH BINDING
#   - CROSS-GENERATION STALE CHECKPOINT REJECTION
#   - CHECKPOINT/MANIFEST/SNAPSHOT TAMPER REJECTION
#   - WAL HASH-CHAIN VALIDATION AFTER COMPACTION
#   - SYNTHETIC TRANSPORT FIREBREAK PRESERVED
# ============================================================================


print("R28 UNIT N.38: MAIN.PY ENTERED", flush=True)

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


print("R28 UNIT N.38: IMPORTS COMPLETE", flush=True)


# ============================================================================
# CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.38"
UNIT_VERSION = "N.38"

SYMBOL = "BTCUSDT"
HTTP_METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TARGET_LEVERAGE = "100"
TARGET_MARGIN_MODE = "ISOLATED"

INTEGRITY_KEY = b"R28-N38-LOCAL-INTEGRITY-KEY"
CERTIFICATE_KEY = b"R28-N38-RECONCILIATION-CERTIFICATE-KEY"
CHECKPOINT_KEY = b"R28-N38-CHECKPOINT-KEY"
MANIFEST_KEY = b"R28-N38-COMPACTION-MANIFEST-KEY"

ZERO_HASH = "0" * 64

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_RECONCILED = "RECONCILED"
PHASE_COMPLETED = "COMPLETED"

COMPACTION_NONE = "NONE"
COMPACTION_PREPARED = "PREPARED"
COMPACTION_CHECKPOINTED = "CHECKPOINTED"
COMPACTION_WAL_REBASED = "WAL_REBASED"
COMPACTION_FINALIZED = "FINALIZED"

HEARTBEAT_SECONDS = 30


print("R28 UNIT N.38: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# BASIC HELPERS
# ============================================================================

class LocalBlock(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalBlock(message)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_hex(key: bytes, value: str) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def deep_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return copy.deepcopy(value)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PromotionTransaction:
    promotion_id: str
    receipt_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    symbol: str
    method: str
    path: str
    payload: Dict[str, Any]
    payload_hash: str

    phase: str = PHASE_PREPARED
    synthetic_dispatch: bool = True
    network_transmitted: bool = False
    reconciliation_certificate_id: Optional[str] = None


@dataclass
class ReconciliationCertificate:
    certificate_id: str
    promotion_id: str
    receipt_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    payload_hash: str
    sequence: int
    signature: str


@dataclass
class WalRecord:
    sequence: int
    record_type: str
    generation: int
    lineage: str
    recovery_epoch: int
    data: Dict[str, Any]
    previous_hash: str
    record_hash: str


@dataclass
class DurableCheckpoint:
    checkpoint_id: str
    generation: int
    lineage: str
    recovery_epoch: int

    compacted_through_sequence: int
    source_wal_final_hash: str

    finalized_promotion_ids: List[str]
    finalized_receipt_ids: List[str]
    reconciled_promotion_ids: List[str]

    active_transaction: Optional[Dict[str, Any]]

    seal: str


@dataclass
class CompactionManifest:
    manifest_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    checkpoint_id: str
    compacted_through_sequence: int

    source_wal_final_hash: str
    rebased_wal_first_sequence: int

    phase: str
    seal: str


@dataclass
class DurableState:
    generation: int = 1
    lineage: str = field(default_factory=lambda: new_id("lineage"))
    recovery_epoch: int = 1

    wal: List[WalRecord] = field(default_factory=list)
    wal_final_hash: str = ZERO_HASH
    next_wal_sequence: int = 1

    active_transaction: Optional[PromotionTransaction] = None

    finalized_promotion_ids: Set[str] = field(default_factory=set)
    finalized_receipt_ids: Set[str] = field(default_factory=set)
    reconciled_promotion_ids: Set[str] = field(default_factory=set)

    certificates: Dict[str, ReconciliationCertificate] = field(
        default_factory=dict
    )

    checkpoint: Optional[DurableCheckpoint] = None
    compaction_manifest: Optional[CompactionManifest] = None

    compaction_epoch: int = 0
    compaction_phase: str = COMPACTION_NONE

    synthetic_dispatch_count: int = 0
    network_write_attempts: int = 0


# ============================================================================
# ENGINE
# ============================================================================

class N38Engine:

    def __init__(self, state: Optional[DurableState] = None):
        self.state = state if state is not None else DurableState()

    # ------------------------------------------------------------------------
    # WAL
    # ------------------------------------------------------------------------

    def _wal_record_material(
        self,
        sequence: int,
        record_type: str,
        generation: int,
        lineage: str,
        recovery_epoch: int,
        data: Dict[str, Any],
        previous_hash: str,
    ) -> str:

        body = {
            "sequence": sequence,
            "record_type": record_type,
            "generation": generation,
            "lineage": lineage,
            "recovery_epoch": recovery_epoch,
            "data": copy.deepcopy(data),
            "previous_hash": previous_hash,
        }

        return canonical_json(body)

    def append_wal(
        self,
        record_type: str,
        data: Dict[str, Any],
    ) -> WalRecord:

        sequence = self.state.next_wal_sequence
        previous_hash = self.state.wal_final_hash

        material = self._wal_record_material(
            sequence=sequence,
            record_type=record_type,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            data=data,
            previous_hash=previous_hash,
        )

        record_hash = sha256_text(material)

        record = WalRecord(
            sequence=sequence,
            record_type=record_type,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            data=copy.deepcopy(data),
            previous_hash=previous_hash,
            record_hash=record_hash,
        )

        self.state.wal.append(record)
        self.state.wal_final_hash = record_hash
        self.state.next_wal_sequence += 1

        return record

    def validate_wal(self) -> None:

        previous_hash = ZERO_HASH
        previous_sequence = 0

        for record in self.state.wal:

            require(
                record.sequence > previous_sequence,
                "WAL sequence is not strictly increasing",
            )

            require(
                record.previous_hash == previous_hash,
                "WAL previous hash mismatch",
            )

            material = self._wal_record_material(
                sequence=record.sequence,
                record_type=record.record_type,
                generation=record.generation,
                lineage=record.lineage,
                recovery_epoch=record.recovery_epoch,
                data=record.data,
                previous_hash=record.previous_hash,
            )

            expected_hash = sha256_text(material)

            require(
                hmac.compare_digest(
                    expected_hash,
                    record.record_hash,
                ),
                "WAL record hash mismatch",
            )

            previous_hash = record.record_hash
            previous_sequence = record.sequence

        expected_final = (
            previous_hash
            if self.state.wal
            else ZERO_HASH
        )

        require(
            self.state.wal_final_hash == expected_final,
            "WAL final hash mismatch",
        )

    # ------------------------------------------------------------------------
    # TRANSACTION
    # ------------------------------------------------------------------------

    def build_payload(self) -> Dict[str, Any]:

        return {
            "symbol": SYMBOL,
            "marginMode": TARGET_MARGIN_MODE,
            "leverage": TARGET_LEVERAGE,
        }

    def prepare_transaction(self) -> PromotionTransaction:

        require(
            self.state.active_transaction is None,
            "pending promotion already exists",
        )

        payload = self.build_payload()
        payload_hash = sha256_text(canonical_json(payload))

        tx = PromotionTransaction(
            promotion_id=new_id("promotion"),
            receipt_id=new_id("receipt"),
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            symbol=SYMBOL,
            method=HTTP_METHOD,
            path=LEVERAGE_ENDPOINT,
            payload=payload,
            payload_hash=payload_hash,
            phase=PHASE_PREPARED,
        )

        self.state.active_transaction = tx

        self.append_wal(
            "PROMOTION_PREPARED",
            {
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
                "payload_hash": tx.payload_hash,
            },
        )

        return tx

    def validate_transaction_binding(
        self,
        tx: PromotionTransaction,
    ) -> None:

        require(
            tx.generation == self.state.generation,
            "promotion transaction generation mismatch",
        )

        require(
            tx.lineage == self.state.lineage,
            "promotion transaction lineage mismatch",
        )

        require(
            tx.recovery_epoch == self.state.recovery_epoch,
            "promotion transaction recovery epoch mismatch",
        )

        require(
            tx.symbol == SYMBOL,
            "promotion transaction symbol mismatch",
        )

        require(
            tx.method == HTTP_METHOD,
            "promotion transaction method mismatch",
        )

        require(
            tx.path == LEVERAGE_ENDPOINT,
            "promotion transaction path mismatch",
        )

        require(
            tx.payload_hash
            == sha256_text(canonical_json(tx.payload)),
            "promotion transaction payload hash mismatch",
        )

    def authorize_transaction(
        self,
        tx: PromotionTransaction,
    ) -> None:

        self.validate_transaction_binding(tx)

        require(
            tx.phase == PHASE_PREPARED,
            "promotion transaction not prepared",
        )

        require(
            tx.promotion_id not in self.state.finalized_promotion_ids,
            "promotion already finalized",
        )

        tx.phase = PHASE_AUTHORIZED

        self.append_wal(
            "PROMOTION_AUTHORIZED",
            {
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
            },
        )

    def commit_transaction(
        self,
        tx: PromotionTransaction,
    ) -> None:

        self.validate_transaction_binding(tx)

        require(
            tx.phase == PHASE_AUTHORIZED,
            "promotion transaction not authorized",
        )

        tx.phase = PHASE_COMMITTED

        self.append_wal(
            "PROMOTION_COMMITTED",
            {
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
                "payload_hash": tx.payload_hash,
            },
        )

    def synthetic_dispatch(
        self,
        tx: PromotionTransaction,
    ) -> None:

        self.validate_transaction_binding(tx)

        require(
            SYNTHETIC_TRANSPORT_ONLY,
            "synthetic transport disabled",
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
            tx.phase == PHASE_COMMITTED,
            "promotion transaction not committed",
        )

        require(
            tx.receipt_id not in self.state.finalized_receipt_ids,
            "promotion receipt already committed",
        )

        self.state.synthetic_dispatch_count += 1

        tx.synthetic_dispatch = True
        tx.network_transmitted = False
        tx.phase = PHASE_DISPATCHED

        self.append_wal(
            "SYNTHETIC_DISPATCH",
            {
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
                "method": tx.method,
                "path": tx.path,
                "payload_hash": tx.payload_hash,
                "network_transmitted": False,
            },
        )

    # ------------------------------------------------------------------------
    # RECONCILIATION CERTIFICATE
    # ------------------------------------------------------------------------

    def _certificate_material(
        self,
        certificate_id: str,
        promotion_id: str,
        receipt_id: str,
        generation: int,
        lineage: str,
        recovery_epoch: int,
        payload_hash: str,
        sequence: int,
    ) -> str:

        return canonical_json(
            {
                "certificate_id": certificate_id,
                "promotion_id": promotion_id,
                "receipt_id": receipt_id,
                "generation": generation,
                "lineage": lineage,
                "recovery_epoch": recovery_epoch,
                "payload_hash": payload_hash,
                "sequence": sequence,
            }
        )

    def create_reconciliation_certificate(
        self,
        tx: PromotionTransaction,
    ) -> ReconciliationCertificate:

        self.validate_transaction_binding(tx)

        require(
            tx.phase == PHASE_DISPATCHED,
            "transaction not dispatched",
        )

        require(
            tx.promotion_id
            not in self.state.reconciled_promotion_ids,
            "promotion transaction already reconciled",
        )

        certificate_id = new_id("reconciliation-cert")
        sequence = self.state.next_wal_sequence

        material = self._certificate_material(
            certificate_id=certificate_id,
            promotion_id=tx.promotion_id,
            receipt_id=tx.receipt_id,
            generation=tx.generation,
            lineage=tx.lineage,
            recovery_epoch=tx.recovery_epoch,
            payload_hash=tx.payload_hash,
            sequence=sequence,
        )

        signature = hmac_hex(
            CERTIFICATE_KEY,
            material,
        )

        cert = ReconciliationCertificate(
            certificate_id=certificate_id,
            promotion_id=tx.promotion_id,
            receipt_id=tx.receipt_id,
            generation=tx.generation,
            lineage=tx.lineage,
            recovery_epoch=tx.recovery_epoch,
            payload_hash=tx.payload_hash,
            sequence=sequence,
            signature=signature,
        )

        self.state.certificates[cert.certificate_id] = cert
        tx.reconciliation_certificate_id = cert.certificate_id

        self.append_wal(
            "RECONCILIATION_CERTIFICATE_CREATED",
            {
                "certificate_id": cert.certificate_id,
                "promotion_id": cert.promotion_id,
                "receipt_id": cert.receipt_id,
            },
        )

        return cert

    def validate_certificate(
        self,
        cert: ReconciliationCertificate,
    ) -> None:

        require(
            cert.generation == self.state.generation,
            "reconciliation certificate generation mismatch",
        )

        require(
            cert.lineage == self.state.lineage,
            "reconciliation certificate lineage mismatch",
        )

        require(
            cert.recovery_epoch == self.state.recovery_epoch,
            "reconciliation certificate recovery epoch mismatch",
        )

        material = self._certificate_material(
            certificate_id=cert.certificate_id,
            promotion_id=cert.promotion_id,
            receipt_id=cert.receipt_id,
            generation=cert.generation,
            lineage=cert.lineage,
            recovery_epoch=cert.recovery_epoch,
            payload_hash=cert.payload_hash,
            sequence=cert.sequence,
        )

        expected_signature = hmac_hex(
            CERTIFICATE_KEY,
            material,
        )

        require(
            hmac.compare_digest(
                expected_signature,
                cert.signature,
            ),
            "reconciliation certificate signature mismatch",
        )

    def reconcile(
        self,
        tx: PromotionTransaction,
        cert: ReconciliationCertificate,
    ) -> None:

        self.validate_transaction_binding(tx)
        self.validate_certificate(cert)

        require(
            tx.phase == PHASE_DISPATCHED,
            "transaction not dispatched",
        )

        require(
            cert.promotion_id == tx.promotion_id,
            "reconciliation certificate promotion mismatch",
        )

        require(
            cert.receipt_id == tx.receipt_id,
            "reconciliation certificate receipt mismatch",
        )

        require(
            cert.payload_hash == tx.payload_hash,
            "reconciliation certificate payload hash mismatch",
        )

        require(
            tx.promotion_id
            not in self.state.reconciled_promotion_ids,
            "promotion transaction already reconciled",
        )

        self.state.reconciled_promotion_ids.add(
            tx.promotion_id
        )

        tx.phase = PHASE_RECONCILED

        self.append_wal(
            "PROMOTION_RECONCILED",
            {
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
                "certificate_id": cert.certificate_id,
            },
        )

    def finalize(
        self,
        tx: PromotionTransaction,
    ) -> None:

        require(
            tx.phase == PHASE_RECONCILED,
            "transaction not reconciled",
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

        self.state.finalized_promotion_ids.add(
            tx.promotion_id
        )

        self.state.finalized_receipt_ids.add(
            tx.receipt_id
        )

        tx.phase = PHASE_COMPLETED

        self.append_wal(
            "PROMOTION_FINALIZED",
            {
                "promotion_id": tx.promotion_id,
                "receipt_id": tx.receipt_id,
            },
        )

    def clear_terminal_transaction(self) -> None:

        tx = self.state.active_transaction

        require(
            tx is not None,
            "no active promotion transaction",
        )

        require(
            tx.phase == PHASE_COMPLETED,
            "promotion transaction is not terminal",
        )

        promotion_id = tx.promotion_id
        receipt_id = tx.receipt_id

        self.state.active_transaction = None

        self.append_wal(
            "TERMINAL_TRANSACTION_CLEARED",
            {
                "promotion_id": promotion_id,
                "receipt_id": receipt_id,
            },
        )

    # ------------------------------------------------------------------------
    # CHECKPOINT
    # ------------------------------------------------------------------------

    def _checkpoint_body(
        self,
        checkpoint_id: str,
        generation: int,
        lineage: str,
        recovery_epoch: int,
        compacted_through_sequence: int,
        source_wal_final_hash: str,
        finalized_promotion_ids: List[str],
        finalized_receipt_ids: List[str],
        reconciled_promotion_ids: List[str],
        active_transaction: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:

        return {
            "checkpoint_id": checkpoint_id,
            "generation": generation,
            "lineage": lineage,
            "recovery_epoch": recovery_epoch,
            "compacted_through_sequence":
                compacted_through_sequence,
            "source_wal_final_hash":
                source_wal_final_hash,
            "finalized_promotion_ids":
                sorted(finalized_promotion_ids),
            "finalized_receipt_ids":
                sorted(finalized_receipt_ids),
            "reconciled_promotion_ids":
                sorted(reconciled_promotion_ids),
            "active_transaction":
                copy.deepcopy(active_transaction),
        }

    def create_checkpoint(self) -> DurableCheckpoint:

        self.validate_wal()

        require(
            self.state.wal,
            "cannot checkpoint empty WAL",
        )

        checkpoint_id = new_id("checkpoint")

        compacted_through_sequence = (
            self.state.wal[-1].sequence
        )

        source_wal_final_hash = (
            self.state.wal_final_hash
        )

        active_tx_dict = (
            asdict(self.state.active_transaction)
            if self.state.active_transaction is not None
            else None
        )

        body = self._checkpoint_body(
            checkpoint_id=checkpoint_id,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            compacted_through_sequence=
                compacted_through_sequence,
            source_wal_final_hash=
                source_wal_final_hash,
            finalized_promotion_ids=list(
                self.state.finalized_promotion_ids
            ),
            finalized_receipt_ids=list(
                self.state.finalized_receipt_ids
            ),
            reconciled_promotion_ids=list(
                self.state.reconciled_promotion_ids
            ),
            active_transaction=active_tx_dict,
        )

        seal = hmac_hex(
            CHECKPOINT_KEY,
            canonical_json(body),
        )

        checkpoint = DurableCheckpoint(
            checkpoint_id=checkpoint_id,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            compacted_through_sequence=
                compacted_through_sequence,
            source_wal_final_hash=
                source_wal_final_hash,
            finalized_promotion_ids=sorted(
                self.state.finalized_promotion_ids
            ),
            finalized_receipt_ids=sorted(
                self.state.finalized_receipt_ids
            ),
            reconciled_promotion_ids=sorted(
                self.state.reconciled_promotion_ids
            ),
            active_transaction=active_tx_dict,
            seal=seal,
        )

        return checkpoint

    def validate_checkpoint(
        self,
        checkpoint: DurableCheckpoint,
        require_current_generation: bool = True,
    ) -> None:

        if require_current_generation:

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

        body = self._checkpoint_body(
            checkpoint_id=checkpoint.checkpoint_id,
            generation=checkpoint.generation,
            lineage=checkpoint.lineage,
            recovery_epoch=checkpoint.recovery_epoch,
            compacted_through_sequence=
                checkpoint.compacted_through_sequence,
            source_wal_final_hash=
                checkpoint.source_wal_final_hash,
            finalized_promotion_ids=
                checkpoint.finalized_promotion_ids,
            finalized_receipt_ids=
                checkpoint.finalized_receipt_ids,
            reconciled_promotion_ids=
                checkpoint.reconciled_promotion_ids,
            active_transaction=
                checkpoint.active_transaction,
        )

        expected_seal = hmac_hex(
            CHECKPOINT_KEY,
            canonical_json(body),
        )

        require(
            hmac.compare_digest(
                expected_seal,
                checkpoint.seal,
            ),
            "checkpoint integrity seal mismatch",
        )

    # ------------------------------------------------------------------------
    # COMPACTION MANIFEST
    # ------------------------------------------------------------------------

    def _manifest_body(
        self,
        manifest_id: str,
        generation: int,
        lineage: str,
        recovery_epoch: int,
        checkpoint_id: str,
        compacted_through_sequence: int,
        source_wal_final_hash: str,
        rebased_wal_first_sequence: int,
        phase: str,
    ) -> Dict[str, Any]:

        return {
            "manifest_id": manifest_id,
            "generation": generation,
            "lineage": lineage,
            "recovery_epoch": recovery_epoch,
            "checkpoint_id": checkpoint_id,
            "compacted_through_sequence":
                compacted_through_sequence,
            "source_wal_final_hash":
                source_wal_final_hash,
            "rebased_wal_first_sequence":
                rebased_wal_first_sequence,
            "phase": phase,
        }

    def make_manifest(
        self,
        checkpoint: DurableCheckpoint,
        phase: str,
    ) -> CompactionManifest:

        manifest_id = new_id("manifest")

        body = self._manifest_body(
            manifest_id=manifest_id,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            checkpoint_id=checkpoint.checkpoint_id,
            compacted_through_sequence=
                checkpoint.compacted_through_sequence,
            source_wal_final_hash=
                checkpoint.source_wal_final_hash,
            rebased_wal_first_sequence=
                checkpoint.compacted_through_sequence + 1,
            phase=phase,
        )

        seal = hmac_hex(
            MANIFEST_KEY,
            canonical_json(body),
        )

        return CompactionManifest(
            manifest_id=manifest_id,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            checkpoint_id=checkpoint.checkpoint_id,
            compacted_through_sequence=
                checkpoint.compacted_through_sequence,
            source_wal_final_hash=
                checkpoint.source_wal_final_hash,
            rebased_wal_first_sequence=
                checkpoint.compacted_through_sequence + 1,
            phase=phase,
            seal=seal,
        )

    def reseal_manifest(
        self,
        manifest: CompactionManifest,
    ) -> None:

        body = self._manifest_body(
            manifest_id=manifest.manifest_id,
            generation=manifest.generation,
            lineage=manifest.lineage,
            recovery_epoch=manifest.recovery_epoch,
            checkpoint_id=manifest.checkpoint_id,
            compacted_through_sequence=
                manifest.compacted_through_sequence,
            source_wal_final_hash=
                manifest.source_wal_final_hash,
            rebased_wal_first_sequence=
                manifest.rebased_wal_first_sequence,
            phase=manifest.phase,
        )

        manifest.seal = hmac_hex(
            MANIFEST_KEY,
            canonical_json(body),
        )

    def validate_manifest(
        self,
        manifest: CompactionManifest,
        checkpoint: DurableCheckpoint,
    ) -> None:

        require(
            manifest.generation
            == checkpoint.generation,
            "manifest/checkpoint generation mismatch",
        )

        require(
            manifest.lineage
            == checkpoint.lineage,
            "manifest/checkpoint lineage mismatch",
        )

        require(
            manifest.recovery_epoch
            == checkpoint.recovery_epoch,
            "manifest/checkpoint recovery epoch mismatch",
        )

        require(
            manifest.checkpoint_id
            == checkpoint.checkpoint_id,
            "manifest checkpoint mismatch",
        )

        require(
            manifest.compacted_through_sequence
            == checkpoint.compacted_through_sequence,
            "manifest checkpoint sequence mismatch",
        )

        require(
            manifest.source_wal_final_hash
            == checkpoint.source_wal_final_hash,
            "manifest checkpoint WAL hash mismatch",
        )

        require(
            manifest.rebased_wal_first_sequence
            == checkpoint.compacted_through_sequence + 1,
            "manifest rebased WAL sequence mismatch",
        )

        body = self._manifest_body(
            manifest_id=manifest.manifest_id,
            generation=manifest.generation,
            lineage=manifest.lineage,
            recovery_epoch=manifest.recovery_epoch,
            checkpoint_id=manifest.checkpoint_id,
            compacted_through_sequence=
                manifest.compacted_through_sequence,
            source_wal_final_hash=
                manifest.source_wal_final_hash,
            rebased_wal_first_sequence=
                manifest.rebased_wal_first_sequence,
            phase=manifest.phase,
        )

        expected_seal = hmac_hex(
            MANIFEST_KEY,
            canonical_json(body),
        )

        require(
            hmac.compare_digest(
                expected_seal,
                manifest.seal,
            ),
            "compaction manifest integrity seal mismatch",
        )

    # ------------------------------------------------------------------------
    # N.38 WAL COMPACTION
    # ------------------------------------------------------------------------

    def begin_compaction(self) -> None:

        require(
            self.state.compaction_phase
            in (
                COMPACTION_NONE,
                COMPACTION_FINALIZED,
            ),
            "compaction already in progress",
        )

        self.validate_wal()

        self.state.compaction_epoch += 1
        self.state.compaction_phase = COMPACTION_PREPARED

    def persist_compaction_checkpoint(self) -> DurableCheckpoint:

        require(
            self.state.compaction_phase
            == COMPACTION_PREPARED,
            "compaction not prepared",
        )

        checkpoint = self.create_checkpoint()

        manifest = self.make_manifest(
            checkpoint,
            COMPACTION_CHECKPOINTED,
        )

        self.state.checkpoint = checkpoint
        self.state.compaction_manifest = manifest
        self.state.compaction_phase = COMPACTION_CHECKPOINTED

        return checkpoint

    def rebase_wal_after_checkpoint(self) -> None:

        require(
            self.state.compaction_phase
            == COMPACTION_CHECKPOINTED,
            "checkpoint not committed",
        )

        checkpoint = self.state.checkpoint
        manifest = self.state.compaction_manifest

        require(
            checkpoint is not None,
            "compaction checkpoint missing",
        )

        require(
            manifest is not None,
            "compaction manifest missing",
        )

        self.validate_checkpoint(checkpoint)
        self.validate_manifest(
            manifest,
            checkpoint,
        )

        self.state.wal = []
        self.state.wal_final_hash = ZERO_HASH

        self.state.next_wal_sequence = (
            checkpoint.compacted_through_sequence + 1
        )

        manifest.phase = COMPACTION_WAL_REBASED
        self.reseal_manifest(manifest)

        self.state.compaction_phase = (
            COMPACTION_WAL_REBASED
        )

    def finalize_compaction(self) -> None:

        require(
            self.state.compaction_phase
            == COMPACTION_WAL_REBASED,
            "WAL not rebased",
        )

        checkpoint = self.state.checkpoint
        manifest = self.state.compaction_manifest

        require(
            checkpoint is not None,
            "compaction checkpoint missing",
        )

        require(
            manifest is not None,
            "compaction manifest missing",
        )

        self.validate_checkpoint(checkpoint)
        self.validate_manifest(
            manifest,
            checkpoint,
        )

        manifest.phase = COMPACTION_FINALIZED
        self.reseal_manifest(manifest)

        self.state.compaction_phase = COMPACTION_FINALIZED

        self.append_wal(
            "COMPACTION_FINALIZED",
            {
                "checkpoint_id":
                    checkpoint.checkpoint_id,
                "compacted_through_sequence":
                    checkpoint.compacted_through_sequence,
                "compaction_epoch":
                    self.state.compaction_epoch,
            },
        )

    def compact(self) -> None:

        self.begin_compaction()
        self.persist_compaction_checkpoint()
        self.rebase_wal_after_checkpoint()
        self.finalize_compaction()

    # ------------------------------------------------------------------------
    # CRASH RECOVERY
    # ------------------------------------------------------------------------

    def recover_compaction(self) -> None:

        phase = self.state.compaction_phase

        if phase == COMPACTION_NONE:
            return

        if phase == COMPACTION_FINALIZED:
            self.validate_durable_state()
            return

        if phase == COMPACTION_PREPARED:
            # No durable checkpoint exists yet.
            # Original WAL remains authoritative.
            self.state.compaction_phase = COMPACTION_NONE
            self.state.checkpoint = None
            self.state.compaction_manifest = None
            self.validate_wal()
            return

        checkpoint = self.state.checkpoint
        manifest = self.state.compaction_manifest

        require(
            checkpoint is not None,
            "compaction checkpoint missing",
        )

        require(
            manifest is not None,
            "compaction manifest missing",
        )

        self.validate_checkpoint(checkpoint)
        self.validate_manifest(
            manifest,
            checkpoint,
        )

        if phase == COMPACTION_CHECKPOINTED:

            # Checkpoint exists while original WAL still exists.
            # Verify the original WAL is still exactly what
            # the checkpoint claims before truncating it.

            self.validate_wal()

            require(
                self.state.wal_final_hash
                == checkpoint.source_wal_final_hash,
                "checkpoint source WAL final hash mismatch",
            )

            require(
                self.state.wal,
                "checkpoint source WAL missing",
            )

            require(
                self.state.wal[-1].sequence
                == checkpoint.compacted_through_sequence,
                "checkpoint source WAL sequence mismatch",
            )

            self.rebase_wal_after_checkpoint()
            self.finalize_compaction()
            return

        if phase == COMPACTION_WAL_REBASED:

            require(
                self.state.wal_final_hash == ZERO_HASH,
                "rebased WAL unexpectedly has legacy hash",
            )

            require(
                len(self.state.wal) == 0,
                "rebased WAL unexpectedly contains records",
            )

            require(
                self.state.next_wal_sequence
                == checkpoint.compacted_through_sequence + 1,
                "rebased WAL sequence mismatch",
            )

            self.finalize_compaction()
            return

        raise LocalBlock(
            "unknown compaction recovery phase"
        )

    # ------------------------------------------------------------------------
    # SNAPSHOT
    # ------------------------------------------------------------------------

    def snapshot_payload(self) -> Dict[str, Any]:

        return {
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch":
                self.state.recovery_epoch,

            "wal": [
                asdict(record)
                for record in self.state.wal
            ],

            "wal_final_hash":
                self.state.wal_final_hash,

            "next_wal_sequence":
                self.state.next_wal_sequence,

            "active_transaction": (
                asdict(self.state.active_transaction)
                if self.state.active_transaction
                else None
            ),

            "finalized_promotion_ids": sorted(
                self.state.finalized_promotion_ids
            ),

            "finalized_receipt_ids": sorted(
                self.state.finalized_receipt_ids
            ),

            "reconciled_promotion_ids": sorted(
                self.state.reconciled_promotion_ids
            ),

            "certificates": {
                key: asdict(value)
                for key, value
                in self.state.certificates.items()
            },

            "checkpoint": (
                asdict(self.state.checkpoint)
                if self.state.checkpoint
                else None
            ),

            "compaction_manifest": (
                asdict(self.state.compaction_manifest)
                if self.state.compaction_manifest
                else None
            ),

            "compaction_epoch":
                self.state.compaction_epoch,

            "compaction_phase":
                self.state.compaction_phase,

            "synthetic_dispatch_count":
                self.state.synthetic_dispatch_count,

            "network_write_attempts":
                self.state.network_write_attempts,
        }

    def serialize_snapshot(self) -> str:

        payload = self.snapshot_payload()

        seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(payload),
        )

        envelope = {
            "unit": UNIT_VERSION,
            "payload": payload,
            "seal": seal,
        }

        return canonical_json(envelope)

    @classmethod
    def restore_snapshot(
        cls,
        serialized: str,
    ) -> "N38Engine":

        envelope = json.loads(serialized)

        require(
            envelope.get("unit") == UNIT_VERSION,
            "snapshot unit mismatch",
        )

        payload = envelope["payload"]
        seal = envelope["seal"]

        expected_seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(payload),
        )

        require(
            hmac.compare_digest(
                expected_seal,
                seal,
            ),
            "snapshot integrity seal mismatch",
        )

        state = DurableState(
            generation=payload["generation"],
            lineage=payload["lineage"],
            recovery_epoch=
                payload["recovery_epoch"],
        )

        state.wal = [
            WalRecord(**record)
            for record in payload["wal"]
        ]

        state.wal_final_hash = (
            payload["wal_final_hash"]
        )

        state.next_wal_sequence = (
            payload["next_wal_sequence"]
        )

        if payload["active_transaction"] is not None:
            state.active_transaction = (
                PromotionTransaction(
                    **payload["active_transaction"]
                )
            )

        state.finalized_promotion_ids = set(
            payload["finalized_promotion_ids"]
        )

        state.finalized_receipt_ids = set(
            payload["finalized_receipt_ids"]
        )

        state.reconciled_promotion_ids = set(
            payload["reconciled_promotion_ids"]
        )

        state.certificates = {
            key: ReconciliationCertificate(**value)
            for key, value
            in payload["certificates"].items()
        }

        if payload["checkpoint"] is not None:
            state.checkpoint = DurableCheckpoint(
                **payload["checkpoint"]
            )

        if payload["compaction_manifest"] is not None:
            state.compaction_manifest = (
                CompactionManifest(
                    **payload["compaction_manifest"]
                )
            )

        state.compaction_epoch = (
            payload["compaction_epoch"]
        )

        state.compaction_phase = (
            payload["compaction_phase"]
        )

        state.synthetic_dispatch_count = (
            payload["synthetic_dispatch_count"]
        )

        state.network_write_attempts = (
            payload["network_write_attempts"]
        )

        engine = cls(state)
        engine.validate_durable_state()

        return engine

    # ------------------------------------------------------------------------
    # DURABLE STATE VALIDATION
    # ------------------------------------------------------------------------

    def validate_durable_state(self) -> None:

        self.validate_wal()

        require(
            self.state.generation >= 1,
            "invalid generation",
        )

        require(
            self.state.recovery_epoch >= 1,
            "invalid recovery epoch",
        )

        require(
            bool(self.state.lineage),
            "missing lineage",
        )

        require(
            self.state.network_write_attempts == 0,
            "network write attempt detected",
        )

        if self.state.active_transaction is not None:

            tx = self.state.active_transaction

            self.validate_transaction_binding(tx)

            require(
                tx.synthetic_dispatch,
                "non-synthetic transaction detected",
            )

            require(
                not tx.network_transmitted,
                "network transmission detected",
            )

        for cert in self.state.certificates.values():

            if (
                cert.generation
                == self.state.generation
                and cert.lineage
                == self.state.lineage
                and cert.recovery_epoch
                == self.state.recovery_epoch
            ):
                self.validate_certificate(cert)

        if self.state.checkpoint is not None:

            self.validate_checkpoint(
                self.state.checkpoint,
                require_current_generation=(
                    self.state.checkpoint.generation
                    == self.state.generation
                ),
            )

        if self.state.compaction_manifest is not None:

            require(
                self.state.checkpoint is not None,
                "manifest exists without checkpoint",
            )

            self.validate_manifest(
                self.state.compaction_manifest,
                self.state.checkpoint,
            )

    # ------------------------------------------------------------------------
    # GENERATION ADVANCE
    # ------------------------------------------------------------------------

    def advance_generation(self) -> None:

        require(
            self.state.active_transaction is None,
            "cannot advance generation with pending promotion",
        )

        require(
            self.state.compaction_phase
            in (
                COMPACTION_NONE,
                COMPACTION_FINALIZED,
            ),
            "cannot advance generation during compaction",
        )

        old_generation = self.state.generation
        old_epoch = self.state.recovery_epoch
        old_lineage = self.state.lineage

        self.state.generation += 1
        self.state.recovery_epoch += 1
        self.state.lineage = new_id("lineage")

        require(
            self.state.generation
            > old_generation,
            "generation did not advance",
        )

        require(
            self.state.recovery_epoch
            > old_epoch,
            "recovery epoch did not advance",
        )

        require(
            self.state.lineage != old_lineage,
            "lineage did not change",
        )

        self.append_wal(
            "GENERATION_ADVANCED",
            {
                "generation":
                    self.state.generation,
                "recovery_epoch":
                    self.state.recovery_epoch,
                "lineage":
                    self.state.lineage,
            },
        )


print("R28 UNIT N.38: ENGINE DEFINITIONS LOADED", flush=True)


# ============================================================================
# TEST HARNESS
# ============================================================================

TEST_NUMBER = 0
PASS_COUNT = 0


def divider() -> None:
    print("-" * 92, flush=True)


def test_header(name: str) -> None:
    global TEST_NUMBER

    TEST_NUMBER += 1

    divider()
    print(
        f"{UNIT_NAME} TEST {TEST_NUMBER}: {name}",
        flush=True,
    )
    divider()


def passed(label: str) -> None:
    global PASS_COUNT

    PASS_COUNT += 1

    print(
        f"{label:<82} ✅ PASS",
        flush=True,
    )


def local_block(label: str, fn) -> None:

    try:
        fn()

    except LocalBlock as exc:

        print(
            f"{UNIT_NAME} LOCAL BLOCK:",
            flush=True,
        )
        print(
            f"  {exc}",
            flush=True,
        )

        passed(label)
        return

    raise AssertionError(
        f"Expected LocalBlock: {label}"
    )


def make_completed_engine() -> Tuple[
    N38Engine,
    PromotionTransaction,
    ReconciliationCertificate,
]:

    engine = N38Engine()

    tx = engine.prepare_transaction()
    engine.authorize_transaction(tx)
    engine.commit_transaction(tx)
    engine.synthetic_dispatch(tx)

    cert = engine.create_reconciliation_certificate(tx)

    engine.reconcile(
        tx,
        cert,
    )

    engine.finalize(tx)

    return engine, tx, cert


# ============================================================================
# R28 UNIT N.38 DIAGNOSTICS
# ============================================================================

def run_diagnostics() -> None:

    global TEST_NUMBER
    global PASS_COUNT

    TEST_NUMBER = 0
    PASS_COUNT = 0

    print()
    divider()
    print(
        f"{UNIT_NAME}: DURABLE WAL COMPACTION "
        f"+ CHECKPOINT HANDOFF",
        flush=True,
    )
    divider()
    print()

    # ------------------------------------------------------------------------
    # TEST 1
    # ------------------------------------------------------------------------

    test_header("INITIAL STATE")

    engine = N38Engine()

    require(
        engine.state.generation == 1,
        "initial generation mismatch",
    )
    passed("Initial Generation Is One")

    require(
        engine.state.recovery_epoch == 1,
        "initial recovery epoch mismatch",
    )
    passed("Initial Recovery Epoch Is One")

    require(
        engine.state.wal_final_hash == ZERO_HASH,
        "initial WAL hash mismatch",
    )
    passed("Initial WAL Final Hash Is Zero")

    # ------------------------------------------------------------------------
    # TEST 2
    # ------------------------------------------------------------------------

    test_header("PROMOTION PREPARATION")

    tx = engine.prepare_transaction()

    require(
        tx.phase == PHASE_PREPARED,
        "transaction not prepared",
    )
    passed("Promotion Transaction Prepared")

    require(
        len(engine.state.wal) == 1,
        "prepare WAL record missing",
    )
    passed("Preparation Recorded In WAL")

    # ------------------------------------------------------------------------
    # TEST 3
    # ------------------------------------------------------------------------

    test_header("AUTHORIZATION")

    engine.authorize_transaction(tx)

    require(
        tx.phase == PHASE_AUTHORIZED,
        "transaction not authorized",
    )
    passed("Promotion Transaction Authorized")

    # ------------------------------------------------------------------------
    # TEST 4
    # ------------------------------------------------------------------------

    test_header("DURABLE COMMIT")

    engine.commit_transaction(tx)

    require(
        tx.phase == PHASE_COMMITTED,
        "transaction not committed",
    )
    passed("Promotion Transaction Committed")

    # ------------------------------------------------------------------------
    # TEST 5
    # ------------------------------------------------------------------------

    test_header("SYNTHETIC DISPATCH")

    engine.synthetic_dispatch(tx)

    require(
        tx.phase == PHASE_DISPATCHED,
        "transaction not dispatched",
    )
    passed("Synthetic Dispatch Completed")

    require(
        not tx.network_transmitted,
        "network transmission occurred",
    )
    passed("Synthetic Dispatch Performed No Network Transmission")

    # ------------------------------------------------------------------------
    # TEST 6
    # ------------------------------------------------------------------------

    test_header("RECONCILIATION CERTIFICATE")

    cert = engine.create_reconciliation_certificate(tx)

    engine.validate_certificate(cert)

    passed("Reconciliation Certificate Validates")

    # ------------------------------------------------------------------------
    # TEST 7
    # ------------------------------------------------------------------------

    test_header("TRANSACTION RECONCILIATION")

    engine.reconcile(tx, cert)

    require(
        tx.phase == PHASE_RECONCILED,
        "transaction not reconciled",
    )
    passed("Promotion Transaction Reconciled")

    # ------------------------------------------------------------------------
    # TEST 8
    # ------------------------------------------------------------------------

    test_header("FINALIZATION")

    engine.finalize(tx)

    require(
        tx.phase == PHASE_COMPLETED,
        "transaction not completed",
    )
    passed("Promotion Transaction Finalized")

    require(
        tx.promotion_id
        in engine.state.finalized_promotion_ids,
        "promotion fence missing",
    )
    passed("Finalized Promotion Fence Established")

    require(
        tx.receipt_id
        in engine.state.finalized_receipt_ids,
        "receipt fence missing",
    )
    passed("Finalized Receipt Fence Established")

    # ------------------------------------------------------------------------
    # TEST 9
    # ------------------------------------------------------------------------

    test_header("TERMINAL TRANSACTION CLEAR")

    promotion_id = tx.promotion_id
    receipt_id = tx.receipt_id

    engine.clear_terminal_transaction()

    require(
        engine.state.active_transaction is None,
        "terminal transaction not cleared",
    )
    passed("Terminal Transaction Cleared")

    # ------------------------------------------------------------------------
    # TEST 10
    # ------------------------------------------------------------------------

    test_header("FINALIZED FENCES SURVIVE CLEAR")

    require(
        promotion_id
        in engine.state.finalized_promotion_ids,
        "promotion fence lost",
    )
    passed("Finalized Promotion Fence Preserved")

    require(
        receipt_id
        in engine.state.finalized_receipt_ids,
        "receipt fence lost",
    )
    passed("Finalized Receipt Fence Preserved")

    # ------------------------------------------------------------------------
    # TEST 11
    # ------------------------------------------------------------------------

    test_header("PRE-COMPACTION WAL VALIDATION")

    engine.validate_wal()

    passed("Pre-Compaction WAL Records Validate")

    require(
        engine.state.wal_final_hash
        == engine.state.wal[-1].record_hash,
        "WAL final hash mismatch",
    )
    passed("Pre-Compaction WAL Final Hash Matches Journal")

    # ------------------------------------------------------------------------
    # TEST 12
    # ------------------------------------------------------------------------

    test_header("COMPACTION PREPARATION")

    original_wal_length = len(engine.state.wal)
    original_wal_hash = engine.state.wal_final_hash

    engine.begin_compaction()

    require(
        engine.state.compaction_phase
        == COMPACTION_PREPARED,
        "compaction not prepared",
    )
    passed("Compaction Prepared")

    require(
        len(engine.state.wal)
        == original_wal_length,
        "WAL changed during preparation",
    )
    passed("Original WAL Preserved Before Checkpoint")

    # ------------------------------------------------------------------------
    # TEST 13
    # ------------------------------------------------------------------------

    test_header("DURABLE COMPACTION CHECKPOINT")

    checkpoint = engine.persist_compaction_checkpoint()

    engine.validate_checkpoint(checkpoint)

    passed("Durable Compaction Checkpoint Validates")

    require(
        checkpoint.source_wal_final_hash
        == original_wal_hash,
        "checkpoint source WAL hash mismatch",
    )
    passed("Checkpoint Bound To Source WAL Final Hash")

    # ------------------------------------------------------------------------
    # TEST 14
    # ------------------------------------------------------------------------

    test_header("COMPACTION MANIFEST")

    manifest = engine.state.compaction_manifest

    require(
        manifest is not None,
        "compaction manifest missing",
    )

    engine.validate_manifest(
        manifest,
        checkpoint,
    )

    passed("Compaction Manifest Validates")

    require(
        manifest.checkpoint_id
        == checkpoint.checkpoint_id,
        "manifest checkpoint mismatch",
    )
    passed("Manifest Bound To Exact Checkpoint")

    # ------------------------------------------------------------------------
    # TEST 15
    # ------------------------------------------------------------------------

    test_header("CHECKPOINT FINALIZED-FENCE CONTENT")

    require(
        promotion_id
        in checkpoint.finalized_promotion_ids,
        "promotion fence missing from checkpoint",
    )
    passed("Checkpoint Contains Finalized Promotion Fence")

    require(
        receipt_id
        in checkpoint.finalized_receipt_ids,
        "receipt fence missing from checkpoint",
    )
    passed("Checkpoint Contains Finalized Receipt Fence")

    require(
        promotion_id
        in checkpoint.reconciled_promotion_ids,
        "reconciliation fence missing from checkpoint",
    )
    passed("Checkpoint Contains Reconciliation Fence")

    # ------------------------------------------------------------------------
    # TEST 16
    # ------------------------------------------------------------------------

    test_header("WAL REBASE")

    engine.rebase_wal_after_checkpoint()

    require(
        len(engine.state.wal) == 0,
        "old WAL not removed",
    )
    passed("Legacy WAL Removed After Checkpoint")

    require(
        engine.state.wal_final_hash == ZERO_HASH,
        "rebased WAL hash not reset",
    )
    passed("Rebased WAL Hash Reset")

    require(
        engine.state.next_wal_sequence
        == checkpoint.compacted_through_sequence + 1,
        "WAL sequence continuity lost",
    )
    passed("WAL Sequence Continuity Preserved")

    # ------------------------------------------------------------------------
    # TEST 17
    # ------------------------------------------------------------------------

    test_header("COMPACTION FINALIZATION")

    engine.finalize_compaction()

    require(
        engine.state.compaction_phase
        == COMPACTION_FINALIZED,
        "compaction not finalized",
    )
    passed("Compaction Finalized")

    require(
        len(engine.state.wal) == 1,
        "post-compaction WAL marker missing",
    )
    passed("New WAL Contains Compaction Finalization Marker")

    # ------------------------------------------------------------------------
    # TEST 18
    # ------------------------------------------------------------------------

    test_header("POST-COMPACTION WAL VALIDATION")

    engine.validate_wal()

    passed("Post-Compaction WAL Records Validate")

    require(
        engine.state.wal_final_hash
        == engine.state.wal[-1].record_hash,
        "post-compaction WAL final hash mismatch",
    )
    passed("Post-Compaction WAL Final Hash Matches Journal")

    # ------------------------------------------------------------------------
    # TEST 19
    # ------------------------------------------------------------------------

    test_header("SNAPSHOT AFTER COMPACTION")

    snapshot = engine.serialize_snapshot()

    recovered = N38Engine.restore_snapshot(snapshot)

    passed("Compacted Durable Snapshot Restored")

    require(
        recovered.state.compaction_phase
        == COMPACTION_FINALIZED,
        "compaction phase not restored",
    )
    passed("Finalized Compaction State Survives Restart")

    # ------------------------------------------------------------------------
    # TEST 20
    # ------------------------------------------------------------------------

    test_header("FINALIZED FENCES SURVIVE COMPACTION RESTART")

    require(
        promotion_id
        in recovered.state.finalized_promotion_ids,
        "promotion fence lost after restart",
    )
    passed("Promotion Fence Survives Compaction Restart")

    require(
        receipt_id
        in recovered.state.finalized_receipt_ids,
        "receipt fence lost after restart",
    )
    passed("Receipt Fence Survives Compaction Restart")

    require(
        promotion_id
        in recovered.state.reconciled_promotion_ids,
        "reconciliation fence lost after restart",
    )
    passed("Reconciliation Fence Survives Compaction Restart")

    # ------------------------------------------------------------------------
    # TEST 21
    # ------------------------------------------------------------------------

    test_header("PRE-CHECKPOINT CRASH RECOVERY")

    crash_a, _, _ = make_completed_engine()
    crash_a.clear_terminal_transaction()

    old_hash = crash_a.state.wal_final_hash

    crash_a.begin_compaction()

    crash_snapshot = crash_a.serialize_snapshot()

    restart_a = N38Engine.restore_snapshot(
        crash_snapshot
    )

    restart_a.recover_compaction()

    require(
        restart_a.state.compaction_phase
        == COMPACTION_NONE,
        "pre-checkpoint recovery did not abort compaction",
    )
    passed("Pre-Checkpoint Crash Recovery Aborted Safely")

    require(
        restart_a.state.wal_final_hash == old_hash,
        "authoritative WAL changed",
    )
    passed("Original WAL Remained Authoritative")

    # ------------------------------------------------------------------------
    # TEST 22
    # ------------------------------------------------------------------------

    test_header(
        "POST-CHECKPOINT / PRE-WAL-TRUNCATION CRASH RECOVERY"
    )

    crash_b, tx_b, _ = make_completed_engine()
    crash_b.clear_terminal_transaction()

    crash_b.begin_compaction()
    cp_b = crash_b.persist_compaction_checkpoint()

    crash_snapshot_b = crash_b.serialize_snapshot()

    restart_b = N38Engine.restore_snapshot(
        crash_snapshot_b
    )

    restart_b.recover_compaction()

    require(
        restart_b.state.compaction_phase
        == COMPACTION_FINALIZED,
        "checkpointed compaction not recovered",
    )
    passed("Checkpointed Compaction Recovered")

    require(
        tx_b.promotion_id
        in restart_b.state.finalized_promotion_ids,
        "promotion fence lost during recovery",
    )
    passed("Promotion Fence Survived Checkpoint Recovery")

    require(
        restart_b.state.next_wal_sequence
        > cp_b.compacted_through_sequence,
        "WAL sequence did not advance beyond checkpoint",
    )
    passed("Recovered WAL Continues Beyond Checkpoint")

    # ------------------------------------------------------------------------
    # TEST 23
    # ------------------------------------------------------------------------

    test_header(
        "POST-WAL-REBASE / PRE-MANIFEST-FINALIZATION RECOVERY"
    )

    crash_c, tx_c, _ = make_completed_engine()
    crash_c.clear_terminal_transaction()

    crash_c.begin_compaction()
    crash_c.persist_compaction_checkpoint()
    crash_c.rebase_wal_after_checkpoint()

    require(
        crash_c.state.compaction_phase
        == COMPACTION_WAL_REBASED,
        "test setup did not reach WAL_REBASED",
    )

    crash_snapshot_c = crash_c.serialize_snapshot()

    restart_c = N38Engine.restore_snapshot(
        crash_snapshot_c
    )

    restart_c.recover_compaction()

    require(
        restart_c.state.compaction_phase
        == COMPACTION_FINALIZED,
        "rebased compaction not finalized",
    )
    passed("Rebased WAL Crash Recovered")

    require(
        tx_c.promotion_id
        in restart_c.state.finalized_promotion_ids,
        "fence lost after rebased recovery",
    )
    passed("Finalized Fence Survived Rebased Recovery")

    # ------------------------------------------------------------------------
    # TEST 24
    # ------------------------------------------------------------------------

    test_header("SECOND RESTART AFTER COMPACTION")

    second_restart = N38Engine.restore_snapshot(
        restart_c.serialize_snapshot()
    )

    second_restart.validate_durable_state()

    passed("Compacted State Survives Second Restart")

    # ------------------------------------------------------------------------
    # TEST 25
    # ------------------------------------------------------------------------

    test_header("IDEMPOTENT FINALIZED COMPACTION RECOVERY")

    before_hash = second_restart.state.wal_final_hash
    before_length = len(second_restart.state.wal)

    second_restart.recover_compaction()

    require(
        second_restart.state.wal_final_hash
        == before_hash,
        "finalized recovery changed WAL hash",
    )

    require(
        len(second_restart.state.wal)
        == before_length,
        "finalized recovery changed WAL length",
    )

    passed("Finalized Compaction Recovery Is Idempotent")

    # ------------------------------------------------------------------------
    # TEST 26
    # ------------------------------------------------------------------------

    test_header("CHECKPOINT TAMPER REJECTION")

    tampered_cp_engine, _, _ = make_completed_engine()
    tampered_cp_engine.clear_terminal_transaction()
    tampered_cp_engine.begin_compaction()

    tampered_cp = (
        tampered_cp_engine.persist_compaction_checkpoint()
    )

    tampered_cp.finalized_promotion_ids.append(
        "FORGED-PROMOTION-ID"
    )

    local_block(
        "Tampered Checkpoint Rejected",
        lambda: tampered_cp_engine.validate_checkpoint(
            tampered_cp
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 27
    # ------------------------------------------------------------------------

    test_header("COMPACTION MANIFEST TAMPER REJECTION")

    tampered_manifest_engine, _, _ = (
        make_completed_engine()
    )

    tampered_manifest_engine.clear_terminal_transaction()
    tampered_manifest_engine.begin_compaction()

    cp_m = (
        tampered_manifest_engine
        .persist_compaction_checkpoint()
    )

    manifest_m = (
        tampered_manifest_engine
        .state
        .compaction_manifest
    )

    require(
        manifest_m is not None,
        "test manifest missing",
    )

    manifest_m.compacted_through_sequence += 1

    local_block(
        "Tampered Compaction Manifest Rejected",
        lambda: tampered_manifest_engine
        .validate_manifest(
            manifest_m,
            cp_m,
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 28
    # ------------------------------------------------------------------------

    test_header("MANIFEST/CHECKPOINT ID MISMATCH REJECTION")

    mismatch_engine, _, _ = make_completed_engine()
    mismatch_engine.clear_terminal_transaction()
    mismatch_engine.begin_compaction()

    cp_x = mismatch_engine.persist_compaction_checkpoint()

    manifest_x = copy.deepcopy(
        mismatch_engine.state.compaction_manifest
    )

    require(
        manifest_x is not None,
        "test manifest missing",
    )

    manifest_x.checkpoint_id = new_id(
        "wrong-checkpoint"
    )

    mismatch_engine.reseal_manifest(
        manifest_x
    )

    local_block(
        "Manifest Pointing To Wrong Checkpoint Rejected",
        lambda: mismatch_engine.validate_manifest(
            manifest_x,
            cp_x,
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 29
    # ------------------------------------------------------------------------

    test_header("CHECKPOINT SOURCE WAL HASH MISMATCH REJECTION")

    hash_engine, _, _ = make_completed_engine()
    hash_engine.clear_terminal_transaction()
    hash_engine.begin_compaction()

    cp_h = hash_engine.persist_compaction_checkpoint()

    bad_cp_h = copy.deepcopy(cp_h)
    bad_cp_h.source_wal_final_hash = "f" * 64

    local_block(
        "Checkpoint Source WAL Hash Tamper Rejected",
        lambda: hash_engine.validate_checkpoint(
            bad_cp_h
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 30
    # ------------------------------------------------------------------------

    test_header("SNAPSHOT TAMPER REJECTION")

    snapshot_engine, _, _ = make_completed_engine()

    snapshot_json = json.loads(
        snapshot_engine.serialize_snapshot()
    )

    snapshot_json["payload"]["generation"] += 100

    tampered_snapshot = canonical_json(
        snapshot_json
    )

    local_block(
        "Tampered Durable Snapshot Rejected",
        lambda: N38Engine.restore_snapshot(
            tampered_snapshot
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 31
    # ------------------------------------------------------------------------

    test_header("WAL RECORD HASH TAMPER REJECTION")

    wal_engine, _, _ = make_completed_engine()

    require(
        wal_engine.state.wal,
        "test WAL missing",
    )

    wal_engine.state.wal[0].data[
        "promotion_id"
    ] = "FORGED"

    local_block(
        "Tampered WAL Record Rejected",
        wal_engine.validate_wal,
    )

    # ------------------------------------------------------------------------
    # TEST 32
    # ------------------------------------------------------------------------

    test_header("WAL FINAL HASH TAMPER REJECTION")

    final_hash_engine, _, _ = make_completed_engine()

    final_hash_engine.state.wal_final_hash = "a" * 64

    local_block(
        "Tampered WAL Final Hash Rejected",
        final_hash_engine.validate_wal,
    )

    # ------------------------------------------------------------------------
    # TEST 33
    # ------------------------------------------------------------------------

    test_header("GENERATION ADVANCE AFTER COMPACTION")

    generation_engine, tx_g, _ = make_completed_engine()

    generation_engine.clear_terminal_transaction()
    generation_engine.compact()

    old_generation = generation_engine.state.generation
    old_lineage = generation_engine.state.lineage
    old_epoch = generation_engine.state.recovery_epoch

    generation_engine.advance_generation()

    require(
        generation_engine.state.generation
        > old_generation,
        "generation did not advance",
    )
    passed("Generation Advanced Monotonically")

    require(
        generation_engine.state.lineage
        != old_lineage,
        "lineage did not change",
    )
    passed("Lineage Changed On Generation Advance")

    require(
        generation_engine.state.recovery_epoch
        > old_epoch,
        "recovery epoch did not advance",
    )
    passed("Recovery Epoch Advanced Monotonically")

    # ------------------------------------------------------------------------
    # TEST 34
    # ------------------------------------------------------------------------

    test_header(
        "FINALIZED FENCE CROSS-GENERATION PRESERVATION"
    )

    require(
        tx_g.promotion_id
        in generation_engine
        .state
        .finalized_promotion_ids,
        "promotion fence lost across generation",
    )
    passed(
        "Finalized Promotion Fence Preserved Across Generation"
    )

    require(
        tx_g.receipt_id
        in generation_engine
        .state
        .finalized_receipt_ids,
        "receipt fence lost across generation",
    )
    passed(
        "Finalized Receipt Fence Preserved Across Generation"
    )

    # ------------------------------------------------------------------------
    # TEST 35
    # ------------------------------------------------------------------------

    test_header(
        "STALE CROSS-GENERATION CHECKPOINT REJECTION"
    )

    old_checkpoint = copy.deepcopy(
        generation_engine.state.checkpoint
    )

    require(
        old_checkpoint is not None,
        "old checkpoint missing",
    )

    local_block(
        "Stale Cross-Generation Checkpoint Rejected",
        lambda: generation_engine.validate_checkpoint(
            old_checkpoint,
            require_current_generation=True,
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 36
    # ------------------------------------------------------------------------

    test_header(
        "GENERATION ADVANCE BLOCKED DURING COMPACTION"
    )

    blocked_engine, _, _ = make_completed_engine()
    blocked_engine.clear_terminal_transaction()

    blocked_engine.begin_compaction()

    local_block(
        "Generation Advance During Compaction Rejected",
        blocked_engine.advance_generation,
    )

    # ------------------------------------------------------------------------
    # TEST 37
    # ------------------------------------------------------------------------

    test_header("COMPLETE DURABLE STATE VALIDATION")

    complete_engine, _, _ = make_completed_engine()

    complete_engine.clear_terminal_transaction()
    complete_engine.compact()

    complete_engine.validate_durable_state()

    passed("Complete Durable State Validates")

    # ------------------------------------------------------------------------
    # TEST 38
    # ------------------------------------------------------------------------

    test_header("POST-COMPACTION WAL INTEGRITY")

    complete_engine.validate_wal()

    passed("WAL Records Validate")

    require(
        complete_engine.state.wal_final_hash
        == complete_engine.state.wal[-1].record_hash,
        "WAL journal final hash mismatch",
    )
    passed("WAL Final Hash Matches Journal")

    require(
        complete_engine.state.wal[0].sequence
        == (
            complete_engine
            .state
            .checkpoint
            .compacted_through_sequence
            + 1
        ),
        "post-compaction WAL sequence mismatch",
    )
    passed("Post-Compaction WAL Sequence Preserved")

    # ------------------------------------------------------------------------
    # TEST 39
    # ------------------------------------------------------------------------

    test_header("SYNTHETIC TRANSPORT FIREBREAK")

    transport_engine, transport_tx, _ = (
        make_completed_engine()
    )

    require(
        transport_tx.synthetic_dispatch,
        "dispatch was not synthetic",
    )
    passed("Dispatch Is Synthetic")

    require(
        not transport_tx.network_transmitted,
        "network transmission occurred",
    )
    passed("No Network Transmission Occurred")

    require(
        transport_tx.method == "POST",
        "transport method mismatch",
    )
    passed("Transport Method Exactly POST")

    require(
        transport_tx.path == LEVERAGE_ENDPOINT,
        "transport path mismatch",
    )
    passed("Transport Path Exactly Leverage Endpoint")

    require(
        transport_tx.payload_hash
        == sha256_text(
            canonical_json(
                transport_tx.payload
            )
        ),
        "transport payload hash mismatch",
    )
    passed("Transport Payload Hash Preserved")

    # ------------------------------------------------------------------------
    # TEST 40
    # ------------------------------------------------------------------------

    test_header("FINAL NETWORK WRITE POLICY")

    require(
        not REAL_POST_ENABLED,
        "real POST enabled",
    )
    passed("Real POST Disabled")

    require(
        not DEMO_POST_ENABLED,
        "demo POST enabled",
    )
    passed("Demo POST Disabled")

    require(
        not NETWORK_WRITES_ENABLED,
        "network writes enabled",
    )
    passed("All Network Writes Disabled")

    require(
        SYNTHETIC_TRANSPORT_ONLY,
        "synthetic transport only disabled",
    )
    passed("Synthetic Transport Only")

    # ------------------------------------------------------------------------
    # FINAL
    # ------------------------------------------------------------------------

    print()
    divider()
    print(
        f"{UNIT_NAME}: ALL DIAGNOSTICS PASSED",
        flush=True,
    )
    divider()

    print(
        "NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO DEMO ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO NETWORK WRITE WAS ATTEMPTED",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: TEST GROUPS EXECUTED = "
        f"{TEST_NUMBER}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: PASS ASSERTIONS = "
        f"{PASS_COUNT}",
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
        os.environ.get(
            "PORT",
            "10000",
        )
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


def start_health_server() -> None:

    thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    thread.start()


# ============================================================================
# HEARTBEAT LOOP
# ============================================================================

def heartbeat_loop() -> None:

    counter = 1

    while True:

        print(
            f"{UNIT_NAME}: HEARTBEAT {counter} "
            f"| synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} "
            f"| network-writes="
            f"{NETWORK_WRITES_ENABLED}",
            flush=True,
        )

        counter += 1

        time.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:

    run_diagnostics()

    start_health_server()

    heartbeat_loop()


if __name__ == "__main__":
    main()
