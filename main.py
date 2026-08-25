# ============================================================================
# R28 UNIT N.23
# DURABLE RECOVERY + GENERATION LINEAGE + EXACT SYNTHETIC TRANSPORT BINDING
#
# CORRECTED COPY/PASTE VERSION
# PART 1 OF 4
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
# ============================================================================

print("R28 UNIT N.23: MAIN.PY ENTERED", flush=True)

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


print("R28 UNIT N.23: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.23"
UNIT_VERSION = "N.23"

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

HEALTH_PORT = int(os.environ.get("PORT", "10000"))

STATE_SCHEMA_VERSION = 23

DEFAULT_ACCOUNT_EPOCH = 1
DEFAULT_SYMBOL_EPOCH = 1
DEFAULT_POSITION_EPOCH = 1
DEFAULT_RECOVERY_EPOCH = 1
DEFAULT_GENERATION = 1

MAX_RECOVERY_ATTEMPTS = 64

SYNTHETIC_RECEIPT_STATUS = "SYNTHETIC_NO_TRANSMISSION"

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
}

ALL_STATES = TERMINAL_STATES | NON_TERMINAL_STATES


print("R28 UNIT N.23: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# BASIC HELPERS
# ============================================================================

def now_ms() -> int:
    return int(time.time() * 1000)


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


def secure_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def deterministic_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:32]}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


def clone(value: Any) -> Any:
    return copy.deepcopy(value)


# ============================================================================
# EXACT LEVERAGE PAYLOAD
# ============================================================================

def build_exact_leverage_payload() -> Dict[str, str]:
    return {
        "leverage": str(LEVERAGE),
        "marginMode": MARGIN_MODE,
        "symbol": SYMBOL,
    }


EXACT_LEVERAGE_PAYLOAD = build_exact_leverage_payload()
EXACT_LEVERAGE_PAYLOAD_JSON = canonical_json(EXACT_LEVERAGE_PAYLOAD)
EXACT_LEVERAGE_PAYLOAD_HASH = sha256_text(EXACT_LEVERAGE_PAYLOAD_JSON)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass(frozen=True)
class GenerationFence:
    account_epoch: int
    symbol_epoch: int
    position_epoch: int
    recovery_epoch: int
    generation: int
    lineage_id: str

    def validate(self) -> None:
        require(self.account_epoch > 0, "account epoch must be positive")
        require(self.symbol_epoch > 0, "symbol epoch must be positive")
        require(self.position_epoch > 0, "position epoch must be positive")
        require(self.recovery_epoch > 0, "recovery epoch must be positive")
        require(self.generation > 0, "generation must be positive")
        require(bool(self.lineage_id), "lineage id required")

    def fingerprint(self) -> str:
        self.validate()
        return sha256_json(asdict(self))


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

    def validate(self) -> None:
        require(bool(self.lease_id), "lease id required")
        require(bool(self.owner_id), "owner id required")
        require(self.generation > 0, "lease generation must be positive")
        require(bool(self.lineage_id), "lease lineage required")
        require(self.recovery_epoch > 0, "lease recovery epoch must be positive")
        require(self.nonce > 0, "lease nonce must be positive")
        require(self.issued_at_ms > 0, "lease issued timestamp invalid")
        require(bool(self.fence_hash), "lease fence hash required")


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

    def validate(self) -> None:
        require(bool(self.authorization_id), "authorization id required")
        require(bool(self.owner_id), "authorization owner required")
        require(bool(self.lease_id), "authorization lease required")

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

        require(bool(self.intent_id), "authorization intent required")
        require(bool(self.dispatch_id), "authorization dispatch required")

        require(
            self.transport_method == TRANSPORT_METHOD,
            "authorization transport method mismatch",
        )
        require(
            self.transport_path == LEVERAGE_ENDPOINT,
            "authorization transport path mismatch",
        )
        require(
            self.payload_hash == EXACT_LEVERAGE_PAYLOAD_HASH,
            "authorization payload hash mismatch",
        )

        require(
            self.issued_at_ms > 0,
            "authorization timestamp invalid",
        )

        if self.consumed:
            require(
                self.consumed_at_ms is not None,
                "consumed authorization missing timestamp",
            )


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

    def validate(self) -> None:
        require(bool(self.dispatch_id), "dispatch id required")
        require(bool(self.intent_id), "intent id required")

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
            self.transport_method == TRANSPORT_METHOD,
            "transport method mismatch",
        )
        require(
            self.transport_path == LEVERAGE_ENDPOINT,
            "transport path mismatch",
        )

        require(
            canonical_json(self.payload) == EXACT_LEVERAGE_PAYLOAD_JSON,
            "exact leverage payload mismatch",
        )

        require(
            sha256_json(self.payload) == self.payload_hash,
            "dispatch payload hash corrupted",
        )

        require(
            self.payload_hash == EXACT_LEVERAGE_PAYLOAD_HASH,
            "dispatch payload hash mismatch",
        )


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

    def validate(self) -> None:
        require(bool(self.receipt_id), "receipt id required")
        require(bool(self.dispatch_id), "receipt dispatch required")

        require(
            self.status == SYNTHETIC_RECEIPT_STATUS,
            "unexpected synthetic receipt status",
        )

        require(
            self.transport_method == TRANSPORT_METHOD,
            "receipt transport method mismatch",
        )
        require(
            self.transport_path == LEVERAGE_ENDPOINT,
            "receipt transport path mismatch",
        )
        require(
            self.payload_hash == EXACT_LEVERAGE_PAYLOAD_HASH,
            "receipt payload hash mismatch",
        )

        require(
            self.transmitted is False,
            "synthetic receipt cannot report transmission",
        )
        require(
            self.network_write is False,
            "synthetic receipt cannot report network write",
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

    payload_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        require(self.sequence > 0, "journal sequence invalid")
        require(bool(self.event), "journal event required")
        require(self.timestamp_ms > 0, "journal timestamp invalid")

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

    active_lease: Optional[RecoveryLease]
    authorization: Optional[RecoveryAuthorization]
    dispatch_binding: Optional[DispatchBinding]
    receipt: Optional[SyntheticReceipt]

    journal: List[JournalRecord]

    completed_dispatch_ids: Set[str]
    consumed_authorization_ids: Set[str]
    retired_lease_ids: Set[str]

    snapshot_sequence: int
    integrity_seal: str = ""

    def fence(self) -> GenerationFence:
        return GenerationFence(
            account_epoch=self.account_epoch,
            symbol_epoch=self.symbol_epoch,
            position_epoch=self.position_epoch,
            recovery_epoch=self.recovery_epoch,
            generation=self.generation,
            lineage_id=self.lineage_id,
        )

    def validate_basic(self) -> None:
        require(
            self.schema_version == STATE_SCHEMA_VERSION,
            "unsupported durable state schema",
        )

        require(
            self.state in ALL_STATES,
            "invalid durable execution state",
        )

        require(self.account_epoch > 0, "account epoch invalid")
        require(self.symbol_epoch > 0, "symbol epoch invalid")
        require(self.position_epoch > 0, "position epoch invalid")
        require(self.recovery_epoch > 0, "recovery epoch invalid")

        require(self.generation > 0, "generation invalid")
        require(bool(self.lineage_id), "lineage id required")

        require(bool(self.intent_id), "intent id required")
        require(bool(self.dispatch_id), "dispatch id required")

        require(self.lease_nonce >= 0, "lease nonce invalid")
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

        for record in self.journal:
            record.validate()


# ============================================================================
# DURABLE STATE SERIALIZATION HELPERS
# ============================================================================

def recovery_lease_to_dict(
    lease: Optional[RecoveryLease],
) -> Optional[Dict[str, Any]]:
    if lease is None:
        return None
    return asdict(lease)


def authorization_to_dict(
    authorization: Optional[RecoveryAuthorization],
) -> Optional[Dict[str, Any]]:
    if authorization is None:
        return None
    return asdict(authorization)


def dispatch_binding_to_dict(
    binding: Optional[DispatchBinding],
) -> Optional[Dict[str, Any]]:
    if binding is None:
        return None
    return asdict(binding)


def receipt_to_dict(
    receipt: Optional[SyntheticReceipt],
) -> Optional[Dict[str, Any]]:
    if receipt is None:
        return None
    return asdict(receipt)


def journal_record_to_dict(
    record: JournalRecord,
) -> Dict[str, Any]:
    return asdict(record)


def state_payload_without_seal(state: DurableState) -> Dict[str, Any]:
    return {
        "schema_version": state.schema_version,
        "state": state.state,

        "account_epoch": state.account_epoch,
        "symbol_epoch": state.symbol_epoch,
        "position_epoch": state.position_epoch,
        "recovery_epoch": state.recovery_epoch,

        "generation": state.generation,
        "lineage_id": state.lineage_id,

        "intent_id": state.intent_id,
        "dispatch_id": state.dispatch_id,

        "lease_nonce": state.lease_nonce,

        "active_lease": recovery_lease_to_dict(state.active_lease),
        "authorization": authorization_to_dict(state.authorization),
        "dispatch_binding": dispatch_binding_to_dict(
            state.dispatch_binding
        ),
        "receipt": receipt_to_dict(state.receipt),

        "journal": [
            journal_record_to_dict(record)
            for record in state.journal
        ],

        "completed_dispatch_ids": sorted(
            state.completed_dispatch_ids
        ),
        "consumed_authorization_ids": sorted(
            state.consumed_authorization_ids
        ),
        "retired_lease_ids": sorted(
            state.retired_lease_ids
        ),

        "snapshot_sequence": state.snapshot_sequence,
    }


def calculate_state_integrity_seal(
    state: DurableState,
) -> str:
    return sha256_json(state_payload_without_seal(state))


def seal_state(state: DurableState) -> DurableState:
    state.integrity_seal = calculate_state_integrity_seal(state)
    return state


def verify_state_integrity(state: DurableState) -> None:
    expected = calculate_state_integrity_seal(state)

    require(
        bool(state.integrity_seal),
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
# ============================================================================

class SyntheticTransport:
    """
    Final transport boundary for Unit N.23.

    This class intentionally performs NO HTTP request and NO socket write.
    It only verifies the exact transport binding and returns a synthetic
    local receipt.
    """

    def __init__(self) -> None:
        self.dispatch_count = 0
        self.network_write_count = 0
        self.real_post_count = 0
        self.demo_post_count = 0
        self.leverage_transmission_count = 0

        self._lock = threading.RLock()

    def dispatch(
        self,
        binding: DispatchBinding,
    ) -> SyntheticReceipt:
        with self._lock:
            binding.validate()

            require(
                LIVE_ORDER_EXECUTION is False,
                "live order execution must remain disabled",
            )
            require(
                DEMO_ORDER_EXECUTION is False,
                "demo order execution must remain disabled",
            )
            require(
                NETWORK_WRITES_ENABLED is False,
                "network writes must remain disabled",
            )
            require(
                REAL_POST_ENABLED is False,
                "real POST must remain disabled",
            )
            require(
                DEMO_POST_ENABLED is False,
                "demo POST must remain disabled",
            )
            require(
                LEVERAGE_TRANSMISSION_ENABLED is False,
                "leverage transmission must remain disabled",
            )

            self.dispatch_count += 1

            receipt = SyntheticReceipt(
                receipt_id=deterministic_id(
                    "receipt",
                    binding.dispatch_id,
                    binding.generation,
                    binding.lineage_id,
                    binding.recovery_epoch,
                    binding.payload_hash,
                ),
                dispatch_id=binding.dispatch_id,
                status=SYNTHETIC_RECEIPT_STATUS,

                transport_method=binding.transport_method,
                transport_path=binding.transport_path,
                payload_hash=binding.payload_hash,

                transmitted=False,
                network_write=False,

                generation=binding.generation,
                lineage_id=binding.lineage_id,
                recovery_epoch=binding.recovery_epoch,

                created_at_ms=now_ms(),
            )

            receipt.validate()
            return receipt


# ============================================================================
# END OF PART 1
# ============================================================================

print("R28 UNIT N.23: PART 1 DEFINITIONS LOADED", flush=True)
