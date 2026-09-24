# ============================================================
# BACKUP + STOP LOSS ORDERING UNIT TEST
#
# PROVES:
# LONG  : B1 > B2 > B3 > SL > FINAL LIQ
# SHORT : B1 < B2 < B3 < SL < FINAL LIQ
#
# ZERO WEEX WRITES
# ============================================================

BACKUP_BUFFER_PERCENT = 0.30

# Distance between B3 and final liquidation allocated to SL.
# 50% means SL sits halfway between B3 and final liquidation.
SL_SAFETY_FRACTION = 0.50


# ============================================================
# BACKUP TRIGGER
# ============================================================

def backup_price(direction, liquidation_price):

    buffer = BACKUP_BUFFER_PERCENT / 100.0

    if direction == "LONG":
        return round(
            liquidation_price * (1 + buffer),
            1
        )

    if direction == "SHORT":
        return round(
            liquidation_price * (1 - buffer),
            1
        )

    raise ValueError(
        "direction must be LONG or SHORT"
    )


# ============================================================
# TEST-ONLY LIQUIDATION RECALCULATION
# ============================================================

def simulate_new_liquidation(
    old_liquidation,
    old_qty,
    backup_qty,
    backup_fill_price,
    direction
):

    new_qty = old_qty + backup_qty
    weight = backup_qty / new_qty

    if direction == "LONG":

        new_liquidation = (
            old_liquidation
            - (
                (backup_fill_price - old_liquidation)
                * weight
            )
        )

    elif direction == "SHORT":

        new_liquidation = (
            old_liquidation
            + (
                (old_liquidation - backup_fill_price)
                * weight
            )
        )

    else:
        raise ValueError(
            "direction must be LONG or SHORT"
        )

    return round(new_liquidation, 1)


# ============================================================
# STOP LOSS AFTER BACKUP 3
# ============================================================

def calculate_final_stop_loss(
    direction,
    backup3_price,
    final_liquidation
):

    # --------------------------------------------------------
    # TEST POLICY:
    #
    # SL must sit between Backup 3 and final liquidation.
    #
    # LONG:
    # B3 > SL > LIQ
    #
    # SHORT:
    # B3 < SL < LIQ
    #
    # --------------------------------------------------------

    if not 0 < SL_SAFETY_FRACTION < 1:
        raise ValueError(
            "SL_SAFETY_FRACTION must be between 0 and 1"
        )

    distance = abs(
        backup3_price - final_liquidation
    )

    if direction == "LONG":

        stop_loss = (
            backup3_price
            - distance * SL_SAFETY_FRACTION
        )

    elif direction == "SHORT":

        stop_loss = (
            backup3_price
            + distance * SL_SAFETY_FRACTION
        )

    else:

        raise ValueError(
            "direction must be LONG or SHORT"
        )

    return round(stop_loss, 1)


# ============================================================
# RUN ONE COMPLETE DIRECTION TEST
# ============================================================

def run_direction_test(
    direction,
    initial_liquidation
):

    current_qty = 0.0004
    backup_qty = 0.0001

    print()
    print("==========================================")
    print(direction, "BACKUP + SL ORDERING TEST")
    print("==========================================")

    print(
        "INITIAL LIQUIDATION =",
        initial_liquidation
    )

    # ========================================================
    # BACKUP 1
    # ========================================================

    b1 = backup_price(
        direction,
        initial_liquidation
    )

    liq_after_b1 = simulate_new_liquidation(
        old_liquidation=initial_liquidation,
        old_qty=current_qty,
        backup_qty=backup_qty,
        backup_fill_price=b1,
        direction=direction
    )

    qty_after_b1 = current_qty + backup_qty

    print()
    print("B1 =", b1)
    print("LIQ AFTER B1 =", liq_after_b1)


    # ========================================================
    # BACKUP 2
    # ========================================================

    b2 = backup_price(
        direction,
        liq_after_b1
    )

    liq_after_b2 = simulate_new_liquidation(
        old_liquidation=liq_after_b1,
        old_qty=qty_after_b1,
        backup_qty=backup_qty,
        backup_fill_price=b2,
        direction=direction
    )

    qty_after_b2 = qty_after_b1 + backup_qty

    print()
    print("B2 =", b2)
    print("LIQ AFTER B2 =", liq_after_b2)


    # ========================================================
    # BACKUP 3
    # ========================================================

    b3 = backup_price(
        direction,
        liq_after_b2
    )

    liq_after_b3 = simulate_new_liquidation(
        old_liquidation=liq_after_b2,
        old_qty=qty_after_b2,
        backup_qty=backup_qty,
        backup_fill_price=b3,
        direction=direction
    )

    print()
    print("B3 =", b3)
    print(
        "FINAL LIQUIDATION AFTER B3 =",
        liq_after_b3
    )


    # ========================================================
    # FINAL STOP LOSS
    # ========================================================

    stop_loss = calculate_final_stop_loss(
        direction=direction,
        backup3_price=b3,
        final_liquidation=liq_after_b3
    )

    print()
    print("FINAL STOP LOSS =", stop_loss)


    # ========================================================
    # ORDERING ASSERTIONS
    # ========================================================

    if direction == "LONG":

        assert b1 > b2
        assert b2 > b3

        # B3 must be reached before SL
        assert b3 > stop_loss

        # SL must be reached before liquidation
        assert stop_loss > liq_after_b3

        print()
        print("LONG ORDER:")
        print(
            b1,
            ">",
            b2,
            ">",
            b3,
            ">",
            stop_loss,
            ">",
            liq_after_b3
        )

        print(
            "PASS: B1 > B2 > B3 > SL > LIQ"
        )


    elif direction == "SHORT":

        assert b1 < b2
        assert b2 < b3

        # B3 must be reached before SL
        assert b3 < stop_loss

        # SL must be reached before liquidation
        assert stop_loss < liq_after_b3

        print()
        print("SHORT ORDER:")
        print(
            b1,
            "<",
            b2,
            "<",
            b3,
            "<",
            stop_loss,
            "<",
            liq_after_b3
        )

        print(
            "PASS: B1 < B2 < B3 < SL < LIQ"
        )


    # ========================================================
    # ADDITIONAL SAFETY ASSERTIONS
    # ========================================================

    assert stop_loss != b3
    assert stop_loss != liq_after_b3

    print(
        "PASS: SL IS STRICTLY BETWEEN B3 AND LIQ"
    )

    return True


# ============================================================
# LONG TEST
# ============================================================

long_pass = run_direction_test(
    direction="LONG",
    initial_liquidation=80000.0
)


# ============================================================
# SHORT TEST
# ============================================================

short_pass = run_direction_test(
    direction="SHORT",
    initial_liquidation=90000.0
)


# ============================================================
# FINAL RESULT
# ============================================================

assert long_pass is True
assert short_pass is True

print()
print("==========================================")
print("BACKUP + SL ORDERING UNIT TEST PASS")
print("==========================================")

print("PASS: LONG B1 -> B2 -> B3 -> SL -> LIQ")
print("PASS: SHORT B1 -> B2 -> B3 -> SL -> LIQ")
print("PASS: SL REMAINS BEFORE LIQUIDATION")

print()
print("ZERO WEEX WRITES")
