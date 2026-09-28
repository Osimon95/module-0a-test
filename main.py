# ============================================================
# SL DISABLE TEST A
# R36F15105 DEMO-PREVIEW SL REMOVAL
# STANDALONE ZERO-WRITE TEST
#
# PURPOSE:
# Prove the exact transformation we intend to apply to the
# output payload of r36f15105_build_demo_preview().
#
# IMPORTANT:
# - Candidate starts WITH the current SL fields.
# - Final payload is a COPY.
# - ONLY SL fields are removed from the copy.
# - Original candidate must remain unchanged.
# - TP / entry fields must remain unchanged.
#
# SAFETY:
# - NO WEEX POST
# - NO DEMO ORDER
# - NO REAL ORDER
# - NO ACCOUNT/POSITION MUTATION
# ============================================================


def r36f_sl_disable_test_a():

    print(
        "==========================================",
        flush=True,
    )

    print(
        "SL DISABLE TEST A START",
        flush=True,
    )

    # --------------------------------------------------------
    # This represents the CURRENT payload shape produced by
    # r36f15105_build_demo_preview().
    # --------------------------------------------------------

    candidate_payload = {
        "symbol": "BTCSUSDT",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": "0.0004",
        "newClientOrderId": "SL-DISABLE-TEST-A",
        "tpTriggerPrice": "85000",
        "slTriggerPrice": "83000",
        "TpWorkingType": "MARK_PRICE",
        "SlWorkingType": "MARK_PRICE",
    }

    # --------------------------------------------------------
    # Preserve an untouched copy so Test A can prove that
    # the transformation does NOT mutate the source payload.
    # --------------------------------------------------------

    original_payload = dict(
        candidate_payload
    )

    # --------------------------------------------------------
    # Proposed transformation.
    #
    # This is the exact behavior we want later at the output
    # of r36f15105_build_demo_preview().
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
    # SL CHECKS
    # --------------------------------------------------------

    candidate_sl_trigger_present = (
        "slTriggerPrice"
        in candidate_payload
    )

    candidate_sl_working_present = (
        "SlWorkingType"
        in candidate_payload
    )

    final_sl_trigger_present = (
        "slTriggerPrice"
        in final_payload
    )

    final_sl_working_present = (
        "SlWorkingType"
        in final_payload
    )

    sl_disabled = (
        not final_sl_trigger_present
        and
        not final_sl_working_present
    )

    # --------------------------------------------------------
    # ORIGINAL-PAYLOAD IMMUTABILITY CHECK
    # --------------------------------------------------------

    original_preserved = (
        candidate_payload
        ==
        original_payload
    )

    # --------------------------------------------------------
    # Determine exactly which fields disappeared.
    # --------------------------------------------------------

    removed_fields = sorted(
        set(
            candidate_payload.keys()
        )
        -
        set(
            final_payload.keys()
        )
    )

    expected_removed_fields = [
        "SlWorkingType",
        "slTriggerPrice",
    ]

    only_sl_removed = (
        removed_fields
        ==
        expected_removed_fields
    )

    # --------------------------------------------------------
    # Required non-SL fields.
    # --------------------------------------------------------

    required_non_sl_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
        "tpTriggerPrice",
        "TpWorkingType",
    }

    missing_non_sl_fields = sorted(
        required_non_sl_fields
        -
        set(
            final_payload.keys()
        )
    )

    all_required_fields_present = (
        len(
            missing_non_sl_fields
        )
        == 0
    )

    # --------------------------------------------------------
    # Verify every remaining field has exactly the same value.
    # --------------------------------------------------------

    changed_non_sl_fields = []

    for key in required_non_sl_fields:

        if (
            candidate_payload.get(
                key
            )
            !=
            final_payload.get(
                key
            )
        ):
            changed_non_sl_fields.append(
                key
            )

    changed_non_sl_fields = sorted(
        changed_non_sl_fields
    )

    non_sl_fields_preserved = (
        len(
            changed_non_sl_fields
        )
        == 0
    )

    # --------------------------------------------------------
    # Explicit important-field checks.
    # --------------------------------------------------------

    symbol_preserved = (
        final_payload.get(
            "symbol"
        )
        ==
        candidate_payload.get(
            "symbol"
        )
    )

    side_preserved = (
        final_payload.get(
            "side"
        )
        ==
        candidate_payload.get(
            "side"
        )
    )

    position_side_preserved = (
        final_payload.get(
            "positionSide"
        )
        ==
        candidate_payload.get(
            "positionSide"
        )
    )

    quantity_preserved = (
        final_payload.get(
            "quantity"
        )
        ==
        candidate_payload.get(
            "quantity"
        )
    )

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

    client_id_preserved = (
        final_payload.get(
            "newClientOrderId"
        )
        ==
        candidate_payload.get(
            "newClientOrderId"
        )
    )

    # --------------------------------------------------------
    # Make sure nothing was accidentally added.
    # --------------------------------------------------------

    added_fields = sorted(
        set(
            final_payload.keys()
        )
        -
        set(
            candidate_payload.keys()
        )
    )

    no_fields_added = (
        len(
            added_fields
        )
        == 0
    )

    # --------------------------------------------------------
    # ZERO-WRITE PROOF FLAGS
    # --------------------------------------------------------

    weex_post = False
    demo_order = False
    real_order = False
    account_mutation = False
    position_mutation = False

    zero_write = bool(
        weex_post is False
        and
        demo_order is False
        and
        real_order is False
        and
        account_mutation is False
        and
        position_mutation is False
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    overall_pass = all(
        [
            candidate_sl_trigger_present,
            candidate_sl_working_present,
            sl_disabled,
            original_preserved,
            only_sl_removed,
            all_required_fields_present,
            non_sl_fields_preserved,
            symbol_preserved,
            side_preserved,
            position_side_preserved,
            quantity_preserved,
            tp_trigger_preserved,
            tp_working_type_preserved,
            client_id_preserved,
            no_fields_added,
            zero_write,
        ]
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print(
        "TEST A CANDIDATE SL TRIGGER PRESENT =",
        candidate_sl_trigger_present,
        flush=True,
    )

    print(
        "TEST A CANDIDATE SL WORKING TYPE PRESENT =",
        candidate_sl_working_present,
        flush=True,
    )

    print(
        "TEST A FINAL SL TRIGGER PRESENT =",
        final_sl_trigger_present,
        flush=True,
    )

    print(
        "TEST A FINAL SL WORKING TYPE PRESENT =",
        final_sl_working_present,
        flush=True,
    )

    print(
        "TEST A SL DISABLED =",
        sl_disabled,
        flush=True,
    )

    print(
        "TEST A ORIGINAL PRESERVED =",
        original_preserved,
        flush=True,
    )

    print(
        "TEST A REMOVED FIELDS =",
        removed_fields,
        flush=True,
    )

    print(
        "TEST A ONLY SL REMOVED =",
        only_sl_removed,
        flush=True,
    )

    print(
        "TEST A MISSING NON-SL FIELDS =",
        missing_non_sl_fields,
        flush=True,
    )

    print(
        "TEST A CHANGED NON-SL FIELDS =",
        changed_non_sl_fields,
        flush=True,
    )

    print(
        "TEST A SYMBOL PRESERVED =",
        symbol_preserved,
        flush=True,
    )

    print(
        "TEST A SIDE PRESERVED =",
        side_preserved,
        flush=True,
    )

    print(
        "TEST A POSITION SIDE PRESERVED =",
        position_side_preserved,
        flush=True,
    )

    print(
        "TEST A QUANTITY PRESERVED =",
        quantity_preserved,
        flush=True,
    )

    print(
        "TEST A TP TRIGGER PRESERVED =",
        tp_trigger_preserved,
        flush=True,
    )

    print(
        "TEST A TP WORKING TYPE PRESERVED =",
        tp_working_type_preserved,
        flush=True,
    )

    print(
        "TEST A CLIENT ID PRESERVED =",
        client_id_preserved,
        flush=True,
    )

    print(
        "TEST A ADDED FIELDS =",
        added_fields,
        flush=True,
    )

    print(
        "TEST A WEEX POST =",
        weex_post,
        flush=True,
    )

    print(
        "TEST A DEMO ORDER =",
        demo_order,
        flush=True,
    )

    print(
        "TEST A REAL ORDER =",
        real_order,
        flush=True,
    )

    print(
        "TEST A ZERO WRITE =",
        zero_write,
        flush=True,
    )

    print(
        "SL DISABLE TEST A RESULT =",
        (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
        flush=True,
    )

    print(
        "==========================================",
        flush=True,
    )

    return overall_pass


# ============================================================
# SL DISABLE TEST A CALL
# ============================================================

r36f_sl_disable_test_a()
