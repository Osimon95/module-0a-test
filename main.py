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
