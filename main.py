# ============================================================================
# R28 UNIT N.27
# DURABLE RECOVERY CERTIFICATE CHAIN + ANCESTRY / ROLLBACK PROTECTION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
# ============================================================================

print("R28 UNIT N.27: MAIN.PY ENTERED", flush=True)

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

print("R28 UNIT N.27: IMPORTS COMPLETE", flush=True)

UNIT_NAME = "R28 UNIT N.27"
UNIT_VERSION = "N.27"

SYMBOL = "BTCUSDT"
LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

INTEGRITY_KEY = b"R28-N27-LOCAL-INTEGRITY-KEY"
CERTIFICATE_KEY = b"R28-N27-RECOVERY-CERTIFICATE-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

ZERO_HASH = "0" * 64

print("R28 UNIT N.27: CONSTANTS INITIALIZED", flush=True)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_hex(key: bytes, value: str) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


@dataclass
class WALRecord:
    index: int
    event: str
    generation: int
    recovery_epoch: int
    payload: Dict[str, Any]
    prev_hash: str
    record_hash: str


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
    payload_hash: str
    consumed: bool = False


@dataclass
class DispatchRecord:
    dispatch_id: str
    generation: int
    lineage: str
    recovery_epoch: int
    method: str
    path: str
    payload_hash: str
    synthetic: bool


@dataclass
class RecoveryCertificate:
    certificate_id: str
    certificate_seq: int
    generation: int
    lineage: str
    recovery_epoch: int
    wal_tip: str
    checkpoint_hash: str
    state_digest: str
    dispatch_id: str
    authorization_id: str
    prev_certificate_hash: str
    certificate_hash: str
    seal: str


@dataclass
class DurableState:
    generation: int = 1
    lineage: str = field(
        default_factory=lambda: uuid.uuid4().hex
    )
    recovery_epoch: int = 1
    phase: str = PHASE_PREPARED
    lease_nonce: int = 0
    authorization: Optional[Authorization] = None
    dispatches: List[DispatchRecord] = field(default_factory=list)
    wal: List[WALRecord] = field(default_factory=list)
    certificates: List[RecoveryCertificate] = field(default_factory=list)
    checkpoint_hash: str = ZERO_HASH
    snapshot_seal: str = ""


class SyntheticTransport:
    def __init__(self) -> None:
        self.calls: List[
            Tuple[str, str, Dict[str, Any]]
        ] = []

    def post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        require(
            SYNTHETIC_TRANSPORT_ONLY,
            "synthetic transport is not mandatory",
        )

        require(
            not NETWORK_WRITES_ENABLED,
            "network writes unexpectedly enabled",
        )

        require(
            not REAL_POST_ENABLED,
            "real POST unexpectedly enabled",
        )

        require(
            not DEMO_POST_ENABLED,
            "demo POST unexpectedly enabled",
        )

        require(
            path == LEVERAGE_ENDPOINT,
            "synthetic transport path mismatch",
        )

        self.calls.append(
            (
                HTTP_METHOD,
                path,
                copy.deepcopy(payload),
            )
        )

        return {
            "synthetic": True,
            "accepted": True,
            "path": path,
            "payload_hash": sha256_text(
                canonical_json(payload)
            ),
        }


def real_network_post(
    path: str,
    payload: Dict[str, Any],
) -> None:

    local_block(
        "real network POST is disabled"
    )

    raise RuntimeError(
        "real network POST is disabled"
    )


print(
    "R28 UNIT N.27: PART 1 DEFINITIONS LOADED",
    flush=True,
)
class N27Engine:
    def __init__(self, state: Optional[DurableState] = None) -> None:
        self.state = copy.deepcopy(state) if state is not None else DurableState()
        self.transport = SyntheticTransport()
        self._lock = threading.RLock()

        if not self.state.wal:
            self._append_wal(
                "GENERATION_CREATED",
                {
                    "phase": self.state.phase,
                },
            )

        self._refresh_checkpoint()
        self._seal_snapshot()

    def _wal_hash(
        self,
        index: int,
        event: str,
        generation: int,
        recovery_epoch: int,
        payload: Dict[str, Any],
        prev_hash: str,
    ) -> str:

        body = {
            "index": index,
            "event": event,
            "generation": generation,
            "recovery_epoch": recovery_epoch,
            "payload": payload,
            "prev_hash": prev_hash,
        }

        return sha256_text(
            canonical_json(body)
        )

    def _append_wal(
        self,
        event: str,
        payload: Dict[str, Any],
    ) -> WALRecord:

        prev_hash = (
            self.state.wal[-1].record_hash
            if self.state.wal
            else ZERO_HASH
        )

        index = len(self.state.wal)

        record_hash = self._wal_hash(
            index,
            event,
            self.state.generation,
            self.state.recovery_epoch,
            payload,
            prev_hash,
        )

        record = WALRecord(
            index=index,
            event=event,
            generation=self.state.generation,
            recovery_epoch=self.state.recovery_epoch,
            payload=copy.deepcopy(payload),
            prev_hash=prev_hash,
            record_hash=record_hash,
        )

        self.state.wal.append(record)

        return record

    def validate_wal(self) -> bool:
        prev = ZERO_HASH

        for expected_index, record in enumerate(
            self.state.wal
        ):
            require(
                record.index == expected_index,
                "torn WAL tail detected",
            )

            require(
                record.prev_hash == prev,
                "WAL predecessor hash mismatch",
            )

            expected_hash = self._wal_hash(
                record.index,
                record.event,
                record.generation,
                record.recovery_epoch,
                record.payload,
                record.prev_hash,
            )

            require(
                hmac.compare_digest(
                    record.record_hash,
                    expected_hash,
                ),
                "WAL record hash mismatch",
            )

            prev = record.record_hash

        return True

    def wal_tip(self) -> str:
        return (
            self.state.wal[-1].record_hash
            if self.state.wal
            else ZERO_HASH
        )

    def _state_digest_material(
        self,
    ) -> Dict[str, Any]:

        auth = (
            asdict(self.state.authorization)
            if self.state.authorization
            else None
        )

        return {
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "phase": self.state.phase,
            "authorization": auth,
            "dispatches": [
                asdict(x)
                for x in self.state.dispatches
            ],
            "wal_tip": self.wal_tip(),
            "certificate_count": len(
                self.state.certificates
            ),
        }

    def state_digest(self) -> str:
        return sha256_text(
            canonical_json(
                self._state_digest_material()
            )
        )

    def _checkpoint_material(
        self,
    ) -> Dict[str, Any]:

        return {
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "phase": self.state.phase,
            "wal_tip": self.wal_tip(),
            "dispatch_ids": [
                x.dispatch_id
                for x in self.state.dispatches
            ],
            "certificate_hashes": [
                x.certificate_hash
                for x in self.state.certificates
            ],
        }

    def _refresh_checkpoint(self) -> None:
        self.state.checkpoint_hash = sha256_text(
            canonical_json(
                self._checkpoint_material()
            )
        )

    def _snapshot_material(
        self,
    ) -> Dict[str, Any]:

        return {
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "phase": self.state.phase,
            "lease_nonce": self.state.lease_nonce,
            "authorization": (
                asdict(self.state.authorization)
                if self.state.authorization
                else None
            ),
            "dispatches": [
                asdict(x)
                for x in self.state.dispatches
            ],
            "wal": [
                asdict(x)
                for x in self.state.wal
            ],
            "certificates": [
                asdict(x)
                for x in self.state.certificates
            ],
            "checkpoint_hash": (
                self.state.checkpoint_hash
            ),
        }

    def _seal_snapshot(self) -> None:
        self._refresh_checkpoint()

        self.state.snapshot_seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(
                self._snapshot_material()
            ),
        )

    def validate_snapshot(self) -> bool:
        self.validate_wal()

        expected_checkpoint = sha256_text(
            canonical_json(
                self._checkpoint_material()
            )
        )

        require(
            hmac.compare_digest(
                self.state.checkpoint_hash,
                expected_checkpoint,
            ),
            "checkpoint integrity seal mismatch",
        )

        expected_seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(
                self._snapshot_material()
            ),
        )

        require(
            hmac.compare_digest(
                self.state.snapshot_seal,
                expected_seal,
            ),
            "snapshot integrity seal mismatch",
        )

        self.validate_certificate_chain()

        return True

    def snapshot(self) -> DurableState:
        with self._lock:
            self._seal_snapshot()

            return copy.deepcopy(
                self.state
            )

    @classmethod
    def restore_state(
        cls,
        state: DurableState,
    ) -> "N27Engine":

        candidate = copy.deepcopy(state)

        engine = cls.__new__(cls)

        engine.state = candidate
        engine.transport = SyntheticTransport()
        engine._lock = threading.RLock()

        engine.validate_snapshot()

        return engine

    def acquire_recovery_lease(
        self,
        owner: str,
    ) -> RecoveryLease:

        with self._lock:
            require(
                self.state.phase
                != PHASE_COMPLETED,
                "terminal generation cannot acquire recovery lease",
            )

            self.state.lease_nonce += 1

            lease = RecoveryLease(
                owner=owner,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                nonce=self.state.lease_nonce,
            )

            self._append_wal(
                "LEASE_ACQUIRED",
                {
                    "owner": owner,
                    "nonce": lease.nonce,
                    "lineage": lease.lineage,
                },
            )

            self._seal_snapshot()

            return lease

    def _validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:

        require(
            lease.generation
            == self.state.generation,
            "recovery lease fence mismatch",
        )

        require(
            lease.lineage
            == self.state.lineage,
            "recovery lease fence mismatch",
        )

        require(
            lease.recovery_epoch
            == self.state.recovery_epoch,
            "recovery lease fence mismatch",
        )

        require(
            lease.nonce
            == self.state.lease_nonce,
            "recovery lease fence mismatch",
        )

    def authorize(
        self,
        lease: RecoveryLease,
        payload: Dict[str, Any],
    ) -> Authorization:

        with self._lock:
            self._validate_lease(lease)

            require(
                self.state.phase
                == PHASE_PREPARED,
                "generation is not prepared",
            )

            payload_hash = sha256_text(
                canonical_json(payload)
            )

            auth = Authorization(
                authorization_id=uuid.uuid4().hex,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                payload_hash=payload_hash,
                consumed=False,
            )

            self.state.authorization = auth
            self.state.phase = PHASE_AUTHORIZED

            self._append_wal(
                "AUTHORIZED",
                {
                    "authorization_id": (
                        auth.authorization_id
                    ),
                    "payload_hash": payload_hash,
                },
            )

            self._seal_snapshot()

            return copy.deepcopy(auth)

    def _consume_authorization(
        self,
        payload: Dict[str, Any],
    ) -> Authorization:

        auth = self.state.authorization

        require(
            auth is not None,
            "generation is not authorized",
        )

        require(
            not auth.consumed,
            "authorization already consumed",
        )

        require(
            auth.generation
            == self.state.generation,
            "authorization generation mismatch",
        )

        require(
            auth.lineage
            == self.state.lineage,
            "authorization lineage mismatch",
        )

        require(
            auth.recovery_epoch
            == self.state.recovery_epoch,
            "authorization recovery epoch mismatch",
        )

        payload_hash = sha256_text(
            canonical_json(payload)
        )

        require(
            auth.payload_hash
            == payload_hash,
            "authorization payload hash mismatch",
        )

        auth.consumed = True

        self._append_wal(
            "AUTHORIZATION_CONSUMED",
            {
                "authorization_id": (
                    auth.authorization_id
                )
            },
        )

        return auth

    def dispatch(
        self,
        lease: RecoveryLease,
        payload: Dict[str, Any],
    ) -> DispatchRecord:

        with self._lock:
            self._validate_lease(lease)

            require(
                self.state.phase
                == PHASE_AUTHORIZED,
                "generation is not authorized",
            )

            auth = self._consume_authorization(
                payload
            )

            response = self.transport.post(
                LEVERAGE_ENDPOINT,
                payload,
            )

            dispatch = DispatchRecord(
                dispatch_id=uuid.uuid4().hex,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload_hash=response[
                    "payload_hash"
                ],
                synthetic=True,
            )

            self.state.dispatches.append(
                dispatch
            )

            self.state.phase = PHASE_DISPATCHED

            self._append_wal(
                "SYNTHETIC_DISPATCHED",
                {
                    "dispatch_id": (
                        dispatch.dispatch_id
                    ),
                    "authorization_id": (
                        auth.authorization_id
                    ),
                    "payload_hash": (
                        dispatch.payload_hash
                    ),
                },
            )

            self.state.phase = PHASE_COMPLETED

            self._append_wal(
                "GENERATION_COMPLETED",
                {
                    "dispatch_id": (
                        dispatch.dispatch_id
                    )
                },
            )

            self._create_recovery_certificate(
                dispatch,
                auth,
            )

            self._seal_snapshot()

            return copy.deepcopy(
                dispatch
            )

    def recover(
        self,
        owner: str,
        payload: Dict[str, Any],
    ) -> Optional[DispatchRecord]:

        with self._lock:
            if (
                self.state.phase
                == PHASE_COMPLETED
            ):
                return None

            lease = self.acquire_recovery_lease(
                owner
            )

            if (
                self.state.phase
                == PHASE_PREPARED
            ):
                self.authorize(
                    lease,
                    payload,
                )

            return self.dispatch(
                lease,
                payload,
            )


print(
    "R28 UNIT N.27: PART 2 DEFINITIONS LOADED",
    flush=True,
)
class N27Engine:
    def __init__(self, state: Optional[DurableState] = None) -> None:
        self.state = copy.deepcopy(state) if state is not None else DurableState()
        self.transport = SyntheticTransport()
        self._lock = threading.RLock()

        if not self.state.wal:
            self._append_wal(
                "GENERATION_CREATED",
                {
                    "phase": self.state.phase,
                },
            )

        self._refresh_checkpoint()
        self._seal_snapshot()

    def _wal_hash(
        self,
        index: int,
        event: str,
        generation: int,
        recovery_epoch: int,
        payload: Dict[str, Any],
        prev_hash: str,
    ) -> str:

        body = {
            "index": index,
            "event": event,
            "generation": generation,
            "recovery_epoch": recovery_epoch,
            "payload": payload,
            "prev_hash": prev_hash,
        }

        return sha256_text(
            canonical_json(body)
        )

    def _append_wal(
        self,
        event: str,
        payload: Dict[str, Any],
    ) -> WALRecord:

        prev_hash = (
            self.state.wal[-1].record_hash
            if self.state.wal
            else ZERO_HASH
        )

        index = len(self.state.wal)

        record_hash = self._wal_hash(
            index,
            event,
            self.state.generation,
            self.state.recovery_epoch,
            payload,
            prev_hash,
        )

        record = WALRecord(
            index=index,
            event=event,
            generation=self.state.generation,
            recovery_epoch=self.state.recovery_epoch,
            payload=copy.deepcopy(payload),
            prev_hash=prev_hash,
            record_hash=record_hash,
        )

        self.state.wal.append(record)

        return record

    def validate_wal(self) -> bool:
        prev = ZERO_HASH

        for expected_index, record in enumerate(
            self.state.wal
        ):
            require(
                record.index == expected_index,
                "torn WAL tail detected",
            )

            require(
                record.prev_hash == prev,
                "WAL predecessor hash mismatch",
            )

            expected_hash = self._wal_hash(
                record.index,
                record.event,
                record.generation,
                record.recovery_epoch,
                record.payload,
                record.prev_hash,
            )

            require(
                hmac.compare_digest(
                    record.record_hash,
                    expected_hash,
                ),
                "WAL record hash mismatch",
            )

            prev = record.record_hash

        return True

    def wal_tip(self) -> str:
        return (
            self.state.wal[-1].record_hash
            if self.state.wal
            else ZERO_HASH
        )

    def _state_digest_material(
        self,
    ) -> Dict[str, Any]:

        auth = (
            asdict(self.state.authorization)
            if self.state.authorization
            else None
        )

        return {
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "phase": self.state.phase,
            "authorization": auth,
            "dispatches": [
                asdict(x)
                for x in self.state.dispatches
            ],
            "wal_tip": self.wal_tip(),
            "certificate_count": len(
                self.state.certificates
            ),
        }

    def state_digest(self) -> str:
        return sha256_text(
            canonical_json(
                self._state_digest_material()
            )
        )

    def _checkpoint_material(
        self,
    ) -> Dict[str, Any]:

        return {
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "phase": self.state.phase,
            "wal_tip": self.wal_tip(),
            "dispatch_ids": [
                x.dispatch_id
                for x in self.state.dispatches
            ],
            "certificate_hashes": [
                x.certificate_hash
                for x in self.state.certificates
            ],
        }

    def _refresh_checkpoint(self) -> None:
        self.state.checkpoint_hash = sha256_text(
            canonical_json(
                self._checkpoint_material()
            )
        )

    def _snapshot_material(
        self,
    ) -> Dict[str, Any]:

        return {
            "generation": self.state.generation,
            "lineage": self.state.lineage,
            "recovery_epoch": self.state.recovery_epoch,
            "phase": self.state.phase,
            "lease_nonce": self.state.lease_nonce,
            "authorization": (
                asdict(self.state.authorization)
                if self.state.authorization
                else None
            ),
            "dispatches": [
                asdict(x)
                for x in self.state.dispatches
            ],
            "wal": [
                asdict(x)
                for x in self.state.wal
            ],
            "certificates": [
                asdict(x)
                for x in self.state.certificates
            ],
            "checkpoint_hash": (
                self.state.checkpoint_hash
            ),
        }

    def _seal_snapshot(self) -> None:
        self._refresh_checkpoint()

        self.state.snapshot_seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(
                self._snapshot_material()
            ),
        )

    def validate_snapshot(self) -> bool:
        self.validate_wal()

        expected_checkpoint = sha256_text(
            canonical_json(
                self._checkpoint_material()
            )
        )

        require(
            hmac.compare_digest(
                self.state.checkpoint_hash,
                expected_checkpoint,
            ),
            "checkpoint integrity seal mismatch",
        )

        expected_seal = hmac_hex(
            INTEGRITY_KEY,
            canonical_json(
                self._snapshot_material()
            ),
        )

        require(
            hmac.compare_digest(
                self.state.snapshot_seal,
                expected_seal,
            ),
            "snapshot integrity seal mismatch",
        )

        self.validate_certificate_chain()

        return True

    def snapshot(self) -> DurableState:
        with self._lock:
            self._seal_snapshot()

            return copy.deepcopy(
                self.state
            )

    @classmethod
    def restore_state(
        cls,
        state: DurableState,
    ) -> "N27Engine":

        candidate = copy.deepcopy(state)

        engine = cls.__new__(cls)

        engine.state = candidate
        engine.transport = SyntheticTransport()
        engine._lock = threading.RLock()

        engine.validate_snapshot()

        return engine

    def acquire_recovery_lease(
        self,
        owner: str,
    ) -> RecoveryLease:

        with self._lock:
            require(
                self.state.phase
                != PHASE_COMPLETED,
                "terminal generation cannot acquire recovery lease",
            )

            self.state.lease_nonce += 1

            lease = RecoveryLease(
                owner=owner,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                nonce=self.state.lease_nonce,
            )

            self._append_wal(
                "LEASE_ACQUIRED",
                {
                    "owner": owner,
                    "nonce": lease.nonce,
                    "lineage": lease.lineage,
                },
            )

            self._seal_snapshot()

            return lease

    def _validate_lease(
        self,
        lease: RecoveryLease,
    ) -> None:

        require(
            lease.generation
            == self.state.generation,
            "recovery lease fence mismatch",
        )

        require(
            lease.lineage
            == self.state.lineage,
            "recovery lease fence mismatch",
        )

        require(
            lease.recovery_epoch
            == self.state.recovery_epoch,
            "recovery lease fence mismatch",
        )

        require(
            lease.nonce
            == self.state.lease_nonce,
            "recovery lease fence mismatch",
        )

    def authorize(
        self,
        lease: RecoveryLease,
        payload: Dict[str, Any],
    ) -> Authorization:

        with self._lock:
            self._validate_lease(lease)

            require(
                self.state.phase
                == PHASE_PREPARED,
                "generation is not prepared",
            )

            payload_hash = sha256_text(
                canonical_json(payload)
            )

            auth = Authorization(
                authorization_id=uuid.uuid4().hex,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                payload_hash=payload_hash,
                consumed=False,
            )

            self.state.authorization = auth
            self.state.phase = PHASE_AUTHORIZED

            self._append_wal(
                "AUTHORIZED",
                {
                    "authorization_id": (
                        auth.authorization_id
                    ),
                    "payload_hash": payload_hash,
                },
            )

            self._seal_snapshot()

            return copy.deepcopy(auth)

    def _consume_authorization(
        self,
        payload: Dict[str, Any],
    ) -> Authorization:

        auth = self.state.authorization

        require(
            auth is not None,
            "generation is not authorized",
        )

        require(
            not auth.consumed,
            "authorization already consumed",
        )

        require(
            auth.generation
            == self.state.generation,
            "authorization generation mismatch",
        )

        require(
            auth.lineage
            == self.state.lineage,
            "authorization lineage mismatch",
        )

        require(
            auth.recovery_epoch
            == self.state.recovery_epoch,
            "authorization recovery epoch mismatch",
        )

        payload_hash = sha256_text(
            canonical_json(payload)
        )

        require(
            auth.payload_hash
            == payload_hash,
            "authorization payload hash mismatch",
        )

        auth.consumed = True

        self._append_wal(
            "AUTHORIZATION_CONSUMED",
            {
                "authorization_id": (
                    auth.authorization_id
                )
            },
        )

        return auth

    def dispatch(
        self,
        lease: RecoveryLease,
        payload: Dict[str, Any],
    ) -> DispatchRecord:

        with self._lock:
            self._validate_lease(lease)

            require(
                self.state.phase
                == PHASE_AUTHORIZED,
                "generation is not authorized",
            )

            auth = self._consume_authorization(
                payload
            )

            response = self.transport.post(
                LEVERAGE_ENDPOINT,
                payload,
            )

            dispatch = DispatchRecord(
                dispatch_id=uuid.uuid4().hex,
                generation=self.state.generation,
                lineage=self.state.lineage,
                recovery_epoch=self.state.recovery_epoch,
                method=HTTP_METHOD,
                path=LEVERAGE_ENDPOINT,
                payload_hash=response[
                    "payload_hash"
                ],
                synthetic=True,
            )

            self.state.dispatches.append(
                dispatch
            )

            self.state.phase = PHASE_DISPATCHED

            self._append_wal(
                "SYNTHETIC_DISPATCHED",
                {
                    "dispatch_id": (
                        dispatch.dispatch_id
                    ),
                    "authorization_id": (
                        auth.authorization_id
                    ),
                    "payload_hash": (
                        dispatch.payload_hash
                    ),
                },
            )

            self.state.phase = PHASE_COMPLETED

            self._append_wal(
                "GENERATION_COMPLETED",
                {
                    "dispatch_id": (
                        dispatch.dispatch_id
                    )
                },
            )

            self._create_recovery_certificate(
                dispatch,
                auth,
            )

            self._seal_snapshot()

            return copy.deepcopy(
                dispatch
            )

    def recover(
        self,
        owner: str,
        payload: Dict[str, Any],
    ) -> Optional[DispatchRecord]:

        with self._lock:
            if (
                self.state.phase
                == PHASE_COMPLETED
            ):
                return None

            lease = self.acquire_recovery_lease(
                owner
            )

            if (
                self.state.phase
                == PHASE_PREPARED
            ):
                self.authorize(
                    lease,
                    payload,
                )

            return self.dispatch(
                lease,
                payload,
            )


print(
    "R28 UNIT N.27: PART 2 DEFINITIONS LOADED",
    flush=True,
)
