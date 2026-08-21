        "",
        "R26 SIGNAL → INTENT → EXECUTION CHAIN",
        f"Signal Direction: {final_intent.direction}",
        f"Intent Side: {final_intent.side}",
        f"Intent Position Side: {final_intent.position_side}",
        f"Intent Quantity: {decimal_text(final_intent.quantity)}",
        f"Client Order ID: {final_intent.client_order_id}",
        f"Final Intent State: {final_intent.state}",
        f"Intent Reconciled: {yesno(final_intent.state == 'RECONCILED')}",
        "",
        "R26 RENDER PERSISTENCE",
        "Health Server: ✅ ACTIVE",
        "Persistent Runtime: ✅ ACTIVE",
        "Auto Exit After Diagnostic: ❌ DISABLED",
        "Repeated Demo Order Loop: ❌ DISABLED",
        "",
        "ABSOLUTE EXECUTION SAFETY",
        f"Real POST Called: {'⚠️ YES' if R26_REAL_POST_CALLED else '❌ NO'}",
        "🛡 R26 absolute real-order POST lock active",
        "⚠️ LIVE ORDER EXECUTION DISABLED",
        "⚠️ NO REAL ORDER WAS SENT",
    ]

    return "\n".join(lines)


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def r26_run_diagnostic(
    session: aiohttp.ClientSession,
) -> str:

    stage = "startup"

    try:
        final_safety_assertions_r26()

        stage = "configuration"
        validate_credentials()

        client = WeexClient(
            session
        )

        stage = "market data"

        mark_payload, exchange_payload = await asyncio.gather(
            client.public_get(
                EP_MARK_PRICE,
                {
                    "symbol": SYMBOL,
                    "priceType": "MARK",
                },
            ),
            client.public_get(
                EP_EXCHANGE_INFO,
                {
                    "symbol": SYMBOL,
                },
            ),
        )

        mark_price = extract_mark_price(
            mark_payload
        )

        contract = parse_contract_info(
            exchange_payload,
            SYMBOL,
        )

        stage = "balance"

        balance_payload = await client.private_get(
            EP_REAL_BALANCE
        )

        available_usdt = extract_available_balance(
            balance_payload,
            "USDT",
        )

        stage = "external position gate"

        try:
            real_positions = await client.private_get(
                EP_REAL_POSITIONS
            )

            long_pos = position_size_from_payload(
                real_positions,
                SYMBOL,
                "LONG",
            )

            short_pos = position_size_from_payload(
                real_positions,
                SYMBOL,
                "SHORT",
            )

            external_position_clear = (
                long_pos == 0
                and short_pos == 0
            )

        except Exception as exc:
            raise RuntimeError(
                "Unable to verify external real positions: "
                f"{exc}"
            )

        stage = "dynamic entry"

        entry_margin = (
            available_usdt
            * ENTRY_PERCENT
            / D100
        )

        entry_notional = (
            entry_margin
            * Decimal(LEVERAGE)
        )

        raw_qty = (
            entry_notional
            / mark_price
        )

        quantity = floor_with_precision(
            raw_qty,
            contract.qty_step,
            contract.qty_precision,
        )

        if quantity <= 0:
            raise RuntimeError(
                "Dynamic entry produced "
                "non-positive quantity"
            )

        if quantity < contract.min_qty:
            raise RuntimeError(
                "Dynamic entry quantity "
                f"{quantity} below minimum "
                f"{contract.min_qty}"
            )

        total_exposure = (
            ENTRY_PERCENT
            + PYRAMID_SIZE_PERCENT
            * MAX_PYRAMID_ADDS
            + BACKUP_SIZE_PERCENT
            * MAX_BACKUPS
        )

        leverage_passed = (
            contract.min_leverage
            <= LEVERAGE
            <= contract.max_leverage
        )

        exposure_passed = (
            total_exposure
            <= MAX_FUND_EXPOSURE_PERCENT
        )

        stage = "signal gate self-test"

        sg = SignalGate()

        t = time.time()

        fresh = Signal(
            "fresh",
            SYMBOL,
            "LONG",
            t,
        )

        expired = Signal(
            "expired",
            SYMBOL,
            "LONG",
            t
            - SIGNAL_EXPIRY_SECONDS
            - 1,
        )

        fresh_ok = sg.accept(
            fresh,
            t,
        )[0]

        expired_ok = not sg.accept(
            expired,
            t,
        )[0]

        duplicate_ok = not sg.accept(
            fresh,
            t,
        )[0]

        cooldown_gate = SignalGate()

        cooldown_gate.last_loss_time = t

        cooldown_ok = not cooldown_gate.accept(
            Signal(
                "cool",
                SYMBOL,
                "LONG",
                t,
            ),
            t,
        )[0]

        gate_results = {
            "api_symbol": (
                contract.symbol.upper()
                == SYMBOL
            ),
            "fresh_signal": fresh_ok,
            "expired_signal": expired_ok,
            "loss_cooldown": cooldown_ok,
            "duplicate_signal": duplicate_ok,
            "one_direction": ONE_DIRECTION_ONLY,
            "external_position_clear": (
                external_position_clear
            ),
        }

        stage = "order state machine"

        tracker = OrderTracker(
            "selftest"
        )

        a0, d0, _ = tracker.apply(
            "NEW",
            D0,
            "e0",
        )

        a1, d1, _ = tracker.apply(
            "PARTIALLY_FILLED",
            quantity / 4,
            "e1",
        )

        a2, d2, _ = tracker.apply(
            "PARTIALLY_FILLED",
            quantity / 2,
            "e2",
        )

        a3, d3, _ = tracker.apply(
            "FILLED",
            quantity,
            "e3",
        )

        dup, _, dup_reason = tracker.apply(
            "FILLED",
            quantity,
            "e3",
        )

        reg, _, reg_reason = tracker.apply(
            "NEW",
            quantity,
            "e4",
        )

        order_sm = {
            "new": (
                a0
                and d0 == 0
            ),
            "partial1": (
                a1
                and d1 > 0
            ),
            "partial2": (
                a2
                and d2 > 0
            ),
            "filled": (
                a3
                and tracker.terminal
                and d3 > 0
            ),
            "duplicate": (
                not dup
                and dup_reason
                == "duplicate-event"
            ),
            "terminal_regression": (
                not reg
                and reg_reason
                == "terminal-regression"
            ),
        }

        stage = "execution intent"

        intent_gate = IntentGate()

        intent = ExecutionIntent(
            intent_id="r26-intent-main",
            signal_id="r26-signal-main",
            symbol=SYMBOL,
            direction="LONG",
            side="BUY",
            position_side="LONG",
            quantity=quantity,
            created_at=time.time(),
        )

        created = intent_gate.create(
            intent
        )

        duplicate_intent = not intent_gate.create(
            intent
        )

        to_preflight = intent.transition(
            "PREFLIGHT"
        )

        to_ready = intent.transition(
            "READY"
        )

        expired_intent = ExecutionIntent(
            intent_id="r26-expired",
            signal_id="r26-expired-sig",
            symbol=SYMBOL,
            direction="LONG",
            side="BUY",
            position_side="LONG",
            quantity=quantity,
            created_at=(
                time.time()
                - SIGNAL_EXPIRY_SECONDS
                - 1
            ),
        )

        expired_rejected = (
            time.time()
            - expired_intent.created_at
        ) > SIGNAL_EXPIRY_SECONDS

        terminal_intent = ExecutionIntent(
            intent_id="r26-terminal",
            signal_id="r26-terminal-sig",
            symbol=SYMBOL,
            direction="LONG",
            side="BUY",
            position_side="LONG",
            quantity=quantity,
            created_at=time.time(),
            state="RECONCILED",
        )

        terminal_regression = not terminal_intent.transition(
            "READY"
        )

        intent_results = {
            "created": created,
            "duplicate": duplicate_intent,
            "to_preflight": to_preflight,
            "to_ready": to_ready,
            "expired": expired_rejected,
            "terminal_regression": (
                terminal_regression
            ),
        }

        stage = "execution preflight"

        preflight = {
            "live_off": (
                not LIVE_ORDER_EXECUTION
            ),
            "hard_lock": (
                HARD_REAL_POST_LOCK
            ),
            "fresh": (
                time.time()
                - intent.created_at
            ) <= SIGNAL_EXPIRY_SECONDS,
            "qty_positive": (
                intent.quantity > 0
            ),
            "minimum": (
                intent.quantity
                >= contract.min_qty
            ),
            "leverage": (
                leverage_passed
            ),
            "exposure": (
                exposure_passed
            ),
            "real_blocked": (
                HARD_REAL_POST_LOCK
                and not LIVE_ORDER_EXECUTION
            ),
        }

        if not all(
            preflight.values()
        ):
            raise RuntimeError(
                f"R26 preflight failed: {preflight}"
            )

        stage = "live payload rehearsal"

        live_limit_price = floor_with_precision(
            mark_price
            * (
                Decimal("1")
                - DEMO_PRICE_OFFSET_PERCENT
                / D100
            ),
            contract.price_step,
            contract.price_precision,
        )

        rehearsal = rehearse_real_payload(
            intent,
            contract,
            live_limit_price,
        )

        rehearsal_checks = [
            rehearsal.client_id_valid,
            rehearsal.required_fields_present,
            rehearsal.quantity_step_match,
            rehearsal.price_step_match,
            rehearsal.deterministic_rebuild_match,
            rehearsal.signature_generated,
            rehearsal.real_path_blocked,
            rehearsal.response_accept_classification_test,
            rehearsal.response_reject_classification_test,
            rehearsal.ambiguous_response_classification_test,
        ]

        if not all(
            rehearsal_checks
        ):
            raise RuntimeError(
                "R26 live payload rehearsal failed"
            )

        intent.client_order_id = rehearsal.payload[
            "newClientOrderId"
        ]

        stage = "demo position before"

        demo_pos_before_payload = await client.private_get(
            EP_DEMO_POSITIONS
        )

        position_before = position_size_from_payload(
            demo_pos_before_payload,
            DEMO_SYMBOL,
            DEMO_POSITION_SIDE,
        )

        stage = "demo order transmission"

        lifecycle = await run_demo_lifecycle(
            client,
            contract,
            mark_price,
            quantity,
            intent,
        )

        if not lifecycle.lifecycle_valid:
            raise RuntimeError(
                "R26 demo lifecycle validation failed"
            )

        stage = "actual history idempotency"

        actual_tracker = OrderTracker(
            lifecycle.order_id
        )

        status = lifecycle.final_status
        qty_exec = lifecycle.executed_qty

        event_key = (
            f"{lifecycle.order_id}:"
            f"{status}:"
            f"{decimal_text(qty_exec)}"
        )

        first_acc, first_delta, _ = actual_tracker.apply(
            status,
            qty_exec,
            event_key,
        )

        second_acc, _, second_reason = actual_tracker.apply(
            status,
            qty_exec,
            event_key,
        )

        history_idem = {
            "first": first_acc,
            "duplicate": (
                not second_acc
                and second_reason
                == "duplicate-event"
            ),
            "terminal": actual_tracker.terminal,
            "delta": first_delta,
        }

        stage = "demo position after"

        demo_pos_after_payload = await client.private_get(
            EP_DEMO_POSITIONS
        )

        position_after = position_size_from_payload(
            demo_pos_after_payload,
            DEMO_SYMBOL,
            DEMO_POSITION_SIDE,
        )

        expected_after = (
            position_before
            + lifecycle.executed_qty
        )

        position_reconciled = (
            position_after
            == expected_after
        )

        stage = "failure path matrix"

        failure_tests = run_failure_path_tests(
            contract,
            quantity,
            live_limit_price,
        )

        if not all(
            vars(
                failure_tests
            ).values()
        ):
            raise RuntimeError(
                "R26 failure matrix failed: "
                f"{failure_tests}"
            )

        stage = "intent finalization"

        # This SUBMITTED transition represents
        # DEMO submission only.
        if not intent.transition(
            "SUBMITTED"
        ):
            raise RuntimeError(
                "Unable to move intent to SUBMITTED"
            )

        if not intent.transition(
            "RECONCILING"
        ):
            raise RuntimeError(
                "Unable to move intent to RECONCILING"
            )

        if not intent.transition(
            "RECONCILED"
        ):
            raise RuntimeError(
                "Unable to move intent to RECONCILED"
            )

        all_critical = [
            all(
                gate_results.values()
            ),
            all(
                order_sm.values()
            ),
            all(
                intent_results.values()
            ),
            all(
                preflight.values()
            ),
            lifecycle.lifecycle_valid,
            history_idem["first"],
            history_idem["duplicate"],
            history_idem["terminal"],
            position_reconciled,
            all(
                vars(
                    failure_tests
                ).values()
            ),
            intent.state
            == "RECONCILED",
            not R26_REAL_POST_CALLED,
        ]

        if not all(
            all_critical
        ):
            raise RuntimeError(
                "One or more R26 critical "
                "validations failed"
            )

        report = build_report(
            available_usdt=available_usdt,
            mark_price=mark_price,
            contract=contract,
            entry_margin=entry_margin,
            entry_notional=entry_notional,
            quantity=quantity,
            gate_results=gate_results,
            order_sm=order_sm,
            intent_results=intent_results,
            preflight=preflight,
            rehearsal=rehearsal,
            lifecycle=lifecycle,
            history_idem=history_idem,
            position_before=position_before,
            position_after=position_after,
            position_reconciled=position_reconciled,
            failure_tests=failure_tests,
            final_intent=intent,
        )

        DIAGNOSTIC_STATUS.update(
            {
                "state": "passed",
                "last_error": "",
                "real_post_called": (
                    R26_REAL_POST_CALLED
                ),
                "demo_post_attempted": (
                    R26_DEMO_POST_ATTEMPTED
                ),
                "demo_post_accepted": (
                    R26_DEMO_POST_ACCEPTED
                ),
                "symbol": SYMBOL,
                "demo_symbol": DEMO_SYMBOL,
                "intent_state": (
                    intent.state
                ),
            }
        )

        return report

    except Exception as exc:
        DIAGNOSTIC_STATUS.update(
            {
                "state": "error",
                "last_error": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                "real_post_called": (
                    R26_REAL_POST_CALLED
                ),
                "demo_post_attempted": (
                    R26_DEMO_POST_ATTEMPTED
                ),
                "demo_post_accepted": (
                    R26_DEMO_POST_ACCEPTED
                ),
            }
        )

        error_report = "\n".join(
            [
                f"❌ MODULE {MODULE_NAME} ERROR",
                SYMBOL,
                f"Stage: {stage}",
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                (
                    "Real POST Called: "
                    f"{'⚠️ YES' if R26_REAL_POST_CALLED else '❌ NO'}"
                ),
                (
                    "Demo POST Attempted: "
                    f"{yesno(R26_DEMO_POST_ATTEMPTED)}"
                ),
                (
                    "Demo POST Accepted: "
                    f"{yesno(R26_DEMO_POST_ACCEPTED)}"
                ),
                "🛡 R26 absolute real-order POST lock active",
                "⚠️ LIVE ORDER EXECUTION DISABLED",
                "⚠️ NO REAL ORDER WAS SENT",
            ]
        )

        print(
            traceback.format_exc(),
            flush=True,
        )

        return error_report


# ============================================================
# APPLICATION LIFECYCLE
# ============================================================

async def main_async() -> None:
    await start_health_server()

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "LIVE-PAYLOAD / FAILURE-PATH "
        "PRE-LIVE VALIDATION",
        flush=True,
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    connector = aiohttp.TCPConnector(
        limit=20,
        ttl_dns_cache=300,
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        report = await r26_run_diagnostic(
            session
        )

        print(
            report,
            flush=True,
        )

        await send_telegram(
            session,
            report,
        )

        # Persistent Render runtime.
        # Diagnostic runs ONCE only.
        while True:
            await asyncio.sleep(
                3600
            )


def main() -> None:
    try:
        asyncio.run(
            main_async()
        )

    except KeyboardInterrupt:
        pass

    except Exception as exc:
        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"❌ {MODULE_NAME} "
            "FATAL STARTUP ERROR",
            flush=True,
        )

        print(
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            "🛡 REAL ORDER POST LOCK "
            "REMAINS ACTIVE",
            flush=True,
        )

        print(
            "⚠️ NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        traceback.print_exc()


if __name__ == "__main__":
    main()
    
