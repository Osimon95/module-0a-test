
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


# ============================================================
# START UNIT 11 STANDALONE EXTENSION V1
# ZERO INDENTATION
#
# PURPOSE:
# - Simulated Unit 10 -> Unit 11 handover
# - Continuous scan sequence simulation
# - Closed candle continuity
# - Duplicate rejection
# - Signal identity preservation
# - Signal expiry and reset
# - Flat position safety
# - Zero exchange writes
#
# FROZEN UNITS 1-10 = UNCHANGED
# EXISTING UNIT 11 TESTS = UNCHANGED
# REAL WEEX ACCESS = NONE
# ============================================================

def unit_11_extension_v1():

    print("=" * 70, flush=True)
    print(
        "UNIT 11 STANDALONE EXTENSION V1 START",
        flush=True,
    )

    passed = 0
    failed = 0

    def report(name, condition):

        nonlocal passed, failed

        if condition:
            passed += 1
            verdict = "PASS"
        else:
            failed += 1
            verdict = "FAIL"

        print(
            verdict + ": " + name,
            flush=True,
        )

    # --------------------------------------------------------
    # SIMULATED UNIT 10 HANDOVER PROVIDER
    # --------------------------------------------------------

    def simulated_unit_10_provider(
        scan,
        mode="BREAKOUT",
        direction="LONG",
        signal_id="BREAKOUT-LONG-001",
        candle_id=None,
        closed=True,
        qualified=True,
        flat=True,
        age_seconds=0,
    ):

        if candle_id is None:
            candle_id = 1800000000000 + (
                (scan - 1) * 60000
            )

        return {
            "unit": 10,
            "scan": scan,
            "mode": mode,
            "direction": direction,
            "signal_id": signal_id,
            "closed_candle_id": candle_id,
            "closed": closed,
            "qualified": qualified,
            "position_flat_verified": flat,
            "signal_age_seconds": age_seconds,
            "read_only": True,
            "trade_authorized": False,
            "exchange_write": False,
            "source": "SIMULATION",
        }

    # --------------------------------------------------------
    # STANDALONE UNIT 11 CONTINUITY ENGINE
    # NOT THE PRODUCTION UNIT 11 FUNCTION
    # --------------------------------------------------------

    def verify_sequence(records):

        confirmations = 0
        previous_candle = None
        previous_identity = None

        outputs = []

        for record in records:

            identity = (
                record.get("mode"),
                record.get("direction"),
                record.get("signal_id"),
            )

            candle = record.get(
                "closed_candle_id"
            )

            reason = "BLOCKED"
            verified = False

            safe = (
                record.get("unit") == 10
                and record.get("source") == "SIMULATION"
                and record.get("read_only") is True
                and record.get("trade_authorized") is False
                and record.get("exchange_write") is False
            )

            qualified = (
                record.get("qualified") is True
                and record.get("closed") is True
                and record.get("mode") in (
                    "SCALP",
                    "STRUCTURE",
                    "BREAKOUT",
                )
                and record.get("direction") in (
                    "LONG",
                    "SHORT",
                )
                and bool(record.get("signal_id"))
                and isinstance(candle, int)
            )

            age = record.get(
                "signal_age_seconds"
            )

            fresh = (
                isinstance(age, (int, float))
                and not isinstance(age, bool)
                and 0 <= age <= 120
            )

            if not safe:
                confirmations = 0
                previous_candle = None
                previous_identity = None
                reason = "UNSAFE_HANDOVER"

            elif not qualified:
                confirmations = 0
                previous_candle = None
                previous_identity = None
                reason = "NO_VALID_SIGNAL"

            elif not fresh:
                confirmations = 0
                previous_candle = None
                previous_identity = None
                reason = "SIGNAL_EXPIRED"

            elif identity != previous_identity:
                confirmations = 1
                previous_identity = identity
                previous_candle = candle
                reason = "FIRST_CONFIRMATION"

            elif candle == previous_candle:
                reason = "DUPLICATE_CANDLE"

            elif candle < previous_candle:
                reason = "STALE_CANDLE"

            elif candle - previous_candle != 60000:
                confirmations = 1
                previous_candle = candle
                reason = "CANDLE_GAP_RESTART"

            else:
                confirmations = min(
                    confirmations + 1,
                    2,
                )
                previous_candle = candle

                if confirmations >= 2:
                    verified = True
                    reason = "CONTINUITY_VERIFIED"
                else:
                    reason = "AWAITING_CONFIRMATION"

            flat = (
                record.get(
                    "position_flat_verified"
                ) is True
            )

            candidate_ready = (
                verified
                and flat
                and safe
                and fresh
                and qualified
            )

            result = {
                "scan": record.get("scan"),
                "mode": record.get("mode"),
                "direction": record.get("direction"),
                "signal_id": record.get("signal_id"),
                "reason": reason,
                "confirmations": confirmations,
                "continuity_verified": verified,
                "candidate_ready": candidate_ready,
                "trade_authorized": False,
                "exchange_write": False,
            }

            outputs.append(result)

        return outputs

    # --------------------------------------------------------
    # TEST 19: UNIT 10 HANDOVER
    # --------------------------------------------------------

    a = simulated_unit_10_provider(1)

    report(
        "19 UNIT 10 HANDOVER",
        a["unit"] == 10
        and a["mode"] == "BREAKOUT"
        and a["direction"] == "LONG"
        and a["source"] == "SIMULATION",
    )

    # --------------------------------------------------------
    # TEST 20: CONTINUOUS SCAN SEQUENCE
    # --------------------------------------------------------

    scans = [
        simulated_unit_10_provider(i)
        for i in range(1, 4)
    ]

    results = verify_sequence(scans)

    report(
        "20 CONTINUOUS SCAN SIMULATION",
        len(results) == 3
        and results[0]["confirmations"] == 1
        and results[1]["confirmations"] == 2
        and results[2]["confirmations"] == 2
        and results[2]["continuity_verified"],
    )

    # --------------------------------------------------------
    # TEST 21: DUPLICATE CANDLE
    # --------------------------------------------------------

    duplicate = [
        simulated_unit_10_provider(1),
        simulated_unit_10_provider(
            2,
            candle_id=1800000000000,
        ),
    ]

    duplicate_results = verify_sequence(
        duplicate
    )

    report(
        "21 DUPLICATE CANDLE REJECTED",
        duplicate_results[-1]["reason"]
        == "DUPLICATE_CANDLE"
        and duplicate_results[-1]["confirmations"] == 1,
    )

    # --------------------------------------------------------
    # TEST 22: MODE AND DIRECTION IDENTITY
    # --------------------------------------------------------

    changed = [
        simulated_unit_10_provider(1),
        simulated_unit_10_provider(
            2,
            mode="STRUCTURE",
            direction="SHORT",
            signal_id="STRUCTURE-SHORT-002",
        ),
    ]

    changed_results = verify_sequence(
        changed
    )

    report(
        "22 SIGNAL IDENTITY RESET",
        changed_results[-1]["confirmations"] == 1
        and changed_results[-1]["reason"]
        == "FIRST_CONFIRMATION",
    )

    # --------------------------------------------------------
    # TEST 23: SIGNAL EXPIRY
    # --------------------------------------------------------

    expired = [
        simulated_unit_10_provider(1),
        simulated_unit_10_provider(
            2,
            age_seconds=121,
        ),
    ]

    expired_results = verify_sequence(
        expired
    )

    report(
        "23 EXPIRED SIGNAL REJECTED",
        expired_results[-1]["reason"]
        == "SIGNAL_EXPIRED"
        and expired_results[-1]["confirmations"] == 0,
    )

    # --------------------------------------------------------
    # TEST 24: POSITION FLAT CHECK
    # --------------------------------------------------------

    occupied = [
        simulated_unit_10_provider(1),
        simulated_unit_10_provider(
            2,
            flat=False,
        ),
    ]

    occupied_results = verify_sequence(
        occupied
    )

    report(
        "24 NON-FLAT POSITION BLOCKED",
        occupied_results[-1][
            "continuity_verified"
        ] is True
        and occupied_results[-1][
            "candidate_ready"
        ] is False,
    )

    # --------------------------------------------------------
    # TEST 25: CONTINUITY CANDIDATE
    # --------------------------------------------------------

    ready = verify_sequence([
        simulated_unit_10_provider(1),
        simulated_unit_10_provider(2),
    ])

    report(
        "25 VERIFIED READ ONLY CANDIDATE",
        ready[-1]["candidate_ready"] is True
        and ready[-1]["trade_authorized"] is False,
    )

    # --------------------------------------------------------
    # TEST 26: ZERO EXCHANGE WRITES
    # --------------------------------------------------------

    unsafe = simulated_unit_10_provider(1)
    unsafe["exchange_write"] = True

    unsafe_results = verify_sequence([
        unsafe
    ])

    report(
        "26 EXCHANGE WRITE SAFETY",
        unsafe_results[-1]["reason"]
        == "UNSAFE_HANDOVER"
        and unsafe_results[-1]["candidate_ready"]
        is False
        and all(
            x["exchange_write"] is False
            for x in (
                results
                + duplicate_results
                + changed_results
                + expired_results
                + occupied_results
                + ready
                + unsafe_results
            )
        ),
    )

    # --------------------------------------------------------
    # FINAL EXTENSION REPORT
    # --------------------------------------------------------

    print("=" * 70, flush=True)

    print(
        "UNIT 11 EXTENSION TESTS PASSED =",
        passed,
        flush=True,
    )

    print(
        "UNIT 11 EXTENSION TESTS FAILED =",
        failed,
        flush=True,
    )

    print(
        "UNIT 11 EXTENSION SOURCE = SIMULATION",
        flush=True,
    )

    print(
        "UNIT 11 EXTENSION REAL WEEX ACCESS = NONE",
        flush=True,
    )

    print(
        "UNIT 11 EXTENSION TRADE AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 11 EXTENSION EXCHANGE WRITE = NONE",
        flush=True,
    )

    verdict = (
        "PASS" if failed == 0 else "FAIL"
    )

    print(
        "UNIT 11 EXTENSION FINAL VERDICT =",
        verdict,
        flush=True,
    )

    print("=" * 70, flush=True)

    return failed == 0


# ============================================================
# EXECUTE UNIT 11 EXTENSION
# ZERO INDENTATION
# ============================================================

UNIT_11_EXTENSION_V1_RESULT = (
    unit_11_extension_v1()
)

# ============================================================
# END UNIT 11 STANDALONE EXTENSION V1
# ZERO INDENTATION
#
# NO CHANGE TO UNITS 1-10
# NO PRODUCTION UNIT 11 REPLACEMENT
# NO EXCHANGE ORDERS
# ============================================================
