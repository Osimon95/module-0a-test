# ============================================================================
# R28 UNIT N.24
# DURABLE DISPATCH COMMIT + CRASH-WINDOW RECOVERY + EXACTLY-ONCE FENCING
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
# N.24 INCREMENT OVER N.23:
#   - DURABLE DISPATCH COMMIT RECORD
#   - PRE-COMMIT CRASH RECOVERY
#   - POST-COMMIT / PRE-DISPATCH CRASH RECOVERY
#   - POST-DISPATCH / PRE-FINALIZATION CRASH RECOVERY MODEL
#   - EXACTLY-ONCE SYNTHETIC DISPATCH FENCING
#   - COMMIT IDENTITY / GENERATION / LINEAGE / EPOCH BINDING
#   - ANTI-ABA COMMIT REJECTION
# ============================================================================

print("R28 UNIT N.24: MAIN.PY ENTERED", flush=True)

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


print("R28 UNIT N.24: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.24"
UNIT_VERSION = "N.24"

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

HEALTH_PORT = int(
    os.environ.get(
        "PORT",
        "10000",
    )
)

STATE_SCHEMA_VERSION = 24

DEFAULT_ACCOUNT_EPOCH = 1
DEFAULT_SYMBOL_EPOCH = 1
DEFAULT_POSITION_EPOCH = 1
DEFAULT_RECOVERY_EPOCH = 1
DEFAULT_GENERATION = 1

MAX_RECOVERY_ATTEMPTS = 64

SYNTHETIC_RECEIPT_STATUS = (
    "SYNTHETIC_NO_TRANSMISSION"
)

COMMIT_STATUS_PREPARED = "PREPARED"
COMMIT_STATUS_COMMITTED = "COMMITTED"
COMMIT_STATUS_DISPATCHED = "DISPATCHED"
COMMIT_STATUS_FINALIZED = "FINALIZED"

VALID_COMMIT_STATUSES = {
    COMMIT_STATUS_PREPARED,
    COMMIT_STATUS_COMMITTED,
    COMMIT_STATUS_DISPATCHED,
    COMMIT_STATUS_FINALIZED,
}

TERMINAL_STATES = {
    "COMPLETED",
    "REJECTED",
    "CANCELED",
    "FAILED",
    "EXPIRED",
}

NON_TERMINAL_STATES = {
    "PREPARED",
    "AUTHORIZED",
    "DISPATCH_PREPARED",
    "DISPATCH_COMMITTED",
    "DISPATCH_INFLIGHT",
}

ALL_STATES = (
    TERMINAL_STATES
    | NON_TERMINAL_STATES
)


print(
    "R28 UNIT N.24: CONSTANTS INITIALIZED",
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
        canonical_json(value)
    )


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
            bool(self.lineage_id),
            "lineage id required",
        )

    def fingerprint(
        self,
    ) -> str:
        self.validate()

        return sha256_json(
            asdict(self)
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
            bool(self.lease_id),
            "lease id required",
        )

        require(
            bool(self.owner_id),
            "lease owner required",
        )

        require(
            self.generation > 0,
            "lease generation must be positive",
        )

        require(
            bool(self.lineage_id),
            "lease lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "lease recovery epoch must be positive",
        )

        require(
            self.nonce > 0,
            "lease nonce must be positive",
        )

        require(
            self.issued_at_ms > 0,
            "lease issued timestamp invalid",
        )

        require(
            bool(self.fence_hash),
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
            bool(self.authorization_id),
            "authorization id required",
        )

        require(
            bool(self.owner_id),
            "authorization owner required",
        )

        require(
            bool(self.lease_id),
            "authorization lease required",
        )

        require(
            self.generation > 0,
            "authorization generation must be positive",
        )

        require(
            bool(self.lineage_id),
            "authorization lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "authorization recovery epoch must be positive",
        )

        require(
            self.nonce > 0,
            "authorization nonce must be positive",
        )

        require(
            bool(self.intent_id),
            "authorization intent required",
        )

        require(
            bool(self.dispatch_id),
            "authorization dispatch required",
        )

        require(
            self.transport_method
            == TRANSPORT_METHOD,
            "authorization transport method mismatch",
        )

        require(
            self.transport_path
            == LEVERAGE_ENDPOINT,
            "authorization transport path mismatch",
        )

        require(
            self.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            "authorization payload hash mismatch",
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
            bool(self.dispatch_id),
            "dispatch id required",
        )

        require(
            bool(self.intent_id),
            "intent id required",
        )

        require(
            self.generation > 0,
            "dispatch generation must be positive",
        )

        require(
            bool(self.lineage_id),
            "dispatch lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "dispatch recovery epoch must be positive",
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
# N.24 DURABLE DISPATCH COMMIT
#
# This is the major new state object introduced by Unit N.24.
#
# The commit is separate from:
#   1. Authorization
#   2. Dispatch binding
#   3. Synthetic transport receipt
#
# This allows restart recovery to distinguish:
#
#   AUTHORIZED
#       ↓
#   DISPATCH_PREPARED
#       ↓
#   COMMIT DURABLY WRITTEN
#       ↓
#   SYNTHETIC TRANSPORT
#       ↓
#   FINALIZED
#
# A transport operation is forbidden unless a matching durable commit exists.
# ============================================================================

@dataclass(frozen=True)
class DispatchCommit:
    commit_id: str

    authorization_id: str
    lease_id: str
    owner_id: str

    intent_id: str
    dispatch_id: str

    generation: int
    lineage_id: str
    recovery_epoch: int

    lease_nonce: int

    transport_method: str
    transport_path: str
    payload_hash: str

    fence_hash: str

    status: str

    committed_at_ms: int

    dispatched_at_ms: Optional[int] = None
    finalized_at_ms: Optional[int] = None

    def validate(
        self,
    ) -> None:
        require(
            bool(self.commit_id),
            "dispatch commit id required",
        )

        require(
            bool(self.authorization_id),
            "dispatch commit authorization required",
        )

        require(
            bool(self.lease_id),
            "dispatch commit lease required",
        )

        require(
            bool(self.owner_id),
            "dispatch commit owner required",
        )

        require(
            bool(self.intent_id),
            "dispatch commit intent required",
        )

        require(
            bool(self.dispatch_id),
            "dispatch commit dispatch id required",
        )

        require(
            self.generation > 0,
            "dispatch commit generation invalid",
        )

        require(
            bool(self.lineage_id),
            "dispatch commit lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "dispatch commit recovery epoch invalid",
        )

        require(
            self.lease_nonce > 0,
            "dispatch commit lease nonce invalid",
        )

        require(
            self.transport_method
            == TRANSPORT_METHOD,
            "dispatch commit transport method mismatch",
        )

        require(
            self.transport_path
            == LEVERAGE_ENDPOINT,
            "dispatch commit transport path mismatch",
        )

        require(
            self.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            "dispatch commit payload hash mismatch",
        )

        require(
            bool(self.fence_hash),
            "dispatch commit fence hash required",
        )

        require(
            self.status
            in VALID_COMMIT_STATUSES,
            "invalid dispatch commit status",
        )

        require(
            self.committed_at_ms > 0,
            "dispatch commit timestamp invalid",
        )

        if self.status == COMMIT_STATUS_COMMITTED:
            require(
                self.dispatched_at_ms is None,
                (
                    "committed dispatch cannot already "
                    "have dispatched timestamp"
                ),
            )

            require(
                self.finalized_at_ms is None,
                (
                    "committed dispatch cannot already "
                    "have finalized timestamp"
                ),
            )

        if self.status == COMMIT_STATUS_DISPATCHED:
            require(
                self.dispatched_at_ms
                is not None,
                (
                    "dispatched commit missing "
                    "dispatch timestamp"
                ),
            )

            require(
                self.finalized_at_ms
                is None,
                (
                    "dispatched commit cannot already "
                    "have finalized timestamp"
                ),
            )

        if self.status == COMMIT_STATUS_FINALIZED:
            require(
                self.dispatched_at_ms
                is not None,
                (
                    "finalized commit missing "
                    "dispatch timestamp"
                ),
            )

            require(
                self.finalized_at_ms
                is not None,
                (
                    "finalized commit missing "
                    "finalization timestamp"
                ),
            )


# ============================================================================
# SYNTHETIC RECEIPT
# ============================================================================

@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str

    dispatch_id: str
    commit_id: str

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
            bool(self.receipt_id),
            "receipt id required",
        )

        require(
            bool(self.dispatch_id),
            "receipt dispatch required",
        )

        require(
            bool(self.commit_id),
            "receipt commit required",
        )

        require(
            self.status
            == SYNTHETIC_RECEIPT_STATUS,
            "unexpected synthetic receipt status",
        )

        require(
            self.transport_method
            == TRANSPORT_METHOD,
            "receipt transport method mismatch",
        )

        require(
            self.transport_path
            == LEVERAGE_ENDPOINT,
            "receipt transport path mismatch",
        )

        require(
            self.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            "receipt payload hash mismatch",
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
            bool(self.lineage_id),
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
# JOURNAL RECORD
# ============================================================================

@dataclass
class JournalRecord:
    sequence: int

    event: str

    timestamp_ms: int

    generation: int
    lineage_id: str
    recovery_epoch: int

    owner_id: Optional[str] = None
    lease_id: Optional[str] = None

    authorization_id: Optional[str] = None

    intent_id: Optional[str] = None
    dispatch_id: Optional[str] = None
    commit_id: Optional[str] = None

    payload_hash: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(
        self,
    ) -> None:
        require(
            self.sequence > 0,
            "journal sequence invalid",
        )

        require(
            bool(self.event),
            "journal event required",
        )

        require(
            self.timestamp_ms > 0,
            "journal timestamp invalid",
        )

        require(
            self.generation > 0,
            "journal generation invalid",
        )

        require(
            bool(self.lineage_id),
            "journal lineage required",
        )

        require(
            self.recovery_epoch > 0,
            "journal recovery epoch invalid",
        )


# ============================================================================
# DURABLE STATE
# ============================================================================

@dataclass
class DurableState:
    schema_version: int

    state: str

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

    dispatch_commit: Optional[
        DispatchCommit
    ]

    receipt: Optional[
        SyntheticReceipt
    ]

    journal: List[
        JournalRecord
    ]

    completed_dispatch_ids: Set[str]

    consumed_authorization_ids: Set[str]

    retired_lease_ids: Set[str]

    committed_dispatch_ids: Set[str]

    dispatched_commit_ids: Set[str]

    finalized_commit_ids: Set[str]

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
    # BASIC STATE VALIDATION
    # ========================================================================

    def validate_basic(
        self,
    ) -> None:
        require(
            self.schema_version
            == STATE_SCHEMA_VERSION,
            "unsupported durable state schema",
        )

        require(
            self.state
            in ALL_STATES,
            "invalid durable execution state",
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
            bool(self.lineage_id),
            "lineage id required",
        )

        require(
            bool(self.intent_id),
            "intent id required",
        )

        require(
            bool(self.dispatch_id),
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

        if self.dispatch_commit is not None:
            self.dispatch_commit.validate()

        if self.receipt is not None:
            self.receipt.validate()

        for record in self.journal:
            record.validate()


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


def dispatch_commit_to_dict(
    commit: Optional[
        DispatchCommit
    ],
) -> Optional[
    Dict[str, Any]
]:
    if commit is None:
        return None

    return asdict(
        commit
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


def journal_record_to_dict(
    record: JournalRecord,
) -> Dict[str, Any]:
    return asdict(
        record
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

        "state":
            state.state,

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

        "dispatch_commit":
            dispatch_commit_to_dict(
                state.dispatch_commit
            ),

        "receipt":
            receipt_to_dict(
                state.receipt
            ),

        "journal": [
            journal_record_to_dict(
                record
            )
            for record
            in state.journal
        ],

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

        "committed_dispatch_ids":
            sorted(
                state.committed_dispatch_ids
            ),

        "dispatched_commit_ids":
            sorted(
                state.dispatched_commit_ids
            ),

        "finalized_commit_ids":
            sorted(
                state.finalized_commit_ids
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
    return sha256_json(
        state_payload_without_seal(
            state
        )
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
        "snapshot integrity seal missing",
    )

    require(
        hmac.compare_digest(
            expected,
            state.integrity_seal,
        ),
        "snapshot integrity seal mismatch",
    )


# ============================================================================
# SYNTHETIC TRANSPORT FIREBREAK
#
# IMPORTANT N.24 RULE:
#
# Transport requires BOTH:
#
#   1. Valid DispatchBinding
#   2. Matching durable DispatchCommit in COMMITTED state
#
# A binding by itself is no longer enough.
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

        self.dispatched_commit_ids: Set[
            str
        ] = set()

        self._lock = (
            threading.RLock()
        )

    def dispatch(
        self,
        binding: DispatchBinding,
        commit: DispatchCommit,
    ) -> SyntheticReceipt:
        with self._lock:
            binding.validate()
            commit.validate()

            # ================================================================
            # HARD EXECUTION FIREBREAK
            # ================================================================

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

            # ================================================================
            # COMMIT MUST BE IN COMMITTED STATE
            # ================================================================

            require(
                commit.status
                == COMMIT_STATUS_COMMITTED,
                (
                    "synthetic transport requires "
                    "durably committed dispatch"
                ),
            )

            # ================================================================
            # EXACT COMMIT ↔ BINDING IDENTITY
            # ================================================================

            require(
                commit.dispatch_id
                == binding.dispatch_id,
                (
                    "transport commit dispatch "
                    "binding mismatch"
                ),
            )

            require(
                commit.intent_id
                == binding.intent_id,
                (
                    "transport commit intent "
                    "binding mismatch"
                ),
            )

            require(
                commit.generation
                == binding.generation,
                (
                    "transport commit generation "
                    "binding mismatch"
                ),
            )

            require(
                commit.lineage_id
                == binding.lineage_id,
                (
                    "transport commit lineage "
                    "binding mismatch"
                ),
            )

            require(
                commit.recovery_epoch
                == binding.recovery_epoch,
                (
                    "transport commit recovery epoch "
                    "binding mismatch"
                ),
            )

            require(
                commit.transport_method
                == binding.transport_method,
                (
                    "transport commit method "
                    "binding mismatch"
                ),
            )

            require(
                commit.transport_path
                == binding.transport_path,
                (
                    "transport commit path "
                    "binding mismatch"
                ),
            )

            require(
                commit.payload_hash
                == binding.payload_hash,
                (
                    "transport commit payload "
                    "binding mismatch"
                ),
            )

            # ================================================================
            # EXACTLY-ONCE LOCAL TRANSPORT FENCE
            # ================================================================

            require(
                commit.commit_id
                not in self.dispatched_commit_ids,
                (
                    "synthetic transport commit "
                    "replay rejected"
                ),
            )

            self.dispatched_commit_ids.add(
                commit.commit_id
            )

            self.dispatch_count += 1

            # ================================================================
            # NO HTTP / SOCKET / NETWORK WRITE OCCURS HERE
            # ================================================================

            receipt = SyntheticReceipt(
                receipt_id=deterministic_id(
                    "receipt",
                    binding.dispatch_id,
                    commit.commit_id,
                    binding.generation,
                    binding.lineage_id,
                    binding.recovery_epoch,
                    binding.payload_hash,
                ),

                dispatch_id=(
                    binding.dispatch_id
                ),

                commit_id=(
                    commit.commit_id
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
# FINAL NETWORK FIREBREAK HELPER
# ============================================================================

def assert_transport_firebreak(
    transport: SyntheticTransport,
) -> None:
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
    "R28 UNIT N.24: PART 1 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.24
# CORRECTED COPY/PASTE VERSION
# PART 2 OF 4
#
# N24 ENGINE
# DURABLE COMMIT + CRASH-WINDOW RECOVERY CORE
# ============================================================================


class N24Engine:
    def __init__(
        self,
        transport: Optional[SyntheticTransport] = None,
    ) -> None:
        self._lock = threading.RLock()

        self.transport = (
            transport
            if transport is not None
            else SyntheticTransport()
        )

        lineage_id = secure_id(
            "lineage"
        )

        intent_id = deterministic_id(
            "intent",
            SYMBOL,
            DEFAULT_ACCOUNT_EPOCH,
            DEFAULT_SYMBOL_EPOCH,
            DEFAULT_POSITION_EPOCH,
            DEFAULT_RECOVERY_EPOCH,
            DEFAULT_GENERATION,
            lineage_id,
        )

        dispatch_id = deterministic_id(
            "dispatch",
            intent_id,
            EXACT_LEVERAGE_PAYLOAD_HASH,
        )

        self.state = DurableState(
            schema_version=STATE_SCHEMA_VERSION,

            state="PREPARED",

            account_epoch=DEFAULT_ACCOUNT_EPOCH,
            symbol_epoch=DEFAULT_SYMBOL_EPOCH,
            position_epoch=DEFAULT_POSITION_EPOCH,
            recovery_epoch=DEFAULT_RECOVERY_EPOCH,

            generation=DEFAULT_GENERATION,
            lineage_id=lineage_id,

            intent_id=intent_id,
            dispatch_id=dispatch_id,

            lease_nonce=0,

            active_lease=None,
            authorization=None,
            dispatch_binding=None,
            dispatch_commit=None,
            receipt=None,

            journal=[],

            completed_dispatch_ids=set(),
            consumed_authorization_ids=set(),
            retired_lease_ids=set(),

            committed_dispatch_ids=set(),
            dispatched_commit_ids=set(),
            finalized_commit_ids=set(),

            snapshot_sequence=0,
            integrity_seal="",
        )

        self._append_journal(
            event="ENGINE_INITIALIZED",
            metadata={
                "symbol": SYMBOL,
                "leverage": LEVERAGE,
                "margin_mode": MARGIN_MODE,
                "schema_version": STATE_SCHEMA_VERSION,
            },
        )

        self._seal()
        self.verify_integrity()

    # ========================================================================
    # JOURNAL
    # ========================================================================

    def _append_journal(
        self,
        event: str,
        owner_id: Optional[str] = None,
        lease_id: Optional[str] = None,
        authorization_id: Optional[str] = None,
        intent_id: Optional[str] = None,
        dispatch_id: Optional[str] = None,
        commit_id: Optional[str] = None,
        payload_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JournalRecord:
        with self._lock:
            sequence = (
                len(self.state.journal) + 1
            )

            record = JournalRecord(
                sequence=sequence,
                event=event,
                timestamp_ms=now_ms(),

                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,

                owner_id=owner_id,
                lease_id=lease_id,
                authorization_id=authorization_id,

                intent_id=(
                    intent_id
                    if intent_id is not None
                    else self.state.intent_id
                ),

                dispatch_id=(
                    dispatch_id
                    if dispatch_id is not None
                    else self.state.dispatch_id
                ),

                commit_id=commit_id,

                payload_hash=payload_hash,

                metadata=(
                    clone(metadata)
                    if metadata is not None
                    else {}
                ),
            )

            record.validate()

            self.state.journal.append(
                record
            )

            return record

    # ========================================================================
    # SNAPSHOT SEAL
    # ========================================================================

    def _seal(
        self,
    ) -> None:
        with self._lock:
            self.state.snapshot_sequence += 1

            seal_state(
                self.state
            )

    # ========================================================================
    # COMPLETE INTEGRITY VALIDATION
    # ========================================================================

    def verify_integrity(
        self,
    ) -> None:
        with self._lock:
            self.state.validate_basic()

            verify_state_integrity(
                self.state
            )

            self._validate_structural_invariants()

    # ========================================================================
    # STRUCTURAL INVARIANTS
    # ========================================================================

    def _validate_structural_invariants(
        self,
    ) -> None:
        state = self.state

        expected_intent_id = deterministic_id(
            "intent",
            SYMBOL,
            state.account_epoch,
            state.symbol_epoch,
            state.position_epoch,
            state.recovery_epoch,
            state.generation,
            state.lineage_id,
        )

        require(
            state.intent_id
            == expected_intent_id,
            "intent identity mismatch",
        )

        expected_dispatch_id = deterministic_id(
            "dispatch",
            state.intent_id,
            EXACT_LEVERAGE_PAYLOAD_HASH,
        )

        require(
            state.dispatch_id
            == expected_dispatch_id,
            "dispatch identity mismatch",
        )

        # ====================================================================
        # ACTIVE LEASE
        # ====================================================================

        if state.active_lease is not None:
            lease = state.active_lease

            require(
                lease.generation
                == state.generation,
                "active lease generation mismatch",
            )

            require(
                lease.lineage_id
                == state.lineage_id,
                "active lease lineage mismatch",
            )

            require(
                lease.recovery_epoch
                == state.recovery_epoch,
                "active lease recovery epoch mismatch",
            )

            require(
                lease.fence_hash
                == state.fence().fingerprint(),
                "recovery lease fence mismatch",
            )

            require(
                lease.lease_id
                not in state.retired_lease_ids,
                "retired lease cannot be active",
            )

        # ====================================================================
        # AUTHORIZATION
        # ====================================================================

        if state.authorization is not None:
            authorization = (
                state.authorization
            )

            require(
                authorization.generation
                == state.generation,
                "authorization generation mismatch",
            )

            require(
                authorization.lineage_id
                == state.lineage_id,
                "authorization lineage mismatch",
            )

            require(
                authorization.recovery_epoch
                == state.recovery_epoch,
                "authorization recovery epoch mismatch",
            )

            require(
                authorization.intent_id
                == state.intent_id,
                "authorization intent mismatch",
            )

            require(
                authorization.dispatch_id
                == state.dispatch_id,
                "authorization dispatch mismatch",
            )

            if authorization.consumed:
                require(
                    authorization.authorization_id
                    in state.consumed_authorization_ids,
                    (
                        "consumed authorization "
                        "not durably persisted"
                    ),
                )

            else:
                require(
                    authorization.authorization_id
                    not in state.consumed_authorization_ids,
                    (
                        "unconsumed authorization "
                        "incorrectly persisted as consumed"
                    ),
                )

        # ====================================================================
        # DISPATCH BINDING
        # ====================================================================

        if state.dispatch_binding is not None:
            binding = (
                state.dispatch_binding
            )

            binding.validate()

            require(
                binding.intent_id
                == state.intent_id,
                "binding intent mismatch",
            )

            require(
                binding.dispatch_id
                == state.dispatch_id,
                "binding dispatch mismatch",
            )

            require(
                binding.generation
                == state.generation,
                "binding generation mismatch",
            )

            require(
                binding.lineage_id
                == state.lineage_id,
                "binding lineage mismatch",
            )

            require(
                binding.recovery_epoch
                == state.recovery_epoch,
                "binding recovery epoch mismatch",
            )

        # ====================================================================
        # DURABLE DISPATCH COMMIT
        # ====================================================================

        if state.dispatch_commit is not None:
            commit = (
                state.dispatch_commit
            )

            commit.validate()

            require(
                state.authorization is not None,
                (
                    "dispatch commit requires "
                    "authorization"
                ),
            )

            require(
                state.dispatch_binding is not None,
                (
                    "dispatch commit requires "
                    "dispatch binding"
                ),
            )

            authorization = (
                state.authorization
            )

            binding = (
                state.dispatch_binding
            )

            require(
                commit.authorization_id
                == authorization.authorization_id,
                (
                    "dispatch commit authorization "
                    "identity mismatch"
                ),
            )

            require(
                commit.lease_id
                == authorization.lease_id,
                (
                    "dispatch commit lease "
                    "identity mismatch"
                ),
            )

            require(
                commit.owner_id
                == authorization.owner_id,
                (
                    "dispatch commit owner "
                    "identity mismatch"
                ),
            )

            require(
                commit.intent_id
                == state.intent_id,
                "dispatch commit intent mismatch",
            )

            require(
                commit.dispatch_id
                == state.dispatch_id,
                "dispatch commit dispatch mismatch",
            )

            require(
                commit.generation
                == state.generation,
                "dispatch commit generation mismatch",
            )

            require(
                commit.lineage_id
                == state.lineage_id,
                "dispatch commit lineage mismatch",
            )

            require(
                commit.recovery_epoch
                == state.recovery_epoch,
                "dispatch commit epoch mismatch",
            )

            require(
                commit.lease_nonce
                == authorization.nonce,
                "dispatch commit nonce mismatch",
            )

            require(
                commit.fence_hash
                == state.fence().fingerprint(),
                "dispatch commit fence mismatch",
            )

            require(
                commit.transport_method
                == binding.transport_method,
                (
                    "dispatch commit transport "
                    "method mismatch"
                ),
            )

            require(
                commit.transport_path
                == binding.transport_path,
                (
                    "dispatch commit transport "
                    "path mismatch"
                ),
            )

            require(
                commit.payload_hash
                == binding.payload_hash,
                (
                    "dispatch commit payload "
                    "hash mismatch"
                ),
            )

            require(
                state.dispatch_id
                in state.committed_dispatch_ids,
                (
                    "durable commit not recorded "
                    "in committed dispatch set"
                ),
            )

            if commit.status in {
                COMMIT_STATUS_DISPATCHED,
                COMMIT_STATUS_FINALIZED,
            }:
                require(
                    commit.commit_id
                    in state.dispatched_commit_ids,
                    (
                        "dispatched commit not "
                        "durably persisted"
                    ),
                )

            if commit.status == COMMIT_STATUS_FINALIZED:
                require(
                    commit.commit_id
                    in state.finalized_commit_ids,
                    (
                        "finalized commit not "
                        "durably persisted"
                    ),
                )

        # ====================================================================
        # RECEIPT
        # ====================================================================

        if state.receipt is not None:
            receipt = state.receipt

            receipt.validate()

            require(
                state.dispatch_commit
                is not None,
                (
                    "receipt requires durable "
                    "dispatch commit"
                ),
            )

            commit = (
                state.dispatch_commit
            )

            require(
                receipt.dispatch_id
                == state.dispatch_id,
                "receipt dispatch mismatch",
            )

            require(
                receipt.commit_id
                == commit.commit_id,
                "receipt commit mismatch",
            )

            require(
                receipt.generation
                == state.generation,
                "receipt generation mismatch",
            )

            require(
                receipt.lineage_id
                == state.lineage_id,
                "receipt lineage mismatch",
            )

            require(
                receipt.recovery_epoch
                == state.recovery_epoch,
                "receipt recovery epoch mismatch",
            )

        # ====================================================================
        # STATE ↔ COMMIT CONSISTENCY
        # ====================================================================

        if state.state == "DISPATCH_COMMITTED":
            require(
                state.dispatch_commit
                is not None,
                (
                    "DISPATCH_COMMITTED state "
                    "missing commit"
                ),
            )

            require(
                state.dispatch_commit.status
                == COMMIT_STATUS_COMMITTED,
                (
                    "DISPATCH_COMMITTED state "
                    "requires COMMITTED commit"
                ),
            )

        if state.state == "DISPATCH_INFLIGHT":
            require(
                state.dispatch_commit
                is not None,
                (
                    "DISPATCH_INFLIGHT state "
                    "missing commit"
                ),
            )

            require(
                state.dispatch_commit.status
                == COMMIT_STATUS_DISPATCHED,
                (
                    "DISPATCH_INFLIGHT state "
                    "requires DISPATCHED commit"
                ),
            )

            require(
                state.receipt is not None,
                (
                    "DISPATCH_INFLIGHT state "
                    "missing synthetic receipt"
                ),
            )

        # ====================================================================
        # COMPLETED STATE
        # ====================================================================

        if state.state == "COMPLETED":
            require(
                state.receipt is not None,
                (
                    "completed state missing "
                    "synthetic receipt"
                ),
            )

            require(
                state.dispatch_commit
                is not None,
                (
                    "completed state missing "
                    "dispatch commit"
                ),
            )

            require(
                state.dispatch_commit.status
                == COMMIT_STATUS_FINALIZED,
                (
                    "completed state requires "
                    "finalized dispatch commit"
                ),
            )

            require(
                state.dispatch_id
                in state.completed_dispatch_ids,
                (
                    "completed dispatch "
                    "not persisted"
                ),
            )

            require(
                state.dispatch_commit.commit_id
                in state.finalized_commit_ids,
                (
                    "completed commit "
                    "not persisted as finalized"
                ),
            )

        if (
            state.dispatch_id
            in state.completed_dispatch_ids
        ):
            require(
                state.state == "COMPLETED",
                (
                    "completed dispatch id requires "
                    "COMPLETED state"
                ),
            )

    # ========================================================================
    # RECOVERY LEASE ACQUISITION
    # ========================================================================

    def acquire_recovery_lease(
        self,
        owner_id: str,
    ) -> RecoveryLease:
        with self._lock:
            self.verify_integrity()

            require(
                bool(owner_id),
                "recovery owner required",
            )

            if (
                self.state.state
                in TERMINAL_STATES
            ):
                local_block(
                    (
                        "terminal generation cannot "
                        "acquire recovery lease"
                    )
                )

                raise ValueError(
                    (
                        "terminal generation cannot "
                        "acquire recovery lease"
                    )
                )

            if (
                self.state.active_lease
                is not None
            ):
                active = (
                    self.state.active_lease
                )

                if (
                    active.owner_id
                    == owner_id
                ):
                    return clone(
                        active
                    )

                local_block(
                    (
                        "recovery lease already "
                        "owned by another worker"
                    )
                )

                raise ValueError(
                    (
                        "recovery lease already "
                        "owned by another worker"
                    )
                )

            self.state.lease_nonce += 1

            lease = RecoveryLease(
                lease_id=deterministic_id(
                    "lease",
                    owner_id,
                    self.state.generation,
                    self.state.lineage_id,
                    self.state.recovery_epoch,
                    self.state.lease_nonce,
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

                issued_at_ms=now_ms(),

                fence_hash=(
                    self.state
                    .fence()
                    .fingerprint()
                ),
            )

            lease.validate()

            self.state.active_lease = (
                lease
            )

            self._append_journal(
                event=(
                    "RECOVERY_LEASE_ACQUIRED"
                ),

                owner_id=(
                    owner_id
                ),

                lease_id=(
                    lease.lease_id
                ),

                metadata={
                    "nonce":
                        lease.nonce,

                    "fence_hash":
                        lease.fence_hash,
                },
            )

            self._seal()
            self.verify_integrity()

            return clone(
                lease
            )

    # ========================================================================
    # LEASE VALIDATION
    # ========================================================================

    def _validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        lease.validate()

        active = (
            self.state.active_lease
        )

        require(
            active is not None,
            "no active recovery lease",
        )

        require(
            lease.lease_id
            == active.lease_id,
            "recovery lease id mismatch",
        )

        require(
            lease.owner_id
            == active.owner_id,
            "recovery lease owner mismatch",
        )

        require(
            lease.generation
            == self.state.generation,
            "recovery lease generation mismatch",
        )

        require(
            lease.lineage_id
            == self.state.lineage_id,
            "recovery lease lineage mismatch",
        )

        require(
            lease.recovery_epoch
            == self.state.recovery_epoch,
            "recovery lease epoch mismatch",
        )

        require(
            lease.nonce
            == active.nonce,
            "recovery lease nonce mismatch",
        )

        require(
            lease.fence_hash
            == self.state.fence().fingerprint(),
            "recovery lease fence mismatch",
        )

        require(
            lease.lease_id
            not in self.state.retired_lease_ids,
            "recovery lease already retired",
        )

    # ========================================================================
    # RECOVERY AUTHORIZATION
    # ========================================================================

    def issue_recovery_authorization(
        self,
        lease: RecoveryLease,
    ) -> RecoveryAuthorization:
        with self._lock:
            self.verify_integrity()

            self._validate_lease(
                lease
            )

            require(
                self.state.state
                not in TERMINAL_STATES,
                (
                    "terminal state cannot "
                    "authorize recovery"
                ),
            )

            existing = (
                self.state.authorization
            )

            if existing is not None:
                if existing.consumed:
                    # N.24 recovery rule:
                    # consumed authorization is acceptable
                    # only when there is already a durable commit.
                    require(
                        self.state.dispatch_commit
                        is not None,
                        (
                            "consumed authorization "
                            "without durable dispatch commit"
                        ),
                    )

                    return clone(
                        existing
                    )

                require(
                    existing.owner_id
                    == lease.owner_id,
                    (
                        "existing authorization "
                        "owner mismatch"
                    ),
                )

                require(
                    existing.lease_id
                    == lease.lease_id,
                    (
                        "existing authorization "
                        "lease mismatch"
                    ),
                )

                return clone(
                    existing
                )

            authorization = RecoveryAuthorization(
                authorization_id=deterministic_id(
                    "authorization",
                    lease.lease_id,
                    self.state.intent_id,
                    self.state.dispatch_id,
                    self.state.generation,
                    self.state.lineage_id,
                    self.state.recovery_epoch,
                    lease.nonce,
                ),

                owner_id=(
                    lease.owner_id
                ),

                lease_id=(
                    lease.lease_id
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

                nonce=(
                    lease.nonce
                ),

                intent_id=(
                    self.state.intent_id
                ),

                dispatch_id=(
                    self.state.dispatch_id
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

            authorization.validate()

            self.state.authorization = (
                authorization
            )

            self.state.state = (
                "AUTHORIZED"
            )

            self._append_journal(
                event=(
                    "RECOVERY_AUTHORIZATION_ISSUED"
                ),

                owner_id=(
                    lease.owner_id
                ),

                lease_id=(
                    lease.lease_id
                ),

                authorization_id=(
                    authorization.authorization_id
                ),

                payload_hash=(
                    authorization.payload_hash
                ),
            )

            self._seal()
            self.verify_integrity()

            return clone(
                authorization
            )

    # ========================================================================
    # AUTHORIZATION VALIDATION
    # ========================================================================

    def _validate_authorization(
        self,
        authorization: RecoveryAuthorization,
        lease: RecoveryLease,
        allow_consumed: bool = False,
    ) -> None:
        authorization.validate()

        self._validate_lease(
            lease
        )

        persisted = (
            self.state.authorization
        )

        require(
            persisted is not None,
            (
                "no persisted recovery "
                "authorization"
            ),
        )

        require(
            authorization.authorization_id
            == persisted.authorization_id,
            "authorization id mismatch",
        )

        require(
            authorization.owner_id
            == lease.owner_id,
            "authorization owner mismatch",
        )

        require(
            authorization.lease_id
            == lease.lease_id,
            "authorization lease mismatch",
        )

        require(
            authorization.generation
            == self.state.generation,
            "authorization generation mismatch",
        )

        require(
            authorization.lineage_id
            == self.state.lineage_id,
            "authorization lineage mismatch",
        )

        require(
            authorization.recovery_epoch
            == self.state.recovery_epoch,
            (
                "authorization recovery "
                "epoch mismatch"
            ),
        )

        require(
            authorization.nonce
            == lease.nonce,
            "authorization nonce mismatch",
        )

        require(
            authorization.intent_id
            == self.state.intent_id,
            "authorization intent mismatch",
        )

        require(
            authorization.dispatch_id
            == self.state.dispatch_id,
            "authorization dispatch mismatch",
        )

        require(
            authorization.transport_method
            == TRANSPORT_METHOD,
            (
                "authorization transport "
                "method mismatch"
            ),
        )

        require(
            authorization.transport_path
            == LEVERAGE_ENDPOINT,
            (
                "authorization transport "
                "path mismatch"
            ),
        )

        require(
            authorization.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            (
                "authorization payload "
                "hash mismatch"
            ),
        )

        if allow_consumed:
            require(
                authorization.consumed
                == persisted.consumed,
                (
                    "authorization consumption "
                    "state mismatch"
                ),
            )

        else:
            require(
                authorization.consumed
                is False,
                "authorization already consumed",
            )

            require(
                authorization.authorization_id
                not in (
                    self.state
                    .consumed_authorization_ids
                ),
                "authorization replay rejected",
            )

    # ========================================================================
    # EXACT DISPATCH BINDING PREPARATION
    # ========================================================================

    def prepare_dispatch_binding(
        self,
        lease: RecoveryLease,
        authorization: RecoveryAuthorization,
    ) -> DispatchBinding:
        with self._lock:
            self.verify_integrity()

            # If authorization was already consumed,
            # preparation is legal only if binding and
            # durable commit already exist.
            if authorization.consumed:
                self._validate_authorization(
                    authorization,
                    lease,
                    allow_consumed=True,
                )

                require(
                    self.state.dispatch_binding
                    is not None,
                    (
                        "consumed authorization "
                        "missing dispatch binding"
                    ),
                )

                require(
                    self.state.dispatch_commit
                    is not None,
                    (
                        "consumed authorization "
                        "missing durable commit"
                    ),
                )

                return clone(
                    self.state.dispatch_binding
                )

            self._validate_authorization(
                authorization,
                lease,
            )

            existing = (
                self.state.dispatch_binding
            )

            if existing is not None:
                existing.validate()

                return clone(
                    existing
                )

            payload = (
                build_exact_leverage_payload()
            )

            binding = DispatchBinding(
                dispatch_id=(
                    self.state.dispatch_id
                ),

                intent_id=(
                    self.state.intent_id
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

                transport_method=(
                    TRANSPORT_METHOD
                ),

                transport_path=(
                    LEVERAGE_ENDPOINT
                ),

                payload=payload,

                payload_hash=(
                    sha256_json(
                        payload
                    )
                ),
            )

            binding.validate()

            self.state.dispatch_binding = (
                binding
            )

            self.state.state = (
                "DISPATCH_PREPARED"
            )

            self._append_journal(
                event=(
                    "DISPATCH_BINDING_PREPARED"
                ),

                owner_id=(
                    lease.owner_id
                ),

                lease_id=(
                    lease.lease_id
                ),

                authorization_id=(
                    authorization.authorization_id
                ),

                dispatch_id=(
                    binding.dispatch_id
                ),

                payload_hash=(
                    binding.payload_hash
                ),

                metadata={
                    "method":
                        binding.transport_method,

                    "path":
                        binding.transport_path,
                },
            )

            self._seal()
            self.verify_integrity()

            return clone(
                binding
            )

    # ========================================================================
    # AUTHORIZATION CONSUMPTION
    # ========================================================================

    def _consume_authorization(
        self,
        lease: RecoveryLease,
        authorization: RecoveryAuthorization,
    ) -> RecoveryAuthorization:
        self._validate_authorization(
            authorization,
            lease,
        )

        consumed = RecoveryAuthorization(
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

        consumed.validate()

        self.state.authorization = (
            consumed
        )

        self.state.consumed_authorization_ids.add(
            consumed.authorization_id
        )

        self._append_journal(
            event=(
                "RECOVERY_AUTHORIZATION_CONSUMED"
            ),

            owner_id=(
                lease.owner_id
            ),

            lease_id=(
                lease.lease_id
            ),

            authorization_id=(
                consumed.authorization_id
            ),

            dispatch_id=(
                consumed.dispatch_id
            ),

            payload_hash=(
                consumed.payload_hash
            ),
        )

        return consumed

    # ========================================================================
    # DURABLE DISPATCH COMMIT
    #
    # N.24 CRITICAL BOUNDARY
    #
    # The authorization is consumed and the DispatchCommit is installed
    # under the same engine lock before transport may be entered.
    # ========================================================================

    def commit_dispatch(
        self,
        lease: RecoveryLease,
        authorization: RecoveryAuthorization,
        binding: DispatchBinding,
    ) -> DispatchCommit:
        with self._lock:
            self.verify_integrity()

            self._validate_lease(
                lease
            )

            persisted_binding = (
                self.state.dispatch_binding
            )

            require(
                persisted_binding is not None,
                (
                    "dispatch binding "
                    "not prepared"
                ),
            )

            binding.validate()

            require(
                binding == persisted_binding,
                "dispatch binding mismatch",
            )

            # ================================================================
            # IDEMPOTENT RECOVERY OF EXISTING COMMIT
            # ================================================================

            existing_commit = (
                self.state.dispatch_commit
            )

            if existing_commit is not None:
                existing_commit.validate()

                require(
                    existing_commit.dispatch_id
                    == binding.dispatch_id,
                    (
                        "existing commit "
                        "dispatch mismatch"
                    ),
                )

                require(
                    existing_commit.intent_id
                    == binding.intent_id,
                    (
                        "existing commit "
                        "intent mismatch"
                    ),
                )

                require(
                    existing_commit.generation
                    == self.state.generation,
                    (
                        "existing commit "
                        "generation mismatch"
                    ),
                )

                require(
                    existing_commit.lineage_id
                    == self.state.lineage_id,
                    (
                        "existing commit "
                        "lineage mismatch"
                    ),
                )

                require(
                    existing_commit.recovery_epoch
                    == self.state.recovery_epoch,
                    (
                        "existing commit "
                        "recovery epoch mismatch"
                    ),
                )

                return clone(
                    existing_commit
                )

            # ================================================================
            # NEW COMMIT REQUIRES UNCONSUMED AUTHORIZATION
            # ================================================================

            self._validate_authorization(
                authorization,
                lease,
            )

            require(
                self.state.dispatch_id
                not in self.state.completed_dispatch_ids,
                "completed dispatch cannot be recommitted",
            )

            require(
                self.state.dispatch_id
                not in self.state.committed_dispatch_ids,
                "dispatch commit replay rejected",
            )

            consumed = (
                self._consume_authorization(
                    lease,
                    authorization,
                )
            )

            commit = DispatchCommit(
                commit_id=deterministic_id(
                    "commit",
                    consumed.authorization_id,
                    binding.dispatch_id,
                    binding.intent_id,
                    self.state.generation,
                    self.state.lineage_id,
                    self.state.recovery_epoch,
                    lease.nonce,
                    binding.payload_hash,
                ),

                authorization_id=(
                    consumed.authorization_id
                ),

                lease_id=(
                    lease.lease_id
                ),

                owner_id=(
                    lease.owner_id
                ),

                intent_id=(
                    binding.intent_id
                ),

                dispatch_id=(
                    binding.dispatch_id
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

                lease_nonce=(
                    lease.nonce
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

                fence_hash=(
                    self.state
                    .fence()
                    .fingerprint()
                ),

                status=(
                    COMMIT_STATUS_COMMITTED
                ),

                committed_at_ms=(
                    now_ms()
                ),

                dispatched_at_ms=None,
                finalized_at_ms=None,
            )

            commit.validate()

            self.state.dispatch_commit = (
                commit
            )

            self.state.committed_dispatch_ids.add(
                binding.dispatch_id
            )

            self.state.state = (
                "DISPATCH_COMMITTED"
            )

            self._append_journal(
                event=(
                    "DISPATCH_DURABLY_COMMITTED"
                ),

                owner_id=(
                    lease.owner_id
                ),

                lease_id=(
                    lease.lease_id
                ),

                authorization_id=(
                    consumed.authorization_id
                ),

                dispatch_id=(
                    binding.dispatch_id
                ),

                commit_id=(
                    commit.commit_id
                ),

                payload_hash=(
                    binding.payload_hash
                ),

                metadata={
                    "status":
                        commit.status,

                    "fence_hash":
                        commit.fence_hash,

                    "lease_nonce":
                        commit.lease_nonce,
                },
            )

            self._seal()
            self.verify_integrity()

            return clone(
                commit
            )

    # ========================================================================
    # COMMIT VALIDATION
    # ========================================================================

    def _validate_commit(
        self,
        lease: RecoveryLease,
        binding: DispatchBinding,
        commit: DispatchCommit,
        allowed_statuses: Set[str],
    ) -> None:
        self._validate_lease(
            lease
        )

        binding.validate()
        commit.validate()

        persisted_binding = (
            self.state.dispatch_binding
        )

        persisted_commit = (
            self.state.dispatch_commit
        )

        require(
            persisted_binding is not None,
            "no persisted dispatch binding",
        )

        require(
            persisted_commit is not None,
            "no persisted dispatch commit",
        )

        require(
            binding == persisted_binding,
            "dispatch binding mismatch",
        )

        require(
            commit.commit_id
            == persisted_commit.commit_id,
            "dispatch commit id mismatch",
        )

        require(
            commit.status
            == persisted_commit.status,
            (
                "dispatch commit "
                "status mismatch"
            ),
        )

        require(
            commit.status
            in allowed_statuses,
            (
                "dispatch commit state "
                "not valid for operation"
            ),
        )

        require(
            commit.dispatch_id
            == self.state.dispatch_id,
            "dispatch commit dispatch mismatch",
        )

        require(
            commit.intent_id
            == self.state.intent_id,
            "dispatch commit intent mismatch",
        )

        require(
            commit.generation
            == self.state.generation,
            "dispatch commit generation mismatch",
        )

        require(
            commit.lineage_id
            == self.state.lineage_id,
            "dispatch commit lineage mismatch",
        )

        require(
            commit.recovery_epoch
            == self.state.recovery_epoch,
            "dispatch commit recovery epoch mismatch",
        )

        require(
            commit.lease_id
            == lease.lease_id,
            "dispatch commit lease mismatch",
        )

        require(
            commit.owner_id
            == lease.owner_id,
            "dispatch commit owner mismatch",
        )

        require(
            commit.lease_nonce
            == lease.nonce,
            "dispatch commit lease nonce mismatch",
        )

        require(
            commit.fence_hash
            == self.state.fence().fingerprint(),
            "dispatch commit fence mismatch",
        )

        require(
            commit.transport_method
            == binding.transport_method,
            (
                "dispatch commit transport "
                "method mismatch"
            ),
        )

        require(
            commit.transport_path
            == binding.transport_path,
            (
                "dispatch commit transport "
                "path mismatch"
            ),
        )

        require(
            commit.payload_hash
            == binding.payload_hash,
            (
                "dispatch commit payload "
                "hash mismatch"
            ),
        )

        require(
            commit.dispatch_id
            in self.state.committed_dispatch_ids,
            (
                "dispatch commit missing "
                "from durable commit set"
            ),
        )

    # ========================================================================
    # MARK COMMIT DISPATCHED
    #
    # This transition is persisted immediately after the synthetic transport
    # returns a valid receipt.
    # ========================================================================

    def _mark_commit_dispatched(
        self,
        lease: RecoveryLease,
        binding: DispatchBinding,
        commit: DispatchCommit,
        receipt: SyntheticReceipt,
    ) -> DispatchCommit:
        self._validate_commit(
            lease,
            binding,
            commit,
            {
                COMMIT_STATUS_COMMITTED,
            },
        )

        receipt.validate()

        require(
            receipt.commit_id
            == commit.commit_id,
            (
                "receipt commit identity "
                "mismatch"
            ),
        )

        require(
            receipt.dispatch_id
            == commit.dispatch_id,
            (
                "receipt dispatch identity "
                "mismatch"
            ),
        )

        dispatched = DispatchCommit(
            commit_id=(
                commit.commit_id
            ),

            authorization_id=(
                commit.authorization_id
            ),

            lease_id=(
                commit.lease_id
            ),

            owner_id=(
                commit.owner_id
            ),

            intent_id=(
                commit.intent_id
            ),

            dispatch_id=(
                commit.dispatch_id
            ),

            generation=(
                commit.generation
            ),

            lineage_id=(
                commit.lineage_id
            ),

            recovery_epoch=(
                commit.recovery_epoch
            ),

            lease_nonce=(
                commit.lease_nonce
            ),

            transport_method=(
                commit.transport_method
            ),

            transport_path=(
                commit.transport_path
            ),

            payload_hash=(
                commit.payload_hash
            ),

            fence_hash=(
                commit.fence_hash
            ),

            status=(
                COMMIT_STATUS_DISPATCHED
            ),

            committed_at_ms=(
                commit.committed_at_ms
            ),

            dispatched_at_ms=(
                receipt.created_at_ms
            ),

            finalized_at_ms=None,
        )

        dispatched.validate()

        self.state.dispatch_commit = (
            dispatched
        )

        self.state.receipt = (
            receipt
        )

        self.state.dispatched_commit_ids.add(
            dispatched.commit_id
        )

        self.state.state = (
            "DISPATCH_INFLIGHT"
        )

        self._append_journal(
            event=(
                "SYNTHETIC_DISPATCH_RECORDED"
            ),

            owner_id=(
                lease.owner_id
            ),

            lease_id=(
                lease.lease_id
            ),

            authorization_id=(
                dispatched.authorization_id
            ),

            dispatch_id=(
                dispatched.dispatch_id
            ),

            commit_id=(
                dispatched.commit_id
            ),

            payload_hash=(
                dispatched.payload_hash
            ),

            metadata={
                "receipt_id":
                    receipt.receipt_id,

                "status":
                    dispatched.status,

                "transmitted":
                    receipt.transmitted,

                "network_write":
                    receipt.network_write,
            },
        )

        return dispatched

    # ========================================================================
    # FINALIZE DURABLE COMMIT
    # ========================================================================

    def _finalize_commit(
        self,
        lease: RecoveryLease,
        binding: DispatchBinding,
        commit: DispatchCommit,
    ) -> DispatchCommit:
        self._validate_commit(
            lease,
            binding,
            commit,
            {
                COMMIT_STATUS_DISPATCHED,
            },
        )

        require(
            self.state.receipt
            is not None,
            (
                "cannot finalize dispatch "
                "without synthetic receipt"
            ),
        )

        receipt = (
            self.state.receipt
        )

        require(
            receipt.commit_id
            == commit.commit_id,
            (
                "finalization receipt "
                "commit mismatch"
            ),
        )

        require(
            receipt.dispatch_id
            == commit.dispatch_id,
            (
                "finalization receipt "
                "dispatch mismatch"
            ),
        )

        finalized = DispatchCommit(
            commit_id=(
                commit.commit_id
            ),

            authorization_id=(
                commit.authorization_id
            ),

            lease_id=(
                commit.lease_id
            ),

            owner_id=(
                commit.owner_id
            ),

            intent_id=(
                commit.intent_id
            ),

            dispatch_id=(
                commit.dispatch_id
            ),

            generation=(
                commit.generation
            ),

            lineage_id=(
                commit.lineage_id
            ),

            recovery_epoch=(
                commit.recovery_epoch
            ),

            lease_nonce=(
                commit.lease_nonce
            ),

            transport_method=(
                commit.transport_method
            ),

            transport_path=(
                commit.transport_path
            ),

            payload_hash=(
                commit.payload_hash
            ),

            fence_hash=(
                commit.fence_hash
            ),

            status=(
                COMMIT_STATUS_FINALIZED
            ),

            committed_at_ms=(
                commit.committed_at_ms
            ),

            dispatched_at_ms=(
                commit.dispatched_at_ms
            ),

            finalized_at_ms=(
                now_ms()
            ),
        )

        finalized.validate()

        self.state.dispatch_commit = (
            finalized
        )

        self.state.finalized_commit_ids.add(
            finalized.commit_id
        )

        self.state.completed_dispatch_ids.add(
            finalized.dispatch_id
        )

        self.state.state = (
            "COMPLETED"
        )

        self._append_journal(
            event=(
                "DISPATCH_COMMIT_FINALIZED"
            ),

            owner_id=(
                lease.owner_id
            ),

            lease_id=(
                lease.lease_id
            ),

            authorization_id=(
                finalized.authorization_id
            ),

            dispatch_id=(
                finalized.dispatch_id
            ),

            commit_id=(
                finalized.commit_id
            ),

            payload_hash=(
                finalized.payload_hash
            ),

            metadata={
                "status":
                    finalized.status,

                "receipt_id":
                    self.state.receipt.receipt_id,
            },
        )

        return finalized

    # ========================================================================
    # RETIRE ACTIVE LEASE
    # ========================================================================

    def _retire_active_lease(
        self,
        lease: RecoveryLease,
        reason: str,
    ) -> None:
        self._validate_lease(
            lease
        )

        self.state.retired_lease_ids.add(
            lease.lease_id
        )

        self._append_journal(
            event=(
                "RECOVERY_LEASE_RETIRED"
            ),

            owner_id=(
                lease.owner_id
            ),

            lease_id=(
                lease.lease_id
            ),

            commit_id=(
                self.state.dispatch_commit.commit_id
                if self.state.dispatch_commit
                is not None
                else None
            ),

            metadata={
                "reason":
                    reason,

                "nonce":
                    lease.nonce,
            },
        )

        self.state.active_lease = (
            None
        )

    # ========================================================================
    # SYNTHETIC DISPATCH FROM DURABLE COMMIT
    # ========================================================================

    def dispatch_committed(
        self,
        lease: RecoveryLease,
        binding: DispatchBinding,
        commit: DispatchCommit,
    ) -> SyntheticReceipt:
        with self._lock:
            self.verify_integrity()

            self._validate_commit(
                lease,
                binding,
                commit,
                {
                    COMMIT_STATUS_COMMITTED,
                },
            )

            require(
                commit.commit_id
                not in self.state.dispatched_commit_ids,
                (
                    "durably recorded dispatch "
                    "already dispatched"
                ),
            )

            require(
                commit.dispatch_id
                not in self.state.completed_dispatch_ids,
                (
                    "completed dispatch "
                    "replay rejected"
                ),
            )

            receipt = (
                self.transport.dispatch(
                    binding,
                    commit,
                )
            )

            receipt.validate()

            dispatched_commit = (
                self._mark_commit_dispatched(
                    lease,
                    binding,
                    commit,
                    receipt,
                )
            )

            # Durable crash boundary:
            # receipt + DISPATCHED commit are now sealed
            # before final completion is recorded.
            self._seal()
            self.verify_integrity()

            finalized_commit = (
                self._finalize_commit(
                    lease,
                    binding,
                    dispatched_commit,
                )
            )

            require(
                finalized_commit.status
                == COMMIT_STATUS_FINALIZED,
                (
                    "dispatch commit "
                    "failed to finalize"
                ),
            )

            self._retire_active_lease(
                lease,
                reason=(
                    "generation completed"
                ),
            )

            self._seal()
            self.verify_integrity()

            require(
                self.state.receipt
                is not None,
                (
                    "completed synthetic dispatch "
                    "missing receipt"
                ),
            )

            return clone(
                self.state.receipt
            )

    # ========================================================================
    # STANDARD FULL EXECUTION
    # ========================================================================

    def execute_synthetic_dispatch(
        self,
        lease: RecoveryLease,
        authorization: RecoveryAuthorization,
        binding: DispatchBinding,
    ) -> SyntheticReceipt:
        with self._lock:
            self.verify_integrity()

            commit = (
                self.commit_dispatch(
                    lease,
                    authorization,
                    binding,
                )
            )

            return self.dispatch_committed(
                lease,
                binding,
                commit,
            )

    # ========================================================================
    # RECOVER ALREADY DISPATCHED BUT NOT FINALIZED COMMIT
    #
    # N.24 POST-DISPATCH / PRE-FINALIZATION CRASH WINDOW
    #
    # IMPORTANT:
    # This path DOES NOT re-enter transport.
    # It finalizes using the already-durable synthetic receipt.
    # ========================================================================

    def finalize_inflight_dispatch(
        self,
        lease: RecoveryLease,
    ) -> SyntheticReceipt:
        with self._lock:
            self.verify_integrity()

            self._validate_lease(
                lease
            )

            binding = (
                self.state.dispatch_binding
            )

            commit = (
                self.state.dispatch_commit
            )

            receipt = (
                self.state.receipt
            )

            require(
                binding is not None,
                (
                    "inflight recovery missing "
                    "dispatch binding"
                ),
            )

            require(
                commit is not None,
                (
                    "inflight recovery missing "
                    "dispatch commit"
                ),
            )

            require(
                receipt is not None,
                (
                    "inflight recovery missing "
                    "synthetic receipt"
                ),
            )

            self._validate_commit(
                lease,
                binding,
                commit,
                {
                    COMMIT_STATUS_DISPATCHED,
                },
            )

            receipt.validate()

            require(
                receipt.commit_id
                == commit.commit_id,
                (
                    "inflight receipt "
                    "commit mismatch"
                ),
            )

            require(
                receipt.dispatch_id
                == commit.dispatch_id,
                (
                    "inflight receipt "
                    "dispatch mismatch"
                ),
            )

            require(
                self.transport.dispatch_count
                == 0,
                (
                    "restart finalization path "
                    "must not redispatch"
                ),
            )

            finalized = (
                self._finalize_commit(
                    lease,
                    binding,
                    commit,
                )
            )

            self._retire_active_lease(
                lease,
                reason=(
                    "recovered inflight "
                    "dispatch finalized"
                ),
            )

            self._seal()
            self.verify_integrity()

            require(
                finalized.status
                == COMMIT_STATUS_FINALIZED,
                (
                    "inflight dispatch "
                    "failed finalization"
                ),
            )

            return clone(
                receipt
            )

    # ========================================================================
    # RECOVER COMMITTED BUT NOT YET DISPATCHED
    #
    # N.24 POST-COMMIT / PRE-DISPATCH CRASH WINDOW
    # ========================================================================

    def resume_committed_dispatch(
        self,
        lease: RecoveryLease,
    ) -> SyntheticReceipt:
        with self._lock:
            self.verify_integrity()

            self._validate_lease(
                lease
            )

            binding = (
                self.state.dispatch_binding
            )

            commit = (
                self.state.dispatch_commit
            )

            require(
                binding is not None,
                (
                    "committed recovery missing "
                    "dispatch binding"
                ),
            )

            require(
                commit is not None,
                (
                    "committed recovery missing "
                    "dispatch commit"
                ),
            )

            require(
                commit.status
                == COMMIT_STATUS_COMMITTED,
                (
                    "resume requires committed "
                    "undispatched commit"
                ),
            )

            require(
                self.state.receipt
                is None,
                (
                    "committed undispatched state "
                    "cannot already contain receipt"
                ),
            )

            return self.dispatch_committed(
                lease,
                binding,
                commit,
            )

    # ========================================================================
    # ONE-SHOT RECOVERY STATE MACHINE
    # ========================================================================

    def recover(
        self,
        owner_id: str,
    ) -> SyntheticReceipt:
        with self._lock:
            self.verify_integrity()

            # ================================================================
            # ALREADY COMPLETED
            # ================================================================

            if self.state.state == "COMPLETED":
                require(
                    self.state.receipt
                    is not None,
                    (
                        "completed generation "
                        "missing receipt"
                    ),
                )

                return clone(
                    self.state.receipt
                )

            # ================================================================
            # RESTORED ACTIVE LEASE OWNER
            # ================================================================

            if (
                self.state.active_lease
                is not None
            ):
                require(
                    self.state.active_lease.owner_id
                    == owner_id,
                    (
                        "recovery lease already owned "
                        "by another worker"
                    ),
                )

                lease = clone(
                    self.state.active_lease
                )

            else:
                lease = (
                    self.acquire_recovery_lease(
                        owner_id
                    )
                )

            # ================================================================
            # CRASH WINDOW:
            # DISPATCHED BUT NOT FINALIZED
            # ================================================================

            if (
                self.state.dispatch_commit
                is not None
                and
                self.state.dispatch_commit.status
                == COMMIT_STATUS_DISPATCHED
            ):
                return (
                    self.finalize_inflight_dispatch(
                        lease
                    )
                )

            # ================================================================
            # CRASH WINDOW:
            # COMMITTED BUT NOT DISPATCHED
            # ================================================================

            if (
                self.state.dispatch_commit
                is not None
                and
                self.state.dispatch_commit.status
                == COMMIT_STATUS_COMMITTED
            ):
                return (
                    self.resume_committed_dispatch(
                        lease
                    )
                )

            # ================================================================
            # NORMAL / PRE-COMMIT RECOVERY
            # ================================================================

            authorization = (
                self.issue_recovery_authorization(
                    lease
                )
            )

            binding = (
                self.prepare_dispatch_binding(
                    lease,
                    authorization,
                )
            )

            commit = (
                self.commit_dispatch(
                    lease,
                    authorization,
                    binding,
                )
            )

            return (
                self.dispatch_committed(
                    lease,
                    binding,
                    commit,
                )
            )

    # ========================================================================
    # SNAPSHOT EXPORT
    # ========================================================================

    def snapshot_state(
        self,
    ) -> DurableState:
        with self._lock:
            self.verify_integrity()

            return clone(
                self.state
            )

    def snapshot_dict(
        self,
    ) -> Dict[str, Any]:
        with self._lock:
            state = (
                self.snapshot_state()
            )

            payload = (
                state_payload_without_seal(
                    state
                )
            )

            payload[
                "integrity_seal"
            ] = state.integrity_seal

            return payload


# ============================================================================
# CRASH-WINDOW TEST HOOKS
#
# These hooks deliberately stop at safe local boundaries.
# They never perform a real or demo network operation.
# ============================================================================

def prepare_to_authorization_boundary(
    engine: N24Engine,
    owner_id: str,
) -> Tuple[
    RecoveryLease,
    RecoveryAuthorization,
]:
    lease = (
        engine.acquire_recovery_lease(
            owner_id
        )
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    return (
        lease,
        authorization,
    )


def prepare_to_binding_boundary(
    engine: N24Engine,
    owner_id: str,
) -> Tuple[
    RecoveryLease,
    RecoveryAuthorization,
    DispatchBinding,
]:
    (
        lease,
        authorization,
    ) = (
        prepare_to_authorization_boundary(
            engine,
            owner_id,
        )
    )

    binding = (
        engine.prepare_dispatch_binding(
            lease,
            authorization,
        )
    )

    return (
        lease,
        authorization,
        binding,
    )


def prepare_to_commit_boundary(
    engine: N24Engine,
    owner_id: str,
) -> Tuple[
    RecoveryLease,
    RecoveryAuthorization,
    DispatchBinding,
    DispatchCommit,
]:
    (
        lease,
        authorization,
        binding,
    ) = (
        prepare_to_binding_boundary(
            engine,
            owner_id,
        )
    )

    commit = (
        engine.commit_dispatch(
            lease,
            authorization,
            binding,
        )
    )

    return (
        lease,
        authorization,
        binding,
        commit,
    )


def prepare_to_inflight_boundary(
    engine: N24Engine,
    owner_id: str,
) -> Tuple[
    RecoveryLease,
    DispatchBinding,
    DispatchCommit,
    SyntheticReceipt,
]:
    (
        lease,
        authorization,
        binding,
        commit,
    ) = (
        prepare_to_commit_boundary(
            engine,
            owner_id,
        )
    )

    # Synthetic transport only.
    receipt = (
        engine.transport.dispatch(
            binding,
            commit,
        )
    )

    receipt.validate()

    dispatched_commit = (
        engine._mark_commit_dispatched(
            lease,
            binding,
            commit,
            receipt,
        )
    )

    engine._seal()
    engine.verify_integrity()

    return (
        lease,
        binding,
        dispatched_commit,
        receipt,
    )


# ============================================================================
# END OF PART 2
# ============================================================================

print(
    "R28 UNIT N.24: PART 2 DEFINITIONS LOADED",
    flush=True,
)
