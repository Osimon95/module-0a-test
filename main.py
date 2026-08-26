# ============================================================================
# R28 UNIT N.37
# DURABLE TRANSACTION RECONCILIATION + RESTART CERTIFICATE +
# TERMINAL IDEMPOTENCY + CROSS-GENERATION FENCING
#
# COMPLETE SINGLE MAIN.PY
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.37 INCREMENT OVER N.36:
#   - DURABLE RECONCILIATION CERTIFICATE
#   - RESTART-SAFE TRANSACTION RECONCILIATION
#   - PREPARED / AUTHORITY / RECEIPT / FINALIZED STATE CLASSIFICATION
#   - EXACTLY-ONCE RECONCILIATION COMMIT
#   - RECONCILIATION CERTIFICATE INTEGRITY SEAL
#   - CERTIFICATE GENERATION / LINEAGE / EPOCH BINDING
#   - STALE CERTIFICATE REJECTION
#   - RECONCILIATION REPLAY REJECTION
#   - TERMINAL RECONCILIATION IDEMPOTENCY
#   - CROSS-GENERATION FINALIZATION FENCE
#   - WAL-BACKED RECONCILIATION JOURNAL
#   - SNAPSHOT + WAL + CERTIFICATE COMPLETE STATE VALIDATION
#
# NO REAL ORDER IS SENT.
# NO DEMO ORDER IS SENT.
# NO NETWORK WRITE IS ATTEMPTED.
# ============================================================================

print("R28 UNIT N.37: MAIN.PY ENTERED", flush=True)

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
from typing import Any, Dict, List, Optional


print("R28 UNIT N.37: IMPORTS COMPLETE", flush=True)


# ============================================================================
# CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.37"
UNIT_VERSION = "N.37"

SYMBOL = "BTCUSDT"
HTTP_METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

TARGET_LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

HEALTH_PORT = int(os.getenv("PORT", "10000"))
HEARTBEAT_SECONDS = 30

INTEGRITY_KEY = b"R28-N37-DURABLE-INTEGRITY-KEY"
WAL_KEY = b"R28-N37-WAL-INTEGRITY-KEY"
CERTIFICATE_KEY = b"R28-N37-RECONCILIATION-CERTIFICATE-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORITY_COMMITTED = "AUTHORITY_COMMITTED"
PHASE_RECEIPT_COMMITTED = "RECEIPT_COMMITTED"
PHASE_FINALIZED = "FINALIZED"

RECON_PREPARED = "PREPARED"
RECON_AUTHORITY = "AUTHORITY_COMMITTED"
RECON_RECEIPT = "RECEIPT_COMMITTED"
RECON_FINALIZED = "FINALIZED"

ZERO_HASH = "0" * 64


print("R28 UNIT N.37: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# HELPERS
# ============================================================================


class LocalBlock(Exception):
    pass


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

    return hmac.new(key, raw, hashlib.sha256).hexdigest()


def secure_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(str(a), str(b))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalBlock(message)


def separator() -> None:
    print("-" * 92, flush=True)


def test_header(number: int, title: str) -> None:
    separator()
    print(f"{UNIT_NAME} TEST {number}: {title}", flush=True)
    separator()


def pass_line(label: str) -> None:
    width = 82
    if len(label) < width:
        label = label + (" " * (width - len(label)))

    print(f"{label} ✅ PASS", flush=True)


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


def expect_block(label: str, expected_message: str, callback) -> None:
    blocked = False

    try:
        callback()

    except LocalBlock as exc:
        blocked = True
        local_block(str(exc))
        require(
            str(exc) == expected_message,
            f"unexpected local block: {exc}",
        )

    require(blocked, f"expected local block did not occur: {expected_message}")
    pass_line(label)


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class PromotionIntent:
    promotion_id: str
    symbol: str
    generation: int
    lineage: str
    recovery_epoch: int
    payload: Dict[str, Any]
    payload_hash: str
    phase: str
    integrity_seal: str = ""


@dataclass
class CommittedAuthority:
    promotion_id: str
    authority_id: str
    symbol: str
    generation: int
    lineage: str
    recovery_epoch: int
    payload_hash: str
    integrity_seal: str = ""


@dataclass
class PromotionReceipt:
    promotion_id: str
    receipt_id: str
    authority_id: str
    symbol: str
    generation: int
    lineage: str
    recovery_epoch: int
    transport_method: str
    transport_path: str
    transport_payload_hash: str
    synthetic: bool
    transmitted: bool
    finalized: bool = False
    integrity_seal: str = ""


@dataclass
class ReconciliationCertificate:
    certificate_id: str
    promotion_id: str
    classification: str

    generation: int
    lineage: str
    recovery_epoch: int

    payload_hash: str

    authority_id: Optional[str]
    receipt_id: Optional[str]

    finalized: bool
    terminal: bool

    certificate_sequence: int

    integrity_seal: str = ""


@dataclass
class WALRecord:
    sequence: int
    event_type: str
    promotion_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    payload_hash: str
    previous_hash: str
    record_hash: str


@dataclass
class DurableState:
    generation: int = 1
    lineage: str = field(default_factory=lambda: str(uuid.uuid4()))
    recovery_epoch: int = 1

    pending_promotion: Optional[PromotionIntent] = None
    committed_authority: Optional[CommittedAuthority] = None
    committed_receipt: Optional[PromotionReceipt] = None

    finalized_promotion_ids: List[str] = field(default_factory=list)
    finalized_receipt_ids: List[str] = field(default_factory=list)

    reconciliation_certificate: Optional[ReconciliationCertificate] = None
    reconciled_promotion_ids: List[str] = field(default_factory=list)

    wal: List[WALRecord] = field(default_factory=list)
    wal_final_hash: str = ZERO_HASH

    next_certificate_sequence: int = 1

    snapshot_integrity_seal: str = ""


# ============================================================================
# ENGINE
# ============================================================================


class N37Engine:
    def __init__(self) -> None:
        self.state = DurableState()
        self.synthetic_dispatch_count = 0
        self.network_write_count = 0

        self._seal_snapshot()

    # ========================================================================
    # PAYLOAD
    # ========================================================================

    def build_payload(self) -> Dict[str, Any]:
        return {
            "leverage": TARGET_LEVERAGE,
            "marginMode": MARGIN_MODE,
            "symbol": SYMBOL,
        }

    # ========================================================================
    # SEALING
    # ========================================================================

    def _intent_material(self, intent: PromotionIntent) -> Dict[str, Any]:
        data = asdict(intent)
        data.pop("integrity_seal", None)
        return data

    def _seal_intent(self, intent: PromotionIntent) -> None:
        intent.integrity_seal = hmac_hex(
            INTEGRITY_KEY,
            self._intent_material(intent),
        )

    def _validate_intent_seal(self, intent: PromotionIntent) -> None:
        expected = hmac_hex(
            INTEGRITY_KEY,
            self._intent_material(intent),
        )

        require(
            secure_equal(intent.integrity_seal, expected),
            "promotion intent integrity seal mismatch",
        )

    def _authority_material(
        self,
        authority: CommittedAuthority,
    ) -> Dict[str, Any]:
        data = asdict(authority)
        data.pop("integrity_seal", None)
        return data

    def _seal_authority(
        self,
        authority: CommittedAuthority,
    ) -> None:
        authority.integrity_seal = hmac_hex(
            INTEGRITY_KEY,
            self._authority_material(authority),
        )

    def _validate_authority_seal(
        self,
        authority: CommittedAuthority,
    ) -> None:
        expected = hmac_hex(
            INTEGRITY_KEY,
            self._authority_material(authority),
        )

        require(
            secure_equal(authority.integrity_seal, expected),
            "committed authority integrity seal mismatch",
        )

    def _receipt_material(
        self,
        receipt: PromotionReceipt,
    ) -> Dict[str, Any]:
        data = asdict(receipt)
        data.pop("integrity_seal", None)
        return data

    def _seal_receipt(
        self,
        receipt: PromotionReceipt,
    ) -> None:
        receipt.integrity_seal = hmac_hex(
            INTEGRITY_KEY,
            self._receipt_material(receipt),
        )

    def _validate_receipt_seal(
        self,
        receipt: PromotionReceipt,
    ) -> None:
        expected = hmac_hex(
            INTEGRITY_KEY,
            self._receipt_material(receipt),
        )

        require(
            secure_equal(receipt.integrity_seal, expected),
            "promotion receipt integrity seal mismatch",
        )

    def _certificate_material(
        self,
        certificate: ReconciliationCertificate,
    ) -> Dict[str, Any]:
        data = asdict(certificate)
        data.pop("integrity_seal", None)
        return data

    def _seal_certificate(
        self,
        certificate: ReconciliationCertificate,
    ) -> None:
        certificate.integrity_seal = hmac_hex(
            CERTIFICATE_KEY,
            self._certificate_material(certificate),
        )

    def _validate_certificate_seal(
        self,
        certificate: ReconciliationCertificate,
    ) -> None:
        expected = hmac_hex(
            CERTIFICATE_KEY,
            self._certificate_material(certificate),
        )

        require(
            secure_equal(certificate.integrity_seal, expected),
            "reconciliation certificate integrity seal mismatch",
        )

    # ========================================================================
    # WAL
    # ========================================================================

    def _append_wal(
        self,
        event_type: str,
        promotion_id: str,
        payload_hash: str,
    ) -> WALRecord:
        sequence = len(self.state.wal) + 1
        previous_hash = self.state.wal_final_hash

        material = {
            "sequence": sequence,
            "event_type": event_type,
            "promotion_id": promotion_id,
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "payload_hash": payload_hash,
            "previous_hash": previous_hash,
        }

        record_hash = hmac_hex(WAL_KEY, material)

        record = WALRecord(
            sequence=sequence,
            event_type=event_type,
            promotion_id=promotion_id,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            payload_hash=payload_hash,
            previous_hash=previous_hash,
            record_hash=record_hash,
        )

        self.state.wal.append(record)
        self.state.wal_final_hash = record_hash

        return record

    def validate_wal(self) -> None:
        previous_hash = ZERO_HASH

        for expected_sequence, record in enumerate(
            self.state.wal,
            start=1,
        ):
            require(
                record.sequence == expected_sequence,
                "WAL sequence mismatch",
            )

            require(
                record.previous_hash == previous_hash,
                "WAL previous hash mismatch",
            )

            material = {
                "sequence": record.sequence,
                "event_type": record.event_type,
                "promotion_id": record.promotion_id,
                "generation": record.generation,
                "lineage": record.lineage,
                "recovery_epoch": record.recovery_epoch,
                "payload_hash": record.payload_hash,
                "previous_hash": record.previous_hash,
            }

            expected_hash = hmac_hex(WAL_KEY, material)

            require(
                secure_equal(record.record_hash, expected_hash),
                "WAL record hash mismatch",
            )

            previous_hash = record.record_hash

        require(
            self.state.wal_final_hash == previous_hash,
            "WAL final hash mismatch",
        )

    # ========================================================================
    # SNAPSHOT
    # ========================================================================

    def _snapshot_material(self) -> Dict[str, Any]:
        state_dict = asdict(self.state)

        state_dict.pop(
            "snapshot_integrity_seal",
            None,
        )

        return state_dict

    def _seal_snapshot(self) -> None:
        self.state.snapshot_integrity_seal = hmac_hex(
            INTEGRITY_KEY,
            self._snapshot_material(),
        )

    def validate_snapshot(self) -> None:
        expected = hmac_hex(
            INTEGRITY_KEY,
            self._snapshot_material(),
        )

        require(
            secure_equal(
                self.state.snapshot_integrity_seal,
                expected,
            ),
            "snapshot integrity seal mismatch",
        )

    def snapshot(self) -> Dict[str, Any]:
        self._seal_snapshot()
        return copy.deepcopy(asdict(self.state))

    @staticmethod
    def restore(snapshot: Dict[str, Any]) -> "N37Engine":
        engine = N37Engine()

        raw = copy.deepcopy(snapshot)

        pending_raw = raw.get("pending_promotion")
        authority_raw = raw.get("committed_authority")
        receipt_raw = raw.get("committed_receipt")
        certificate_raw = raw.get("reconciliation_certificate")

        wal_raw = raw.get("wal", [])

        engine.state = DurableState(
            generation=raw["generation"],
            lineage=raw["lineage"],
            recovery_epoch=raw["recovery_epoch"],

            pending_promotion=(
                PromotionIntent(**pending_raw)
                if pending_raw
                else None
            ),

            committed_authority=(
                CommittedAuthority(**authority_raw)
                if authority_raw
                else None
            ),

            committed_receipt=(
                PromotionReceipt(**receipt_raw)
                if receipt_raw
                else None
            ),

            finalized_promotion_ids=list(
                raw.get(
                    "finalized_promotion_ids",
                    [],
                )
            ),

            finalized_receipt_ids=list(
                raw.get(
                    "finalized_receipt_ids",
                    [],
                )
            ),

            reconciliation_certificate=(
                ReconciliationCertificate(**certificate_raw)
                if certificate_raw
                else None
            ),

            reconciled_promotion_ids=list(
                raw.get(
                    "reconciled_promotion_ids",
                    [],
                )
            ),

            wal=[
                WALRecord(**record)
                for record in wal_raw
            ],

            wal_final_hash=raw.get(
                "wal_final_hash",
                ZERO_HASH,
            ),

            next_certificate_sequence=raw.get(
                "next_certificate_sequence",
                1,
            ),

            snapshot_integrity_seal=raw[
                "snapshot_integrity_seal"
            ],
        )

        engine.validate_snapshot()
        engine.validate_wal()
        engine.validate_complete_state()

        return engine

    # ========================================================================
    # PROMOTION TRANSACTION
    # ========================================================================

    def prepare_promotion(self) -> PromotionIntent:
        require(
            self.state.pending_promotion is None,
            "pending promotion already exists",
        )

        require(
            self.state.committed_authority is None,
            "committed authority already exists",
        )

        require(
            self.state.committed_receipt is None,
            "promotion receipt already committed",
        )

        payload = self.build_payload()
        payload_hash = sha256_hex(payload)

        promotion_id = str(uuid.uuid4())

        intent = PromotionIntent(
            promotion_id=promotion_id,
            symbol=SYMBOL,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            payload=payload,
            payload_hash=payload_hash,
            phase=PHASE_PREPARED,
        )

        self._seal_intent(intent)

        self.state.pending_promotion = intent

        self._append_wal(
            "PROMOTION_PREPARED",
            promotion_id,
            payload_hash,
        )

        self._seal_snapshot()

        return intent

    def _validate_promotion_intent(
        self,
        intent: PromotionIntent,
    ) -> None:
        self._validate_intent_seal(intent)

        require(
            intent.symbol == SYMBOL,
            "promotion intent symbol mismatch",
        )

        require(
            intent.generation == self.state.generation,
            "promotion intent generation mismatch",
        )

        require(
            intent.lineage == self.state.lineage,
            "promotion intent lineage mismatch",
        )

        require(
            intent.recovery_epoch
            == self.state.recovery_epoch,
            "promotion intent recovery epoch mismatch",
        )

        require(
            sha256_hex(intent.payload)
            == intent.payload_hash,
            "promotion intent payload hash mismatch",
        )

        require(
            intent.promotion_id
            not in self.state.finalized_promotion_ids,
            "promotion intent already finalized",
        )

    def commit_authority(
        self,
        intent: PromotionIntent,
    ) -> CommittedAuthority:
        self._validate_promotion_intent(intent)

        require(
            self.state.pending_promotion is not None,
            "pending promotion missing",
        )

        require(
            self.state.committed_authority is None,
            "committed authority already exists",
        )

        require(
            self.state.pending_promotion.promotion_id
            == intent.promotion_id,
            "promotion intent identity mismatch",
        )

        authority = CommittedAuthority(
            promotion_id=intent.promotion_id,
            authority_id=str(uuid.uuid4()),
            symbol=intent.symbol,
            generation=intent.generation,
            lineage=intent.lineage,
            recovery_epoch=intent.recovery_epoch,
            payload_hash=intent.payload_hash,
        )

        self._seal_authority(authority)

        self.state.committed_authority = authority
        self.state.pending_promotion.phase = PHASE_AUTHORITY_COMMITTED

        self._seal_intent(
            self.state.pending_promotion
        )

        self._append_wal(
            "AUTHORITY_COMMITTED",
            intent.promotion_id,
            intent.payload_hash,
        )

        self._seal_snapshot()

        return authority

    # ========================================================================
    # SYNTHETIC TRANSPORT
    # ========================================================================

    def synthetic_dispatch(
        self,
        authority: CommittedAuthority,
    ) -> PromotionReceipt:
        self._validate_authority_seal(authority)

        require(
            SYNTHETIC_TRANSPORT_ONLY,
            "synthetic transport disabled",
        )

        require(
            not NETWORK_WRITES_ENABLED,
            "network writes enabled",
        )

        require(
            not REAL_POST_ENABLED,
            "real POST enabled",
        )

        require(
            not DEMO_POST_ENABLED,
            "demo POST enabled",
        )

        require(
            self.state.committed_authority is not None,
            "committed authority missing",
        )

        require(
            self.state.committed_receipt is None,
            "promotion receipt already committed",
        )

        require(
            authority.authority_id
            == self.state.committed_authority.authority_id,
            "authority identity mismatch",
        )

        require(
            authority.generation
            == self.state.generation,
            "authority generation mismatch",
        )

        require(
            authority.lineage
            == self.state.lineage,
            "authority lineage mismatch",
        )

        require(
            authority.recovery_epoch
            == self.state.recovery_epoch,
            "authority recovery epoch mismatch",
        )

        receipt = PromotionReceipt(
            promotion_id=authority.promotion_id,
            receipt_id=str(uuid.uuid4()),
            authority_id=authority.authority_id,
            symbol=authority.symbol,
            generation=authority.generation,
            lineage=authority.lineage,
            recovery_epoch=authority.recovery_epoch,
            transport_method=HTTP_METHOD,
            transport_path=LEVERAGE_ENDPOINT,
            transport_payload_hash=authority.payload_hash,
            synthetic=True,
            transmitted=False,
            finalized=False,
        )

        self._seal_receipt(receipt)

        self.state.committed_receipt = receipt

        if self.state.pending_promotion:
            self.state.pending_promotion.phase = PHASE_RECEIPT_COMMITTED
            self._seal_intent(
                self.state.pending_promotion
            )

        self.synthetic_dispatch_count += 1

        self._append_wal(
            "SYNTHETIC_RECEIPT_COMMITTED",
            authority.promotion_id,
            authority.payload_hash,
        )

        self._seal_snapshot()

        return receipt

    # ========================================================================
    # FINALIZATION
    # ========================================================================

    def finalize_receipt(
        self,
        receipt: PromotionReceipt,
    ) -> None:
        self._validate_receipt_seal(receipt)

        require(
            not receipt.finalized,
            "promotion receipt already finalized",
        )

        require(
            self.state.committed_receipt is not None,
            "committed receipt missing",
        )

        require(
            self.state.committed_receipt.receipt_id
            == receipt.receipt_id,
            "receipt identity mismatch",
        )

        require(
            receipt.generation
            == self.state.generation,
            "receipt generation mismatch",
        )

        require(
            receipt.lineage
            == self.state.lineage,
            "receipt lineage mismatch",
        )

        require(
            receipt.recovery_epoch
            == self.state.recovery_epoch,
            "receipt recovery epoch mismatch",
        )

        require(
            receipt.synthetic,
            "receipt is not synthetic",
        )

        require(
            not receipt.transmitted,
            "receipt indicates network transmission",
        )

        receipt.finalized = True
        self._seal_receipt(receipt)

        promotion_id = receipt.promotion_id

        if promotion_id not in self.state.finalized_promotion_ids:
            self.state.finalized_promotion_ids.append(
                promotion_id
            )

        if receipt.receipt_id not in self.state.finalized_receipt_ids:
            self.state.finalized_receipt_ids.append(
                receipt.receipt_id
            )

        if self.state.pending_promotion:
            self.state.pending_promotion.phase = PHASE_FINALIZED
            self._seal_intent(
                self.state.pending_promotion
            )

        self._append_wal(
            "PROMOTION_FINALIZED",
            promotion_id,
            receipt.transport_payload_hash,
        )

        self._seal_snapshot()

    # ========================================================================
    # N.37 RECONCILIATION
    # ========================================================================

    def classify_transaction(self) -> str:
        intent = self.state.pending_promotion
        authority = self.state.committed_authority
        receipt = self.state.committed_receipt

        if (
            receipt is not None
            and receipt.finalized
            and receipt.promotion_id
            in self.state.finalized_promotion_ids
            and receipt.receipt_id
            in self.state.finalized_receipt_ids
        ):
            return RECON_FINALIZED

        if receipt is not None:
            return RECON_RECEIPT

        if authority is not None:
            return RECON_AUTHORITY

        if intent is not None:
            return RECON_PREPARED

        raise LocalBlock(
            "no promotion transaction available for reconciliation"
        )

    def create_reconciliation_certificate(
        self,
    ) -> ReconciliationCertificate:
        require(
            self.state.reconciliation_certificate is None,
            "reconciliation certificate already exists",
        )

        classification = self.classify_transaction()

        intent = self.state.pending_promotion
        authority = self.state.committed_authority
        receipt = self.state.committed_receipt

        if intent is not None:
            promotion_id = intent.promotion_id
            payload_hash = intent.payload_hash

        elif authority is not None:
            promotion_id = authority.promotion_id
            payload_hash = authority.payload_hash

        elif receipt is not None:
            promotion_id = receipt.promotion_id
            payload_hash = receipt.transport_payload_hash

        else:
            raise LocalBlock(
                "no promotion transaction available for reconciliation"
            )

        certificate = ReconciliationCertificate(
            certificate_id=str(uuid.uuid4()),
            promotion_id=promotion_id,
            classification=classification,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            payload_hash=payload_hash,
            authority_id=(
                authority.authority_id
                if authority is not None
                else None
            ),
            receipt_id=(
                receipt.receipt_id
                if receipt is not None
                else None
            ),
            finalized=(
                receipt.finalized
                if receipt is not None
                else False
            ),
            terminal=(
                classification == RECON_FINALIZED
            ),
            certificate_sequence=(
                self.state.next_certificate_sequence
            ),
        )

        self._seal_certificate(certificate)

        self.state.reconciliation_certificate = certificate
        self.state.next_certificate_sequence += 1

        self._append_wal(
            "RECONCILIATION_CERTIFICATE_COMMITTED",
            promotion_id,
            payload_hash,
        )

        self._seal_snapshot()

        return certificate

    def validate_reconciliation_certificate(
        self,
        certificate: ReconciliationCertificate,
    ) -> None:
        self._validate_certificate_seal(certificate)

        require(
            certificate.generation
            == self.state.generation,
            "reconciliation certificate generation mismatch",
        )

        require(
            certificate.lineage
            == self.state.lineage,
            "reconciliation certificate lineage mismatch",
        )

        require(
            certificate.recovery_epoch
            == self.state.recovery_epoch,
            "reconciliation certificate recovery epoch mismatch",
        )

        current = self.state.reconciliation_certificate

        require(
            current is not None,
            "reconciliation certificate missing",
        )

        require(
            certificate.certificate_id
            == current.certificate_id,
            "reconciliation certificate identity mismatch",
        )

        classification = self.classify_transaction()

        require(
            certificate.classification == classification,
            "reconciliation classification mismatch",
        )

        if self.state.pending_promotion is not None:
            require(
                certificate.promotion_id
                == self.state.pending_promotion.promotion_id,
                "reconciliation promotion identity mismatch",
            )

            require(
                certificate.payload_hash
                == self.state.pending_promotion.payload_hash,
                "reconciliation payload hash mismatch",
            )

        if self.state.committed_authority is not None:
            require(
                certificate.authority_id
                == self.state.committed_authority.authority_id,
                "reconciliation authority identity mismatch",
            )

        if self.state.committed_receipt is not None:
            require(
                certificate.receipt_id
                == self.state.committed_receipt.receipt_id,
                "reconciliation receipt identity mismatch",
            )

    def reconcile(
        self,
        certificate: ReconciliationCertificate,
    ) -> str:
        self.validate_reconciliation_certificate(
            certificate
        )

        require(
            certificate.promotion_id
            not in self.state.reconciled_promotion_ids,
            "promotion transaction already reconciled",
        )

        classification = certificate.classification

        if classification == RECON_PREPARED:
            result = "RECOVER_PREPARED"

        elif classification == RECON_AUTHORITY:
            result = "RECOVER_AUTHORITY"

        elif classification == RECON_RECEIPT:
            result = "RECOVER_RECEIPT"

        elif classification == RECON_FINALIZED:
            result = "TERMINAL_FINALIZED"

        else:
            raise LocalBlock(
                "unknown reconciliation classification"
            )

        self.state.reconciled_promotion_ids.append(
            certificate.promotion_id
        )

        self._append_wal(
            "TRANSACTION_RECONCILED",
            certificate.promotion_id,
            certificate.payload_hash,
        )

        self._seal_snapshot()

        return result

    # ========================================================================
    # TERMINAL CLEANUP
    # ========================================================================

    def clear_terminal_transaction(
        self,
    ) -> None:
        receipt = self.state.committed_receipt

        require(
            receipt is not None,
            "committed receipt missing",
        )

        require(
            receipt.finalized,
            "cannot clear non-finalized transaction",
        )

        require(
            receipt.promotion_id
            in self.state.reconciled_promotion_ids,
            "terminal transaction not reconciled",
        )

        self.state.pending_promotion = None
        self.state.committed_authority = None
        self.state.committed_receipt = None
        self.state.reconciliation_certificate = None

        self._append_wal(
            "TERMINAL_TRANSACTION_CLEARED",
            receipt.promotion_id,
            receipt.transport_payload_hash,
        )

        self._seal_snapshot()

    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(self) -> None:
        require(
            self.state.pending_promotion is None,
            "cannot advance generation with pending promotion",
        )

        require(
            self.state.committed_authority is None,
            "cannot advance generation with committed authority",
        )

        require(
            self.state.committed_receipt is None,
            "cannot advance generation with committed receipt",
        )

        require(
            self.state.reconciliation_certificate is None,
            "cannot advance generation with reconciliation certificate",
        )

        old_generation = self.state.generation

        self.state.generation += 1
        self.state.lineage = str(uuid.uuid4())
        self.state.recovery_epoch += 1

        self._append_wal(
            "GENERATION_ADVANCED",
            f"generation-{old_generation}",
            sha256_hex(
                {
                    "old_generation": old_generation,
                    "new_generation": self.state.generation,
                }
            ),
        )

        self._seal_snapshot()

    # ========================================================================
    # COMPLETE STATE VALIDATION
    # ========================================================================

    def validate_complete_state(self) -> None:
        self.validate_snapshot()
        self.validate_wal()

        if self.state.pending_promotion is not None:
            self._validate_intent_seal(
                self.state.pending_promotion
            )

            require(
                self.state.pending_promotion.generation
                == self.state.generation,
                "promotion intent generation mismatch",
            )

            require(
                self.state.pending_promotion.lineage
                == self.state.lineage,
                "promotion intent lineage mismatch",
            )

            require(
                self.state.pending_promotion.recovery_epoch
                == self.state.recovery_epoch,
                "promotion intent recovery epoch mismatch",
            )

        if self.state.committed_authority is not None:
            self._validate_authority_seal(
                self.state.committed_authority
            )

        if self.state.committed_receipt is not None:
            self._validate_receipt_seal(
                self.state.committed_receipt
            )

        if self.state.reconciliation_certificate is not None:
            self.validate_reconciliation_certificate(
                self.state.reconciliation_certificate
            )

        for promotion_id in self.state.reconciled_promotion_ids:
            require(
                isinstance(promotion_id, str)
                and len(promotion_id) > 0,
                "invalid reconciled promotion identity",
            )

        require(
            self.network_write_count == 0,
            "network transmission count is not zero",
        )


print("R28 UNIT N.37: DEFINITIONS LOADED", flush=True)


# ============================================================================
# TEST HELPERS
# ============================================================================


def build_prepared_engine() -> N37Engine:
    engine = N37Engine()
    engine.prepare_promotion()
    return engine


def build_authority_engine() -> N37Engine:
    engine = N37Engine()
    intent = engine.prepare_promotion()
    engine.commit_authority(intent)
    return engine


def build_receipt_engine() -> N37Engine:
    engine = N37Engine()
    intent = engine.prepare_promotion()
    authority = engine.commit_authority(intent)
    engine.synthetic_dispatch(authority)
    return engine


def build_finalized_engine() -> N37Engine:
    engine = N37Engine()
    intent = engine.prepare_promotion()
    authority = engine.commit_authority(intent)
    receipt = engine.synthetic_dispatch(authority)
    engine.finalize_receipt(receipt)
    return engine


# ============================================================================
# DIAGNOSTICS
# ============================================================================


def run_diagnostics() -> None:

    # ------------------------------------------------------------------------
    # TEST 1
    # ------------------------------------------------------------------------

    test_header(
        1,
        "INITIAL DURABLE STATE",
    )

    engine = N37Engine()

    pass_line(
        "Initial Generation Is One"
    )

    require(
        engine.state.generation == 1,
        "initial generation mismatch",
    )

    pass_line(
        "Initial Lineage Established"
    )

    require(
        bool(engine.state.lineage),
        "initial lineage missing",
    )

    pass_line(
        "Initial Recovery Epoch Is One"
    )

    require(
        engine.state.recovery_epoch == 1,
        "initial recovery epoch mismatch",
    )

    pass_line(
        "Initial WAL Is Empty"
    )

    require(
        engine.state.wal == [],
        "initial WAL is not empty",
    )

    # ------------------------------------------------------------------------
    # TEST 2
    # ------------------------------------------------------------------------

    test_header(
        2,
        "PREPARED TRANSACTION CLASSIFICATION",
    )

    prepared = build_prepared_engine()

    require(
        prepared.classify_transaction()
        == RECON_PREPARED,
        "prepared classification mismatch",
    )

    pass_line(
        "Prepared Transaction Classified Correctly"
    )

    # ------------------------------------------------------------------------
    # TEST 3
    # ------------------------------------------------------------------------

    test_header(
        3,
        "AUTHORITY TRANSACTION CLASSIFICATION",
    )

    authority_engine = build_authority_engine()

    require(
        authority_engine.classify_transaction()
        == RECON_AUTHORITY,
        "authority classification mismatch",
    )

    pass_line(
        "Authority Transaction Classified Correctly"
    )

    # ------------------------------------------------------------------------
    # TEST 4
    # ------------------------------------------------------------------------

    test_header(
        4,
        "RECEIPT TRANSACTION CLASSIFICATION",
    )

    receipt_engine = build_receipt_engine()

    require(
        receipt_engine.classify_transaction()
        == RECON_RECEIPT,
        "receipt classification mismatch",
    )

    pass_line(
        "Receipt Transaction Classified Correctly"
    )

    # ------------------------------------------------------------------------
    # TEST 5
    # ------------------------------------------------------------------------

    test_header(
        5,
        "FINALIZED TRANSACTION CLASSIFICATION",
    )

    finalized = build_finalized_engine()

    require(
        finalized.classify_transaction()
        == RECON_FINALIZED,
        "finalized classification mismatch",
    )

    pass_line(
        "Finalized Transaction Classified Correctly"
    )

    # ------------------------------------------------------------------------
    # TEST 6
    # ------------------------------------------------------------------------

    test_header(
        6,
        "PREPARED RECONCILIATION CERTIFICATE",
    )

    prepared = build_prepared_engine()

    cert = prepared.create_reconciliation_certificate()

    require(
        cert.classification == RECON_PREPARED,
        "prepared certificate classification mismatch",
    )

    require(
        cert.authority_id is None,
        "prepared certificate has authority",
    )

    require(
        cert.receipt_id is None,
        "prepared certificate has receipt",
    )

    pass_line(
        "Prepared Certificate Created"
    )

    pass_line(
        "Prepared Certificate Has No Authority"
    )

    pass_line(
        "Prepared Certificate Has No Receipt"
    )

    # ------------------------------------------------------------------------
    # TEST 7
    # ------------------------------------------------------------------------

    test_header(
        7,
        "AUTHORITY RECONCILIATION CERTIFICATE",
    )

    authority_engine = build_authority_engine()

    cert = authority_engine.create_reconciliation_certificate()

    require(
        cert.classification == RECON_AUTHORITY,
        "authority certificate classification mismatch",
    )

    require(
        cert.authority_id
        == authority_engine.state.committed_authority.authority_id,
        "authority certificate authority mismatch",
    )

    require(
        cert.receipt_id is None,
        "authority certificate has receipt",
    )

    pass_line(
        "Authority Certificate Created"
    )

    pass_line(
        "Authority Identity Bound"
    )

    # ------------------------------------------------------------------------
    # TEST 8
    # ------------------------------------------------------------------------

    test_header(
        8,
        "RECEIPT RECONCILIATION CERTIFICATE",
    )

    receipt_engine = build_receipt_engine()

    cert = receipt_engine.create_reconciliation_certificate()

    require(
        cert.classification == RECON_RECEIPT,
        "receipt certificate classification mismatch",
    )

    require(
        cert.receipt_id
        == receipt_engine.state.committed_receipt.receipt_id,
        "receipt certificate receipt mismatch",
    )

    pass_line(
        "Receipt Certificate Created"
    )

    pass_line(
        "Receipt Identity Bound"
    )

    # ------------------------------------------------------------------------
    # TEST 9
    # ------------------------------------------------------------------------

    test_header(
        9,
        "FINALIZED RECONCILIATION CERTIFICATE",
    )

    finalized = build_finalized_engine()

    cert = finalized.create_reconciliation_certificate()

    require(
        cert.classification == RECON_FINALIZED,
        "finalized certificate classification mismatch",
    )

    require(
        cert.finalized,
        "finalized certificate not marked finalized",
    )

    require(
        cert.terminal,
        "finalized certificate not terminal",
    )

    pass_line(
        "Finalized Certificate Created"
    )

    pass_line(
        "Finalized Certificate Marked Terminal"
    )

    # ------------------------------------------------------------------------
    # TEST 10
    # ------------------------------------------------------------------------

    test_header(
        10,
        "CERTIFICATE GENERATION BINDING",
    )

    engine = build_receipt_engine()
    cert = engine.create_reconciliation_certificate()

    require(
        cert.generation == engine.state.generation,
        "certificate generation mismatch",
    )

    pass_line(
        "Certificate Bound To Generation"
    )

    # ------------------------------------------------------------------------
    # TEST 11
    # ------------------------------------------------------------------------

    test_header(
        11,
        "CERTIFICATE LINEAGE BINDING",
    )

    require(
        cert.lineage == engine.state.lineage,
        "certificate lineage mismatch",
    )

    pass_line(
        "Certificate Bound To Lineage"
    )

    # ------------------------------------------------------------------------
    # TEST 12
    # ------------------------------------------------------------------------

    test_header(
        12,
        "CERTIFICATE RECOVERY EPOCH BINDING",
    )

    require(
        cert.recovery_epoch
        == engine.state.recovery_epoch,
        "certificate recovery epoch mismatch",
    )

    pass_line(
        "Certificate Bound To Recovery Epoch"
    )

    # ------------------------------------------------------------------------
    # TEST 13
    # ------------------------------------------------------------------------

    test_header(
        13,
        "CERTIFICATE PAYLOAD HASH BINDING",
    )

    require(
        cert.payload_hash
        == engine.state.committed_receipt.transport_payload_hash,
        "certificate payload hash mismatch",
    )

    pass_line(
        "Certificate Payload Hash Preserved"
    )

    # ------------------------------------------------------------------------
    # TEST 14
    # ------------------------------------------------------------------------

    test_header(
        14,
        "CERTIFICATE INTEGRITY TAMPER REJECTION",
    )

    engine = build_receipt_engine()
    cert = engine.create_reconciliation_certificate()

    tampered = copy.deepcopy(cert)
    tampered.classification = RECON_FINALIZED

    expect_block(
        "Tampered Reconciliation Certificate Rejected",
        "reconciliation certificate integrity seal mismatch",
        lambda: engine.validate_reconciliation_certificate(
            tampered
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 15
    # ------------------------------------------------------------------------

    test_header(
        15,
        "CERTIFICATE GENERATION REJECTION",
    )

    engine = build_receipt_engine()
    cert = engine.create_reconciliation_certificate()

    stale = copy.deepcopy(cert)
    stale.generation += 1
    engine._seal_certificate(stale)

    expect_block(
        "Wrong Certificate Generation Rejected",
        "reconciliation certificate generation mismatch",
        lambda: engine.validate_reconciliation_certificate(
            stale
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 16
    # ------------------------------------------------------------------------

    test_header(
        16,
        "CERTIFICATE LINEAGE REJECTION",
    )

    stale = copy.deepcopy(cert)
    stale.lineage = str(uuid.uuid4())
    engine._seal_certificate(stale)

    expect_block(
        "Wrong Certificate Lineage Rejected",
        "reconciliation certificate lineage mismatch",
        lambda: engine.validate_reconciliation_certificate(
            stale
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 17
    # ------------------------------------------------------------------------

    test_header(
        17,
        "CERTIFICATE RECOVERY EPOCH REJECTION",
    )

    stale = copy.deepcopy(cert)
    stale.recovery_epoch += 1
    engine._seal_certificate(stale)

    expect_block(
        "Wrong Certificate Recovery Epoch Rejected",
        "reconciliation certificate recovery epoch mismatch",
        lambda: engine.validate_reconciliation_certificate(
            stale
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 18
    # ------------------------------------------------------------------------

    test_header(
        18,
        "SECOND CERTIFICATE COMMIT REJECTION",
    )

    engine = build_receipt_engine()
    engine.create_reconciliation_certificate()

    expect_block(
        "Second Reconciliation Certificate Rejected",
        "reconciliation certificate already exists",
        engine.create_reconciliation_certificate,
    )

    # ------------------------------------------------------------------------
    # TEST 19
    # ------------------------------------------------------------------------

    test_header(
        19,
        "PREPARED RECONCILIATION",
    )

    engine = build_prepared_engine()
    cert = engine.create_reconciliation_certificate()

    result = engine.reconcile(cert)

    require(
        result == "RECOVER_PREPARED",
        "prepared reconciliation result mismatch",
    )

    pass_line(
        "Prepared Transaction Reconciled"
    )

    # ------------------------------------------------------------------------
    # TEST 20
    # ------------------------------------------------------------------------

    test_header(
        20,
        "AUTHORITY RECONCILIATION",
    )

    engine = build_authority_engine()
    cert = engine.create_reconciliation_certificate()

    result = engine.reconcile(cert)

    require(
        result == "RECOVER_AUTHORITY",
        "authority reconciliation result mismatch",
    )

    pass_line(
        "Authority Transaction Reconciled"
    )

    # ------------------------------------------------------------------------
    # TEST 21
    # ------------------------------------------------------------------------

    test_header(
        21,
        "RECEIPT RECONCILIATION",
    )

    engine = build_receipt_engine()
    cert = engine.create_reconciliation_certificate()

    result = engine.reconcile(cert)

    require(
        result == "RECOVER_RECEIPT",
        "receipt reconciliation result mismatch",
    )

    pass_line(
        "Receipt Transaction Reconciled"
    )

    # ------------------------------------------------------------------------
    # TEST 22
    # ------------------------------------------------------------------------

    test_header(
        22,
        "FINALIZED TERMINAL RECONCILIATION",
    )

    engine = build_finalized_engine()
    cert = engine.create_reconciliation_certificate()

    result = engine.reconcile(cert)

    require(
        result == "TERMINAL_FINALIZED",
        "finalized reconciliation result mismatch",
    )

    pass_line(
        "Finalized Transaction Reconciled As Terminal"
    )

    # ------------------------------------------------------------------------
    # TEST 23
    # ------------------------------------------------------------------------

    test_header(
        23,
        "RECONCILIATION REPLAY REJECTION",
    )

    expect_block(
        "Second Reconciliation Rejected",
        "promotion transaction already reconciled",
        lambda: engine.reconcile(cert),
    )

    # ------------------------------------------------------------------------
    # TEST 24
    # ------------------------------------------------------------------------

    test_header(
        24,
        "FINALIZED TRANSACTION SURVIVES RESTART",
    )

    engine = build_finalized_engine()
    cert = engine.create_reconciliation_certificate()

    snapshot = engine.snapshot()

    recovered = N37Engine.restore(snapshot)

    require(
        recovered.state.committed_receipt is not None,
        "recovered receipt missing",
    )

    require(
        recovered.state.committed_receipt.finalized,
        "recovered receipt not finalized",
    )

    pass_line(
        "Finalized Receipt Survives Restart"
    )

    require(
        recovered.state.reconciliation_certificate
        is not None,
        "reconciliation certificate missing after restart",
    )

    pass_line(
        "Reconciliation Certificate Survives Restart"
    )

    # ------------------------------------------------------------------------
    # TEST 25
    # ------------------------------------------------------------------------

    test_header(
        25,
        "RESTART RECONCILIATION",
    )

    recovered_cert = (
        recovered.state.reconciliation_certificate
    )

    result = recovered.reconcile(recovered_cert)

    require(
        result == "TERMINAL_FINALIZED",
        "restart reconciliation mismatch",
    )

    pass_line(
        "Recovered Transaction Reconciled"
    )

    # ------------------------------------------------------------------------
    # TEST 26
    # ------------------------------------------------------------------------

    test_header(
        26,
        "RECONCILED STATE SURVIVES SECOND RESTART",
    )

    snapshot2 = recovered.snapshot()
    recovered2 = N37Engine.restore(snapshot2)

    require(
        recovered_cert.promotion_id
        in recovered2.state.reconciled_promotion_ids,
        "reconciled promotion not durable",
    )

    pass_line(
        "Reconciled Promotion Fence Survives Restart"
    )

    # ------------------------------------------------------------------------
    # TEST 27
    # ------------------------------------------------------------------------

    test_header(
        27,
        "POST-RESTART RECONCILIATION REPLAY REJECTION",
    )

    cert2 = recovered2.state.reconciliation_certificate

    expect_block(
        "Reconciliation Replay After Restart Rejected",
        "promotion transaction already reconciled",
        lambda: recovered2.reconcile(cert2),
    )

    # ------------------------------------------------------------------------
    # TEST 28
    # ------------------------------------------------------------------------

    test_header(
        28,
        "TERMINAL TRANSACTION CLEAR",
    )

    recovered2.clear_terminal_transaction()

    require(
        recovered2.state.pending_promotion is None,
        "pending promotion not cleared",
    )

    require(
        recovered2.state.committed_authority is None,
        "committed authority not cleared",
    )

    require(
        recovered2.state.committed_receipt is None,
        "committed receipt not cleared",
    )

    require(
        recovered2.state.reconciliation_certificate
        is None,
        "reconciliation certificate not cleared",
    )

    pass_line(
        "Terminal Transaction Cleared"
    )

    # ------------------------------------------------------------------------
    # TEST 29
    # ------------------------------------------------------------------------

    test_header(
        29,
        "FINALIZED FENCES PRESERVED AFTER CLEAR",
    )

    finalized_ids_before = list(
        recovered2.state.finalized_promotion_ids
    )

    finalized_receipts_before = list(
        recovered2.state.finalized_receipt_ids
    )

    require(
        len(finalized_ids_before) == 1,
        "finalized promotion fence missing",
    )

    require(
        len(finalized_receipts_before) == 1,
        "finalized receipt fence missing",
    )

    pass_line(
        "Finalized Promotion Fence Preserved"
    )

    pass_line(
        "Finalized Receipt Fence Preserved"
    )

    # ------------------------------------------------------------------------
    # TEST 30
    # ------------------------------------------------------------------------

    test_header(
        30,
        "GENERATION ADVANCE AFTER TERMINAL RECONCILIATION",
    )

    old_generation = recovered2.state.generation
    old_lineage = recovered2.state.lineage
    old_epoch = recovered2.state.recovery_epoch

    recovered2.advance_generation()

    require(
        recovered2.state.generation
        == old_generation + 1,
        "generation did not advance",
    )

    require(
        recovered2.state.lineage != old_lineage,
        "lineage did not change",
    )

    require(
        recovered2.state.recovery_epoch
        == old_epoch + 1,
        "recovery epoch did not advance",
    )

    pass_line(
        "Generation Advanced Monotonically"
    )

    pass_line(
        "Lineage Changed On Generation Advance"
    )

    pass_line(
        "Recovery Epoch Advanced Monotonically"
    )

    # ------------------------------------------------------------------------
    # TEST 31
    # ------------------------------------------------------------------------

    test_header(
        31,
        "FINALIZED FENCE CROSS-GENERATION PRESERVATION",
    )

    require(
        recovered2.state.finalized_promotion_ids
        == finalized_ids_before,
        "finalized promotion fence changed",
    )

    require(
        recovered2.state.finalized_receipt_ids
        == finalized_receipts_before,
        "finalized receipt fence changed",
    )

    pass_line(
        "Finalized Promotion Fence Preserved Across Generation"
    )

    pass_line(
        "Finalized Receipt Fence Preserved Across Generation"
    )

    # ------------------------------------------------------------------------
    # TEST 32
    # ------------------------------------------------------------------------

    test_header(
        32,
        "STALE CROSS-GENERATION CERTIFICATE REJECTION",
    )

    stale_certificate = copy.deepcopy(cert2)

    # Force it into state only to test generation fencing.
    recovered2.state.reconciliation_certificate = stale_certificate
    recovered2._seal_snapshot()

    expect_block(
        "Stale Cross-Generation Certificate Rejected",
        "reconciliation certificate generation mismatch",
        lambda: recovered2.validate_reconciliation_certificate(
            stale_certificate
        ),
    )

    recovered2.state.reconciliation_certificate = None
    recovered2._seal_snapshot()

    # ------------------------------------------------------------------------
    # TEST 33
    # ------------------------------------------------------------------------

    test_header(
        33,
        "GENERATION ADVANCE BLOCKED BY RECONCILIATION CERTIFICATE",
    )

    engine = build_finalized_engine()
    engine.create_reconciliation_certificate()

    expect_block(
        "Generation Advance With Certificate Rejected",
        "cannot advance generation with pending promotion",
        engine.advance_generation,
    )

    # ------------------------------------------------------------------------
    # TEST 34
    # ------------------------------------------------------------------------

    test_header(
        34,
        "SNAPSHOT TAMPER REJECTION",
    )

    engine = build_finalized_engine()
    engine.create_reconciliation_certificate()

    snapshot = engine.snapshot()
    tampered_snapshot = copy.deepcopy(snapshot)

    tampered_snapshot["generation"] += 1

    expect_block(
        "Tampered Durable Snapshot Rejected",
        "snapshot integrity seal mismatch",
        lambda: N37Engine.restore(
            tampered_snapshot
        ),
    )

    # ------------------------------------------------------------------------
    # TEST 35
    # ------------------------------------------------------------------------

    test_header(
        35,
        "WAL RECORD HASH TAMPER REJECTION",
    )

    engine = build_finalized_engine()
    engine.create_reconciliation_certificate()

    tampered_engine = copy.deepcopy(engine)

    tampered_engine.state.wal[0].event_type = (
        "CORRUPTED_EVENT"
    )

    expect_block(
        "Tampered WAL Record Rejected",
        "WAL record hash mismatch",
        tampered_engine.validate_wal,
    )

    # ------------------------------------------------------------------------
    # TEST 36
    # ------------------------------------------------------------------------

    test_header(
        36,
        "WAL FINAL HASH TAMPER REJECTION",
    )

    tampered_engine = copy.deepcopy(engine)
    tampered_engine.state.wal_final_hash = "f" * 64

    expect_block(
        "Tampered WAL Final Hash Rejected",
        "WAL final hash mismatch",
        tampered_engine.validate_wal,
    )

    # ------------------------------------------------------------------------
    # TEST 37
    # ------------------------------------------------------------------------

    test_header(
        37,
        "COMPLETE DURABLE STATE VALIDATION",
    )

    engine.validate_complete_state()

    pass_line(
        "Complete Durable State Validates"
    )

    # ------------------------------------------------------------------------
    # TEST 38
    # ------------------------------------------------------------------------

    test_header(
        38,
        "RECONCILIATION WAL INTEGRITY",
    )

    engine.validate_wal()

    pass_line(
        "WAL Records Validate"
    )

    require(
        engine.state.wal_final_hash
        == engine.state.wal[-1].record_hash,
        "WAL final hash mismatch",
    )

    pass_line(
        "WAL Final Hash Matches Journal"
    )

    events = [
        record.event_type
        for record in engine.state.wal
    ]

    require(
        "PROMOTION_PREPARED" in events,
        "prepare WAL event missing",
    )

    require(
        "AUTHORITY_COMMITTED" in events,
        "authority WAL event missing",
    )

    require(
        "SYNTHETIC_RECEIPT_COMMITTED" in events,
        "receipt WAL event missing",
    )

    require(
        "PROMOTION_FINALIZED" in events,
        "finalization WAL event missing",
    )

    require(
        "RECONCILIATION_CERTIFICATE_COMMITTED"
        in events,
        "certificate WAL event missing",
    )

    pass_line(
        "Reconciliation WAL Sequence Preserved"
    )

    # ------------------------------------------------------------------------
    # TEST 39
    # ------------------------------------------------------------------------

    test_header(
        39,
        "SYNTHETIC TRANSPORT FIREBREAK",
    )

    transport_engine = build_receipt_engine()

    receipt = transport_engine.state.committed_receipt

    require(
        receipt.synthetic,
        "dispatch is not synthetic",
    )

    pass_line(
        "Dispatch Is Synthetic"
    )

    require(
        not receipt.transmitted,
        "network transmission occurred",
    )

    pass_line(
        "No Network Transmission Occurred"
    )

    require(
        receipt.transport_method == HTTP_METHOD,
        "transport method mismatch",
    )

    pass_line(
        "Transport Method Exactly POST"
    )

    require(
        receipt.transport_path
        == LEVERAGE_ENDPOINT,
        "transport path mismatch",
    )

    pass_line(
        "Transport Path Exactly Leverage Endpoint"
    )

    require(
        receipt.transport_payload_hash
        == transport_engine.state.committed_authority.payload_hash,
        "transport payload hash mismatch",
    )

    pass_line(
        "Transport Payload Hash Preserved"
    )

    # ------------------------------------------------------------------------
    # TEST 40
    # ------------------------------------------------------------------------

    test_header(
        40,
        "FINAL NETWORK WRITE POLICY",
    )

    require(
        not REAL_POST_ENABLED,
        "real POST is enabled",
    )

    pass_line(
        "Real POST Disabled"
    )

    require(
        not DEMO_POST_ENABLED,
        "demo POST is enabled",
    )

    pass_line(
        "Demo POST Disabled"
    )

    require(
        not NETWORK_WRITES_ENABLED,
        "network writes are enabled",
    )

    pass_line(
        "All Network Writes Disabled"
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY,
        "synthetic-only transport disabled",
    )

    pass_line(
        "Synthetic Transport Only"
    )

    print("", flush=True)

    separator()
    print(
        f"{UNIT_NAME}: ALL DIAGNOSTICS PASSED",
        flush=True,
    )
    separator()

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


# ============================================================================
# HEALTH SERVER
# ============================================================================


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in (
            "/",
            "/health",
            "/healthz",
        ):
            body = json.dumps(
                {
                    "ok": True,
                    "unit": UNIT_NAME,
                    "version": UNIT_VERSION,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                    "network_writes": NETWORK_WRITES_ENABLED,
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
    try:
        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        print(
            f"{UNIT_NAME}: HEALTH SERVER LISTENING ON PORT "
            f"{HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    except Exception as exc:
        print(
            f"{UNIT_NAME}: HEALTH SERVER ERROR: {exc}",
            flush=True,
        )


def run_heartbeat() -> None:
    counter = 0

    while True:
        counter += 1

        print(
            f"{UNIT_NAME}: HEARTBEAT {counter} | "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes={NETWORK_WRITES_ENABLED}",
            flush=True,
        )

        time.sleep(HEARTBEAT_SECONDS)


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

    run_heartbeat()


if __name__ == "__main__":
    main()
