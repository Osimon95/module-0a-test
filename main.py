#!/usr/bin/env python3

"""
R36F.15.10
HISTORICAL CLUSTER REJECTION DIAGNOSTIC UNIT

PURPOSE
-------
Determine whether R36F.15.9 is missing otherwise useful BTC moves because
the historical TP cluster gates are too restrictive.

THIS UNIT DOES NOT:
- place real orders
- place demo orders
- modify leverage
- modify positions
- weaken required_clusters=2
- alter R36F.15.9 strategy logic

IT ONLY DIAGNOSES WHY CLUSTERS PASS OR FAIL.

CURRENT FROZEN POLICY
---------------------
CLUSTER_TOLERANCE_PERCENT = 0.20
MIN_CLUSTER_TOUCHES = 2
REQUIRED_CLUSTERS = 2

LONG:
    historical resistance cluster must be ABOVE entry

SHORT:
    historical support cluster must be BELOW entry
"""

from decimal import Decimal, InvalidOperation
import json
import os
import sys
import traceback
from datetime import datetime, timezone


STAGE = "R36F.15.10"

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
WRITE_TRANSPORT = False

CLUSTER_TOLERANCE_PERCENT = Decimal(
    os.getenv("R36F1510_CLUSTER_TOLERANCE_PERCENT", "0.20")
)

MIN_CLUSTER_TOUCHES = int(
    os.getenv("R36F1510_MIN_CLUSTER_TOUCHES", "2")
)

REQUIRED_CLUSTERS = int(
    os.getenv("R36F1510_REQUIRED_CLUSTERS", "2")
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(f"{utc_now()} {message}", flush=True)


def d(value):
    return Decimal(str(value))


def safe_decimal(value):
    try:
        return d(value)
    except (InvalidOperation, ValueError, TypeError):
        return None


def calculate_member_spread_percent(members):
    if not members:
        return None

    values = []

    for value in members:
        parsed = safe_decimal(value)

        if parsed is None:
            return None

        values.append(parsed)

    if len(values) < 2:
        return Decimal("0")

    lowest = min(values)
    highest = max(values)

    midpoint = sum(values) / Decimal(len(values))

    if midpoint <= 0:
        return None

    spread = (
        (highest - lowest)
        / midpoint
        * Decimal("100")
    )

    return spread


def audit_cluster(
    entry_price,
    direction,
    cluster,
    cluster_number,
):
    reasons = []

    entry = safe_decimal(entry_price)

    if entry is None or entry <= 0:
        raise ValueError(
            "ENTRY_PRICE_INVALID"
        )

    direction = str(direction).upper().strip()

    if direction not in ("LONG", "SHORT"):
        raise ValueError(
            "DIRECTION_MUST_BE_LONG_OR_SHORT"
        )

    if not isinstance(cluster, dict):
        return {
            "cluster_number": cluster_number,
            "valid": False,
            "reasons": [
                "MALFORMED_CLUSTER"
            ],
        }

    average = safe_decimal(
        cluster.get("average")
    )

    try:
        touches = int(
            cluster.get("touches", 0)
        )
    except Exception:
        touches = 0

    members = cluster.get(
        "members",
        [],
    )

    if not isinstance(members, list):
        members = []

    if average is None:
        reasons.append(
            "AVERAGE_NOT_NUMERIC"
        )

    elif average <= 0:
        reasons.append(
            "NON_POSITIVE_AVERAGE"
        )

    else:
        if (
            direction == "LONG"
            and average <= entry
        ):
            reasons.append(
                "CLUSTER_NOT_ABOVE_ENTRY"
            )

        if (
            direction == "SHORT"
            and average >= entry
        ):
            reasons.append(
                "CLUSTER_NOT_BELOW_ENTRY"
            )

    if touches < MIN_CLUSTER_TOUCHES:
        reasons.append(
            "INSUFFICIENT_TOUCHES"
        )

    spread_percent = (
        calculate_member_spread_percent(
            members
        )
    )

    if (
        spread_percent is not None
        and spread_percent
        > CLUSTER_TOLERANCE_PERCENT
    ):
        reasons.append(
            "CLUSTER_SPREAD_EXCEEDS_TOLERANCE"
        )

    valid = len(reasons) == 0

    return {
        "cluster_number": cluster_number,
        "direction": direction,
        "entry_price": str(entry),
        "average": (
            str(average)
            if average is not None
            else None
        ),
        "touches": touches,
        "minimum_touches":
            MIN_CLUSTER_TOUCHES,
        "spread_percent": (
            str(spread_percent)
            if spread_percent
            is not None
            else None
        ),
        "maximum_spread_percent":
            str(
                CLUSTER_TOLERANCE_PERCENT
            ),
        "valid": valid,
        "reasons": (
            ["VALID"]
            if valid
            else reasons
        ),
    }


def audit_direction(
    entry_price,
    direction,
    candidates,
):
    results = []

    for number, candidate in enumerate(
        candidates,
        start=1,
    ):
        result = audit_cluster(
            entry_price=entry_price,
            direction=direction,
            cluster=candidate,
            cluster_number=number,
        )

        results.append(result)

    valid_clusters = [
        result
        for result in results
        if result.get("valid")
    ]

    valid_count = len(
        valid_clusters
    )

    approved = (
        valid_count
        >= REQUIRED_CLUSTERS
    )

    return {
        "stage": STAGE,
        "direction": direction,
        "entry_price":
            str(entry_price),
        "required_clusters":
            REQUIRED_CLUSTERS,
        "valid_cluster_count":
            valid_count,
        "candidate_count":
            len(results),
        "approval": (
            "APPROVED"
            if approved
            else "REJECTED"
        ),
        "candidates":
            results,
    }


def print_audit(audit):
    log(
        "--------------------------------"
        "--------------------------------"
    )

    log(
        f"{STAGE} "
        f"{audit['direction']} "
        f"CLUSTER AUDIT"
    )

    log(
        f"{STAGE} "
        f"{audit['direction']} "
        f"ENTRY_PRICE = "
        f"{audit['entry_price']}"
    )

    log(
        f"{STAGE} "
        f"{audit['direction']} "
        f"CANDIDATE_COUNT = "
        f"{audit['candidate_count']}"
    )

    log(
        f"{STAGE} "
        f"{audit['direction']} "
        f"VALID_CLUSTER_COUNT = "
        f"{audit['valid_cluster_count']}"
    )

    log(
        f"{STAGE} "
        f"{audit['direction']} "
        f"REQUIRED_CLUSTERS = "
        f"{audit['required_clusters']}"
    )

    for candidate in (
        audit["candidates"]
    ):
        log(
            f"{STAGE} "
            f"{audit['direction']} "
            f"CLUSTER "
            f"{candidate['cluster_number']} "
            f"AVG="
            f"{candidate.get('average')} "
            f"TOUCHES="
            f"{candidate.get('touches')} "
            f"SPREAD_PERCENT="
            f"{candidate.get('spread_percent')} "
            f"VALID="
            f"{candidate.get('valid')} "
            f"REASONS="
            f"{','.join(candidate['reasons'])}"
        )

    log(
        f"{STAGE} "
        f"{audit['direction']} "
        f"FINAL_APPROVAL = "
        f"{audit['approval']}"
    )


def assert_test(
    name,
    condition,
):
    if condition:
        log(
            f"PASS: {name}"
        )
        return True

    log(
        f"FAIL: {name}"
    )

    return False


def run_synthetic_tests():
    log(
        "================================"
        "================================"
    )

    log(
        f"{STAGE}: STARTING "
        "DETERMINISTIC SYNTHETIC TESTS"
    )

    log(
        "================================"
        "================================"
    )

    all_passed = True

    entry = Decimal("79000")

    test_1 = [
        {
            "average": "79200",
            "touches": 2,
            "members": [
                "79180",
                "79220",
            ],
        },
        {
            "average": "79500",
            "touches": 3,
            "members": [
                "79480",
                "79510",
                "79510",
            ],
        },
    ]

    audit_1 = audit_direction(
        entry,
        "LONG",
        test_1,
    )

    print_audit(audit_1)

    all_passed &= assert_test(
        "TWO_VALID_LONG_CLUSTERS_APPROVED",
        (
            audit_1[
                "valid_cluster_count"
            ]
            == 2
            and audit_1[
                "approval"
            ]
            == "APPROVED"
        ),
    )

    test_2 = [
        {
            "average": "78800",
            "touches": 3,
            "members": [
                "78790",
                "78810",
                "78800",
            ],
        },
        {
            "average": "79300",
            "touches": 1,
            "members": [
                "79300",
            ],
        },
        {
            "average": "79600",
            "touches": 3,
            "members": [
                "79500",
                "79600",
                "79700",
            ],
        },
    ]

    audit_2 = audit_direction(
        entry,
        "LONG",
        test_2,
    )

    print_audit(audit_2)

    reasons_2 = [
        reason
        for candidate
        in audit_2["candidates"]
        for reason
        in candidate["reasons"]
    ]

    all_passed &= assert_test(
        "WRONG_SIDE_OF_ENTRY_DETECTED",
        (
            "CLUSTER_NOT_ABOVE_ENTRY"
            in reasons_2
        ),
    )

    all_passed &= assert_test(
        "INSUFFICIENT_TOUCHES_DETECTED",
        (
            "INSUFFICIENT_TOUCHES"
            in reasons_2
        ),
    )

    all_passed &= assert_test(
        "CLUSTER_TOLERANCE_FAILURE_DETECTED",
        (
            "CLUSTER_SPREAD_EXCEEDS_TOLERANCE"
            in reasons_2
        ),
    )

    all_passed &= assert_test(
        "INVALID_LONG_SET_REJECTED",
        (
            audit_2[
                "approval"
            ]
            == "REJECTED"
        ),
    )

    test_3 = [
        {
            "average": "78750",
            "touches": 2,
            "members": [
                "78740",
                "78760",
            ],
        },
        {
            "average": "78400",
            "touches": 2,
            "members": [
                "78390",
                "78410",
            ],
        },
    ]

    audit_3 = audit_direction(
        entry,
        "SHORT",
        test_3,
    )

    print_audit(audit_3)

    all_passed &= assert_test(
        "TWO_VALID_SHORT_CLUSTERS_APPROVED",
        (
            audit_3[
                "valid_cluster_count"
            ]
            == 2
            and audit_3[
                "approval"
            ]
            == "APPROVED"
        ),
    )

    all_passed &= assert_test(
        "REAL_ORDER_EXECUTION_DISABLED",
        REAL_ORDER_EXECUTION
        is False,
    )

    all_passed &= assert_test(
        "DEMO_ORDER_EXECUTION_DISABLED",
        DEMO_ORDER_EXECUTION
        is False,
    )

    all_passed &= assert_test(
        "WRITE_TRANSPORT_DISABLED",
        WRITE_TRANSPORT
        is False,
    )

    all_passed &= assert_test(
        "REQUIRED_CLUSTERS_REMAINS_TWO",
        REQUIRED_CLUSTERS
        == 2,
    )

    if all_passed:
        final_status = "PASS"
    else:
        final_status = "FAIL"

    log(
        "================================"
        "================================"
    )

    log(
        f"{STAGE} "
        f"SYNTHETIC TEST FINAL STATUS = "
        f"{final_status}"
    )

    log(
        f"{STAGE} "
        "NO REAL ORDER WAS SENT"
    )

    log(
        f"{STAGE} "
        "NO DEMO ORDER WAS SENT"
    )

    log(
        f"{STAGE} "
        "NO EXCHANGE MUTATION WAS SENT"
    )

    log(
        "================================"
        "================================"
    )

    return all_passed


def load_optional_real_snapshot():
    """
    OPTIONAL TEST INPUT

    To test actual cluster candidates without
    connecting this standalone diagnostic unit
    to the writer, set:

    R36F1510_ENTRY_PRICE

    R36F1510_LONG_CANDIDATES_JSON

    R36F1510_SHORT_CANDIDATES_JSON

    Example JSON:

    [
      {
        "average": 79200,
        "touches": 3,
        "members": [79190,79200,79210]
      }
    ]
    """

    entry_raw = os.getenv(
        "R36F1510_ENTRY_PRICE",
        "",
    ).strip()

    long_raw = os.getenv(
        "R36F1510_LONG_CANDIDATES_JSON",
        "",
    ).strip()

    short_raw = os.getenv(
        "R36F1510_SHORT_CANDIDATES_JSON",
        "",
    ).strip()

    if not entry_raw:
        log(
            f"{STAGE} "
            "REAL_SNAPSHOT_TEST = SKIPPED "
            "reason=NO_ENTRY_PRICE_PROVIDED"
        )
        return

    entry = safe_decimal(
        entry_raw
    )

    if entry is None:
        log(
            f"{STAGE} "
            "REAL_SNAPSHOT_TEST = FAIL "
            "reason=INVALID_ENTRY_PRICE"
        )
        return

    if long_raw:
        try:
            long_candidates = json.loads(
                long_raw
            )

            long_audit = audit_direction(
                entry,
                "LONG",
                long_candidates,
            )

            print_audit(
                long_audit
            )

        except Exception as exc:
            log(
                f"{STAGE} "
                "LONG_REAL_SNAPSHOT_ERROR = "
                f"{exc}"
            )

    if short_raw:
        try:
            short_candidates = json.loads(
                short_raw
            )

            short_audit = audit_direction(
                entry,
                "SHORT",
                short_candidates,
            )

            print_audit(
                short_audit
            )

        except Exception as exc:
            log(
                f"{STAGE} "
                "SHORT_REAL_SNAPSHOT_ERROR = "
                f"{exc}"
            )


def main():
    log(
        "================================"
        "================================"
    )

    log(
        f"{STAGE}: HISTORICAL CLUSTER "
        "REJECTION DIAGNOSTIC UNIT"
    )

    log(
        f"{STAGE}: "
        f"CLUSTER_TOLERANCE_PERCENT="
        f"{CLUSTER_TOLERANCE_PERCENT}"
    )

    log(
        f"{STAGE}: "
        f"MIN_CLUSTER_TOUCHES="
        f"{MIN_CLUSTER_TOUCHES}"
    )

    log(
        f"{STAGE}: "
        f"REQUIRED_CLUSTERS="
        f"{REQUIRED_CLUSTERS}"
    )

    log(
        f"{STAGE}: "
        "REAL_ORDER_EXECUTION=False"
    )

    log(
        f"{STAGE}: "
        "DEMO_ORDER_EXECUTION=False"
    )

    log(
        f"{STAGE}: "
        "WRITE_TRANSPORT=False"
    )

    tests_passed = (
        run_synthetic_tests()
    )

    if not tests_passed:
        raise RuntimeError(
            "R36F.15.10 "
            "SYNTHETIC_TEST_FAILURE"
        )

    load_optional_real_snapshot()

    log(
        f"{STAGE} FINAL STATUS = PASS"
    )


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} EXCEPTION = "
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        sys.exit(1)
