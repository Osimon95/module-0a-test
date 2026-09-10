
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

def evaluate_writer_quantity_feasibility(entry_quantity):
    quantity, tp1, tp2, tp3 = writer_quantities(entry_quantity)
    allocation = select_tp_allocation(quantity)
    checks = validate_writer_quantities(quantity, tp1, tp2, tp3)
    minimum_required = minimum_adjustable_tp_entry_quantity()
    feasible = bool(checks.get('all_valid'))
    return {'feasible': feasible, 'reason': 'ADJUSTABLE_TP_ALLOCATION_REPRESENTABLE' if feasible else 'POSITION_TOO_SMALL_OR_NOT_REPRESENTABLE_BY_APPROVED_TP_ALLOCATIONS', 'entry_quantity': decimal_to_string(quantity), 'tp1_quantity': decimal_to_string(tp1), 'tp2_quantity': decimal_to_string(tp2), 'tp3_quantity': decimal_to_string(tp3), 'requested_allocation': '20/20/60', 'selected_allocation': allocation['label'] if allocation else None, 'allocation_adjusted': bool(allocation and allocation['adjusted']), 'selected_tp1_percent': decimal_to_string(allocation['tp1_percent']) if allocation else None, 'selected_tp2_percent': decimal_to_string(allocation['tp2_percent']) if allocation else None, 'selected_tp3_percent': decimal_to_string(allocation['tp3_percent']) if allocation else None, 'minimum_required_entry_quantity': decimal_to_string(minimum_required), 'checks': checks}

def evaluate_strict_tp_balance_readiness(available_balance, mark_price, leverage):
    """
    Classify balance readiness under R36F.10
    approved adjustable TP allocation.
    """
    available_balance = D(available_balance)
    mark_price = D(mark_price)
    leverage = D(leverage)
    if available_balance < Decimal('0'):
        raise ValueError('available_balance must be non-negative')
    if mark_price <= Decimal('0'):
        raise ValueError('mark_price must be positive')
    if leverage <= Decimal('0'):
        raise ValueError('leverage must be positive')
    entry_fraction = ENTRY_MARGIN_PERCENT / Decimal('100')
    if entry_fraction <= Decimal('0'):
        raise ValueError('ENTRY_MARGIN_PERCENT must be positive')
    raw_entry_quantity = available_balance * entry_fraction * leverage / mark_price
    planned_entry_quantity = quantize_down(raw_entry_quantity, QUANTITY_STEP)
    quantity_feasibility = evaluate_writer_quantity_feasibility(planned_entry_quantity)
    minimum_entry_quantity = minimum_adjustable_tp_entry_quantity()
    required_entry_margin = minimum_entry_quantity * mark_price / leverage
    required_available_balance = required_entry_margin / entry_fraction
    available_balance_shortfall = max(Decimal('0'), required_available_balance - available_balance)
    eligible = bool(quantity_feasibility['feasible'] and available_balance >= required_available_balance)
    return {'eligible': eligible, 'status': 'ELIGIBLE' if eligible else 'TRADE_NOT_ELIGIBLE', 'reason': 'ADJUSTABLE_TP_BALANCE_AND_QUANTITY_READY' if eligible else 'INSUFFICIENT_BALANCE_FOR_APPROVED_TP_ALLOCATION', 'available_balance': decimal_to_string(available_balance), 'mark_price': decimal_to_string(mark_price), 'leverage': decimal_to_string(leverage), 'entry_margin_percent': decimal_to_string(ENTRY_MARGIN_PERCENT), 'raw_entry_quantity': decimal_to_string(raw_entry_quantity), 'planned_entry_quantity': decimal_to_string(planned_entry_quantity), 'minimum_strict_tp_entry_quantity': decimal_to_string(minimum_entry_quantity), 'required_margin_for_minimum_qty': decimal_to_string(required_entry_margin), 'required_available_balance': decimal_to_string(required_available_balance), 'available_balance_shortfall': decimal_to_string(available_balance_shortfall), 'quantity_feasible': quantity_feasibility['feasible'], 'quantity_feasibility_reason': quantity_feasibility['reason'], 'requested_allocation': quantity_feasibility['requested_allocation'], 'selected_allocation': quantity_feasibility['selected_allocation'], 'allocation_adjusted': quantity_feasibility['allocation_adjusted'], 'tp1_quantity': quantity_feasibility['tp1_quantity'], 'tp2_quantity': quantity_feasibility['tp2_quantity'], 'tp3_quantity': quantity_feasibility['tp3_quantity']}

async def r36f14_read_demo_account():
    """Read only documented WEEX V3 paper-trading resources."""
    balance_rows = await weex_get(R36F14_DEMO_BALANCE_ENDPOINT, authenticated=True)
    position_rows = await weex_get(R36F14_DEMO_POSITIONS_ENDPOINT, authenticated=True)
    history_rows = await weex_get(R36F14_DEMO_ORDER_HISTORY_ENDPOINT, params={'symbol': R36F14_DEMO_SYMBOL, 'limit': 20, 'page': 0}, authenticated=True)
    balance_rows = balance_rows if isinstance(balance_rows, list) else []
    position_rows = position_rows if isinstance(position_rows, list) else []
    history_rows = history_rows if isinstance(history_rows, list) else []
    demo_asset_row = None
    for row in balance_rows:
        if str(row.get('asset', '')).upper() == R36F14_DEMO_ASSET:
            demo_asset_row = row
            break
    demo_positions = [row for row in position_rows if str(row.get('symbol', '')).upper() == R36F14_DEMO_SYMBOL and D(row.get('size', '0')) != 0]
    return {'balance_endpoint': R36F14_DEMO_BALANCE_ENDPOINT, 'positions_endpoint': R36F14_DEMO_POSITIONS_ENDPOINT, 'history_endpoint': R36F14_DEMO_ORDER_HISTORY_ENDPOINT, 'demo_symbol': R36F14_DEMO_SYMBOL, 'demo_asset': R36F14_DEMO_ASSET, 'asset_present': demo_asset_row is not None, 'balance': str(demo_asset_row.get('balance')) if demo_asset_row else None, 'available_balance': str(demo_asset_row.get('availableBalance')) if demo_asset_row else None, 'open_demo_position_count': len(demo_positions), 'history_count': len(history_rows), 'all_reads_successful': demo_asset_row is not None}

def build_r36f14_demo_order_preview(direction, entry_quantity, tp_snapshot, protective_stop_price):
    """
    Construct only the documented WEEX V3 demo Place Order payload.

    WEEX's documented demo surface exposes Place Order with optional single
    tpTriggerPrice/slTriggerPrice but does not document demo equivalents of the
    production multi-TP conditional/trailing endpoints. Therefore the frozen
    TP1/TP2/TP3 plan remains validated and preserved internally; the demo entry
    preview carries TP1 plus the mandatory protective stop. No POST is sent.
    """
    if not tp_snapshot or not tp_snapshot.get('tp_approval', {}).get('approved'):
        raise ValueError('demo writer requires approved complete TP snapshot')
    direction = str(direction).upper()
    entry_quantity = quantize_down(D(entry_quantity), QUANTITY_STEP)
    stop_price = quantize_down(D(protective_stop_price), PRICE_STEP)
    tp1_price = quantize_down(D(tp_snapshot['tp1']), PRICE_STEP)
    if direction == 'LONG':
        side = 'BUY'
        position_side = 'LONG'
    elif direction == 'SHORT':
        side = 'SELL'
        position_side = 'SHORT'
    else:
        raise ValueError('unsupported demo direction')
    if entry_quantity <= 0:
        raise ValueError('demo entry quantity must be positive')
    payload = {'symbol': R36F14_DEMO_SYMBOL, 'side': side, 'positionSide': position_side, 'type': 'MARKET', 'quantity': decimal_to_string(entry_quantity), 'newClientOrderId': writer_client_id(direction, 'D14'), 'tpTriggerPrice': decimal_to_string(tp1_price), 'slTriggerPrice': decimal_to_string(stop_price), 'TpWorkingType': 'MARK_PRICE', 'SlWorkingType': 'MARK_PRICE'}
    full_tp_plan = {'tp1': tp_snapshot.get('tp1'), 'tp2': tp_snapshot.get('tp2'), 'tp3': tp_snapshot.get('tp3'), 'allocation_percent': {'tp1': decimal_to_string(TP1_ALLOCATION_PERCENT), 'tp2': decimal_to_string(TP2_ALLOCATION_PERCENT), 'tp3': decimal_to_string(TP3_ALLOCATION_PERCENT)}, 'tp3_trailing_distance_percent': decimal_to_string(TP3_TRAILING_DISTANCE_PERCENT), 'preserved_internally': True, 'demo_api_multi_tp_not_assumed': True}
    return {'stage': STAGE, 'endpoint': R36F14_DEMO_ORDER_ENDPOINT, 'method': 'POST', 'payload': payload, 'full_tp_plan': full_tp_plan, 'submitted': False, 'demo_post_transport_enabled': R36F14_DEMO_POST_TRANSPORT_ENABLED, 'demo_order_submission_enabled': R36F14_DEMO_ORDER_SUBMISSION_ENABLED, 'first_demo_order_allowed': R36F14_FIRST_DEMO_ORDER_ALLOWED, 'real_order_execution': REAL_ORDER_EXECUTION, 'integrity_sha256': sha256_text(canonical_json(payload))}

def validate_r36f14_demo_order_preview(preview, direction, entry_price):
    if not preview:
        return {'all_valid': False, 'reason': 'DEMO_PREVIEW_MISSING'}
    payload = preview.get('payload', {})
    direction = str(direction).upper()
    entry_price = D(entry_price)
    required = {'symbol', 'side', 'positionSide', 'type', 'quantity', 'newClientOrderId', 'tpTriggerPrice', 'slTriggerPrice', 'TpWorkingType', 'SlWorkingType'}
    client_id = str(payload.get('newClientOrderId', ''))
    qty = D(payload.get('quantity', '0'))
    tp = D(payload.get('tpTriggerPrice', '0'))
    sl = D(payload.get('slTriggerPrice', '0'))
    direction_ok = direction == 'LONG' and payload.get('side') == 'BUY' and (payload.get('positionSide') == 'LONG') or (direction == 'SHORT' and payload.get('side') == 'SELL' and (payload.get('positionSide') == 'SHORT'))
    price_direction_ok = direction == 'LONG' and tp > entry_price and (sl < entry_price) or (direction == 'SHORT' and tp < entry_price and (sl > entry_price))
    checks = {'documented_endpoint': preview.get('endpoint') == R36F14_DEMO_ORDER_ENDPOINT, 'post_preview_only': preview.get('method') == 'POST' and preview.get('submitted') is False, 'required_fields_present': required.issubset(set(payload.keys())), 'demo_symbol_exact': payload.get('symbol') == R36F14_DEMO_SYMBOL, 'market_order': payload.get('type') == 'MARKET', 'direction_mapping': direction_ok, 'quantity_positive': qty > 0, 'client_id_valid_length': 1 <= len(client_id) <= 36, 'tp_sl_direction_valid': price_direction_ok, 'working_types_mark_price': payload.get('TpWorkingType') == 'MARK_PRICE' and payload.get('SlWorkingType') == 'MARK_PRICE', 'demo_transport_disabled': R36F14_DEMO_POST_TRANSPORT_ENABLED is False, 'demo_submission_disabled': R36F14_DEMO_ORDER_SUBMISSION_ENABLED is False, 'first_demo_order_disabled': R36F14_FIRST_DEMO_ORDER_ALLOWED is False, 'real_execution_disabled': REAL_ORDER_EXECUTION is False}
    checks['all_valid'] = all(checks.values())
    return {'checks': checks, 'all_valid': checks['all_valid']}

def synthetic_r36f14_demo_integration_tests():
    synthetic_tp = {'tp_approval': {'approved': True}, 'tp1': '80400.0', 'tp2': '80800.0', 'tp3': 'TRAILING_RUNNER'}
    preview = build_r36f14_demo_order_preview('LONG', Decimal('0.0004'), synthetic_tp, Decimal('79600.0'))
    validation = validate_r36f14_demo_order_preview(preview, 'LONG', Decimal('80000.0'))
    for name, result in validation['checks'].items():
        if name == 'all_valid':
            continue
        check('R36F14_SYNTHETIC_DEMO_' + name.upper(), result)
    check('R36F14_SYNTHETIC_DEMO_INTEGRATION_VALID', validation['all_valid'])
    check('R36F14_SYNTHETIC_DEMO_POST_NOT_SENT', preview['submitted'] is False)
    return {'preview': preview, 'validation': validation}

def build_writer_request_preview(direction, entry_price, quantity, tp_snapshot):
    if not tp_snapshot or not tp_snapshot.get('tp_approval', {}).get('approved'):
        raise ValueError('writer requires an approved complete TP snapshot')
    entry_price = quantize_down(entry_price, PRICE_STEP)
    entry_quantity, tp1_qty, tp2_qty, tp3_qty = writer_quantities(quantity)
    quantity_checks = validate_writer_quantities(entry_quantity, tp1_qty, tp2_qty, tp3_qty)
    entry_side, position_side = writer_entry_side(direction)
    close_side, close_position_side = writer_close_side(direction)
    tp1_price = quantize_down(D(tp_snapshot['tp1']), PRICE_STEP)
    tp2_price = quantize_down(D(tp_snapshot['tp2']), PRICE_STEP)
    if direction == 'LONG':
        if not (tp1_price > entry_price and tp2_price > tp1_price):
            raise ValueError('LONG TP ordering invalid')
    elif direction == 'SHORT':
        if not (tp1_price < entry_price and tp2_price < tp1_price):
            raise ValueError('SHORT TP ordering invalid')
    else:
        raise ValueError('Invalid writer direction')
    entry_leg = {'endpoint': WRITER_ENDPOINT_ENTRY, 'method': 'POST', 'symbol': SYMBOL, 'side': entry_side, 'positionSide': position_side, 'type': 'MARKET', 'quantity': decimal_to_string(entry_quantity), 'newClientOrderId': writer_client_id(direction, 'ENTRY'), 'reduceOnly': False}
    tp1_leg = {'endpoint': WRITER_ENDPOINT_TPSL, 'method': 'POST', 'symbol': SYMBOL, 'positionSide': close_position_side, 'planType': 'TAKE_PROFIT', 'triggerPrice': decimal_to_string(tp1_price), 'executePrice': decimal_to_string(tp1_price), 'quantity': decimal_to_string(tp1_qty), 'triggerPriceType': 'MARK_PRICE', 'clientAlgoId': writer_client_id(direction, 'TP1'), 'reduceOnly': True}
    tp2_leg = {'endpoint': WRITER_ENDPOINT_TPSL, 'method': 'POST', 'symbol': SYMBOL, 'positionSide': close_position_side, 'planType': 'TAKE_PROFIT', 'triggerPrice': decimal_to_string(tp2_price), 'executePrice': decimal_to_string(tp2_price), 'quantity': decimal_to_string(tp2_qty), 'triggerPriceType': 'MARK_PRICE', 'clientAlgoId': writer_client_id(direction, 'TP2'), 'reduceOnly': True}
    tp3_leg = {'endpoint': WRITER_ENDPOINT_TRAILING, 'method': 'POST', 'symbol': SYMBOL, 'side': close_side, 'positionSide': close_position_side, 'type': 'TRAILING_MARKET', 'quantity': decimal_to_string(tp3_qty), 'callbackRate': decimal_to_string(TP3_TRAILING_DISTANCE_PERCENT), 'workingType': 'MARK_PRICE', 'clientAlgoId': writer_client_id(direction, 'TP3'), 'reduceOnly': True}
    legs = {'entry': entry_leg, 'tp1': tp1_leg, 'tp2': tp2_leg, 'tp3': tp3_leg}
    integrity_hash = sha256_text(canonical_json(legs))
    return {'stage': STAGE, 'symbol': SYMBOL, 'direction': direction, 'entry_price': decimal_to_string(entry_price), 'entry_quantity': decimal_to_string(entry_quantity), 'tp1_quantity': decimal_to_string(tp1_qty), 'tp2_quantity': decimal_to_string(tp2_qty), 'tp3_quantity': decimal_to_string(tp3_qty), 'allocation_percent': {'tp1': decimal_to_string(select_tp_allocation(entry_quantity)['tp1_percent']), 'tp2': decimal_to_string(select_tp_allocation(entry_quantity)['tp2_percent']), 'tp3': decimal_to_string(select_tp_allocation(entry_quantity)['tp3_percent'])}, 'allocation_label': select_tp_allocation(entry_quantity)['label'], 'allocation_adjusted': select_tp_allocation(entry_quantity)['adjusted'], 'quantity_validation': quantity_checks, 'tp_approval': tp_snapshot['tp_approval'], 'tp1': tp_snapshot['tp1'], 'tp2': tp_snapshot['tp2'], 'tp3': tp_snapshot['tp3'], 'legs': legs, 'primary_tp_immutable': True, 'submitted': False, 'transport_enabled': EXCHANGE_MUTATION_TRANSPORT_ENABLED, 'integrity_sha256': integrity_hash}

def validate_weex_v3_writer_shapes(writer_preview):
    """
    Validate only documented request fields needed
    by the frozen writer.
    """
    if not writer_preview:
        return {'all_valid': False, 'reason': 'WRITER_PREVIEW_MISSING'}
    legs = writer_preview.get('legs', {})
    entry = legs.get('entry', {})
    tp1 = legs.get('tp1', {})
    tp2 = legs.get('tp2', {})
    tp3 = legs.get('tp3', {})
    entry_required = {'endpoint', 'method', 'symbol', 'side', 'positionSide', 'type', 'quantity', 'newClientOrderId', 'reduceOnly'}
    tpsl_required = {'endpoint', 'method', 'symbol', 'positionSide', 'planType', 'triggerPrice', 'executePrice', 'quantity', 'triggerPriceType', 'clientAlgoId', 'reduceOnly'}
    trailing_required = {'endpoint', 'method', 'symbol', 'side', 'positionSide', 'type', 'quantity', 'callbackRate', 'workingType', 'clientAlgoId', 'reduceOnly'}
    checks = {'entry_endpoint': entry.get('endpoint') == '/capi/v3/order', 'entry_method': entry.get('method') == 'POST', 'entry_required_fields': entry_required.issubset(entry.keys()), 'entry_market_type': entry.get('type') == 'MARKET', 'entry_reduce_only_false': entry.get('reduceOnly') is False, 'tp1_endpoint': tp1.get('endpoint') == '/capi/v3/placeTpSlOrder', 'tp2_endpoint': tp2.get('endpoint') == '/capi/v3/placeTpSlOrder', 'tp1_plan_type': tp1.get('planType') == 'TAKE_PROFIT', 'tp2_plan_type': tp2.get('planType') == 'TAKE_PROFIT', 'tp1_required_fields': tpsl_required.issubset(tp1.keys()), 'tp2_required_fields': tpsl_required.issubset(tp2.keys()), 'tp1_no_legacy_side': 'side' not in tp1, 'tp2_no_legacy_side': 'side' not in tp2, 'tp1_no_legacy_type': 'type' not in tp1, 'tp2_no_legacy_type': 'type' not in tp2, 'trailing_endpoint': tp3.get('endpoint') == '/capi/v3/algoOrder', 'trailing_type': tp3.get('type') == 'TRAILING_MARKET', 'trailing_required_fields': trailing_required.issubset(tp3.keys())}
    checks['all_valid'] = all(checks.values())
    return checks

def parse_canary_stop_price(text):
    if not text:
        return None
    value = D(text)
    if value <= Decimal('0'):
        raise ValueError('R36F12_CANARY_STOP_PRICE must be positive')
    return quantize_down(value, PRICE_STEP)

def validate_canary_stop(direction, entry_price, stop_price):
    entry_price = D(entry_price)
    stop_price = D(stop_price)
    if direction == 'LONG':
        return stop_price < entry_price
    if direction == 'SHORT':
        return stop_price > entry_price
    return False

def calculate_r36f13_protective_stop(direction, entry_price):
    """
    Calculate the mandatory preview protective stop;
    never submits it.
    """
    entry_price = D(entry_price)
    distance = R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT / Decimal('100')
    if direction == 'LONG':
        raw_stop = entry_price * (Decimal('1') - distance)
        stop_price = quantize_down(raw_stop, PRICE_STEP)
    elif direction == 'SHORT':
        raw_stop = entry_price * (Decimal('1') + distance)
        stop_price = quantize_down(raw_stop, PRICE_STEP)
        if stop_price <= entry_price:
            stop_price = quantize_down(entry_price, PRICE_STEP) + PRICE_STEP
    else:
        raise ValueError('Invalid protective-stop direction')
    return stop_price

def validate_r36f13_protective_stop(direction, entry_price, stop_price, tp1_price, tp2_price):
    entry_price = D(entry_price)
    stop_price = D(stop_price)
    tp1_price = D(tp1_price)
    tp2_price = D(tp2_price)
    on_step = stop_price % PRICE_STEP == 0
    positive = stop_price > 0
    if direction == 'LONG':
        correct_side = stop_price < entry_price
        separated_from_tp = stop_price < entry_price < tp1_price < tp2_price
    elif direction == 'SHORT':
        correct_side = stop_price > entry_price
        separated_from_tp = stop_price > entry_price > tp1_price > tp2_price
    else:
        correct_side = False
        separated_from_tp = False
    checks = {'configured_or_calculated': True, 'positive': positive, 'correct_side_of_entry': correct_side, 'price_step_normalized': on_step, 'does_not_cross_entry_or_tp': separated_from_tp}
    checks['all_valid'] = all(checks.values())
    return checks

def calculate_r36f131_stop_distance_percent(entry_price, stop_price):
    entry_price = D(entry_price)
    stop_price = D(stop_price)
    if entry_price <= 0:
        raise ValueError('entry_price must be positive')
    return abs(stop_price - entry_price) / entry_price * Decimal('100')

def validate_r36f131_stop_risk_envelope(direction, entry_price, stop_price, leverage):
    entry_price = D(entry_price)
    stop_price = D(stop_price)
    leverage = D(leverage)
    if leverage <= 0:
        raise ValueError('leverage must be positive')
    distance_percent = calculate_r36f131_stop_distance_percent(entry_price, stop_price)
    leverage_reference_percent = Decimal('100') / leverage
    minimum_step_distance_percent = PRICE_STEP / entry_price * Decimal('100')
    checks = {'direction_valid': direction in {'LONG', 'SHORT'}, 'distance_positive': distance_percent > 0, 'at_least_one_price_step': abs(stop_price - entry_price) >= PRICE_STEP, 'within_configured_maximum': distance_percent <= R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT, 'inside_leverage_reference': distance_percent < leverage_reference_percent}
    checks['all_valid'] = all(checks.values())
    return {'distance_percent': decimal_to_string(distance_percent), 'configured_maximum_percent': decimal_to_string(R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT), 'leverage_reference_percent': decimal_to_string(leverage_reference_percent), 'minimum_step_distance_percent': decimal_to_string(minimum_step_distance_percent), 'leverage': decimal_to_string(leverage), 'reference_is_not_liquidation_price': True, 'checks': checks, 'all_valid': checks['all_valid']}

def validate_r36f132_stop_loss_budget(entry_price, stop_price, entry_quantity, available_balance, leverage):
    entry_price = D(entry_price)
    stop_price = D(stop_price)
    entry_quantity = D(entry_quantity)
    available_balance = D(available_balance)
    leverage = D(leverage)
    if entry_price <= 0:
        raise ValueError('entry_price must be positive')
    if entry_quantity <= 0:
        raise ValueError('entry_quantity must be positive')
    if available_balance <= 0:
        raise ValueError('available_balance must be positive')
    if leverage <= 0:
        raise ValueError('leverage must be positive')
    price_distance = abs(entry_price - stop_price)
    expected_loss = price_distance * entry_quantity
    expected_loss_percent = expected_loss / available_balance * Decimal('100')
    account_loss_budget = available_balance * R36F132_MAX_ACCOUNT_LOSS_PERCENT / Decimal('100')
    isolated_entry_margin = entry_price * entry_quantity / leverage
    checks = {'price_distance_positive': price_distance > 0, 'expected_loss_positive': expected_loss > 0, 'within_account_loss_budget': expected_loss <= account_loss_budget, 'within_isolated_entry_margin_budget': expected_loss <= isolated_entry_margin}
    checks['all_valid'] = all(checks.values())
    return {'entry_price': decimal_to_string(entry_price), 'stop_price': decimal_to_string(stop_price), 'entry_quantity': decimal_to_string(entry_quantity), 'available_balance': decimal_to_string(available_balance), 'leverage': decimal_to_string(leverage), 'price_distance': decimal_to_string(price_distance), 'expected_loss_usdt': decimal_to_string(expected_loss), 'expected_loss_percent_of_available_balance': decimal_to_string(expected_loss_percent), 'configured_max_account_loss_percent': decimal_to_string(R36F132_MAX_ACCOUNT_LOSS_PERCENT), 'account_loss_budget_usdt': decimal_to_string(account_loss_budget), 'isolated_entry_margin_usdt': decimal_to_string(isolated_entry_margin), 'checks': checks, 'all_valid': checks['all_valid']}

def apply_r36f132_stop_loss_budget_authorization_gate(command_preview, loss_budget):
    preview = dict(command_preview or {})
    preview['r36f132_stop_loss_budget_required'] = True
    preview['r36f132_stop_loss_budget_valid'] = bool(loss_budget and loss_budget.get('all_valid'))
    if not preview.get('authorized_preview'):
        return preview
    if not loss_budget or not loss_budget.get('all_valid'):
        preview['authorized_preview'] = False
        preview['reason'] = 'PROTECTIVE_STOP_LOSS_BUDGET_NOT_READY'
        preview['exchange_order_sent'] = False
        return preview
    preview['reason'] = 'COMMAND_EMA_TP_STOP_RISK_ENVELOPE_AND_LOSS_BUDGET_AGREE'
    preview['exchange_order_sent'] = False
    return preview

def synthetic_r36f132_stop_loss_budget_tests():
    passing = validate_r36f132_stop_loss_budget(Decimal('80000'), Decimal('79600'), Decimal('0.0004'), Decimal('7.19'), Decimal('100'))
    check('R36F132_SYNTHETIC_STOP_LOSS_BUDGET_APPROVED', passing['all_valid'] is True)
    check('R36F132_SYNTHETIC_EXPECTED_LOSS_016_USDT', passing['expected_loss_usdt'] == '0.16')
    check('R36F132_SYNTHETIC_WITHIN_ACCOUNT_LOSS_BUDGET', passing['checks']['within_account_loss_budget'] is True)
    check('R36F132_SYNTHETIC_WITHIN_ENTRY_MARGIN_BUDGET', passing['checks']['within_isolated_entry_margin_budget'] is True)
    failing = validate_r36f132_stop_loss_budget(Decimal('80000'), Decimal('79200'), Decimal('0.0004'), Decimal('7.19'), Decimal('100'))
    check('R36F132_SYNTHETIC_EXCESSIVE_ACCOUNT_LOSS_REJECTED', failing['checks']['within_account_loss_budget'] is False)
    authorized = apply_r36f132_stop_loss_budget_authorization_gate({'authorized_preview': True, 'exchange_order_sent': False}, passing)
    blocked = apply_r36f132_stop_loss_budget_authorization_gate({'authorized_preview': True, 'exchange_order_sent': False}, failing)
    check('R36F132_SYNTHETIC_AUTHORIZATION_GATE_APPROVES_SAFE_LOSS', authorized['authorized_preview'] is True)
    check('R36F132_SYNTHETIC_AUTHORIZATION_GATE_BLOCKS_EXCESSIVE_LOSS', blocked['authorized_preview'] is False)
    check('R36F132_SYNTHETIC_GATE_NEVER_SENDS_ORDER', authorized.get('exchange_order_sent') is False and blocked.get('exchange_order_sent') is False)
    return True

def apply_r36f131_risk_envelope_authorization_gate(command_preview, envelope):
    preview = dict(command_preview or {})
    preview['r36f131_stop_risk_envelope_required'] = True
    preview['r36f131_stop_risk_envelope_valid'] = bool(envelope and envelope.get('all_valid'))
    if not preview.get('authorized_preview'):
        return preview
    if not envelope or not envelope.get('all_valid'):
        preview['authorized_preview'] = False
        preview['reason'] = 'PROTECTIVE_STOP_RISK_ENVELOPE_NOT_READY'
        preview['exchange_order_sent'] = False
        return preview
    preview['reason'] = 'COMMAND_EMA_TP_STOP_AND_RISK_ENVELOPE_AGREE'
    preview['exchange_order_sent'] = False
    return preview

def apply_r36f13_stop_authorization_gate(command_preview, stop_checks):
    preview = dict(command_preview or {})
    if not preview.get('authorized_preview'):
        preview['r36f13_protective_stop_required'] = True
        preview['r36f13_protective_stop_valid'] = bool(stop_checks and stop_checks.get('all_valid'))
        return preview
    if not stop_checks or not stop_checks.get('all_valid'):
        preview['authorized_preview'] = False
        preview['reason'] = 'PROTECTIVE_STOP_NOT_READY'
        preview['r36f13_protective_stop_required'] = True
        preview['r36f13_protective_stop_valid'] = False
        preview['exchange_order_sent'] = False
        return preview
    preview['reason'] = 'COMMAND_EMA_TP_AND_PROTECTIVE_STOP_AGREE'
    preview['r36f13_protective_stop_required'] = True
    preview['r36f13_protective_stop_valid'] = True
    preview['exchange_order_sent'] = False
    return preview

def unresolved_canary_journal(journal):
    if not journal:
        return False
    return str(journal.get('status', '')).upper() in {'PREPARED', 'DISPATCHING', 'SUBMITTED', 'AMBIGUOUS'}

def build_protected_canary_preview(writer_preview, stop_price, explicit_arm_requested, journal, flat_position):
    """
    Build the R36F.12-ready canary package without sending it.
    """
    if not writer_preview:
        raise ValueError('writer preview required')
    direction = writer_preview['direction']
    entry_price = D(writer_preview['entry_price'])
    entry_quantity = D(writer_preview['entry_quantity'])
    stop_price = D(stop_price)
    schema_checks = validate_weex_v3_writer_shapes(writer_preview)
    stop_valid = validate_canary_stop(direction, entry_price, stop_price)
    quantity_capped = entry_quantity <= CANARY_MAX_ENTRY_QUANTITY
    journal_clear = not unresolved_canary_journal(journal)
    protected_entry = dict(writer_preview['legs']['entry'])
    protected_entry['slTriggerPrice'] = decimal_to_string(stop_price)
    protected_entry['SlWorkingType'] = CANARY_STOP_WORKING_TYPE
    ready = bool(schema_checks.get('all_valid') and stop_valid and quantity_capped and explicit_arm_requested and journal_clear and flat_position and writer_preview.get('quantity_validation', {}).get('all_valid'))
    return {'stage': STAGE, 'status': 'READY_FOR_R36F12' if ready else 'BLOCKED', 'ready_for_r36f12': ready, 'direction': direction, 'entry_quantity': decimal_to_string(entry_quantity), 'canary_max_entry_quantity': decimal_to_string(CANARY_MAX_ENTRY_QUANTITY), 'quantity_capped': quantity_capped, 'stop_price': decimal_to_string(stop_price), 'stop_valid': stop_valid, 'stop_working_type': CANARY_STOP_WORKING_TYPE, 'explicit_arm_requested': bool(explicit_arm_requested), 'journal_clear': journal_clear, 'flat_position': bool(flat_position), 'writer_schema_valid': bool(schema_checks.get('all_valid')), 'writer_schema_checks': schema_checks, 'protected_entry_request': protected_entry, 'tp1_request': writer_preview['legs']['tp1'], 'tp2_request': writer_preview['legs']['tp2'], 'tp3_request': writer_preview['legs']['tp3'], 'submitted': False, 'exchange_request_sent': False, 'r36f12_transport_hard_disabled': True}

def synthetic_r36f12_writer_safety_tests():
    synthetic_entry = Decimal('80000')
    synthetic_rows = [[0, '80000', '80200', '79900', '80100', '1'], [1, '80100', '80300', '80000', '80200', '1'], [2, '80200', '80400', '80100', '80300', '1'], [3, '80300', '80500', '80200', '80400', '1'], [4, '80400', '80600', '80300', '80500', '1']]
    tp_snapshot = {'tp_approval': {'approved': True, 'status': 'APPROVED', 'reason': 'SYNTHETIC'}, 'tp1': '80100', 'tp2': '80300', 'tp3': 'TRAILING'}
    preview = build_writer_request_preview('LONG', synthetic_entry, Decimal('0.0004'), tp_snapshot)
    shape = validate_weex_v3_writer_shapes(preview)
    check('R36F12_WEEX_V3_WRITER_SHAPES', shape['all_valid'])
    clear = build_protected_canary_preview(preview, Decimal('79600'), True, {}, True)
    check('R36F12_SYNTHETIC_PROTECTED_CANARY_READY', clear['ready_for_r36f12'] is True)
    check('R36F12_SYNTHETIC_CANARY_QTY_CAP_00004', clear['entry_quantity'] == '0.0004')
    check('R36F12_SYNTHETIC_STOP_ATTACHED', clear['protected_entry_request'].get('slTriggerPrice') == '79600')
    ambiguous = build_protected_canary_preview(preview, Decimal('79600'), True, {'status': 'AMBIGUOUS'}, True)
    check('R36F12_AMBIGUOUS_JOURNAL_BLOCKS', ambiguous['ready_for_r36f12'] is False)
    unarmed = build_protected_canary_preview(preview, Decimal('79600'), False, {}, True)
    check('R36F12_EXPLICIT_ARM_REQUIRED', unarmed['ready_for_r36f12'] is False)
    wrong_stop = build_protected_canary_preview(preview, Decimal('80400'), True, {}, True)
    check('R36F12_WRONG_SIDE_STOP_BLOCKS', wrong_stop['ready_for_r36f12'] is False)
    return True

def synthetic_writer_quantity_tests():
    adjusted = evaluate_writer_quantity_feasibility(Decimal('0.0004'))
    check('ADJUSTABLE_00004_APPROVED', adjusted['feasible'] is True)
    check('ADJUSTABLE_00004_SELECTED_25_25_50', adjusted['selected_allocation'] == '25/25/50')
    check('ADJUSTABLE_00004_ADJUSTED_TRUE', adjusted['allocation_adjusted'] is True)
    check('ADJUSTABLE_00004_TP1', adjusted['tp1_quantity'] == '0.0001')
    check('ADJUSTABLE_00004_TP2', adjusted['tp2_quantity'] == '0.0001')
    check('ADJUSTABLE_00004_TP3', adjusted['tp3_quantity'] == '0.0002')
    preferred = evaluate_writer_quantity_feasibility(Decimal('0.0005'))
    check('PREFERRED_00005_APPROVED', preferred['feasible'] is True)
    check('PREFERRED_00005_RETAINS_20_20_60', preferred['selected_allocation'] == '20/20/60')
    check('PREFERRED_00005_ADJUSTED_FALSE', preferred['allocation_adjusted'] is False)
    check('PREFERRED_00005_TP1', preferred['tp1_quantity'] == '0.0001')
    check('PREFERRED_00005_TP2', preferred['tp2_quantity'] == '0.0001')
    check('PREFERRED_00005_TP3', preferred['tp3_quantity'] == '0.0003')
    smaller = evaluate_writer_quantity_feasibility(Decimal('0.0003'))
    check('ADJUSTABLE_00003_REJECTED', smaller['feasible'] is False)
    check('ADJUSTABLE_MINIMUM_ENTRY_00004', adjusted['minimum_required_entry_quantity'] == '0.0004')
    return True

def synthetic_balance_readiness_tests():
    approved = evaluate_strict_tp_balance_readiness(Decimal('7.19'), Decimal('80000'), Decimal('100'))
    check('ADJUSTABLE_BALANCE_READINESS_7_19_APPROVED', approved['eligible'] is True)
    check('ADJUSTABLE_BALANCE_READINESS_7_19_PLANNED_00004', approved['planned_entry_quantity'] == '0.0004')
    check('ADJUSTABLE_BALANCE_READINESS_7_19_SELECTED_25_25_50', approved['selected_allocation'] == '25/25/50')
    check('ADJUSTABLE_BALANCE_READINESS_REQUIRED_BALANCE_6_40', approved['required_available_balance'] == '6.4')
    preferred = evaluate_strict_tp_balance_readiness(Decimal('8'), Decimal('80000'), Decimal('100'))
    check('PREFERRED_BALANCE_READINESS_8_00_APPROVED', preferred['eligible'] is True)
    check('PREFERRED_BALANCE_READINESS_8_00_PLANNED_00005', preferred['planned_entry_quantity'] == '0.0005')
    check('PREFERRED_BALANCE_READINESS_8_00_RETAINS_20_20_60', preferred['selected_allocation'] == '20/20/60')
    return True
