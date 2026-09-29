#!/usr/bin/env python3

"""
WEEX PARALLEL BOT RECONSTRUCTION

UNIT 4
REGIME + DIRECTION ENGINE
STANDALONE TEST UNIT

PURPOSE
-------
Prove the regime and directional classification logic
independently before connecting it to frozen Unit 3.

THIS UNIT TESTS
---------------
1. LONG EMA direction.
2. SHORT EMA direction.
3. Mixed EMA / no direction.
4. Positive signed price movement.
5. Negative signed price movement.
6. Zero price movement.
7. SCALP classification.
8. STRUCTURE classification.
9. LONG BREAKOUT classification.
10. SHORT BREAKOUT classification.
11. Exact classifier boundaries.
12. Three-confirmation mode transition.
13. Pending-mode reset.
14. Active-trade mode lock.
15. Invalid-mode rejection.
16. Invalid-price rejection.
17. Execution firebreak.

SAFETY
------
ZERO WEEX POST
ZERO DEMO ORDER
ZERO REAL ORDER
ZERO EXCHANGE MUTATION
NO NETWORK ACCESS
NO ORDER PAYLOAD
NO POSITION SIZING
NO TP
NO SL
NO BACKUP EXECUTION

IMPORTANT
---------
This is a standalone deterministic test unit.

It does NOT modify frozen Unit 3.

Only after this unit passes will Unit 4 be connected
to the frozen Unit 3 EMA/candle output.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "WEEX_PARALLEL_BOT"

APP_VERSION = "0.4.0"

RECONSTRUCTION_UNIT = (
    "UNIT_4_REGIME_DIRECTION_ENGINE_STANDALONE"
)


# ============================================================
# DECIMAL
# ============================================================

def D(
    value: Any,
) -> Decimal:

    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def decimal_to_string(
    value: Any,
) -> str:

    value = D(
        value
    )

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = (
            text
            .rstrip("0")
            .rstrip(".")
        )

    return text


# ============================================================
# TIME / LOGGING
# ============================================================

def utc_now_iso() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(
    message: str,
) -> None:

    print(
        f"{utc_now_iso()} {message}",
        flush=True,
    )


def separator() -> None:

    print(
        "-" * 80,
        flush=True,
    )


# ============================================================
# UNIT 4 CONFIGURATION
# ============================================================

REGIME_STRONG_EMA_SEPARATION_PERCENT = Decimal(
    "0.05"
)

REGIME_BREAKOUT_MOVE_PERCENT = Decimal(
    "0.60"
)

REGIME_MODE_CONFIRMATIONS_REQUIRED = 3

REGIME_VALID_MODES = (
    "SCALP",
    "STRUCTURE",
    "BREAKOUT",
)


# ============================================================
# EXECUTION FIREBREAK
# ============================================================

WEEX_POST = False

DEMO_ORDER = False

REAL_ORDER = False

EXCHANGE_MUTATION = False

ORDER_PAYLOAD_GENERATED = False

NETWORK_ACCESS = False


# ============================================================
# UNIT 4 INPUT SNAPSHOT
#
# This deliberately contains only the information Unit 4
# requires from upstream Unit 3.
#
# Unit 4 therefore does not depend on the Unit 3 implementation.
# ============================================================

@dataclass(
    frozen=True
)
class Unit4MarketSnapshot:

    close_price: Decimal

    ema19: Decimal

    ema50: Decimal

    ema200: Decimal

    ema19_50_separation_percent: Decimal


# ============================================================
# UNIT 4 RESULT
# ============================================================

@dataclass(
    frozen=True
)
class RegimeResult:

    raw_mode: str

    active_mode: str

    direction: str | None

    ema_separation_percent: Decimal

    short_term_move_percent: Decimal

    pending_mode: str | None

    pending_count: int

    mode_locked: bool

    reason: str


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_market_snapshot(
    snapshot: Unit4MarketSnapshot,
) -> None:

    if snapshot.close_price <= 0:

        raise ValueError(
            "UNIT 4 invalid close price."
        )

    if snapshot.ema19 <= 0:

        raise ValueError(
            "UNIT 4 invalid EMA19."
        )

    if snapshot.ema50 <= 0:

        raise ValueError(
            "UNIT 4 invalid EMA50."
        )

    if snapshot.ema200 <= 0:

        raise ValueError(
            "UNIT 4 invalid EMA200."
        )

    if (
        snapshot.ema19_50_separation_percent
        < 0
    ):

        raise ValueError(
            "UNIT 4 invalid EMA separation."
        )


# ============================================================
# UNIT 4 REGIME ENGINE
# ============================================================

class RegimeEngine:

    def __init__(
        self,
    ) -> None:

        self.active_mode: str | None = None

        self.pending_mode: str | None = None

        self.pending_count: int = 0

        self.mode_locked: bool = False

        self.reference_price: Decimal | None = None

        self.last_reason: str = (
            "NOT_EVALUATED"
        )


    # ========================================================
    # EMA DIRECTION
    # ========================================================

    @staticmethod
    def direction_from_ema(
        snapshot: Unit4MarketSnapshot,
    ) -> str | None:

        validate_market_snapshot(
            snapshot
        )

        if (
            snapshot.ema19
            > snapshot.ema50
            > snapshot.ema200
        ):

            return "LONG"

        if (
            snapshot.ema19
            < snapshot.ema50
            < snapshot.ema200
        ):

            return "SHORT"

        return None


    # ========================================================
    # SIGNED PRICE MOVEMENT
    #
    # IMPORTANT:
    #
    # Positive:
    #     current price > reference price
    #
    # Negative:
    #     current price < reference price
    #
    # Zero:
    #     current price == reference price
    #
    # This intentionally DOES NOT use abs(current-reference).
    # ========================================================

    @staticmethod
    def move_percent(
        current: Decimal,
        reference: Decimal | None,
    ) -> Decimal:

        current = D(
            current
        )

        if current <= 0:

            raise ValueError(
                "UNIT 4 current price must be positive."
            )

        if reference is None:

            return Decimal(
                "0"
            )

        reference = D(
            reference
        )

        if reference <= 0:

            raise ValueError(
                "UNIT 4 reference price must be positive."
            )

        return (
            (
                current
                - reference
            )
            / reference
            * Decimal("100")
        )


    # ========================================================
    # REGIME CLASSIFIER
    #
    # BREAKOUT:
    #
    # LONG requires positive movement >= threshold.
    #
    # SHORT requires negative movement <= -threshold.
    #
    # STRUCTURE:
    #
    # Confirmed EMA direction and sufficient EMA separation.
    #
    # SCALP:
    #
    # No confirmed structure or breakout condition.
    # ========================================================

    @staticmethod
    def classify(
        direction: str | None,
        ema_separation_percent: Decimal,
        movement_percent: Decimal,
    ) -> tuple[str, str]:

        ema_separation_percent = D(
            ema_separation_percent
        )

        movement_percent = D(
            movement_percent
        )

        if ema_separation_percent < 0:

            raise ValueError(
                "UNIT 4 EMA separation cannot be negative."
            )

        if direction not in (
            None,
            "LONG",
            "SHORT",
        ):

            raise ValueError(
                "UNIT 4 invalid direction: "
                + str(direction)
            )

        # ----------------------------------------------------
        # LONG BREAKOUT
        # ----------------------------------------------------

        if (
            direction == "LONG"
            and movement_percent
            >= REGIME_BREAKOUT_MOVE_PERCENT
        ):

            return (
                "BREAKOUT",
                "LONG_BREAKOUT_MOVE_CONFIRMED",
            )

        # ----------------------------------------------------
        # SHORT BREAKOUT
        # ----------------------------------------------------

        if (
            direction == "SHORT"
            and movement_percent
            <= -REGIME_BREAKOUT_MOVE_PERCENT
        ):

            return (
                "BREAKOUT",
                "SHORT_BREAKOUT_MOVE_CONFIRMED",
            )

        # ----------------------------------------------------
        # STRUCTURE
        # ----------------------------------------------------

        if (
            direction in (
                "LONG",
                "SHORT",
            )
            and ema_separation_percent
            >= REGIME_STRONG_EMA_SEPARATION_PERCENT
        ):

            return (
                "STRUCTURE",
                "STRONG_EMA_DIRECTION_CONFIRMED",
            )

        # ----------------------------------------------------
        # SCALP
        # ----------------------------------------------------

        return (
            "SCALP",
            "NO_CONFIRMED_STRUCTURE_OR_BREAKOUT_CONDITION",
        )


    # ========================================================
    # MODE STATE MACHINE
    # ========================================================

    def update_mode(
        self,
        raw_mode: str,
        reason: str,
        *,
        trade_active: bool = False,
    ) -> str:

        if raw_mode not in REGIME_VALID_MODES:

            raise ValueError(
                "Invalid regime mode: "
                + str(raw_mode)
            )

        # ----------------------------------------------------
        # ACTIVE TRADE MODE LOCK
        # ----------------------------------------------------

        if trade_active:

            self.mode_locked = True

            if self.active_mode is None:

                self.active_mode = (
                    raw_mode
                )

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "ACTIVE_TRADE_MODE_LOCK"
            )

            return self.active_mode

        # ----------------------------------------------------
        # NO ACTIVE TRADE
        # ----------------------------------------------------

        self.mode_locked = False

        # ----------------------------------------------------
        # FIRST MODE
        # ----------------------------------------------------

        if self.active_mode is None:

            self.active_mode = (
                raw_mode
            )

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "INITIAL_MODE_SELECTED:"
                + reason
            )

            return self.active_mode

        # ----------------------------------------------------
        # CURRENT MODE RECONFIRMED
        # ----------------------------------------------------

        if raw_mode == self.active_mode:

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "ACTIVE_MODE_CONFIRMED:"
                + reason
            )

            return self.active_mode

        # ----------------------------------------------------
        # NEW CANDIDATE MODE
        # ----------------------------------------------------

        if self.pending_mode != raw_mode:

            self.pending_mode = (
                raw_mode
            )

            self.pending_count = 1

            self.last_reason = (
                "NEW_MODE_PENDING:"
                + reason
            )

            return self.active_mode

        # ----------------------------------------------------
        # CONTINUE CONFIRMING CANDIDATE
        # ----------------------------------------------------

        self.pending_count += 1

        if (
            self.pending_count
            >= REGIME_MODE_CONFIRMATIONS_REQUIRED
        ):

            previous_mode = (
                self.active_mode
            )

            self.active_mode = (
                raw_mode
            )

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "THREE_CONFIRMATION_TRANSITION:"
                + str(previous_mode)
                + "_TO_"
                + raw_mode
            )

            return self.active_mode

        self.last_reason = (
            "MODE_CONFIRMATION_PENDING:"
            + reason
        )

        return self.active_mode


    # ========================================================
    # COMPLETE EVALUATION
    # ========================================================

    def evaluate(
        self,
        snapshot: Unit4MarketSnapshot,
        *,
        trade_active: bool = False,
    ) -> RegimeResult:

        validate_market_snapshot(
            snapshot
        )

        direction = (
            self.direction_from_ema(
                snapshot
            )
        )

        movement_percent = (
            self.move_percent(
                snapshot.close_price,
                self.reference_price,
            )
        )

        (
            raw_mode,
            classifier_reason,
        ) = self.classify(
            direction,
            snapshot.ema19_50_separation_percent,
            movement_percent,
        )

        active_mode = (
            self.update_mode(
                raw_mode,
                classifier_reason,
                trade_active=trade_active,
            )
        )

        self.reference_price = (
            snapshot.close_price
        )

        return RegimeResult(

            raw_mode=raw_mode,

            active_mode=active_mode,

            direction=direction,

            ema_separation_percent=(
                snapshot
                .ema19_50_separation_percent
            ),

            short_term_move_percent=(
                movement_percent
            ),

            pending_mode=(
                self.pending_mode
            ),

            pending_count=(
                self.pending_count
            ),

            mode_locked=(
                self.mode_locked
            ),

            reason=(
                self.last_reason
            ),

        )


# ============================================================
# TEST SNAPSHOT FACTORY
# ============================================================

def make_snapshot(
    *,
    close: str,
    ema19: str,
    ema50: str,
    ema200: str,
    separation: str,
) -> Unit4MarketSnapshot:

    return Unit4MarketSnapshot(

        close_price=D(
            close
        ),

        ema19=D(
            ema19
        ),

        ema50=D(
            ema50
        ),

        ema200=D(
            ema200
        ),

        ema19_50_separation_percent=D(
            separation
        ),

    )


# ============================================================
# TEST ASSERTION
# ============================================================

def require(
    condition: bool,
    message: str,
) -> None:

    if not condition:

        raise RuntimeError(
            message
        )


# ============================================================
# TEST 1
# EMA DIRECTION
# ============================================================

def test_ema_direction() -> None:

    bullish = make_snapshot(
        close="100",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    bearish = make_snapshot(
        close="100",
        ema19="99",
        ema50="100",
        ema200="101",
        separation="0.10",
    )

    mixed = make_snapshot(
        close="100",
        ema19="101",
        ema50="99",
        ema200="100",
        separation="0.10",
    )

    require(
        RegimeEngine.direction_from_ema(
            bullish
        )
        == "LONG",
        "UNIT 4 LONG direction test failed.",
    )

    require(
        RegimeEngine.direction_from_ema(
            bearish
        )
        == "SHORT",
        "UNIT 4 SHORT direction test failed.",
    )

    require(
        RegimeEngine.direction_from_ema(
            mixed
        )
        is None,
        "UNIT 4 NONE direction test failed.",
    )

    log(
        "PASS: UNIT 4 EMA DIRECTION TESTS"
    )


# ============================================================
# TEST 2
# SIGNED MOVEMENT
# ============================================================

def test_signed_movement() -> None:

    upward = (
        RegimeEngine.move_percent(
            D("101"),
            D("100"),
        )
    )

    downward = (
        RegimeEngine.move_percent(
            D("99"),
            D("100"),
        )
    )

    unchanged = (
        RegimeEngine.move_percent(
            D("100"),
            D("100"),
        )
    )

    require(
        upward == D("1"),
        "UNIT 4 positive movement test failed.",
    )

    require(
        downward == D("-1"),
        "UNIT 4 negative movement test failed.",
    )

    require(
        unchanged == D("0"),
        "UNIT 4 zero movement test failed.",
    )

    require(
        upward > 0,
        "UNIT 4 upward movement lost positive sign.",
    )

    require(
        downward < 0,
        "UNIT 4 downward movement lost negative sign.",
    )

    log(
        "PASS: UNIT 4 SIGNED MOVEMENT TESTS"
    )


# ============================================================
# TEST 3
# CLASSIFIER BOUNDARIES
# ============================================================

def test_classifier_boundaries() -> None:

    # --------------------------------------------------------
    # SCALP just below STRUCTURE threshold.
    # --------------------------------------------------------

    mode, reason = (
        RegimeEngine.classify(
            "LONG",
            D("0.0499"),
            D("0.10"),
        )
    )

    require(
        mode == "SCALP",
        "UNIT 4 SCALP boundary test failed.",
    )

    # --------------------------------------------------------
    # STRUCTURE exactly at threshold.
    # --------------------------------------------------------

    mode, reason = (
        RegimeEngine.classify(
            "LONG",
            D("0.05"),
            D("0.10"),
        )
    )

    require(
        mode == "STRUCTURE",
        "UNIT 4 STRUCTURE boundary test failed.",
    )

    # --------------------------------------------------------
    # LONG BREAKOUT exactly at +0.60%.
    # --------------------------------------------------------

    mode, reason = (
        RegimeEngine.classify(
            "LONG",
            D("0.01"),
            D("0.60"),
        )
    )

    require(
        mode == "BREAKOUT",
        "UNIT 4 LONG breakout boundary failed.",
    )

    require(
        reason
        == "LONG_BREAKOUT_MOVE_CONFIRMED",
        "UNIT 4 LONG breakout reason failed.",
    )

    # --------------------------------------------------------
    # SHORT BREAKOUT exactly at -0.60%.
    # --------------------------------------------------------

    mode, reason = (
        RegimeEngine.classify(
            "SHORT",
            D("0.01"),
            D("-0.60"),
        )
    )

    require(
        mode == "BREAKOUT",
        "UNIT 4 SHORT breakout boundary failed.",
    )

    require(
        reason
        == "SHORT_BREAKOUT_MOVE_CONFIRMED",
        "UNIT 4 SHORT breakout reason failed.",
    )

    # --------------------------------------------------------
    # IMPORTANT SYMMETRY CHECK:
    #
    # Positive movement must NOT trigger SHORT breakout.
    # --------------------------------------------------------

    mode, reason = (
        RegimeEngine.classify(
            "SHORT",
            D("0.01"),
            D("0.60"),
        )
    )

    require(
        mode != "BREAKOUT",
        (
            "UNIT 4 positive movement incorrectly "
            "triggered SHORT breakout."
        ),
    )

    # --------------------------------------------------------
    # Negative movement must NOT trigger LONG breakout.
    # --------------------------------------------------------

    mode, reason = (
        RegimeEngine.classify(
            "LONG",
            D("0.01"),
            D("-0.60"),
        )
    )

    require(
        mode != "BREAKOUT",
        (
            "UNIT 4 negative movement incorrectly "
            "triggered LONG breakout."
        ),
    )

    log(
        "PASS: UNIT 4 CLASSIFIER BOUNDARIES"
    )


# ============================================================
# TEST 4
# NO-DIRECTION CLASSIFICATION
# ============================================================

def test_no_direction_classification() -> None:

    mode, reason = (
        RegimeEngine.classify(
            None,
            D("1.00"),
            D("5.00"),
        )
    )

    require(
        mode == "SCALP",
        (
            "UNIT 4 no-direction state incorrectly "
            "produced STRUCTURE/BREAKOUT."
        ),
    )

    log(
        "PASS: UNIT 4 NO-DIRECTION CLASSIFICATION"
    )


# ============================================================
# TEST 5
# THREE-CONFIRMATION MODE TRANSITION
# ============================================================

def test_three_confirmation_transition() -> None:

    engine = RegimeEngine()

    # --------------------------------------------------------
    # Establish STRUCTURE as active mode.
    # --------------------------------------------------------

    initial = make_snapshot(
        close="100",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    first = engine.evaluate(
        initial
    )

    require(
        first.active_mode == "STRUCTURE",
        (
            "UNIT 4 initial STRUCTURE "
            "selection failed."
        ),
    )

    require(
        first.pending_count == 0,
        (
            "UNIT 4 initial pending count "
            "must be zero."
        ),
    )

    # --------------------------------------------------------
    # Candidate BREAKOUT 1.
    #
    # 100 -> 101 = +1%.
    # --------------------------------------------------------

    breakout_1 = make_snapshot(
        close="101",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    result_1 = engine.evaluate(
        breakout_1
    )

    require(
        result_1.raw_mode == "BREAKOUT",
        (
            "UNIT 4 transition candidate 1 "
            "did not classify BREAKOUT."
        ),
    )

    require(
        result_1.active_mode == "STRUCTURE",
        (
            "UNIT 4 changed mode before "
            "three confirmations."
        ),
    )

    require(
        result_1.pending_mode == "BREAKOUT",
        (
            "UNIT 4 transition candidate 1 "
            "pending mode failed."
        ),
    )

    require(
        result_1.pending_count == 1,
        (
            "UNIT 4 transition confirmation "
            "count 1 failed."
        ),
    )

    # --------------------------------------------------------
    # To produce another +1% move, reference is now 101.
    # 101 -> 102.01 = +1%.
    # --------------------------------------------------------

    breakout_2 = make_snapshot(
        close="102.01",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    result_2 = engine.evaluate(
        breakout_2
    )

    require(
        result_2.raw_mode == "BREAKOUT",
        (
            "UNIT 4 transition candidate 2 "
            "did not classify BREAKOUT."
        ),
    )

    require(
        result_2.active_mode == "STRUCTURE",
        (
            "UNIT 4 changed mode at only "
            "two confirmations."
        ),
    )

    require(
        result_2.pending_count == 2,
        (
            "UNIT 4 transition confirmation "
            "count 2 failed."
        ),
    )

    # --------------------------------------------------------
    # Third consecutive +1% movement.
    #
    # 102.01 -> 103.0301 = +1%.
    # --------------------------------------------------------

    breakout_3 = make_snapshot(
        close="103.0301",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    result_3 = engine.evaluate(
        breakout_3
    )

    require(
        result_3.raw_mode == "BREAKOUT",
        (
            "UNIT 4 transition candidate 3 "
            "did not classify BREAKOUT."
        ),
    )

    require(
        result_3.active_mode == "BREAKOUT",
        (
            "UNIT 4 failed three-confirmation "
            "mode transition."
        ),
    )

    require(
        result_3.pending_mode is None,
        (
            "UNIT 4 pending mode not cleared "
            "after transition."
        ),
    )

    require(
        result_3.pending_count == 0,
        (
            "UNIT 4 pending count not reset "
            "after transition."
        ),
    )

    require(
        result_3.reason.startswith(
            "THREE_CONFIRMATION_TRANSITION:"
        ),
        (
            "UNIT 4 transition reason "
            "not recorded."
        ),
    )

    log(
        "PASS: UNIT 4 THREE-CONFIRMATION TRANSITION"
    )


# ============================================================
# TEST 6
# PENDING MODE RESET
# ============================================================

def test_pending_mode_reset() -> None:

    engine = RegimeEngine()

    structure = make_snapshot(
        close="100",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    engine.evaluate(
        structure
    )

    breakout = make_snapshot(
        close="101",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    pending = engine.evaluate(
        breakout
    )

    require(
        pending.pending_mode == "BREAKOUT",
        (
            "UNIT 4 pending-reset setup "
            "did not create pending mode."
        ),
    )

    require(
        pending.pending_count == 1,
        (
            "UNIT 4 pending-reset setup "
            "count failed."
        ),
    )

    # --------------------------------------------------------
    # Return to current active STRUCTURE mode.
    # Movement is intentionally small.
    # --------------------------------------------------------

    structure_again = make_snapshot(
        close="101.01",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    reset = engine.evaluate(
        structure_again
    )

    require(
        reset.raw_mode == "STRUCTURE",
        (
            "UNIT 4 pending-reset state "
            "was not STRUCTURE."
        ),
    )

    require(
        reset.active_mode == "STRUCTURE",
        (
            "UNIT 4 active mode changed "
            "during pending reset."
        ),
    )

    require(
        reset.pending_mode is None,
        (
            "UNIT 4 pending mode was not reset."
        ),
    )

    require(
        reset.pending_count == 0,
        (
            "UNIT 4 pending count was not reset."
        ),
    )

    log(
        "PASS: UNIT 4 PENDING MODE RESET"
    )


# ============================================================
# TEST 7
# ACTIVE TRADE MODE LOCK
# ============================================================

def test_active_trade_mode_lock() -> None:

    engine = RegimeEngine()

    structure = make_snapshot(
        close="100",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    initial = engine.evaluate(
        structure
    )

    require(
        initial.active_mode == "STRUCTURE",
        (
            "UNIT 4 mode-lock setup "
            "failed."
        ),
    )

    breakout = make_snapshot(
        close="101",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    locked = engine.evaluate(
        breakout,
        trade_active=True,
    )

    require(
        locked.raw_mode == "BREAKOUT",
        (
            "UNIT 4 lock test raw mode "
            "did not become BREAKOUT."
        ),
    )

    require(
        locked.active_mode == "STRUCTURE",
        (
            "UNIT 4 active mode changed "
            "while trade was active."
        ),
    )

    require(
        locked.mode_locked is True,
        (
            "UNIT 4 active-trade lock "
            "was not enabled."
        ),
    )

    require(
        locked.pending_mode is None,
        (
            "UNIT 4 pending mode exists "
            "while trade mode is locked."
        ),
    )

    require(
        locked.pending_count == 0,
        (
            "UNIT 4 pending count exists "
            "while trade mode is locked."
        ),
    )

    require(
        locked.reason
        == "ACTIVE_TRADE_MODE_LOCK",
        (
            "UNIT 4 active-trade lock "
            "reason failed."
        ),
    )

    log(
        "PASS: UNIT 4 ACTIVE-TRADE MODE LOCK"
    )


# ============================================================
# TEST 8
# SHORT DIRECTION END-TO-END
# ============================================================

def test_short_direction_end_to_end() -> None:

    engine = RegimeEngine()

    # --------------------------------------------------------
    # Establish SHORT STRUCTURE at 100.
    # --------------------------------------------------------

    initial = make_snapshot(
        close="100",
        ema19="99",
        ema50="100",
        ema200="101",
        separation="0.10",
    )

    first = engine.evaluate(
        initial
    )

    require(
        first.direction == "SHORT",
        (
            "UNIT 4 SHORT end-to-end "
            "direction failed."
        ),
    )

    require(
        first.raw_mode == "STRUCTURE",
        (
            "UNIT 4 SHORT end-to-end "
            "initial STRUCTURE failed."
        ),
    )

    # --------------------------------------------------------
    # Price falls 1%.
    #
    # Signed movement must be -1%.
    # --------------------------------------------------------

    falling = make_snapshot(
        close="99",
        ema19="98.9",
        ema50="100",
        ema200="101",
        separation="0.10",
    )

    second = engine.evaluate(
        falling
    )

    require(
        second.direction == "SHORT",
        (
            "UNIT 4 SHORT direction "
            "was lost after price fall."
        ),
    )

    require(
        second.short_term_move_percent
        == D("-1"),
        (
            "UNIT 4 SHORT movement "
            "was not preserved as negative."
        ),
    )

    require(
        second.raw_mode == "BREAKOUT",
        (
            "UNIT 4 SHORT negative movement "
            "did not classify BREAKOUT."
        ),
    )

    log(
        "PASS: UNIT 4 SHORT DIRECTION END-TO-END"
    )


# ============================================================
# TEST 9
# LONG DIRECTION END-TO-END
# ============================================================

def test_long_direction_end_to_end() -> None:

    engine = RegimeEngine()

    initial = make_snapshot(
        close="100",
        ema19="101",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    first = engine.evaluate(
        initial
    )

    require(
        first.direction == "LONG",
        (
            "UNIT 4 LONG end-to-end "
            "direction failed."
        ),
    )

    require(
        first.raw_mode == "STRUCTURE",
        (
            "UNIT 4 LONG end-to-end "
            "initial STRUCTURE failed."
        ),
    )

    rising = make_snapshot(
        close="101",
        ema19="101.1",
        ema50="100",
        ema200="99",
        separation="0.10",
    )

    second = engine.evaluate(
        rising
    )

    require(
        second.short_term_move_percent
        == D("1"),
        (
            "UNIT 4 LONG movement "
            "was not preserved as positive."
        ),
    )

    require(
        second.raw_mode == "BREAKOUT",
        (
            "UNIT 4 LONG positive movement "
            "did not classify BREAKOUT."
        ),
    )

    log(
        "PASS: UNIT 4 LONG DIRECTION END-TO-END"
    )


# ============================================================
# TEST 10
# INVALID INPUT REJECTION
# ============================================================

def test_invalid_input_rejection() -> None:

    # --------------------------------------------------------
    # Invalid current price.
    # --------------------------------------------------------

    rejected = False

    try:

        RegimeEngine.move_percent(
            D("0"),
            D("100"),
        )

    except ValueError:

        rejected = True

    require(
        rejected,
        (
            "UNIT 4 invalid current price "
            "was not rejected."
        ),
    )

    # --------------------------------------------------------
    # Invalid reference price.
    # --------------------------------------------------------

    rejected = False

    try:

        RegimeEngine.move_percent(
            D("100"),
            D("0"),
        )

    except ValueError:

        rejected = True

    require(
        rejected,
        (
            "UNIT 4 invalid reference price "
            "was not rejected."
        ),
    )

    # --------------------------------------------------------
    # Invalid direction.
    # --------------------------------------------------------

    rejected = False

    try:

        RegimeEngine.classify(
            "SIDEWAYS",
            D("0.10"),
            D("1"),
        )

    except ValueError:

        rejected = True

    require(
        rejected,
        (
            "UNIT 4 invalid direction "
            "was not rejected."
        ),
    )

    # --------------------------------------------------------
    # Invalid mode.
    # --------------------------------------------------------

    rejected = False

    try:

        engine = RegimeEngine()

        engine.update_mode(
            "INVALID",
            "TEST",
        )

    except ValueError:

        rejected = True

    require(
        rejected,
        (
            "UNIT 4 invalid mode "
            "was not rejected."
        ),
    )

    # --------------------------------------------------------
    # Invalid snapshot.
    # --------------------------------------------------------

    rejected = False

    try:

        invalid_snapshot = make_snapshot(
            close="0",
            ema19="101",
            ema50="100",
            ema200="99",
            separation="0.10",
        )

        validate_market_snapshot(
            invalid_snapshot
        )

    except ValueError:

        rejected = True

    require(
        rejected,
        (
            "UNIT 4 invalid snapshot "
            "was not rejected."
        ),
    )

    log(
        "PASS: UNIT 4 INVALID INPUT REJECTION"
    )


# ============================================================
# TEST 11
# EXECUTION FIREBREAK
# ============================================================

def test_execution_firebreak() -> None:

    require(
        WEEX_POST is False,
        "UNIT 4 WEEX POST firebreak failed.",
    )

    require(
        DEMO_ORDER is False,
        "UNIT 4 demo-order firebreak failed.",
    )

    require(
        REAL_ORDER is False,
        "UNIT 4 real-order firebreak failed.",
    )

    require(
        EXCHANGE_MUTATION is False,
        (
            "UNIT 4 exchange-mutation "
            "firebreak failed."
        ),
    )

    require(
        ORDER_PAYLOAD_GENERATED is False,
        (
            "UNIT 4 order-payload "
            "firebreak failed."
        ),
    )

    require(
        NETWORK_ACCESS is False,
        (
            "UNIT 4 network-access "
            "firebreak failed."
        ),
    )

    log(
        "PASS: UNIT 4 EXECUTION FIREBREAK"
    )

    log(
        "ZERO WEEX POST = TRUE"
    )

    log(
        "ZERO DEMO ORDER = TRUE"
    )

    log(
        "ZERO REAL ORDER = TRUE"
    )

    log(
        "ZERO EXCHANGE MUTATION = TRUE"
    )

    log(
        "NO ORDER PAYLOAD GENERATED = TRUE"
    )

    log(
        "NO NETWORK ACCESS = TRUE"
    )


# ============================================================
# COMPLETE UNIT 4 TEST
# ============================================================

def run_unit_4_standalone_tests() -> bool:

    separator()

    log(
        "RECONSTRUCTION UNIT 4 STANDALONE TEST START"
    )

    separator()

    test_ema_direction()

    test_signed_movement()

    test_classifier_boundaries()

    test_no_direction_classification()

    test_three_confirmation_transition()

    test_pending_mode_reset()

    test_active_trade_mode_lock()

    test_short_direction_end_to_end()

    test_long_direction_end_to_end()

    test_invalid_input_rejection()

    test_execution_firebreak()

    separator()

    log(
        "UNIT 4 STANDALONE TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 4 RESULT = PASS"
    )

    separator()

    return True


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    log(
        f"{APP_NAME} {APP_VERSION}"
    )

    log(
        f"STARTING {RECONSTRUCTION_UNIT}"
    )

    try:

        result = (
            run_unit_4_standalone_tests()
        )

    except Exception as exc:

        separator()

        log(
            "RECONSTRUCTION UNIT 4 RESULT = FAIL"
        )

        log(
            "ERROR TYPE = "
            + type(
                exc
            ).__name__
        )

        log(
            "ERROR = "
            + repr(
                exc
            )
        )

        separator()

        raise

    if not result:

        raise RuntimeError(
            "Unit 4 standalone test did not pass."
        )


if __name__ == "__main__":

    main()
