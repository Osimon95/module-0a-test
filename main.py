
async def reconcile_weex():
    await load_mark_price()
    try:
        await load_available_balance()
    except Exception as exc:
        log(f'BALANCE READ FAILED = {exc}')
        raise
    try:
        await load_open_positions()
    except Exception as exc:
        log(f'POSITION READ FAILED = {exc}')
        raise
    try:
        await load_exchange_config()
    except Exception as exc:
        log(f'EXCHANGE CONFIG READ FAILED = {exc}')
        raise
    return True

async def load_historical_klines():
    all_rows = []
    for page in range(MAX_HISTORICAL_PAGES):
        params = {'symbol': SYMBOL, 'interval': KLINE_INTERVAL, 'limit': HISTORICAL_LIMIT}
        if page > 0:
            params['endTime'] = int(time.time() * 1000) - page * HISTORICAL_LIMIT * 60 * 1000
        data = await weex_get('/capi/v3/market/klines', params=params, authenticated=False)
        rows = data
        if isinstance(data, dict):
            rows = data.get('data', data.get('result', []))
        if not isinstance(rows, list):
            raise RuntimeError('Unexpected kline response')
        all_rows.extend(rows)
        if len(rows) < HISTORICAL_LIMIT:
            break
    return all_rows

def candle_high(row):
    if isinstance(row, dict):
        for key in ('high', 'highPrice'):
            if key in row:
                return D(row[key])
    if isinstance(row, list) and len(row) >= 3:
        return D(row[2])
    raise ValueError('Unable to read candle high')

def candle_low(row):
    if isinstance(row, dict):
        for key in ('low', 'lowPrice'):
            if key in row:
                return D(row[key])
    if isinstance(row, list) and len(row) >= 4:
        return D(row[3])
    raise ValueError('Unable to read candle low')

def historical_highs(rows):
    return [candle_high(row) for row in rows]

def historical_lows(rows):
    return [candle_low(row) for row in rows]

def candle_close(row):
    if isinstance(row, dict):
        for key in ('close', 'closePrice', 'c', 'lastPrice'):
            if key in row:
                return D(row[key])
    if isinstance(row, list) and len(row) >= 5:
        return D(row[4])
    raise ValueError('Unable to read candle close')

def candle_timestamp(row):
    if isinstance(row, dict):
        for key in ('timestamp', 'ts', 'time', 'startTime', 'openTime'):
            if key in row:
                try:
                    return int(float(row[key]))
                except Exception:
                    return None
    if isinstance(row, list) and row:
        try:
            return int(float(row[0]))
        except Exception:
            return None
    return None

def chronological_rows(rows):
    usable = []
    for row in rows:
        try:
            close = candle_close(row)
            if close <= 0:
                continue
            ts = candle_timestamp(row)
            usable.append((ts, row))
        except Exception:
            continue
    if usable and all((item[0] is not None for item in usable)):
        by_ts = {item[0]: item[1] for item in usable}
        return [by_ts[ts] for ts in sorted(by_ts)]
    return [item[1] for item in usable]

def ema_series(values, period):
    if len(values) < period:
        return None
    multiplier = Decimal('2') / Decimal(period + 1)
    ema = sum(values[:period]) / Decimal(period)
    for price in values[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_emas(closes):
    return (
        ema_series(closes, EMA_FAST),
        ema_series(closes, EMA_MID),
        ema_series(closes, EMA_SLOW)
    )

def ema_structure(ema19, ema50, ema200):
    if ema19 > ema50 > ema200:
        return 'STRONG_BULLISH'
    if ema19 < ema50 < ema200:
        return 'STRONG_BEARISH'
    if ema19 > ema50:
        return 'EARLY_BULLISH'
    if ema19 < ema50:
        return 'EARLY_BEARISH'
    return 'NEUTRAL'

def ema_direction(structure):
    if structure == 'STRONG_BULLISH':
        return 'LONG'
    if structure == 'STRONG_BEARISH':
        return 'SHORT'
    return None

def ema_separation_percent(price, ema19, ema50):
    if price <= 0:
        return Decimal('0')
    return abs(ema19 - ema50) / price * Decimal('100')

def detect_ema19_50_crossover(previous19, previous50, current19, current50):
    if None in (previous19, previous50, current19, current50):
        return None
    if previous19 <= previous50 and current19 > current50:
        return 'LONG'
    if previous19 >= previous50 and current19 < current50:
        return 'SHORT'
    return None

def build_ema_signal_snapshot(rows):
    ordered = chronological_rows(rows)
    closes = [candle_close(row) for row in ordered]
    if len(closes) < EMA_SLOW + EMA_CONFIRMATION_CANDLES:
        return {
            'ready': False,
            'reason': 'INSUFFICIENT_CANDLES_FOR_EMA200_CONFIRMATION',
            'rows': len(closes)
        }

    current19, current50, current200 = calculate_emas(closes)
    previous19, previous50, previous200 = calculate_emas(closes[:-1])
    current_price = closes[-1]
    structure = ema_structure(current19, current50, current200)
    direction = ema_direction(structure)
    separation = ema_separation_percent(current_price, current19, current50)
    crossover = detect_ema19_50_crossover(
        previous19,
        previous50,
        current19,
        current50
    )
    quality_ok = separation >= MIN_EMA_19_50_SEPARATION_PERCENT
    ideal_direction = direction if quality_ok else None

    return {
        'ready': True,
        'reason': 'EMA_ENGINE_READY',
        'rows': len(closes),
        'price': decimal_to_string(current_price),
        'ema19': decimal_to_string(current19),
        'ema50': decimal_to_string(current50),
        'ema200': decimal_to_string(current200),
        'structure': structure,
        'direction': direction,
        'ideal_direction': ideal_direction,
        'ema19_50_separation_percent': decimal_to_string(separation),
        'minimum_separation_percent': decimal_to_string(
            MIN_EMA_19_50_SEPARATION_PERCENT
        ),
        'quality_ok': quality_ok,
        'fresh_crossover': crossover,
        'confirmation_policy': 'NEXT_CLOSED_1M_CANDLE',
        'signal_expiry_seconds': SIGNAL_EXPIRY_SECONDS
    }

def normalize_telegram_command(text):
    return ' '.join(str(text or '').strip().upper().split())

def parse_telegram_trade_command(text):
    normalized = normalize_telegram_command(text)
    if normalized == TELEGRAM_BUY_COMMAND:
        return {
            'recognized': True,
            'command': normalized,
            'direction': 'LONG'
        }
    if normalized == TELEGRAM_SELL_COMMAND:
        return {
            'recognized': True,
            'command': normalized,
            'direction': 'SHORT'
        }
    return {
        'recognized': False,
        'command': normalized,
        'direction': None
    }

def validate_telegram_command_against_signal(
    text,
    ema_snapshot,
    long_eligible,
    short_eligible
):
    parsed = parse_telegram_trade_command(text)
    direction = parsed['direction']

    if not parsed['recognized']:
        return {
            **parsed,
            'authorized_preview': False,
            'reason': 'UNRECOGNIZED_COMMAND'
        }

    if not ema_snapshot.get('ready'):
        return {
            **parsed,
            'authorized_preview': False,
            'reason': 'EMA_ENGINE_NOT_READY'
        }

    ideal = ema_snapshot.get('ideal_direction')

    if ideal != direction:
        return {
            **parsed,
            'authorized_preview': False,
            'reason': 'COMMAND_DIRECTION_DOES_NOT_MATCH_IDEAL_EMA_CONDITION',
            'ema_ideal_direction': ideal
        }

    market_ok = long_eligible if direction == 'LONG' else short_eligible

    if not market_ok:
        return {
            **parsed,
            'authorized_preview': False,
            'reason': 'COMMAND_DIRECTION_TP_MARKET_NOT_ELIGIBLE',
            'ema_ideal_direction': ideal
        }

    return {
        **parsed,
        'authorized_preview': True,
        'reason': 'COMMAND_AND_EMA_AND_TP_DIRECTION_AGREE',
        'ema_ideal_direction': ideal,
        'exchange_order_sent': False
    }

def build_ideal_condition_alert(ema_snapshot):
    if not ema_snapshot.get('ready'):
        return None

    direction = ema_snapshot.get('ideal_direction')

    if direction not in ('LONG', 'SHORT'):
        return None

    command = (
        TELEGRAM_BUY_COMMAND
        if direction == 'LONG'
        else TELEGRAM_SELL_COMMAND
    )

    return (
        f"R36F.13.2 IDEAL {direction} CONDITION | {SYMBOL}\n"
        f"Price={ema_snapshot.get('price')} "
        f"EMA19={ema_snapshot.get('ema19')} "
        f"EMA50={ema_snapshot.get('ema50')} "
        f"EMA200={ema_snapshot.get('ema200')}\n"
        f"Structure={ema_snapshot.get('structure')} "
        f"EMA19/50 separation="
        f"{ema_snapshot.get('ema19_50_separation_percent')}%\n"
        f"Manual command: {command}\n"
        "R36F.13.2 exchange execution remains disabled."
    )

async def send_r36f12_telegram_alert(message):
    if not message:
        return {
            'attempted': False,
            'sent': False,
            'reason': 'NO_IDEAL_ALERT'
        }

    if not R36F12_TELEGRAM_ALERTS_ENABLED:
        return {
            'attempted': False,
            'sent': False,
            'reason': 'ALERTS_DISABLED_BY_DEFAULT'
        }

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            'attempted': False,
            'sent': False,
            'reason': 'TELEGRAM_CONFIG_MISSING'
        }

    url = (
        f'https://api.telegram.org/'
        f'bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    )

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'disable_web_page_preview': True
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                body = await response.text()

                return {
                    'attempted': True,
                    'sent': 200 <= response.status < 300,
                    'http_status': response.status,
                    'response_preview': body[:200]
                }

    except Exception as exc:
        return {
            'attempted': True,
            'sent': False,
            'reason': f'{type(exc).__name__}: {exc}'
        }

def r36f1541_classify_demo_event(command_preview, submission):
    command_preview = (
        command_preview
        if isinstance(command_preview, dict)
        else {}
    )

    submission = (
        submission
        if isinstance(submission, dict)
        else {}
    )

    direction = str(
        command_preview.get('direction')
        or 'UNKNOWN'
    ).upper()

    authorized = bool(
        command_preview.get('authorized_preview')
    )

    reason = str(
        submission.get('reason')
        or ''
    )

    if submission.get('accepted') is True:
        return (
            'DEMO_ORDER_ACCEPTED',
            direction
        )

    if (
        submission.get('attempted') is True
        and submission.get('accepted') is not True
    ):
        return (
            'DEMO_ORDER_REJECTED',
            direction
        )

    if reason == 'JIT_DEMO_TRIGGER_VALIDATION_BLOCKED':
        return (
            'JIT_TRIGGER_BLOCKED',
            direction
        )

    if (
        authorized
        and reason not in (
            'FIRST_DEMO_ORDER_ALREADY_COMPLETED',
            'UNRESOLVED_DEMO_JOURNAL_BLOCKS_RETRY'
        )
    ):
        return (
            'DEMO_TRADE_READY',
            direction
        )

    return (
        'WAITING',
        direction
    )

def r36f1541_build_event_message(
    event_name,
    direction,
    command_preview,
    submission
):
    command_preview = (
        command_preview
        if isinstance(command_preview, dict)
        else {}
    )

    submission = (
        submission
        if isinstance(submission, dict)
        else {}
    )

    jit = (
        submission.get('jit_validation')
        if isinstance(
            submission.get('jit_validation'),
            dict
        )
        else {}
    )

    journal = (
        submission.get('journal')
        if isinstance(
            submission.get('journal'),
            dict
        )
        else {}
    )

    transport = (
        submission.get('transport')
        if isinstance(
            submission.get('transport'),
            dict
        )
        else {}
    )

    if event_name == 'DEMO_ORDER_ACCEPTED':
        title = '✅✅✅ WEEX DEMO ORDER ACCEPTED ✅✅✅'

    elif event_name == 'DEMO_ORDER_REJECTED':
        title = '❌❌❌ WEEX DEMO ORDER REJECTED ❌❌❌'

    elif event_name == 'JIT_TRIGGER_BLOCKED':
        title = '⛔⛔⛔ DEMO TRADE BLOCKED ⛔⛔⛔'

    else:
        title = '🚨🚨🚨 R36F.15.4.1 ACTION ALERT 🚨🚨🚨'

    reason = str(
        submission.get('reason')
        or journal.get('error_message')
        or journal.get('error')
        or 'NONE'
    )

    lines = [
        title,
        f'Event: {event_name}',
        f'Direction: {direction}',
        f"EMA: {EMA_SIGNAL_SNAPSHOT.get('ideal_direction')}",
        (
            'Command authorized: '
            f"{command_preview.get('authorized_preview', False)}"
        ),
        f'Reason: {reason}'
    ]

    if jit:
        lines.extend([
            (
                'JIT: '
                + (
                    'PASSED'
                    if jit.get('valid')
                    else 'BLOCKED'
                )
            ),
            f"Fresh mark: {jit.get('fresh_mark_price')}",
            f"TP: {jit.get('tp_trigger_price')}",
            f"SL: {jit.get('sl_trigger_price')}"
        ])

    order_id = (
        journal.get('order_id')
        or ''
    )

    if order_id:
        lines.append(
            f'Demo order ID: {order_id}'
        )

    http_status = transport.get(
        'http_status'
    )

    if http_status is not None:
        lines.append(
            f'WEEX HTTP: {http_status}'
        )

    lines.append(
        'Production real-money execution remains disabled.'
    )

    return '\n'.join(
        lines
    )

async def send_r36f1541_state_change_alert(
    command_preview,
    submission
):
    event_name, direction = (
        r36f1541_classify_demo_event(
            command_preview,
            submission
        )
    )

    previous = read_json_file(
        R36F1541_TELEGRAM_EVENT_STATE_FILE,
        default={}
    )

    previous_event = str(
        previous.get('event_name')
        or ''
    )

    previous_direction = str(
        previous.get('direction')
        or ''
    )

    if event_name == 'WAITING':
        if (
            previous_event != 'WAITING'
            or previous_direction != direction
        ):
            write_json_file(
                R36F1541_TELEGRAM_EVENT_STATE_FILE,
                {
                    'stage': STAGE,
                    'event_name': 'WAITING',
                    'direction': direction,
                    'updated_at': now_iso()
                }
            )

        return {
            'attempted': False,
            'sent': False,
            'reason': 'WAITING_STATE_SILENT'
        }

    if (
        previous_event == event_name
        and previous_direction == direction
    ):
        return {
            'attempted': False,
            'sent': False,
            'deduplicated': True,
            'reason': 'DUPLICATE_NOTIFICATION_BLOCKED',
            'event_name': event_name
        }

    message = (
        r36f1541_build_event_message(
            event_name,
            direction,
            command_preview,
            submission
        )
    )

    result = await send_r36f12_telegram_alert(
        message
    )

    if result.get('sent'):
        write_json_file(
            R36F1541_TELEGRAM_EVENT_STATE_FILE,
            {
                'stage': STAGE,
                'event_name': event_name,
                'direction': direction,
                'updated_at': now_iso()
            }
        )

    result = dict(
        result
    )

    result['event_name'] = event_name
    result['direction'] = direction

    return result

def synthetic_r36f12_ema_telegram_tests():
    bullish = {
        'ready': True,
        'ideal_direction': 'LONG',
        'structure': 'STRONG_BULLISH',
        'price': '80000',
        'ema19': '80100',
        'ema50': '80000',
        'ema200': '79000',
        'ema19_50_separation_percent': '0.125'
    }

    bearish = {
        'ready': True,
        'ideal_direction': 'SHORT',
        'structure': 'STRONG_BEARISH',
        'price': '80000',
        'ema19': '79900',
        'ema50': '80000',
        'ema200': '81000',
        'ema19_50_separation_percent': '0.125'
    }

    buy = parse_telegram_trade_command(
        '  buy   btc now '
    )

    sell = parse_telegram_trade_command(
        'SELL BTC NOW'
    )

    check(
        'R36F12_TELEGRAM_BUY_COMMAND_PARSES_LONG',
        buy['recognized']
        and buy['direction'] == 'LONG'
    )

    check(
        'R36F12_TELEGRAM_SELL_COMMAND_PARSES_SHORT',
        sell['recognized']
        and sell['direction'] == 'SHORT'
    )

    check(
        'R36F12_TELEGRAM_UNKNOWN_COMMAND_REJECTED',
        parse_telegram_trade_command(
            'BUY ETH NOW'
        )['recognized']
        is False
    )

    buy_ok = (
        validate_telegram_command_against_signal(
            'BUY BTC NOW',
            bullish,
            True,
            False
        )
    )

    sell_ok = (
        validate_telegram_command_against_signal(
            'SELL BTC NOW',
            bearish,
            False,
            True
        )
    )

    mismatch = (
        validate_telegram_command_against_signal(
            'SELL BTC NOW',
            bullish,
            True,
            True
        )
    )

    check(
        'R36F12_BUY_MATCHING_IDEAL_LONG_PREVIEW_APPROVED',
        buy_ok['authorized_preview']
        is True
    )

    check(
        'R36F12_SELL_MATCHING_IDEAL_SHORT_PREVIEW_APPROVED',
        sell_ok['authorized_preview']
        is True
    )

    check(
        'R36F12_DIRECTION_MISMATCH_BLOCKED',
        mismatch['authorized_preview']
        is False
    )

    check(
        'R36F12_COMMAND_PREVIEW_NEVER_SENDS_ORDER',
        buy_ok.get('exchange_order_sent')
        is False
    )

    return True

def build_extrema(values):
    if len(values) < 3:
        return []

    extrema = []

    for index in range(
        1,
        len(values) - 1
    ):
        previous_value = D(
            values[index - 1]
        )

        current_value = D(
            values[index]
        )

        next_value = D(
            values[index + 1]
        )

        if (
            current_value >= previous_value
            and current_value >= next_value
        ):
            extrema.append(
                current_value
            )

        elif (
            current_value <= previous_value
            and current_value <= next_value
        ):
            extrema.append(
                current_value
            )

    return extrema

def local_extrema_values(rows, side):
    if side == 'LONG':
        values = historical_highs(rows)

    elif side == 'SHORT':
        values = historical_lows(rows)

    else:
        raise ValueError(
            f'Unsupported side={side}'
        )

    return build_extrema(
        values
    )

def cluster_extrema(extrema):
    if not extrema:
        return []

    sorted_values = sorted([
        D(value)
        for value in extrema
    ])

    clusters = []
    current = [
        sorted_values[0]
    ]

    for value in sorted_values[1:]:
        current_average = (
            sum(current)
            / Decimal(
                len(current)
            )
        )

        tolerance = (
            current_average
            * CLUSTER_TOLERANCE_PERCENT
            / Decimal('100')
        )

        if (
            abs(
                value
                - current_average
            )
            <= tolerance
        ):
            current.append(
                value
            )

        else:
            clusters.append({
                'minimum': min(current),
                'maximum': max(current),
                'average': (
                    sum(current)
                    / Decimal(
                        len(current)
                    )
                ),
                'touches': len(current)
            })

            current = [
                value
            ]

    clusters.append({
        'minimum': min(current),
        'maximum': max(current),
        'average': (
            sum(current)
            / Decimal(
                len(current)
            )
        ),
        'touches': len(current)
    })

    return clusters

def validate_clusters(
    clusters,
    entry_price,
    side
):
    entry_price = D(
        entry_price
    )

    valid = []
    invalid = []

    for cluster in clusters:
        reasons = []
        touches = cluster[
            'touches'
        ]

        average = D(
            cluster['average']
        )

        if touches < MIN_CLUSTER_TOUCHES:
            reasons.append(
                'INSUFFICIENT_TOUCHES'
            )

        if side == 'LONG':
            if average <= entry_price:
                reasons.append(
                    'CLUSTER_NOT_ABOVE_ENTRY'
                )

        elif side == 'SHORT':
            if average >= entry_price:
                reasons.append(
                    'CLUSTER_NOT_BELOW_ENTRY'
                )

        else:
            reasons.append(
                'INVALID_DIRECTION'
            )

        result = dict(
            cluster
        )

        result['valid'] = not reasons
        result['reasons'] = reasons

        if reasons:
            invalid.append(
                result
            )

        else:
            valid.append(
                result
            )

    if side == 'LONG':
        valid.sort(
            key=lambda item:
            item['average']
        )

    elif side == 'SHORT':
        valid.sort(
            key=lambda item:
            item['average'],
            reverse=True
        )

    return (
        valid,
        invalid
    )

def build_cluster_diagnostics(
    rows,
    entry_price,
    side
):
    entry_price = D(
        entry_price
    )

    if side == 'LONG':
        values = historical_highs(
            rows
        )

    elif side == 'SHORT':
        values = historical_lows(
            rows
        )

    else:
        raise ValueError(
            f'Unsupported side={side}'
        )

    extrema = build_extrema(
        values
    )

    clusters = cluster_extrema(
        extrema
    )

    valid, invalid = (
        validate_clusters(
            clusters,
            entry_price,
            side
        )
    )

    diagnostics = {
        'side': side,
        'entry_price': decimal_to_string(
            entry_price
        ),
        'historical_row_count': len(rows),
        'extrema_count': len(extrema),
        'cluster_count': len(clusters),
        'valid_cluster_count': len(valid),
        'invalid_cluster_count': len(invalid),
        'required_valid_clusters': REQUIRED_TP_CLUSTERS,
        'valid_clusters': valid,
        'invalid_clusters': invalid
    }

    if len(valid) >= REQUIRED_TP_CLUSTERS:
        diagnostics[
            'failure_reason'
        ] = None

    elif len(valid) == 1:
        diagnostics[
            'failure_reason'
        ] = (
            'ONLY_ONE_VALID_CLUSTER'
        )

    elif len(extrema) == 0:
        diagnostics[
            'failure_reason'
        ] = (
            'NO_LOCAL_EXTREMA'
        )

    elif len(clusters) == 0:
        diagnostics[
            'failure_reason'
        ] = (
            'NO_HISTORICAL_CLUSTERS'
        )

    else:
        diagnostics[
            'failure_reason'
        ] = (
            'EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET'
        )

    log(
        f"{side} HISTORICAL ROW COUNT = "
        f"{diagnostics['historical_row_count']}"
    )

    log(
        f"{side} EXTREMA COUNT = "
        f"{diagnostics['extrema_count']}"
    )

    log(
        f"{side} CLUSTER COUNT = "
        f"{diagnostics['cluster_count']}"
    )

    log(
        f"{side} VALID CLUSTER COUNT = "
        f"{diagnostics['valid_cluster_count']}"
    )

    for index, cluster in enumerate(
        clusters,
        start=1
    ):
        log(
            f"{side} CLUSTER {index}: "
            f"average="
            f"{decimal_to_string(cluster['average'])} "
            f"minimum="
            f"{decimal_to_string(cluster['minimum'])} "
            f"maximum="
            f"{decimal_to_string(cluster['maximum'])} "
            f"touches={cluster['touches']}"
        )

    for index, cluster in enumerate(
        invalid,
        start=1
    ):
        log(
            f"{side} INVALID CLUSTER {index}: "
            f"average="
            f"{decimal_to_string(cluster['average'])} "
            f"reasons="
            f"{','.join(cluster['reasons'])}"
        )

    if diagnostics[
        'failure_reason'
    ]:
        log(
            f"{side} CLUSTER DIAGNOSTIC "
            f"FAILURE_REASON = "
            f"{diagnostics['failure_reason']}"
        )

    return diagnostics

def evaluate_tp_approval(
    diagnostics
):
    valid_count = int(
        diagnostics.get(
            'valid_cluster_count',
            0
        )
    )

    if valid_count >= REQUIRED_TP_CLUSTERS:
        approval = {
            'status': 'APPROVED',
            'approved': True,
            'required_valid_clusters': REQUIRED_TP_CLUSTERS,
            'available_valid_clusters': valid_count,
            'reason': 'TWO_OR_MORE_VALID_HISTORICAL_CLUSTERS'
        }

    else:
        failure_reason = (
            diagnostics.get(
                'failure_reason'
            )
            or 'INSUFFICIENT_VALID_HISTORICAL_CLUSTERS'
        )

        approval = {
            'status': 'REJECTED',
            'approved': False,
            'required_valid_clusters': REQUIRED_TP_CLUSTERS,
            'available_valid_clusters': valid_count,
            'reason': failure_reason
        }

    log(
        f"{STAGE}_TP_APPROVAL = "
        f"{approval['status']}"
    )

    log(
        f"{STAGE}_TP_APPROVAL_REASON = "
        f"{approval['reason']}"
    )

    log(
        f'{STAGE}_TP_REQUIRED_CLUSTERS = '
        f'{REQUIRED_TP_CLUSTERS}'
    )

    log(
        f'{STAGE}_TP_AVAILABLE_CLUSTERS = '
        f'{valid_count}'
    )

    return approval

def valid_clusters(
    rows,
    entry_price,
    side
):
    entry_price = D(
        entry_price
    )

    extrema = local_extrema_values(
        rows,
        side
    )

    clusters = cluster_extrema(
        extrema
    )

    valid = []

    for cluster in clusters:
        if (
            cluster['touches']
            < MIN_CLUSTER_TOUCHES
        ):
            continue

        average = cluster[
            'average'
        ]

        if side == 'LONG':
            if average <= entry_price:
                continue

        elif side == 'SHORT':
            if average >= entry_price:
                continue

        else:
            raise ValueError(
                f'Unsupported side={side}'
            )

        valid.append(
            cluster
        )

    if side == 'LONG':
        valid.sort(
            key=lambda c:
            c['average']
        )

    else:
        valid.sort(
            key=lambda c:
            c['average'],
            reverse=True
        )

    return valid

def calculate_tp_prices(
    entry_price,
    valid_cluster_list,
    direction
):
    entry_price = D(
        entry_price
    )

    if (
        len(valid_cluster_list)
        < REQUIRED_TP_CLUSTERS
    ):
        raise RuntimeError(
            'Cannot calculate complete TP set: '
            'fewer than two valid historical clusters'
        )

    cluster1 = D(
        valid_cluster_list[0][
            'average'
        ]
    )

    cluster2 = D(
        valid_cluster_list[1][
            'average'
        ]
    )

    progress1 = (
        TP1_PROFIT_MARGIN_PERCENT
        / Decimal('100')
    )

    progress2 = (
        TP2_PROFIT_MARGIN_PERCENT
        / Decimal('100')
    )

    if direction == 'LONG':
        tp1 = (
            entry_price
            + (
                cluster1
                - entry_price
            )
            * progress1
        )

        tp2 = (
            entry_price
            + (
                cluster2
                - entry_price
            )
            * progress2
        )

    elif direction == 'SHORT':
        tp1 = (
            entry_price
            - (
                entry_price
                - cluster1
            )
            * progress1
        )

        tp2 = (
            entry_price
            - (
                entry_price
                - cluster2
            )
            * progress2
        )

    else:
        raise RuntimeError(
            'Invalid TP direction'
        )

    return {
        'tp1': quantize_down(
            tp1,
            PRICE_STEP
        ),
        'tp2': quantize_down(
            tp2,
            PRICE_STEP
        ),
        'tp3': {
            'type': 'TRAILING',
            'allocation_percent': TP3_ALLOCATION_PERCENT,
            'trailing_distance_percent': TP3_TRAILING_DISTANCE_PERCENT
        },
        'cluster1_average': cluster1,
        'cluster2_average': cluster2
    }

def run_tp_engine(
    rows,
    entry_price,
    direction
):
    if direction == 'LONG':
        values = historical_highs(
            rows
        )
        extrema = build_extrema(
            values
        )

    elif direction == 'SHORT':
        values = historical_lows(
            rows
        )
        extrema = build_extrema(
            values
        )

    else:
        raise RuntimeError(
            'Invalid direction'
        )

    clusters = cluster_extrema(
        extrema
    )

    valid, invalid = (
        validate_clusters(
            clusters,
            entry_price,
            direction
        )
    )

    approval = evaluate_tp_approval({
        'valid_cluster_count': len(valid),
        'failure_reason': (
            'ONLY_ONE_VALID_CLUSTER'
            if len(valid) == 1
            else 'INSUFFICIENT_VALID_CLUSTERS'
        )
    })

    if not approval['approved']:
        return {
            'approved': False,
            'approval': approval,
            'valid_clusters': valid,
            'invalid_clusters': invalid
        }

    prices = calculate_tp_prices(
        entry_price,
        valid,
        direction
    )

    return {
        'approved': True,
        'approval': approval,
        'valid_clusters': valid,
        'invalid_clusters': invalid,
        'prices': prices
    }

def build_cluster_tp_snapshot(
    entry_price,
    rows,
    side,
    fill_label
):
    global LAST_TP_APPROVAL

    entry_price = D(
        entry_price
    )

    diagnostics = build_cluster_diagnostics(
        rows,
        entry_price,
        side
    )

    approval = evaluate_tp_approval(
        diagnostics
    )

    LAST_TP_APPROVAL = approval

    if not approval['approved']:
        log(
            f"{side} TP SET REJECTED: "
            f"{approval['reason']}"
        )

        raise RuntimeError(
            f"{side} historical TP set rejected: "
            f"requires at least "
            f"{REQUIRED_TP_CLUSTERS} "
            f"valid clusters; found "
            f"{approval['available_valid_clusters']}"
        )

    clusters = valid_clusters(
        rows,
        entry_price,
        side
    )

    if (
        len(clusters)
        < REQUIRED_TP_CLUSTERS
    ):
        raise RuntimeError(
            'TP approval inconsistency: '
            'diagnostics approved but '
            'independent cluster extraction '
            'found fewer than two valid clusters'
        )

    prices = calculate_tp_prices(
        entry_price,
        clusters,
        side
    )

    snapshot = {
        'fill_label': fill_label,
        'side': side,
        'entry_price': decimal_to_string(
            entry_price
        ),
        'historical_diagnostics': diagnostics,
        'tp_approval': approval,
        'tp1': decimal_to_string(
            prices['tp1']
        ),
        'tp2': decimal_to_string(
            prices['tp2']
        ),
        'tp3': {
            'type': 'TRAILING',
            'allocation_percent': decimal_to_string(
                TP3_ALLOCATION_PERCENT
            ),
            'trailing_distance_percent': decimal_to_string(
                TP3_TRAILING_DISTANCE_PERCENT
            )
        },
        'cluster1_average': decimal_to_string(
            prices['cluster1_average']
        ),
        'cluster2_average': decimal_to_string(
            prices['cluster2_average']
        ),
        'primary_tp_immutable': True
    }

    log(
        f'{side} TP SET APPROVED WITH '
        f'{len(clusters)} VALID CLUSTERS'
    )

    log(
        f"{side} TP1 = {snapshot['tp1']} "
        '(20% adjustable progress)'
    )

    log(
        f"{side} TP2 = {snapshot['tp2']} "
        '(50% adjustable progress)'
    )

    log(
        f'{side} TP3 = '
        f'{TP3_ALLOCATION_PERCENT}% '
        'trailing runner'
    )

    return snapshot

def synthetic_cluster_tests():
    long_rows = [
        [1, '99000', '100000', '99500', '99500', '1'],
        [2, '99500', '100100', '99600', '99800', '1'],
        [3, '99600', '100000', '99500', '99700', '1'],
        [4, '99500', '101000', '99900', '100100', '1'],
        [5, '99900', '100200', '99500', '100000', '1'],
        [6, '99500', '101500', '100000', '100500', '1'],
        [7, '100000', '101000', '99500', '100500', '1'],
        [8, '99500', '101400', '99900', '100800', '1']
    ]

    short_rows = [
        [1, '81000', '81500', '80000', '81000', '1'],
        [2, '81000', '81500', '80100', '80800', '1'],
        [3, '80800', '81400', '80050', '80500', '1'],
        [4, '80500', '81300', '79900', '80300', '1'],
        [5, '80300', '81200', '80000', '80500', '1'],
        [6, '80500', '81400', '79800', '80400', '1'],
        [7, '80400', '81300', '80100', '80600', '1'],
        [8, '80600', '81500', '79950', '80800', '1']
    ]

    long_diagnostics = build_cluster_diagnostics(
        long_rows,
        Decimal('99000'),
        'LONG'
    )

    long_approval = evaluate_tp_approval(
        long_diagnostics
    )

    check(
        'SYNTHETIC_LONG_TWO_CLUSTER_APPROVAL',
        long_approval['approved'] is True
    )

    short_diagnostics = build_cluster_diagnostics(
        short_rows,
        Decimal('82000'),
        'SHORT'
    )

    short_approval = evaluate_tp_approval(
        short_diagnostics
    )

    check(
        'SYNTHETIC_SHORT_TWO_CLUSTER_APPROVAL',
        short_approval['approved'] is True
    )

    return (
        long_approval,
        short_approval
    )

def synthetic_tp_rejection_test():
    rows = [
        [1, '99000', '100000', '99500', '99500', '1'],
        [2, '99500', '100100', '99600', '99800', '1'],
        [3, '99600', '100000', '99500', '99700', '1'],
        [4, '99500', '100100', '99800', '99900', '1']
    ]

    entry = Decimal('99500')

    diagnostics = build_cluster_diagnostics(
        rows,
        entry,
        'LONG'
    )

    approval = evaluate_tp_approval(
        diagnostics
    )

    check(
        'ONE_CLUSTER_TP_REJECTED',
        approval['approved'] is False
    )

    check(
        'ONE_CLUSTER_APPROVAL_STATUS_REJECTED',
        approval['status'] == 'REJECTED'
    )

    check(
        'ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET',
        approval['available_valid_clusters']
        < REQUIRED_TP_CLUSTERS
    )

    return approval

def build_canary_preview():
    return {
        'stage': STAGE,
        'symbol': SYMBOL,
        'real_order_execution': REAL_ORDER_EXECUTION,
        'demo_order_execution': DEMO_ORDER_EXECUTION,
        'exchange_mutation_transport_enabled': EXCHANGE_MUTATION_TRANSPORT_ENABLED,
        'order_submission_enabled': ORDER_SUBMISSION_ENABLED,
        'first_real_order_allowed': FIRST_REAL_ORDER_ALLOWED,
        'submitted': False,
        'exchange_request_sent': False
    }

WRITER_ENDPOINT_ENTRY = '/capi/v3/order'
WRITER_ENDPOINT_TPSL = '/capi/v3/placeTpSlOrder'
WRITER_ENDPOINT_TRAILING = '/capi/v3/algoOrder'

def writer_entry_side(direction):
    if direction == 'LONG':
        return (
            'BUY',
            'LONG'
        )

    if direction == 'SHORT':
        return (
            'SELL',
            'SHORT'
        )

    raise ValueError(
        f'Unsupported direction={direction}'
    )

def writer_close_side(direction):
    if direction == 'LONG':
        return (
            'SELL',
            'LONG'
        )

    if direction == 'SHORT':
        return (
            'BUY',
            'SHORT'
        )

    raise ValueError(
        f'Unsupported direction={direction}'
    )

def writer_client_id(direction, leg):
    value = (
        f'R36F8-{direction}-{leg}-0001'
    )

    if len(value) > 36:
        raise ValueError(
            'writer client id exceeds WEEX limit'
        )

    return value

ADJUSTED_TP1_ALLOCATION_PERCENT = Decimal('25')
ADJUSTED_TP2_ALLOCATION_PERCENT = Decimal('25')
ADJUSTED_TP3_ALLOCATION_PERCENT = Decimal('50')

def allocation_exactly_representable(
    entry_quantity,
    tp1_percent,
    tp2_percent,
    tp3_percent
):
    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP
    )

    percentages = (
        D(tp1_percent),
        D(tp2_percent),
        D(tp3_percent)
    )

    if sum(percentages) != Decimal('100'):
        return False

    quantities = [
        (
            entry_quantity
            * percent
            / Decimal('100')
        )
        for percent in percentages
    ]

    return bool(
        entry_quantity >= MIN_QUANTITY
        and all(
            q >= MIN_QUANTITY
            for q in quantities
        )
        and all(
            quantize_down(
                q,
                QUANTITY_STEP
            ) == q
            for q in quantities
        )
        and sum(quantities) == entry_quantity
    )

def select_tp_allocation(entry_quantity):
    """
    Prefer 20/20/60; fall back only to
    the approved 25/25/50 allocation.
    """

    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP
    )

    preferred = (
        TP1_ALLOCATION_PERCENT,
        TP2_ALLOCATION_PERCENT,
        TP3_ALLOCATION_PERCENT
    )

    adjusted = (
        ADJUSTED_TP1_ALLOCATION_PERCENT,
        ADJUSTED_TP2_ALLOCATION_PERCENT,
        ADJUSTED_TP3_ALLOCATION_PERCENT
    )

    if allocation_exactly_representable(
        entry_quantity,
        *preferred
    ):
        return {
            'tp1_percent': preferred[0],
            'tp2_percent': preferred[1],
            'tp3_percent': preferred[2],
            'adjusted': False,
            'label': '20/20/60'
        }

    if allocation_exactly_representable(
        entry_quantity,
        *adjusted
    ):
        return {
            'tp1_percent': adjusted[0],
            'tp2_percent': adjusted[1],
            'tp3_percent': adjusted[2],
            'adjusted': True,
            'label': '25/25/50'
        }

    return None

def writer_quantities(entry_quantity):
    """
    Allocate TP quantities using preferred 20/20/60
    or approved 25/25/50 fallback.
    """

    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP
    )

    allocation = select_tp_allocation(
        entry_quantity
    )

    if allocation is None:
        return (
            entry_quantity,
            Decimal('0'),
            Decimal('0'),
            Decimal('0')
        )

    tp1 = (
        entry_quantity
        * allocation['tp1_percent']
        / Decimal('100')
    )

    tp2 = (
        entry_quantity
        * allocation['tp2_percent']
        / Decimal('100')
    )

    tp3 = (
        entry_quantity
        * allocation['tp3_percent']
        / Decimal('100')
    )

    return (
        entry_quantity,
        tp1,
        tp2,
        tp3
    )

def validate_writer_quantities(
    entry_quantity,
    tp1,
    tp2,
    tp3
):
    allocation = select_tp_allocation(
        entry_quantity
    )

    if allocation is None:
        return {
            'allocation_selected': False,
            'all_valid': False
        }

    exact_tp1 = (
        entry_quantity
        * allocation['tp1_percent']
        / Decimal('100')
    )

    exact_tp2 = (
        entry_quantity
        * allocation['tp2_percent']
        / Decimal('100')
    )

    exact_tp3 = (
        entry_quantity
        * allocation['tp3_percent']
        / Decimal('100')
    )

    checks = {
        'allocation_selected': True,
        'entry_on_step': (
            quantize_down(
                entry_quantity,
                QUANTITY_STEP
            ) == entry_quantity
        ),
        'tp1_on_step': (
            quantize_down(
                tp1,
                QUANTITY_STEP
            ) == tp1
        ),
        'tp2_on_step': (
            quantize_down(
                tp2,
                QUANTITY_STEP
            ) == tp2
        ),
        'tp3_on_step': (
            quantize_down(
                tp3,
                QUANTITY_STEP
            ) == tp3
        ),
        'entry_minimum': (
            entry_quantity
            >= MIN_QUANTITY
        ),
        'tp1_minimum': (
            tp1
            >= MIN_QUANTITY
        ),
        'tp2_minimum': (
            tp2
            >= MIN_QUANTITY
        ),
        'tp3_minimum': (
            tp3
            >= MIN_QUANTITY
        ),
        'allocation_sum_exact': (
            tp1
            + tp2
            + tp3
            == entry_quantity
        ),
        'tp1_selected_percent_exact': (
            tp1
            == exact_tp1
        ),
        'tp2_selected_percent_exact': (
            tp2
            == exact_tp2
        ),
        'tp3_selected_percent_exact': (
            tp3
            == exact_tp3
        ),
        'tp3_non_negative': (
            tp3
            >= Decimal('0')
        )
    }

    checks[
        'all_valid'
    ] = all(
        checks.values()
    )

    return checks

def minimum_adjustable_tp_entry_quantity():
    """
    Return first exchange-step quantity
    supported by an approved allocation.
    """

    candidate = QUANTITY_STEP

    for _ in range(100000):
        quantity, tp1, tp2, tp3 = (
            writer_quantities(
                candidate
            )
        )

        checks = validate_writer_quantities(
            quantity,
            tp1,
            tp2,
            tp3
        )

        if checks.get(
            'all_valid'
        ):
            return quantity

        candidate += QUANTITY_STEP

    raise RuntimeError(
        'Unable to find adjustable TP minimum entry quantity'
    )

def minimum_strict_tp_entry_quantity():
    """
    Compatibility alias: R36F.10 minimum under
    the approved adjustable allocation policy.
    """

    return minimum_adjustable_tp_entry_quantity()
