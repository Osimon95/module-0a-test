# ============================================================
# RECONSTRUCTION UNIT 7
# WEEX DEMO ENTRY PAYLOAD BUILDER
# STANDALONE ZERO-WRITE TEST
#
# PURPOSE:
# Build and validate the candidate WEEX demo entry payload
# from an already-qualified Unit 6 entry instruction.
#
# THIS UNIT DOES NOT:
# - POST to WEEX
# - submit a demo order
# - submit a real order
# - mutate exchange/account state
# - create backups
# - create an SL
#
# IMPORTANT:
# Unit 7 is PAYLOAD CONSTRUCTION ONLY.
# Actual demo submission belongs to the later execution unit.
# ============================================================

from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
import hashlib


# ============================================================
# BASIC HELPERS
# ============================================================

def unit7_now():
    return datetime.now(
        timezone.utc
    ).isoformat()


def unit7_log(message):
    print(
        f"{unit7_now()} {message}",
        flush=True,
    )


def unit7_decimal(value):
    try:
        return Decimal(
            str(value)
        )
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return None


# ============================================================
# UNIT 7 CONFIGURATION
# ============================================================

UNIT7_SYMBOL = "BTCSUSDT"

UNIT7_ALLOWED_DIRECTIONS = {
    "LONG",
    "SHORT",
}

UNIT7_ALLOWED_MODES = {
    "SCALP",
    "STRUCTURE",
    "BREAKOUT",
}

UNIT7_MIN_QUANTITY = Decimal(
    "0.0001"
)

UNIT7_QTY_STEP = Decimal(
    "0.0001"
)


# ============================================================
# CLIENT ORDER ID
# ============================================================

def reconstruction_unit_7_client_order_id(
    *,
    direction,
    quantity,
    entry_price,
):
    """
    Construct a deterministic test client-order ID.

    This is NOT submitted anywhere.
    """

    raw = (
        f"UNIT7|"
        f"{direction}|"
        f"{quantity}|"
        f"{entry_price}"
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]

    return (
        f"R7-{direction}-{digest}"
    )


# ============================================================
# QUANTITY VALIDATION
# ============================================================

def reconstruction_unit_7_quantity_valid(
    quantity,
):
    quantity = unit7_decimal(
        quantity
    )

    if quantity is None:
        return False

    if quantity <= 0:
        return False

    if quantity < UNIT7_MIN_QUANTITY:
        return False

    remainder = (
        quantity
        % UNIT7_QTY_STEP
    )

    if remainder != 0:
        return False

    return True


# ============================================================
# DIRECTION -> WEEX ORDER MAPPING
# ============================================================

def reconstruction_unit_7_order_mapping(
    direction,
):
    """
    Convert strategy direction into the candidate
    WEEX entry-order direction fields.

    LONG:
        BUY / LONG

    SHORT:
        SELL / SHORT
    """

    if direction == "LONG":
        return {
            "side": "BUY",
            "positionSide": "LONG",
        }

    if direction == "SHORT":
        return {
            "side": "SELL",
            "positionSide": "SHORT",
        }

    return None


# ============================================================
# SL FIELD GUARD
# ============================================================

def reconstruction_unit_7_contains_sl_fields(
    payload,
):
    """
    Unit 7 must NOT introduce stop-loss fields.

    This follows the already-tested SL-disabled design.
    """

    forbidden_sl_fields = {
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    }

    found = []

    for field in forbidden_sl_fields:
        if field in payload:
            found.append(
                field
            )

    return found


# ============================================================
# UNIT 7 PAYLOAD BUILDER
# ============================================================

def reconstruction_unit_7_build_demo_entry_payload(
    *,
    unit6_instruction,
):
    """
    Build the candidate WEEX DEMO entry payload.

    ZERO WRITE.

    unit6_instruction must already represent a
    qualified Unit 6 entry instruction.
    """

    result = {
        "valid": False,
        "reason": None,
        "payload": None,
        "client_order_id": None,
        "weex_post": False,
        "demo_order_sent": False,
        "real_order_sent": False,
        "exchange_mutation": False,
    }

    # --------------------------------------------------------
    # BASIC INPUT CHECK
    # --------------------------------------------------------

    if not isinstance(
        unit6_instruction,
        dict,
    ):
        result["reason"] = (
            "INVALID_UNIT6_INSTRUCTION"
        )

        return result

    # --------------------------------------------------------
    # QUALIFICATION GATE
    # --------------------------------------------------------

    qualified = (
        unit6_instruction.get(
            "qualified",
            False,
        )
    )

    if qualified is not True:
        result["reason"] = (
            "UNIT6_NOT_QUALIFIED"
        )

        return result

    # --------------------------------------------------------
    # MODE
    # --------------------------------------------------------

    active_mode = (
        unit6_instruction.get(
            "active_mode"
        )
    )

    if active_mode not in UNIT7_ALLOWED_MODES:
        result["reason"] = (
            "INVALID_ACTIVE_MODE"
        )

        return result

    # --------------------------------------------------------
    # DIRECTION
    # --------------------------------------------------------

    direction = (
        unit6_instruction.get(
            "direction"
        )
    )

    if direction not in UNIT7_ALLOWED_DIRECTIONS:
        result["reason"] = (
            "INVALID_DIRECTION"
        )

        return result

    # --------------------------------------------------------
    # ENTRY PRICE
    # --------------------------------------------------------

    entry_price = unit7_decimal(
        unit6_instruction.get(
            "entry_price"
        )
    )

    if (
        entry_price is None
        or entry_price <= 0
    ):
        result["reason"] = (
            "INVALID_ENTRY_PRICE"
        )

        return result

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    quantity = unit7_decimal(
        unit6_instruction.get(
            "quantity"
        )
    )

    if not reconstruction_unit_7_quantity_valid(
        quantity
    ):
        result["reason"] = (
            "INVALID_QUANTITY"
        )

        return result

    # --------------------------------------------------------
    # ORDER DIRECTION MAPPING
    # --------------------------------------------------------

    mapping = (
        reconstruction_unit_7_order_mapping(
            direction
        )
    )

    if mapping is None:
        result["reason"] = (
            "ORDER_MAPPING_FAILED"
        )

        return result

    # --------------------------------------------------------
    # CLIENT ORDER ID
    # --------------------------------------------------------

    client_order_id = (
        reconstruction_unit_7_client_order_id(
            direction=direction,
            quantity=quantity,
            entry_price=entry_price,
        )
    )

    # --------------------------------------------------------
    # BUILD CANDIDATE DEMO ENTRY PAYLOAD
    #
    # IMPORTANT:
    # NO SL FIELDS.
    #
    # This payload is constructed in memory only.
    # --------------------------------------------------------

    payload = {
        "symbol": UNIT7_SYMBOL,
        "side": mapping["side"],
        "positionSide": (
            mapping["positionSide"]
        ),
        "type": "MARKET",
        "quantity": format(
            quantity,
            "f",
        ),
        "newClientOrderId": (
            client_order_id
        ),
    }

    # --------------------------------------------------------
    # SL GUARD
    # --------------------------------------------------------

    sl_fields = (
        reconstruction_unit_7_contains_sl_fields(
            payload
        )
    )

    if sl_fields:
        result["reason"] = (
            "FORBIDDEN_SL_FIELDS_PRESENT"
        )

        result["sl_fields"] = (
            sl_fields
        )

        return result

    # --------------------------------------------------------
    # FINAL PAYLOAD FIELD VALIDATION
    # --------------------------------------------------------

    required_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    missing_fields = (
        required_fields
        - set(
            payload.keys()
        )
    )

    if missing_fields:
        result["reason"] = (
            "MISSING_REQUIRED_FIELDS"
        )

        result["missing_fields"] = sorted(
            missing_fields
        )

        return result

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    result["valid"] = True

    result["reason"] = (
        "UNIT7_PAYLOAD_VALID"
    )

    result["payload"] = (
        payload
    )

    result["client_order_id"] = (
        client_order_id
    )

    return result


# ============================================================
# UNIT 7 STANDALONE TEST
# ============================================================

def reconstruction_unit_7_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    unit7_log(
        "RECONSTRUCTION UNIT 7 STANDALONE TEST START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # SIMULATED QUALIFIED UNIT 6 INSTRUCTION
    #
    # This intentionally does NOT read live account state.
    # It does NOT call Unit 6C.
    # It does NOT contact WEEX.
    # --------------------------------------------------------

    simulated_unit6_instruction = {
        "qualified": True,
        "active_mode": "STRUCTURE",
        "direction": "LONG",
        "entry_price": Decimal(
            "85000.0"
        ),
        "quantity": Decimal(
            "0.0004"
        ),
    }

    unit7_log(
        "UNIT 7 TEST INPUT SOURCE = "
        "DETERMINISTIC SIMULATED UNIT 6 INSTRUCTION"
    )

    unit7_log(
        "UNIT 7 TEST QUALIFIED = "
        f"{simulated_unit6_instruction['qualified']}"
    )

    unit7_log(
        "UNIT 7 TEST ACTIVE MODE = "
        f"{simulated_unit6_instruction['active_mode']}"
    )

    unit7_log(
        "UNIT 7 TEST DIRECTION = "
        f"{simulated_unit6_instruction['direction']}"
    )

    unit7_log(
        "UNIT 7 TEST ENTRY PRICE = "
        f"{simulated_unit6_instruction['entry_price']}"
    )

    unit7_log(
        "UNIT 7 TEST QUANTITY = "
        f"{simulated_unit6_instruction['quantity']}"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # BUILD PAYLOAD
    # --------------------------------------------------------

    result = (
        reconstruction_unit_7_build_demo_entry_payload(
            unit6_instruction=(
                simulated_unit6_instruction
            ),
        )
    )

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    unit7_log(
        "UNIT 7 PAYLOAD VALID = "
        f"{result['valid']}"
    )

    unit7_log(
        "UNIT 7 RESULT REASON = "
        f"{result['reason']}"
    )

    unit7_log(
        "UNIT 7 CLIENT ORDER ID = "
        f"{result['client_order_id']}"
    )

    payload = result.get(
        "payload"
    )

    unit7_log(
        "UNIT 7 CANDIDATE PAYLOAD = "
        f"{payload}"
    )

    # --------------------------------------------------------
    # PAYLOAD MUST EXIST
    # --------------------------------------------------------

    assert (
        result["valid"] is True
    ), (
        "UNIT 7 FAILED: "
        "PAYLOAD DID NOT VALIDATE"
    )

    assert (
        isinstance(
            payload,
            dict,
        )
    ), (
        "UNIT 7 FAILED: "
        "PAYLOAD NOT CREATED"
    )

    # --------------------------------------------------------
    # VERIFY SYMBOL
    # --------------------------------------------------------

    assert (
        payload["symbol"]
        == UNIT7_SYMBOL
    ), (
        "UNIT 7 FAILED: "
        "SYMBOL MISMATCH"
    )

    # --------------------------------------------------------
    # VERIFY LONG MAPPING
    # --------------------------------------------------------

    assert (
        payload["side"]
        == "BUY"
    ), (
        "UNIT 7 FAILED: "
        "LONG SIDE MAPPING"
    )

    assert (
        payload["positionSide"]
        == "LONG"
    ), (
        "UNIT 7 FAILED: "
        "LONG POSITION SIDE MAPPING"
    )

    # --------------------------------------------------------
    # VERIFY MARKET ORDER
    # --------------------------------------------------------

    assert (
        payload["type"]
        == "MARKET"
    ), (
        "UNIT 7 FAILED: "
        "ORDER TYPE IS NOT MARKET"
    )

    # --------------------------------------------------------
    # VERIFY QUANTITY
    # --------------------------------------------------------

    assert (
        payload["quantity"]
        == "0.0004"
    ), (
        "UNIT 7 FAILED: "
        "QUANTITY MISMATCH"
    )

    # --------------------------------------------------------
    # VERIFY CLIENT ORDER ID
    # --------------------------------------------------------

    assert (
        payload[
            "newClientOrderId"
        ]
        == result[
            "client_order_id"
        ]
    ), (
        "UNIT 7 FAILED: "
        "CLIENT ORDER ID MISMATCH"
    )

    # --------------------------------------------------------
    # VERIFY SL DISABLED
    # --------------------------------------------------------

    sl_fields = (
        reconstruction_unit_7_contains_sl_fields(
            payload
        )
    )

    assert (
        sl_fields == []
    ), (
        "UNIT 7 FAILED: "
        f"SL FIELDS PRESENT {sl_fields}"
    )

    unit7_log(
        "PASS: UNIT 7 SL-DISABLED PAYLOAD GUARD"
    )

    unit7_log(
        "UNIT 7 SL TRIGGER PRESENT = "
        f"{'slTriggerPrice' in payload}"
    )

    unit7_log(
        "UNIT 7 SL WORKING TYPE PRESENT = "
        f"{'SlWorkingType' in payload}"
    )

    # --------------------------------------------------------
    # VERIFY ZERO-WRITE FIREBREAK
    # --------------------------------------------------------

    assert (
        result["weex_post"]
        is False
    )

    assert (
        result["demo_order_sent"]
        is False
    )

    assert (
        result["real_order_sent"]
        is False
    )

    assert (
        result["exchange_mutation"]
        is False
    )

    print(
        "-" * 80,
        flush=True,
    )

    unit7_log(
        "PASS: UNIT 7 EXECUTION FIREBREAK"
    )

    unit7_log(
        "ZERO WEEX POST = TRUE"
    )

    unit7_log(
        "ZERO DEMO ORDER = TRUE"
    )

    unit7_log(
        "ZERO REAL ORDER = TRUE"
    )

    unit7_log(
        "ZERO EXCHANGE MUTATION = TRUE"
    )

    unit7_log(
        "NO SL GENERATED = TRUE"
    )

    unit7_log(
        "NO BACKUP EXECUTION = TRUE"
    )

    print(
        "-" * 80,
        flush=True,
    )

    unit7_log(
        "UNIT 7 STANDALONE TESTS = PASS"
    )

    unit7_log(
        "RECONSTRUCTION UNIT 7 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


# ============================================================
# RUN UNIT 7 STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    reconstruction_unit_7_standalone_test()
