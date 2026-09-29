# ============================================================
# RECONSTRUCTION UNIT 5
# SIGNAL / ENTRY QUALIFICATION ENGINE
#
# PURPOSE:
# Convert a confirmed market regime + direction into an
# auditable ENTRY QUALIFIED / NOT QUALIFIED decision.
#
# IMPORTANT:
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO ORDER PAYLOAD
# - NO POSITION SIZING
# - NO TP / SL
# - NO BACKUP EXECUTION
# ============================================================

from decimal import Decimal


# ------------------------------------------------------------
# UNIT 5 CONSTANTS
# ------------------------------------------------------------

U5_MIN_EMA19_50_SEPARATION_PCT = Decimal("0.05")

# Maximum distance allowed between price and EMA19.
# Prevents chasing a move that is already excessively extended.
U5_MAX_PRICE_EMA19_DISTANCE_PCT = Decimal("0.50")

# Minimum recent directional movement required.
# Kept deliberately small because this is confirmation,
# not the primary regime detector.
U5_MIN_MOMENTUM_PCT = Decimal("0.01")

U5_ALLOWED_MODES = {
    "SCALP",
    "STRUCTURE",
    "BREAKOUT",
}

U5_ALLOWED_DIRECTIONS = {
    "LONG",
    "SHORT",
}


# ------------------------------------------------------------
# SAFE DECIMAL CONVERSION
# ------------------------------------------------------------

def u5_decimal(value):
    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


# ------------------------------------------------------------
# PERCENT DISTANCE
# ------------------------------------------------------------

def u5_percent_distance(a, b):
    a = u5_decimal(a)
    b = u5_decimal(b)

    if b == 0:
        raise ValueError(
            "UNIT 5 percent-distance denominator is zero"
        )

    return (
        abs(a - b)
        / abs(b)
        * Decimal("100")
    )


# ------------------------------------------------------------
# CORE ENTRY QUALIFICATION ENGINE
# ------------------------------------------------------------

def reconstruction_unit_5_qualify_entry(
    *,
    active_mode,
    direction,
    live_price,
    ema19,
    ema50,
    ema200,
    ema19_50_separation_pct,
    short_term_move_pct,
):
    """
    Pure decision function.

    This function performs ZERO exchange operations.

    It returns an auditable dictionary describing every
    qualification condition.
    """

    result = {
        "valid": False,
        "entry_qualified": False,
        "reason": None,

        "active_mode": active_mode,
        "direction": direction,

        "mode_valid": False,
        "direction_valid": False,
        "ema_structure_valid": False,
        "ema_separation_valid": False,
        "price_location_valid": False,
        "momentum_confirmation": False,
        "anti_chase_check": False,

        "price_ema19_distance_pct": None,

        "order_payload_generated": False,
        "weex_post": False,
        "demo_order": False,
        "real_order": False,
        "exchange_mutation": False,
    }

    try:

        # ----------------------------------------------------
        # NORMALIZE
        # ----------------------------------------------------

        mode = (
            str(active_mode).strip().upper()
            if active_mode is not None
            else None
        )

        side = (
            str(direction).strip().upper()
            if direction is not None
            else None
        )

        price = u5_decimal(live_price)
        e19 = u5_decimal(ema19)
        e50 = u5_decimal(ema50)
        e200 = u5_decimal(ema200)

        separation = u5_decimal(
            ema19_50_separation_pct
        )

        momentum = u5_decimal(
            short_term_move_pct
        )

        result["active_mode"] = mode
        result["direction"] = side

        # ----------------------------------------------------
        # BASIC DATA VALIDATION
        # ----------------------------------------------------

        if price <= 0:
            result["reason"] = (
                "INVALID_LIVE_PRICE"
            )
            return result

        if (
            e19 <= 0
            or e50 <= 0
            or e200 <= 0
        ):
            result["reason"] = (
                "INVALID_EMA_VALUE"
            )
            return result

        # ----------------------------------------------------
        # MODE CHECK
        # ----------------------------------------------------

        result["mode_valid"] = (
            mode in U5_ALLOWED_MODES
        )

        if not result["mode_valid"]:
            result["reason"] = (
                "ACTIVE_MODE_NOT_ELIGIBLE"
            )
            result["valid"] = True
            return result

        # ----------------------------------------------------
        # DIRECTION CHECK
        # ----------------------------------------------------

        result["direction_valid"] = (
            side in U5_ALLOWED_DIRECTIONS
        )

        if not result["direction_valid"]:
            result["reason"] = (
                "NO_CONFIRMED_DIRECTION"
            )
            result["valid"] = True
            return result

        # ----------------------------------------------------
        # EMA STRUCTURE
        #
        # LONG:
        # EMA19 > EMA50 > EMA200
        #
        # SHORT:
        # EMA19 < EMA50 < EMA200
        # ----------------------------------------------------

        if side == "LONG":

            result["ema_structure_valid"] = (
                e19 > e50 > e200
            )

        elif side == "SHORT":

            result["ema_structure_valid"] = (
                e19 < e50 < e200
            )

        # ----------------------------------------------------
        # EMA SEPARATION
        # ----------------------------------------------------

        result["ema_separation_valid"] = (
            separation
            >= U5_MIN_EMA19_50_SEPARATION_PCT
        )

        # ----------------------------------------------------
        # PRICE LOCATION
        #
        # LONG:
        # Price should be above EMA19.
        #
        # SHORT:
        # Price should be below EMA19.
        # ----------------------------------------------------

        if side == "LONG":

            result["price_location_valid"] = (
                price > e19
            )

        elif side == "SHORT":

            result["price_location_valid"] = (
                price < e19
            )

        # ----------------------------------------------------
        # PRICE DISTANCE / ANTI-CHASE
        # ----------------------------------------------------

        price_distance = u5_percent_distance(
            price,
            e19,
        )

        result[
            "price_ema19_distance_pct"
        ] = price_distance

        result["anti_chase_check"] = (
            price_distance
            <= U5_MAX_PRICE_EMA19_DISTANCE_PCT
        )

        # ----------------------------------------------------
        # MOMENTUM CONFIRMATION
        #
        # IMPORTANT:
        # short_term_move_pct is expected to be SIGNED.
        #
        # Positive = upward movement
        # Negative = downward movement
        # ----------------------------------------------------

        if side == "LONG":

            result["momentum_confirmation"] = (
                momentum
                >= U5_MIN_MOMENTUM_PCT
            )

        elif side == "SHORT":

            result["momentum_confirmation"] = (
                momentum
                <= -U5_MIN_MOMENTUM_PCT
            )

        # ----------------------------------------------------
        # FINAL ENTRY DECISION
        # ----------------------------------------------------

        checks = [
            result["mode_valid"],
            result["direction_valid"],
            result["ema_structure_valid"],
            result["ema_separation_valid"],
            result["price_location_valid"],
            result["momentum_confirmation"],
            result["anti_chase_check"],
        ]

        result["entry_qualified"] = all(checks)

        # ----------------------------------------------------
        # EXPLICIT REASON
        # ----------------------------------------------------

        if result["entry_qualified"]:

            result["reason"] = (
                "ENTRY_CONDITIONS_CONFIRMED"
            )

        elif not result["ema_structure_valid"]:

            result["reason"] = (
                "EMA_STRUCTURE_NOT_CONFIRMED"
            )

        elif not result["ema_separation_valid"]:

            result["reason"] = (
                "EMA_SEPARATION_TOO_SMALL"
            )

        elif not result["price_location_valid"]:

            result["reason"] = (
                "PRICE_LOCATION_NOT_CONFIRMED"
            )

        elif not result["momentum_confirmation"]:

            result["reason"] = (
                "MOMENTUM_NOT_CONFIRMED"
            )

        elif not result["anti_chase_check"]:

            result["reason"] = (
                "ANTI_CHASE_BLOCK"
            )

        else:

            result["reason"] = (
                "ENTRY_NOT_QUALIFIED"
            )

        result["valid"] = True

        return result

    except Exception as exc:

        result["reason"] = (
            "UNIT_5_EXCEPTION: "
            + str(exc)
        )

        return result


# ============================================================
# UNIT 5 LOCAL TEST HARNESS
# ============================================================

def reconstruction_unit_5_local_tests():

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 5 LOCAL ENTRY QUALIFICATION TESTS START",
        flush=True,
    )

    all_pass = True

    # ========================================================
    # TEST 1
    # VALID LONG
    # ========================================================

    long_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction="LONG",
            live_price=Decimal("101.10"),
            ema19=Decimal("101.00"),
            ema50=Decimal("100.50"),
            ema200=Decimal("99.00"),
            ema19_50_separation_pct=Decimal("0.4975"),
            short_term_move_pct=Decimal("0.05"),
        )
    )

    test_1_pass = (
        long_result["valid"]
        and long_result["entry_qualified"]
        and long_result["reason"]
        == "ENTRY_CONDITIONS_CONFIRMED"
    )

    print(
        (
            "PASS"
            if test_1_pass
            else "FAIL"
        )
        + ": UNIT 5 VALID LONG",
        flush=True,
    )

    if not test_1_pass:
        all_pass = False
        print(
            "UNIT 5 LONG RESULT = "
            + str(long_result),
            flush=True,
        )

    # ========================================================
    # TEST 2
    # VALID SHORT
    # ========================================================

    short_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction="SHORT",
            live_price=Decimal("98.90"),
            ema19=Decimal("99.00"),
            ema50=Decimal("99.50"),
            ema200=Decimal("101.00"),
            ema19_50_separation_pct=Decimal("0.5025"),
            short_term_move_pct=Decimal("-0.05"),
        )
    )

    test_2_pass = (
        short_result["valid"]
        and short_result["entry_qualified"]
        and short_result["reason"]
        == "ENTRY_CONDITIONS_CONFIRMED"
    )

    print(
        (
            "PASS"
            if test_2_pass
            else "FAIL"
        )
        + ": UNIT 5 VALID SHORT",
        flush=True,
    )

    if not test_2_pass:
        all_pass = False
        print(
            "UNIT 5 SHORT RESULT = "
            + str(short_result),
            flush=True,
        )

    # ========================================================
    # TEST 3
    # WRONG PRICE LOCATION
    # ========================================================

    price_block_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction="SHORT",
            live_price=Decimal("99.20"),
            ema19=Decimal("99.00"),
            ema50=Decimal("99.50"),
            ema200=Decimal("101.00"),
            ema19_50_separation_pct=Decimal("0.50"),
            short_term_move_pct=Decimal("-0.05"),
        )
    )

    test_3_pass = (
        price_block_result["valid"]
        and not price_block_result[
            "entry_qualified"
        ]
        and price_block_result["reason"]
        == "PRICE_LOCATION_NOT_CONFIRMED"
    )

    print(
        (
            "PASS"
            if test_3_pass
            else "FAIL"
        )
        + ": UNIT 5 PRICE LOCATION BLOCK",
        flush=True,
    )

    if not test_3_pass:
        all_pass = False

    # ========================================================
    # TEST 4
    # MOMENTUM BLOCK
    # ========================================================

    momentum_block_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction="SHORT",
            live_price=Decimal("98.90"),
            ema19=Decimal("99.00"),
            ema50=Decimal("99.50"),
            ema200=Decimal("101.00"),
            ema19_50_separation_pct=Decimal("0.50"),
            short_term_move_pct=Decimal("0.02"),
        )
    )

    test_4_pass = (
        momentum_block_result["valid"]
        and not momentum_block_result[
            "entry_qualified"
        ]
        and momentum_block_result["reason"]
        == "MOMENTUM_NOT_CONFIRMED"
    )

    print(
        (
            "PASS"
            if test_4_pass
            else "FAIL"
        )
        + ": UNIT 5 MOMENTUM BLOCK",
        flush=True,
    )

    if not test_4_pass:
        all_pass = False

    # ========================================================
    # TEST 5
    # ANTI-CHASE BLOCK
    # ========================================================

    chase_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="BREAKOUT",
            direction="SHORT",
            live_price=Decimal("98.00"),
            ema19=Decimal("99.00"),
            ema50=Decimal("99.50"),
            ema200=Decimal("101.00"),
            ema19_50_separation_pct=Decimal("0.50"),
            short_term_move_pct=Decimal("-0.10"),
        )
    )

    test_5_pass = (
        chase_result["valid"]
        and not chase_result[
            "entry_qualified"
        ]
        and chase_result["reason"]
        == "ANTI_CHASE_BLOCK"
    )

    print(
        (
            "PASS"
            if test_5_pass
            else "FAIL"
        )
        + ": UNIT 5 ANTI-CHASE BLOCK",
        flush=True,
    )

    if not test_5_pass:
        all_pass = False

    # ========================================================
    # TEST 6
    # NO DIRECTION
    # ========================================================

    no_direction_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction=None,
            live_price=Decimal("100"),
            ema19=Decimal("99"),
            ema50=Decimal("98"),
            ema200=Decimal("97"),
            ema19_50_separation_pct=Decimal("1"),
            short_term_move_pct=Decimal("0.10"),
        )
    )

    test_6_pass = (
        no_direction_result["valid"]
        and not no_direction_result[
            "entry_qualified"
        ]
        and no_direction_result["reason"]
        == "NO_CONFIRMED_DIRECTION"
    )

    print(
        (
            "PASS"
            if test_6_pass
            else "FAIL"
        )
        + ": UNIT 5 NO-DIRECTION BLOCK",
        flush=True,
    )

    if not test_6_pass:
        all_pass = False

    # ========================================================
    # FIREBREAK VERIFICATION
    # ========================================================

    firebreak_results = [
        long_result,
        short_result,
        price_block_result,
        momentum_block_result,
        chase_result,
        no_direction_result,
    ]

    firebreak_pass = all(
        (
            result[
                "order_payload_generated"
            ] is False
            and result["weex_post"] is False
            and result["demo_order"] is False
            and result["real_order"] is False
            and result[
                "exchange_mutation"
            ] is False
        )
        for result in firebreak_results
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        (
            "PASS"
            if firebreak_pass
            else "FAIL"
        )
        + ": UNIT 5 EXECUTION FIREBREAK",
        flush=True,
    )

    print(
        "ZERO WEEX POST = "
        + str(firebreak_pass).upper(),
        flush=True,
    )

    print(
        "ZERO DEMO ORDER = "
        + str(firebreak_pass).upper(),
        flush=True,
    )

    print(
        "ZERO REAL ORDER = "
        + str(firebreak_pass).upper(),
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = "
        + str(firebreak_pass).upper(),
        flush=True,
    )

    if not firebreak_pass:
        all_pass = False

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 5 LOCAL ENTRY QUALIFICATION TESTS = "
        + (
            "PASS"
            if all_pass
            else "FAIL"
        ),
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    return all_pass


# ============================================================
# UNIT 5 LOCAL TEST EXECUTION
# ============================================================

UNIT_5_LOCAL_TEST_RESULT = (
    reconstruction_unit_5_local_tests()
)

if not UNIT_5_LOCAL_TEST_RESULT:
    raise RuntimeError(
        "RECONSTRUCTION UNIT 5 LOCAL TEST FAILURE"
  )
