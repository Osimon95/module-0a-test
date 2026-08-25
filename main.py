# ============================================================================
# R28 UNIT N.27
# DURABLE WAL RECOVERY + CHECKPOINT BINDING + RESTART-SAFE FINALITY
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
# N.27 INCREMENT OVER N.26:
#   - DURABLE WAL + CHECKPOINT CROSS-BINDING
#   - WAL HEAD / TAIL INTEGRITY VALIDATION
#   - WAL HASH-CHAIN VALIDATION
#   - CHECKPOINT ↔ WAL FINAL HASH BINDING
#   - RESTART REPLAY VALIDATION
#   - TORN WAL TAIL REJECTION
#   - STALE CHECKPOINT REJECTION
#   - FINALITY PRESERVATION ACROSS RESTART
#   - EXACTLY-ONCE SYNTHETIC DISPATCH FENCING
#   - GENERATION / LINEAGE / RECOVERY-EPOCH BINDING
#   - HARD NETWORK-WRITE FIREBREAK
#
# IMPORTANT COPY/PASTE RULE:
#   PART 1 ENDS ONLY AT:
#
#       R28 UNIT N.27: PART 1 DEFINITIONS LOADED
#
#   PART 2 MUST BEGIN AT COLUMN ZERO.
# ============================================================================

print(
    "R28 UNIT N.27: MAIN.PY ENTERED",
    flush=True,
)

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


print(
    "R28 UNIT N.27: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.27"
UNIT_VERSION = "N.27"

SYMBOL = "BTCUSDT"
LEVERAGE = 100
MARGIN_MODE = "ISOLATED"

TRANSPORT_METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
LEVERAGE_TRANSMISSION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

HEALTH_PORT = int(
    os.environ.get(
        "PORT",
        "10000",
    )
)

STATE_SCHEMA_VERSION = 27
WAL_SCHEMA_VERSION = 27
CHECKPOINT_SCHEMA_VERSION = 27

DEFAULT_ACCOUNT_EPOCH = 1
DEFAULT_SYMBOL_EPOCH = 1
DEFAULT_POSITION_EPOCH = 1
DEFAULT_RECOVERY_EPOCH = 1
DEFAULT_GENERATION = 1

MAX_RECOVERY_ATTEMPTS = 64

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

TERMINAL_PHASES = {
    PHASE_COMPLETED,
    "REJECTED",
    "CANCELED",
    "FAILED",
    "EXPIRED",
}

NON_TERMINAL_PHASES = {
    PHASE_PREPARED,
    PHASE_AUTHORIZED,
    PHASE_COMMITTED,
    PHASE_DISPATCHED,
}

ALL_PHASES = (
    TERMINAL_PHASES
    | NON_TERMINAL_PHASES
)

SYNTHETIC_RECEIPT_STATUS = (
    "SYNTHETIC_NO_TRANSMISSION"
)

WAL_EVENT_PREPARED = "PREPARED"
WAL_EVENT_AUTHORIZED = "AUTHORIZED"
WAL_EVENT_COMMITTED = "COMMITTED"
WAL_EVENT_DISPATCHED = "DISPATCHED"
WAL_EVENT_COMPLETED = "COMPLETED"
WAL_EVENT_CHECKPOINT = "CHECKPOINT"

VALID_WAL_EVENTS = {
    WAL_EVENT_PREPARED,
    WAL_EVENT_AUTHORIZED,
    WAL_EVENT_COMMITTED,
    WAL_EVENT_DISPATCHED,
    WAL_EVENT_COMPLETED,
    WAL_EVENT_CHECKPOINT,
}

GENESIS_WAL_HASH = (
    hashlib.sha256(
        b"R28-N27-WAL-GENESIS"
    ).hexdigest()
)

INTEGRITY_KEY = (
    b"R28-N27-LOCAL-INTEGRITY-KEY"
)

CHECKPOINT_KEY = (
    b"R28-N27-CHECKPOINT-INTEGRITY-KEY"
)

CERTIFICATE_KEY = (
    b"R28-N27-RECOVERY-CERTIFICATE-KEY"
)


print(
    "R28 UNIT N.27: CONSTANTS INITIALIZED",
    flush=True,
)


# ============================================================================
# BASIC HELPERS
# ============================================================================

def now_ms() -> int:
    return int(
        time.time() * 1000
    )


def canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_json(
    value: Any,
) -> str:
    return sha256_text(
        canonical_json(
            value
        )
    )


def hmac_sha256(
    key: bytes,
    value: str,
) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def secure_id(
    prefix: str,
) -> str:
    return (
        f"{prefix}-"
        f"{uuid.uuid4().hex}"
    )


def deterministic_id(
    prefix: str,
    *parts: Any,
) -> str:
    raw = "|".join(
        str(part)
        for part in parts
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()

    return (
        f"{prefix}-"
        f"{digest[:32]}"
    )


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise ValueError(
            message
        )


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


def clone(
    value: Any,
) -> Any:
    return copy.deepcopy(
        value
    )


# ============================================================================
# EXACT LEVERAGE PAYLOAD
# ============================================================================

def build_exact_leverage_payload(
) -> Dict[str, str]:
    return {
        "leverage": str(
            LEVERAGE
        ),
        "marginMode": MARGIN_MODE,
        "symbol": SYMBOL,
    }


EXACT_LEVERAGE_PAYLOAD = (
    build_exact_leverage_payload()
)

EXACT_LEVERAGE_PAYLOAD_JSON = (
    canonical_json(
        EXACT_LEVERAGE_PAYLOAD
    )
)

EXACT_LEVERAGE_PAYLOAD_HASH = (
    sha256_text(
        EXACT_LEVERAGE_PAYLOAD_JSON
    )
)


# ============================================================================
# GENERATION FENCE
# ============================================================================

@dataclass(frozen=True)
class GenerationFence:
    account_epoch: int
    symbol_epoch: int
    position_epoch: int
    recovery_epoch: int

    generation: int
    lineage_id: str

    def validate(
        self,
    ) -> None:
        require(
            self.account_epoch > 0,
            "account epoch must be positive",
        )

        require(
            self.symbol_epoch > 0,
            "symbol epoch must be positive",
        )

        require(
            self.position_epoch > 0,
            "position epoch must be positive",
        )

        require(
            self.recovery_epoch > 0,
            "recovery epoch must be positive",
        )

        require(
            self.generation > 0,
            "generation must be positive",
        )

        require(
            bool(
                self.lineage_id
            ),
            "lineage id required",
        )

    def fingerprint(
        self,
    ) -> str:
        self.validate()

        return sha256_json(
            asdict(
                self
            )
        )


# ============================================================================
# RECOVERY LEASE
# ============================================================================

@dataclass(frozen=True)
class RecoveryLease:
    lease_id: str
    owner_id: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    nonce: int
    issued_at_ms: int

    fence_hash: str

    def validate(
        self,
    ) -> None:
        require(
            bool(
                self.lease_id
            ),
            "lease id required",
        )

        require(
            bool(
                self.owner_id
            ),
            "lease owner required",
        )

        require(
            self.generation > 0,
            "lease generation invalid",
        )

        require(
            bool(
                self.lineage_id
            ),
            "lease lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "lease recovery epoch invalid",
        )

        require(
            self.nonce > 0,
            "lease nonce invalid",
        )

        require(
            self.issued_at_ms > 0,
            "lease timestamp invalid",
        )

        require(
            bool(
                self.fence_hash
            ),
            "lease fence hash required",
        )


# ============================================================================
# RECOVERY AUTHORIZATION
# ============================================================================

@dataclass(frozen=True)
class RecoveryAuthorization:
    authorization_id: str

    owner_id: str
    lease_id: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    nonce: int

    intent_id: str
    dispatch_id: str

    transport_method: str
    transport_path: str
    payload_hash: str

    issued_at_ms: int

    consumed: bool = False
    consumed_at_ms: Optional[int] = None

    def validate(
        self,
    ) -> None:
        require(
            bool(
                self.authorization_id
            ),
            "authorization id required",
        )

        require(
            bool(
                self.owner_id
            ),
            "authorization owner required",
        )

        require(
            bool(
                self.lease_id
            ),
            "authorization lease required",
        )

        require(
            self.generation > 0,
            "authorization generation invalid",
        )

        require(
            bool(
                self.lineage_id
            ),
            "authorization lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "authorization recovery epoch invalid",
        )

        require(
            self.nonce > 0,
            "authorization nonce invalid",
        )

        require(
            bool(
                self.intent_id
            ),
            "authorization intent required",
        )

        require(
            bool(
                self.dispatch_id
            ),
            "authorization dispatch required",
        )

        require(
            self.transport_method
            == TRANSPORT_METHOD,
            (
                "authorization transport "
                "method mismatch"
            ),
        )

        require(
            self.transport_path
            == LEVERAGE_ENDPOINT,
            (
                "authorization transport "
                "path mismatch"
            ),
        )

        require(
            self.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            (
                "authorization payload "
                "hash mismatch"
            ),
        )

        require(
            self.issued_at_ms > 0,
            "authorization timestamp invalid",
        )

        if self.consumed:
            require(
                self.consumed_at_ms
                is not None,
                (
                    "consumed authorization "
                    "missing timestamp"
                ),
            )

        else:
            require(
                self.consumed_at_ms
                is None,
                (
                    "unconsumed authorization "
                    "cannot have consumed timestamp"
                ),
            )


# ============================================================================
# EXACT DISPATCH BINDING
# ============================================================================

@dataclass(frozen=True)
class DispatchBinding:
    dispatch_id: str
    intent_id: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    transport_method: str
    transport_path: str

    payload: Dict[str, str]
    payload_hash: str

    def validate(
        self,
    ) -> None:
        require(
            bool(
                self.dispatch_id
            ),
            "dispatch id required",
        )

        require(
            bool(
                self.intent_id
            ),
            "intent id required",
        )

        require(
            self.generation > 0,
            "dispatch generation invalid",
        )

        require(
            bool(
                self.lineage_id
            ),
            "dispatch lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "dispatch recovery epoch invalid",
        )

        require(
            self.transport_method
            == TRANSPORT_METHOD,
            "transport method mismatch",
        )

        require(
            self.transport_path
            == LEVERAGE_ENDPOINT,
            "transport path mismatch",
        )

        require(
            canonical_json(
                self.payload
            )
            == EXACT_LEVERAGE_PAYLOAD_JSON,
            "exact leverage payload mismatch",
        )

        require(
            sha256_json(
                self.payload
            )
            == self.payload_hash,
            "dispatch payload hash corrupted",
        )

        require(
            self.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            "dispatch payload hash mismatch",
        )


# ============================================================================
# N.27 WAL RECORD
#
# Every durable transition is represented by one immutable record.
#
# Hash chain:
#
#   GENESIS
#      ↓
#   RECORD 1
#      ↓
#   RECORD 2
#      ↓
#   RECORD 3
#      ↓
#   ...
#
# A valid record therefore binds:
#
#   - Sequence
#   - Previous WAL hash
#   - Generation
#   - Lineage
#   - Recovery epoch
#   - Intent
#   - Dispatch
#   - Event
#   - Payload hash
#
# Changing any historical record breaks every subsequent hash.
# ============================================================================

@dataclass(frozen=True)
class WALRecord:
    sequence: int
    event: str

    timestamp_ms: int

    generation: int
    lineage_id: str
    recovery_epoch: int

    intent_id: str
    dispatch_id: str

    authorization_id: Optional[str]
    lease_id: Optional[str]

    payload_hash: str

    previous_hash: str
    record_hash: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def payload_without_hash(
        self,
    ) -> Dict[str, Any]:
        return {
            "sequence":
                self.sequence,

            "event":
                self.event,

            "timestamp_ms":
                self.timestamp_ms,

            "generation":
                self.generation,

            "lineage_id":
                self.lineage_id,

            "recovery_epoch":
                self.recovery_epoch,

            "intent_id":
                self.intent_id,

            "dispatch_id":
                self.dispatch_id,

            "authorization_id":
                self.authorization_id,

            "lease_id":
                self.lease_id,

            "payload_hash":
                self.payload_hash,

            "previous_hash":
                self.previous_hash,

            "metadata":
                clone(
                    self.metadata
                ),
        }

    def calculate_hash(
        self,
    ) -> str:
        return sha256_json(
            self.payload_without_hash()
        )

    def validate(
        self,
    ) -> None:
        require(
            self.sequence > 0,
            "WAL sequence invalid",
        )

        require(
            self.event
            in VALID_WAL_EVENTS,
            "invalid WAL event",
        )

        require(
            self.timestamp_ms > 0,
            "WAL timestamp invalid",
        )

        require(
            self.generation > 0,
            "WAL generation invalid",
        )

        require(
            bool(
                self.lineage_id
            ),
            "WAL lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "WAL recovery epoch invalid",
        )

        require(
            bool(
                self.intent_id
            ),
            "WAL intent required",
        )

        require(
            bool(
                self.dispatch_id
            ),
            "WAL dispatch required",
        )

        require(
            self.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            "WAL payload hash mismatch",
        )

        require(
            bool(
                self.previous_hash
            ),
            "WAL previous hash required",
        )

        require(
            bool(
                self.record_hash
            ),
            "WAL record hash required",
        )

        require(
            hmac.compare_digest(
                self.calculate_hash(),
                self.record_hash,
            ),
            "WAL record hash mismatch",
        )


# ============================================================================
# WAL FACTORY
# ============================================================================

def create_wal_record(
    *,
    sequence: int,
    event: str,

    generation: int,
    lineage_id: str,
    recovery_epoch: int,

    intent_id: str,
    dispatch_id: str,

    authorization_id: Optional[str],
    lease_id: Optional[str],

    previous_hash: str,

    metadata: Optional[
        Dict[str, Any]
    ] = None,

) -> WALRecord:

    payload = {
        "sequence":
            sequence,

        "event":
            event,

        "timestamp_ms":
            now_ms(),

        "generation":
            generation,

        "lineage_id":
            lineage_id,

        "recovery_epoch":
            recovery_epoch,

        "intent_id":
            intent_id,

        "dispatch_id":
            dispatch_id,

        "authorization_id":
            authorization_id,

        "lease_id":
            lease_id,

        "payload_hash":
            EXACT_LEVERAGE_PAYLOAD_HASH,

        "previous_hash":
            previous_hash,

        "metadata":
            clone(
                metadata or {}
            ),
    }

    record_hash = sha256_json(
        payload
    )

    record = WALRecord(
        sequence=(
            payload["sequence"]
        ),

        event=(
            payload["event"]
        ),

        timestamp_ms=(
            payload["timestamp_ms"]
        ),

        generation=(
            payload["generation"]
        ),

        lineage_id=(
            payload["lineage_id"]
        ),

        recovery_epoch=(
            payload["recovery_epoch"]
        ),

        intent_id=(
            payload["intent_id"]
        ),

        dispatch_id=(
            payload["dispatch_id"]
        ),

        authorization_id=(
            payload["authorization_id"]
        ),

        lease_id=(
            payload["lease_id"]
        ),

        payload_hash=(
            payload["payload_hash"]
        ),

        previous_hash=(
            payload["previous_hash"]
        ),

        record_hash=(
            record_hash
        ),

        metadata=clone(
            payload["metadata"]
        ),
    )

    record.validate()

    return record


# ============================================================================
# WAL VALIDATION
# ============================================================================

def validate_wal(
    records: List[
        WALRecord
    ],
) -> None:

    previous_hash = (
        GENESIS_WAL_HASH
    )

    expected_sequence = 1

    for record in records:
        record.validate()

        require(
            record.sequence
            == expected_sequence,
            "WAL sequence discontinuity",
        )

        require(
            hmac.compare_digest(
                record.previous_hash,
                previous_hash,
            ),
            "WAL hash chain mismatch",
        )

        previous_hash = (
            record.record_hash
        )

        expected_sequence += 1


def wal_final_hash(
    records: List[
        WALRecord
    ],
) -> str:

    validate_wal(
        records
    )

    if not records:
        return GENESIS_WAL_HASH

    return records[-1].record_hash


# ============================================================================
# N.27 CHECKPOINT
#
# A checkpoint is not trusted merely because its own seal is valid.
#
# It must also bind to:
#
#   - WAL length
#   - WAL final record hash
#   - Generation
#   - Lineage
#   - Recovery epoch
#   - Execution phase
#   - Intent
#   - Dispatch
#
# Therefore an old checkpoint cannot silently replace a newer WAL history.
# ============================================================================

@dataclass(frozen=True)
class Checkpoint:
    schema_version: int

    checkpoint_id: str

    sequence: int

    phase: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    intent_id: str
    dispatch_id: str

    wal_length: int
    wal_final_hash: str

    created_at_ms: int

    integrity_seal: str

    def payload_without_seal(
        self,
    ) -> Dict[str, Any]:
        return {
            "schema_version":
                self.schema_version,

            "checkpoint_id":
                self.checkpoint_id,

            "sequence":
                self.sequence,

            "phase":
                self.phase,

            "generation":
                self.generation,

            "lineage_id":
                self.lineage_id,

            "recovery_epoch":
                self.recovery_epoch,

            "intent_id":
                self.intent_id,

            "dispatch_id":
                self.dispatch_id,

            "wal_length":
                self.wal_length,

            "wal_final_hash":
                self.wal_final_hash,

            "created_at_ms":
                self.created_at_ms,
        }

    def calculate_integrity_seal(
        self,
    ) -> str:
        return hmac_sha256(
            CHECKPOINT_KEY,
            canonical_json(
                self.payload_without_seal()
            ),
        )

    def validate(
        self,
    ) -> None:
        require(
            self.schema_version
            == CHECKPOINT_SCHEMA_VERSION,
            "checkpoint schema mismatch",
        )

        require(
            bool(
                self.checkpoint_id
            ),
            "checkpoint id required",
        )

        require(
            self.sequence >= 0,
            "checkpoint sequence invalid",
        )

        require(
            self.phase
            in ALL_PHASES,
            "checkpoint phase invalid",
        )

        require(
            self.generation > 0,
            "checkpoint generation invalid",
        )

        require(
            bool(
                self.lineage_id
            ),
            "checkpoint lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "checkpoint recovery epoch invalid",
        )

        require(
            bool(
                self.intent_id
            ),
            "checkpoint intent required",
        )

        require(
            bool(
                self.dispatch_id
            ),
            "checkpoint dispatch required",
        )

        require(
            self.wal_length >= 0,
            "checkpoint WAL length invalid",
        )

        require(
            bool(
                self.wal_final_hash
            ),
            "checkpoint WAL hash required",
        )

        require(
            self.created_at_ms > 0,
            "checkpoint timestamp invalid",
        )

        require(
            bool(
                self.integrity_seal
            ),
            "checkpoint integrity seal missing",
        )

        require(
            hmac.compare_digest(
                self.calculate_integrity_seal(),
                self.integrity_seal,
            ),
            "checkpoint integrity seal mismatch",
        )


# ============================================================================
# CHECKPOINT FACTORY
# ============================================================================

def create_checkpoint(
    *,
    sequence: int,
    phase: str,

    generation: int,
    lineage_id: str,
    recovery_epoch: int,

    intent_id: str,
    dispatch_id: str,

    wal: List[
        WALRecord
    ],

) -> Checkpoint:

    validate_wal(
        wal
    )

    checkpoint_id = deterministic_id(
        "checkpoint",
        sequence,
        phase,
        generation,
        lineage_id,
        recovery_epoch,
        intent_id,
        dispatch_id,
        len(wal),
        wal_final_hash(
            wal
        ),
    )

    provisional = Checkpoint(
        schema_version=(
            CHECKPOINT_SCHEMA_VERSION
        ),

        checkpoint_id=(
            checkpoint_id
        ),

        sequence=(
            sequence
        ),

        phase=(
            phase
        ),

        generation=(
            generation
        ),

        lineage_id=(
            lineage_id
        ),

        recovery_epoch=(
            recovery_epoch
        ),

        intent_id=(
            intent_id
        ),

        dispatch_id=(
            dispatch_id
        ),

        wal_length=(
            len(wal)
        ),

        wal_final_hash=(
            wal_final_hash(
                wal
            )
        ),

        created_at_ms=(
            now_ms()
        ),

        integrity_seal="",
    )

    seal = (
        provisional
        .calculate_integrity_seal()
    )

    checkpoint = Checkpoint(
        schema_version=(
            provisional.schema_version
        ),

        checkpoint_id=(
            provisional.checkpoint_id
        ),

        sequence=(
            provisional.sequence
        ),

        phase=(
            provisional.phase
        ),

        generation=(
            provisional.generation
        ),

        lineage_id=(
            provisional.lineage_id
        ),

        recovery_epoch=(
            provisional.recovery_epoch
        ),

        intent_id=(
            provisional.intent_id
        ),

        dispatch_id=(
            provisional.dispatch_id
        ),

        wal_length=(
            provisional.wal_length
        ),

        wal_final_hash=(
            provisional.wal_final_hash
        ),

        created_at_ms=(
            provisional.created_at_ms
        ),

        integrity_seal=(
            seal
        ),
    )

    checkpoint.validate()

    return checkpoint


# ============================================================================
# CHECKPOINT ↔ WAL BINDING
# ============================================================================

def validate_checkpoint_wal_binding(
    checkpoint: Checkpoint,
    wal: List[
        WALRecord
    ],
) -> None:

    checkpoint.validate()

    validate_wal(
        wal
    )

    require(
        checkpoint.wal_length
        == len(wal),
        "checkpoint WAL length mismatch",
    )

    require(
        hmac.compare_digest(
            checkpoint.wal_final_hash,
            wal_final_hash(
                wal
            ),
        ),
        (
            "checkpoint WAL final "
            "hash mismatch"
        ),
    )

    if wal:
        tail = wal[-1]

        require(
            tail.generation
            == checkpoint.generation,
            (
                "checkpoint generation "
                "does not match WAL"
            ),
        )

        require(
            tail.lineage_id
            == checkpoint.lineage_id,
            (
                "checkpoint lineage "
                "does not match WAL"
            ),
        )

        require(
            tail.recovery_epoch
            == checkpoint.recovery_epoch,
            (
                "checkpoint recovery epoch "
                "does not match WAL"
            ),
        )

        require(
            tail.intent_id
            == checkpoint.intent_id,
            (
                "checkpoint intent "
                "does not match WAL"
            ),
        )

        require(
            tail.dispatch_id
            == checkpoint.dispatch_id,
            (
                "checkpoint dispatch "
                "does not match WAL"
            ),
        )


# ============================================================================
# SYNTHETIC RECEIPT
# ============================================================================

@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str

    dispatch_id: str

    status: str

    transport_method: str
    transport_path: str
    payload_hash: str

    transmitted: bool
    network_write: bool

    generation: int
    lineage_id: str
    recovery_epoch: int

    created_at_ms: int

    def validate(
        self,
    ) -> None:
        require(
            bool(
                self.receipt_id
            ),
            "receipt id required",
        )

        require(
            bool(
                self.dispatch_id
            ),
            "receipt dispatch required",
        )

        require(
            self.status
            == SYNTHETIC_RECEIPT_STATUS,
            (
                "unexpected synthetic "
                "receipt status"
            ),
        )

        require(
            self.transport_method
            == TRANSPORT_METHOD,
            (
                "receipt transport "
                "method mismatch"
            ),
        )

        require(
            self.transport_path
            == LEVERAGE_ENDPOINT,
            (
                "receipt transport "
                "path mismatch"
            ),
        )

        require(
            self.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            (
                "receipt payload "
                "hash mismatch"
            ),
        )

        require(
            self.transmitted is False,
            (
                "synthetic receipt cannot "
                "report transmission"
            ),
        )

        require(
            self.network_write is False,
            (
                "synthetic receipt cannot "
                "report network write"
            ),
        )

        require(
            self.generation > 0,
            "receipt generation invalid",
        )

        require(
            bool(
                self.lineage_id
            ),
            "receipt lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "receipt recovery epoch invalid",
        )

        require(
            self.created_at_ms > 0,
            "receipt timestamp invalid",
        )


# ============================================================================
# SYNTHETIC TRANSPORT
# ============================================================================

class SyntheticTransport:
    def __init__(
        self,
    ) -> None:
        self.dispatch_count = 0

        self.network_write_count = 0
        self.real_post_count = 0
        self.demo_post_count = 0

        self.leverage_transmission_count = 0

        self.dispatched_ids: Set[
            str
        ] = set()

        self._lock = (
            threading.RLock()
        )

    def dispatch(
        self,
        binding: DispatchBinding,
    ) -> SyntheticReceipt:

        with self._lock:
            binding.validate()

            require(
                SYNTHETIC_TRANSPORT_ONLY
                is True,
                (
                    "synthetic-only transport "
                    "must remain enabled"
                ),
            )

            require(
                LIVE_ORDER_EXECUTION
                is False,
                (
                    "live order execution "
                    "must remain disabled"
                ),
            )

            require(
                DEMO_ORDER_EXECUTION
                is False,
                (
                    "demo order execution "
                    "must remain disabled"
                ),
            )

            require(
                NETWORK_WRITES_ENABLED
                is False,
                (
                    "network writes "
                    "must remain disabled"
                ),
            )

            require(
                REAL_POST_ENABLED
                is False,
                (
                    "real POST "
                    "must remain disabled"
                ),
            )

            require(
                DEMO_POST_ENABLED
                is False,
                (
                    "demo POST "
                    "must remain disabled"
                ),
            )

            require(
                LEVERAGE_TRANSMISSION_ENABLED
                is False,
                (
                    "leverage transmission "
                    "must remain disabled"
                ),
            )

            require(
                binding.dispatch_id
                not in self.dispatched_ids,
                (
                    "synthetic dispatch "
                    "replay rejected"
                ),
            )

            self.dispatched_ids.add(
                binding.dispatch_id
            )

            self.dispatch_count += 1

            receipt = SyntheticReceipt(
                receipt_id=(
                    deterministic_id(
                        "receipt",
                        binding.dispatch_id,
                        binding.generation,
                        binding.lineage_id,
                        binding.recovery_epoch,
                        binding.payload_hash,
                    )
                ),

                dispatch_id=(
                    binding.dispatch_id
                ),

                status=(
                    SYNTHETIC_RECEIPT_STATUS
                ),

                transport_method=(
                    binding.transport_method
                ),

                transport_path=(
                    binding.transport_path
                ),

                payload_hash=(
                    binding.payload_hash
                ),

                transmitted=False,

                network_write=False,

                generation=(
                    binding.generation
                ),

                lineage_id=(
                    binding.lineage_id
                ),

                recovery_epoch=(
                    binding.recovery_epoch
                ),

                created_at_ms=(
                    now_ms()
                ),
            )

            receipt.validate()

            return receipt


# ============================================================================
# FINAL NETWORK FIREBREAK
# ============================================================================

def assert_transport_firebreak(
    transport: SyntheticTransport,
) -> None:

    require(
        SYNTHETIC_TRANSPORT_ONLY
        is True,
        (
            "synthetic-only transport "
            "unexpectedly disabled"
        ),
    )

    require(
        LIVE_ORDER_EXECUTION
        is False,
        "live execution unexpectedly enabled",
    )

    require(
        DEMO_ORDER_EXECUTION
        is False,
        "demo execution unexpectedly enabled",
    )

    require(
        NETWORK_WRITES_ENABLED
        is False,
        "network writes unexpectedly enabled",
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
        LEVERAGE_TRANSMISSION_ENABLED
        is False,
        (
            "leverage transmission "
            "unexpectedly enabled"
        ),
    )

    require(
        transport.network_write_count
        == 0,
        "network write detected",
    )

    require(
        transport.real_post_count
        == 0,
        "real POST detected",
    )

    require(
        transport.demo_post_count
        == 0,
        "demo POST detected",
    )

    require(
        transport.leverage_transmission_count
        == 0,
        "leverage transmission detected",
    )


# ============================================================================
# END OF PART 1
# ============================================================================

print(
    "R28 UNIT N.27: PART 1 DEFINITIONS LOADED",
    flush=True,
)
