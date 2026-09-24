# ============================================================
# NEW BACKUP CHAIN UNIT TEST
# STAGE:
# B1 -> NEW LIQ -> B2 -> NEW LIQ -> B3 -> STOP
#
# ZERO WEEX WRITES
# ============================================================

NEW_BACKUPS_ENABLED = True

BACKUP_1_ENABLED = True
BACKUP_2_ENABLED = True
BACKUP_3_ENABLED = True

MAX_BACKUPS = 3

BACKUP_SIZE_PERCENT = 5.0
BACKUP_BUFFER_PERCENT = 0.30


# ============================================================
# ENABLE GATE
# ============================================================

def backup_enabled(backup_number):

    if not NEW_BACKUPS_ENABLED:
        return False

    switches = {
        1: BACKUP_1_ENABLED,
        2: BACKUP_2_ENABLED,
        3: BACKUP_3_ENABLED,
    }

    if backup_number not in switches:
        return False

    if backup_number > MAX_BACKUPS:
        return False

    return switches[backup_number]


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

    # --------------------------------------------------------
    # TEST ONLY.
    #
    # This proves that each NEXT backup uses a newly
    # calculated liquidation price.
    #
    # This is NOT claimed to be WEEX's liquidation formula.
    # Production logic should use the updated liquidation
    # supplied by WEEX after an actual backup fill.
    # --------------------------------------------------------

    new_qty = old_qty + backup_qty

    weight = backup_qty / new_qty

    if direction == "LONG":

        new_liquidation = (
            old_liquidation
            - (
                (
                    backup_fill_price
                    - old_liquidation
                )
                * weight
            )
        )

    elif direction == "SHORT":

        new_liquidation = (
            old_liquidation
            + (
                (
                    old_liquidation
                    - backup_fill_price
                )
                * weight
            )
        )

    else:

        raise ValueError(
            "direction must be LONG or SHORT"
        )

    return round(new_liquidation, 1)


# ============================================================
# TEST POSITION
# ============================================================

direction = "LONG"

current_liquidation = 80000.0

current_qty = 0.0004

backup_qty = 0.0001


print("==========================================")
print("NEW BACKUP CHAIN UNIT TEST")
print("==========================================")

print()
print("DIRECTION =", direction)
print("INITIAL QTY =", current_qty)
print(
    "INITIAL LIQUIDATION =",
    current_liquidation
)

print()
print("MASTER ENABLED =", NEW_BACKUPS_ENABLED)
print(
    "BACKUP 1 ENABLED =",
    backup_enabled(1)
)
print(
    "BACKUP 2 ENABLED =",
    backup_enabled(2)
)
print(
    "BACKUP 3 ENABLED =",
    backup_enabled(3)
)
print(
    "BACKUP 4 ENABLED =",
    backup_enabled(4)
)


# ============================================================
# BACKUP 1
# ============================================================

assert backup_enabled(1) is True

backup1_liq_used = current_liquidation

backup1_price = backup_price(
    direction,
    backup1_liq_used
)

print()
print("------------------------------------------")
print("BACKUP 1")
print("------------------------------------------")

print(
    "BACKUP 1 LIQ USED =",
    backup1_liq_used
)

print(
    "BACKUP 1 TRIGGER =",
    backup1_price
)


# ============================================================
# SIMULATE BACKUP 1 FILL
# ============================================================

liq_after_b1 = simulate_new_liquidation(
    old_liquidation=current_liquidation,
    old_qty=current_qty,
    backup_qty=backup_qty,
    backup_fill_price=backup1_price,
    direction=direction
)

qty_after_b1 = current_qty + backup_qty

print("BACKUP 1 FILLED")

print(
    "QTY AFTER BACKUP 1 =",
    qty_after_b1
)

print(
    "NEW LIQUIDATION AFTER BACKUP 1 =",
    liq_after_b1
)


# ============================================================
# BACKUP 2
# ============================================================

assert backup_enabled(2) is True

backup2_liq_used = liq_after_b1

backup2_price = backup_price(
    direction,
    backup2_liq_used
)

print()
print("------------------------------------------")
print("BACKUP 2")
print("------------------------------------------")

print(
    "BACKUP 2 LIQ USED =",
    backup2_liq_used
)

print(
    "BACKUP 2 TRIGGER =",
    backup2_price
)


# ============================================================
# CRITICAL ASSERTION:
# B2 MUST USE LIQ AFTER B1
# ============================================================

assert backup2_liq_used == liq_after_b1

assert backup2_liq_used != backup1_liq_used

expected_b2 = round(
    liq_after_b1
    * (
        1
        + BACKUP_BUFFER_PERCENT / 100.0
    ),
    1
)

assert backup2_price == expected_b2


# ============================================================
# SIMULATE BACKUP 2 FILL
# ============================================================

liq_after_b2 = simulate_new_liquidation(
    old_liquidation=liq_after_b1,
    old_qty=qty_after_b1,
    backup_qty=backup_qty,
    backup_fill_price=backup2_price,
    direction=direction
)

qty_after_b2 = qty_after_b1 + backup_qty

print("BACKUP 2 FILLED")

print(
    "QTY AFTER BACKUP 2 =",
    qty_after_b2
)

print(
    "NEW LIQUIDATION AFTER BACKUP 2 =",
    liq_after_b2
)


# ============================================================
# BACKUP 3
# ============================================================

assert backup_enabled(3) is True

backup3_liq_used = liq_after_b2

backup3_price = backup_price(
    direction,
    backup3_liq_used
)

print()
print("------------------------------------------")
print("BACKUP 3")
print("------------------------------------------")

print(
    "BACKUP 3 LIQ USED =",
    backup3_liq_used
)

print(
    "BACKUP 3 TRIGGER =",
    backup3_price
)


# ============================================================
# CRITICAL ASSERTION:
# B3 MUST USE LIQ AFTER B2
# ============================================================

assert backup3_liq_used == liq_after_b2

assert backup3_liq_used != backup2_liq_used

expected_b3 = round(
    liq_after_b2
    * (
        1
        + BACKUP_BUFFER_PERCENT / 100.0
    ),
    1
)

assert backup3_price == expected_b3


# ============================================================
# SIMULATE BACKUP 3 FILL
# ============================================================

liq_after_b3 = simulate_new_liquidation(
    old_liquidation=liq_after_b2,
    old_qty=qty_after_b2,
    backup_qty=backup_qty,
    backup_fill_price=backup3_price,
    direction=direction
)

qty_after_b3 = qty_after_b2 + backup_qty

print("BACKUP 3 FILLED")

print(
    "QTY AFTER BACKUP 3 =",
    qty_after_b3
)

print(
    "NEW LIQUIDATION AFTER BACKUP 3 =",
    liq_after_b3
)


# ============================================================
# BACKUP 4 MUST BE BLOCKED
# ============================================================

print()
print("------------------------------------------")
print("BACKUP 4 SAFETY CHECK")
print("------------------------------------------")

backup4_allowed = backup_enabled(4)

print(
    "BACKUP 4 ENABLED =",
    backup4_allowed
)

assert backup4_allowed is False


# ============================================================
# FINAL CHAIN ASSERTIONS
# ============================================================

assert liq_after_b1 != current_liquidation

assert liq_after_b2 != liq_after_b1

assert liq_after_b3 != liq_after_b2

# ============================================================
# QTY ASSERTIONS
# FLOAT-SAFE
# ============================================================

assert abs(qty_after_b1 - 0.0005) < 1e-12
assert abs(qty_after_b2 - 0.0006) < 1e-12
assert abs(qty_after_b3 - 0.0007) < 1e-12


# ============================================================
# RESULT
# ============================================================

print()
print("==========================================")
print("NEW BACKUP CHAIN UNIT TEST PASS")
print("==========================================")

print(
    "PASS: B1 USED INITIAL LIQ =",
    backup1_liq_used
)

print(
    "PASS: B2 USED NEW LIQ =",
    backup2_liq_used
)

print(
    "PASS: B3 USED NEW LIQ =",
    backup3_liq_used
)

print("PASS: B4 BLOCKED")

print()
print(
    "FINAL TEST QTY =",
    qty_after_b3
)

print(
    "FINAL TEST LIQUIDATION =",
    liq_after_b3
)

print()
print("ZERO WEEX WRITES")

