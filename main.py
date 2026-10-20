
# ============================================================
# START FRESH UNIT 11 STANDALONE
# ZERO INDENTATION
# SIGNAL CONTINUITY SIMULATION
# NO MAIN.PY IMPORT
# ZERO EXCHANGE WRITE
# ============================================================

from dataclasses import dataclass

REQUIRED_CONFIRMATIONS = 2
CANDLE_MS = 60000
SIGNAL_EXPIRY_SECONDS = 120

VALID_MODES = (
    "BREAKOUT",
    "STRUCTURE",
    "SCALP",
)

VALID_DIRECTIONS = (
    "LONG",
    "SHORT",
)


# ============================================================
# SIMULATED UNIT 10 SIGNAL INPUT
# ZERO INDENTATION
# ============================================================

@dataclass(frozen=True)
class Snapshot:

    candle_id: int
    observed_at: float

    mode: str = "NONE"
    direction: str = "NONE"

    qualified: bool = False
    signal_id: str = ""

    candle_closed: bool = True
    market_fresh: bool = True

    position_flat_verified: bool = False
    read_only: bool = True


# ============================================================
# FRESH UNIT 11 SIGNAL CONTINUITY ENGINE
# ZERO INDENTATION
# ============================================================

class Unit11:

    def __init__(self):
        self.reset()

    def reset(self):

        self.key = None
        self.last_candle_id = None
        self.first_seen = None
        self.confirmations = 0
        self.last_observation = None

    # ========================================================
    # PROCESS ONE SCAN
    # ========================================================

    def scan(self, x):

        if not isinstance(x, Snapshot):
            raise TypeError("Expected Snapshot")

        # ----------------------------------------------------
        # REJECT OUT-OF-ORDER OBSERVATIONS
        # ----------------------------------------------------

        if (
            self.last_observation is not None
            and x.observed_at < self.last_observation
        ):
            return self._result(
                "STALE_OBSERVATION"
            )

        self.last_observation = x.observed_at

        # ----------------------------------------------------
        # SAFETY CHECK
        # ----------------------------------------------------

        if not x.read_only:

            self.reset()

            return self._result(
                "UNSAFE_INPUT"
            )

        # ----------------------------------------------------
        # VALIDATE CLOSED MARKET CANDLE
        # ----------------------------------------------------

        if (
            not x.market_fresh
            or not x.candle_closed
            or not isinstance(x.candle_id, int)
            or x.candle_id <= 0
        ):

            self.reset()

            return self._result(
                "MARKET_CANDLE_UNVERIFIED"
            )

        # ----------------------------------------------------
        # VALIDATE QUALIFIED SIGNAL
        # ----------------------------------------------------

        if (
            not x.qualified
            or x.mode not in VALID_MODES
            or x.direction not in VALID_DIRECTIONS
        ):

            self.reset()

            return self._result(
                "NO_QUALIFIED_SIGNAL"
            )

        if not x.signal_id:

            self.reset()

            return self._result(
                "SIGNAL_ID_MISSING"
            )

        # ----------------------------------------------------
        # BUILD SIGNAL IDENTITY
        # ----------------------------------------------------

        key = (
            x.mode,
            x.direction,
            x.signal_id,
        )

        # ----------------------------------------------------
        # FIRST SIGNAL OR CHANGED SIGNAL
        # ----------------------------------------------------

        if self.key != key:

            self.reset()

            self.last_observation = x.observed_at

            self.key = key
            self.first_seen = x.observed_at

            self.last_candle_id = x.candle_id
            self.confirmations = 1

            return self._result(
                "FIRST_CONFIRMATION",
                x.position_flat_verified,
            )

        # ----------------------------------------------------
        # SIGNAL EXPIRY
        # ----------------------------------------------------

        if (
            x.observed_at - self.first_seen
            > SIGNAL_EXPIRY_SECONDS
        ):

            self.reset()

            self.last_observation = x.observed_at

            self.key = key
            self.first_seen = x.observed_at

            self.last_candle_id = x.candle_id
            self.confirmations = 1

            return self._result(
                "SIGNAL_EXPIRED_RESTART",
                x.position_flat_verified,
            )

        # ----------------------------------------------------
        # DUPLICATE CANDLE REJECTION
        # ----------------------------------------------------

        if x.candle_id == self.last_candle_id:

            return self._result(
                "DUPLICATE_CANDLE",
                x.position_flat_verified,
            )

        # ----------------------------------------------------
        # STALE CANDLE REJECTION
        # ----------------------------------------------------

        if x.candle_id < self.last_candle_id:

            return self._result(
                "STALE_CANDLE",
                x.position_flat_verified,
            )

        # ----------------------------------------------------
        # MISSING CLOSED CANDLE
        # ----------------------------------------------------

        if (
            x.candle_id - self.last_candle_id
            != CANDLE_MS
        ):

            self.reset()

            self.last_observation = x.observed_at

            self.key = key
            self.first_seen = x.observed_at

            self.last_candle_id = x.candle_id
            self.confirmations = 1

            return self._result(
                "CANDLE_GAP_RESTART",
                x.position_flat_verified,
            )

        # ----------------------------------------------------
        # CONTINUITY CONFIRMATION
        # ----------------------------------------------------

        self.last_candle_id = x.candle_id

        self.confirmations = min(
            REQUIRED_CONFIRMATIONS,
            self.confirmations + 1,
        )

        return self._result(
            "CONTINUITY_VERIFIED",
            x.position_flat_verified,
        )

    # ========================================================
    # GENERATE READ-ONLY RESULT
    # ========================================================

    def _result(self, reason, flat=False):

        continuity = (
            self.confirmations
            >= REQUIRED_CONFIRMATIONS
            and reason in (
                "CONTINUITY_VERIFIED",
                "DUPLICATE_CANDLE",
            )
        )

        return {

            "status":
                "VERIFIED" if continuity
                else "WAITING",

            "reason": reason,

            "mode":
                self.key[0]
                if self.key else "NONE",

            "direction":
                self.key[1]
                if self.key else "NONE",

            "closed_candle_id":
                self.last_candle_id,

            "confirmations":
                self.confirmations,

            "required":
                REQUIRED_CONFIRMATIONS,

            "continuity_verified":
                continuity,

            "position_flat_verified":
                bool(flat),

            "reentry_candidate":
                continuity and bool(flat),

            "trade_authorized":
                False,

            "exchange_write":
                "NONE",
        }


# ============================================================
# SIMULATED MARKET SIGNAL GENERATOR
# ZERO INDENTATION
# ============================================================

def snapshot(
    candle,
    seconds,
    mode="BREAKOUT",
    direction="LONG",
    signal="S1",
    **changes,
):

    fields = dict(
        candle_id=candle,
        observed_at=seconds,
        mode=mode,
        direction=direction,
        qualified=True,
        signal_id=signal,
    )

    fields.update(changes)

    return Snapshot(**fields)


# ============================================================
# FRESH UNIT 11 AUTOMATED TESTS
# ZERO INDENTATION
# ============================================================

def self_test():

    passed = 0
    failed = 0

    def run(name, sequence, check):

        nonlocal passed, failed

        results = []

        engine = Unit11()

        try:

            results = [
                engine.scan(s)
                for s in sequence
            ]

            ok = bool(check(results))

        except Exception as exc:

            ok = False

            print(
                "UNIT 11 TEST ERROR =",
                name,
                repr(exc),
                flush=True,
            )

        if ok:

            passed += 1

            print(
                "PASS:",
                name,
                flush=True,
            )

        else:

            failed += 1

            print(
                "FAIL:",
                name,
                flush=True,
            )

        for i, result in enumerate(results, 1):

            print(
                "SCAN",
                i,
                "|",
                result["reason"],
                "| CONFIRMATIONS =",
                result["confirmations"],
                "| VERIFIED =",
                result["continuity_verified"],
                flush=True,
            )

    # ========================================================
    # CONTROLLED CANDLE TIMESTAMP
    # ========================================================

    b = 1800000000000

    # TEST 1
    run(
        "FIRST CANDLE ONLY",
        [snapshot(b, 0)],
        lambda r:
            r[-1]["confirmations"] == 1
            and not r[-1]["continuity_verified"],
    )

    # TEST 2
    run(
        "TWO CONSECUTIVE CANDLES",
        [
            snapshot(b, 0),
            snapshot(b + CANDLE_MS, 60),
        ],
        lambda r:
            r[-1]["continuity_verified"],
    )

    # TEST 3
    run(
        "DUPLICATE DOES NOT COUNT",
        [
            snapshot(b, 0),
            snapshot(b, 10),
        ],
        lambda r:
            r[-1]["confirmations"] == 1,
    )

    # TEST 4
    run(
        "STALE CANDLE REJECTED",
        [
            snapshot(b, 0),
            snapshot(b - CANDLE_MS, 10),
        ],
        lambda r:
            r[-1]["reason"] == "STALE_CANDLE",
    )

    # TEST 5
    run(
        "GAP RESTARTS",
        [
            snapshot(b, 0),
            snapshot(b + 2 * CANDLE_MS, 60),
        ],
        lambda r:
            r[-1]["confirmations"] == 1
            and r[-1]["reason"]
            == "CANDLE_GAP_RESTART",
    )

    # TEST 6
    run(
        "MODE CHANGE RESTARTS",
        [
            snapshot(b, 0),
            snapshot(
                b + CANDLE_MS,
                60,
                mode="STRUCTURE",
            ),
        ],
        lambda r:
            r[-1]["confirmations"] == 1,
    )

    # TEST 7
    run(
        "DIRECTION CHANGE RESTARTS",
        [
            snapshot(b, 0),
            snapshot(
                b + CANDLE_MS,
                60,
                direction="SHORT",
            ),
        ],
        lambda r:
            r[-1]["confirmations"] == 1,
    )

    # TEST 8
    run(
        "SIGNAL ID CHANGE RESTARTS",
        [
            snapshot(b, 0),
            snapshot(
                b + CANDLE_MS,
                60,
                signal="S2",
            ),
        ],
        lambda r:
            r[-1]["confirmations"] == 1,
    )

    # TEST 9
    run(
        "SIGNAL EXPIRES",
        [
            snapshot(b, 0),
            snapshot(b + CANDLE_MS, 121),
        ],
        lambda r:
            r[-1]["reason"]
            == "SIGNAL_EXPIRED_RESTART",
    )

    # TEST 10
    run(
        "IDLE RESETS",
        [
            snapshot(b, 0),
            snapshot(
                b + CANDLE_MS,
                60,
                qualified=False,
            ),
        ],
        lambda r:
            r[-1]["confirmations"] == 0,
    )

    # TEST 11
    run(
        "UNFINISHED CANDLE REJECTED",
        [
            snapshot(
                b,
                0,
                candle_closed=False,
            ),
        ],
        lambda r:
            r[-1]["reason"]
            == "MARKET_CANDLE_UNVERIFIED",
    )

    # TEST 12
    run(
        "NO SIGNAL ID REJECTED",
        [
            snapshot(
                b,
                0,
                signal="",
            ),
        ],
        lambda r:
            r[-1]["reason"]
            == "SIGNAL_ID_MISSING",
    )

    # TEST 13
    run(
        "READ ONLY ENFORCED",
        [
            snapshot(
                b,
                0,
                read_only=False,
            ),
        ],
        lambda r:
            r[-1]["reason"]
            == "UNSAFE_INPUT",
    )

    # TEST 14
    run(
        "NO FLAT VERIFICATION",
        [
            snapshot(b, 0),
            snapshot(b + CANDLE_MS, 60),
        ],
        lambda r:
            r[-1]["continuity_verified"]
            and not r[-1]["reentry_candidate"],
    )

    # TEST 15
    run(
        "FLAT VERIFIED CANDIDATE",
        [
            snapshot(b, 0),
            snapshot(
                b + CANDLE_MS,
                60,
                position_flat_verified=True,
            ),
        ],
        lambda r:
            r[-1]["reentry_candidate"]
            and not r[-1]["trade_authorized"],
    )

    # TEST 16
    run(
        "SCALP CONTINUITY",
        [
            snapshot(
                b,
                0,
                mode="SCALP",
            ),
            snapshot(
                b + CANDLE_MS,
                60,
                mode="SCALP",
            ),
        ],
        lambda r:
            r[-1]["continuity_verified"],
    )

    # TEST 17
    run(
        "OUT OF ORDER OBSERVATION",
        [
            snapshot(b, 60),
            snapshot(
                b + CANDLE_MS,
                50,
            ),
        ],
        lambda r:
            r[-1]["reason"]
            == "STALE_OBSERVATION",
    )

    # TEST 18
    run(
        "NO EXCHANGE WRITES",
        [
            snapshot(b, 0),
            snapshot(b + CANDLE_MS, 60),
        ],
        lambda r:
            all(
                z["exchange_write"] == "NONE"
                and not z["trade_authorized"]
                for z in r
            ),
    )

    # ========================================================
    # ACTUAL CALCULATED TEST SUMMARY
    # ========================================================

    print("=" * 68, flush=True)

    print(
        "UNIT 11 STANDALONE TESTS PASSED =",
        passed,
        flush=True,
    )

    print(
        "UNIT 11 STANDALONE TESTS FAILED =",
        failed,
        flush=True,
    )

    print(
        "UNIT 11 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "UNIT 11 FINAL VERDICT =",
        "PASS" if failed == 0 else "FAIL",
        flush=True,
    )

    return failed == 0


# ============================================================
# EXECUTE FRESH UNIT 11 STANDALONE
# ZERO INDENTATION
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        0 if self_test() else 1
    )


# ============================================================
# END FRESH UNIT 11 STANDALONE
# ZERO INDENTATION
# DO NOT MODIFY FROZEN UNITS 1-10
# ============================================================
