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
# ============================================================================
# R28 UNIT N.23
# CORRECTED COPY/PASTE VERSION
# PART 2 OF 4
#
# N23 ENGINE
# ============================================================================


class N23Engine:
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

        lineage_id = secure_id("lineage")

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
            receipt=None,

            journal=[],

            completed_dispatch_ids=set(),
            consumed_authorization_ids=set(),
            retired_lease_ids=set(),

            snapshot_sequence=0,
            integrity_seal="",
        )

        self._append_journal(
            event="ENGINE_INITIALIZED",
            metadata={
                "symbol": SYMBOL,
                "leverage": LEVERAGE,
                "margin_mode": MARGIN_MODE,
            },
        )

        self._seal()

    # ========================================================================
    # INTERNAL JOURNAL
    # ========================================================================

    def _append_journal(
        self,
        event: str,
        owner_id: Optional[str] = None,
        lease_id: Optional[str] = None,
        authorization_id: Optional[str] = None,
        intent_id: Optional[str] = None,
        dispatch_id: Optional[str] = None,
        payload_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JournalRecord:
        with self._lock:
            sequence = len(self.state.journal) + 1

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

                payload_hash=payload_hash,
                metadata=(
                    clone(metadata)
                    if metadata is not None
                    else {}
                ),
            )

            record.validate()
            self.state.journal.append(record)

            return record

    # ========================================================================
    # STATE INTEGRITY
    # ========================================================================

    def _seal(self) -> None:
        with self._lock:
            self.state.snapshot_sequence += 1
            seal_state(self.state)

    def verify_integrity(self) -> None:
        with self._lock:
            self.state.validate_basic()
            verify_state_integrity(self.state)
            self._validate_structural_invariants()

    def _validate_structural_invariants(self) -> None:
        state = self.state

        require(
            state.intent_id
            == deterministic_id(
                "intent",
                SYMBOL,
                state.account_epoch,
                state.symbol_epoch,
                state.position_epoch,
                state.recovery_epoch,
                state.generation,
                state.lineage_id,
            ),
            "intent identity mismatch",
        )

        require(
            state.dispatch_id
            == deterministic_id(
                "dispatch",
                state.intent_id,
                EXACT_LEVERAGE_PAYLOAD_HASH,
            ),
            "dispatch identity mismatch",
        )

        if state.active_lease is not None:
            lease = state.active_lease

            require(
                lease.generation == state.generation,
                "active lease generation mismatch",
            )
            require(
                lease.lineage_id == state.lineage_id,
                "active lease lineage mismatch",
            )
            require(
                lease.recovery_epoch == state.recovery_epoch,
                "active lease recovery epoch mismatch",
            )
            require(
                lease.fence_hash == state.fence().fingerprint(),
                "recovery lease fence mismatch",
            )
            require(
                lease.lease_id not in state.retired_lease_ids,
                "retired lease cannot be active",
            )

        if state.authorization is not None:
            authorization = state.authorization

            require(
                authorization.generation == state.generation,
                "authorization generation mismatch",
            )
            require(
                authorization.lineage_id == state.lineage_id,
                "authorization lineage mismatch",
            )
            require(
                authorization.recovery_epoch
                == state.recovery_epoch,
                "authorization recovery epoch mismatch",
            )
            require(
                authorization.intent_id == state.intent_id,
                "authorization intent mismatch",
            )
            require(
                authorization.dispatch_id == state.dispatch_id,
                "authorization dispatch mismatch",
            )

            if authorization.consumed:
                require(
                    authorization.authorization_id
                    in state.consumed_authorization_ids,
                    "consumed authorization not persisted",
                )
            else:
                require(
                    authorization.authorization_id
                    not in state.consumed_authorization_ids,
                    "unconsumed authorization marked consumed",
                )

        if state.dispatch_binding is not None:
            binding = state.dispatch_binding

            require(
                binding.intent_id == state.intent_id,
                "binding intent mismatch",
            )
            require(
                binding.dispatch_id == state.dispatch_id,
                "binding dispatch mismatch",
            )
            require(
                binding.generation == state.generation,
                "binding generation mismatch",
            )
            require(
                binding.lineage_id == state.lineage_id,
                "binding lineage mismatch",
            )
            require(
                binding.recovery_epoch
                == state.recovery_epoch,
                "binding recovery epoch mismatch",
            )

        if state.receipt is not None:
            receipt = state.receipt

            require(
                receipt.dispatch_id == state.dispatch_id,
                "receipt dispatch mismatch",
            )
            require(
                receipt.generation == state.generation,
                "receipt generation mismatch",
            )
            require(
                receipt.lineage_id == state.lineage_id,
                "receipt lineage mismatch",
            )
            require(
                receipt.recovery_epoch
                == state.recovery_epoch,
                "receipt recovery epoch mismatch",
            )

        if state.state == "COMPLETED":
            require(
                state.receipt is not None,
                "completed state missing synthetic receipt",
            )
            require(
                state.dispatch_id
                in state.completed_dispatch_ids,
                "completed dispatch not persisted",
            )

        if state.dispatch_id in state.completed_dispatch_ids:
            require(
                state.state == "COMPLETED",
                "completed dispatch requires terminal completed state",
            )

    # ========================================================================
    # LEASE ACQUISITION
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

            if self.state.state in TERMINAL_STATES:
                local_block(
                    "terminal generation cannot acquire recovery lease"
                )
                raise ValueError(
                    "terminal generation cannot acquire recovery lease"
                )

            if self.state.active_lease is not None:
                active = self.state.active_lease

                if active.owner_id == owner_id:
                    return active

                local_block(
                    "recovery lease already owned by another worker"
                )
                raise ValueError(
                    "recovery lease already owned by another worker"
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
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                nonce=self.state.lease_nonce,
                issued_at_ms=now_ms(),
                fence_hash=self.state.fence().fingerprint(),
            )

            lease.validate()

            self.state.active_lease = lease

            self._append_journal(
                event="RECOVERY_LEASE_ACQUIRED",
                owner_id=owner_id,
                lease_id=lease.lease_id,
                metadata={
                    "nonce": lease.nonce,
                    "fence_hash": lease.fence_hash,
                },
            )

            self._seal()
            self.verify_integrity()

            return clone(lease)

    # ========================================================================
    # LEASE VALIDATION
    # ========================================================================

    def _validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        lease.validate()

        active = self.state.active_lease

        require(
            active is not None,
            "no active recovery lease",
        )

        require(
            lease.lease_id == active.lease_id,
            "recovery lease id mismatch",
        )
        require(
            lease.owner_id == active.owner_id,
            "recovery lease owner mismatch",
        )
        require(
            lease.generation == self.state.generation,
            "recovery lease generation mismatch",
        )
        require(
            lease.lineage_id == self.state.lineage_id,
            "recovery lease lineage mismatch",
        )
        require(
            lease.recovery_epoch
            == self.state.recovery_epoch,
            "recovery lease epoch mismatch",
        )
        require(
            lease.nonce == active.nonce,
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
            self._validate_lease(lease)

            require(
                self.state.state not in TERMINAL_STATES,
                "terminal state cannot authorize recovery",
            )

            existing = self.state.authorization

            if existing is not None:
                if existing.consumed:
                    local_block(
                        "recovery authorization already consumed"
                    )
                    raise ValueError(
                        "recovery authorization already consumed"
                    )

                require(
                    existing.owner_id == lease.owner_id,
                    "existing authorization owner mismatch",
                )
                require(
                    existing.lease_id == lease.lease_id,
                    "existing authorization lease mismatch",
                )

                return clone(existing)

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
                owner_id=lease.owner_id,
                lease_id=lease.lease_id,

                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                nonce=lease.nonce,

                intent_id=self.state.intent_id,
                dispatch_id=self.state.dispatch_id,

                transport_method=TRANSPORT_METHOD,
                transport_path=LEVERAGE_ENDPOINT,
                payload_hash=EXACT_LEVERAGE_PAYLOAD_HASH,

                issued_at_ms=now_ms(),
                consumed=False,
                consumed_at_ms=None,
            )

            authorization.validate()

            self.state.authorization = authorization
            self.state.state = "AUTHORIZED"

            self._append_journal(
                event="RECOVERY_AUTHORIZATION_ISSUED",
                owner_id=lease.owner_id,
                lease_id=lease.lease_id,
                authorization_id=authorization.authorization_id,
                payload_hash=authorization.payload_hash,
            )

            self._seal()
            self.verify_integrity()

            return clone(authorization)

    # ========================================================================
    # AUTHORIZATION VALIDATION
    # ========================================================================

    def _validate_authorization(
        self,
        authorization: RecoveryAuthorization,
        lease: RecoveryLease,
    ) -> None:
        authorization.validate()
        self._validate_lease(lease)

        persisted = self.state.authorization

        require(
            persisted is not None,
            "no persisted recovery authorization",
        )

        require(
            authorization.authorization_id
            == persisted.authorization_id,
            "authorization id mismatch",
        )
        require(
            authorization.owner_id == lease.owner_id,
            "authorization owner mismatch",
        )
        require(
            authorization.lease_id == lease.lease_id,
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
            "authorization recovery epoch mismatch",
        )
        require(
            authorization.nonce == lease.nonce,
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
            "authorization transport method mismatch",
        )
        require(
            authorization.transport_path
            == LEVERAGE_ENDPOINT,
            "authorization transport path mismatch",
        )
        require(
            authorization.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH,
            "authorization payload hash mismatch",
        )

        require(
            authorization.consumed is False,
            "authorization already consumed",
        )
        require(
            authorization.authorization_id
            not in self.state.consumed_authorization_ids,
            "authorization replay rejected",
        )

    # ========================================================================
    # EXACT DISPATCH BINDING
    # ========================================================================

    def prepare_dispatch_binding(
        self,
        lease: RecoveryLease,
        authorization: RecoveryAuthorization,
    ) -> DispatchBinding:
        with self._lock:
            self.verify_integrity()

            self._validate_authorization(
                authorization,
                lease,
            )

            existing = self.state.dispatch_binding

            if existing is not None:
                existing.validate()
                return clone(existing)

            payload = build_exact_leverage_payload()

            binding = DispatchBinding(
                dispatch_id=self.state.dispatch_id,
                intent_id=self.state.intent_id,

                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,

                transport_method=TRANSPORT_METHOD,
                transport_path=LEVERAGE_ENDPOINT,

                payload=payload,
                payload_hash=sha256_json(payload),
            )

            binding.validate()

            self.state.dispatch_binding = binding
            self.state.state = "DISPATCH_PREPARED"

            self._append_journal(
                event="DISPATCH_BINDING_PREPARED",
                owner_id=lease.owner_id,
                lease_id=lease.lease_id,
                authorization_id=authorization.authorization_id,
                dispatch_id=binding.dispatch_id,
                payload_hash=binding.payload_hash,
                metadata={
                    "method": binding.transport_method,
                    "path": binding.transport_path,
                },
            )

            self._seal()
            self.verify_integrity()

            return clone(binding)

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
            authorization_id=authorization.authorization_id,
            owner_id=authorization.owner_id,
            lease_id=authorization.lease_id,

            generation=authorization.generation,
            lineage_id=authorization.lineage_id,
            recovery_epoch=authorization.recovery_epoch,
            nonce=authorization.nonce,

            intent_id=authorization.intent_id,
            dispatch_id=authorization.dispatch_id,

            transport_method=authorization.transport_method,
            transport_path=authorization.transport_path,
            payload_hash=authorization.payload_hash,

            issued_at_ms=authorization.issued_at_ms,
            consumed=True,
            consumed_at_ms=now_ms(),
        )

        consumed.validate()

        self.state.authorization = consumed
        self.state.consumed_authorization_ids.add(
            consumed.authorization_id
        )

        self._append_journal(
            event="RECOVERY_AUTHORIZATION_CONSUMED",
            owner_id=lease.owner_id,
            lease_id=lease.lease_id,
            authorization_id=consumed.authorization_id,
            dispatch_id=consumed.dispatch_id,
            payload_hash=consumed.payload_hash,
        )

        return consumed

    # ========================================================================
    # FINAL SYNTHETIC DISPATCH
    # ========================================================================

    def execute_synthetic_dispatch(
        self,
        lease: RecoveryLease,
        authorization: RecoveryAuthorization,
        binding: DispatchBinding,
    ) -> SyntheticReceipt:
        with self._lock:
            self.verify_integrity()

            self._validate_lease(lease)
            self._validate_authorization(
                authorization,
                lease,
            )

            persisted_binding = self.state.dispatch_binding

            require(
                persisted_binding is not None,
                "dispatch binding not prepared",
            )

            binding.validate()

            require(
                binding == persisted_binding,
                "dispatch binding mismatch",
            )

            require(
                binding.dispatch_id
                not in self.state.completed_dispatch_ids,
                "dispatch replay rejected",
            )

            consumed = self._consume_authorization(
                lease,
                authorization,
            )

            self._seal()
            self.verify_integrity()

            receipt = self.transport.dispatch(binding)
            receipt.validate()

            require(
                consumed.authorization_id
                in self.state.consumed_authorization_ids,
                "authorization consumption not durable",
            )

            self.state.receipt = receipt
            self.state.completed_dispatch_ids.add(
                binding.dispatch_id
            )
            self.state.state = "COMPLETED"

            self._append_journal(
                event="SYNTHETIC_DISPATCH_COMPLETED",
                owner_id=lease.owner_id,
                lease_id=lease.lease_id,
                authorization_id=consumed.authorization_id,
                dispatch_id=binding.dispatch_id,
                payload_hash=binding.payload_hash,
                metadata={
                    "receipt_id": receipt.receipt_id,
                    "transmitted": receipt.transmitted,
                    "network_write": receipt.network_write,
                },
            )

            self._retire_active_lease(
                lease,
                reason="generation completed",
            )

            self._seal()
            self.verify_integrity()

            return clone(receipt)

    # ========================================================================
    # LEASE RETIREMENT
    # ========================================================================

    def _retire_active_lease(
        self,
        lease: RecoveryLease,
        reason: str,
    ) -> None:
        self._validate_lease(lease)

        self.state.retired_lease_ids.add(
            lease.lease_id
        )

        self._append_journal(
            event="RECOVERY_LEASE_RETIRED",
            owner_id=lease.owner_id,
            lease_id=lease.lease_id,
            metadata={
                "reason": reason,
                "nonce": lease.nonce,
            },
        )

        self.state.active_lease = None

    # ========================================================================
    # ONE-SHOT RECOVERY
    # ========================================================================

    def recover(
        self,
        owner_id: str,
    ) -> SyntheticReceipt:
        with self._lock:
            self.verify_integrity()

            if self.state.state == "COMPLETED":
                require(
                    self.state.receipt is not None,
                    "completed generation missing receipt",
                )
                return clone(self.state.receipt)

            lease = self.acquire_recovery_lease(
                owner_id
            )

            authorization = (
                self.issue_recovery_authorization(
                    lease
                )
            )

            binding = self.prepare_dispatch_binding(
                lease,
                authorization,
            )

            return self.execute_synthetic_dispatch(
                lease,
                authorization,
                binding,
            )

    # ========================================================================
    # SNAPSHOT EXPORT
    # ========================================================================

    def snapshot_state(self) -> DurableState:
        with self._lock:
            self.verify_integrity()
            return clone(self.state)

    def snapshot_dict(self) -> Dict[str, Any]:
        with self._lock:
            state = self.snapshot_state()

            payload = state_payload_without_seal(
                state
            )

            payload["integrity_seal"] = (
                state.integrity_seal
            )

            return payload


# ============================================================================
# END OF PART 2
# ============================================================================
# ============================================================================
# R28 UNIT N.23
# CORRECTED COPY/PASTE VERSION
# PART 3 OF 4
#
# DURABLE RESTORE + GENERATION LINEAGE + ANTI-ABA RECOVERY
# ============================================================================


# ============================================================================
# DESERIALIZATION HELPERS
# ============================================================================

def recovery_lease_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[RecoveryLease]:
    if value is None:
        return None

    lease = RecoveryLease(
        lease_id=str(value["lease_id"]),
        owner_id=str(value["owner_id"]),
        generation=int(value["generation"]),
        lineage_id=str(value["lineage_id"]),
        recovery_epoch=int(value["recovery_epoch"]),
        nonce=int(value["nonce"]),
        issued_at_ms=int(value["issued_at_ms"]),
        fence_hash=str(value["fence_hash"]),
    )

    lease.validate()
    return lease


def authorization_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[RecoveryAuthorization]:
    if value is None:
        return None

    consumed_at_raw = value.get(
        "consumed_at_ms"
    )

    authorization = RecoveryAuthorization(
        authorization_id=str(
            value["authorization_id"]
        ),
        owner_id=str(
            value["owner_id"]
        ),
        lease_id=str(
            value["lease_id"]
        ),

        generation=int(
            value["generation"]
        ),
        lineage_id=str(
            value["lineage_id"]
        ),
        recovery_epoch=int(
            value["recovery_epoch"]
        ),
        nonce=int(
            value["nonce"]
        ),

        intent_id=str(
            value["intent_id"]
        ),
        dispatch_id=str(
            value["dispatch_id"]
        ),

        transport_method=str(
            value["transport_method"]
        ),
        transport_path=str(
            value["transport_path"]
        ),
        payload_hash=str(
            value["payload_hash"]
        ),

        issued_at_ms=int(
            value["issued_at_ms"]
        ),
        consumed=bool(
            value.get("consumed", False)
        ),
        consumed_at_ms=(
            int(consumed_at_raw)
            if consumed_at_raw is not None
            else None
        ),
    )

    authorization.validate()
    return authorization


def dispatch_binding_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[DispatchBinding]:
    if value is None:
        return None

    payload_raw = value.get("payload")

    require(
        isinstance(payload_raw, dict),
        "dispatch payload must be object",
    )

    payload = {
        str(key): str(item)
        for key, item in payload_raw.items()
    }

    binding = DispatchBinding(
        dispatch_id=str(
            value["dispatch_id"]
        ),
        intent_id=str(
            value["intent_id"]
        ),

        generation=int(
            value["generation"]
        ),
        lineage_id=str(
            value["lineage_id"]
        ),
        recovery_epoch=int(
            value["recovery_epoch"]
        ),

        transport_method=str(
            value["transport_method"]
        ),
        transport_path=str(
            value["transport_path"]
        ),

        payload=payload,
        payload_hash=str(
            value["payload_hash"]
        ),
    )

    binding.validate()
    return binding


def receipt_from_dict(
    value: Optional[Dict[str, Any]],
) -> Optional[SyntheticReceipt]:
    if value is None:
        return None

    receipt = SyntheticReceipt(
        receipt_id=str(
            value["receipt_id"]
        ),
        dispatch_id=str(
            value["dispatch_id"]
        ),
        status=str(
            value["status"]
        ),

        transport_method=str(
            value["transport_method"]
        ),
        transport_path=str(
            value["transport_path"]
        ),
        payload_hash=str(
            value["payload_hash"]
        ),

        transmitted=bool(
            value["transmitted"]
        ),
        network_write=bool(
            value["network_write"]
        ),

        generation=int(
            value["generation"]
        ),
        lineage_id=str(
            value["lineage_id"]
        ),
        recovery_epoch=int(
            value["recovery_epoch"]
        ),

        created_at_ms=int(
            value["created_at_ms"]
        ),
    )

    receipt.validate()
    return receipt


def journal_record_from_dict(
    value: Dict[str, Any],
) -> JournalRecord:
    metadata_raw = value.get(
        "metadata",
        {},
    )

    require(
        isinstance(metadata_raw, dict),
        "journal metadata must be object",
    )

    record = JournalRecord(
        sequence=int(
            value["sequence"]
        ),
        event=str(
            value["event"]
        ),
        timestamp_ms=int(
            value["timestamp_ms"]
        ),

        generation=int(
            value["generation"]
        ),
        lineage_id=str(
            value["lineage_id"]
        ),
        recovery_epoch=int(
            value["recovery_epoch"]
        ),

        owner_id=(
            str(value["owner_id"])
            if value.get("owner_id")
            is not None
            else None
        ),
        lease_id=(
            str(value["lease_id"])
            if value.get("lease_id")
            is not None
            else None
        ),
        authorization_id=(
            str(value["authorization_id"])
            if value.get("authorization_id")
            is not None
            else None
        ),
        intent_id=(
            str(value["intent_id"])
            if value.get("intent_id")
            is not None
            else None
        ),
        dispatch_id=(
            str(value["dispatch_id"])
            if value.get("dispatch_id")
            is not None
            else None
        ),

        payload_hash=(
            str(value["payload_hash"])
            if value.get("payload_hash")
            is not None
            else None
        ),

        metadata=clone(
            metadata_raw
        ),
    )

    record.validate()
    return record


def durable_state_from_dict(
    value: Dict[str, Any],
) -> DurableState:
    require(
        isinstance(value, dict),
        "snapshot must be object",
    )

    journal_raw = value.get(
        "journal",
        [],
    )

    require(
        isinstance(journal_raw, list),
        "snapshot journal must be list",
    )

    completed_raw = value.get(
        "completed_dispatch_ids",
        [],
    )

    consumed_raw = value.get(
        "consumed_authorization_ids",
        [],
    )

    retired_raw = value.get(
        "retired_lease_ids",
        [],
    )

    require(
        isinstance(completed_raw, list),
        "completed dispatch set invalid",
    )

    require(
        isinstance(consumed_raw, list),
        "consumed authorization set invalid",
    )

    require(
        isinstance(retired_raw, list),
        "retired lease set invalid",
    )

    state = DurableState(
        schema_version=int(
            value["schema_version"]
        ),

        state=str(
            value["state"]
        ),

        account_epoch=int(
            value["account_epoch"]
        ),
        symbol_epoch=int(
            value["symbol_epoch"]
        ),
        position_epoch=int(
            value["position_epoch"]
        ),
        recovery_epoch=int(
            value["recovery_epoch"]
        ),

        generation=int(
            value["generation"]
        ),
        lineage_id=str(
            value["lineage_id"]
        ),

        intent_id=str(
            value["intent_id"]
        ),
        dispatch_id=str(
            value["dispatch_id"]
        ),

        lease_nonce=int(
            value["lease_nonce"]
        ),

        active_lease=recovery_lease_from_dict(
            value.get("active_lease")
        ),
        authorization=authorization_from_dict(
            value.get("authorization")
        ),
        dispatch_binding=dispatch_binding_from_dict(
            value.get("dispatch_binding")
        ),
        receipt=receipt_from_dict(
            value.get("receipt")
        ),

        journal=[
            journal_record_from_dict(
                record
            )
            for record in journal_raw
        ],

        completed_dispatch_ids={
            str(item)
            for item in completed_raw
        },

        consumed_authorization_ids={
            str(item)
            for item in consumed_raw
        },

        retired_lease_ids={
            str(item)
            for item in retired_raw
        },

        snapshot_sequence=int(
            value["snapshot_sequence"]
        ),

        integrity_seal=str(
            value.get(
                "integrity_seal",
                "",
            )
        ),
    )

    state.validate_basic()
    verify_state_integrity(state)

    return state


# ============================================================================
# RESTORE VALIDATION
# ============================================================================

def validate_restored_journal(
    state: DurableState,
) -> None:
    expected_sequence = 1

    for record in state.journal:
        require(
            record.sequence
            == expected_sequence,
            "journal sequence discontinuity",
        )

        expected_sequence += 1


def validate_restored_state(
    state: DurableState,
) -> None:
    state.validate_basic()
    verify_state_integrity(state)
    validate_restored_journal(state)

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
        "restored intent identity mismatch",
    )

    expected_dispatch_id = deterministic_id(
        "dispatch",
        state.intent_id,
        EXACT_LEVERAGE_PAYLOAD_HASH,
    )

    require(
        state.dispatch_id
        == expected_dispatch_id,
        "restored dispatch identity mismatch",
    )

    if state.active_lease is not None:
        lease = state.active_lease

        require(
            lease.generation
            == state.generation,
            "restored lease generation mismatch",
        )

        require(
            lease.lineage_id
            == state.lineage_id,
            "restored lease lineage mismatch",
        )

        require(
            lease.recovery_epoch
            == state.recovery_epoch,
            "restored lease recovery epoch mismatch",
        )

        require(
            lease.fence_hash
            == state.fence().fingerprint(),
            "restored lease fence mismatch",
        )

        require(
            lease.lease_id
            not in state.retired_lease_ids,
            "restored active lease already retired",
        )

    if state.authorization is not None:
        authorization = state.authorization

        require(
            authorization.generation
            == state.generation,
            "restored authorization generation mismatch",
        )

        require(
            authorization.lineage_id
            == state.lineage_id,
            "restored authorization lineage mismatch",
        )

        require(
            authorization.recovery_epoch
            == state.recovery_epoch,
            "restored authorization epoch mismatch",
        )

        require(
            authorization.intent_id
            == state.intent_id,
            "restored authorization intent mismatch",
        )

        require(
            authorization.dispatch_id
            == state.dispatch_id,
            "restored authorization dispatch mismatch",
        )

        if authorization.consumed:
            require(
                authorization.authorization_id
                in state.consumed_authorization_ids,
                "consumed authorization lost on restore",
            )

    if state.dispatch_binding is not None:
        binding = state.dispatch_binding

        binding.validate()

        require(
            binding.dispatch_id
            == state.dispatch_id,
            "restored binding dispatch mismatch",
        )

        require(
            binding.intent_id
            == state.intent_id,
            "restored binding intent mismatch",
        )

        require(
            binding.generation
            == state.generation,
            "restored binding generation mismatch",
        )

        require(
            binding.lineage_id
            == state.lineage_id,
            "restored binding lineage mismatch",
        )

        require(
            binding.recovery_epoch
            == state.recovery_epoch,
            "restored binding epoch mismatch",
        )

    if state.receipt is not None:
        receipt = state.receipt

        receipt.validate()

        require(
            receipt.dispatch_id
            == state.dispatch_id,
            "restored receipt dispatch mismatch",
        )

    if state.state == "COMPLETED":
        require(
            state.receipt is not None,
            "restored completed state missing receipt",
        )

        require(
            state.dispatch_id
            in state.completed_dispatch_ids,
            "restored completed dispatch missing",
        )


# ============================================================================
# ENGINE RESTORATION
#
# IMPORTANT:
# This is intentionally TOP-LEVEL code.
# It is NOT indented inside class N23Engine.
# ============================================================================

def _n23_restore_state(
    cls: Any,
    state: DurableState,
) -> "N23Engine":
    require(
        isinstance(state, DurableState),
        "restore requires DurableState",
    )

    restored_state = clone(
        state
    )

    validate_restored_state(
        restored_state
    )

    engine = cls.__new__(
        cls
    )

    engine._lock = threading.RLock()
    engine.transport = SyntheticTransport()
    engine.state = restored_state

    engine.verify_integrity()

    return engine


N23Engine.restore_state = classmethod(
    _n23_restore_state
)


# ============================================================================
# RESTORE FROM DICTIONARY
# ============================================================================

def _n23_restore_dict(
    cls: Any,
    value: Dict[str, Any],
) -> "N23Engine":
    state = durable_state_from_dict(
        value
    )

    return cls.restore_state(
        state
    )


N23Engine.restore_dict = classmethod(
    _n23_restore_dict
)


# ============================================================================
# GENERATION ROLLOVER
# ============================================================================

def advance_generation(
    engine: N23Engine,
) -> DurableState:
    with engine._lock:
        engine.verify_integrity()

        require(
            engine.state.state
            in TERMINAL_STATES,
            "generation can advance only after terminal state",
        )

        previous = clone(
            engine.state
        )

        next_generation = (
            previous.generation + 1
        )

        next_recovery_epoch = (
            previous.recovery_epoch + 1
        )

        next_lineage_id = secure_id(
            "lineage"
        )

        next_intent_id = deterministic_id(
            "intent",
            SYMBOL,
            previous.account_epoch,
            previous.symbol_epoch,
            previous.position_epoch,
            next_recovery_epoch,
            next_generation,
            next_lineage_id,
        )

        next_dispatch_id = deterministic_id(
            "dispatch",
            next_intent_id,
            EXACT_LEVERAGE_PAYLOAD_HASH,
        )

        next_state = DurableState(
            schema_version=STATE_SCHEMA_VERSION,

            state="PREPARED",

            account_epoch=previous.account_epoch,
            symbol_epoch=previous.symbol_epoch,
            position_epoch=previous.position_epoch,

            recovery_epoch=next_recovery_epoch,

            generation=next_generation,
            lineage_id=next_lineage_id,

            intent_id=next_intent_id,
            dispatch_id=next_dispatch_id,

            lease_nonce=previous.lease_nonce,

            active_lease=None,
            authorization=None,
            dispatch_binding=None,
            receipt=None,

            journal=clone(
                previous.journal
            ),

            completed_dispatch_ids=set(
                previous.completed_dispatch_ids
            ),

            consumed_authorization_ids=set(
                previous.consumed_authorization_ids
            ),

            retired_lease_ids=set(
                previous.retired_lease_ids
            ),

            snapshot_sequence=(
                previous.snapshot_sequence
            ),

            integrity_seal="",
        )

        engine.state = next_state

        engine._append_journal(
            event="GENERATION_ADVANCED",
            metadata={
                "previous_generation":
                    previous.generation,

                "new_generation":
                    next_generation,

                "previous_lineage":
                    previous.lineage_id,

                "new_lineage":
                    next_lineage_id,

                "previous_recovery_epoch":
                    previous.recovery_epoch,

                "new_recovery_epoch":
                    next_recovery_epoch,
            },
        )

        engine._seal()
        engine.verify_integrity()

        return clone(
            engine.state
        )


# ============================================================================
# ANTI-ABA LEASE CHECK
# ============================================================================

def validate_lease_against_current_generation(
    engine: N23Engine,
    lease: RecoveryLease,
) -> None:
    engine.verify_integrity()

    require(
        lease.generation
        == engine.state.generation,
        "stale generation lease rejected",
    )

    require(
        lease.lineage_id
        == engine.state.lineage_id,
        "stale lineage lease rejected",
    )

    require(
        lease.recovery_epoch
        == engine.state.recovery_epoch,
        "stale recovery epoch lease rejected",
    )

    require(
        lease.fence_hash
        == engine.state.fence().fingerprint(),
        "recovery lease fence mismatch",
    )

    require(
        lease.lease_id
        not in engine.state.retired_lease_ids,
        "retired recovery lease rejected",
    )


# ============================================================================
# CRASH/RESTART HELPER
# ============================================================================

def simulate_restart(
    engine: N23Engine,
) -> N23Engine:
    snapshot = engine.snapshot_state()

    restarted = N23Engine.restore_state(
        snapshot
    )

    restarted.verify_integrity()

    return restarted


# ============================================================================
# SNAPSHOT TAMPER HELPER
# ============================================================================

def clone_snapshot_dict(
    engine: N23Engine,
) -> Dict[str, Any]:
    return clone(
        engine.snapshot_dict()
    )


# ============================================================================
# FINAL NETWORK FIREBREAK ASSERTION
# ============================================================================

def assert_transport_firebreak(
    transport: SyntheticTransport,
) -> None:
    require(
        LIVE_ORDER_EXECUTION is False,
        "live execution unexpectedly enabled",
    )

    require(
        DEMO_ORDER_EXECUTION is False,
        "demo execution unexpectedly enabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "network writes unexpectedly enabled",
    )

    require(
        REAL_POST_ENABLED is False,
        "real POST unexpectedly enabled",
    )

    require(
        DEMO_POST_ENABLED is False,
        "demo POST unexpectedly enabled",
    )

    require(
        LEVERAGE_TRANSMISSION_ENABLED is False,
        "leverage transmission unexpectedly enabled",
    )

    require(
        transport.network_write_count == 0,
        "network write detected",
    )

    require(
        transport.real_post_count == 0,
        "real POST detected",
    )

    require(
        transport.demo_post_count == 0,
        "demo POST detected",
    )

    require(
        transport.leverage_transmission_count == 0,
        "leverage transmission detected",
    )


# ============================================================================
# BASIC TEST DISPLAY HELPERS
# ============================================================================

PASS_MARK = "✅ PASS"
FAIL_MARK = "❌ FAIL"

TEST_FAILURES: List[str] = []


def separator() -> None:
    print(
        "-" * 92,
        flush=True,
    )


def test_header(
    number: int,
    title: str,
) -> None:
    print(
        "",
        flush=True,
    )

    print(
        f"{UNIT_NAME} TEST {number}: {title}",
        flush=True,
    )

    separator()


def report_test(
    name: str,
    passed: bool,
) -> None:
    status = (
        PASS_MARK
        if passed
        else FAIL_MARK
    )

    print(
        f"{name:<84} {status}",
        flush=True,
    )

    if not passed:
        TEST_FAILURES.append(
            name
        )


def expect_exception(
    function: Any,
    expected_fragment: Optional[str] = None,
) -> bool:
    try:
        function()

    except Exception as exc:
        if expected_fragment is None:
            return True

        return (
            expected_fragment.lower()
            in str(exc).lower()
        )

    return False


# ============================================================================
# HEALTH SERVER
# ============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):
    def do_GET(self) -> None:
        body = (
            f"{UNIT_NAME} ACTIVE\n"
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        return


def start_health_server() -> Optional[threading.Thread]:
    try:
        server = HTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

    except OSError as exc:
        print(
            f"{UNIT_NAME}: HEALTH SERVER SKIPPED: {exc}",
            flush=True,
        )

        return None

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    print(
        f"{UNIT_NAME}: HEALTH SERVER ACTIVE ON PORT {HEALTH_PORT}",
        flush=True,
    )

    return thread


# ============================================================================
# END OF PART 3
# ============================================================================

print(
    "R28 UNIT N.23: PART 3 DEFINITIONS LOADED",
    flush=True,
)
# ============================================================================
# R28 UNIT N.23
# CORRECTED COPY/PASTE VERSION
# PART 4 OF 4
#
# DIAGNOSTIC TEST SUITE + RUNTIME
# ============================================================================


# ============================================================================
# TEST 1
# BASIC ENGINE INITIALIZATION
# ============================================================================

def run_test_1() -> None:
    test_header(
        1,
        "BASIC ENGINE INITIALIZATION",
    )

    engine = N23Engine()

    report_test(
        "Engine Starts In PREPARED State",
        engine.state.state == "PREPARED",
    )

    report_test(
        "Initial Generation Is One",
        engine.state.generation == 1,
    )

    report_test(
        "Initial Recovery Epoch Is One",
        engine.state.recovery_epoch == 1,
    )

    report_test(
        "Initial Lineage Present",
        bool(engine.state.lineage_id),
    )

    report_test(
        "Initial Integrity Seal Present",
        bool(engine.state.integrity_seal),
    )

    try:
        engine.verify_integrity()
        valid = True
    except Exception:
        valid = False

    report_test(
        "Initial Durable State Integrity Valid",
        valid,
    )


# ============================================================================
# TEST 2
# RECOVERY LEASE ACQUISITION
# ============================================================================

def run_test_2() -> None:
    test_header(
        2,
        "RECOVERY LEASE ACQUISITION",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    report_test(
        "Recovery Lease Acquired",
        lease is not None,
    )

    report_test(
        "Lease Owner Preserved",
        lease.owner_id == "worker-A",
    )

    report_test(
        "Lease Generation Bound",
        lease.generation == engine.state.generation,
    )

    report_test(
        "Lease Lineage Bound",
        lease.lineage_id == engine.state.lineage_id,
    )

    report_test(
        "Lease Recovery Epoch Bound",
        (
            lease.recovery_epoch
            == engine.state.recovery_epoch
        ),
    )

    report_test(
        "Lease Fence Bound",
        (
            lease.fence_hash
            == engine.state.fence().fingerprint()
        ),
    )


# ============================================================================
# TEST 3
# SINGLE OWNER LEASE ENFORCEMENT
# ============================================================================

def run_test_3() -> None:
    test_header(
        3,
        "SINGLE OWNER RECOVERY LEASE",
    )

    engine = N23Engine()

    lease_a = engine.acquire_recovery_lease(
        "worker-A"
    )

    lease_a_repeat = engine.acquire_recovery_lease(
        "worker-A"
    )

    report_test(
        "Same Owner Reacquires Same Lease",
        lease_a_repeat.lease_id == lease_a.lease_id,
    )

    second_owner_blocked = expect_exception(
        lambda: engine.acquire_recovery_lease(
            "worker-B"
        ),
        "already owned",
    )

    report_test(
        "Second Concurrent Owner Rejected",
        second_owner_blocked,
    )


# ============================================================================
# TEST 4
# AUTHORIZATION BINDING
# ============================================================================

def run_test_4() -> None:
    test_header(
        4,
        "RECOVERY AUTHORIZATION BINDING",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    report_test(
        "Recovery Authorization Issued",
        authorization is not None,
    )

    report_test(
        "Authorization Bound To Lease",
        authorization.lease_id == lease.lease_id,
    )

    report_test(
        "Authorization Bound To Generation",
        (
            authorization.generation
            == engine.state.generation
        ),
    )

    report_test(
        "Authorization Bound To Lineage",
        (
            authorization.lineage_id
            == engine.state.lineage_id
        ),
    )

    report_test(
        "Authorization Bound To Recovery Epoch",
        (
            authorization.recovery_epoch
            == engine.state.recovery_epoch
        ),
    )

    report_test(
        "Authorization Initially Unconsumed",
        authorization.consumed is False,
    )


# ============================================================================
# TEST 5
# EXACT TRANSPORT BINDING
# ============================================================================

def run_test_5() -> None:
    test_header(
        5,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    binding = engine.prepare_dispatch_binding(
        lease,
        authorization,
    )

    report_test(
        "Transport Method Exactly POST",
        binding.transport_method == "POST",
    )

    report_test(
        "Transport Path Exactly Leverage Endpoint",
        (
            binding.transport_path
            == LEVERAGE_ENDPOINT
        ),
    )

    report_test(
        "Exact Leverage Payload Preserved",
        (
            canonical_json(binding.payload)
            == EXACT_LEVERAGE_PAYLOAD_JSON
        ),
    )

    report_test(
        "Transport Payload Hash Preserved",
        (
            binding.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH
        ),
    )


# ============================================================================
# TEST 6
# SYNTHETIC DISPATCH
# ============================================================================

def run_test_6() -> None:
    test_header(
        6,
        "SINGLE SYNTHETIC DISPATCH",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    binding = engine.prepare_dispatch_binding(
        lease,
        authorization,
    )

    receipt = engine.execute_synthetic_dispatch(
        lease,
        authorization,
        binding,
    )

    report_test(
        "Synthetic Dispatch Completed",
        engine.state.state == "COMPLETED",
    )

    report_test(
        "Synthetic Receipt Created",
        receipt is not None,
    )

    report_test(
        "Synthetic Receipt Reports No Transmission",
        receipt.transmitted is False,
    )

    report_test(
        "Synthetic Receipt Reports No Network Write",
        receipt.network_write is False,
    )

    report_test(
        "Dispatch Recorded As Completed",
        (
            engine.state.dispatch_id
            in engine.state.completed_dispatch_ids
        ),
    )

    report_test(
        "Recovery Authorization Persisted As Consumed",
        (
            engine.state.authorization is not None
            and engine.state.authorization.consumed
        ),
    )


# ============================================================================
# TEST 7
# REPLAY REJECTION
# ============================================================================

def run_test_7() -> None:
    test_header(
        7,
        "AUTHORIZATION AND DISPATCH REPLAY REJECTION",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    binding = engine.prepare_dispatch_binding(
        lease,
        authorization,
    )

    engine.execute_synthetic_dispatch(
        lease,
        authorization,
        binding,
    )

    replay_blocked = expect_exception(
        lambda: engine.execute_synthetic_dispatch(
            lease,
            authorization,
            binding,
        )
    )

    report_test(
        "Second Synthetic Dispatch Rejected",
        replay_blocked,
    )

    report_test(
        "Exactly One Synthetic Dispatch Recorded",
        engine.transport.dispatch_count == 1,
    )


# ============================================================================
# TEST 8
# RESTART AFTER COMPLETION
# ============================================================================

def run_test_8() -> None:
    test_header(
        8,
        "RESTART AFTER COMPLETED GENERATION",
    )

    engine = N23Engine()

    receipt_before = engine.recover(
        "worker-A"
    )

    restarted = simulate_restart(
        engine
    )

    report_test(
        "Completed State Survived Restart",
        restarted.state.state == "COMPLETED",
    )

    report_test(
        "Completed Dispatch Survived Restart",
        (
            restarted.state.dispatch_id
            in restarted.state.completed_dispatch_ids
        ),
    )

    report_test(
        "Consumed Authorization Survived Restart",
        (
            restarted.state.authorization is not None
            and restarted.state.authorization.consumed
        ),
    )

    receipt_after = restarted.recover(
        "worker-B"
    )

    report_test(
        "Repeated Recovery Returns Existing Receipt",
        (
            receipt_after.receipt_id
            == receipt_before.receipt_id
        ),
    )

    report_test(
        "Restart Replay Produced No New Dispatch",
        restarted.transport.dispatch_count == 0,
    )


# ============================================================================
# TEST 9
# SNAPSHOT SERIALIZATION
# ============================================================================

def run_test_9() -> None:
    test_header(
        9,
        "SNAPSHOT SERIALIZATION AND RESTORE",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    engine.issue_recovery_authorization(
        lease
    )

    snapshot = engine.snapshot_dict()

    restored = N23Engine.restore_dict(
        snapshot
    )

    report_test(
        "Snapshot Restored Successfully",
        restored is not None,
    )

    report_test(
        "Restored Generation Preserved",
        (
            restored.state.generation
            == engine.state.generation
        ),
    )

    report_test(
        "Restored Lineage Preserved",
        (
            restored.state.lineage_id
            == engine.state.lineage_id
        ),
    )

    report_test(
        "Restored Recovery Epoch Preserved",
        (
            restored.state.recovery_epoch
            == engine.state.recovery_epoch
        ),
    )

    report_test(
        "Restored Active Lease Preserved",
        (
            restored.state.active_lease is not None
            and
            restored.state.active_lease.lease_id
            == lease.lease_id
        ),
    )


# ============================================================================
# TEST 10
# CORRUPTED SNAPSHOT REJECTION
# ============================================================================

def run_test_10() -> None:
    test_header(
        10,
        "CORRUPTED SNAPSHOT REJECTION",
    )

    engine = N23Engine()

    snapshot = clone_snapshot_dict(
        engine
    )

    snapshot["generation"] += 1

    corrupted_rejected = expect_exception(
        lambda: N23Engine.restore_dict(
            snapshot
        ),
        "integrity seal",
    )

    report_test(
        "Corrupted Snapshot Integrity Seal Rejected",
        corrupted_rejected,
    )


# ============================================================================
# TEST 11
# TAMPERED TRANSPORT BINDING
# ============================================================================

def run_test_11() -> None:
    test_header(
        11,
        "TAMPERED TRANSPORT BINDING REJECTION",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    binding = engine.prepare_dispatch_binding(
        lease,
        authorization,
    )

    tampered = DispatchBinding(
        dispatch_id=binding.dispatch_id,
        intent_id=binding.intent_id,

        generation=binding.generation,
        lineage_id=binding.lineage_id,
        recovery_epoch=binding.recovery_epoch,

        transport_method=binding.transport_method,
        transport_path="/tampered/path",

        payload=clone(binding.payload),
        payload_hash=binding.payload_hash,
    )

    rejected = expect_exception(
        lambda: engine.execute_synthetic_dispatch(
            lease,
            authorization,
            tampered,
        )
    )

    report_test(
        "Tampered Recovery Binding Rejected",
        rejected,
    )

    report_test(
        "Tampered Recovery Produced No Synthetic Dispatch",
        engine.transport.dispatch_count == 0,
    )


# ============================================================================
# TEST 12
# GENERATION ADVANCEMENT
# ============================================================================

def run_test_12() -> None:
    test_header(
        12,
        "GENERATION AND RECOVERY EPOCH ADVANCEMENT",
    )

    engine = N23Engine()

    engine.recover(
        "worker-A"
    )

    old_generation = engine.state.generation
    old_epoch = engine.state.recovery_epoch
    old_lineage = engine.state.lineage_id

    advance_generation(
        engine
    )

    report_test(
        "Generation Advanced Monotonically",
        engine.state.generation > old_generation,
    )

    report_test(
        "Recovery Epoch Advanced Monotonically",
        engine.state.recovery_epoch > old_epoch,
    )

    report_test(
        "New Generation Uses Different Lineage",
        engine.state.lineage_id != old_lineage,
    )

    report_test(
        "New Generation Returns To PREPARED",
        engine.state.state == "PREPARED",
    )

    report_test(
        "Prior Completed Dispatch Preserved",
        len(engine.state.completed_dispatch_ids) == 1,
    )


# ============================================================================
# TEST 13
# ANTI-ABA STALE LEASE
# ============================================================================

def run_test_13() -> None:
    test_header(
        13,
        "ANTI-ABA STALE LEASE REJECTION",
    )

    engine = N23Engine()

    old_lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    old_authorization = (
        engine.issue_recovery_authorization(
            old_lease
        )
    )

    old_binding = (
        engine.prepare_dispatch_binding(
            old_lease,
            old_authorization,
        )
    )

    engine.execute_synthetic_dispatch(
        old_lease,
        old_authorization,
        old_binding,
    )

    advance_generation(
        engine
    )

    stale_rejected = expect_exception(
        lambda: validate_lease_against_current_generation(
            engine,
            old_lease,
        )
    )

    report_test(
        "Old Generation Lease Rejected",
        stale_rejected,
    )

    report_test(
        "Old Lease Recorded As Retired",
        (
            old_lease.lease_id
            in engine.state.retired_lease_ids
        ),
    )


# ============================================================================
# TEST 14
# ANTI-ABA OWNER REUSE
# ============================================================================

def run_test_14() -> None:
    test_header(
        14,
        "ANTI-ABA OWNER REUSE ACROSS GENERATION LINEAGE",
    )

    engine = N23Engine()

    first_lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    first_authorization = (
        engine.issue_recovery_authorization(
            first_lease
        )
    )

    first_binding = (
        engine.prepare_dispatch_binding(
            first_lease,
            first_authorization,
        )
    )

    engine.execute_synthetic_dispatch(
        first_lease,
        first_authorization,
        first_binding,
    )

    first_generation = first_lease.generation
    first_lineage = first_lease.lineage_id
    first_epoch = first_lease.recovery_epoch
    first_nonce = first_lease.nonce

    advance_generation(
        engine
    )

    second_lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    report_test(
        "Reacquired Owner Uses Higher Generation",
        second_lease.generation > first_generation,
    )

    report_test(
        "Reacquired Owner Uses Different Lineage",
        second_lease.lineage_id != first_lineage,
    )

    report_test(
        "Reacquired Owner Uses Higher Epoch",
        second_lease.recovery_epoch > first_epoch,
    )

    report_test(
        "Reacquired Owner Uses Higher Nonce",
        second_lease.nonce > first_nonce,
    )

    replay_rejected = expect_exception(
        lambda: validate_lease_against_current_generation(
            engine,
            first_lease,
        )
    )

    report_test(
        "Reused Worker Identity Cannot Resurrect Prior Generation Lease",
        replay_rejected,
    )


# ============================================================================
# TEST 15
# EXACT SYNTHETIC TRANSPORT BINDING
# ============================================================================

def run_test_15() -> None:
    test_header(
        15,
        "EXACT SYNTHETIC TRANSPORT BINDING",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    binding = engine.prepare_dispatch_binding(
        lease,
        authorization,
    )

    report_test(
        "Transport Method Exactly POST",
        binding.transport_method == "POST",
    )

    report_test(
        "Transport Path Exactly Leverage Endpoint",
        binding.transport_path == LEVERAGE_ENDPOINT,
    )

    report_test(
        "Transport Payload Hash Preserved",
        (
            binding.payload_hash
            == EXACT_LEVERAGE_PAYLOAD_HASH
        ),
    )


# ============================================================================
# TEST 16
# CONCURRENT RECOVERY SINGLE WINNER
# ============================================================================

def run_test_16() -> None:
    test_header(
        16,
        "CONCURRENT RECOVERY SINGLE-DISPATCH",
    )

    engine = N23Engine()

    receipts: List[SyntheticReceipt] = []
    errors: List[str] = []

    result_lock = threading.Lock()

    def worker(
        owner_id: str,
    ) -> None:
        try:
            receipt = engine.recover(
                owner_id
            )

            with result_lock:
                receipts.append(
                    receipt
                )

        except Exception as exc:
            with result_lock:
                errors.append(
                    str(exc)
                )

    threads = [
        threading.Thread(
            target=worker,
            args=("worker-A",),
        ),
        threading.Thread(
            target=worker,
            args=("worker-B",),
        ),
        threading.Thread(
            target=worker,
            args=("worker-C",),
        ),
        threading.Thread(
            target=worker,
            args=("worker-D",),
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    report_test(
        "Concurrent Recovery Produced Exactly One Synthetic Dispatch",
        engine.transport.dispatch_count == 1,
    )

    report_test(
        "Concurrent Recovery Final State Completed",
        engine.state.state == "COMPLETED",
    )

    report_test(
        "Concurrent Recovery Preserved Consumed Authorization",
        (
            engine.state.authorization is not None
            and engine.state.authorization.consumed
        ),
    )

    structural_errors = []

    for error in errors:
        allowed = (
            "already owned"
            in error.lower()
        )

        if not allowed:
            structural_errors.append(
                error
            )

    report_test(
        "Concurrent Recovery Produced No Structural Errors",
        len(structural_errors) == 0,
    )


# ============================================================================
# TEST 17
# FORGED HIGHER EPOCH
# ============================================================================

def run_test_17() -> None:
    test_header(
        17,
        "FORGED HIGHER EPOCH WITHOUT MATCHING AUTHORIZATION",
    )

    engine = N23Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    authorization = (
        engine.issue_recovery_authorization(
            lease
        )
    )

    forged = RecoveryAuthorization(
        authorization_id=authorization.authorization_id,
        owner_id=authorization.owner_id,
        lease_id=authorization.lease_id,

        generation=authorization.generation,
        lineage_id=authorization.lineage_id,
        recovery_epoch=(
            authorization.recovery_epoch + 1
        ),
        nonce=authorization.nonce,

        intent_id=authorization.intent_id,
        dispatch_id=authorization.dispatch_id,

        transport_method=authorization.transport_method,
        transport_path=authorization.transport_path,
        payload_hash=authorization.payload_hash,

        issued_at_ms=authorization.issued_at_ms,
        consumed=False,
        consumed_at_ms=None,
    )

    rejected = expect_exception(
        lambda: engine.prepare_dispatch_binding(
            lease,
            forged,
        ),
        "recovery epoch",
    )

    report_test(
        "Forged Epoch Transition Rejected",
        rejected,
    )

    report_test(
        "Forged Epoch Produced No Synthetic Dispatch",
        engine.transport.dispatch_count == 0,
    )


# ============================================================================
# TEST 18
# TERMINAL IMMUTABILITY
# ============================================================================

def run_test_18() -> None:
    test_header(
        18,
        "TERMINAL GENERATION IMMUTABILITY",
    )

    engine = N23Engine()

    first_receipt = engine.recover(
        "worker-A"
    )

    blocked = expect_exception(
        lambda: engine.acquire_recovery_lease(
            "worker-B"
        ),
        "terminal generation",
    )

    report_test(
        "Terminal Generation Rejects New Recovery Lease",
        blocked,
    )

    second_receipt = engine.recover(
        "worker-C"
    )

    report_test(
        "Repeated Recovery Is Already Final",
        (
            second_receipt.receipt_id
            == first_receipt.receipt_id
        ),
    )

    report_test(
        "Repeated Recovery Produced No Second Dispatch",
        engine.transport.dispatch_count == 1,
    )


# ============================================================================
# TEST 19
# RESTORED CONSUMED AUTHORIZATION CANNOT RESURRECT
# ============================================================================

def run_test_19() -> None:
    test_header(
        19,
        "RESTART AFTER AUTHORIZATION CONSUMPTION",
    )

    engine = N23Engine()

    engine.recover(
        "worker-A"
    )

    snapshot = engine.snapshot_state()

    restarted = N23Engine.restore_state(
        snapshot
    )

    report_test(
        "Consumed Authorization State Survived Restart",
        (
            restarted.state.authorization is not None
            and restarted.state.authorization.consumed
        ),
    )

    old_authorization = clone(
        restarted.state.authorization
    )

    resurrection_rejected = False

    if old_authorization is not None:
        fake_lease = RecoveryLease(
            lease_id=old_authorization.lease_id,
            owner_id=old_authorization.owner_id,
            generation=old_authorization.generation,
            lineage_id=old_authorization.lineage_id,
            recovery_epoch=old_authorization.recovery_epoch,
            nonce=old_authorization.nonce,
            issued_at_ms=old_authorization.issued_at_ms,
            fence_hash=restarted.state.fence().fingerprint(),
        )

        resurrection_rejected = expect_exception(
            lambda: restarted.prepare_dispatch_binding(
                fake_lease,
                old_authorization,
            )
        )

    report_test(
        "Post-Restart Authorization Resurrection Rejected",
        resurrection_rejected,
    )

    report_test(
        "Restart Replay Produced No Second Synthetic Dispatch",
        restarted.transport.dispatch_count == 0,
    )


# ============================================================================
# TEST 20
# JOURNAL PRESERVATION
# ============================================================================

def run_test_20() -> None:
    test_header(
        20,
        "DURABLE JOURNAL PRESERVATION",
    )

    engine = N23Engine()

    engine.recover(
        "worker-A"
    )

    original_count = len(
        engine.state.journal
    )

    restarted = simulate_restart(
        engine
    )

    restored_count = len(
        restarted.state.journal
    )

    report_test(
        "Journal Survived Restart",
        restored_count == original_count,
    )

    report_test(
        "Journal Preserves Dispatch Identity",
        all(
            (
                record.dispatch_id
                in {
                    None,
                    restarted.state.dispatch_id,
                }
            )
            for record in restarted.state.journal
        ),
    )

    sequences = [
        record.sequence
        for record in restarted.state.journal
    ]

    report_test(
        "Journal Sequence Preserved",
        sequences == list(
            range(
                1,
                len(sequences) + 1,
            )
        ),
    )


# ============================================================================
# TEST 21
# SECOND GENERATION DISTINCT IDENTITY
# ============================================================================

def run_test_21() -> None:
    test_header(
        21,
        "SECOND GENERATION DISTINCT IDENTITY",
    )

    engine = N23Engine()

    engine.recover(
        "worker-A"
    )

    first_intent = engine.state.intent_id
    first_dispatch = engine.state.dispatch_id
    first_lineage = engine.state.lineage_id

    advance_generation(
        engine
    )

    report_test(
        "Second Generation Uses Different Intent",
        engine.state.intent_id != first_intent,
    )

    report_test(
        "Second Generation Uses Different Dispatch",
        engine.state.dispatch_id != first_dispatch,
    )

    report_test(
        "Second Generation Uses Different Lineage",
        engine.state.lineage_id != first_lineage,
    )


# ============================================================================
# TEST 22
# FINAL NETWORK WRITE FIREBREAK
# ============================================================================

def run_test_22() -> None:
    test_header(
        22,
        "FINAL NETWORK WRITE FIREBREAK",
    )

    engine = N23Engine()

    engine.recover(
        "worker-A"
    )

    try:
        assert_transport_firebreak(
            engine.transport
        )
        firebreak_valid = True

    except Exception:
        firebreak_valid = False

    report_test(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    report_test(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    report_test(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    report_test(
        "Leverage Transmission Disabled",
        LEVERAGE_TRANSMISSION_ENABLED is False,
    )

    report_test(
        "Network POST Count Remains Zero",
        engine.transport.real_post_count == 0,
    )

    report_test(
        "Demo POST Count Remains Zero",
        engine.transport.demo_post_count == 0,
    )

    report_test(
        "Network Write Count Remains Zero",
        engine.transport.network_write_count == 0,
    )

    report_test(
        "Leverage Transmission Count Remains Zero",
        (
            engine.transport.leverage_transmission_count
            == 0
        ),
    )

    report_test(
        "Final Transport Firebreak Valid",
        firebreak_valid,
    )


# ============================================================================
# COMPLETE DIAGNOSTIC
# ============================================================================

def run_diagnostic() -> None:
    print(
        "",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    print(
        "0F-4H-R28-UNIT-N.23 STARTING",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    print(
        f"Symbol = {SYMBOL}",
        flush=True,
    )

    print(
        f"Leverage = {LEVERAGE}x",
        flush=True,
    )

    print(
        f"Margin Mode = {MARGIN_MODE}",
        flush=True,
    )

    print(
        f"Transport Method = {TRANSPORT_METHOD}",
        flush=True,
    )

    print(
        f"Transport Path = {LEVERAGE_ENDPOINT}",
        flush=True,
    )

    print(
        (
            "Exact Payload = "
            f"{EXACT_LEVERAGE_PAYLOAD_JSON}"
        ),
        flush=True,
    )

    print(
        (
            "Payload SHA256 = "
            f"{EXACT_LEVERAGE_PAYLOAD_HASH}"
        ),
        flush=True,
    )

    print(
        "",
        flush=True,
    )

    tests = [
        run_test_1,
        run_test_2,
        run_test_3,
        run_test_4,
        run_test_5,
        run_test_6,
        run_test_7,
        run_test_8,
        run_test_9,
        run_test_10,
        run_test_11,
        run_test_12,
        run_test_13,
        run_test_14,
        run_test_15,
        run_test_16,
        run_test_17,
        run_test_18,
        run_test_19,
        run_test_20,
        run_test_21,
        run_test_22,
    ]

    for test_function in tests:
        try:
            test_function()

        except Exception as exc:
            name = test_function.__name__

            TEST_FAILURES.append(
                name
            )

            print(
                "",
                flush=True,
            )

            print(
                f"{UNIT_NAME} UNHANDLED TEST ERROR:",
                flush=True,
            )

            print(
                f"  {name}: {exc}",
                flush=True,
            )

    print(
        "",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    print(
        f"{UNIT_NAME} EXECUTION-READINESS ASSESSMENT",
        flush=True,
    )

    separator()

    print(
        (
            "Structural Safety Failures = "
            f"{len(TEST_FAILURES)}"
        ),
        flush=True,
    )

    print(
        "Real Network POSTs = 0",
        flush=True,
    )

    print(
        "Demo Network POSTs = 0",
        flush=True,
    )

    print(
        "Network Writes = 0",
        flush=True,
    )

    print(
        "Leverage Transmissions = 0",
        flush=True,
    )

    print(
        "Synthetic Transport Only = ✅ ACTIVE",
        flush=True,
    )

    print(
        "Durable Recovery = ✅ TESTED LOCALLY",
        flush=True,
    )

    print(
        "Generation Fencing = ✅ TESTED LOCALLY",
        flush=True,
    )

    print(
        "Anti-ABA Protection = ✅ TESTED LOCALLY",
        flush=True,
    )

    print(
        "Exact Transport Binding = ✅ TESTED LOCALLY",
        flush=True,
    )

    print(
        "Hard Network Firebreak = ✅ ACTIVE",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    if TEST_FAILURES:
        print(
            f"❌ {UNIT_NAME} FAILED",
            flush=True,
        )

        print(
            "Failures:",
            flush=True,
        )

        for failure in TEST_FAILURES:
            print(
                f"  - {failure}",
                flush=True,
            )

        raise RuntimeError(
            f"{UNIT_NAME} diagnostic failure"
        )

    print(
        f"✅ {UNIT_NAME} PASSED",
        flush=True,
    )

    print(
        "✅ READY FOR NEXT UNIT",
        flush=True,
    )

    print(
        "⚠️ NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )


# ============================================================================
# RUNTIME
# ============================================================================

def main() -> None:
    print(
        f"{UNIT_NAME}: RUNTIME STARTING",
        flush=True,
    )

    start_health_server()

    run_diagnostic()

    heartbeat = 0

    while True:
        heartbeat += 1

        print(
            (
                f"{UNIT_NAME}: HEARTBEAT "
                f"{heartbeat} ✅ ACTIVE"
            ),
            flush=True,
        )

        time.sleep(
            15
        )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
