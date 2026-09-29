#!/usr/bin/env python3

"""
WEEX PARALLEL BOT RECONSTRUCTION

UNIT 4B
UNIT 3 -> UNIT 4 BRIDGE
STANDALONE INTEGRATION TEST

PURPOSE
-------
Prove that verified Unit 3 output can be transferred into
the already-tested Unit 4 regime/direction engine without
changing the meaning of the data.

THIS UNIT DOES NOT
------------------
- Contact WEEX
- Send HTTP POST
- Send demo orders
- Send real orders
- Mutate exchange state
- Build order payloads
- Size positions
- Calculate TP
- Calculate SL
- Execute backups

IMPORTANT
---------
Unit 3 has already passed independently.
Unit 4 has already passed independently.

Unit 4B tests ONLY the interface between them.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "WEEX_PARALLEL_BOT"

APP_VERSION = "0.4.1"

RECONSTRUCTION_UNIT = (
    "UNIT_4B_UNIT3_TO_UNIT4_BRIDGE"
)


# ============================================================
# DECIMAL HELPERS
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
# LOGGING
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
# EXECUTION FIREBREAK
# ============================================================

WEEX_POST = False

DEMO_ORDER = False

REAL_ORDER = False

EXCHANGE_MUTATION = False

ORDER_PAYLOAD_GENERATED = False

NETWORK_ACCESS = False

TRADING_DECISION_GENERATED = False


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
# UNIT 3 OUTPUT CONTRACT
#
# This represents the data Unit 3 is allowed to hand to Unit 4.
# ============================================================

@dataclass(
    frozen=True
)
class Unit3Output:

    latest_close: Decimal

    ema19: Decimal

    ema50: Decimal

    ema200: Decimal

    ema19_50_separation_percent: Decimal


# ============================================================
# UNIT 4 INPUT CONTRACT
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
# UNIT 4 RESULT CONTRACT
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
# ASSERTION
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
# UNIT 3 OUTPUT VALIDATION
# ============================================================

def validate_unit3_output(
    output: Unit3Output,
) -> None:

    if output.latest_close <= 0:

        raise ValueError(
            "UNIT 4B invalid Unit 3 latest close."
        )

    if output.ema19 <= 0:

        raise ValueError(
            "UNIT 4B invalid Unit 3 EMA19."
        )

    if output.ema50 <= 0:

        raise ValueError(
            "UNIT 4B invalid Unit 3 EMA50."
        )

    if output.ema200 <= 0:

        raise ValueError(
            "UNIT 4B invalid Unit 3 EMA200."
        )

    if (
        output.ema19_50_separation_percent
        < 0
    ):

        raise ValueError(
            "UNIT 4B invalid Unit 3 EMA separation."
        )


# ============================================================
# UNIT 4 INPUT VALIDATION
# ============================================================

def validate_unit4_snapshot(
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
# UNIT 4 ENGINE
#
# This preserves the corrected behavior already proven by the
# standalone Unit 4 test.
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


    @staticmethod
    def direction_from_ema(
        snapshot: Unit4MarketSnapshot,
    ) -> str | None:

        validate_unit4_snapshot(
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

        if (
            direction == "LONG"
            and movement_percent
            >= REGIME_BREAKOUT_MOVE_PERCENT
        ):

            return (
                "BREAKOUT",
                "LONG_BREAKOUT_MOVE_CONFIRMED",
            )

        if (
            direction == "SHORT"
            and movement_percent
            <= -REGIME_BREAKOUT_MOVE_PERCENT
        ):

            return (
                "BREAKOUT",
                "SHORT_BREAKOUT_MOVE_CONFIRMED",
            )

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

        return (
            "SCALP",
            "NO_CONFIRMED_STRUCTURE_OR_BREAKOUT_CONDITION",
        )


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

        self.mode_locked = False

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

        if raw_mode == self.active_mode:

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "ACTIVE_MODE_CONFIRMED:"
                + reason
            )

            return self.active_mode

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


    def evaluate(
        self,
        snapshot: Unit4MarketSnapshot,
        *,
        trade_active: bool = False,
    ) -> RegimeResult:

        validate_unit4_snapshot(
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
# UNIT 4B BRIDGE
#
# This is the only new functional component being tested.
# ============================================================

def unit4b_bridge(
    unit3_output: Unit3Output,
) -> Unit4MarketSnapshot:

    validate_unit3_output(
        unit3_output
    )

    snapshot = Unit4MarketSnapshot(

        close_price=(
            unit3_output.latest_close
        ),

        ema19=(
            unit3_output.ema19
        ),

        ema50=(
            unit3_output.ema50
        ),

        ema200=(
            unit3_output.ema200
        ),

        ema19_50_separation_percent=(
            unit3_output
            .ema19_50_separation_percent
        ),

    )

    validate_unit4_snapshot(
        snapshot
    )

    return snapshot


# ============================================================
# VERIFIED UNIT 3 SAMPLE
#
# These values are taken from the successful frozen Unit 3
# runtime.
# ============================================================

def build_verified_unit3_sample() -> Unit3Output:

    return Unit3Output(

        latest_close=D(
            "83620.6"
        ),

        ema19=D(
            "83617.85014746295351228158386"
        ),

        ema50=D(
            "83546.52064162984548497329171"
        ),

        ema200=D(
            "83309.36289196458650420172653"
        ),

        ema19_50_separation_percent=D(
            "0.08537699150761009389534685018"
        ),

    )


# ============================================================
# TEST 1
# EXACT DATA PRESERVATION
# ============================================================

def test_bridge_exact_data_preservation() -> None:

    upstream = (
        build_verified_unit3_sample()
    )

    downstream = (
        unit4b_bridge(
            upstream
        )
    )

    require(
        downstream.close_price
        == upstream.latest_close,
        (
            "UNIT 4B bridge changed "
            "latest close."
        ),
    )

    require(
        downstream.ema19
        == upstream.ema19,
        (
            "UNIT 4B bridge changed EMA19."
        ),
    )

    require(
        downstream.ema50
        == upstream.ema50,
        (
            "UNIT 4B bridge changed EMA50."
        ),
    )

    require(
        downstream.ema200
        == upstream.ema200,
        (
            "UNIT 4B bridge changed EMA200."
        ),
    )

    require(
        (
            downstream
            .ema19_50_separation_percent
        )
        == (
            upstream
            .ema19_50_separation_percent
        ),
        (
            "UNIT 4B bridge changed "
            "EMA19/50 separation."
        ),
    )

    log(
        "PASS: UNIT 4B EXACT DATA PRESERVATION"
    )


# ============================================================
# TEST 2
# DIRECTION PRESERVATION
# ============================================================

def test_bridge_direction() -> None:

    upstream = (
        build_verified_unit3_sample()
    )

    snapshot = (
        unit4b_bridge(
            upstream
        )
    )

    direction = (
        RegimeEngine.direction_from_ema(
            snapshot
        )
    )

    require(
        direction == "LONG",
        (
            "UNIT 4B expected LONG direction "
            "from verified bullish Unit 3 sample."
        ),
    )

    log(
        "PASS: UNIT 4B DIRECTION = LONG"
    )


# ============================================================
# TEST 3
# REGIME CLASSIFICATION
#
# First evaluation has no previous reference price.
# Therefore signed short-term movement is correctly 0.
#
# With LONG EMA alignment and separation > 0.05%,
# the expected initial regime is STRUCTURE.
# ============================================================

def test_bridge_regime_classification() -> None:

    upstream = (
        build_verified_unit3_sample()
    )

    snapshot = (
        unit4b_bridge(
            upstream
        )
    )

    engine = (
        RegimeEngine()
    )

    result = (
        engine.evaluate(
            snapshot
        )
    )

    require(
        result.direction == "LONG",
        (
            "UNIT 4B regime evaluation "
            "lost LONG direction."
        ),
    )

    require(
        result.short_term_move_percent
        == D("0"),
        (
            "UNIT 4B first evaluation "
            "movement must be zero."
        ),
    )

    require(
        result.raw_mode == "STRUCTURE",
        (
            "UNIT 4B expected STRUCTURE "
            "from verified Unit 3 sample."
        ),
    )

    require(
        result.active_mode == "STRUCTURE",
        (
            "UNIT 4B expected initial "
            "active mode STRUCTURE."
        ),
    )

    require(
        result.mode_locked is False,
        (
            "UNIT 4B mode unexpectedly locked."
        ),
    )

    log(
        "PASS: UNIT 4B REGIME CLASSIFICATION"
    )

    log(
        "UNIT 4B RAW MODE = "
        + result.raw_mode
    )

    log(
        "UNIT 4B ACTIVE MODE = "
        + result.active_mode
    )

    log(
        "UNIT 4B DIRECTION = "
        + str(
            result.direction
        )
    )

    log(
        "UNIT 4B EMA19/50 SEPARATION % = "
        + decimal_to_string(
            result.ema_separation_percent
        )
    )

    log(
        "UNIT 4B SHORT-TERM MOVE % = "
        + decimal_to_string(
            result.short_term_move_percent
        )
    )

    log(
        "UNIT 4B MODE LOCKED = "
        + str(
            result.mode_locked
        )
    )

    log(
        "UNIT 4B REASON = "
        + result.reason
    )


# ============================================================
# TEST 4
# SIGNED MOVEMENT THROUGH BRIDGE
#
# We create two valid Unit 3 output snapshots.
# The bridge must preserve their closes and Unit 4 must
# calculate signed movement correctly.
# ============================================================

def test_bridge_signed_movement() -> None:

    engine = (
        RegimeEngine()
    )

    first_output = Unit3Output(

        latest_close=D(
            "100"
        ),

        ema19=D(
            "101"
        ),

        ema50=D(
            "100"
        ),

        ema200=D(
            "99"
        ),

        ema19_50_separation_percent=D(
            "0.10"
        ),

    )

    second_output = Unit3Output(

        latest_close=D(
            "99"
        ),

        ema19=D(
            "98"
        ),

        ema50=D(
            "99"
        ),

        ema200=D(
            "100"
        ),

        ema19_50_separation_percent=D(
            "0.10"
        ),

    )

    first_snapshot = (
        unit4b_bridge(
            first_output
        )
    )

    second_snapshot = (
        unit4b_bridge(
            second_output
        )
    )

    first_result = (
        engine.evaluate(
            first_snapshot
        )
    )

    second_result = (
        engine.evaluate(
            second_snapshot
        )
    )

    require(
        first_result.short_term_move_percent
        == D("0"),
        (
            "UNIT 4B initial movement "
            "must be zero."
        ),
    )

    require(
        second_result.short_term_move_percent
        == D("-1"),
        (
            "UNIT 4B failed to preserve "
            "negative signed movement."
        ),
    )

    require(
        second_result.direction == "SHORT",
        (
            "UNIT 4B signed movement test "
            "expected SHORT direction."
        ),
    )

    require(
        second_result.raw_mode
        == "BREAKOUT",
        (
            "UNIT 4B negative SHORT movement "
            "did not classify BREAKOUT."
        ),
    )

    log(
        "PASS: UNIT 4B SIGNED MOVEMENT THROUGH BRIDGE"
    )


# ============================================================
# TEST 5
# INVALID UPSTREAM DATA REJECTION
# ============================================================

def test_bridge_invalid_upstream_rejection() -> None:

    rejected = False

    try:

        invalid = Unit3Output(

            latest_close=D(
                "0"
            ),

            ema19=D(
                "101"
            ),

            ema50=D(
                "100"
            ),

            ema200=D(
                "99"
            ),

            ema19_50_separation_percent=D(
                "0.10"
            ),

        )

        unit4b_bridge(
            invalid
        )

    except ValueError:

        rejected = True

    require(
        rejected,
        (
            "UNIT 4B invalid upstream "
            "close was not rejected."
        ),
    )

    rejected = False

    try:

        invalid = Unit3Output(

            latest_close=D(
                "100"
            ),

            ema19=D(
                "101"
            ),

            ema50=D(
                "100"
            ),

            ema200=D(
                "99"
            ),

            ema19_50_separation_percent=D(
                "-0.01"
            ),

        )

        unit4b_bridge(
            invalid
        )

    except ValueError:

        rejected = True

    require(
        rejected,
        (
            "UNIT 4B invalid upstream "
            "separation was not rejected."
        ),
    )

    log(
        "PASS: UNIT 4B INVALID UPSTREAM REJECTION"
    )


# ============================================================
# TEST 6
# EXECUTION FIREBREAK
# ============================================================

def test_unit4b_firebreak() -> None:

    require(
        WEEX_POST is False,
        "UNIT 4B WEEX POST firebreak failed.",
    )

    require(
        DEMO_ORDER is False,
        "UNIT 4B demo-order firebreak failed.",
    )

    require(
        REAL_ORDER is False,
        "UNIT 4B real-order firebreak failed.",
    )

    require(
        EXCHANGE_MUTATION is False,
        (
            "UNIT 4B exchange-mutation "
            "firebreak failed."
        ),
    )

    require(
        ORDER_PAYLOAD_GENERATED is False,
        (
            "UNIT 4B order-payload "
            "firebreak failed."
        ),
    )

    require(
        NETWORK_ACCESS is False,
        (
            "UNIT 4B network-access "
            "firebreak failed."
        ),
    )

    require(
        TRADING_DECISION_GENERATED is False,
        (
            "UNIT 4B trading-decision "
            "firebreak failed."
        ),
    )

    log(
        "PASS: UNIT 4B EXECUTION FIREBREAK"
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

    log(
        "NO TRADING DECISION GENERATED = TRUE"
    )


# ============================================================
# COMPLETE UNIT 4B TEST
# ============================================================

def run_unit_4b_tests() -> bool:

    separator()

    log(
        "RECONSTRUCTION UNIT 4B TEST START"
    )

    separator()

    test_bridge_exact_data_preservation()

    test_bridge_direction()

    test_bridge_regime_classification()

    test_bridge_signed_movement()

    test_bridge_invalid_upstream_rejection()

    test_unit4b_firebreak()

    separator()

    log(
        "UNIT 4B BRIDGE TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 4B RESULT = PASS"
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
            run_unit_4b_tests()
        )

    except Exception as exc:

        separator()

        log(
            "RECONSTRUCTION UNIT 4B RESULT = FAIL"
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
            "Unit 4B bridge test did not pass."
        )


if __name__ == "__main__":

    main()
