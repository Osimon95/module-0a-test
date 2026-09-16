# ============================================================
# R36F.15.10.4a
# AUTO BREAKOUT + MODE-TRANSITION VALIDATION
# STANDALONE ZERO-WRITE TESTABLE UNIT
# ============================================================

import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ============================================================
# STAGE
# ============================================================

STAGE = "R36F.15.10.4a"

print("=" * 80)
print(f"{STAGE}: AUTO BREAKOUT + MODE-TRANSITION VALIDATION")
print("=" * 80)


# ============================================================
# HARD SAFETY FREEZE
# ============================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
WRITE_TRANSPORT = False
ORDER_SUBMISSION_ENABLED = False
FIRST_REAL_ORDER_ENABLED = False
FIRST_DEMO_ORDER_ENABLED = False
EXCHANGE_MUTATION_ENABLED = False


# ============================================================
# AUTO-MODE POLICY
# ============================================================

MODE_SCALP = "SCALP"
MODE_STRUCTURE = "STRUCTURE"
MODE_BREAKOUT = "BREAKOUT"

VALID_MODES = (
    MODE_SCALP,
    MODE_STRUCTURE,
    MODE_BREAKOUT,
)

EXCLUSIVE_MODE = True
MODE_CHANGE_CONFIRMATIONS = 3
ACTIVE_TRADE_MODE_LOCK = True

REEVALUATION_SECONDS = 60


# ============================================================
# DIAGNOSTIC STORAGE
# ============================================================

PASS_COUNT = 0
FAIL_COUNT = 0
DIAGNOSTICS = []


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def diagnostic(name, passed, detail=""):
    global PASS_COUNT
    global FAIL_COUNT

    passed = bool(passed)

    if passed:
        PASS_COUNT += 1
        status = "PASS"
    else:
        FAIL_COUNT += 1
        status = "FAIL"

    record = {
        "name": name,
        "passed": passed,
        "detail": str(detail),
    }

    DIAGNOSTICS.append(record)

    print(
        f"{utc_now()} DIAGNOSTIC {status}: "
        f"{name}"
    )

    if detail:
        print(
            f"{utc_now()}       {detail}"
        )

    return passed


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            f"{STAGE} "
            f"status={'PASS' if FAIL_COUNT == 0 else 'FAIL'} "
            f"real_execution={REAL_ORDER_EXECUTION} "
            f"demo_execution={DEMO_ORDER_EXECUTION} "
            f"write_transport={WRITE_TRANSPORT}\n"
        )

        encoded = body.encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain",
        )
        self.send_header(
            "Content-Length",
            str(len(encoded)),
        )
        self.end_headers()

        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    print(
        f"{utc_now()} "
        f"{STAGE}: HEALTH SERVER STARTED "
        f"ON PORT {port}"
    )

    return server


# ============================================================
# AUTO MODE CONTROLLER
# ============================================================

class AutoModeController:

    def __init__(
        self,
        initial_mode=MODE_SCALP,
        confirmations=MODE_CHANGE_CONFIRMATIONS,
    ):
        if initial_mode not in VALID_MODES:
            raise ValueError(
                f"INVALID_INITIAL_MODE:{initial_mode}"
            )

        self.active_mode = initial_mode
        self.pending_mode = None
        self.pending_count = 0

        self.confirmations = int(confirmations)

        self.trade_locked = False
        self.locked_trade_mode = None

        self.cycle = 0

    def snapshot(self):
        return {
            "cycle": self.cycle,
            "active_mode": self.active_mode,
            "pending_mode": self.pending_mode,
            "pending_count": self.pending_count,
            "trade_locked": self.trade_locked,
            "locked_trade_mode": self.locked_trade_mode,
        }

    def lock_trade(self):
        if not ACTIVE_TRADE_MODE_LOCK:
            return

        self.trade_locked = True
        self.locked_trade_mode = self.active_mode

        print(
            f"{utc_now()} "
            f"{STAGE} TRADE MODE LOCKED = "
            f"{self.locked_trade_mode}"
        )

    def unlock_trade(self):
        self.trade_locked = False
        self.locked_trade_mode = None

        print(
            f"{utc_now()} "
            f"{STAGE} TRADE MODE UNLOCKED"
        )

    def evaluate(self, raw_mode):

        self.cycle += 1

        if raw_mode not in VALID_MODES:
            raise ValueError(
                f"INVALID_RAW_MODE:{raw_mode}"
            )

        previous_active = self.active_mode

        # ----------------------------------------------------
        # ACTIVE TRADE MODE LOCK
        # ----------------------------------------------------

        if (
            ACTIVE_TRADE_MODE_LOCK
            and self.trade_locked
        ):
            self.pending_mode = None
            self.pending_count = 0

            print(
                f"{utc_now()} "
                f"{STAGE} CYCLE={self.cycle} "
                f"raw_mode={raw_mode} "
                f"active_mode={self.active_mode} "
                f"pending_mode=None "
                f"pending_count=0 "
                f"locked=True "
                f"reason=ACTIVE_TRADE_MODE_LOCK"
            )

            return self.snapshot()

        # ----------------------------------------------------
        # RAW MODE ALREADY ACTIVE
        # Cancel any pending transition.
        # ----------------------------------------------------

        if raw_mode == self.active_mode:

            self.pending_mode = None
            self.pending_count = 0

            print(
                f"{utc_now()} "
                f"{STAGE} CYCLE={self.cycle} "
                f"raw_mode={raw_mode} "
                f"active_mode={self.active_mode} "
                f"pending_mode=None "
                f"pending_count=0 "
                f"locked=False "
                f"reason=ACTIVE_MODE_CONFIRMED"
            )

            return self.snapshot()

        # ----------------------------------------------------
        # NEW CANDIDATE MODE
        # ----------------------------------------------------

        if self.pending_mode != raw_mode:

            self.pending_mode = raw_mode
            self.pending_count = 1

            print(
                f"{utc_now()} "
                f"{STAGE} CYCLE={self.cycle} "
                f"raw_mode={raw_mode} "
                f"active_mode={self.active_mode} "
                f"pending_mode={self.pending_mode} "
                f"pending_count={self.pending_count} "
                f"locked=False "
                f"reason=NEW_MODE_PENDING"
            )

            return self.snapshot()

        # ----------------------------------------------------
        # SAME CANDIDATE SEEN AGAIN
        # ----------------------------------------------------

        self.pending_count += 1

        # ----------------------------------------------------
        # CONFIRMATION THRESHOLD REACHED
        # ----------------------------------------------------

        if self.pending_count >= self.confirmations:

            new_mode = self.pending_mode

            self.active_mode = new_mode
            self.pending_mode = None
            self.pending_count = 0

            print(
                f"{utc_now()} "
                f"{STAGE} CYCLE={self.cycle} "
                f"raw_mode={raw_mode} "
                f"previous_active_mode={previous_active} "
                f"active_mode={self.active_mode} "
                f"pending_mode=None "
                f"pending_count=0 "
                f"locked=False "
                f"reason=THREE_CONFIRMATION_TRANSITION"
            )

            return self.snapshot()

        print(
            f"{utc_now()} "
            f"{STAGE} CYCLE={self.cycle} "
            f"raw_mode={raw_mode} "
            f"active_mode={self.active_mode} "
            f"pending_mode={self.pending_mode} "
            f"pending_count={self.pending_count} "
            f"locked=False "
            f"reason=MODE_CONFIRMATION_PENDING"
        )

        return self.snapshot()


# ============================================================
# TEST 1
# BASIC CONFIGURATION
# ============================================================

def test_configuration():

    print("-" * 80)
    print(
        f"{STAGE} TEST 1: CONFIGURATION"
    )
    print("-" * 80)

    diagnostic(
        "THREE_VALID_MODES",
        set(VALID_MODES)
        == {
            MODE_SCALP,
            MODE_STRUCTURE,
            MODE_BREAKOUT,
        },
    )

    diagnostic(
        "EXCLUSIVE_MODE_ENABLED",
        EXCLUSIVE_MODE is True,
    )

    diagnostic(
        "MODE_CHANGE_CONFIRMATIONS_EQUALS_3",
        MODE_CHANGE_CONFIRMATIONS == 3,
    )

    diagnostic(
        "ACTIVE_TRADE_MODE_LOCK_ENABLED",
        ACTIVE_TRADE_MODE_LOCK is True,
    )


# ============================================================
# TEST 2
# SCALP -> BREAKOUT
# THREE CONFIRMATIONS REQUIRED
# ============================================================

def test_scalp_to_breakout():

    print("-" * 80)
    print(
        f"{STAGE} TEST 2: "
        f"SCALP -> BREAKOUT"
    )
    print("-" * 80)

    controller = AutoModeController(
        initial_mode=MODE_SCALP,
    )

    diagnostic(
        "SCALP_BREAKOUT_INITIAL_MODE",
        controller.active_mode
        == MODE_SCALP,
    )

    first = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "BREAKOUT_CONFIRMATION_1_DOES_NOT_SWITCH",
        (
            first["active_mode"]
            == MODE_SCALP
            and first["pending_mode"]
            == MODE_BREAKOUT
            and first["pending_count"]
            == 1
        ),
    )

    second = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "BREAKOUT_CONFIRMATION_2_DOES_NOT_SWITCH",
        (
            second["active_mode"]
            == MODE_SCALP
            and second["pending_mode"]
            == MODE_BREAKOUT
            and second["pending_count"]
            == 2
        ),
    )

    third = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "BREAKOUT_CONFIRMATION_3_SWITCHES_MODE",
        (
            third["active_mode"]
            == MODE_BREAKOUT
            and third["pending_mode"]
            is None
            and third["pending_count"]
            == 0
        ),
    )

    diagnostic(
        "SCALP_TO_BREAKOUT_THREE_CONFIRMATION_TRANSITION",
        controller.active_mode
        == MODE_BREAKOUT,
    )


# ============================================================
# TEST 3
# STRUCTURE -> BREAKOUT
# THREE CONFIRMATIONS REQUIRED
# ============================================================

def test_structure_to_breakout():

    print("-" * 80)
    print(
        f"{STAGE} TEST 3: "
        f"STRUCTURE -> BREAKOUT"
    )
    print("-" * 80)

    controller = AutoModeController(
        initial_mode=MODE_STRUCTURE,
    )

    first = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "STRUCTURE_BREAKOUT_CONFIRMATION_1",
        (
            first["active_mode"]
            == MODE_STRUCTURE
            and first["pending_count"]
            == 1
        ),
    )

    second = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "STRUCTURE_BREAKOUT_CONFIRMATION_2",
        (
            second["active_mode"]
            == MODE_STRUCTURE
            and second["pending_count"]
            == 2
        ),
    )

    third = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "STRUCTURE_BREAKOUT_CONFIRMATION_3",
        (
            third["active_mode"]
            == MODE_BREAKOUT
            and third["pending_mode"]
            is None
            and third["pending_count"]
            == 0
        ),
    )


# ============================================================
# TEST 4
# FALSE BREAKOUT MUST NOT SWITCH MODE
# ============================================================

def test_false_breakout_rejection():

    print("-" * 80)
    print(
        f"{STAGE} TEST 4: "
        f"FALSE BREAKOUT REJECTION"
    )
    print("-" * 80)

    controller = AutoModeController(
        initial_mode=MODE_STRUCTURE,
    )

    first = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "FALSE_BREAKOUT_FIRST_PENDING",
        (
            first["active_mode"]
            == MODE_STRUCTURE
            and first["pending_mode"]
            == MODE_BREAKOUT
            and first["pending_count"]
            == 1
        ),
    )

    second = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "FALSE_BREAKOUT_SECOND_PENDING",
        (
            second["active_mode"]
            == MODE_STRUCTURE
            and second["pending_mode"]
            == MODE_BREAKOUT
            and second["pending_count"]
            == 2
        ),
    )

    reset = controller.evaluate(
        MODE_STRUCTURE
    )

    diagnostic(
        "FALSE_BREAKOUT_CANCELLED_BY_STRUCTURE",
        (
            reset["active_mode"]
            == MODE_STRUCTURE
            and reset["pending_mode"]
            is None
            and reset["pending_count"]
            == 0
        ),
    )

    diagnostic(
        "FALSE_BREAKOUT_DID_NOT_SWITCH_MODE",
        controller.active_mode
        == MODE_STRUCTURE,
    )


# ============================================================
# TEST 5
# CANDIDATE CHANGE RESETS CONFIRMATION COUNT
# ============================================================

def test_candidate_reset():

    print("-" * 80)
    print(
        f"{STAGE} TEST 5: "
        f"CANDIDATE RESET"
    )
    print("-" * 80)

    controller = AutoModeController(
        initial_mode=MODE_SCALP,
    )

    controller.evaluate(
        MODE_BREAKOUT
    )

    before = controller.snapshot()

    diagnostic(
        "BREAKOUT_PENDING_BEFORE_RESET",
        (
            before["pending_mode"]
            == MODE_BREAKOUT
            and before["pending_count"]
            == 1
        ),
    )

    changed = controller.evaluate(
        MODE_STRUCTURE
    )

    diagnostic(
        "NEW_CANDIDATE_RESETS_COUNT_TO_1",
        (
            changed["active_mode"]
            == MODE_SCALP
            and changed["pending_mode"]
            == MODE_STRUCTURE
            and changed["pending_count"]
            == 1
        ),
    )

    diagnostic(
        "BREAKOUT_CONFIRMATION_NOT_CARRIED_TO_STRUCTURE",
        changed["pending_count"] == 1,
    )


# ============================================================
# TEST 6
# ACTIVE TRADE MODE LOCK
# ============================================================

def test_active_trade_mode_lock():

    print("-" * 80)
    print(
        f"{STAGE} TEST 6: "
        f"ACTIVE TRADE MODE LOCK"
    )
    print("-" * 80)

    controller = AutoModeController(
        initial_mode=MODE_STRUCTURE,
    )

    controller.lock_trade()

    diagnostic(
        "TRADE_LOCK_ACTIVATED",
        (
            controller.trade_locked
            and controller.locked_trade_mode
            == MODE_STRUCTURE
        ),
    )

    first = controller.evaluate(
        MODE_BREAKOUT
    )

    second = controller.evaluate(
        MODE_BREAKOUT
    )

    third = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "LOCK_BLOCKS_BREAKOUT_CONFIRMATION_1",
        first["active_mode"]
        == MODE_STRUCTURE,
    )

    diagnostic(
        "LOCK_BLOCKS_BREAKOUT_CONFIRMATION_2",
        second["active_mode"]
        == MODE_STRUCTURE,
    )

    diagnostic(
        "LOCK_BLOCKS_BREAKOUT_CONFIRMATION_3",
        third["active_mode"]
        == MODE_STRUCTURE,
    )

    diagnostic(
        "ACTIVE_TRADE_MODE_LOCK_PRESERVES_STRUCTURE",
        (
            controller.active_mode
            == MODE_STRUCTURE
            and controller.pending_mode
            is None
            and controller.pending_count
            == 0
        ),
    )

    controller.unlock_trade()

    diagnostic(
        "TRADE_LOCK_RELEASED",
        not controller.trade_locked,
    )

    controller.evaluate(
        MODE_BREAKOUT
    )

    controller.evaluate(
        MODE_BREAKOUT
    )

    after_unlock = controller.evaluate(
        MODE_BREAKOUT
    )

    diagnostic(
        "BREAKOUT_ALLOWED_AFTER_TRADE_UNLOCK",
        after_unlock["active_mode"]
        == MODE_BREAKOUT,
    )


# ============================================================
# TEST 7
# EXCLUSIVE MODE INVARIANT
# ============================================================

def test_exclusive_mode():

    print("-" * 80)
    print(
        f"{STAGE} TEST 7: "
        f"EXCLUSIVE MODE INVARIANT"
    )
    print("-" * 80)

    for initial_mode in VALID_MODES:

        controller = AutoModeController(
            initial_mode=initial_mode,
        )

        snapshot = controller.snapshot()

        active = snapshot["active_mode"]

        diagnostic(
            f"EXCLUSIVE_MODE_{initial_mode}",
            (
                active in VALID_MODES
                and isinstance(active, str)
            ),
            f"active_mode={active}",
        )


# ============================================================
# TEST 8
# INVALID MODE MUST BE REJECTED
# ============================================================

def test_invalid_mode():

    print("-" * 80)
    print(
        f"{STAGE} TEST 8: "
        f"INVALID MODE REJECTION"
    )
    print("-" * 80)

    controller = AutoModeController(
        initial_mode=MODE_SCALP,
    )

    rejected = False

    try:
        controller.evaluate(
            "INVALID_MODE"
        )
    except ValueError:
        rejected = True

    diagnostic(
        "INVALID_MODE_REJECTED",
        rejected,
    )

    diagnostic(
        "INVALID_MODE_DID_NOT_CHANGE_ACTIVE_MODE",
        controller.active_mode
        == MODE_SCALP,
    )


# ============================================================
# TEST 9
# ZERO-WRITE INVARIANT
# ============================================================

def test_zero_write():

    print("-" * 80)
    print(
        f"{STAGE} TEST 9: "
        f"ZERO-WRITE SAFETY"
    )
    print("-" * 80)

    diagnostic(
        "REAL_ORDER_EXECUTION_DISABLED",
        REAL_ORDER_EXECUTION is False,
    )

    diagnostic(
        "DEMO_ORDER_EXECUTION_DISABLED",
        DEMO_ORDER_EXECUTION is False,
    )

    diagnostic(
        "WRITE_TRANSPORT_DISABLED",
        WRITE_TRANSPORT is False,
    )

    diagnostic(
        "ORDER_SUBMISSION_DISABLED",
        ORDER_SUBMISSION_ENABLED is False,
    )

    diagnostic(
        "FIRST_REAL_ORDER_DISABLED",
        FIRST_REAL_ORDER_ENABLED is False,
    )

    diagnostic(
        "FIRST_DEMO_ORDER_DISABLED",
        FIRST_DEMO_ORDER_ENABLED is False,
    )

    diagnostic(
        "EXCHANGE_MUTATION_DISABLED",
        EXCHANGE_MUTATION_ENABLED is False,
    )

    zero_write = (
        REAL_ORDER_EXECUTION is False
        and DEMO_ORDER_EXECUTION is False
        and WRITE_TRANSPORT is False
        and ORDER_SUBMISSION_ENABLED is False
        and FIRST_REAL_ORDER_ENABLED is False
        and FIRST_DEMO_ORDER_ENABLED is False
        and EXCHANGE_MUTATION_ENABLED is False
    )

    diagnostic(
        "R36F15104A_ZERO_WRITE_INVARIANT",
        zero_write,
    )


# ============================================================
# RUN COMPLETE VALIDATION
# ============================================================

def run_validation():

    print("=" * 80)
    print(
        f"{STAGE}: VALIDATION START"
    )
    print("=" * 80)

    test_configuration()

    test_scalp_to_breakout()

    test_structure_to_breakout()

    test_false_breakout_rejection()

    test_candidate_reset()

    test_active_trade_mode_lock()

    test_exclusive_mode()

    test_invalid_mode()

    test_zero_write()

    print("=" * 80)

    final_status = (
        "PASS"
        if FAIL_COUNT == 0
        else "FAIL"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} FINAL STATUS = "
        f"{final_status}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} PASS COUNT = "
        f"{PASS_COUNT}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} FAIL COUNT = "
        f"{FAIL_COUNT}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} MODE_CHANGE_CONFIRMATIONS = "
        f"{MODE_CHANGE_CONFIRMATIONS}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} EXCLUSIVE_MODE = "
        f"{EXCLUSIVE_MODE}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} ACTIVE_TRADE_MODE_LOCK = "
        f"{ACTIVE_TRADE_MODE_LOCK}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} REAL_ORDER_EXECUTION = "
        f"{REAL_ORDER_EXECUTION}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} DEMO_ORDER_EXECUTION = "
        f"{DEMO_ORDER_EXECUTION}"
    )

    print(
        f"{utc_now()} "
        f"{STAGE} WRITE_TRANSPORT = "
        f"{WRITE_TRANSPORT}"
    )

    if zero_write_final():
        print(
            f"{utc_now()} "
            "NO REAL ORDER WAS SENT"
        )

        print(
            f"{utc_now()} "
            "NO DEMO ORDER WAS SENT"
        )

        print(
            f"{utc_now()} "
            "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
        )

    print("=" * 80)

    return final_status


def zero_write_final():

    return (
        REAL_ORDER_EXECUTION is False
        and DEMO_ORDER_EXECUTION is False
        and WRITE_TRANSPORT is False
        and ORDER_SUBMISSION_ENABLED is False
        and FIRST_REAL_ORDER_ENABLED is False
        and FIRST_DEMO_ORDER_ENABLED is False
        and EXCHANGE_MUTATION_ENABLED is False
    )


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop():

    count = 0

    while True:

        count += 1

        status = (
            "PASS"
            if FAIL_COUNT == 0
            else "FAIL"
        )

        print(
            f"{utc_now()} "
            f"HEARTBEAT "
            f"stage={STAGE} "
            f"status={status} "
            f"count={count} "
            f"pass_count={PASS_COUNT} "
            f"fail_count={FAIL_COUNT} "
            f"exclusive_mode={EXCLUSIVE_MODE} "
            f"confirmations={MODE_CHANGE_CONFIRMATIONS} "
            f"trade_mode_lock={ACTIVE_TRADE_MODE_LOCK} "
            f"write_transport={WRITE_TRANSPORT} "
            f"real_execution={REAL_ORDER_EXECUTION} "
            f"demo_execution={DEMO_ORDER_EXECUTION}"
        )

        time.sleep(
            REEVALUATION_SECONDS
        )


# ============================================================
# MAIN
# ============================================================

def main():

    start_health_server()

    final_status = run_validation()

    if final_status != "PASS":
        print(
            f"{utc_now()} "
            f"{STAGE}: VALIDATION FAILED"
        )

    else:
        print(
            f"{utc_now()} "
            f"{STAGE}: "
            f"BREAKOUT + MODE-TRANSITION "
            f"VALIDATION COMPLETE"
        )

    heartbeat_loop()


if __name__ == "__main__":
    main()
