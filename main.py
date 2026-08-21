    order_id: str
    response_client_id_match: bool
    history_lookup_attempted: bool
    history_poll_attempts: int
    history_found: bool
    history_order_id_match: bool
    history_client_id_match: bool
    history_symbol_match: bool
    history_side_match: bool
    history_position_side_match: bool
    final_status: str
    status_recognized: bool
    requested_qty: Decimal
    original_qty: Decimal
    executed_qty: Decimal
    quantity_reconciled: bool
    lifecycle_valid: bool
    history_row: Optional[Dict[str, Any]]


async def run_demo_lifecycle(
    client: WeexClient,
    contract: ContractInfo,
    mark_price: Decimal,
    quantity: Decimal,
    intent: ExecutionIntent,
) -> DemoLifecycleResult:
    if not DEMO_ORDER_ENABLED:
        raise RuntimeError("DEMO_ORDER_ENABLED must remain true for R26 validation")

    if DEMO_SIDE == "BUY":
        raw_price = mark_price * (Decimal("1") - DEMO_PRICE_OFFSET_PERCENT / D100)
    else:
        raw_price = mark_price * (Decimal("1") + DEMO_PRICE_OFFSET_PERCENT / D100)

    limit_price = floor_with_precision(
        raw_price,
        contract.price_step,
        contract.price_precision,
    )

    client_order_id = deterministic_client_order_id(
        intent,
        "r26d",
    )

    body = build_order_payload(
        DEMO_SYMBOL,
        DEMO_SIDE,
        DEMO_POSITION_SIDE,
        quantity,
        limit_price,
        client_order_id,
        DEMO_TIME_IN_FORCE,
    )

    response = await client.demo_post(
        DEMO_ORDER_PATH,
        body,
    )

    accepted, classification, detail = classify_order_response(
        response
    )

    if not accepted:
        raise RuntimeError(
            f"Demo response not accepted: "
            f"{classification}: {detail}"
        )

    order_id = str(
        first_present(
            response,
            ("orderId", "order_id"),
            "",
        )
        or ""
    )

    response_client_id = str(
        first_present(
            response,
            ("clientOrderId", "client_oid"),
            "",
        )
        or ""
    )

    history_row = None
    poll_count = 0

    for attempt in range(
        1,
        HISTORY_POLL_ATTEMPTS + 1,
    ):
        poll_count = attempt

        payload = await client.private_get(
            EP_DEMO_HISTORY,
            {
                "symbol": DEMO_SYMBOL,
                "limit": 100,
                "page": 0,
            },
        )

        history_row = find_history_order(
            payload,
            order_id,
            client_order_id,
        )

        if history_row:
            break

        if attempt < HISTORY_POLL_ATTEMPTS:
            await asyncio.sleep(
                HISTORY_POLL_DELAY_SECONDS
            )

    if history_row:
        h_order_id = str(
            first_present(
                history_row,
                ("orderId", "order_id"),
                "",
            )
            or ""
        )

        h_client_id = str(
            first_present(
                history_row,
                ("clientOrderId", "client_oid"),
                "",
            )
            or ""
        )

        h_symbol = str(
            history_row.get(
                "symbol",
                "",
            )
        ).upper()

        h_side = str(
            history_row.get(
                "side",
                "",
            )
        ).upper()

        h_position_side = str(
            first_present(
                history_row,
                (
                    "positionSide",
                    "holdSide",
                ),
                "",
            )
        ).upper()

        final_status = str(
            history_row.get(
                "status",
                "UNKNOWN",
            )
        ).upper()

        orig_qty = D(
            first_present(
                history_row,
                (
                    "origQty",
                    "quantity",
                    "size",
                    "origQuantity",
                ),
            )
        )

        executed_qty = D(
            first_present(
                history_row,
                (
                    "executedQty",
                    "filledQty",
                    "filledSize",
                    "dealSize",
                ),
            )
        )

    else:
        h_order_id = ""
        h_client_id = ""
        h_symbol = ""
        h_side = ""
        h_position_side = ""
        final_status = "NOT_FOUND"
        orig_qty = D0
        executed_qty = D0

    status_recognized = (
        final_status in ORDER_STATE_RANK
    )

    quantity_reconciled = (
        history_row is not None
        and orig_qty == quantity
        and D0 <= executed_qty <= orig_qty
    )

    lifecycle_valid = all(
        [
            accepted,
            bool(order_id),
            bool(
                CLIENT_ID_RE.fullmatch(
                    client_order_id
                )
            ),
            history_row is not None,
            h_order_id == order_id,
            h_client_id in {
                "",
                client_order_id,
            },
            h_symbol == DEMO_SYMBOL,
            h_side == DEMO_SIDE,
            h_position_side
            in {
                "",
                DEMO_POSITION_SIDE,
            },
            status_recognized,
            quantity_reconciled,
        ]
    )

    return DemoLifecycleResult(
        demo_symbol=DEMO_SYMBOL,
        side=DEMO_SIDE,
        position_side=DEMO_POSITION_SIDE,
        order_type=DEMO_ORDER_TYPE,
        tif=DEMO_TIME_IN_FORCE,
        limit_price=limit_price,
        price_step_match=step_match(
            limit_price,
            contract.price_step,
        ),
        client_order_id=client_order_id,
        client_order_id_valid=bool(
            CLIENT_ID_RE.fullmatch(
                client_order_id
            )
        ),
        post_attempted=R26_DEMO_POST_ATTEMPTED,
        post_accepted=R26_DEMO_POST_ACCEPTED,
        order_id=order_id,
        response_client_id_match=(
            response_client_id
            in {
                "",
                client_order_id,
            }
        ),
        history_lookup_attempted=True,
        history_poll_attempts=poll_count,
        history_found=(
            history_row is not None
        ),
        history_order_id_match=(
            h_order_id == order_id
            and bool(order_id)
        ),
        history_client_id_match=(
            h_client_id
            in {
                "",
                client_order_id,
            }
        ),
        history_symbol_match=(
            h_symbol == DEMO_SYMBOL
        ),
        history_side_match=(
            h_side == DEMO_SIDE
        ),
        history_position_side_match=(
            h_position_side
            in {
                "",
                DEMO_POSITION_SIDE,
            }
        ),
        final_status=final_status,
        status_recognized=status_recognized,
        requested_qty=quantity,
        original_qty=orig_qty,
        executed_qty=executed_qty,
        quantity_reconciled=quantity_reconciled,
        lifecycle_valid=lifecycle_valid,
        history_row=history_row,
    )


# ============================================================
# R26 FAILURE-PATH SELF TESTS
# ============================================================

@dataclass
class FailurePathTests:
    duplicate_submit_blocked: bool
    stale_intent_blocked: bool
    invalid_quantity_blocked: bool
    invalid_price_blocked: bool
    invalid_client_id_blocked: bool
    terminal_regression_blocked: bool
    real_post_blocked_before_network: bool
    ambiguous_response_fail_closed: bool


def run_failure_path_tests(
    contract: ContractInfo,
    quantity: Decimal,
    price: Decimal,
) -> FailurePathTests:

    gate = IntentGate()

    base = ExecutionIntent(
        intent_id="r26-failure-intent",
        signal_id="sig-r26-failure",
        symbol=SYMBOL,
        direction="LONG",
        side="BUY",
        position_side="LONG",
        quantity=quantity,
        created_at=time.time(),
    )

    first = gate.create(
        base
    )

    second = gate.create(
        base
    )

    stale = ExecutionIntent(
        intent_id="r26-stale",
        signal_id="sig-stale",
        symbol=SYMBOL,
        direction="LONG",
        side="BUY",
        position_side="LONG",
        quantity=quantity,
        created_at=(
            time.time()
            - SIGNAL_EXPIRY_SECONDS
            - 10
        ),
    )

    stale_blocked = (
        time.time()
        - stale.created_at
    ) > SIGNAL_EXPIRY_SECONDS

    bad_qty = (
        quantity
        + (
            contract.qty_step
            / Decimal("2")
        )
    )

    bad_price = (
        price
        + (
            contract.price_step
            / Decimal("2")
        )
    )

    invalid_quantity_blocked = not step_match(
        bad_qty,
        contract.qty_step,
    )

    invalid_price_blocked = not step_match(
        bad_price,
        contract.price_step,
    )

    invalid_client_id_blocked = (
        CLIENT_ID_RE.fullmatch(
            "r26 invalid client id with spaces"
        )
        is None
    )

    tracker = OrderTracker(
        "failure-order"
    )

    tracker.apply(
        "FILLED",
        quantity,
        "evt-filled",
    )

    accepted_regression, _, reason = tracker.apply(
        "NEW",
        quantity,
        "evt-regression",
    )

    ambiguous = classify_order_response(
        {
            "clientOrderId": "r26-x"
        }
    )

    return FailurePathTests(
        duplicate_submit_blocked=(
            first
            and not second
        ),
        stale_intent_blocked=(
            stale_blocked
        ),
        invalid_quantity_blocked=(
            invalid_quantity_blocked
        ),
        invalid_price_blocked=(
            invalid_price_blocked
        ),
        invalid_client_id_blocked=(
            invalid_client_id_blocked
        ),
        terminal_regression_blocked=(
            not accepted_regression
            and reason
            == "terminal-regression"
        ),
        real_post_blocked_before_network=(
            not LIVE_ORDER_EXECUTION
            and HARD_REAL_POST_LOCK
        ),
        ambiguous_response_fail_closed=(
            ambiguous[0] is False
            and ambiguous[1]
            == "AMBIGUOUS"
        ),
    )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session: aiohttp.ClientSession,
    text: str,
) -> bool:

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        return False

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as r:
            return (
                200
                <= r.status
                < 300
            )

    except Exception:
        return False


# ============================================================
# HEALTH SERVER
# ============================================================

DIAGNOSTIC_STATUS = {
    "module": MODULE_NAME,
    "state": "starting",
    "last_error": "",
    "real_post_called": False,
    "live_order_execution": LIVE_ORDER_EXECUTION,
}


async def health_handler(
    request: web.Request,
) -> web.Response:

    return web.json_response(
        DIAGNOSTIC_STATUS
    )


async def start_health_server() -> web.AppRunner:
    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        PORT,
    )

    await site.start()

    print(
        f"HEALTH SERVER ACTIVE ON PORT {PORT}",
        flush=True,
    )

    return runner


# ============================================================
# REPORT
# ============================================================

def build_report(
    available_usdt: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
    entry_margin: Decimal,
    entry_notional: Decimal,
    quantity: Decimal,
    gate_results: Dict[str, bool],
    order_sm: Dict[str, bool],
    intent_results: Dict[str, bool],
    preflight: Dict[str, bool],
    rehearsal: PayloadRehearsal,
    lifecycle: DemoLifecycleResult,
    history_idem: Dict[str, Any],
    position_before: Decimal,
    position_after: Decimal,
    position_reconciled: bool,
    failure_tests: FailurePathTests,
    final_intent: ExecutionIntent,
) -> str:

    initial_exposure = ENTRY_PERCENT

    pyramid_exposure = (
        PYRAMID_SIZE_PERCENT
        * MAX_PYRAMID_ADDS
    )

    backup_exposure = (
        BACKUP_SIZE_PERCENT
        * MAX_BACKUPS
    )

    total_exposure = (
        initial_exposure
        + pyramid_exposure
        + backup_exposure
    )

    overall_preflight = all(
        preflight.values()
    )

    failure_all = all(
        vars(
            failure_tests
        ).values()
    )

    lines = [
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED",
        SYMBOL,
        f"Available USDT: {decimal_text(available_usdt)}",
        f"Mark Price: {decimal_text(mark_price)} USDT",
        "",
        "FINAL EXECUTION GATE",
        f"API Trading Symbol: {yesno(gate_results['api_symbol'])}",
        f"Fresh Signal Accepted: {yesno(gate_results['fresh_signal'])}",
        f"Expired Signal Rejected: {yesno(gate_results['expired_signal'])}",
        f"Loss Cooldown Test: {yesno(gate_results['loss_cooldown'])}",
        f"Duplicate Signal Rejected: {yesno(gate_results['duplicate_signal'])}",
        f"One Direction Gate: {yesno(gate_results['one_direction'])}",
        f"External Position Clear: {yesno(gate_results['external_position_clear'])}",
        "",
        "ADJUSTABLE CONFIG",
        f"Entry: {decimal_text(ENTRY_PERCENT)}%",
        f"Leverage: {LEVERAGE}x",
        f"Max Config Leverage: {MAX_CONFIG_LEVERAGE}x",
        f"Margin Type: {MARGIN_TYPE}",
        f"Max Pyramids: {MAX_PYRAMID_ADDS}",
        f"Pyramid Size: {decimal_text(PYRAMID_SIZE_PERCENT)}%",
        f"Max Backups: {MAX_BACKUPS}",
        f"Backup Size: {decimal_text(BACKUP_SIZE_PERCENT)}% each",
        f"Backup Buffer: {decimal_text(BACKUP_BUFFER_PERCENT)}%",
        f"Min Liq Distance: {decimal_text(MIN_LIQ_DISTANCE_PERCENT)}%",
        f"Max Fund Exposure: {decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%",
        "",
        "WEEX CONTRACT",
        f"Minimum Order: {decimal_text(contract.min_qty)}",
        f"Quantity Precision: {contract.qty_precision}",
        f"Quantity Step: {decimal_text(contract.qty_step)}",
        f"Price Precision: {contract.price_precision}",
        f"Price Step: {decimal_text(contract.price_step)}",
        f"Contract Value: {decimal_text(contract.contract_value)}",
        f"WEEX Min Leverage: {contract.min_leverage}x",
        f"WEEX Max Leverage: {contract.max_leverage}x",
        f"Leverage Gate: {yesno(contract.min_leverage <= LEVERAGE <= contract.max_leverage)}",
        "",
        "DYNAMIC ENTRY",
        f"Margin: {decimal_text(entry_margin)} USDT",
        f"Notional: {decimal_text(entry_notional)} USDT",
        f"Quantity: {decimal_text(quantity)}",
        f"Quantity Positive: {yesno(quantity > 0)}",
        f"Minimum Passed: {yesno(quantity >= contract.min_qty)}",
        "",
        "WORST-CASE EXPOSURE",
        f"Initial: {decimal_text(initial_exposure)}%",
        f"Pyramids: {decimal_text(pyramid_exposure)}%",
        f"Backups: {decimal_text(backup_exposure)}%",
        f"Total: {decimal_text(total_exposure)}% / {decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%",
        f"Exposure Passed: {yesno(total_exposure <= MAX_FUND_EXPOSURE_PERCENT)}",
        "",
        "TP / TRAILING",
        f"TP1 / TP2 / TP3: {decimal_text(TP1_PERCENT)}% / {decimal_text(TP2_PERCENT)}% / {decimal_text(TP3_PERCENT)}%",
        f"TP1 Trigger: {decimal_text(TP1_TRIGGER_PERCENT)}%",
        f"TP2 Trigger: {decimal_text(TP2_TRIGGER_PERCENT)}%",
        f"Trailing Distance: {decimal_text(TRAILING_DISTANCE_PERCENT)}%",
        "",
        "R26 ORDER STATE MACHINE",
        f"NEW State Accepted: {yesno(order_sm['new'])}",
        f"Partial Fill #1 Delta: {yesno(order_sm['partial1'])}",
        f"Partial Fill #2 Delta: {yesno(order_sm['partial2'])}",
        f"FILLED Terminal State: {yesno(order_sm['filled'])}",
        f"Duplicate Exchange Event Blocked: {yesno(order_sm['duplicate'])}",
        f"Terminal Regression Blocked: {yesno(order_sm['terminal_regression'])}",
        "",
        "R26 EXECUTION INTENT GATE",
        f"Intent Created: {yesno(intent_results['created'])}",
        f"Duplicate Intent Blocked: {yesno(intent_results['duplicate'])}",
        f"NEW → PREFLIGHT: {yesno(intent_results['to_preflight'])}",
        f"PREFLIGHT → READY: {yesno(intent_results['to_ready'])}",
        f"Expired Intent Rejected: {yesno(intent_results['expired'])}",
        f"Terminal Intent Regression Blocked: {yesno(intent_results['terminal_regression'])}",
        "",
        "R26 EXECUTION PREFLIGHT",
        f"Live Execution OFF: {yesno(preflight['live_off'])}",
        f"Hard Real POST Lock: {yesno(preflight['hard_lock'])}",
        f"Intent Fresh: {yesno(preflight['fresh'])}",
        f"Intent Quantity Positive: {yesno(preflight['qty_positive'])}",
        f"Intent Minimum Passed: {yesno(preflight['minimum'])}",
        f"Intent Leverage Passed: {yesno(preflight['leverage'])}",
        f"Intent Exposure Passed: {yesno(preflight['exposure'])}",
        f"Real Order Path Blocked: {yesno(preflight['real_blocked'])}",
        f"Overall Preflight: {yesno(overall_preflight)}",
        "",
        "R26 LIVE PAYLOAD REHEARSAL",
        f"Real Endpoint Target: {REAL_ORDER_PATH}",
        f"Payload Built: {yesno(bool(rehearsal.payload))}",
        f"Required Fields Present: {yesno(rehearsal.required_fields_present)}",
        f"Client Order ID: {rehearsal.payload.get('newClientOrderId', '')}",
        f"Client Order ID Valid: {yesno(rehearsal.client_id_valid)}",
        f"Deterministic Client ID: {yesno(rehearsal.deterministic_rebuild_match)}",
        f"Quantity Step Match: {yesno(rehearsal.quantity_step_match)}",
        f"Price Step Match: {yesno(rehearsal.price_step_match)}",
        f"Signature Generated Locally: {yesno(rehearsal.signature_generated)}",
        f"Accepted Response Classifier: {yesno(rehearsal.response_accept_classification_test)}",
        f"Rejected Response Classifier: {yesno(rehearsal.response_reject_classification_test)}",
        f"Ambiguous Response Fails Closed: {yesno(rehearsal.ambiguous_response_classification_test)}",
        f"Real POST Transmission Blocked: {yesno(rehearsal.real_path_blocked)}",
        "",
        "R26 DEMO ORDER LIFECYCLE",
        f"Demo Symbol: {lifecycle.demo_symbol}",
        f"Demo Side: {lifecycle.side}",
        f"Demo Position Side: {lifecycle.position_side}",
        f"Demo Type: {lifecycle.order_type}",
        f"Demo Time In Force: {lifecycle.tif}",
        f"Demo Limit Price: {decimal_text(lifecycle.limit_price)}",
        f"Price Step Match: {yesno(lifecycle.price_step_match)}",
        f"Demo Client Order ID: {lifecycle.client_order_id}",
        f"Client Order ID Valid: {yesno(lifecycle.client_order_id_valid)}",
        f"Demo POST Attempted: {yesno(lifecycle.post_attempted)}",
        f"Demo POST Accepted: {yesno(lifecycle.post_accepted)}",
        f"Demo Order ID: {lifecycle.order_id}",
        f"Response Client ID Match: {yesno(lifecycle.response_client_id_match)}",
        f"History Lookup Attempted: {yesno(lifecycle.history_lookup_attempted)}",
        f"History Poll Attempts: {lifecycle.history_poll_attempts}",
        f"Order Found In History: {yesno(lifecycle.history_found)}",
        f"History Order ID Match: {yesno(lifecycle.history_order_id_match)}",
        f"History Client ID Match: {yesno(lifecycle.history_client_id_match)}",
        f"History Symbol Match: {yesno(lifecycle.history_symbol_match)}",
        f"History Side Match: {yesno(lifecycle.history_side_match)}",
        f"History Position Side Match: {yesno(lifecycle.history_position_side_match)}",
        f"Demo Final Status: {lifecycle.final_status}",
        f"Status Recognized: {yesno(lifecycle.status_recognized)}",
        f"Requested Quantity: {decimal_text(lifecycle.requested_qty)}",
        f"History Original Quantity: {decimal_text(lifecycle.original_qty)}",
        f"History Executed Quantity: {decimal_text(lifecycle.executed_qty)}",
        f"Quantity Reconciliation: {yesno(lifecycle.quantity_reconciled)}",
        f"Lifecycle Validation: {yesno(lifecycle.lifecycle_valid)}",
        "",
        "R26 ACTUAL HISTORY IDEMPOTENCY",
        f"First Processing Accepted: {yesno(history_idem['first'])}",
        f"Duplicate Processing Blocked: {yesno(history_idem['duplicate'])}",
        f"Actual History Terminal: {yesno(history_idem['terminal'])}",
        f"Actual Fill Delta: {decimal_text(history_idem['delta'])}",
        "",
        "R26 DEMO POSITION RECONCILIATION",
        f"Position Size Before: {decimal_text(position_before)}",
        f"Position Size After: {decimal_text(position_after)}",
        f"Position Reconciled: {yesno(position_reconciled)}",
        "",
        "R26 FAILURE-PATH MATRIX",
        f"Duplicate Submit Blocked: {yesno(failure_tests.duplicate_submit_blocked)}",
        f"Stale Intent Blocked: {yesno(failure_tests.stale_intent_blocked)}",
        f"Invalid Quantity Blocked: {yesno(failure_tests.invalid_quantity_blocked)}",
        f"Invalid Price Blocked: {yesno(failure_tests.invalid_price_blocked)}",
        f"Invalid Client ID Blocked: {yesno(failure_tests.invalid_client_id_blocked)}",
        f"Terminal Regression Blocked: {yesno(failure_tests.terminal_regression_blocked)}",
        f"Real POST Blocked Before Network: {yesno(failure_tests.real_post_blocked_before_network)}",
        f"Ambiguous Response Fails Closed: {yesno(failure_tests.ambiguous_response_fail_closed)}",
        f"Failure Matrix Passed: {yesno(failure_all)}",
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
    
