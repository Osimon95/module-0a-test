# ============================================================
# 0F-4H-R28-UNIT-D
# STANDALONE EXECUTION STATE MACHINE
# + CONTROLLED DEMO TRANSITION SAFETY VALIDATION
#
# NO EXCHANGE CONNECTION
# NO TELEGRAM
# NO REAL ORDER TRANSMISSION
# NO DEMO ORDER TRANSMISSION
# ============================================================

from __future__ import annotations

import hashlib
import json
import time

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Set


# ============================================================
# MODULE IDENTITY
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-D"

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

HARD_REAL_POST_LOCK = True

HARD_DEMO_POST_LOCK = True


# ============================================================
# ORDER PATH LOCKS
# ============================================================

REAL_ORDER_PATH = "/capi/v3/order"

DEMO_ORDER_PATH = "/capi/v3/sim/order"

ALLOWED_SHADOW_METHOD = "POST"


# ============================================================
# SAFETY LIMITS
# ============================================================

MAX_CONFIG_LEVERAGE = 100

MIN_QUANTITY = Decimal("0.0001")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")


# ============================================================
# GLOBAL TRANSMISSION FLAGS
# ============================================================

R28_REAL_POST_CALLED = False

R28_DEMO_POST_CALLED = False


# ============================================================
# HELPERS
# ============================================================

def stable_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )


def sha256_hex(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def fmt_decimal(
    value: Decimal,
) -> str:

    normalized = value.normalize()

    text = format(
        normalized,
        "f",
    )

    if "." in text:

        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    return text


def pass_fail(
    value: bool,
) -> str:

    return (
        "✅ PASS"
        if value
        else "❌ FAIL"
    )


# ============================================================
# EXECUTION STATES
# ============================================================

class ExecutionState(
    str,
    Enum,
):

    CREATED = "CREATED"

    VALIDATED = "VALIDATED"

    SHADOW_COMMITTED = (
        "SHADOW_COMMITTED"
    )

    DEMO_PENDING = "DEMO_PENDING"

    DEMO_ACCEPTED = "DEMO_ACCEPTED"

    DEMO_REJECTED = "DEMO_REJECTED"

    COMPLETED = "COMPLETED"

    REJECTED = "REJECTED"


# ============================================================
# TERMINAL STATES
# ============================================================

TERMINAL_STATES: Set[
    ExecutionState
] = {

    ExecutionState.DEMO_REJECTED,

    ExecutionState.COMPLETED,

    ExecutionState.REJECTED,
}


# ============================================================
# VALID TRANSITIONS
# ============================================================

VALID_TRANSITIONS: Dict[
    ExecutionState,
    Set[ExecutionState],
] = {

    ExecutionState.CREATED: {

        ExecutionState.VALIDATED,

        ExecutionState.REJECTED,
    },

    ExecutionState.VALIDATED: {

        ExecutionState.SHADOW_COMMITTED,

        ExecutionState.REJECTED,
    },

    ExecutionState.SHADOW_COMMITTED: {

        ExecutionState.DEMO_PENDING,

        ExecutionState.REJECTED,
    },

    ExecutionState.DEMO_PENDING: {

        ExecutionState.DEMO_ACCEPTED,

        ExecutionState.DEMO_REJECTED,

        ExecutionState.REJECTED,
    },

    ExecutionState.DEMO_ACCEPTED: {

        ExecutionState.COMPLETED,

        ExecutionState.REJECTED,
    },

    ExecutionState.DEMO_REJECTED: set(),

    ExecutionState.COMPLETED: set(),

    ExecutionState.REJECTED: set(),
}


# ============================================================
# EXECUTION INTENT
# ============================================================

@dataclass(
    frozen=True
)
class ExecutionIntent:

    intent_id: str

    signal_id: str

    symbol: str

    side: str

    position_side: str

    quantity: Decimal

    leverage: int

    client_order_id: str


# ============================================================
# SHADOW COMMIT
# ============================================================

@dataclass(
    frozen=True
)
class ShadowCommit:

    intent_id: str

    method: str

    path: str

    payload: Dict[
        str,
        Any,
    ]

    request_fingerprint: str

    commit_token: str

    created_ms: int


# ============================================================
# EXECUTION RECORD
# ============================================================

@dataclass
class ExecutionRecord:

    intent: ExecutionIntent

    shadow_commit: ShadowCommit

    state: ExecutionState

    transition_history: List[
        str
    ]

    demo_response: Optional[
        Dict[
            str,
            Any,
        ]
    ] = None


# ============================================================
# INTENT CREATION
# ============================================================

def build_execution_intent(
    signal_id: str,
    symbol: str,
    side: str,
    position_side: str,
    quantity: Decimal,
    leverage: int,
) -> ExecutionIntent:

    signal_id = (
        signal_id
        .strip()
    )

    symbol = (
        symbol
        .strip()
        .upper()
    )

    side = (
        side
        .strip()
        .upper()
    )

    position_side = (
        position_side
        .strip()
        .upper()
    )

    if not signal_id:

        raise ValueError(
            "signal_id cannot be empty"
        )

    if not symbol:

        raise ValueError(
            "symbol cannot be empty"
        )

    if side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            f"Invalid side: {side}"
        )

    if position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "Invalid position_side: "
            f"{position_side}"
        )

    if quantity <= 0:

        raise ValueError(
            "quantity must be positive"
        )

    if quantity < MIN_QUANTITY:

        raise ValueError(
            "quantity below minimum"
        )

    if leverage <= 0:

        raise ValueError(
            "leverage must be positive"
        )

    if leverage > MAX_CONFIG_LEVERAGE:

        raise ValueError(
            "leverage exceeds configured maximum"
        )

    intent_source = "|".join(
        [
            signal_id,
            symbol,
            side,
            position_side,
            fmt_decimal(
                quantity
            ),
            str(
                leverage
            ),
        ]
    )

    intent_id = (
        "r28i-"
        + sha256_hex(
            intent_source
        )[:24]
    )

    client_order_id = (
        "r28-"
        + sha256_hex(
            "CLIENT|"
            + intent_id
        )[:20]
    )

    return ExecutionIntent(
        intent_id=intent_id,
        signal_id=signal_id,
        symbol=symbol,
        side=side,
        position_side=position_side,
        quantity=quantity,
        leverage=leverage,
        client_order_id=client_order_id,
    )


# ============================================================
# EXECUTION PAYLOAD
# ============================================================

def build_execution_payload(
    intent: ExecutionIntent,
) -> Dict[str, Any]:

    return {

        "symbol":
            intent.symbol,

        "side":
            intent.side,

        "positionSide":
            intent.position_side,

        "quantity":
            fmt_decimal(
                intent.quantity
            ),

        "leverage":
            intent.leverage,

        "clientOrderId":
            intent.client_order_id,

        "orderType":
            "MARKET",
    }


# ============================================================
# SHADOW COMMIT
# ============================================================

def build_shadow_commit(
    intent: ExecutionIntent,
    payload: Dict[
        str,
        Any,
    ],
) -> ShadowCommit:

    method = (
        ALLOWED_SHADOW_METHOD
    )

    path = (
        REAL_ORDER_PATH
    )

    if method != "POST":

        raise RuntimeError(
            "Shadow method lock failure"
        )

    if path != REAL_ORDER_PATH:

        raise RuntimeError(
            "Shadow path lock failure"
        )

    canonical_payload = (
        stable_json(
            payload
        )
    )

    request_fingerprint = (
        sha256_hex(
            method
            + "|"
            + path
            + "|"
            + canonical_payload
        )
    )

    created_ms = int(
        time.time()
        * 1000
    )

    commit_token = (
        sha256_hex(
            intent.intent_id
            + "|"
            + request_fingerprint
            + "|"
            + str(
                created_ms
            )
        )
    )

    return ShadowCommit(
        intent_id=intent.intent_id,
        method=method,
        path=path,
        payload=dict(
            payload
        ),
        request_fingerprint=(
            request_fingerprint
        ),
        commit_token=commit_token,
        created_ms=created_ms,
    )


# ============================================================
# EXECUTION RECORD CREATION
# ============================================================

def create_execution_record(
    intent: ExecutionIntent,
    shadow_commit: ShadowCommit,
) -> ExecutionRecord:

    if (
        intent.intent_id
        != shadow_commit.intent_id
    ):

        raise ValueError(
            "Intent ID does not match shadow commit"
        )

    return ExecutionRecord(
        intent=intent,
        shadow_commit=shadow_commit,
        state=ExecutionState.CREATED,
        transition_history=[
            ExecutionState.CREATED.value
        ],
    )


# ============================================================
# STATE TRANSITION VALIDATOR
# ============================================================

def can_transition(
    current_state: ExecutionState,
    next_state: ExecutionState,
) -> bool:

    allowed_states = (
        VALID_TRANSITIONS.get(
            current_state,
            set(),
        )
    )

    return (
        next_state
        in allowed_states
    )


# ============================================================
# STATE TRANSITION ENGINE
# ============================================================

def transition_state(
    record: ExecutionRecord,
    next_state: ExecutionState,
) -> None:

    current_state = (
        record.state
    )

    if (
        current_state
        in TERMINAL_STATES
    ):

        raise RuntimeError(
            "Cannot transition from terminal state "
            f"{current_state.value}"
        )

    if not can_transition(
        current_state,
        next_state,
    ):

        raise RuntimeError(
            "Invalid execution transition: "
            f"{current_state.value}"
            " -> "
            f"{next_state.value}"
        )

    record.state = (
        next_state
    )

    record.transition_history.append(
        next_state.value
    )


# ============================================================
# INTENT VALIDATION GATE
# ============================================================

def validate_execution_intent(
    record: ExecutionRecord,
) -> None:

    intent = (
        record.intent
    )

    if intent.quantity <= 0:

        raise RuntimeError(
            "Invalid execution quantity"
        )

    if (
        intent.leverage
        > MAX_CONFIG_LEVERAGE
    ):

        raise RuntimeError(
            "Execution leverage exceeds maximum"
        )

    if intent.side not in {
        "BUY",
        "SELL",
    }:

        raise RuntimeError(
            "Invalid execution side"
        )

    if intent.position_side not in {
        "LONG",
        "SHORT",
    }:

        raise RuntimeError(
            "Invalid position side"
        )

    transition_state(
        record,
        ExecutionState.VALIDATED,
    )


# ============================================================
# SHADOW COMMIT VALIDATION GATE
# ============================================================

def validate_shadow_commit(
    record: ExecutionRecord,
) -> None:

    commit = (
        record.shadow_commit
    )

    if (
        commit.intent_id
        != record.intent.intent_id
    ):

        raise RuntimeError(
            "Shadow commit intent mismatch"
        )

    if (
        commit.method
        != "POST"
    ):

        raise RuntimeError(
            "Shadow POST method lock violated"
        )

    if (
        commit.path
        != REAL_ORDER_PATH
    ):

        raise RuntimeError(
            "Shadow order path lock violated"
        )

    canonical_payload = (
        stable_json(
            commit.payload
        )
    )

    expected_fingerprint = (
        sha256_hex(
            commit.method
            + "|"
            + commit.path
            + "|"
            + canonical_payload
        )
    )

    if (
        expected_fingerprint
        != commit.request_fingerprint
    ):

        raise RuntimeError(
            "Shadow request fingerprint mismatch"
        )

    transition_state(
        record,
        ExecutionState.SHADOW_COMMITTED,
    )


# ============================================================
# ABSOLUTE REAL POST BLOCK
# ============================================================

def real_order_post(
    *args: Any,
    **kwargs: Any,
) -> None:

    global R28_REAL_POST_CALLED

    R28_REAL_POST_CALLED = True

    raise RuntimeError(
        "R28 UNIT D REAL ORDER POST BLOCKED"
    )


# ============================================================
# ABSOLUTE DEMO POST BLOCK
# ============================================================

def demo_order_post(
    *args: Any,
    **kwargs: Any,
) -> None:

    global R28_DEMO_POST_CALLED

    R28_DEMO_POST_CALLED = True

    raise RuntimeError(
        "R28 UNIT D DEMO ORDER POST BLOCKED"
    )


# ============================================================
# DEMO PENDING GATE
# ============================================================

def enter_demo_pending(
    record: ExecutionRecord,
) -> None:

    if LIVE_ORDER_EXECUTION:

        raise RuntimeError(
            "LIVE_ORDER_EXECUTION must remain False"
        )

    if not HARD_REAL_POST_LOCK:

        raise RuntimeError(
            "HARD_REAL_POST_LOCK must remain enabled"
        )

    if DEMO_ORDER_EXECUTION:

        raise RuntimeError(
            "UNIT D standalone test requires "
            "DEMO_ORDER_EXECUTION=False"
        )

    if not HARD_DEMO_POST_LOCK:

        raise RuntimeError(
            "HARD_DEMO_POST_LOCK must remain enabled"
        )

    transition_state(
        record,
        ExecutionState.DEMO_PENDING,
    )


# ============================================================
# SIMULATED DEMO RESPONSE
# ============================================================

def simulated_demo_response(
    accepted: bool,
) -> Dict[
    str,
    Any,
]:

    if accepted:

        return {
            "code": "0",
            "msg": "SIMULATED_ACCEPTED",
            "data": {
                "orderId":
                    "SIMULATED-R28-ORDER"
            },
        }

    return {
        "code": "-1",
        "msg": "SIMULATED_REJECTED",
        "data": None,
    }


# ============================================================
# DEMO RESPONSE CLASSIFIER
# ============================================================

def classify_demo_response(
    response: Dict[
        str,
        Any,
    ],
) -> bool:

    code = str(
        response.get(
            "code",
            ""
        )
    )

    return (
        code == "0"
    )


# ============================================================
# HANDLE SIMULATED DEMO RESULT
# ============================================================

def apply_simulated_demo_result(
    record: ExecutionRecord,
    response: Dict[
        str,
        Any,
    ],
) -> None:

    if (
        record.state
        != ExecutionState.DEMO_PENDING
    ):

        raise RuntimeError(
            "Demo result requires DEMO_PENDING state"
        )

    record.demo_response = dict(
        response
    )

    accepted = (
        classify_demo_response(
            response
        )
    )

    if accepted:

        transition_state(
            record,
            ExecutionState.DEMO_ACCEPTED,
        )

    else:

        transition_state(
            record,
            ExecutionState.DEMO_REJECTED,
        )


# ============================================================
# COMPLETE SIMULATED ACCEPTED EXECUTION
# ============================================================

def complete_execution(
    record: ExecutionRecord,
) -> None:

    if (
        record.state
        != ExecutionState.DEMO_ACCEPTED
    ):

        raise RuntimeError(
            "Only DEMO_ACCEPTED execution "
            "may be completed"
        )

    transition_state(
        record,
        ExecutionState.COMPLETED,
    )


# ============================================================
# TEST RECORD FACTORY
# ============================================================

def build_test_record(
) -> ExecutionRecord:

    intent = (
        build_execution_intent(
            signal_id=(
                "r28-unit-d-test-signal"
            ),
            symbol="BTCUSDT",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=100,
        )
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    shadow_commit = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    return create_execution_record(
        intent,
        shadow_commit,
    )


# ============================================================
# TEST 1
# VALID STATE PATH
# ============================================================

def test_valid_state_path(
) -> bool:

    record = (
        build_test_record()
    )

    validate_execution_intent(
        record
    )

    validate_shadow_commit(
        record
    )

    enter_demo_pending(
        record
    )

    response = (
        simulated_demo_response(
            accepted=True
        )
    )

    apply_simulated_demo_result(
        record,
        response,
    )

    complete_execution(
        record
    )

    expected_history = [

        "CREATED",

        "VALIDATED",

        "SHADOW_COMMITTED",

        "DEMO_PENDING",

        "DEMO_ACCEPTED",

        "COMPLETED",
    ]

    return (
        record.state
        == ExecutionState.COMPLETED
        and
        record.transition_history
        == expected_history
    )


# ============================================================
# TEST 2
# INVALID CREATED -> DEMO_PENDING
# ============================================================

def test_invalid_skip_transition(
) -> bool:

    record = (
        build_test_record()
    )

    try:

        transition_state(
            record,
            ExecutionState.DEMO_PENDING,
        )

    except RuntimeError:

        return True

    return False


# ============================================================
# TEST 3
# TERMINAL STATE LOCK
# ============================================================

def test_terminal_state_lock(
) -> bool:

    record = (
        build_test_record()
    )

    validate_execution_intent(
        record
    )

    validate_shadow_commit(
        record
    )

    enter_demo_pending(
        record
    )

    response = (
        simulated_demo_response(
            accepted=False
        )
    )

    apply_simulated_demo_result(
        record,
        response,
    )

    if (
        record.state
        != ExecutionState.DEMO_REJECTED
    ):

        return False

    try:

        transition_state(
            record,
            ExecutionState.COMPLETED,
        )

    except RuntimeError:

        return True

    return False


# ============================================================
# TEST 4
# REJECTED DEMO RESPONSE
# ============================================================

def test_demo_rejection_path(
) -> bool:

    record = (
        build_test_record()
    )

    validate_execution_intent(
        record
    )

    validate_shadow_commit(
        record
    )

    enter_demo_pending(
        record
    )

    response = (
        simulated_demo_response(
            accepted=False
        )
    )

    apply_simulated_demo_result(
        record,
        response,
    )

    return (
        record.state
        == ExecutionState.DEMO_REJECTED
    )


# ============================================================
# TEST 5
# COMPLETION REQUIRES ACCEPTANCE
# ============================================================

def test_completion_gate(
) -> bool:

    record = (
        build_test_record()
    )

    validate_execution_intent(
        record
    )

    validate_shadow_commit(
        record
    )

    enter_demo_pending(
        record
    )

    try:

        complete_execution(
            record
        )

    except RuntimeError:

        return True

    return False


# ============================================================
# TEST 6
# INVALID REVERSE TRANSITION
# ============================================================

def test_reverse_transition_rejected(
) -> bool:

    record = (
        build_test_record()
    )

    validate_execution_intent(
        record
    )

    try:

        transition_state(
            record,
            ExecutionState.CREATED,
        )

    except RuntimeError:

        return True

    return False


# ============================================================
# TEST 7
# REAL POST ABSOLUTE LOCK
# ============================================================

def test_real_post_lock(
) -> bool:

    global R28_REAL_POST_CALLED

    R28_REAL_POST_CALLED = False

    blocked = False

    try:

        real_order_post(
            REAL_ORDER_PATH,
            {
                "symbol":
                    "BTCUSDT"
            },
        )

    except RuntimeError:

        blocked = True

    return (
        blocked
        and
        R28_REAL_POST_CALLED
        and
        LIVE_ORDER_EXECUTION
        is False
        and
        HARD_REAL_POST_LOCK
        is True
    )


# ============================================================
# TEST 8
# DEMO POST ABSOLUTE LOCK
# ============================================================

def test_demo_post_lock(
) -> bool:

    global R28_DEMO_POST_CALLED

    R28_DEMO_POST_CALLED = False

    blocked = False

    try:

        demo_order_post(
            DEMO_ORDER_PATH,
            {
                "symbol":
                    "BTCUSDT"
            },
        )

    except RuntimeError:

        blocked = True

    return (
        blocked
        and
        R28_DEMO_POST_CALLED
        and
        DEMO_ORDER_EXECUTION
        is False
        and
        HARD_DEMO_POST_LOCK
        is True
    )


# ============================================================
# TEST 9
# SHADOW COMMIT REQUIRED
# ============================================================

def test_shadow_commit_required(
) -> bool:

    record = (
        build_test_record()
    )

    validate_execution_intent(
        record
    )

    try:

        enter_demo_pending(
            record
        )

    except RuntimeError:

        return True

    return False


# ============================================================
# TEST 10
# SHADOW COMMIT FINGERPRINT LOCK
# ============================================================

def test_shadow_fingerprint_lock(
) -> bool:

    record = (
        build_test_record()
    )

    validate_execution_intent(
        record
    )

    record.shadow_commit.payload[
        "quantity"
    ] = "999"

    try:

        validate_shadow_commit(
            record
        )

    except RuntimeError:

        return True

    return False


# ============================================================
# TEST 11
# STATE MACHINE TABLE
# ============================================================

def test_state_machine_table(
) -> bool:

    return (

        can_transition(
            ExecutionState.CREATED,
            ExecutionState.VALIDATED,
        )

        and

        can_transition(
            ExecutionState.VALIDATED,
            ExecutionState.SHADOW_COMMITTED,
        )

        and

        can_transition(
            ExecutionState.SHADOW_COMMITTED,
            ExecutionState.DEMO_PENDING,
        )

        and

        can_transition(
            ExecutionState.DEMO_PENDING,
            ExecutionState.DEMO_ACCEPTED,
        )

        and

        can_transition(
            ExecutionState.DEMO_ACCEPTED,
            ExecutionState.COMPLETED,
        )

        and

        not can_transition(
            ExecutionState.CREATED,
            ExecutionState.COMPLETED,
        )

        and

        not can_transition(
            ExecutionState.COMPLETED,
            ExecutionState.CREATED,
        )
    )


# ============================================================
# TEST 12
# NO NETWORK TRANSMISSION CONFIG
# ============================================================

def test_no_transmission_configuration(
) -> bool:

    return (

        LIVE_ORDER_EXECUTION
        is False

        and

        DEMO_ORDER_EXECUTION
        is False

        and

        HARD_REAL_POST_LOCK
        is True

        and

        HARD_DEMO_POST_LOCK
        is True
    )


# ============================================================
# UNIT D DIAGNOSTIC
# ============================================================

def r28_unit_d_run_diagnostic(
) -> bool:

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "STANDALONE EXECUTION STATE MACHINE"
    )

    print(
        "+ CONTROLLED DEMO TRANSITION VALIDATION"
    )

    print(
        "NO EXCHANGE CONNECTION"
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )

    print(
        "DEMO ORDER TRANSMISSION DISABLED"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "R28 UNIT D STATE MACHINE GATES"
    )

    print(
        "-" * 60
    )

    tests = [

        (
            "Valid Execution State Path",
            test_valid_state_path,
        ),

        (
            "Invalid Skip Transition Rejected",
            test_invalid_skip_transition,
        ),

        (
            "Terminal State Locked",
            test_terminal_state_lock,
        ),

        (
            "Demo Rejection Path",
            test_demo_rejection_path,
        ),

        (
            "Completion Requires Acceptance",
            test_completion_gate,
        ),

        (
            "Reverse Transition Rejected",
            test_reverse_transition_rejected,
        ),

        (
            "Real POST Absolute Lock",
            test_real_post_lock,
        ),

        (
            "Demo POST Absolute Lock",
            test_demo_post_lock,
        ),

        (
            "Shadow Commit Required",
            test_shadow_commit_required,
        ),

        (
            "Shadow Fingerprint Locked",
            test_shadow_fingerprint_lock,
        ),

        (
            "State Machine Table Valid",
            test_state_machine_table,
        ),

        (
            "No Transmission Configuration",
            test_no_transmission_configuration,
        ),
    ]

    results: Dict[
        str,
        bool,
    ] = {}

    for (
        label,
        test_function,
    ) in tests:

        try:

            result = bool(
                test_function()
            )

        except Exception as exc:

            result = False

            print(
                f"{label:<40}"
                f" ❌ FAIL"
            )

            print(
                "    "
                + type(
                    exc
                ).__name__
                + ": "
                + str(
                    exc
                )
            )

            results[
                label
            ] = False

            continue

        results[
            label
        ] = result

        print(
            f"{label:<40}"
            f" {pass_fail(result)}"
        )

    print(
        "-" * 60
    )

    all_passed = all(
        results.values()
    )

    if all_passed:

        print(
            "✅ R28 UNIT D DIAGNOSTIC PASSED"
        )

        print(
            "✅ EXECUTION STATE MACHINE VALIDATED"
        )

        print(
            "✅ CONTROLLED DEMO TRANSITIONS VALIDATED"
        )

        print(
            "✅ UNIT D READY FOR INTEGRATION"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

    else:

        print(
            "❌ R28 UNIT D DIAGNOSTIC FAILED"
        )

        print(
            "❌ UNIT D NOT READY FOR INTEGRATION"
        )

    print(
        "=" * 60
    )

    return all_passed


# ============================================================
# MAIN
# ============================================================

def main(
) -> None:

    passed = (
        r28_unit_d_run_diagnostic()
    )

    if not passed:

        raise SystemExit(
            1
        )


if __name__ == "__main__":

    main()
