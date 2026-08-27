from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


print("R29 UNIT F: MAIN.PY ENTERED", flush=True)


# =============================================================================
# R29 UNIT F
# RESTART / CRASH MUTATION-INTENT FENCING
#
# SAFETY DISCIPLINE:
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO NETWORK WRITES
#   - NO LIVE LEVERAGE MUTATION
#   - NO LIVE MARGIN MUTATION
#   - NO LIVE POSITION MUTATION
#   - NO LIVE ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE:
#   Unit E proved:
#       coherent read-only snapshot
#       -> exact 100x leverage mutation envelope
#       -> local signing
#       -> one-time authorization
#       -> synthetic dispatch
#       -> durable replay protection
#
#   Unit F now proves:
#       mutation intent
#       -> durable prepare
#       -> generation / recovery-epoch binding
#       -> crash-window recovery
#       -> exactly-once synthetic dispatch fence
#       -> terminal finalization
#       -> restart replay rejection
#
# IMPORTANT:
#   This file contains no implementation path capable of sending an HTTP POST,
#   PUT, PATCH, DELETE, WebSocket write, real order, demo order, leverage
#   mutation, margin mutation, position mutation, or account mutation.
# =============================================================================


print("R29 UNIT F: IMPORTS COMPLETE", flush=True)


# =============================================================================
# PART 1 — CONSTANTS / DATA MODEL / BASIC UTILITIES
# =============================================================================

UNIT = "R29 UNIT F"

SEPARATOR = "-" * 92

STRATEGY_SYMBOL = os.getenv("STRATEGY_SYMBOL", "BTCUSDT").strip().upper()
STRATEGY_ASSET = os.getenv("STRATEGY_ASSET", "USDT").strip().upper()
TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

LEVERAGE_METHOD = "POST"
LEVERAGE_PATH = "/capi/v3/account/leverage"

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True
WEBSOCKET_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

HEALTH_PORT = int(os.getenv("PORT", "10000"))
HEARTBEAT_SECONDS = 30

STATE_PATH = Path(
    os.getenv("R29_UNIT_F_STATE_PATH", "/tmp/r29_unit_f_state.json")
)
WAL_PATH = Path(
    os.getenv("R29_UNIT_F_WAL_PATH", "/tmp/r29_unit_f_wal.jsonl")
)

AUTHORIZATION_TTL_SECONDS = int(
    os.getenv("R29_UNIT_F_AUTH_TTL_SECONDS", "120")
)

PASS_ASSERTIONS = 0
TEST_GROUPS_EXECUTED = 0


class LocalBlock(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def integrity_hash(value: Dict[str, Any], excluded: Optional[List[str]] = None) -> str:
    excluded = excluded or []
    filtered = {k: v for k, v in value.items() if k not in excluded}
    return sha256_text(canonical_json(filtered))


def now_ms() -> int:
    return int(time.time() * 1000)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def print_separator() -> None:
    print(SEPARATOR, flush=True)


def test_header(number: int, title: str) -> None:
    global TEST_GROUPS_EXECUTED
    TEST_GROUPS_EXECUTED += 1
    print_separator()
    print(f"{UNIT} TEST {number}: {title}", flush=True)
    print_separator()


def require(condition: bool, label: str) -> None:
    global PASS_ASSERTIONS
    if not condition:
        print(f"{label:<82} ❌ FAIL", flush=True)
        raise AssertionError(label)
    PASS_ASSERTIONS += 1
    print(f"{label:<82} ✅ PASS", flush=True)


def local_block(message: str) -> None:
    print(f"{UNIT} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)
    raise LocalBlock(message)


def expect_local_block(label: str, fn) -> None:
    blocked = False
    try:
        fn()
    except LocalBlock:
        blocked = True
    require(blocked, label)


@dataclass
class MutationIntent:
    mutation_id: str
    symbol: str
    method: str
    path: str
    body: Dict[str, str]
    body_hash: str
    snapshot_id: str
    snapshot_hash: str
    generation: int
    recovery_epoch: int
    created_ms: int
    executable: bool
    synthetic_only: bool
    integrity_hash: str


@dataclass
class Authorization:
    authorization_id: str
    mutation_id: str
    body_hash: str
    snapshot_hash: str
    generation: int
    recovery_epoch: int
    issued_ms: int
    expires_ms: int
    consumed: bool
    consumed_ms: Optional[int]
    integrity_hash: str


@dataclass
class DispatchReceipt:
    receipt_id: str
    mutation_id: str
    authorization_id: str
    generation: int
    recovery_epoch: int
    body_hash: str
    transport: str
    transmitted: bool
    network_write_count: int
    created_ms: int
    integrity_hash: str


@dataclass
class DurableState:
    runtime_id: str
    generation: int
    recovery_epoch: int
    boot_count: int
    phase: str
    snapshot_id: str
    snapshot_hash: str
    mutation: MutationIntent
    authorization: Authorization
    receipt: Optional[DispatchReceipt]
    dispatch_fence_key: str
    finalized_fence_key: Optional[str]
    synthetic_dispatch_count: int
    real_order_count: int
    demo_order_count: int
    network_write_count: int
    websocket_write_count: int
    real_write_firebreak_count: int
    demo_write_firebreak_count: int
    websocket_firebreak_count: int
    leverage_mutation_firebreak_count: int
    margin_mutation_firebreak_count: int
    position_mutation_firebreak_count: int
    account_mutation_firebreak_count: int
    state_integrity_hash: str = field(default="")


print("R29 UNIT F: CONSTANTS INITIALIZED", flush=True)


# =============================================================================
# DURABLE SERIALIZATION / RESTORE
# =============================================================================

def mutation_from_dict(data: Dict[str, Any]) -> MutationIntent:
    return MutationIntent(**data)


def authorization_from_dict(data: Dict[str, Any]) -> Authorization:
    return Authorization(**data)


def receipt_from_dict(data: Optional[Dict[str, Any]]) -> Optional[DispatchReceipt]:
    if data is None:
        return None
    return DispatchReceipt(**data)


def state_to_dict(state: DurableState) -> Dict[str, Any]:
    return asdict(state)


def state_from_dict(data: Dict[str, Any]) -> DurableState:
    copied = dict(data)
    copied["mutation"] = mutation_from_dict(copied["mutation"])
    copied["authorization"] = authorization_from_dict(copied["authorization"])
    copied["receipt"] = receipt_from_dict(copied.get("receipt"))
    return DurableState(**copied)


def compute_state_integrity(state: DurableState) -> str:
    data = state_to_dict(state)
    data.pop("state_integrity_hash", None)
    return sha256_text(canonical_json(data))


def validate_mutation(mutation: MutationIntent) -> None:
    require(mutation.symbol == STRATEGY_SYMBOL, "Mutation Symbol Binding Valid")
    require(mutation.method == LEVERAGE_METHOD, "Mutation Method Binding Valid")
    require(mutation.path == LEVERAGE_PATH, "Mutation Path Binding Valid")
    require(
        mutation.body_hash == sha256_text(canonical_json(mutation.body)),
        "Mutation Body Hash Valid",
    )
    raw = asdict(mutation)
    require(
        mutation.integrity_hash
        == integrity_hash(raw, excluded=["integrity_hash"]),
        "Mutation Integrity Hash Valid",
    )


def validate_authorization(auth: Authorization, mutation: MutationIntent) -> None:
    require(
        auth.mutation_id == mutation.mutation_id,
        "Authorization Mutation Binding Valid",
    )
    require(
        auth.body_hash == mutation.body_hash,
        "Authorization Body Binding Valid",
    )
    require(
        auth.snapshot_hash == mutation.snapshot_hash,
        "Authorization Snapshot Binding Valid",
    )
    require(
        auth.generation == mutation.generation,
        "Authorization Generation Binding Valid",
    )
    require(
        auth.recovery_epoch == mutation.recovery_epoch,
        "Authorization Recovery Epoch Binding Valid",
    )
    raw = asdict(auth)
    require(
        auth.integrity_hash == integrity_hash(raw, excluded=["integrity_hash"]),
        "Authorization Integrity Hash Valid",
    )


def validate_receipt(
    receipt: DispatchReceipt,
    mutation: MutationIntent,
    auth: Authorization,
) -> None:
    require(
        receipt.mutation_id == mutation.mutation_id,
        "Receipt Mutation Binding Valid",
    )
    require(
        receipt.authorization_id == auth.authorization_id,
        "Receipt Authorization Binding Valid",
    )
    require(
        receipt.body_hash == mutation.body_hash,
        "Receipt Body Hash Binding Valid",
    )
    require(
        receipt.generation == mutation.generation,
        "Receipt Generation Binding Valid",
    )
    require(
        receipt.recovery_epoch == mutation.recovery_epoch,
        "Receipt Recovery Epoch Binding Valid",
    )
    require(
        receipt.transport == "SYNTHETIC",
        "Receipt Synthetic Transport Valid",
    )
    require(
        receipt.transmitted is False,
        "Receipt Reports No Transmission",
    )
    require(
        receipt.network_write_count == 0,
        "Receipt Network Write Count Zero",
    )
    raw = asdict(receipt)
    require(
        receipt.integrity_hash == integrity_hash(raw, excluded=["integrity_hash"]),
        "Receipt Integrity Hash Valid",
    )


def save_state(state: DurableState) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state.state_integrity_hash = compute_state_integrity(state)
    payload = canonical_json(state_to_dict(state))
    temp = STATE_PATH.with_suffix(".tmp")
    temp.write_text(payload, encoding="utf-8")
    os.replace(temp, STATE_PATH)


def load_state() -> Optional[DurableState]:
    if not STATE_PATH.exists():
        return None

    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state = state_from_dict(data)
    expected = compute_state_integrity(state)

    if state.state_integrity_hash != expected:
        local_block("durable state integrity mismatch")

    return state


def append_wal(
    event: str,
    state: DurableState,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    WAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "event_id": new_id("wal"),
        "event": event,
        "runtime_id": state.runtime_id,
        "generation": state.generation,
        "recovery_epoch": state.recovery_epoch,
        "mutation_id": state.mutation.mutation_id,
        "authorization_id": state.authorization.authorization_id,
        "phase": state.phase,
        "timestamp_ms": now_ms(),
        "extra": extra or {},
    }

    record["record_hash"] = integrity_hash(
        record,
        excluded=["record_hash"],
    )

    with WAL_PATH.open("a", encoding="utf-8") as fh:
        fh.write(canonical_json(record) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def read_wal() -> List[Dict[str, Any]]:
    if not WAL_PATH.exists():
        return []

    records: List[Dict[str, Any]] = []

    for line in WAL_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        record = json.loads(line)
        expected = integrity_hash(
            record,
            excluded=["record_hash"],
        )

        if record.get("record_hash") != expected:
            local_block("WAL record integrity mismatch")

        records.append(record)

    return records


print("R29 UNIT F: PART 1 DEFINITIONS LOADED", flush=True)
# =============================================================================
# PART 2 — CONSTRUCTION / FIREBREAKS / SYNTHETIC DISPATCH
# =============================================================================

def build_snapshot() -> Dict[str, Any]:
    # Unit F deliberately uses a frozen local compatibility snapshot.
    # It performs no external network calls.
    snapshot = {
        "snapshot_id": new_id("snapshot"),
        "symbol": STRATEGY_SYMBOL,
        "asset": STRATEGY_ASSET,
        "margin_type": TARGET_MARGIN_TYPE,
        "position_count": 0,
        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,
        "source": "R29_UNIT_F_LOCAL_FROZEN_COMPATIBILITY_SNAPSHOT",
        "created_ms": now_ms(),
    }

    snapshot["snapshot_hash"] = integrity_hash(
        snapshot,
        excluded=["snapshot_hash"],
    )

    return snapshot


def build_mutation(
    snapshot: Dict[str, Any],
    generation: int,
    recovery_epoch: int,
) -> MutationIntent:
    body = {
        "isolatedLongLeverage": str(TARGET_LONG_LEVERAGE),
        "isolatedShortLeverage": str(TARGET_SHORT_LEVERAGE),
        "marginType": TARGET_MARGIN_TYPE,
        "symbol": STRATEGY_SYMBOL,
    }

    mutation = MutationIntent(
        mutation_id=new_id("mutation"),
        symbol=STRATEGY_SYMBOL,
        method=LEVERAGE_METHOD,
        path=LEVERAGE_PATH,
        body=body,
        body_hash=sha256_text(canonical_json(body)),
        snapshot_id=snapshot["snapshot_id"],
        snapshot_hash=snapshot["snapshot_hash"],
        generation=generation,
        recovery_epoch=recovery_epoch,
        created_ms=now_ms(),
        executable=False,
        synthetic_only=True,
        integrity_hash="",
    )

    mutation.integrity_hash = integrity_hash(
        asdict(mutation),
        excluded=["integrity_hash"],
    )

    return mutation


def build_authorization(
    mutation: MutationIntent,
) -> Authorization:
    issued = now_ms()

    auth = Authorization(
        authorization_id=new_id("auth"),
        mutation_id=mutation.mutation_id,
        body_hash=mutation.body_hash,
        snapshot_hash=mutation.snapshot_hash,
        generation=mutation.generation,
        recovery_epoch=mutation.recovery_epoch,
        issued_ms=issued,
        expires_ms=issued + AUTHORIZATION_TTL_SECONDS * 1000,
        consumed=False,
        consumed_ms=None,
        integrity_hash="",
    )

    auth.integrity_hash = integrity_hash(
        asdict(auth),
        excluded=["integrity_hash"],
    )

    return auth


def dispatch_fence_key(
    mutation: MutationIntent,
    authorization: Authorization,
) -> str:
    material = {
        "mutation_id": mutation.mutation_id,
        "authorization_id": authorization.authorization_id,
        "body_hash": mutation.body_hash,
        "snapshot_hash": mutation.snapshot_hash,
        "generation": mutation.generation,
        "recovery_epoch": mutation.recovery_epoch,
    }

    return sha256_text(canonical_json(material))


# =============================================================================
# HARD WRITE FIREBREAKS
# =============================================================================

def real_http_write(
    state: DurableState,
    method: str,
    path: str,
) -> None:
    state.real_write_firebreak_count += 1
    save_state(state)

    local_block(
        f"REAL network {method} blocked for {path}"
    )


def demo_http_write(
    state: DurableState,
    method: str,
    path: str,
) -> None:
    state.demo_write_firebreak_count += 1
    save_state(state)

    local_block(
        f"DEMO network {method} blocked for {path}"
    )


def websocket_write(
    state: DurableState,
) -> None:
    state.websocket_firebreak_count += 1
    save_state(state)

    local_block(
        "WebSocket write blocked"
    )


def leverage_mutation(
    state: DurableState,
) -> None:
    state.leverage_mutation_firebreak_count += 1
    save_state(state)

    local_block(
        "leverage mutation disabled"
    )


def margin_mutation(
    state: DurableState,
) -> None:
    state.margin_mutation_firebreak_count += 1
    save_state(state)

    local_block(
        "margin mutation disabled"
    )


def position_mutation(
    state: DurableState,
) -> None:
    state.position_mutation_firebreak_count += 1
    save_state(state)

    local_block(
        "position mutation disabled"
    )


def account_mutation(
    state: DurableState,
) -> None:
    state.account_mutation_firebreak_count += 1
    save_state(state)

    local_block(
        "account mutation disabled"
    )


# =============================================================================
# SYNTHETIC DISPATCH PRECONDITIONS
# =============================================================================

def verify_dispatch_preconditions(
    state: DurableState,
) -> None:
    if state.phase not in {"AUTHORIZED", "DISPATCHING"}:
        local_block(
            "dispatch phase is not authorized"
        )

    if state.authorization.consumed:
        local_block(
            "authorization replay rejected"
        )

    if now_ms() > state.authorization.expires_ms:
        local_block(
            "authorization token is stale"
        )

    if state.mutation.executable:
        local_block(
            "mutation unexpectedly marked executable"
        )

    if not state.mutation.synthetic_only:
        local_block(
            "mutation is not synthetic-only"
        )

    if state.mutation.generation != state.generation:
        local_block(
            "mutation generation mismatch"
        )

    if state.authorization.generation != state.generation:
        local_block(
            "authorization generation mismatch"
        )

    if state.mutation.recovery_epoch != state.recovery_epoch:
        local_block(
            "mutation recovery epoch mismatch"
        )

    if state.authorization.recovery_epoch != state.recovery_epoch:
        local_block(
            "authorization recovery epoch mismatch"
        )

    if state.dispatch_fence_key != dispatch_fence_key(
        state.mutation,
        state.authorization,
    ):
        local_block(
            "dispatch fence key mismatch"
        )


# =============================================================================
# SYNTHETIC-ONLY DISPATCH
# =============================================================================

def synthetic_dispatch(
    state: DurableState,
) -> DispatchReceipt:
    verify_dispatch_preconditions(state)

    # Durable authorization consumption occurs BEFORE the synthetic receipt
    # is returned. This closes the crash/restart window in which an
    # authorization might otherwise be reused.

    state.phase = "DISPATCHING"

    state.authorization.consumed = True
    state.authorization.consumed_ms = now_ms()

    state.authorization.integrity_hash = integrity_hash(
        asdict(state.authorization),
        excluded=["integrity_hash"],
    )

    save_state(state)

    append_wal(
        "AUTHORIZATION_CONSUMED",
        state,
    )

    receipt = DispatchReceipt(
        receipt_id=new_id("receipt"),
        mutation_id=state.mutation.mutation_id,
        authorization_id=state.authorization.authorization_id,
        generation=state.generation,
        recovery_epoch=state.recovery_epoch,
        body_hash=state.mutation.body_hash,
        transport="SYNTHETIC",
        transmitted=False,
        network_write_count=0,
        created_ms=now_ms(),
        integrity_hash="",
    )

    receipt.integrity_hash = integrity_hash(
        asdict(receipt),
        excluded=["integrity_hash"],
    )

    state.receipt = receipt
    state.synthetic_dispatch_count += 1
    state.phase = "DISPATCHED"

    save_state(state)

    append_wal(
        "SYNTHETIC_DISPATCHED",
        state,
        {
            "receipt_id": receipt.receipt_id,
        },
    )

    return receipt


# =============================================================================
# TERMINAL FINALIZATION
# =============================================================================

def finalize(
    state: DurableState,
) -> None:
    if state.phase != "DISPATCHED":
        local_block(
            "finalization requires DISPATCHED phase"
        )

    if state.receipt is None:
        local_block(
            "finalization requires synthetic receipt"
        )

    state.finalized_fence_key = state.dispatch_fence_key
    state.phase = "COMPLETED"

    save_state(state)

    append_wal(
        "FINALIZED",
        state,
    )


print("R29 UNIT F: PART 2 DEFINITIONS LOADED", flush=True)
# =============================================================================
# PART 3 — CRASH / RESTART RECOVERY RULES
# =============================================================================

def clone_state(state: DurableState) -> DurableState:
    return state_from_dict(json.loads(canonical_json(state_to_dict(state))))


def validate_full_state(state: DurableState) -> None:
    validate_mutation(state.mutation)
    validate_authorization(state.authorization, state.mutation)
    require(
        state.dispatch_fence_key
        == dispatch_fence_key(state.mutation, state.authorization),
        "Dispatch Fence Key Valid",
    )
    require(state.network_write_count == 0, "Durable Network Write Count Zero")
    require(state.real_order_count == 0, "Durable Real Order Count Zero")
    require(state.demo_order_count == 0, "Durable Demo Order Count Zero")
    if state.receipt is not None:
        validate_receipt(state.receipt, state.mutation, state.authorization)
    require(
        state.state_integrity_hash == compute_state_integrity(state),
        "Durable State Integrity Hash Valid",
    )


def recover_state(state: DurableState) -> DurableState:
    validate_full_state(state)

    if state.phase == "PREPARED":
        local_block("prepared state has no durable authorization")

    if state.phase == "AUTHORIZED":
        # Authorization survived but has not yet been consumed.
        # Recovery preserves it without dispatching automatically.
        return state

    if state.phase == "DISPATCHING":
        # Consumption is durable. A recovery may not issue another dispatch.
        if not state.authorization.consumed:
            local_block("dispatching state missing consumed authorization")
        state.phase = "FENCED_AFTER_CRASH"
        save_state(state)
        append_wal("RECOVERED_CONSUMED_FENCE", state)
        return state

    if state.phase == "DISPATCHED":
        if state.receipt is None:
            local_block("dispatched state missing receipt")
        finalize(state)
        return state

    if state.phase == "COMPLETED":
        if state.finalized_fence_key != state.dispatch_fence_key:
            local_block("finalized fence mismatch")
        return state

    if state.phase == "FENCED_AFTER_CRASH":
        return state

    local_block("unknown durable phase")
    raise AssertionError("unreachable")


def reject_generation_substitution(state: DurableState) -> None:
    forged = clone_state(state)
    forged.generation += 1
    forged.state_integrity_hash = compute_state_integrity(forged)
    verify_dispatch_preconditions(forged)


def reject_recovery_epoch_substitution(state: DurableState) -> None:
    forged = clone_state(state)
    forged.recovery_epoch += 1
    forged.state_integrity_hash = compute_state_integrity(forged)
    verify_dispatch_preconditions(forged)


def reject_snapshot_substitution(state: DurableState) -> None:
    forged = clone_state(state)
    forged.mutation.snapshot_hash = sha256_text("forged-snapshot")
    forged.mutation.integrity_hash = integrity_hash(
        asdict(forged.mutation), excluded=["integrity_hash"]
    )
    forged.state_integrity_hash = compute_state_integrity(forged)
    if forged.authorization.snapshot_hash != forged.mutation.snapshot_hash:
        local_block("authorization snapshot binding mismatch")
    raise AssertionError("forged snapshot substitution was not rejected")


def reject_body_substitution(state: DurableState) -> None:
    forged = clone_state(state)
    forged.mutation.body["isolatedLongLeverage"] = "99"
    forged.mutation.body_hash = sha256_text(canonical_json(forged.mutation.body))
    forged.mutation.integrity_hash = integrity_hash(
        asdict(forged.mutation), excluded=["integrity_hash"]
    )
    forged.state_integrity_hash = compute_state_integrity(forged)
    if forged.authorization.body_hash != forged.mutation.body_hash:
        local_block("authorization body hash mismatch")
    raise AssertionError("forged body substitution was not rejected")


def reject_fence_substitution(state: DurableState) -> None:
    forged = clone_state(state)
    forged.dispatch_fence_key = sha256_text("forged-fence")
    forged.state_integrity_hash = compute_state_integrity(forged)
    verify_dispatch_preconditions(forged)


def recover_from_disk() -> Optional[DurableState]:
    state = load_state()
    if state is None:
        return None
    state.boot_count += 1
    save_state(state)
    return recover_state(state)


print("R29 UNIT F: PART 3 DEFINITIONS LOADED", flush=True)
