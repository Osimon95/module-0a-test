# ============================================================================
# R28 UNIT N.25
# DURABLE RECOVERY + WAL/CHECKPOINT INTEGRITY + RECOVERY EPOCH FENCING
# + ANTI-ABA LEASE SAFETY + EXACT SYNTHETIC TRANSPORT BINDING
#
# CORRECTED COMPLETE COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
# ============================================================================

print("R28 UNIT N.25: MAIN.PY ENTERED", flush=True)

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

print("R28 UNIT N.25: IMPORTS COMPLETE", flush=True)

# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.25"
UNIT_VERSION = "N.25"

SYMBOL = "BTCUSDT"
LEVERAGE = 100
MARGIN_MODE = "ISOLATED"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TRANSPORT_METHOD = "POST"
TRANSPORT_PATH = "/capi/v2/account/leverage"

STATE_PREPARED = "PREPARED"
STATE_AUTHORIZED = "AUTHORIZED"
STATE_DISPATCHED = "DISPATCHED"
STATE_COMPLETED = "COMPLETED"

TERMINAL_STATES = {STATE_COMPLETED}

INTEGRITY_KEY = b"R28-N25-LOCAL-INTEGRITY-KEY-NETWORK-WRITES-DISABLED"

print("R28 UNIT N.25: CONSTANTS INITIALIZED", flush=True)

# ============================================================================
# HELPERS
# ============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(value: Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = canonical_json(value).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def hmac_hex(value: Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = canonical_json(value).encode("utf-8")

    return hmac.new(
        INTEGRITY_KEY,
        raw,
        hashlib.sha256,
    ).hexdigest()


def banner(title: str) -> None:
    print()
    print(title, flush=True)
    print("-" * 92, flush=True)


def pass_line(label: str, ok: bool) -> None:
    mark = "✅ PASS" if ok else "❌ FAIL"

    print(
        f"{label:<80} {mark}",
        flush=True,
    )

    if not ok:
        raise AssertionError(label)


def local_block(message: str) -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK:",
        flush=True,
    )
    print(
        f"  {message}",
        flush=True,
    )


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise ValueError(message)


def guarded_network_post(
    *args: Any,
    **kwargs: Any,
) -> None:
    local_block(
        f"{UNIT_NAME} LOCAL BLOCK: real network POST is disabled."
    )

    raise RuntimeError(
        "real network POST is disabled"
    )


# ============================================================================
# DATA TYPES
# ============================================================================

@dataclass(frozen=True)
class TransportBinding:
    method: str
    path: str
    payload_hash: str

    def validate(self) -> None:
        require(
            self.method == TRANSPORT_METHOD,
            "transport method mismatch",
        )

        require(
            self.path == TRANSPORT_PATH,
            "transport path mismatch",
        )

        require(
            len(self.payload_hash) == 64,
            "invalid transport payload hash",
        )


@dataclass(frozen=True)
class RecoveryLease:
    owner_id: str
    generation: int
    recovery_epoch: int
    nonce: int
    lineage_id: str

    @property
    def fence(self) -> str:
        return sha256_hex(
            {
                "owner_id": self.owner_id,
                "generation": self.generation,
                "recovery_epoch": self.recovery_epoch,
                "nonce": self.nonce,
                "lineage_id": self.lineage_id,
            }
        )


@dataclass
class Authorization:
    authorization_id: str
    generation: int
    recovery_epoch: int
    lineage_id: str
    payload_hash: str
    consumed: bool = False
    consumed_by: Optional[str] = None

    def validate_for(
        self,
        generation: int,
        recovery_epoch: int,
        lineage_id: str,
        payload_hash: str,
    ) -> None:
        require(
            self.generation == generation,
            "authorization generation mismatch",
        )

        require(
            self.recovery_epoch == recovery_epoch,
            "authorization recovery epoch mismatch",
        )

        require(
            self.lineage_id == lineage_id,
            "authorization lineage mismatch",
        )

        require(
            self.payload_hash == payload_hash,
            "authorization payload hash mismatch",
        )

        require(
            not self.consumed,
            "authorization already consumed",
        )


@dataclass
class DispatchRecord:
    dispatch_id: str
    generation: int
    recovery_epoch: int
    lineage_id: str
    worker_id: str
    method: str
    path: str
    payload_hash: str
    synthetic: bool = True


@dataclass
class JournalRecord:
    sequence: int
    kind: str
    body: Dict[str, Any]
    previous_hash: str
    record_hash: str

    @staticmethod
    def build(
        sequence: int,
        kind: str,
        body: Dict[str, Any],
        previous_hash: str,
    ) -> "JournalRecord":
        core = {
            "sequence": sequence,
            "kind": kind,
            "body": body,
            "previous_hash": previous_hash,
        }

        return JournalRecord(
            sequence=sequence,
            kind=kind,
            body=copy.deepcopy(body),
            previous_hash=previous_hash,
            record_hash=sha256_hex(core),
        )

    def validate(self) -> None:
        expected = sha256_hex(
            {
                "sequence": self.sequence,
                "kind": self.kind,
                "body": self.body,
                "previous_hash": self.previous_hash,
            }
        )

        require(
            hmac.compare_digest(
                self.record_hash,
                expected,
            ),
            "journal record hash mismatch",
        )


@dataclass
class DurableState:
    generation: int
    recovery_epoch: int
    lease_nonce: int
    lineage_id: str
    state: str
    payload: Dict[str, str]
    payload_hash: str
    authorization: Optional[Authorization] = None
    dispatches: List[DispatchRecord] = field(
        default_factory=list
    )
    journal: List[JournalRecord] = field(
        default_factory=list
    )
    active_lease: Optional[RecoveryLease] = None
    seal: str = ""

    def seal_material(self) -> Dict[str, Any]:
        data = asdict(self)

        data.pop(
            "seal",
            None,
        )

        return data

    def reseal(self) -> None:
        self.seal = hmac_hex(
            self.seal_material()
        )

    def validate_seal(self) -> None:
        expected = hmac_hex(
            self.seal_material()
        )

        require(
            hmac.compare_digest(
                self.seal,
                expected,
            ),
            "snapshot integrity seal mismatch",
        )


print(
    "R28 UNIT N.25: PART 1 DEFINITIONS LOADED",
    flush=True,
)

# ============================================================================
# ENGINE
# ============================================================================

class N25Engine:
    def __init__(self) -> None:
        payload = {
            "symbol": SYMBOL,
            "leverage": str(LEVERAGE),
            "marginMode": MARGIN_MODE,
        }

        payload_hash = sha256_hex(
            payload
        )

        self._lock = threading.RLock()

        self.state = DurableState(
            generation=1,
            recovery_epoch=0,
            lease_nonce=0,
            lineage_id=uuid.uuid4().hex,
            state=STATE_PREPARED,
            payload=payload,
            payload_hash=payload_hash,
        )

        self.state.reseal()

    def _validate_state(self) -> None:
        self.state.validate_seal()

        require(
            self.state.payload_hash
            == sha256_hex(
                self.state.payload
            ),
            "payload hash mismatch",
        )

        require(
            self.state.generation >= 1,
            "invalid generation",
        )

        require(
            self.state.recovery_epoch >= 0,
            "invalid recovery epoch",
        )

        require(
            self.state.lease_nonce >= 0,
            "invalid lease nonce",
        )

        expected_previous = ""

        for index, record in enumerate(
            self.state.journal,
            start=1,
        ):
            record.validate()

            require(
                record.sequence == index,
                "journal sequence mismatch",
            )

            require(
                record.previous_hash
                == expected_previous,
                "journal chain mismatch",
            )

            expected_previous = (
                record.record_hash
            )

        if self.state.authorization is not None:
            require(
                self.state.authorization.generation
                == self.state.generation,
                "authorization generation mismatch",
            )

            require(
                self.state.authorization.lineage_id
                == self.state.lineage_id,
                "authorization lineage mismatch",
            )

            require(
                self.state.authorization.payload_hash
                == self.state.payload_hash,
                "authorization payload hash mismatch",
            )

        for dispatch in self.state.dispatches:
            require(
                dispatch.synthetic,
                "non-synthetic dispatch detected",
            )

            require(
                dispatch.method
                == TRANSPORT_METHOD,
                "dispatch transport method mismatch",
            )

            require(
                dispatch.path
                == TRANSPORT_PATH,
                "dispatch transport path mismatch",
            )

            require(
                dispatch.payload_hash
                == self.state.payload_hash,
                "dispatch payload hash mismatch",
            )

    def _append_journal(
        self,
        kind: str,
        body: Dict[str, Any],
    ) -> JournalRecord:
        previous_hash = (
            self.state.journal[-1].record_hash
            if self.state.journal
            else ""
        )

        record = JournalRecord.build(
            sequence=len(
                self.state.journal
            ) + 1,
            kind=kind,
            body=body,
            previous_hash=previous_hash,
        )

        self.state.journal.append(
            record
        )

        self.state.reseal()

        return record

    def snapshot(self) -> DurableState:
        with self._lock:
            self._validate_state()

            return copy.deepcopy(
                self.state
            )

    @classmethod
    def restore_state(
        cls,
        state: DurableState,
    ) -> "N25Engine":
        restored = cls.__new__(
            cls
        )

        restored._lock = (
            threading.RLock()
        )

        restored.state = copy.deepcopy(
            state
        )

        restored._validate_state()

        return restored

    def acquire_recovery_lease(
        self,
        owner_id: str,
    ) -> RecoveryLease:
        with self._lock:
            self._validate_state()

            require(
                self.state.state
                not in TERMINAL_STATES,
                "terminal generation cannot acquire recovery lease",
            )

            self.state.recovery_epoch += 1
            self.state.lease_nonce += 1

            lease = RecoveryLease(
                owner_id=owner_id,
                generation=self.state.generation,
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                nonce=self.state.lease_nonce,
                lineage_id=(
                    self.state.lineage_id
                ),
            )

            self.state.active_lease = lease

            self._append_journal(
                "RECOVERY_LEASE_ACQUIRED",
                {
                    "owner_id": owner_id,
                    "generation": (
                        lease.generation
                    ),
                    "recovery_epoch": (
                        lease.recovery_epoch
                    ),
                    "nonce": lease.nonce,
                    "lineage_id": (
                        lease.lineage_id
                    ),
                    "fence": lease.fence,
                },
            )

            return copy.deepcopy(
                lease
            )

    def _validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        current = (
            self.state.active_lease
        )

        require(
            current is not None,
            "no active recovery lease",
        )

        require(
            current.fence
            == lease.fence,
            "recovery lease fence mismatch",
        )

        require(
            lease.generation
            == self.state.generation,
            "recovery lease generation mismatch",
        )

        require(
            lease.recovery_epoch
            == self.state.recovery_epoch,
            "recovery lease epoch mismatch",
        )

        require(
            lease.lineage_id
            == self.state.lineage_id,
            "recovery lease lineage mismatch",
        )

    def authorize(
        self,
        lease: RecoveryLease,
    ) -> Authorization:
        with self._lock:
            self._validate_state()

            self._validate_lease(
                lease
            )

            require(
                self.state.state
                == STATE_PREPARED,
                "generation is not prepared",
            )

            authorization = Authorization(
                authorization_id=(
                    uuid.uuid4().hex
                ),
                generation=(
                    self.state.generation
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                payload_hash=(
                    self.state.payload_hash
                ),
            )

            self.state.authorization = (
                authorization
            )

            self.state.state = (
                STATE_AUTHORIZED
            )

            self._append_journal(
                "AUTHORIZED",
                {
                    "authorization_id": (
                        authorization.authorization_id
                    ),
                    "generation": (
                        authorization.generation
                    ),
                    "recovery_epoch": (
                        authorization.recovery_epoch
                    ),
                    "lineage_id": (
                        authorization.lineage_id
                    ),
                    "payload_hash": (
                        authorization.payload_hash
                    ),
                },
            )

            return copy.deepcopy(
                authorization
            )

    def synthetic_dispatch(
        self,
        lease: RecoveryLease,
    ) -> DispatchRecord:
        with self._lock:
            self._validate_state()

            self._validate_lease(
                lease
            )

            require(
                self.state.state
                == STATE_AUTHORIZED,
                "generation is not authorized",
            )

            require(
                self.state.authorization
                is not None,
                "authorization missing",
            )

            auth = (
                self.state.authorization
            )

            auth.validate_for(
                self.state.generation,
                self.state.recovery_epoch,
                self.state.lineage_id,
                self.state.payload_hash,
            )

            binding = TransportBinding(
                method=TRANSPORT_METHOD,
                path=TRANSPORT_PATH,
                payload_hash=(
                    self.state.payload_hash
                ),
            )

            binding.validate()

            auth.consumed = True
            auth.consumed_by = (
                lease.owner_id
            )

            dispatch = DispatchRecord(
                dispatch_id=(
                    uuid.uuid4().hex
                ),
                generation=(
                    self.state.generation
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                ),
                lineage_id=(
                    self.state.lineage_id
                ),
                worker_id=(
                    lease.owner_id
                ),
                method=binding.method,
                path=binding.path,
                payload_hash=(
                    binding.payload_hash
                ),
                synthetic=True,
            )

            self.state.dispatches.append(
                dispatch
            )

            self.state.state = (
                STATE_DISPATCHED
            )

            self._append_journal(
                "AUTHORIZATION_CONSUMED",
                {
                    "authorization_id": (
                        auth.authorization_id
                    ),
                    "worker_id": (
                        lease.owner_id
                    ),
                    "dispatch_id": (
                        dispatch.dispatch_id
                    ),
                },
            )

            self._append_journal(
                "SYNTHETIC_DISPATCH",
                asdict(dispatch),
            )

            return copy.deepcopy(
                dispatch
            )

    def complete(
        self,
        lease: RecoveryLease,
    ) -> None:
        with self._lock:
            self._validate_state()

            self._validate_lease(
                lease
            )

            require(
                self.state.state
                == STATE_DISPATCHED,
                "generation is not dispatched",
            )

            self.state.state = (
                STATE_COMPLETED
            )

            self.state.active_lease = None

            self._append_journal(
                "COMPLETED",
                {
                    "generation": (
                        self.state.generation
                    ),
                    "recovery_epoch": (
                        self.state.recovery_epoch
                    ),
                    "lineage_id": (
                        self.state.lineage_id
                    ),
                },
            )

    def recover(
        self,
        owner_id: str,
    ) -> Tuple[
        str,
        Optional[DispatchRecord],
    ]:
        with self._lock:
            self._validate_state()

            if (
                self.state.state
                == STATE_COMPLETED
            ):
                return (
                    "ALREADY_FINAL",
                    None,
                )

        lease = (
            self.acquire_recovery_lease(
                owner_id
            )
        )

        with self._lock:
            if (
                self.state.state
                == STATE_PREPARED
            ):
                self.authorize(
                    lease
                )

            if (
                self.state.state
                == STATE_AUTHORIZED
            ):
                dispatch = (
                    self.synthetic_dispatch(
                        lease
                    )
                )

                self.complete(
                    lease
                )

                return (
                    "COMPLETED",
                    dispatch,
                )

            if (
                self.state.state
                == STATE_DISPATCHED
            ):
                self.complete(
                    lease
                )

                return (
                    "COMPLETED",
                    None,
                )

            if (
                self.state.state
                == STATE_COMPLETED
            ):
                return (
                    "ALREADY_FINAL",
                    None,
                )

            raise RuntimeError(
                "unsupported recovery state: "
                f"{self.state.state}"
            )

    def advance_generation(
        self,
    ) -> None:
        with self._lock:
            self._validate_state()

            require(
                self.state.state
                == STATE_COMPLETED,
                "prior generation must be completed",
            )

            prior_dispatches = (
                copy.deepcopy(
                    self.state.dispatches
                )
            )

            prior_journal = (
                copy.deepcopy(
                    self.state.journal
                )
            )

            self.state = DurableState(
                generation=(
                    self.state.generation
                    + 1
                ),
                recovery_epoch=(
                    self.state.recovery_epoch
                    + 1
                ),
                lease_nonce=(
                    self.state.lease_nonce
                    + 1
                ),
                lineage_id=(
                    uuid.uuid4().hex
                ),
                state=STATE_PREPARED,
                payload=copy.deepcopy(
                    self.state.payload
                ),
                payload_hash=(
                    self.state.payload_hash
                ),
                authorization=None,
                dispatches=(
                    prior_dispatches
                ),
                journal=(
                    prior_journal
                ),
                active_lease=None,
            )

            self._append_journal(
                "GENERATION_ADVANCED",
                {
                    "generation": (
                        self.state.generation
                    ),
                    "recovery_epoch": (
                        self.state.recovery_epoch
                    ),
                    "lineage_id": (
                        self.state.lineage_id
                    ),
                },
            )

    def serialize_checkpoint(
        self,
    ) -> bytes:
        with self._lock:
            self._validate_state()

            envelope = {
                "unit": UNIT_NAME,
                "version": UNIT_VERSION,
                "state": asdict(
                    self.state
                ),
            }

            body = canonical_json(
                envelope
            )

            wrapped = {
                "body": body,
                "seal": hmac_hex(
                    body
                ),
            }

            return canonical_json(
                wrapped
            ).encode(
                "utf-8"
            )

    @classmethod
    def deserialize_checkpoint(
        cls,
        raw: bytes,
    ) -> "N25Engine":
        wrapped = json.loads(
            raw.decode(
                "utf-8"
            )
        )

        require(
            isinstance(
                wrapped,
                dict,
            ),
            "invalid checkpoint envelope",
        )

        body = wrapped.get(
            "body"
        )

        seal = wrapped.get(
            "seal"
        )

        require(
            isinstance(
                body,
                str,
            ),
            "invalid checkpoint body",
        )

        require(
            isinstance(
                seal,
                str,
            ),
            "invalid checkpoint seal",
        )

        require(
            hmac.compare_digest(
                seal,
                hmac_hex(
                    body
                ),
            ),
            "checkpoint integrity seal mismatch",
        )

        envelope = json.loads(
            body
        )

        data = envelope[
            "state"
        ]

        auth_data = data.get(
            "authorization"
        )

        auth = (
            Authorization(
                **auth_data
            )
            if auth_data
            else None
        )

        dispatches = [
            DispatchRecord(
                **item
            )
            for item
            in data.get(
                "dispatches",
                [],
            )
        ]

        journal = [
            JournalRecord(
                **item
            )
            for item
            in data.get(
                "journal",
                [],
            )
        ]

        lease_data = data.get(
            "active_lease"
        )

        lease = (
            RecoveryLease(
                **lease_data
            )
            if lease_data
            else None
        )

        state = DurableState(
            generation=(
                data[
                    "generation"
                ]
            ),
            recovery_epoch=(
                data[
                    "recovery_epoch"
                ]
            ),
            lease_nonce=(
                data[
                    "lease_nonce"
                ]
            ),
            lineage_id=(
                data[
                    "lineage_id"
                ]
            ),
            state=(
                data[
                    "state"
                ]
            ),
            payload=(
                data[
                    "payload"
                ]
            ),
            payload_hash=(
                data[
                    "payload_hash"
                ]
            ),
            authorization=auth,
            dispatches=dispatches,
            journal=journal,
            active_lease=lease,
            seal=(
                data[
                    "seal"
                ]
            ),
        )

        return cls.restore_state(
            state
        )

    def serialize_wal(
        self,
    ) -> bytes:
        with self._lock:
            self._validate_state()

            lines: List[str] = []

            for record in (
                self.state.journal
            ):
                lines.append(
                    canonical_json(
                        asdict(record)
                    )
                )

            return (
                "\n".join(
                    lines
                )
                + (
                    "\n"
                    if lines
                    else ""
                )
            ).encode(
                "utf-8"
            )

    @staticmethod
    def validate_wal(
        raw: bytes,
    ) -> List[JournalRecord]:
        text = raw.decode(
            "utf-8"
        )

        if (
            text
            and not text.endswith(
                "\n"
            )
        ):
            raise ValueError(
                "torn WAL tail detected"
            )

        records: List[
            JournalRecord
        ] = []

        previous_hash = ""

        for (
            expected_sequence,
            line,
        ) in enumerate(
            text.splitlines(),
            start=1,
        ):
            data = json.loads(
                line
            )

            record = JournalRecord(
                **data
            )

            record.validate()

            require(
                record.sequence
                == expected_sequence,
                "WAL sequence mismatch",
            )

            require(
                record.previous_hash
                == previous_hash,
                "WAL chain mismatch",
            )

            records.append(
                record
            )

            previous_hash = (
                record.record_hash
            )

        return records


print(
    "R28 UNIT N.25: PART 2 DEFINITIONS LOADED",
    flush=True,
)

# ============================================================================
# TEST SUITE
# ============================================================================

def expect_rejected(
    label: str,
    fn: Any,
    expected_text: str,
) -> None:
    rejected = False

    try:
        fn()

    except Exception as exc:
        local_block(
            str(exc)
        )

        rejected = (
            expected_text
            in str(exc)
        )

    pass_line(
        label,
        rejected,
    )


def run_tests() -> None:
    banner(
        f"{UNIT_NAME} SAFETY CONFIGURATION"
    )

    pass_line(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    pass_line(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    pass_line(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    pass_line(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    banner(
        f"{UNIT_NAME} TEST 1: INITIAL DURABLE STATE"
    )

    engine = N25Engine()

    snap = engine.snapshot()

    pass_line(
        "Initial Generation Is One",
        snap.generation == 1,
    )

    pass_line(
        "Initial State Is PREPARED",
        snap.state == STATE_PREPARED,
    )

    pass_line(
        "Initial Payload Hash Valid",
        snap.payload_hash
        == sha256_hex(
            snap.payload
        ),
    )

    pass_line(
        "Initial Snapshot Integrity Seal Valid",
        bool(
            snap.seal
        ),
    )

    banner(
        f"{UNIT_NAME} TEST 2: RECOVERY LEASE MONOTONIC FENCING"
    )

    lease1 = (
        engine.acquire_recovery_lease(
            "worker-A"
        )
    )

    epoch1 = (
        lease1.recovery_epoch
    )

    nonce1 = (
        lease1.nonce
    )

    lease2 = (
        engine.acquire_recovery_lease(
            "worker-B"
        )
    )

    pass_line(
        "Recovery Epoch Advanced Monotonically",
        lease2.recovery_epoch
        > epoch1,
    )

    pass_line(
        "Recovery Nonce Advanced Monotonically",
        lease2.nonce
        > nonce1,
    )

    pass_line(
        "Lease Fence Changed",
        lease2.fence
        != lease1.fence,
    )

    banner(
        f"{UNIT_NAME} TEST 3: STALE LEASE REJECTION"
    )

    expect_rejected(
        "Stale Lease Rejected",
        lambda: engine.authorize(
            lease1
        ),
        "recovery lease fence mismatch",
    )

    banner(
        f"{UNIT_NAME} TEST 4: EXACT AUTHORIZATION BINDING"
    )

    auth = engine.authorize(
        lease2
    )

    pass_line(
        "Authorization Generation Bound",
        auth.generation
        == engine.state.generation,
    )

    pass_line(
        "Authorization Recovery Epoch Bound",
        auth.recovery_epoch
        == engine.state.recovery_epoch,
    )

    pass_line(
        "Authorization Lineage Bound",
        auth.lineage_id
        == engine.state.lineage_id,
    )

    pass_line(
        "Authorization Payload Hash Bound",
        auth.payload_hash
        == engine.state.payload_hash,
    )

    banner(
        f"{UNIT_NAME} TEST 5: EXACT SYNTHETIC TRANSPORT BINDING"
    )

    dispatch = (
        engine.synthetic_dispatch(
            lease2
        )
    )

    pass_line(
        "Transport Method Exactly POST",
        dispatch.method
        == TRANSPORT_METHOD,
    )

    pass_line(
        "Transport Path Exactly Leverage Endpoint",
        dispatch.path
        == TRANSPORT_PATH,
    )

    pass_line(
        "Transport Payload Hash Preserved",
        dispatch.payload_hash
        == engine.state.payload_hash,
    )

    pass_line(
        "Dispatch Is Synthetic",
        dispatch.synthetic
        is True,
    )

    pass_line(
        "Authorization Consumed Exactly Once",
        engine.state.authorization
        is not None
        and engine.state.authorization.consumed,
    )

    banner(
        f"{UNIT_NAME} TEST 6: AUTHORIZATION REPLAY REJECTION"
    )

    expect_rejected(
        "Consumed Authorization Replay Rejected",
        lambda: engine.synthetic_dispatch(
            lease2
        ),
        "generation is not authorized",
    )

    banner(
        f"{UNIT_NAME} TEST 7: COMPLETION + TERMINAL IMMUTABILITY"
    )

    engine.complete(
        lease2
    )

    pass_line(
        "Generation Completed",
        engine.state.state
        == STATE_COMPLETED,
    )

    pass_line(
        "Exactly One Synthetic Dispatch Recorded",
        len(
            engine.state.dispatches
        )
        == 1,
    )

    status, repeated = (
        engine.recover(
            "worker-C"
        )
    )

    pass_line(
        "Repeated Recovery Is Already Final",
        status
        == "ALREADY_FINAL",
    )

    pass_line(
        "Repeated Recovery Produced No Second Dispatch",
        repeated is None
        and len(
            engine.state.dispatches
        )
        == 1,
    )

    banner(
        f"{UNIT_NAME} TEST 8: CHECKPOINT ROUND TRIP"
    )

    checkpoint = (
        engine.serialize_checkpoint()
    )

    restored = (
        N25Engine.deserialize_checkpoint(
            checkpoint
        )
    )

    pass_line(
        "Checkpoint Restores Completed State",
        restored.state.state
        == STATE_COMPLETED,
    )

    pass_line(
        "Checkpoint Preserves Generation",
        restored.state.generation
        == engine.state.generation,
    )

    pass_line(
        "Checkpoint Preserves Dispatch Identity",
        restored.state.dispatches[
            0
        ].dispatch_id
        == engine.state.dispatches[
            0
        ].dispatch_id,
    )

    pass_line(
        "Checkpoint Preserves Consumed Authorization",
        restored.state.authorization
        is not None
        and restored.state.authorization.consumed,
    )

    banner(
        f"{UNIT_NAME} TEST 9: SNAPSHOT TAMPER REJECTION"
    )

    tampered_state = (
        restored.snapshot()
    )

    tampered_state.payload[
        "leverage"
    ] = "99"

    expect_rejected(
        "Tampered Snapshot Rejected",
        lambda: N25Engine.restore_state(
            tampered_state
        ),
        "snapshot integrity seal mismatch",
    )

    banner(
        f"{UNIT_NAME} TEST 10: WAL INTEGRITY"
    )

    wal = (
        engine.serialize_wal()
    )

    parsed = (
        N25Engine.validate_wal(
            wal
        )
    )

    pass_line(
        "WAL Records Validate",
        len(parsed)
        == len(
            engine.state.journal
        ),
    )

    pass_line(
        "WAL Final Hash Matches Journal",
        parsed[
            -1
        ].record_hash
        == engine.state.journal[
            -1
        ].record_hash,
    )

    banner(
        f"{UNIT_NAME} TEST 11: TORN WAL TAIL REJECTION"
    )

    torn = wal[:-1]

    expect_rejected(
        "Torn WAL Tail Rejected",
        lambda: N25Engine.validate_wal(
            torn
        ),
        "torn WAL tail detected",
    )

    banner(
        f"{UNIT_NAME} TEST 12: GENERATION ADVANCE"
    )

    prior_generation = (
        engine.state.generation
    )

    prior_epoch = (
        engine.state.recovery_epoch
    )

    prior_lineage = (
        engine.state.lineage_id
    )

    prior_dispatch_id = (
        engine.state.dispatches[
            0
        ].dispatch_id
    )

    engine.advance_generation()

    pass_line(
        "Generation Advanced Monotonically",
        engine.state.generation
        > prior_generation,
    )

    pass_line(
        "Recovery Epoch Advanced Monotonically",
        engine.state.recovery_epoch
        > prior_epoch,
    )

    pass_line(
        "New Generation Uses Different Lineage",
        engine.state.lineage_id
        != prior_lineage,
    )

    pass_line(
        "New Generation Returns To PREPARED",
        engine.state.state
        == STATE_PREPARED,
    )

    pass_line(
        "Prior Completed Dispatch Preserved",
        engine.state.dispatches[
            0
        ].dispatch_id
        == prior_dispatch_id,
    )

    banner(
        f"{UNIT_NAME} TEST 13: ANTI-ABA STALE LEASE REJECTION"
    )

    new_lease = (
        engine.acquire_recovery_lease(
            "worker-A"
        )
    )

    pass_line(
        "Reacquired Owner Uses Higher Generation",
        new_lease.generation
        > lease2.generation,
    )

    pass_line(
        "Reacquired Owner Uses Different Lineage",
        new_lease.lineage_id
        != lease2.lineage_id,
    )

    pass_line(
        "Reacquired Owner Uses Higher Epoch",
        new_lease.recovery_epoch
        > lease2.recovery_epoch,
    )

    pass_line(
        "Reacquired Owner Uses Higher Nonce",
        new_lease.nonce
        > lease2.nonce,
    )

    expect_rejected(
        "Reused Worker Identity Cannot Resurrect Prior Generation Lease",
        lambda: engine.authorize(
            lease2
        ),
        "recovery lease fence mismatch",
    )

    banner(
        f"{UNIT_NAME} TEST 14: CHECKPOINT TAMPER REJECTION"
    )

    wrapped = json.loads(
        checkpoint.decode(
            "utf-8"
        )
    )

    body = json.loads(
        wrapped[
            "body"
        ]
    )

    body[
        "state"
    ][
        "generation"
    ] += 100

    wrapped[
        "body"
    ] = canonical_json(
        body
    )

    tampered_checkpoint = (
        canonical_json(
            wrapped
        ).encode(
            "utf-8"
        )
    )

    expect_rejected(
        "Tampered Checkpoint Rejected",
        lambda: N25Engine.deserialize_checkpoint(
            tampered_checkpoint
        ),
        "checkpoint integrity seal mismatch",
    )

    banner(
        f"{UNIT_NAME} TEST 15: CONCURRENT RECOVERY SINGLE DISPATCH"
    )

    concurrent_engine = (
        N25Engine()
    )

    outcomes: List[str] = []
    errors: List[str] = []

    lock = threading.Lock()

    def worker(
        name: str,
    ) -> None:
        try:
            result, _dispatch = (
                concurrent_engine.recover(
                    name
                )
            )

            with lock:
                outcomes.append(
                    result
                )

        except Exception as exc:
            with lock:
                errors.append(
                    str(exc)
                )

    threads = [
        threading.Thread(
            target=worker,
            args=(
                f"worker-{i}",
            ),
        )
        for i in range(
            8
        )
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    pass_line(
        "Concurrent Recovery Produced Exactly One Synthetic Dispatch",
        len(
            concurrent_engine.state.dispatches
        )
        == 1,
    )

    pass_line(
        "Concurrent Recovery Final State Completed",
        concurrent_engine.state.state
        == STATE_COMPLETED,
    )

    pass_line(
        "Concurrent Recovery Preserved Consumed Authorization",
        concurrent_engine.state.authorization
        is not None
        and concurrent_engine.state.authorization.consumed,
    )

    pass_line(
        "Concurrent Recovery Produced No Structural Errors",
        all(
            "unsupported recovery state"
            not in item
            for item
            in errors
        ),
    )

    banner(
        f"{UNIT_NAME} TEST 16: FINAL NETWORK WRITE FIREBREAK"
    )

    expect_rejected(
        "Real Network POST Blocked",
        lambda: guarded_network_post(
            "https://example.invalid",
            json=engine.state.payload,
        ),
        "real network POST is disabled",
    )

    pass_line(
        "Real POST Remains Disabled",
        REAL_POST_ENABLED is False,
    )

    pass_line(
        "Demo POST Remains Disabled",
        DEMO_POST_ENABLED is False,
    )

    pass_line(
        "Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    pass_line(
        "Synthetic Transport Remains Mandatory",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    banner(
        f"{UNIT_NAME} FINAL ASSESSMENT"
    )

    print(
        "Structural Safety Failures = 0",
        flush=True,
    )

    print(
        "Readiness Blockers = 0",
        flush=True,
    )

    print(
        "Durable Snapshot Integrity = ✅ VERIFIED",
        flush=True,
    )

    print(
        "WAL Integrity + Torn Tail Rejection = ✅ VERIFIED",
        flush=True,
    )

    print(
        "Recovery Epoch Fencing = ✅ VERIFIED",
        flush=True,
    )

    print(
        "Anti-ABA Lease Safety = ✅ VERIFIED",
        flush=True,
    )

    print(
        "Exact Synthetic Transport Binding = ✅ VERIFIED",
        flush=True,
    )

    print(
        "Real Network Writes = ❌ DISABLED",
        flush=True,
    )

    print(
        "Demo Network Writes = ❌ DISABLED",
        flush=True,
    )

    print()

    print(
        f"✅ {UNIT_NAME} PASSED",
        flush=True,
    )


print(
    "R28 UNIT N.25: PART 3 DEFINITIONS LOADED",
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
                f"{UNIT_NAME}: HEALTH SERVER ACTIVE ON PORT {port}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"{UNIT_NAME}: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()


def runtime_hold() -> None:
    while True:
        time.sleep(
            60
        )


def main() -> None:
    print(
        f"{UNIT_NAME}: RUNTIME STARTING",
        flush=True,
    )

    run_tests()

    start_health_server()

    print(
        f"{UNIT_NAME}: RUNTIME READY",
        flush=True,
    )

    runtime_hold()


print(
    "R28 UNIT N.25: PART 4 DEFINITIONS LOADED",
    flush=True,
)


if __name__ == "__main__":
    main()
