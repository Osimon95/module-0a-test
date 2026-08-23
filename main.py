# ============================================================
# 0F-4H-R28-UNIT-C
# STANDALONE EXECUTION PAYLOAD + SHADOW COMMIT VALIDATION
#
# PURPOSE:
#   Validate the transformation:
#
#       ExecutionIntent
#             ↓
#       Execution Payload
#             ↓
#       Shadow Commit
#
#   WITHOUT:
#       - WEEX API connection
#       - HTTP requests
#       - aiohttp
#       - Telegram
#       - exchange credentials
#       - real order transmission
#       - demo order transmission
#
# SAFETY:
#   THIS FILE CANNOT TRANSMIT AN ORDER.
#
# ============================================================

from __future__ import annotations

import hashlib
import json
import os
import time

from dataclasses import dataclass
from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_DOWN,
)
from typing import (
    Any,
    Dict,
    Optional,
)


# ============================================================
# MODULE IDENTITY
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-C"

UNIT_NAME = (
    "STANDALONE EXECUTION PAYLOAD "
    "+ SHADOW COMMIT SAFETY VALIDATION"
)


# ============================================================
# ABSOLUTE SAFETY CONFIGURATION
# ============================================================

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

HARD_REAL_POST_LOCK = True

NETWORK_ACCESS_ALLOWED = False


# ============================================================
# EXECUTION CONSTANTS
# ============================================================

REAL_ORDER_PATH = "/capi/v3/order"

SHADOW_METHOD = "POST"

MARGIN_MODE = "ISOLATED"

MAX_CONFIG_LEVERAGE = 100

MIN_CONFIG_LEVERAGE = 1

MAX_QUANTITY_DECIMALS = 8


# ============================================================
# GLOBAL TRANSMISSION TELEMETRY
# ============================================================

REAL_POST_CALLED = False

DEMO_POST_CALLED = False

NETWORK_CALL_CALLED = False


# ============================================================
# DATA MODELS
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


@dataclass(frozen=True)
class ExecutionPayload:

    symbol: str

    side: str

    position_side: str

    order_type: str

    quantity: str

    leverage: str

    margin_mode: str

    client_order_id: str

    reduce_only: bool


@dataclass(frozen=True)
class ShadowCommit:

    intent_id: str

    intent_fingerprint: str

    payload_fingerprint: str

    request_fingerprint: str

    commit_token: str

    method: str

    path: str

    canonical_payload: str


# ============================================================
# BASIC HELPERS
# ============================================================

def sha256_hex(
    value: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise TypeError(
            "sha256_hex requires a string"
        )

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


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
        ensure_ascii=False,
    )


def normalize_decimal_string(
    value: Decimal,
) -> str:

    if not isinstance(
        value,
        Decimal,
    ):

        try:

            value = Decimal(
                str(
                    value
                )
            )

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as exc:

            raise ValueError(
                "Invalid decimal value"
            ) from exc

    if not value.is_finite():

        raise ValueError(
            "Decimal must be finite"
        )

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    if text in {
        "",
        "-0",
    }:

        text = "0"

    return text


def bool_text(
    value: bool,
) -> str:

    return (
        "true"
        if value
        else "false"
    )


# ============================================================
# HARD SAFETY ASSERTIONS
# ============================================================

def assert_transmission_disabled(
) -> None:

    if LIVE_ORDER_EXECUTION:

        raise RuntimeError(
            "LIVE_ORDER_EXECUTION must remain False"
        )

    if DEMO_ORDER_EXECUTION:

        raise RuntimeError(
            "DEMO_ORDER_EXECUTION must remain False"
        )

    if not HARD_REAL_POST_LOCK:

        raise RuntimeError(
            "HARD_REAL_POST_LOCK must remain True"
        )

    if NETWORK_ACCESS_ALLOWED:

        raise RuntimeError(
            "NETWORK_ACCESS_ALLOWED must remain False"
        )


def real_order_post(
    *args: Any,
    **kwargs: Any,
) -> None:

    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise RuntimeError(
        "R28 UNIT C SAFETY LOCK: "
        "real order POST is forbidden"
    )


def demo_order_post(
    *args: Any,
    **kwargs: Any,
) -> None:

    global DEMO_POST_CALLED

    DEMO_POST_CALLED = True

    raise RuntimeError(
        "R28 UNIT C SAFETY LOCK: "
        "demo order POST is forbidden"
    )


def network_request(
    *args: Any,
    **kwargs: Any,
) -> None:

    global NETWORK_CALL_CALLED

    NETWORK_CALL_CALLED = True

    raise RuntimeError(
        "R28 UNIT C SAFETY LOCK: "
        "network access is forbidden"
    )


# ============================================================
# EXECUTION INTENT VALIDATION
# ============================================================

def validate_execution_intent(
    intent: ExecutionIntent,
) -> None:

    if not isinstance(
        intent,
        ExecutionIntent,
    ):

        raise TypeError(
            "Expected ExecutionIntent"
        )

    if not intent.intent_id.strip():

        raise ValueError(
            "intent_id cannot be empty"
        )

    if not intent.signal_id.strip():

        raise ValueError(
            "signal_id cannot be empty"
        )

    if not intent.symbol.strip():

        raise ValueError(
            "symbol cannot be empty"
        )

    if intent.symbol != (
        intent.symbol
        .strip()
        .upper()
    ):

        raise ValueError(
            "symbol must already be normalized"
        )

    if intent.side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            f"Invalid side: {intent.side}"
        )

    if intent.position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "Invalid position_side: "
            f"{intent.position_side}"
        )

    if intent.quantity <= 0:

        raise ValueError(
            "quantity must be greater than zero"
        )

    if not intent.quantity.is_finite():

        raise ValueError(
            "quantity must be finite"
        )

    if intent.leverage < (
        MIN_CONFIG_LEVERAGE
    ):

        raise ValueError(
            "leverage below minimum"
        )

    if intent.leverage > (
        MAX_CONFIG_LEVERAGE
    ):

        raise ValueError(
            "leverage exceeds configured maximum"
        )

    if not (
        intent.client_order_id
        .strip()
    ):

        raise ValueError(
            "client_order_id cannot be empty"
        )


# ============================================================
# SIDE / POSITION CONSISTENCY
# ============================================================

def validate_open_direction(
    side: str,
    position_side: str,
) -> None:

    allowed = {
        (
            "BUY",
            "LONG",
        ),
        (
            "SELL",
            "SHORT",
        ),
    }

    combination = (
        side,
        position_side,
    )

    if combination not in allowed:

        raise ValueError(
            "Invalid opening direction: "
            f"{side}/{position_side}"
        )


# ============================================================
# PAYLOAD CREATION
# ============================================================

def build_execution_payload(
    intent: ExecutionIntent,
) -> ExecutionPayload:

    validate_execution_intent(
        intent
    )

    validate_open_direction(
        intent.side,
        intent.position_side,
    )

    quantity_text = (
        normalize_decimal_string(
            intent.quantity
        )
    )

    if Decimal(
        quantity_text
    ) <= 0:

        raise ValueError(
            "Serialized quantity "
            "must remain positive"
        )

    return ExecutionPayload(
        symbol=intent.symbol,
        side=intent.side,
        position_side=(
            intent.position_side
        ),
        order_type="MARKET",
        quantity=quantity_text,
        leverage=str(
            intent.leverage
        ),
        margin_mode=MARGIN_MODE,
        client_order_id=(
            intent.client_order_id
        ),
        reduce_only=False,
    )


# ============================================================
# PAYLOAD TO DICTIONARY
# ============================================================

def execution_payload_dict(
    payload: ExecutionPayload,
) -> Dict[str, Any]:

    if not isinstance(
        payload,
        ExecutionPayload,
    ):

        raise TypeError(
            "Expected ExecutionPayload"
        )

    return {
        "symbol": (
            payload.symbol
        ),
        "side": (
            payload.side
        ),
        "positionSide": (
            payload.position_side
        ),
        "orderType": (
            payload.order_type
        ),
        "quantity": (
            payload.quantity
        ),
        "leverage": (
            payload.leverage
        ),
        "marginMode": (
            payload.margin_mode
        ),
        "clientOrderId": (
            payload.client_order_id
        ),
        "reduceOnly": (
            payload.reduce_only
        ),
    }


# ============================================================
# PAYLOAD VALIDATION
# ============================================================

def validate_execution_payload(
    payload: ExecutionPayload,
) -> None:

    if not payload.symbol:

        raise ValueError(
            "payload symbol cannot be empty"
        )

    if payload.side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            "payload side invalid"
        )

    if payload.position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "payload position side invalid"
        )

    validate_open_direction(
        payload.side,
        payload.position_side,
    )

    if payload.order_type != "MARKET":

        raise ValueError(
            "UNIT C expects MARKET order type"
        )

    try:

        quantity = Decimal(
            payload.quantity
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:

        raise ValueError(
            "payload quantity invalid"
        ) from exc

    if not quantity.is_finite():

        raise ValueError(
            "payload quantity must be finite"
        )

    if quantity <= 0:

        raise ValueError(
            "payload quantity must be positive"
        )

    try:

        leverage = int(
            payload.leverage
        )

    except (
        ValueError,
        TypeError,
    ) as exc:

        raise ValueError(
            "payload leverage invalid"
        ) from exc

    if leverage < (
        MIN_CONFIG_LEVERAGE
    ):

        raise ValueError(
            "payload leverage below minimum"
        )

    if leverage > (
        MAX_CONFIG_LEVERAGE
    ):

        raise ValueError(
            "payload leverage above maximum"
        )

    if payload.margin_mode != (
        MARGIN_MODE
    ):

        raise ValueError(
            "payload margin mode invalid"
        )

    if not (
        payload.client_order_id
        .strip()
    ):

        raise ValueError(
            "payload client order ID empty"
        )

    if payload.reduce_only is not False:

        raise ValueError(
            "opening payload cannot "
            "be reduce-only"
        )


# ============================================================
# INTENT FINGERPRINT
# ============================================================

def build_intent_fingerprint(
    intent: ExecutionIntent,
) -> str:

    validate_execution_intent(
        intent
    )

    canonical = stable_json(
        {
            "intent_id": (
                intent.intent_id
            ),
            "signal_id": (
                intent.signal_id
            ),
            "symbol": (
                intent.symbol
            ),
            "side": (
                intent.side
            ),
            "position_side": (
                intent.position_side
            ),
            "quantity": (
                normalize_decimal_string(
                    intent.quantity
                )
            ),
            "leverage": (
                intent.leverage
            ),
            "client_order_id": (
                intent.client_order_id
            ),
        }
    )

    return sha256_hex(
        canonical
    )


# ============================================================
# PAYLOAD FINGERPRINT
# ============================================================

def build_payload_fingerprint(
    payload: ExecutionPayload,
) -> str:

    validate_execution_payload(
        payload
    )

    canonical_payload = (
        stable_json(
            execution_payload_dict(
                payload
            )
        )
    )

    return sha256_hex(
        canonical_payload
    )


# ============================================================
# REQUEST FINGERPRINT
# ============================================================

def build_request_fingerprint(
    payload: ExecutionPayload,
) -> str:

    validate_execution_payload(
        payload
    )

    canonical_payload = (
        stable_json(
            execution_payload_dict(
                payload
            )
        )
    )

    request_material = (
        SHADOW_METHOD
        + "|"
        + REAL_ORDER_PATH
        + "|"
        + canonical_payload
    )

    return sha256_hex(
        request_material
    )


# ============================================================
# SHADOW COMMIT
# ============================================================

def build_shadow_commit(
    intent: ExecutionIntent,
    payload: ExecutionPayload,
) -> ShadowCommit:

    assert_transmission_disabled()

    validate_execution_intent(
        intent
    )

    validate_execution_payload(
        payload
    )

    if payload.symbol != (
        intent.symbol
    ):

        raise ValueError(
            "payload symbol differs from intent"
        )

    if payload.side != (
        intent.side
    ):

        raise ValueError(
            "payload side differs from intent"
        )

    if payload.position_side != (
        intent.position_side
    ):

        raise ValueError(
            "payload position side "
            "differs from intent"
        )

    if payload.quantity != (
        normalize_decimal_string(
            intent.quantity
        )
    ):

        raise ValueError(
            "payload quantity differs from intent"
        )

    if payload.leverage != (
        str(
            intent.leverage
        )
    ):

        raise ValueError(
            "payload leverage differs from intent"
        )

    if payload.client_order_id != (
        intent.client_order_id
    ):

        raise ValueError(
            "payload client order ID "
            "differs from intent"
        )

    payload_dict = (
        execution_payload_dict(
            payload
        )
    )

    canonical_payload = (
        stable_json(
            payload_dict
        )
    )

    intent_fingerprint = (
        build_intent_fingerprint(
            intent
        )
    )

    payload_fingerprint = (
        build_payload_fingerprint(
            payload
        )
    )

    request_fingerprint = (
        build_request_fingerprint(
            payload
        )
    )

    commit_material = stable_json(
        {
            "intent_id": (
                intent.intent_id
            ),
            "intent_fingerprint": (
                intent_fingerprint
            ),
            "payload_fingerprint": (
                payload_fingerprint
            ),
            "request_fingerprint": (
                request_fingerprint
            ),
            "method": (
                SHADOW_METHOD
            ),
            "path": (
                REAL_ORDER_PATH
            ),
        }
    )

    commit_token = (
        sha256_hex(
            commit_material
        )
    )

    return ShadowCommit(
        intent_id=(
            intent.intent_id
        ),
        intent_fingerprint=(
            intent_fingerprint
        ),
        payload_fingerprint=(
            payload_fingerprint
        ),
        request_fingerprint=(
            request_fingerprint
        ),
        commit_token=(
            commit_token
        ),
        method=(
            SHADOW_METHOD
        ),
        path=(
            REAL_ORDER_PATH
        ),
        canonical_payload=(
            canonical_payload
        ),
    )


# ============================================================
# TEST DATA FACTORY
# ============================================================

def make_test_intent(
    *,
    signal_id: str = (
        "r28-unit-c-signal-001"
    ),
    symbol: str = "BTCUSDT",
    side: str = "BUY",
    position_side: str = "LONG",
    quantity: Decimal = Decimal(
        "0.0005"
    ),
    leverage: int = 100,
) -> ExecutionIntent:

    intent_material = stable_json(
        {
            "signal_id": signal_id,
            "symbol": symbol,
            "side": side,
            "position_side": (
                position_side
            ),
            "quantity": (
                normalize_decimal_string(
                    quantity
                )
            ),
            "leverage": leverage,
        }
    )

    intent_id = (
        "r28i-"
        + sha256_hex(
            intent_material
        )[:24]
    )

    client_order_id = (
        "r28c-"
        + sha256_hex(
            intent_id
        )[:24]
    )

    return ExecutionIntent(
        intent_id=(
            intent_id
        ),
        signal_id=(
            signal_id
        ),
        symbol=(
            symbol
            .strip()
            .upper()
        ),
        side=(
            side
            .strip()
            .upper()
        ),
        position_side=(
            position_side
            .strip()
            .upper()
        ),
        quantity=quantity,
        leverage=leverage,
        client_order_id=(
            client_order_id
        ),
    )


# ============================================================
# TEST HELPERS
# ============================================================

def expect_exception(
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


def result_icon(
    passed: bool,
) -> str:

    return (
        "✅ PASS"
        if passed
        else "❌ FAIL"
    )


# ============================================================
# UNIT C DIAGNOSTIC
# ============================================================

def run_unit_c_diagnostic(
) -> Dict[str, bool]:

    assert_transmission_disabled()

    intent = (
        make_test_intent()
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    validate_execution_payload(
        payload
    )

    shadow = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    # --------------------------------------------------------
    # 1. PAYLOAD BUILDS
    # --------------------------------------------------------

    payload_created = (
        isinstance(
            payload,
            ExecutionPayload,
        )
    )

    # --------------------------------------------------------
    # 2. SYMBOL PRESERVED
    # --------------------------------------------------------

    symbol_preserved = (
        payload.symbol
        == intent.symbol
    )

    # --------------------------------------------------------
    # 3. SIDE PRESERVED
    # --------------------------------------------------------

    side_preserved = (
        payload.side
        == intent.side
    )

    # --------------------------------------------------------
    # 4. POSITION SIDE PRESERVED
    # --------------------------------------------------------

    position_side_preserved = (
        payload.position_side
        == intent.position_side
    )

    # --------------------------------------------------------
    # 5. QUANTITY PRESERVED
    # --------------------------------------------------------

    quantity_preserved = (
        payload.quantity
        == normalize_decimal_string(
            intent.quantity
        )
    )

    # --------------------------------------------------------
    # 6. LEVERAGE PRESERVED
    # --------------------------------------------------------

    leverage_preserved = (
        payload.leverage
        == str(
            intent.leverage
        )
    )

    # --------------------------------------------------------
    # 7. MARGIN MODE LOCKED
    # --------------------------------------------------------

    margin_mode_locked = (
        payload.margin_mode
        == "ISOLATED"
    )

    # --------------------------------------------------------
    # 8. MARKET TYPE LOCKED
    # --------------------------------------------------------

    market_type_locked = (
        payload.order_type
        == "MARKET"
    )

    # --------------------------------------------------------
    # 9. OPENING ORDER NOT REDUCE ONLY
    # --------------------------------------------------------

    reduce_only_safe = (
        payload.reduce_only
        is False
    )

    # --------------------------------------------------------
    # 10. DETERMINISTIC PAYLOAD
    # --------------------------------------------------------

    payload_two = (
        build_execution_payload(
            intent
        )
    )

    deterministic_payload = (
        stable_json(
            execution_payload_dict(
                payload
            )
        )
        ==
        stable_json(
            execution_payload_dict(
                payload_two
            )
        )
    )

    # --------------------------------------------------------
    # 11. DETERMINISTIC INTENT FINGERPRINT
    # --------------------------------------------------------

    intent_fp_1 = (
        build_intent_fingerprint(
            intent
        )
    )

    intent_fp_2 = (
        build_intent_fingerprint(
            intent
        )
    )

    deterministic_intent_fp = (
        intent_fp_1
        == intent_fp_2
    )

    # --------------------------------------------------------
    # 12. DETERMINISTIC PAYLOAD FINGERPRINT
    # --------------------------------------------------------

    payload_fp_1 = (
        build_payload_fingerprint(
            payload
        )
    )

    payload_fp_2 = (
        build_payload_fingerprint(
            payload
        )
    )

    deterministic_payload_fp = (
        payload_fp_1
        == payload_fp_2
    )

    # --------------------------------------------------------
    # 13. DETERMINISTIC REQUEST FINGERPRINT
    # --------------------------------------------------------

    request_fp_1 = (
        build_request_fingerprint(
            payload
        )
    )

    request_fp_2 = (
        build_request_fingerprint(
            payload
        )
    )

    deterministic_request_fp = (
        request_fp_1
        == request_fp_2
    )

    # --------------------------------------------------------
    # 14. DETERMINISTIC SHADOW COMMIT
    # --------------------------------------------------------

    shadow_two = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    deterministic_commit = (
        shadow.commit_token
        == shadow_two.commit_token
    )

    # --------------------------------------------------------
    # 15. DIFFERENT INTENT PRODUCES DIFFERENT COMMIT
    # --------------------------------------------------------

    second_intent = (
        make_test_intent(
            signal_id=(
                "r28-unit-c-signal-002"
            )
        )
    )

    second_payload = (
        build_execution_payload(
            second_intent
        )
    )

    second_shadow = (
        build_shadow_commit(
            second_intent,
            second_payload,
        )
    )

    unique_commit = (
        shadow.commit_token
        != second_shadow.commit_token
    )

    # --------------------------------------------------------
    # 16. PAYLOAD TAMPERING REJECTED
    # --------------------------------------------------------

    tampered_payload = (
        ExecutionPayload(
            symbol=payload.symbol,
            side=payload.side,
            position_side=(
                payload.position_side
            ),
            order_type=(
                payload.order_type
            ),
            quantity="0.9999",
            leverage=(
                payload.leverage
            ),
            margin_mode=(
                payload.margin_mode
            ),
            client_order_id=(
                payload.client_order_id
            ),
            reduce_only=(
                payload.reduce_only
            ),
        )
    )

    tampered_payload_rejected = (
        expect_exception(
            build_shadow_commit,
            intent,
            tampered_payload,
        )
    )

    # --------------------------------------------------------
    # 17. INVALID OPEN DIRECTION REJECTED
    # --------------------------------------------------------

    invalid_direction_intent = (
        make_test_intent(
            side="SELL",
            position_side="LONG",
        )
    )

    invalid_direction_rejected = (
        expect_exception(
            build_execution_payload,
            invalid_direction_intent,
        )
    )

    # --------------------------------------------------------
    # 18. EXCESSIVE LEVERAGE REJECTED
    # --------------------------------------------------------

    excessive_leverage_intent = (
        make_test_intent(
            leverage=101
        )
    )

    excessive_leverage_rejected = (
        expect_exception(
            build_execution_payload,
            excessive_leverage_intent,
        )
    )

    # --------------------------------------------------------
    # 19. ZERO QUANTITY REJECTED
    # --------------------------------------------------------

    zero_quantity_intent = (
        make_test_intent(
            quantity=Decimal(
                "0"
            )
        )
    )

    zero_quantity_rejected = (
        expect_exception(
            build_execution_payload,
            zero_quantity_intent,
        )
    )

    # --------------------------------------------------------
    # 20. NEGATIVE QUANTITY REJECTED
    # --------------------------------------------------------

    negative_quantity_intent = (
        make_test_intent(
            quantity=Decimal(
                "-0.0005"
            )
        )
    )

    negative_quantity_rejected = (
        expect_exception(
            build_execution_payload,
            negative_quantity_intent,
        )
    )

    # --------------------------------------------------------
    # 21. SHADOW METHOD LOCKED
    # --------------------------------------------------------

    shadow_method_locked = (
        shadow.method
        == "POST"
    )

    # --------------------------------------------------------
    # 22. SHADOW PATH LOCKED
    # --------------------------------------------------------

    shadow_path_locked = (
        shadow.path
        == REAL_ORDER_PATH
    )

    # --------------------------------------------------------
    # 23. REAL POST NOT CALLED
    # --------------------------------------------------------

    real_post_not_called = (
        REAL_POST_CALLED
        is False
    )

    # --------------------------------------------------------
    # 24. DEMO POST NOT CALLED
    # --------------------------------------------------------

    demo_post_not_called = (
        DEMO_POST_CALLED
        is False
    )

    # --------------------------------------------------------
    # 25. NETWORK NOT CALLED
    # --------------------------------------------------------

    network_not_called = (
        NETWORK_CALL_CALLED
        is False
    )

    # --------------------------------------------------------
    # 26. HARD REAL POST LOCK ACTIVE
    # --------------------------------------------------------

    hard_post_lock_active = (
        HARD_REAL_POST_LOCK
        is True
    )

    # --------------------------------------------------------
    # 27. LIVE EXECUTION DISABLED
    # --------------------------------------------------------

    live_execution_disabled = (
        LIVE_ORDER_EXECUTION
        is False
    )

    # --------------------------------------------------------
    # 28. DEMO EXECUTION DISABLED
    # --------------------------------------------------------

    demo_execution_disabled = (
        DEMO_ORDER_EXECUTION
        is False
    )

    # --------------------------------------------------------
    # 29. NETWORK ACCESS DISABLED
    # --------------------------------------------------------

    network_disabled = (
        NETWORK_ACCESS_ALLOWED
        is False
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    return {
        "Execution Payload Generated":
            payload_created,

        "Symbol Preserved":
            symbol_preserved,

        "Side Preserved":
            side_preserved,

        "Position Side Preserved":
            position_side_preserved,

        "Quantity Preserved":
            quantity_preserved,

        "Leverage Preserved":
            leverage_preserved,

        "Isolated Margin Locked":
            margin_mode_locked,

        "Market Order Type Locked":
            market_type_locked,

        "Reduce Only Safety":
            reduce_only_safe,

        "Deterministic Payload":
            deterministic_payload,

        "Deterministic Intent Fingerprint":
            deterministic_intent_fp,

        "Deterministic Payload Fingerprint":
            deterministic_payload_fp,

        "Deterministic Request Fingerprint":
            deterministic_request_fp,

        "Deterministic Shadow Commit":
            deterministic_commit,

        "Unique Intent Commit":
            unique_commit,

        "Payload Tampering Rejected":
            tampered_payload_rejected,

        "Invalid Open Direction Rejected":
            invalid_direction_rejected,

        "Excessive Leverage Rejected":
            excessive_leverage_rejected,

        "Zero Quantity Rejected":
            zero_quantity_rejected,

        "Negative Quantity Rejected":
            negative_quantity_rejected,

        "Shadow POST Method Locked":
            shadow_method_locked,

        "Shadow Order Path Locked":
            shadow_path_locked,

        "Real POST Never Called":
            real_post_not_called,

        "Demo POST Never Called":
            demo_post_not_called,

        "Network Never Called":
            network_not_called,

        "Hard Real POST Lock Active":
            hard_post_lock_active,

        "Live Execution Disabled":
            live_execution_disabled,

        "Demo Execution Disabled":
            demo_execution_disabled,

        "Network Access Disabled":
            network_disabled,
    }


# ============================================================
# PRINT DIAGNOSTIC
# ============================================================

def print_diagnostic(
    results: Dict[str, bool],
) -> None:

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        UNIT_NAME
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

    print(
        "R28 UNIT C "
        "PAYLOAD + SHADOW COMMIT GATES"
    )

    print(
        "-" * 60
    )

    for name, passed in (
        results.items()
    ):

        print(
            f"{name:<38} "
            f"{result_icon(passed)}"
        )

    print(
        "-" * 60
    )

    all_passed = all(
        results.values()
    )

    if all_passed:

        print(
            "✅ R28 UNIT C DIAGNOSTIC PASSED"
        )

        print(
            "✅ EXECUTION PAYLOAD SAFETY VALIDATED"
        )

        print(
            "✅ SHADOW COMMIT SAFETY VALIDATED"
        )

        print(
            "✅ UNIT C READY FOR INTEGRATION"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

    else:

        print(
            "❌ R28 UNIT C DIAGNOSTIC FAILED"
        )

        print(
            "❌ DO NOT INTEGRATE UNIT C"
        )

        print(
            "🛡 ORDER TRANSMISSION REMAINS DISABLED"
        )

    print(
        "=" * 60
    )

    if not all_passed:

        raise RuntimeError(
            "R28 UNIT C diagnostic failure"
        )


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions(
) -> None:

    assert_transmission_disabled()

    if REAL_POST_CALLED:

        raise RuntimeError(
            "SAFETY FAILURE: "
            "real POST was called"
        )

    if DEMO_POST_CALLED:

        raise RuntimeError(
            "SAFETY FAILURE: "
            "demo POST was called"
        )

    if NETWORK_CALL_CALLED:

        raise RuntimeError(
            "SAFETY FAILURE: "
            "network request was called"
        )


# ============================================================
# MAIN
# ============================================================

def main(
) -> None:

    results = (
        run_unit_c_diagnostic()
    )

    final_safety_assertions()

    print_diagnostic(
        results
    )

    final_safety_assertions()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print(
            "=" * 60
        )

        print(
            "❌ R28 UNIT C FATAL ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

        print(
            "=" * 60
        )

        raise
    
