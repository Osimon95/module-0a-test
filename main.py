print("R28 UNIT N.26: MAIN.PY ENTERED", flush=True)

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
from typing import Any, Dict, List, Optional, Tuple

print("R28 UNIT N.26: IMPORTS COMPLETE", flush=True)

UNIT_NAME = "R28 UNIT N.26"
UNIT_VERSION = "N.26"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

INTEGRITY_KEY = b"R28-N26-LOCAL-INTEGRITY-KEY"
CERTIFICATE_KEY = b"R28-N26-RECOVERY-CERTIFICATE-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

print("R28 UNIT N.26: CONSTANTS INITIALIZED", flush=True)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_hex(key: bytes, value: str) -> str:
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()


def deterministic_id(prefix: str, *parts: Any) -> str:
    material = "|".join(str(p) for p in parts)
    return f"{prefix}_{sha256_text(material)[:24]}"


def print_rule() -> None:
    print("-" * 92, flush=True)


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


def assert_pass(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"{label:<82} ✅ PASS", flush=True)


@dataclass
class RecoveryLease:
    owner: str
    generation: int
    lineage: str
    recovery_epoch: int
    nonce: int


@dataclass
class Authorization:
    authorization_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    owner: str
    consumed: bool = False


@dataclass
class DispatchRecord:
    dispatch_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    authorization_id: str
    method: str
    path: str
    payload_hash: str
    synthetic: bool
    created_at_ns: int


@dataclass
class JournalRecord:
    index: int
    event: str
    generation: int
    lineage: str
    recovery_epoch: int
    data: Dict[str, Any]
    prev_hash: str
    record_hash: str


@dataclass
class RecoveryCertificate:
    certificate_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    authorization_id: str
    dispatch_id: str
    wal_tip: str
    state_digest: str
    seal: str


@dataclass
class DurableState:
    generation: int = 1
    recovery_epoch: int = 1
    lineage: str = field(default_factory=lambda: uuid.uuid4().hex)
    phase: str = PHASE_PREPARED
    lease_nonce_counter: int = 0
    active_lease: Optional[RecoveryLease] = None
    authorization: Optional[Authorization] = None
    dispatches: List[DispatchRecord] = field(default_factory=list)
    journal: List[JournalRecord] = field(default_factory=list)
    certificates: List[RecoveryCertificate] = field(default_factory=list)


class SyntheticTransport:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not SYNTHETIC_TRANSPORT_ONLY:
            raise RuntimeError("synthetic transport requirement disabled")
        payload_hash = sha256_text(canonical_json(payload))
        call = {
            "method": HTTP_METHOD,
            "path": path,
            "payload": copy.deepcopy(payload),
            "payload_hash": payload_hash,
            "synthetic": True,
        }
        self.calls.append(call)
        return copy.deepcopy(call)


def real_network_post(path: str, payload: Dict[str, Any]) -> None:
    local_block(f"{UNIT_NAME} LOCAL BLOCK: real network POST is disabled.")
    raise RuntimeError("real network POST is disabled")
class N26Engine:
    def __init__(self, state: Optional[DurableState] = None) -> None:
        self.state = state if state is not None else DurableState()
        self.transport = SyntheticTransport()
        self._lock = threading.RLock()
        if not self.state.journal:
            self._append_journal("ENGINE_CREATED", {"phase": self.state.phase})

    @property
    def wal_tip(self) -> str:
        if not self.state.journal:
            return "0" * 64
        return self.state.journal[-1].record_hash

    def _append_journal(self, event: str, data: Dict[str, Any]) -> JournalRecord:
        prev_hash = (
            self.state.journal[-1].record_hash
            if self.state.journal
            else "0" * 64
        )
        index = len(self.state.journal)

        body = {
            "index": index,
            "event": event,
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "data": copy.deepcopy(data),
            "prev_hash": prev_hash,
        }

        record_hash = sha256_text(canonical_json(body))

        record = JournalRecord(
            index=index,
            event=event,
            generation=self.state.generation,
            lineage=self.state.lineage,
            recovery_epoch=self.state.recovery_epoch,
            data=copy.deepcopy(data),
            prev_hash=prev_hash,
            record_hash=record_hash,
        )

        self.state.journal.append(record)
        return record

    def validate_wal(
        self,
        journal: Optional[List[JournalRecord]] = None,
    ) -> bool:
        records = journal if journal is not None else self.state.journal

        prev_hash = "0" * 64

        for expected_index, record in enumerate(records):
            if record.index != expected_index:
                raise ValueError("WAL record index mismatch")

            if record.prev_hash != prev_hash:
                raise ValueError("WAL previous hash mismatch")

            body = {
                "index": record.index,
                "event": record.event,
                "generation": record.generation,
                "lineage": record.lineage,
                "recovery_epoch": record.recovery_epoch,
                "data": copy.deepcopy(record.data),
                "prev_hash": record.prev_hash,
            }

            expected_hash = sha256_text(canonical_json(body))

            if not hmac.compare_digest(
                expected_hash,
                record.record_hash,
            ):
                raise ValueError("WAL record hash mismatch")

            prev_hash = record.record_hash

        return True

    def detect_torn_wal_tail(
        self,
        serialized_records: List[Dict[str, Any]],
    ) -> None:
        for item in serialized_records:
            required = {
                "index",
                "event",
                "generation",
                "lineage",
                "recovery_epoch",
                "data",
                "prev_hash",
                "record_hash",
            }

            if not required.issubset(set(item.keys())):
                raise ValueError("torn WAL tail detected")

    def acquire_recovery_lease(
        self,
        owner: str,
    ) -> RecoveryLease:
        with self._lock:
            if self.state.phase == PHASE_COMPLETED:
                raise ValueError(
                    "terminal generation cannot acquire recovery lease"
                )

            self.state.lease_nonce_counter += 1

            lease = RecoveryLease(
                owner=owner,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                nonce=self.state.lease_nonce_counter,
            )

            self.state.active_lease = lease

            self._append_journal(
                "LEASE_ACQUIRED",
                {
                    "owner": owner,
                    "nonce": lease.nonce,
                },
            )

            return copy.deepcopy(lease)

    def _validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:
        active = self.state.active_lease

        if active is None:
            raise ValueError("recovery lease fence mismatch")

        if asdict(active) != asdict(lease):
            raise ValueError("recovery lease fence mismatch")

        if lease.generation != self.state.generation:
            raise ValueError("recovery lease fence mismatch")

        if lease.lineage != self.state.lineage:
            raise ValueError("recovery lease fence mismatch")

        if lease.recovery_epoch != self.state.recovery_epoch:
            raise ValueError("recovery lease fence mismatch")

    def authorize(
        self,
        lease: RecoveryLease,
    ) -> Authorization:
        with self._lock:
            self._validate_lease(lease)

            if self.state.phase != PHASE_PREPARED:
                raise ValueError("generation is not prepared")

            auth_id = deterministic_id(
                "auth",
                self.state.generation,
                self.state.lineage,
                self.state.recovery_epoch,
                lease.owner,
                lease.nonce,
            )

            auth = Authorization(
                authorization_id=auth_id,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                owner=lease.owner,
                consumed=False,
            )

            self.state.authorization = auth
            self.state.phase = PHASE_AUTHORIZED

            self._append_journal(
                "AUTHORIZED",
                {
                    "authorization_id": auth.authorization_id,
                    "owner": auth.owner,
                },
            )

            return copy.deepcopy(auth)

    def _payload(self) -> Dict[str, Any]:
        return {
            "symbol": SYMBOL,
            "leverage": "100",
            "marginType": "ISOLATED",
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recoveryEpoch": self.state.recovery_epoch,
        }

    def recover_and_dispatch(
        self,
        lease: RecoveryLease,
    ) -> Tuple[str, Optional[DispatchRecord]]:
        with self._lock:
            if self.state.phase == PHASE_COMPLETED:
                return "already_final", None

            self._validate_lease(lease)

            auth = self.state.authorization

            if (
                auth is None
                or self.state.phase != PHASE_AUTHORIZED
                or auth.consumed
                or auth.generation != self.state.generation
                or auth.lineage != self.state.lineage
                or auth.recovery_epoch != self.state.recovery_epoch
                or auth.owner != lease.owner
            ):
                raise ValueError("generation is not authorized")

            auth.consumed = True

            self._append_journal(
                "AUTHORIZATION_CONSUMED",
                {
                    "authorization_id": auth.authorization_id,
                },
            )

            payload = self._payload()

            call = self.transport.post(
                LEVERAGE_ENDPOINT,
                payload,
            )

            dispatch_id = deterministic_id(
                "dispatch",
                self.state.generation,
                self.state.lineage,
                self.state.recovery_epoch,
                auth.authorization_id,
                call["payload_hash"],
            )

            record = DispatchRecord(
                dispatch_id=dispatch_id,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                authorization_id=auth.authorization_id,
                method=call["method"],
                path=call["path"],
                payload_hash=call["payload_hash"],
                synthetic=call["synthetic"],
                created_at_ns=time.time_ns(),
            )

            self.state.dispatches.append(record)
            self.state.phase = PHASE_DISPATCHED

            self._append_journal(
                "SYNTHETIC_DISPATCH",
                {
                    "dispatch_id": record.dispatch_id,
                    "authorization_id": record.authorization_id,
                    "method": record.method,
                    "path": record.path,
                    "payload_hash": record.payload_hash,
                    "synthetic": record.synthetic,
                },
            )

            return "dispatched", copy.deepcopy(record)

    def _core_state_for_digest(self) -> Dict[str, Any]:
        return {
            "generation": self.state.generation,
            "recovery_epoch": self.state.recovery_epoch,
            "lineage": self.state.lineage,
            "phase": self.state.phase,
            "lease_nonce_counter": self.state.lease_nonce_counter,
            "active_lease": (
                asdict(self.state.active_lease)
                if self.state.active_lease
                else None
            ),
            "authorization": (
                asdict(self.state.authorization)
                if self.state.authorization
                else None
            ),
            "dispatches": [
                asdict(item)
                for item in self.state.dispatches
            ],
            "journal": [
                asdict(item)
                for item in self.state.journal
            ],
        }

    def state_digest(self) -> str:
        return sha256_text(
            canonical_json(
                self._core_state_for_digest()
            )
        )

    def _certificate_body(
        self,
        certificate_id: str,
        generation: int,
        lineage: str,
        recovery_epoch: int,
        authorization_id: str,
        dispatch_id: str,
        wal_tip: str,
        state_digest: str,
    ) -> Dict[str, Any]:
        return {
            "certificate_id": certificate_id,
            "generation": generation,
            "lineage": lineage,
            "recovery_epoch": recovery_epoch,
            "authorization_id": authorization_id,
            "dispatch_id": dispatch_id,
            "wal_tip": wal_tip,
            "state_digest": state_digest,
        }

    def issue_recovery_certificate(
        self,
    ) -> RecoveryCertificate:
        with self._lock:
            if self.state.phase != PHASE_COMPLETED:
                raise ValueError("generation is not completed")

            auth = self.state.authorization

            if auth is None or not auth.consumed:
                raise ValueError(
                    "consumed authorization required"
                )

            generation_dispatches = [
                item
                for item in self.state.dispatches
                if (
                    item.generation == self.state.generation
                    and item.lineage == self.state.lineage
                )
            ]

            if len(generation_dispatches) != 1:
                raise ValueError(
                    "exactly one dispatch required for certificate"
                )

            dispatch = generation_dispatches[0]

            for existing in self.state.certificates:
                if (
                    existing.generation
                    == self.state.generation
                    and existing.lineage
                    == self.state.lineage
                ):
                    return copy.deepcopy(existing)

            wal_tip = self.wal_tip
            digest = self.state_digest()

            certificate_id = deterministic_id(
                "cert",
                self.state.generation,
                self.state.lineage,
                self.state.recovery_epoch,
                auth.authorization_id,
                dispatch.dispatch_id,
                wal_tip,
                digest,
            )

            body = self._certificate_body(
                certificate_id,
                self.state.generation,
                self.state.lineage,
                self.state.recovery_epoch,
                auth.authorization_id,
                dispatch.dispatch_id,
                wal_tip,
                digest,
            )

            seal = hmac_hex(
                CERTIFICATE_KEY,
                canonical_json(body),
            )

            cert = RecoveryCertificate(
                certificate_id=certificate_id,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                authorization_id=auth.authorization_id,
                dispatch_id=dispatch.dispatch_id,
                wal_tip=wal_tip,
                state_digest=digest,
                seal=seal,
            )

            self.state.certificates.append(cert)

            return copy.deepcopy(cert)

    def validate_certificate(
        self,
        cert: RecoveryCertificate,
        require_current_state: bool = True,
    ) -> bool:
        body = self._certificate_body(
            cert.certificate_id,
            cert.generation,
            cert.lineage,
            cert.recovery_epoch,
            cert.authorization_id,
            cert.dispatch_id,
            cert.wal_tip,
            cert.state_digest,
        )

        expected = hmac_hex(
            CERTIFICATE_KEY,
            canonical_json(body),
        )

        if not hmac.compare_digest(
            expected,
            cert.seal,
        ):
            raise ValueError(
                "recovery certificate seal mismatch"
            )

        matching_dispatches = [
            item
            for item in self.state.dispatches
            if item.dispatch_id == cert.dispatch_id
        ]

        if len(matching_dispatches) != 1:
            raise ValueError(
                "recovery certificate dispatch binding mismatch"
            )

        dispatch = matching_dispatches[0]

        if (
            dispatch.generation != cert.generation
            or dispatch.lineage != cert.lineage
            or dispatch.recovery_epoch != cert.recovery_epoch
            or dispatch.authorization_id
            != cert.authorization_id
        ):
            raise ValueError(
                "recovery certificate dispatch binding mismatch"
            )

        if require_current_state:
            if (
                cert.generation != self.state.generation
                or cert.lineage != self.state.lineage
            ):
                raise ValueError(
                    "recovery certificate is not for current generation"
                )

            if (
                cert.recovery_epoch
                != self.state.recovery_epoch
            ):
                raise ValueError(
                    "recovery certificate recovery epoch mismatch"
                )

            if cert.wal_tip != self.wal_tip:
                raise ValueError(
                    "recovery certificate WAL binding mismatch"
                )

            if cert.state_digest != self.state_digest():
                raise ValueError(
                    "recovery certificate state digest mismatch"
                )

        return True

    def complete_generation(
        self,
        lease: RecoveryLease,
    ) -> RecoveryCertificate:
        with self._lock:
            if self.state.phase == PHASE_COMPLETED:
                existing = [
                    item
                    for item in self.state.certificates
                    if (
                        item.generation
                        == self.state.generation
                        and item.lineage
                        == self.state.lineage
                    )
                ]

                if not existing:
                    raise ValueError(
                        "completed generation missing certificate"
                    )

                return copy.deepcopy(existing[0])

            self._validate_lease(lease)

            if self.state.phase != PHASE_DISPATCHED:
                raise ValueError(
                    "generation is not dispatched"
                )

            self.state.phase = PHASE_COMPLETED

            self._append_journal(
                "GENERATION_COMPLETED",
                {},
            )

            return self.issue_recovery_certificate()

    def checkpoint_payload(self) -> Dict[str, Any]:
        return {
            "generation": self.state.generation,
            "recovery_epoch": self.state.recovery_epoch,
            "lineage": self.state.lineage,
            "phase": self.state.phase,
            "lease_nonce_counter": self.state.lease_nonce_counter,
            "active_lease": (
                asdict(self.state.active_lease)
                if self.state.active_lease
                else None
            ),
            "authorization": (
                asdict(self.state.authorization)
                if self.state.authorization
                else None
            ),
            "dispatches": [
                asdict(item)
                for item in self.state.dispatches
            ],
            "journal": [
                asdict(item)
                for item in self.state.journal
            ],
            "certificates": [
                asdict(item)
                for item in self.state.certificates
            ],
        }

    def checkpoint(self) -> Dict[str, Any]:
        payload = self.checkpoint_payload()

        seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(payload),
        )

        return {
            "payload": payload,
            "seal": seal,
        }

    @classmethod
    def restore_checkpoint(
        cls,
        checkpoint: Dict[str, Any],
    ) -> "N26Engine":
        payload = copy.deepcopy(
            checkpoint.get("payload")
        )

        supplied_seal = checkpoint.get(
            "seal",
            "",
        )

        expected_seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(payload),
        )

        if not hmac.compare_digest(
            supplied_seal,
            expected_seal,
        ):
            raise ValueError(
                "checkpoint integrity seal mismatch"
            )

        active_lease_data = payload.get(
            "active_lease"
        )

        authorization_data = payload.get(
            "authorization"
        )

        state = DurableState(
            generation=payload["generation"],
            recovery_epoch=payload["recovery_epoch"],
            lineage=payload["lineage"],
            phase=payload["phase"],
            lease_nonce_counter=payload[
                "lease_nonce_counter"
            ],
            active_lease=(
                RecoveryLease(**active_lease_data)
                if active_lease_data
                else None
            ),
            authorization=(
                Authorization(**authorization_data)
                if authorization_data
                else None
            ),
            dispatches=[
                DispatchRecord(**item)
                for item in payload["dispatches"]
            ],
            journal=[
                JournalRecord(**item)
                for item in payload["journal"]
            ],
            certificates=[
                RecoveryCertificate(**item)
                for item in payload["certificates"]
            ],
        )

        engine = cls(state=state)

        engine.validate_wal()

        return engine

    def advance_generation(
        self,
    ) -> Tuple[int, str, int]:
        with self._lock:
            if self.state.phase != PHASE_COMPLETED:
                raise ValueError(
                    "current generation is not completed"
                )

            self.state.generation += 1
            self.state.recovery_epoch += 1
            self.state.lineage = uuid.uuid4().hex
            self.state.phase = PHASE_PREPARED
            self.state.active_lease = None
            self.state.authorization = None

            self._append_journal(
                "GENERATION_ADVANCED",
                {
                    "generation": self.state.generation,
                    "lineage": self.state.lineage,
                    "recovery_epoch": self.state.recovery_epoch,
                },
            )

            return (
                self.state.generation,
                self.state.lineage,
                self.state.recovery_epoch,
            )


print("R28 UNIT N.26: PART 2 DEFINITIONS LOADED", flush=True)
def expect_block(
    label: str,
    fn,
    expected_text: str,
) -> None:
    try:
        fn()
    except Exception as exc:
        local_block(str(exc))
        assert_pass(
            label,
            expected_text in str(exc),
        )
        return

    raise AssertionError(
        f"{label}: expected rejection"
    )


def make_completed_engine(
    owner: str = "worker-A",
) -> Tuple[
    N26Engine,
    RecoveryLease,
    RecoveryCertificate,
]:
    engine = N26Engine()

    lease = engine.acquire_recovery_lease(
        owner
    )

    engine.authorize(
        lease
    )

    status, dispatch = engine.recover_and_dispatch(
        lease
    )

    if (
        status != "dispatched"
        or dispatch is None
    ):
        raise AssertionError(
            "failed to synthesize dispatch"
        )

    cert = engine.complete_generation(
        lease
    )

    return (
        engine,
        lease,
        cert,
    )


def test_1_bootstrap() -> None:
    print(
        f"\n{UNIT_NAME} TEST 1: BOOTSTRAP SAFETY"
    )
    print_rule()

    engine = N26Engine()

    assert_pass(
        "Initial Generation Is One",
        engine.state.generation == 1,
    )

    assert_pass(
        "Initial Recovery Epoch Is One",
        engine.state.recovery_epoch == 1,
    )

    assert_pass(
        "Initial Phase Is PREPARED",
        engine.state.phase
        == PHASE_PREPARED,
    )

    assert_pass(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    assert_pass(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    assert_pass(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    assert_pass(
        "Synthetic Transport Mandatory",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )


def test_2_lease_and_authorization() -> None:
    print(
        f"\n{UNIT_NAME} TEST 2: LEASE + AUTHORIZATION BINDING"
    )
    print_rule()

    engine = N26Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    auth = engine.authorize(
        lease
    )

    assert_pass(
        "Lease Bound To Generation",
        lease.generation
        == engine.state.generation,
    )

    assert_pass(
        "Lease Bound To Lineage",
        lease.lineage
        == engine.state.lineage,
    )

    assert_pass(
        "Lease Bound To Recovery Epoch",
        lease.recovery_epoch
        == engine.state.recovery_epoch,
    )

    assert_pass(
        "Authorization Bound To Lease Owner",
        auth.owner == lease.owner,
    )

    assert_pass(
        "Authorization Starts Unconsumed",
        auth.consumed is False,
    )


def test_3_exact_synthetic_transport() -> None:
    print(
        f"\n{UNIT_NAME} TEST 3: EXACT SYNTHETIC TRANSPORT BINDING"
    )
    print_rule()

    engine = N26Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    engine.authorize(
        lease
    )

    status, dispatch = engine.recover_and_dispatch(
        lease
    )

    assert_pass(
        "Synthetic Dispatch Created",
        status == "dispatched"
        and dispatch is not None,
    )

    assert dispatch is not None

    assert_pass(
        "Transport Method Exactly POST",
        dispatch.method
        == HTTP_METHOD,
    )

    assert_pass(
        "Transport Path Exactly Leverage Endpoint",
        dispatch.path
        == LEVERAGE_ENDPOINT,
    )

    expected_hash = sha256_text(
        canonical_json(
            engine._payload()
        )
    )

    assert_pass(
        "Transport Payload Hash Preserved",
        dispatch.payload_hash
        == expected_hash,
    )

    assert_pass(
        "Dispatch Is Synthetic",
        dispatch.synthetic is True,
    )

    assert_pass(
        "Authorization Consumed Exactly Once",
        engine.state.authorization
        is not None
        and engine.state.authorization.consumed,
    )


def test_4_authorization_replay() -> None:
    print(
        f"\n{UNIT_NAME} TEST 4: AUTHORIZATION REPLAY REJECTION"
    )
    print_rule()

    engine = N26Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    engine.authorize(
        lease
    )

    engine.recover_and_dispatch(
        lease
    )

    expect_block(
        "Consumed Authorization Replay Rejected",
        lambda: engine.recover_and_dispatch(
            lease
        ),
        "generation is not authorized",
    )


def test_5_completion_terminality() -> None:
    print(
        f"\n{UNIT_NAME} TEST 5: COMPLETION + TERMINAL IMMUTABILITY"
    )
    print_rule()

    engine, lease, cert = (
        make_completed_engine()
    )

    before = len(
        engine.state.dispatches
    )

    status, dispatch = engine.recover_and_dispatch(
        lease
    )

    assert_pass(
        "Generation Completed",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    assert_pass(
        "Exactly One Synthetic Dispatch Recorded",
        before == 1,
    )

    assert_pass(
        "Repeated Recovery Is Already Final",
        status == "already_final",
    )

    assert_pass(
        "Repeated Recovery Produced No Second Dispatch",
        dispatch is None
        and len(engine.state.dispatches)
        == before,
    )

    assert_pass(
        "Completion Certificate Exists",
        cert.generation
        == engine.state.generation,
    )


def test_6_checkpoint_round_trip() -> None:
    print(
        f"\n{UNIT_NAME} TEST 6: CHECKPOINT ROUND TRIP"
    )
    print_rule()

    engine, _, cert = (
        make_completed_engine()
    )

    checkpoint = engine.checkpoint()

    restored = N26Engine.restore_checkpoint(
        checkpoint
    )

    assert_pass(
        "Checkpoint Restores Completed State",
        restored.state.phase
        == PHASE_COMPLETED,
    )

    assert_pass(
        "Checkpoint Preserves Generation",
        restored.state.generation
        == engine.state.generation,
    )

    assert_pass(
        "Checkpoint Preserves Dispatch Identity",
        restored.state.dispatches[
            0
        ].dispatch_id
        == engine.state.dispatches[
            0
        ].dispatch_id,
    )

    assert_pass(
        "Checkpoint Preserves Consumed Authorization",
        restored.state.authorization
        is not None
        and restored.state.authorization.consumed,
    )

    assert_pass(
        "Checkpoint Preserves Recovery Certificate",
        len(
            restored.state.certificates
        )
        == 1
        and restored.state.certificates[
            0
        ].certificate_id
        == cert.certificate_id,
    )


def test_7_snapshot_tamper() -> None:
    print(
        f"\n{UNIT_NAME} TEST 7: SNAPSHOT TAMPER REJECTION"
    )
    print_rule()

    engine, _, _ = (
        make_completed_engine()
    )

    snapshot = engine.checkpoint()

    snapshot[
        "payload"
    ][
        "generation"
    ] += 99

    try:
        N26Engine.restore_checkpoint(
            snapshot
        )

    except Exception as exc:
        message = str(exc).replace(
            "checkpoint",
            "snapshot",
        )

        local_block(
            message
        )

        assert_pass(
            "Tampered Snapshot Rejected",
            "integrity seal mismatch"
            in str(exc),
        )

        return

    raise AssertionError(
        "Tampered Snapshot Rejected"
    )


def test_8_wal_integrity() -> None:
    print(
        f"\n{UNIT_NAME} TEST 8: WAL INTEGRITY"
    )
    print_rule()

    engine, _, _ = (
        make_completed_engine()
    )

    assert_pass(
        "WAL Records Validate",
        engine.validate_wal(),
    )

    final_hash = (
        engine.state.journal[
            -1
        ].record_hash
    )

    assert_pass(
        "WAL Final Hash Matches Journal",
        engine.wal_tip
        == final_hash,
    )


def test_9_torn_tail() -> None:
    print(
        f"\n{UNIT_NAME} TEST 9: TORN WAL TAIL REJECTION"
    )
    print_rule()

    engine, _, _ = (
        make_completed_engine()
    )

    serialized = [
        asdict(item)
        for item
        in engine.state.journal
    ]

    torn = copy.deepcopy(
        serialized
    )

    torn[
        -1
    ].pop(
        "record_hash",
        None,
    )

    try:
        engine.detect_torn_wal_tail(
            torn
        )

    except Exception as exc:
        local_block(
            str(exc)
        )

        assert_pass(
            "Torn WAL Tail Rejected",
            "torn WAL tail detected"
            in str(exc),
        )

        return

    raise AssertionError(
        "Torn WAL Tail Rejected"
    )


def test_10_generation_advance() -> None:
    print(
        f"\n{UNIT_NAME} TEST 10: GENERATION ADVANCE"
    )
    print_rule()

    engine, _, prior_cert = (
        make_completed_engine()
    )

    old_generation = (
        engine.state.generation
    )

    old_epoch = (
        engine.state.recovery_epoch
    )

    old_lineage = (
        engine.state.lineage
    )

    old_dispatch = (
        engine.state.dispatches[
            0
        ].dispatch_id
    )

    (
        new_generation,
        new_lineage,
        new_epoch,
    ) = engine.advance_generation()

    assert_pass(
        "Generation Advanced Monotonically",
        new_generation
        > old_generation,
    )

    assert_pass(
        "Recovery Epoch Advanced Monotonically",
        new_epoch
        > old_epoch,
    )

    assert_pass(
        "New Generation Uses Different Lineage",
        new_lineage
        != old_lineage,
    )

    assert_pass(
        "New Generation Returns To PREPARED",
        engine.state.phase
        == PHASE_PREPARED,
    )

    assert_pass(
        "Prior Completed Dispatch Preserved",
        any(
            item.dispatch_id
            == old_dispatch
            for item
            in engine.state.dispatches
        ),
    )

    assert_pass(
        "Prior Recovery Certificate Preserved",
        any(
            item.certificate_id
            == prior_cert.certificate_id
            for item
            in engine.state.certificates
        ),
    )


def test_11_anti_aba() -> None:
    print(
        f"\n{UNIT_NAME} TEST 11: ANTI-ABA STALE LEASE REJECTION"
    )
    print_rule()

    engine, old_lease, _ = (
        make_completed_engine(
            "worker-reused"
        )
    )

    old_generation = (
        old_lease.generation
    )

    old_lineage = (
        old_lease.lineage
    )

    old_epoch = (
        old_lease.recovery_epoch
    )

    old_nonce = (
        old_lease.nonce
    )

    engine.advance_generation()

    new_lease = engine.acquire_recovery_lease(
        "worker-reused"
    )

    assert_pass(
        "Reacquired Owner Uses Higher Generation",
        new_lease.generation
        > old_generation,
    )

    assert_pass(
        "Reacquired Owner Uses Different Lineage",
        new_lease.lineage
        != old_lineage,
    )

    assert_pass(
        "Reacquired Owner Uses Higher Epoch",
        new_lease.recovery_epoch
        > old_epoch,
    )

    assert_pass(
        "Reacquired Owner Uses Higher Nonce",
        new_lease.nonce
        > old_nonce,
    )

    expect_block(
        "Reused Worker Identity Cannot Resurrect Prior Generation Lease",
        lambda: engine.authorize(
            old_lease
        ),
        "recovery lease fence mismatch",
    )


def test_12_checkpoint_tamper() -> None:
    print(
        f"\n{UNIT_NAME} TEST 12: CHECKPOINT TAMPER REJECTION"
    )
    print_rule()

    engine, _, _ = (
        make_completed_engine()
    )

    checkpoint = (
        engine.checkpoint()
    )

    checkpoint[
        "payload"
    ][
        "phase"
    ] = PHASE_PREPARED

    expect_block(
        "Tampered Checkpoint Rejected",
        lambda: N26Engine.restore_checkpoint(
            checkpoint
        ),
        "checkpoint integrity seal mismatch",
    )


def test_13_concurrent_single_dispatch() -> None:
    print(
        f"\n{UNIT_NAME} TEST 13: CONCURRENT RECOVERY SINGLE DISPATCH"
    )
    print_rule()

    engine = N26Engine()

    lease = engine.acquire_recovery_lease(
        "worker-A"
    )

    engine.authorize(
        lease
    )

    results: List[str] = []
    errors: List[str] = []

    gate = threading.Barrier(
        8
    )

    def worker() -> None:
        try:
            gate.wait()

            try:
                status, _ = (
                    engine.recover_and_dispatch(
                        lease
                    )
                )

                results.append(
                    status
                )

            except ValueError as exc:
                if (
                    "generation is not authorized"
                    in str(exc)
                ):
                    results.append(
                        "rejected"
                    )

                else:
                    errors.append(
                        str(exc)
                    )

        except Exception as exc:
            errors.append(
                str(exc)
            )

    threads = [
        threading.Thread(
            target=worker
        )
        for _ in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    engine.complete_generation(
        lease
    )

    generation_dispatches = [
        item
        for item
        in engine.state.dispatches
        if item.generation
        == engine.state.generation
    ]

    assert_pass(
        "Concurrent Recovery Produced Exactly One Synthetic Dispatch",
        len(
            generation_dispatches
        )
        == 1,
    )

    assert_pass(
        "Concurrent Recovery Final State Completed",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    assert_pass(
        "Concurrent Recovery Preserved Consumed Authorization",
        engine.state.authorization
        is not None
        and engine.state.authorization.consumed,
    )

    assert_pass(
        "Concurrent Recovery Produced No Structural Errors",
        len(errors) == 0,
    )


def test_14_certificate_binding() -> None:
    print(
        f"\n{UNIT_NAME} TEST 14: DURABLE RECOVERY CERTIFICATE BINDING"
    )
    print_rule()

    engine, _, cert = (
        make_completed_engine()
    )

    assert_pass(
        "Recovery Certificate Seal Valid",
        engine.validate_certificate(
            cert
        ),
    )

    assert_pass(
        "Certificate Bound To Generation",
        cert.generation
        == engine.state.generation,
    )

    assert_pass(
        "Certificate Bound To Lineage",
        cert.lineage
        == engine.state.lineage,
    )

    assert_pass(
        "Certificate Bound To Recovery Epoch",
        cert.recovery_epoch
        == engine.state.recovery_epoch,
    )

    assert_pass(
        "Certificate Bound To WAL Tip",
        cert.wal_tip
        == engine.wal_tip,
    )

    assert_pass(
        "Certificate Bound To State Digest",
        cert.state_digest
        == engine.state_digest(),
    )

    assert_pass(
        "Certificate Bound To Dispatch Identity",
        cert.dispatch_id
        == engine.state.dispatches[
            -1
        ].dispatch_id,
    )

    assert_pass(
        "Certificate Bound To Consumed Authorization",
        engine.state.authorization
        is not None
        and cert.authorization_id
        == engine.state.authorization.authorization_id
        and engine.state.authorization.consumed,
    )


def test_15_certificate_tamper() -> None:
    print(
        f"\n{UNIT_NAME} TEST 15: RECOVERY CERTIFICATE TAMPER REJECTION"
    )
    print_rule()

    engine, _, cert = (
        make_completed_engine()
    )

    forged = copy.deepcopy(
        cert
    )

    forged.dispatch_id = (
        "dispatch_forged"
    )

    expect_block(
        "Tampered Recovery Certificate Rejected",
        lambda: engine.validate_certificate(
            forged
        ),
        "recovery certificate seal mismatch",
    )


def test_16_certificate_restart_and_anti_replay() -> None:
    print(
        f"\n{UNIT_NAME} TEST 16: CERTIFICATE RESTART + CROSS-GENERATION ANTI-REPLAY"
    )
    print_rule()

    engine, _, cert = (
        make_completed_engine()
    )

    restored = (
        N26Engine.restore_checkpoint(
            engine.checkpoint()
        )
    )

    restored_cert = (
        restored.state.certificates[
            0
        ]
    )

    assert_pass(
        "Certificate Survives Restart",
        restored_cert.certificate_id
        == cert.certificate_id,
    )

    assert_pass(
        "Restored Certificate Validates",
        restored.validate_certificate(
            restored_cert
        ),
    )

    restored.advance_generation()

    expect_block(
        "Prior Certificate Cannot Authorize New Generation",
        lambda: restored.validate_certificate(
            restored_cert,
            require_current_state=True,
        ),
        "not for current generation",
    )

    assert_pass(
        "Prior Certificate Remains Historically Verifiable",
        restored.validate_certificate(
            restored_cert,
            require_current_state=False,
        ),
    )


def test_17_final_firebreak() -> None:
    print(
        f"\n{UNIT_NAME} TEST 17: FINAL NETWORK WRITE FIREBREAK"
    )
    print_rule()

    try:
        real_network_post(
            LEVERAGE_ENDPOINT,
            {
                "symbol": SYMBOL,
            },
        )

    except Exception as exc:
        local_block(
            str(exc)
        )

        assert_pass(
            "Real Network POST Blocked",
            "real network POST is disabled"
            in str(exc),
        )

    else:
        raise AssertionError(
            "Real Network POST Blocked"
        )

    assert_pass(
        "Real POST Remains Disabled",
        REAL_POST_ENABLED is False,
    )

    assert_pass(
        "Demo POST Remains Disabled",
        DEMO_POST_ENABLED is False,
    )

    assert_pass(
        "Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    assert_pass(
        "Synthetic Transport Remains Mandatory",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )


def run_tests() -> None:
    tests = [
        test_1_bootstrap,
        test_2_lease_and_authorization,
        test_3_exact_synthetic_transport,
        test_4_authorization_replay,
        test_5_completion_terminality,
        test_6_checkpoint_round_trip,
        test_7_snapshot_tamper,
        test_8_wal_integrity,
        test_9_torn_tail,
        test_10_generation_advance,
        test_11_anti_aba,
        test_12_checkpoint_tamper,
        test_13_concurrent_single_dispatch,
        test_14_certificate_binding,
        test_15_certificate_tamper,
        test_16_certificate_restart_and_anti_replay,
        test_17_final_firebreak,
    ]

    for test in tests:
        test()


print(
    "R28 UNIT N.26: PART 3 DEFINITIONS LOADED",
    flush=True,
)
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
                    "real_post": REAL_POST_ENABLED,
                    "demo_post": DEMO_POST_ENABLED,
                    "network_writes": NETWORK_WRITES_ENABLED,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
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


def final_assessment() -> None:
    print(
        f"\n{UNIT_NAME} FINAL ASSESSMENT"
    )
    print_rule()

    structural_failures = 0
    readiness_blockers = 0

    print(
        f"Structural Safety Failures = {structural_failures}",
        flush=True,
    )

    print(
        f"Readiness Blockers = {readiness_blockers}",
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
        "Durable Recovery Certificate = ✅ VERIFIED",
        flush=True,
    )

    print(
        "Certificate Restart Persistence = ✅ VERIFIED",
        flush=True,
    )

    print(
        "Cross-Generation Certificate Anti-Replay = ✅ VERIFIED",
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

    print(
        f"\n✅ {UNIT_NAME} PASSED",
        flush=True,
    )


def main() -> None:
    run_tests()

    final_assessment()

    print(
        f"{UNIT_NAME}: RUNTIME READY",
        flush=True,
    )

    start_health_server()

    try:
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        print(
            f"{UNIT_NAME}: SHUTDOWN REQUESTED",
            flush=True,
        )


if __name__ == "__main__":
    main()
