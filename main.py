# ============================================================
# BACKUP LIQUIDATION RECALCULATION UNIT TEST
# STAGE: B1 -> NEW LIQ -> B2
# ZERO WEEX WRITES
# ============================================================

BACKUP_SIZE_PERCENT = 5.0
BACKUP_BUFFER_PERCENT = 0.30


def backup_price(direction, liquidation_price):

    buffer = BACKUP_BUFFER_PERCENT / 100.0

    if direction == "LONG":
        return liquidation_price * (1 + buffer)

    if direction == "SHORT":
        return liquidation_price * (1 - buffer)

    raise ValueError("direction must be LONG or SHORT")


def simulate_new_liquidation(
    old_liquidation,
    old_qty,
    backup_qty,
    backup_fill_price,
    direction
):

    # --------------------------------------------------------
    # TEST-ONLY liquidation movement model.
    #
    # Purpose:
    # prove that after a backup fill, the NEXT backup uses
    # a newly calculated liquidation instead of the original.
    #
    # This is NOT yet claimed to be WEEX's liquidation formula.
    # --------------------------------------------------------

    new_qty = old_qty + backup_qty

    weight = backup_qty / new_qty

    if direction == "LONG":

        new_liquidation = (
            old_liquidation
            - ((backup_fill_price - old_liquidation) * weight)
        )

    elif direction == "SHORT":

        new_liquidation = (
            old_liquidation
            + ((old_liquidation - backup_fill_price) * weight)
        )

    else:
        raise ValueError("direction must be LONG or SHORT")

    return round(new_liquidation, 1)


# ============================================================
# TEST POSITION
# ============================================================

direction = "LONG"

current_liquidation = 80000.0

current_qty = 0.0004

backup_qty = 0.0001


print("INITIAL LIQUIDATION =", current_liquidation)


# ============================================================
# BACKUP 1
# ============================================================

backup1_price = backup_price(
    direction,
    current_liquidation
)

backup1_price = round(backup1_price, 1)

print()
print("BACKUP 1 TRIGGER =", backup1_price)
print("BACKUP 1 LIQ USED =", current_liquidation)


# ============================================================
# SIMULATE BACKUP 1 FILL
# ============================================================

new_liquidation = simulate_new_liquidation(
    old_liquidation=current_liquidation,
    old_qty=current_qty,
    backup_qty=backup_qty,
    backup_fill_price=backup1_price,
    direction=direction
)

new_qty = current_qty + backup_qty

print()
print("BACKUP 1 FILLED")
print("OLD QTY =", current_qty)
print("NEW QTY =", new_qty)

print(
    "NEW LIQUIDATION AFTER BACKUP 1 =",
    new_liquidation
)


# ============================================================
# BACKUP 2 MUST USE NEW LIQUIDATION
# ============================================================

backup2_price = backup_price(
    direction,
    new_liquidation
)

backup2_price = round(backup2_price, 1)

print()
print("BACKUP 2 TRIGGER =", backup2_price)
print("BACKUP 2 LIQ USED =", new_liquidation)


# ============================================================
# ASSERTIONS
# ============================================================

assert new_liquidation != current_liquidation

assert backup2_price != backup1_price

expected_backup2 = round(
    new_liquidation
    * (1 + BACKUP_BUFFER_PERCENT / 100.0),
    1
)

assert backup2_price == expected_backup2


print()
print("==========================================")
print("LIQUIDATION RECALCULATION UNIT TEST PASS")
print("==========================================")

print(
    "PASS: Backup 2 used NEW liquidation:",
    new_liquidation
)

print("ZERO WEEX WRITES")
