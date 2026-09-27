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
# SL DISABLING TESTABLE UNIT 2
# PAYLOAD TRANSFORMATION / PRESERVATION TEST
#
# PURPOSE:
# Prove that SL fields can be removed from an entry payload
# while every non-SL field remains exactly unchanged.
#
# ZERO WEEX POST
# ZERO DEMO ORDER
# ZERO REAL ORDER
# ZERO STATE CHANGE
# ============================================================

def r36f_sl_disabled_payload_test_unit_2():

    log(
        "R36F SL-DISABLE TEST UNIT 2 START"
    )

    # --------------------------------------------------------
    # Simulate the shape of the existing demo-entry payload
    # BEFORE SL disabling.
    # --------------------------------------------------------

    original_payload = {
        "symbol":
            R36F14_DEMO_SYMBOL,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0001",

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
    # Make a copy.
    #
    # We deliberately do NOT modify original_payload.
    # --------------------------------------------------------

    transformed_payload = dict(
        original_payload
    )

    # --------------------------------------------------------
    # Disable SL by removing ONLY the two SL fields.
    # --------------------------------------------------------

    transformed_payload.pop(
        "slTriggerPrice",
        None,
    )

    transformed_payload.pop(
        "SlWorkingType",
        None,
    )

    # --------------------------------------------------------
    # TEST 1:
    # SL trigger must be absent.
    # --------------------------------------------------------

    sl_trigger_present = (
        "slTriggerPrice"
        in transformed_payload
    )

    log(
        "R36F SL-DISABLE TEST2 "
        "SL_TRIGGER_PRESENT = "
        + str(sl_trigger_present)
    )

    # --------------------------------------------------------
    # TEST 2:
    # SL working type must be absent.
    # --------------------------------------------------------

    sl_working_type_present = (
        "SlWorkingType"
        in transformed_payload
    )

    log(
        "R36F SL-DISABLE TEST2 "
        "SL_WORKING_TYPE_PRESENT = "
        + str(sl_working_type_present)
    )

    # --------------------------------------------------------
    # TEST 3:
    # Original payload must still contain SL.
    #
    # This proves we transformed a copy instead of mutating
    # the source payload.
    # --------------------------------------------------------

    original_preserved = (
        "slTriggerPrice"
        in original_payload
        and
        "SlWorkingType"
        in original_payload
    )

    log(
        "R36F SL-DISABLE TEST2 "
        "ORIGINAL_PRESERVED = "
        + str(original_preserved)
    )

    # --------------------------------------------------------
    # TEST 4:
    # Every NON-SL field must be identical.
    # --------------------------------------------------------

    non_sl_fields = [
        key
        for key
        in original_payload
        if key
        not in (
            "slTriggerPrice",
            "SlWorkingType",
        )
    ]

    changed_non_sl_fields = []

    for key in non_sl_fields:

        if (
            transformed_payload.get(key)
            !=
            original_payload.get(key)
        ):
            changed_non_sl_fields.append(
                key
            )

    log(
        "R36F SL-DISABLE TEST2 "
        "CHANGED_NON_SL_FIELDS = "
        + str(
            changed_non_sl_fields
        )
    )

    # --------------------------------------------------------
    # TEST 5:
    # Required entry fields must remain.
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
        for key
        in required_entry_fields
        if key
        not in transformed_payload
    ]

    log(
        "R36F SL-DISABLE TEST2 "
        "MISSING_ENTRY_FIELDS = "
        + str(
            missing_entry_fields
        )
    )

    # --------------------------------------------------------
    # TEST 6:
    # TP fields must remain unchanged.
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

    log(
        "R36F SL-DISABLE TEST2 "
        "TP_PRESERVED = "
        + str(tp_preserved)
    )

    # --------------------------------------------------------
    # SAFETY PROOF
    # --------------------------------------------------------

    weex_post = False
    demo_order = False
    real_order = False

    log(
        "R36F SL-DISABLE TEST2 "
        "WEEX_POST = "
        + str(weex_post)
    )

    log(
        "R36F SL-DISABLE TEST2 "
        "DEMO_ORDER = "
        + str(demo_order)
    )

    log(
        "R36F SL-DISABLE TEST2 "
        "REAL_ORDER = "
        + str(real_order)
    )

    # --------------------------------------------------------
    # FINAL PASS / FAIL
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

    log(
        "R36F SL-DISABLE TEST2 "
        "RESULT = "
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

    log(
        "R36F SL-DISABLE TEST2 "
        "ORIGINAL PAYLOAD = "
        + str(
            original_payload
        )
    )

    log(
        "R36F SL-DISABLE TEST2 "
        "TRANSFORMED PAYLOAD = "
        + str(
            transformed_payload
        )
    )

    return passed


# ============================================================
# RUN TEST UNIT 2
# ============================================================

r36f_sl_disabled_payload_test_unit_2()
