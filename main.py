# ============================================================
# 0F-4H-R28-UNIT-H
# END-TO-END INTEGRATION / RECOVERY / PERSISTENCE VALIDATION
#
# STANDALONE TEST UNIT
# NO EXCHANGE CONNECTION
# NO REAL ORDER TRANSMISSION
# NO DEMO ORDER TRANSMISSION
# NO NETWORK ACCESS
# ============================================================

print(
    "R28 UNIT H: MAIN.PY ENTERED",
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
import time
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Dict, Optional, Set


print(
    "R28 UNIT H: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-H"
MODULE_VERSION = "R28-H"


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
# TEST CONFIGURATION
# ============================================================

SIGNAL_EXPIRY_SECONDS = 120
MAX_LEVERAGE = 100

TEST_SYMBOL = "BTCUSDT"
TEST_SIDE = "BUY"
TEST_POSITION_SIDE = "LONG"

TEST_QUANTITY = Decimal("0.0001")
TEST_LEVERAGE = 100

STATE_FILE = "/tmp/r28_unit_h_state.json"

HEARTBEAT_INTERVAL_SECONDS = 5


# ============================================================
# GLOBAL RUNTIME STATE
# ============================================================

shutdown_event = asyncio.Event()

processed_signal_ids: Set[str] = set()
processed_intent_ids: Set[str] = set()
shadow_commit_ids: Set[str] = set()

intent_states: Dict[str, str] = {}

heartbeat_counter = 0


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class Signal:
    signal_id: str
    symbol: str
    side: str
    position_side: str
    quantity: str
    leverage: int
    created_at: int


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
class ExecutionPayload:
    intent_id: str
    symbol: str
    side: str
    position_side: str
    quantity: str
    leverage: int
    client_order_id: str


@dataclass(frozen=True)
class ShadowCommit:
    commit_id: str
    intent_id: str
    payload_hash: str
    created_at: int


# ============================================================
# DETERMINISTIC SERIALIZATION
# ============================================================

def canonical_json(data) -> str:

    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


# ============================================================
# SIGNAL VALIDATION
# ============================================================

def validate_signal(signal: Signal) -> None:

    if not signal.signal_id.strip():

        raise ValueError(
            "signal_id cannot be empty"
        )

    if not signal.symbol.strip():

        raise ValueError(
            "symbol cannot be empty"
        )

    if signal.side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            "invalid signal side"
        )

    if signal.position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "invalid position side"
        )

    quantity = Decimal(
        signal.quantity
    )

    if quantity <= 0:

        raise ValueError(
            "quantity must be positive"
        )

    if signal.leverage <= 0:

        raise ValueError(
            "leverage must be positive"
        )

    if signal.leverage > MAX_LEVERAGE:

        raise ValueError(
            "leverage exceeds local safety cap"
        )

    signal_age = (
        int(time.time())
        - signal.created_at
    )

    if signal_age > SIGNAL_EXPIRY_SECONDS:

        raise ValueError(
            "signal expired"
        )


# ============================================================
# SIGNAL REGISTRATION
# ============================================================

def register_signal(signal: Signal) -> None:

    validate_signal(
        signal
    )

    if signal.signal_id in processed_signal_ids:

        raise ValueError(
            "duplicate signal replay rejected"
        )

    processed_signal_ids.add(
        signal.signal_id
    )


# ============================================================
# EXECUTION INTENT CREATION
# ============================================================

def build_execution_intent(
    signal: Signal,
) -> ExecutionIntent:

    intent_source = canonical_json(
        {
            "signal_id": signal.signal_id,
            "symbol": signal.symbol,
            "side": signal.side,
            "position_side": signal.position_side,
            "quantity": signal.quantity,
            "leverage": signal.leverage,
        }
    )

    intent_id = (
        "r28h-intent-"
        + sha256_text(
            intent_source
        )[:20]
    )

    return ExecutionIntent(
        intent_id=intent_id,
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        side=signal.side,
        position_side=signal.position_side,
        quantity=signal.quantity,
        leverage=signal.leverage,
    )


# ============================================================
# INTENT REGISTRATION
# ============================================================

def register_intent(
    intent: ExecutionIntent,
) -> None:

    if intent.intent_id in processed_intent_ids:

        raise ValueError(
            "duplicate intent replay rejected"
        )

    processed_intent_ids.add(
        intent.intent_id
    )

    intent_states[
        intent.intent_id
    ] = "NEW"


# ============================================================
# PAYLOAD GENERATION
# ============================================================

def build_execution_payload(
    intent: ExecutionIntent,
) -> ExecutionPayload:

    client_order_source = canonical_json(
        {
            "intent_id": intent.intent_id,
            "symbol": intent.symbol,
            "side": intent.side,
            "position_side": intent.position_side,
        }
    )

    client_order_id = (
        "r28h-"
        + sha256_text(
            client_order_source
        )[:20]
    )

    return ExecutionPayload(
        intent_id=intent.intent_id,
        symbol=intent.symbol,
        side=intent.side,
        position_side=intent.position_side,
        quantity=intent.quantity,
        leverage=intent.leverage,
        client_order_id=client_order_id,
    )


# ============================================================
# PAYLOAD VALIDATION
# ============================================================

def validate_payload_binding(
    intent: ExecutionIntent,
    payload: ExecutionPayload,
) -> None:

    if payload.intent_id != intent.intent_id:

        raise ValueError(
            "payload intent mismatch"
        )

    if payload.symbol != intent.symbol:

        raise ValueError(
            "payload symbol mismatch"
        )

    if payload.side != intent.side:

        raise ValueError(
            "payload side mismatch"
        )

    if payload.position_side != intent.position_side:

        raise ValueError(
            "payload position side mismatch"
        )

    if payload.quantity != intent.quantity:

        raise ValueError(
            "payload quantity mismatch"
        )

    if payload.leverage != intent.leverage:

        raise ValueError(
            "payload leverage mismatch"
        )


# ============================================================
# SHADOW COMMIT
# ============================================================

def build_shadow_commit(
    payload: ExecutionPayload,
) -> ShadowCommit:

    payload_json = canonical_json(
        asdict(
            payload
        )
    )

    payload_hash = sha256_text(
        payload_json
    )

    commit_id = (
        "r28h-shadow-"
        + sha256_text(
            payload.intent_id
            + payload_hash
        )[:20]
    )

    return ShadowCommit(
        commit_id=commit_id,
        intent_id=payload.intent_id,
        payload_hash=payload_hash,
        created_at=int(time.time()),
    )


def register_shadow_commit(
    commit: ShadowCommit,
) -> None:

    if commit.commit_id in shadow_commit_ids:

        raise ValueError(
            "duplicate shadow commit rejected"
        )

    shadow_commit_ids.add(
        commit.commit_id
    )


# ============================================================
# SHADOW BINDING VALIDATION
# ============================================================

def validate_shadow_binding(
    payload: ExecutionPayload,
    commit: ShadowCommit,
) -> None:

    payload_hash = sha256_text(
        canonical_json(
            asdict(
                payload
            )
        )
    )

    if commit.intent_id != payload.intent_id:

        raise ValueError(
            "shadow intent mismatch"
        )

    if commit.payload_hash != payload_hash:

        raise ValueError(
            "shadow payload hash mismatch"
        )


# ============================================================
# STATE MACHINE
# ============================================================

ALLOWED_TRANSITIONS = {

    "NEW": {
        "VALIDATED",
    },

    "VALIDATED": {
        "SHADOW_COMMITTED",
    },

    "SHADOW_COMMITTED": {
        "RECONCILED",
    },

    "RECONCILED": set(),
}


def transition_intent(
    intent_id: str,
    new_state: str,
) -> None:

    if intent_id not in intent_states:

        raise ValueError(
            "unknown intent"
        )

    current_state = intent_states[
        intent_id
    ]

    allowed = ALLOWED_TRANSITIONS.get(
        current_state,
        set(),
    )

    if new_state not in allowed:

        raise ValueError(
            "invalid state transition: "
            f"{current_state} -> {new_state}"
        )

    intent_states[
        intent_id
    ] = new_state


# ============================================================
# PERSISTENCE
# ============================================================

def build_snapshot() -> dict:

    return {

        "module": MODULE_NAME,

        "version": MODULE_VERSION,

        "processed_signal_ids": sorted(
            processed_signal_ids
        ),

        "processed_intent_ids": sorted(
            processed_intent_ids
        ),

        "shadow_commit_ids": sorted(
            shadow_commit_ids
        ),

        "intent_states": dict(
            sorted(
                intent_states.items()
            )
        ),
    }


def snapshot_fingerprint(
    snapshot: dict,
) -> str:

    return sha256_text(
        canonical_json(
            snapshot
        )
    )


def save_state() -> str:

    snapshot = build_snapshot()

    envelope = {

        "snapshot": snapshot,

        "fingerprint": snapshot_fingerprint(
            snapshot
        ),
    }

    temporary_file = (
        STATE_FILE
        + ".tmp"
    )

    with open(
        temporary_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            envelope,
            file,
            sort_keys=True,
            separators=(",", ":"),
        )

        file.flush()

        os.fsync(
            file.fileno()
        )

    os.replace(
        temporary_file,
        STATE_FILE,
    )

    return envelope[
        "fingerprint"
    ]


def load_state() -> str:

    global processed_signal_ids
    global processed_intent_ids
    global shadow_commit_ids
    global intent_states

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        envelope = json.load(
            file
        )

    snapshot = envelope.get(
        "snapshot"
    )

    fingerprint = envelope.get(
        "fingerprint"
    )

    if not isinstance(
        snapshot,
        dict,
    ):

        raise ValueError(
            "invalid persisted snapshot"
        )

    expected_fingerprint = snapshot_fingerprint(
        snapshot
    )

    if fingerprint != expected_fingerprint:

        raise ValueError(
            "persisted state integrity failure"
        )

    processed_signal_ids = set(
        snapshot[
            "processed_signal_ids"
        ]
    )

    processed_intent_ids = set(
        snapshot[
            "processed_intent_ids"
        ]
    )

    shadow_commit_ids = set(
        snapshot[
            "shadow_commit_ids"
        ]
    )

    intent_states = dict(
        snapshot[
            "intent_states"
        ]
    )

    return fingerprint


# ============================================================
# CLEAR MEMORY ONLY
# ============================================================

def clear_runtime_memory() -> None:

    processed_signal_ids.clear()

    processed_intent_ids.clear()

    shadow_commit_ids.clear()

    intent_states.clear()


# ============================================================
# ABSOLUTE ORDER TRANSMISSION LOCKS
# ============================================================

async def real_order_post(*args, **kwargs):

    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise RuntimeError(
        "ABSOLUTE SAFETY LOCK: "
        "REAL ORDER TRANSMISSION DISABLED"
    )


async def demo_order_post(*args, **kwargs):

    global DEMO_POST_CALLED

    DEMO_POST_CALLED = True

    raise RuntimeError(
        "ABSOLUTE SAFETY LOCK: "
        "DEMO ORDER TRANSMISSION DISABLED"
    )


async def network_request(*args, **kwargs):

    global NETWORK_CALLED

    NETWORK_CALLED = True

    raise RuntimeError(
        "ABSOLUTE SAFETY LOCK: "
        "NETWORK ACCESS DISABLED"
    )


# ============================================================
# TEST HELPERS
# ============================================================

def pass_fail(
    condition: bool,
) -> str:

    if condition:

        return "✅ PASS"

    return "❌ FAIL"


def print_gate(
    name: str,
    condition: bool,
) -> None:

    print(
        f"{name:<44} "
        f"{pass_fail(condition)}",
        flush=True,
    )


def expect_failure(
    function,
    *args,
    **kwargs,
) -> bool:

    try:

        function(
            *args,
            **kwargs,
        )

    except Exception:

        return True

    return False


# ============================================================
# UNIT H DIAGNOSTIC
# ============================================================

def run_unit_h_diagnostic() -> None:

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "END-TO-END INTEGRATION + RESTART VALIDATION",
        flush=True,
    )

    print(
        "SIGNAL -> INTENT -> PAYLOAD -> SHADOW -> STATE -> DISK",
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

    # --------------------------------------------------------
    # CLEAN START
    # --------------------------------------------------------

    clear_runtime_memory()

    try:

        os.remove(
            STATE_FILE
        )

    except FileNotFoundError:

        pass

    # --------------------------------------------------------
    # CREATE SIGNAL
    # --------------------------------------------------------

    signal_object = Signal(

        signal_id="R28-H-SIGNAL-001",

        symbol=TEST_SYMBOL,

        side=TEST_SIDE,

        position_side=TEST_POSITION_SIDE,

        quantity=str(
            TEST_QUANTITY
        ),

        leverage=TEST_LEVERAGE,

        created_at=int(
            time.time()
        ),
    )

    signal_valid = True

    try:

        validate_signal(
            signal_object
        )

    except Exception:

        signal_valid = False

    # --------------------------------------------------------
    # REGISTER SIGNAL
    # --------------------------------------------------------

    register_signal(
        signal_object
    )

    signal_registered = (
        signal_object.signal_id
        in processed_signal_ids
    )

    # --------------------------------------------------------
    # INTENT
    # --------------------------------------------------------

    intent = build_execution_intent(
        signal_object
    )

    register_intent(
        intent
    )

    intent_created = (
        intent.intent_id
        in processed_intent_ids
    )

    deterministic_intent = (

        build_execution_intent(
            signal_object
        ).intent_id

        ==

        intent.intent_id
    )

    # --------------------------------------------------------
    # PAYLOAD
    # --------------------------------------------------------

    payload = build_execution_payload(
        intent
    )

    payload_valid = True

    try:

        validate_payload_binding(
            intent,
            payload,
        )

    except Exception:

        payload_valid = False

    deterministic_payload = (

        build_execution_payload(
            intent
        )

        ==

        payload
    )

    # --------------------------------------------------------
    # STATE NEW -> VALIDATED
    # --------------------------------------------------------

    transition_intent(
        intent.intent_id,
        "VALIDATED",
    )

    validated_state = (
        intent_states[
            intent.intent_id
        ]
        == "VALIDATED"
    )

    # --------------------------------------------------------
    # SHADOW COMMIT
    # --------------------------------------------------------

    shadow = build_shadow_commit(
        payload
    )

    shadow_binding_valid = True

    try:

        validate_shadow_binding(
            payload,
            shadow,
        )

    except Exception:

        shadow_binding_valid = False

    register_shadow_commit(
        shadow
    )

    shadow_registered = (
        shadow.commit_id
        in shadow_commit_ids
    )

    transition_intent(
        intent.intent_id,
        "SHADOW_COMMITTED",
    )

    shadow_state_valid = (
        intent_states[
            intent.intent_id
        ]
        == "SHADOW_COMMITTED"
    )

    # --------------------------------------------------------
    # RECONCILE
    # --------------------------------------------------------

    transition_intent(
        intent.intent_id,
        "RECONCILED",
    )

    reconciled = (
        intent_states[
            intent.intent_id
        ]
        == "RECONCILED"
    )

    # --------------------------------------------------------
    # REPLAY TESTS BEFORE RESTART
    # --------------------------------------------------------

    duplicate_signal_rejected = expect_failure(
        register_signal,
        signal_object,
    )

    duplicate_intent_rejected = expect_failure(
        register_intent,
        intent,
    )

    duplicate_shadow_rejected = expect_failure(
        register_shadow_commit,
        shadow,
    )

    terminal_state_locked = expect_failure(
        transition_intent,
        intent.intent_id,
        "VALIDATED",
    )

    # --------------------------------------------------------
    # SNAPSHOT DETERMINISM
    # --------------------------------------------------------

    snapshot_one = build_snapshot()

    snapshot_two = build_snapshot()

    deterministic_snapshot = (
        canonical_json(
            snapshot_one
        )
        ==
        canonical_json(
            snapshot_two
        )
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    saved_fingerprint = save_state()

    persistence_file_created = os.path.exists(
        STATE_FILE
    )

    # --------------------------------------------------------
    # SIMULATED PROCESS MEMORY LOSS
    # --------------------------------------------------------

    clear_runtime_memory()

    memory_cleared = (

        len(processed_signal_ids) == 0

        and

        len(processed_intent_ids) == 0

        and

        len(shadow_commit_ids) == 0

        and

        len(intent_states) == 0
    )

    # --------------------------------------------------------
    # RESTORE
    # --------------------------------------------------------

    restored_fingerprint = load_state()

    restart_state_restored = (

        signal_object.signal_id
        in processed_signal_ids

        and

        intent.intent_id
        in processed_intent_ids

        and

        shadow.commit_id
        in shadow_commit_ids

        and

        intent_states.get(
            intent.intent_id
        )
        == "RECONCILED"
    )

    deterministic_restore = (
        restored_fingerprint
        ==
        saved_fingerprint
    )

    # --------------------------------------------------------
    # REPLAY AFTER RESTART
    # --------------------------------------------------------

    replay_signal_after_restart = expect_failure(
        register_signal,
        signal_object,
    )

    replay_intent_after_restart = expect_failure(
        register_intent,
        intent,
    )

    replay_shadow_after_restart = expect_failure(
        register_shadow_commit,
        shadow,
    )

    replay_terminal_after_restart = expect_failure(
        transition_intent,
        intent.intent_id,
        "SHADOW_COMMITTED",
    )

    # --------------------------------------------------------
    # PAYLOAD TAMPERING
    # --------------------------------------------------------

    tampered_payload = ExecutionPayload(

        intent_id=payload.intent_id,

        symbol=payload.symbol,

        side="SELL",

        position_side=payload.position_side,

        quantity=payload.quantity,

        leverage=payload.leverage,

        client_order_id=payload.client_order_id,
    )

    tampered_payload_rejected = expect_failure(
        validate_payload_binding,
        intent,
        tampered_payload,
    )

    tampered_shadow_rejected = expect_failure(
        validate_shadow_binding,
        tampered_payload,
        shadow,
    )

    # --------------------------------------------------------
    # PERSISTED FILE CORRUPTION TEST
    # --------------------------------------------------------

    original_file_text = None

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        original_file_text = file.read()

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        corrupted = json.loads(
            original_file_text
        )

        corrupted[
            "snapshot"
        ][
            "intent_states"
        ][
            intent.intent_id
        ] = "INVALID_STATE"

        json.dump(
            corrupted,
            file,
            sort_keys=True,
            separators=(",", ":"),
        )

    corrupted_snapshot_rejected = expect_failure(
        load_state
    )

    # restore correct state file

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            original_file_text
        )

    load_state()

    # --------------------------------------------------------
    # SAFETY LOCKS
    # --------------------------------------------------------

    execution_locks_active = (

        LIVE_ORDER_EXECUTION is False

        and

        DEMO_ORDER_EXECUTION is False

        and

        NETWORK_ACCESS_ENABLED is False

        and

        HARD_REAL_POST_LOCK is True

        and

        HARD_DEMO_POST_LOCK is True
    )

    no_transmission_occurred = (

        REAL_POST_CALLED is False

        and

        DEMO_POST_CALLED is False

        and

        NETWORK_CALLED is False
    )

    # ========================================================
    # RESULTS
    # ========================================================

    results = {

        "Signal Validation":
            signal_valid,

        "Signal Registered":
            signal_registered,

        "Execution Intent Created":
            intent_created,

        "Deterministic Intent":
            deterministic_intent,

        "Payload Binding Valid":
            payload_valid,

        "Deterministic Payload":
            deterministic_payload,

        "Validated State Reached":
            validated_state,

        "Shadow Binding Valid":
            shadow_binding_valid,

        "Shadow Commit Registered":
            shadow_registered,

        "Shadow State Reached":
            shadow_state_valid,

        "Intent Reconciled":
            reconciled,

        "Duplicate Signal Rejected":
            duplicate_signal_rejected,

        "Duplicate Intent Rejected":
            duplicate_intent_rejected,

        "Duplicate Shadow Rejected":
            duplicate_shadow_rejected,

        "Terminal State Locked":
            terminal_state_locked,

        "Deterministic Snapshot":
            deterministic_snapshot,

        "Persistence File Created":
            persistence_file_created,

        "Runtime Memory Cleared":
            memory_cleared,

        "Restart State Restored":
            restart_state_restored,

        "Deterministic Restore":
            deterministic_restore,

        "Signal Replay After Restart Rejected":
            replay_signal_after_restart,

        "Intent Replay After Restart Rejected":
            replay_intent_after_restart,

        "Shadow Replay After Restart Rejected":
            replay_shadow_after_restart,

        "Terminal Replay After Restart Rejected":
            replay_terminal_after_restart,

        "Tampered Payload Rejected":
            tampered_payload_rejected,

        "Tampered Shadow Rejected":
            tampered_shadow_rejected,

        "Corrupted Snapshot Rejected":
            corrupted_snapshot_rejected,

        "Execution Locks Active":
            execution_locks_active,

        "No Transmission Occurred":
            no_transmission_occurred,
    }

    print(
        "R28 UNIT H END-TO-END GATES",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    for gate_name, gate_result in results.items():

        print_gate(
            gate_name,
            gate_result,
        )

    print(
        "-" * 60,
        flush=True,
    )

    diagnostic_passed = all(
        results.values()
    )

    if not diagnostic_passed:

        print(
            "❌ R28 UNIT H DIAGNOSTIC FAILED",
            flush=True,
        )

        raise RuntimeError(
            "R28 UNIT H validation failure"
        )

    print(
        "✅ R28 UNIT H DIAGNOSTIC PASSED",
        flush=True,
    )

    print(
        "✅ END-TO-END EXECUTION CHAIN VALIDATED",
        flush=True,
    )

    print(
        "✅ SIGNAL / INTENT / PAYLOAD BINDING VALIDATED",
        flush=True,
    )

    print(
        "✅ SHADOW COMMIT CHAIN VALIDATED",
        flush=True,
    )

    print(
        "✅ RESTART RECOVERY VALIDATED",
        flush=True,
    )

    print(
        "✅ REPLAY PROTECTION AFTER RESTART VALIDATED",
        flush=True,
    )

    print(
        "✅ PERSISTENCE INTEGRITY VALIDATED",
        flush=True,
    )

    print(
        "✅ UNIT H READY FOR A-G INTEGRATION",
        flush=True,
    )

    print(
        "🛡 REAL ORDER TRANSMISSION IMPOSSIBLE",
        flush=True,
    )

    print(
        "🛡 DEMO ORDER TRANSMISSION IMPOSSIBLE",
        flush=True,
    )

    print(
        "🛡 NETWORK ACCESS DISABLED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )


# ============================================================
# HEARTBEAT
# ============================================================

async def heartbeat_loop():

    global heartbeat_counter

    while not shutdown_event.is_set():

        heartbeat_counter += 1

        print(
            "R28 UNIT H: "
            f"HEARTBEAT {heartbeat_counter} "
            "✅ ACTIVE",
            flush=True,
        )

        try:

            await asyncio.wait_for(
                shutdown_event.wait(),
                timeout=HEARTBEAT_INTERVAL_SECONDS,
            )

        except asyncio.TimeoutError:

            pass


# ============================================================
# SHUTDOWN HANDLING
# ============================================================

def request_shutdown():

    if not shutdown_event.is_set():

        print(
            "R28 UNIT H: "
            "SHUTDOWN REQUESTED",
            flush=True,
        )

        shutdown_event.set()


def install_signal_handlers(
    loop,
):

    for signal_name in (
        signal.SIGTERM,
        signal.SIGINT,
    ):

        try:

            loop.add_signal_handler(
                signal_name,
                request_shutdown,
            )

        except (
            NotImplementedError,
            RuntimeError,
        ):

            pass


# ============================================================
# ASYNC MAIN
# ============================================================

async def main():

    print(
        "R28 UNIT H: "
        "RUNTIME STARTING",
        flush=True,
    )

    run_unit_h_diagnostic()

    loop = asyncio.get_running_loop()

    install_signal_handlers(
        loop
    )

    print(
        "R28 UNIT H: "
        "PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT H: "
        "WAITING WITH SAFETY LOCKS ACTIVE",
        flush=True,
    )

    await heartbeat_loop()

    print(
        "R28 UNIT H: "
        "RUNTIME STOPPED CLEANLY",
        flush=True,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "R28 UNIT H: "
            "KEYBOARD INTERRUPT",
            flush=True,
        )

    except Exception as exc:

        print(
            "❌ R28 UNIT H FATAL ERROR:",
            type(exc).__name__,
            str(exc),
            flush=True,
        )

        raise
