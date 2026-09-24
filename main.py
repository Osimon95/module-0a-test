# ============================================================
# NEW BACKUP ENABLE GATE UNIT TEST
# STAGE: ENABLE / DISABLE BACKUPS 1-3
# ZERO WEEX WRITES
# ============================================================

NEW_BACKUPS_ENABLED = True

BACKUP_1_ENABLED = True
BACKUP_2_ENABLED = True
BACKUP_3_ENABLED = True

MAX_BACKUPS = 3


def backup_enabled(backup_number):

    # Master kill switch
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
# TEST
# ============================================================

print("==========================================")
print("NEW BACKUP ENABLE GATE TEST")
print("==========================================")

print("MASTER ENABLED =", NEW_BACKUPS_ENABLED)
print("BACKUP 1 ENABLED =", backup_enabled(1))
print("BACKUP 2 ENABLED =", backup_enabled(2))
print("BACKUP 3 ENABLED =", backup_enabled(3))
print("BACKUP 4 ENABLED =", backup_enabled(4))


# ============================================================
# ASSERTIONS
# ============================================================

assert backup_enabled(1) is True
assert backup_enabled(2) is True
assert backup_enabled(3) is True

# There must never be an accidental Backup 4
assert backup_enabled(4) is False


print()
print("==========================================")
print("NEW BACKUP ENABLE GATE TEST PASS")
print("==========================================")

print("PASS: BACKUP 1 ENABLED")
print("PASS: BACKUP 2 ENABLED")
print("PASS: BACKUP 3 ENABLED")
print("PASS: BACKUP 4 BLOCKED")
print("ZERO WEEX WRITES")
