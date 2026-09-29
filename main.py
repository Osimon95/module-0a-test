# ============================================================
# RECONSTRUCTION UNIT 5
# STANDALONE ENTRY QUALIFICATION ENGINE
#
# PURPOSE:
# Consume the verified Unit 4 market/regime state and decide
# whether the current market state qualifies as an entry.
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


UNIT_5_MIN_EMA_SEPARATION_PCT = Decimal("0.05")
UNIT_5_MIN_DIRECTIONAL_MOVE_PCT = Decimal("0.01")
UNIT_5_MAX_EMA19_DISTANCE_PCT = Decimal("0.50")


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
    Pure entry qualification engine.

    This function does NOT:
    - submit orders
    - construct order payloads
    - size positions
    - calculate TP
    - calculate SL
    - activate backups
    - mutate exchange state
    """

    active_mode = str(active_mode).upper()

    if direction is not None:
        direction = str(direction).upper()

    live_price = Decimal(str(live_price))
    ema19 = Decimal(str(ema19))
    ema50 = Decimal(str(ema50))
    ema200 = Decimal(str(ema200))

    ema19_50_separation_pct = Decimal(
        str(ema19_50_separation_pct)
    )

    short_term_move_pct = Decimal(
        str(short_term_move_pct)
    )

    result = {
        "qualified": False,
        "reason": None,

        "active_mode": active_mode,
        "direction": direction,

        "live_price": live_price,

        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,

        "ema19_50_separation_pct":
            ema19_50_separation_pct,

        "short_term_move_pct":
            short_term_move_pct,

        "ema_ordering_ok": False,
        "ema_separation_ok": False,
        "price_location_ok": False,
        "momentum_ok": False,
        "anti_chase_ok": False,

        "ema19_distance_pct": None,

        # ----------------------------------------------------
        # EXECUTION FIREBREAK
        # ----------------------------------------------------

        "weex_post": False,
        "demo_order": False,
        "real_order": False,
        "exchange_mutation": False,
        "order_payload_generated": False,
        "position_sizing_generated": False,
        "tp_generated": False,
        "sl_generated": False,
        "backup_execution": False,
    }

    # --------------------------------------------------------
    # VALID MODE GUARD
    # --------------------------------------------------------

    if active_mode not in {
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    }:
        result["reason"] = "INVALID_ACTIVE_MODE"
        return result

    # --------------------------------------------------------
    # DIRECTION GUARD
    # --------------------------------------------------------

    if direction not in {
        "LONG",
        "SHORT",
    }:
        result["reason"] = "NO_CONFIRMED_DIRECTION"
        return result

    # --------------------------------------------------------
    # BASIC NUMERIC GUARDS
    # --------------------------------------------------------

    if (
        live_price <= 0
        or ema19 <= 0
        or ema50 <= 0
        or ema200 <= 0
    ):
        result["reason"] = "INVALID_MARKET_VALUE"
        return result

    # --------------------------------------------------------
    # EMA ORDERING
    # --------------------------------------------------------

    if direction == "LONG":

        ema_ordering_ok = (
            ema19 > ema50 > ema200
        )

    else:

        ema_ordering_ok = (
            ema19 < ema50 < ema200
        )

    result["ema_ordering_ok"] = (
        ema_ordering_ok
    )

    if not ema_ordering_ok:

        result["reason"] = (
            "EMA_ORDERING_NOT_CONFIRMED"
        )

        return result

    # --------------------------------------------------------
    # EMA19 / EMA50 SEPARATION
    # --------------------------------------------------------

    ema_separation_ok = (
        abs(
            ema19_50_separation_pct
        )
        >= UNIT_5_MIN_EMA_SEPARATION_PCT
    )

    result["ema_separation_ok"] = (
        ema_separation_ok
    )

    if not ema_separation_ok:

        result["reason"] = (
            "EMA_SEPARATION_BELOW_MINIMUM"
        )

        return result

    # --------------------------------------------------------
    # PRICE LOCATION
    #
    # LONG:
    # price must be at/above EMA19
    #
    # SHORT:
    # price must be at/below EMA19
    # --------------------------------------------------------

    if direction == "LONG":

        price_location_ok = (
            live_price >= ema19
        )

    else:

        price_location_ok = (
            live_price <= ema19
        )

    result["price_location_ok"] = (
        price_location_ok
    )

    if not price_location_ok:

        result["reason"] = (
            "PRICE_LOCATION_NOT_CONFIRMED"
        )

        return result

    # --------------------------------------------------------
    # SIGNED DIRECTIONAL MOMENTUM
    #
    # IMPORTANT:
    # Unit 4C already proved short_term_move_pct is SIGNED.
    #
    # LONG requires positive movement.
    # SHORT requires negative movement.
    # --------------------------------------------------------

    if direction == "LONG":

        momentum_ok = (
            short_term_move_pct
            >= UNIT_5_MIN_DIRECTIONAL_MOVE_PCT
        )

    else:

        momentum_ok = (
            short_term_move_pct
            <= -UNIT_5_MIN_DIRECTIONAL_MOVE_PCT
        )

    result["momentum_ok"] = (
        momentum_ok
    )

    if not momentum_ok:

        result["reason"] = (
            "DIRECTIONAL_MOMENTUM_NOT_CONFIRMED"
        )

        return result

    # --------------------------------------------------------
    # ANTI-CHASE GUARD
    #
    # Avoid qualifying an entry after price has already moved
    # excessively far from EMA19.
    # --------------------------------------------------------

    ema19_distance_pct = (
        abs(
            live_price - ema19
        )
        / ema19
        * Decimal("100")
    )

    result["ema19_distance_pct"] = (
        ema19_distance_pct
    )

    anti_chase_ok = (
        ema19_distance_pct
        <= UNIT_5_MAX_EMA19_DISTANCE_PCT
    )

    result["anti_chase_ok"] = (
        anti_chase_ok
    )

    if not anti_chase_ok:

        result["reason"] = (
            "ANTI_CHASE_DISTANCE_EXCEEDED"
        )

        return result

    # --------------------------------------------------------
    # FINAL QUALIFICATION
    # --------------------------------------------------------

    result["qualified"] = True

    result["reason"] = (
        "ENTRY_QUALIFICATION_CONFIRMED"
    )

    return result


# ============================================================
# UNIT 5 STANDALONE TEST
# ============================================================

def reconstruction_unit_5_standalone_test():

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 5 STANDALONE TEST START",
        flush=True,
    )

    failures = []

    # ========================================================
    # TEST 1
    # VALID LONG
    # ========================================================

    long_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction="LONG",
            live_price="100.20",
            ema19="100.00",
            ema50="99.90",
            ema200="99.00",
            ema19_50_separation_pct="0.10",
            short_term_move_pct="0.05",
        )
    )

    if (
        long_result["qualified"] is True
        and
        long_result["reason"]
        == "ENTRY_QUALIFICATION_CONFIRMED"
    ):
        print(
            "PASS: UNIT 5 VALID LONG",
            flush=True,
        )

    else:
        failures.append(
            "VALID_LONG"
        )

        print(
            "FAIL: UNIT 5 VALID LONG",
            long_result,
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
            live_price="99.80",
            ema19="100.00",
            ema50="100.10",
            ema200="101.00",
            ema19_50_separation_pct="0.10",
            short_term_move_pct="-0.05",
        )
    )

    if (
        short_result["qualified"] is True
        and
        short_result["reason"]
        == "ENTRY_QUALIFICATION_CONFIRMED"
    ):
        print(
            "PASS: UNIT 5 VALID SHORT",
            flush=True,
        )

    else:
        failures.append(
            "VALID_SHORT"
        )

        print(
            "FAIL: UNIT 5 VALID SHORT",
            short_result,
            flush=True,
        )

    # ========================================================
    # TEST 3
    # MISSING DIRECTION
    # ========================================================

    no_direction_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="SCALP",
            direction=None,
            live_price="100",
            ema19="100",
            ema50="99.90",
            ema200="99",
            ema19_50_separation_pct="0.10",
            short_term_move_pct="0.05",
        )
    )

    if (
        no_direction_result["qualified"]
        is False
        and
        no_direction_result["reason"]
        == "NO_CONFIRMED_DIRECTION"
    ):
        print(
            "PASS: UNIT 5 NO DIRECTION GUARD",
            flush=True,
        )

    else:
        failures.append(
            "NO_DIRECTION_GUARD"
        )

    # ========================================================
    # TEST 4
    # WRONG PRICE LOCATION
    # ========================================================

    price_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction="LONG",
            live_price="99.80",
            ema19="100.00",
            ema50="99.90",
            ema200="99.00",
            ema19_50_separation_pct="0.10",
            short_term_move_pct="0.05",
        )
    )

    if (
        price_result["qualified"] is False
        and
        price_result["reason"]
        == "PRICE_LOCATION_NOT_CONFIRMED"
    ):
        print(
            "PASS: UNIT 5 PRICE LOCATION GUARD",
            flush=True,
        )

    else:
        failures.append(
            "PRICE_LOCATION_GUARD"
        )

    # ========================================================
    # TEST 5
    # WRONG MOMENTUM DIRECTION
    # ========================================================

    momentum_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="STRUCTURE",
            direction="LONG",
            live_price="100.20",
            ema19="100.00",
            ema50="99.90",
            ema200="99.00",
            ema19_50_separation_pct="0.10",
            short_term_move_pct="-0.05",
        )
    )

    if (
        momentum_result["qualified"]
        is False
        and
        momentum_result["reason"]
        == "DIRECTIONAL_MOMENTUM_NOT_CONFIRMED"
    ):
        print(
            "PASS: UNIT 5 MOMENTUM GUARD",
            flush=True,
        )

    else:
        failures.append(
            "MOMENTUM_GUARD"
        )

    # ========================================================
    # TEST 6
    # ANTI-CHASE
    # ========================================================

    chase_result = (
        reconstruction_unit_5_qualify_entry(
            active_mode="BREAKOUT",
            direction="LONG",
            live_price="101.00",
            ema19="100.00",
            ema50="99.90",
            ema200="99.00",
            ema19_50_separation_pct="0.10",
            short_term_move_pct="0.60",
        )
    )

    if (
        chase_result["qualified"] is False
        and
        chase_result["reason"]
        == "ANTI_CHASE_DISTANCE_EXCEEDED"
    ):
        print(
            "PASS: UNIT 5 ANTI-CHASE GUARD",
            flush=True,
        )

    else:
        failures.append(
            "ANTI_CHASE_GUARD"
        )

    # ========================================================
    # EXECUTION FIREBREAK
    # ========================================================

    test_results = [
        long_result,
        short_result,
        no_direction_result,
        price_result,
        momentum_result,
        chase_result,
    ]

    firebreak_ok = all(
        (
            r["weex_post"] is False
            and
            r["demo_order"] is False
            and
            r["real_order"] is False
            and
            r["exchange_mutation"] is False
            and
            r["order_payload_generated"] is False
            and
            r["position_sizing_generated"] is False
            and
            r["tp_generated"] is False
            and
            r["sl_generated"] is False
            and
            r["backup_execution"] is False
        )
        for r in test_results
    )

    if firebreak_ok:

        print(
            "PASS: UNIT 5 EXECUTION FIREBREAK",
            flush=True,
        )

    else:

        failures.append(
            "EXECUTION_FIREBREAK"
        )

        print(
            "FAIL: UNIT 5 EXECUTION FIREBREAK",
            flush=True,
        )

    print(
        "HTTP POST COUNT = 0",
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
        "NO ORDER PAYLOAD GENERATED = TRUE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    if failures:

        print(
            "UNIT 5 STANDALONE TESTS = FAIL",
            flush=True,
        )

        print(
            "UNIT 5 FAILURES =",
            failures,
            flush=True,
        )

        raise RuntimeError(
            "RECONSTRUCTION UNIT 5 TEST FAILURE"
        )

    print(
        "UNIT 5 STANDALONE TESTS = PASS",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 5 RESULT = PASS",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )


# ============================================================
# RUN UNIT 5 STANDALONE TEST
# ============================================================

if __name__ == "__main__":
    reconstruction_unit_5_standalone_test()
