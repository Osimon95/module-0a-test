# ============================================================
# RECONSTRUCTION UNIT 6
# STANDALONE POSITION SIZING + ENTRY INSTRUCTION TEST
#
# PURPOSE:
# Prove that a QUALIFIED Unit 5 signal can be transformed into
# a deterministic initial-trade instruction.
#
# THIS UNIT DOES NOT SUBMIT ANY ORDER.
#
# IMPORTANT:
# - STANDALONE TEST
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
# - Initial committed margin = 5% of available balance
# - Leverage = 100x
# - Quantity step = 0.0001 BTC
# - Minimum quantity = 0.0001 BTC
# ============================================================

from decimal import (
    Decimal,
    ROUND_DOWN,
)


def reconstruction_unit_6_decimal(
    value,
):
    """
    Convert input safely to Decimal.
    """

    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def reconstruction_unit_6_normalize_quantity(
    *,
    raw_quantity,
    quantity_step,
):
    """
    Round quantity DOWN to the exchange quantity step.

    Example:

    raw_quantity = 0.0004307
    step         = 0.0001

    result       = 0.0004
    """

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
    """
    Convert an approved Unit 5 signal into an initial
    position-sizing instruction.

    ZERO-WRITE ONLY.

    This function does NOT construct a WEEX API payload.
    """

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6 ENTRY INSTRUCTION START",
        flush=True,
    )

    # --------------------------------------------------------
    # INPUT NORMALIZATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RESULT SHELL
    # --------------------------------------------------------

    result = {
        "valid": False,
        "reason": None,

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

        # --------------------------------------------
        # EXECUTION FIREBREAK
        # --------------------------------------------

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

    # --------------------------------------------------------
    # UNIT 5 QUALIFICATION GUARD
    # --------------------------------------------------------

    if not unit_5_qualified:

        result[
            "reason"
        ] = (
            "UNIT_5_NOT_QUALIFIED"
        )

        return result

    # --------------------------------------------------------
    # ACTIVE MODE VALIDATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DIRECTION VALIDATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ENTRY PRICE VALIDATION
    # --------------------------------------------------------

    if entry_price <= 0:

        result[
            "reason"
        ] = (
            "INVALID_ENTRY_PRICE"
        )

        return result

    # --------------------------------------------------------
    # BALANCE VALIDATION
    # --------------------------------------------------------

    if available_balance <= 0:

        result[
            "reason"
        ] = (
            "INVALID_AVAILABLE_BALANCE"
        )

        return result

    # --------------------------------------------------------
    # MARGIN PERCENT VALIDATION
    # --------------------------------------------------------

    if (
        margin_percent
        <= 0
        or
        margin_percent
        > 100
    ):

        result[
            "reason"
        ] = (
            "INVALID_MARGIN_PERCENT"
        )

        return result

    # --------------------------------------------------------
    # LEVERAGE VALIDATION
    # --------------------------------------------------------

    if leverage <= 0:

        result[
            "reason"
        ] = (
            "INVALID_LEVERAGE"
        )

        return result

    # --------------------------------------------------------
    # QUANTITY RULE VALIDATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # INITIAL COMMITTED MARGIN
    #
    # Example:
    #
    # Balance = 7.18945017 USDT
    # Margin  = 5%
    #
    # committed margin
    # = 7.18945017 * 0.05
    # = 0.3594725085 USDT
    # --------------------------------------------------------

    committed_margin = (
        available_balance
        * (
            margin_percent
            / Decimal("100")
        )
    )

    result[
        "committed_margin"
    ] = committed_margin

    # --------------------------------------------------------
    # POSITION NOTIONAL
    #
    # 100x leverage:
    #
    # 0.3594725085 * 100
    # =
    # 35.9472508500 USDT
    # --------------------------------------------------------

    position_notional = (
        committed_margin
        * leverage
    )

    result[
        "position_notional"
    ] = position_notional

    # --------------------------------------------------------
    # RAW BTC QUANTITY
    #
    # notional / BTC entry price
    # --------------------------------------------------------

    raw_quantity = (
        position_notional
        / entry_price
    )

    result[
        "raw_quantity"
    ] = raw_quantity

    # --------------------------------------------------------
    # NORMALIZE TO WEEX QUANTITY STEP
    # --------------------------------------------------------

    quantity = (
        reconstruction_unit_6_normalize_quantity(
            raw_quantity=raw_quantity,
            quantity_step=quantity_step,
        )
    )

    result[
        "quantity"
    ] = quantity

    # --------------------------------------------------------
    # MINIMUM QUANTITY GUARD
    #
    # IMPORTANT:
    #
    # We DO NOT automatically increase an undersized order
    # to minimum quantity.
    #
    # If calculated risk sizing cannot meet minimum quantity,
    # the trade must be rejected instead.
    # --------------------------------------------------------

    if quantity < minimum_quantity:

        result[
            "reason"
        ] = (
            "QUANTITY_BELOW_MINIMUM"
        )

        return result

    # --------------------------------------------------------
    # FINAL APPROVAL
    # --------------------------------------------------------

    result[
        "valid"
    ] = True

    result[
        "reason"
    ] = (
        "ENTRY_INSTRUCTION_APPROVED"
    )

    return result


def reconstruction_unit_6_standalone_test():
    """
    Standalone deterministic Unit 6 test.

    Uses a simulated QUALIFIED Unit 5 signal.

    ZERO NETWORK WRITE.
    """

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6 STANDALONE TEST START",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # SIMULATED QUALIFIED UNIT 5 OUTPUT
    #
    # We deliberately DO NOT depend on live Unit 5B yet.
    # --------------------------------------------------------

    test_unit_5_qualified = True

    test_active_mode = (
        "STRUCTURE"
    )

    test_direction = (
        "LONG"
    )

    test_entry_price = (
        Decimal(
            "83500"
        )
    )

    # --------------------------------------------------------
    # TEST ACCOUNT PARAMETERS
    #
    # This is only a deterministic test value.
    # No account endpoint is called.
    # --------------------------------------------------------

    test_available_balance = (
        Decimal(
            "7.18945017"
        )
    )

    test_margin_percent = (
        Decimal(
            "5"
        )
    )

    test_leverage = (
        Decimal(
            "100"
        )
    )

    test_quantity_step = (
        Decimal(
            "0.0001"
        )
    )

    test_minimum_quantity = (
        Decimal(
            "0.0001"
        )
    )

    result = (
        reconstruction_unit_6_build_entry_instruction(
            unit_5_qualified=
                test_unit_5_qualified,

            active_mode=
                test_active_mode,

            direction=
                test_direction,

            entry_price=
                test_entry_price,

            available_balance=
                test_available_balance,

            margin_percent=
                test_margin_percent,

            leverage=
                test_leverage,

            quantity_step=
                test_quantity_step,

            minimum_quantity=
                test_minimum_quantity,
        )
    )

    # --------------------------------------------------------
    # EXPECTED VALUES
    # --------------------------------------------------------

    expected_committed_margin = (
        Decimal(
            "0.3594725085"
        )
    )

    expected_position_notional = (
        Decimal(
            "35.9472508500"
        )
    )

    expected_quantity = (
        Decimal(
            "0.0004"
        )
    )

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    print(
        "UNIT 6 VALID = "
        + str(
            result[
                "valid"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 REASON = "
        + str(
            result[
                "reason"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 ACTIVE MODE = "
        + str(
            result[
                "active_mode"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 DIRECTION = "
        + str(
            result[
                "direction"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 ENTRY PRICE = "
        + str(
            result[
                "entry_price"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 AVAILABLE BALANCE = "
        + str(
            result[
                "available_balance"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 MARGIN PERCENT = "
        + str(
            result[
                "margin_percent"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 LEVERAGE = "
        + str(
            result[
                "leverage"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 COMMITTED MARGIN = "
        + str(
            result[
                "committed_margin"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 POSITION NOTIONAL = "
        + str(
            result[
                "position_notional"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 RAW QUANTITY = "
        + str(
            result[
                "raw_quantity"
            ]
        ),
        flush=True,
    )

    print(
        "UNIT 6 NORMALIZED QUANTITY = "
        + str(
            result[
                "quantity"
            ]
        ),
        flush=True,
    )

    # --------------------------------------------------------
    # FUNCTIONAL ASSERTIONS
    # --------------------------------------------------------

    assert (
        result[
            "valid"
        ]
        is True
    )

    assert (
        result[
            "reason"
        ]
        ==
        "ENTRY_INSTRUCTION_APPROVED"
    )

    assert (
        result[
            "committed_margin"
        ]
        ==
        expected_committed_margin
    )

    assert (
        result[
            "position_notional"
        ]
        ==
        expected_position_notional
    )

    assert (
        result[
            "quantity"
        ]
        ==
        expected_quantity
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 6 POSITION SIZING",
        flush=True,
    )

    print(
        "EXPECTED COMMITTED MARGIN = "
        + str(
            expected_committed_margin
        ),
        flush=True,
    )

    print(
        "EXPECTED POSITION NOTIONAL = "
        + str(
            expected_position_notional
        ),
        flush=True,
    )

    print(
        "EXPECTED NORMALIZED QUANTITY = "
        + str(
            expected_quantity
        ),
        flush=True,
    )

    # --------------------------------------------------------
    # EXECUTION FIREBREAK ASSERTIONS
    # --------------------------------------------------------

    assert (
        result[
            "weex_post"
        ]
        is False
    )

    assert (
        result[
            "demo_order"
        ]
        is False
    )

    assert (
        result[
            "real_order"
        ]
        is False
    )

    assert (
        result[
            "exchange_mutation"
        ]
        is False
    )

    assert (
        result[
            "order_payload_generated"
        ]
        is False
    )

    assert (
        result[
            "tp_generated"
        ]
        is False
    )

    assert (
        result[
            "sl_generated"
        ]
        is False
    )

    assert (
        result[
            "backup_execution"
        ]
        is False
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 6 EXECUTION FIREBREAK",
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
        "RECONSTRUCTION UNIT 6 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


# ============================================================
# RUN UNIT 6 STANDALONE TEST
# ============================================================

if __name__ == "__main__":
    reconstruction_unit_6_standalone_test()
