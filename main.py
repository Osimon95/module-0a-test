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
