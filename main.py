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
# ============================================================================
# R28 UNIT N.27
# DURABLE WAL RECOVERY + CHECKPOINT BINDING + RESTART-SAFE FINALITY
#
# CORRECTED COPY/PASTE VERSION
# PART 2 OF 4
#
# IMPORTANT:
#   - PASTE DIRECTLY BELOW PART 1
#   - FIRST LINE MUST START AT COLUMN ZERO
#   - DO NOT ADD ANOTHER PART 1 / PART 2 MARKER
# ============================================================================


# ============================================================================
# DURABLE EXECUTION STATE
# ============================================================================

@dataclass
class DurableState:
    schema_version: int

    phase: str

    account_epoch: int
    symbol_epoch: int
    position_epoch: int
    recovery_epoch: int

    generation: int
    lineage_id: str

    intent_id: str
    dispatch_id: str

    lease_nonce: int

    active_lease: Optional[
        RecoveryLease
    ]

    authorization: Optional[
        RecoveryAuthorization
    ]

    dispatch_binding: Optional[
        DispatchBinding
    ]

    receipt: Optional[
        SyntheticReceipt
    ]

    wal: List[
        WALRecord
    ]

    checkpoint: Optional[
        Checkpoint
    ]

    completed_dispatch_ids: Set[str]

    consumed_authorization_ids: Set[str]

    retired_lease_ids: Set[str]

    snapshot_sequence: int

    integrity_seal: str = ""

    # ========================================================================
    # CURRENT GENERATION FENCE
    # ========================================================================

    def fence(
        self,
    ) -> GenerationFence:

        return GenerationFence(
            account_epoch=(
                self.account_epoch
            ),

            symbol_epoch=(
                self.symbol_epoch
            ),

            position_epoch=(
                self.position_epoch
            ),

            recovery_epoch=(
                self.recovery_epoch
            ),

            generation=(
                self.generation
            ),

            lineage_id=(
                self.lineage_id
            ),
        )

    # ========================================================================
    # BASIC VALIDATION
    # ========================================================================

    def validate_basic(
        self,
    ) -> None:

        require(
            self.schema_version
            == STATE_SCHEMA_VERSION,
            (
                "unsupported durable "
                "state schema"
            ),
        )

        require(
            self.phase
            in ALL_PHASES,
            (
                "invalid durable "
                "execution phase"
            ),
        )

        require(
            self.account_epoch > 0,
            "account epoch invalid",
        )

        require(
            self.symbol_epoch > 0,
            "symbol epoch invalid",
        )

        require(
            self.position_epoch > 0,
            "position epoch invalid",
        )

        require(
            self.recovery_epoch > 0,
            "recovery epoch invalid",
        )

        require(
            self.generation > 0,
            "generation invalid",
        )

        require(
            bool(
                self.lineage_id
            ),
            "lineage id required",
        )

        require(
            bool(
                self.intent_id
            ),
            "intent id required",
        )

        require(
            bool(
                self.dispatch_id
            ),
            "dispatch id required",
        )

        require(
            self.lease_nonce >= 0,
            "lease nonce invalid",
        )

        require(
            self.snapshot_sequence >= 0,
            "snapshot sequence invalid",
        )

        self.fence().validate()

        if self.active_lease is not None:
            self.active_lease.validate()

        if self.authorization is not None:
            self.authorization.validate()

        if self.dispatch_binding is not None:
            self.dispatch_binding.validate()

        if self.receipt is not None:
            self.receipt.validate()

        validate_wal(
            self.wal
        )

        if self.checkpoint is not None:
            validate_checkpoint_wal_binding(
                self.checkpoint,
                self.wal,
            )

        # ====================================================================
        # ACTIVE LEASE BINDING
        # ====================================================================

        if self.active_lease is not None:

            require(
                self.active_lease.generation
                == self.generation,
                (
                    "active lease generation "
                    "mismatch"
                ),
            )

            require(
                self.active_lease.lineage_id
                == self.lineage_id,
                (
                    "active lease lineage "
                    "mismatch"
                ),
            )

            require(
                self.active_lease.recovery_epoch
                == self.recovery_epoch,
                (
                    "active lease recovery "
                    "epoch mismatch"
                ),
            )

            require(
                self.active_lease.nonce
                == self.lease_nonce,
                (
                    "active lease nonce "
                    "mismatch"
                ),
            )

            require(
                hmac.compare_digest(
                    self.active_lease.fence_hash,
                    self.fence().fingerprint(),
                ),
                (
                    "active lease fence "
                    "mismatch"
                ),
            )

            require(
                self.active_lease.lease_id
                not in self.retired_lease_ids,
                (
                    "active lease cannot "
                    "already be retired"
                ),
            )

        # ====================================================================
        # AUTHORIZATION BINDING
        # ====================================================================

        if self.authorization is not None:

            require(
                self.authorization.generation
                == self.generation,
                (
                    "authorization generation "
                    "mismatch"
                ),
            )

            require(
                self.authorization.lineage_id
                == self.lineage_id,
                (
                    "authorization lineage "
                    "mismatch"
                ),
            )

            require(
                self.authorization.recovery_epoch
                == self.recovery_epoch,
                (
                    "authorization recovery "
                    "epoch mismatch"
                ),
            )

            require(
                self.authorization.intent_id
                == self.intent_id,
                (
                    "authorization intent "
                    "mismatch"
                ),
            )

            require(
                self.authorization.dispatch_id
                == self.dispatch_id,
                (
                    "authorization dispatch "
                    "mismatch"
                ),
            )

            if self.authorization.consumed:

                require(
                    self.authorization.authorization_id
                    in self.consumed_authorization_ids,
                    (
                        "consumed authorization "
                        "missing durable fence"
                    ),
                )

            else:

                require(
                    self.authorization.authorization_id
                    not in self.consumed_authorization_ids,
                    (
                        "unconsumed authorization "
                        "cannot be in consumed set"
                    ),
                )

        # ====================================================================
        # DISPATCH BINDING
        # ====================================================================

        if self.dispatch_binding is not None:

            require(
                self.dispatch_binding.dispatch_id
                == self.dispatch_id,
                (
                    "dispatch binding id "
                    "mismatch"
                ),
            )

            require(
                self.dispatch_binding.intent_id
                == self.intent_id,
                (
                    "dispatch binding intent "
                    "mismatch"
                ),
            )

            require(
                self.dispatch_binding.generation
                == self.generation,
                (
                    "dispatch binding generation "
                    "mismatch"
                ),
            )

            require(
                self.dispatch_binding.lineage_id
                == self.lineage_id,
                (
                    "dispatch binding lineage "
                    "mismatch"
                ),
            )

            require(
                self.dispatch_binding.recovery_epoch
                == self.recovery_epoch,
                (
                    "dispatch binding recovery "
                    "epoch mismatch"
                ),
            )

        # ====================================================================
        # RECEIPT BINDING
        # ====================================================================

        if self.receipt is not None:

            require(
                self.receipt.dispatch_id
                == self.dispatch_id,
                (
                    "receipt dispatch "
                    "mismatch"
                ),
            )

            require(
                self.receipt.generation
                == self.generation,
                (
                    "receipt generation "
                    "mismatch"
                ),
            )

            require(
                self.receipt.lineage_id
                == self.lineage_id,
                (
                    "receipt lineage "
                    "mismatch"
                ),
            )

            require(
                self.receipt.recovery_epoch
                == self.recovery_epoch,
                (
                    "receipt recovery epoch "
                    "mismatch"
                ),
            )

        # ====================================================================
        # TERMINAL FINALITY
        # ====================================================================

        if self.phase in TERMINAL_PHASES:

            require(
                self.dispatch_id
                in self.completed_dispatch_ids,
                (
                    "terminal state missing "
                    "completed dispatch fence"
                ),
            )

            require(
                self.receipt
                is not None,
                (
                    "terminal completed state "
                    "missing receipt"
                ),
            )


# ============================================================================
# SERIALIZATION HELPERS
# ============================================================================

def recovery_lease_to_dict(
    lease: Optional[
        RecoveryLease
    ],
) -> Optional[
    Dict[str, Any]
]:

    if lease is None:
        return None

    return asdict(
        lease
    )


def authorization_to_dict(
    authorization: Optional[
        RecoveryAuthorization
    ],
) -> Optional[
    Dict[str, Any]
]:

    if authorization is None:
        return None

    return asdict(
        authorization
    )


def dispatch_binding_to_dict(
    binding: Optional[
        DispatchBinding
    ],
) -> Optional[
    Dict[str, Any]
]:

    if binding is None:
        return None

    return asdict(
        binding
    )


def receipt_to_dict(
    receipt: Optional[
        SyntheticReceipt
    ],
) -> Optional[
    Dict[str, Any]
]:

    if receipt is None:
        return None

    return asdict(
        receipt
    )


def wal_record_to_dict(
    record: WALRecord,
) -> Dict[str, Any]:

    return asdict(
        record
    )


def checkpoint_to_dict(
    checkpoint: Optional[
        Checkpoint
    ],
) -> Optional[
    Dict[str, Any]
]:

    if checkpoint is None:
        return None

    return asdict(
        checkpoint
    )


# ============================================================================
# STATE PAYLOAD WITHOUT INTEGRITY SEAL
# ============================================================================

def state_payload_without_seal(
    state: DurableState,
) -> Dict[str, Any]:

    return {
        "schema_version":
            state.schema_version,

        "phase":
            state.phase,

        "account_epoch":
            state.account_epoch,

        "symbol_epoch":
            state.symbol_epoch,

        "position_epoch":
            state.position_epoch,

        "recovery_epoch":
            state.recovery_epoch,

        "generation":
            state.generation,

        "lineage_id":
            state.lineage_id,

        "intent_id":
            state.intent_id,

        "dispatch_id":
            state.dispatch_id,

        "lease_nonce":
            state.lease_nonce,

        "active_lease":
            recovery_lease_to_dict(
                state.active_lease
            ),

        "authorization":
            authorization_to_dict(
                state.authorization
            ),

        "dispatch_binding":
            dispatch_binding_to_dict(
                state.dispatch_binding
            ),

        "receipt":
            receipt_to_dict(
                state.receipt
            ),

        "wal": [
            wal_record_to_dict(
                record
            )
            for record
            in state.wal
        ],

        "checkpoint":
            checkpoint_to_dict(
                state.checkpoint
            ),

        "completed_dispatch_ids":
            sorted(
                state.completed_dispatch_ids
            ),

        "consumed_authorization_ids":
            sorted(
                state.consumed_authorization_ids
            ),

        "retired_lease_ids":
            sorted(
                state.retired_lease_ids
            ),

        "snapshot_sequence":
            state.snapshot_sequence,
    }


# ============================================================================
# DURABLE SNAPSHOT INTEGRITY
# ============================================================================

def calculate_state_integrity_seal(
    state: DurableState,
) -> str:

    return hmac_sha256(
        INTEGRITY_KEY,
        canonical_json(
            state_payload_without_seal(
                state
            )
        ),
    )


def seal_state(
    state: DurableState,
) -> DurableState:

    state.integrity_seal = (
        calculate_state_integrity_seal(
            state
        )
    )

    return state


def verify_state_integrity(
    state: DurableState,
) -> None:

    expected = (
        calculate_state_integrity_seal(
            state
        )
    )

    require(
        bool(
            state.integrity_seal
        ),
        (
            "snapshot integrity "
            "seal missing"
        ),
    )

    require(
        hmac.compare_digest(
            expected,
            state.integrity_seal,
        ),
        (
            "snapshot integrity "
            "seal mismatch"
        ),
    )


# ============================================================================
# DEEP DURABLE STATE VALIDATION
# ============================================================================

def validate_durable_state(
    state: DurableState,
) -> None:

    verify_state_integrity(
        state
    )

    state.validate_basic()

    # ========================================================================
    # WAL RECORDS MUST MATCH CURRENT GENERATION
    # ========================================================================

    for record in state.wal:

        require(
            record.generation
            == state.generation,
            (
                "WAL generation "
                "does not match state"
            ),
        )

        require(
            record.lineage_id
            == state.lineage_id,
            (
                "WAL lineage "
                "does not match state"
            ),
        )

        require(
            record.recovery_epoch
            == state.recovery_epoch,
            (
                "WAL recovery epoch "
                "does not match state"
            ),
        )

        require(
            record.intent_id
            == state.intent_id,
            (
                "WAL intent "
                "does not match state"
            ),
        )

        require(
            record.dispatch_id
            == state.dispatch_id,
            (
                "WAL dispatch "
                "does not match state"
            ),
        )

    # ========================================================================
    # PHASE ↔ WAL TAIL CONSISTENCY
    # ========================================================================

    if state.wal:

        tail_event = (
            state.wal[-1].event
        )

        expected_tail_by_phase = {
            PHASE_PREPARED:
                WAL_EVENT_PREPARED,

            PHASE_AUTHORIZED:
                WAL_EVENT_AUTHORIZED,

            PHASE_COMMITTED:
                WAL_EVENT_COMMITTED,

            PHASE_DISPATCHED:
                WAL_EVENT_DISPATCHED,

            PHASE_COMPLETED:
                WAL_EVENT_COMPLETED,
        }

        if state.phase in expected_tail_by_phase:

            require(
                tail_event
                == expected_tail_by_phase[
                    state.phase
                ]
                or tail_event
                == WAL_EVENT_CHECKPOINT,
                (
                    "state phase does not "
                    "match WAL tail"
                ),
            )

    # ========================================================================
    # CHECKPOINT MUST REPRESENT CURRENT DURABLE HISTORY
    # ========================================================================

    if state.checkpoint is not None:

        validate_checkpoint_wal_binding(
            state.checkpoint,
            state.wal,
        )

        require(
            state.checkpoint.generation
            == state.generation,
            (
                "checkpoint generation "
                "mismatch"
            ),
        )

        require(
            state.checkpoint.lineage_id
            == state.lineage_id,
            (
                "checkpoint lineage "
                "mismatch"
            ),
        )

        require(
            state.checkpoint.recovery_epoch
            == state.recovery_epoch,
            (
                "checkpoint recovery "
                "epoch mismatch"
            ),
        )

        require(
            state.checkpoint.intent_id
            == state.intent_id,
            (
                "checkpoint intent "
                "mismatch"
            ),
        )

        require(
            state.checkpoint.dispatch_id
            == state.dispatch_id,
            (
                "checkpoint dispatch "
                "mismatch"
            ),
        )


# ============================================================================
# INITIAL DURABLE STATE FACTORY
# ============================================================================

def create_initial_state(
) -> DurableState:

    generation = (
        DEFAULT_GENERATION
    )

    recovery_epoch = (
        DEFAULT_RECOVERY_EPOCH
    )

    lineage_id = secure_id(
        "lineage"
    )

    intent_id = deterministic_id(
        "intent",
        SYMBOL,
        generation,
        lineage_id,
        recovery_epoch,
        EXACT_LEVERAGE_PAYLOAD_HASH,
    )

    dispatch_id = deterministic_id(
        "dispatch",
        intent_id,
        generation,
        lineage_id,
        recovery_epoch,
    )

    initial_record = create_wal_record(
        sequence=1,

        event=(
            WAL_EVENT_PREPARED
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

        authorization_id=None,
        lease_id=None,

        previous_hash=(
            GENESIS_WAL_HASH
        ),

        metadata={
            "phase":
                PHASE_PREPARED,

            "symbol":
                SYMBOL,

            "leverage":
                LEVERAGE,

            "margin_mode":
                MARGIN_MODE,
        },
    )

    wal = [
        initial_record
    ]

    checkpoint = create_checkpoint(
        sequence=1,

        phase=(
            PHASE_PREPARED
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

        wal=(
            wal
        ),
    )

    state = DurableState(
        schema_version=(
            STATE_SCHEMA_VERSION
        ),

        phase=(
            PHASE_PREPARED
        ),

        account_epoch=(
            DEFAULT_ACCOUNT_EPOCH
        ),

        symbol_epoch=(
            DEFAULT_SYMBOL_EPOCH
        ),

        position_epoch=(
            DEFAULT_POSITION_EPOCH
        ),

        recovery_epoch=(
            recovery_epoch
        ),

        generation=(
            generation
        ),

        lineage_id=(
            lineage_id
        ),

        intent_id=(
            intent_id
        ),

        dispatch_id=(
            dispatch_id
        ),

        lease_nonce=0,

        active_lease=None,

        authorization=None,

        dispatch_binding=None,

        receipt=None,

        wal=(
            wal
        ),

        checkpoint=(
            checkpoint
        ),

        completed_dispatch_ids=set(),

        consumed_authorization_ids=set(),

        retired_lease_ids=set(),

        snapshot_sequence=1,

        integrity_seal="",
    )

    seal_state(
        state
    )

    validate_durable_state(
        state
    )

    return state


# ============================================================================
# WAL APPEND HELPER
# ============================================================================

def append_wal_event(
    state: DurableState,
    event: str,
    *,
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> WALRecord:

    require(
        event
        in VALID_WAL_EVENTS,
        "invalid WAL append event",
    )

    validate_wal(
        state.wal
    )

    sequence = (
        len(state.wal) + 1
    )

    previous_hash = wal_final_hash(
        state.wal
    )

    authorization_id = None
    lease_id = None

    if state.authorization is not None:
        authorization_id = (
            state.authorization
            .authorization_id
        )

    if state.active_lease is not None:
        lease_id = (
            state.active_lease
            .lease_id
        )

    record = create_wal_record(
        sequence=(
            sequence
        ),

        event=(
            event
        ),

        generation=(
            state.generation
        ),

        lineage_id=(
            state.lineage_id
        ),

        recovery_epoch=(
            state.recovery_epoch
        ),

        intent_id=(
            state.intent_id
        ),

        dispatch_id=(
            state.dispatch_id
        ),

        authorization_id=(
            authorization_id
        ),

        lease_id=(
            lease_id
        ),

        previous_hash=(
            previous_hash
        ),

        metadata=(
            metadata or {}
        ),
    )

    state.wal.append(
        record
    )

    return record


# ============================================================================
# CHECKPOINT REFRESH
# ============================================================================

def refresh_checkpoint(
    state: DurableState,
) -> Checkpoint:

    validate_wal(
        state.wal
    )

    state.snapshot_sequence += 1

    checkpoint = create_checkpoint(
        sequence=(
            state.snapshot_sequence
        ),

        phase=(
            state.phase
        ),

        generation=(
            state.generation
        ),

        lineage_id=(
            state.lineage_id
        ),

        recovery_epoch=(
            state.recovery_epoch
        ),

        intent_id=(
            state.intent_id
        ),

        dispatch_id=(
            state.dispatch_id
        ),

        wal=(
            state.wal
        ),
    )

    state.checkpoint = (
        checkpoint
    )

    seal_state(
        state
    )

    return checkpoint


# ============================================================================
# RECOVERY LEASE ACQUISITION
# ============================================================================

def acquire_recovery_lease(
    state: DurableState,
    owner_id: str,
) -> RecoveryLease:

    require(
        bool(
            owner_id
        ),
        "recovery owner required",
    )

    require(
        state.phase
        not in TERMINAL_PHASES,
        (
            "terminal generation cannot "
            "acquire recovery lease"
        ),
    )

    if state.active_lease is not None:

        require(
            state.active_lease.owner_id
            == owner_id,
            (
                "recovery lease already "
                "owned by another owner"
            ),
        )

        require(
            state.active_lease.lease_id
            not in state.retired_lease_ids,
            (
                "active recovery lease "
                "already retired"
            ),
        )

        return (
            state.active_lease
        )

    state.lease_nonce += 1

    lease_id = deterministic_id(
        "lease",
        owner_id,
        state.generation,
        state.lineage_id,
        state.recovery_epoch,
        state.lease_nonce,
        state.fence().fingerprint(),
    )

    lease = RecoveryLease(
        lease_id=(
            lease_id
        ),

        owner_id=(
            owner_id
        ),

        generation=(
            state.generation
        ),

        lineage_id=(
            state.lineage_id
        ),

        recovery_epoch=(
            state.recovery_epoch
        ),

        nonce=(
            state.lease_nonce
        ),

        issued_at_ms=(
            now_ms()
        ),

        fence_hash=(
            state.fence()
            .fingerprint()
        ),
    )

    lease.validate()

    state.active_lease = (
        lease
    )

    seal_state(
        state
    )

    return lease


# ============================================================================
# RECOVERY LEASE FENCE VALIDATION
# ============================================================================

def validate_recovery_lease(
    state: DurableState,
    lease: RecoveryLease,
) -> None:

    lease.validate()

    require(
        state.active_lease
        is not None,
        (
            "no active recovery "
            "lease"
        ),
    )

    require(
        state.active_lease.lease_id
        == lease.lease_id,
        (
            "recovery lease "
            "identity mismatch"
        ),
    )

    require(
        state.active_lease.owner_id
        == lease.owner_id,
        (
            "recovery lease "
            "owner mismatch"
        ),
    )

    require(
        lease.generation
        == state.generation,
        (
            "recovery lease generation "
            "mismatch"
        ),
    )

    require(
        lease.lineage_id
        == state.lineage_id,
        (
            "recovery lease lineage "
            "mismatch"
        ),
    )

    require(
        lease.recovery_epoch
        == state.recovery_epoch,
        (
            "recovery lease fence mismatch"
        ),
    )

    require(
        lease.nonce
        == state.lease_nonce,
        (
            "recovery lease nonce "
            "mismatch"
        ),
    )

    require(
        lease.lease_id
        not in state.retired_lease_ids,
        (
            "retired recovery lease "
            "cannot be reused"
        ),
    )

    require(
        hmac.compare_digest(
            lease.fence_hash,
            state.fence().fingerprint(),
        ),
        (
            "recovery lease fence mismatch"
        ),
    )


# ============================================================================
# AUTHORIZATION ISSUANCE
# ============================================================================

def issue_recovery_authorization(
    state: DurableState,
    lease: RecoveryLease,
) -> RecoveryAuthorization:

    validate_recovery_lease(
        state,
        lease,
    )

    require(
        state.phase
        == PHASE_PREPARED,
        (
            "generation is not "
            "prepared"
        ),
    )

    require(
        state.authorization
        is None,
        (
            "authorization already "
            "exists"
        ),
    )

    authorization_id = deterministic_id(
        "authorization",
        lease.lease_id,
        lease.owner_id,
        state.intent_id,
        state.dispatch_id,
        state.generation,
        state.lineage_id,
        state.recovery_epoch,
        lease.nonce,
        EXACT_LEVERAGE_PAYLOAD_HASH,
    )

    authorization = (
        RecoveryAuthorization(
            authorization_id=(
                authorization_id
            ),

            owner_id=(
                lease.owner_id
            ),

            lease_id=(
                lease.lease_id
            ),

            generation=(
                state.generation
            ),

            lineage_id=(
                state.lineage_id
            ),

            recovery_epoch=(
                state.recovery_epoch
            ),

            nonce=(
                lease.nonce
            ),

            intent_id=(
                state.intent_id
            ),

            dispatch_id=(
                state.dispatch_id
            ),

            transport_method=(
                TRANSPORT_METHOD
            ),

            transport_path=(
                LEVERAGE_ENDPOINT
            ),

            payload_hash=(
                EXACT_LEVERAGE_PAYLOAD_HASH
            ),

            issued_at_ms=(
                now_ms()
            ),

            consumed=False,

            consumed_at_ms=None,
        )
    )

    authorization.validate()

    state.authorization = (
        authorization
    )

    state.phase = (
        PHASE_AUTHORIZED
    )

    append_wal_event(
        state,
        WAL_EVENT_AUTHORIZED,
        metadata={
            "authorization_id":
                authorization.authorization_id,

            "lease_id":
                lease.lease_id,
        },
    )

    refresh_checkpoint(
        state
    )

    validate_durable_state(
        state
    )

    return authorization


# ============================================================================
# AUTHORIZATION CONSUMPTION
# ============================================================================

def consume_authorization(
    state: DurableState,
    authorization: RecoveryAuthorization,
    lease: RecoveryLease,
) -> RecoveryAuthorization:

    validate_recovery_lease(
        state,
        lease,
    )

    require(
        state.authorization
        is not None,
        "generation is not authorized",
    )

    require(
        state.phase
        == PHASE_AUTHORIZED,
        (
            "generation is not "
            "authorized"
        ),
    )

    require(
        authorization.authorization_id
        == state.authorization.authorization_id,
        (
            "authorization identity "
            "mismatch"
        ),
    )

    require(
        authorization.lease_id
        == lease.lease_id,
        (
            "authorization lease "
            "mismatch"
        ),
    )

    require(
        authorization.owner_id
        == lease.owner_id,
        (
            "authorization owner "
            "mismatch"
        ),
    )

    require(
        authorization.generation
        == state.generation,
        (
            "authorization generation "
            "mismatch"
        ),
    )

    require(
        authorization.lineage_id
        == state.lineage_id,
        (
            "authorization lineage "
            "mismatch"
        ),
    )

    require(
        authorization.recovery_epoch
        == state.recovery_epoch,
        (
            "authorization recovery "
            "epoch mismatch"
        ),
    )

    require(
        authorization.nonce
        == lease.nonce,
        (
            "authorization lease "
            "nonce mismatch"
        ),
    )

    require(
        authorization.intent_id
        == state.intent_id,
        (
            "authorization intent "
            "mismatch"
        ),
    )

    require(
        authorization.dispatch_id
        == state.dispatch_id,
        (
            "authorization dispatch "
            "mismatch"
        ),
    )

    require(
        authorization.consumed
        is False,
        (
            "authorization already "
            "consumed"
        ),
    )

    require(
        authorization.authorization_id
        not in state.consumed_authorization_ids,
        (
            "authorization replay "
            "rejected"
        ),
    )

    consumed = (
        RecoveryAuthorization(
            authorization_id=(
                authorization.authorization_id
            ),

            owner_id=(
                authorization.owner_id
            ),

            lease_id=(
                authorization.lease_id
            ),

            generation=(
                authorization.generation
            ),

            lineage_id=(
                authorization.lineage_id
            ),

            recovery_epoch=(
                authorization.recovery_epoch
            ),

            nonce=(
                authorization.nonce
            ),

            intent_id=(
                authorization.intent_id
            ),

            dispatch_id=(
                authorization.dispatch_id
            ),

            transport_method=(
                authorization.transport_method
            ),

            transport_path=(
                authorization.transport_path
            ),

            payload_hash=(
                authorization.payload_hash
            ),

            issued_at_ms=(
                authorization.issued_at_ms
            ),

            consumed=True,

            consumed_at_ms=(
                now_ms()
            ),
        )
    )

    consumed.validate()

    state.authorization = (
        consumed
    )

    state.consumed_authorization_ids.add(
        consumed.authorization_id
    )

    return consumed


# ============================================================================
# DISPATCH BINDING PREPARATION
# ============================================================================

def build_dispatch_binding(
    state: DurableState,
) -> DispatchBinding:

    require(
        state.authorization
        is not None,
        (
            "dispatch requires "
            "authorization"
        ),
    )

    require(
        state.authorization.consumed
        is True,
        (
            "dispatch requires consumed "
            "authorization"
        ),
    )

    binding = DispatchBinding(
        dispatch_id=(
            state.dispatch_id
        ),

        intent_id=(
            state.intent_id
        ),

        generation=(
            state.generation
        ),

        lineage_id=(
            state.lineage_id
        ),

        recovery_epoch=(
            state.recovery_epoch
        ),

        transport_method=(
            TRANSPORT_METHOD
        ),

        transport_path=(
            LEVERAGE_ENDPOINT
        ),

        payload=clone(
            EXACT_LEVERAGE_PAYLOAD
        ),

        payload_hash=(
            EXACT_LEVERAGE_PAYLOAD_HASH
        ),
    )

    binding.validate()

    return binding


# ============================================================================
# DURABLE COMMIT TRANSITION
# ============================================================================

def commit_dispatch(
    state: DurableState,
    binding: DispatchBinding,
) -> None:

    binding.validate()

    require(
        state.phase
        == PHASE_AUTHORIZED,
        (
            "dispatch commit requires "
            "AUTHORIZED phase"
        ),
    )

    require(
        state.authorization
        is not None,
        (
            "dispatch commit requires "
            "authorization"
        ),
    )

    require(
        state.authorization.consumed
        is True,
        (
            "dispatch commit requires "
            "consumed authorization"
        ),
    )

    require(
        binding.dispatch_id
        == state.dispatch_id,
        (
            "dispatch binding id "
            "mismatch"
        ),
    )

    require(
        binding.intent_id
        == state.intent_id,
        (
            "dispatch binding intent "
            "mismatch"
        ),
    )

    require(
        binding.generation
        == state.generation,
        (
            "dispatch binding generation "
            "mismatch"
        ),
    )

    require(
        binding.lineage_id
        == state.lineage_id,
        (
            "dispatch binding lineage "
            "mismatch"
        ),
    )

    require(
        binding.recovery_epoch
        == state.recovery_epoch,
        (
            "dispatch binding recovery "
            "epoch mismatch"
        ),
    )

    state.dispatch_binding = (
        clone(
            binding
        )
    )

    state.phase = (
        PHASE_COMMITTED
    )

    append_wal_event(
        state,
        WAL_EVENT_COMMITTED,
        metadata={
            "payload_hash":
                binding.payload_hash,

            "transport_method":
                binding.transport_method,

            "transport_path":
                binding.transport_path,
        },
    )

    refresh_checkpoint(
        state
    )

    validate_durable_state(
        state
    )


# ============================================================================
# SYNTHETIC DISPATCH TRANSITION
# ============================================================================

def execute_synthetic_dispatch(
    state: DurableState,
    transport: SyntheticTransport,
) -> SyntheticReceipt:

    require(
        state.phase
        == PHASE_COMMITTED,
        (
            "synthetic dispatch requires "
            "COMMITTED phase"
        ),
    )

    require(
        state.dispatch_binding
        is not None,
        (
            "synthetic dispatch missing "
            "dispatch binding"
        ),
    )

    require(
        state.dispatch_id
        not in state.completed_dispatch_ids,
        (
            "completed dispatch replay "
            "rejected"
        ),
    )

    receipt = transport.dispatch(
        state.dispatch_binding
    )

    receipt.validate()

    state.receipt = (
        receipt
    )

    state.phase = (
        PHASE_DISPATCHED
    )

    append_wal_event(
        state,
        WAL_EVENT_DISPATCHED,
        metadata={
            "receipt_id":
                receipt.receipt_id,

            "synthetic":
                True,

            "network_write":
                False,
        },
    )

    refresh_checkpoint(
        state
    )

    validate_durable_state(
        state
    )

    return receipt


# ============================================================================
# FINALIZATION TRANSITION
# ============================================================================

def finalize_dispatch(
    state: DurableState,
) -> None:

    require(
        state.phase
        == PHASE_DISPATCHED,
        (
            "finalization requires "
            "DISPATCHED phase"
        ),
    )

    require(
        state.receipt
        is not None,
        (
            "finalization requires "
            "synthetic receipt"
        ),
    )

    require(
        state.dispatch_id
        not in state.completed_dispatch_ids,
        (
            "dispatch already "
            "finalized"
        ),
    )

    state.completed_dispatch_ids.add(
        state.dispatch_id
    )

    state.phase = (
        PHASE_COMPLETED
    )

    if state.active_lease is not None:

        state.retired_lease_ids.add(
            state.active_lease.lease_id
        )

        state.active_lease = None

    append_wal_event(
        state,
        WAL_EVENT_COMPLETED,
        metadata={
            "completed":
                True,

            "dispatch_id":
                state.dispatch_id,
        },
    )

    refresh_checkpoint(
        state
    )

    validate_durable_state(
        state
    )


# ============================================================================
# COMPLETE SYNTHETIC EXECUTION
# ============================================================================

def complete_synthetic_execution(
    state: DurableState,
    transport: SyntheticTransport,
    owner_id: str,
) -> SyntheticReceipt:

    validate_durable_state(
        state
    )

    lease = acquire_recovery_lease(
        state,
        owner_id,
    )

    authorization = (
        issue_recovery_authorization(
            state,
            lease,
        )
    )

    consume_authorization(
        state,
        authorization,
        lease,
    )

    binding = build_dispatch_binding(
        state
    )

    commit_dispatch(
        state,
        binding,
    )

    receipt = execute_synthetic_dispatch(
        state,
        transport,
    )

    finalize_dispatch(
        state
    )

    assert_transport_firebreak(
        transport
    )

    return receipt


# ============================================================================
# END OF PART 2
# ============================================================================

print(
    "R28 UNIT N.27: PART 2 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.27
# DURABLE WAL RECOVERY + CHECKPOINT BINDING + RESTART-SAFE FINALITY
#
# CORRECTED COPY/PASTE VERSION
# PART 3 OF 4
#
# IMPORTANT:
#   - PASTE DIRECTLY BELOW PART 2
#   - FIRST LINE MUST START AT COLUMN ZERO
#   - THIS PART DEFINES RESTART / RECOVERY / CORRUPTION TEST SUPPORT
# ============================================================================


# ============================================================================
# SNAPSHOT CLONE / RESTORE
# ============================================================================

def snapshot_state(
    state: DurableState,
) -> DurableState:

    validate_durable_state(
        state
    )

    snapshot = clone(
        state
    )

    validate_durable_state(
        snapshot
    )

    return snapshot


def restore_state(
    snapshot: DurableState,
) -> DurableState:

    restored = clone(
        snapshot
    )

    validate_durable_state(
        restored
    )

    return restored


# ============================================================================
# REBUILD CHECKPOINT AFTER VALID WAL
# ============================================================================

def rebuild_checkpoint_from_wal(
    state: DurableState,
) -> None:

    validate_wal(
        state.wal
    )

    state.snapshot_sequence += 1

    state.checkpoint = create_checkpoint(
        sequence=(
            state.snapshot_sequence
        ),

        phase=(
            state.phase
        ),

        generation=(
            state.generation
        ),

        lineage_id=(
            state.lineage_id
        ),

        recovery_epoch=(
            state.recovery_epoch
        ),

        intent_id=(
            state.intent_id
        ),

        dispatch_id=(
            state.dispatch_id
        ),

        wal=(
            state.wal
        ),
    )

    seal_state(
        state
    )


# ============================================================================
# RECOVERY ENGINE
# ============================================================================

def recover_execution(
    snapshot: DurableState,
    transport: SyntheticTransport,
    owner_id: str,
) -> DurableState:

    state = restore_state(
        snapshot
    )

    validate_durable_state(
        state
    )

    # ========================================================================
    # TERMINAL FINALITY
    # ========================================================================

    if state.phase in TERMINAL_PHASES:

        require(
            state.dispatch_id
            in state.completed_dispatch_ids,
            (
                "terminal recovery missing "
                "completed dispatch"
            ),
        )

        assert_transport_firebreak(
            transport
        )

        return state

    # ========================================================================
    # PREPARED
    # ========================================================================

    if state.phase == PHASE_PREPARED:

        complete_synthetic_execution(
            state,
            transport,
            owner_id,
        )

        return state

    # ========================================================================
    # AUTHORIZED
    # ========================================================================

    if state.phase == PHASE_AUTHORIZED:

        require(
            state.authorization
            is not None,
            (
                "authorized recovery missing "
                "authorization"
            ),
        )

        lease = (
            state.active_lease
        )

        require(
            lease is not None,
            (
                "authorized recovery missing "
                "active lease"
            ),
        )

        validate_recovery_lease(
            state,
            lease,
        )

        if not state.authorization.consumed:

            consume_authorization(
                state,
                state.authorization,
                lease,
            )

        binding = build_dispatch_binding(
            state
        )

        commit_dispatch(
            state,
            binding,
        )

        execute_synthetic_dispatch(
            state,
            transport,
        )

        finalize_dispatch(
            state
        )

        return state

    # ========================================================================
    # COMMITTED
    # ========================================================================

    if state.phase == PHASE_COMMITTED:

        require(
            state.dispatch_binding
            is not None,
            (
                "committed recovery missing "
                "dispatch binding"
            ),
        )

        execute_synthetic_dispatch(
            state,
            transport,
        )

        finalize_dispatch(
            state
        )

        return state

    # ========================================================================
    # DISPATCHED
    # ========================================================================

    if state.phase == PHASE_DISPATCHED:

        require(
            state.receipt
            is not None,
            (
                "dispatched recovery missing "
                "receipt"
            ),
        )

        finalize_dispatch(
            state
        )

        return state

    raise ValueError(
        "unsupported recovery phase"
    )


# ============================================================================
# GENERATION ADVANCE
# ============================================================================

def advance_generation(
    state: DurableState,
) -> DurableState:

    validate_durable_state(
        state
    )

    require(
        state.phase
        in TERMINAL_PHASES,
        (
            "new generation requires "
            "terminal prior generation"
        ),
    )

    next_generation = (
        state.generation + 1
    )

    next_recovery_epoch = (
        state.recovery_epoch + 1
    )

    next_lineage = secure_id(
        "lineage"
    )

    next_intent = deterministic_id(
        "intent",
        SYMBOL,
        next_generation,
        next_lineage,
        next_recovery_epoch,
        EXACT_LEVERAGE_PAYLOAD_HASH,
    )

    next_dispatch = deterministic_id(
        "dispatch",
        next_intent,
        next_generation,
        next_lineage,
        next_recovery_epoch,
    )

    record = create_wal_record(
        sequence=1,

        event=(
            WAL_EVENT_PREPARED
        ),

        generation=(
            next_generation
        ),

        lineage_id=(
            next_lineage
        ),

        recovery_epoch=(
            next_recovery_epoch
        ),

        intent_id=(
            next_intent
        ),

        dispatch_id=(
            next_dispatch
        ),

        authorization_id=None,
        lease_id=None,

        previous_hash=(
            GENESIS_WAL_HASH
        ),

        metadata={
            "phase":
                PHASE_PREPARED,

            "prior_generation":
                state.generation,

            "prior_dispatch_id":
                state.dispatch_id,
        },
    )

    next_state = DurableState(
        schema_version=(
            STATE_SCHEMA_VERSION
        ),

        phase=(
            PHASE_PREPARED
        ),

        account_epoch=(
            state.account_epoch
        ),

        symbol_epoch=(
            state.symbol_epoch
        ),

        position_epoch=(
            state.position_epoch
        ),

        recovery_epoch=(
            next_recovery_epoch
        ),

        generation=(
            next_generation
        ),

        lineage_id=(
            next_lineage
        ),

        intent_id=(
            next_intent
        ),

        dispatch_id=(
            next_dispatch
        ),

        lease_nonce=0,

        active_lease=None,

        authorization=None,

        dispatch_binding=None,

        receipt=None,

        wal=[
            record
        ],

        checkpoint=None,

        completed_dispatch_ids=set(
            state.completed_dispatch_ids
        ),

        consumed_authorization_ids=set(
            state.consumed_authorization_ids
        ),

        retired_lease_ids=set(
            state.retired_lease_ids
        ),

        snapshot_sequence=(
            state.snapshot_sequence + 1
        ),

        integrity_seal="",
    )

    next_state.checkpoint = create_checkpoint(
        sequence=(
            next_state.snapshot_sequence
        ),

        phase=(
            next_state.phase
        ),

        generation=(
            next_state.generation
        ),

        lineage_id=(
            next_state.lineage_id
        ),

        recovery_epoch=(
            next_state.recovery_epoch
        ),

        intent_id=(
            next_state.intent_id
        ),

        dispatch_id=(
            next_state.dispatch_id
        ),

        wal=(
            next_state.wal
        ),
    )

    seal_state(
        next_state
    )

    validate_durable_state(
        next_state
    )

    return next_state


# ============================================================================
# TEST OUTPUT HELPERS
# ============================================================================

TEST_SEPARATOR = (
    "-" * 92
)


def print_test_header(
    number: int,
    title: str,
) -> None:

    print(
        "",
        flush=True,
    )

    print(
        (
            f"{UNIT_NAME} TEST "
            f"{number}: {title}"
        ),
        flush=True,
    )

    print(
        TEST_SEPARATOR,
        flush=True,
    )


def pass_check(
    label: str,
    condition: bool,
) -> None:

    require(
        condition,
        label,
    )

    print(
        f"{label:<80} ✅ PASS",
        flush=True,
    )


def expect_rejection(
    label: str,
    operation: Any,
) -> None:

    rejected = False

    try:
        operation()

    except (
        ValueError,
        TypeError,
        AssertionError,
    ) as exc:

        rejected = True

        local_block(
            str(
                exc
            )
        )

    pass_check(
        label,
        rejected,
    )


# ============================================================================
# TEST 1
# INITIAL STATE + CHECKPOINT / WAL BINDING
# ============================================================================

def test_initial_state(
) -> None:

    print_test_header(
        1,
        (
            "INITIAL DURABLE STATE "
            "AND WAL BINDING"
        ),
    )

    state = create_initial_state()

    pass_check(
        "Initial Phase Is PREPARED",
        (
            state.phase
            == PHASE_PREPARED
        ),
    )

    pass_check(
        "Initial WAL Has One Record",
        (
            len(
                state.wal
            )
            == 1
        ),
    )

    pass_check(
        "Initial WAL Begins At Sequence One",
        (
            state.wal[0].sequence
            == 1
        ),
    )

    pass_check(
        "Initial WAL Previous Hash Is Genesis",
        (
            state.wal[0].previous_hash
            == GENESIS_WAL_HASH
        ),
    )

    pass_check(
        "Initial Checkpoint Present",
        (
            state.checkpoint
            is not None
        ),
    )

    pass_check(
        "Checkpoint WAL Length Preserved",
        (
            state.checkpoint is not None
            and
            state.checkpoint.wal_length
            == len(
                state.wal
            )
        ),
    )

    pass_check(
        "Checkpoint WAL Final Hash Preserved",
        (
            state.checkpoint is not None
            and
            state.checkpoint.wal_final_hash
            == wal_final_hash(
                state.wal
            )
        ),
    )


# ============================================================================
# TEST 2
# COMPLETE SYNTHETIC EXECUTION
# ============================================================================

def test_complete_execution(
) -> None:

    print_test_header(
        2,
        (
            "COMPLETE EXACTLY-ONCE "
            "SYNTHETIC EXECUTION"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    receipt = complete_synthetic_execution(
        state,
        transport,
        "worker-test-2",
    )

    pass_check(
        "Execution Reached COMPLETED",
        (
            state.phase
            == PHASE_COMPLETED
        ),
    )

    pass_check(
        "Exactly One Synthetic Dispatch",
        (
            transport.dispatch_count
            == 1
        ),
    )

    pass_check(
        "Synthetic Receipt Was Not Transmitted",
        (
            receipt.transmitted
            is False
        ),
    )

    pass_check(
        "Synthetic Receipt Has No Network Write",
        (
            receipt.network_write
            is False
        ),
    )

    pass_check(
        "Dispatch Finality Fence Recorded",
        (
            state.dispatch_id
            in state.completed_dispatch_ids
        ),
    )

    pass_check(
        "Final WAL Event Is COMPLETED",
        (
            state.wal[-1].event
            == WAL_EVENT_COMPLETED
        ),
    )

    assert_transport_firebreak(
        transport
    )


# ============================================================================
# TEST 3
# WAL HASH CHAIN
# ============================================================================

def test_wal_hash_chain(
) -> None:

    print_test_header(
        3,
        "WAL HASH-CHAIN VALIDATION",
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    complete_synthetic_execution(
        state,
        transport,
        "worker-test-3",
    )

    validate_wal(
        state.wal
    )

    pass_check(
        "WAL Records Validate",
        True,
    )

    chain_valid = True

    previous = (
        GENESIS_WAL_HASH
    )

    for record in state.wal:

        if (
            record.previous_hash
            != previous
        ):
            chain_valid = False
            break

        previous = (
            record.record_hash
        )

    pass_check(
        "WAL Previous Hash Chain Preserved",
        chain_valid,
    )

    pass_check(
        "WAL Final Hash Matches Checkpoint",
        (
            state.checkpoint is not None
            and
            state.checkpoint.wal_final_hash
            == wal_final_hash(
                state.wal
            )
        ),
    )


# ============================================================================
# TEST 4
# RESTART AFTER PREPARED
# ============================================================================

def test_restart_prepared(
) -> None:

    print_test_header(
        4,
        (
            "RESTART FROM PREPARED "
            "TO SINGLE FINAL DISPATCH"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    snapshot = snapshot_state(
        state
    )

    recovered = recover_execution(
        snapshot,
        transport,
        "worker-restart-prepared",
    )

    pass_check(
        "Prepared Recovery Completed",
        (
            recovered.phase
            == PHASE_COMPLETED
        ),
    )

    pass_check(
        "Prepared Recovery Produced Exactly One Dispatch",
        (
            transport.dispatch_count
            == 1
        ),
    )

    pass_check(
        "Prepared Recovery Finality Preserved",
        (
            recovered.dispatch_id
            in recovered.completed_dispatch_ids
        ),
    )


# ============================================================================
# TEST 5
# RESTART AFTER AUTHORIZATION
# ============================================================================

def test_restart_authorized(
) -> None:

    print_test_header(
        5,
        (
            "RESTART AFTER AUTHORIZATION "
            "WITH SINGLE CONSUMPTION"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    lease = acquire_recovery_lease(
        state,
        "worker-auth-crash",
    )

    authorization = issue_recovery_authorization(
        state,
        lease,
    )

    snapshot = snapshot_state(
        state
    )

    recovered = recover_execution(
        snapshot,
        transport,
        "worker-auth-crash",
    )

    pass_check(
        "Authorized Recovery Completed",
        (
            recovered.phase
            == PHASE_COMPLETED
        ),
    )

    pass_check(
        "Authorized Recovery Produced Exactly One Dispatch",
        (
            transport.dispatch_count
            == 1
        ),
    )

    pass_check(
        "Authorization Consumed Exactly Once",
        (
            authorization.authorization_id
            in recovered.consumed_authorization_ids
        ),
    )


# ============================================================================
# TEST 6
# RESTART AFTER COMMIT
# ============================================================================

def test_restart_committed(
) -> None:

    print_test_header(
        6,
        (
            "RESTART AFTER COMMIT "
            "BEFORE SYNTHETIC DISPATCH"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    lease = acquire_recovery_lease(
        state,
        "worker-commit-crash",
    )

    authorization = issue_recovery_authorization(
        state,
        lease,
    )

    consume_authorization(
        state,
        authorization,
        lease,
    )

    binding = build_dispatch_binding(
        state
    )

    commit_dispatch(
        state,
        binding,
    )

    snapshot = snapshot_state(
        state
    )

    recovered = recover_execution(
        snapshot,
        transport,
        "worker-commit-crash",
    )

    pass_check(
        "Committed Recovery Completed",
        (
            recovered.phase
            == PHASE_COMPLETED
        ),
    )

    pass_check(
        "Committed Recovery Produced Exactly One Dispatch",
        (
            transport.dispatch_count
            == 1
        ),
    )


# ============================================================================
# TEST 7
# RESTART AFTER DISPATCH BEFORE FINALIZATION
# ============================================================================

def test_restart_dispatched(
) -> None:

    print_test_header(
        7,
        (
            "RESTART AFTER DISPATCH "
            "BEFORE FINALIZATION"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    lease = acquire_recovery_lease(
        state,
        "worker-dispatch-crash",
    )

    authorization = issue_recovery_authorization(
        state,
        lease,
    )

    consume_authorization(
        state,
        authorization,
        lease,
    )

    binding = build_dispatch_binding(
        state
    )

    commit_dispatch(
        state,
        binding,
    )

    execute_synthetic_dispatch(
        state,
        transport,
    )

    pass_check(
        "Pre-Crash Synthetic Dispatch Count Is One",
        (
            transport.dispatch_count
            == 1
        ),
    )

    snapshot = snapshot_state(
        state
    )

    recovered = recover_execution(
        snapshot,
        transport,
        "worker-dispatch-crash",
    )

    pass_check(
        "Dispatched Recovery Completed",
        (
            recovered.phase
            == PHASE_COMPLETED
        ),
    )

    pass_check(
        "Dispatched Recovery Produced No Second Dispatch",
        (
            transport.dispatch_count
            == 1
        ),
    )


# ============================================================================
# TEST 8
# TERMINAL RESTART IDEMPOTENCY
# ============================================================================

def test_terminal_restart(
) -> None:

    print_test_header(
        8,
        (
            "TERMINAL RESTART "
            "IDEMPOTENCY"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    complete_synthetic_execution(
        state,
        transport,
        "worker-terminal",
    )

    snapshot = snapshot_state(
        state
    )

    restored = recover_execution(
        snapshot,
        transport,
        "worker-terminal-restart",
    )

    pass_check(
        "Terminal Recovery Remains COMPLETED",
        (
            restored.phase
            == PHASE_COMPLETED
        ),
    )

    pass_check(
        "Terminal Recovery Produced No Second Dispatch",
        (
            transport.dispatch_count
            == 1
        ),
    )

    pass_check(
        "Terminal Dispatch Finality Preserved",
        (
            restored.dispatch_id
            in restored.completed_dispatch_ids
        ),
    )


# ============================================================================
# TEST 9
# TORN WAL TAIL REJECTION
# ============================================================================

def test_torn_wal_tail(
) -> None:

    print_test_header(
        9,
        "TORN WAL TAIL REJECTION",
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    complete_synthetic_execution(
        state,
        transport,
        "worker-torn-tail",
    )

    damaged = clone(
        state
    )

    tail = damaged.wal[-1]

    damaged.wal[-1] = WALRecord(
        sequence=(
            tail.sequence
        ),

        event=(
            tail.event
        ),

        timestamp_ms=(
            tail.timestamp_ms
        ),

        generation=(
            tail.generation
        ),

        lineage_id=(
            tail.lineage_id
        ),

        recovery_epoch=(
            tail.recovery_epoch
        ),

        intent_id=(
            tail.intent_id
        ),

        dispatch_id=(
            tail.dispatch_id
        ),

        authorization_id=(
            tail.authorization_id
        ),

        lease_id=(
            tail.lease_id
        ),

        payload_hash=(
            tail.payload_hash
        ),

        previous_hash=(
            tail.previous_hash
        ),

        record_hash=(
            tail.record_hash[:-1]
            + (
                "0"
                if tail.record_hash[-1]
                != "0"
                else "1"
            )
        ),

        metadata=clone(
            tail.metadata
        ),
    )

    damaged.integrity_seal = (
        calculate_state_integrity_seal(
            damaged
        )
    )

    expect_rejection(
        "Torn WAL Tail Rejected",
        lambda: restore_state(
            damaged
        ),
    )


# ============================================================================
# TEST 10
# HISTORICAL WAL RECORD TAMPER REJECTION
# ============================================================================

def test_historical_wal_tamper(
) -> None:

    print_test_header(
        10,
        (
            "HISTORICAL WAL RECORD "
            "TAMPER REJECTION"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    complete_synthetic_execution(
        state,
        transport,
        "worker-wal-history",
    )

    damaged = clone(
        state
    )

    original = damaged.wal[0]

    damaged.wal[0] = WALRecord(
        sequence=(
            original.sequence
        ),

        event=(
            original.event
        ),

        timestamp_ms=(
            original.timestamp_ms
        ),

        generation=(
            original.generation
        ),

        lineage_id=(
            original.lineage_id
        ),

        recovery_epoch=(
            original.recovery_epoch
        ),

        intent_id=(
            original.intent_id
        ),

        dispatch_id=(
            original.dispatch_id
        ),

        authorization_id=(
            original.authorization_id
        ),

        lease_id=(
            original.lease_id
        ),

        payload_hash=(
            original.payload_hash
        ),

        previous_hash=(
            original.previous_hash
        ),

        record_hash=(
            original.record_hash
        ),

        metadata={
            **clone(
                original.metadata
            ),
            "tampered": True,
        },
    )

    damaged.integrity_seal = (
        calculate_state_integrity_seal(
            damaged
        )
    )

    expect_rejection(
        "Historical WAL Tamper Rejected",
        lambda: restore_state(
            damaged
        ),
    )


# ============================================================================
# TEST 11
# CHECKPOINT TAMPER REJECTION
# ============================================================================

def test_checkpoint_tamper(
) -> None:

    print_test_header(
        11,
        "CHECKPOINT TAMPER REJECTION",
    )

    state = create_initial_state()

    require(
        state.checkpoint
        is not None,
        "checkpoint missing",
    )

    damaged = clone(
        state
    )

    checkpoint = (
        damaged.checkpoint
    )

    require(
        checkpoint
        is not None,
        "checkpoint missing",
    )

    damaged.checkpoint = Checkpoint(
        schema_version=(
            checkpoint.schema_version
        ),

        checkpoint_id=(
            checkpoint.checkpoint_id
        ),

        sequence=(
            checkpoint.sequence
        ),

        phase=(
            checkpoint.phase
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

        intent_id=(
            checkpoint.intent_id
        ),

        dispatch_id=(
            checkpoint.dispatch_id
        ),

        wal_length=(
            checkpoint.wal_length
        ),

        wal_final_hash=(
            checkpoint.wal_final_hash
        ),

        created_at_ms=(
            checkpoint.created_at_ms
        ),

        integrity_seal=(
            checkpoint.integrity_seal[:-1]
            + (
                "0"
                if checkpoint.integrity_seal[-1]
                != "0"
                else "1"
            )
        ),
    )

    damaged.integrity_seal = (
        calculate_state_integrity_seal(
            damaged
        )
    )

    expect_rejection(
        "Tampered Checkpoint Rejected",
        lambda: restore_state(
            damaged
        ),
    )


# ============================================================================
# TEST 12
# STALE CHECKPOINT REJECTION
# ============================================================================

def test_stale_checkpoint(
) -> None:

    print_test_header(
        12,
        "STALE CHECKPOINT REJECTION",
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    old_checkpoint = clone(
        state.checkpoint
    )

    lease = acquire_recovery_lease(
        state,
        "worker-stale-checkpoint",
    )

    issue_recovery_authorization(
        state,
        lease,
    )

    damaged = clone(
        state
    )

    damaged.checkpoint = (
        old_checkpoint
    )

    damaged.integrity_seal = (
        calculate_state_integrity_seal(
            damaged
        )
    )

    expect_rejection(
        "Stale Checkpoint Rejected",
        lambda: restore_state(
            damaged
        ),
    )


# ============================================================================
# TEST 13
# CHECKPOINT WAL HASH MISMATCH
# ============================================================================

def test_checkpoint_wal_hash_mismatch(
) -> None:

    print_test_header(
        13,
        (
            "CHECKPOINT TO WAL "
            "FINAL HASH MISMATCH"
        ),
    )

    state = create_initial_state()

    damaged = clone(
        state
    )

    checkpoint = (
        damaged.checkpoint
    )

    require(
        checkpoint
        is not None,
        "checkpoint missing",
    )

    provisional = Checkpoint(
        schema_version=(
            checkpoint.schema_version
        ),

        checkpoint_id=(
            checkpoint.checkpoint_id
        ),

        sequence=(
            checkpoint.sequence
        ),

        phase=(
            checkpoint.phase
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

        intent_id=(
            checkpoint.intent_id
        ),

        dispatch_id=(
            checkpoint.dispatch_id
        ),

        wal_length=(
            checkpoint.wal_length
        ),

        wal_final_hash=(
            "f" * 64
        ),

        created_at_ms=(
            checkpoint.created_at_ms
        ),

        integrity_seal="",
    )

    damaged.checkpoint = Checkpoint(
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
            provisional.calculate_integrity_seal()
        ),
    )

    damaged.integrity_seal = (
        calculate_state_integrity_seal(
            damaged
        )
    )

    expect_rejection(
        "Checkpoint WAL Hash Mismatch Rejected",
        lambda: restore_state(
            damaged
        ),
    )


# ============================================================================
# TEST 14
# GENERATION ADVANCE + ANTI-ABA
# ============================================================================

def test_generation_advance(
) -> None:

    print_test_header(
        14,
        (
            "GENERATION ADVANCE "
            "AND ANTI-ABA FENCING"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    lease = acquire_recovery_lease(
        state,
        "worker-generation-a",
    )

    old_lease = clone(
        lease
    )

    complete_authorization = (
        issue_recovery_authorization(
            state,
            lease,
        )
    )

    consume_authorization(
        state,
        complete_authorization,
        lease,
    )

    binding = build_dispatch_binding(
        state
    )

    commit_dispatch(
        state,
        binding,
    )

    execute_synthetic_dispatch(
        state,
        transport,
    )

    finalize_dispatch(
        state
    )

    next_state = advance_generation(
        state
    )

    pass_check(
        "Generation Advanced Monotonically",
        (
            next_state.generation
            > state.generation
        ),
    )

    pass_check(
        "Recovery Epoch Advanced Monotonically",
        (
            next_state.recovery_epoch
            > state.recovery_epoch
        ),
    )

    pass_check(
        "New Generation Uses Different Lineage",
        (
            next_state.lineage_id
            != state.lineage_id
        ),
    )

    pass_check(
        "New Generation Returns To PREPARED",
        (
            next_state.phase
            == PHASE_PREPARED
        ),
    )

    pass_check(
        "Prior Completed Dispatch Preserved",
        (
            state.dispatch_id
            in next_state.completed_dispatch_ids
        ),
    )

    expect_rejection(
        "Prior Generation Lease Rejected",
        lambda: validate_recovery_lease(
            next_state,
            old_lease,
        ),
    )


# ============================================================================
# TEST 15
# REUSED OWNER ANTI-ABA
# ============================================================================

def test_owner_reuse_anti_aba(
) -> None:

    print_test_header(
        15,
        (
            "OWNER REUSE ACROSS "
            "GENERATION LINEAGE"
        ),
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    owner = (
        "worker-reused-owner"
    )

    first_lease = acquire_recovery_lease(
        state,
        owner,
    )

    authorization = issue_recovery_authorization(
        state,
        first_lease,
    )

    consume_authorization(
        state,
        authorization,
        first_lease,
    )

    binding = build_dispatch_binding(
        state
    )

    commit_dispatch(
        state,
        binding,
    )

    execute_synthetic_dispatch(
        state,
        transport,
    )

    finalize_dispatch(
        state
    )

    next_state = advance_generation(
        state
    )

    second_lease = acquire_recovery_lease(
        next_state,
        owner,
    )

    pass_check(
        "Reacquired Owner Uses Higher Generation",
        (
            second_lease.generation
            > first_lease.generation
        ),
    )

    pass_check(
        "Reacquired Owner Uses Different Lineage",
        (
            second_lease.lineage_id
            != first_lease.lineage_id
        ),
    )

    pass_check(
        "Reacquired Owner Uses Higher Epoch",
        (
            second_lease.recovery_epoch
            > first_lease.recovery_epoch
        ),
    )

    pass_check(
        "Reused Owner Cannot Resurrect Prior Lease",
        (
            second_lease.lease_id
            != first_lease.lease_id
        ),
    )


# ============================================================================
# TEST 16
# EXACT TRANSPORT BINDING
# ============================================================================

def test_exact_transport_binding(
) -> None:

    print_test_header(
        16,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    state = create_initial_state()

    lease = acquire_recovery_lease(
        state,
        "worker-binding",
    )

    authorization = issue_recovery_authorization(
        state,
        lease,
    )

    consume_authorization(
        state,
        authorization,
        lease,
    )

    binding = build_dispatch_binding(
        state
    )

    pass_check(
        "Transport Method Exactly POST",
        (
            binding.transport_method
            == "POST"
        ),
    )

    pass_check(
        "Transport Path Exactly Leverage Endpoint",
        (
            binding.transport_path
            == LEVERAGE_ENDPOINT
        ),
    )

    pass_check(
        "Transport Payload Hash Preserved",
        (
            binding.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH
        ),
    )

    pass_check(
        "Transport Payload Exactly Preserved",
        (
            canonical_json(
                binding.payload
            )
            == EXACT_LEVERAGE_PAYLOAD_JSON
        ),
    )


# ============================================================================
# TEST 17
# FINAL NETWORK-WRITE FIREBREAK
# ============================================================================

def test_final_firebreak(
) -> None:

    print_test_header(
        17,
        "FINAL NETWORK WRITE FIREBREAK",
    )

    transport = (
        SyntheticTransport()
    )

    state = create_initial_state()

    complete_synthetic_execution(
        state,
        transport,
        "worker-firebreak",
    )

    assert_transport_firebreak(
        transport
    )

    pass_check(
        "Live Execution Disabled",
        (
            LIVE_ORDER_EXECUTION
            is False
        ),
    )

    pass_check(
        "Demo Execution Disabled",
        (
            DEMO_ORDER_EXECUTION
            is False
        ),
    )

    pass_check(
        "Network Writes Disabled",
        (
            NETWORK_WRITES_ENABLED
            is False
        ),
    )

    pass_check(
        "Real POST Disabled",
        (
            REAL_POST_ENABLED
            is False
        ),
    )

    pass_check(
        "Demo POST Disabled",
        (
            DEMO_POST_ENABLED
            is False
        ),
    )

    pass_check(
        "Synthetic Transport Only",
        (
            SYNTHETIC_TRANSPORT_ONLY
            is True
        ),
    )

    pass_check(
        "Network Write Count Remains Zero",
        (
            transport.network_write_count
            == 0
        ),
    )

    pass_check(
        "Real POST Count Remains Zero",
        (
            transport.real_post_count
            == 0
        ),
    )

    pass_check(
        "Demo POST Count Remains Zero",
        (
            transport.demo_post_count
            == 0
        ),
    )


# ============================================================================
# DIAGNOSTIC TEST RUNNER
# ============================================================================

def run_diagnostic(
) -> None:

    print(
        "",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    print(
        (
            "R28 UNIT N.27 "
            "DIAGNOSTIC START"
        ),
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    test_initial_state()
    test_complete_execution()
    test_wal_hash_chain()
    test_restart_prepared()
    test_restart_authorized()
    test_restart_committed()
    test_restart_dispatched()
    test_terminal_restart()
    test_torn_wal_tail()
    test_historical_wal_tamper()
    test_checkpoint_tamper()
    test_stale_checkpoint()
    test_checkpoint_wal_hash_mismatch()
    test_generation_advance()
    test_owner_reuse_anti_aba()
    test_exact_transport_binding()
    test_final_firebreak()

    print(
        "",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    print(
        (
            "✅ R28 UNIT N.27 PASSED — "
            "DURABLE WAL + CHECKPOINT "
            "RECOVERY VALIDATED"
        ),
        flush=True,
    )

    print(
        (
            "✅ NO REAL ORDER WAS SENT — "
            "NO DEMO ORDER WAS SENT — "
            "NO NETWORK WRITE OCCURRED"
        ),
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )


# ============================================================================
# END OF PART 3
# ============================================================================

print(
    "R28 UNIT N.27: PART 3 DEFINITIONS LOADED",
    flush=True,
)
