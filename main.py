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
