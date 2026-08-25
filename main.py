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
