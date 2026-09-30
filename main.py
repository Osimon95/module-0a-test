# ============================================================
# RECONSTRUCTION UNIT 6B
# UNIT 5B -> UNIT 6 QUALIFICATION / SIZING BRIDGE TEST
#
# PURPOSE:
#
# Prove that Unit 6 position sizing can only be reached after
# Unit 5B has produced a QUALIFIED entry.
#
# THIS TEST PROVES TWO PATHS:
#
# PATH 1:
# Unit 5B NOT QUALIFIED
# -> Unit 6 sizing BLOCKED
#
# PATH 2:
# Unit 5B QUALIFIED
# -> Unit 6 sizing ALLOWED
#
# IMPORTANT:
#
# - STANDALONE
# - DETERMINISTIC
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO WEEX ORDER PAYLOAD
# - NO TP
# - NO SL
# - NO BACKUP EXECUTION
#
# STRATEGY REQUIREMENTS:
#
# Initial committed margin = 5%
# Leverage = 100x
# Quantity step = 0.0001 BTC
# Minimum quantity = 0.0001 BTC
#
# ============================================================


from decimal import (
    Decimal,
    ROUND_DOWN,
)


# ============================================================
# UNIT 6 DECIMAL HELPER
# ============================================================


def reconstruction_unit_6_decimal(
    value,
):

    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


# ============================================================
# UNIT 6 QUANTITY NORMALIZER
# ============================================================


def reconstruction_unit_6_normalize_quantity(
    *,
    raw_quantity,
    quantity_step,
):

    raw_quantity = (
        reconstruction_unit_6_decimal(
            raw_quantity
        )
    )

    quantity_step = (
        reconstruction_unit_6_decimal(
            quantity_step
        )
    )

    if quantity_step <= 0:

        raise ValueError(
            "quantity_step must be positive"
        )

    steps = (
        raw_quantity
        / quantity_step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    normalized_quantity = (
        steps
        * quantity_step
    )

    return normalized_quantity


# ============================================================
# FROZEN UNIT 6 ENTRY INSTRUCTION ENGINE
# ============================================================


def reconstruction_unit_6_build_entry_instruction(
    *,
    unit_5_qualified,
    active_mode,
    direction,
    entry_price,
    available_balance,
    margin_percent,
    leverage,
    quantity_step,
    minimum_quantity,
):

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6 ENTRY INSTRUCTION START",
        flush=True,
    )

    entry_price = (
        reconstruction_unit_6_decimal(
            entry_price
        )
    )

    available_balance = (
        reconstruction_unit_6_decimal(
            available_balance
        )
    )

    margin_percent = (
        reconstruction_unit_6_decimal(
            margin_percent
        )
    )

    leverage = (
        reconstruction_unit_6_decimal(
            leverage
        )
    )

    quantity_step = (
        reconstruction_unit_6_decimal(
            quantity_step
        )
    )

    minimum_quantity = (
        reconstruction_unit_6_decimal(
            minimum_quantity
        )
    )

    result = {

        "valid":
            False,

        "reason":
            None,

        "unit_5_qualified":
            bool(
                unit_5_qualified
            ),

        "active_mode":
            active_mode,

        "direction":
            direction,

        "entry_price":
            entry_price,

        "available_balance":
            available_balance,

        "margin_percent":
            margin_percent,

        "leverage":
            leverage,

        "committed_margin":
            None,

        "position_notional":
            None,

        "raw_quantity":
            None,

        "quantity":
            None,

        "quantity_step":
            quantity_step,

        "minimum_quantity":
            minimum_quantity,

        # ----------------------------------------------------
        # EXECUTION FIREBREAK
        # ----------------------------------------------------

        "weex_post":
            False,

        "demo_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,

        "order_payload_generated":
            False,

        "tp_generated":
            False,

        "sl_generated":
            False,

        "backup_execution":
            False,
    }

    # ========================================================
    # UNIT 5 QUALIFICATION GUARD
    # ========================================================

    if not unit_5_qualified:

        result[
            "reason"
        ] = (
            "UNIT_5_NOT_QUALIFIED"
        )

        return result

    # ========================================================
    # MODE VALIDATION
    # ========================================================

    valid_modes = {
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    }

    if active_mode not in valid_modes:

        result[
            "reason"
        ] = (
            "INVALID_ACTIVE_MODE"
        )

        return result

    # ========================================================
    # DIRECTION VALIDATION
    # ========================================================

    if direction not in {
        "LONG",
        "SHORT",
    }:

        result[
            "reason"
        ] = (
            "INVALID_DIRECTION"
        )

        return result

    # ========================================================
    # ENTRY PRICE VALIDATION
    # ========================================================

    if entry_price <= 0:

        result[
            "reason"
        ] = (
            "INVALID_ENTRY_PRICE"
        )

        return result

    # ========================================================
    # BALANCE VALIDATION
    # ========================================================

    if available_balance <= 0:

        result[
            "reason"
        ] = (
            "INVALID_AVAILABLE_BALANCE"
        )

        return result

    # ========================================================
    # MARGIN VALIDATION
    # ========================================================

    if (
        margin_percent <= 0
        or
        margin_percent > 100
    ):

        result[
            "reason"
        ] = (
            "INVALID_MARGIN_PERCENT"
        )

        return result

    # ========================================================
    # LEVERAGE VALIDATION
    # ========================================================

    if leverage <= 0:

        result[
            "reason"
        ] = (
            "INVALID_LEVERAGE"
        )

        return result

    # ========================================================
    # QUANTITY RULE VALIDATION
    # ========================================================

    if quantity_step <= 0:

        result[
            "reason"
        ] = (
            "INVALID_QUANTITY_STEP"
        )

        return result

    if minimum_quantity <= 0:

        result[
            "reason"
        ] = (
            "INVALID_MINIMUM_QUANTITY"
        )

        return result

    # ========================================================
    # POSITION SIZING
    # ========================================================

    committed_margin = (
        available_balance
        * (
            margin_percent
            / Decimal(
                "100"
            )
        )
    )

    result[
        "committed_margin"
    ] = committed_margin

    position_notional = (
        committed_margin
        * leverage
    )

    result[
        "position_notional"
    ] = position_notional

    raw_quantity = (
        position_notional
        / entry_price
    )

    result[
        "raw_quantity"
    ] = raw_quantity

    quantity = (
        reconstruction_unit_6_normalize_quantity(
            raw_quantity=
                raw_quantity,

            quantity_step=
                quantity_step,
        )
    )

    result[
        "quantity"
    ] = quantity

    # ========================================================
    # MINIMUM QUANTITY GUARD
    # ========================================================

    if quantity < minimum_quantity:

        result[
            "reason"
        ] = (
            "QUANTITY_BELOW_MINIMUM"
        )

        return result

    # ========================================================
    # APPROVED
    # ========================================================

    result[
        "valid"
    ] = True

    result[
        "reason"
    ] = (
        "ENTRY_INSTRUCTION_APPROVED"
    )

    return result


# ============================================================
# UNIT 6B BRIDGE
# ============================================================


def reconstruction_unit_6b_bridge(
    *,
    unit_5b_result,
    available_balance,
    margin_percent,
    leverage,
    quantity_step,
    minimum_quantity,
):

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6B BRIDGE START",
        flush=True,
    )

    # ========================================================
    # VALIDATE UNIT 5B RESULT TYPE
    # ========================================================

    if not isinstance(
        unit_5b_result,
        dict,
    ):

        return {

            "valid":
                False,

            "reason":
                "INVALID_UNIT_5B_RESULT",

            "sizing_attempted":
                False,

            "unit_6_result":
                None,

            "weex_post":
                False,

            "demo_order":
                False,

            "real_order":
                False,

            "exchange_mutation":
                False,
        }

    # ========================================================
    # READ ONLY THE FIELDS UNIT 6B NEEDS
    # ========================================================

    qualified = bool(
        unit_5b_result.get(
            "qualified",
            False,
        )
    )

    qualification_reason = (
        unit_5b_result.get(
            "reason"
        )
    )

    active_mode = (
        unit_5b_result.get(
            "active_mode"
        )
    )

    direction = (
        unit_5b_result.get(
            "direction"
        )
    )

    live_price = (
        unit_5b_result.get(
            "live_price"
        )
    )

    print(
        "UNIT 6B UNIT 5B QUALIFIED = "
        + str(
            qualified
        ),
        flush=True,
    )

    print(
        "UNIT 6B UNIT 5B REASON = "
        + str(
            qualification_reason
        ),
        flush=True,
    )

    print(
        "UNIT 6B ACTIVE MODE = "
        + str(
            active_mode
        ),
        flush=True,
    )

    print(
        "UNIT 6B DIRECTION = "
        + str(
            direction
        ),
        flush=True,
    )

    print(
        "UNIT 6B ENTRY PRICE = "
        + str(
            live_price
        ),
        flush=True,
    )

    # ========================================================
    # CRITICAL QUALIFICATION FIREWALL
    #
    # Do not even call Unit 6 sizing when Unit 5B has rejected
    # the market setup.
    # ========================================================

    if not qualified:

        print(
            "UNIT 6B SIZING ATTEMPTED = FALSE",
            flush=True,
        )

        print(
            "UNIT 6B SIZING BLOCKED BY UNIT 5B",
            flush=True,
        )

        return {

            "valid":
                False,

            "reason":
                "UNIT_5B_NOT_QUALIFIED",

            "unit_5b_reason":
                qualification_reason,

            "sizing_attempted":
                False,

            "unit_6_result":
                None,

            "weex_post":
                False,

            "demo_order":
                False,

            "real_order":
                False,

            "exchange_mutation":
                False,

            "order_payload_generated":
                False,

            "tp_generated":
                False,

            "sl_generated":
                False,

            "backup_execution":
                False,
        }

    # ========================================================
    # QUALIFIED PATH
    #
    # Only now may Unit 6 calculate position size.
    # ========================================================

    print(
        "UNIT 6B QUALIFICATION GATE = PASS",
        flush=True,
    )

    print(
        "UNIT 6B SIZING ATTEMPTED = TRUE",
        flush=True,
    )

    unit_6_result = (
        reconstruction_unit_6_build_entry_instruction(

            unit_5_qualified=
                True,

            active_mode=
                active_mode,

            direction=
                direction,

            entry_price=
                live_price,

            available_balance=
                available_balance,

            margin_percent=
                margin_percent,

            leverage=
                leverage,

            quantity_step=
                quantity_step,

            minimum_quantity=
                minimum_quantity,
        )
    )

    if not unit_6_result.get(
        "valid",
        False,
    ):

        return {

            "valid":
                False,

            "reason":
                "UNIT_6_SIZING_REJECTED",

            "unit_5b_reason":
                qualification_reason,

            "sizing_attempted":
                True,

            "unit_6_result":
                unit_6_result,

            "weex_post":
                False,

            "demo_order":
                False,

            "real_order":
                False,

            "exchange_mutation":
                False,

            "order_payload_generated":
                False,

            "tp_generated":
                False,

            "sl_generated":
                False,

            "backup_execution":
                False,
        }

    return {

        "valid":
            True,

        "reason":
            "UNIT_6B_ENTRY_INSTRUCTION_READY",

        "unit_5b_reason":
            qualification_reason,

        "sizing_attempted":
            True,

        "unit_6_result":
            unit_6_result,

        "weex_post":
            False,

        "demo_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,

        "order_payload_generated":
            False,

        "tp_generated":
            False,

        "sl_generated":
            False,

        "backup_execution":
            False,
    }


# ============================================================
# UNIT 6B STANDALONE TEST
# ============================================================


def reconstruction_unit_6b_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6B STANDALONE TEST START",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    # ========================================================
    # TEST PARAMETERS
    # ========================================================

    available_balance = (
        Decimal(
            "7.18945017"
        )
    )

    margin_percent = (
        Decimal(
            "5"
        )
    )

    leverage = (
        Decimal(
            "100"
        )
    )

    quantity_step = (
        Decimal(
            "0.0001"
        )
    )

    minimum_quantity = (
        Decimal(
            "0.0001"
        )
    )

    # ========================================================
    # TEST 1
    #
    # Simulate the CURRENT live Unit 5B condition.
    #
    # Latest observed state:
    #
    # SCALP
    # SHORT
    # NOT QUALIFIED
    # EMA_SEPARATION_BELOW_MINIMUM
    #
    # Expected:
    #
    # Unit 6 sizing MUST NOT RUN.
    # ========================================================

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 6B TEST 1 = NOT QUALIFIED PATH",
        flush=True,
    )

    rejected_unit_5b = {

        "qualified":
            False,

        "reason":
            "EMA_SEPARATION_BELOW_MINIMUM",

        "active_mode":
            "SCALP",

        "direction":
            "SHORT",

        "live_price":
            Decimal(
                "83472.4"
            ),
    }

    rejected_result = (
        reconstruction_unit_6b_bridge(

            unit_5b_result=
                rejected_unit_5b,

            available_balance=
                available_balance,

            margin_percent=
                margin_percent,

            leverage=
                leverage,

            quantity_step=
                quantity_step,

            minimum_quantity=
                minimum_quantity,
        )
    )

    assert (
        rejected_result[
            "valid"
        ]
        is False
    )

    assert (
        rejected_result[
            "reason"
        ]
        ==
        "UNIT_5B_NOT_QUALIFIED"
    )

    assert (
        rejected_result[
            "sizing_attempted"
        ]
        is False
    )

    assert (
        rejected_result[
            "unit_6_result"
        ]
        is None
    )

    print(
        "PASS: UNIT 6B NOT QUALIFIED SIGNAL BLOCKED",
        flush=True,
    )

    print(
        "PASS: UNIT 6 SIZING WAS NOT CALLED",
        flush=True,
    )

    # ========================================================
    # TEST 2
    #
    # Simulate a valid QUALIFIED Unit 5B signal.
    #
    # This does NOT mean the current market is qualified.
    #
    # It only proves the bridge behavior.
    # ========================================================

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 6B TEST 2 = QUALIFIED PATH",
        flush=True,
    )

    qualified_unit_5b = {

        "qualified":
            True,

        "reason":
            "ENTRY_QUALIFIED",

        "active_mode":
            "STRUCTURE",

        "direction":
            "LONG",

        "live_price":
            Decimal(
                "83500"
            ),
    }

    qualified_result = (
        reconstruction_unit_6b_bridge(

            unit_5b_result=
                qualified_unit_5b,

            available_balance=
                available_balance,

            margin_percent=
                margin_percent,

            leverage=
                leverage,

            quantity_step=
                quantity_step,

            minimum_quantity=
                minimum_quantity,
        )
    )

    assert (
        qualified_result[
            "valid"
        ]
        is True
    )

    assert (
        qualified_result[
            "reason"
        ]
        ==
        "UNIT_6B_ENTRY_INSTRUCTION_READY"
    )

    assert (
        qualified_result[
            "sizing_attempted"
        ]
        is True
    )

    unit_6_result = (
        qualified_result[
            "unit_6_result"
        ]
    )

    assert (
        unit_6_result
        is not None
    )

    assert (
        unit_6_result[
            "valid"
        ]
        is True
    )

    assert (
        unit_6_result[
            "reason"
        ]
        ==
        "ENTRY_INSTRUCTION_APPROVED"
    )

    assert (
        unit_6_result[
            "committed_margin"
        ]
        ==
        Decimal(
            "0.3594725085"
        )
    )

    assert (
        unit_6_result[
            "position_notional"
        ]
        ==
        Decimal(
            "35.9472508500"
        )
    )

    assert (
        unit_6_result[
            "quantity"
        ]
        ==
        Decimal(
            "0.0004"
        )
    )

    print(
        "PASS: UNIT 6B QUALIFIED SIGNAL REACHED UNIT 6",
        flush=True,
    )

    print(
        "UNIT 6B COMMITTED MARGIN = "
        + str(
            unit_6_result[
                "committed_margin"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6B POSITION NOTIONAL = "
        + str(
            unit_6_result[
                "position_notional"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6B NORMALIZED QUANTITY = "
        + str(
            unit_6_result[
                "quantity"
            ]
        ),
        flush=True,
    )

    # ========================================================
    # FINAL EXECUTION FIREBREAK
    # ========================================================

    for test_result in (
        rejected_result,
        qualified_result,
    ):

        assert (
            test_result[
                "weex_post"
            ]
            is False
        )

        assert (
            test_result[
                "demo_order"
            ]
            is False
        )

        assert (
            test_result[
                "real_order"
            ]
            is False
        )

        assert (
            test_result[
                "exchange_mutation"
            ]
            is False
        )

        assert (
            test_result[
                "order_payload_generated"
            ]
            is False
        )

        assert (
            test_result[
                "tp_generated"
            ]
            is False
        )

        assert (
            test_result[
                "sl_generated"
            ]
            is False
        )

        assert (
            test_result[
                "backup_execution"
            ]
            is False
        )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 6B EXECUTION FIREBREAK",
        flush=True,
    )

    print(
        "ZERO WEEX POST = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "NO WEEX ORDER PAYLOAD GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO TP GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO SL GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO BACKUP EXECUTION = TRUE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6B RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "rejected_path":
            rejected_result,

        "qualified_path":
            qualified_result,
    }


# ============================================================
# RUN UNIT 6B STANDALONE TEST
# ============================================================


if __name__ == "__main__":

    reconstruction_unit_6b_standalone_test()
