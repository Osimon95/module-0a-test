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
