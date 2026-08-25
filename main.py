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
