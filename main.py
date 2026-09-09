
#!/usr/bin/env python3
"""
R36F.15.3 STANDALONE DEMO-JOURNAL RECONCILIATION TEST MODULE

Purpose:
    Verify the journal-reconciliation decision logic BEFORE merging it into
    the working R36F.15.2 bot.

Safety:
    - NO WEEX network calls.
    - NO exchange writes.
    - NO demo order submission.
    - NO real order submission.
    - NO modification of the R36F.15.2 journal file.
    - Pure deterministic reconciliation logic only.

Provider lookup abstraction:
    FOUND      = the exact client_order_id exists in WEEX demo order history.
    NOT_FOUND  = WEEX demo history definitively confirms it does not exist.
    UNKNOWN    = lookup failed, timed out, was unavailable, or was ambiguous.

Policy:
    1. COMPLETED+success journal remains terminal and blocks another first demo.
    2. REJECTED journal is terminal-rejected and permits a fresh demo attempt.
    3. PREPARED/SENT_AMBIGUOUS + FOUND => reconcile as COMPLETED/FOUND and block retry.
    4. PREPARED/SENT_AMBIGUOUS + NOT_FOUND => reconcile as REJECTED/NOT_FOUND and permit retry.
    5. PREPARED/SENT_AMBIGUOUS + UNKNOWN => remain unresolved and block retry.
    6. Never clear an unresolved journal merely from an exception string.
"""

from copy import deepcopy

STAGE = "R36F.15.3-JOURNAL-RECONCILIATION-TEST"

LOOKUP_FOUND = "FOUND"
LOOKUP_NOT_FOUND = "NOT_FOUND"
LOOKUP_UNKNOWN = "UNKNOWN"

UNRESOLVED_STATES = {"PREPARED", "SENT_AMBIGUOUS"}


def reconcile_demo_journal(journal, lookup_status, lookup_record=None):
    """Pure reconciliation function. It performs no I/O and no network calls."""
    original = deepcopy(journal) if isinstance(journal, dict) else {}
    lookup_record = deepcopy(lookup_record) if isinstance(lookup_record, dict) else {}

    if not original:
        return {
            "action": "NO_JOURNAL",
            "retry_allowed": True,
            "resolved": True,
            "journal": {},
            "reason": "NO_EXISTING_DEMO_JOURNAL",
        }

    state = str(original.get("state", "")).upper()

    if state == "COMPLETED" and original.get("success") is True:
        return {
            "action": "KEEP_COMPLETED",
            "retry_allowed": False,
            "resolved": True,
            "journal": original,
            "reason": "FIRST_DEMO_ORDER_ALREADY_COMPLETED",
        }

    if state == "REJECTED":
        return {
            "action": "KEEP_REJECTED",
            "retry_allowed": True,
            "resolved": True,
            "journal": original,
            "reason": "PREVIOUS_DEMO_ORDER_REJECTED",
        }

    if state not in UNRESOLVED_STATES:
        return {
            "action": "KEEP_BLOCKED_UNKNOWN_STATE",
            "retry_allowed": False,
            "resolved": False,
            "journal": original,
            "reason": "UNKNOWN_JOURNAL_STATE_REQUIRES_MANUAL_REVIEW",
        }

    client_order_id = str(original.get("client_order_id", "")).strip()
    if not client_order_id:
        return {
            "action": "KEEP_BLOCKED_MISSING_CLIENT_ID",
            "retry_allowed": False,
            "resolved": False,
            "journal": original,
            "reason": "UNRESOLVED_JOURNAL_MISSING_CLIENT_ORDER_ID",
        }

    status = str(lookup_status or LOOKUP_UNKNOWN).upper()

    if status == LOOKUP_FOUND:
        reconciled = {
            **original,
            "state": "COMPLETED",
            "success": True,
            "reconciliation_status": LOOKUP_FOUND,
            "reconciliation_reason": "EXACT_CLIENT_ORDER_ID_FOUND_IN_DEMO_HISTORY",
            "reconciled_order_id": str(
                lookup_record.get("orderId", lookup_record.get("order_id", ""))
            ),
            "reconciled_client_order_id": str(
                lookup_record.get(
                    "clientOrderId",
                    lookup_record.get("client_order_id", client_order_id),
                )
            ),
            "reconciliation_record": lookup_record,
        }
        return {
            "action": "MARK_COMPLETED_FOUND",
            "retry_allowed": False,
            "resolved": True,
            "journal": reconciled,
            "reason": "EXISTING_DEMO_ORDER_FOUND_DO_NOT_RESEND",
        }

    if status == LOOKUP_NOT_FOUND:
        reconciled = {
            **original,
            "state": "REJECTED",
            "success": False,
            "reconciliation_status": LOOKUP_NOT_FOUND,
            "reconciliation_reason": "EXACT_CLIENT_ORDER_ID_NOT_FOUND_IN_DEMO_HISTORY",
        }
        return {
            "action": "MARK_REJECTED_NOT_FOUND",
            "retry_allowed": True,
            "resolved": True,
            "journal": reconciled,
            "reason": "NO_EXISTING_DEMO_ORDER_SAFE_FOR_FRESH_CLIENT_ID",
        }

    return {
        "action": "KEEP_UNRESOLVED",
        "retry_allowed": False,
        "resolved": False,
        "journal": original,
        "reason": "DEMO_ORDER_LOOKUP_NOT_DEFINITIVE",
    }


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"{status}: {name}")
    if detail:
        print(f"      {detail}")
    if not condition:
        raise AssertionError(name)


def run_tests():
    print("-" * 100)
    print(f"{STAGE}: START")
    print("NO NETWORK | NO EXCHANGE WRITE | NO JOURNAL FILE WRITE")
    print("-" * 100)

    old_ambiguous = {
        "stage": "R36F.15.2",
        "state": "SENT_AMBIGUOUS",
        "client_order_id": "R36F8-SHORT-D14-0001",
        "endpoint": "/capi/v3/sim/order",
        "error": (
            'WEEX DEMO POST HTTP 500: {"code":-1054,"msg":"INVALID_ARGUMENT: '
            'The sell short order take profit param triggerPrice must be less than price"}'
        ),
        "success": False,
    }

    result = reconcile_demo_journal({}, LOOKUP_UNKNOWN)
    check("NO_JOURNAL_RESOLVED", result["resolved"] is True)
    check("NO_JOURNAL_RETRY_ALLOWED", result["retry_allowed"] is True)

    completed = {
        "state": "COMPLETED",
        "success": True,
        "client_order_id": "DONE-1",
    }
    result = reconcile_demo_journal(completed, LOOKUP_NOT_FOUND)
    check("COMPLETED_REMAINS_TERMINAL", result["action"] == "KEEP_COMPLETED")
    check("COMPLETED_BLOCKS_RETRY", result["retry_allowed"] is False)

    rejected = {
        "state": "REJECTED",
        "success": False,
        "client_order_id": "REJECTED-1",
    }
    result = reconcile_demo_journal(rejected, LOOKUP_UNKNOWN)
    check("REJECTED_REMAINS_TERMINAL", result["action"] == "KEEP_REJECTED")
    check("REJECTED_PERMITS_FRESH_RETRY", result["retry_allowed"] is True)

    found_record = {
        "orderId": "DEMO-ORDER-123",
        "clientOrderId": "R36F8-SHORT-D14-0001",
        "status": "FILLED",
    }
    result = reconcile_demo_journal(
        old_ambiguous,
        LOOKUP_FOUND,
        found_record,
    )
    check("AMBIGUOUS_FOUND_RESOLVED", result["resolved"] is True)
    check(
        "AMBIGUOUS_FOUND_MARKED_COMPLETED",
        result["journal"].get("state") == "COMPLETED",
    )
    check(
        "AMBIGUOUS_FOUND_BLOCKS_RESEND",
        result["retry_allowed"] is False,
    )
    check(
        "AMBIGUOUS_FOUND_PRESERVES_CLIENT_ID",
        result["journal"].get("client_order_id")
        == "R36F8-SHORT-D14-0001",
    )

    result = reconcile_demo_journal(
        old_ambiguous,
        LOOKUP_NOT_FOUND,
    )
    check("AMBIGUOUS_NOT_FOUND_RESOLVED", result["resolved"] is True)
    check(
        "AMBIGUOUS_NOT_FOUND_MARKED_REJECTED",
        result["journal"].get("state") == "REJECTED",
    )
    check(
        "AMBIGUOUS_NOT_FOUND_PERMITS_FRESH_RETRY",
        result["retry_allowed"] is True,
    )

    result = reconcile_demo_journal(
        old_ambiguous,
        LOOKUP_UNKNOWN,
    )
    check(
        "AMBIGUOUS_UNKNOWN_REMAINS_UNRESOLVED",
        result["resolved"] is False,
    )
    check(
        "AMBIGUOUS_UNKNOWN_BLOCKS_RETRY",
        result["retry_allowed"] is False,
    )
    check(
        "AMBIGUOUS_UNKNOWN_STATE_UNCHANGED",
        result["journal"].get("state") == "SENT_AMBIGUOUS",
    )

    prepared = {
        "state": "PREPARED",
        "client_order_id": "PREPARED-1",
        "success": False,
    }
    result = reconcile_demo_journal(
        prepared,
        LOOKUP_NOT_FOUND,
    )
    check(
        "PREPARED_NOT_FOUND_MARKED_REJECTED",
        result["journal"].get("state") == "REJECTED",
    )
    check(
        "PREPARED_NOT_FOUND_PERMITS_RETRY",
        result["retry_allowed"] is True,
    )

    missing_id = {
        "state": "SENT_AMBIGUOUS",
    }
    result = reconcile_demo_journal(
        missing_id,
        LOOKUP_NOT_FOUND,
    )
    check(
        "MISSING_CLIENT_ID_NOT_AUTO_CLEARED",
        result["resolved"] is False,
    )
    check(
        "MISSING_CLIENT_ID_BLOCKS_RETRY",
        result["retry_allowed"] is False,
    )

    unknown_state = {
        "state": "SOMETHING_NEW",
        "client_order_id": "X-1",
    }
    result = reconcile_demo_journal(
        unknown_state,
        LOOKUP_NOT_FOUND,
    )
    check(
        "UNKNOWN_STATE_NOT_AUTO_CLEARED",
        result["resolved"] is False,
    )
    check(
        "UNKNOWN_STATE_BLOCKS_RETRY",
        result["retry_allowed"] is False,
    )

    result = reconcile_demo_journal(
        old_ambiguous,
        LOOKUP_UNKNOWN,
    )
    check(
        "INVALID_ARGUMENT_TEXT_ALONE_DOES_NOT_CLEAR_JOURNAL",
        result["journal"].get("state") == "SENT_AMBIGUOUS"
        and result["retry_allowed"] is False,
    )

    print("-" * 100)
    print(f"{STAGE}: FINAL STATUS = PASS")
    print("MERGE_ELIGIBLE = True")
    print("EXCHANGE_WRITE_COUNT = 0")
    print("DEMO_ORDER_SUBMISSION_COUNT = 0")
    print("REAL_ORDER_SUBMISSION_COUNT = 0")
    print("JOURNAL_FILE_WRITE_COUNT = 0")
    print("-" * 100)


if __name__ == "__main__":
    run_tests()

