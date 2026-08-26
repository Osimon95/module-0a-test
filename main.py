# ============================================================================
# R28 UNIT N.31
# TRANSACTIONAL CHECKPOINT PROMOTION + COMMITTED-MANIFEST ANCHORING
#
# CORRECTED SINGLE-FILE COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.31 INCREMENT:
#   - TRANSACTIONAL CHECKPOINT PROMOTION
#   - PENDING PROMOTION INTENT
#   - COMMITTED MANIFEST ANCHORING
#   - CHECKPOINT/WAL PREFIX VALIDATION
#   - POST-CHECKPOINT WAL APPENDS ALLOWED
#   - CHECKPOINT HASH BOUNDARY PRESERVED
#   - PROMOTION REPLAY REJECTION
#   - STALE/TAMPERED CHECKPOINT REJECTION
#   - TRUNCATED WAL REJECTION
#   - COMMITTED AUTHORITY SURVIVES RESTART
#   - SYNTHETIC DISPATCH ONLY
#
# CRITICAL N.31 CORRECTION:
#
#   A checkpoint seals a HISTORICAL WAL PREFIX.
#
#   If checkpoint.wal_length == N, later records such as:
#
#       PROMOTION_INTENT
#       MANIFEST_COMMIT
#
#   may legitimately make the current WAL longer than N.
#
#   Therefore checkpoint validation requires:
#
#       len(current_wal) >= checkpoint.wal_length
#
#   and validates:
#
#       current_wal[:checkpoint.wal_length]
#
#   It MUST NOT require:
#
#       len(current_wal) == checkpoint.wal_length
#
# ============================================================================


print("R28 UNIT N.31: MAIN.PY ENTERED", flush=True)


# ============================================================================
# IMPORTS
# ============================================================================

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


print("R28 UNIT N.31: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.31"
UNIT_VERSION = "N.31"

SYMBOL = "BTCUSDT"

HTTP_METHOD = "POST"

LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TARGET_LEVERAGE = "100"
TARGET_MARGIN_MODE = "ISOLATED"

INTEGRITY_KEY = b"R28-N31-CHECKPOINT-INTEGRITY-KEY"
PROMOTION_KEY = b"R28-N31-PROMOTION-INTENT-KEY"
MANIFEST_KEY = b"R28-N31-COMMITTED-MANIFEST-KEY"
AUTHORIZATION_KEY = b"R28-N31-AUTHORIZATION-KEY"

EMPTY_WAL_HASH = hashlib.sha256(
    b"R28-N31-EMPTY-WAL"
).hexdigest()

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

PROMOTION_PENDING = "PENDING"
PROMOTION_COMMITTED = "COMMITTED"

CHECKPOINT_SLOT_A = "A"
CHECKPOINT_SLOT_B = "B"

VALID_CHECKPOINT_SLOTS = {
    CHECKPOINT_SLOT_A,
    CHECKPOINT_SLOT_B,
}

LINE_WIDTH = 92


print("R28 UNIT N.31: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# BASIC HELPERS
# ============================================================================

def stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def hmac_hex(
    key: bytes,
    value: str,
) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def now_ns() -> int:
    return time.time_ns()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def separator() -> None:
    print("-" * LINE_WIDTH, flush=True)


def banner(title: str) -> None:
    print("=" * LINE_WIDTH, flush=True)
    print(title, flush=True)
    print("=" * LINE_WIDTH, flush=True)


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
    condition: bool,
) -> None:
    if condition:
        print(
            f"{label:<76} ✅ PASS",
            flush=True,
        )
        return

    print(
        f"{label:<76} ❌ FAIL",
        flush=True,
    )

    raise AssertionError(label)


def local_block(
    message: str,
) -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK:",
        flush=True,
    )
    print(
        f"  {message}",
        flush=True,
    )


def expect_rejection(
    label: str,
    callback,
) -> None:
    rejected = False

    try:
        callback()

    except Exception as exc:
        rejected = True
        local_block(str(exc))

    pass_line(
        label,
        rejected,
    )


# ============================================================================
# PAYLOAD
# ============================================================================

def build_payload() -> Dict[str, str]:
    return {
        "symbol": SYMBOL,
        "marginMode": TARGET_MARGIN_MODE,
        "leverage": TARGET_LEVERAGE,
    }


def payload_hash(
    payload: Dict[str, Any],
) -> str:
    return sha256_text(
        stable_json(payload)
    )


# ============================================================================
# WAL MODEL
# ============================================================================

@dataclass
class WALRecord:
    sequence: int
    record_type: str

    generation: int
    lineage: str
    recovery_epoch: int

    payload: Dict[str, Any]

    previous_hash: str
    record_hash: str = ""


def wal_record_material(
    record: WALRecord,
) -> str:
    return stable_json(
        {
            "sequence": record.sequence,
            "record_type": record.record_type,
            "generation": record.generation,
            "lineage": record.lineage,
            "recovery_epoch": record.recovery_epoch,
            "payload": record.payload,
            "previous_hash": record.previous_hash,
        }
    )


def compute_wal_record_hash(
    record: WALRecord,
) -> str:
    return sha256_text(
        wal_record_material(record)
    )


def validate_wal(
    wal: List[WALRecord],
) -> None:
    expected_previous = EMPTY_WAL_HASH

    for expected_sequence, record in enumerate(
        wal,
        start=1,
    ):
        if record.sequence != expected_sequence:
            raise ValueError(
                "WAL sequence mismatch"
            )

        if record.previous_hash != expected_previous:
            raise ValueError(
                "WAL previous hash mismatch"
            )

        expected_hash = compute_wal_record_hash(
            record
        )

        if record.record_hash != expected_hash:
            raise ValueError(
                "WAL record hash mismatch"
            )

        expected_previous = record.record_hash


# ============================================================================
# RECOVERY LEASE
# ============================================================================

@dataclass
class RecoveryLease:
    lease_id: str
    owner: str

    generation: int
    lineage: str
    recovery_epoch: int

    nonce: int
    issued_ns: int


# ============================================================================
# AUTHORIZATION
# ============================================================================

@dataclass
class Authorization:
    authorization_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    payload_hash: str

    consumed: bool
    issued_ns: int

    seal: str = ""


def authorization_material(
    authorization: Authorization,
) -> str:
    return stable_json(
        {
            "authorization_id":
                authorization.authorization_id,

            "generation":
                authorization.generation,

            "lineage":
                authorization.lineage,

            "recovery_epoch":
                authorization.recovery_epoch,

            "payload_hash":
                authorization.payload_hash,

            "consumed":
                authorization.consumed,

            "issued_ns":
                authorization.issued_ns,
        }
    )


def compute_authorization_seal(
    authorization: Authorization,
) -> str:
    return hmac_hex(
        AUTHORIZATION_KEY,
        authorization_material(
            authorization
        ),
    )


def validate_authorization_seal(
    authorization: Authorization,
) -> None:
    expected = compute_authorization_seal(
        authorization
    )

    if not hmac.compare_digest(
        authorization.seal,
        expected,
    ):
        raise ValueError(
            "authorization integrity seal mismatch"
        )


# ============================================================================
# SYNTHETIC DISPATCH RECEIPT
# ============================================================================

@dataclass
class DispatchReceipt:
    dispatch_id: str

    generation: int
    lineage: str
    recovery_epoch: int

    method: str
    path: str

    payload_hash: str

    synthetic: bool
    transmitted: bool

    completed_ns: int


# ============================================================================
# CHECKPOINT MODEL
# ============================================================================

@dataclass
class CheckpointRecord:
    slot: str

    checkpoint_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    phase: str

    payload_hash: str

    wal_length: int
    wal_final_hash: str

    dispatch_count: int

    created_ns: int

    integrity_seal: str = ""


def checkpoint_material(
    checkpoint: CheckpointRecord,
) -> str:
    return stable_json(
        {
            "slot":
                checkpoint.slot,

            "checkpoint_sequence":
                checkpoint.checkpoint_sequence,

            "generation":
                checkpoint.generation,

            "lineage":
                checkpoint.lineage,

            "recovery_epoch":
                checkpoint.recovery_epoch,

            "phase":
                checkpoint.phase,

            "payload_hash":
                checkpoint.payload_hash,

            "wal_length":
                checkpoint.wal_length,

            "wal_final_hash":
                checkpoint.wal_final_hash,

            "dispatch_count":
                checkpoint.dispatch_count,

            "created_ns":
                checkpoint.created_ns,
        }
    )


def checkpoint_integrity_seal(
    checkpoint: CheckpointRecord,
) -> str:
    return hmac_hex(
        INTEGRITY_KEY,
        checkpoint_material(
            checkpoint
        ),
    )


def validate_checkpoint(
    checkpoint: CheckpointRecord,
    wal: List[WALRecord],
) -> None:
    """
    N.31 CORRECTED CHECKPOINT VALIDATOR.

    A checkpoint represents a historical prefix of the WAL.

    New WAL entries are allowed AFTER the checkpoint boundary.

    Therefore:

        len(wal) < checkpoint.wal_length
            => rejection

        len(wal) == checkpoint.wal_length
            => valid candidate

        len(wal) > checkpoint.wal_length
            => also valid candidate, provided the sealed prefix
               still validates exactly.

    This is the correction for the Test 9 failure:

        ValueError:
            checkpoint WAL length mismatch
    """

    if checkpoint.slot not in VALID_CHECKPOINT_SLOTS:
        raise ValueError(
            "checkpoint slot invalid"
        )

    if checkpoint.wal_length < 0:
        raise ValueError(
            "checkpoint WAL length invalid"
        )

    # ------------------------------------------------------------------
    # CRITICAL FIX:
    #
    # Old behavior effectively required:
    #
    #     len(wal) == checkpoint.wal_length
    #
    # That fails as soon as PROMOTION_INTENT is appended.
    #
    # Correct behavior only rejects truncation.
    # ------------------------------------------------------------------

    if len(wal) < checkpoint.wal_length:
        raise ValueError(
            "checkpoint WAL length mismatch"
        )

    # Historical WAL prefix represented by checkpoint.
    checkpoint_wal = wal[
        :checkpoint.wal_length
    ]

    # ------------------------------------------------------------------
    # Checkpoint integrity
    # ------------------------------------------------------------------

    expected_seal = checkpoint_integrity_seal(
        checkpoint
    )

    if not hmac.compare_digest(
        checkpoint.integrity_seal,
        expected_seal,
    ):
        raise ValueError(
            "checkpoint integrity seal mismatch"
        )

    # ------------------------------------------------------------------
    # Validate the exact historical WAL prefix.
    # ------------------------------------------------------------------

    validate_wal(
        checkpoint_wal
    )

    # ------------------------------------------------------------------
    # Validate checkpoint final WAL hash at checkpoint boundary.
    # ------------------------------------------------------------------

    if checkpoint.wal_length == 0:
        expected_final_hash = EMPTY_WAL_HASH

    else:
        expected_final_hash = (
            checkpoint_wal[-1].record_hash
        )

    if checkpoint.wal_final_hash != expected_final_hash:
        raise ValueError(
            "checkpoint WAL final hash mismatch"
        )


# ============================================================================
# PROMOTION INTENT
# ============================================================================

@dataclass
class PromotionIntent:
    intent_id: str

    slot: str
    checkpoint_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    checkpoint_wal_length: int
    checkpoint_wal_final_hash: str

    status: str

    created_ns: int

    seal: str = ""


def promotion_intent_material(
    intent: PromotionIntent,
) -> str:
    return stable_json(
        {
            "intent_id":
                intent.intent_id,

            "slot":
                intent.slot,

            "checkpoint_sequence":
                intent.checkpoint_sequence,

            "generation":
                intent.generation,

            "lineage":
                intent.lineage,

            "recovery_epoch":
                intent.recovery_epoch,

            "checkpoint_wal_length":
                intent.checkpoint_wal_length,

            "checkpoint_wal_final_hash":
                intent.checkpoint_wal_final_hash,

            "status":
                intent.status,

            "created_ns":
                intent.created_ns,
        }
    )


def promotion_intent_seal(
    intent: PromotionIntent,
) -> str:
    return hmac_hex(
        PROMOTION_KEY,
        promotion_intent_material(
            intent
        ),
    )


def validate_promotion_intent(
    intent: PromotionIntent,
) -> None:
    expected = promotion_intent_seal(
        intent
    )

    if not hmac.compare_digest(
        intent.seal,
        expected,
    ):
        raise ValueError(
            "promotion intent integrity seal mismatch"
        )


# ============================================================================
# COMMITTED MANIFEST
# ============================================================================

@dataclass
class CommittedManifest:
    manifest_sequence: int

    slot: str
    checkpoint_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    checkpoint_wal_length: int
    checkpoint_wal_final_hash: str

    promotion_intent_id: str

    committed_ns: int

    seal: str = ""


def manifest_material(
    manifest: CommittedManifest,
) -> str:
    return stable_json(
        {
            "manifest_sequence":
                manifest.manifest_sequence,

            "slot":
                manifest.slot,

            "checkpoint_sequence":
                manifest.checkpoint_sequence,

            "generation":
                manifest.generation,

            "lineage":
                manifest.lineage,

            "recovery_epoch":
                manifest.recovery_epoch,

            "checkpoint_wal_length":
                manifest.checkpoint_wal_length,

            "checkpoint_wal_final_hash":
                manifest.checkpoint_wal_final_hash,

            "promotion_intent_id":
                manifest.promotion_intent_id,

            "committed_ns":
                manifest.committed_ns,
        }
    )


def manifest_seal(
    manifest: CommittedManifest,
) -> str:
    return hmac_hex(
        MANIFEST_KEY,
        manifest_material(
            manifest
        ),
    )


def validate_manifest(
    manifest: CommittedManifest,
) -> None:
    expected = manifest_seal(
        manifest
    )

    if not hmac.compare_digest(
        manifest.seal,
        expected,
    ):
        raise ValueError(
            "committed manifest integrity seal mismatch"
        )


# ============================================================================
# DURABLE STATE
# ============================================================================

@dataclass
class DurableState:
    generation: int
    lineage: str
    recovery_epoch: int

    phase: str

    payload: Dict[str, Any]
    payload_hash: str

    wal: List[WALRecord] = field(
        default_factory=list
    )

    checkpoints: Dict[
        str,
        CheckpointRecord,
    ] = field(
        default_factory=dict
    )

    promotion_intents: Dict[
        str,
        PromotionIntent,
    ] = field(
        default_factory=dict
    )

    committed_manifest: Optional[
        CommittedManifest
    ] = None

    authorization: Optional[
        Authorization
    ] = None

    dispatch_receipts: List[
        DispatchReceipt
    ] = field(
        default_factory=list
    )

    checkpoint_sequence: int = 0
    manifest_sequence: int = 0

    lease_nonce: int = 0

    consumed_promotion_ids: List[str] = field(
        default_factory=list
    )


# ============================================================================
# N.31 ENGINE
# ============================================================================

class N31Engine:
    def __init__(
        self,
        state: Optional[DurableState] = None,
    ) -> None:

        self._lock = threading.RLock()

        if state is None:
            payload = build_payload()

            self.state = DurableState(
                generation=1,
                lineage=new_id(
                    "lineage"
                ),
                recovery_epoch=1,

                phase=PHASE_PREPARED,

                payload=payload,
                payload_hash=payload_hash(
                    payload
                ),
            )

            self._append_wal(
                "ENGINE_INITIALIZED",
                {
                    "phase":
                        PHASE_PREPARED,

                    "payload_hash":
                        self.state.payload_hash,
                },
            )

        else:
            self.state = copy.deepcopy(
                state
            )

            validate_wal(
                self.state.wal
            )

    # ========================================================================
    # WAL APPEND
    # ========================================================================

    def _append_wal(
        self,
        record_type: str,
        payload: Dict[str, Any],
    ) -> WALRecord:

        previous_hash = (
            self.state.wal[-1].record_hash
            if self.state.wal
            else EMPTY_WAL_HASH
        )

        record = WALRecord(
            sequence=len(
                self.state.wal
            ) + 1,

            record_type=record_type,

            generation=
                self.state.generation,

            lineage=
                self.state.lineage,

            recovery_epoch=
                self.state.recovery_epoch,

            payload=copy.deepcopy(
                payload
            ),

            previous_hash=
                previous_hash,
        )

        record.record_hash = (
            compute_wal_record_hash(
                record
            )
        )

        self.state.wal.append(
            record
        )

        return record

    # ========================================================================
    # LEASE
    # ========================================================================

    def acquire_recovery_lease(
        self,
        owner: str,
    ) -> RecoveryLease:

        with self._lock:

            self.state.lease_nonce += 1

            lease = RecoveryLease(
                lease_id=new_id(
                    "lease"
                ),

                owner=owner,

                generation=
                    self.state.generation,

                lineage=
                    self.state.lineage,

                recovery_epoch=
                    self.state.recovery_epoch,

                nonce=
                    self.state.lease_nonce,

                issued_ns=now_ns(),
            )

            self._append_wal(
                "RECOVERY_LEASE_ACQUIRED",
                {
                    "lease_id":
                        lease.lease_id,

                    "owner":
                        lease.owner,

                    "nonce":
                        lease.nonce,
                },
            )

            return lease

    def validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:

        if lease.generation != self.state.generation:
            raise ValueError(
                "recovery lease generation mismatch"
            )

        if lease.lineage != self.state.lineage:
            raise ValueError(
                "recovery lease lineage mismatch"
            )

        if (
            lease.recovery_epoch
            != self.state.recovery_epoch
        ):
            raise ValueError(
                "recovery lease epoch mismatch"
            )

    # ========================================================================
    # AUTHORIZATION
    # ========================================================================

    def authorize(
        self,
        lease: RecoveryLease,
    ) -> Authorization:

        with self._lock:

            self.validate_lease(
                lease
            )

            if self.state.phase != PHASE_PREPARED:
                raise ValueError(
                    "generation is not prepared"
                )

            authorization = Authorization(
                authorization_id=new_id(
                    "authorization"
                ),

                generation=
                    self.state.generation,

                lineage=
                    self.state.lineage,

                recovery_epoch=
                    self.state.recovery_epoch,

                payload_hash=
                    self.state.payload_hash,

                consumed=False,

                issued_ns=now_ns(),
            )

            authorization.seal = (
                compute_authorization_seal(
                    authorization
                )
            )

            self.state.authorization = (
                authorization
            )

            self.state.phase = (
                PHASE_AUTHORIZED
            )

            self._append_wal(
                "AUTHORIZED",
                {
                    "authorization_id":
                        authorization.authorization_id,

                    "payload_hash":
                        authorization.payload_hash,
                },
            )

            return copy.deepcopy(
                authorization
            )

    # ========================================================================
    # SYNTHETIC DISPATCH
    # ========================================================================

    def synthetic_dispatch(
        self,
        authorization: Authorization,
    ) -> DispatchReceipt:

        with self._lock:

            if REAL_POST_ENABLED:
                raise RuntimeError(
                    "real network POST is disabled"
                )

            if DEMO_POST_ENABLED:
                raise RuntimeError(
                    "demo network POST is disabled"
                )

            if NETWORK_WRITES_ENABLED:
                raise RuntimeError(
                    "network writes are disabled"
                )

            if not SYNTHETIC_TRANSPORT_ONLY:
                raise RuntimeError(
                    "synthetic-only transport required"
                )

            stored = self.state.authorization

            if stored is None:
                raise ValueError(
                    "authorization missing"
                )

            validate_authorization_seal(
                authorization
            )

            validate_authorization_seal(
                stored
            )

            if (
                authorization.authorization_id
                != stored.authorization_id
            ):
                raise ValueError(
                    "authorization identity mismatch"
                )

            if stored.consumed:
                raise ValueError(
                    "authorization already consumed"
                )

            if (
                authorization.generation
                != self.state.generation
            ):
                raise ValueError(
                    "authorization generation mismatch"
                )

            if (
                authorization.lineage
                != self.state.lineage
            ):
                raise ValueError(
                    "authorization lineage mismatch"
                )

            if (
                authorization.recovery_epoch
                != self.state.recovery_epoch
            ):
                raise ValueError(
                    "authorization recovery epoch mismatch"
                )

            if (
                authorization.payload_hash
                != self.state.payload_hash
            ):
                raise ValueError(
                    "authorization payload hash mismatch"
                )

            # ----------------------------------------------------------------
            # Consume durable authorization.
            # ----------------------------------------------------------------

            self.state.authorization.consumed = True

            self.state.authorization.seal = (
                compute_authorization_seal(
                    self.state.authorization
                )
            )

            self.state.phase = PHASE_DISPATCHED

            self._append_wal(
                "AUTHORIZATION_CONSUMED",
                {
                    "authorization_id":
                        authorization.authorization_id,
                },
            )

            # ----------------------------------------------------------------
            # SYNTHETIC RECEIPT ONLY.
            #
            # transmitted=False is mandatory.
            # ----------------------------------------------------------------

            receipt = DispatchReceipt(
                dispatch_id=new_id(
                    "synthetic-dispatch"
                ),

                generation=
                    self.state.generation,

                lineage=
                    self.state.lineage,

                recovery_epoch=
                    self.state.recovery_epoch,

                method=HTTP_METHOD,

                path=LEVERAGE_ENDPOINT,

                payload_hash=
                    self.state.payload_hash,

                synthetic=True,

                transmitted=False,

                completed_ns=now_ns(),
            )

            self.state.dispatch_receipts.append(
                receipt
            )

            self._append_wal(
                "SYNTHETIC_DISPATCH",
                {
                    "dispatch_id":
                        receipt.dispatch_id,

                    "method":
                        receipt.method,

                    "path":
                        receipt.path,

                    "payload_hash":
                        receipt.payload_hash,

                    "synthetic":
                        receipt.synthetic,

                    "transmitted":
                        receipt.transmitted,
                },
            )

            self.state.phase = PHASE_COMPLETED

            self._append_wal(
                "GENERATION_COMPLETED",
                {
                    "dispatch_id":
                        receipt.dispatch_id,
                },
            )

            return copy.deepcopy(
                receipt
            )

    # ========================================================================
    # CHECKPOINT
    # ========================================================================

    def create_checkpoint(
        self,
        slot: str,
    ) -> CheckpointRecord:

        with self._lock:

            if slot not in VALID_CHECKPOINT_SLOTS:
                raise ValueError(
                    "checkpoint slot invalid"
                )

            validate_wal(
                self.state.wal
            )

            self.state.checkpoint_sequence += 1

            wal_length = len(
                self.state.wal
            )

            if wal_length == 0:
                wal_final_hash = (
                    EMPTY_WAL_HASH
                )

            else:
                wal_final_hash = (
                    self.state
                    .wal[-1]
                    .record_hash
                )

            checkpoint = CheckpointRecord(
                slot=slot,

                checkpoint_sequence=
                    self.state.checkpoint_sequence,

                generation=
                    self.state.generation,

                lineage=
                    self.state.lineage,

                recovery_epoch=
                    self.state.recovery_epoch,

                phase=
                    self.state.phase,

                payload_hash=
                    self.state.payload_hash,

                wal_length=
                    wal_length,

                wal_final_hash=
                    wal_final_hash,

                dispatch_count=len(
                    self.state.dispatch_receipts
                ),

                created_ns=now_ns(),
            )

            checkpoint.integrity_seal = (
                checkpoint_integrity_seal(
                    checkpoint
                )
            )

            # IMPORTANT:
            #
            # Store checkpoint BEFORE adding any
            # post-checkpoint WAL activity.
            #
            # Its WAL boundary remains historical.
            self.state.checkpoints[
                slot
            ] = copy.deepcopy(
                checkpoint
            )

            return copy.deepcopy(
                checkpoint
            )

    # ========================================================================
    # PROMOTION INTENT
    # ========================================================================

    def create_promotion_intent(
        self,
        slot: str,
    ) -> PromotionIntent:

        with self._lock:

            checkpoint = (
                self.state.checkpoints.get(
                    slot
                )
            )

            if checkpoint is None:
                raise ValueError(
                    "checkpoint missing"
                )

            # Correct N.31 prefix-aware validation.
            validate_checkpoint(
                checkpoint,
                self.state.wal,
            )

            intent = PromotionIntent(
                intent_id=new_id(
                    "promotion"
                ),

                slot=checkpoint.slot,

                checkpoint_sequence=
                    checkpoint.checkpoint_sequence,

                generation=
                    checkpoint.generation,

                lineage=
                    checkpoint.lineage,

                recovery_epoch=
                    checkpoint.recovery_epoch,

                checkpoint_wal_length=
                    checkpoint.wal_length,

                checkpoint_wal_final_hash=
                    checkpoint.wal_final_hash,

                status=
                    PROMOTION_PENDING,

                created_ns=now_ns(),
            )

            intent.seal = (
                promotion_intent_seal(
                    intent
                )
            )

            self.state.promotion_intents[
                intent.intent_id
            ] = copy.deepcopy(
                intent
            )

            # ---------------------------------------------------------------
            # This append is AFTER checkpoint creation.
            #
            # Consequently:
            #
            #     current WAL length
            #         >
            #     checkpoint WAL length
            #
            # That is VALID in N.31.
            # ---------------------------------------------------------------

            self._append_wal(
                "PROMOTION_INTENT",
                {
                    "intent_id":
                        intent.intent_id,

                    "slot":
                        intent.slot,

                    "checkpoint_sequence":
                        intent.checkpoint_sequence,

                    "checkpoint_wal_length":
                        intent.checkpoint_wal_length,

                    "checkpoint_wal_final_hash":
                        intent.checkpoint_wal_final_hash,
                },
            )

            return copy.deepcopy(
                intent
            )

    # ========================================================================
    # CHECKPOINT PROMOTION
    # ========================================================================

    def commit_checkpoint_promotion(
        self,
        intent: PromotionIntent,
    ) -> CommittedManifest:

        with self._lock:

            validate_promotion_intent(
                intent
            )

            stored_intent = (
                self.state
                .promotion_intents
                .get(intent.intent_id)
            )

            if stored_intent is None:
                raise ValueError(
                    "promotion intent not found"
                )

            validate_promotion_intent(
                stored_intent
            )

            if (
                intent.intent_id
                in self.state.consumed_promotion_ids
            ):
                raise ValueError(
                    "promotion intent already consumed"
                )

            if (
                stored_intent.status
                != PROMOTION_PENDING
            ):
                raise ValueError(
                    "promotion intent is not pending"
                )

            if (
                intent.slot
                != stored_intent.slot
            ):
                raise ValueError(
                    "promotion intent slot mismatch"
                )

            if (
                intent.checkpoint_sequence
                != stored_intent.checkpoint_sequence
            ):
                raise ValueError(
                    "promotion checkpoint sequence mismatch"
                )

            checkpoint = (
                self.state
                .checkpoints
                .get(intent.slot)
            )

            if checkpoint is None:
                raise ValueError(
                    "promotion checkpoint missing"
                )

            # ================================================================
            # CRITICAL N.31 CORRECTION
            #
            # The current WAL already contains PROMOTION_INTENT.
            #
            # Therefore it is EXPECTED to be longer than the checkpoint WAL.
            #
            # validate_checkpoint() validates the historical prefix:
            #
            #     self.state.wal[:checkpoint.wal_length]
            #
            # It does not demand total-WAL equality.
            # ================================================================

            validate_checkpoint(
                checkpoint,
                self.state.wal,
            )

            # ----------------------------------------------------------------
            # Cross-bind promotion intent to checkpoint.
            # ----------------------------------------------------------------

            if (
                checkpoint.checkpoint_sequence
                != intent.checkpoint_sequence
            ):
                raise ValueError(
                    "promotion target checkpoint sequence mismatch"
                )

            if (
                checkpoint.generation
                != intent.generation
            ):
                raise ValueError(
                    "promotion generation mismatch"
                )

            if (
                checkpoint.lineage
                != intent.lineage
            ):
                raise ValueError(
                    "promotion lineage mismatch"
                )

            if (
                checkpoint.recovery_epoch
                != intent.recovery_epoch
            ):
                raise ValueError(
                    "promotion recovery epoch mismatch"
                )

            if (
                checkpoint.wal_length
                != intent.checkpoint_wal_length
            ):
                raise ValueError(
                    "promotion checkpoint WAL length mismatch"
                )

            if (
                checkpoint.wal_final_hash
                != intent.checkpoint_wal_final_hash
            ):
                raise ValueError(
                    "promotion checkpoint WAL final hash mismatch"
                )

            # ----------------------------------------------------------------
            # Manifest creation.
            # ----------------------------------------------------------------

            self.state.manifest_sequence += 1

            manifest = CommittedManifest(
                manifest_sequence=
                    self.state.manifest_sequence,

                slot=
                    checkpoint.slot,

                checkpoint_sequence=
                    checkpoint.checkpoint_sequence,

                generation=
                    checkpoint.generation,

                lineage=
                    checkpoint.lineage,

                recovery_epoch=
                    checkpoint.recovery_epoch,

                checkpoint_wal_length=
                    checkpoint.wal_length,

                checkpoint_wal_final_hash=
                    checkpoint.wal_final_hash,

                promotion_intent_id=
                    intent.intent_id,

                committed_ns=now_ns(),
            )

            manifest.seal = (
                manifest_seal(
                    manifest
                )
            )

            validate_manifest(
                manifest
            )

            # ----------------------------------------------------------------
            # Commit manifest authority BEFORE appending MANIFEST_COMMIT.
            # ----------------------------------------------------------------

            self.state.committed_manifest = (
                copy.deepcopy(
                    manifest
                )
            )

            # ----------------------------------------------------------------
            # Mark promotion consumed.
            # ----------------------------------------------------------------

            stored_intent.status = (
                PROMOTION_COMMITTED
            )

            stored_intent.seal = (
                promotion_intent_seal(
                    stored_intent
                )
            )

            self.state.promotion_intents[
                stored_intent.intent_id
            ] = stored_intent

            self.state.consumed_promotion_ids.append(
                intent.intent_id
            )

            # ----------------------------------------------------------------
            # MANIFEST_COMMIT is also AFTER checkpoint boundary.
            # ----------------------------------------------------------------

            self._append_wal(
                "MANIFEST_COMMIT",
                {
                    "manifest_sequence":
                        manifest.manifest_sequence,

                    "slot":
                        manifest.slot,

                    "checkpoint_sequence":
                        manifest.checkpoint_sequence,

                    "promotion_intent_id":
                        manifest.promotion_intent_id,

                    "checkpoint_wal_length":
                        manifest.checkpoint_wal_length,

                    "checkpoint_wal_final_hash":
                        manifest.checkpoint_wal_final_hash,
                },
            )

            return copy.deepcopy(
                manifest
            )

    # ========================================================================
    # COMMITTED MANIFEST RECOVERY
    # ========================================================================

    def recover_committed_checkpoint(
        self,
    ) -> CheckpointRecord:

        with self._lock:

            manifest = (
                self.state.committed_manifest
            )

            if manifest is None:
                raise ValueError(
                    "committed manifest missing"
                )

            validate_manifest(
                manifest
            )

            checkpoint = (
                self.state
                .checkpoints
                .get(manifest.slot)
            )

            if checkpoint is None:
                raise ValueError(
                    "manifest checkpoint missing"
                )

            validate_checkpoint(
                checkpoint,
                self.state.wal,
            )

            if (
                checkpoint.checkpoint_sequence
                != manifest.checkpoint_sequence
            ):
                raise ValueError(
                    "manifest checkpoint sequence mismatch"
                )

            if (
                checkpoint.generation
                != manifest.generation
            ):
                raise ValueError(
                    "manifest generation mismatch"
                )

            if (
                checkpoint.lineage
                != manifest.lineage
            ):
                raise ValueError(
                    "manifest lineage mismatch"
                )

            if (
                checkpoint.recovery_epoch
                != manifest.recovery_epoch
            ):
                raise ValueError(
                    "manifest recovery epoch mismatch"
                )

            if (
                checkpoint.wal_length
                != manifest.checkpoint_wal_length
            ):
                raise ValueError(
                    "manifest checkpoint WAL length mismatch"
                )

            if (
                checkpoint.wal_final_hash
                != manifest.checkpoint_wal_final_hash
            ):
                raise ValueError(
                    "manifest checkpoint WAL final hash mismatch"
                )

            return copy.deepcopy(
                checkpoint
            )

    # ========================================================================
    # PENDING PROMOTION RECOVERY
    # ========================================================================

    def recover_pending_promotion(
        self,
    ) -> Optional[CommittedManifest]:

        with self._lock:

            pending = []

            for intent in (
                self.state
                .promotion_intents
                .values()
            ):
                validate_promotion_intent(
                    intent
                )

                if (
                    intent.status
                    == PROMOTION_PENDING
                ):
                    pending.append(
                        copy.deepcopy(
                            intent
                        )
                    )

            if not pending:
                return None

            pending.sort(
                key=lambda item:
                    item.created_ns
            )

            # Deterministic oldest pending promotion.
            intent = pending[0]

            return self.commit_checkpoint_promotion(
                intent
            )

    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(
        self,
    ) -> None:

        with self._lock:

            old_generation = (
                self.state.generation
            )

            old_epoch = (
                self.state.recovery_epoch
            )

            self.state.generation += 1
            self.state.recovery_epoch += 1

            self.state.lineage = new_id(
                "lineage"
            )

            self.state.phase = (
                PHASE_PREPARED
            )

            self.state.authorization = None

            self._append_wal(
                "GENERATION_ADVANCED",
                {
                    "old_generation":
                        old_generation,

                    "new_generation":
                        self.state.generation,

                    "old_recovery_epoch":
                        old_epoch,

                    "new_recovery_epoch":
                        self.state.recovery_epoch,
                },
            )

    # ========================================================================
    # RESTART
    # ========================================================================

    def snapshot(
        self,
    ) -> DurableState:

        with self._lock:

            return copy.deepcopy(
                self.state
            )

    @classmethod
    def restore_state(
        cls,
        state: DurableState,
    ) -> "N31Engine":

        return cls(
            state=copy.deepcopy(
                state
            )
        )


print("R28 UNIT N.31: ENGINE DEFINITIONS LOADED", flush=True)


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def run_diagnostics() -> None:

    banner(
        "R28 UNIT N.31 — TRANSACTIONAL CHECKPOINT PROMOTION + "
        "COMMITTED-MANIFEST ANCHORING"
    )

    # ========================================================================
    # TEST 1
    # ========================================================================

    test_header(
        1,
        "ENGINE INITIALIZATION",
    )

    engine = N31Engine()

    pass_line(
        "Engine Starts PREPARED",
        engine.state.phase
        == PHASE_PREPARED,
    )

    pass_line(
        "Initial Generation Is One",
        engine.state.generation == 1,
    )

    pass_line(
        "Initial Recovery Epoch Is One",
        engine.state.recovery_epoch == 1,
    )

    pass_line(
        "Payload Hash Established",
        bool(
            engine.state.payload_hash
        ),
    )

    # ========================================================================
    # TEST 2
    # ========================================================================

    test_header(
        2,
        "RECOVERY LEASE BINDING",
    )

    lease = engine.acquire_recovery_lease(
        "worker-N31"
    )

    pass_line(
        "Lease Bound To Current Generation",
        lease.generation
        == engine.state.generation,
    )

    pass_line(
        "Lease Bound To Current Lineage",
        lease.lineage
        == engine.state.lineage,
    )

    pass_line(
        "Lease Bound To Current Recovery Epoch",
        lease.recovery_epoch
        == engine.state.recovery_epoch,
    )

    # ========================================================================
    # TEST 3
    # ========================================================================

    test_header(
        3,
        "AUTHORIZATION BINDING",
    )

    authorization = engine.authorize(
        lease
    )

    pass_line(
        "Authorization Bound To Generation",
        authorization.generation
        == engine.state.generation,
    )

    pass_line(
        "Authorization Bound To Lineage",
        authorization.lineage
        == engine.state.lineage,
    )

    pass_line(
        "Authorization Payload Hash Preserved",
        authorization.payload_hash
        == engine.state.payload_hash,
    )

    # ========================================================================
    # TEST 4
    # ========================================================================

    test_header(
        4,
        "SYNTHETIC DISPATCH",
    )

    receipt = engine.synthetic_dispatch(
        authorization
    )

    pass_line(
        "Synthetic Dispatch Completed",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    pass_line(
        "Exactly One Dispatch Produced",
        len(
            engine.state.dispatch_receipts
        ) == 1,
    )

    pass_line(
        "Dispatch Is Synthetic",
        (
            receipt.synthetic
            and not receipt.transmitted
        ),
    )

    # ========================================================================
    # TEST 5
    # ========================================================================

    test_header(
        5,
        "CHECKPOINT CREATION",
    )

    checkpoint = engine.create_checkpoint(
        CHECKPOINT_SLOT_A
    )

    pass_line(
        "Checkpoint Created In Valid Slot",
        checkpoint.slot
        in VALID_CHECKPOINT_SLOTS,
    )

    pass_line(
        "Checkpoint Bound To Current Generation",
        checkpoint.generation
        == engine.state.generation,
    )

    pass_line(
        "Checkpoint Bound To Current Lineage",
        checkpoint.lineage
        == engine.state.lineage,
    )

    pass_line(
        "Checkpoint WAL Length Preserved",
        checkpoint.wal_length
        == len(engine.state.wal),
    )

    # ========================================================================
    # TEST 6
    # ========================================================================

    test_header(
        6,
        "CHECKPOINT INTEGRITY VALIDATION",
    )

    validate_checkpoint(
        checkpoint,
        engine.state.wal,
    )

    pass_line(
        "Checkpoint Integrity Validates",
        True,
    )

    # ========================================================================
    # TEST 7
    # ========================================================================

    test_header(
        7,
        "PROMOTION INTENT CREATION",
    )

    intent = engine.create_promotion_intent(
        CHECKPOINT_SLOT_A
    )

    pass_line(
        "Promotion Intent Is Pending",
        intent.status
        == PROMOTION_PENDING,
    )

    pass_line(
        "Promotion Targets Correct Slot",
        intent.slot
        == checkpoint.slot,
    )

    pass_line(
        "Promotion Targets Correct Checkpoint Sequence",
        intent.checkpoint_sequence
        == checkpoint.checkpoint_sequence,
    )

    pass_line(
        "Promotion Bound To Current Generation",
        intent.generation
        == engine.state.generation,
    )

    # ========================================================================
    # TEST 8
    # ========================================================================

    test_header(
        8,
        "PROMOTION INTENT INTEGRITY",
    )

    validate_promotion_intent(
        intent
    )

    pass_line(
        "Promotion Intent Seal Validates",
        True,
    )

    # ========================================================================
    # TEST 9
    #
    # THIS IS THE TEST THAT PREVIOUSLY FAILED WITH:
    #
    #     ValueError:
    #         checkpoint WAL length mismatch
    #
    # ========================================================================

    test_header(
        9,
        "COMMITTED MANIFEST PROMOTION",
    )

    wal_length_before_commit = len(
        engine.state.wal
    )

    pass_line(
        "Current WAL Extends Beyond Checkpoint Boundary",
        wal_length_before_commit
        > checkpoint.wal_length,
    )

    # ------------------------------------------------------------------------
    # This must now succeed.
    #
    # validate_checkpoint() validates the historical prefix instead of
    # incorrectly requiring the current WAL to be exactly the same length.
    # ------------------------------------------------------------------------

    manifest = (
        engine.commit_checkpoint_promotion(
            intent
        )
    )

    pass_line(
        "Checkpoint Promotion Committed",
        engine.state.committed_manifest
        is not None,
    )

    pass_line(
        "Committed Manifest Targets Correct Slot",
        manifest.slot
        == checkpoint.slot,
    )

    pass_line(
        "Committed Manifest Targets Correct Checkpoint",
        manifest.checkpoint_sequence
        == checkpoint.checkpoint_sequence,
    )

    pass_line(
        "Manifest Anchors Checkpoint WAL Length",
        manifest.checkpoint_wal_length
        == checkpoint.wal_length,
    )

    pass_line(
        "Manifest Anchors Checkpoint WAL Final Hash",
        manifest.checkpoint_wal_final_hash
        == checkpoint.wal_final_hash,
    )

    # ========================================================================
    # TEST 10
    # ========================================================================

    test_header(
        10,
        "POST-PROMOTION CHECKPOINT VALIDATION",
    )

    pass_line(
        "Current WAL Is Longer Than Promoted Checkpoint",
        len(engine.state.wal)
        > checkpoint.wal_length,
    )

    validate_checkpoint(
        checkpoint,
        engine.state.wal,
    )

    pass_line(
        "Historical Checkpoint Still Validates Against WAL Prefix",
        True,
    )

    # ========================================================================
    # TEST 11
    # ========================================================================

    test_header(
        11,
        "COMMITTED MANIFEST INTEGRITY",
    )

    validate_manifest(
        manifest
    )

    pass_line(
        "Committed Manifest Integrity Validates",
        True,
    )

    # ========================================================================
    # TEST 12
    # ========================================================================

    test_header(
        12,
        "PROMOTION REPLAY REJECTION",
    )

    expect_rejection(
        "Consumed Promotion Intent Replay Rejected",
        lambda:
            engine.commit_checkpoint_promotion(
                intent
            ),
    )

    # ========================================================================
    # TEST 13
    # ========================================================================

    test_header(
        13,
        "CHECKPOINT TAMPER REJECTION",
    )

    tampered_checkpoint = copy.deepcopy(
        checkpoint
    )

    tampered_checkpoint.payload_hash = (
        sha256_text(
            "tampered-payload"
        )
    )

    expect_rejection(
        "Tampered Checkpoint Rejected",
        lambda:
            validate_checkpoint(
                tampered_checkpoint,
                engine.state.wal,
            ),
    )

    # ========================================================================
    # TEST 14
    # ========================================================================

    test_header(
        14,
        "TRUNCATED WAL REJECTION",
    )

    truncated_wal = copy.deepcopy(
        engine.state.wal[
            :max(
                checkpoint.wal_length - 1,
                0,
            )
        ]
    )

    expect_rejection(
        "Checkpoint With Truncated WAL Rejected",
        lambda:
            validate_checkpoint(
                checkpoint,
                truncated_wal,
            ),
    )

    # ========================================================================
    # TEST 15
    # ========================================================================

    test_header(
        15,
        "CHECKPOINT WAL PREFIX TAMPER REJECTION",
    )

    tampered_wal = copy.deepcopy(
        engine.state.wal
    )

    if checkpoint.wal_length > 0:
        tampered_wal[
            checkpoint.wal_length - 1
        ].payload["tampered"] = True

    expect_rejection(
        "Tampered Checkpoint WAL Prefix Rejected",
        lambda:
            validate_checkpoint(
                checkpoint,
                tampered_wal,
            ),
    )

    # ========================================================================
    # TEST 16
    # ========================================================================

    test_header(
        16,
        "POST-CHECKPOINT WAL TAIL IS NOT PART OF CHECKPOINT",
    )

    extended_wal = copy.deepcopy(
        engine.state.wal
    )

    previous_hash = (
        extended_wal[-1].record_hash
        if extended_wal
        else EMPTY_WAL_HASH
    )

    harmless_tail = WALRecord(
        sequence=len(
            extended_wal
        ) + 1,

        record_type=
            "POST_CHECKPOINT_DIAGNOSTIC",

        generation=
            engine.state.generation,

        lineage=
            engine.state.lineage,

        recovery_epoch=
            engine.state.recovery_epoch,

        payload={
            "diagnostic": True,
        },

        previous_hash=
            previous_hash,
    )

    harmless_tail.record_hash = (
        compute_wal_record_hash(
            harmless_tail
        )
    )

    extended_wal.append(
        harmless_tail
    )

    validate_checkpoint(
        checkpoint,
        extended_wal,
    )

    pass_line(
        "Valid Post-Checkpoint WAL Tail Accepted",
        len(extended_wal)
        > checkpoint.wal_length,
    )

    # ========================================================================
    # TEST 17
    # ========================================================================

    test_header(
        17,
        "COMMITTED CHECKPOINT RECOVERY",
    )

    recovered_checkpoint = (
        engine.recover_committed_checkpoint()
    )

    pass_line(
        "Authoritative Checkpoint Recovered",
        recovered_checkpoint.slot
        == manifest.slot,
    )

    pass_line(
        "Recovered Checkpoint Matches Manifest Slot",
        recovered_checkpoint.slot
        == manifest.slot,
    )

    pass_line(
        "Recovered Checkpoint Matches Manifest Sequence",
        recovered_checkpoint.checkpoint_sequence
        == manifest.checkpoint_sequence,
    )

    # ========================================================================
    # TEST 18
    # ========================================================================

    test_header(
        18,
        "COMMITTED AUTHORITY SURVIVES RESTART",
    )

    snapshot = engine.snapshot()

    restarted = N31Engine.restore_state(
        snapshot
    )

    pass_line(
        "Committed Manifest Survives Restart",
        restarted.state.committed_manifest
        is not None,
    )

    recovered_after_restart = (
        restarted.recover_committed_checkpoint()
    )

    pass_line(
        "Committed Authority Remains Recoverable",
        recovered_after_restart.checkpoint_sequence
        == checkpoint.checkpoint_sequence,
    )

    # ========================================================================
    # TEST 19
    # ========================================================================

    test_header(
        19,
        "MANIFEST TAMPER REJECTION",
    )

    tampered_manifest_engine = (
        N31Engine.restore_state(
            snapshot
        )
    )

    tampered_manifest_engine.state.committed_manifest.slot = (
        CHECKPOINT_SLOT_B
    )

    expect_rejection(
        "Tampered Committed Manifest Rejected",
        lambda:
            tampered_manifest_engine
            .recover_committed_checkpoint(),
    )

    # ========================================================================
    # TEST 20
    # ========================================================================

    test_header(
        20,
        "PENDING PROMOTION SURVIVES RESTART",
    )

    pending_engine = N31Engine()

    pending_lease = (
        pending_engine.acquire_recovery_lease(
            "pending-worker"
        )
    )

    pending_auth = pending_engine.authorize(
        pending_lease
    )

    pending_engine.synthetic_dispatch(
        pending_auth
    )

    pending_checkpoint = (
        pending_engine.create_checkpoint(
            CHECKPOINT_SLOT_A
        )
    )

    pending_intent = (
        pending_engine.create_promotion_intent(
            CHECKPOINT_SLOT_A
        )
    )

    pending_snapshot = (
        pending_engine.snapshot()
    )

    pending_restart = (
        N31Engine.restore_state(
            pending_snapshot
        )
    )

    pass_line(
        "Pending Promotion Intent Survives Restart",
        (
            pending_intent.intent_id
            in pending_restart.state.promotion_intents
        ),
    )

    recovered_manifest = (
        pending_restart
        .recover_pending_promotion()
    )

    pass_line(
        "Pending Promotion Commits After Restart",
        recovered_manifest
        is not None,
    )

    pass_line(
        "Recovered Promotion Anchors Original Checkpoint",
        (
            recovered_manifest.checkpoint_sequence
            == pending_checkpoint.checkpoint_sequence
        ),
    )

    # ========================================================================
    # TEST 21
    # ========================================================================

    test_header(
        21,
        "STALE CHECKPOINT REJECTION AFTER PREFIX LOSS",
    )

    stale_engine = N31Engine.restore_state(
        snapshot
    )

    stale_checkpoint = copy.deepcopy(
        checkpoint
    )

    # Remove one WAL record from checkpoint prefix.
    stale_engine.state.wal = (
        stale_engine.state.wal[
            :checkpoint.wal_length - 1
        ]
    )

    expect_rejection(
        "Stale Checkpoint Without Full WAL Prefix Rejected",
        lambda:
            validate_checkpoint(
                stale_checkpoint,
                stale_engine.state.wal,
            ),
    )

    # ========================================================================
    # TEST 22
    # ========================================================================

    test_header(
        22,
        "CHECKPOINT FINAL HASH MISMATCH",
    )

    wrong_hash_checkpoint = (
        copy.deepcopy(
            checkpoint
        )
    )

    wrong_hash_checkpoint.wal_final_hash = (
        sha256_text(
            "wrong-final-hash"
        )
    )

    # Reseal to ensure the rejection is caused by WAL binding,
    # not simply by a stale outer integrity seal.
    wrong_hash_checkpoint.integrity_seal = (
        checkpoint_integrity_seal(
            wrong_hash_checkpoint
        )
    )

    expect_rejection(
        "Checkpoint To WAL Final Hash Mismatch Rejected",
        lambda:
            validate_checkpoint(
                wrong_hash_checkpoint,
                engine.state.wal,
            ),
    )

    # ========================================================================
    # TEST 23
    # ========================================================================

    test_header(
        23,
        "MANIFEST/CHECKPOINT SLOT MISMATCH",
    )

    slot_mismatch_engine = (
        N31Engine.restore_state(
            snapshot
        )
    )

    original_manifest = (
        slot_mismatch_engine
        .state
        .committed_manifest
    )

    assert original_manifest is not None

    forged = copy.deepcopy(
        original_manifest
    )

    forged.slot = CHECKPOINT_SLOT_B

    forged.seal = manifest_seal(
        forged
    )

    slot_mismatch_engine.state.committed_manifest = (
        forged
    )

    expect_rejection(
        "Manifest Pointing To Missing Checkpoint Slot Rejected",
        lambda:
            slot_mismatch_engine
            .recover_committed_checkpoint(),
    )

    # ========================================================================
    # TEST 24
    # ========================================================================

    test_header(
        24,
        "GENERATION ADVANCE",
    )

    generation_engine = (
        N31Engine.restore_state(
            snapshot
        )
    )

    old_generation = (
        generation_engine.state.generation
    )

    old_lineage = (
        generation_engine.state.lineage
    )

    old_epoch = (
        generation_engine.state.recovery_epoch
    )

    generation_engine.advance_generation()

    pass_line(
        "Generation Advanced Monotonically",
        generation_engine.state.generation
        == old_generation + 1,
    )

    pass_line(
        "Recovery Epoch Advanced Monotonically",
        generation_engine.state.recovery_epoch
        == old_epoch + 1,
    )

    pass_line(
        "New Generation Uses Different Lineage",
        generation_engine.state.lineage
        != old_lineage,
    )

    pass_line(
        "New Generation Returns To PREPARED",
        generation_engine.state.phase
        == PHASE_PREPARED,
    )

    # ========================================================================
    # TEST 25
    # ========================================================================

    test_header(
        25,
        "ANTI-ABA STALE LEASE REJECTION",
    )

    stale_lease_engine = N31Engine()

    old_lease = (
        stale_lease_engine
        .acquire_recovery_lease(
            "aba-worker"
        )
    )

    stale_lease_engine.advance_generation()

    expect_rejection(
        "Prior Generation Lease Rejected",
        lambda:
            stale_lease_engine.validate_lease(
                old_lease
            ),
    )

    # ========================================================================
    # TEST 26
    # ========================================================================

    test_header(
        26,
        "AUTHORIZATION REPLAY REJECTION",
    )

    auth_replay_engine = N31Engine()

    auth_replay_lease = (
        auth_replay_engine
        .acquire_recovery_lease(
            "auth-replay-worker"
        )
    )

    auth_replay = (
        auth_replay_engine.authorize(
            auth_replay_lease
        )
    )

    auth_replay_engine.synthetic_dispatch(
        auth_replay
    )

    expect_rejection(
        "Consumed Authorization Replay Rejected",
        lambda:
            auth_replay_engine
            .synthetic_dispatch(
                auth_replay
            ),
    )

    # ========================================================================
    # TEST 27
    # ========================================================================

    test_header(
        27,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    pass_line(
        "Transport Method Exactly POST",
        receipt.method
        == HTTP_METHOD,
    )

    pass_line(
        "Transport Path Exactly Leverage Endpoint",
        receipt.path
        == LEVERAGE_ENDPOINT,
    )

    pass_line(
        "Transport Payload Hash Preserved",
        receipt.payload_hash
        == engine.state.payload_hash,
    )

    pass_line(
        "Dispatch Was Never Transmitted",
        not receipt.transmitted,
    )

    # ========================================================================
    # TEST 28
    # ========================================================================

    test_header(
        28,
        "FINAL NETWORK WRITE FIREBREAK",
    )

    pass_line(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    pass_line(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    pass_line(
        "All Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    pass_line(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    # ========================================================================
    # TEST 29
    # ========================================================================

    test_header(
        29,
        "WAL VALIDATION AFTER MANIFEST COMMIT",
    )

    validate_wal(
        engine.state.wal
    )

    pass_line(
        "Complete WAL Validates",
        True,
    )

    pass_line(
        "WAL Extends Beyond Checkpoint Without Invalidating It",
        len(engine.state.wal)
        > checkpoint.wal_length,
    )

    validate_checkpoint(
        checkpoint,
        engine.state.wal,
    )

    pass_line(
        "Checkpoint Historical WAL Prefix Remains Authoritative",
        True,
    )

    # ========================================================================
    # TEST 30
    # ========================================================================

    test_header(
        30,
        "FINAL COMMITTED AUTHORITY",
    )

    final_checkpoint = (
        engine.recover_committed_checkpoint()
    )

    final_manifest = (
        engine.state.committed_manifest
    )

    pass_line(
        "Committed Manifest Exists",
        final_manifest is not None,
    )

    pass_line(
        "Committed Checkpoint Is Recoverable",
        final_checkpoint.checkpoint_sequence
        == checkpoint.checkpoint_sequence,
    )

    pass_line(
        "Committed Authority Generation Preserved",
        final_checkpoint.generation
        == checkpoint.generation,
    )

    pass_line(
        "Committed Authority Lineage Preserved",
        final_checkpoint.lineage
        == checkpoint.lineage,
    )

    pass_line(
        "Committed Authority WAL Boundary Preserved",
        (
            final_checkpoint.wal_length
            == checkpoint.wal_length
        ),
    )

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    separator()

    print(
        f"{UNIT_NAME} DIAGNOSTIC SUMMARY",
        flush=True,
    )

    separator()

    print(
        f"Generation:              "
        f"{engine.state.generation}",
        flush=True,
    )

    print(
        f"Recovery Epoch:          "
        f"{engine.state.recovery_epoch}",
        flush=True,
    )

    print(
        f"Phase:                   "
        f"{engine.state.phase}",
        flush=True,
    )

    print(
        f"WAL Records:             "
        f"{len(engine.state.wal)}",
        flush=True,
    )

    print(
        f"Checkpoint Slot:         "
        f"{checkpoint.slot}",
        flush=True,
    )

    print(
        f"Checkpoint Sequence:     "
        f"{checkpoint.checkpoint_sequence}",
        flush=True,
    )

    print(
        f"Checkpoint WAL Length:   "
        f"{checkpoint.wal_length}",
        flush=True,
    )

    print(
        f"Current WAL Length:      "
        f"{len(engine.state.wal)}",
        flush=True,
    )

    print(
        f"Manifest Sequence:       "
        f"{manifest.manifest_sequence}",
        flush=True,
    )

    print(
        f"Synthetic Dispatches:    "
        f"{len(engine.state.dispatch_receipts)}",
        flush=True,
    )

    print(
        f"Real POST Enabled:       "
        f"{REAL_POST_ENABLED}",
        flush=True,
    )

    print(
        f"Demo POST Enabled:       "
        f"{DEMO_POST_ENABLED}",
        flush=True,
    )

    print(
        f"Network Writes Enabled:  "
        f"{NETWORK_WRITES_ENABLED}",
        flush=True,
    )

    print(
        f"Synthetic Only:          "
        f"{SYNTHETIC_TRANSPORT_ONLY}",
        flush=True,
    )

    separator()

    print(
        f"{UNIT_NAME}: ALL DIAGNOSTICS PASSED",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: NO REAL ORDER OR ACCOUNT MUTATION WAS SENT",
        flush=True,
    )

    separator()


# ============================================================================
# HEALTH SERVER
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
            body = stable_json(
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
                }
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
        daemon=True,
        name="n31-health-server",
    )

    thread.start()


# ============================================================================
# PERSISTENT RUNTIME
# ============================================================================

def persistent_runtime() -> None:
    heartbeat = 0

    while True:
        heartbeat += 1

        print(
            f"{UNIT_NAME}: HEARTBEAT {heartbeat}",
            flush=True,
        )

        time.sleep(
            30
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    # Start the health endpoint first so Render can observe a live port
    # while the local diagnostic sequence executes.
    start_health_server()

    run_diagnostics()

    print(
        f"{UNIT_NAME}: ENTERING PERSISTENT SAFE RUNTIME",
        flush=True,
    )

    persistent_runtime()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
