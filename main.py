# ============================================================================
# R28 UNIT N.25
# DURABLE WAL + CHECKPOINT + EXACTLY-ONCE SYNTHETIC TRANSPORT
# + GENERATION LINEAGE + ANTI-ABA RECOVERY FENCING
#
# CORRECTED COMPLETE STANDALONE COPY/PASTE VERSION
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
from typing import Any, Dict, List, Optional, Tuple

print("R28 UNIT N.25: IMPORTS COMPLETE", flush=True)

# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.25"
UNIT_VERSION = "N.25"

SYMBOL = "BTCUSDT"
LEVERAGE = 100
MARGIN_MODE = "ISOLATED"
TRANSPORT_METHOD = "POST"
TRANSPORT_PATH = "/capi/v2/account/leverage"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

STATE_PREPARED = "PREPARED"
STATE_COMMITTED = "COMMITTED"
STATE_DISPATCHED = "DISPATCHED"
STATE_COMPLETED = "COMPLETED"

WAL_GENESIS = "0" * 64
SNAPSHOT_KEY = b"R28-N25-SNAPSHOT-INTEGRITY-KEY"

print("R28 UNIT N.25: CONSTANTS INITIALIZED", flush=True)

# ============================================================================
# HELPERS
# ============================================================================


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hmac_sha256(key: bytes, value: str) -> str:
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()


def new_lineage_id() -> str:
    return uuid.uuid4().hex


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)
    raise RuntimeError(message)


def test_header(number: int, title: str) -> None:
    print("", flush=True)
    print(f"{UNIT_NAME} TEST {number}: {title}", flush=True)
    print("-" * 92, flush=True)


def passed(label: str) -> None:
    print(f"{label:<84} ✅ PASS", flush=True)


def expect_rejection(fn, label: str) -> str:
    rejected = False
    message = ""
    try:
        fn()
    except RuntimeError as exc:
        rejected = True
        message = str(exc)
    require(rejected, f"{label} was unexpectedly accepted")
    passed(label)
    return message


def payload_for_leverage() -> Dict[str, str]:
    return {
        "symbol": SYMBOL,
        "leverage": str(LEVERAGE),
        "marginMode": MARGIN_MODE,
    }


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass(frozen=True)
class RecoveryLease:
    owner: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    lease_nonce: int

    def identity(self) -> Tuple[Any, ...]:
        return (
            self.owner,
            self.generation,
            self.lineage_id,
            self.recovery_epoch,
            self.lease_nonce,
        )


@dataclass(frozen=True)
class DurableCommit:
    commit_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    payload: Dict[str, str]
    payload_hash: str
    transport_method: str
    transport_path: str

    def binding(self) -> Tuple[Any, ...]:
        return (
            self.commit_id,
            self.generation,
            self.lineage_id,
            self.recovery_epoch,
            self.payload_hash,
            self.transport_method,
            self.transport_path,
        )


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    commit_id: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    payload_hash: str
    transport_method: str
    transport_path: str
    transmitted: bool


@dataclass(frozen=True)
class WalRecord:
    sequence: int
    record_type: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    body: Dict[str, Any]
    prev_hash: str
    record_hash: str


@dataclass
class DurableState:
    generation: int = 1
    lineage_id: str = field(default_factory=new_lineage_id)
    recovery_epoch: int = 1
    lease_nonce_counter: int = 0
    state: str = STATE_PREPARED
    payload: Dict[str, str] = field(default_factory=payload_for_leverage)
    payload_hash: str = ""
    durable_commit: Optional[DurableCommit] = None
    receipt: Optional[SyntheticReceipt] = None
    finalized_commit_id: Optional[str] = None
    completed_dispatches: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    synthetic_transport_count: int = 0
    last_lease: Optional[RecoveryLease] = None
    wal: List[WalRecord] = field(default_factory=list)
    checkpoint_seal: str = ""

    def __post_init__(self) -> None:
        if not self.payload_hash:
            self.payload_hash = sha256_text(canonical_json(self.payload))
