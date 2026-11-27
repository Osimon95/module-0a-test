
    # ========================================================
    # 6. EXACT BTC QUANTITY PASS-THROUGH
    # ========================================================

    sizing = plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 11 SIZING MISSING"
        )

    quantity = unit_11_v3_decimal(
        plan.get("quantity"),
        "PLAN QUANTITY"
        )

        )

                "
            
            )

        
                                method=method,
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
                      "            )

            
            )

            )

        
        ) * step


def unit_13_14_active_symbols():

    exchange = (
        FRESH_RECONSTRUCTION_CONFIG["exchange"]
    )

    
    )

    
                            "    # 
        )

                raise RuntimeError(
            "UNIT 13 NON-DEMO CONTRACT BLOCKED"
        )

    D = unit_13_v4_D
    _, demo_symbol = unit_13_14_active_symbols()

    step = D(
        precision.get("quantity_step"),
        "QTY STEP"
    )
    minimum = D(
        precision.get("minimum_quantity"),
        "MINIMUM QTY"
    )
    price_step = D(
        precision.get("price_step"),
        "PRICE STEP"
    )

    tp1_floor = D(
        strategy.get(
            "tp1_net_roi_floor_percent", 20
        ),
        "TP1 FLOOR"
    )
    tp2_floor = D(
        strategy.get(
            "tp2_net_roi_floor_percent", 40
        ),
        "TP2 FLOOR"
    )
    fee = D(
        strategy.get(
            "futures_taker_fee_percent", "0.08"
        ),
        "FEE",
        True
    )

    trail_ref = D(
        strategy.get(
            "tp3_trailing_reference_percent",
            "0.20"
        ),
        "TRAIL REF"
    )
    trail_min = D(
        strategy.get(
            "tp3_trailing_min_percent",
            "0.10"
        ),
        "TRAIL MIN"
    )
    trail_max = D(
        strategy.get(
            "tp3_trailing_max_percent",
            "0.40"
        ),
        "TRAIL MAX"
    )

    if (
        tp1_floor <= 0
        or tp2_floor <= tp1_floor
        or not (
            0 < trail_min
            <= trail_ref
            <= trail_max
        )
    ):
        raise RuntimeError(
            "UNIT 13 TP CONFIGURATION INVALID"
        )

    print(
        "PASS: UNIT 13 RECEIVED UNIT 12 RESULT",
        flush=True
    )
    print(
        "UNIT 13 RECEIVED UNIT 12 STATUS =",
        unit_12_result.get("status"),
        flush=True
    )
    print(
        "UNIT 13 POSITION MANAGEMENT INDEPENDENT "
        "OF BOT_MODE = TRUE",
        flush=True
    )
    print(
        "UNIT 13 TP ALLOCATION =",
        strategy.get("tp1_allocation_percent", 10),
        "/",
        strategy.get("tp2_allocation_percent", 20),
        "/",
        strategy.get("tp3_allocation_percent", 70),
        flush=True
    )
    print(
        "UNIT 13 TP1 NET ROI FLOOR =",
        tp1_floor,
        flush=True
    )
    print(
        "UNIT 13 TP2 NET ROI FLOOR =",
        tp2_floor,
        flush=True
    )

    # ========================================================
    # ALWAYS READ CURRENT WEEX DEMO POSITION.
    # DO NOT CHECK BOT_MODE HERE.
    # ========================================================

    positions = unit_13_v4_signed_request(
        "GET",
        UNIT13_V4_POSITION,
    )

    if not isinstance(positions, list):
        raise RuntimeError(
            "UNIT 13 POSITIONS NOT LIST"
        )

    active = []

    for p in positions:

        if not isinstance(p, dict):
            raise RuntimeError(
                "UNIT 13 POSITION RECORD MALFORMED"
            )

        if str(
            p.get("symbol", "")
                ).upper() != unit_13_14_active_symbols()[1]:
            continue

        size = D(
            p.get("size"),
            "POSITION SIZE",
            True
        )

        if size > 0:
            active.append(p)

    if not active:

        result = unit_13_v4_base_result(
            unit_12_result,
            "IDLE_NO_POSITION",
            "NO_ACTIVE_DEMO_POSITION",
        )

        print(
            "UNIT 13 STATUS = IDLE_NO_POSITION",
            flush=True
        )
        print(
            "UNIT 13 EXCHANGE WRITE = False",
            flush=True
        )

        return result

    if len(active) > 1:

        original_side = str(
            os.getenv(
                "ORIGINAL_POSITION_SIDE",
                ""
            )
        ).strip().upper()

        if original_side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT 13 ORIGINAL POSITION SIDE "
                "REQUIRED FOR ACTIVE HEDGE PAIR"
            )

        matching = [
            position
            for position in active
            if str(
                position.get("side", "")
            ).upper() == original_side
        ]

        if len(matching) != 1:
            raise RuntimeError(
                "UNIT 13 ORIGINAL POSITION "
                "NOT UNIQUELY IDENTIFIED"
            )

        p = matching[0]

    else:
        p = active[0]

    side = str(
        p.get("side", "")
    ).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 13 INVALID POSITION SIDE"
        )

    size = D(
        p.get("size"),
        "ACTIVE SIZE"
    )

    open_value = D(
        p.get("openValue"),
        "OPEN VALUE"
    )

    
    print(
        "UNIT 13 EXCHANGE POSITION LEVERAGE FIELDS =",
        {
            key: value
            for key, value in p.items()
            if "lever" in key.lower()
            or "margin" in key.lower()
        },
        flush=True
    )

    print(
        "UNIT 13 RENDER LONG LEVERAGE =",
        os.getenv("WEEX_LEVERAGE_LONG"),
        flush=True
    )

    print(
        "UNIT 13 RENDER SHORT LEVERAGE =",
        os.getenv("WEEX_LEVERAGE_SHORT"),
        flush=True
    )

    leverage = D(
        p.get("leverage"),
        "POSITION LEVERAGE"
    )

    entry = open_value / size

    # Cumulative position data is used for
    # quantity planning, never as proof of
    # TP1 or TP2 completion.

    if (
        "cumOpenSize" not in p
        or "cumCloseSize" not in p
    ):
        raise RuntimeError(
            "UNIT 13 CUMULATIVE HISTORY MISSING "
            "- NO TP ORDER"
        )

    cum_open = D(
        p["cumOpenSize"],
        "CUM OPEN"
    )
    cum_close = D(
        p["cumCloseSize"],
        "CUM CLOSE",
        True
    )

    if (
        cum_open < size
        or cum_close > cum_open
    ):
        raise RuntimeError(
            "UNIT 13 POSITION HISTORY INCONSISTENT"
        )

    # ========================================================
    # STEP-AWARE TP ALLOCATION
    # USE EXISTING UNIT 2 RENDER CONFIGURATION
    # ========================================================

    q1, q2, q3 = unit_13_v4_allocation(
        cum_open,
        step,
        strategy.get(
            "tp1_allocation_percent", 10
        ),
        strategy.get(
            "tp2_allocation_percent", 20
        ),
    )

    # ========================================================
    # TP1 / TP2 NET ROI TARGETS
    # ========================================================

    t1, t2 = unit_13_v4_targets(
        entry,
        leverage,
        side,
        price_step,
        tp1_floor,
        tp2_floor,
        fee,
    )

    mark = unit_13_v4_mark_price()

    # ========================================================
    # PERSISTENT ORIGINAL-POSITION CYCLE
    # NEVER PROMOTE TP FROM cumCloseSize
    # ========================================================

    cycle = str(
        p.get("id")
        or (
            str(
                p.get("createdTime")
                or p.get("openTime")
                or ""
            )
            + ":"
            + str(entry)
            + ":"
            + str(cum_open)
        )
    )

    state_path = unit_13_v4_state_path(
        demo_symbol,
        side,
        cycle
    )

    state = unit_13_v4_load(state_path)

    if state is None:

        state = {
            "cycle": cycle,
            "orders": {},
            "version": 1,
            "legacy_closures_unattributed": bool(
                cum_close > 0
            ),
        }

        # Historical closures may be TP fills,
        # hedges, or manual reductions.
        # Never assign them to TP1 or TP2
        # without their exchange order IDs.

        unit_13_v4_save(
            state_path,
            state
        )

    # ========================================================
    # EXCHANGE-CONFIRMED TP FILLS
    # ========================================================

    history = unit_13_v4_history(
        demo_symbol
    )

    totals, unresolved = unit_13_v4_verified(
        state,
        history,
        side,
        demo_symbol
    )

    tp1_filled = totals["TP1"]
    tp2_filled = totals["TP2"]

    done1 = (
        q1 == 0
        or tp1_filled >= q1
    )

    done2 = (
        q2 == 0
        or tp2_filled >= q2
    )

    # ========================================================
    # TARGET REACHED CHECK
    # ========================================================

    reached1 = (
        mark >= t1
        if side == "LONG"
        else mark <= t1
    )

    reached2 = (
        mark >= t2
        if side == "LONG"
        else mark <= t2
    )

    action = "NONE"
    close_qty = Decimal(0)

    # Never submit a duplicate TP order
    # while its previous submission remains
    # unresolved or partially filled.

    if (
        not unresolved
        and not state.get(
            "legacy_closures_unattributed"
        )
    ):

        if (
            not done1
            and reached1
            and "TP1" not in state["orders"]
        ):

            action = "TP1"
            close_qty = q1

        elif (
            done1
            and not done2
            and reached2
            and "TP2" not in state["orders"]
        ):

            action = "TP2"
            close_qty = q2

    if close_qty > 0:

        close_qty = (
            (
                min(close_qty, size) / step
            ).to_integral_value(
                rounding=ROUND_DOWN
            ) * step
        )

    # ========================================================
    # TP3 ARMING
    # ONLY VERIFIED TP COMPLETION COUNTS
    # ========================================================

    armed = bool(
        done1
        and done2
        and q3 > 0
        and size > 0
        and not state.get(
            "legacy_closures_unattributed"
        )
    )

    result = unit_13_v4_base_result(
        unit_12_result,
        (
            "TP3_ARMED"
            if armed
            else "MONITORING"
        ),
        (
            "DYNAMIC_TP3_RUNTIME_REQUIRED"
            if armed
            else "DYNAMIC_TP_TARGET_NOT_REACHED"
        ),
    )

    result.update({
        "active_position_exists": True,
        "position_exists": True,
        "tp_management_required": True,
        "position_side": side,
        "position_size": float(size),
        "average_entry_price": float(entry),
        "mark_price": float(mark),

        "tp_target_allocation": "{}/{}/{}".format(
            strategy.get(
                "tp1_allocation_percent", 10
            ),
            strategy.get(
                "tp2_allocation_percent", 20
            ),
            strategy.get(
                "tp3_allocation_percent", 70
            ),
        ),

        "tp1_verified_filled_quantity":
            str(tp1_filled),

        "tp2_verified_filled_quantity":
            str(tp2_filled),

        "tp_history_unresolved": unresolved,

        "tp_legacy_closures_unattributed": bool(
            state.get(
                "legacy_closures_unattributed"
            )
        ),

        "tp1_target": float(t1),
        "tp2_target": float(t2),

        "tp1_target_price": str(t1),
        "tp2_target_price": str(t2),

        "tp1_quantity": float(q1),
        "tp2_quantity": float(q2),
        "tp3_quantity": float(q3),

        "tp1_completed": done1,
        "tp2_completed": done2,
        "tp3_armed": armed,

        "tp3_trailing_percent":
            float(trail_ref),

        "tp3_trailing_reference_percent":
            float(trail_ref),

        "tp3_trailing_min_percent":
            float(trail_min),

        "tp3_trailing_max_percent":
            float(trail_max),

        "tp3_trailing_dynamic": True,

        "tp1_net_roi_floor_percent":
            float(tp1_floor),

        "tp2_net_roi_floor_percent":
            float(tp2_floor),

        "tp_action": action,
    })

    # ========================================================
    # PART 3 ENDS INSIDE fresh_reconstruction_unit_13()
    # PART 4 CONTINUES AT FOUR-SPACE INDENTATION
    # DO NOT CLOSE OR EXECUTE THIS FUNCTION YET
    # ========================================================


    # ========================================================
    # 8. POSITION PNL AND TP EXECUTION REPORT
    # ========================================================

    direction = (
        Decimal("1")
        if side == "LONG"
        else Decimal("-1")
    )

    unrealized_pnl = (
        (mark - entry) * size * direction
    )

    estimated_margin = (
        entry * size / leverage
    )

    estimated_roi = (
        unrealized_pnl / estimated_margin
        * Decimal("100")
        if estimated_margin > 0
        else Decimal("0")
    )

    result.update({
        "position_leverage": float(leverage),
        "position_entry_price": float(entry),
        "position_mark_price": float(mark),
        "position_unrealized_pnl":
            float(unrealized_pnl),
        "position_unrealized_roi_percent":
            float(estimated_roi),
        "tp1_target_reached": reached1,
        "tp2_target_reached": reached2,
        "tp_execution_attempted": False,
        "tp_execution_completed": False,
        "exchange_write": False,
    })

    print(
        "UNIT 13 POSITION SIDE =",
        side,
        flush=True
    )
    print(
        "UNIT 13 POSITION SIZE =",
        size,
        flush=True
    )
    print(
        "UNIT 13 ENTRY PRICE =",
        entry,
        flush=True
    )
    print(
        "UNIT 13 MARK PRICE =",
        mark,
        flush=True
    )
    print(
        "UNIT 13 LEVERAGE =",
        leverage,
        flush=True
    )
    print(
        "UNIT 13 ESTIMATED UNREALIZED PNL =",
        unrealized_pnl,
        flush=True
    )
    print(
        "UNIT 13 ESTIMATED ROI % =",
        estimated_roi,
        flush=True
    )
    print(
        "UNIT 13 TP1 TARGET =",
        t1,
        flush=True
    )
    print(
        "UNIT 13 TP2 TARGET =",
        t2,
        flush=True
    )
    print(
        "UNIT 13 TP1 VERIFIED FILLED =",
        tp1_filled,
        flush=True
    )
    print(
        "UNIT 13 TP2 VERIFIED FILLED =",
        tp2_filled,
        flush=True
    )
    print(
        "UNIT 13 TP HISTORY UNRESOLVED =",
        unresolved,
        flush=True
    )
    print(
        "UNIT 13 TP ACTION =",
        action,
        flush=True
    )

    # ========================================================
    # 9. EXCHANGE-CONFIRMED DEMO TP EXECUTION
    # ========================================================

    if action != "NONE":

        if close_qty < minimum:

            result["skip_reason"] = (
                "TP_QUANTITY_BELOW_EXCHANGE_MINIMUM"
            )

            print(
                "UNIT 13 TP BELOW MINIMUM =",
                close_qty,
                flush=True
            )

        elif close_qty > size:

            result["skip_reason"] = (
                "TP_QUANTITY_EXCEEDS_POSITION"
            )

        else:

            if action in state["orders"]:

                result["skip_reason"] = (
                    "TP_PREVIOUS_ORDER_UNRESOLVED"
                )

            else:

                client_id = (
                    "FR13-"
                    + action
                    + "-"
                    + hashlib.sha256(
                        (
                            cycle
                            + ":"
                            + action
                        ).encode("utf-8")
                    ).hexdigest()[:24]
                )

                close_side = (
                    "SELL"
                    if side == "LONG"
                    else "BUY"
                )

                payload = {
                    "symbol": demo_symbol,
                    "side": close_side,
                    "positionSide": side,
                    "type": "MARKET",
                    "quantity": format(
                        close_qty, "f"
                    ),
                    "newClientOrderId": client_id,
                }

                # Persist the intent before POST.
                # Never blindly retry an uncertain
                # exchange submission.

                state["orders"][action] = {
                    "client_id": client_id,
                    "order_id": None,
                    "quantity": str(close_qty),
                    "status": "INTENT_PERSISTED",
                    "created_at_ms": int(
                        time.time() * 1000
                    ),
                }

                unit_13_v4_save(
                    state_path,
                    state
                )

                print(
                    "UNIT 13 DEMO TP SUBMISSION =",
                    action,
                    flush=True
                )
                print(
                    "UNIT 13 TP CLOSE QUANTITY =",
                    close_qty,
                    flush=True
                )
                print(
                    "UNIT 13 TP CLIENT ORDER ID =",
                    client_id,
                    flush=True
                )

                result["tp_execution_attempted"] = True

                try:

                    reply = unit_13_v4_signed_request(
                        "POST",
                        UNIT13_V4_ORDER,
                        payload,
                    )

                except Exception:

                    print(
                        "UNIT 13 TP OUTCOME UNCERTAIN "
                        "- EXCHANGE RECONCILIATION REQUIRED",
                        flush=True
                    )

                    result["status"] = (
                        "TP_SUBMISSION_UNCERTAIN"
                    )
                    result["skip_reason"] = (
                        "TP_POST_OUTCOME_UNKNOWN"
                    )

                    # Keep the persistent intent.
                    # Do not submit another order
                    # with a new client ID.

                    return result

                if not isinstance(reply, dict):

                    result["status"] = (
                        "TP_SUBMISSION_UNCERTAIN"
                    )
                    result["skip_reason"] = (
                        "INVALID_EXCHANGE_RESPONSE"
                    )

                    return result

                order_id = reply.get("orderId")

                if (
                    reply.get("success") is not True
                    or not order_id
                ):

                    result["status"] = (
                        "TP_SUBMISSION_UNCONFIRMED"
                    )
                    result["skip_reason"] = (
                        "EXCHANGE_ACK_NOT_CONFIRMED"
                    )

                    print(
                        "UNIT 13 TP RESPONSE =",
                        str(reply)[:400],
                        flush=True
                    )

                    return result

                state["orders"][action][
                    "order_id"
                ] = str(order_id)

                state["orders"][action][
                    "status"
                ] = "ACKNOWLEDGED_NOT_FILL_VERIFIED"

                unit_13_v4_save(
                    state_path,
                    state
                )

                result.update({
                    "status": "TP_ORDER_ACKNOWLEDGED",
                    "skip_reason":
                        "AWAITING_EXCHANGE_CONFIRMED_FILL",
                    "tp_execution_completed": False,
                    "demo_order_executed": False,
                    "tp_order_id": str(order_id),
                    "tp_close_quantity":
                        str(close_qty),
                    "exchange_write": True,
                })

                print(
                    "UNIT 13 TP ORDER ACKNOWLEDGED =",
                    order_id,
                    flush=True
                )
                print(
                    "UNIT 13 TP FILL VERIFICATION = PENDING",
                    flush=True
                )

    # ========================================================
    # 10. FINAL UNIT 13 RESULT
    # ========================================================

    if (
        result["status"] == "MONITORING"
        and (
            unresolved
            or state.get(
                "legacy_closures_unattributed"
            )
        )
    ):

        result["skip_reason"] = (
            "TP_HISTORY_RECONCILIATION_REQUIRED"
        )

    print(
        "UNIT 13 STATUS =",
        result["status"],
        flush=True
    )
    print(
        "UNIT 13 TP1 COMPLETED =",
        done1,
        flush=True
    )
    print(
        "UNIT 13 TP2 COMPLETED =",
        done2,
        flush=True
    )
    print(
        "UNIT 13 TP3 ARMED =",
        result["tp3_armed"],
        flush=True
    )
    print(
        "UNIT 13 EXCHANGE WRITE =",
        result["exchange_write"],
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 13 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# END UNIT 13 V5 PART 4
# MAIN FUNCTION COMPLETE
# PART 5: HYBRID ADAPTER AND VALIDATION
# ============================================================



# ============================================================
# UNIT 13 V5 - PART 5 OF 5
# HYBRID ADAPTER, VALIDATION AND UNIT 14 HANDOVER
# ZERO INDENTATION
# ============================================================


# ============================================================
# 11. UNIT 13 HYBRID ADAPTER
# ============================================================

def fresh_unit_13_hybrid_adapter(
    config,
    unit_12_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 13 V5 HYBRID ADAPTER START",
        flush=True
    )

    try:

        result = fresh_reconstruction_unit_13(
            config,
            unit_12_result,
        )

    except Exception as exc:

        print(
            "UNIT 13 EXECUTION ERROR =",
            str(exc),
            flush=True
        )

        result = unit_13_v4_base_result(
            unit_12_result,
            "ERROR",
            str(exc),
        )

        result["execution_error"] = str(exc)

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 13 RESULT CONTRACT INVALID"
        )

    if result.get("unit") != 13:
        raise RuntimeError(
            "UNIT 13 RESULT UNIT MISMATCH"
        )

    # ========================================================
    # EXISTING POSITION MANAGEMENT MUST REMAIN
    # INDEPENDENT OF BOT_MODE.
    # ========================================================

    result["position_management_independent_of_bot_mode"] = True

    # ========================================================
    # EXCHANGE ACKNOWLEDGMENT IS NOT A TP FILL.
    # ========================================================

    if result.get("status") in (
        "TP_ORDER_ACKNOWLEDGED",
        "TP_SUBMISSION_UNCERTAIN",
        "TP_SUBMISSION_UNCONFIRMED",
    ):

        result["tp_execution_completed"] = False

    # ========================================================
    # TP3 MUST NEVER BE ARMED BY HEDGE CLOSURES.
    # ========================================================

    tp1_done = bool(
        result.get("tp1_completed", False)
    )

    tp2_done = bool(
        result.get("tp2_completed", False)
    )

    if not (tp1_done and tp2_done):

        result["tp3_armed"] = False

    if result.get(
        "tp_legacy_closures_unattributed",
        False
    ):

        result["tp3_armed"] = False

    if result.get(
        "tp_history_unresolved",
        False
    ):

        result["tp3_armed"] = False

    # ========================================================
    # DO NOT REPORT REAL-CASH SUBMISSION.
    # ========================================================

    result["real_submission_attempted"] = False

    print(
        "UNIT 13 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True
    )
    print(
        "UNIT 13 TP1 COMPLETED =",
        result.get("tp1_completed", False),
        flush=True
    )
    print(
        "UNIT 13 TP2 COMPLETED =",
        result.get("tp2_completed", False),
        flush=True
    )
    print(
        "UNIT 13 TP3 ARMED =",
        result.get("tp3_armed", False),
        flush=True
    )
    print(
        "UNIT 13 EXCHANGE WRITE =",
        result.get("exchange_write", False),
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 12. UNIT 13 LOCAL VALIDATION
# NO EXCHANGE ORDERS
# ============================================================

def unit_13_validation_v5():

    checks = {}

    # ========================================================
    # DECIMAL VALIDATION
    # ========================================================

    try:

        assert unit_13_v4_D(
            "0.5", "TEST"
        ) == Decimal("0.5")

        assert unit_13_v4_D(
            "0", "TEST", True
        ) == Decimal("0")

        checks["DECIMAL_VALIDATION"] = "PASS"

    except Exception as exc:

        checks["DECIMAL_VALIDATION"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # STEP-AWARE TP ALLOCATION
    # ========================================================

    try:

        a = unit_13_v4_allocation(
            Decimal("0.001"),
            Decimal("0.001"),
        )

        assert a == (
            Decimal("0"),
            Decimal("0"),
            Decimal("0.001"),
        )

        b = unit_13_v4_allocation(
            Decimal("0.002"),
            Decimal("0.001"),
        )

        assert b == (
            Decimal("0.001"),
            Decimal("0"),
            Decimal("0.001"),
        )

        c = unit_13_v4_allocation(
            Decimal("0.010"),
            Decimal("0.001"),
        )

        assert sum(c) == Decimal("0.010")
        assert all(x > 0 for x in c)

        checks["TP_ALLOCATION"] = "PASS"

    except Exception as exc:

        checks["TP_ALLOCATION"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # TP NET ROI TARGETS
    # ========================================================

    try:

        long_t1, long_t2 = unit_13_v4_targets(
            Decimal("100"),
            Decimal("10"),
            "LONG",
            Decimal("0.01"),
            Decimal("20"),
            Decimal("40"),
            Decimal("0.08"),
        )

        assert long_t2 > long_t1 > Decimal("100")

        short_t1, short_t2 = unit_13_v4_targets(
            Decimal("100"),
            Decimal("10"),
            "SHORT",
            Decimal("0.01"),
            Decimal("20"),
            Decimal("40"),
            Decimal("0.08"),
        )

        assert Decimal("100") > short_t1 > short_t2

        checks["TP_NET_ROI_TARGETS"] = "PASS"

    except Exception as exc:

        checks["TP_NET_ROI_TARGETS"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # TP FILL VERIFICATION
    # HEDGE CLOSURES MUST NOT COUNT.
    # ========================================================

    try:

        state = {
            "orders": {
                "TP1": {
                    "client_id": "FR13-TP1-TEST",
                    "order_id": "10001",
                    "quantity": "0.001",
                }
            }
        }

        history = [
            {
                "symbol": "BTCSUSDT",
                "positionSide": "LONG",
                "side": "SELL",
                "clientOrderId": "HEDGE-CLOSE-TEST",
                "orderId": "99999",
                "executedQty": "0.010",
                "status": "FILLED",
            },
            {
                "symbol": "BTCSUSDT",
                "positionSide": "LONG",
                "side": "SELL",
                "clientOrderId": "FR13-TP1-TEST",
                "orderId": "10001",
                "executedQty": "0.001",
                "status": "FILLED",
            },
        ]

        totals, pending = unit_13_v4_verified(
            state,
            history,
            "LONG",
            "BTCSUSDT",
        )

        assert totals["TP1"] == Decimal("0.001")
        assert totals["TP2"] == Decimal("0")
        assert pending is False

        checks["TP_FILL_IDENTITY"] = "PASS"

    except Exception as exc:

        checks["TP_FILL_IDENTITY"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # ACKNOWLEDGMENT MUST NOT COUNT AS COMPLETION.
    # ========================================================

    try:

        sample = unit_13_v4_base_result(
            {"status": "PAUSED"},
            "TP_ORDER_ACKNOWLEDGED",
            "AWAITING_FILL",
        )

        assert sample["tp_execution_completed"] is False
        assert sample["tp3_armed"] is False

        checks["ACK_NOT_FILL"] = "PASS"

    except Exception as exc:

        checks["ACK_NOT_FILL"] = (
            "FAIL: " + str(exc)
        )

    passed = all(
        value == "PASS"
        for value in checks.values()
    )

    print("=" * 80, flush=True)
    print(
        "UNIT 13 V5 VALIDATION RESULTS",
        flush=True
    )

    for name, status in checks.items():

        print(
            "UNIT 13",
            name,
            "=",
            status,
            flush=True
        )

    print(
        "UNIT 13 V5 VALIDATION =",
        "PASS" if passed else "FAIL",
        flush=True
    )

    print("=" * 80, flush=True)

    return {
        "unit": 13,
        "version": "V5",
        "passed": passed,
        "checks": checks,
    }


# ============================================================
# 13. UNIT 13 INITIALIZATION AND HANDOVER
# ============================================================

FRESH_UNIT_13_VALIDATION_READY = (
    unit_13_validation_v5()
)

if not FRESH_UNIT_13_VALIDATION_READY["passed"]:

    raise RuntimeError(
        "UNIT 13 V5 LOCAL VALIDATION FAILED"
    )


FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_unit_13_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)


# ============================================================
# END COMPLETE UNIT 13 V5 REPLACEMENT
# NEXT EXISTING SECTION: UNIT 14
# ============================================================


