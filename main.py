# ============================================================================
# R28 UNIT N.33
# DURABLE MANIFEST PROMOTION INTENT + CRASH-WINDOW RECOVERY
# + STALE PROMOTION FENCING + SAFE SLOT RECLAMATION
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
# N.33 INCREMENT OVER N.32:
#   - DURABLE MANIFEST PROMOTION INTENT
#   - PROMOTION INTENT INTEGRITY SEAL
#   - PROMOTION GENERATION / LINEAGE / EPOCH BINDING
#   - PROMOTION SOURCE / TARGET SLOT BINDING
#   - PROMOTION CHECKPOINT IDENTITY BINDING
#   - PRE-COMMIT PROMOTION CRASH RECOVERY
#   - POST-MANIFEST / PRE-FINALIZATION CRASH RECOVERY
#   - STALE PROMOTION INTENT REJECTION
#   - PROMOTION REPLAY REJECTION
#   - SAFE CHECKPOINT SLOT RECLAMATION
#   - ACTIVE / FALLBACK AUTHORITY PRESERVATION
#   - HISTORICAL WAL PREFIX PRESERVATION
#   - N.32 DUAL-SLOT AUTHORITY RULES RETAINED
#
# IMPORTANT:
#   This diagnostic NEVER transmits a network POST.
# ============================================================================

print("R28 UNIT N.33: MAIN.PY ENTERED", flush=True)

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


print("R28 UNIT N.33: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.33"
UNIT_VERSION = "N.33"

SYMBOL = "BTCUSDT"
HTTP_METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TARGET_LEVERAGE = "100"
TARGET_MARGIN_MODE = "ISOLATED"

INTEGRITY_KEY = b"R28-N33-LOCAL-INTEGRITY-KEY"
MANIFEST_KEY = b"R28-N33-MANIFEST-INTEGRITY-KEY"
CHECKPOINT_KEY = b"R28-N33-CHECKPOINT-INTEGRITY-KEY"
PROMOTION_KEY = b"R28-N33-PROMOTION-INTEGRITY-KEY"
AUTHORIZATION_KEY = b"R28-N33-AUTHORIZATION-INTEGRITY-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

PROMOTION_PENDING = "PENDING"
PROMOTION_COMMITTED = "COMMITTED"
PROMOTION_FINALIZED = "FINALIZED"
PROMOTION_REJECTED = "REJECTED"

SLOT_A = "A"
SLOT_B = "B"
VALID_SLOTS = {SLOT_A, SLOT_B}

ZERO_HASH = "0" * 64

HEARTBEAT_SECONDS = 30


print("R28 UNIT N.33: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# LOCAL EXCEPTIONS
# ============================================================================

class LocalBlock(Exception):
    pass


class ValidationFailure(Exception):
    pass


# ============================================================================
# BASIC HELPERS
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


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


def hmac_hex(key: bytes, value: str) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def secure_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(str(left), str(right))


def now_ns() -> int:
    return time.time_ns()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def opposite_slot(slot: str) -> str:
    if slot == SLOT_A:
        return SLOT_B
    if slot == SLOT_B:
        return SLOT_A
    raise LocalBlock("invalid checkpoint slot")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalBlock(message)


def announce_test(number: int, name: str) -> None:
    print("-" * 92, flush=True)
    print(
        f"R28 UNIT N.33 TEST {number}: {name}",
        flush=True,
    )
    print("-" * 92, flush=True)


def local_block(message: str) -> None:
    print("R28 UNIT N.33 LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


def pass_line(label: str) -> None:
    width = 76
    print(f"{label:<{width}} ✅ PASS", flush=True)


def fail_line(label: str) -> None:
    width = 76
    print(f"{label:<{width}} ❌ FAIL", flush=True)
    raise ValidationFailure(label)


def expect_local_block(
    label: str,
    expected_substring: str,
    func: Any,
) -> None:
    try:
        func()
    except LocalBlock as exc:
        local_block(str(exc))
        if expected_substring not in str(exc):
            fail_line(
                f"{label} "
                f"(expected '{expected_substring}', got '{exc}')"
            )
        pass_line(label)
        return

    fail_line(label)


# ============================================================================
# EXACT SYNTHETIC LEVERAGE PAYLOAD
# ============================================================================

def build_leverage_payload() -> Dict[str, str]:
    return {
        "leverage": TARGET_LEVERAGE,
        "marginMode": TARGET_MARGIN_MODE,
        "symbol": SYMBOL,
    }


LEVERAGE_PAYLOAD = build_leverage_payload()
LEVERAGE_PAYLOAD_HASH = sha256_json(LEVERAGE_PAYLOAD)


# ============================================================================
# WAL RECORD
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

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "record_type": self.record_type,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "payload": copy.deepcopy(self.payload),
            "previous_hash": self.previous_hash,
        }

    def calculate_hash(self) -> str:
        return sha256_json(self.unsigned_dict())

    def seal(self) -> None:
        self.record_hash = self.calculate_hash()

    def validate(self) -> None:
        require(
            self.sequence >= 1,
            "invalid WAL sequence",
        )
        require(
            bool(self.record_type),
            "invalid WAL record type",
        )
        require(
            bool(self.lineage),
            "invalid WAL lineage",
        )
        require(
            len(self.previous_hash) == 64,
            "invalid WAL previous hash",
        )
        require(
            secure_equal(
                self.record_hash,
                self.calculate_hash(),
            ),
            "WAL record hash mismatch",
        )


# ============================================================================
# RECOVERY LEASE
# ============================================================================

@dataclass
class RecoveryLease:
    lease_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    owner: str
    nonce: int
    active: bool = True

    def identity(self) -> Tuple[Any, ...]:
        return (
            self.lease_id,
            self.generation,
            self.lineage,
            self.recovery_epoch,
            self.owner,
            self.nonce,
        )


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
    lease_id: str
    lease_nonce: int
    consumed: bool = False
    seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "payload_hash": self.payload_hash,
            "lease_id": self.lease_id,
            "lease_nonce": self.lease_nonce,
            "consumed": self.consumed,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            AUTHORIZATION_KEY,
            canonical_json(self.unsigned_dict()),
        )

    def reseal(self) -> None:
        self.seal = self.calculate_seal()

    def validate_seal(self) -> None:
        require(
            secure_equal(
                self.seal,
                self.calculate_seal(),
            ),
            "authorization integrity seal mismatch",
        )


# ============================================================================
# SYNTHETIC DISPATCH
# ============================================================================

@dataclass
class SyntheticDispatch:
    dispatch_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    method: str
    path: str
    payload: Dict[str, Any]
    payload_hash: str
    transmitted: bool = False
    created_ns: int = field(default_factory=now_ns)

    def validate_binding(self) -> None:
        require(
            self.method == HTTP_METHOD,
            "transport method mismatch",
        )
        require(
            self.path == LEVERAGE_ENDPOINT,
            "transport path mismatch",
        )
        require(
            self.payload == LEVERAGE_PAYLOAD,
            "transport payload mismatch",
        )
        require(
            secure_equal(
                self.payload_hash,
                LEVERAGE_PAYLOAD_HASH,
            ),
            "transport payload hash mismatch",
        )
        require(
            self.transmitted is False,
            "synthetic dispatch was transmitted",
        )


# ============================================================================
# CHECKPOINT
# ============================================================================

@dataclass
class Checkpoint:
    checkpoint_id: str
    slot: str
    checkpoint_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    phase: str

    wal_length: int
    wal_final_hash: str

    payload_hash: str

    synthetic_dispatch_count: int

    authorization_consumed: bool

    created_ns: int = field(default_factory=now_ns)

    seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "slot": self.slot,
            "checkpoint_sequence": self.checkpoint_sequence,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "phase": self.phase,
            "wal_length": self.wal_length,
            "wal_final_hash": self.wal_final_hash,
            "payload_hash": self.payload_hash,
            "synthetic_dispatch_count": self.synthetic_dispatch_count,
            "authorization_consumed": self.authorization_consumed,
            "created_ns": self.created_ns,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            CHECKPOINT_KEY,
            canonical_json(self.unsigned_dict()),
        )

    def reseal(self) -> None:
        self.seal = self.calculate_seal()

    def validate_seal(self) -> None:
        require(
            secure_equal(
                self.seal,
                self.calculate_seal(),
            ),
            "checkpoint integrity seal mismatch",
        )

    def validate_shape(self) -> None:
        require(
            self.slot in VALID_SLOTS,
            "invalid checkpoint slot",
        )

        require(
            self.checkpoint_sequence >= 1,
            "invalid checkpoint sequence",
        )

        require(
            self.wal_length >= 0,
            "invalid checkpoint WAL length",
        )

        require(
            len(self.wal_final_hash) == 64,
            "invalid checkpoint WAL final hash",
        )

        require(
            secure_equal(
                self.payload_hash,
                LEVERAGE_PAYLOAD_HASH,
            ),
            "checkpoint payload hash mismatch",
        )


# ============================================================================
# COMMITTED MANIFEST
# ============================================================================

@dataclass
class CommittedManifest:
    manifest_id: str
    manifest_sequence: int

    checkpoint_slot: str
    checkpoint_id: str
    checkpoint_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    wal_length: int
    wal_final_hash: str

    previous_manifest_id: Optional[str]
    previous_manifest_sequence: int

    created_ns: int = field(default_factory=now_ns)

    seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "manifest_sequence": self.manifest_sequence,
            "checkpoint_slot": self.checkpoint_slot,
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_sequence": self.checkpoint_sequence,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "wal_length": self.wal_length,
            "wal_final_hash": self.wal_final_hash,
            "previous_manifest_id": self.previous_manifest_id,
            "previous_manifest_sequence": (
                self.previous_manifest_sequence
            ),
            "created_ns": self.created_ns,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            MANIFEST_KEY,
            canonical_json(self.unsigned_dict()),
        )

    def reseal(self) -> None:
        self.seal = self.calculate_seal()

    def validate_seal(self) -> None:
        require(
            secure_equal(
                self.seal,
                self.calculate_seal(),
            ),
            "committed manifest integrity seal mismatch",
        )

    def validate_shape(self) -> None:
        require(
            self.manifest_sequence >= 1,
            "invalid committed manifest sequence",
        )

        require(
            self.checkpoint_slot in VALID_SLOTS,
            "invalid committed manifest checkpoint slot",
        )

        require(
            self.checkpoint_sequence >= 1,
            "invalid committed manifest checkpoint sequence",
        )

        require(
            self.wal_length >= 0,
            "invalid committed manifest WAL length",
        )

        require(
            len(self.wal_final_hash) == 64,
            "invalid committed manifest WAL final hash",
        )


# ============================================================================
# N.33 DURABLE MANIFEST PROMOTION INTENT
# ============================================================================

@dataclass
class ManifestPromotionIntent:
    promotion_id: str
    promotion_sequence: int

    generation: int
    lineage: str
    recovery_epoch: int

    source_manifest_id: Optional[str]
    source_manifest_sequence: int
    source_slot: Optional[str]

    target_slot: str
    target_checkpoint_id: str
    target_checkpoint_sequence: int

    target_wal_length: int
    target_wal_final_hash: str

    state: str

    committed_manifest_id: Optional[str] = None
    committed_manifest_sequence: Optional[int] = None

    created_ns: int = field(default_factory=now_ns)
    finalized_ns: Optional[int] = None

    seal: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        return {
            "promotion_id": self.promotion_id,
            "promotion_sequence": self.promotion_sequence,
            "generation": self.generation,
            "lineage": self.lineage,
            "recovery_epoch": self.recovery_epoch,
            "source_manifest_id": self.source_manifest_id,
            "source_manifest_sequence": self.source_manifest_sequence,
            "source_slot": self.source_slot,
            "target_slot": self.target_slot,
            "target_checkpoint_id": self.target_checkpoint_id,
            "target_checkpoint_sequence": (
                self.target_checkpoint_sequence
            ),
            "target_wal_length": self.target_wal_length,
            "target_wal_final_hash": self.target_wal_final_hash,
            "state": self.state,
            "committed_manifest_id": self.committed_manifest_id,
            "committed_manifest_sequence": (
                self.committed_manifest_sequence
            ),
            "created_ns": self.created_ns,
            "finalized_ns": self.finalized_ns,
        }

    def calculate_seal(self) -> str:
        return hmac_hex(
            PROMOTION_KEY,
            canonical_json(self.unsigned_dict()),
        )

    def reseal(self) -> None:
        self.seal = self.calculate_seal()

    def validate_seal(self) -> None:
        require(
            secure_equal(
                self.seal,
                self.calculate_seal(),
            ),
            "promotion intent integrity seal mismatch",
        )

    def validate_shape(self) -> None:
        require(
            bool(self.promotion_id),
            "invalid promotion id",
        )

        require(
            self.promotion_sequence >= 1,
            "invalid promotion sequence",
        )

        require(
            self.target_slot in VALID_SLOTS,
            "invalid promotion target slot",
        )

        require(
            self.target_checkpoint_sequence >= 1,
            "invalid promotion checkpoint sequence",
        )

        require(
            self.target_wal_length >= 0,
            "invalid promotion WAL length",
        )

        require(
            len(self.target_wal_final_hash) == 64,
            "invalid promotion WAL final hash",
        )

        require(
            self.state in {
                PROMOTION_PENDING,
                PROMOTION_COMMITTED,
                PROMOTION_FINALIZED,
                PROMOTION_REJECTED,
            },
            "invalid promotion state",
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

    wal: List[WALRecord]

    checkpoints: Dict[str, Optional[Checkpoint]]

    committed_manifest: Optional[CommittedManifest]
    fallback_manifest: Optional[CommittedManifest]

    pending_promotion: Optional[ManifestPromotionIntent]
    finalized_promotion_ids: Set[str]

    recovery_lease: Optional[RecoveryLease]
    authorization: Optional[Authorization]

    synthetic_dispatches: List[SyntheticDispatch]

    next_checkpoint_sequence: int
    next_manifest_sequence: int
    next_promotion_sequence: int

    highest_committed_manifest_sequence: int
    highest_committed_checkpoint_sequence: int

    reclaimed_checkpoint_ids: Set[str]

    def clone(self) -> "DurableState":
        return copy.deepcopy(self)


# ============================================================================
# ENGINE
# ============================================================================

class N33Engine:
    def __init__(self) -> None:
        self._lock = threading.RLock()

        self.state = DurableState(
            generation=1,
            lineage=new_id("lineage"),
            recovery_epoch=1,
            phase=PHASE_PREPARED,

            wal=[],

            checkpoints={
                SLOT_A: None,
                SLOT_B: None,
            },

            committed_manifest=None,
            fallback_manifest=None,

            pending_promotion=None,
            finalized_promotion_ids=set(),

            recovery_lease=None,
            authorization=None,

            synthetic_dispatches=[],

            next_checkpoint_sequence=1,
            next_manifest_sequence=1,
            next_promotion_sequence=1,

            highest_committed_manifest_sequence=0,
            highest_committed_checkpoint_sequence=0,

            reclaimed_checkpoint_ids=set(),
        )

        self._append_wal(
            "ENGINE_INITIALIZED",
            {
                "phase": PHASE_PREPARED,
                "payload_hash": LEVERAGE_PAYLOAD_HASH,
            },
        )

    # ========================================================================
    # WAL
    # ========================================================================

    def _append_wal(
        self,
        record_type: str,
        payload: Dict[str, Any],
    ) -> WALRecord:
        previous_hash = (
            self.state.wal[-1].record_hash
            if self.state.wal
            else ZERO_HASH
        )

        record = WALRecord(
            sequence=len(self.state.wal) + 1,
            record_type=record_type,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            payload=copy.deepcopy(payload),
            previous_hash=previous_hash,
        )

        record.seal()

        self.state.wal.append(record)

        return record

    def validate_wal(
        self,
        upto_length: Optional[int] = None,
    ) -> str:
        with self._lock:
            wal = self.state.wal

            if upto_length is None:
                upto_length = len(wal)

            require(
                0 <= upto_length <= len(wal),
                "invalid WAL validation length",
            )

            previous_hash = ZERO_HASH

            for index in range(upto_length):
                record = wal[index]

                record.validate()

                require(
                    record.sequence == index + 1,
                    "WAL sequence mismatch",
                )

                require(
                    secure_equal(
                        record.previous_hash,
                        previous_hash,
                    ),
                    "WAL hash-chain mismatch",
                )

                previous_hash = record.record_hash

            return previous_hash

    def current_wal_final_hash(self) -> str:
        if not self.state.wal:
            return ZERO_HASH

        return self.state.wal[-1].record_hash

    # ========================================================================
    # RECOVERY LEASE
    # ========================================================================

    def acquire_recovery_lease(
        self,
        owner: str = "local-n33-worker",
    ) -> RecoveryLease:
        with self._lock:
            require(
                self.state.phase != PHASE_COMPLETED,
                "terminal generation cannot acquire recovery lease",
            )

            prior_nonce = 0

            if self.state.recovery_lease is not None:
                prior_nonce = self.state.recovery_lease.nonce

                require(
                    not self.state.recovery_lease.active,
                    "recovery lease already active",
                )

            lease = RecoveryLease(
                lease_id=new_id("lease"),
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                owner=owner,
                nonce=prior_nonce + 1,
                active=True,
            )

            self.state.recovery_lease = lease

            self._append_wal(
                "RECOVERY_LEASE_ACQUIRED",
                {
                    "lease_id": lease.lease_id,
                    "owner": lease.owner,
                    "nonce": lease.nonce,
                },
            )

            return copy.deepcopy(lease)

    def validate_recovery_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        with self._lock:
            current = self.state.recovery_lease

            require(
                current is not None,
                "recovery lease missing",
            )

            require(
                current.active,
                "recovery lease inactive",
            )

            require(
                lease.generation == self.state.generation,
                "recovery lease generation mismatch",
            )

            require(
                lease.lineage == self.state.lineage,
                "recovery lease lineage mismatch",
            )

            require(
                lease.recovery_epoch == self.state.recovery_epoch,
                "recovery lease recovery epoch mismatch",
            )

            require(
                lease.lease_id == current.lease_id,
                "recovery lease id mismatch",
            )

            require(
                lease.owner == current.owner,
                "recovery lease owner mismatch",
            )

            require(
                lease.nonce == current.nonce,
                "recovery lease nonce mismatch",
            )

    # ========================================================================
    # AUTHORIZATION
    # ========================================================================

    def authorize(
        self,
        lease: RecoveryLease,
    ) -> Authorization:
        with self._lock:
            self.validate_recovery_lease(lease)

            require(
                self.state.phase == PHASE_PREPARED,
                "generation is not prepared",
            )

            authorization = Authorization(
                authorization_id=new_id("auth"),
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                payload_hash=LEVERAGE_PAYLOAD_HASH,
                lease_id=lease.lease_id,
                lease_nonce=lease.nonce,
                consumed=False,
            )

            authorization.reseal()

            self.state.authorization = authorization
            self.state.phase = PHASE_AUTHORIZED

            self._append_wal(
                "AUTHORIZATION_GRANTED",
                {
                    "authorization_id": (
                        authorization.authorization_id
                    ),
                    "payload_hash": authorization.payload_hash,
                    "lease_id": authorization.lease_id,
                    "lease_nonce": authorization.lease_nonce,
                },
            )

            return copy.deepcopy(authorization)

    def validate_authorization(
        self,
        authorization: Authorization,
        lease: RecoveryLease,
    ) -> None:
        with self._lock:
            authorization.validate_seal()

            self.validate_recovery_lease(lease)

            current = self.state.authorization

            require(
                current is not None,
                "authorization missing",
            )

            current.validate_seal()

            require(
                authorization.authorization_id
                == current.authorization_id,
                "authorization id mismatch",
            )

            require(
                authorization.generation
                == self.state.generation,
                "authorization generation mismatch",
            )

            require(
                authorization.lineage
                == self.state.lineage,
                "authorization lineage mismatch",
            )

            require(
                authorization.recovery_epoch
                == self.state.recovery_epoch,
                "authorization recovery epoch mismatch",
            )

            require(
                secure_equal(
                    authorization.payload_hash,
                    LEVERAGE_PAYLOAD_HASH,
                ),
                "authorization payload hash mismatch",
            )

            require(
                authorization.lease_id == lease.lease_id,
                "authorization lease mismatch",
            )

            require(
                authorization.lease_nonce == lease.nonce,
                "authorization lease nonce mismatch",
            )

            require(
                current.consumed is False,
                "authorization already consumed",
            )

    def consume_authorization(
        self,
        authorization: Authorization,
        lease: RecoveryLease,
    ) -> None:
        with self._lock:
            self.validate_authorization(
                authorization,
                lease,
            )

            current = self.state.authorization

            require(
                current is not None,
                "authorization missing",
            )

            current.consumed = True
            current.reseal()

            self._append_wal(
                "AUTHORIZATION_CONSUMED",
                {
                    "authorization_id": (
                        current.authorization_id
                    ),
                },
            )

    # ========================================================================
    # SYNTHETIC TRANSPORT
    # ========================================================================

    def synthetic_dispatch(
        self,
        authorization: Authorization,
        lease: RecoveryLease,
    ) -> SyntheticDispatch:
        with self._lock:
            self.validate_recovery_lease(lease)

            current_auth = self.state.authorization

            require(
                current_auth is not None,
                "authorization missing",
            )

            current_auth.validate_seal()

            require(
                current_auth.authorization_id
                == authorization.authorization_id,
                "authorization id mismatch",
            )

            require(
                current_auth.consumed,
                "authorization has not been consumed",
            )

            require(
                self.state.phase in {
                    PHASE_AUTHORIZED,
                    PHASE_COMMITTED,
                },
                "generation cannot dispatch",
            )

            require(
                len(self.state.synthetic_dispatches) == 0,
                "synthetic dispatch already exists",
            )

            dispatch = SyntheticDispatch(
                dispatch_id=new_id("dispatch"),
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload=copy.deepcopy(LEVERAGE_PAYLOAD),
                payload_hash=LEVERAGE_PAYLOAD_HASH,
                transmitted=False,
            )

            dispatch.validate_binding()

            self.state.synthetic_dispatches.append(dispatch)
            self.state.phase = PHASE_DISPATCHED

            self._append_wal(
                "SYNTHETIC_DISPATCH_CREATED",
                {
                    "dispatch_id": dispatch.dispatch_id,
                    "method": dispatch.method,
                    "path": dispatch.path,
                    "payload_hash": dispatch.payload_hash,
                    "transmitted": False,
                },
            )

            return copy.deepcopy(dispatch)

    # ========================================================================
    # HARD NETWORK FIREBREAK
    # ========================================================================

    def real_network_post(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        raise LocalBlock(
            "real network POST is disabled"
        )

    def demo_network_post(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        raise LocalBlock(
            "demo network POST is disabled"
        )


print("R28 UNIT N.33: PART 1 DEFINITIONS LOADED", flush=True)

# ============================================================================
# END OF PART 1 OF 4
#
# NEXT:
#   PART 2 CONTINUES AT ZERO INDENTATION WITH:
#     - CHECKPOINT CREATION / VALIDATION
#     - COMMITTED MANIFEST VALIDATION
#     - N.33 PROMOTION INTENT CREATION
#     - PROMOTION COMMIT / FINALIZATION
#     - RESTART RECOVERY
#     - SAFE SLOT RECLAMATION
#
# DO NOT ADD OR REMOVE INDENTATION AT THE PART-1 / PART-2 JOINT.
# ============================================================================
# ============================================================================
# R28 UNIT N.33
# DURABLE MANIFEST PROMOTION INTENT + CRASH-WINDOW RECOVERY
# + STALE PROMOTION FENCING + SAFE SLOT RECLAMATION
#
# CORRECTED COPY/PASTE VERSION
# PART 2 OF 4
# ============================================================================


# ============================================================================
# CHECKPOINT CREATION
# ============================================================================

def _n33_create_checkpoint(
    self: N33Engine,
    slot: Optional[str] = None,
) -> Checkpoint:
    with self._lock:
        self.validate_wal()

        if slot is None:
            if self.state.committed_manifest is None:
                slot = SLOT_A
            else:
                slot = opposite_slot(
                    self.state.committed_manifest.checkpoint_slot
                )

        require(
            slot in VALID_SLOTS,
            "invalid checkpoint slot",
        )

        checkpoint_sequence = (
            self.state.next_checkpoint_sequence
        )

        wal_length = len(self.state.wal)

        wal_final_hash = self.validate_wal(
            wal_length
        )

        checkpoint = Checkpoint(
            checkpoint_id=new_id("checkpoint"),
            slot=slot,
            checkpoint_sequence=checkpoint_sequence,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            phase=self.state.phase,
            wal_length=wal_length,
            wal_final_hash=wal_final_hash,
            payload_hash=LEVERAGE_PAYLOAD_HASH,
            synthetic_dispatch_count=len(
                self.state.synthetic_dispatches
            ),
            authorization_consumed=(
                self.state.authorization is not None
                and self.state.authorization.consumed
            ),
        )

        checkpoint.reseal()

        self.state.checkpoints[slot] = checkpoint

        self.state.next_checkpoint_sequence += 1

        self._append_wal(
            "CHECKPOINT_WRITTEN",
            {
                "checkpoint_id": checkpoint.checkpoint_id,
                "slot": checkpoint.slot,
                "checkpoint_sequence": (
                    checkpoint.checkpoint_sequence
                ),
                "checkpoint_wal_length": (
                    checkpoint.wal_length
                ),
                "checkpoint_wal_final_hash": (
                    checkpoint.wal_final_hash
                ),
            },
        )

        return copy.deepcopy(checkpoint)


N33Engine.create_checkpoint = _n33_create_checkpoint


# ============================================================================
# CHECKPOINT VALIDATION
# ============================================================================

def _n33_validate_checkpoint(
    self: N33Engine,
    checkpoint: Checkpoint,
) -> None:
    with self._lock:
        checkpoint.validate_shape()
        checkpoint.validate_seal()

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
            checkpoint.wal_length
            <= len(self.state.wal),
            "checkpoint WAL length mismatch",
        )

        historical_hash = self.validate_wal(
            checkpoint.wal_length
        )

        require(
            secure_equal(
                historical_hash,
                checkpoint.wal_final_hash,
            ),
            "checkpoint WAL final hash mismatch",
        )

        require(
            checkpoint.checkpoint_id
            not in self.state.reclaimed_checkpoint_ids,
            "checkpoint has been reclaimed",
        )


N33Engine.validate_checkpoint = _n33_validate_checkpoint


# ============================================================================
# CHECKPOINT SLOT LOOKUP
# ============================================================================

def _n33_get_checkpoint(
    self: N33Engine,
    slot: str,
) -> Checkpoint:
    with self._lock:
        require(
            slot in VALID_SLOTS,
            "invalid checkpoint slot",
        )

        checkpoint = self.state.checkpoints.get(
            slot
        )

        require(
            checkpoint is not None,
            "manifest checkpoint missing",
        )

        return checkpoint


N33Engine.get_checkpoint = _n33_get_checkpoint


# ============================================================================
# MANIFEST VALIDATION
# ============================================================================

def _n33_validate_manifest(
    self: N33Engine,
    manifest: CommittedManifest,
    *,
    enforce_high_watermark: bool = True,
) -> None:
    with self._lock:
        manifest.validate_shape()
        manifest.validate_seal()

        require(
            manifest.generation
            == self.state.generation,
            "committed manifest generation mismatch",
        )

        require(
            manifest.lineage
            == self.state.lineage,
            "committed manifest lineage mismatch",
        )

        require(
            manifest.recovery_epoch
            == self.state.recovery_epoch,
            "committed manifest recovery epoch mismatch",
        )

        checkpoint = self.get_checkpoint(
            manifest.checkpoint_slot
        )

        self.validate_checkpoint(
            checkpoint
        )

        require(
            checkpoint.checkpoint_id
            == manifest.checkpoint_id,
            "manifest checkpoint identity mismatch",
        )

        require(
            checkpoint.checkpoint_sequence
            == manifest.checkpoint_sequence,
            "manifest checkpoint sequence mismatch",
        )

        require(
            checkpoint.generation
            == manifest.generation,
            "manifest/checkpoint generation mismatch",
        )

        require(
            checkpoint.lineage
            == manifest.lineage,
            "manifest/checkpoint lineage mismatch",
        )

        require(
            checkpoint.recovery_epoch
            == manifest.recovery_epoch,
            "manifest/checkpoint recovery epoch mismatch",
        )

        require(
            checkpoint.wal_length
            == manifest.wal_length,
            "manifest/checkpoint WAL length mismatch",
        )

        require(
            secure_equal(
                checkpoint.wal_final_hash,
                manifest.wal_final_hash,
            ),
            "manifest/checkpoint WAL hash mismatch",
        )

        historical_hash = self.validate_wal(
            manifest.wal_length
        )

        require(
            secure_equal(
                historical_hash,
                manifest.wal_final_hash,
            ),
            "committed manifest historical WAL mismatch",
        )

        if enforce_high_watermark:
            require(
                manifest.manifest_sequence
                >= self.state.highest_committed_manifest_sequence,
                "committed manifest sequence rollback detected",
            )

            require(
                manifest.checkpoint_sequence
                >= self.state.highest_committed_checkpoint_sequence,
                "committed checkpoint sequence rollback detected",
            )


N33Engine.validate_manifest = _n33_validate_manifest


# ============================================================================
# INITIAL COMMITTED MANIFEST
# ============================================================================

def _n33_commit_initial_manifest(
    self: N33Engine,
    checkpoint: Checkpoint,
) -> CommittedManifest:
    with self._lock:
        require(
            self.state.committed_manifest is None,
            "committed manifest already exists",
        )

        self.validate_checkpoint(
            checkpoint
        )

        stored = self.get_checkpoint(
            checkpoint.slot
        )

        require(
            stored.checkpoint_id
            == checkpoint.checkpoint_id,
            "checkpoint identity mismatch",
        )

        manifest_sequence = (
            self.state.next_manifest_sequence
        )

        manifest = CommittedManifest(
            manifest_id=new_id("manifest"),
            manifest_sequence=manifest_sequence,
            checkpoint_slot=checkpoint.slot,
            checkpoint_id=checkpoint.checkpoint_id,
            checkpoint_sequence=(
                checkpoint.checkpoint_sequence
            ),
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            wal_length=checkpoint.wal_length,
            wal_final_hash=checkpoint.wal_final_hash,
            previous_manifest_id=None,
            previous_manifest_sequence=0,
        )

        manifest.reseal()

        self.state.committed_manifest = manifest
        self.state.fallback_manifest = None

        self.state.next_manifest_sequence += 1

        self.state.highest_committed_manifest_sequence = (
            manifest.manifest_sequence
        )

        self.state.highest_committed_checkpoint_sequence = (
            checkpoint.checkpoint_sequence
        )

        self._append_wal(
            "INITIAL_MANIFEST_COMMITTED",
            {
                "manifest_id": manifest.manifest_id,
                "manifest_sequence": (
                    manifest.manifest_sequence
                ),
                "checkpoint_slot": (
                    manifest.checkpoint_slot
                ),
                "checkpoint_id": (
                    manifest.checkpoint_id
                ),
                "checkpoint_sequence": (
                    manifest.checkpoint_sequence
                ),
            },
        )

        return copy.deepcopy(manifest)


N33Engine.commit_initial_manifest = (
    _n33_commit_initial_manifest
)


# ============================================================================
# N.33 PROMOTION INTENT CREATION
# ============================================================================

def _n33_prepare_manifest_promotion(
    self: N33Engine,
    checkpoint: Checkpoint,
) -> ManifestPromotionIntent:
    with self._lock:
        require(
            self.state.committed_manifest is not None,
            "committed manifest missing",
        )

        require(
            self.state.pending_promotion is None,
            "manifest promotion already pending",
        )

        current_manifest = (
            self.state.committed_manifest
        )

        self.validate_manifest(
            current_manifest
        )

        self.validate_checkpoint(
            checkpoint
        )

        stored_checkpoint = self.get_checkpoint(
            checkpoint.slot
        )

        require(
            stored_checkpoint.checkpoint_id
            == checkpoint.checkpoint_id,
            "promotion checkpoint identity mismatch",
        )

        require(
            checkpoint.slot
            != current_manifest.checkpoint_slot,
            "promotion target slot equals committed slot",
        )

        require(
            checkpoint.checkpoint_sequence
            > current_manifest.checkpoint_sequence,
            "promotion checkpoint sequence not newer",
        )

        require(
            checkpoint.wal_length
            >= current_manifest.wal_length,
            "promotion WAL boundary rollback detected",
        )

        require(
            checkpoint.generation
            == current_manifest.generation,
            "promotion generation mismatch",
        )

        require(
            checkpoint.lineage
            == current_manifest.lineage,
            "promotion lineage mismatch",
        )

        require(
            checkpoint.recovery_epoch
            == current_manifest.recovery_epoch,
            "promotion recovery epoch mismatch",
        )

        intent = ManifestPromotionIntent(
            promotion_id=new_id("promotion"),
            promotion_sequence=(
                self.state.next_promotion_sequence
            ),
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            source_manifest_id=(
                current_manifest.manifest_id
            ),
            source_manifest_sequence=(
                current_manifest.manifest_sequence
            ),
            source_slot=(
                current_manifest.checkpoint_slot
            ),
            target_slot=checkpoint.slot,
            target_checkpoint_id=(
                checkpoint.checkpoint_id
            ),
            target_checkpoint_sequence=(
                checkpoint.checkpoint_sequence
            ),
            target_wal_length=(
                checkpoint.wal_length
            ),
            target_wal_final_hash=(
                checkpoint.wal_final_hash
            ),
            state=PROMOTION_PENDING,
        )

        intent.reseal()

        self.state.pending_promotion = intent

        self.state.next_promotion_sequence += 1

        self._append_wal(
            "MANIFEST_PROMOTION_PREPARED",
            {
                "promotion_id": intent.promotion_id,
                "promotion_sequence": (
                    intent.promotion_sequence
                ),
                "source_manifest_id": (
                    intent.source_manifest_id
                ),
                "source_manifest_sequence": (
                    intent.source_manifest_sequence
                ),
                "source_slot": intent.source_slot,
                "target_slot": intent.target_slot,
                "target_checkpoint_id": (
                    intent.target_checkpoint_id
                ),
                "target_checkpoint_sequence": (
                    intent.target_checkpoint_sequence
                ),
                "target_wal_length": (
                    intent.target_wal_length
                ),
                "target_wal_final_hash": (
                    intent.target_wal_final_hash
                ),
            },
        )

        return copy.deepcopy(intent)


N33Engine.prepare_manifest_promotion = (
    _n33_prepare_manifest_promotion
)


# ============================================================================
# PROMOTION INTENT VALIDATION
# ============================================================================

def _n33_validate_promotion_intent(
    self: N33Engine,
    intent: ManifestPromotionIntent,
) -> None:
    with self._lock:
        intent.validate_shape()
        intent.validate_seal()

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
            intent.promotion_id
            not in self.state.finalized_promotion_ids,
            "promotion intent already finalized",
        )

        current = self.state.pending_promotion

        require(
            current is not None,
            "pending promotion missing",
        )

        current.validate_seal()

        require(
            intent.promotion_id
            == current.promotion_id,
            "promotion intent id mismatch",
        )

        require(
            intent.promotion_sequence
            == current.promotion_sequence,
            "promotion intent sequence mismatch",
        )

        require(
            intent.source_manifest_id
            == current.source_manifest_id,
            "promotion source manifest mismatch",
        )

        require(
            intent.source_manifest_sequence
            == current.source_manifest_sequence,
            "promotion source manifest sequence mismatch",
        )

        require(
            intent.source_slot
            == current.source_slot,
            "promotion source slot mismatch",
        )

        require(
            intent.target_slot
            == current.target_slot,
            "promotion target slot mismatch",
        )

        require(
            intent.target_checkpoint_id
            == current.target_checkpoint_id,
            "promotion checkpoint identity mismatch",
        )

        require(
            intent.target_checkpoint_sequence
            == current.target_checkpoint_sequence,
            "promotion checkpoint sequence mismatch",
        )

        require(
            intent.target_wal_length
            == current.target_wal_length,
            "promotion WAL length mismatch",
        )

        require(
            secure_equal(
                intent.target_wal_final_hash,
                current.target_wal_final_hash,
            ),
            "promotion WAL final hash mismatch",
        )

        require(
            intent.state == current.state,
            "promotion intent state mismatch",
        )

        require(
            intent.state in {
                PROMOTION_PENDING,
                PROMOTION_COMMITTED,
            },
            "promotion intent is not recoverable",
        )

        checkpoint = self.get_checkpoint(
            intent.target_slot
        )

        self.validate_checkpoint(
            checkpoint
        )

        require(
            checkpoint.checkpoint_id
            == intent.target_checkpoint_id,
            "promotion checkpoint identity mismatch",
        )

        require(
            checkpoint.checkpoint_sequence
            == intent.target_checkpoint_sequence,
            "promotion checkpoint sequence mismatch",
        )

        require(
            checkpoint.wal_length
            == intent.target_wal_length,
            "promotion checkpoint WAL length mismatch",
        )

        require(
            secure_equal(
                checkpoint.wal_final_hash,
                intent.target_wal_final_hash,
            ),
            "promotion checkpoint WAL hash mismatch",
        )


N33Engine.validate_promotion_intent = (
    _n33_validate_promotion_intent
)


# ============================================================================
# STALE PROMOTION SOURCE FENCING
# ============================================================================

def _n33_validate_promotion_source(
    self: N33Engine,
    intent: ManifestPromotionIntent,
) -> None:
    with self._lock:
        current_manifest = (
            self.state.committed_manifest
        )

        require(
            current_manifest is not None,
            "committed manifest missing",
        )

        current_manifest.validate_seal()

        if intent.state == PROMOTION_PENDING:
            require(
                intent.source_manifest_id
                == current_manifest.manifest_id,
                "stale promotion source manifest",
            )

            require(
                intent.source_manifest_sequence
                == current_manifest.manifest_sequence,
                "stale promotion source sequence",
            )

            require(
                intent.source_slot
                == current_manifest.checkpoint_slot,
                "stale promotion source slot",
            )

        elif intent.state == PROMOTION_COMMITTED:
            require(
                intent.committed_manifest_id
                == current_manifest.manifest_id,
                "promotion committed manifest mismatch",
            )

            require(
                intent.committed_manifest_sequence
                == current_manifest.manifest_sequence,
                "promotion committed manifest sequence mismatch",
            )


N33Engine.validate_promotion_source = (
    _n33_validate_promotion_source
)


# ============================================================================
# COMMIT MANIFEST PROMOTION
# ============================================================================

def _n33_commit_manifest_promotion(
    self: N33Engine,
    intent: ManifestPromotionIntent,
) -> CommittedManifest:
    with self._lock:
        self.validate_promotion_intent(
            intent
        )

        self.validate_promotion_source(
            intent
        )

        require(
            intent.state == PROMOTION_PENDING,
            "promotion intent is not pending",
        )

        current_manifest = (
            self.state.committed_manifest
        )

        require(
            current_manifest is not None,
            "committed manifest missing",
        )

        checkpoint = self.get_checkpoint(
            intent.target_slot
        )

        self.validate_checkpoint(
            checkpoint
        )

        require(
            checkpoint.checkpoint_id
            == intent.target_checkpoint_id,
            "promotion checkpoint identity mismatch",
        )

        require(
            checkpoint.checkpoint_sequence
            == intent.target_checkpoint_sequence,
            "promotion checkpoint sequence mismatch",
        )

        require(
            checkpoint.checkpoint_sequence
            > current_manifest.checkpoint_sequence,
            "promotion checkpoint sequence rollback detected",
        )

        manifest_sequence = (
            self.state.next_manifest_sequence
        )

        require(
            manifest_sequence
            > current_manifest.manifest_sequence,
            "manifest sequence did not advance",
        )

        new_manifest = CommittedManifest(
            manifest_id=new_id("manifest"),
            manifest_sequence=manifest_sequence,
            checkpoint_slot=checkpoint.slot,
            checkpoint_id=checkpoint.checkpoint_id,
            checkpoint_sequence=(
                checkpoint.checkpoint_sequence
            ),
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            wal_length=checkpoint.wal_length,
            wal_final_hash=checkpoint.wal_final_hash,
            previous_manifest_id=(
                current_manifest.manifest_id
            ),
            previous_manifest_sequence=(
                current_manifest.manifest_sequence
            ),
        )

        new_manifest.reseal()

        self.state.fallback_manifest = copy.deepcopy(
            current_manifest
        )

        self.state.committed_manifest = new_manifest

        self.state.next_manifest_sequence += 1

        self.state.highest_committed_manifest_sequence = (
            new_manifest.manifest_sequence
        )

        self.state.highest_committed_checkpoint_sequence = (
            new_manifest.checkpoint_sequence
        )

        current_intent = (
            self.state.pending_promotion
        )

        require(
            current_intent is not None,
            "pending promotion missing",
        )

        current_intent.state = PROMOTION_COMMITTED
        current_intent.committed_manifest_id = (
            new_manifest.manifest_id
        )
        current_intent.committed_manifest_sequence = (
            new_manifest.manifest_sequence
        )
        current_intent.reseal()

        self._append_wal(
            "MANIFEST_PROMOTION_COMMITTED",
            {
                "promotion_id": (
                    current_intent.promotion_id
                ),
                "manifest_id": (
                    new_manifest.manifest_id
                ),
                "manifest_sequence": (
                    new_manifest.manifest_sequence
                ),
                "checkpoint_slot": (
                    new_manifest.checkpoint_slot
                ),
                "checkpoint_id": (
                    new_manifest.checkpoint_id
                ),
                "checkpoint_sequence": (
                    new_manifest.checkpoint_sequence
                ),
                "fallback_manifest_id": (
                    self.state.fallback_manifest.manifest_id
                ),
                "fallback_manifest_sequence": (
                    self.state.fallback_manifest.manifest_sequence
                ),
            },
        )

        return copy.deepcopy(new_manifest)


N33Engine.commit_manifest_promotion = (
    _n33_commit_manifest_promotion
)


# ============================================================================
# FINALIZE MANIFEST PROMOTION
# ============================================================================

def _n33_finalize_manifest_promotion(
    self: N33Engine,
    intent: ManifestPromotionIntent,
) -> None:
    with self._lock:
        self.validate_promotion_intent(
            intent
        )

        self.validate_promotion_source(
            intent
        )

        current_intent = (
            self.state.pending_promotion
        )

        require(
            current_intent is not None,
            "pending promotion missing",
        )

        require(
            current_intent.state
            == PROMOTION_COMMITTED,
            "promotion has not committed",
        )

        require(
            current_intent.committed_manifest_id
            is not None,
            "promotion committed manifest missing",
        )

        require(
            current_intent.committed_manifest_sequence
            is not None,
            "promotion committed manifest sequence missing",
        )

        current_intent.state = (
            PROMOTION_FINALIZED
        )

        current_intent.finalized_ns = now_ns()

        current_intent.reseal()

        finalized_id = (
            current_intent.promotion_id
        )

        self.state.finalized_promotion_ids.add(
            finalized_id
        )

        self._append_wal(
            "MANIFEST_PROMOTION_FINALIZED",
            {
                "promotion_id": finalized_id,
                "manifest_id": (
                    current_intent.committed_manifest_id
                ),
                "manifest_sequence": (
                    current_intent.committed_manifest_sequence
                ),
            },
        )

        self.state.pending_promotion = None


N33Engine.finalize_manifest_promotion = (
    _n33_finalize_manifest_promotion
)


# ============================================================================
# SAFE CHECKPOINT SLOT RECLAMATION
# ============================================================================

def _n33_reclaim_checkpoint_slot(
    self: N33Engine,
    slot: str,
) -> Optional[str]:
    with self._lock:
        require(
            slot in VALID_SLOTS,
            "invalid checkpoint slot",
        )

        current_manifest = (
            self.state.committed_manifest
        )

        require(
            current_manifest is not None,
            "committed manifest missing",
        )

        require(
            slot
            != current_manifest.checkpoint_slot,
            "cannot reclaim active checkpoint slot",
        )

        if self.state.fallback_manifest is not None:
            require(
                slot
                != self.state.fallback_manifest.checkpoint_slot,
                "cannot reclaim fallback checkpoint slot",
            )

        if self.state.pending_promotion is not None:
            pending = self.state.pending_promotion

            require(
                slot != pending.target_slot,
                "cannot reclaim pending promotion target slot",
            )

            if pending.source_slot is not None:
                require(
                    slot != pending.source_slot,
                    "cannot reclaim pending promotion source slot",
                )

        checkpoint = self.state.checkpoints.get(
            slot
        )

        if checkpoint is None:
            return None

        checkpoint.validate_seal()

        checkpoint_id = checkpoint.checkpoint_id

        self.state.reclaimed_checkpoint_ids.add(
            checkpoint_id
        )

        self.state.checkpoints[slot] = None

        self._append_wal(
            "CHECKPOINT_SLOT_RECLAIMED",
            {
                "slot": slot,
                "checkpoint_id": checkpoint_id,
            },
        )

        return checkpoint_id


N33Engine.reclaim_checkpoint_slot = (
    _n33_reclaim_checkpoint_slot
)


# ============================================================================
# FALLBACK MANIFEST RELEASE
# ============================================================================

def _n33_release_fallback_manifest(
    self: N33Engine,
) -> Optional[CommittedManifest]:
    with self._lock:
        fallback = self.state.fallback_manifest

        if fallback is None:
            return None

        require(
            self.state.pending_promotion is None,
            "cannot release fallback during promotion",
        )

        current = self.state.committed_manifest

        require(
            current is not None,
            "committed manifest missing",
        )

        require(
            fallback.manifest_sequence
            < current.manifest_sequence,
            "fallback manifest sequence is not older",
        )

        released = copy.deepcopy(
            fallback
        )

        self.state.fallback_manifest = None

        self._append_wal(
            "FALLBACK_MANIFEST_RELEASED",
            {
                "manifest_id": (
                    released.manifest_id
                ),
                "manifest_sequence": (
                    released.manifest_sequence
                ),
                "checkpoint_slot": (
                    released.checkpoint_slot
                ),
            },
        )

        return released


N33Engine.release_fallback_manifest = (
    _n33_release_fallback_manifest
)


# ============================================================================
# RESTORE ENGINE FROM DURABLE STATE
# ============================================================================

def _n33_restore_state(
    cls: Any,
    state: DurableState,
) -> N33Engine:
    engine = cls.__new__(cls)

    engine._lock = threading.RLock()

    engine.state = copy.deepcopy(
        state
    )

    engine.validate_wal()

    return engine


N33Engine.restore_state = classmethod(
    _n33_restore_state
)


# ============================================================================
# RESTART-SAFE PENDING PROMOTION RECOVERY
# ============================================================================

def _n33_recover_pending_promotion(
    self: N33Engine,
) -> Optional[CommittedManifest]:
    with self._lock:
        intent = self.state.pending_promotion

        if intent is None:
            return None

        intent.validate_shape()
        intent.validate_seal()

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
            intent.promotion_id
            not in self.state.finalized_promotion_ids,
            "promotion intent already finalized",
        )

        if intent.state == PROMOTION_PENDING:
            self.validate_promotion_intent(
                copy.deepcopy(intent)
            )

            self.validate_promotion_source(
                copy.deepcopy(intent)
            )

            committed = self.commit_manifest_promotion(
                copy.deepcopy(intent)
            )

            committed_intent = copy.deepcopy(
                self.state.pending_promotion
            )

            require(
                committed_intent is not None,
                "committed promotion intent missing",
            )

            self.finalize_manifest_promotion(
                committed_intent
            )

            return committed

        if intent.state == PROMOTION_COMMITTED:
            self.validate_promotion_intent(
                copy.deepcopy(intent)
            )

            self.validate_promotion_source(
                copy.deepcopy(intent)
            )

            manifest = copy.deepcopy(
                self.state.committed_manifest
            )

            require(
                manifest is not None,
                "committed manifest missing",
            )

            self.finalize_manifest_promotion(
                copy.deepcopy(intent)
            )

            return manifest

        raise LocalBlock(
            "promotion intent is not recoverable"
        )


N33Engine.recover_pending_promotion = (
    _n33_recover_pending_promotion
)


# ============================================================================
# COMMITTED AUTHORITY RECOVERY
# ============================================================================

def _n33_recover_committed_authority(
    self: N33Engine,
) -> Checkpoint:
    with self._lock:
        manifest = self.state.committed_manifest

        require(
            manifest is not None,
            "committed manifest missing",
        )

        self.validate_manifest(
            manifest
        )

        checkpoint = self.get_checkpoint(
            manifest.checkpoint_slot
        )

        self.validate_checkpoint(
            checkpoint
        )

        require(
            checkpoint.checkpoint_id
            == manifest.checkpoint_id,
            "manifest checkpoint identity mismatch",
        )

        require(
            checkpoint.checkpoint_sequence
            == manifest.checkpoint_sequence,
            "manifest checkpoint sequence mismatch",
        )

        return copy.deepcopy(
            checkpoint
        )


N33Engine.recover_committed_authority = (
    _n33_recover_committed_authority
)


# ============================================================================
# GENERATION ADVANCE
# ============================================================================

def _n33_advance_generation(
    self: N33Engine,
) -> Tuple[int, str, int]:
    with self._lock:
        require(
            self.state.pending_promotion is None,
            "cannot advance generation with pending promotion",
        )

        old_generation = self.state.generation
        old_lineage = self.state.lineage
        old_epoch = self.state.recovery_epoch

        self.state.generation += 1
        self.state.lineage = new_id("lineage")
        self.state.recovery_epoch += 1

        self.state.phase = PHASE_PREPARED

        self.state.recovery_lease = None
        self.state.authorization = None

        self.state.synthetic_dispatches = []

        self.state.checkpoints = {
            SLOT_A: None,
            SLOT_B: None,
        }

        self.state.committed_manifest = None
        self.state.fallback_manifest = None

        self.state.pending_promotion = None

        self.state.next_checkpoint_sequence = 1
        self.state.next_manifest_sequence = 1
        self.state.next_promotion_sequence = 1

        self.state.highest_committed_manifest_sequence = 0
        self.state.highest_committed_checkpoint_sequence = 0

        self._append_wal(
            "GENERATION_ADVANCED",
            {
                "prior_generation": old_generation,
                "prior_lineage": old_lineage,
                "prior_recovery_epoch": old_epoch,
                "new_generation": self.state.generation,
                "new_lineage": self.state.lineage,
                "new_recovery_epoch": (
                    self.state.recovery_epoch
                ),
            },
        )

        return (
            self.state.generation,
            self.state.lineage,
            self.state.recovery_epoch,
        )


N33Engine.advance_generation = (
    _n33_advance_generation
)


# ============================================================================
# COMPLETE CURRENT GENERATION
# ============================================================================

def _n33_complete_generation(
    self: N33Engine,
) -> None:
    with self._lock:
        require(
            len(self.state.synthetic_dispatches) == 1,
            "exactly one synthetic dispatch required",
        )

        dispatch = (
            self.state.synthetic_dispatches[0]
        )

        dispatch.validate_binding()

        self.state.phase = PHASE_COMPLETED

        if self.state.recovery_lease is not None:
            self.state.recovery_lease.active = False

        self._append_wal(
            "GENERATION_COMPLETED",
            {
                "dispatch_id": dispatch.dispatch_id,
                "synthetic_dispatch_count": 1,
            },
        )


N33Engine.complete_generation = (
    _n33_complete_generation
)


# ============================================================================
# FULL STATE VALIDATION
# ============================================================================

def _n33_validate_durable_state(
    self: N33Engine,
) -> None:
    with self._lock:
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
            "invalid lineage",
        )

        require(
            self.state.phase in {
                PHASE_PREPARED,
                PHASE_AUTHORIZED,
                PHASE_COMMITTED,
                PHASE_DISPATCHED,
                PHASE_COMPLETED,
            },
            "invalid durable phase",
        )

        for slot in VALID_SLOTS:
            checkpoint = (
                self.state.checkpoints.get(slot)
            )

            if checkpoint is not None:
                self.validate_checkpoint(
                    checkpoint
                )

                require(
                    checkpoint.slot == slot,
                    "checkpoint stored in wrong slot",
                )

        if self.state.committed_manifest is not None:
            self.validate_manifest(
                self.state.committed_manifest
            )

        if self.state.fallback_manifest is not None:
            fallback = (
                self.state.fallback_manifest
            )

            fallback.validate_shape()
            fallback.validate_seal()

            require(
                fallback.generation
                == self.state.generation,
                "fallback manifest generation mismatch",
            )

            require(
                fallback.lineage
                == self.state.lineage,
                "fallback manifest lineage mismatch",
            )

            require(
                fallback.recovery_epoch
                == self.state.recovery_epoch,
                "fallback manifest recovery epoch mismatch",
            )

            require(
                self.state.committed_manifest
                is not None,
                "fallback exists without committed manifest",
            )

            require(
                fallback.manifest_sequence
                < self.state.committed_manifest.manifest_sequence,
                "fallback manifest is not historical",
            )

            fallback_checkpoint = self.get_checkpoint(
                fallback.checkpoint_slot
            )

            self.validate_checkpoint(
                fallback_checkpoint
            )

            require(
                fallback_checkpoint.checkpoint_id
                == fallback.checkpoint_id,
                "fallback checkpoint identity mismatch",
            )

            require(
                fallback_checkpoint.checkpoint_sequence
                == fallback.checkpoint_sequence,
                "fallback checkpoint sequence mismatch",
            )

        if self.state.pending_promotion is not None:
            promotion = (
                self.state.pending_promotion
            )

            promotion.validate_shape()
            promotion.validate_seal()

            require(
                promotion.state in {
                    PROMOTION_PENDING,
                    PROMOTION_COMMITTED,
                },
                "invalid pending promotion state",
            )

        if self.state.authorization is not None:
            self.state.authorization.validate_seal()

        for dispatch in self.state.synthetic_dispatches:
            dispatch.validate_binding()


N33Engine.validate_durable_state = (
    _n33_validate_durable_state
)


# ============================================================================
# STATE SNAPSHOT
# ============================================================================

def snapshot_state(
    engine: N33Engine,
) -> DurableState:
    with engine._lock:
        engine.validate_durable_state()

        return engine.state.clone()


# ============================================================================
# INITIAL AUTHORITY BOOTSTRAP
# ============================================================================

def bootstrap_initial_authority(
    engine: N33Engine,
) -> Tuple[
    RecoveryLease,
    Authorization,
    SyntheticDispatch,
    Checkpoint,
    CommittedManifest,
]:
    lease = engine.acquire_recovery_lease(
        "n33-bootstrap-worker"
    )

    authorization = engine.authorize(
        lease
    )

    engine.consume_authorization(
        authorization,
        lease,
    )

    dispatch = engine.synthetic_dispatch(
        authorization,
        lease,
    )

    engine.complete_generation()

    checkpoint = engine.create_checkpoint(
        SLOT_A
    )

    manifest = engine.commit_initial_manifest(
        checkpoint
    )

    return (
        lease,
        authorization,
        dispatch,
        checkpoint,
        manifest,
    )


print(
    "R28 UNIT N.33: PART 2 DEFINITIONS LOADED",
    flush=True,
)

# ============================================================================
# END OF PART 2 OF 4
#
# NEXT:
#   PART 3 CONTINUES AT ZERO INDENTATION WITH:
#     - N.33 TEST HARNESS
#     - INITIAL AUTHORITY VALIDATION
#     - ROTATED CHECKPOINT CREATION
#     - DURABLE PROMOTION INTENT TESTS
#     - PRE-COMMIT CRASH RECOVERY
#     - POST-COMMIT / PRE-FINALIZATION RECOVERY
#     - PROMOTION TAMPER / STALE / REPLAY REJECTIONS
#
# DO NOT ADD OR REMOVE INDENTATION AT THE PART-2 / PART-3 JOINT.
# ============================================================================
# ============================================================================
# R28 UNIT N.33
# DURABLE MANIFEST PROMOTION INTENT + CRASH-WINDOW RECOVERY
# + STALE PROMOTION FENCING + SAFE SLOT RECLAMATION
#
# CORRECTED COPY/PASTE VERSION
# PART 3 OF 4
# ============================================================================


# ============================================================================
# TEST HARNESS HELPERS
# ============================================================================

def clone_engine(
    engine: N33Engine,
) -> N33Engine:
    return N33Engine.restore_state(
        snapshot_state(engine)
    )


def assert_true(
    condition: bool,
    label: str,
) -> None:
    if condition:
        pass_line(label)
        return

    fail_line(label)


def assert_equal(
    left: Any,
    right: Any,
    label: str,
) -> None:
    if left == right:
        pass_line(label)
        return

    fail_line(
        f"{label} "
        f"(left={left!r}, right={right!r})"
    )


def assert_not_equal(
    left: Any,
    right: Any,
    label: str,
) -> None:
    if left != right:
        pass_line(label)
        return

    fail_line(
        f"{label} "
        f"(both={left!r})"
    )


def assert_secure_equal(
    left: str,
    right: str,
    label: str,
) -> None:
    if secure_equal(left, right):
        pass_line(label)
        return

    fail_line(label)


# ============================================================================
# BUILD COMPLETED GENERATION WITH INITIAL SLOT-A AUTHORITY
# ============================================================================

def build_initial_authority_engine() -> Tuple[
    N33Engine,
    RecoveryLease,
    Authorization,
    SyntheticDispatch,
    Checkpoint,
    CommittedManifest,
]:
    engine = N33Engine()

    (
        lease,
        authorization,
        dispatch,
        checkpoint,
        manifest,
    ) = bootstrap_initial_authority(
        engine
    )

    engine.validate_wal()
    engine.validate_durable_state()

    return (
        engine,
        lease,
        authorization,
        dispatch,
        checkpoint,
        manifest,
    )


# ============================================================================
# CREATE ROTATED SLOT-B CHECKPOINT
# ============================================================================

def build_rotated_checkpoint(
    engine: N33Engine,
) -> Checkpoint:
    committed = engine.state.committed_manifest

    require(
        committed is not None,
        "committed manifest missing",
    )

    target_slot = opposite_slot(
        committed.checkpoint_slot
    )

    checkpoint = engine.create_checkpoint(
        target_slot
    )

    engine.validate_checkpoint(
        checkpoint
    )

    return checkpoint


# ============================================================================
# CREATE AND COMMIT NORMAL PROMOTION
# ============================================================================

def perform_normal_promotion(
    engine: N33Engine,
) -> Tuple[
    Checkpoint,
    ManifestPromotionIntent,
    CommittedManifest,
]:
    checkpoint = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint
    )

    engine.validate_promotion_intent(
        intent
    )

    manifest = engine.commit_manifest_promotion(
        intent
    )

    committed_intent = copy.deepcopy(
        engine.state.pending_promotion
    )

    require(
        committed_intent is not None,
        "committed promotion intent missing",
    )

    engine.finalize_manifest_promotion(
        committed_intent
    )

    return (
        checkpoint,
        intent,
        manifest,
    )


# ============================================================================
# TEST 1: INITIAL ENGINE STATE
# ============================================================================

def test_01_initial_engine_state() -> None:
    announce_test(
        1,
        "INITIAL ENGINE STATE",
    )

    engine = N33Engine()

    assert_equal(
        engine.state.generation,
        1,
        "Initial Generation Is One",
    )

    assert_equal(
        engine.state.recovery_epoch,
        1,
        "Initial Recovery Epoch Is One",
    )

    assert_equal(
        engine.state.phase,
        PHASE_PREPARED,
        "Initial Phase Is PREPARED",
    )

    assert_true(
        bool(engine.state.lineage),
        "Initial Lineage Established",
    )

    assert_equal(
        len(engine.state.wal),
        1,
        "Initial WAL Contains Bootstrap Record",
    )

    assert_secure_equal(
        engine.validate_wal(),
        engine.current_wal_final_hash(),
        "Initial WAL Chain Validates",
    )

    assert_secure_equal(
        LEVERAGE_PAYLOAD_HASH,
        sha256_json(LEVERAGE_PAYLOAD),
        "Payload Hash Established",
    )


# ============================================================================
# TEST 2: RECOVERY LEASE BINDING
# ============================================================================

def test_02_recovery_lease_binding() -> None:
    announce_test(
        2,
        "RECOVERY LEASE BINDING",
    )

    engine = N33Engine()

    lease = engine.acquire_recovery_lease(
        "n33-test-worker"
    )

    engine.validate_recovery_lease(
        lease
    )

    assert_equal(
        lease.generation,
        engine.state.generation,
        "Lease Bound To Current Generation",
    )

    assert_equal(
        lease.lineage,
        engine.state.lineage,
        "Lease Bound To Current Lineage",
    )

    assert_equal(
        lease.recovery_epoch,
        engine.state.recovery_epoch,
        "Lease Bound To Current Recovery Epoch",
    )

    assert_true(
        lease.active,
        "Recovery Lease Is Active",
    )

    assert_equal(
        lease.nonce,
        1,
        "Initial Recovery Lease Nonce Is One",
    )


# ============================================================================
# TEST 3: AUTHORIZATION BINDING
# ============================================================================

def test_03_authorization_binding() -> None:
    announce_test(
        3,
        "AUTHORIZATION BINDING",
    )

    engine = N33Engine()

    lease = engine.acquire_recovery_lease(
        "n33-auth-worker"
    )

    authorization = engine.authorize(
        lease
    )

    engine.validate_authorization(
        authorization,
        lease,
    )

    assert_equal(
        authorization.generation,
        engine.state.generation,
        "Authorization Bound To Generation",
    )

    assert_equal(
        authorization.lineage,
        engine.state.lineage,
        "Authorization Bound To Lineage",
    )

    assert_equal(
        authorization.recovery_epoch,
        engine.state.recovery_epoch,
        "Authorization Bound To Recovery Epoch",
    )

    assert_secure_equal(
        authorization.payload_hash,
        LEVERAGE_PAYLOAD_HASH,
        "Authorization Bound To Exact Payload Hash",
    )

    assert_true(
        authorization.consumed is False,
        "Authorization Initially Unconsumed",
    )


# ============================================================================
# TEST 4: AUTHORIZATION CONSUMPTION
# ============================================================================

def test_04_authorization_consumption() -> None:
    announce_test(
        4,
        "AUTHORIZATION CONSUMPTION",
    )

    engine = N33Engine()

    lease = engine.acquire_recovery_lease(
        "n33-consume-worker"
    )

    authorization = engine.authorize(
        lease
    )

    engine.consume_authorization(
        authorization,
        lease,
    )

    current = engine.state.authorization

    assert_true(
        current is not None,
        "Authorization Remains Durable",
    )

    assert_true(
        current is not None
        and current.consumed,
        "Authorization Consumed Exactly Once",
    )

    if current is not None:
        current.validate_seal()

        assert_secure_equal(
            current.seal,
            current.calculate_seal(),
            "Consumed Authorization Resealed",
        )


# ============================================================================
# TEST 5: EXACT SYNTHETIC DISPATCH
# ============================================================================

def test_05_exact_synthetic_dispatch() -> None:
    announce_test(
        5,
        "EXACT SYNTHETIC DISPATCH",
    )

    engine = N33Engine()

    lease = engine.acquire_recovery_lease(
        "n33-dispatch-worker"
    )

    authorization = engine.authorize(
        lease
    )

    engine.consume_authorization(
        authorization,
        lease,
    )

    dispatch = engine.synthetic_dispatch(
        authorization,
        lease,
    )

    dispatch.validate_binding()

    assert_equal(
        dispatch.method,
        HTTP_METHOD,
        "Transport Method Exactly POST",
    )

    assert_equal(
        dispatch.path,
        LEVERAGE_ENDPOINT,
        "Transport Path Exactly Leverage Endpoint",
    )

    assert_equal(
        dispatch.payload,
        LEVERAGE_PAYLOAD,
        "Transport Payload Preserved Exactly",
    )

    assert_secure_equal(
        dispatch.payload_hash,
        LEVERAGE_PAYLOAD_HASH,
        "Transport Payload Hash Preserved",
    )

    assert_true(
        dispatch.transmitted is False,
        "Dispatch Was Never Transmitted",
    )

    assert_equal(
        len(engine.state.synthetic_dispatches),
        1,
        "Exactly One Synthetic Dispatch Exists",
    )


# ============================================================================
# TEST 6: INITIAL CHECKPOINT AUTHORITY
# ============================================================================

def test_06_initial_checkpoint_authority() -> None:
    announce_test(
        6,
        "INITIAL CHECKPOINT AUTHORITY",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint,
        manifest,
    ) = build_initial_authority_engine()

    engine.validate_checkpoint(
        checkpoint
    )

    engine.validate_manifest(
        manifest
    )

    assert_equal(
        checkpoint.slot,
        SLOT_A,
        "Initial Checkpoint Uses Slot A",
    )

    assert_equal(
        manifest.checkpoint_slot,
        SLOT_A,
        "Initial Manifest Points To Slot A",
    )

    assert_equal(
        checkpoint.checkpoint_id,
        manifest.checkpoint_id,
        "Manifest Checkpoint Identity Preserved",
    )

    assert_equal(
        checkpoint.checkpoint_sequence,
        manifest.checkpoint_sequence,
        "Manifest Checkpoint Sequence Preserved",
    )

    assert_equal(
        manifest.manifest_sequence,
        1,
        "Initial Manifest Sequence Is One",
    )

    assert_equal(
        engine.state.highest_committed_manifest_sequence,
        1,
        "Manifest High-Watermark Established",
    )

    assert_equal(
        engine.state.highest_committed_checkpoint_sequence,
        checkpoint.checkpoint_sequence,
        "Checkpoint High-Watermark Established",
    )


# ============================================================================
# TEST 7: ROTATED CHECKPOINT CREATION
# ============================================================================

def test_07_rotated_checkpoint_creation() -> None:
    announce_test(
        7,
        "ROTATED CHECKPOINT CREATION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    assert_equal(
        checkpoint_a.slot,
        SLOT_A,
        "Committed Authority Initially Uses Slot A",
    )

    assert_equal(
        manifest_a.checkpoint_slot,
        SLOT_A,
        "Initial Manifest Uses Slot A",
    )

    assert_equal(
        checkpoint_b.slot,
        SLOT_B,
        "Rotated Checkpoint Uses Slot B",
    )

    assert_true(
        checkpoint_b.checkpoint_sequence
        > checkpoint_a.checkpoint_sequence,
        "Checkpoint Sequence Advanced",
    )

    assert_true(
        checkpoint_b.wal_length
        >= checkpoint_a.wal_length,
        "Rotated Checkpoint WAL Boundary Did Not Regress",
    )

    assert_secure_equal(
        engine.validate_wal(
            checkpoint_b.wal_length
        ),
        checkpoint_b.wal_final_hash,
        "Rotated Checkpoint Historical WAL Prefix Validates",
    )


# ============================================================================
# TEST 8: DURABLE PROMOTION INTENT CREATION
# ============================================================================

def test_08_durable_promotion_intent_creation() -> None:
    announce_test(
        8,
        "DURABLE PROMOTION INTENT CREATION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    engine.validate_promotion_intent(
        intent
    )

    assert_equal(
        intent.state,
        PROMOTION_PENDING,
        "Promotion Intent Is PENDING",
    )

    assert_equal(
        intent.source_manifest_id,
        manifest_a.manifest_id,
        "Promotion Bound To Source Manifest Identity",
    )

    assert_equal(
        intent.source_manifest_sequence,
        manifest_a.manifest_sequence,
        "Promotion Bound To Source Manifest Sequence",
    )

    assert_equal(
        intent.source_slot,
        checkpoint_a.slot,
        "Promotion Bound To Source Slot",
    )

    assert_equal(
        intent.target_slot,
        checkpoint_b.slot,
        "Promotion Bound To Target Slot",
    )

    assert_equal(
        intent.target_checkpoint_id,
        checkpoint_b.checkpoint_id,
        "Promotion Bound To Target Checkpoint Identity",
    )

    assert_equal(
        intent.target_checkpoint_sequence,
        checkpoint_b.checkpoint_sequence,
        "Promotion Bound To Target Checkpoint Sequence",
    )

    assert_secure_equal(
        intent.target_wal_final_hash,
        checkpoint_b.wal_final_hash,
        "Promotion Bound To Target WAL Hash",
    )

    assert_true(
        engine.state.pending_promotion is not None,
        "Promotion Intent Persisted Durably",
    )


# ============================================================================
# TEST 9: PROMOTION INTENT SURVIVES RESTART
# ============================================================================

def test_09_promotion_intent_survives_restart() -> None:
    announce_test(
        9,
        "PROMOTION INTENT SURVIVES RESTART",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    snapshot = snapshot_state(
        engine
    )

    restarted = N33Engine.restore_state(
        snapshot
    )

    restarted.validate_durable_state()

    restored_intent = (
        restarted.state.pending_promotion
    )

    assert_true(
        restored_intent is not None,
        "Pending Promotion Intent Survives Restart",
    )

    assert_equal(
        restored_intent.promotion_id
        if restored_intent is not None
        else None,
        intent.promotion_id,
        "Promotion Identity Survives Restart",
    )

    assert_equal(
        restored_intent.target_checkpoint_id
        if restored_intent is not None
        else None,
        checkpoint_b.checkpoint_id,
        "Promotion Checkpoint Binding Survives Restart",
    )

    if restored_intent is not None:
        restored_intent.validate_seal()

        assert_secure_equal(
            restored_intent.seal,
            restored_intent.calculate_seal(),
            "Restarted Promotion Seal Validates",
        )


# ============================================================================
# TEST 10: PRE-COMMIT CRASH PROMOTION RECOVERY
# ============================================================================

def test_10_pre_commit_crash_recovery() -> None:
    announce_test(
        10,
        "PRE-COMMIT PROMOTION CRASH RECOVERY",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    crash_snapshot = snapshot_state(
        engine
    )

    restarted = N33Engine.restore_state(
        crash_snapshot
    )

    recovered_manifest = (
        restarted.recover_pending_promotion()
    )

    assert_true(
        recovered_manifest is not None,
        "Pending Promotion Commits After Restart",
    )

    assert_equal(
        recovered_manifest.checkpoint_slot
        if recovered_manifest is not None
        else None,
        SLOT_B,
        "Recovered Promotion Commits Slot B",
    )

    assert_equal(
        restarted.state.pending_promotion,
        None,
        "Recovered Promotion Finalized",
    )

    assert_equal(
        restarted.state.committed_manifest.checkpoint_id
        if restarted.state.committed_manifest
        else None,
        checkpoint_b.checkpoint_id,
        "Recovered Authority Uses Target Checkpoint",
    )

    assert_equal(
        restarted.state.fallback_manifest.manifest_id
        if restarted.state.fallback_manifest
        else None,
        manifest_a.manifest_id,
        "Prior Manifest Preserved As Fallback",
    )

    assert_equal(
        restarted.state.fallback_manifest.checkpoint_id
        if restarted.state.fallback_manifest
        else None,
        checkpoint_a.checkpoint_id,
        "Fallback Preserves Prior Checkpoint",
    )

    assert_true(
        intent.promotion_id
        in restarted.state.finalized_promotion_ids,
        "Recovered Promotion Recorded As Finalized",
    )

    restarted.validate_durable_state()


# ============================================================================
# TEST 11: POST-COMMIT / PRE-FINALIZATION CRASH RECOVERY
# ============================================================================

def test_11_post_commit_pre_finalize_recovery() -> None:
    announce_test(
        11,
        "POST-COMMIT / PRE-FINALIZATION CRASH RECOVERY",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    committed_manifest = (
        engine.commit_manifest_promotion(
            intent
        )
    )

    pending = engine.state.pending_promotion

    assert_true(
        pending is not None,
        "Committed Promotion Intent Remains Pending Finalization",
    )

    assert_equal(
        pending.state if pending is not None else None,
        PROMOTION_COMMITTED,
        "Promotion State Is COMMITTED Before Finalization",
    )

    crash_snapshot = snapshot_state(
        engine
    )

    restarted = N33Engine.restore_state(
        crash_snapshot
    )

    recovered = (
        restarted.recover_pending_promotion()
    )

    assert_true(
        recovered is not None,
        "Committed Promotion Recovered After Restart",
    )

    assert_equal(
        recovered.manifest_id
        if recovered is not None
        else None,
        committed_manifest.manifest_id,
        "Recovery Preserved Already-Committed Manifest Identity",
    )

    assert_equal(
        restarted.state.committed_manifest.manifest_id
        if restarted.state.committed_manifest
        else None,
        committed_manifest.manifest_id,
        "Committed Authority Was Not Duplicated",
    )

    assert_equal(
        restarted.state.fallback_manifest.manifest_id
        if restarted.state.fallback_manifest
        else None,
        manifest_a.manifest_id,
        "Fallback Manifest Remains Original Authority",
    )

    assert_equal(
        restarted.state.pending_promotion,
        None,
        "Committed Promotion Finalization Completed",
    )

    assert_true(
        intent.promotion_id
        in restarted.state.finalized_promotion_ids,
        "Committed Promotion Finalized Exactly Once",
    )


# ============================================================================
# TEST 12: NORMAL PROMOTION COMMIT
# ============================================================================

def test_12_normal_promotion_commit() -> None:
    announce_test(
        12,
        "NORMAL MANIFEST PROMOTION COMMIT",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    (
        checkpoint_b,
        intent,
        manifest_b,
    ) = perform_normal_promotion(
        engine
    )

    assert_equal(
        manifest_b.checkpoint_slot,
        SLOT_B,
        "New Committed Manifest Uses Slot B",
    )

    assert_equal(
        manifest_b.checkpoint_id,
        checkpoint_b.checkpoint_id,
        "New Manifest Uses Rotated Checkpoint",
    )

    assert_true(
        manifest_b.manifest_sequence
        > manifest_a.manifest_sequence,
        "Manifest Sequence Advanced Monotonically",
    )

    assert_true(
        manifest_b.checkpoint_sequence
        > checkpoint_a.checkpoint_sequence,
        "Committed Checkpoint Sequence Advanced Monotonically",
    )

    assert_equal(
        manifest_b.previous_manifest_id,
        manifest_a.manifest_id,
        "Manifest Preserves Prior Manifest Identity",
    )

    assert_equal(
        manifest_b.previous_manifest_sequence,
        manifest_a.manifest_sequence,
        "Manifest Preserves Prior Manifest Sequence",
    )

    assert_true(
        intent.promotion_id
        in engine.state.finalized_promotion_ids,
        "Promotion Finalization Recorded",
    )

    assert_equal(
        engine.state.pending_promotion,
        None,
        "No Pending Promotion Remains",
    )

    engine.validate_durable_state()


# ============================================================================
# TEST 13: FALLBACK AUTHORITY PRESERVED
# ============================================================================

def test_13_fallback_authority_preserved() -> None:
    announce_test(
        13,
        "FALLBACK AUTHORITY PRESERVATION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    (
        _checkpoint_b,
        _intent,
        manifest_b,
    ) = perform_normal_promotion(
        engine
    )

    fallback = engine.state.fallback_manifest

    assert_true(
        fallback is not None,
        "Fallback Manifest Exists",
    )

    assert_equal(
        fallback.manifest_id
        if fallback is not None
        else None,
        manifest_a.manifest_id,
        "Fallback Manifest Identity Preserved",
    )

    assert_equal(
        fallback.checkpoint_id
        if fallback is not None
        else None,
        checkpoint_a.checkpoint_id,
        "Fallback Checkpoint Identity Preserved",
    )

    assert_equal(
        fallback.checkpoint_slot
        if fallback is not None
        else None,
        SLOT_A,
        "Fallback Authority Uses Slot A",
    )

    assert_equal(
        engine.state.committed_manifest.manifest_id
        if engine.state.committed_manifest
        else None,
        manifest_b.manifest_id,
        "Active Authority Uses New Manifest",
    )

    assert_equal(
        engine.state.committed_manifest.checkpoint_slot
        if engine.state.committed_manifest
        else None,
        SLOT_B,
        "Active Authority Uses Slot B",
    )


# ============================================================================
# TEST 14: PROMOTION INTENT INTEGRITY TAMPER REJECTION
# ============================================================================

def test_14_promotion_intent_tamper_rejection() -> None:
    announce_test(
        14,
        "PROMOTION INTENT INTEGRITY TAMPER REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    forged = copy.deepcopy(
        intent
    )

    forged.target_checkpoint_sequence += 1

    expect_local_block(
        "Tampered Promotion Intent Rejected",
        "promotion intent integrity seal mismatch",
        lambda: engine.validate_promotion_intent(
            forged
        ),
    )


# ============================================================================
# TEST 15: PROMOTION TARGET SLOT TAMPER REJECTION
# ============================================================================

def test_15_promotion_target_slot_tamper_rejection() -> None:
    announce_test(
        15,
        "PROMOTION TARGET SLOT TAMPER REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    forged = copy.deepcopy(
        intent
    )

    forged.target_slot = SLOT_A

    forged.reseal()

    expect_local_block(
        "Promotion Target Slot Mismatch Rejected",
        "promotion target slot mismatch",
        lambda: engine.validate_promotion_intent(
            forged
        ),
    )


# ============================================================================
# TEST 16: PROMOTION CHECKPOINT IDENTITY TAMPER REJECTION
# ============================================================================

def test_16_promotion_checkpoint_identity_rejection() -> None:
    announce_test(
        16,
        "PROMOTION CHECKPOINT IDENTITY TAMPER REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    forged = copy.deepcopy(
        intent
    )

    forged.target_checkpoint_id = new_id(
        "forged-checkpoint"
    )

    forged.reseal()

    expect_local_block(
        "Promotion Checkpoint Identity Mismatch Rejected",
        "promotion checkpoint identity mismatch",
        lambda: engine.validate_promotion_intent(
            forged
        ),
    )


# ============================================================================
# TEST 17: PROMOTION WAL HASH TAMPER REJECTION
# ============================================================================

def test_17_promotion_wal_hash_tamper_rejection() -> None:
    announce_test(
        17,
        "PROMOTION WAL HASH TAMPER REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    forged = copy.deepcopy(
        intent
    )

    forged.target_wal_final_hash = "f" * 64

    forged.reseal()

    expect_local_block(
        "Promotion WAL Hash Mismatch Rejected",
        "promotion WAL final hash mismatch",
        lambda: engine.validate_promotion_intent(
            forged
        ),
    )


# ============================================================================
# TEST 18: STALE PROMOTION GENERATION REJECTION
# ============================================================================

def test_18_stale_promotion_generation_rejection() -> None:
    announce_test(
        18,
        "STALE PROMOTION GENERATION REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    forged = copy.deepcopy(
        intent
    )

    forged.generation += 1

    forged.reseal()

    expect_local_block(
        "Wrong Generation Promotion Rejected",
        "promotion intent generation mismatch",
        lambda: engine.validate_promotion_intent(
            forged
        ),
    )


# ============================================================================
# TEST 19: STALE PROMOTION LINEAGE REJECTION
# ============================================================================

def test_19_stale_promotion_lineage_rejection() -> None:
    announce_test(
        19,
        "STALE PROMOTION LINEAGE REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    forged = copy.deepcopy(
        intent
    )

    forged.lineage = new_id(
        "forged-lineage"
    )

    forged.reseal()

    expect_local_block(
        "Wrong Lineage Promotion Rejected",
        "promotion intent lineage mismatch",
        lambda: engine.validate_promotion_intent(
            forged
        ),
    )


# ============================================================================
# TEST 20: STALE PROMOTION RECOVERY EPOCH REJECTION
# ============================================================================

def test_20_stale_promotion_epoch_rejection() -> None:
    announce_test(
        20,
        "STALE PROMOTION RECOVERY EPOCH REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    forged = copy.deepcopy(
        intent
    )

    forged.recovery_epoch += 1

    forged.reseal()

    expect_local_block(
        "Wrong Recovery Epoch Promotion Rejected",
        "promotion intent recovery epoch mismatch",
        lambda: engine.validate_promotion_intent(
            forged
        ),
    )


# ============================================================================
# TEST 21: PROMOTION SOURCE MANIFEST FENCING
# ============================================================================

def test_21_promotion_source_manifest_fencing() -> None:
    announce_test(
        21,
        "PROMOTION SOURCE MANIFEST FENCING",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    current_manifest = (
        engine.state.committed_manifest
    )

    require(
        current_manifest is not None,
        "committed manifest missing",
    )

    forged_manifest = copy.deepcopy(
        current_manifest
    )

    forged_manifest.manifest_id = new_id(
        "replacement-manifest"
    )

    forged_manifest.reseal()

    engine.state.committed_manifest = (
        forged_manifest
    )

    expect_local_block(
        "Stale Promotion Source Manifest Rejected",
        "stale promotion source manifest",
        lambda: engine.validate_promotion_source(
            intent
        ),
    )


# ============================================================================
# TEST 22: PROMOTION REPLAY REJECTION
# ============================================================================

def test_22_promotion_replay_rejection() -> None:
    announce_test(
        22,
        "PROMOTION REPLAY REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    engine.commit_manifest_promotion(
        intent
    )

    committed_intent = copy.deepcopy(
        engine.state.pending_promotion
    )

    require(
        committed_intent is not None,
        "committed promotion intent missing",
    )

    engine.finalize_manifest_promotion(
        committed_intent
    )

    expect_local_block(
        "Finalized Promotion Replay Rejected",
        "pending promotion missing",
        lambda: engine.commit_manifest_promotion(
            intent
        ),
    )


# ============================================================================
# TEST 23: SECOND CONCURRENT PROMOTION REJECTION
# ============================================================================

def test_23_second_pending_promotion_rejection() -> None:
    announce_test(
        23,
        "SECOND PENDING PROMOTION REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    engine.prepare_manifest_promotion(
        checkpoint_b
    )

    expect_local_block(
        "Second Pending Promotion Rejected",
        "manifest promotion already pending",
        lambda: engine.prepare_manifest_promotion(
            checkpoint_b
        ),
    )


# ============================================================================
# TEST 24: ACTIVE SLOT RECLAMATION REJECTION
# ============================================================================

def test_24_active_slot_reclamation_rejection() -> None:
    announce_test(
        24,
        "ACTIVE SLOT RECLAMATION REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    expect_local_block(
        "Active Checkpoint Slot Reclamation Rejected",
        "cannot reclaim active checkpoint slot",
        lambda: engine.reclaim_checkpoint_slot(
            SLOT_A
        ),
    )


# ============================================================================
# TEST 25: FALLBACK SLOT RECLAMATION REJECTION
# ============================================================================

def test_25_fallback_slot_reclamation_rejection() -> None:
    announce_test(
        25,
        "FALLBACK SLOT RECLAMATION REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    perform_normal_promotion(
        engine
    )

    assert_equal(
        engine.state.committed_manifest.checkpoint_slot
        if engine.state.committed_manifest
        else None,
        SLOT_B,
        "Active Authority Rotated To Slot B",
    )

    assert_equal(
        engine.state.fallback_manifest.checkpoint_slot
        if engine.state.fallback_manifest
        else None,
        SLOT_A,
        "Fallback Authority Retains Slot A",
    )

    expect_local_block(
        "Fallback Checkpoint Slot Reclamation Rejected",
        "cannot reclaim fallback checkpoint slot",
        lambda: engine.reclaim_checkpoint_slot(
            SLOT_A
        ),
    )


# ============================================================================
# TEST 26: SAFE FALLBACK RELEASE AND SLOT RECLAMATION
# ============================================================================

def test_26_safe_fallback_release_and_reclamation() -> None:
    announce_test(
        26,
        "SAFE FALLBACK RELEASE AND SLOT RECLAMATION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    perform_normal_promotion(
        engine
    )

    released = (
        engine.release_fallback_manifest()
    )

    assert_true(
        released is not None,
        "Fallback Manifest Released",
    )

    assert_equal(
        engine.state.fallback_manifest,
        None,
        "Fallback Authority Cleared After Release",
    )

    reclaimed_id = (
        engine.reclaim_checkpoint_slot(
            SLOT_A
        )
    )

    assert_equal(
        reclaimed_id,
        checkpoint_a.checkpoint_id,
        "Released Historical Checkpoint Reclaimed",
    )

    assert_equal(
        engine.state.checkpoints[SLOT_A],
        None,
        "Reclaimed Slot A Is Empty",
    )

    assert_true(
        checkpoint_a.checkpoint_id
        in engine.state.reclaimed_checkpoint_ids,
        "Reclaimed Checkpoint Identity Fenced",
    )

    assert_true(
        engine.state.committed_manifest is not None
        and engine.state.committed_manifest.checkpoint_slot
        == SLOT_B,
        "Active Slot B Authority Preserved",
    )


# ============================================================================
# TEST 27: RECLAIMED CHECKPOINT IDENTITY REJECTION
# ============================================================================

def test_27_reclaimed_checkpoint_identity_rejection() -> None:
    announce_test(
        27,
        "RECLAIMED CHECKPOINT IDENTITY REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    perform_normal_promotion(
        engine
    )

    engine.release_fallback_manifest()

    engine.reclaim_checkpoint_slot(
        SLOT_A
    )

    expect_local_block(
        "Reclaimed Checkpoint Identity Rejected",
        "checkpoint has been reclaimed",
        lambda: engine.validate_checkpoint(
            checkpoint_a
        ),
    )


# ============================================================================
# TEST 28: COMMITTED AUTHORITY SURVIVES RESTART
# ============================================================================

def test_28_committed_authority_survives_restart() -> None:
    announce_test(
        28,
        "COMMITTED AUTHORITY SURVIVES RESTART",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    (
        checkpoint_b,
        _intent,
        manifest_b,
    ) = perform_normal_promotion(
        engine
    )

    snapshot = snapshot_state(
        engine
    )

    restarted = N33Engine.restore_state(
        snapshot
    )

    recovered_checkpoint = (
        restarted.recover_committed_authority()
    )

    assert_equal(
        restarted.state.committed_manifest.manifest_id
        if restarted.state.committed_manifest
        else None,
        manifest_b.manifest_id,
        "Committed Manifest Survives Restart",
    )

    assert_equal(
        recovered_checkpoint.checkpoint_id,
        checkpoint_b.checkpoint_id,
        "Committed Checkpoint Survives Restart",
    )

    assert_equal(
        recovered_checkpoint.slot,
        SLOT_B,
        "Restarted Authority Uses Slot B",
    )

    assert_secure_equal(
        restarted.validate_wal(
            recovered_checkpoint.wal_length
        ),
        recovered_checkpoint.wal_final_hash,
        "Restarted Historical WAL Prefix Validates",
    )


# ============================================================================
# TEST 29: COMMITTED MANIFEST SEQUENCE ROLLBACK REJECTION
# ============================================================================

def test_29_manifest_sequence_rollback_rejection() -> None:
    announce_test(
        29,
        "COMMITTED MANIFEST SEQUENCE ROLLBACK REJECTION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    perform_normal_promotion(
        engine
    )

    expect_local_block(
        "Rolled-Back Manifest Sequence Rejected",
        "committed manifest sequence rollback detected",
        lambda: engine.validate_manifest(
            manifest_a
        ),
    )


# ============================================================================
# TEST 30: HISTORICAL WAL PREFIX PRESERVATION
# ============================================================================

def test_30_historical_wal_prefix_preservation() -> None:
    announce_test(
        30,
        "HISTORICAL WAL PREFIX PRESERVATION",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    (
        checkpoint_b,
        _intent,
        _manifest_b,
    ) = perform_normal_promotion(
        engine
    )

    hash_a = engine.validate_wal(
        checkpoint_a.wal_length
    )

    hash_b = engine.validate_wal(
        checkpoint_b.wal_length
    )

    assert_secure_equal(
        hash_a,
        checkpoint_a.wal_final_hash,
        "Historical Slot A WAL Prefix Still Validates",
    )

    assert_secure_equal(
        hash_b,
        checkpoint_b.wal_final_hash,
        "Historical Slot B WAL Prefix Validates",
    )

    assert_true(
        checkpoint_b.wal_length
        >= checkpoint_a.wal_length,
        "Checkpoint WAL Boundary Is Monotonic",
    )


# ============================================================================
# TEST 31: GENERATION ADVANCE AFTER AUTHORITY RELEASE
# ============================================================================

def test_31_generation_advance() -> None:
    announce_test(
        31,
        "GENERATION ADVANCE",
    )

    (
        engine,
        lease,
        _authorization,
        _dispatch,
        _checkpoint_a,
        _manifest_a,
    ) = build_initial_authority_engine()

    perform_normal_promotion(
        engine
    )

    old_generation = (
        engine.state.generation
    )

    old_lineage = (
        engine.state.lineage
    )

    old_epoch = (
        engine.state.recovery_epoch
    )

    new_generation, new_lineage, new_epoch = (
        engine.advance_generation()
    )

    assert_true(
        new_generation > old_generation,
        "Generation Advanced Monotonically",
    )

    assert_true(
        new_epoch > old_epoch,
        "Recovery Epoch Advanced Monotonically",
    )

    assert_not_equal(
        new_lineage,
        old_lineage,
        "New Generation Uses Different Lineage",
    )

    assert_equal(
        engine.state.phase,
        PHASE_PREPARED,
        "New Generation Returns To PREPARED",
    )

    expect_local_block(
        "Prior Generation Lease Rejected",
        "recovery lease missing",
        lambda: engine.validate_recovery_lease(
            lease
        ),
    )


# ============================================================================
# TEST 32: STALE LEASE GENERATION REJECTION
# ============================================================================

def test_32_stale_lease_generation_rejection() -> None:
    announce_test(
        32,
        "ANTI-ABA STALE LEASE REJECTION",
    )

    engine = N33Engine()

    lease = engine.acquire_recovery_lease(
        "n33-old-worker"
    )

    engine.state.recovery_lease.active = False

    engine.state.generation += 1
    engine.state.lineage = new_id(
        "lineage"
    )
    engine.state.recovery_epoch += 1

    replacement = RecoveryLease(
        lease_id=new_id("lease"),
        generation=engine.state.generation,
        lineage=engine.state.lineage,
        recovery_epoch=engine.state.recovery_epoch,
        owner="n33-new-worker",
        nonce=lease.nonce + 1,
        active=True,
    )

    engine.state.recovery_lease = replacement

    expect_local_block(
        "Prior Generation Lease Rejected",
        "recovery lease generation mismatch",
        lambda: engine.validate_recovery_lease(
            lease
        ),
    )


# ============================================================================
# TEST 33: AUTHORIZATION REPLAY REJECTION
# ============================================================================

def test_33_authorization_replay_rejection() -> None:
    announce_test(
        33,
        "AUTHORIZATION REPLAY REJECTION",
    )

    engine = N33Engine()

    lease = engine.acquire_recovery_lease(
        "n33-replay-worker"
    )

    authorization = engine.authorize(
        lease
    )

    engine.consume_authorization(
        authorization,
        lease,
    )

    expect_local_block(
        "Consumed Authorization Replay Rejected",
        "authorization already consumed",
        lambda: engine.consume_authorization(
            authorization,
            lease,
        ),
    )


# ============================================================================
# TEST 34: FINAL EXACT SYNTHETIC TRANSPORT BINDING
# ============================================================================

def test_34_exact_synthetic_transport_binding() -> None:
    announce_test(
        34,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    (
        engine,
        _lease,
        _authorization,
        dispatch,
        _checkpoint,
        _manifest,
    ) = build_initial_authority_engine()

    dispatch.validate_binding()

    assert_equal(
        dispatch.method,
        "POST",
        "Transport Method Exactly POST",
    )

    assert_equal(
        dispatch.path,
        LEVERAGE_ENDPOINT,
        "Transport Path Exactly Leverage Endpoint",
    )

    assert_secure_equal(
        dispatch.payload_hash,
        LEVERAGE_PAYLOAD_HASH,
        "Transport Payload Hash Preserved",
    )

    assert_true(
        dispatch.transmitted is False,
        "Dispatch Was Never Transmitted",
    )

    assert_equal(
        len(engine.state.synthetic_dispatches),
        1,
        "Exactly One Synthetic Dispatch Preserved",
    )


# ============================================================================
# TEST 35: FINAL NETWORK WRITE FIREBREAK
# ============================================================================

def test_35_final_network_write_firebreak() -> None:
    announce_test(
        35,
        "FINAL NETWORK WRITE FIREBREAK",
    )

    engine = N33Engine()

    assert_true(
        REAL_POST_ENABLED is False,
        "Real POST Disabled",
    )

    assert_true(
        DEMO_POST_ENABLED is False,
        "Demo POST Disabled",
    )

    assert_true(
        NETWORK_WRITES_ENABLED is False,
        "All Network Writes Disabled",
    )

    assert_true(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic Transport Only",
    )

    expect_local_block(
        "Real POST Firebreak Enforced",
        "real network POST is disabled",
        lambda: engine.real_network_post(
            LEVERAGE_ENDPOINT,
            LEVERAGE_PAYLOAD,
        ),
    )

    expect_local_block(
        "Demo POST Firebreak Enforced",
        "demo network POST is disabled",
        lambda: engine.demo_network_post(
            LEVERAGE_ENDPOINT,
            LEVERAGE_PAYLOAD,
        ),
    )


# ============================================================================
# TEST 36: FINAL N.33 COMMITTED AUTHORITY
# ============================================================================

def test_36_final_committed_authority() -> N33Engine:
    announce_test(
        36,
        "FINAL N.33 COMMITTED AUTHORITY",
    )

    (
        engine,
        _lease,
        _authorization,
        _dispatch,
        checkpoint_a,
        manifest_a,
    ) = build_initial_authority_engine()

    checkpoint_b = build_rotated_checkpoint(
        engine
    )

    intent = engine.prepare_manifest_promotion(
        checkpoint_b
    )

    committed_manifest = (
        engine.commit_manifest_promotion(
            intent
        )
    )

    committed_intent = copy.deepcopy(
        engine.state.pending_promotion
    )

    require(
        committed_intent is not None,
        "committed promotion intent missing",
    )

    engine.finalize_manifest_promotion(
        committed_intent
    )

    engine.validate_durable_state()

    recovered = (
        engine.recover_committed_authority()
    )

    assert_true(
        engine.state.committed_manifest is not None,
        "Committed Manifest Exists",
    )

    assert_equal(
        committed_manifest.manifest_sequence,
        2,
        "Committed Manifest Sequence Is Two",
    )

    assert_equal(
        committed_manifest.checkpoint_slot,
        SLOT_B,
        "Committed Authority Uses Rotated Slot B",
    )

    assert_equal(
        committed_manifest.checkpoint_id,
        checkpoint_b.checkpoint_id,
        "Committed Authority Uses Rotated Checkpoint",
    )

    assert_equal(
        committed_manifest.checkpoint_sequence,
        checkpoint_b.checkpoint_sequence,
        "Committed Checkpoint Sequence Preserved",
    )

    assert_equal(
        committed_manifest.generation,
        engine.state.generation,
        "Committed Authority Generation Preserved",
    )

    assert_equal(
        committed_manifest.lineage,
        engine.state.lineage,
        "Committed Authority Lineage Preserved",
    )

    assert_equal(
        committed_manifest.recovery_epoch,
        engine.state.recovery_epoch,
        "Committed Authority Recovery Epoch Preserved",
    )

    assert_equal(
        committed_manifest.wal_length,
        checkpoint_b.wal_length,
        "Committed Authority WAL Boundary Preserved",
    )

    assert_secure_equal(
        committed_manifest.wal_final_hash,
        checkpoint_b.wal_final_hash,
        "Committed Authority WAL Hash Preserved",
    )

    assert_secure_equal(
        engine.validate_wal(
            committed_manifest.wal_length
        ),
        committed_manifest.wal_final_hash,
        "Committed Authority Historical WAL Prefix Validates",
    )

    assert_equal(
        recovered.checkpoint_id,
        checkpoint_b.checkpoint_id,
        "Recovered Checkpoint Matches Manifest Identity",
    )

    assert_true(
        engine.state.fallback_manifest is not None,
        "Fallback Manifest Preserved",
    )

    assert_equal(
        engine.state.fallback_manifest.manifest_id
        if engine.state.fallback_manifest
        else None,
        manifest_a.manifest_id,
        "Fallback Manifest Is Original Manifest",
    )

    assert_equal(
        engine.state.fallback_manifest.checkpoint_id
        if engine.state.fallback_manifest
        else None,
        checkpoint_a.checkpoint_id,
        "Fallback Checkpoint Is Original Slot A Checkpoint",
    )

    assert_true(
        intent.promotion_id
        in engine.state.finalized_promotion_ids,
        "Promotion Identity Permanently Finalized",
    )

    assert_equal(
        engine.state.pending_promotion,
        None,
        "No Pending Promotion Remains",
    )

    assert_equal(
        len(engine.state.synthetic_dispatches),
        1,
        "Exactly One Synthetic Dispatch Preserved",
    )

    assert_true(
        engine.state.synthetic_dispatches[0].transmitted
        is False,
        "Final Dispatch Was Never Transmitted",
    )

    return engine


print(
    "R28 UNIT N.33: PART 3 DEFINITIONS LOADED",
    flush=True,
)

# ============================================================================
# END OF PART 3 OF 4
#
# NEXT:
#   PART 4 CONTINUES AT ZERO INDENTATION WITH:
#     - TEST EXECUTION ORDER
#     - FINAL DIAGNOSTIC SUMMARY
#     - HEALTH SERVER
#     - PERSISTENT SAFE RUNTIME
#     - __main__ ENTRY POINT
#
# DO NOT ADD OR REMOVE INDENTATION AT THE PART-3 / PART-4 JOINT.
# ============================================================================
# ============================================================================
# R28 UNIT N.33
# DURABLE MANIFEST PROMOTION INTENT + CRASH-WINDOW RECOVERY
# + STALE PROMOTION FENCING + SAFE SLOT RECLAMATION
#
# CORRECTED COPY/PASTE VERSION
# PART 4 OF 4
# ============================================================================


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_all_diagnostics() -> N33Engine:
    print("-" * 92, flush=True)
    print(
        "R28 UNIT N.33: STARTING DIAGNOSTICS",
        flush=True,
    )
    print("-" * 92, flush=True)

    test_01_initial_engine_state()
    test_02_recovery_lease_binding()
    test_03_authorization_binding()
    test_04_authorization_consumption()
    test_05_exact_synthetic_dispatch()
    test_06_initial_checkpoint_authority()
    test_07_rotated_checkpoint_creation()
    test_08_durable_promotion_intent_creation()
    test_09_promotion_intent_survives_restart()
    test_10_pre_commit_crash_recovery()
    test_11_post_commit_pre_finalize_recovery()
    test_12_normal_promotion_commit()
    test_13_fallback_authority_preserved()
    test_14_promotion_intent_tamper_rejection()
    test_15_promotion_target_slot_tamper_rejection()
    test_16_promotion_checkpoint_identity_rejection()
    test_17_promotion_wal_hash_tamper_rejection()
    test_18_stale_promotion_generation_rejection()
    test_19_stale_promotion_lineage_rejection()
    test_20_stale_promotion_epoch_rejection()
    test_21_promotion_source_manifest_fencing()
    test_22_promotion_replay_rejection()
    test_23_second_pending_promotion_rejection()
    test_24_active_slot_reclamation_rejection()
    test_25_fallback_slot_reclamation_rejection()
    test_26_safe_fallback_release_and_reclamation()
    test_27_reclaimed_checkpoint_identity_rejection()
    test_28_committed_authority_survives_restart()
    test_29_manifest_sequence_rollback_rejection()
    test_30_historical_wal_prefix_preservation()
    test_31_generation_advance()
    test_32_stale_lease_generation_rejection()
    test_33_authorization_replay_rejection()
    test_34_exact_synthetic_transport_binding()
    test_35_final_network_write_firebreak()

    final_engine = (
        test_36_final_committed_authority()
    )

    return final_engine


# ============================================================================
# FINAL DIAGNOSTIC SUMMARY
# ============================================================================

def print_diagnostic_summary(
    engine: N33Engine,
) -> None:
    print("-" * 92, flush=True)
    print(
        "R28 UNIT N.33 DIAGNOSTIC SUMMARY",
        flush=True,
    )
    print("-" * 92, flush=True)

    committed = (
        engine.state.committed_manifest
    )

    fallback = (
        engine.state.fallback_manifest
    )

    pending = (
        engine.state.pending_promotion
    )

    committed_slot = (
        committed.checkpoint_slot
        if committed is not None
        else "NONE"
    )

    committed_checkpoint_sequence = (
        committed.checkpoint_sequence
        if committed is not None
        else 0
    )

    committed_checkpoint_wal_length = (
        committed.wal_length
        if committed is not None
        else 0
    )

    committed_manifest_sequence = (
        committed.manifest_sequence
        if committed is not None
        else 0
    )

    fallback_manifest_sequence = (
        fallback.manifest_sequence
        if fallback is not None
        else 0
    )

    pending_state = (
        pending.state
        if pending is not None
        else "NONE"
    )

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
        f"{committed_slot}",
        flush=True,
    )

    print(
        f"Checkpoint Sequence:     "
        f"{committed_checkpoint_sequence}",
        flush=True,
    )

    print(
        f"Checkpoint WAL Length:   "
        f"{committed_checkpoint_wal_length}",
        flush=True,
    )

    print(
        f"Current WAL Length:      "
        f"{len(engine.state.wal)}",
        flush=True,
    )

    print(
        f"Manifest Sequence:       "
        f"{committed_manifest_sequence}",
        flush=True,
    )

    print(
        f"Fallback Manifest:       "
        f"{fallback_manifest_sequence}",
        flush=True,
    )

    print(
        f"Pending Promotion:       "
        f"{pending_state}",
        flush=True,
    )

    print(
        f"Finalized Promotions:    "
        f"{len(engine.state.finalized_promotion_ids)}",
        flush=True,
    )

    print(
        f"Reclaimed Checkpoints:   "
        f"{len(engine.state.reclaimed_checkpoint_ids)}",
        flush=True,
    )

    print(
        f"Synthetic Dispatches:    "
        f"{len(engine.state.synthetic_dispatches)}",
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

    print("-" * 92, flush=True)


# ============================================================================
# FINAL SAFETY VALIDATION
# ============================================================================

def final_safety_validation(
    engine: N33Engine,
) -> None:
    engine.validate_durable_state()

    require(
        REAL_POST_ENABLED is False,
        "real POST safety flag unexpectedly enabled",
    )

    require(
        DEMO_POST_ENABLED is False,
        "demo POST safety flag unexpectedly enabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "network writes unexpectedly enabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "synthetic-only safety flag unexpectedly disabled",
    )

    require(
        len(engine.state.synthetic_dispatches) == 1,
        "final synthetic dispatch count mismatch",
    )

    dispatch = (
        engine.state.synthetic_dispatches[0]
    )

    dispatch.validate_binding()

    require(
        dispatch.transmitted is False,
        "final synthetic dispatch was transmitted",
    )

    require(
        engine.state.committed_manifest is not None,
        "final committed manifest missing",
    )

    require(
        engine.state.pending_promotion is None,
        "final promotion remains pending",
    )

    committed = (
        engine.state.committed_manifest
    )

    require(
        committed.checkpoint_slot == SLOT_B,
        "final committed authority is not slot B",
    )

    require(
        committed.manifest_sequence == 2,
        "final committed manifest sequence mismatch",
    )

    require(
        committed.checkpoint_sequence == 2,
        "final committed checkpoint sequence mismatch",
    )

    engine.validate_manifest(
        committed
    )

    checkpoint = engine.get_checkpoint(
        committed.checkpoint_slot
    )

    engine.validate_checkpoint(
        checkpoint
    )

    require(
        checkpoint.checkpoint_id
        == committed.checkpoint_id,
        "final manifest/checkpoint identity mismatch",
    )

    require(
        checkpoint.checkpoint_sequence
        == committed.checkpoint_sequence,
        "final manifest/checkpoint sequence mismatch",
    )

    require(
        secure_equal(
            engine.validate_wal(
                committed.wal_length
            ),
            committed.wal_final_hash,
        ),
        "final committed historical WAL prefix mismatch",
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
                f"R28 UNIT N.33: "
                f"HEALTH SERVER LISTENING "
                f"ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"R28 UNIT N.33: "
                f"HEALTH SERVER ERROR: "
                f"{exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        name="n33-health-server",
        daemon=True,
    )

    thread.start()


# ============================================================================
# PERSISTENT SAFE RUNTIME
# ============================================================================

def enter_persistent_safe_runtime() -> None:
    print(
        "R28 UNIT N.33: "
        "ENTERING PERSISTENT SAFE RUNTIME",
        flush=True,
    )

    heartbeat = 0

    while True:
        heartbeat += 1

        print(
            f"R28 UNIT N.33: "
            f"HEARTBEAT {heartbeat}",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    try:
        final_engine = (
            run_all_diagnostics()
        )

        final_safety_validation(
            final_engine
        )

        print_diagnostic_summary(
            final_engine
        )

        print(
            "R28 UNIT N.33: "
            "ALL DIAGNOSTICS PASSED",
            flush=True,
        )

        print(
            "R28 UNIT N.33: "
            "NO REAL ORDER OR ACCOUNT MUTATION WAS SENT",
            flush=True,
        )

        print("-" * 92, flush=True)

        start_health_server()

        enter_persistent_safe_runtime()

    except ValidationFailure as exc:
        print("-" * 92, flush=True)

        print(
            "R28 UNIT N.33: "
            f"DIAGNOSTIC FAILURE: {exc}",
            flush=True,
        )

        print(
            "R28 UNIT N.33: "
            "NO REAL ORDER OR ACCOUNT MUTATION WAS SENT",
            flush=True,
        )

        print("-" * 92, flush=True)

        raise

    except LocalBlock as exc:
        print("-" * 92, flush=True)

        print(
            "R28 UNIT N.33 LOCAL BLOCK:",
            flush=True,
        )

        print(
            f"  {exc}",
            flush=True,
        )

        print(
            "R28 UNIT N.33: "
            "DIAGNOSTIC ABORTED SAFELY",
            flush=True,
        )

        print(
            "R28 UNIT N.33: "
            "NO REAL ORDER OR ACCOUNT MUTATION WAS SENT",
            flush=True,
        )

        print("-" * 92, flush=True)

        raise

    except KeyboardInterrupt:
        print(
            "R28 UNIT N.33: "
            "SAFE RUNTIME STOPPED",
            flush=True,
        )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()


# ============================================================================
# END OF R28 UNIT N.33
#
# EXPECTED SUCCESS TERMINAL:
#
#   R28 UNIT N.33: ALL DIAGNOSTICS PASSED
#   R28 UNIT N.33: NO REAL ORDER OR ACCOUNT MUTATION WAS SENT
#   R28 UNIT N.33: ENTERING PERSISTENT SAFE RUNTIME
#   R28 UNIT N.33: HEARTBEAT 1
#   R28 UNIT N.33: HEARTBEAT 2
#   ...
#
# N.33 SAFETY GUARANTEES:
#
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#   - EXACT POST METHOD BINDING
#   - EXACT LEVERAGE ENDPOINT BINDING
#   - EXACT PAYLOAD HASH BINDING
#   - AUTHORIZATION CONSUMED EXACTLY ONCE
#   - DURABLE DUAL-SLOT CHECKPOINT AUTHORITY
#   - COMMITTED MANIFEST HIGH-WATERMARK
#   - DURABLE MANIFEST PROMOTION INTENT
#   - PROMOTION INTENT INTEGRITY SEAL
#   - SOURCE MANIFEST FENCING
#   - TARGET CHECKPOINT FENCING
#   - GENERATION / LINEAGE / EPOCH FENCING
#   - PRE-COMMIT CRASH RECOVERY
#   - POST-COMMIT / PRE-FINALIZATION RECOVERY
#   - PROMOTION REPLAY REJECTION
#   - FALLBACK AUTHORITY PRESERVATION
#   - ACTIVE SLOT RECLAMATION REJECTION
#   - FALLBACK SLOT RECLAMATION REJECTION
#   - SAFE HISTORICAL SLOT RECLAMATION
#   - RECLAIMED CHECKPOINT IDENTITY FENCING
#   - HISTORICAL WAL PREFIX VALIDATION
#   - ANTI-ABA STALE LEASE REJECTION
#   - PERSISTENT HEALTH SERVER
#   - PERSISTENT SAFE HEARTBEAT RUNTIME
#
# ============================================================================
