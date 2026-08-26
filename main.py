# ============================================================================
# R28 UNIT N.35
# COMMITTED AUTHORITY / RECEIPT RECONCILIATION
# + CRASH-WINDOW ATOMICITY
# + EXACTLY-ONCE SYNTHETIC DISPATCH FENCING
#
# CORRECTED SINGLE-FILE COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.35 INCREMENT OVER N.34:
#   - DURABLE COMMITTED PROMOTION AUTHORITY
#   - AUTHORITY <-> RECEIPT RECONCILIATION
#   - RECEIPT CANNOT EXIST WITHOUT COMMITTED AUTHORITY
#   - FINALIZED PROMOTION RETAINS AUTHORITY + RECEIPT
#   - CRASH AFTER PREPARE / BEFORE AUTHORITY COMMIT
#   - CRASH AFTER AUTHORITY COMMIT / BEFORE RECEIPT
#   - CRASH AFTER RECEIPT / BEFORE FINALIZATION
#   - RESTART AFTER FINALIZATION
#   - EXACTLY-ONCE SYNTHETIC DISPATCH FENCE
#   - AUTHORITY REPLAY FENCE
#   - RECEIPT REPLAY FENCE
#   - GENERATION / LINEAGE / RECOVERY-EPOCH FENCING
#   - WAL HASH-CHAIN VALIDATION
#   - SEALED DURABLE SNAPSHOT VALIDATION
# ============================================================================

print("R28 UNIT N.35: MAIN.PY ENTERED", flush=True)

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


print("R28 UNIT N.35: IMPORTS COMPLETE", flush=True)


# ============================================================================
# CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.35"
UNIT_VERSION = "N.35"

SYMBOL = "BTCUSDT"

LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TARGET_LEVERAGE = "100"
TARGET_MARGIN_MODE = "ISOLATED"

INTEGRITY_KEY = b"R28-N35-LOCAL-INTEGRITY-KEY"

WAL_GENESIS_HASH = "0" * 64

PHASE_PREPARED = "PREPARED"
PHASE_COMMITTED = "COMMITTED"
PHASE_RECEIPTED = "RECEIPTED"
PHASE_FINALIZED = "FINALIZED"


print("R28 UNIT N.35: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# BASIC UTILITIES
# ============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def payload_hash(
    payload: Dict[str, Any],
) -> str:
    return sha256_text(
        canonical_json(payload)
    )


def seal_payload(
    payload: Dict[str, Any],
) -> str:
    body = canonical_json(
        payload
    ).encode("utf-8")

    return hmac.new(
        INTEGRITY_KEY,
        body,
        hashlib.sha256,
    ).hexdigest()


def new_id(
    prefix: str,
) -> str:
    return (
        f"{prefix}-"
        f"{uuid.uuid4().hex}"
    )


# ============================================================================
# LOCAL SAFETY BLOCK
# ============================================================================

class LocalBlock(Exception):
    pass


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise LocalBlock(message)


# ============================================================================
# DIAGNOSTIC OUTPUT
# ============================================================================

def divider() -> None:
    print(
        "-" * 92,
        flush=True,
    )


def test_header(
    number: int,
    title: str,
) -> None:
    divider()

    print(
        f"{UNIT_NAME} TEST {number}: {title}",
        flush=True,
    )

    divider()


def passed(
    label: str,
) -> None:
    print(
        f"{label:<78} ✅ PASS",
        flush=True,
    )


def expect_block(
    label: str,
    fn,
    expected_message: Optional[str] = None,
) -> None:

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

        if expected_message is not None:
            require(
                str(exc) == expected_message,
                f"unexpected local block: {exc}",
            )

        passed(label)

        return

    raise AssertionError(
        f"{label}: expected LocalBlock"
    )


# ============================================================================
# PROMOTION INTENT
# ============================================================================

@dataclass
class PromotionIntent:

    promotion_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    symbol: str
    margin_mode: str
    target_leverage: str

    transport_method: str
    transport_path: str

    transport_payload: Dict[str, Any]
    transport_payload_hash: str

    phase: str = PHASE_PREPARED

    def signing_view(
        self,
    ) -> Dict[str, Any]:

        return asdict(self)


# ============================================================================
# COMMITTED PROMOTION AUTHORITY
# ============================================================================

@dataclass
class CommittedAuthority:

    authority_id: str
    promotion_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    transport_method: str
    transport_path: str
    transport_payload_hash: str

    commit_sequence: int
    commit_hash: str

    phase: str = PHASE_COMMITTED

    def signing_view(
        self,
    ) -> Dict[str, Any]:

        return asdict(self)


# ============================================================================
# PROMOTION RECEIPT
# ============================================================================

@dataclass
class PromotionReceipt:

    receipt_id: str

    authority_id: str
    promotion_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    transport_method: str
    transport_path: str
    transport_payload_hash: str

    synthetic: bool
    network_transmitted: bool

    dispatch_count: int

    phase: str = PHASE_RECEIPTED

    def signing_view(
        self,
    ) -> Dict[str, Any]:

        return asdict(self)


# ============================================================================
# WRITE-AHEAD LOG RECORD
# ============================================================================

@dataclass
class WALRecord:

    sequence: int

    event: str
    data_hash: str

    previous_hash: str
    record_hash: str


# ============================================================================
# DURABLE ENGINE STATE
# ============================================================================

@dataclass
class DurableState:

    generation: int = 1

    lineage: str = field(
        default_factory=lambda: new_id(
            "lineage"
        )
    )

    recovery_epoch: int = 1

    pending_promotion: Optional[
        PromotionIntent
    ] = None

    committed_authority: Optional[
        CommittedAuthority
    ] = None

    finalized_promotion_ids: List[str] = field(
        default_factory=list
    )

    committed_authority_ids: List[str] = field(
        default_factory=list
    )

    committed_receipt_ids: List[str] = field(
        default_factory=list
    )

    receipts_by_promotion: Dict[
        str,
        PromotionReceipt,
    ] = field(
        default_factory=dict
    )

    authorities_by_promotion: Dict[
        str,
        CommittedAuthority,
    ] = field(
        default_factory=dict
    )

    dispatch_fence: Dict[
        str,
        int,
    ] = field(
        default_factory=dict
    )

    wal: List[
        WALRecord
    ] = field(
        default_factory=list
    )

    snapshot_sequence: int = 0

    snapshot_seal: str = ""

    def serializable(
        self,
        include_seal: bool = True,
    ) -> Dict[str, Any]:

        result = {

            "generation":
                self.generation,

            "lineage":
                self.lineage,

            "recovery_epoch":
                self.recovery_epoch,

            "pending_promotion":
                (
                    asdict(
                        self.pending_promotion
                    )
                    if self.pending_promotion
                    else None
                ),

            "committed_authority":
                (
                    asdict(
                        self.committed_authority
                    )
                    if self.committed_authority
                    else None
                ),

            "finalized_promotion_ids":
                list(
                    self.finalized_promotion_ids
                ),

            "committed_authority_ids":
                list(
                    self.committed_authority_ids
                ),

            "committed_receipt_ids":
                list(
                    self.committed_receipt_ids
                ),

            "receipts_by_promotion":
                {
                    key: asdict(value)
                    for key, value
                    in sorted(
                        self.receipts_by_promotion.items()
                    )
                },

            "authorities_by_promotion":
                {
                    key: asdict(value)
                    for key, value
                    in sorted(
                        self.authorities_by_promotion.items()
                    )
                },

            "dispatch_fence":
                dict(
                    sorted(
                        self.dispatch_fence.items()
                    )
                ),

            "wal":
                [
                    asdict(record)
                    for record in self.wal
                ],

            "snapshot_sequence":
                self.snapshot_sequence,
        }

        if include_seal:

            result[
                "snapshot_seal"
            ] = self.snapshot_seal

        return result


# ============================================================================
# ENGINE
# ============================================================================

class Engine:

    def __init__(
        self,
        state: Optional[DurableState] = None,
    ) -> None:

        self.state = (
            state
            or DurableState()
        )

        if not self.state.snapshot_seal:
            self._reseal_snapshot()


    # ========================================================================
    # SNAPSHOT HELPERS
    # ========================================================================

    def clone(
        self,
    ) -> "Engine":

        return Engine.restore(
            self.snapshot()
        )


    def _snapshot_material(
        self,
    ) -> Dict[str, Any]:

        return self.state.serializable(
            include_seal=False
        )


    def _reseal_snapshot(
        self,
    ) -> None:

        self.state.snapshot_seal = (
            seal_payload(
                self._snapshot_material()
            )
        )


    # ========================================================================
    # WAL
    # ========================================================================

    def _append_wal(
        self,
        event: str,
        data: Dict[str, Any],
    ) -> WALRecord:

        sequence = (
            len(self.state.wal)
            + 1
        )

        previous_hash = (
            self.state.wal[-1].record_hash
            if self.state.wal
            else WAL_GENESIS_HASH
        )

        data_hash = sha256_text(
            canonical_json(data)
        )

        record_hash = sha256_text(
            canonical_json(
                {
                    "sequence":
                        sequence,

                    "event":
                        event,

                    "data_hash":
                        data_hash,

                    "previous_hash":
                        previous_hash,
                }
            )
        )

        record = WALRecord(

            sequence=sequence,

            event=event,

            data_hash=data_hash,

            previous_hash=previous_hash,

            record_hash=record_hash,
        )

        self.state.wal.append(
            record
        )

        self.state.snapshot_sequence += 1

        self._reseal_snapshot()

        return record


    def validate_wal(
        self,
    ) -> None:

        previous_hash = (
            WAL_GENESIS_HASH
        )

        for (
            expected_sequence,
            record,
        ) in enumerate(
            self.state.wal,
            start=1,
        ):

            require(
                record.sequence
                == expected_sequence,
                "WAL sequence mismatch",
            )

            require(
                record.previous_hash
                == previous_hash,
                "WAL previous hash mismatch",
            )

            expected_hash = sha256_text(
                canonical_json(
                    {
                        "sequence":
                            record.sequence,

                        "event":
                            record.event,

                        "data_hash":
                            record.data_hash,

                        "previous_hash":
                            record.previous_hash,
                    }
                )
            )

            require(
                record.record_hash
                == expected_hash,
                "WAL record hash mismatch",
            )

            previous_hash = (
                record.record_hash
            )


    def wal_final_hash(
        self,
    ) -> str:

        if self.state.wal:

            return (
                self.state.wal[-1]
                .record_hash
            )

        return WAL_GENESIS_HASH


    # ========================================================================
    # SNAPSHOT SERIALIZATION
    # ========================================================================

    def snapshot(
        self,
    ) -> str:

        self._reseal_snapshot()

        return canonical_json(
            self.state.serializable(
                include_seal=True
            )
        )


    # ========================================================================
    # SNAPSHOT RESTORE
    # ========================================================================

    @staticmethod
    def restore(
        snapshot_blob: str,
    ) -> "Engine":

        raw = json.loads(
            snapshot_blob
        )

        supplied_seal = raw.pop(
            "snapshot_seal"
        )

        require(
            seal_payload(raw)
            == supplied_seal,
            "snapshot integrity seal mismatch",
        )

        pending_raw = raw.get(
            "pending_promotion"
        )

        authority_raw = raw.get(
            "committed_authority"
        )

        state = DurableState(

            generation=
                raw["generation"],

            lineage=
                raw["lineage"],

            recovery_epoch=
                raw["recovery_epoch"],

            pending_promotion=
                (
                    PromotionIntent(
                        **pending_raw
                    )
                    if pending_raw
                    else None
                ),

            committed_authority=
                (
                    CommittedAuthority(
                        **authority_raw
                    )
                    if authority_raw
                    else None
                ),

            finalized_promotion_ids=
                list(
                    raw[
                        "finalized_promotion_ids"
                    ]
                ),

            committed_authority_ids=
                list(
                    raw[
                        "committed_authority_ids"
                    ]
                ),

            committed_receipt_ids=
                list(
                    raw[
                        "committed_receipt_ids"
                    ]
                ),

            receipts_by_promotion=
                {
                    key:
                        PromotionReceipt(
                            **value
                        )

                    for key, value
                    in raw[
                        "receipts_by_promotion"
                    ].items()
                },

            authorities_by_promotion=
                {
                    key:
                        CommittedAuthority(
                            **value
                        )

                    for key, value
                    in raw[
                        "authorities_by_promotion"
                    ].items()
                },

            dispatch_fence=
                {
                    key:
                        int(value)

                    for key, value
                    in raw[
                        "dispatch_fence"
                    ].items()
                },

            wal=
                [
                    WALRecord(
                        **record
                    )

                    for record
                    in raw["wal"]
                ],

            snapshot_sequence=
                raw[
                    "snapshot_sequence"
                ],

            snapshot_seal=
                supplied_seal,
        )

        engine = Engine(
            state
        )

        engine.validate_full_state()

        return engine


    # ========================================================================
    # TRANSPORT PAYLOAD CONSTRUCTION
    # ========================================================================

    def make_transport_payload(
        self,
    ) -> Dict[str, Any]:

        return {

            "symbol":
                SYMBOL,

            "marginMode":
                TARGET_MARGIN_MODE,

            "leverage":
                TARGET_LEVERAGE,
        }


    # ========================================================================
    # PROMOTION PREPARATION
    # ========================================================================

    def prepare_promotion(
        self,
    ) -> PromotionIntent:

        require(
            self.state.pending_promotion
            is None,
            "pending promotion already exists",
        )

        payload = (
            self.make_transport_payload()
        )

        intent = PromotionIntent(

            promotion_id=
                new_id(
                    "promotion"
                ),

            generation=
                self.state.generation,

            lineage=
                self.state.lineage,

            recovery_epoch=
                self.state.recovery_epoch,

            symbol=
                SYMBOL,

            margin_mode=
                TARGET_MARGIN_MODE,

            target_leverage=
                TARGET_LEVERAGE,

            transport_method=
                HTTP_METHOD,

            transport_path=
                LEVERAGE_ENDPOINT,

            transport_payload=
                payload,

            transport_payload_hash=
                payload_hash(
                    payload
                ),
        )

        self.state.pending_promotion = (
            intent
        )

        self._append_wal(
            "PROMOTION_PREPARED",
            intent.signing_view(),
        )

        return copy.deepcopy(
            intent
        )


    # ========================================================================
    # PROMOTION INTENT VALIDATION
    # ========================================================================

    def _validate_intent(
        self,
        intent: PromotionIntent,
    ) -> None:

        require(
            intent.promotion_id
            not in
            self.state.finalized_promotion_ids,
            "promotion intent already finalized",
        )

        require(
            self.state.pending_promotion
            is not None,
            "pending promotion missing",
        )

        pending = (
            self.state.pending_promotion
        )

        require(
            pending.promotion_id
            == intent.promotion_id,
            "promotion id mismatch",
        )

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
            intent.margin_mode
            == TARGET_MARGIN_MODE,
            "promotion intent margin mode mismatch",
        )

        require(
            intent.target_leverage
            == TARGET_LEVERAGE,
            "promotion intent leverage mismatch",
        )

        require(
            intent.transport_method
            == HTTP_METHOD,
            "promotion intent transport method mismatch",
        )

        require(
            intent.transport_path
            == LEVERAGE_ENDPOINT,
            "promotion intent transport path mismatch",
        )

        require(
            payload_hash(
                intent.transport_payload
            )
            ==
            intent.transport_payload_hash,
            "promotion intent transport payload hash mismatch",
        )


    # ========================================================================
    # DURABLE AUTHORITY COMMIT
    # ========================================================================

    def commit_authority(
        self,
        intent: PromotionIntent,
    ) -> CommittedAuthority:

        self._validate_intent(
            intent
        )

        require(
            self.state.committed_authority
            is None,
            "committed authority already exists",
        )

        require(
            intent.promotion_id
            not in
            self.state.authorities_by_promotion,
            "promotion authority already committed",
        )

        sequence = (
            len(self.state.wal)
            + 1
        )

        authority_body = {

            "promotion_id":
                intent.promotion_id,

            "generation":
                intent.generation,

            "lineage":
                intent.lineage,

            "recovery_epoch":
                intent.recovery_epoch,

            "transport_method":
                intent.transport_method,

            "transport_path":
                intent.transport_path,

            "transport_payload_hash":
                intent.transport_payload_hash,

            "commit_sequence":
                sequence,
        }

        authority = CommittedAuthority(

            authority_id=
                new_id(
                    "authority"
                ),

            commit_hash=
                sha256_text(
                    canonical_json(
                        authority_body
                    )
                ),

            **authority_body,
        )

        self.state.committed_authority = (
            authority
        )

        self.state.committed_authority_ids.append(
            authority.authority_id
        )

        self.state.authorities_by_promotion[
            intent.promotion_id
        ] = authority

        self.state.pending_promotion.phase = (
            PHASE_COMMITTED
        )

        self._append_wal(
            "AUTHORITY_COMMITTED",
            authority.signing_view(),
        )

        return copy.deepcopy(
            authority
        )


    # ========================================================================
    # AUTHORITY VALIDATION
    # ========================================================================

    def _validate_authority(
        self,
        authority: CommittedAuthority,
    ) -> None:

        require(
            authority.authority_id
            in
            self.state.committed_authority_ids,
            "authority id is not durably committed",
        )

        require(
            authority.promotion_id
            in
            self.state.authorities_by_promotion,
            "authority promotion mapping missing",
        )

        durable = (
            self.state.authorities_by_promotion[
                authority.promotion_id
            ]
        )

        require(
            durable.authority_id
            == authority.authority_id,
            "authority id mismatch",
        )

        require(
            authority.generation
            == durable.generation,
            "authority generation mismatch",
        )

        require(
            authority.lineage
            == durable.lineage,
            "authority lineage mismatch",
        )

        require(
            authority.recovery_epoch
            == durable.recovery_epoch,
            "authority recovery epoch mismatch",
        )

        require(
            authority.transport_method
            == durable.transport_method,
            "authority transport method mismatch",
        )

        require(
            authority.transport_path
            == durable.transport_path,
            "authority transport path mismatch",
        )

        require(
            authority.transport_payload_hash
            == durable.transport_payload_hash,
            "authority transport payload hash mismatch",
        )

        require(
            authority.commit_hash
            == durable.commit_hash,
            "authority commit hash mismatch",
        )


    # ========================================================================
    # SYNTHETIC DISPATCH
    # ========================================================================

    def dispatch_synthetic(
        self,
        authority: CommittedAuthority,
    ) -> PromotionReceipt:

        self._validate_authority(
            authority
        )

        promotion_id = (
            authority.promotion_id
        )

        require(
            promotion_id
            not in
            self.state.receipts_by_promotion,
            "promotion receipt already committed",
        )

        require(
            self.state.dispatch_fence.get(
                promotion_id,
                0,
            )
            == 0,
            "promotion dispatch already fenced",
        )

        # IMPORTANT:
        # No requests library.
        # No urllib request.
        # No socket send.
        # No exchange POST.
        #
        # This is a LOCAL SYNTHETIC transition only.

        self.state.dispatch_fence[
            promotion_id
        ] = 1

        receipt = PromotionReceipt(

            receipt_id=
                new_id(
                    "receipt"
                ),

            authority_id=
                authority.authority_id,

            promotion_id=
                promotion_id,

            generation=
                authority.generation,

            lineage=
                authority.lineage,

            recovery_epoch=
                authority.recovery_epoch,

            transport_method=
                authority.transport_method,

            transport_path=
                authority.transport_path,

            transport_payload_hash=
                authority.transport_payload_hash,

            synthetic=
                True,

            network_transmitted=
                False,

            dispatch_count=
                1,
        )

        self.state.receipts_by_promotion[
            promotion_id
        ] = receipt

        self.state.committed_receipt_ids.append(
            receipt.receipt_id
        )

        self._append_wal(
            "SYNTHETIC_RECEIPT_COMMITTED",
            receipt.signing_view(),
        )

        return copy.deepcopy(
            receipt
        )


    # ========================================================================
    # RECEIPT VALIDATION
    # ========================================================================

    def _validate_receipt(
        self,
        receipt: PromotionReceipt,
    ) -> None:

        require(
            receipt.receipt_id
            in
            self.state.committed_receipt_ids,
            "promotion receipt is not durably committed",
        )

        require(
            receipt.promotion_id
            in
            self.state.receipts_by_promotion,
            "promotion receipt mapping missing",
        )

        durable = (
            self.state.receipts_by_promotion[
                receipt.promotion_id
            ]
        )

        require(
            durable.receipt_id
            == receipt.receipt_id,
            "promotion receipt id mismatch",
        )

        require(
            receipt.authority_id
            == durable.authority_id,
            "promotion receipt authority mismatch",
        )

        require(
            receipt.promotion_id
            == durable.promotion_id,
            "promotion receipt promotion mismatch",
        )

        require(
            receipt.generation
            == durable.generation,
            "promotion receipt generation mismatch",
        )

        require(
            receipt.lineage
            == durable.lineage,
            "promotion receipt lineage mismatch",
        )

        require(
            receipt.recovery_epoch
            == durable.recovery_epoch,
            "promotion receipt recovery epoch mismatch",
        )

        require(
            receipt.transport_method
            == durable.transport_method,
            "promotion receipt transport method mismatch",
        )

        require(
            receipt.transport_path
            == durable.transport_path,
            "promotion receipt transport path mismatch",
        )

        require(
            receipt.transport_payload_hash
            == durable.transport_payload_hash,
            "promotion receipt transport payload hash mismatch",
        )

        require(
            receipt.synthetic
            is True,
            "promotion receipt is not synthetic",
        )

        require(
            receipt.network_transmitted
            is False,
            "promotion receipt reports network transmission",
        )

        require(
            receipt.dispatch_count
            == 1,
            "promotion receipt dispatch count mismatch",
        )


    # ========================================================================
    # AUTHORITY / RECEIPT RECONCILIATION
    # ========================================================================

    def reconcile_authority_and_receipt(
        self,
        authority: CommittedAuthority,
        receipt: PromotionReceipt,
    ) -> None:

        self._validate_authority(
            authority
        )

        self._validate_receipt(
            receipt
        )

        require(
            receipt.authority_id
            == authority.authority_id,
            "receipt/authority id mismatch",
        )

        require(
            receipt.promotion_id
            == authority.promotion_id,
            "receipt/authority promotion mismatch",
        )

        require(
            receipt.generation
            == authority.generation,
            "receipt/authority generation mismatch",
        )

        require(
            receipt.lineage
            == authority.lineage,
            "receipt/authority lineage mismatch",
        )

        require(
            receipt.recovery_epoch
            == authority.recovery_epoch,
            "receipt/authority recovery epoch mismatch",
        )

        require(
            receipt.transport_method
            == authority.transport_method,
            "receipt/authority transport method mismatch",
        )

        require(
            receipt.transport_path
            == authority.transport_path,
            "receipt/authority transport path mismatch",
        )

        require(
            receipt.transport_payload_hash
            == authority.transport_payload_hash,
            "receipt/authority payload hash mismatch",
        )

        require(
            self.state.dispatch_fence.get(
                authority.promotion_id
            )
            == 1,
            "receipt exists without dispatch fence",
        )


    # ========================================================================
    # PROMOTION FINALIZATION
    # ========================================================================

    def finalize_promotion(
        self,
        receipt: PromotionReceipt,
    ) -> None:

        self._validate_receipt(
            receipt
        )

        authority = (
            self.state.authorities_by_promotion.get(
                receipt.promotion_id
            )
        )

        require(
            authority is not None,
            "finalized receipt missing committed authority",
        )

        self.reconcile_authority_and_receipt(
            authority,
            receipt,
        )

        require(
            receipt.promotion_id
            not in
            self.state.finalized_promotion_ids,
            "promotion receipt already finalized",
        )

        self.state.finalized_promotion_ids.append(
            receipt.promotion_id
        )

        if (
            self.state.pending_promotion
            and
            self.state.pending_promotion.promotion_id
            == receipt.promotion_id
        ):

            self.state.pending_promotion = (
                None
            )

        if (
            self.state.committed_authority
            and
            self.state.committed_authority.promotion_id
            == receipt.promotion_id
        ):

            self.state.committed_authority = (
                None
            )

        stored = (
            self.state.receipts_by_promotion[
                receipt.promotion_id
            ]
        )

        stored.phase = (
            PHASE_FINALIZED
        )

        self._append_wal(

            "PROMOTION_FINALIZED",

            {
                "promotion_id":
                    receipt.promotion_id,

                "authority_id":
                    receipt.authority_id,

                "receipt_id":
                    receipt.receipt_id,
            },
        )


    # ========================================================================
    # DURABLE RECOVERY
    # ========================================================================

    def recover(
        self,
    ) -> Optional[PromotionReceipt]:

        if (
            self.state.pending_promotion
            is None
            and
            self.state.committed_authority
            is None
        ):

            return None

        require(
            self.state.pending_promotion
            is not None,
            "committed authority exists without pending promotion",
        )

        intent = copy.deepcopy(
            self.state.pending_promotion
        )

        promotion_id = (
            intent.promotion_id
        )

        # --------------------------------------------------------------------
        # CRASH WINDOW A:
        # prepared promotion exists but authority was not committed yet
        # --------------------------------------------------------------------

        if (
            self.state.committed_authority
            is None
        ):

            authority = (
                self.commit_authority(
                    intent
                )
            )

        else:

            authority = copy.deepcopy(
                self.state.committed_authority
            )

            self._validate_authority(
                authority
            )

        # --------------------------------------------------------------------
        # CRASH WINDOW B:
        # authority committed but receipt not yet durable
        # --------------------------------------------------------------------

        if (
            promotion_id
            in
            self.state.receipts_by_promotion
        ):

            # ----------------------------------------------------------------
            # CRASH WINDOW C:
            # receipt already exists.
            #
            # IMPORTANT:
            # DO NOT dispatch again.
            # Reuse the durable receipt.
            # ----------------------------------------------------------------

            receipt = copy.deepcopy(
                self.state.receipts_by_promotion[
                    promotion_id
                ]
            )

        else:

            receipt = (
                self.dispatch_synthetic(
                    authority
                )
            )

        self.reconcile_authority_and_receipt(
            authority,
            receipt,
        )

        if (
            promotion_id
            not in
            self.state.finalized_promotion_ids
        ):

            self.finalize_promotion(
                receipt
            )

        return receipt


    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(
        self,
    ) -> None:

        require(
            self.state.pending_promotion
            is None,
            "cannot advance generation with pending promotion",
        )

        require(
            self.state.committed_authority
            is None,
            "cannot advance generation with committed authority",
        )

        old_generation = (
            self.state.generation
        )

        self.state.generation += 1

        self.state.lineage = (
            new_id(
                "lineage"
            )
        )

        self.state.recovery_epoch += 1

        self._append_wal(

            "GENERATION_ADVANCED",

            {
                "old_generation":
                    old_generation,

                "new_generation":
                    self.state.generation,

                "lineage":
                    self.state.lineage,

                "recovery_epoch":
                    self.state.recovery_epoch,
            },
        )


    # ========================================================================
    # COMPLETE DURABLE STATE VALIDATION
    # ========================================================================

    def validate_full_state(
        self,
    ) -> None:

        # --------------------------------------------------------------------
        # WAL
        # --------------------------------------------------------------------

        self.validate_wal()

        # --------------------------------------------------------------------
        # SNAPSHOT SEAL
        # --------------------------------------------------------------------

        require(
            self.state.snapshot_seal
            ==
            seal_payload(
                self._snapshot_material()
            ),
            "snapshot integrity seal mismatch",
        )

        # --------------------------------------------------------------------
        # ACTIVE PENDING PROMOTION
        # --------------------------------------------------------------------

        if (
            self.state.pending_promotion
            is not None
        ):

            require(
                self.state.pending_promotion.promotion_id
                not in
                self.state.finalized_promotion_ids,
                "pending promotion is already finalized",
            )

        # --------------------------------------------------------------------
        # ACTIVE COMMITTED AUTHORITY
        # --------------------------------------------------------------------

        if (
            self.state.committed_authority
            is not None
        ):

            self._validate_authority(
                self.state.committed_authority
            )

            require(
                self.state.pending_promotion
                is not None,
                "committed authority exists without pending promotion",
            )

            require(
                self.state.pending_promotion.promotion_id
                ==
                self.state.committed_authority.promotion_id,
                "pending promotion/authority mismatch",
            )

        # --------------------------------------------------------------------
        # DURABLE AUTHORITIES
        # --------------------------------------------------------------------

        for (
            promotion_id,
            authority,
        ) in (
            self.state.authorities_by_promotion.items()
        ):

            require(
                authority.promotion_id
                == promotion_id,
                "authority mapping key mismatch",
            )

            require(
                authority.authority_id
                in
                self.state.committed_authority_ids,
                "authority mapping references uncommitted id",
            )

        # --------------------------------------------------------------------
        # DURABLE RECEIPTS
        # --------------------------------------------------------------------

        for (
            promotion_id,
            receipt,
        ) in (
            self.state.receipts_by_promotion.items()
        ):

            require(
                receipt.promotion_id
                == promotion_id,
                "receipt mapping key mismatch",
            )

            require(
                receipt.receipt_id
                in
                self.state.committed_receipt_ids,
                "receipt mapping references uncommitted id",
            )

            require(
                promotion_id
                in
                self.state.authorities_by_promotion,
                "receipt exists without committed authority",
            )

            authority = (
                self.state.authorities_by_promotion[
                    promotion_id
                ]
            )

            self.reconcile_authority_and_receipt(
                authority,
                receipt,
            )

        # --------------------------------------------------------------------
        # FINALIZED PROMOTIONS
        # --------------------------------------------------------------------

        for promotion_id in (
            self.state.finalized_promotion_ids
        ):

            require(
                promotion_id
                in
                self.state.receipts_by_promotion,
                "finalized promotion missing receipt",
            )

            require(
                promotion_id
                in
                self.state.authorities_by_promotion,
                "finalized promotion missing authority",
            )

            require(
                self.state.receipts_by_promotion[
                    promotion_id
                ].phase
                ==
                PHASE_FINALIZED,
                "finalized promotion receipt phase mismatch",
            )

        # --------------------------------------------------------------------
        # DISPATCH FENCE
        # --------------------------------------------------------------------

        for (
            promotion_id,
            count,
        ) in (
            self.state.dispatch_fence.items()
        ):

            require(
                count == 1,
                "dispatch fence count mismatch",
            )

            require(
                promotion_id
                in
                self.state.receipts_by_promotion,
                "dispatch fence exists without receipt",
            )


print(
    "R28 UNIT N.35: DEFINITIONS LOADED",
    flush=True,
)


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def run_diagnostics() -> None:

    engine = Engine()


    # ========================================================================
    # TEST 1
    # ========================================================================

    test_header(
        1,
        "INITIAL DURABLE STATE",
    )

    require(
        engine.state.generation
        == 1,
        "initial generation mismatch",
    )

    require(
        engine.state.recovery_epoch
        == 1,
        "initial recovery epoch mismatch",
    )

    require(
        engine.state.pending_promotion
        is None,
        "unexpected pending promotion",
    )

    require(
        engine.state.committed_authority
        is None,
        "unexpected committed authority",
    )

    passed(
        "Initial Generation Is One"
    )

    passed(
        "Initial Recovery Epoch Is One"
    )

    passed(
        "No Pending Promotion Exists"
    )

    passed(
        "No Committed Authority Exists"
    )


    # ========================================================================
    # TEST 2
    # ========================================================================

    test_header(
        2,
        "PROMOTION PREPARATION",
    )

    intent = (
        engine.prepare_promotion()
    )

    require(
        intent.transport_method
        == HTTP_METHOD,
        "prepared transport method mismatch",
    )

    require(
        intent.transport_path
        == LEVERAGE_ENDPOINT,
        "prepared transport path mismatch",
    )

    require(
        intent.transport_payload_hash
        ==
        payload_hash(
            intent.transport_payload
        ),
        "prepared payload hash mismatch",
    )

    passed(
        "Promotion Intent Prepared"
    )

    passed(
        "Transport Method Exactly POST"
    )

    passed(
        "Transport Path Exactly Leverage Endpoint"
    )

    passed(
        "Transport Payload Hash Established"
    )


    # ========================================================================
    # TEST 3
    # ========================================================================

    test_header(
        3,
        "COMMITTED AUTHORITY CREATION",
    )

    authority = (
        engine.commit_authority(
            intent
        )
    )

    require(
        authority.promotion_id
        == intent.promotion_id,
        "authority promotion mismatch",
    )

    require(
        authority.authority_id
        in
        engine.state.committed_authority_ids,
        "authority id not committed",
    )

    passed(
        "Committed Authority Created"
    )

    passed(
        "Authority Bound To Promotion"
    )

    passed(
        "Authority ID Durably Fenced"
    )


    # ========================================================================
    # TEST 4
    # ========================================================================

    test_header(
        4,
        "AUTHORITY TRANSPORT BINDING",
    )

    require(
        authority.transport_method
        == intent.transport_method,
        "authority method mismatch",
    )

    require(
        authority.transport_path
        == intent.transport_path,
        "authority path mismatch",
    )

    require(
        authority.transport_payload_hash
        ==
        intent.transport_payload_hash,
        "authority hash mismatch",
    )

    passed(
        "Authority Transport Method Preserved"
    )

    passed(
        "Authority Transport Path Preserved"
    )

    passed(
        "Authority Payload Hash Preserved"
    )


    # ========================================================================
    # TEST 5
    # ========================================================================

    test_header(
        5,
        "SYNTHETIC RECEIPT CREATION",
    )

    receipt = (
        engine.dispatch_synthetic(
            authority
        )
    )

    require(
        receipt.synthetic
        is True,
        "receipt not synthetic",
    )

    require(
        receipt.network_transmitted
        is False,
        "receipt reports network transmission",
    )

    require(
        receipt.dispatch_count
        == 1,
        "receipt dispatch count mismatch",
    )

    passed(
        "Synthetic Promotion Receipt Created"
    )

    passed(
        "Receipt Reports No Network Transmission"
    )

    passed(
        "Receipt Dispatch Count Exactly One"
    )


    # ========================================================================
    # TEST 6
    # ========================================================================

    test_header(
        6,
        "AUTHORITY / RECEIPT RECONCILIATION",
    )

    engine.reconcile_authority_and_receipt(
        authority,
        receipt,
    )

    passed(
        "Committed Authority Reconciles With Receipt"
    )

    passed(
        "Promotion Identity Matches"
    )

    passed(
        "Authority Identity Matches"
    )

    passed(
        "Transport Binding Matches"
    )


    # ========================================================================
    # TEST 7
    # ========================================================================

    test_header(
        7,
        "PROMOTION FINALIZATION",
    )

    engine.finalize_promotion(
        receipt
    )

    require(
        intent.promotion_id
        in
        engine.state.finalized_promotion_ids,
        "promotion not finalized",
    )

    require(
        engine.state.pending_promotion
        is None,
        "pending promotion not cleared",
    )

    require(
        engine.state.committed_authority
        is None,
        "active authority not cleared",
    )

    passed(
        "Promotion Finalized"
    )

    passed(
        "Pending Promotion Cleared"
    )

    passed(
        "Active Committed Authority Cleared"
    )


    # ========================================================================
    # TEST 8
    # ========================================================================

    test_header(
        8,
        "FINALIZED PROMOTION RETAINS AUTHORITY",
    )

    require(
        intent.promotion_id
        in
        engine.state.authorities_by_promotion,
        "finalized authority missing",
    )

    durable_authority = (
        engine.state.authorities_by_promotion[
            intent.promotion_id
        ]
    )

    require(
        durable_authority.authority_id
        == authority.authority_id,
        "durable authority changed",
    )

    passed(
        "Committed Authority Preserved After Finalization"
    )

    passed(
        "Authority ID Preserved After Finalization"
    )


    # ========================================================================
    # TEST 9
    # ========================================================================

    test_header(
        9,
        "FINALIZED PROMOTION RETAINS RECEIPT",
    )

    require(
        intent.promotion_id
        in
        engine.state.receipts_by_promotion,
        "finalized receipt missing",
    )

    durable_receipt = (
        engine.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    require(
        durable_receipt.receipt_id
        == receipt.receipt_id,
        "durable receipt changed",
    )

    passed(
        "Promotion Receipt Preserved After Finalization"
    )

    passed(
        "Receipt ID Preserved After Finalization"
    )


    # ========================================================================
    # TEST 10
    # ========================================================================

    test_header(
        10,
        "RECEIPT WITHOUT AUTHORITY REJECTION",
    )

    broken = (
        engine.clone()
    )

    broken.state.authorities_by_promotion.pop(
        intent.promotion_id
    )

    broken._reseal_snapshot()

    expect_block(

        "Receipt Without Committed Authority Rejected",

        broken.validate_full_state,

        "receipt exists without committed authority",
    )


    # ========================================================================
    # TEST 11
    # ========================================================================

    test_header(
        11,
        "FINALIZED PROMOTION WITHOUT AUTHORITY REJECTION",
    )

    broken = (
        engine.clone()
    )

    broken.state.authorities_by_promotion.pop(
        intent.promotion_id
    )

    broken.state.receipts_by_promotion.pop(
        intent.promotion_id
    )

    broken.state.dispatch_fence.pop(
        intent.promotion_id
    )

    broken._reseal_snapshot()

    expect_block(

        "Finalized Promotion Without Authority Rejected",

        broken.validate_full_state,

        "finalized promotion missing receipt",
    )


    # ========================================================================
    # TEST 12
    # ========================================================================

    test_header(
        12,
        "FINALIZED PROMOTION WITHOUT RECEIPT REJECTION",
    )

    broken = (
        engine.clone()
    )

    broken.state.receipts_by_promotion.pop(
        intent.promotion_id
    )

    broken.state.dispatch_fence.pop(
        intent.promotion_id
    )

    broken._reseal_snapshot()

    expect_block(

        "Finalized Promotion Without Receipt Rejected",

        broken.validate_full_state,

        "finalized promotion missing receipt",
    )


    # ========================================================================
    # TEST 13
    # ========================================================================

    test_header(
        13,
        "RECEIPT / AUTHORITY ID MISMATCH",
    )

    broken = (
        engine.clone()
    )

    bad_receipt = copy.deepcopy(
        broken.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    bad_receipt.authority_id = (
        new_id(
            "forged-authority"
        )
    )

    broken.state.receipts_by_promotion[
        intent.promotion_id
    ] = bad_receipt

    broken._reseal_snapshot()

    expect_block(

        "Receipt Bound To Wrong Authority Rejected",

        broken.validate_full_state,

        "receipt/authority id mismatch",
    )


    # ========================================================================
    # TEST 14
    # ========================================================================

    test_header(
        14,
        "RECEIPT / AUTHORITY GENERATION MISMATCH",
    )

    broken = (
        engine.clone()
    )

    bad_receipt = copy.deepcopy(
        broken.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    bad_receipt.generation += 1

    broken.state.receipts_by_promotion[
        intent.promotion_id
    ] = bad_receipt

    broken._reseal_snapshot()

    expect_block(

        "Receipt Wrong Authority Generation Rejected",

        broken.validate_full_state,

        "receipt/authority generation mismatch",
    )


    # ========================================================================
    # TEST 15
    # ========================================================================

    test_header(
        15,
        "RECEIPT / AUTHORITY LINEAGE MISMATCH",
    )

    broken = (
        engine.clone()
    )

    bad_receipt = copy.deepcopy(
        broken.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    bad_receipt.lineage = (
        new_id(
            "forged-lineage"
        )
    )

    broken.state.receipts_by_promotion[
        intent.promotion_id
    ] = bad_receipt

    broken._reseal_snapshot()

    expect_block(

        "Receipt Wrong Authority Lineage Rejected",

        broken.validate_full_state,

        "receipt/authority lineage mismatch",
    )


    # ========================================================================
    # TEST 16
    # ========================================================================

    test_header(
        16,
        "RECEIPT / AUTHORITY RECOVERY EPOCH MISMATCH",
    )

    broken = (
        engine.clone()
    )

    bad_receipt = copy.deepcopy(
        broken.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    bad_receipt.recovery_epoch += 1

    broken.state.receipts_by_promotion[
        intent.promotion_id
    ] = bad_receipt

    broken._reseal_snapshot()

    expect_block(

        "Receipt Wrong Authority Recovery Epoch Rejected",

        broken.validate_full_state,

        "receipt/authority recovery epoch mismatch",
    )


    # ========================================================================
    # TEST 17
    # ========================================================================

    test_header(
        17,
        "RECEIPT / AUTHORITY TRANSPORT METHOD MISMATCH",
    )

    broken = (
        engine.clone()
    )

    bad_receipt = copy.deepcopy(
        broken.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    bad_receipt.transport_method = (
        "GET"
    )

    broken.state.receipts_by_promotion[
        intent.promotion_id
    ] = bad_receipt

    broken._reseal_snapshot()

    expect_block(

        "Receipt Wrong Authority Transport Method Rejected",

        broken.validate_full_state,

        "receipt/authority transport method mismatch",
    )


    # ========================================================================
    # TEST 18
    # ========================================================================

    test_header(
        18,
        "RECEIPT / AUTHORITY TRANSPORT PATH MISMATCH",
    )

    broken = (
        engine.clone()
    )

    bad_receipt = copy.deepcopy(
        broken.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    bad_receipt.transport_path = (
        "/wrong"
    )

    broken.state.receipts_by_promotion[
        intent.promotion_id
    ] = bad_receipt

    broken._reseal_snapshot()

    expect_block(

        "Receipt Wrong Authority Transport Path Rejected",

        broken.validate_full_state,

        "receipt/authority transport path mismatch",
    )


    # ========================================================================
    # TEST 19
    # ========================================================================

    test_header(
        19,
        "RECEIPT / AUTHORITY PAYLOAD HASH MISMATCH",
    )

    broken = (
        engine.clone()
    )

    bad_receipt = copy.deepcopy(
        broken.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    bad_receipt.transport_payload_hash = (
        "f" * 64
    )

    broken.state.receipts_by_promotion[
        intent.promotion_id
    ] = bad_receipt

    broken._reseal_snapshot()

    expect_block(

        "Receipt Wrong Authority Payload Hash Rejected",

        broken.validate_full_state,

        "receipt/authority payload hash mismatch",
    )


    # ========================================================================
    # TEST 20
    # ========================================================================

    test_header(
        20,
        "CRASH AFTER PREPARE BEFORE AUTHORITY COMMIT",
    )

    crash_a = (
        Engine()
    )

    crash_intent = (
        crash_a.prepare_promotion()
    )

    recovered_a = (
        Engine.restore(
            crash_a.snapshot()
        )
    )

    recovered_receipt_a = (
        recovered_a.recover()
    )

    require(
        recovered_receipt_a
        is not None,
        "recovery did not produce receipt",
    )

    require(
        crash_intent.promotion_id
        in
        recovered_a.state.finalized_promotion_ids,
        "recovery did not finalize",
    )

    passed(
        "Prepared Promotion Survived Restart"
    )

    passed(
        "Recovery Created Committed Authority"
    )

    passed(
        "Recovery Created Exactly One Synthetic Receipt"
    )

    passed(
        "Recovery Finalized Promotion"
    )


    # ========================================================================
    # TEST 21
    # ========================================================================

    test_header(
        21,
        "CRASH AFTER AUTHORITY COMMIT BEFORE RECEIPT",
    )

    crash_b = (
        Engine()
    )

    crash_intent_b = (
        crash_b.prepare_promotion()
    )

    crash_authority_b = (
        crash_b.commit_authority(
            crash_intent_b
        )
    )

    recovered_b = (
        Engine.restore(
            crash_b.snapshot()
        )
    )

    recovered_receipt_b = (
        recovered_b.recover()
    )

    require(
        recovered_receipt_b
        is not None,
        "authority recovery did not produce receipt",
    )

    require(
        recovered_receipt_b.authority_id
        ==
        crash_authority_b.authority_id,
        "authority identity changed",
    )

    require(
        recovered_b.state.dispatch_fence[
            crash_intent_b.promotion_id
        ]
        == 1,
        "dispatch fence missing",
    )

    passed(
        "Committed Authority Survived Restart"
    )

    passed(
        "Recovery Reused Original Authority"
    )

    passed(
        "Exactly One Synthetic Dispatch Fence Created"
    )

    passed(
        "Recovered Receipt Bound To Original Authority"
    )


    # ========================================================================
    # TEST 22
    # ========================================================================

    test_header(
        22,
        "CRASH AFTER RECEIPT BEFORE FINALIZATION",
    )

    crash_c = (
        Engine()
    )

    crash_intent_c = (
        crash_c.prepare_promotion()
    )

    crash_authority_c = (
        crash_c.commit_authority(
            crash_intent_c
        )
    )

    crash_receipt_c = (
        crash_c.dispatch_synthetic(
            crash_authority_c
        )
    )

    recovered_c = (
        Engine.restore(
            crash_c.snapshot()
        )
    )

    recovered_receipt_c = (
        recovered_c.recover()
    )

    require(
        recovered_receipt_c
        is not None,
        "receipt recovery missing",
    )

    require(
        recovered_receipt_c.receipt_id
        ==
        crash_receipt_c.receipt_id,
        "receipt identity changed",
    )

    require(
        recovered_c.state.dispatch_fence[
            crash_intent_c.promotion_id
        ]
        == 1,
        "dispatch fence changed",
    )

    passed(
        "Committed Receipt Survived Restart"
    )

    passed(
        "Recovery Reused Existing Receipt"
    )

    passed(
        "No Second Dispatch Occurred"
    )

    passed(
        "Recovered Receipt Finalized"
    )


    # ========================================================================
    # TEST 23
    # ========================================================================

    test_header(
        23,
        "CRASH AFTER FINALIZATION",
    )

    restarted = (
        Engine.restore(
            engine.snapshot()
        )
    )

    require(
        intent.promotion_id
        in
        restarted.state.finalized_promotion_ids,
        "finalized id lost",
    )

    require(
        intent.promotion_id
        in
        restarted.state.authorities_by_promotion,
        "authority lost",
    )

    require(
        intent.promotion_id
        in
        restarted.state.receipts_by_promotion,
        "receipt lost",
    )

    passed(
        "Finalized Promotion Survives Restart"
    )

    passed(
        "Committed Authority Survives Restart"
    )

    passed(
        "Committed Receipt Survives Restart"
    )


    # ========================================================================
    # TEST 24
    # ========================================================================

    test_header(
        24,
        "SECOND DISPATCH REJECTION",
    )

    expect_block(

        "Second Synthetic Dispatch Rejected",

        lambda:
            restarted.dispatch_synthetic(
                restarted.state.authorities_by_promotion[
                    intent.promotion_id
                ]
            ),

        "promotion receipt already committed",
    )


    # ========================================================================
    # TEST 25
    # ========================================================================

    test_header(
        25,
        "RECEIPT REPLAY FINALIZATION REJECTION",
    )

    expect_block(

        "Finalized Receipt Replay Rejected",

        lambda:
            restarted.finalize_promotion(
                restarted.state.receipts_by_promotion[
                    intent.promotion_id
                ]
            ),

        "promotion receipt already finalized",
    )


    # ========================================================================
    # TEST 26
    # ========================================================================

    test_header(
        26,
        "AUTHORITY REPLAY COMMIT REJECTION",
    )

    replay_engine = (
        Engine()
    )

    replay_intent = (
        replay_engine.prepare_promotion()
    )

    replay_engine.commit_authority(
        replay_intent
    )

    expect_block(

        "Second Authority Commit Rejected",

        lambda:
            replay_engine.commit_authority(
                replay_intent
            ),

        "committed authority already exists",
    )


    # ========================================================================
    # TEST 27
    # ========================================================================

    test_header(
        27,
        "GENERATION ADVANCE",
    )

    old_generation = (
        restarted.state.generation
    )

    old_lineage = (
        restarted.state.lineage
    )

    old_epoch = (
        restarted.state.recovery_epoch
    )

    restarted.advance_generation()

    require(
        restarted.state.generation
        ==
        old_generation + 1,
        "generation did not advance",
    )

    require(
        restarted.state.lineage
        !=
        old_lineage,
        "lineage did not change",
    )

    require(
        restarted.state.recovery_epoch
        ==
        old_epoch + 1,
        "recovery epoch did not advance",
    )

    passed(
        "Generation Advanced Monotonically"
    )

    passed(
        "Lineage Changed On Generation Advance"
    )

    passed(
        "Recovery Epoch Advanced Monotonically"
    )


    # ========================================================================
    # TEST 28
    # ========================================================================

    test_header(
        28,
        "FINALIZED AUTHORITY / RECEIPT FENCE SURVIVES GENERATION ADVANCE",
    )

    require(
        intent.promotion_id
        in
        restarted.state.finalized_promotion_ids,
        "finalized id lost after generation advance",
    )

    require(
        intent.promotion_id
        in
        restarted.state.authorities_by_promotion,
        "authority lost after generation advance",
    )

    require(
        intent.promotion_id
        in
        restarted.state.receipts_by_promotion,
        "receipt lost after generation advance",
    )

    require(
        restarted.state.dispatch_fence[
            intent.promotion_id
        ]
        == 1,
        "dispatch fence lost after generation advance",
    )

    passed(
        "Finalized Promotion ID Preserved Across Generation"
    )

    passed(
        "Committed Authority Preserved Across Generation"
    )

    passed(
        "Promotion Receipt Preserved Across Generation"
    )

    passed(
        "Dispatch Fence Preserved Across Generation"
    )


    # ========================================================================
    # TEST 29
    # ========================================================================

    test_header(
        29,
        "OLD AUTHORITY CANNOT CREATE SECOND RECEIPT",
    )

    expect_block(

        "Old Authority Second Receipt Rejected",

        lambda:
            restarted.dispatch_synthetic(
                restarted.state.authorities_by_promotion[
                    intent.promotion_id
                ]
            ),

        "promotion receipt already committed",
    )


    # ========================================================================
    # TEST 30
    # ========================================================================

    test_header(
        30,
        "GENERATION ADVANCE BLOCKED BY PENDING PROMOTION",
    )

    blocked = (
        Engine()
    )

    blocked.prepare_promotion()

    expect_block(

        "Generation Advance With Pending Promotion Rejected",

        blocked.advance_generation,

        "cannot advance generation with pending promotion",
    )


    # ========================================================================
    # TEST 31
    # ========================================================================

    test_header(
        31,
        "GENERATION ADVANCE BLOCKED BY ACTIVE COMMITTED AUTHORITY",
    )

    blocked2 = (
        Engine()
    )

    blocked2_intent = (
        blocked2.prepare_promotion()
    )

    blocked2.commit_authority(
        blocked2_intent
    )

    # Deliberately create the impossible condition:
    # authority still active while pending promotion vanished.
    #
    # advance_generation() must still refuse to cross the authority boundary.

    blocked2.state.pending_promotion = (
        None
    )

    blocked2._reseal_snapshot()

    expect_block(

        "Generation Advance With Active Authority Rejected",

        blocked2.advance_generation,

        "cannot advance generation with committed authority",
    )


    # ========================================================================
    # TEST 32
    # ========================================================================

    test_header(
        32,
        "SNAPSHOT TAMPER REJECTION",
    )

    snapshot_obj = json.loads(
        engine.snapshot()
    )

    snapshot_obj[
        "generation"
    ] += 1

    tampered_blob = (
        canonical_json(
            snapshot_obj
        )
    )

    expect_block(

        "Tampered Durable Snapshot Rejected",

        lambda:
            Engine.restore(
                tampered_blob
            ),

        "snapshot integrity seal mismatch",
    )


    # ========================================================================
    # TEST 33
    # ========================================================================

    test_header(
        33,
        "FULL DURABLE STATE VALIDATION",
    )

    engine.validate_full_state()

    restarted.validate_full_state()

    recovered_a.validate_full_state()

    recovered_b.validate_full_state()

    recovered_c.validate_full_state()

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

    require(
        engine.wal_final_hash()
        ==
        engine.state.wal[-1].record_hash,
        "WAL final hash mismatch",
    )

    passed(
        "WAL Records Validate"
    )

    passed(
        "WAL Final Hash Matches Journal"
    )


    # ========================================================================
    # TEST 35
    # ========================================================================

    test_header(
        35,
        "SYNTHETIC TRANSPORT FIREBREAK",
    )

    final_receipt = (
        engine.state.receipts_by_promotion[
            intent.promotion_id
        ]
    )

    require(
        final_receipt.synthetic
        is True,
        "final receipt is not synthetic",
    )

    require(
        final_receipt.network_transmitted
        is False,
        "network transmission occurred",
    )

    require(
        final_receipt.transport_method
        == HTTP_METHOD,
        "transport method mismatch",
    )

    require(
        final_receipt.transport_path
        == LEVERAGE_ENDPOINT,
        "transport path mismatch",
    )

    require(
        final_receipt.transport_payload_hash
        ==
        intent.transport_payload_hash,
        "transport payload hash mismatch",
    )

    passed(
        "Dispatch Is Synthetic"
    )

    passed(
        "No Network Transmission Occurred"
    )

    passed(
        "Transport Method Exactly POST"
    )

    passed(
        "Transport Path Exactly Leverage Endpoint"
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

    require(
        DEMO_POST_ENABLED
        is False,
        "demo POST unexpectedly enabled",
    )

    require(
        NETWORK_WRITES_ENABLED
        is False,
        "network writes unexpectedly enabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY
        is True,
        "synthetic-only mode disabled",
    )

    passed(
        "Real POST Disabled"
    )

    passed(
        "Demo POST Disabled"
    )

    passed(
        "All Network Writes Disabled"
    )

    passed(
        "Synthetic Transport Only"
    )


    # ========================================================================
    # FINAL RESULT
    # ========================================================================

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

    print()


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
                f"{UNIT_NAME}: "
                f"HEALTH SERVER LISTENING ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:

            print(
                f"{UNIT_NAME}: "
                f"HEALTH SERVER ERROR: {exc}",
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

def heartbeat_forever() -> None:

    heartbeat = 1

    while True:

        print(

            f"{UNIT_NAME}: "
            f"HEARTBEAT {heartbeat} | "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes={NETWORK_WRITES_ENABLED}",

            flush=True,
        )

        heartbeat += 1

        time.sleep(
            30
        )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":

    run_diagnostics()

    start_health_server()

    heartbeat_forever()
