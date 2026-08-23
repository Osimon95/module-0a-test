# ============================================================
# 0F-4H-R28-UNIT-G
# STARTUP / RUNTIME / PERSISTENCE VALIDATION
#
# STANDALONE TEST UNIT
# NO EXCHANGE CONNECTION
# NO REAL ORDER TRANSMISSION
# NO DEMO ORDER TRANSMISSION
# ============================================================

print(
    "R28 UNIT G: MAIN.PY ENTERED",
    flush=True,
)

# ============================================================
# IMPORTS
# ============================================================

import asyncio
import hashlib
import json
import os
import signal
import sys
import time
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Dict, Optional, Set

print(
    "R28 UNIT G: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-G"
MODULE_VERSION = "R28-G"

print(
    "R28 UNIT G: CONSTANTS INITIALIZING",
    flush=True,
)


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_ACCESS_ENABLED = False

HARD_REAL_POST_LOCK = True
HARD_DEMO_POST_LOCK = True

REAL_POST_CALLED = False
DEMO_POST_CALLED = False
NETWORK_CALLED = False


# ============================================================
# RUNTIME CONFIGURATION
# ============================================================

RUNTIME_HEARTBEAT_SECONDS = 60

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# EXECUTION STATES
# ============================================================

STATE_NEW = "NEW"
STATE_VALIDATED = "VALIDATED"
STATE_SHADOW_COMMITTED = "SHADOW_COMMITTED"
STATE_RECONCILED = "RECONCILED"

TERMINAL_STATES = {
    "FILLED",
    "CANCELED",
    "REJECTED",
    "EXPIRED",
}


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass(frozen=True)
class Signal:
    signal_id: str
    symbol: str
    direction: str
    created_ms: int


@dataclass(frozen=True)
class ExecutionIntent:
    intent_id: str
    signal_id: str
    symbol: str
    side: str
    position_side: str
    quantity: str
    leverage: int


@dataclass(frozen=True)
class ShadowCommit:
    commit_id: str
    intent_id: str
    payload_hash: str
    created_ms: int


# ============================================================
# DETERMINISTIC HELPERS
# ============================================================

def stable_json(
    value,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8",
        )
    ).hexdigest()


# ============================================================
# SIGNAL VALIDATION
# ============================================================

def validate_signal(
    signal_obj: Signal,
) -> bool:

    if not signal_obj.signal_id.strip():
        raise ValueError(
            "signal_id cannot be empty"
        )

    if not signal_obj.symbol.strip():
        raise ValueError(
            "symbol cannot be empty"
        )

    if signal_obj.direction not in {
        "LONG",
        "SHORT",
    }:
        raise ValueError(
            "invalid signal direction"
        )

    if signal_obj.created_ms <= 0:
        raise ValueError(
            "invalid signal timestamp"
        )

    return True


# ============================================================
# EXECUTION INTENT CREATION
# ============================================================

def build_execution_intent(
    signal_obj: Signal,
    quantity: Decimal,
    leverage: int,
) -> ExecutionIntent:

    validate_signal(
        signal_obj,
    )

    if quantity <= Decimal("0"):
        raise ValueError(
            "quantity must be positive"
        )

    if leverage <= 0:
        raise ValueError(
            "leverage must be positive"
        )

    if leverage > 100:
        raise ValueError(
            "leverage exceeds local safety limit"
        )

    if signal_obj.direction == "LONG":

        side = "BUY"
        position_side = "LONG"

    else:

        side = "SELL"
        position_side = "SHORT"

    fingerprint_source = stable_json(
        {
            "signal_id": signal_obj.signal_id,
            "symbol": signal_obj.symbol,
            "side": side,
            "position_side": position_side,
            "quantity": str(
                quantity
            ),
            "leverage": leverage,
        }
    )

    intent_id = (
        "r28g-"
        + sha256_text(
            fingerprint_source
        )[:20]
    )

    return ExecutionIntent(
        intent_id=intent_id,
        signal_id=signal_obj.signal_id,
        symbol=signal_obj.symbol,
        side=side,
        position_side=position_side,
        quantity=str(
            quantity
        ),
        leverage=leverage,
    )


# ============================================================
# PAYLOAD CREATION
# ============================================================

def build_payload(
    intent: ExecutionIntent,
) -> Dict[str, str]:

    return {
        "symbol": intent.symbol,
        "side": intent.side,
        "positionSide": intent.position_side,
        "quantity": intent.quantity,
        "leverage": str(
            intent.leverage
        ),
        "clientOrderId": intent.intent_id,
    }


# ============================================================
# SHADOW COMMIT
# ============================================================

def create_shadow_commit(
    intent: ExecutionIntent,
    payload: Dict[str, str],
    created_ms: int,
) -> ShadowCommit:

    payload_hash = sha256_text(
        stable_json(
            payload
        )
    )

    commit_source = stable_json(
        {
            "intent_id": intent.intent_id,
            "payload_hash": payload_hash,
        }
    )

    commit_id = (
        "shadow-"
        + sha256_text(
            commit_source
        )[:20]
    )

    return ShadowCommit(
        commit_id=commit_id,
        intent_id=intent.intent_id,
        payload_hash=payload_hash,
        created_ms=created_ms,
    )


# ============================================================
# SHADOW VALIDATION
# ============================================================

def validate_shadow_commit(
    intent: ExecutionIntent,
    payload: Dict[str, str],
    commit: ShadowCommit,
) -> bool:

    expected_payload_hash = sha256_text(
        stable_json(
            payload
        )
    )

    if commit.intent_id != intent.intent_id:
        raise ValueError(
            "shadow intent mismatch"
        )

    if commit.payload_hash != expected_payload_hash:
        raise ValueError(
            "shadow payload mismatch"
        )

    return True


# ============================================================
# REPLAY PROTECTION
# ============================================================

class ReplayGuard:

    def __init__(
        self,
    ):

        self.signal_ids: Set[str] = set()
        self.intent_ids: Set[str] = set()
        self.commit_ids: Set[str] = set()

    def register_signal(
        self,
        signal_id: str,
    ) -> bool:

        if signal_id in self.signal_ids:
            return False

        self.signal_ids.add(
            signal_id
        )

        return True

    def register_intent(
        self,
        intent_id: str,
    ) -> bool:

        if intent_id in self.intent_ids:
            return False

        self.intent_ids.add(
            intent_id
        )

        return True

    def register_commit(
        self,
        commit_id: str,
    ) -> bool:

        if commit_id in self.commit_ids:
            return False

        self.commit_ids.add(
            commit_id
        )

        return True


# ============================================================
# EXECUTION STATE MACHINE
# ============================================================

class ExecutionStateMachine:

    def __init__(
        self,
    ):

        self.state = STATE_NEW

    def validate(
        self,
    ):

        if self.state != STATE_NEW:
            raise RuntimeError(
                "invalid validation transition"
            )

        self.state = STATE_VALIDATED

    def shadow_commit(
        self,
    ):

        if self.state != STATE_VALIDATED:
            raise RuntimeError(
                "invalid shadow transition"
            )

        self.state = STATE_SHADOW_COMMITTED

    def reconcile(
        self,
    ):

        if self.state != STATE_SHADOW_COMMITTED:
            raise RuntimeError(
                "invalid reconcile transition"
            )

        self.state = STATE_RECONCILED


# ============================================================
# ABSOLUTE TRANSMISSION LOCKS
# ============================================================

def real_order_post(
    *args,
    **kwargs,
):

    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise RuntimeError(
        "REAL ORDER POST ABSOLUTELY DISABLED"
    )


def demo_order_post(
    *args,
    **kwargs,
):

    global DEMO_POST_CALLED

    DEMO_POST_CALLED = True

    raise RuntimeError(
        "DEMO ORDER POST DISABLED IN UNIT G"
    )


def network_request(
    *args,
    **kwargs,
):

    global NETWORK_CALLED

    NETWORK_CALLED = True

    raise RuntimeError(
        "NETWORK ACCESS DISABLED IN UNIT G"
    )


# ============================================================
# DIAGNOSTIC RESULT HELPER
# ============================================================

def print_gate(
    name: str,
    passed: bool,
):

    status = (
        "✅ PASS"
        if passed
        else
        "❌ FAIL"
    )

    print(
        f"{name:<44} {status}",
        flush=True,
    )


# ============================================================
# UNIT G DIAGNOSTIC
# ============================================================

def run_unit_g_diagnostic(
) -> bool:

    print(
        "R28 UNIT G: DIAGNOSTIC ENTERED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "STARTUP / RUNTIME / PERSISTENCE VALIDATION",
        flush=True,
    )

    print(
        "NO EXCHANGE CONNECTION",
        flush=True,
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "DEMO ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "NETWORK ACCESS DISABLED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    now_ms = int(
        time.time()
        * 1000
    )

    signal_obj = Signal(
        signal_id="r28-unit-g-signal",
        symbol="BTCUSDT",
        direction="LONG",
        created_ms=now_ms,
    )

    results: Dict[str, bool] = {}

    # --------------------------------------------------------
    # SIGNAL
    # --------------------------------------------------------

    results[
        "Signal Validation"
    ] = validate_signal(
        signal_obj
    )

    # --------------------------------------------------------
    # INTENT
    # --------------------------------------------------------

    intent_1 = build_execution_intent(
        signal_obj=signal_obj,
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    intent_2 = build_execution_intent(
        signal_obj=signal_obj,
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    results[
        "Execution Intent Generated"
    ] = bool(
        intent_1.intent_id
    )

    results[
        "Deterministic Intent"
    ] = (
        intent_1
        == intent_2
    )

    # --------------------------------------------------------
    # PAYLOAD
    # --------------------------------------------------------

    payload_1 = build_payload(
        intent_1
    )

    payload_2 = build_payload(
        intent_2
    )

    results[
        "Execution Payload Generated"
    ] = bool(
        payload_1
    )

    results[
        "Deterministic Payload"
    ] = (
        payload_1
        == payload_2
    )

    # --------------------------------------------------------
    # SHADOW COMMIT
    # --------------------------------------------------------

    shadow_1 = create_shadow_commit(
        intent=intent_1,
        payload=payload_1,
        created_ms=now_ms,
    )

    shadow_2 = create_shadow_commit(
        intent=intent_2,
        payload=payload_2,
        created_ms=now_ms,
    )

    results[
        "Shadow Commit Generated"
    ] = bool(
        shadow_1.commit_id
    )

    results[
        "Deterministic Shadow Commit"
    ] = (
        shadow_1.commit_id
        == shadow_2.commit_id
    )

    results[
        "Shadow Binding Valid"
    ] = validate_shadow_commit(
        intent=intent_1,
        payload=payload_1,
        commit=shadow_1,
    )

    # --------------------------------------------------------
    # TAMPER TEST
    # --------------------------------------------------------

    tampered_payload = dict(
        payload_1
    )

    tampered_payload[
        "quantity"
    ] = "999"

    tamper_rejected = False

    try:

        validate_shadow_commit(
            intent=intent_1,
            payload=tampered_payload,
            commit=shadow_1,
        )

    except ValueError:

        tamper_rejected = True

    results[
        "Tampered Payload Rejected"
    ] = tamper_rejected

    # --------------------------------------------------------
    # REPLAY TEST
    # --------------------------------------------------------

    replay_guard = ReplayGuard()

    first_signal = replay_guard.register_signal(
        signal_obj.signal_id
    )

    duplicate_signal = replay_guard.register_signal(
        signal_obj.signal_id
    )

    results[
        "First Signal Accepted"
    ] = first_signal

    results[
        "Duplicate Signal Rejected"
    ] = (
        not duplicate_signal
    )

    first_intent = replay_guard.register_intent(
        intent_1.intent_id
    )

    duplicate_intent = replay_guard.register_intent(
        intent_1.intent_id
    )

    results[
        "First Intent Accepted"
    ] = first_intent

    results[
        "Duplicate Intent Rejected"
    ] = (
        not duplicate_intent
    )

    first_commit = replay_guard.register_commit(
        shadow_1.commit_id
    )

    duplicate_commit = replay_guard.register_commit(
        shadow_1.commit_id
    )

    results[
        "First Shadow Commit Accepted"
    ] = first_commit

    results[
        "Duplicate Shadow Commit Rejected"
    ] = (
        not duplicate_commit
    )

    # --------------------------------------------------------
    # STATE MACHINE
    # --------------------------------------------------------

    machine = ExecutionStateMachine()

    results[
        "Initial State NEW"
    ] = (
        machine.state
        == STATE_NEW
    )

    machine.validate()

    results[
        "State VALIDATED"
    ] = (
        machine.state
        == STATE_VALIDATED
    )

    machine.shadow_commit()

    results[
        "State SHADOW_COMMITTED"
    ] = (
        machine.state
        == STATE_SHADOW_COMMITTED
    )

    machine.reconcile()

    results[
        "State RECONCILED"
    ] = (
        machine.state
        == STATE_RECONCILED
    )

    # --------------------------------------------------------
    # SAFETY FLAGS
    # --------------------------------------------------------

    results[
        "Live Execution Disabled"
    ] = (
        LIVE_ORDER_EXECUTION
        is False
    )

    results[
        "Demo Execution Disabled"
    ] = (
        DEMO_ORDER_EXECUTION
        is False
    )

    results[
        "Network Access Disabled"
    ] = (
        NETWORK_ACCESS_ENABLED
        is False
    )

    results[
        "Hard Real POST Lock Active"
    ] = (
        HARD_REAL_POST_LOCK
        is True
    )

    results[
        "Hard Demo POST Lock Active"
    ] = (
        HARD_DEMO_POST_LOCK
        is True
    )

    results[
        "Real POST Never Called"
    ] = (
        REAL_POST_CALLED
        is False
    )

    results[
        "Demo POST Never Called"
    ] = (
        DEMO_POST_CALLED
        is False
    )

    results[
        "Network Never Called"
    ] = (
        NETWORK_CALLED
        is False
    )

    # --------------------------------------------------------
    # STARTUP / RUNTIME VALIDATION
    # --------------------------------------------------------

    results[
        "Main Module Loaded"
    ] = True

    results[
        "Imports Completed"
    ] = True

    results[
        "Diagnostic Reached"
    ] = True

    results[
        "Runtime Configuration Valid"
    ] = (
        RUNTIME_HEARTBEAT_SECONDS
        > 0
    )

    results[
        "Port Configuration Valid"
    ] = (
        PORT
        > 0
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print(
        "R28 UNIT G RUNTIME GATES",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    for name, passed in results.items():

        print_gate(
            name,
            passed,
        )

    print(
        "-" * 60,
        flush=True,
    )

    all_passed = all(
        results.values()
    )

    if all_passed:

        print(
            "✅ R28 UNIT G DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ STARTUP PATH VALIDATED",
            flush=True,
        )

        print(
            "✅ RUNTIME PERSISTENCE READY",
            flush=True,
        )

        print(
            "✅ EXECUTION SAFETY LOCKS VALIDATED",
            flush=True,
        )

        print(
            "✅ UNIT G READY FOR INTEGRATION",
            flush=True,
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT G DIAGNOSTIC FAILED",
            flush=True,
        )

    print(
        "=" * 60,
        flush=True,
    )

    print(
        "R28 UNIT G: DIAGNOSTIC COMPLETE",
        flush=True,
    )

    return all_passed


# ============================================================
# MINIMAL RENDER HEALTH SERVER
# ============================================================

async def handle_health_request(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):

    try:

        await reader.read(
            4096
        )

        body = (
            "R28 UNIT G ACTIVE\n"
        )

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )

        writer.write(
            response.encode(
                "utf-8"
            )
        )

        await writer.drain()

    except Exception as exc:

        print(
            "R28 UNIT G: HEALTH REQUEST ERROR:",
            repr(exc),
            flush=True,
        )

    finally:

        try:

            writer.close()

            await writer.wait_closed()

        except Exception:

            pass


async def start_health_server(
):

    print(
        f"R28 UNIT G: STARTING HEALTH SERVER ON PORT {PORT}",
        flush=True,
    )

    server = await asyncio.start_server(
        handle_health_request,
        host="0.0.0.0",
        port=PORT,
    )

    print(
        f"R28 UNIT G: HEALTH SERVER ACTIVE ON PORT {PORT}",
        flush=True,
    )

    return server


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime(
):

    print(
        "R28 UNIT G: PERSISTENT RUNTIME ENTERED",
        flush=True,
    )

    server = await start_health_server()

    print(
        "R28 UNIT G: SERVICE WILL REMAIN ACTIVE",
        flush=True,
    )

    heartbeat_number = 0

    async with server:

        while True:

            await asyncio.sleep(
                RUNTIME_HEARTBEAT_SECONDS
            )

            heartbeat_number += 1

            print(
                "R28 UNIT G: "
                f"HEARTBEAT {heartbeat_number} "
                "✅ ACTIVE",
                flush=True,
            )


# ============================================================
# MAIN ASYNC CONTROLLER
# ============================================================

async def main(
):

    print(
        "R28 UNIT G: MAIN FUNCTION ENTERED",
        flush=True,
    )

    diagnostic_passed = (
        run_unit_g_diagnostic()
    )

    if not diagnostic_passed:

        raise RuntimeError(
            "R28 UNIT G diagnostic failed"
        )

    print(
        "R28 UNIT G: STARTING PERSISTENT SERVICE",
        flush=True,
    )

    await persistent_runtime()


# ============================================================
# PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":

    print(
        "R28 UNIT G: __MAIN__ BLOCK ENTERED",
        flush=True,
    )

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "R28 UNIT G: SHUTDOWN REQUESTED",
            flush=True,
        )

    except Exception as exc:

        print(
            "=" * 60,
            flush=True,
        )

        print(
            "❌ R28 UNIT G FATAL ERROR",
            flush=True,
        )

        print(
            type(exc).__name__
            + ": "
            + str(exc),
            flush=True,
        )

        print(
            "🛡 NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        raise
      
