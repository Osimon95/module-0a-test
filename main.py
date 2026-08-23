# ============================================================
# 0F-4H-R28-UNIT-B
# STANDALONE EXECUTION INTENT VALIDATION
#
# PURPOSE:
# - Validate execution-intent construction
# - Validate side / position-side rules
# - Validate quantity safety
# - Validate leverage safety
# - Validate deterministic intent fingerprints
# - Validate client order ID generation
#
# SAFETY:
# - NO EXCHANGE CONNECTION
# - NO TELEGRAM
# - NO HTTP REQUESTS
# - NO REAL ORDER TRANSMISSION
# - NO DEMO ORDER TRANSMISSION
# ============================================================


import hashlib
import json
import time

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict


# ============================================================
# MODULE IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-B"


# ============================================================
# SAFETY CONFIGURATION
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_REAL_POST_LOCK = True

MAX_CONFIG_LEVERAGE = 100


# ============================================================
# EXECUTION INTENT MODEL
# ============================================================

@dataclass(frozen=True)
class ExecutionIntent:
    intent_id: str
    signal_id: str
    symbol: str
    side: str
    position_side: str
    quantity: Decimal
    leverage: int
    client_order_id: str
    created_ms: int


# ============================================================
# BASIC HELPERS
# ============================================================

def sha256_hex(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def stable_json(
    value: Dict,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )


def fmt_decimal(
    value: Decimal,
) -> str:

    formatted = format(
        value,
        "f",
    )

    if "." in formatted:

        formatted = formatted.rstrip(
            "0"
        )

        formatted = formatted.rstrip(
            "."
        )

    return formatted


# ============================================================
# CLIENT ORDER ID CREATION
# ============================================================

def create_client_order_id(
    signal_id: str,
    symbol: str,
    side: str,
    position_side: str,
) -> str:

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

    seed = "|".join(
        [
            signal_id,
            symbol,
            side,
            position_side,
        ]
    )

    digest = sha256_hex(
        seed
    )

    return (
        "R28B-"
        + digest[:24]
    )


# ============================================================
# INTENT ID CREATION
# ============================================================

def create_intent_id(
    signal_id: str,
    symbol: str,
    side: str,
    position_side: str,
    quantity: Decimal,
    leverage: int,
) -> str:

    canonical = "|".join(
        [
            signal_id.strip(),
            symbol.strip().upper(),
            side.strip().upper(),
            position_side.strip().upper(),
            fmt_decimal(
                quantity
            ),
            str(
                leverage
            ),
        ]
    )

    return sha256_hex(
        canonical
    )


# ============================================================
# QUANTITY VALIDATION
# ============================================================

def validate_execution_quantity(
    quantity: Decimal,
) -> None:

    if not isinstance(
        quantity,
        Decimal,
    ):

        raise TypeError(
            "quantity must be Decimal"
        )

    if not quantity.is_finite():

        raise ValueError(
            "quantity must be finite"
        )

    if quantity <= 0:

        raise ValueError(
            "quantity must be greater than zero"
        )


# ============================================================
# LEVERAGE VALIDATION
# ============================================================

def validate_execution_leverage(
    leverage: int,
) -> None:

    if isinstance(
        leverage,
        bool,
    ):

        raise TypeError(
            "leverage must be integer"
        )

    if not isinstance(
        leverage,
        int,
    ):

        raise TypeError(
            "leverage must be integer"
        )

    if leverage <= 0:

        raise ValueError(
            "leverage must be greater than zero"
        )

    if leverage > MAX_CONFIG_LEVERAGE:

        raise ValueError(
            "leverage exceeds configured maximum "
            f"of {MAX_CONFIG_LEVERAGE}x"
        )


# ============================================================
# SIDE VALIDATION
# ============================================================

def validate_execution_side(
    side: str,
) -> str:

    side = (
        side
        .strip()
        .upper()
    )

    if side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            f"Invalid side: {side}"
        )

    return side


# ============================================================
# POSITION SIDE VALIDATION
# ============================================================

def validate_position_side(
    position_side: str,
) -> str:

    position_side = (
        position_side
        .strip()
        .upper()
    )

    if position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "Invalid position_side: "
            f"{position_side}"
        )

    return position_side


# ============================================================
# TRADE DIRECTION VALIDATION
# ============================================================

def validate_trade_direction(
    side: str,
    position_side: str,
) -> None:

    valid_pairs = {
        (
            "BUY",
            "LONG",
        ),
        (
            "SELL",
            "SHORT",
        ),
    }

    pair = (
        side,
        position_side,
    )

    if pair not in valid_pairs:

        raise ValueError(
            "Invalid opening trade direction: "
            f"{side}/{position_side}"
        )


# ============================================================
# EXECUTION INTENT CREATION
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

    side = validate_execution_side(
        side
    )

    position_side = validate_position_side(
        position_side
    )

    validate_trade_direction(
        side,
        position_side,
    )

    validate_execution_quantity(
        quantity
    )

    validate_execution_leverage(
        leverage
    )

    intent_id = create_intent_id(
        signal_id=signal_id,
        symbol=symbol,
        side=side,
        position_side=position_side,
        quantity=quantity,
        leverage=leverage,
    )

    client_order_id = create_client_order_id(
        signal_id=signal_id,
        symbol=symbol,
        side=side,
        position_side=position_side,
    )

    created_ms = int(
        time.time()
        * 1000
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
        created_ms=created_ms,
    )


# ============================================================
# SAFETY ASSERTIONS
# ============================================================

def assert_transmission_disabled(
) -> bool:

    if LIVE_ORDER_EXECUTION:

        raise RuntimeError(
            "UNIT B SAFETY FAILURE: "
            "LIVE_ORDER_EXECUTION must remain False"
        )

    if not HARD_REAL_POST_LOCK:

        raise RuntimeError(
            "UNIT B SAFETY FAILURE: "
            "HARD_REAL_POST_LOCK must remain True"
        )

    return True


# ============================================================
# TEST 1
# VALID EXECUTION INTENT
# ============================================================

def test_valid_intent_creation(
) -> bool:

    intent = build_execution_intent(
        signal_id="r28-unit-b-test-signal",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0005"
        ),
        leverage=100,
    )

    return (
        intent.signal_id
        == "r28-unit-b-test-signal"
        and intent.symbol
        == "BTCUSDT"
        and intent.side
        == "BUY"
        and intent.position_side
        == "LONG"
        and intent.quantity
        == Decimal(
            "0.0005"
        )
        and intent.leverage
        == 100
        and bool(
            intent.intent_id
        )
        and bool(
            intent.client_order_id
        )
    )


# ============================================================
# TEST 2
# INVALID QUANTITY REJECTED
# ============================================================

def test_invalid_quantity_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-bad-quantity",
            symbol="BTCUSDT",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "0"
            ),
            leverage=100,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 3
# NEGATIVE QUANTITY REJECTED
# ============================================================

def test_negative_quantity_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-negative-quantity",
            symbol="BTCUSDT",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "-0.0005"
            ),
            leverage=100,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 4
# INVALID LEVERAGE REJECTED
# ============================================================

def test_invalid_leverage_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-bad-leverage",
            symbol="BTCUSDT",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=0,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 5
# EXCESSIVE LEVERAGE REJECTED
# ============================================================

def test_excessive_leverage_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-high-leverage",
            symbol="BTCUSDT",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=101,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 6
# INVALID SIDE REJECTED
# ============================================================

def test_invalid_side_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-bad-side",
            symbol="BTCUSDT",
            side="HOLD",
            position_side="LONG",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=100,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 7
# INVALID POSITION SIDE REJECTED
# ============================================================

def test_invalid_position_side_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-bad-position-side",
            symbol="BTCUSDT",
            side="BUY",
            position_side="FLAT",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=100,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 8
# INVALID TRADE DIRECTION REJECTED
# ============================================================

def test_invalid_trade_direction_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-invalid-direction",
            symbol="BTCUSDT",
            side="SELL",
            position_side="LONG",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=100,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 9
# DETERMINISTIC INTENT ID
# ============================================================

def test_deterministic_intent_id(
) -> bool:

    first = create_intent_id(
        signal_id="r28-deterministic-test",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0005"
        ),
        leverage=100,
    )

    second = create_intent_id(
        signal_id="r28-deterministic-test",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0005"
        ),
        leverage=100,
    )

    return (
        first
        == second
        and len(
            first
        )
        == 64
    )


# ============================================================
# TEST 10
# DIFFERENT SIGNAL PRODUCES DIFFERENT INTENT
# ============================================================

def test_unique_signal_intent(
) -> bool:

    first = create_intent_id(
        signal_id="r28-signal-one",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0005"
        ),
        leverage=100,
    )

    second = create_intent_id(
        signal_id="r28-signal-two",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0005"
        ),
        leverage=100,
    )

    return (
        first
        != second
    )


# ============================================================
# TEST 11
# CLIENT ORDER ID GENERATED
# ============================================================

def test_client_order_id_generated(
) -> bool:

    client_order_id = create_client_order_id(
        signal_id="r28-client-order-test",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
    )

    return (
        client_order_id.startswith(
            "R28B-"
        )
        and len(
            client_order_id
        )
        > 10
    )


# ============================================================
# TEST 12
# CLIENT ORDER ID DETERMINISTIC
# ============================================================

def test_client_order_id_deterministic(
) -> bool:

    first = create_client_order_id(
        signal_id="r28-client-deterministic",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
    )

    second = create_client_order_id(
        signal_id="r28-client-deterministic",
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
    )

    return (
        first
        == second
    )


# ============================================================
# TEST 13
# INPUT NORMALIZATION
# ============================================================

def test_input_normalization(
) -> bool:

    intent = build_execution_intent(
        signal_id="  r28-normalization  ",
        symbol=" btcusdt ",
        side=" buy ",
        position_side=" long ",
        quantity=Decimal(
            "0.0005"
        ),
        leverage=100,
    )

    return (
        intent.signal_id
        == "r28-normalization"
        and intent.symbol
        == "BTCUSDT"
        and intent.side
        == "BUY"
        and intent.position_side
        == "LONG"
    )


# ============================================================
# TEST 14
# EMPTY SIGNAL ID REJECTED
# ============================================================

def test_empty_signal_id_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="   ",
            symbol="BTCUSDT",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=100,
        )

    except ValueError:

        return True

    return False


# ============================================================
# TEST 15
# EMPTY SYMBOL REJECTED
# ============================================================

def test_empty_symbol_rejected(
) -> bool:

    try:

        build_execution_intent(
            signal_id="r28-empty-symbol",
            symbol="   ",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "0.0005"
            ),
            leverage=100,
        )

    except ValueError:

        return True

    return False


# ============================================================
# DIAGNOSTIC RESULT HELPER
# ============================================================

def status_icon(
    passed: bool,
) -> str:

    if passed:

        return "✅ PASS"

    return "❌ FAIL"


# ============================================================
# R28 UNIT B DIAGNOSTIC
# ============================================================

def run_unit_b_diagnostic(
) -> bool:

    print(
        "="
        * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "STANDALONE EXECUTION INTENT VALIDATION"
    )

    print(
        "NO EXCHANGE CONNECTION"
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )

    print(
        "="
        * 60
    )

    assert_transmission_disabled()

    results = {
        "Valid Intent Creation":
            test_valid_intent_creation(),

        "Invalid Quantity Rejected":
            test_invalid_quantity_rejected(),

        "Negative Quantity Rejected":
            test_negative_quantity_rejected(),

        "Invalid Leverage Rejected":
            test_invalid_leverage_rejected(),

        "Excessive Leverage Rejected":
            test_excessive_leverage_rejected(),

        "Invalid Side Rejected":
            test_invalid_side_rejected(),

        "Invalid Position Side":
            test_invalid_position_side_rejected(),

        "Invalid Direction Rejected":
            test_invalid_trade_direction_rejected(),

        "Deterministic Intent ID":
            test_deterministic_intent_id(),

        "Unique Signal Intent":
            test_unique_signal_intent(),

        "Client Order ID Generated":
            test_client_order_id_generated(),

        "Client Order ID Deterministic":
            test_client_order_id_deterministic(),

        "Input Normalization":
            test_input_normalization(),

        "Empty Signal ID Rejected":
            test_empty_signal_id_rejected(),

        "Empty Symbol Rejected":
            test_empty_symbol_rejected(),
    }

    print()

    print(
        "R28 UNIT B EXECUTION INTENT GATES"
    )

    print(
        "-"
        * 60
    )

    for name, passed in results.items():

        print(
            f"{name:<34}"
            f"{status_icon(passed)}"
        )

    print(
        "-"
        * 60
    )

    all_passed = all(
        results.values()
    )

    if all_passed:

        print(
            "✅ R28 UNIT B DIAGNOSTIC PASSED"
        )

        print(
            "✅ EXECUTION INTENT SAFETY VALIDATED"
        )

        print(
            "✅ UNIT B READY FOR INTEGRATION"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

    else:

        print(
            "❌ R28 UNIT B DIAGNOSTIC FAILED"
        )

        print(
            "❌ UNIT B NOT READY FOR INTEGRATION"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

    print(
        "="
        * 60
    )

    return all_passed


# ============================================================
# MAIN
# ============================================================

def main(
) -> None:

    try:

        passed = run_unit_b_diagnostic()

        if not passed:

            raise RuntimeError(
                "R28 UNIT B diagnostic failure"
            )

    except Exception as exc:

        print(
            "="
            * 60
        )

        print(
            "❌ R28 UNIT B FATAL ERROR"
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

        print(
            "="
            * 60
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()

