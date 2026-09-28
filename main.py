# ============================================================
# SL DISABLING — STANDALONE TESTABLE UNIT 1
# ZERO-WRITE PAYLOAD SHAPE TEST
#
# NO WEEX CONNECTION
# NO WEEX POST
# NO DEMO ORDER
# NO REAL ORDER
# ============================================================

def r36f_sl_disabled_payload_test():

    print(
        "R36F SL-DISABLE TEST UNIT 1 START"
    )

    test_payload = {
        "symbol": "BTCSUSDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": "0.0001",
        "newClientOrderId":
            "SL-DISABLE-TEST-001",
        "tpTriggerPrice": "99999.9",
        "TpWorkingType": "MARK_PRICE",
    }

    sl_trigger_present = (
        "slTriggerPrice"
        in test_payload
    )

    sl_working_type_present = (
        "SlWorkingType"
        in test_payload
    )

    required_entry_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
        "tpTriggerPrice",
        "TpWorkingType",
    }

    missing_fields = sorted(
        required_entry_fields
        -
        set(test_payload.keys())
    )

    passed = (
        not sl_trigger_present
        and
        not sl_working_type_present
        and
        not missing_fields
    )

    print(
        "R36F SL-DISABLE TEST "
        "SL_TRIGGER_PRESENT =",
        sl_trigger_present,
    )

    print(
        "R36F SL-DISABLE TEST "
        "SL_WORKING_TYPE_PRESENT =",
        sl_working_type_present,
    )

    print(
        "R36F SL-DISABLE TEST "
        "MISSING_ENTRY_FIELDS =",
        missing_fields,
    )

    print(
        "R36F SL-DISABLE TEST "
        "WEEX_POST = False"
    )

    print(
        "R36F SL-DISABLE TEST "
        "DEMO_ORDER = False"
    )

    print(
        "R36F SL-DISABLE TEST "
        "REAL_ORDER = False"
    )

    print(
        "R36F SL-DISABLE TEST RESULT =",
        "PASS"
        if passed
        else "FAIL",
    )

    print(
        "R36F SL-DISABLE TEST PAYLOAD =",
        test_payload,
    )

    return passed


if __name__ == "__main__":
    r36f_sl_disabled_payload_test()
# ============================================================
# R36F SL DISABLING TESTABLE UNIT 2
# STANDALONE PAYLOAD TRANSFORMATION BRIDGE
#
# PURPOSE:
# Prove independently that an existing entry payload
# containing SL can be converted into an SL-disabled
# payload without changing any other field.
#
# NO log() DEPENDENCY
# NO ASYNC DEPENDENCY
# NO WEEX POST
# NO DEMO ORDER
# NO REAL ORDER
# NO STATE CHANGE
# ============================================================


def r36f_sl_disable_transform(payload):

    if not isinstance(payload, dict):
        raise TypeError(
            "payload must be a dict"
        )

    transformed = dict(payload)

    transformed.pop(
        "slTriggerPrice",
        None,
    )

    transformed.pop(
        "SlWorkingType",
        None,
    )

    return transformed


def r36f_sl_disabled_payload_test_unit_2():

    print(
        "R36F SL-DISABLE TEST UNIT 2 START"
    )

    # --------------------------------------------------------
    # SELF-CONTAINED TEST PAYLOAD
    #
    # Deliberately contains both SL fields.
    # --------------------------------------------------------

    original_payload = {
        "symbol": "BTCSUSDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": "0.0001",
        "newClientOrderId":
            "SL-DISABLE-TEST-002",
        "tpTriggerPrice":
            "99999.9",
        "TpWorkingType":
            "MARK_PRICE",
        "slTriggerPrice":
            "1.0",
        "SlWorkingType":
            "MARK_PRICE",
    }

    # --------------------------------------------------------
    # TRANSFORM
    # --------------------------------------------------------

    transformed_payload = (
        r36f_sl_disable_transform(
            original_payload
        )
    )

    # --------------------------------------------------------
    # TEST A
    # SL fields removed
    # --------------------------------------------------------

    sl_trigger_present = (
        "slTriggerPrice"
        in transformed_payload
    )

    sl_working_type_present = (
        "SlWorkingType"
        in transformed_payload
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "SL_TRIGGER_PRESENT =",
        sl_trigger_present,
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "SL_WORKING_TYPE_PRESENT =",
        sl_working_type_present,
    )

    # --------------------------------------------------------
    # TEST B
    # Original payload was NOT mutated
    # --------------------------------------------------------

    original_preserved = (
        original_payload.get(
            "slTriggerPrice"
        )
        == "1.0"
        and
        original_payload.get(
            "SlWorkingType"
        )
        == "MARK_PRICE"
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "ORIGINAL_PRESERVED =",
        original_preserved,
    )

    # --------------------------------------------------------
    # TEST C
    # All non-SL fields preserved exactly
    # --------------------------------------------------------

    changed_non_sl_fields = []

    for key, value in (
        original_payload.items()
    ):

        if key in (
            "slTriggerPrice",
            "SlWorkingType",
        ):
            continue

        if (
            transformed_payload.get(key)
            != value
        ):
            changed_non_sl_fields.append(
                key
            )

    print(
        "R36F SL-DISABLE TEST2 "
        "CHANGED_NON_SL_FIELDS =",
        changed_non_sl_fields,
    )

    # --------------------------------------------------------
    # TEST D
    # Required entry fields still exist
    # --------------------------------------------------------

    required_entry_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    )

    missing_entry_fields = [
        key
        for key
        in required_entry_fields
        if key
        not in transformed_payload
    ]

    print(
        "R36F SL-DISABLE TEST2 "
        "MISSING_ENTRY_FIELDS =",
        missing_entry_fields,
    )

    # --------------------------------------------------------
    # TEST E
    # TP remains intact
    # --------------------------------------------------------

    tp_preserved = (
        transformed_payload.get(
            "tpTriggerPrice"
        )
        ==
        original_payload.get(
            "tpTriggerPrice"
        )
        and
        transformed_payload.get(
            "TpWorkingType"
        )
        ==
        original_payload.get(
            "TpWorkingType"
        )
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "TP_PRESERVED =",
        tp_preserved,
    )

    # --------------------------------------------------------
    # ZERO-WRITE PROOF
    # --------------------------------------------------------

    weex_post = False
    demo_order = False
    real_order = False

    print(
        "R36F SL-DISABLE TEST2 "
        "WEEX_POST =",
        weex_post,
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "DEMO_ORDER =",
        demo_order,
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "REAL_ORDER =",
        real_order,
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    passed = (
        sl_trigger_present is False
        and
        sl_working_type_present is False
        and
        original_preserved is True
        and
        changed_non_sl_fields == []
        and
        missing_entry_fields == []
        and
        tp_preserved is True
        and
        weex_post is False
        and
        demo_order is False
        and
        real_order is False
    )

    print(
        "R36F SL-DISABLE TEST2 RESULT =",
        "PASS"
        if passed
        else "FAIL",
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "ORIGINAL PAYLOAD =",
        original_payload,
    )

    print(
        "R36F SL-DISABLE TEST2 "
        "TRANSFORMED PAYLOAD =",
        transformed_payload,
    )

    return passed


# ============================================================
# EXECUTE STANDALONE TEST UNIT 2
# ============================================================

if __name__ == "__main__":
    r36f_sl_disabled_payload_test_unit_2()
# ============================================================
# R36F SL DISABLING TESTABLE UNIT 3
# PRE-SUBMISSION PAYLOAD BOUNDARY TEST
#
# PURPOSE:
# Simulate the payload immediately before the WEEX demo
# submission boundary.
#
# Uses the already-proven:
#     r36f_sl_disable_transform(payload)
#
# PROVES:
# 1. Candidate payload may contain SL.
# 2. SL transformer removes only SL.
# 3. Required demo-entry fields survive.
# 4. TP survives unchanged.
# 5. Final payload is ready to cross the submission boundary.
#
# IMPORTANT:
# THIS UNIT DOES NOT CROSS THAT BOUNDARY.
#
# NO WEEX POST
# NO DEMO ORDER
# NO REAL ORDER
# NO STATE CHANGE
# ============================================================


def r36f_sl_disabled_payload_test_unit_3():

    print(
        "R36F SL-DISABLE TEST UNIT 3 START"
    )

    # --------------------------------------------------------
    # STEP 1
    # Build candidate payload representing what the trading
    # engine could hand to the demo submission layer.
    # --------------------------------------------------------

    candidate_payload = {
        "symbol":
            "BTCSUSDT",

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0001",

        "newClientOrderId":
            "SL-DISABLE-TEST-003",

        "tpTriggerPrice":
            "99999.9",

        "TpWorkingType":
            "MARK_PRICE",

        "slTriggerPrice":
            "1.0",

        "SlWorkingType":
            "MARK_PRICE",
    }

    # --------------------------------------------------------
    # STEP 2
    # Confirm the candidate really contains SL BEFORE
    # transformation.
    # --------------------------------------------------------

    candidate_sl_present = (
        "slTriggerPrice"
        in candidate_payload
        and
        "SlWorkingType"
        in candidate_payload
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "CANDIDATE_SL_PRESENT =",
        candidate_sl_present,
    )

    # --------------------------------------------------------
    # STEP 3
    # Pass candidate through the transformer proven by
    # Test Unit 2.
    # --------------------------------------------------------

    final_payload = (
        r36f_sl_disable_transform(
            candidate_payload
        )
    )

    # --------------------------------------------------------
    # STEP 4
    # SL must now be absent.
    # --------------------------------------------------------

    final_sl_trigger_present = (
        "slTriggerPrice"
        in final_payload
    )

    final_sl_working_type_present = (
        "SlWorkingType"
        in final_payload
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "FINAL_SL_TRIGGER_PRESENT =",
        final_sl_trigger_present,
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "FINAL_SL_WORKING_TYPE_PRESENT =",
        final_sl_working_type_present,
    )

    # --------------------------------------------------------
    # STEP 5
    # Verify all required entry fields remain.
    # --------------------------------------------------------

    required_entry_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    )

    missing_entry_fields = [
        field
        for field
        in required_entry_fields
        if field
        not in final_payload
    ]

    print(
        "R36F SL-DISABLE TEST3 "
        "MISSING_ENTRY_FIELDS =",
        missing_entry_fields,
    )

    # --------------------------------------------------------
    # STEP 6
    # Verify values of required entry fields were not changed.
    # --------------------------------------------------------

    changed_entry_fields = []

    for field in required_entry_fields:

        if (
            candidate_payload.get(field)
            !=
            final_payload.get(field)
        ):
            changed_entry_fields.append(
                field
            )

    print(
        "R36F SL-DISABLE TEST3 "
        "CHANGED_ENTRY_FIELDS =",
        changed_entry_fields,
    )

    # --------------------------------------------------------
    # STEP 7
    # TP must survive exactly.
    # --------------------------------------------------------

    tp_trigger_preserved = (
        final_payload.get(
            "tpTriggerPrice"
        )
        ==
        candidate_payload.get(
            "tpTriggerPrice"
        )
    )

    tp_working_type_preserved = (
        final_payload.get(
            "TpWorkingType"
        )
        ==
        candidate_payload.get(
            "TpWorkingType"
        )
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "TP_TRIGGER_PRESERVED =",
        tp_trigger_preserved,
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "TP_WORKING_TYPE_PRESERVED =",
        tp_working_type_preserved,
    )

    # --------------------------------------------------------
    # STEP 8
    # Verify ONLY the expected SL fields disappeared.
    # --------------------------------------------------------

    removed_fields = sorted(
        set(candidate_payload.keys())
        -
        set(final_payload.keys())
    )

    expected_removed_fields = sorted(
        [
            "slTriggerPrice",
            "SlWorkingType",
        ]
    )

    only_sl_removed = (
        removed_fields
        ==
        expected_removed_fields
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "REMOVED_FIELDS =",
        removed_fields,
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "ONLY_SL_REMOVED =",
        only_sl_removed,
    )

    # --------------------------------------------------------
    # STEP 9
    # Verify no unexpected field was added.
    # --------------------------------------------------------

    added_fields = sorted(
        set(final_payload.keys())
        -
        set(candidate_payload.keys())
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "ADDED_FIELDS =",
        added_fields,
    )

    # --------------------------------------------------------
    # STEP 10
    # Submission-boundary readiness.
    #
    # This DOES NOT mean an order was submitted.
    # It only means the payload passed our local checks.
    # --------------------------------------------------------

    submission_boundary_ready = (
        candidate_sl_present is True
        and
        final_sl_trigger_present is False
        and
        final_sl_working_type_present is False
        and
        missing_entry_fields == []
        and
        changed_entry_fields == []
        and
        tp_trigger_preserved is True
        and
        tp_working_type_preserved is True
        and
        only_sl_removed is True
        and
        added_fields == []
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "SUBMISSION_BOUNDARY_READY =",
        submission_boundary_ready,
    )

    # --------------------------------------------------------
    # ABSOLUTE ZERO-WRITE FLAGS
    # --------------------------------------------------------

    weex_post = False
    demo_order = False
    real_order = False

    print(
        "R36F SL-DISABLE TEST3 "
        "WEEX_POST =",
        weex_post,
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "DEMO_ORDER =",
        demo_order,
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "REAL_ORDER =",
        real_order,
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    passed = (
        submission_boundary_ready is True
        and
        weex_post is False
        and
        demo_order is False
        and
        real_order is False
    )

    print(
        "R36F SL-DISABLE TEST3 RESULT =",
        "PASS"
        if passed
        else "FAIL",
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "CANDIDATE PAYLOAD =",
        candidate_payload,
    )

    print(
        "R36F SL-DISABLE TEST3 "
        "FINAL PAYLOAD =",
        final_payload,
    )

    return passed


# ============================================================
# EXECUTE TEST UNIT 3
# ============================================================

if __name__ == "__main__":
    r36f_sl_disabled_payload_test_unit_3()
# ============================================================
# R36F SL DISABLING TESTABLE UNIT 4
# DEMO SUBMISSION ADAPTER - ZERO WRITE
#
# PURPOSE:
# Build the bridge between the proven SL-removal transformer
# and the future WEEX demo submission function.
#
# FLOW:
#
# candidate payload
#       ↓
# demo submission adapter
#       ↓
# r36f_sl_disable_transform()
#       ↓
# validation
#       ↓
# final demo payload
#       ↓
# NETWORK BOUNDARY
#       X
# STOP HERE
#
# NO WEEX POST
# NO DEMO ORDER
# NO REAL ORDER
# NO STATE CHANGE
# ============================================================


def r36f_prepare_sl_disabled_demo_submission(
    payload
):

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not isinstance(payload, dict):
        return {
            "ready": False,
            "reason": "PAYLOAD_NOT_DICT",
            "payload": None,
            "weex_post": False,
        }

    # --------------------------------------------------------
    # PRESERVE CALLER PAYLOAD
    # --------------------------------------------------------

    original_payload = dict(payload)

    # --------------------------------------------------------
    # APPLY PROVEN UNIT-2 TRANSFORMER
    # --------------------------------------------------------

    try:

        final_payload = (
            r36f_sl_disable_transform(
                original_payload
            )
        )

    except Exception as exc:

        return {
            "ready": False,
            "reason":
                "SL_TRANSFORM_ERROR: "
                + str(exc),
            "payload": None,
            "weex_post": False,
        }

    # --------------------------------------------------------
    # REQUIRED ENTRY FIELDS
    # --------------------------------------------------------

    required_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    )

    missing_fields = [
        field
        for field
        in required_fields
        if field not in final_payload
    ]

    if missing_fields:

        return {
            "ready": False,
            "reason":
                "MISSING_ENTRY_FIELDS",
            "missing_fields":
                missing_fields,
            "payload":
                final_payload,
            "weex_post":
                False,
        }

    # --------------------------------------------------------
    # SL MUST NOT EXIST AFTER TRANSFORMATION
    # --------------------------------------------------------

    forbidden_sl_fields = [
        field
        for field
        in (
            "slTriggerPrice",
            "SlWorkingType",
        )
        if field in final_payload
    ]

    if forbidden_sl_fields:

        return {
            "ready": False,
            "reason":
                "SL_FIELDS_STILL_PRESENT",
            "sl_fields":
                forbidden_sl_fields,
            "payload":
                final_payload,
            "weex_post":
                False,
        }

    # --------------------------------------------------------
    # TP PRESERVATION
    #
    # If TP existed in the incoming payload, its value must
    # remain exactly unchanged.
    # --------------------------------------------------------

    tp_fields = (
        "tpTriggerPrice",
        "TpWorkingType",
    )

    changed_tp_fields = []

    for field in tp_fields:

        if field in original_payload:

            if (
                final_payload.get(field)
                !=
                original_payload.get(field)
            ):
                changed_tp_fields.append(
                    field
                )

    if changed_tp_fields:

        return {
            "ready": False,
            "reason":
                "TP_CHANGED",
            "changed_tp_fields":
                changed_tp_fields,
            "payload":
                final_payload,
            "weex_post":
                False,
        }

    # --------------------------------------------------------
    # VERIFY ALL NON-SL FIELDS ARE UNCHANGED
    # --------------------------------------------------------

    changed_non_sl_fields = []

    for field, value in (
        original_payload.items()
    ):

        if field in (
            "slTriggerPrice",
            "SlWorkingType",
        ):
            continue

        if (
            final_payload.get(field)
            != value
        ):
            changed_non_sl_fields.append(
                field
            )

    if changed_non_sl_fields:

        return {
            "ready": False,
            "reason":
                "NON_SL_FIELD_CHANGED",
            "changed_fields":
                changed_non_sl_fields,
            "payload":
                final_payload,
            "weex_post":
                False,
        }

    # --------------------------------------------------------
    # VERIFY NO NEW FIELDS WERE CREATED
    # --------------------------------------------------------

    added_fields = sorted(
        set(final_payload.keys())
        -
        set(original_payload.keys())
    )

    if added_fields:

        return {
            "ready": False,
            "reason":
                "UNEXPECTED_FIELDS_ADDED",
            "added_fields":
                added_fields,
            "payload":
                final_payload,
            "weex_post":
                False,
        }

    # --------------------------------------------------------
    # SUCCESS
    #
    # IMPORTANT:
    #
    # ready=True means:
    #
    #     LOCAL PAYLOAD VALIDATION PASSED
    #
    # It DOES NOT mean an order was sent.
    # --------------------------------------------------------

    return {
        "ready": True,
        "reason":
            "READY_AT_NETWORK_BOUNDARY",
        "payload":
            final_payload,

        # HARD ZERO-WRITE MARKER
        "weex_post":
            False,
    }


# ============================================================
# UNIT 4 TEST
# ============================================================


def r36f_sl_disabled_payload_test_unit_4():

    print(
        "R36F SL-DISABLE TEST UNIT 4 START"
    )

    # --------------------------------------------------------
    # Candidate demo entry.
    #
    # Contains SL deliberately.
    # --------------------------------------------------------

    candidate_payload = {
        "symbol":
            "BTCSUSDT",

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0001",

        "newClientOrderId":
            "SL-DISABLE-TEST-004",

        "tpTriggerPrice":
            "99999.9",

        "TpWorkingType":
            "MARK_PRICE",

        "slTriggerPrice":
            "1.0",

        "SlWorkingType":
            "MARK_PRICE",
    }

    # --------------------------------------------------------
    # Save candidate before adapter call.
    # --------------------------------------------------------

    candidate_before = dict(
        candidate_payload
    )

    # --------------------------------------------------------
    # PASS THROUGH DEMO SUBMISSION ADAPTER
    # --------------------------------------------------------

    result = (
        r36f_prepare_sl_disabled_demo_submission(
            candidate_payload
        )
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print(
        "R36F SL-DISABLE TEST4 "
        "ADAPTER_READY =",
        result.get(
            "ready"
        ),
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "ADAPTER_REASON =",
        result.get(
            "reason"
        ),
    )

    final_payload = result.get(
        "payload"
    )

    # --------------------------------------------------------
    # Verify caller payload was not mutated.
    # --------------------------------------------------------

    caller_payload_preserved = (
        candidate_payload
        ==
        candidate_before
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "CALLER_PAYLOAD_PRESERVED =",
        caller_payload_preserved,
    )

    # --------------------------------------------------------
    # Final payload must exist.
    # --------------------------------------------------------

    final_payload_exists = (
        isinstance(
            final_payload,
            dict,
        )
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "FINAL_PAYLOAD_EXISTS =",
        final_payload_exists,
    )

    # --------------------------------------------------------
    # Check SL state.
    # --------------------------------------------------------

    if final_payload_exists:

        final_sl_trigger_present = (
            "slTriggerPrice"
            in final_payload
        )

        final_sl_working_type_present = (
            "SlWorkingType"
            in final_payload
        )

    else:

        final_sl_trigger_present = True
        final_sl_working_type_present = True

    print(
        "R36F SL-DISABLE TEST4 "
        "FINAL_SL_TRIGGER_PRESENT =",
        final_sl_trigger_present,
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "FINAL_SL_WORKING_TYPE_PRESENT =",
        final_sl_working_type_present,
    )

    # --------------------------------------------------------
    # Check TP.
    # --------------------------------------------------------

    if final_payload_exists:

        tp_preserved = (
            final_payload.get(
                "tpTriggerPrice"
            )
            ==
            candidate_before.get(
                "tpTriggerPrice"
            )
            and
            final_payload.get(
                "TpWorkingType"
            )
            ==
            candidate_before.get(
                "TpWorkingType"
            )
        )

    else:

        tp_preserved = False

    print(
        "R36F SL-DISABLE TEST4 "
        "TP_PRESERVED =",
        tp_preserved,
    )

    # --------------------------------------------------------
    # Network boundary MUST remain closed.
    # --------------------------------------------------------

    weex_post = result.get(
        "weex_post",
        True,
    )

    demo_order = False
    real_order = False

    print(
        "R36F SL-DISABLE TEST4 "
        "WEEX_POST =",
        weex_post,
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "DEMO_ORDER =",
        demo_order,
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "REAL_ORDER =",
        real_order,
    )

    # --------------------------------------------------------
    # FINAL PASS
    # --------------------------------------------------------

    passed = (
        result.get(
            "ready"
        )
        is True
        and
        result.get(
            "reason"
        )
        ==
        "READY_AT_NETWORK_BOUNDARY"
        and
        caller_payload_preserved
        is True
        and
        final_payload_exists
        is True
        and
        final_sl_trigger_present
        is False
        and
        final_sl_working_type_present
        is False
        and
        tp_preserved
        is True
        and
        weex_post
        is False
        and
        demo_order
        is False
        and
        real_order
        is False
    )

    print(
        "R36F SL-DISABLE TEST4 RESULT =",
        "PASS"
        if passed
        else "FAIL",
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "INPUT PAYLOAD =",
        candidate_before,
    )

    print(
        "R36F SL-DISABLE TEST4 "
        "NETWORK-BOUNDARY PAYLOAD =",
        final_payload,
    )

    return passed


# ============================================================
# EXECUTE TEST UNIT 4
# ============================================================

if __name__ == "__main__":
    r36f_sl_disabled_payload_test_unit_4()
# ============================================================
# R36F SL-DISABLE TESTABLE UNIT 5
# SELF-CONTAINED SUBMISSION-BOUNDARY PAYLOAD TEST
#
# PURPOSE:
# Verify that the final payload immediately before the
# submission boundary contains the required entry/TP fields
# while SL fields have been removed.
#
# IMPORTANT:
# - SELF-CONTAINED
# - NO R36F14_DEMO_SYMBOL DEPENDENCY
# - NO WEEX POST
# - NO DEMO ORDER
# - NO REAL ORDER
# - NO ACCOUNT/POSITION STATE CHANGE
# ============================================================

def r36f_sl_disabled_payload_test_unit_5():

    print(
        "R36F SL-DISABLE TEST UNIT 5 START",
        flush=True,
    )

    # --------------------------------------------------------
    # Build a completely local candidate payload.
    #
    # This intentionally starts WITH the SL fields so Unit 5
    # can prove that only those fields disappear before the
    # simulated submission boundary.
    # --------------------------------------------------------

    candidate_payload = {
        "symbol": "BTCSUSDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": "0.0001",
        "newClientOrderId":
            "SL-DISABLE-TEST-005",
        "tpTriggerPrice": "99999.9",
        "TpWorkingType": "MARK_PRICE",
        "slTriggerPrice": "1.0",
        "SlWorkingType": "MARK_PRICE",
    }

    # --------------------------------------------------------
    # Preserve an untouched copy for comparison.
    # --------------------------------------------------------

    original_payload = dict(
        candidate_payload
    )

    # --------------------------------------------------------
    # Simulate the final payload preparation immediately
    # before the submission boundary.
    #
    # IMPORTANT:
    # No HTTP request occurs here.
    # --------------------------------------------------------

    final_payload = dict(
        candidate_payload
    )

    final_payload.pop(
        "slTriggerPrice",
        None,
    )

    final_payload.pop(
        "SlWorkingType",
        None,
    )

    # --------------------------------------------------------
    # Required entry fields.
    # --------------------------------------------------------

    required_entry_fields = [
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    ]

    missing_entry_fields = [
        field
        for field in required_entry_fields
        if field not in final_payload
    ]

    # --------------------------------------------------------
    # Confirm entry fields were not changed.
    # --------------------------------------------------------

    changed_entry_fields = [
        field
        for field in required_entry_fields
        if (
            field in original_payload
            and field in final_payload
            and original_payload[field]
            != final_payload[field]
        )
    ]

    # --------------------------------------------------------
    # SL checks.
    # --------------------------------------------------------

    candidate_sl_trigger_present = (
        "slTriggerPrice"
        in candidate_payload
    )

    candidate_sl_working_type_present = (
        "SlWorkingType"
        in candidate_payload
    )

    final_sl_trigger_present = (
        "slTriggerPrice"
        in final_payload
    )

    final_sl_working_type_present = (
        "SlWorkingType"
        in final_payload
    )

    # --------------------------------------------------------
    # TP preservation checks.
    # --------------------------------------------------------

    tp_trigger_preserved = (
        final_payload.get(
            "tpTriggerPrice"
        )
        ==
        original_payload.get(
            "tpTriggerPrice"
        )
    )

    tp_working_type_preserved = (
        final_payload.get(
            "TpWorkingType"
        )
        ==
        original_payload.get(
            "TpWorkingType"
        )
    )

    # --------------------------------------------------------
    # Determine exactly which fields were removed or added.
    # --------------------------------------------------------

    removed_fields = sorted(
        set(original_payload.keys())
        -
        set(final_payload.keys())
    )

    added_fields = sorted(
        set(final_payload.keys())
        -
        set(original_payload.keys())
    )

    only_sl_removed = (
        removed_fields
        ==
        [
            "SlWorkingType",
            "slTriggerPrice",
        ]
    )

    # --------------------------------------------------------
    # Verify all non-SL fields retain their original values.
    # --------------------------------------------------------

    changed_non_sl_fields = []

    for field in original_payload:

        if field in (
            "slTriggerPrice",
            "SlWorkingType",
        ):
            continue

        if (
            field not in final_payload
            or
            final_payload[field]
            != original_payload[field]
        ):
            changed_non_sl_fields.append(
                field
            )

    # --------------------------------------------------------
    # Simulated submission-boundary readiness.
    #
    # This means PAYLOAD READY only.
    # It does NOT mean an order was submitted.
    # --------------------------------------------------------

    submission_boundary_ready = (
        candidate_sl_trigger_present
        and
        candidate_sl_working_type_present
        and
        not final_sl_trigger_present
        and
        not final_sl_working_type_present
        and
        not missing_entry_fields
        and
        not changed_entry_fields
        and
        tp_trigger_preserved
        and
        tp_working_type_preserved
        and
        only_sl_removed
        and
        not added_fields
        and
        not changed_non_sl_fields
    )

    # --------------------------------------------------------
    # Explicit zero-write proof flags.
    # --------------------------------------------------------

    weex_post = False
    demo_order = False
    real_order = False

    result_pass = (
        submission_boundary_ready
        and
        weex_post is False
        and
        demo_order is False
        and
        real_order is False
    )

    # --------------------------------------------------------
    # Output.
    # --------------------------------------------------------

    print(
        "R36F SL-DISABLE TEST5 "
        "CANDIDATE_SL_TRIGGER_PRESENT =",
        candidate_sl_trigger_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "CANDIDATE_SL_WORKING_TYPE_PRESENT =",
        candidate_sl_working_type_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "FINAL_SL_TRIGGER_PRESENT =",
        final_sl_trigger_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "FINAL_SL_WORKING_TYPE_PRESENT =",
        final_sl_working_type_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "MISSING_ENTRY_FIELDS =",
        missing_entry_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "CHANGED_ENTRY_FIELDS =",
        changed_entry_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "CHANGED_NON_SL_FIELDS =",
        changed_non_sl_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "TP_TRIGGER_PRESERVED =",
        tp_trigger_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "TP_WORKING_TYPE_PRESERVED =",
        tp_working_type_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "REMOVED_FIELDS =",
        removed_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "ONLY_SL_REMOVED =",
        only_sl_removed,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "ADDED_FIELDS =",
        added_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "SUBMISSION_BOUNDARY_READY =",
        submission_boundary_ready,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "WEEX_POST =",
        weex_post,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "DEMO_ORDER =",
        demo_order,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "REAL_ORDER =",
        real_order,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 RESULT =",
        (
            "PASS"
            if result_pass
            else "FAIL"
        ),
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "CANDIDATE PAYLOAD =",
        candidate_payload,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST5 "
        "FINAL PAYLOAD =",
        final_payload,
        flush=True,
    )

    return result_pass
r36f_sl_disabled_payload_test_unit_5()

# ============================================================
# R36F SL-DISABLE TESTABLE UNIT 6
# ZERO-WRITE PRE-POST INTERCEPTION TEST
#
# PURPOSE:
# Verify the exact payload that reaches the final simulated
# WEEX POST boundary after SL removal.
#
# Unit 6 proves:
#
# candidate payload
#       |
#       v
# SL-removal boundary
#       |
#       v
# demo submission function
#       |
#       v
# intercepted POST
#
# The intercepted POST MUST receive:
# - all required entry fields
# - TP fields unchanged
# - NO slTriggerPrice
# - NO SlWorkingType
#
# SAFETY:
# - POST FUNCTION IS LOCAL INTERCEPTOR ONLY
# - NO HTTP LIBRARY IS CALLED
# - NO WEEX POST
# - NO DEMO ORDER
# - NO REAL ORDER
# - NO ACCOUNT/POSITION STATE CHANGE
# ============================================================


def r36f_sl_disabled_payload_test_unit_6():

    print(
        "R36F SL-DISABLE TEST UNIT 6 START",
        flush=True,
    )

    # --------------------------------------------------------
    # Completely local candidate payload.
    #
    # Start WITH SL so Unit 6 can prove that the payload
    # reaching the intercepted POST boundary has SL removed.
    # --------------------------------------------------------

    candidate_payload = {
        "symbol": "BTCSUSDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": "0.0001",
        "newClientOrderId":
            "SL-DISABLE-TEST-006",
        "tpTriggerPrice": "99999.9",
        "TpWorkingType": "MARK_PRICE",
        "slTriggerPrice": "1.0",
        "SlWorkingType": "MARK_PRICE",
    }

    original_payload = dict(
        candidate_payload
    )

    # --------------------------------------------------------
    # Interception storage.
    #
    # This records what WOULD reach the POST function.
    # It cannot perform a network operation.
    # --------------------------------------------------------

    interception = {
        "called": False,
        "payload": None,
        "network_request": False,
        "demo_order": False,
        "real_order": False,
    }

    # --------------------------------------------------------
    # LOCAL FAKE POST.
    #
    # IMPORTANT:
    # This is deliberately NOT requests.post,
    # aiohttp.post, httpx.post, or any WEEX function.
    #
    # Its only job is to capture the final payload.
    # --------------------------------------------------------

    def intercepted_weex_post(
        payload,
    ):

        interception[
            "called"
        ] = True

        interception[
            "payload"
        ] = dict(
            payload
        )

        # Explicit zero-write flags.

        interception[
            "network_request"
        ] = False

        interception[
            "demo_order"
        ] = False

        interception[
            "real_order"
        ] = False

        return {
            "intercepted": True,
            "submitted": False,
        }

    # --------------------------------------------------------
    # LOCAL DEMO SUBMISSION ADAPTER.
    #
    # This represents the final payload-processing stage.
    #
    # It copies the caller payload first.
    # Therefore the original caller payload is not modified.
    # --------------------------------------------------------

    def demo_submission_adapter(
        payload,
    ):

        final_payload = dict(
            payload
        )

        # ----------------------------------------------------
        # SL DISABLING AT FINAL SUBMISSION BOUNDARY.
        # ----------------------------------------------------

        final_payload.pop(
            "slTriggerPrice",
            None,
        )

        final_payload.pop(
            "SlWorkingType",
            None,
        )

        # ----------------------------------------------------
        # Instead of a real WEEX POST, send the final payload
        # into the local interceptor.
        # ----------------------------------------------------

        response = intercepted_weex_post(
            final_payload
        )

        return (
            final_payload,
            response,
        )

    # --------------------------------------------------------
    # Preserve caller payload before adapter execution.
    # --------------------------------------------------------

    caller_before = dict(
        candidate_payload
    )

    # --------------------------------------------------------
    # Execute the local submission path.
    #
    # ZERO NETWORK WRITE.
    # --------------------------------------------------------

    (
        final_payload,
        intercepted_response,
    ) = demo_submission_adapter(
        candidate_payload
    )

    # --------------------------------------------------------
    # Confirm caller payload was not mutated.
    # --------------------------------------------------------

    caller_payload_preserved = (
        candidate_payload
        ==
        caller_before
    )

    # --------------------------------------------------------
    # Retrieve the exact payload seen by intercepted POST.
    # --------------------------------------------------------

    intercepted_payload = (
        interception.get(
            "payload"
        )
    )

    post_boundary_called = (
        interception.get(
            "called"
        )
        is True
    )

    intercepted_payload_exists = (
        isinstance(
            intercepted_payload,
            dict,
        )
    )

    # --------------------------------------------------------
    # Required entry fields.
    # --------------------------------------------------------

    required_entry_fields = [
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    ]

    if intercepted_payload_exists:

        missing_entry_fields = [
            field
            for field
            in required_entry_fields
            if field
            not in intercepted_payload
        ]

    else:

        missing_entry_fields = list(
            required_entry_fields
        )

    # --------------------------------------------------------
    # Verify entry values reaching intercepted POST.
    # --------------------------------------------------------

    changed_entry_fields = []

    if intercepted_payload_exists:

        for field in required_entry_fields:

            if (
                field
                not in intercepted_payload
                or
                intercepted_payload.get(
                    field
                )
                !=
                original_payload.get(
                    field
                )
            ):
                changed_entry_fields.append(
                    field
                )

    else:

        changed_entry_fields = list(
            required_entry_fields
        )

    # --------------------------------------------------------
    # Candidate SL presence.
    # --------------------------------------------------------

    candidate_sl_trigger_present = (
        "slTriggerPrice"
        in original_payload
    )

    candidate_sl_working_type_present = (
        "SlWorkingType"
        in original_payload
    )

    # --------------------------------------------------------
    # Intercepted POST SL absence.
    # --------------------------------------------------------

    if intercepted_payload_exists:

        post_sl_trigger_present = (
            "slTriggerPrice"
            in intercepted_payload
        )

        post_sl_working_type_present = (
            "SlWorkingType"
            in intercepted_payload
        )

    else:

        post_sl_trigger_present = True
        post_sl_working_type_present = True

    # --------------------------------------------------------
    # TP preservation at intercepted POST boundary.
    # --------------------------------------------------------

    if intercepted_payload_exists:

        tp_trigger_preserved = (
            intercepted_payload.get(
                "tpTriggerPrice"
            )
            ==
            original_payload.get(
                "tpTriggerPrice"
            )
        )

        tp_working_type_preserved = (
            intercepted_payload.get(
                "TpWorkingType"
            )
            ==
            original_payload.get(
                "TpWorkingType"
            )
        )

    else:

        tp_trigger_preserved = False
        tp_working_type_preserved = False

    # --------------------------------------------------------
    # Determine removed and added fields at POST boundary.
    # --------------------------------------------------------

    if intercepted_payload_exists:

        removed_fields = sorted(
            set(
                original_payload.keys()
            )
            -
            set(
                intercepted_payload.keys()
            )
        )

        added_fields = sorted(
            set(
                intercepted_payload.keys()
            )
            -
            set(
                original_payload.keys()
            )
        )

    else:

        removed_fields = []
        added_fields = []

    only_sl_removed = (
        removed_fields
        ==
        [
            "SlWorkingType",
            "slTriggerPrice",
        ]
    )

    # --------------------------------------------------------
    # Verify every non-SL field reaching POST is unchanged.
    # --------------------------------------------------------

    changed_non_sl_fields = []

    if intercepted_payload_exists:

        for field in original_payload:

            if field in (
                "slTriggerPrice",
                "SlWorkingType",
            ):
                continue

            if (
                field
                not in intercepted_payload
                or
                intercepted_payload.get(
                    field
                )
                !=
                original_payload.get(
                    field
                )
            ):
                changed_non_sl_fields.append(
                    field
                )

    else:

        changed_non_sl_fields.append(
            "NO_INTERCEPTED_PAYLOAD"
        )

    # --------------------------------------------------------
    # Verify adapter-returned final payload is EXACTLY the
    # same payload seen by the intercepted POST function.
    # --------------------------------------------------------

    final_equals_intercepted = (
        intercepted_payload_exists
        and
        final_payload
        ==
        intercepted_payload
    )

    # --------------------------------------------------------
    # Verify fake response proves interception rather than
    # submission.
    # --------------------------------------------------------

    interceptor_response_valid = (
        isinstance(
            intercepted_response,
            dict,
        )
        and
        intercepted_response.get(
            "intercepted"
        )
        is True
        and
        intercepted_response.get(
            "submitted"
        )
        is False
    )

    # --------------------------------------------------------
    # Explicit zero-write proof.
    # --------------------------------------------------------

    network_request = (
        interception.get(
            "network_request"
        )
    )

    demo_order = (
        interception.get(
            "demo_order"
        )
    )

    real_order = (
        interception.get(
            "real_order"
        )
    )

    # --------------------------------------------------------
    # Complete Unit 6 PASS condition.
    # --------------------------------------------------------

    result_pass = (
        candidate_sl_trigger_present
        and
        candidate_sl_working_type_present
        and
        caller_payload_preserved
        and
        post_boundary_called
        and
        intercepted_payload_exists
        and
        not post_sl_trigger_present
        and
        not post_sl_working_type_present
        and
        not missing_entry_fields
        and
        not changed_entry_fields
        and
        tp_trigger_preserved
        and
        tp_working_type_preserved
        and
        only_sl_removed
        and
        not added_fields
        and
        not changed_non_sl_fields
        and
        final_equals_intercepted
        and
        interceptor_response_valid
        and
        network_request is False
        and
        demo_order is False
        and
        real_order is False
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print(
        "R36F SL-DISABLE TEST6 "
        "CANDIDATE_SL_TRIGGER_PRESENT =",
        candidate_sl_trigger_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "CANDIDATE_SL_WORKING_TYPE_PRESENT =",
        candidate_sl_working_type_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "CALLER_PAYLOAD_PRESERVED =",
        caller_payload_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "POST_BOUNDARY_CALLED =",
        post_boundary_called,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "INTERCEPTED_PAYLOAD_EXISTS =",
        intercepted_payload_exists,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "POST_SL_TRIGGER_PRESENT =",
        post_sl_trigger_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "POST_SL_WORKING_TYPE_PRESENT =",
        post_sl_working_type_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "MISSING_ENTRY_FIELDS =",
        missing_entry_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "CHANGED_ENTRY_FIELDS =",
        changed_entry_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "CHANGED_NON_SL_FIELDS =",
        changed_non_sl_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "TP_TRIGGER_PRESERVED =",
        tp_trigger_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "TP_WORKING_TYPE_PRESERVED =",
        tp_working_type_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "REMOVED_FIELDS =",
        removed_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "ONLY_SL_REMOVED =",
        only_sl_removed,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "ADDED_FIELDS =",
        added_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "FINAL_EQUALS_INTERCEPTED =",
        final_equals_intercepted,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "INTERCEPTOR_RESPONSE_VALID =",
        interceptor_response_valid,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "NETWORK_REQUEST =",
        network_request,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "DEMO_ORDER =",
        demo_order,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "REAL_ORDER =",
        real_order,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 RESULT =",
        (
            "PASS"
            if result_pass
            else "FAIL"
        ),
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "CANDIDATE PAYLOAD =",
        candidate_payload,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "FINAL PAYLOAD =",
        final_payload,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST6 "
        "INTERCEPTED POST PAYLOAD =",
        intercepted_payload,
        flush=True,
    )

    return result_pass


# ============================================================
# R36F SL-DISABLE TESTABLE UNIT 6 CALL
# ============================================================

r36f_sl_disabled_payload_test_unit_6()
# ============================================================
# R36F SL-DISABLE TESTABLE UNIT 7
# ACTUAL DEMO-SUBMISSION BOUNDARY TRANSFORMATION TEST
#
# PURPOSE:
# Verify the exact payload transformation required immediately
# before the existing:
#
#     await weex_demo_post(
#         R36F14_DEMO_ORDER_ENDPOINT,
#         payload,
#     )
#
# This test proves:
#
# 1. Entry fields remain unchanged.
# 2. TP fields remain unchanged.
# 3. newClientOrderId remains unchanged.
# 4. slTriggerPrice is removed.
# 5. SlWorkingType is removed.
# 6. No other field is removed.
# 7. No field is added.
# 8. No WEEX POST occurs.
# 9. No demo order occurs.
# 10. No real order occurs.
#
# IMPORTANT:
# - SELF-CONTAINED
# - ZERO WRITE
# - NO JOURNAL WRITE
# - NO NETWORK CALL
# - NO WEEX POST
# - NO DEMO ORDER
# - NO REAL ORDER
# ============================================================

def r36f_sl_disabled_payload_test_unit_7():

    print(
        "R36F SL-DISABLE TEST UNIT 7 START",
        flush=True,
    )

    # --------------------------------------------------------
    # This represents the payload immediately before the
    # existing WEEX demo POST boundary.
    #
    # It deliberately contains both TP and SL so Unit 7 can
    # prove that ONLY the SL fields disappear.
    # --------------------------------------------------------

    submission_payload = {
        "symbol": "BTCSUSDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": "0.0001",
        "newClientOrderId": "R36F-SL-UNIT7-001",

        "tpTriggerPrice": "99999.9",
        "TpWorkingType": "MARK_PRICE",

        "slTriggerPrice": "90000.0",
        "SlWorkingType": "MARK_PRICE",
    }

    original_payload = dict(
        submission_payload
    )

    # --------------------------------------------------------
    # Simulate the exact final transformation that will later
    # be inserted immediately before:
    #
    # await weex_demo_post(
    #     R36F14_DEMO_ORDER_ENDPOINT,
    #     payload,
    # )
    #
    # IMPORTANT:
    # Work on a copy so the caller payload is preserved.
    # --------------------------------------------------------

    final_payload = dict(
        submission_payload
    )

    final_payload.pop(
        "slTriggerPrice",
        None,
    )

    final_payload.pop(
        "SlWorkingType",
        None,
    )

    # --------------------------------------------------------
    # Simulated POST-boundary interceptor.
    #
    # NO NETWORK CALL.
    # --------------------------------------------------------

    intercepted_payload = dict(
        final_payload
    )

    post_boundary_called = True

    # --------------------------------------------------------
    # Required entry fields.
    # --------------------------------------------------------

    required_entry_fields = [
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    ]

    missing_entry_fields = [
        key
        for key in required_entry_fields
        if key not in intercepted_payload
    ]

    changed_entry_fields = [
        key
        for key in required_entry_fields
        if (
            key in original_payload
            and key in intercepted_payload
            and original_payload[key]
            != intercepted_payload[key]
        )
    ]

    # --------------------------------------------------------
    # TP preservation.
    # --------------------------------------------------------

    tp_trigger_preserved = (
        intercepted_payload.get(
            "tpTriggerPrice"
        )
        ==
        original_payload.get(
            "tpTriggerPrice"
        )
    )

    tp_working_type_preserved = (
        intercepted_payload.get(
            "TpWorkingType"
        )
        ==
        original_payload.get(
            "TpWorkingType"
        )
    )

    # --------------------------------------------------------
    # Client order ID preservation.
    # --------------------------------------------------------

    client_order_id_preserved = (
        intercepted_payload.get(
            "newClientOrderId"
        )
        ==
        original_payload.get(
            "newClientOrderId"
        )
    )

    # --------------------------------------------------------
    # SL removal.
    # --------------------------------------------------------

    final_sl_trigger_present = (
        "slTriggerPrice"
        in intercepted_payload
    )

    final_sl_working_type_present = (
        "SlWorkingType"
        in intercepted_payload
    )

    # --------------------------------------------------------
    # Determine exact removed fields.
    # --------------------------------------------------------

    removed_fields = sorted(
        set(original_payload.keys())
        -
        set(intercepted_payload.keys())
    )

    added_fields = sorted(
        set(intercepted_payload.keys())
        -
        set(original_payload.keys())
    )

    expected_removed_fields = sorted([
        "slTriggerPrice",
        "SlWorkingType",
    ])

    only_sl_removed = (
        removed_fields
        ==
        expected_removed_fields
    )

    # --------------------------------------------------------
    # Detect changes to any surviving non-SL field.
    # --------------------------------------------------------

    changed_non_sl_fields = sorted([
        key
        for key in original_payload
        if (
            key
            not in {
                "slTriggerPrice",
                "SlWorkingType",
            }
            and key in intercepted_payload
            and original_payload[key]
            != intercepted_payload[key]
        )
    ])

    caller_payload_preserved = (
        submission_payload
        ==
        original_payload
    )

    final_equals_intercepted = (
        final_payload
        ==
        intercepted_payload
    )

    # --------------------------------------------------------
    # ZERO-WRITE invariants.
    # --------------------------------------------------------

    weex_post = False
    demo_order = False
    real_order = False
    journal_write = False
    network_call = False

    # --------------------------------------------------------
    # Overall result.
    # --------------------------------------------------------

    overall_pass = all([
        caller_payload_preserved,
        post_boundary_called,
        final_equals_intercepted,

        not final_sl_trigger_present,
        not final_sl_working_type_present,

        missing_entry_fields == [],
        changed_entry_fields == [],

        tp_trigger_preserved,
        tp_working_type_preserved,
        client_order_id_preserved,

        only_sl_removed,
        added_fields == [],
        changed_non_sl_fields == [],

        weex_post is False,
        demo_order is False,
        real_order is False,
        journal_write is False,
        network_call is False,
    ])

    # --------------------------------------------------------
    # Visible evidence.
    # --------------------------------------------------------

    print(
        "R36F SL-DISABLE TEST7 CALLER_PAYLOAD_PRESERVED =",
        caller_payload_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 POST_BOUNDARY_CALLED =",
        post_boundary_called,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 FINAL_EQUALS_INTERCEPTED =",
        final_equals_intercepted,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 FINAL_SL_TRIGGER_PRESENT =",
        final_sl_trigger_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 FINAL_SL_WORKING_TYPE_PRESENT =",
        final_sl_working_type_present,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 MISSING_ENTRY_FIELDS =",
        missing_entry_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 CHANGED_ENTRY_FIELDS =",
        changed_entry_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 TP_TRIGGER_PRESERVED =",
        tp_trigger_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 TP_WORKING_TYPE_PRESERVED =",
        tp_working_type_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 CLIENT_ORDER_ID_PRESERVED =",
        client_order_id_preserved,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 REMOVED_FIELDS =",
        removed_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 ONLY_SL_REMOVED =",
        only_sl_removed,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 ADDED_FIELDS =",
        added_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 CHANGED_NON_SL_FIELDS =",
        changed_non_sl_fields,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 NETWORK_CALL =",
        network_call,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 JOURNAL_WRITE =",
        journal_write,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 WEEX_POST =",
        weex_post,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 DEMO_ORDER =",
        demo_order,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 REAL_ORDER =",
        real_order,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST7 INTERCEPTED_PAYLOAD =",
        intercepted_payload,
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST UNIT 7 RESULT =",
        "PASS"
        if overall_pass
        else "FAIL",
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST UNIT 7 END",
        flush=True,
    )

    return overall_pass


# ============================================================
# R36F SL-DISABLE TESTABLE UNIT 7 CALL
# ============================================================

r36f_sl_disabled_payload_test_unit_7()
