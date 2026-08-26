# ============================================================================
# R28 UNIT N.31
# TRANSACTIONAL CHECKPOINT PROMOTION + COMMITTED-MANIFEST ANCHORING
#
# CORRECTED COPY/PASTE VERSION
# SINGLE MAIN.PY
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.31 INCREMENT OVER N.30:
#   - TRANSACTIONAL CHECKPOINT PROMOTION INTENT
#   - DUAL CHECKPOINT SLOT MODEL
#   - COMMITTED MANIFEST ANCHOR
#   - PROMOTION INTENT INTEGRITY SEAL
#   - MANIFEST INTEGRITY SEAL
#   - CHECKPOINT-BOUND WAL PREFIX VALIDATION
#   - PROMOTION CRASH-WINDOW RECOVERY
#   - STALE / TAMPERED PROMOTION REJECTION
#   - COMMITTED AUTHORITY RESTART RECOVERY
# ============================================================================

print("R28 UNIT N.31: MAIN.PY ENTERED", flush=True)

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

print("R28 UNIT N.31: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.31"
UNIT_VERSION = "N.31"
UNIT_DESCRIPTION = "TRANSACTIONAL CHECKPOINT PROMOTION + COMMITTED-MANIFEST ANCHORING"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"
MARGIN_MODE = "ISOLATED"
TARGET_LEVERAGE = "100"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

INTEGRITY_KEY = b"R28-N31-LOCAL-INTEGRITY-KEY"
CHECKPOINT_KEY = b"R28-N31-CHECKPOINT-KEY"
PROMOTION_KEY = b"R28-N31-PROMOTION-KEY"
MANIFEST_KEY = b"R28-N31-MANIFEST-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

PROMOTION_PENDING = "PENDING"
PROMOTION_COMMITTED = "COMMITTED"

CHECKPOINT_SLOT_A = "A"
CHECKPOINT_SLOT_B = "B"
VALID_CHECKPOINT_SLOTS = {CHECKPOINT_SLOT_A, CHECKPOINT_SLOT_B}

SEPARATOR = "-" * 92
HEAVY_SEPARATOR = "=" * 92

print("R28 UNIT N.31: CONSTANTS INITIALIZED", flush=True)


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


def secure_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(
        str(a),
        str(b),
    )


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def deep_clone(value: Any) -> Any:
    return copy.deepcopy(value)


def print_test(number: int, title: str) -> None:
    print(SEPARATOR, flush=True)
    print(
        f"{UNIT_NAME} TEST {number}: {title}",
        flush=True,
    )
    print(SEPARATOR, flush=True)


def pass_line(label: str) -> None:
    print(
        f"{label:<76} ✅ PASS",
        flush=True,
    )


def fail_line(label: str) -> None:
    print(
        f"{label:<76} ❌ FAIL",
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


def assert_pass(
    condition: bool,
    label: str,
) -> None:
    if not condition:
        fail_line(label)
        raise AssertionError(label)

    pass_line(label)


def expect_rejection(
    fn,
    expected_fragment: str,
    label: str,
) -> None:
    try:
        fn()

    except Exception as exc:
        local_block(str(exc))

        if expected_fragment not in str(exc):
            fail_line(label)

            raise AssertionError(
                f"expected rejection containing "
                f"{expected_fragment!r}, "
                f"got {str(exc)!r}"
            ) from exc

        pass_line(label)
        return

    fail_line(label)

    raise AssertionError(
        f"expected rejection: {label}"
    )


# ============================================================================
# DOMAIN RECORDS
# ============================================================================


@dataclass
class WALRecord:
    sequence: int
    event_type: str
    payload: Dict[str, Any]
    previous_hash: str
    record_hash: str = ""
    integrity_seal: str = ""

    def signing_body(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
        }


@dataclass
class RecoveryLease:
    lease_id: str
    owner_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    nonce: int
    issued_at_ns: int
    integrity_seal: str = ""

    def signing_body(self) -> Dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "owner_id": self.owner_id,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "nonce": self.nonce,
            "issued_at_ns": self.issued_at_ns,
        }


@dataclass
class Authorization:
    authorization_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    lease_id: str
    payload_hash: str
    consumed: bool = False
    integrity_seal: str = ""

    def signing_body(self) -> Dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "lease_id": self.lease_id,
            "payload_hash": self.payload_hash,
            "consumed": self.consumed,
        }


@dataclass
class SyntheticDispatchReceipt:
    dispatch_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    method: str
    path: str
    payload_hash: str
    synthetic: bool
    transmitted: bool
    sequence: int
    integrity_seal: str = ""

    def signing_body(self) -> Dict[str, Any]:
        return {
            "dispatch_id": self.dispatch_id,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "method": self.method,
            "path": self.path,
            "payload_hash": self.payload_hash,
            "synthetic": self.synthetic,
            "transmitted": self.transmitted,
            "sequence": self.sequence,
        }


@dataclass
class Checkpoint:
    checkpoint_id: str
    sequence: int
    slot: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    phase: str
    payload_hash: str
    dispatch_count: int
    wal_length: int
    wal_final_hash: str
    state_digest: str
    created_at_ns: int
    integrity_seal: str = ""

    def signing_body(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "sequence": self.sequence,
            "slot": self.slot,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "phase": self.phase,
            "payload_hash": self.payload_hash,
            "dispatch_count": self.dispatch_count,
            "wal_length": self.wal_length,
            "wal_final_hash": self.wal_final_hash,
            "state_digest": self.state_digest,
            "created_at_ns": self.created_at_ns,
        }


@dataclass
class PromotionIntent:
    intent_id: str
    status: str
    target_slot: str
    target_checkpoint_sequence: int
    target_checkpoint_id: str
    target_checkpoint_seal: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    checkpoint_wal_length: int
    checkpoint_wal_final_hash: str
    created_at_ns: int
    integrity_seal: str = ""

    def signing_body(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "status": self.status,
            "target_slot": self.target_slot,
            "target_checkpoint_sequence": (
                self.target_checkpoint_sequence
            ),
            "target_checkpoint_id": (
                self.target_checkpoint_id
            ),
            "target_checkpoint_seal": (
                self.target_checkpoint_seal
            ),
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "checkpoint_wal_length": (
                self.checkpoint_wal_length
            ),
            "checkpoint_wal_final_hash": (
                self.checkpoint_wal_final_hash
            ),
            "created_at_ns": self.created_at_ns,
        }


@dataclass
class CommittedManifest:
    manifest_id: str
    manifest_sequence: int
    committed_slot: str
    checkpoint_sequence: int
    checkpoint_id: str
    checkpoint_seal: str
    checkpoint_wal_length: int
    checkpoint_wal_final_hash: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    promotion_intent_id: str
    committed_at_ns: int
    integrity_seal: str = ""

    def signing_body(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "manifest_sequence": (
                self.manifest_sequence
            ),
            "committed_slot": self.committed_slot,
            "checkpoint_sequence": (
                self.checkpoint_sequence
            ),
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_seal": self.checkpoint_seal,
            "checkpoint_wal_length": (
                self.checkpoint_wal_length
            ),
            "checkpoint_wal_final_hash": (
                self.checkpoint_wal_final_hash
            ),
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "promotion_intent_id": (
                self.promotion_intent_id
            ),
            "committed_at_ns": self.committed_at_ns,
        }


@dataclass
class DurableState:
    generation: int
    lineage_id: str
    recovery_epoch: int
    phase: str
    payload: Dict[str, Any]
    payload_hash: str

    lease_nonce: int = 0
    checkpoint_sequence: int = 0
    manifest_sequence: int = 0

    wal: List[WALRecord] = field(
        default_factory=list
    )

    lease: Optional[RecoveryLease] = None

    authorization: Optional[
        Authorization
    ] = None

    dispatches: List[
        SyntheticDispatchReceipt
    ] = field(
        default_factory=list
    )

    checkpoint_slots: Dict[
        str,
        Checkpoint,
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


# ============================================================================
# RECORD SEAL / VALIDATION FUNCTIONS
# ============================================================================


def seal_wal_record(
    record: WALRecord,
) -> WALRecord:

    record.record_hash = sha256_hex(
        record.signing_body()
    )

    record.integrity_seal = hmac_hex(
        INTEGRITY_KEY,
        {
            "record_hash": record.record_hash,
            **record.signing_body(),
        },
    )

    return record


def validate_wal(
    wal: List[WALRecord],
) -> None:

    previous_hash = "GENESIS"
    expected_sequence = 1

    for record in wal:

        if record.sequence != expected_sequence:
            raise ValueError(
                "WAL sequence mismatch"
            )

        if record.previous_hash != previous_hash:
            raise ValueError(
                "WAL chain previous hash mismatch"
            )

        expected_hash = sha256_hex(
            record.signing_body()
        )

        if not secure_equal(
            record.record_hash,
            expected_hash,
        ):
            raise ValueError(
                "WAL record hash mismatch"
            )

        expected_seal = hmac_hex(
            INTEGRITY_KEY,
            {
                "record_hash": record.record_hash,
                **record.signing_body(),
            },
        )

        if not secure_equal(
            record.integrity_seal,
            expected_seal,
        ):
            raise ValueError(
                "WAL record integrity seal mismatch"
            )

        previous_hash = record.record_hash
        expected_sequence += 1


def wal_final_hash(
    wal: List[WALRecord],
) -> str:

    if not wal:
        return "GENESIS"

    return wal[-1].record_hash


def seal_lease(
    lease: RecoveryLease,
) -> RecoveryLease:

    lease.integrity_seal = hmac_hex(
        INTEGRITY_KEY,
        lease.signing_body(),
    )

    return lease


def validate_lease(
    lease: RecoveryLease,
) -> None:

    expected = hmac_hex(
        INTEGRITY_KEY,
        lease.signing_body(),
    )

    if not secure_equal(
        lease.integrity_seal,
        expected,
    ):
        raise ValueError(
            "recovery lease integrity seal mismatch"
        )


def seal_authorization(
    auth: Authorization,
) -> Authorization:

    auth.integrity_seal = hmac_hex(
        INTEGRITY_KEY,
        auth.signing_body(),
    )

    return auth


def validate_authorization(
    auth: Authorization,
) -> None:

    expected = hmac_hex(
        INTEGRITY_KEY,
        auth.signing_body(),
    )

    if not secure_equal(
        auth.integrity_seal,
        expected,
    ):
        raise ValueError(
            "authorization integrity seal mismatch"
        )


def seal_dispatch(
    receipt: SyntheticDispatchReceipt,
) -> SyntheticDispatchReceipt:

    receipt.integrity_seal = hmac_hex(
        INTEGRITY_KEY,
        receipt.signing_body(),
    )

    return receipt


def validate_dispatch(
    receipt: SyntheticDispatchReceipt,
) -> None:

    expected = hmac_hex(
        INTEGRITY_KEY,
        receipt.signing_body(),
    )

    if not secure_equal(
        receipt.integrity_seal,
        expected,
    ):
        raise ValueError(
            "dispatch integrity seal mismatch"
        )

    if (
        not receipt.synthetic
        or receipt.transmitted
    ):
        raise ValueError(
            "dispatch violates synthetic-only "
            "transport policy"
        )

    if (
        receipt.method != HTTP_METHOD
        or receipt.path != LEVERAGE_ENDPOINT
    ):
        raise ValueError(
            "dispatch transport binding mismatch"
        )


def seal_checkpoint(
    checkpoint: Checkpoint,
) -> Checkpoint:

    checkpoint.integrity_seal = hmac_hex(
        CHECKPOINT_KEY,
        checkpoint.signing_body(),
    )

    return checkpoint


def validate_checkpoint(
    checkpoint: Checkpoint,
    wal: List[WALRecord],
) -> None:

    if (
        checkpoint.slot
        not in VALID_CHECKPOINT_SLOTS
    ):
        raise ValueError(
            "checkpoint slot invalid"
        )

    expected_seal = hmac_hex(
        CHECKPOINT_KEY,
        checkpoint.signing_body(),
    )

    if not secure_equal(
        checkpoint.integrity_seal,
        expected_seal,
    ):
        raise ValueError(
            "checkpoint integrity seal mismatch"
        )

    # ------------------------------------------------------------------------
    # IMPORTANT N.31 RULE
    #
    # This validator remains STRICT.
    #
    # The WAL passed here must be exactly the WAL prefix captured when the
    # checkpoint was created.
    #
    # We deliberately do NOT weaken this function to accept any later WAL.
    # ------------------------------------------------------------------------

    if checkpoint.wal_length != len(wal):
        raise ValueError(
            "checkpoint WAL length mismatch"
        )

    validate_wal(wal)

    if (
        checkpoint.wal_final_hash
        != wal_final_hash(wal)
    ):
        raise ValueError(
            "checkpoint WAL final hash mismatch"
        )


def checkpoint_wal_prefix(
    checkpoint: Checkpoint,
    wal: List[WALRecord],
) -> List[WALRecord]:

    if checkpoint.wal_length < 0:
        raise ValueError(
            "checkpoint WAL length invalid"
        )

    if checkpoint.wal_length > len(wal):
        raise ValueError(
            "checkpoint WAL length exceeds current WAL"
        )

    prefix = wal[
        : checkpoint.wal_length
    ]

    validate_checkpoint(
        checkpoint,
        prefix,
    )

    return prefix


def seal_promotion_intent(
    intent: PromotionIntent,
) -> PromotionIntent:

    intent.integrity_seal = hmac_hex(
        PROMOTION_KEY,
        intent.signing_body(),
    )

    return intent


def validate_promotion_intent(
    intent: PromotionIntent,
) -> None:

    expected = hmac_hex(
        PROMOTION_KEY,
        intent.signing_body(),
    )

    if not secure_equal(
        intent.integrity_seal,
        expected,
    ):
        raise ValueError(
            "promotion intent integrity seal mismatch"
        )

    if intent.status not in (
        PROMOTION_PENDING,
        PROMOTION_COMMITTED,
    ):
        raise ValueError(
            "promotion intent status invalid"
        )

    if (
        intent.target_slot
        not in VALID_CHECKPOINT_SLOTS
    ):
        raise ValueError(
            "promotion target slot invalid"
        )


def seal_manifest(
    manifest: CommittedManifest,
) -> CommittedManifest:

    manifest.integrity_seal = hmac_hex(
        MANIFEST_KEY,
        manifest.signing_body(),
    )

    return manifest


def validate_manifest(
    manifest: CommittedManifest,
) -> None:

    expected = hmac_hex(
        MANIFEST_KEY,
        manifest.signing_body(),
    )

    if not secure_equal(
        manifest.integrity_seal,
        expected,
    ):
        raise ValueError(
            "committed manifest integrity seal mismatch"
        )

    if (
        manifest.committed_slot
        not in VALID_CHECKPOINT_SLOTS
    ):
        raise ValueError(
            "committed manifest slot invalid"
        )


# ============================================================================
# ENGINE
# ============================================================================


class N31Engine:

    def __init__(
        self,
        state: Optional[DurableState] = None,
    ) -> None:

        if state is None:

            payload = {
                "symbol": SYMBOL,
                "marginMode": MARGIN_MODE,
                "leverage": TARGET_LEVERAGE,
            }

            state = DurableState(
                generation=1,
                lineage_id=new_id(
                    "lineage"
                ),
                recovery_epoch=1,
                phase=PHASE_PREPARED,
                payload=payload,
                payload_hash=sha256_hex(
                    payload
                ),
            )

        self.state = state

        self._lock = threading.RLock()


    # ========================================================================
    # DURABLE WAL
    # ========================================================================

    def append_wal(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> WALRecord:

        with self._lock:

            previous_hash = wal_final_hash(
                self.state.wal
            )

            record = WALRecord(
                sequence=(
                    len(self.state.wal) + 1
                ),
                event_type=event_type,
                payload=deep_clone(
                    payload
                ),
                previous_hash=previous_hash,
            )

            seal_wal_record(
                record
            )

            self.state.wal.append(
                record
            )

            return record


    # ========================================================================
    # RECOVERY LEASE
    # ========================================================================

    def acquire_recovery_lease(
        self,
        owner_id: str,
    ) -> RecoveryLease:

        with self._lock:

            if (
                self.state.phase
                == PHASE_COMPLETED
            ):
                raise ValueError(
                    "terminal generation cannot "
                    "acquire recovery lease"
                )

            self.state.lease_nonce += 1

            lease = RecoveryLease(
                lease_id=new_id(
                    "lease"
                ),
                owner_id=owner_id,
                generation=(
                    self.state.generation
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                nonce=(
                    self.state.lease_nonce
                ),
                issued_at_ns=time.time_ns(),
            )

            seal_lease(
                lease
            )

            self.state.lease = lease

            self.append_wal(
                "RECOVERY_LEASE_ACQUIRED",
                {
                    "lease_id": (
                        lease.lease_id
                    ),
                    "owner_id": (
                        lease.owner_id
                    ),
                    "generation": (
                        lease.generation
                    ),
                    "lineage_id": (
                        lease.lineage_id
                    ),
                    "recovery_epoch": (
                        lease.recovery_epoch
                    ),
                    "nonce": (
                        lease.nonce
                    ),
                },
            )

            return deep_clone(
                lease
            )


    def _validate_current_lease(
        self,
        lease: RecoveryLease,
    ) -> None:

        validate_lease(
            lease
        )

        current = self.state.lease

        if current is None:
            raise ValueError(
                "no active recovery lease"
            )

        validate_lease(
            current
        )

        if (
            lease.lease_id
            != current.lease_id
        ):
            raise ValueError(
                "recovery lease fence mismatch"
            )

        if (
            lease.generation
            != self.state.generation
        ):
            raise ValueError(
                "recovery lease generation mismatch"
            )

        if (
            lease.lineage_id
            != self.state.lineage_id
        ):
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

        if (
            lease.nonce
            != current.nonce
        ):
            raise ValueError(
                "recovery lease nonce mismatch"
            )


    # ========================================================================
    # AUTHORIZATION
    # ========================================================================

    def authorize(
        self,
        lease: RecoveryLease,
    ) -> Authorization:

        with self._lock:

            self._validate_current_lease(
                lease
            )

            if (
                self.state.authorization
                is not None
                and not
                self.state.authorization.consumed
            ):
                raise ValueError(
                    "generation already authorized"
                )

            auth = Authorization(
                authorization_id=new_id(
                    "auth"
                ),
                generation=(
                    self.state.generation
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                lease_id=(
                    lease.lease_id
                ),
                payload_hash=(
                    self.state.payload_hash
                ),
                consumed=False,
            )

            seal_authorization(
                auth
            )

            self.state.authorization = auth
            self.state.phase = PHASE_AUTHORIZED

            self.append_wal(
                "AUTHORIZED",
                {
                    "authorization_id": (
                        auth.authorization_id
                    ),
                    "generation": (
                        auth.generation
                    ),
                    "lineage_id": (
                        auth.lineage_id
                    ),
                    "recovery_epoch": (
                        auth.recovery_epoch
                    ),
                    "lease_id": (
                        auth.lease_id
                    ),
                    "payload_hash": (
                        auth.payload_hash
                    ),
                },
            )

            return deep_clone(
                auth
            )


    def _validate_current_authorization(
        self,
        auth: Authorization,
    ) -> None:

        validate_authorization(
            auth
        )

        current = self.state.authorization

        if current is None:
            raise ValueError(
                "generation is not authorized"
            )

        validate_authorization(
            current
        )

        if (
            auth.authorization_id
            != current.authorization_id
        ):
            raise ValueError(
                "authorization fence mismatch"
            )

        if (
            auth.generation
            != self.state.generation
        ):
            raise ValueError(
                "authorization generation mismatch"
            )

        if (
            auth.lineage_id
            != self.state.lineage_id
        ):
            raise ValueError(
                "authorization lineage mismatch"
            )

        if (
            auth.recovery_epoch
            != self.state.recovery_epoch
        ):
            raise ValueError(
                "authorization epoch mismatch"
            )

        if (
            auth.payload_hash
            != self.state.payload_hash
        ):
            raise ValueError(
                "authorization payload hash mismatch"
            )

        if current.consumed:
            raise ValueError(
                "authorization already consumed"
            )


    # ========================================================================
    # SYNTHETIC DISPATCH ONLY
    # ========================================================================

    def dispatch_synthetic(
        self,
        auth: Authorization,
    ) -> SyntheticDispatchReceipt:

        with self._lock:

            self._validate_current_authorization(
                auth
            )

            if (
                REAL_POST_ENABLED
                or DEMO_POST_ENABLED
                or NETWORK_WRITES_ENABLED
            ):
                raise RuntimeError(
                    "network write firebreak "
                    "configuration violated"
                )

            if not SYNTHETIC_TRANSPORT_ONLY:
                raise RuntimeError(
                    "synthetic-only transport disabled"
                )

            if self.state.dispatches:
                raise ValueError(
                    "dispatch already produced "
                    "for generation"
                )

            receipt = SyntheticDispatchReceipt(
                dispatch_id=new_id(
                    "dispatch"
                ),
                generation=(
                    self.state.generation
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload_hash=(
                    self.state.payload_hash
                ),
                synthetic=True,
                transmitted=False,
                sequence=1,
            )

            seal_dispatch(
                receipt
            )

            self.state.dispatches.append(
                receipt
            )

            # ----------------------------------------------------------------
            # CONSUME AUTHORIZATION DURABLY
            # ----------------------------------------------------------------

            self.state.authorization.consumed = True

            seal_authorization(
                self.state.authorization
            )

            self.state.phase = PHASE_COMPLETED

            self.append_wal(
                "SYNTHETIC_DISPATCH_COMPLETED",
                {
                    "dispatch_id": (
                        receipt.dispatch_id
                    ),
                    "generation": (
                        receipt.generation
                    ),
                    "lineage_id": (
                        receipt.lineage_id
                    ),
                    "recovery_epoch": (
                        receipt.recovery_epoch
                    ),
                    "method": (
                        receipt.method
                    ),
                    "path": (
                        receipt.path
                    ),
                    "payload_hash": (
                        receipt.payload_hash
                    ),
                    "synthetic": (
                        receipt.synthetic
                    ),
                    "transmitted": (
                        receipt.transmitted
                    ),
                },
            )

            self.append_wal(
                "AUTHORIZATION_CONSUMED",
                {
                    "authorization_id": (
                        self.state
                        .authorization
                        .authorization_id
                    ),
                    "generation": (
                        self.state.generation
                    ),
                },
            )

            return deep_clone(
                receipt
            )


    # ========================================================================
    # CHECKPOINT CREATION / VALIDATION
    # ========================================================================

    def _checkpoint_state_digest(
        self,
    ) -> str:

        digest_body = {
            "generation": (
                self.state.generation
            ),
            "lineage_id": (
                self.state.lineage_id
            ),
            "recovery_epoch": (
                self.state.recovery_epoch
            ),
            "phase": (
                self.state.phase
            ),
            "payload_hash": (
                self.state.payload_hash
            ),
            "dispatch_ids": [
                dispatch.dispatch_id
                for dispatch
                in self.state.dispatches
            ],
            "authorization_consumed": (
                self.state.authorization.consumed
                if self.state.authorization
                else None
            ),
        }

        return sha256_hex(
            digest_body
        )


    def create_checkpoint(
        self,
        slot: Optional[str] = None,
    ) -> Checkpoint:

        with self._lock:

            validate_wal(
                self.state.wal
            )

            if slot is None:

                committed_slot = (
                    self.state
                    .committed_manifest
                    .committed_slot
                    if self.state.committed_manifest
                    is not None
                    else None
                )

                if (
                    committed_slot
                    == CHECKPOINT_SLOT_A
                ):
                    slot = CHECKPOINT_SLOT_B
                else:
                    slot = CHECKPOINT_SLOT_A

            if (
                slot
                not in VALID_CHECKPOINT_SLOTS
            ):
                raise ValueError(
                    "checkpoint slot invalid"
                )

            self.state.checkpoint_sequence += 1

            checkpoint = Checkpoint(
                checkpoint_id=new_id(
                    "checkpoint"
                ),
                sequence=(
                    self.state
                    .checkpoint_sequence
                ),
                slot=slot,
                generation=(
                    self.state.generation
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                phase=(
                    self.state.phase
                ),
                payload_hash=(
                    self.state.payload_hash
                ),
                dispatch_count=len(
                    self.state.dispatches
                ),
                wal_length=len(
                    self.state.wal
                ),
                wal_final_hash=wal_final_hash(
                    self.state.wal
                ),
                state_digest=(
                    self._checkpoint_state_digest()
                ),
                created_at_ns=time.time_ns(),
            )

            seal_checkpoint(
                checkpoint
            )

            self.state.checkpoint_slots[
                slot
            ] = checkpoint

            # ----------------------------------------------------------------
            # IMPORTANT:
            #
            # Do not append a checkpoint-created WAL record after sealing this
            # checkpoint. The checkpoint's WAL boundary is intentionally the
            # exact historical prefix at creation time.
            # ----------------------------------------------------------------

            return deep_clone(
                checkpoint
            )


    # ========================================================================
    # TRANSACTIONAL PROMOTION
    # ========================================================================

    def create_promotion_intent(
        self,
        checkpoint: Checkpoint,
    ) -> PromotionIntent:

        with self._lock:

            slot_checkpoint = (
                self.state.checkpoint_slots.get(
                    checkpoint.slot
                )
            )

            if slot_checkpoint is None:
                raise ValueError(
                    "promotion target checkpoint missing"
                )

            if (
                slot_checkpoint.checkpoint_id
                != checkpoint.checkpoint_id
            ):
                raise ValueError(
                    "promotion target checkpoint "
                    "identity mismatch"
                )

            # ----------------------------------------------------------------
            # Validate checkpoint against its original historical WAL prefix.
            # ----------------------------------------------------------------

            checkpoint_wal_prefix(
                slot_checkpoint,
                self.state.wal,
            )

            if (
                checkpoint.generation
                != self.state.generation
            ):
                raise ValueError(
                    "promotion checkpoint "
                    "generation mismatch"
                )

            if (
                checkpoint.lineage_id
                != self.state.lineage_id
            ):
                raise ValueError(
                    "promotion checkpoint "
                    "lineage mismatch"
                )

            if (
                checkpoint.recovery_epoch
                != self.state.recovery_epoch
            ):
                raise ValueError(
                    "promotion checkpoint "
                    "epoch mismatch"
                )

            intent = PromotionIntent(
                intent_id=new_id(
                    "promotion"
                ),
                status=PROMOTION_PENDING,
                target_slot=(
                    checkpoint.slot
                ),
                target_checkpoint_sequence=(
                    checkpoint.sequence
                ),
                target_checkpoint_id=(
                    checkpoint.checkpoint_id
                ),
                target_checkpoint_seal=(
                    checkpoint.integrity_seal
                ),
                generation=(
                    checkpoint.generation
                ),
                lineage_id=(
                    checkpoint.lineage_id
                ),
                recovery_epoch=(
                    checkpoint.recovery_epoch
                ),
                checkpoint_wal_length=(
                    checkpoint.wal_length
                ),
                checkpoint_wal_final_hash=(
                    checkpoint.wal_final_hash
                ),
                created_at_ns=time.time_ns(),
            )

            seal_promotion_intent(
                intent
            )

            self.state.promotion_intents[
                intent.intent_id
            ] = intent

            # ----------------------------------------------------------------
            # This WAL record legitimately occurs AFTER the checkpoint WAL
            # boundary.
            #
            # This is why commit_checkpoint_promotion() must validate the
            # checkpoint against its captured WAL prefix, not self.state.wal.
            # ----------------------------------------------------------------

            self.append_wal(
                "CHECKPOINT_PROMOTION_INTENT",
                {
                    "intent_id": (
                        intent.intent_id
                    ),
                    "target_slot": (
                        intent.target_slot
                    ),
                    "target_checkpoint_sequence": (
                        intent
                        .target_checkpoint_sequence
                    ),
                    "target_checkpoint_id": (
                        intent
                        .target_checkpoint_id
                    ),
                    "checkpoint_wal_length": (
                        intent
                        .checkpoint_wal_length
                    ),
                    "generation": (
                        intent.generation
                    ),
                    "lineage_id": (
                        intent.lineage_id
                    ),
                    "recovery_epoch": (
                        intent.recovery_epoch
                    ),
                },
            )

            return deep_clone(
                intent
            )


    def _validate_intent_checkpoint_binding(
        self,
        intent: PromotionIntent,
        checkpoint: Checkpoint,
    ) -> None:

        validate_promotion_intent(
            intent
        )

        if intent.status != PROMOTION_PENDING:
            raise ValueError(
                "promotion intent is not pending"
            )

        if (
            intent.target_slot
            != checkpoint.slot
        ):
            raise ValueError(
                "promotion target slot mismatch"
            )

        if (
            intent.target_checkpoint_sequence
            != checkpoint.sequence
        ):
            raise ValueError(
                "promotion checkpoint "
                "sequence mismatch"
            )

        if (
            intent.target_checkpoint_id
            != checkpoint.checkpoint_id
        ):
            raise ValueError(
                "promotion checkpoint "
                "identity mismatch"
            )

        if not secure_equal(
            intent.target_checkpoint_seal,
            checkpoint.integrity_seal,
        ):
            raise ValueError(
                "promotion checkpoint seal mismatch"
            )

        if (
            intent.generation
            != checkpoint.generation
        ):
            raise ValueError(
                "promotion checkpoint "
                "generation mismatch"
            )

        if (
            intent.lineage_id
            != checkpoint.lineage_id
        ):
            raise ValueError(
                "promotion checkpoint "
                "lineage mismatch"
            )

        if (
            intent.recovery_epoch
            != checkpoint.recovery_epoch
        ):
            raise ValueError(
                "promotion checkpoint epoch mismatch"
            )

        if (
            intent.checkpoint_wal_length
            != checkpoint.wal_length
        ):
            raise ValueError(
                "promotion checkpoint "
                "WAL length mismatch"
            )

        if (
            intent.checkpoint_wal_final_hash
            != checkpoint.wal_final_hash
        ):
            raise ValueError(
                "promotion checkpoint "
                "WAL final hash mismatch"
            )


    def commit_checkpoint_promotion(
        self,
        intent: PromotionIntent,
    ) -> CommittedManifest:

        with self._lock:

            stored_intent = (
                self.state.promotion_intents.get(
                    intent.intent_id
                )
            )

            if stored_intent is None:
                raise ValueError(
                    "promotion intent missing"
                )

            validate_promotion_intent(
                stored_intent
            )

            validate_promotion_intent(
                intent
            )

            # ----------------------------------------------------------------
            # IDEMPOTENT COMMIT RESOLUTION
            #
            # After a successful commit, the durable stored intent changes from
            # PENDING to COMMITTED and receives a new integrity seal.
            #
            # A caller may still legitimately hold the original sealed PENDING
            # intent. Therefore resolve an already-committed manifest BEFORE
            # requiring the stored-intent seal to equal the caller's old seal.
            # ----------------------------------------------------------------

            existing = (
                self.state.committed_manifest
            )

            if existing is not None:

                validate_manifest(
                    existing
                )

                if (
                    existing.promotion_intent_id
                    == intent.intent_id
                ):

                    if (
                        intent.target_slot
                        != existing.committed_slot
                    ):
                        raise ValueError(
                            "promotion replay "
                            "slot mismatch"
                        )

                    if (
                        intent
                        .target_checkpoint_sequence
                        != existing
                        .checkpoint_sequence
                    ):
                        raise ValueError(
                            "promotion replay "
                            "checkpoint sequence mismatch"
                        )

                    if (
                        intent
                        .target_checkpoint_id
                        != existing
                        .checkpoint_id
                    ):
                        raise ValueError(
                            "promotion replay "
                            "checkpoint identity mismatch"
                        )

                    if not secure_equal(
                        intent
                        .target_checkpoint_seal,
                        existing
                        .checkpoint_seal,
                    ):
                        raise ValueError(
                            "promotion replay "
                            "checkpoint seal mismatch"
                        )

                    return deep_clone(
                        existing
                    )

            if not secure_equal(
                stored_intent.integrity_seal,
                intent.integrity_seal,
            ):
                raise ValueError(
                    "promotion intent does not "
                    "match durable intent"
                )

            checkpoint = (
                self.state.checkpoint_slots.get(
                    intent.target_slot
                )
            )

            if checkpoint is None:
                raise ValueError(
                    "promotion target checkpoint missing"
                )

            self._validate_intent_checkpoint_binding(
                intent,
                checkpoint,
            )

            # =================================================================
            # N.31 CRITICAL CORRECTION
            #
            # OLD BROKEN LOGIC:
            #
            #     validate_checkpoint(
            #         checkpoint,
            #         self.state.wal,
            #     )
            #
            # That fails after CHECKPOINT_PROMOTION_INTENT is appended because
            # the current WAL is now longer than the WAL captured by the
            # checkpoint.
            #
            # CORRECT LOGIC:
            #
            # Validate the checkpoint against exactly its historical WAL prefix.
            # =================================================================

            prefix = checkpoint_wal_prefix(
                checkpoint,
                self.state.wal,
            )

            if (
                len(prefix)
                != intent.checkpoint_wal_length
            ):
                raise ValueError(
                    "promotion checkpoint "
                    "prefix length mismatch"
                )

            if (
                wal_final_hash(prefix)
                != intent
                .checkpoint_wal_final_hash
            ):
                raise ValueError(
                    "promotion checkpoint "
                    "prefix hash mismatch"
                )

            # ----------------------------------------------------------------
            # CURRENT AUTHORITY FENCING
            # ----------------------------------------------------------------

            if (
                checkpoint.generation
                != self.state.generation
            ):
                raise ValueError(
                    "stale checkpoint generation"
                )

            if (
                checkpoint.lineage_id
                != self.state.lineage_id
            ):
                raise ValueError(
                    "stale checkpoint lineage"
                )

            if (
                checkpoint.recovery_epoch
                != self.state.recovery_epoch
            ):
                raise ValueError(
                    "stale checkpoint recovery epoch"
                )

            self.state.manifest_sequence += 1

            manifest = CommittedManifest(
                manifest_id=new_id(
                    "manifest"
                ),
                manifest_sequence=(
                    self.state
                    .manifest_sequence
                ),
                committed_slot=(
                    checkpoint.slot
                ),
                checkpoint_sequence=(
                    checkpoint.sequence
                ),
                checkpoint_id=(
                    checkpoint.checkpoint_id
                ),
                checkpoint_seal=(
                    checkpoint.integrity_seal
                ),
                checkpoint_wal_length=(
                    checkpoint.wal_length
                ),
                checkpoint_wal_final_hash=(
                    checkpoint.wal_final_hash
                ),
                generation=(
                    checkpoint.generation
                ),
                lineage_id=(
                    checkpoint.lineage_id
                ),
                recovery_epoch=(
                    checkpoint.recovery_epoch
                ),
                promotion_intent_id=(
                    intent.intent_id
                ),
                committed_at_ns=time.time_ns(),
            )

            seal_manifest(
                manifest
            )

            # ----------------------------------------------------------------
            # Publish committed authority.
            # ----------------------------------------------------------------

            self.state.committed_manifest = (
                manifest
            )

            # ----------------------------------------------------------------
            # Mark durable intent committed and reseal it.
            # ----------------------------------------------------------------

            stored_intent.status = (
                PROMOTION_COMMITTED
            )

            seal_promotion_intent(
                stored_intent
            )

            self.state.promotion_intents[
                intent.intent_id
            ] = stored_intent

            # ----------------------------------------------------------------
            # This WAL entry also occurs after the checkpoint boundary.
            # ----------------------------------------------------------------

            self.append_wal(
                "CHECKPOINT_PROMOTION_COMMITTED",
                {
                    "manifest_id": (
                        manifest.manifest_id
                    ),
                    "manifest_sequence": (
                        manifest
                        .manifest_sequence
                    ),
                    "committed_slot": (
                        manifest.committed_slot
                    ),
                    "checkpoint_sequence": (
                        manifest
                        .checkpoint_sequence
                    ),
                    "checkpoint_id": (
                        manifest.checkpoint_id
                    ),
                    "promotion_intent_id": (
                        manifest
                        .promotion_intent_id
                    ),
                    "generation": (
                        manifest.generation
                    ),
                    "lineage_id": (
                        manifest.lineage_id
                    ),
                    "recovery_epoch": (
                        manifest.recovery_epoch
                    ),
                },
            )

            return deep_clone(
                manifest
            )


    # ========================================================================
    # COMMITTED AUTHORITY RECOVERY
    # ========================================================================

    def recover_authoritative_checkpoint(
        self,
    ) -> Checkpoint:

        with self._lock:

            manifest = (
                self.state.committed_manifest
            )

            if manifest is None:
                raise ValueError(
                    "no committed manifest"
                )

            validate_manifest(
                manifest
            )

            checkpoint = (
                self.state.checkpoint_slots.get(
                    manifest.committed_slot
                )
            )

            if checkpoint is None:
                raise ValueError(
                    "committed checkpoint missing"
                )

            checkpoint_wal_prefix(
                checkpoint,
                self.state.wal,
            )

            if (
                checkpoint.sequence
                != manifest.checkpoint_sequence
            ):
                raise ValueError(
                    "manifest checkpoint "
                    "sequence mismatch"
                )

            if (
                checkpoint.checkpoint_id
                != manifest.checkpoint_id
            ):
                raise ValueError(
                    "manifest checkpoint "
                    "identity mismatch"
                )

            if not secure_equal(
                checkpoint.integrity_seal,
                manifest.checkpoint_seal,
            ):
                raise ValueError(
                    "manifest checkpoint "
                    "seal mismatch"
                )

            if (
                checkpoint.wal_length
                != manifest
                .checkpoint_wal_length
            ):
                raise ValueError(
                    "manifest checkpoint "
                    "WAL length mismatch"
                )

            if (
                checkpoint.wal_final_hash
                != manifest
                .checkpoint_wal_final_hash
            ):
                raise ValueError(
                    "manifest checkpoint "
                    "WAL hash mismatch"
                )

            if (
                checkpoint.generation
                != manifest.generation
            ):
                raise ValueError(
                    "manifest generation mismatch"
                )

            if (
                checkpoint.lineage_id
                != manifest.lineage_id
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

            return deep_clone(
                checkpoint
            )


    def recover_pending_promotion(
        self,
    ) -> Optional[CommittedManifest]:

        with self._lock:

            pending: List[
                PromotionIntent
            ] = []

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
                        intent
                    )

            if not pending:
                return None

            if len(pending) > 1:
                raise ValueError(
                    "multiple pending "
                    "promotion intents"
                )

            return (
                self
                .commit_checkpoint_promotion(
                    deep_clone(
                        pending[0]
                    )
                )
            )


    # ========================================================================
    # SNAPSHOT / RESTART
    # ========================================================================

    def export_state(
        self,
    ) -> DurableState:

        with self._lock:
            return deep_clone(
                self.state
            )


    @classmethod
    def restore_state(
        cls,
        state: DurableState,
    ) -> "N31Engine":

        restored = cls(
            deep_clone(
                state
            )
        )

        validate_wal(
            restored.state.wal
        )

        if (
            restored.state.lease
            is not None
        ):
            validate_lease(
                restored.state.lease
            )

        if (
            restored.state.authorization
            is not None
        ):
            validate_authorization(
                restored
                .state
                .authorization
            )

        for receipt in (
            restored.state.dispatches
        ):
            validate_dispatch(
                receipt
            )

        for checkpoint in (
            restored
            .state
            .checkpoint_slots
            .values()
        ):
            checkpoint_wal_prefix(
                checkpoint,
                restored.state.wal,
            )

        for intent in (
            restored
            .state
            .promotion_intents
            .values()
        ):
            validate_promotion_intent(
                intent
            )

        if (
            restored
            .state
            .committed_manifest
            is not None
        ):

            validate_manifest(
                restored
                .state
                .committed_manifest
            )

            restored.recover_authoritative_checkpoint()

        return restored


    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(
        self,
    ) -> None:

        with self._lock:

            if (
                self.state.phase
                != PHASE_COMPLETED
            ):
                raise ValueError(
                    "generation must be "
                    "terminal before advance"
                )

            self.state.generation += 1
            self.state.recovery_epoch += 1

            self.state.lineage_id = new_id(
                "lineage"
            )

            self.state.phase = (
                PHASE_PREPARED
            )

            self.state.lease = None
            self.state.authorization = None
            self.state.dispatches = []

            self.append_wal(
                "GENERATION_ADVANCED",
                {
                    "generation": (
                        self.state.generation
                    ),
                    "lineage_id": (
                        self.state.lineage_id
                    ),
                    "recovery_epoch": (
                        self.state
                        .recovery_epoch
                    ),
                },
            )


print(
    "R28 UNIT N.31: ENGINE DEFINITIONS LOADED",
    flush=True,
)


# ============================================================================
# DIAGNOSTIC HELPERS
# ============================================================================


def build_completed_engine() -> Tuple[
    N31Engine,
    RecoveryLease,
    Authorization,
    SyntheticDispatchReceipt,
]:

    engine = N31Engine()

    lease = engine.acquire_recovery_lease(
        "worker-n31"
    )

    auth = engine.authorize(
        lease
    )

    receipt = engine.dispatch_synthetic(
        auth
    )

    return (
        engine,
        lease,
        auth,
        receipt,
    )


# ============================================================================
# DIAGNOSTICS
# ============================================================================


def run_diagnostics() -> None:

    print(
        HEAVY_SEPARATOR,
        flush=True,
    )

    print(
        f"{UNIT_NAME} — "
        f"{UNIT_DESCRIPTION}",
        flush=True,
    )

    print(
        HEAVY_SEPARATOR,
        flush=True,
    )


    # ========================================================================
    # TEST 1
    # ========================================================================

    print_test(
        1,
        "ENGINE INITIALIZATION",
    )

    engine = N31Engine()

    assert_pass(
        engine.state.phase
        == PHASE_PREPARED,
        "Engine Starts PREPARED",
    )

    assert_pass(
        engine.state.generation == 1,
        "Initial Generation Is One",
    )

    assert_pass(
        engine.state.recovery_epoch == 1,
        "Initial Recovery Epoch Is One",
    )

    assert_pass(
        len(
            engine.state.payload_hash
        ) == 64,
        "Payload Hash Established",
    )


    # ========================================================================
    # TEST 2
    # ========================================================================

    print_test(
        2,
        "RECOVERY LEASE BINDING",
    )

    lease = engine.acquire_recovery_lease(
        "worker-n31"
    )

    assert_pass(
        lease.generation
        == engine.state.generation,
        "Lease Bound To Current Generation",
    )

    assert_pass(
        lease.lineage_id
        == engine.state.lineage_id,
        "Lease Bound To Current Lineage",
    )

    assert_pass(
        lease.recovery_epoch
        == engine.state.recovery_epoch,
        "Lease Bound To Current Recovery Epoch",
    )


    # ========================================================================
    # TEST 3
    # ========================================================================

    print_test(
        3,
        "AUTHORIZATION BINDING",
    )

    auth = engine.authorize(
        lease
    )

    assert_pass(
        auth.generation
        == engine.state.generation,
        "Authorization Bound To Generation",
    )

    assert_pass(
        auth.lineage_id
        == engine.state.lineage_id,
        "Authorization Bound To Lineage",
    )

    assert_pass(
        auth.payload_hash
        == engine.state.payload_hash,
        "Authorization Payload Hash Preserved",
    )


    # ========================================================================
    # TEST 4
    # ========================================================================

    print_test(
        4,
        "SYNTHETIC DISPATCH",
    )

    receipt = engine.dispatch_synthetic(
        auth
    )

    assert_pass(
        engine.state.phase
        == PHASE_COMPLETED,
        "Synthetic Dispatch Completed",
    )

    assert_pass(
        len(
            engine.state.dispatches
        ) == 1,
        "Exactly One Dispatch Produced",
    )

    assert_pass(
        receipt.synthetic
        and not receipt.transmitted,
        "Dispatch Is Synthetic",
    )


    # ========================================================================
    # TEST 5
    # ========================================================================

    print_test(
        5,
        "CHECKPOINT CREATION",
    )

    checkpoint = engine.create_checkpoint()

    assert_pass(
        checkpoint.slot
        in VALID_CHECKPOINT_SLOTS,
        "Checkpoint Created In Valid Slot",
    )

    assert_pass(
        checkpoint.generation
        == engine.state.generation,
        "Checkpoint Bound To Current Generation",
    )

    assert_pass(
        checkpoint.lineage_id
        == engine.state.lineage_id,
        "Checkpoint Bound To Current Lineage",
    )

    assert_pass(
        checkpoint.wal_length
        == len(engine.state.wal),
        "Checkpoint WAL Length Preserved",
    )


    # ========================================================================
    # TEST 6
    # ========================================================================

    print_test(
        6,
        "CHECKPOINT INTEGRITY VALIDATION",
    )

    validate_checkpoint(
        checkpoint,
        engine.state.wal[
            : checkpoint.wal_length
        ],
    )

    pass_line(
        "Checkpoint Integrity Validates"
    )


    # ========================================================================
    # TEST 7
    # ========================================================================

    print_test(
        7,
        "PROMOTION INTENT CREATION",
    )

    intent = engine.create_promotion_intent(
        checkpoint
    )

    assert_pass(
        intent.status
        == PROMOTION_PENDING,
        "Promotion Intent Is Pending",
    )

    assert_pass(
        intent.target_slot
        == checkpoint.slot,
        "Promotion Targets Correct Slot",
    )

    assert_pass(
        intent.target_checkpoint_sequence
        == checkpoint.sequence,
        "Promotion Targets Correct Checkpoint Sequence",
    )

    assert_pass(
        intent.generation
        == engine.state.generation,
        "Promotion Bound To Current Generation",
    )


    # ========================================================================
    # TEST 8
    # ========================================================================

    print_test(
        8,
        "PROMOTION INTENT INTEGRITY",
    )

    validate_promotion_intent(
        intent
    )

    pass_line(
        "Promotion Intent Seal Validates"
    )


    # ========================================================================
    # TEST 9
    # ========================================================================

    print_test(
        9,
        "COMMITTED MANIFEST PROMOTION",
    )

    manifest = engine.commit_checkpoint_promotion(
        intent
    )

    assert_pass(
        manifest.committed_slot
        == checkpoint.slot,
        "Manifest Commits Correct Slot",
    )

    assert_pass(
        manifest.checkpoint_sequence
        == checkpoint.sequence,
        "Manifest Anchors Checkpoint Sequence",
    )

    assert_pass(
        manifest.checkpoint_id
        == checkpoint.checkpoint_id,
        "Manifest Anchors Checkpoint Identity",
    )

    assert_pass(
        manifest.checkpoint_wal_length
        == checkpoint.wal_length,
        "Manifest Preserves Checkpoint WAL Boundary",
    )


    # ========================================================================
    # TEST 10
    # ========================================================================

    print_test(
        10,
        "COMMITTED MANIFEST INTEGRITY",
    )

    validate_manifest(
        manifest
    )

    pass_line(
        "Committed Manifest Seal Validates"
    )

    stored_intent = (
        engine
        .state
        .promotion_intents[
            intent.intent_id
        ]
    )

    assert_pass(
        stored_intent.status
        == PROMOTION_COMMITTED,
        "Promotion Intent Marked COMMITTED",
    )


    # ========================================================================
    # TEST 11
    # ========================================================================

    print_test(
        11,
        "POST-CHECKPOINT WAL PREFIX VALIDATION",
    )

    assert_pass(
        len(engine.state.wal)
        > checkpoint.wal_length,
        "Promotion Records Exist After Checkpoint Boundary",
    )

    prefix = checkpoint_wal_prefix(
        checkpoint,
        engine.state.wal,
    )

    assert_pass(
        len(prefix)
        == checkpoint.wal_length,
        "Checkpoint WAL Prefix Length Recovered",
    )

    assert_pass(
        wal_final_hash(prefix)
        == checkpoint.wal_final_hash,
        "Checkpoint WAL Prefix Hash Preserved",
    )


    # ========================================================================
    # TEST 12
    # ========================================================================

    print_test(
        12,
        "AUTHORITATIVE CHECKPOINT RECOVERY",
    )

    authoritative = (
        engine
        .recover_authoritative_checkpoint()
    )

    assert_pass(
        authoritative.slot
        == manifest.committed_slot,
        "Authoritative Checkpoint Matches Manifest Slot",
    )

    assert_pass(
        authoritative.sequence
        == manifest.checkpoint_sequence,
        "Authoritative Checkpoint Matches Manifest Sequence",
    )

    assert_pass(
        authoritative.checkpoint_id
        == manifest.checkpoint_id,
        "Authoritative Checkpoint Identity Preserved",
    )


    # ========================================================================
    # TEST 13
    # ========================================================================

    print_test(
        13,
        "COMMITTED AUTHORITY SURVIVES RESTART",
    )

    restarted = N31Engine.restore_state(
        engine.export_state()
    )

    restarted_manifest = (
        restarted
        .state
        .committed_manifest
    )

    assert_pass(
        restarted_manifest
        is not None,
        "Committed Manifest Survives Restart",
    )

    recovered = (
        restarted
        .recover_authoritative_checkpoint()
    )

    assert_pass(
        recovered.checkpoint_id
        == checkpoint.checkpoint_id,
        "Committed Authority Remains Recoverable",
    )


    # ========================================================================
    # TEST 14
    # ========================================================================

    print_test(
        14,
        "PROMOTION COMMIT IDEMPOTENCY",
    )

    same_manifest = (
        engine
        .commit_checkpoint_promotion(
            intent
        )
    )

    assert_pass(
        same_manifest.manifest_id
        == manifest.manifest_id,
        "Repeated Commit Returns Existing Manifest",
    )

    assert_pass(
        engine.state.manifest_sequence
        == 1,
        "Repeated Commit Does Not Advance Manifest Sequence",
    )


    # ========================================================================
    # TEST 15
    # ========================================================================

    print_test(
        15,
        "CHECKPOINT TAMPER REJECTION",
    )

    tampered_engine = (
        N31Engine.restore_state(
            engine.export_state()
        )
    )

    tampered_checkpoint = (
        tampered_engine
        .state
        .checkpoint_slots[
            manifest.committed_slot
        ]
    )

    tampered_checkpoint.wal_final_hash = (
        "0" * 64
    )

    expect_rejection(
        lambda: (
            tampered_engine
            .recover_authoritative_checkpoint()
        ),
        "checkpoint integrity seal mismatch",
        "Tampered Checkpoint Rejected",
    )


    # ========================================================================
    # TEST 16
    # ========================================================================

    print_test(
        16,
        "PROMOTION INTENT TAMPER REJECTION",
    )

    (
        e16,
        _,
        _,
        _,
    ) = build_completed_engine()

    cp16 = e16.create_checkpoint()

    i16 = e16.create_promotion_intent(
        cp16
    )

    bad_i16 = deep_clone(
        i16
    )

    bad_i16.target_checkpoint_sequence += 1

    expect_rejection(
        lambda: (
            e16
            .commit_checkpoint_promotion(
                bad_i16
            )
        ),
        "promotion intent integrity seal mismatch",
        "Tampered Promotion Intent Rejected",
    )


    # ========================================================================
    # TEST 17
    # ========================================================================

    print_test(
        17,
        "MANIFEST TAMPER REJECTION",
    )

    e17 = N31Engine.restore_state(
        engine.export_state()
    )

    assert (
        e17.state.committed_manifest
        is not None
    )

    (
        e17
        .state
        .committed_manifest
        .checkpoint_sequence
    ) += 1

    expect_rejection(
        lambda: (
            e17
            .recover_authoritative_checkpoint()
        ),
        "committed manifest integrity seal mismatch",
        "Tampered Manifest Rejected",
    )


    # ========================================================================
    # TEST 18
    # ========================================================================

    print_test(
        18,
        "STALE CHECKPOINT GENERATION REJECTION",
    )

    (
        e18,
        _,
        _,
        _,
    ) = build_completed_engine()

    stale_cp = (
        e18.create_checkpoint()
    )

    stale_intent = (
        e18.create_promotion_intent(
            stale_cp
        )
    )

    e18.advance_generation()

    expect_rejection(
        lambda: (
            e18
            .commit_checkpoint_promotion(
                stale_intent
            )
        ),
        "stale checkpoint generation",
        "Stale Generation Checkpoint Rejected",
    )


    # ========================================================================
    # TEST 19
    # ========================================================================

    print_test(
        19,
        "CHECKPOINT WAL FINAL HASH MISMATCH",
    )

    (
        e19,
        _,
        _,
        _,
    ) = build_completed_engine()

    cp19 = e19.create_checkpoint()

    # ------------------------------------------------------------------------
    # Reseal checkpoint so the seal itself is valid while the WAL hash claim
    # is deliberately incorrect.
    # ------------------------------------------------------------------------

    cp19.wal_final_hash = (
        "f" * 64
    )

    seal_checkpoint(
        cp19
    )

    e19.state.checkpoint_slots[
        cp19.slot
    ] = deep_clone(
        cp19
    )

    expect_rejection(
        lambda: checkpoint_wal_prefix(
            cp19,
            e19.state.wal,
        ),
        "checkpoint WAL final hash mismatch",
        "Checkpoint WAL Final Hash Mismatch Rejected",
    )


    # ========================================================================
    # TEST 20
    # ========================================================================

    print_test(
        20,
        "CHECKPOINT WAL LENGTH MISMATCH",
    )

    (
        e20,
        _,
        _,
        _,
    ) = build_completed_engine()

    cp20 = e20.create_checkpoint()

    cp20.wal_length += 1

    seal_checkpoint(
        cp20
    )

    expect_rejection(
        lambda: checkpoint_wal_prefix(
            cp20,
            e20.state.wal,
        ),
        "checkpoint WAL length exceeds current WAL",
        "Invalid Checkpoint WAL Length Rejected",
    )


    # ========================================================================
    # TEST 21
    # ========================================================================

    print_test(
        21,
        "PENDING PROMOTION SURVIVES RESTART",
    )

    (
        e21,
        _,
        _,
        _,
    ) = build_completed_engine()

    cp21 = e21.create_checkpoint()

    i21 = e21.create_promotion_intent(
        cp21
    )

    e21r = N31Engine.restore_state(
        e21.export_state()
    )

    assert_pass(
        (
            e21r
            .state
            .promotion_intents[
                i21.intent_id
            ]
            .status
        )
        == PROMOTION_PENDING,
        "Pending Promotion Intent Survives Restart",
    )

    m21 = (
        e21r
        .recover_pending_promotion()
    )

    assert_pass(
        m21 is not None,
        "Pending Promotion Recovered",
    )

    assert_pass(
        m21.checkpoint_id
        == cp21.checkpoint_id,
        "Recovered Promotion Commits Intended Checkpoint",
    )


    # ========================================================================
    # TEST 22
    # ========================================================================

    print_test(
        22,
        "POST-COMMIT RESTART RECOVERY",
    )

    e22r = N31Engine.restore_state(
        e21r.export_state()
    )

    a22 = (
        e22r
        .recover_authoritative_checkpoint()
    )

    assert_pass(
        a22.checkpoint_id
        == cp21.checkpoint_id,
        "Committed Checkpoint Recoverable After Second Restart",
    )

    assert_pass(
        e22r.recover_pending_promotion()
        is None,
        "No Pending Promotion After Commit",
    )


    # ========================================================================
    # TEST 23
    # ========================================================================

    print_test(
        23,
        "MANIFEST TO CHECKPOINT SEAL BINDING",
    )

    e23 = N31Engine.restore_state(
        engine.export_state()
    )

    assert (
        e23.state.committed_manifest
        is not None
    )

    cp23 = (
        e23
        .state
        .checkpoint_slots[
            e23
            .state
            .committed_manifest
            .committed_slot
        ]
    )

    # ------------------------------------------------------------------------
    # Reseal a different checkpoint body. The checkpoint itself becomes
    # internally valid, but the committed manifest must still reject it
    # because the manifest is bound to the original checkpoint seal.
    # ------------------------------------------------------------------------

    cp23.phase = PHASE_PREPARED

    seal_checkpoint(
        cp23
    )

    expect_rejection(
        lambda: (
            e23
            .recover_authoritative_checkpoint()
        ),
        "manifest checkpoint seal mismatch",
        "Manifest Rejects Resealed Different Checkpoint",
    )


    # ========================================================================
    # TEST 24
    # ========================================================================

    print_test(
        24,
        "NETWORK WRITE FIREBREAK",
    )

    assert_pass(
        REAL_POST_ENABLED is False,
        "Real POST Disabled",
    )

    assert_pass(
        DEMO_POST_ENABLED is False,
        "Demo POST Disabled",
    )

    assert_pass(
        NETWORK_WRITES_ENABLED is False,
        "All Network Writes Disabled",
    )

    assert_pass(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic Transport Only",
    )

    assert_pass(
        receipt.transmitted is False,
        "No Network Transmission Occurred",
    )


    # ========================================================================
    # TEST 25
    # ========================================================================

    print_test(
        25,
        "FINAL WAL VALIDATION",
    )

    validate_wal(
        engine.state.wal
    )

    pass_line(
        "WAL Records Validate"
    )

    assert_pass(
        wal_final_hash(
            engine.state.wal
        )
        == (
            engine
            .state
            .wal[-1]
            .record_hash
        ),
        "WAL Final Hash Valid",
    )


    # ========================================================================
    # FINAL RESULT
    # ========================================================================

    print(
        HEAVY_SEPARATOR,
        flush=True,
    )

    print(
        f"{UNIT_NAME}: "
        f"ALL DIAGNOSTICS PASSED",
        flush=True,
    )

    print(
        HEAVY_SEPARATOR,
        flush=True,
    )

    print(
        "SAFETY SUMMARY:",
        flush=True,
    )

    print(
        "  REAL POST DISABLED",
        flush=True,
    )

    print(
        "  DEMO POST DISABLED",
        flush=True,
    )

    print(
        "  ALL NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        "  SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )

    print(
        "  NO REAL ORDER OR LEVERAGE "
        "MUTATION WAS SENT",
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
                    "unit": UNIT_NAME,
                    "version": UNIT_VERSION,
                    "status": "ok",
                    "real_post": (
                        REAL_POST_ENABLED
                    ),
                    "demo_post": (
                        DEMO_POST_ENABLED
                    ),
                    "network_writes": (
                        NETWORK_WRITES_ENABLED
                    ),
                    "synthetic_only": (
                        SYNTHETIC_TRANSPORT_ONLY
                    ),
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
                f"HEALTH SERVER LISTENING "
                f"ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:

            print(
                f"{UNIT_NAME}: "
                f"HEALTH SERVER ERROR: "
                f"{exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:

    run_diagnostics()

    # ------------------------------------------------------------------------
    # Render-style persistent process support.
    #
    # Default:
    #     persistent health server + heartbeat
    #
    # One-shot local test:
    #     N31_PERSIST=0 python3 main.py
    # ------------------------------------------------------------------------

    persist = (
        os.environ.get(
            "N31_PERSIST",
            "1",
        )
        .strip()
        .lower()
        not in {
            "0",
            "false",
            "no",
            "off",
        }
    )

    if not persist:
        return

    start_health_server()

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{UNIT_NAME}: "
            f"HEARTBEAT {heartbeat}",
            flush=True,
        )

        time.sleep(
            30
        )


if __name__ == "__main__":
    main()
