# ============================================================
# 0F-4H-R28 UNIT A
# STANDALONE SIGNAL SAFETY GATE TEST
#
# PURPOSE:
# Test the first R28 upgrade unit independently.
#
# NO WEEX API
# NO DEMO ORDER
# NO REAL ORDER
# NO EXCHANGE CREDENTIALS REQUIRED
# ============================================================

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Dict, Set, Tuple


# ============================================================
# CONFIGURATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-A"

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)


# ============================================================
# SAFETY FLAGS
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

REAL_POST_CALLED = False
DEMO_POST_ATTEMPTED = False
DEMO_POST_ACCEPTED = False


# ============================================================
# TEST SIGNAL
# ============================================================

@dataclass
class Signal:
    symbol: str
    direction: str
    created_ms: int
    signal_id: str


# ============================================================
# R28 UNIT A
# SIGNAL FRESHNESS GATE
# ============================================================

def signal_is_fresh(
    signal: Signal,
    now_ms: int,
) -> bool:

    try:
        created_ms = int(
            signal.created_ms
        )

        age_ms = (
            int(now_ms)
            - created_ms
        )

        # Future timestamp is considered invalid.
        if age_ms < 0:
            return False

        expiry_ms = (
            SIGNAL_EXPIRY_SECONDS
            * 1000
        )

        return (
            age_ms
            <= expiry_ms
        )

    except Exception:
        return False


# ============================================================
# R28 UNIT A
# LOSS COOLDOWN GATE
# ============================================================

def loss_cooldown_active(
    last_loss_ms,
    now_ms: int,
) -> bool:

    if last_loss_ms is None:
        return False

    try:
        elapsed_ms = (
            int(now_ms)
            - int(last_loss_ms)
        )

        # Conservative behaviour if clock data looks wrong.
        if elapsed_ms < 0:
            return True

        cooldown_ms = (
            LOSS_COOLDOWN_SECONDS
            * 1000
        )

        return (
            elapsed_ms
            < cooldown_ms
        )

    except Exception:
        return True


# ============================================================
# R28 UNIT A
# DUPLICATE SIGNAL GATE
# ============================================================

def signal_already_seen(
    signal: Signal,
    seen_signal_ids: Set[str],
) -> bool:

    try:
        signal_id = str(
            signal.signal_id
        ).strip()

        if not signal_id:
            return True

        return (
            signal_id
            in seen_signal_ids
        )

    except Exception:
        return True


# ============================================================
# R28 UNIT A
# DIRECTION GATE
# ============================================================

def signal_direction_valid(
    signal: Signal,
) -> bool:

    try:
        direction = str(
            signal.direction
        ).strip().upper()

        return direction in {
            "LONG",
            "SHORT",
        }

    except Exception:
        return False


# ============================================================
# R28 UNIT A
# SYMBOL GATE
# ============================================================

def signal_symbol_valid(
    signal: Signal,
) -> bool:

    try:
        symbol = str(
            signal.symbol
        ).strip().upper()

        return (
            len(symbol) > 0
        )

    except Exception:
        return False


# ============================================================
# R28 UNIT A
# COMPLETE SIGNAL GATE
# ============================================================

def evaluate_signal_gate(
    signal: Signal,
    now_ms: int,
    seen_signal_ids: Set[str],
    last_loss_ms=None,
) -> Tuple[bool, str]:

    if not signal_symbol_valid(
        signal
    ):
        return (
            False,
            "INVALID_SYMBOL",
        )

    if not signal_direction_valid(
        signal
    ):
        return (
            False,
            "INVALID_DIRECTION",
        )

    if not signal_is_fresh(
        signal,
        now_ms,
    ):
        return (
            False,
            "SIGNAL_EXPIRED",
        )

    if signal_already_seen(
        signal,
        seen_signal_ids,
    ):
        return (
            False,
            "DUPLICATE_SIGNAL",
        )

    if loss_cooldown_active(
        last_loss_ms,
        now_ms,
    ):
        return (
            False,
            "LOSS_COOLDOWN_ACTIVE",
        )

    return (
        True,
        "SIGNAL_ACCEPTED",
    )


# ============================================================
# TEST HELPERS
# ============================================================

def pass_fail(
    condition: bool,
) -> str:

    if condition:
        return "✅ PASS"

    return "❌ FAIL"


# ============================================================
# R28 UNIT A SELF TEST
# ============================================================

def test_signal_gates() -> Dict[str, bool]:

    now_ms = int(
        time.time()
        * 1000
    )

    # ========================================================
    # TEST SIGNALS
    # ========================================================

    fresh_signal = Signal(
        symbol="BTCUSDT",
        direction="LONG",
        created_ms=now_ms,
        signal_id="r28-fresh-signal",
    )

    expired_signal = Signal(
        symbol="BTCUSDT",
        direction="LONG",
        created_ms=(
            now_ms
            - (
                SIGNAL_EXPIRY_SECONDS
                + 10
            )
            * 1000
        ),
        signal_id="r28-expired-signal",
    )

    duplicate_signal = Signal(
        symbol="BTCUSDT",
        direction="SHORT",
        created_ms=now_ms,
        signal_id="r28-duplicate-signal",
    )

    invalid_direction_signal = Signal(
        symbol="BTCUSDT",
        direction="SIDEWAYS",
        created_ms=now_ms,
        signal_id="r28-invalid-direction",
    )

    invalid_symbol_signal = Signal(
        symbol="",
        direction="LONG",
        created_ms=now_ms,
        signal_id="r28-invalid-symbol",
    )

    future_signal = Signal(
        symbol="BTCUSDT",
        direction="LONG",
        created_ms=(
            now_ms
            + 10_000
        ),
        signal_id="r28-future-signal",
    )

    # ========================================================
    # DUPLICATE STATE
    # ========================================================

    seen_signals: Set[str] = {
        duplicate_signal.signal_id
    }

    # ========================================================
    # COOLDOWN DATA
    # ========================================================

    recent_loss_ms = (
        now_ms
        - 1000
    )

    old_loss_ms = (
        now_ms
        - (
            LOSS_COOLDOWN_SECONDS
            + 10
        )
        * 1000
    )

    # ========================================================
    # BASIC GATE TESTS
    # ========================================================

    fresh_signal_test = (
        signal_is_fresh(
            fresh_signal,
            now_ms,
        )
    )

    expired_signal_test = (
        not signal_is_fresh(
            expired_signal,
            now_ms,
        )
    )

    future_signal_test = (
        not signal_is_fresh(
            future_signal,
            now_ms,
        )
    )

    cooldown_active_test = (
        loss_cooldown_active(
            recent_loss_ms,
            now_ms,
        )
    )

    cooldown_expired_test = (
        not loss_cooldown_active(
            old_loss_ms,
            now_ms,
        )
    )

    no_loss_test = (
        not loss_cooldown_active(
            None,
            now_ms,
        )
    )

    duplicate_test = (
        signal_already_seen(
            duplicate_signal,
            seen_signals,
        )
    )

    unseen_test = (
        not signal_already_seen(
            fresh_signal,
            seen_signals,
        )
    )

    valid_long_test = (
        signal_direction_valid(
            fresh_signal
        )
    )

    valid_short_test = (
        signal_direction_valid(
            duplicate_signal
        )
    )

    invalid_direction_test = (
        not signal_direction_valid(
            invalid_direction_signal
        )
    )

    valid_symbol_test = (
        signal_symbol_valid(
            fresh_signal
        )
    )

    invalid_symbol_test = (
        not signal_symbol_valid(
            invalid_symbol_signal
        )
    )

    # ========================================================
    # COMPLETE GATE TESTS
    # ========================================================

    fresh_allowed, fresh_reason = (
        evaluate_signal_gate(
            signal=fresh_signal,
            now_ms=now_ms,
            seen_signal_ids=set(),
            last_loss_ms=None,
        )
    )

    expired_allowed, expired_reason = (
        evaluate_signal_gate(
            signal=expired_signal,
            now_ms=now_ms,
            seen_signal_ids=set(),
            last_loss_ms=None,
        )
    )

    duplicate_allowed, duplicate_reason = (
        evaluate_signal_gate(
            signal=duplicate_signal,
            now_ms=now_ms,
            seen_signal_ids=seen_signals,
            last_loss_ms=None,
        )
    )

    cooldown_allowed, cooldown_reason = (
        evaluate_signal_gate(
            signal=fresh_signal,
            now_ms=now_ms,
            seen_signal_ids=set(),
            last_loss_ms=recent_loss_ms,
        )
    )

    direction_allowed, direction_reason = (
        evaluate_signal_gate(
            signal=invalid_direction_signal,
            now_ms=now_ms,
            seen_signal_ids=set(),
            last_loss_ms=None,
        )
    )

    symbol_allowed, symbol_reason = (
        evaluate_signal_gate(
            signal=invalid_symbol_signal,
            now_ms=now_ms,
            seen_signal_ids=set(),
            last_loss_ms=None,
        )
    )

    # ========================================================
    # VERIFY COMPLETE GATE REASONS
    # ========================================================

    fresh_gate_test = (
        fresh_allowed
        and fresh_reason
        == "SIGNAL_ACCEPTED"
    )

    expired_gate_test = (
        not expired_allowed
        and expired_reason
        == "SIGNAL_EXPIRED"
    )

    duplicate_gate_test = (
        not duplicate_allowed
        and duplicate_reason
        == "DUPLICATE_SIGNAL"
    )

    cooldown_gate_test = (
        not cooldown_allowed
        and cooldown_reason
        == "LOSS_COOLDOWN_ACTIVE"
    )

    direction_gate_test = (
        not direction_allowed
        and direction_reason
        == "INVALID_DIRECTION"
    )

    symbol_gate_test = (
        not symbol_allowed
        and symbol_reason
        == "INVALID_SYMBOL"
    )

    # ========================================================
    # RESULTS
    # ========================================================

    results = {
        "fresh_signal":
            fresh_signal_test,

        "expired_signal":
            expired_signal_test,

        "future_signal":
            future_signal_test,

        "cooldown_active":
            cooldown_active_test,

        "cooldown_expired":
            cooldown_expired_test,

        "no_loss":
            no_loss_test,

        "duplicate_signal":
            duplicate_test,

        "unseen_signal":
            unseen_test,

        "long_direction":
            valid_long_test,

        "short_direction":
            valid_short_test,

        "invalid_direction":
            invalid_direction_test,

        "valid_symbol":
            valid_symbol_test,

        "invalid_symbol":
            invalid_symbol_test,

        "fresh_complete_gate":
            fresh_gate_test,

        "expired_complete_gate":
            expired_gate_test,

        "duplicate_complete_gate":
            duplicate_gate_test,

        "cooldown_complete_gate":
            cooldown_gate_test,

        "direction_complete_gate":
            direction_gate_test,

        "symbol_complete_gate":
            symbol_gate_test,
    }

    return results


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions() -> bool:

    checks = [
        LIVE_ORDER_EXECUTION is False,
        HARD_REAL_POST_LOCK is True,
        REAL_POST_CALLED is False,
        DEMO_POST_ATTEMPTED is False,
        DEMO_POST_ACCEPTED is False,
    ]

    return all(
        checks
    )


# ============================================================
# R28 UNIT A DIAGNOSTIC
# ============================================================

async def r28_unit_a_diagnostic():

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "STANDALONE SIGNAL SAFETY VALIDATION"
    )

    print(
        "NO EXCHANGE CONNECTION"
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )

    print(
        "=" * 60
    )

    results = (
        test_signal_gates()
    )

    print()

    print(
        "R28 UNIT A SIGNAL GATES"
    )

    print(
        "-" * 60
    )

    labels = {
        "fresh_signal":
            "Fresh Signal Accepted",

        "expired_signal":
            "Expired Signal Rejected",

        "future_signal":
            "Future Timestamp Rejected",

        "cooldown_active":
            "Loss Cooldown Detected",

        "cooldown_expired":
            "Expired Cooldown Cleared",

        "no_loss":
            "No-Loss Cooldown Cleared",

        "duplicate_signal":
            "Duplicate Signal Detected",

        "unseen_signal":
            "Unseen Signal Accepted",

        "long_direction":
            "LONG Direction Valid",

        "short_direction":
            "SHORT Direction Valid",

        "invalid_direction":
            "Invalid Direction Rejected",

        "valid_symbol":
            "Valid Symbol Accepted",

        "invalid_symbol":
            "Empty Symbol Rejected",

        "fresh_complete_gate":
            "Complete Fresh Signal Gate",

        "expired_complete_gate":
            "Complete Expiry Gate",

        "duplicate_complete_gate":
            "Complete Duplicate Gate",

        "cooldown_complete_gate":
            "Complete Cooldown Gate",

        "direction_complete_gate":
            "Complete Direction Gate",

        "symbol_complete_gate":
            "Complete Symbol Gate",
    }

    for key, label in labels.items():

        print(
            f"{label}: "
            f"{pass_fail(results[key])}"
        )

    print(
        "-" * 60
    )

    unit_passed = all(
        results.values()
    )

    safety_passed = (
        final_safety_assertions()
    )

    print()

    print(
        "R28 UNIT A CONFIGURATION"
    )

    print(
        "-" * 60
    )

    print(
        "Signal Expiry:",
        f"{SIGNAL_EXPIRY_SECONDS}s",
    )

    print(
        "Loss Cooldown:",
        f"{LOSS_COOLDOWN_SECONDS}s",
    )

    print()

    print(
        "EXECUTION SAFETY"
    )

    print(
        "-" * 60
    )

    print(
        "Live Order Execution:",
        "❌ DISABLED",
    )

    print(
        "Hard Real POST Lock:",
        (
            "✅ ACTIVE"
            if HARD_REAL_POST_LOCK
            else "❌ INACTIVE"
        ),
    )

    print(
        "Real POST Called:",
        (
            "❌ NO"
            if not REAL_POST_CALLED
            else "⚠️ YES"
        ),
    )

    print(
        "Demo POST Attempted:",
        (
            "❌ NO"
            if not DEMO_POST_ATTEMPTED
            else "⚠️ YES"
        ),
    )

    print(
        "Demo POST Accepted:",
        (
            "❌ NO"
            if not DEMO_POST_ACCEPTED
            else "⚠️ YES"
        ),
    )

    print()

    print(
        "Final Safety Assertions:",
        pass_fail(
            safety_passed
        ),
    )

    print(
        "=" * 60
    )

    if (
        unit_passed
        and safety_passed
    ):

        print(
            "✅ R28 UNIT A DIAGNOSTIC PASSED"
        )

        print(
            "✅ SIGNAL SAFETY GATES VALIDATED"
        )

        print(
            "✅ UNIT A READY FOR R27 INTEGRATION"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

    else:

        print(
            "❌ R28 UNIT A DIAGNOSTIC FAILED"
        )

        failed_tests = [
            key
            for key, passed
            in results.items()
            if not passed
        ]

        if failed_tests:

            print(
                "FAILED TESTS:"
            )

            for test_name in failed_tests:

                print(
                    f" - {test_name}"
                )

        if not safety_passed:

            print(
                "❌ SAFETY ASSERTION FAILURE"
            )

        raise RuntimeError(
            "R28 UNIT A validation failed"
        )

    print(
        "=" * 60
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    try:

        await r28_unit_a_diagnostic()

    except Exception as exc:

        print()

        print(
            "=" * 60
        )

        print(
            f"{MODULE_NAME} ERROR"
        )

        print(
            type(exc).__name__
            + ": "
            + str(exc)
        )

        print(
            "=" * 60
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
