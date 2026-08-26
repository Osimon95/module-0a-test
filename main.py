print("R28 UNIT N.36: MAIN.PY ENTERED", flush=True)

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

print("R28 UNIT N.36: IMPORTS COMPLETE", flush=True)

# ============================================================================
# R28 UNIT N.36
# ATOMIC PROMOTION TRANSACTION + CRASH-BOUNDARY RECOVERY +
# CROSS-RECORD CONSISTENCY + EXACTLY-ONCE SYNTHETIC DISPATCH
#
# SINGLE-FILE CORRECTED COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.36 INCREMENT OVER N.35:
#   - ATOMIC PROMOTION TRANSACTION ID
#   - AUTHORITY / RECEIPT / FINALIZATION CROSS-RECORD BINDING
#   - DURABLE TRANSACTION PHASE MARKERS
#   - CRASH RECOVERY AT EACH TRANSACTION BOUNDARY
#   - TORN / PARTIAL TRANSACTION REJECTION
#   - STALE TRANSACTION REJECTION
#   - TRANSACTION HASH / WAL BINDING
#   - EXACTLY-ONCE SYNTHETIC DISPATCH PRESERVATION
# ============================================================================

UNIT_NAME = "R28 UNIT N.36"
UNIT_VERSION = "N.36"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TARGET_LEVERAGE = "100"
TARGET_MARGIN_MODE = "ISOLATED"

INTEGRITY_KEY = b"R28-N36-LOCAL-INTEGRITY-KEY"
WAL_GENESIS_HASH = "0" * 64

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORITY_COMMITTED = "AUTHORITY_COMMITTED"
PHASE_RECEIPT_COMMITTED = "RECEIPT_COMMITTED"
PHASE_FINALIZED = "FINALIZED"

print("R28 UNIT N.36: CONSTANTS INITIALIZED", flush=True)


class LocalBlock(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalBlock(message)


def stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_hex(value: str) -> str:
    return hmac.new(
        INTEGRITY_KEY,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def make_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def separator() -> None:
    print("-" * 92, flush=True)


def test_header(number: int, title: str) -> None:
    separator()
    print(
        f"{UNIT_NAME} TEST {number}: {title}",
        flush=True,
    )
    separator()


def passed(label: str) -> None:
    print(
        f"{label:<82} ✅ PASS",
        flush=True,
    )


def local_block(message: str) -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK:",
        flush=True,
    )
    print(
        f"  {message}",
        flush=True,
    )


def expect_block(
    fn,
    expected_message: str,
    label: str,
) -> None:
    try:
        fn()

    except LocalBlock as exc:
        local_block(str(exc))

        require(
            str(exc) == expected_message,
            f"unexpected local block: {exc}",
        )

        passed(label)
        return

    raise AssertionError(
        f"expected LocalBlock: {expected_message}"
    )


# ============================================================================
# DURABLE RECORD MODELS
# ============================================================================

@dataclass
class PromotionIntent:
    promotion_id: str
    transaction_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    symbol: str
    method: str
    path: str

    payload: Dict[str, str]
    payload_hash: str

    intent_hash: str


@dataclass
class CommittedAuthority:
    promotion_id: str
    transaction_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    symbol: str
    method: str
    path: str

    payload_hash: str
    intent_hash: str
    authority_hash: str


@dataclass
class PromotionReceipt:
    promotion_id: str
    transaction_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    method: str
    path: str

    payload_hash: str
    authority_hash: str

    dispatch_id: str

    synthetic: bool
    transmitted: bool

    receipt_hash: str


@dataclass
class PromotionTransaction:
    transaction_id: str
    promotion_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    phase: str

    intent_hash: str
    authority_hash: Optional[str] = None
    receipt_hash: Optional[str] = None

    transaction_hash: str = ""


@dataclass
class WalRecord:
    sequence: int
    event: str

    transaction_id: str
    promotion_id: str
    phase: str

    data_hash: str

    previous_hash: str
    record_hash: str


@dataclass
class DurableState:
    generation: int = 1

    lineage: str = field(
        default_factory=lambda: make_id("lineage")
    )

    recovery_epoch: int = 1

    pending_intent: Optional[PromotionIntent] = None

    committed_authority: Optional[
        CommittedAuthority
    ] = None

    committed_receipt: Optional[
        PromotionReceipt
    ] = None

    active_transaction: Optional[
        PromotionTransaction
    ] = None

    finalized_promotion_ids: List[str] = field(
        default_factory=list
    )

    finalized_transaction_ids: List[str] = field(
        default_factory=list
    )

    dispatch_fence_ids: List[str] = field(
        default_factory=list
    )

    wal: List[WalRecord] = field(
        default_factory=list
    )

    wal_final_hash: str = WAL_GENESIS_HASH

    synthetic_dispatch_count: int = 0

    snapshot_seal: str = ""


# ============================================================================
# ENGINE
# ============================================================================

class Engine:

    def __init__(
        self,
        state: Optional[DurableState] = None,
    ) -> None:

        self.state = state or DurableState()

        self._refresh_snapshot_seal()

    # ========================================================================
    # PAYLOAD / HASH CONSTRUCTION
    # ========================================================================

    def _payload(self) -> Dict[str, str]:

        return {
            "symbol": SYMBOL,
            "marginMode": TARGET_MARGIN_MODE,
            "leverage": TARGET_LEVERAGE,
        }

    def _payload_hash(
        self,
        payload: Dict[str, str],
    ) -> str:

        return sha256_text(
            stable_json(payload)
        )

    def _intent_hash(
        self,
        promotion_id: str,
        transaction_id: str,
        generation: int,
        lineage: str,
        recovery_epoch: int,
        payload_hash: str,
    ) -> str:

        material = {
            "promotion_id": promotion_id,
            "transaction_id": transaction_id,

            "generation": generation,
            "lineage": lineage,
            "recovery_epoch": recovery_epoch,

            "symbol": SYMBOL,
            "method": HTTP_METHOD,
            "path": LEVERAGE_ENDPOINT,

            "payload_hash": payload_hash,
        }

        return sha256_text(
            stable_json(material)
        )

    def _authority_hash(
        self,
        intent: PromotionIntent,
    ) -> str:

        material = {
            "promotion_id":
                intent.promotion_id,

            "transaction_id":
                intent.transaction_id,

            "generation":
                intent.generation,

            "lineage":
                intent.lineage,

            "recovery_epoch":
                intent.recovery_epoch,

            "symbol":
                intent.symbol,

            "method":
                intent.method,

            "path":
                intent.path,

            "payload_hash":
                intent.payload_hash,

            "intent_hash":
                intent.intent_hash,
        }

        return sha256_text(
            stable_json(material)
        )

    def _receipt_hash(
        self,
        authority: CommittedAuthority,
        dispatch_id: str,
        synthetic: bool,
        transmitted: bool,
    ) -> str:

        material = {
            "promotion_id":
                authority.promotion_id,

            "transaction_id":
                authority.transaction_id,

            "generation":
                authority.generation,

            "lineage":
                authority.lineage,

            "recovery_epoch":
                authority.recovery_epoch,

            "method":
                authority.method,

            "path":
                authority.path,

            "payload_hash":
                authority.payload_hash,

            "authority_hash":
                authority.authority_hash,

            "dispatch_id":
                dispatch_id,

            "synthetic":
                synthetic,

            "transmitted":
                transmitted,
        }

        return sha256_text(
            stable_json(material)
        )

    def _transaction_hash(
        self,
        tx: PromotionTransaction,
    ) -> str:

        material = {
            "transaction_id":
                tx.transaction_id,

            "promotion_id":
                tx.promotion_id,

            "generation":
                tx.generation,

            "lineage":
                tx.lineage,

            "recovery_epoch":
                tx.recovery_epoch,

            "phase":
                tx.phase,

            "intent_hash":
                tx.intent_hash,

            "authority_hash":
                tx.authority_hash,

            "receipt_hash":
                tx.receipt_hash,
        }

        return sha256_text(
            stable_json(material)
        )

    # ========================================================================
    # WAL
    # ========================================================================

    def _append_wal(
        self,
        event: str,
        transaction_id: str,
        promotion_id: str,
        phase: str,
        data_hash: str,
    ) -> None:

        sequence = (
            len(self.state.wal) + 1
        )

        previous_hash = (
            self.state.wal_final_hash
        )

        material = stable_json(
            {
                "sequence":
                    sequence,

                "event":
                    event,

                "transaction_id":
                    transaction_id,

                "promotion_id":
                    promotion_id,

                "phase":
                    phase,

                "data_hash":
                    data_hash,

                "previous_hash":
                    previous_hash,
            }
        )

        record_hash = sha256_text(
            material
        )

        record = WalRecord(
            sequence=sequence,
            event=event,

            transaction_id=transaction_id,
            promotion_id=promotion_id,
            phase=phase,

            data_hash=data_hash,

            previous_hash=previous_hash,
            record_hash=record_hash,
        )

        self.state.wal.append(
            record
        )

        self.state.wal_final_hash = (
            record_hash
        )

        self._refresh_snapshot_seal()

    def validate_wal(self) -> None:

        previous = WAL_GENESIS_HASH

        for index, record in enumerate(
            self.state.wal,
            start=1,
        ):

            require(
                record.sequence == index,
                "WAL sequence mismatch",
            )

            require(
                record.previous_hash == previous,
                "WAL previous hash mismatch",
            )

            material = stable_json(
                {
                    "sequence":
                        record.sequence,

                    "event":
                        record.event,

                    "transaction_id":
                        record.transaction_id,

                    "promotion_id":
                        record.promotion_id,

                    "phase":
                        record.phase,

                    "data_hash":
                        record.data_hash,

                    "previous_hash":
                        record.previous_hash,
                }
            )

            require(
                record.record_hash
                == sha256_text(material),

                "WAL record hash mismatch",
            )

            previous = (
                record.record_hash
            )

        require(
            self.state.wal_final_hash
            == previous,

            "WAL final hash mismatch",
        )

    # ========================================================================
    # SNAPSHOT INTEGRITY
    # ========================================================================

    def _snapshot_material(
        self,
    ) -> str:

        data = asdict(
            self.state
        )

        data.pop(
            "snapshot_seal",
            None,
        )

        return stable_json(
            data
        )

    def _refresh_snapshot_seal(
        self,
    ) -> None:

        self.state.snapshot_seal = (
            hmac_hex(
                self._snapshot_material()
            )
        )

    def validate_snapshot(
        self,
    ) -> None:

        expected = hmac_hex(
            self._snapshot_material()
        )

        require(
            self.state.snapshot_seal
            == expected,

            "snapshot integrity seal mismatch",
        )

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        self._refresh_snapshot_seal()

        return copy.deepcopy(
            asdict(self.state)
        )

    # ========================================================================
    # SNAPSHOT RESTORE
    # ========================================================================

    @staticmethod
    def restore(
        snapshot: Dict[str, Any],
    ) -> "Engine":

        raw = copy.deepcopy(
            snapshot
        )

        def parse_intent(value):
            if value:
                return PromotionIntent(
                    **value
                )
            return None

        def parse_authority(value):
            if value:
                return CommittedAuthority(
                    **value
                )
            return None

        def parse_receipt(value):
            if value:
                return PromotionReceipt(
                    **value
                )
            return None

        def parse_transaction(value):
            if value:
                return PromotionTransaction(
                    **value
                )
            return None

        state = DurableState(

            generation=raw[
                "generation"
            ],

            lineage=raw[
                "lineage"
            ],

            recovery_epoch=raw[
                "recovery_epoch"
            ],

            pending_intent=parse_intent(
                raw.get(
                    "pending_intent"
                )
            ),

            committed_authority=
                parse_authority(
                    raw.get(
                        "committed_authority"
                    )
                ),

            committed_receipt=
                parse_receipt(
                    raw.get(
                        "committed_receipt"
                    )
                ),

            active_transaction=
                parse_transaction(
                    raw.get(
                        "active_transaction"
                    )
                ),

            finalized_promotion_ids=list(
                raw.get(
                    "finalized_promotion_ids",
                    [],
                )
            ),

            finalized_transaction_ids=list(
                raw.get(
                    "finalized_transaction_ids",
                    [],
                )
            ),

            dispatch_fence_ids=list(
                raw.get(
                    "dispatch_fence_ids",
                    [],
                )
            ),

            wal=[
                WalRecord(**record)
                for record
                in raw.get(
                    "wal",
                    [],
                )
            ],

            wal_final_hash=raw.get(
                "wal_final_hash",
                WAL_GENESIS_HASH,
            ),

            synthetic_dispatch_count=
                raw.get(
                    "synthetic_dispatch_count",
                    0,
                ),

            snapshot_seal=raw[
                "snapshot_seal"
            ],
        )

        engine = Engine.__new__(
            Engine
        )

        engine.state = state

        engine.validate_snapshot()
        engine.validate_wal()
        engine.validate_durable_state()

        return engine

    # ========================================================================
    # PREPARE PROMOTION
    # ========================================================================

    def prepare_promotion(
        self,
    ) -> PromotionIntent:

        require(
            self.state.pending_intent
            is None,

            "pending promotion already exists",
        )

        require(
            self.state.committed_authority
            is None,

            "committed authority already exists",
        )

        require(
            self.state.committed_receipt
            is None,

            "promotion receipt already committed",
        )

        require(
            self.state.active_transaction
            is None,

            "active promotion transaction already exists",
        )

        promotion_id = make_id(
            "promotion"
        )

        transaction_id = make_id(
            "txn"
        )

        payload = self._payload()

        payload_hash = (
            self._payload_hash(
                payload
            )
        )

        intent_hash = (
            self._intent_hash(
                promotion_id,
                transaction_id,

                self.state.generation,
                self.state.lineage,
                self.state.recovery_epoch,

                payload_hash,
            )
        )

        intent = PromotionIntent(

            promotion_id=
                promotion_id,

            transaction_id=
                transaction_id,

            generation=
                self.state.generation,

            lineage=
                self.state.lineage,

            recovery_epoch=
                self.state.recovery_epoch,

            symbol=
                SYMBOL,

            method=
                HTTP_METHOD,

            path=
                LEVERAGE_ENDPOINT,

            payload=
                payload,

            payload_hash=
                payload_hash,

            intent_hash=
                intent_hash,
        )

        transaction = PromotionTransaction(

            transaction_id=
                transaction_id,

            promotion_id=
                promotion_id,

            generation=
                self.state.generation,

            lineage=
                self.state.lineage,

            recovery_epoch=
                self.state.recovery_epoch,

            phase=
                PHASE_PREPARED,

            intent_hash=
                intent_hash,
        )

        transaction.transaction_hash = (
            self._transaction_hash(
                transaction
            )
        )

        self.state.pending_intent = (
            intent
        )

        self.state.active_transaction = (
            transaction
        )

        self._append_wal(

            "PROMOTION_PREPARED",

            transaction_id,

            promotion_id,

            PHASE_PREPARED,

            transaction.transaction_hash,
        )

        return intent

    # ========================================================================
    # INTENT VALIDATION
    # ========================================================================

    def _validate_intent(
        self,
        intent: PromotionIntent,
    ) -> None:

        require(
            intent.generation
            == self.state.generation,

            "promotion intent generation mismatch",
        )

        require(
            intent.lineage
            == self.state.lineage,

            "promotion intent lineage mismatch",
        )

        require(
            intent.recovery_epoch
            == self.state.recovery_epoch,

            "promotion intent recovery epoch mismatch",
        )

        require(
            intent.symbol
            == SYMBOL,

            "promotion intent symbol mismatch",
        )

        require(
            intent.method
            == HTTP_METHOD,

            "promotion intent method mismatch",
        )

        require(
            intent.path
            == LEVERAGE_ENDPOINT,

            "promotion intent path mismatch",
        )

        require(
            intent.payload_hash
            == self._payload_hash(
                intent.payload
            ),

            "promotion intent payload hash mismatch",
        )

        expected_hash = (
            self._intent_hash(

                intent.promotion_id,

                intent.transaction_id,

                intent.generation,

                intent.lineage,

                intent.recovery_epoch,

                intent.payload_hash,
            )
        )

        require(
            intent.intent_hash
            == expected_hash,

            "promotion intent hash mismatch",
        )

        require(
            intent.promotion_id
            not in self.state.finalized_promotion_ids,

            "promotion intent already finalized",
        )

        require(
            intent.transaction_id
            not in self.state.finalized_transaction_ids,

            "promotion transaction already finalized",
        )

    # ========================================================================
    # AUTHORITY COMMIT
    # ========================================================================

    def commit_authority(
        self,
    ) -> CommittedAuthority:

        require(
            self.state.pending_intent
            is not None,

            "pending promotion missing",
        )

        require(
            self.state.committed_authority
            is None,

            "committed authority already exists",
        )

        require(
            self.state.active_transaction
            is not None,

            "active promotion transaction missing",
        )

        intent = (
            self.state.pending_intent
        )

        transaction = (
            self.state.active_transaction
        )

        self._validate_intent(
            intent
        )

        require(
            transaction.transaction_id
            == intent.transaction_id,

            "transaction intent transaction ID mismatch",
        )

        require(
            transaction.promotion_id
            == intent.promotion_id,

            "transaction intent promotion ID mismatch",
        )

        require(
            transaction.phase
            == PHASE_PREPARED,

            "promotion transaction phase mismatch",
        )

        require(
            transaction.intent_hash
            == intent.intent_hash,

            "transaction intent hash mismatch",
        )

        authority_hash = (
            self._authority_hash(
                intent
            )
        )

        authority = CommittedAuthority(

            promotion_id=
                intent.promotion_id,

            transaction_id=
                intent.transaction_id,

            generation=
                intent.generation,

            lineage=
                intent.lineage,

            recovery_epoch=
                intent.recovery_epoch,

            symbol=
                intent.symbol,

            method=
                intent.method,

            path=
                intent.path,

            payload_hash=
                intent.payload_hash,

            intent_hash=
                intent.intent_hash,

            authority_hash=
                authority_hash,
        )

        self.state.committed_authority = (
            authority
        )

        transaction.phase = (
            PHASE_AUTHORITY_COMMITTED
        )

        transaction.authority_hash = (
            authority_hash
        )

        transaction.transaction_hash = (
            self._transaction_hash(
                transaction
            )
        )

        self._append_wal(

            "AUTHORITY_COMMITTED",

            transaction.transaction_id,

            transaction.promotion_id,

            transaction.phase,

            transaction.transaction_hash,
        )

        return authority

    # ========================================================================
    # AUTHORITY VALIDATION
    # ========================================================================

    def _validate_authority(
        self,
        authority: CommittedAuthority,
    ) -> None:

        require(
            authority.generation
            == self.state.generation,

            "committed authority generation mismatch",
        )

        require(
            authority.lineage
            == self.state.lineage,

            "committed authority lineage mismatch",
        )

        require(
            authority.recovery_epoch
            == self.state.recovery_epoch,

            "committed authority recovery epoch mismatch",
        )

        require(
            authority.symbol
            == SYMBOL,

            "committed authority symbol mismatch",
        )

        require(
            authority.method
            == HTTP_METHOD,

            "committed authority method mismatch",
        )

        require(
            authority.path
            == LEVERAGE_ENDPOINT,

            "committed authority path mismatch",
        )

        expected_hash = sha256_text(
            stable_json(
                {
                    "promotion_id":
                        authority.promotion_id,

                    "transaction_id":
                        authority.transaction_id,

                    "generation":
                        authority.generation,

                    "lineage":
                        authority.lineage,

                    "recovery_epoch":
                        authority.recovery_epoch,

                    "symbol":
                        authority.symbol,

                    "method":
                        authority.method,

                    "path":
                        authority.path,

                    "payload_hash":
                        authority.payload_hash,

                    "intent_hash":
                        authority.intent_hash,
                }
            )
        )

        require(
            authority.authority_hash
            == expected_hash,

            "committed authority hash mismatch",
        )

    # ========================================================================
    # SYNTHETIC DISPATCH
    # ========================================================================

    def synthetic_dispatch(
        self,
    ) -> PromotionReceipt:

        require(
            SYNTHETIC_TRANSPORT_ONLY,

            "synthetic transport required",
        )

        require(
            not NETWORK_WRITES_ENABLED,

            "network writes must remain disabled",
        )

        require(
            self.state.committed_authority
            is not None,

            "committed authority missing",
        )

        require(
            self.state.active_transaction
            is not None,

            "active promotion transaction missing",
        )

        require(
            self.state.committed_receipt
            is None,

            "promotion receipt already committed",
        )

        authority = (
            self.state.committed_authority
        )

        transaction = (
            self.state.active_transaction
        )

        self._validate_authority(
            authority
        )

        require(
            transaction.phase
            == PHASE_AUTHORITY_COMMITTED,

            "promotion transaction phase mismatch",
        )

        require(
            transaction.transaction_id
            == authority.transaction_id,

            "transaction authority transaction ID mismatch",
        )

        require(
            transaction.promotion_id
            == authority.promotion_id,

            "transaction authority promotion ID mismatch",
        )

        require(
            transaction.authority_hash
            == authority.authority_hash,

            "transaction authority hash mismatch",
        )

        require(
            authority.promotion_id
            not in self.state.dispatch_fence_ids,

            "promotion dispatch already fenced",
        )

        dispatch_id = make_id(
            "synthetic-dispatch"
        )

        receipt_hash = (
            self._receipt_hash(
                authority,
                dispatch_id,
                True,
                False,
            )
        )

        receipt = PromotionReceipt(

            promotion_id=
                authority.promotion_id,

            transaction_id=
                authority.transaction_id,

            generation=
                authority.generation,

            lineage=
                authority.lineage,

            recovery_epoch=
                authority.recovery_epoch,

            method=
                authority.method,

            path=
                authority.path,

            payload_hash=
                authority.payload_hash,

            authority_hash=
                authority.authority_hash,

            dispatch_id=
                dispatch_id,

            synthetic=True,

            transmitted=False,

            receipt_hash=
                receipt_hash,
        )

        self.state.committed_receipt = (
            receipt
        )

        self.state.dispatch_fence_ids.append(
            authority.promotion_id
        )

        self.state.synthetic_dispatch_count += 1

        transaction.phase = (
            PHASE_RECEIPT_COMMITTED
        )

        transaction.receipt_hash = (
            receipt_hash
        )

        transaction.transaction_hash = (
            self._transaction_hash(
                transaction
            )
        )

        self._append_wal(

            "RECEIPT_COMMITTED",

            transaction.transaction_id,

            transaction.promotion_id,

            transaction.phase,

            transaction.transaction_hash,
        )

        return receipt

    # ========================================================================
    # RECEIPT VALIDATION
    # ========================================================================

    def _validate_receipt(
        self,
        receipt: PromotionReceipt,
    ) -> None:

        require(
            receipt.synthetic is True,

            "promotion receipt is not synthetic",
        )

        require(
            receipt.transmitted is False,

            "promotion receipt indicates network transmission",
        )

        require(
            receipt.method
            == HTTP_METHOD,

            "promotion receipt method mismatch",
        )

        require(
            receipt.path
            == LEVERAGE_ENDPOINT,

            "promotion receipt path mismatch",
        )

        require(
            self.state.committed_authority
            is not None,

            "committed authority missing",
        )

        authority = (
            self.state.committed_authority
        )

        require(
            receipt.promotion_id
            == authority.promotion_id,

            "receipt authority promotion ID mismatch",
        )

        require(
            receipt.transaction_id
            == authority.transaction_id,

            "receipt authority transaction ID mismatch",
        )

        require(
            receipt.generation
            == authority.generation,

            "receipt authority generation mismatch",
        )

        require(
            receipt.lineage
            == authority.lineage,

            "receipt authority lineage mismatch",
        )

        require(
            receipt.recovery_epoch
            == authority.recovery_epoch,

            "receipt authority recovery epoch mismatch",
        )

        require(
            receipt.payload_hash
            == authority.payload_hash,

            "receipt authority payload hash mismatch",
        )

        require(
            receipt.authority_hash
            == authority.authority_hash,

            "receipt authority hash mismatch",
        )

        expected_hash = (
            self._receipt_hash(
                authority,
                receipt.dispatch_id,
                receipt.synthetic,
                receipt.transmitted,
            )
        )

        require(
            receipt.receipt_hash
            == expected_hash,

            "promotion receipt hash mismatch",
        )

    # ========================================================================
    # FINALIZATION
    # ========================================================================

    def finalize_promotion(
        self,
    ) -> PromotionReceipt:

        require(
            self.state.committed_receipt
            is not None,

            "promotion receipt missing",
        )

        receipt = (
            self.state.committed_receipt
        )

        # Permanent replay fences are checked before active-transaction
        # existence because finalization intentionally clears the active
        # transaction.

        require(
            receipt.promotion_id
            not in self.state.finalized_promotion_ids,

            "promotion receipt already finalized",
        )

        require(
            receipt.transaction_id
            not in self.state.finalized_transaction_ids,

            "promotion transaction already finalized",
        )

        require(
            self.state.committed_authority
            is not None,

            "committed authority missing",
        )

        require(
            self.state.active_transaction
            is not None,

            "active promotion transaction missing",
        )

        authority = (
            self.state.committed_authority
        )

        transaction = (
            self.state.active_transaction
        )

        self._validate_authority(
            authority
        )

        self._validate_receipt(
            receipt
        )

        require(
            transaction.phase
            == PHASE_RECEIPT_COMMITTED,

            "promotion transaction phase mismatch",
        )

        require(
            transaction.transaction_id
            == receipt.transaction_id,

            "transaction receipt transaction ID mismatch",
        )

        require(
            transaction.promotion_id
            == receipt.promotion_id,

            "transaction receipt promotion ID mismatch",
        )

        require(
            transaction.authority_hash
            == receipt.authority_hash,

            "transaction receipt authority hash mismatch",
        )

        require(
            transaction.receipt_hash
            == receipt.receipt_hash,

            "transaction receipt hash mismatch",
        )

        transaction.phase = (
            PHASE_FINALIZED
        )

        transaction.transaction_hash = (
            self._transaction_hash(
                transaction
            )
        )

        self.state.finalized_promotion_ids.append(
            receipt.promotion_id
        )

        self.state.finalized_transaction_ids.append(
            receipt.transaction_id
        )

        self._append_wal(

            "PROMOTION_FINALIZED",

            transaction.transaction_id,

            transaction.promotion_id,

            transaction.phase,

            transaction.transaction_hash,
        )

        # Durable authority / receipt / dispatch fence remain after
        # finalization. Only the pending intent and active transaction clear.

        self.state.pending_intent = None

        self.state.active_transaction = None

        self._refresh_snapshot_seal()

        return receipt

    # ========================================================================
    # RECOVERY
    # ========================================================================

    def recover(
        self,
    ) -> Optional[PromotionReceipt]:

        self.validate_snapshot()
        self.validate_wal()
        self.validate_durable_state()

        # No active transaction means this state is either finalized or idle.
        # Recovery must never redispatch a finalized transaction.

        if self.state.active_transaction is None:

            return (
                self.state.committed_receipt
            )

        transaction = (
            self.state.active_transaction
        )

        # --------------------------------------------------------------------
        # CRASH AFTER PREPARE
        # --------------------------------------------------------------------

        if transaction.phase == PHASE_PREPARED:

            require(
                self.state.pending_intent
                is not None,

                "prepared transaction missing intent",
            )

            require(
                self.state.committed_authority
                is None,

                "prepared transaction has unexpected authority",
            )

            require(
                self.state.committed_receipt
                is None,

                "prepared transaction has unexpected receipt",
            )

            self.commit_authority()

            self.synthetic_dispatch()

            return self.finalize_promotion()

        # --------------------------------------------------------------------
        # CRASH AFTER AUTHORITY COMMIT
        # --------------------------------------------------------------------

        if (
            transaction.phase
            == PHASE_AUTHORITY_COMMITTED
        ):

            require(
                self.state.committed_authority
                is not None,

                "authority transaction missing authority",
            )

            require(
                self.state.committed_receipt
                is None,

                "authority transaction has unexpected receipt",
            )

            self.synthetic_dispatch()

            return self.finalize_promotion()

        # --------------------------------------------------------------------
        # CRASH AFTER RECEIPT COMMIT
        # --------------------------------------------------------------------

        if (
            transaction.phase
            == PHASE_RECEIPT_COMMITTED
        ):

            require(
                self.state.committed_authority
                is not None,

                "receipt transaction missing authority",
            )

            require(
                self.state.committed_receipt
                is not None,

                "receipt transaction missing receipt",
            )

            return self.finalize_promotion()

        # --------------------------------------------------------------------
        # FINALIZED TRANSACTION
        # --------------------------------------------------------------------

        if (
            transaction.phase
            == PHASE_FINALIZED
        ):

            require(
                transaction.transaction_id
                in self.state.finalized_transaction_ids,

                "finalized transaction fence missing",
            )

            return (
                self.state.committed_receipt
            )

        raise LocalBlock(
            "unknown promotion transaction phase"
        )

    # ========================================================================
    # COMPLETE DURABLE STATE VALIDATION
    # ========================================================================

    def validate_durable_state(
        self,
    ) -> None:

        state = self.state

        # --------------------------------------------------------------------
        # INTENT
        # --------------------------------------------------------------------

        if state.pending_intent is not None:

            self._validate_intent(
                state.pending_intent
            )

        # --------------------------------------------------------------------
        # AUTHORITY
        # --------------------------------------------------------------------

        if state.committed_authority is not None:

            self._validate_authority(
                state.committed_authority
            )

        # --------------------------------------------------------------------
        # RECEIPT
        # --------------------------------------------------------------------

        if state.committed_receipt is not None:

            self._validate_receipt(
                state.committed_receipt
            )

        # --------------------------------------------------------------------
        # ACTIVE TRANSACTION
        # --------------------------------------------------------------------

        transaction = (
            state.active_transaction
        )

        if transaction is not None:

            require(
                transaction.generation
                == state.generation,

                "promotion transaction generation mismatch",
            )

            require(
                transaction.lineage
                == state.lineage,

                "promotion transaction lineage mismatch",
            )

            require(
                transaction.recovery_epoch
                == state.recovery_epoch,

                "promotion transaction recovery epoch mismatch",
            )

            require(
                transaction.transaction_hash
                == self._transaction_hash(
                    transaction
                ),

                "promotion transaction hash mismatch",
            )

            require(
                state.pending_intent
                is not None,

                "active transaction missing promotion intent",
            )

            intent = (
                state.pending_intent
            )

            require(
                transaction.transaction_id
                == intent.transaction_id,

                "transaction intent transaction ID mismatch",
            )

            require(
                transaction.promotion_id
                == intent.promotion_id,

                "transaction intent promotion ID mismatch",
            )

            require(
                transaction.intent_hash
                == intent.intent_hash,

                "transaction intent hash mismatch",
            )

            # ----------------------------------------------------------------
            # PREPARED
            # ----------------------------------------------------------------

            if (
                transaction.phase
                == PHASE_PREPARED
            ):

                require(
                    state.committed_authority
                    is None,

                    "prepared transaction has unexpected authority",
                )

                require(
                    state.committed_receipt
                    is None,

                    "prepared transaction has unexpected receipt",
                )

            # ----------------------------------------------------------------
            # AUTHORITY COMMITTED
            # ----------------------------------------------------------------

            elif (
                transaction.phase
                == PHASE_AUTHORITY_COMMITTED
            ):

                require(
                    state.committed_authority
                    is not None,

                    "authority transaction missing authority",
                )

                require(
                    state.committed_receipt
                    is None,

                    "authority transaction has unexpected receipt",
                )

                require(
                    transaction.authority_hash
                    == state.committed_authority.authority_hash,

                    "transaction authority hash mismatch",
                )

            # ----------------------------------------------------------------
            # RECEIPT COMMITTED
            # ----------------------------------------------------------------

            elif (
                transaction.phase
                == PHASE_RECEIPT_COMMITTED
            ):

                require(
                    state.committed_authority
                    is not None,

                    "receipt transaction missing authority",
                )

                require(
                    state.committed_receipt
                    is not None,

                    "receipt transaction missing receipt",
                )

                require(
                    transaction.authority_hash
                    == state.committed_authority.authority_hash,

                    "transaction authority hash mismatch",
                )

                require(
                    transaction.receipt_hash
                    == state.committed_receipt.receipt_hash,

                    "transaction receipt hash mismatch",
                )

            # ----------------------------------------------------------------
            # FINALIZED
            # ----------------------------------------------------------------

            elif (
                transaction.phase
                == PHASE_FINALIZED
            ):

                require(
                    transaction.transaction_id
                    in state.finalized_transaction_ids,

                    "finalized transaction fence missing",
                )

            else:

                raise LocalBlock(
                    "unknown promotion transaction phase"
                )

        # --------------------------------------------------------------------
        # RECEIPT MUST HAVE A DISPATCH FENCE
        # --------------------------------------------------------------------

        if (
            state.committed_receipt
            is not None
        ):

            require(
                state.committed_receipt.promotion_id
                in state.dispatch_fence_ids,

                "committed receipt missing dispatch fence",
            )

        # --------------------------------------------------------------------
        # FINALIZED PROMOTIONS MUST RETAIN THEIR DISPATCH FENCE
        # --------------------------------------------------------------------

        for promotion_id in (
            state.finalized_promotion_ids
        ):

            require(
                promotion_id
                in state.dispatch_fence_ids,

                "finalized promotion missing dispatch fence",
            )

        # --------------------------------------------------------------------
        # EXACTLY-ONCE COUNTER CONSISTENCY
        # --------------------------------------------------------------------

        require(
            state.synthetic_dispatch_count
            == len(
                state.dispatch_fence_ids
            ),

            "synthetic dispatch count mismatch",
        )

    def validate_all(
        self,
    ) -> None:

        self.validate_snapshot()

        self.validate_wal()

        self.validate_durable_state()

    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(
        self,
    ) -> None:

        # Prefer the most advanced durable blocker so diagnostics identify the
        # exact crash boundary preventing generation transition.

        if (
            self.state.committed_receipt
            is not None
        ):

            require(
                self.state.committed_receipt.promotion_id
                in self.state.finalized_promotion_ids,

                "cannot advance generation with committed receipt",
            )

        if (
            self.state.committed_authority
            is not None
        ):

            require(
                self.state.committed_authority.promotion_id
                in self.state.finalized_promotion_ids,

                "cannot advance generation with committed authority",
            )

        require(
            self.state.pending_intent
            is None,

            "cannot advance generation with pending promotion",
        )

        require(
            self.state.active_transaction
            is None,

            "cannot advance generation with active transaction",
        )

        self.state.generation += 1

        self.state.lineage = make_id(
            "lineage"
        )

        self.state.recovery_epoch += 1

        generation_hash = sha256_text(
            stable_json(
                {
                    "generation":
                        self.state.generation,

                    "lineage":
                        self.state.lineage,

                    "recovery_epoch":
                        self.state.recovery_epoch,
                }
            )
        )

        self._append_wal(

            "GENERATION_ADVANCED",

            "-",

            "-",

            "GENERATION",

            generation_hash,
        )


# ============================================================================
# CLONE / RESTART HELPER
# ============================================================================

def clone_engine(
    engine: Engine,
) -> Engine:

    return Engine.restore(
        engine.snapshot()
    )


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def run_diagnostics() -> None:

    separator()

    print(
        f"{UNIT_NAME}: "
        "ATOMIC PROMOTION TRANSACTION DIAGNOSTICS",
        flush=True,
    )

    separator()

    # ========================================================================
    # TEST 1
    # ========================================================================

    test_header(
        1,
        "INITIAL STATE",
    )

    engine = Engine()

    require(
        engine.state.generation
        == 1,

        "initial generation mismatch",
    )

    passed(
        "Initial Generation Is One"
    )

    require(
        engine.state.recovery_epoch
        == 1,

        "initial recovery epoch mismatch",
    )

    passed(
        "Initial Recovery Epoch Is One"
    )

    require(
        engine.state.synthetic_dispatch_count
        == 0,

        "initial dispatch count mismatch",
    )

    passed(
        "Initial Synthetic Dispatch Count Is Zero"
    )

    # ========================================================================
    # TEST 2
    # ========================================================================

    test_header(
        2,
        "PREPARE ATOMIC PROMOTION TRANSACTION",
    )

    intent = (
        engine.prepare_promotion()
    )

    require(
        engine.state.active_transaction
        is not None,

        "transaction not created",
    )

    require(
        engine.state.active_transaction.phase
        == PHASE_PREPARED,

        "transaction not prepared",
    )

    passed(
        "Promotion Transaction Prepared"
    )

    require(
        intent.transaction_id
        == engine.state.active_transaction.transaction_id,

        "transaction ID not bound",
    )

    passed(
        "Intent Bound To Transaction ID"
    )

    require(
        intent.payload_hash
        == sha256_text(
            stable_json(
                intent.payload
            )
        ),

        "payload hash mismatch",
    )

    passed(
        "Intent Payload Hash Established"
    )

    # ========================================================================
    # TEST 3
    # ========================================================================

    test_header(
        3,
        "AUTHORITY COMMIT",
    )

    authority = (
        engine.commit_authority()
    )

    require(
        engine.state.active_transaction.phase
        == PHASE_AUTHORITY_COMMITTED,

        "authority phase mismatch",
    )

    passed(
        "Authority Committed Atomically"
    )

    require(
        authority.transaction_id
        == intent.transaction_id,

        "authority transaction mismatch",
    )

    passed(
        "Authority Bound To Transaction"
    )

    require(
        engine.state.active_transaction.authority_hash
        == authority.authority_hash,

        "authority hash not bound",
    )

    passed(
        "Transaction Bound To Authority Hash"
    )

    # ========================================================================
    # TEST 4
    # ========================================================================

    test_header(
        4,
        "SYNTHETIC RECEIPT COMMIT",
    )

    receipt = (
        engine.synthetic_dispatch()
    )

    require(
        engine.state.active_transaction.phase
        == PHASE_RECEIPT_COMMITTED,

        "receipt phase mismatch",
    )

    passed(
        "Synthetic Receipt Committed Atomically"
    )

    require(
        receipt.transaction_id
        == authority.transaction_id,

        "receipt transaction mismatch",
    )

    passed(
        "Receipt Bound To Transaction"
    )

    require(
        receipt.synthetic
        and not receipt.transmitted,

        "transport firebreak failure",
    )

    passed(
        "Receipt Confirms Synthetic Non-Transmission"
    )

    require(
        engine.state.synthetic_dispatch_count
        == 1,

        "dispatch count mismatch",
    )

    passed(
        "Exactly One Synthetic Dispatch Recorded"
    )

    # ========================================================================
    # TEST 5
    # ========================================================================

    test_header(
        5,
        "FINALIZATION",
    )

    final_receipt = (
        engine.finalize_promotion()
    )

    require(
        final_receipt.promotion_id
        in engine.state.finalized_promotion_ids,

        "promotion not finalized",
    )

    passed(
        "Promotion Finalized"
    )

    require(
        final_receipt.transaction_id
        in engine.state.finalized_transaction_ids,

        "transaction not finalized",
    )

    passed(
        "Transaction Finalized"
    )

    require(
        engine.state.active_transaction
        is None,

        "active transaction not cleared",
    )

    passed(
        "Active Transaction Cleared"
    )

    require(
        engine.state.pending_intent
        is None,

        "pending intent not cleared",
    )

    passed(
        "Pending Intent Cleared"
    )

    # ========================================================================
    # TEST 6
    # ========================================================================

    test_header(
        6,
        "FINALIZED RESTART",
    )

    restarted = clone_engine(
        engine
    )

    require(
        final_receipt.promotion_id
        in restarted.state.finalized_promotion_ids,

        "finalized promotion lost",
    )

    passed(
        "Finalized Promotion Survived Restart"
    )

    require(
        restarted.state.committed_authority
        is not None,

        "authority lost",
    )

    passed(
        "Committed Authority Survived Restart"
    )

    require(
        restarted.state.committed_receipt
        is not None,

        "receipt lost",
    )

    passed(
        "Committed Receipt Survived Restart"
    )

    require(
        restarted.state.synthetic_dispatch_count
        == 1,

        "dispatch count changed",
    )

    passed(
        "Exactly-Once Dispatch Fence Survived Restart"
    )

    # ========================================================================
    # TEST 7
    # ========================================================================

    test_header(
        7,
        "CRASH AFTER PREPARE",
    )

    engine = Engine()

    engine.prepare_promotion()

    before = (
        engine.state.synthetic_dispatch_count
    )

    restarted = clone_engine(
        engine
    )

    recovered = (
        restarted.recover()
    )

    require(
        recovered
        is not None,

        "prepared recovery failed",
    )

    passed(
        "Prepared Transaction Recovered"
    )

    require(
        restarted.state.synthetic_dispatch_count
        == before + 1,

        "prepared recovery dispatch mismatch",
    )

    passed(
        "Prepared Recovery Produced Exactly One Synthetic Dispatch"
    )

    require(
        recovered.promotion_id
        in restarted.state.finalized_promotion_ids,

        "prepared recovery not finalized",
    )

    passed(
        "Prepared Recovery Finalized Transaction"
    )

    # ========================================================================
    # TEST 8
    # ========================================================================

    test_header(
        8,
        "CRASH AFTER AUTHORITY COMMIT",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    before = (
        engine.state.synthetic_dispatch_count
    )

    restarted = clone_engine(
        engine
    )

    restarted.recover()

    require(
        restarted.state.synthetic_dispatch_count
        == before + 1,

        "authority recovery dispatch mismatch",
    )

    passed(
        "Authority Recovery Produced Exactly One Synthetic Dispatch"
    )

    require(
        restarted.state.committed_receipt
        is not None,

        "receipt not created",
    )

    passed(
        "Authority Recovery Created Receipt"
    )

    require(
        restarted.state.committed_receipt.promotion_id
        in restarted.state.finalized_promotion_ids,

        "authority recovery not finalized",
    )

    passed(
        "Authority Recovery Finalized"
    )

    # ========================================================================
    # TEST 9
    # ========================================================================

    test_header(
        9,
        "CRASH AFTER RECEIPT COMMIT",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    old_receipt = (
        engine.synthetic_dispatch()
    )

    before = (
        engine.state.synthetic_dispatch_count
    )

    restarted = clone_engine(
        engine
    )

    recovered = (
        restarted.recover()
    )

    require(
        recovered is not None
        and recovered.receipt_hash
        == old_receipt.receipt_hash,

        "receipt not reused",
    )

    passed(
        "Committed Receipt Survived Restart"
    )

    passed(
        "Recovery Reused Existing Receipt"
    )

    require(
        restarted.state.synthetic_dispatch_count
        == before,

        "second dispatch occurred",
    )

    passed(
        "No Second Dispatch Occurred"
    )

    require(
        old_receipt.promotion_id
        in restarted.state.finalized_promotion_ids,

        "recovered receipt not finalized",
    )

    passed(
        "Recovered Receipt Finalized"
    )

    # ========================================================================
    # TEST 10
    # ========================================================================

    test_header(
        10,
        "CRASH AFTER FINALIZATION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    engine.synthetic_dispatch()

    engine.finalize_promotion()

    before = (
        engine.state.synthetic_dispatch_count
    )

    restarted = clone_engine(
        engine
    )

    restarted.recover()

    require(
        restarted.state.synthetic_dispatch_count
        == before,

        "finalized recovery redispatched",
    )

    passed(
        "Finalized Transaction Survives Restart"
    )

    passed(
        "Finalized Recovery Did Not Redispatch"
    )

    passed(
        "Durable Finalized Fences Preserved"
    )

    # ========================================================================
    # TEST 11
    # ========================================================================

    test_header(
        11,
        "TORN PREPARED TRANSACTION REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "pending_intent"
    ] = None

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "active transaction missing promotion intent",

        "Torn Prepared Transaction Rejected",
    )

    # ========================================================================
    # TEST 12
    # ========================================================================

    test_header(
        12,
        "TORN AUTHORITY TRANSACTION REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    bad = engine.snapshot()

    bad[
        "committed_authority"
    ] = None

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "authority transaction missing authority",

        "Torn Authority Transaction Rejected",
    )

    # ========================================================================
    # TEST 13
    # ========================================================================

    test_header(
        13,
        "TORN RECEIPT TRANSACTION REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    engine.synthetic_dispatch()

    bad = engine.snapshot()

    bad[
        "committed_receipt"
    ] = None

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "receipt transaction missing receipt",

        "Torn Receipt Transaction Rejected",
    )

    # ========================================================================
    # TEST 14
    # ========================================================================

    test_header(
        14,
        "TRANSACTION ID MISMATCH REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "active_transaction"
    ][
        "transaction_id"
    ] = make_id(
        "forged-txn"
    )

    transaction = PromotionTransaction(
        **bad["active_transaction"]
    )

    transaction.transaction_hash = ""

    transaction.transaction_hash = (
        engine._transaction_hash(
            transaction
        )
    )

    bad[
        "active_transaction"
    ][
        "transaction_hash"
    ] = transaction.transaction_hash

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "transaction intent transaction ID mismatch",

        "Cross-Record Transaction ID Mismatch Rejected",
    )

    # ========================================================================
    # TEST 15
    # ========================================================================

    test_header(
        15,
        "PROMOTION ID MISMATCH REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "active_transaction"
    ][
        "promotion_id"
    ] = make_id(
        "forged-promotion"
    )

    transaction = PromotionTransaction(
        **bad["active_transaction"]
    )

    transaction.transaction_hash = ""

    transaction.transaction_hash = (
        engine._transaction_hash(
            transaction
        )
    )

    bad[
        "active_transaction"
    ][
        "transaction_hash"
    ] = transaction.transaction_hash

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "transaction intent promotion ID mismatch",

        "Cross-Record Promotion ID Mismatch Rejected",
    )

    # ========================================================================
    # TEST 16
    # ========================================================================

    test_header(
        16,
        "INTENT HASH MISMATCH REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "active_transaction"
    ][
        "intent_hash"
    ] = "f" * 64

    transaction = PromotionTransaction(
        **bad["active_transaction"]
    )

    transaction.transaction_hash = ""

    transaction.transaction_hash = (
        engine._transaction_hash(
            transaction
        )
    )

    bad[
        "active_transaction"
    ][
        "transaction_hash"
    ] = transaction.transaction_hash

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "transaction intent hash mismatch",

        "Cross-Record Intent Hash Mismatch Rejected",
    )

    # ========================================================================
    # TEST 17
    # ========================================================================

    test_header(
        17,
        "AUTHORITY HASH MISMATCH REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    bad = engine.snapshot()

    bad[
        "active_transaction"
    ][
        "authority_hash"
    ] = "a" * 64

    transaction = PromotionTransaction(
        **bad["active_transaction"]
    )

    transaction.transaction_hash = ""

    transaction.transaction_hash = (
        engine._transaction_hash(
            transaction
        )
    )

    bad[
        "active_transaction"
    ][
        "transaction_hash"
    ] = transaction.transaction_hash

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "transaction authority hash mismatch",

        "Cross-Record Authority Hash Mismatch Rejected",
    )

    # ========================================================================
    # TEST 18
    # ========================================================================

    test_header(
        18,
        "RECEIPT HASH MISMATCH REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    engine.synthetic_dispatch()

    bad = engine.snapshot()

    bad[
        "active_transaction"
    ][
        "receipt_hash"
    ] = "b" * 64

    transaction = PromotionTransaction(
        **bad["active_transaction"]
    )

    transaction.transaction_hash = ""

    transaction.transaction_hash = (
        engine._transaction_hash(
            transaction
        )
    )

    bad[
        "active_transaction"
    ][
        "transaction_hash"
    ] = transaction.transaction_hash

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "transaction receipt hash mismatch",

        "Cross-Record Receipt Hash Mismatch Rejected",
    )

    # ========================================================================
    # TEST 19
    # ========================================================================

    test_header(
        19,
        "TRANSACTION PHASE HASH TAMPER REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "active_transaction"
    ][
        "phase"
    ] = PHASE_AUTHORITY_COMMITTED

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "promotion transaction hash mismatch",

        "Transaction Phase Tamper Rejected",
    )

    # ========================================================================
    # TEST 20
    # ========================================================================

    test_header(
        20,
        "STALE GENERATION TRANSACTION REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "generation"
    ] += 1

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "promotion intent generation mismatch",

        "Stale Generation Transaction Rejected",
    )

    # ========================================================================
    # TEST 21
    # ========================================================================

    test_header(
        21,
        "STALE LINEAGE TRANSACTION REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "lineage"
    ] = make_id(
        "new-lineage"
    )

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "promotion intent lineage mismatch",

        "Stale Lineage Transaction Rejected",
    )

    # ========================================================================
    # TEST 22
    # ========================================================================

    test_header(
        22,
        "STALE RECOVERY EPOCH TRANSACTION REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "recovery_epoch"
    ] += 1

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "promotion intent recovery epoch mismatch",

        "Stale Recovery Epoch Transaction Rejected",
    )

    # ========================================================================
    # TEST 23
    # ========================================================================

    test_header(
        23,
        "SECOND DISPATCH REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    engine.synthetic_dispatch()

    expect_block(

        engine.synthetic_dispatch,

        "promotion receipt already committed",

        "Second Synthetic Dispatch Rejected",
    )

    # ========================================================================
    # TEST 24
    # ========================================================================

    test_header(
        24,
        "RECEIPT REPLAY FINALIZATION REJECTION",
    )

    engine.finalize_promotion()

    expect_block(

        engine.finalize_promotion,

        "promotion receipt already finalized",

        "Finalized Receipt Replay Rejected",
    )

    # ========================================================================
    # TEST 25
    # ========================================================================

    test_header(
        25,
        "SECOND AUTHORITY COMMIT REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    expect_block(

        engine.commit_authority,

        "committed authority already exists",

        "Second Authority Commit Rejected",
    )

    # ========================================================================
    # TEST 26
    # ========================================================================

    test_header(
        26,
        "GENERATION ADVANCE",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    engine.synthetic_dispatch()

    engine.finalize_promotion()

    old_generation = (
        engine.state.generation
    )

    old_lineage = (
        engine.state.lineage
    )

    old_epoch = (
        engine.state.recovery_epoch
    )

    old_finalized = list(
        engine.state.finalized_promotion_ids
    )

    old_receipt_hash = (
        engine.state.committed_receipt.receipt_hash
    )

    engine.advance_generation()

    require(
        engine.state.generation
        == old_generation + 1,

        "generation did not advance",
    )

    passed(
        "Generation Advanced Monotonically"
    )

    require(
        engine.state.lineage
        != old_lineage,

        "lineage did not change",
    )

    passed(
        "Lineage Changed On Generation Advance"
    )

    require(
        engine.state.recovery_epoch
        == old_epoch + 1,

        "recovery epoch did not advance",
    )

    passed(
        "Recovery Epoch Advanced Monotonically"
    )

    require(
        engine.state.finalized_promotion_ids
        == old_finalized,

        "finalized fence lost",
    )

    passed(
        "Finalized Promotion Fence Preserved"
    )

    require(
        engine.state.committed_receipt.receipt_hash
        == old_receipt_hash,

        "receipt changed across generation",
    )

    passed(
        "Finalized Receipt Preserved Across Generation"
    )

    # ========================================================================
    # TEST 27
    # ========================================================================

    test_header(
        27,
        "GENERATION ADVANCE BLOCKED BY PREPARED TRANSACTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    expect_block(

        engine.advance_generation,

        "cannot advance generation with pending promotion",

        "Generation Advance With Prepared Transaction Rejected",
    )

    # ========================================================================
    # TEST 28
    # ========================================================================

    test_header(
        28,
        "GENERATION ADVANCE BLOCKED BY AUTHORITY TRANSACTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    expect_block(

        engine.advance_generation,

        "cannot advance generation with committed authority",

        "Generation Advance With Authority Transaction Rejected",
    )

    # ========================================================================
    # TEST 29
    # ========================================================================

    test_header(
        29,
        "GENERATION ADVANCE BLOCKED BY RECEIPT TRANSACTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    engine.synthetic_dispatch()

    expect_block(

        engine.advance_generation,

        "cannot advance generation with committed receipt",

        "Generation Advance With Receipt Transaction Rejected",
    )

    # ========================================================================
    # TEST 30
    # ========================================================================

    test_header(
        30,
        "SNAPSHOT TAMPER REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "generation"
    ] = 999

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "snapshot integrity seal mismatch",

        "Tampered Durable Snapshot Rejected",
    )

    # ========================================================================
    # TEST 31
    # ========================================================================

    test_header(
        31,
        "WAL RECORD HASH TAMPER REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "wal"
    ][0][
        "record_hash"
    ] = "e" * 64

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "WAL record hash mismatch",

        "Tampered WAL Record Rejected",
    )

    # ========================================================================
    # TEST 32
    # ========================================================================

    test_header(
        32,
        "WAL FINAL HASH TAMPER REJECTION",
    )

    engine = Engine()

    engine.prepare_promotion()

    bad = engine.snapshot()

    bad[
        "wal_final_hash"
    ] = "d" * 64

    data = copy.deepcopy(
        bad
    )

    data.pop(
        "snapshot_seal",
        None,
    )

    bad[
        "snapshot_seal"
    ] = hmac_hex(
        stable_json(data)
    )

    expect_block(

        lambda: Engine.restore(
            bad
        ),

        "WAL final hash mismatch",

        "Tampered WAL Final Hash Rejected",
    )

    # ========================================================================
    # TEST 33
    # ========================================================================

    test_header(
        33,
        "COMPLETE DURABLE STATE VALIDATION",
    )

    engine = Engine()

    engine.prepare_promotion()

    engine.commit_authority()

    engine.synthetic_dispatch()

    engine.finalize_promotion()

    engine.validate_all()

    passed(
        "Complete Durable State Validates"
    )

    # ========================================================================
    # TEST 34
    # ========================================================================

    test_header(
        34,
        "WAL INTEGRITY",
    )

    engine.validate_wal()

    passed(
        "WAL Records Validate"
    )

    require(
        engine.state.wal_final_hash
        == engine.state.wal[-1].record_hash,

        "WAL final hash mismatch",
    )

    passed(
        "WAL Final Hash Matches Journal"
    )

    events = [
        record.event
        for record
        in engine.state.wal
    ]

    require(
        events
        == [
            "PROMOTION_PREPARED",
            "AUTHORITY_COMMITTED",
            "RECEIPT_COMMITTED",
            "PROMOTION_FINALIZED",
        ],

        "transaction WAL event sequence mismatch",
    )

    passed(
        "Atomic Transaction WAL Sequence Preserved"
    )

    # ========================================================================
    # TEST 35
    # ========================================================================

    test_header(
        35,
        "SYNTHETIC TRANSPORT FIREBREAK",
    )

    receipt = (
        engine.state.committed_receipt
    )

    require(
        receipt is not None
        and receipt.synthetic,

        "dispatch is not synthetic",
    )

    passed(
        "Dispatch Is Synthetic"
    )

    require(
        receipt.transmitted
        is False,

        "network transmission occurred",
    )

    passed(
        "No Network Transmission Occurred"
    )

    require(
        receipt.method
        == HTTP_METHOD,

        "transport method mismatch",
    )

    passed(
        "Transport Method Exactly POST"
    )

    require(
        receipt.path
        == LEVERAGE_ENDPOINT,

        "transport path mismatch",
    )

    passed(
        "Transport Path Exactly Leverage Endpoint"
    )

    require(
        receipt.payload_hash
        == engine.state.committed_authority.payload_hash,

        "transport payload hash mismatch",
    )

    passed(
        "Transport Payload Hash Preserved"
    )

    # ========================================================================
    # TEST 36
    # ========================================================================

    test_header(
        36,
        "FINAL NETWORK WRITE POLICY",
    )

    require(
        REAL_POST_ENABLED
        is False,

        "real POST unexpectedly enabled",
    )

    passed(
        "Real POST Disabled"
    )

    require(
        DEMO_POST_ENABLED
        is False,

        "demo POST unexpectedly enabled",
    )

    passed(
        "Demo POST Disabled"
    )

    require(
        NETWORK_WRITES_ENABLED
        is False,

        "network writes unexpectedly enabled",
    )

    passed(
        "All Network Writes Disabled"
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY
        is True,

        "synthetic-only policy disabled",
    )

    passed(
        "Synthetic Transport Only"
    )

    print(
        "",
        flush=True,
    )

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
# OPTIONAL HEALTH SERVER
# ============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

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
                    "unit":
                        UNIT_NAME,

                    "version":
                        UNIT_VERSION,

                    "status":
                        "ok",

                    "real_post":
                        REAL_POST_ENABLED,

                    "demo_post":
                        DEMO_POST_ENABLED,

                    "network_writes":
                        NETWORK_WRITES_ENABLED,

                    "synthetic_only":
                        SYNTHETIC_TRANSPORT_ONLY,
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
                    len(body)
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
        fmt: str,
        *args: Any,
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
                f"{UNIT_NAME}: "
                f"HEALTH SERVER LISTENING ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except OSError as exc:

            print(
                f"{UNIT_NAME}: "
                f"HEALTH SERVER NOT STARTED: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()


# ============================================================================
# HEARTBEAT
# ============================================================================

def heartbeat_loop() -> None:

    counter = 1

    interval = float(
        os.environ.get(
            "HEARTBEAT_SECONDS",
            "30",
        )
    )

    max_heartbeats_raw = (
        os.environ.get(
            "MAX_HEARTBEATS",
            "",
        ).strip()
    )

    if max_heartbeats_raw:

        max_heartbeats = int(
            max_heartbeats_raw
        )

    else:

        max_heartbeats = None

    while True:

        print(
            f"{UNIT_NAME}: "
            f"HEARTBEAT {counter} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes="
            f"{NETWORK_WRITES_ENABLED}",
            flush=True,
        )

        if (
            max_heartbeats
            is not None
            and counter
            >= max_heartbeats
        ):

            break

        counter += 1

        time.sleep(
            interval
        )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    run_diagnostics()

    start_health_server()

    heartbeat_loop()
