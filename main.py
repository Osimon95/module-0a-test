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
