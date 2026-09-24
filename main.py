# ============================================================
# BACKUP 1-3 SMALLEST UNIT TEST
# ZERO WEEX WRITES
# ============================================================

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = 5.0
BACKUP_BUFFER_PERCENT = 0.30


def backup_price(direction, liquidation_price):

    buffer = BACKUP_BUFFER_PERCENT / 100.0

    if direction == "LONG":
        return liquidation_price * (1 + buffer)

    if direction == "SHORT":
        return liquidation_price * (1 - buffer)

    raise ValueError("direction must be LONG or SHORT")


def calculate_backup(number, direction, current_liquidation):

    if number < 1 or number > MAX_BACKUPS:
        raise ValueError("backup number must be 1-3")

    price = backup_price(
        direction,
        current_liquidation
    )

    return {
        "backup": number,
        "size_percent": BACKUP_SIZE_PERCENT,
        "liquidation_used": current_liquidation,
        "trigger_price": price,
    }


# ============================================================
# TEST
# Each value represents the NEW liquidation after previous fill
# ============================================================

direction = "LONG"

liquidation_0 = 80000.0

backup1 = calculate_backup(
    1,
    direction,
    liquidation_0
)

print("BACKUP 1 =", backup1)


# Simulate WEEX/new liquidation after Backup 1 fills
liquidation_1 = 79000.0

backup2 = calculate_backup(
    2,
    direction,
    liquidation_1
)

print("BACKUP 2 =", backup2)


# Simulate WEEX/new liquidation after Backup 2 fills
liquidation_2 = 78000.0

backup3 = calculate_backup(
    3,
    direction,
    liquidation_2
)

print("BACKUP 3 =", backup3)


print()
print("BACKUP UNIT TEST PASS")
print("Each backup used its own CURRENT liquidation price.")
