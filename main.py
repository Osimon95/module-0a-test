from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional


STAGE = "R36F.15.10.2"

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
WRITE_TRANSPORT = False

CLASSIFICATION_CONFIRMATIONS_REQUIRED = 3

MODE_SCALP = "SCALP"
MODE_STRUCTURE = "STRUCTURE"
MODE_BREAKOUT = "BREAKOUT"

VALID_MODES = {
    MODE_SCALP,
    MODE_STRUCTURE,
    MODE_BREAKOUT,
}


def D(value):
    if isinstance(value, Decimal):
        return value

    try:
        return Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        raise ValueError(
            f"Invalid decimal value: {value}"
        )


def utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat()


def log(message):
    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def separator():
    log(
        "-" * 100
    )


@dataclass
class MarketSnapshot:
    price: Decimal

    ema19: Decimal
    ema50: Decimal
    ema200: Decimal

    ema_structure: str
    ema_ideal_direction: Optional[str]

    long_valid_clusters: int
    short_valid_clusters: int

    short_term_move_percent: Decimal
    ema19_50_separation_percent: Decimal


@dataclass
class Classification:
    mode: str
    reason: str
    direction: Optional[str]


class ExclusiveAutoClassifier:

    def __init__(
        self,
        confirmations_required=3,
    ):
        self.confirmations_required = (
            confirmations_required
        )

        self.active_mode = None

        self.pending_mode = None
        self.pending_count = 0

        self.mode_locked = False
        self.locked_mode = None

    def raw_classify(
        self,
        snapshot,
    ):
        strong_bullish = (
            snapshot.ema_structure
            == "STRONG_BULLISH"
        )

        strong_bearish = (
            snapshot.ema_structure
            == "STRONG_BEARISH"
        )

        strong_direction = (
            snapshot.ema_ideal_direction
            in (
                "LONG",
                "SHORT",
            )
        )

        absolute_move = abs(
            snapshot.short_term_move_percent
        )

        ema_separation = abs(
            snapshot.ema19_50_separation_percent
        )

        if (
            strong_direction
            and (
                strong_bullish
                or strong_bearish
            )
            and absolute_move
            >= Decimal("1.00")
        ):
            return Classification(
                mode=MODE_BREAKOUT,
                direction=(
                    snapshot.ema_ideal_direction
                ),
                reason=(
                    "STRONG_EMA_DIRECTION_"
                    "PLUS_LARGE_SHORT_TERM_MOVE"
                ),
            )

        if (
            strong_direction
            and (
                strong_bullish
                or strong_bearish
            )
        ):
            direction = (
                snapshot.ema_ideal_direction
            )

            if direction == "LONG":
                cluster_count = (
                    snapshot.long_valid_clusters
                )
            else:
                cluster_count = (
                    snapshot.short_valid_clusters
                )

            if cluster_count >= 2:
                return Classification(
                    mode=MODE_STRUCTURE,
                    direction=direction,
                    reason=(
                        "STRONG_EMA_DIRECTION_"
                        "WITH_TWO_OR_MORE_"
                        "VALID_CLUSTERS"
                    ),
                )

            if (
                cluster_count < 2
                and (
                    absolute_move
                    >= Decimal("0.50")
                    or ema_separation
                    >= Decimal("0.10")
                )
            ):
                return Classification(
                    mode=MODE_BREAKOUT,
                    direction=direction,
                    reason=(
                        "STRONG_EMA_DIRECTION_"
                        "BUT_TWO_CLUSTER_"
                        "STRUCTURE_UNAVAILABLE"
                    ),
                )

        return Classification(
            mode=MODE_SCALP,
            direction=(
                snapshot.ema_ideal_direction
            ),
            reason=(
                "NO_CONFIRMED_STRUCTURE_"
                "OR_BREAKOUT_CONDITION"
            ),
        )

    def update(
        self,
        snapshot,
    ):
        raw = self.raw_classify(
            snapshot
        )

        if self.mode_locked:
            return {
                "raw_mode":
                    raw.mode,

                "active_mode":
                    self.locked_mode,

                "reason":
                    (
                        "MODE_LOCKED_"
                        "FOR_ACTIVE_TRADE"
                    ),

                "direction":
                    raw.direction,

                "pending_mode":
                    self.pending_mode,

                "pending_count":
                    self.pending_count,

                "locked":
                    True,
            }

        if self.active_mode is None:
            self.active_mode = (
                raw.mode
            )

            self.pending_mode = None
            self.pending_count = 0

            return {
                "raw_mode":
                    raw.mode,

                "active_mode":
                    self.active_mode,

                "reason":
                    (
                        "INITIAL_MODE_"
                        "SELECTED:"
                        + raw.reason
                    ),

                "direction":
                    raw.direction,

                "pending_mode":
                    None,

                "pending_count":
                    0,

                "locked":
                    False,
            }

        if raw.mode == self.active_mode:
            self.pending_mode = None
            self.pending_count = 0

            return {
                "raw_mode":
                    raw.mode,

                "active_mode":
                    self.active_mode,

                "reason":
                    (
                        "ACTIVE_MODE_"
                        "CONFIRMED:"
                        + raw.reason
                    ),

                "direction":
                    raw.direction,

                "pending_mode":
                    None,

                "pending_count":
                    0,

                "locked":
                    False,
            }

        if raw.mode != self.pending_mode:
            self.pending_mode = (
                raw.mode
            )

            self.pending_count = 1

        else:
            self.pending_count += 1

        if (
            self.pending_count
            >= self.confirmations_required
        ):
            old_mode = (
                self.active_mode
            )

            self.active_mode = (
                self.pending_mode
            )

            self.pending_mode = None
            self.pending_count = 0

            return {
                "raw_mode":
                    raw.mode,

                "active_mode":
                    self.active_mode,

                "reason":
                    (
                        "MODE_CHANGED_AFTER_"
                        f"{self.confirmations_required}_"
                        "CONFIRMATIONS:"
                        f"{old_mode}_TO_"
                        f"{self.active_mode}"
                    ),

                "direction":
                    raw.direction,

                "pending_mode":
                    None,

                "pending_count":
                    0,

                "locked":
                    False,
            }

        return {
            "raw_mode":
                raw.mode,

            "active_mode":
                self.active_mode,

            "reason":
                (
                    "MODE_CHANGE_PENDING:"
                    + raw.reason
                ),

            "direction":
                raw.direction,

            "pending_mode":
                self.pending_mode,

            "pending_count":
                self.pending_count,

            "locked":
                False,
        }

    def lock_mode(
        self,
    ):
        if self.active_mode not in VALID_MODES:
            raise RuntimeError(
                "NO_ACTIVE_MODE_TO_LOCK"
            )

        self.mode_locked = True
        self.locked_mode = (
            self.active_mode
        )

    def unlock_mode(
        self,
    ):
        self.mode_locked = False
        self.locked_mode = None

        self.pending_mode = None
        self.pending_count = 0


def snapshot(
    price,
    ema19,
    ema50,
    ema200,
    structure,
    ideal_direction,
    long_clusters,
    short_clusters,
    move_percent,
    separation_percent,
):
    return MarketSnapshot(
        price=D(price),

        ema19=D(ema19),
        ema50=D(ema50),
        ema200=D(ema200),

        ema_structure=structure,

        ema_ideal_direction=(
            ideal_direction
        ),

        long_valid_clusters=(
            int(long_clusters)
        ),

        short_valid_clusters=(
            int(short_clusters)
        ),

        short_term_move_percent=D(
            move_percent
        ),

        ema19_50_separation_percent=D(
            separation_percent
        ),
    )


def assert_pass(
    condition,
    name,
):
    if not condition:
        raise AssertionError(
            name
        )

    log(
        f"PASS: {name}"
    )


def print_result(
    name,
    result,
):
    log(
        f"{STAGE} TEST={name} "
        f"raw_mode={result['raw_mode']} "
        f"active_mode={result['active_mode']} "
        f"direction={result['direction']} "
        f"pending_mode={result['pending_mode']} "
        f"pending_count={result['pending_count']} "
        f"locked={result['locked']} "
        f"reason={result['reason']}"
    )


def run_test_1_scalp():

    separator()

    log(
        f"{STAGE} TEST 1: "
        "NORMAL SMALL-MOVEMENT MARKET"
    )

    classifier = (
        ExclusiveAutoClassifier()
    )

    s = snapshot(
        price="75640",
        ema19="75642",
        ema50="75645",
        ema200="75660",
        structure="MIXED",
        ideal_direction=None,
        long_clusters=1,
        short_clusters=1,
        move_percent="0.12",
        separation_percent="0.004",
    )

    result = classifier.update(
        s
    )

    print_result(
        "SCALP",
        result,
    )

    assert_pass(
        result["active_mode"]
        == MODE_SCALP,
        "NORMAL_MARKET_SELECTS_SCALP",
    )


def run_test_2_structure():

    separator()

    log(
        f"{STAGE} TEST 2: "
        "STRONG TREND WITH "
        "TWO VALID CLUSTERS"
    )

    classifier = (
        ExclusiveAutoClassifier()
    )

    s = snapshot(
        price="75640",
        ema19="75700",
        ema50="75650",
        ema200="75500",
        structure="STRONG_BULLISH",
        ideal_direction="LONG",
        long_clusters=3,
        short_clusters=1,
        move_percent="0.35",
        separation_percent="0.066",
    )

    result = classifier.update(
        s
    )

    print_result(
        "STRUCTURE",
        result,
    )

    assert_pass(
        result["active_mode"]
        == MODE_STRUCTURE,
        "TWO_CLUSTER_TREND_SELECTS_STRUCTURE",
    )


def run_test_3_breakout_large_move():

    separator()

    log(
        f"{STAGE} TEST 3: "
        "LARGE BULLISH BREAKOUT"
    )

    classifier = (
        ExclusiveAutoClassifier()
    )

    s = snapshot(
        price="79200",
        ema19="78900",
        ema50="78300",
        ema200="77500",
        structure="STRONG_BULLISH",
        ideal_direction="LONG",
        long_clusters=1,
        short_clusters=4,
        move_percent="3.70",
        separation_percent="0.77",
    )

    result = classifier.update(
        s
    )

    print_result(
        "BREAKOUT_LARGE_MOVE",
        result,
    )

    assert_pass(
        result["active_mode"]
        == MODE_BREAKOUT,
        "LARGE_TREND_MOVE_SELECTS_BREAKOUT",
    )


def run_test_4_breakout_consumed_structure():

    separator()

    log(
        f"{STAGE} TEST 4: "
        "STRONG TREND WITH "
        "CONSUMED HISTORICAL STRUCTURE"
    )

    classifier = (
        ExclusiveAutoClassifier()
    )

    s = snapshot(
        price="79000",
        ema19="78950",
        ema50="78800",
        ema200="78000",
        structure="STRONG_BULLISH",
        ideal_direction="LONG",
        long_clusters=1,
        short_clusters=3,
        move_percent="0.70",
        separation_percent="0.19",
    )

    result = classifier.update(
        s
    )

    print_result(
        "BREAKOUT_ONE_CLUSTER",
        result,
    )

    assert_pass(
        result["active_mode"]
        == MODE_BREAKOUT,
        "ONE_CLUSTER_STRONG_TREND_SELECTS_BREAKOUT",
    )


def run_test_5_hysteresis():

    separator()

    log(
        f"{STAGE} TEST 5: "
        "MODE CHANGE CONFIRMATION"
    )

    classifier = (
        ExclusiveAutoClassifier(
            confirmations_required=3
        )
    )

    scalp_snapshot = snapshot(
        price="75640",
        ema19="75640",
        ema50="75642",
        ema200="75650",
        structure="MIXED",
        ideal_direction=None,
        long_clusters=1,
        short_clusters=1,
        move_percent="0.10",
        separation_percent="0.003",
    )

    breakout_snapshot = snapshot(
        price="76500",
        ema19="76450",
        ema50="76100",
        ema200="75500",
        structure="STRONG_BULLISH",
        ideal_direction="LONG",
        long_clusters=1,
        short_clusters=3,
        move_percent="1.20",
        separation_percent="0.46",
    )

    first = classifier.update(
        scalp_snapshot
    )

    assert_pass(
        first["active_mode"]
        == MODE_SCALP,
        "HYSTERESIS_STARTS_SCALP",
    )

    change_1 = classifier.update(
        breakout_snapshot
    )

    print_result(
        "HYSTERESIS_1",
        change_1,
    )

    assert_pass(
        (
            change_1["active_mode"]
            == MODE_SCALP
            and
            change_1["pending_mode"]
            == MODE_BREAKOUT
            and
            change_1["pending_count"]
            == 1
        ),
        "FIRST_BREAKOUT_SIGNAL_DOES_NOT_SWITCH",
    )

    change_2 = classifier.update(
        breakout_snapshot
    )

    print_result(
        "HYSTERESIS_2",
        change_2,
    )

    assert_pass(
        (
            change_2["active_mode"]
            == MODE_SCALP
            and
            change_2["pending_count"]
            == 2
        ),
        "SECOND_BREAKOUT_SIGNAL_DOES_NOT_SWITCH",
    )

    change_3 = classifier.update(
        breakout_snapshot
    )

    print_result(
        "HYSTERESIS_3",
        change_3,
    )

    assert_pass(
        change_3["active_mode"]
        == MODE_BREAKOUT,
        "THIRD_BREAKOUT_SIGNAL_SWITCHES_MODE",
    )


def run_test_6_noise_reset():

    separator()

    log(
        f"{STAGE} TEST 6: "
        "ONE-CYCLE BREAKOUT NOISE"
    )

    classifier = (
        ExclusiveAutoClassifier(
            confirmations_required=3
        )
    )

    scalp_snapshot = snapshot(
        price="75640",
        ema19="75640",
        ema50="75642",
        ema200="75650",
        structure="MIXED",
        ideal_direction=None,
        long_clusters=1,
        short_clusters=1,
        move_percent="0.10",
        separation_percent="0.003",
    )

    breakout_snapshot = snapshot(
        price="76500",
        ema19="76450",
        ema50="76100",
        ema200="75500",
        structure="STRONG_BULLISH",
        ideal_direction="LONG",
        long_clusters=1,
        short_clusters=3,
        move_percent="1.20",
        separation_percent="0.46",
    )

    classifier.update(
        scalp_snapshot
    )

    classifier.update(
        breakout_snapshot
    )

    result = classifier.update(
        scalp_snapshot
    )

    print_result(
        "NOISE_RESET",
        result,
    )

    assert_pass(
        (
            result["active_mode"]
            == MODE_SCALP
            and
            result["pending_mode"]
            is None
            and
            result["pending_count"]
            == 0
        ),
        "ONE_CYCLE_NOISE_CANNOT_CHANGE_MODE",
    )


def run_test_7_mode_lock():

    separator()

    log(
        f"{STAGE} TEST 7: "
        "ACTIVE TRADE MODE LOCK"
    )

    classifier = (
        ExclusiveAutoClassifier()
    )

    structure_snapshot = snapshot(
        price="75640",
        ema19="75700",
        ema50="75650",
        ema200="75500",
        structure="STRONG_BULLISH",
        ideal_direction="LONG",
        long_clusters=3,
        short_clusters=1,
        move_percent="0.35",
        separation_percent="0.066",
    )

    breakout_snapshot = snapshot(
        price="77000",
        ema19="76800",
        ema50="76200",
        ema200="75500",
        structure="STRONG_BULLISH",
        ideal_direction="LONG",
        long_clusters=1,
        short_clusters=4,
        move_percent="1.80",
        separation_percent="0.78",
    )

    first = classifier.update(
        structure_snapshot
    )

    assert_pass(
        first["active_mode"]
        == MODE_STRUCTURE,
        "LOCK_TEST_STARTS_STRUCTURE",
    )

    classifier.lock_mode()

    locked = classifier.update(
        breakout_snapshot
    )

    print_result(
        "MODE_LOCK",
        locked,
    )

    assert_pass(
        (
            locked["active_mode"]
            == MODE_STRUCTURE
            and
            locked["raw_mode"]
            == MODE_BREAKOUT
            and
            locked["locked"]
            is True
        ),
        "BREAKOUT_CANNOT_CHANGE_LOCKED_STRUCTURE_TRADE",
    )

    classifier.unlock_mode()

    assert_pass(
        classifier.mode_locked
        is False,
        "MODE_UNLOCKS_AFTER_TRADE_CLOSE",
    )


def run_test_8_exclusivity():

    separator()

    log(
        f"{STAGE} TEST 8: "
        "EXCLUSIVE MODE GUARANTEE"
    )

    classifier = (
        ExclusiveAutoClassifier()
    )

    test_snapshots = [
        snapshot(
            "75640",
            "75640",
            "75642",
            "75650",
            "MIXED",
            None,
            1,
            1,
            "0.10",
            "0.003",
        ),

        snapshot(
            "75640",
            "75700",
            "75650",
            "75500",
            "STRONG_BULLISH",
            "LONG",
            3,
            1,
            "0.35",
            "0.066",
        ),

        snapshot(
            "79200",
            "78900",
            "78300",
            "77500",
            "STRONG_BULLISH",
            "LONG",
            1,
            4,
            "3.70",
            "0.77",
        ),
    ]

    for index, s in enumerate(
        test_snapshots,
        start=1,
    ):
        raw = classifier.raw_classify(
            s
        )

        assert_pass(
            raw.mode in VALID_MODES,
            (
                "EXCLUSIVE_CLASSIFICATION_"
                f"{index}"
            ),
        )

        assert_pass(
            isinstance(
                raw.mode,
                str,
            ),
            (
                "ONLY_ONE_MODE_RETURNED_"
                f"{index}"
            ),
        )


def run_all_tests():

    separator()

    log(
        f"{STAGE} "
        "EXCLUSIVE AUTO-MODE "
        "CLASSIFIER TEST START"
    )

    log(
        f"{STAGE} "
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"{STAGE} "
        f"DEMO_ORDER_EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        f"{STAGE} "
        f"WRITE_TRANSPORT="
        f"{WRITE_TRANSPORT}"
    )

    log(
        f"{STAGE} "
        "THIS UNIT DOES NOT "
        "CONNECT TO WEEX"
    )

    separator()

    run_test_1_scalp()

    run_test_2_structure()

    run_test_3_breakout_large_move()

    run_test_4_breakout_consumed_structure()

    run_test_5_hysteresis()

    run_test_6_noise_reset()

    run_test_7_mode_lock()

    run_test_8_exclusivity()

    separator()

    assert_pass(
        REAL_ORDER_EXECUTION
        is False,
        "REAL_ORDER_EXECUTION_DISABLED",
    )

    assert_pass(
        DEMO_ORDER_EXECUTION
        is False,
        "DEMO_ORDER_EXECUTION_DISABLED",
    )

    assert_pass(
        WRITE_TRANSPORT
        is False,
        "WRITE_TRANSPORT_DISABLED",
    )

    separator()

    log(
        f"{STAGE} "
        "FINAL STATUS = PASS"
    )

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO DEMO ORDER WAS SENT"
    )

    log(
        "NO EXCHANGE MUTATION WAS SENT"
    )

    separator()


if __name__ == "__main__":
    run_all_tests()
