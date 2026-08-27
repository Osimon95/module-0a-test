from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


print("R29 UNIT F: MAIN.PY ENTERED", flush=True)


# =============================================================================
# R29 UNIT F
# SYNTHETIC RECOVERY / DURABLE EXECUTION VALIDATION
#
# SAFETY DISCIPLINE
#
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE
#
#   Continue R29 restart-safe validation while maintaining a completely
#   non-executable transport boundary.
#
#   Unit F validates:
#
#       configuration
#           ->
#       durable intent
#           ->
#       authorization binding
#           ->
#       synthetic dispatch
#           ->
#       durable receipt
#           ->
#       restart recovery
#           ->
#       replay rejection
#           ->
#       persistent heartbeat
#
# =============================================================================


print("R29 UNIT F: IMPORTS COMPLETE", flush=True)


# =============================================================================
# CONSTANTS
# =============================================================================

UNIT_NAME = "R29 UNIT F"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT")

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False
WEBSOCKET_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

GENERATION = 1
RECOVERY_EPOCH = 1

HEARTBEAT_INTERVAL_SECONDS = 30

STATE_DIR = Path(os.getenv("R29_STATE_DIR", "/tmp/r29_unit_f"))
STATE_FILE = STATE_DIR / "runtime_state.json"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

SEPARATOR = "-" * 92


print("R29 UNIT F: CONSTANTS INITIALIZED", flush=True)


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class RuntimeState:
    unit: str
    runtime_id: str
    generation: int
    recovery_epoch: int
    synthetic_only: bool
    network_writes: bool
    leverage_mutation: bool
    dispatch_count: int
    receipt_count: int
    replay_blocks: int
    finalized: bool
    last_receipt_id: Optional[str]


@dataclass(frozen=True)
class SyntheticIntent:
    intent_id: str
    symbol: str
    generation: int
    recovery_epoch: int
    action: str
    transport: str


@dataclass(frozen=True)
class SyntheticAuthorization:
    authorization_id: str
    intent_id: str
    generation: int
    recovery_epoch: int
    payload_hash: str


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    intent_id: str
    authorization_id: str
    payload_hash: str
    synthetic: bool
    transmitted: bool
    generation: int
    recovery_epoch: int


# =============================================================================
# GENERAL HELPERS
# =============================================================================


def banner(title: str) -> None:
    print(SEPARATOR, flush=True)
    print(title, flush=True)
    print(SEPARATOR, flush=True)


def pass_line(label: str) -> None:
    print(f"{label:<82} ✅ PASS", flush=True)


def fail_line(label: str) -> None:
    print(f"{label:<82} ❌ FAIL", flush=True)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_value(value: Any) -> str:
    encoded = canonical_json(value).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def require(condition: bool, label: str) -> None:
    if not condition:
        fail_line(label)
        raise RuntimeError(f"{UNIT_NAME}: validation failed: {label}")

    pass_line(label)


# =============================================================================
# DURABLE STATE
# =============================================================================


def default_state() -> RuntimeState:
    return RuntimeState(
        unit=UNIT_NAME,
        runtime_id=str(uuid.uuid4()),
        generation=GENERATION,
        recovery_epoch=RECOVERY_EPOCH,
        synthetic_only=True,
        network_writes=False,
        leverage_mutation=False,
        dispatch_count=0,
        receipt_count=0,
        replay_blocks=0,
        finalized=False,
        last_receipt_id=None,
    )


def save_state(state: RuntimeState) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    temp_file = STATE_FILE.with_suffix(".tmp")

    payload = canonical_json(asdict(state))

    temp_file.write_text(payload, encoding="utf-8")

    os.replace(temp_file, STATE_FILE)


def load_state() -> RuntimeState:
    if not STATE_FILE.exists():
        state = default_state()
        save_state(state)
        return state

    raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    return RuntimeState(
        unit=str(raw["unit"]),
        runtime_id=str(raw["runtime_id"]),
        generation=int(raw["generation"]),
        recovery_epoch=int(raw["recovery_epoch"]),
        synthetic_only=bool(raw["synthetic_only"]),
        network_writes=bool(raw["network_writes"]),
        leverage_mutation=bool(raw["leverage_mutation"]),
        dispatch_count=int(raw["dispatch_count"]),
        receipt_count=int(raw["receipt_count"]),
        replay_blocks=int(raw["replay_blocks"]),
        finalized=bool(raw["finalized"]),
        last_receipt_id=raw.get("last_receipt_id"),
    )


# =============================================================================
# HARD SAFETY BOUNDARY
# =============================================================================


class NetworkWriteBlocked(RuntimeError):
    pass


class MutationBlocked(RuntimeError):
    pass


class ReplayBlocked(RuntimeError):
    pass


def block_network_write(method: str, path: str) -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK: REAL network {method.upper()} blocked | path={path}",
        flush=True,
    )

    raise NetworkWriteBlocked(
        f"{UNIT_NAME}: network writes are permanently disabled"
    )


def block_leverage_mutation() -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK: leverage mutation disabled",
        flush=True,
    )

    raise MutationBlocked(
        f"{UNIT_NAME}: leverage mutation is disabled"
    )


def block_margin_mutation() -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK: margin mutation disabled",
        flush=True,
    )

    raise MutationBlocked(
        f"{UNIT_NAME}: margin mutation is disabled"
    )


def block_position_mutation() -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK: position mutation disabled",
        flush=True,
    )

    raise MutationBlocked(
        f"{UNIT_NAME}: position mutation is disabled"
    )


# =============================================================================
# SYNTHETIC EXECUTION PIPELINE
# =============================================================================


def build_intent() -> SyntheticIntent:
    return SyntheticIntent(
        intent_id=str(uuid.uuid4()),
        symbol=SYMBOL,
        generation=GENERATION,
        recovery_epoch=RECOVERY_EPOCH,
        action="VALIDATE_SYNTHETIC_DISPATCH",
        transport="SYNTHETIC_ONLY",
    )


def build_authorization(
    intent: SyntheticIntent,
) -> SyntheticAuthorization:

    payload = {
        "intent_id": intent.intent_id,
        "symbol": intent.symbol,
        "generation": intent.generation,
        "recovery_epoch": intent.recovery_epoch,
        "action": intent.action,
        "transport": intent.transport,
    }

    payload_hash = sha256_value(payload)

    return SyntheticAuthorization(
        authorization_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        generation=intent.generation,
        recovery_epoch=intent.recovery_epoch,
        payload_hash=payload_hash,
    )


def synthetic_dispatch(
    intent: SyntheticIntent,
    authorization: SyntheticAuthorization,
    state: RuntimeState,
) -> SyntheticReceipt:

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            f"{UNIT_NAME}: synthetic-only transport requirement violated"
        )

    if NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            f"{UNIT_NAME}: network-write configuration violation"
        )

    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            f"{UNIT_NAME}: live execution unexpectedly enabled"
        )

    if DEMO_ORDER_EXECUTION:
        raise RuntimeError(
            f"{UNIT_NAME}: demo execution unexpectedly enabled"
        )

    if state.finalized:
        state.replay_blocks += 1
        save_state(state)

        raise ReplayBlocked(
            f"{UNIT_NAME}: finalized synthetic dispatch cannot be replayed"
        )

    expected_payload = {
        "intent_id": intent.intent_id,
        "symbol": intent.symbol,
        "generation": intent.generation,
        "recovery_epoch": intent.recovery_epoch,
        "action": intent.action,
        "transport": intent.transport,
    }

    expected_hash = sha256_value(expected_payload)

    if authorization.payload_hash != expected_hash:
        raise RuntimeError(
            f"{UNIT_NAME}: authorization payload hash mismatch"
        )

    if authorization.intent_id != intent.intent_id:
        raise RuntimeError(
            f"{UNIT_NAME}: authorization intent binding mismatch"
        )

    if authorization.generation != state.generation:
        raise RuntimeError(
            f"{UNIT_NAME}: authorization generation mismatch"
        )

    if authorization.recovery_epoch != state.recovery_epoch:
        raise RuntimeError(
            f"{UNIT_NAME}: authorization recovery epoch mismatch"
        )

    receipt = SyntheticReceipt(
        receipt_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        authorization_id=authorization.authorization_id,
        payload_hash=authorization.payload_hash,
        synthetic=True,
        transmitted=False,
        generation=state.generation,
        recovery_epoch=state.recovery_epoch,
    )

    state.dispatch_count += 1
    state.receipt_count += 1
    state.finalized = True
    state.last_receipt_id = receipt.receipt_id

    save_state(state)

    return receipt


# =============================================================================
# HEALTH SERVER
# =============================================================================


class HealthHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        try:
            request = self.request.recv(1024)

            if not request:
                return

            body = json.dumps(
                {
                    "status": "ok",
                    "unit": UNIT_NAME,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                    "network_writes": NETWORK_WRITES_ENABLED,
                    "leverage_mutation": LEVERAGE_MUTATION_ENABLED,
                    "generation": GENERATION,
                    "recovery_epoch": RECOVERY_EPOCH,
                }
            ).encode("utf-8")

            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json\r\n"
                + f"Content-Length: {len(body)}\r\n".encode("utf-8")
                + b"Connection: close\r\n"
                + b"\r\n"
                + body
            )

            self.request.sendall(response)

        except Exception:
            pass


class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_health_server() -> None:

    def run_server() -> None:
        try:
            with ThreadedTCPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            ) as server:

                print(
                    f"{UNIT_NAME}: HEALTH SERVER LISTENING ON PORT "
                    f"{HEALTH_PORT}",
                    flush=True,
                )

                server.serve_forever()

        except Exception as exc:
            print(
                f"{UNIT_NAME}: HEALTH SERVER WARNING: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=run_server,
        name="r29-unit-f-health",
        daemon=True,
    )

    thread.start()


# =============================================================================
# VALIDATION TESTS
# =============================================================================


def test_1_safety_configuration() -> None:
    banner(f"{UNIT_NAME} TEST 1: SAFETY CONFIGURATION")

    require(
        LIVE_ORDER_EXECUTION is False,
        "Real Order Execution Disabled",
    )

    require(
        DEMO_ORDER_EXECUTION is False,
        "Demo Order Execution Disabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "Network Writes Disabled",
    )

    require(
        LEVERAGE_MUTATION_ENABLED is False,
        "Leverage Mutation Disabled",
    )

    require(
        MARGIN_MUTATION_ENABLED is False,
        "Margin Mutation Disabled",
    )

    require(
        POSITION_MUTATION_ENABLED is False,
        "Position Mutation Disabled",
    )

    require(
        ACCOUNT_MUTATION_ENABLED is False,
        "Account Mutation Disabled",
    )

    require(
        WEBSOCKET_WRITES_ENABLED is False,
        "WebSocket Writes Disabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic Transport Only",
    )


def test_2_runtime_state(state: RuntimeState) -> None:
    banner(f"{UNIT_NAME} TEST 2: DURABLE RUNTIME STATE")

    require(
        state.unit == UNIT_NAME,
        "Runtime Unit Identity Matches",
    )

    require(
        bool(state.runtime_id),
        "Runtime ID Present",
    )

    require(
        state.generation == GENERATION,
        "Generation Matches",
    )

    require(
        state.recovery_epoch == RECOVERY_EPOCH,
        "Recovery Epoch Matches",
    )

    require(
        state.synthetic_only is True,
        "Persisted Synthetic-Only Flag True",
    )

    require(
        state.network_writes is False,
        "Persisted Network-Write Flag False",
    )

    require(
        state.leverage_mutation is False,
        "Persisted Leverage Mutation Flag False",
    )


def test_3_write_firebreak() -> None:
    banner(f"{UNIT_NAME} TEST 3: NETWORK WRITE FIREBREAK")

    methods = (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    )

    for method in methods:

        blocked = False

        try:
            block_network_write(
                method,
                "/synthetic/r29/unit-f",
            )

        except NetworkWriteBlocked:
            blocked = True

        require(
            blocked,
            f"HTTP {method} Blocked",
        )


def test_4_mutation_firebreaks() -> None:
    banner(f"{UNIT_NAME} TEST 4: MUTATION FIREBREAKS")

    leverage_blocked = False

    try:
        block_leverage_mutation()
    except MutationBlocked:
        leverage_blocked = True

    require(
        leverage_blocked,
        "Leverage Mutation Firebreak Active",
    )

    margin_blocked = False

    try:
        block_margin_mutation()
    except MutationBlocked:
        margin_blocked = True

    require(
        margin_blocked,
        "Margin Mutation Firebreak Active",
    )

    position_blocked = False

    try:
        block_position_mutation()
    except MutationBlocked:
        position_blocked = True

    require(
        position_blocked,
        "Position Mutation Firebreak Active",
    )


def test_5_synthetic_intent(
    state: RuntimeState,
) -> tuple[
    SyntheticIntent,
    SyntheticAuthorization,
]:

    banner(f"{UNIT_NAME} TEST 5: SYNTHETIC INTENT AND AUTHORIZATION")

    intent = build_intent()

    require(
        intent.symbol == SYMBOL,
        "Intent Symbol Matches",
    )

    require(
        intent.generation == state.generation,
        "Intent Generation Matches",
    )

    require(
        intent.recovery_epoch == state.recovery_epoch,
        "Intent Recovery Epoch Matches",
    )

    require(
        intent.transport == "SYNTHETIC_ONLY",
        "Intent Transport Synthetic Only",
    )

    authorization = build_authorization(intent)

    require(
        authorization.intent_id == intent.intent_id,
        "Authorization Bound To Intent",
    )

    require(
        bool(authorization.payload_hash),
        "Authorization Payload Hash Present",
    )

    require(
        len(authorization.payload_hash) == 64,
        "Authorization SHA256 Length Valid",
    )

    return intent, authorization


def test_6_synthetic_dispatch(
    state: RuntimeState,
    intent: SyntheticIntent,
    authorization: SyntheticAuthorization,
) -> Optional[SyntheticReceipt]:

    banner(f"{UNIT_NAME} TEST 6: SYNTHETIC DISPATCH")

    if state.finalized:

        print(
            f"{UNIT_NAME}: EXISTING FINALIZED STATE DETECTED",
            flush=True,
        )

        pass_line(
            "Previously Finalized Synthetic Dispatch Recovered"
        )

        require(
            state.dispatch_count >= 1,
            "Existing Dispatch Count Preserved",
        )

        require(
            state.receipt_count >= 1,
            "Existing Receipt Count Preserved",
        )

        require(
            bool(state.last_receipt_id),
            "Existing Receipt ID Preserved",
        )

        return None

    receipt = synthetic_dispatch(
        intent,
        authorization,
        state,
    )

    require(
        receipt.synthetic is True,
        "Receipt Marked Synthetic",
    )

    require(
        receipt.transmitted is False,
        "Receipt Confirms No Transmission",
    )

    require(
        receipt.intent_id == intent.intent_id,
        "Receipt Intent Binding Matches",
    )

    require(
        receipt.authorization_id
        == authorization.authorization_id,
        "Receipt Authorization Binding Matches",
    )

    require(
        receipt.payload_hash
        == authorization.payload_hash,
        "Receipt Payload Hash Matches",
    )

    require(
        state.dispatch_count == 1,
        "Exactly One Synthetic Dispatch Recorded",
    )

    require(
        state.receipt_count == 1,
        "Exactly One Synthetic Receipt Recorded",
    )

    require(
        state.finalized is True,
        "Synthetic Dispatch Finalized",
    )

    return receipt


def test_7_restart_recovery() -> RuntimeState:
    banner(f"{UNIT_NAME} TEST 7: DURABLE RESTART RECOVERY")

    recovered = load_state()

    require(
        recovered.finalized is True,
        "Finalized State Restored",
    )

    require(
        recovered.dispatch_count >= 1,
        "Dispatch Count Restored",
    )

    require(
        recovered.receipt_count >= 1,
        "Receipt Count Restored",
    )

    require(
        bool(recovered.last_receipt_id),
        "Receipt Identity Restored",
    )

    require(
        recovered.generation == GENERATION,
        "Recovered Generation Matches",
    )

    require(
        recovered.recovery_epoch == RECOVERY_EPOCH,
        "Recovered Recovery Epoch Matches",
    )

    return recovered


def test_8_replay_rejection(
    state: RuntimeState,
) -> None:

    banner(f"{UNIT_NAME} TEST 8: FINALIZED REPLAY REJECTION")

    intent = build_intent()

    authorization = build_authorization(intent)

    blocked = False

    try:
        synthetic_dispatch(
            intent,
            authorization,
            state,
        )

    except ReplayBlocked:
        blocked = True

        print(
            f"{UNIT_NAME} LOCAL BLOCK: finalized dispatch replay rejected",
            flush=True,
        )

    require(
        blocked,
        "Finalized Synthetic Replay Rejected",
    )

    recovered = load_state()

    require(
        recovered.dispatch_count == state.dispatch_count,
        "Replay Did Not Create Second Dispatch",
    )

    require(
        recovered.receipt_count == state.receipt_count,
        "Replay Did Not Create Second Receipt",
    )

    require(
        recovered.replay_blocks >= 1,
        "Replay Block Counter Recorded",
    )


def test_9_atomic_persistence() -> None:
    banner(f"{UNIT_NAME} TEST 9: ATOMIC STATE PERSISTENCE")

    require(
        STATE_FILE.exists(),
        "Durable State File Exists",
    )

    recovered = load_state()

    require(
        recovered.unit == UNIT_NAME,
        "Persisted Unit Identity Matches",
    )

    require(
        recovered.synthetic_only is True,
        "Persisted Synthetic Safety Preserved",
    )

    require(
        recovered.network_writes is False,
        "Persisted Network Write Lock Preserved",
    )

    require(
        recovered.leverage_mutation is False,
        "Persisted Leverage Mutation Lock Preserved",
    )


def test_10_final_safety_assertion() -> None:
    banner(f"{UNIT_NAME} TEST 10: FINAL EXECUTION FIREBREAK")

    require(
        LIVE_ORDER_EXECUTION is False,
        "Real Execution Remains Disabled",
    )

    require(
        DEMO_ORDER_EXECUTION is False,
        "Demo Execution Remains Disabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "Network Writes Remain Disabled",
    )

    require(
        LEVERAGE_MUTATION_ENABLED is False,
        "Leverage Mutation Remains Disabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic-Only Boundary Remains Active",
    )


# =============================================================================
# VALIDATION RUNNER
# =============================================================================


def run_validation() -> RuntimeState:

    banner(f"{UNIT_NAME}: STARTING VALIDATION")

    state = load_state()

    test_1_safety_configuration()

    test_2_runtime_state(state)

    test_3_write_firebreak()

    test_4_mutation_firebreaks()

    intent, authorization = test_5_synthetic_intent(
        state
    )

    test_6_synthetic_dispatch(
        state,
        intent,
        authorization,
    )

    recovered = test_7_restart_recovery()

    test_8_replay_rejection(
        recovered
    )

    test_9_atomic_persistence()

    test_10_final_safety_assertion()

    banner(f"{UNIT_NAME}: VALIDATION SUMMARY")

    print(
        f"{UNIT_NAME}: synthetic-only="
        f"{SYNTHETIC_TRANSPORT_ONLY}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: network-writes="
        f"{NETWORK_WRITES_ENABLED}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: leverage-mutation="
        f"{LEVERAGE_MUTATION_ENABLED}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: generation="
        f"{recovered.generation}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: recovery-epoch="
        f"{recovered.recovery_epoch}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: dispatch-count="
        f"{recovered.dispatch_count}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: receipt-count="
        f"{recovered.receipt_count}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: replay-blocks="
        f"{recovered.replay_blocks}",
        flush=True,
    )

    banner(f"{UNIT_NAME}: ALL TESTS PASSED")

    return load_state()


# =============================================================================
# PERSISTENT HEARTBEAT
# =============================================================================


def heartbeat_loop() -> None:

    heartbeat = 0

    while True:

        heartbeat += 1

        try:
            state = load_state()

            generation = state.generation
            recovery_epoch = state.recovery_epoch

        except Exception:
            generation = GENERATION
            recovery_epoch = RECOVERY_EPOCH

        print(
            f"{UNIT_NAME}: HEARTBEAT {heartbeat} | "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes={NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"generation={generation} | "
            f"recovery-epoch={recovery_epoch}",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_INTERVAL_SECONDS
        )


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:

    print(
        "R29 UNIT F: ALL DEFINITIONS LOADED",
        flush=True,
    )

    start_health_server()

    run_validation()

    banner(
        "R29 UNIT F: ENTERING PERSISTENT "
        "SYNTHETIC-ONLY RUNTIME"
    )

    heartbeat_loop()


if __name__ == "__main__":
    main()
