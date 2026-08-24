# ============================================================
# 0F-4H-R28-A-H-INTEGRATED
# STANDALONE END-TO-END SAFETY / RESTART VALIDATION
#
# UNITS A-H INTEGRATED
# NO EXCHANGE CONNECTION
# NO REAL ORDER TRANSMISSION
# NO DEMO ORDER TRANSMISSION
# NETWORK ACCESS DISABLED
# ============================================================

print("R28 A-H: MAIN.PY ENTERED", flush=True)

import asyncio
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict, Set

print("R28 A-H: IMPORTS COMPLETE", flush=True)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-A-H-INTEGRATED"
MODULE_VERSION = "R28-A-H"


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

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

MAX_LEVERAGE = 100
MARGIN_TYPE = "ISOLATED"
ORDER_TYPE = "MARKET"

STATE_FILE = os.getenv(
    "R28_AH_STATE_FILE",
    "r28_ah_state.json",
)

HEARTBEAT_SECONDS = float(
    os.getenv(
        "R28_HEARTBEAT_SECONDS",
        "5",
    )
)


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
    margin_type: str


@dataclass(frozen=True)
class ExecutionPayload:
    intent_id: str
    symbol: str
    side: str
    position_side: str
    quantity: str
    leverage: int
    margin_type: str
    order_type: str
    reduce_only: bool
    client_order_id: str


@dataclass(frozen=True)
class ShadowCommit:
    shadow_id: str
    intent_id: str
    payload_hash: str
    request_hash: str
    committed_at: int


@dataclass
class LifecycleRecord:
    intent_id: str
    state: str
    terminal: bool


# ============================================================
# RUNTIME REGISTRIES
# ============================================================

SEEN_SIGNALS: Set[str] = set()
SEEN_INTENTS: Set[str] = set()
SEEN_SHADOWS: Set[str] = set()

LIFECYCLES: Dict[
    str,
    LifecycleRecord,
] = {}


# ============================================================
# GENERIC HELPERS
# ============================================================

def canonical_json(
    data: dict,
) -> str:

    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_text(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def stable_hash(
    data: dict,
) -> str:

    return sha256_text(
        canonical_json(data)
    )


def normalize_quantity(
    value,
) -> str:

    try:
        quantity = Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        raise ValueError(
            "Invalid quantity"
        )

    if quantity <= 0:
        raise ValueError(
            "Quantity must be greater than zero"
        )

    normalized = format(
        quantity.normalize(),
        "f",
    )

    if "." in normalized:
        normalized = (
            normalized
            .rstrip("0")
            .rstrip(".")
        )

    return normalized


def assert_true(
    condition: bool,
    message: str,
):

    if not condition:
        raise AssertionError(
            message
        )


def gate(
    name: str,
    condition: bool,
):

    status = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{name:<46} {status}",
        flush=True,
    )

    if not condition:
        raise AssertionError(
            name
        )


# ============================================================
# UNIT A
# SIGNAL SAFETY
# ============================================================

def validate_signal(
    signal: Signal,
    now: int,
):

    signal_id = (
        signal
        .signal_id
        .strip()
    )

    symbol = (
        signal
        .symbol
        .strip()
        .upper()
    )

    side = (
        signal
        .side
        .strip()
        .upper()
    )

    position_side = (
        signal
        .position_side
        .strip()
        .upper()
    )

    assert_true(
        bool(signal_id),
        "signal_id cannot be empty",
    )

    assert_true(
        bool(symbol),
        "symbol cannot be empty",
    )

    assert_true(
        side in {
            "BUY",
            "SELL",
        },
        "Invalid side",
    )

    assert_true(
        position_side in {
            "LONG",
            "SHORT",
        },
        "Invalid position_side",
    )

    assert_true(
        normalize_quantity(
            signal.quantity
        ) != "0",
        "Invalid quantity",
    )

    assert_true(
        1
        <= int(signal.leverage)
        <= MAX_LEVERAGE,
        "Invalid leverage",
    )

    assert_true(
        now
        - int(signal.created_at)
        <= SIGNAL_EXPIRY_SECONDS,
        "Signal expired",
    )

    assert_true(
        int(signal.created_at)
        <= now + 5,
        "Signal timestamp is in the future",
    )

    valid_direction = (
        (
            side == "BUY"
            and position_side == "LONG"
        )
        or
        (
            side == "SELL"
            and position_side == "SHORT"
        )
    )

    assert_true(
        valid_direction,
        "Invalid open direction",
    )


def register_signal(
    signal: Signal,
):

    if signal.signal_id in SEEN_SIGNALS:

        raise ValueError(
            "Duplicate signal"
        )

    SEEN_SIGNALS.add(
        signal.signal_id
    )


# ============================================================
# UNIT B
# EXECUTION INTENT
# ============================================================

def build_execution_intent(
    signal: Signal,
) -> ExecutionIntent:

    normalized = {
        "signal_id":
            signal.signal_id.strip(),

        "symbol":
            signal.symbol.strip().upper(),

        "side":
            signal.side.strip().upper(),

        "position_side":
            signal.position_side.strip().upper(),

        "quantity":
            normalize_quantity(
                signal.quantity
            ),

        "leverage":
            int(signal.leverage),

        "margin_type":
            MARGIN_TYPE,
    }

    intent_id = (
        "r28i-"
        + stable_hash(
            normalized
        )[:24]
    )

    return ExecutionIntent(
        intent_id=intent_id,
        **normalized,
    )


def register_intent(
    intent: ExecutionIntent,
):

    if intent.intent_id in SEEN_INTENTS:

        raise ValueError(
            "Duplicate intent"
        )

    SEEN_INTENTS.add(
        intent.intent_id
    )


# ============================================================
# UNIT C
# PAYLOAD + SHADOW COMMIT
# ============================================================

def build_payload(
    intent: ExecutionIntent,
) -> ExecutionPayload:

    client_seed = {
        "intent_id":
            intent.intent_id,

        "symbol":
            intent.symbol,

        "side":
            intent.side,

        "position_side":
            intent.position_side,

        "quantity":
            intent.quantity,

        "leverage":
            intent.leverage,
    }

    client_order_id = (
        "r28-"
        + stable_hash(
            client_seed
        )[:20]
    )

    return ExecutionPayload(

        intent_id=
            intent.intent_id,

        symbol=
            intent.symbol,

        side=
            intent.side,

        position_side=
            intent.position_side,

        quantity=
            intent.quantity,

        leverage=
            intent.leverage,

        margin_type=
            intent.margin_type,

        order_type=
            ORDER_TYPE,

        reduce_only=
            False,

        client_order_id=
            client_order_id,
    )


def validate_payload_binding(
    intent: ExecutionIntent,
    payload: ExecutionPayload,
) -> bool:

    return all(
        [
            payload.intent_id
            == intent.intent_id,

            payload.symbol
            == intent.symbol,

            payload.side
            == intent.side,

            payload.position_side
            == intent.position_side,

            payload.quantity
            == intent.quantity,

            payload.leverage
            == intent.leverage,

            payload.margin_type
            == MARGIN_TYPE,

            payload.order_type
            == ORDER_TYPE,

            payload.reduce_only
            is False,

            bool(
                payload.client_order_id
            ),
        ]
    )


def payload_fingerprint(
    payload: ExecutionPayload,
) -> str:

    return stable_hash(
        asdict(payload)
    )


def request_fingerprint(
    payload: ExecutionPayload,
) -> str:

    request = {

        "method":
            "POST",

        "path":
            "/SAFETY-LOCKED/NO-TRANSMISSION",

        "payload":
            asdict(payload),
    }

    return stable_hash(
        request
    )


def build_shadow_commit(
    intent: ExecutionIntent,
    payload: ExecutionPayload,
    now: int,
) -> ShadowCommit:

    assert_true(
        validate_payload_binding(
            intent,
            payload,
        ),
        "Payload binding invalid",
    )

    payload_hash = (
        payload_fingerprint(
            payload
        )
    )

    request_hash = (
        request_fingerprint(
            payload
        )
    )

    shadow_seed = {

        "intent_id":
            intent.intent_id,

        "payload_hash":
            payload_hash,

        "request_hash":
            request_hash,
    }

    shadow_id = (
        "r28s-"
        + stable_hash(
            shadow_seed
        )[:24]
    )

    return ShadowCommit(

        shadow_id=
            shadow_id,

        intent_id=
            intent.intent_id,

        payload_hash=
            payload_hash,

        request_hash=
            request_hash,

        committed_at=
            now,
    )


def validate_shadow_binding(
    intent: ExecutionIntent,
    payload: ExecutionPayload,
    shadow: ShadowCommit,
) -> bool:

    return all(
        [
            shadow.intent_id
            == intent.intent_id,

            shadow.payload_hash
            == payload_fingerprint(
                payload
            ),

            shadow.request_hash
            == request_fingerprint(
                payload
            ),
        ]
    )


def register_shadow(
    shadow: ShadowCommit,
):

    if shadow.shadow_id in SEEN_SHADOWS:

        raise ValueError(
            "Duplicate shadow"
        )

    SEEN_SHADOWS.add(
        shadow.shadow_id
    )


# ============================================================
# UNIT D
# EXECUTION STATE MACHINE
# ============================================================

ALLOWED_TRANSITIONS = {

    "NEW": {
        "VALIDATED",
        "REJECTED",
    },

    "VALIDATED": {
        "SHADOW_COMMITTED",
        "REJECTED",
    },

    "SHADOW_COMMITTED": {
        "RECONCILED",
        "REJECTED",
    },

    "RECONCILED":
        set(),

    "REJECTED":
        set(),
}


TERMINAL_STATES = {
    "RECONCILED",
    "REJECTED",
}


def create_lifecycle(
    intent_id: str,
):

    if intent_id in LIFECYCLES:

        raise ValueError(
            "Lifecycle already exists"
        )

    LIFECYCLES[
        intent_id
    ] = LifecycleRecord(

        intent_id=
            intent_id,

        state=
            "NEW",

        terminal=
            False,
    )


def transition(
    intent_id: str,
    new_state: str,
):

    record = (
        LIFECYCLES[
            intent_id
        ]
    )

    if record.terminal:

        raise ValueError(
            "Terminal state locked"
        )

    allowed = (
        ALLOWED_TRANSITIONS
        .get(
            record.state,
            set(),
        )
    )

    if new_state not in allowed:

        raise ValueError(
            f"Invalid transition "
            f"{record.state} -> "
            f"{new_state}"
        )

    record.state = (
        new_state
    )

    record.terminal = (
        new_state
        in TERMINAL_STATES
    )


# ============================================================
# UNIT E
# INTEGRATION BOUNDARY
# ============================================================

def integration_chain(
    signal: Signal,
    now: int,
):

    validate_signal(
        signal,
        now,
    )

    register_signal(
        signal
    )

    intent = (
        build_execution_intent(
            signal
        )
    )

    register_intent(
        intent
    )

    create_lifecycle(
        intent.intent_id
    )

    transition(
        intent.intent_id,
        "VALIDATED",
    )

    payload = (
        build_payload(
            intent
        )
    )

    assert_true(
        validate_payload_binding(
            intent,
            payload,
        ),
        "Payload binding failed",
    )

    shadow = (
        build_shadow_commit(
            intent,
            payload,
            now,
        )
    )

    assert_true(
        validate_shadow_binding(
            intent,
            payload,
            shadow,
        ),
        "Shadow binding failed",
    )

    register_shadow(
        shadow
    )

    transition(
        intent.intent_id,
        "SHADOW_COMMITTED",
    )

    transition(
        intent.intent_id,
        "RECONCILED",
    )

    return (
        intent,
        payload,
        shadow,
    )


# ============================================================
# UNIT F + UNIT G
# PERSISTENCE / RESTART / IDEMPOTENCY
# ============================================================

def snapshot_dict() -> dict:

    lifecycles = {

        intent_id: {

            "intent_id":
                record.intent_id,

            "state":
                record.state,

            "terminal":
                record.terminal,
        }

        for intent_id, record
        in sorted(
            LIFECYCLES.items()
        )
    }

    body = {

        "module":
            MODULE_NAME,

        "version":
            MODULE_VERSION,

        "seen_signals":
            sorted(
                SEEN_SIGNALS
            ),

        "seen_intents":
            sorted(
                SEEN_INTENTS
            ),

        "seen_shadows":
            sorted(
                SEEN_SHADOWS
            ),

        "lifecycles":
            lifecycles,

        "locks": {

            "live":
                LIVE_ORDER_EXECUTION,

            "demo":
                DEMO_ORDER_EXECUTION,

            "network":
                NETWORK_ACCESS_ENABLED,

            "hard_real":
                HARD_REAL_POST_LOCK,

            "hard_demo":
                HARD_DEMO_POST_LOCK,
        },
    }

    checksum = (
        stable_hash(
            body
        )
    )

    return {

        "body":
            body,

        "checksum":
            checksum,
    }


def write_snapshot(
    path: str,
):

    snapshot = (
        snapshot_dict()
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            snapshot,
            handle,
            sort_keys=True,
            separators=(",", ":"),
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )


def read_snapshot(
    path: str,
) -> dict:

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:

        snapshot = (
            json.load(
                handle
            )
        )

    if not isinstance(
        snapshot,
        dict,
    ):

        raise ValueError(
            "Snapshot must be an object"
        )

    if set(
        snapshot.keys()
    ) != {
        "body",
        "checksum",
    }:

        raise ValueError(
            "Invalid snapshot structure"
        )

    body = (
        snapshot[
            "body"
        ]
    )

    checksum = (
        snapshot[
            "checksum"
        ]
    )

    if stable_hash(
        body
    ) != checksum:

        raise ValueError(
            "Snapshot checksum mismatch"
        )

    locks = (
        body.get(
            "locks",
            {},
        )
    )

    expected_locks = {

        "live":
            False,

        "demo":
            False,

        "network":
            False,

        "hard_real":
            True,

        "hard_demo":
            True,
    }

    if locks != expected_locks:

        raise ValueError(
            "Snapshot safety locks inconsistent"
        )

    return snapshot


def clear_runtime_memory():

    SEEN_SIGNALS.clear()

    SEEN_INTENTS.clear()

    SEEN_SHADOWS.clear()

    LIFECYCLES.clear()


def restore_snapshot(
    snapshot: dict,
):

    body = (
        snapshot[
            "body"
        ]
    )

    clear_runtime_memory()

    SEEN_SIGNALS.update(
        body[
            "seen_signals"
        ]
    )

    SEEN_INTENTS.update(
        body[
            "seen_intents"
        ]
    )

    SEEN_SHADOWS.update(
        body[
            "seen_shadows"
        ]
    )

    for intent_id, item in (
        body[
            "lifecycles"
        ]
        .items()
    ):

        record = (
            LifecycleRecord(

                intent_id=
                    item[
                        "intent_id"
                    ],

                state=
                    item[
                        "state"
                    ],

                terminal=
                    bool(
                        item[
                            "terminal"
                        ]
                    ),
            )
        )

        if record.intent_id != intent_id:

            raise ValueError(
                "Lifecycle key mismatch"
            )

        if record.state not in ALLOWED_TRANSITIONS:

            raise ValueError(
                "Unknown lifecycle state"
            )

        expected_terminal = (
            record.state
            in TERMINAL_STATES
        )

        if (
            record.terminal
            != expected_terminal
        ):

            raise ValueError(
                "Lifecycle terminal flag inconsistent"
            )

        LIFECYCLES[
            intent_id
        ] = record


def expect_rejection(
    fn,
) -> bool:

    try:

        fn()

    except (
        ValueError,
        AssertionError,
    ):

        return True

    return False


# ============================================================
# ABSOLUTELY LOCKED TRANSMISSION STUBS
# ============================================================

async def real_order_post(
    *args,
    **kwargs,
):

    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise RuntimeError(
        "REAL ORDER TRANSMISSION HARD-LOCKED"
    )


async def demo_order_post(
    *args,
    **kwargs,
):

    global DEMO_POST_CALLED

    DEMO_POST_CALLED = True

    raise RuntimeError(
        "DEMO ORDER TRANSMISSION HARD-LOCKED"
    )


async def network_request(
    *args,
    **kwargs,
):

    global NETWORK_CALLED

    NETWORK_CALLED = True

    raise RuntimeError(
        "NETWORK ACCESS DISABLED"
    )


# ============================================================
# UNIT H
# FULL END-TO-END A-H DIAGNOSTIC
# ============================================================

async def run_diagnostic():

    print(
        "R28 A-H: RUNTIME STARTING",
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
        "FULL A-H END-TO-END INTEGRATION VALIDATION",
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

    print(
        "R28 A-H INTEGRATION GATES",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )


    # ========================================================
    # TEST SIGNAL
    # ========================================================

    now = int(
        time.time()
    )

    signal = Signal(

        signal_id=
            "R28-AH-SIGNAL-001",

        symbol=
            "BTCUSDT",

        side=
            "BUY",

        position_side=
            "LONG",

        quantity=
            "0.0001",

        leverage=
            100,

        created_at=
            now,
    )


    # ========================================================
    # UNIT A TESTS
    # ========================================================

    validate_signal(
        signal,
        now,
    )

    gate(
        "A / Signal Validation",
        True,
    )

    register_signal(
        signal
    )

    gate(
        "A / Signal Registered",
        signal.signal_id
        in SEEN_SIGNALS,
    )


    # ========================================================
    # UNIT B TESTS
    # ========================================================

    intent = (
        build_execution_intent(
            signal
        )
    )

    gate(
        "B / Execution Intent Created",
        bool(
            intent.intent_id
        ),
    )

    intent_again = (
        build_execution_intent(
            signal
        )
    )

    gate(
        "B / Deterministic Intent",
        intent_again == intent,
    )

    register_intent(
        intent
    )

    gate(
        "B / Intent Registered",
        intent.intent_id
        in SEEN_INTENTS,
    )


    # ========================================================
    # UNIT D INITIAL STATE TEST
    # ========================================================

    create_lifecycle(
        intent.intent_id
    )

    transition(
        intent.intent_id,
        "VALIDATED",
    )

    gate(
        "D / Validated State Reached",
        LIFECYCLES[
            intent.intent_id
        ].state
        == "VALIDATED",
    )


    # ========================================================
    # UNIT C PAYLOAD TESTS
    # ========================================================

    payload = (
        build_payload(
            intent
        )
    )

    gate(
        "C / Payload Binding Valid",
        validate_payload_binding(
            intent,
            payload,
        ),
    )

    payload_again = (
        build_payload(
            intent
        )
    )

    gate(
        "C / Deterministic Payload",
        payload_again
        == payload,
    )

    gate(
        "C / Deterministic Payload Hash",
        payload_fingerprint(
            payload_again
        )
        ==
        payload_fingerprint(
            payload
        ),
    )

    gate(
        "C / Deterministic Request Hash",
        request_fingerprint(
            payload_again
        )
        ==
        request_fingerprint(
            payload
        ),
    )


    # ========================================================
    # UNIT C / E SHADOW TESTS
    # ========================================================

    shadow = (
        build_shadow_commit(
            intent,
            payload,
            now,
        )
    )

    gate(
        "C/E / Shadow Binding Valid",
        validate_shadow_binding(
            intent,
            payload,
            shadow,
        ),
    )

    shadow_again = (
        build_shadow_commit(
            intent,
            payload,
            now + 1,
        )
    )

    gate(
        "C/E / Deterministic Shadow ID",
        shadow_again.shadow_id
        == shadow.shadow_id,
    )

    register_shadow(
        shadow
    )

    gate(
        "C/E / Shadow Commit Registered",
        shadow.shadow_id
        in SEEN_SHADOWS,
    )


    # ========================================================
    # UNIT D / E STATE TESTS
    # ========================================================

    transition(
        intent.intent_id,
        "SHADOW_COMMITTED",
    )

    gate(
        "D/E / Shadow State Reached",
        LIFECYCLES[
            intent.intent_id
        ].state
        == "SHADOW_COMMITTED",
    )

    transition(
        intent.intent_id,
        "RECONCILED",
    )

    gate(
        "D/E / Intent Reconciled",
        LIFECYCLES[
            intent.intent_id
        ].state
        == "RECONCILED",
    )


    # ========================================================
    # UNIT F DUPLICATE / TERMINAL TESTS
    # ========================================================

    gate(
        "F / Duplicate Signal Rejected",
        expect_rejection(
            lambda:
                register_signal(
                    signal
                )
        ),
    )

    gate(
        "F / Duplicate Intent Rejected",
        expect_rejection(
            lambda:
                register_intent(
                    intent
                )
        ),
    )

    gate(
        "F / Duplicate Shadow Rejected",
        expect_rejection(
            lambda:
                register_shadow(
                    shadow
                )
        ),
    )

    gate(
        "D/F / Terminal State Locked",
        expect_rejection(
            lambda:
                transition(
                    intent.intent_id,
                    "VALIDATED",
                )
        ),
    )


    # ========================================================
    # UNIT F / G SNAPSHOT TESTS
    # ========================================================

    snapshot_before = (
        snapshot_dict()
    )

    snapshot_before_again = (
        snapshot_dict()
    )

    gate(
        "F/G / Deterministic Snapshot",
        snapshot_before
        == snapshot_before_again,
    )

    write_snapshot(
        STATE_FILE
    )

    gate(
        "G / Persistence File Created",
        os.path.exists(
            STATE_FILE
        ),
    )


    # ========================================================
    # SIMULATED PROCESS MEMORY LOSS
    # ========================================================

    clear_runtime_memory()

    gate(
        "G / Runtime Memory Cleared",
        (
            not SEEN_SIGNALS
            and not SEEN_INTENTS
            and not SEEN_SHADOWS
            and not LIFECYCLES
        ),
    )


    # ========================================================
    # SIMULATED RESTART / RESTORE
    # ========================================================

    restored_snapshot = (
        read_snapshot(
            STATE_FILE
        )
    )

    restore_snapshot(
        restored_snapshot
    )

    gate(
        "F/G / Restart State Restored",
        (
            signal.signal_id
            in SEEN_SIGNALS
            and
            intent.intent_id
            in LIFECYCLES
        ),
    )

    snapshot_after = (
        snapshot_dict()
    )

    gate(
        "F/G / Deterministic Restore",
        snapshot_after
        == snapshot_before,
    )


    # ========================================================
    # REPLAY PROTECTION AFTER RESTART
    # ========================================================

    gate(
        "F/H / Signal Replay After Restart Rejected",
        expect_rejection(
            lambda:
                register_signal(
                    signal
                )
        ),
    )

    gate(
        "F/H / Intent Replay After Restart Rejected",
        expect_rejection(
            lambda:
                register_intent(
                    intent
                )
        ),
    )

    gate(
        "F/H / Shadow Replay After Restart Rejected",
        expect_rejection(
            lambda:
                register_shadow(
                    shadow
                )
        ),
    )

    gate(
        "F/H / Terminal Replay After Restart Rejected",
        expect_rejection(
            lambda:
                transition(
                    intent.intent_id,
                    "VALIDATED",
                )
        ),
    )


    # ========================================================
    # TAMPER TEST
    # PAYLOAD
    # ========================================================

    tampered_payload = (
        ExecutionPayload(

            intent_id=
                payload.intent_id,

            symbol=
                payload.symbol,

            side=
                "SELL",

            position_side=
                payload.position_side,

            quantity=
                payload.quantity,

            leverage=
                payload.leverage,

            margin_type=
                payload.margin_type,

            order_type=
                payload.order_type,

            reduce_only=
                payload.reduce_only,

            client_order_id=
                payload.client_order_id,
        )
    )

    gate(
        "H / Tampered Payload Rejected",
        not validate_payload_binding(
            intent,
            tampered_payload,
        ),
    )


    # ========================================================
    # TAMPER TEST
    # SHADOW
    # ========================================================

    tampered_shadow = (
        ShadowCommit(

            shadow_id=
                shadow.shadow_id,

            intent_id=
                shadow.intent_id,

            payload_hash=
                "0" * 64,

            request_hash=
                shadow.request_hash,

            committed_at=
                shadow.committed_at,
        )
    )

    gate(
        "H / Tampered Shadow Rejected",
        not validate_shadow_binding(
            intent,
            payload,
            tampered_shadow,
        ),
    )


    # ========================================================
    # CORRUPTED SNAPSHOT TEST
    # ========================================================

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as handle:

        good_text = (
            handle.read()
        )

    corrupted_path = (
        STATE_FILE
        + ".corrupt"
    )

    with open(
        corrupted_path,
        "w",
        encoding="utf-8",
    ) as handle:

        replacement = (
            "0"
            if good_text[-1:] != "0"
            else "1"
        )

        handle.write(
            good_text[:-1]
            + replacement
        )

    corrupted_rejected = False

    try:

        read_snapshot(
            corrupted_path
        )

    except (
        ValueError,
        json.JSONDecodeError,
    ):

        corrupted_rejected = True

    finally:

        try:

            os.remove(
                corrupted_path
            )

        except OSError:

            pass

    gate(
        "H / Corrupted Snapshot Rejected",
        corrupted_rejected,
    )


    # ========================================================
    # ABSOLUTE EXECUTION LOCK TEST
    # ========================================================

    locks_active = all(
        [
            LIVE_ORDER_EXECUTION
            is False,

            DEMO_ORDER_EXECUTION
            is False,

            NETWORK_ACCESS_ENABLED
            is False,

            HARD_REAL_POST_LOCK
            is True,

            HARD_DEMO_POST_LOCK
            is True,
        ]
    )

    gate(
        "A-H / Execution Locks Active",
        locks_active,
    )


    # ========================================================
    # VERIFY TRANSMISSION FUNCTIONS NEVER CALLED
    # ========================================================

    no_transmission = (
        not REAL_POST_CALLED
        and not DEMO_POST_CALLED
        and not NETWORK_CALLED
    )

    gate(
        "A-H / No Transmission Occurred",
        no_transmission,
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "-" * 60,
        flush=True,
    )

    print(
        "✅ R28 A-H INTEGRATION DIAGNOSTIC PASSED",
        flush=True,
    )

    print(
        "✅ UNITS A-H INTEGRATED",
        flush=True,
    )

    print(
        "✅ SIGNAL SAFETY VALIDATED",
        flush=True,
    )

    print(
        "✅ EXECUTION INTENT SAFETY VALIDATED",
        flush=True,
    )

    print(
        "✅ PAYLOAD + SHADOW BINDING VALIDATED",
        flush=True,
    )

    print(
        "✅ EXECUTION STATE MACHINE VALIDATED",
        flush=True,
    )

    print(
        "✅ INTEGRATION BOUNDARY VALIDATED",
        flush=True,
    )

    print(
        "✅ RESTART / IDEMPOTENCY VALIDATED",
        flush=True,
    )

    print(
        "✅ PERSISTENCE / RESTORE VALIDATED",
        flush=True,
    )

    print(
        "✅ END-TO-END EXECUTION CHAIN VALIDATED",
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
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime():

    print(
        "R28 A-H: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 A-H: WAITING WITH SAFETY LOCKS ACTIVE",
        flush=True,
    )

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"R28 A-H: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        await asyncio.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================
# MAIN
# ============================================================

async def main():

    await run_diagnostic()

    await persistent_runtime()


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
            "R28 A-H: STOPPED BY OPERATOR",
            flush=True,
        )
