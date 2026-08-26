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
