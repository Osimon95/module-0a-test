
"""
R36F.15.2 - SELECTED TP SNAPSHOT SCOPE FIX FOR CONTROLLED WEEX DEMO

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5.4/R36F.8 safety baseline
    while correcting ONLY the remaining pre-live readiness classification:

        A market may have a valid historical TP set but still be unable to
        represent the frozen 20% / 20% / 60% TP quantity split because the
        planned entry quantity is below the strict exchange-representable
        minimum. That condition is normal TRADE INELIGIBILITY, not a writer
        capability failure and not a FINAL_BLOCKER.

R36F.15.2 CHANGE:

    1. Preserve the complete R36F.15.1 continuous fresh-market reevaluation pipeline.
    2. Fix ONLY the stale selected_tp_snapshot reference in the eligible writer/demo path.
    3. Use the already-selected direction-specific selected_snapshot consistently for demo preview construction.
    4. Add an explicit blocker if the eligible writer/demo construction pipeline raises an unexpected exception.
    5. Preserve normal TRADE_NOT_ELIGIBLE states as non-final-blocking market conditions.
    6. Preserve EMA, two-cluster TP, 20/20/60 quantity allocation, protective stop, stop-risk envelope, stop-loss budget, backup configuration, exactly-once demo journal, and all real-money firebreaks unchanged.

R36F.15.1 CHANGE:

    1. Keep the full R36F.15 startup validation and demo execution chain unchanged.
    2. After each runtime interval, rerun the complete fresh market/account pipeline.
    3. Refetch mark price and up to the existing 1000 one-minute historical candles.
    4. Recalculate EMA19/EMA50/EMA200 and LONG/SHORT historical TP clusters.
    5. Revalidate the configured Telegram command against the fresh EMA direction
       and fresh direction-specific TP market eligibility.
    6. Rebuild quantity, protective-stop, stop-risk-envelope and stop-loss-budget
       authorization previews from the fresh market snapshot.
    7. Permit WEEX demo transport only through the existing R36F.15 arm and full
       authorization chain.
    8. Preserve the durable demo dispatch journal so one completed first demo order
       cannot be submitted again on later reevaluation cycles or restart.
    9. Keep every production / real-money mutation switch hard-disabled.
   10. Make the runtime interval configurable with R36F151_REEVALUATION_SECONDS,
       default 60 seconds and minimum 15 seconds.

R36F.11 CHANGE:

    1. Preserve the R36F.8 WEEX read-only position route and GET signing.
    2. Preserve historical two-cluster TP approval unchanged.
    3. Preserve TP price policy unchanged:
           TP1 = 20% adjustable progress toward Cluster 1
           TP2 = 50% adjustable progress toward Cluster 2
           TP3 = 60% trailing runner
    4. Preserve TP quantity allocation unchanged:
           TP1 = 20%
           TP2 = 20%
           TP3 = 60%
    5. Preserve strict minimum entry quantity discovery unchanged.
    6. Add explicit quantity/balance readiness calculation before writer
       construction:
           planned_entry_qty
           minimum_strict_tp_entry_qty
           required_margin_for_minimum_qty
           required_available_balance
           available_balance_shortfall
           quantity_feasible
           trade_readiness_status/reason
    7. Classify insufficient balance/quantity as TRADE_NOT_ELIGIBLE:
           INSUFFICIENT_BALANCE_FOR_STRICT_20_20_60
       rather than as a system/final-blocker failure.
    8. Writer construction remains blocked unless readiness is ELIGIBLE.
    9. Do NOT promote TP legs or redistribute quantity.
   10. Keep submitted=False and ALL exchange mutation disabled.

IMPORTANT:

    This version MAY send exactly one WEEX paper-trading POST to /capi/v3/sim/order when the explicit R36F15 arm phrase and the complete frozen authorization chain both pass.

    Production /capi/v3/order remains unreachable; REAL_ORDER_EXECUTION and all production mutation switches remain False.

TP POLICY:

    A complete historical TP1/TP2 set requires TWO OR MORE valid
    historical clusters.

    LONG:
        Cluster 1 = first valid historical-high resistance cluster
        Cluster 2 = second valid historical-high resistance cluster

        TP1 = 20% adjustable progress from entry toward Cluster 1
        TP2 = 50% adjustable progress from entry toward Cluster 2
        TP3 = 60% trailing runner

    SHORT:
        Cluster 1 = first valid historical-low support cluster
        Cluster 2 = second valid historical-low support cluster

        TP1 = 20% adjustable progress from entry toward Cluster 1
        TP2 = 50% adjustable progress from entry toward Cluster 2
        TP3 = 60% trailing runner

    Two-cluster approval applies to the complete TP1 + TP2 set.

    TP3 does not fabricate a missing historical TP1 or TP2.

EXECUTION FIREBREAK:

    REAL_ORDER_EXECUTION = False
    DEMO_ORDER_EXECUTION = False
    EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
    ORDER_SUBMISSION_ENABLED = False
    LEVERAGE_MUTATION_ENABLED = False
    MARGIN_MODE_MUTATION_ENABLED = False
    POSITION_MUTATION_ENABLED = False
    FIRST_REAL_ORDER_ALLOWED = False
"""
import asyncio
import aiohttp
import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

STAGE = 'R36F.15.4.1'
PURPOSE = 'SELECTED TP SNAPSHOT SCOPE FIX: preserve the complete R36F.15.1 continuous EMA19/EMA50/EMA200 + Telegram + two-cluster TP + quantity/readiness + mandatory protective-stop + stop-risk-envelope + stop-loss-budget + exactly-once WEEX demo dispatch chain, while fixing only the stale selected_tp_snapshot reference so the already-selected direction-specific TP snapshot reaches demo preview construction correctly. Production /capi/v3/order and every real-money mutation remain hard-disabled.'

API_BASE_URL = 'https://api-contract.weex.com'
SYMBOL = 'BTCUSDT'
PUBLIC_TICKER_SYMBOL = 'cmt_btcusdt'
KLINE_INTERVAL = '1m'
HISTORICAL_LIMIT = 250
MAX_HISTORICAL_PAGES = 4
R36F151_REEVALUATION_SECONDS = max(
    15,
    int(os.getenv('R36F151_REEVALUATION_SECONDS', '60'))
)

PRICE_STEP = Decimal('0.1')
QUANTITY_STEP = Decimal('0.0001')
MIN_QUANTITY = Decimal('0.0001')
ENTRY_MARGIN_PERCENT = Decimal('5')
LEVERAGE_LONG = Decimal('100')
LEVERAGE_SHORT = Decimal('100')
MARGIN_MODE = 'ISOLATED'
PYRAMID_ADD_PERCENT = Decimal('5')
MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3
BACKUP_MARGIN_PERCENT = Decimal('5')
BACKUP_BUFFER_PERCENT = Decimal('0.3')
MAX_FUND_EXPOSURE_PERCENT = Decimal('35')
SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300
ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True

EMA_FAST = 19
EMA_MID = 50
EMA_SLOW = 200
EMA_CONFIRMATION_CANDLES = 1
MIN_EMA_19_50_SEPARATION_PERCENT = Decimal('0.01')

TELEGRAM_BOT_TOKEN = os.getenv(
    'TELEGRAM_BOT_TOKEN',
    ''
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    'TELEGRAM_CHAT_ID',
    ''
).strip()

R36F12_TELEGRAM_ALERTS_ENABLED = (
    os.getenv(
        'R36F12_TELEGRAM_ALERTS_ENABLED',
        'false'
    ).strip().lower()
    in {'1', 'true', 'yes', 'on'}
)

R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED = (
    os.getenv(
        'R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED',
        'false'
    ).strip().lower()
    in {'1', 'true', 'yes', 'on'}
)

TELEGRAM_BUY_COMMAND = 'BUY BTC NOW'
TELEGRAM_SELL_COMMAND = 'SELL BTC NOW'

TP1_PROFIT_MARGIN_PERCENT = Decimal('20')
TP2_PROFIT_MARGIN_PERCENT = Decimal('50')
TP3_PROFIT_MARGIN_PERCENT = Decimal('60')

TP1_ALLOCATION_PERCENT = Decimal('20')
TP2_ALLOCATION_PERCENT = Decimal('20')
TP3_ALLOCATION_PERCENT = Decimal('60')

TP3_TRAILING_DISTANCE_PERCENT = Decimal('0.20')
CLUSTER_TOLERANCE_PERCENT = Decimal('0.20')
MIN_CLUSTER_TOUCHES = 2
REQUIRED_TP_CLUSTERS = 2

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
FIRST_REAL_ORDER_ALLOWED = False

CANARY_MAX_ENTRY_QUANTITY = Decimal('0.0004')
CANARY_ARM_PHRASE = 'ARM_FIRST_LIVE_CANARY'
CANARY_ARM_REQUESTED = (
    os.getenv(
        'R36F12_LIVE_CANARY_ARM',
        ''
    ).strip()
    == CANARY_ARM_PHRASE
)

CANARY_STOP_PRICE_TEXT = os.getenv(
    'R36F12_CANARY_STOP_PRICE',
    ''
).strip()

CANARY_STOP_WORKING_TYPE = 'MARK_PRICE'

R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(
    os.getenv(
        'R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT',
        '0.50'
    )
)

if R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError(
        'R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive'
    )

R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(
    os.getenv(
        'R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT',
        '0.75'
    )
)

if R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError(
        'R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive'
    )

R36F132_MAX_ACCOUNT_LOSS_PERCENT = Decimal(
    os.getenv(
        'R36F132_MAX_ACCOUNT_LOSS_PERCENT',
        '2.50'
    )
)

if R36F132_MAX_ACCOUNT_LOSS_PERCENT <= 0:
    raise ValueError(
        'R36F132_MAX_ACCOUNT_LOSS_PERCENT must be positive'
    )

R36F14_DEMO_SYMBOL = os.getenv(
    'R36F14_DEMO_SYMBOL',
    'BTCSUSDT'
).strip().upper()

R36F14_DEMO_ASSET = os.getenv(
    'R36F14_DEMO_ASSET',
    'SUSDT'
).strip().upper()

R36F14_DEMO_BALANCE_ENDPOINT = '/capi/v3/sim/balance'
R36F14_DEMO_POSITIONS_ENDPOINT = '/capi/v3/sim/position/allPosition'
R36F14_DEMO_ORDER_HISTORY_ENDPOINT = '/capi/v3/sim/order/history'
R36F14_DEMO_ORDER_ENDPOINT = '/capi/v3/sim/order'

R36F14_DEMO_READS_ENABLED = True
R36F14_DEMO_POST_TRANSPORT_ENABLED = False
R36F14_DEMO_ORDER_SUBMISSION_ENABLED = False
R36F14_FIRST_DEMO_ORDER_ALLOWED = False

R36F15_DEMO_ARM_PHRASE = 'ARM_FIRST_WEEX_DEMO_ORDER'

R36F15_DEMO_ARM_REQUESTED = (
    os.getenv(
        'R36F15_DEMO_ARM',
        ''
    ).strip()
    == R36F15_DEMO_ARM_PHRASE
)

R36F15_DEMO_POST_TRANSPORT_ENABLED = True
R36F15_DEMO_ORDER_SUBMISSION_ENABLED = True
R36F15_FIRST_DEMO_ORDER_ALLOWED = True

R36F15_RECONCILE_DELAY_SECONDS = Decimal(
    os.getenv(
        'R36F15_RECONCILE_DELAY_SECONDS',
        '1.0'
    )
)

R36A_STATE_DIR = '/var/data/r36a_state'
R36C_STATE_DIR = '/var/data/r36c_state'
R36D_STATE_DIR = '/var/data/r36d_state'
R36F_STATE_DIR = '/var/data/r36f_state'

os.makedirs(R36F_STATE_DIR, exist_ok=True)

R36A_DEDUPE_FILE = os.path.join(
    R36A_STATE_DIR,
    'telegram_processed_updates.json'
)

R36A_DECISION_FILE = os.path.join(
    R36A_STATE_DIR,
    'synthetic_decisions.json'
)

R36C_DEDUPE_FILE = os.path.join(
    R36C_STATE_DIR,
    'telegram_processed_updates.json'
)

R36C_DECISION_FILE = os.path.join(
    R36C_STATE_DIR,
    'synthetic_decisions.json'
)

R36D_SNAPSHOT_FILE = os.path.join(
    R36D_STATE_DIR,
    'pre_live_readiness_snapshot.json'
)

R36F_SNAPSHOT_FILE = os.path.join(
    R36F_STATE_DIR,
    'pre_live_readiness_snapshot.json'
)

R36F12_CANARY_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    'first_live_canary_dispatch_journal.json'
)

R36F12_TELEGRAM_SIGNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    'r36f12_ema_telegram_signal_snapshot.json'
)

R36F12_TELEGRAM_COMMAND_FILE = os.path.join(
    R36F_STATE_DIR,
    'r36f12_telegram_command_preview.json'
)

R36F15_DEMO_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    'r36f15_demo_dispatch_journal.json'
)

R36F1541_TELEGRAM_EVENT_STATE_FILE = os.path.join(
    R36F_STATE_DIR,
    'r36f1541_telegram_event_state.json'
)

OLD_R36A_UPDATE_ID = 'R36A_SYNTHETIC_UPDATE_000001'
R36C_UPDATE_ID = 'R36C_SYNTHETIC_UPDATE_000001'

TEST_STATUS = 'NOT_STARTED'
HEARTBEAT_COUNT = 0
DURABLE_EVIDENCE_OK = False
R36A_EVIDENCE_OK = False
R36C_EVIDENCE_OK = False
R36D_EVIDENCE_OK = False
WEEX_READ_ONLY_OK = False
ZERO_WRITE_INVARIANT_OK = False
FINAL_GATE_OK = False
FINAL_BLOCKERS = []

MARK_PRICE = None
AVAILABLE_BALANCE = None
OPEN_POSITIONS = []
WEEX_CONFIG = {}
SHORT_DIAGNOSTICS = {}
LONG_DIAGNOSTICS = {}
LAST_TP_APPROVAL = None
EMA_SIGNAL_SNAPSHOT = {}
TELEGRAM_COMMAND_PREVIEW = {}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def line():
    print(
        '----------------------------------------------------------------------------------------------------',
        flush=True
    )


def log(message):
    print(
        f'{now_iso()} {message}',
        flush=True
    )


def check(name, condition, detail=None):
    if condition:
        log(f'PASS: {name}')
        if detail:
            log(f'      {detail}')
        return True

    log(f'FAIL: {name}')

    if detail:
        log(f'      {detail}')

    FINAL_BLOCKERS.append(name)
    return False


def diagnostic_check(name, condition, detail=None):
    if condition:
        log(f'DIAGNOSTIC PASS: {name}')
        if detail:
            log(f'      {detail}')
        return True

    log(f'DIAGNOSTIC FAIL: {name}')

    if detail:
        log(f'      {detail}')

    return False


def D(value):
    return Decimal(str(value))


def quantize_down(value, step):
    value = D(value)
    step = D(step)

    if step <= 0:
        raise ValueError('Invalid quantization step')

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_to_string(value):
    if value is None:
        return None

    value = D(value)
    text = format(value, 'f')

    if '.' in text:
        text = text.rstrip('0').rstrip('.')

    return text


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':'),
        default=str
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode('utf-8')
    ).hexdigest()


def read_json_file(path, default=None):
    if default is None:
        default = {}

    try:
        if not os.path.exists(path):
            return default

        with open(
            path,
            'r',
            encoding='utf-8'
        ) as f:
            return json.load(f)

    except Exception as exc:
        log(
            f'READ JSON FAILED path={path} error={exc}'
        )
        return default


def write_json_file(path, data):
    tmp = path + '.tmp'

    with open(
        tmp,
        'w',
        encoding='utf-8'
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            sort_keys=True,
            default=str
        )

    os.replace(tmp, path)


def collect_ids_from_file(path):
    ids = set()
    data = read_json_file(
        path,
        default=None
    )

    if data is None:
        return ids

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if (
                    isinstance(key, str)
                    and 'id' in key.lower()
                    and isinstance(item, str)
                ):
                    ids.add(item)

                walk(item)

        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    return ids


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            f'stage={STAGE}\n'
            f'status={TEST_STATUS}\n'
        ).encode()

        self.send_response(200)
        self.send_header(
            'Content-Type',
            'text/plain'
        )
        self.send_header(
            'Content-Length',
            str(len(body))
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(
        self,
        format_string,
        *args
    ):
        return


def start_health_server():
    port = int(
        os.getenv(
            'PORT',
            '10000'
        )
    )

    server = HTTPServer(
        ('0.0.0.0', port),
        HealthHandler
    )

    thread = Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    log(
        f'{STAGE}: HEALTH SERVER STARTED ON PORT {port}'
    )


def build_signature(
    timestamp,
    method,
    request_path,
    body=''
):
    api_secret = os.getenv(
        'WEEX_API_SECRET'
    )

    if not api_secret:
        raise RuntimeError(
            'WEEX_API_SECRET missing'
        )

    prehash = (
        str(timestamp)
        + method.upper()
        + request_path
        + body
    )

    digest = hmac.new(
        api_secret.encode(),
        prehash.encode(),
        hashlib.sha256
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


async def weex_get(
    path,
    params=None,
    authenticated=False
):
    """
    Read-only WEEX GET.

    R36F.9 signs the exact query string for authenticated GET requests.
    No POST/PUT/PATCH/DELETE transport exists here.
    """
    params = params or {}

    from urllib.parse import urlencode

    query_string = urlencode(
        params,
        doseq=True
    )

    request_target = path

    if query_string:
        request_target += '?' + query_string

    url = API_BASE_URL + request_target
    headers = {}

    if authenticated:
        api_key = os.getenv(
            'WEEX_API_KEY'
        )

        passphrase = os.getenv(
            'WEEX_API_PASSPHRASE'
        )

        if not api_key:
            raise RuntimeError(
                'WEEX_API_KEY missing'
            )

        if not passphrase:
            raise RuntimeError(
                'WEEX_API_PASSPHRASE missing'
            )

        timestamp = str(
            int(time.time() * 1000)
        )

        signature = build_signature(
            timestamp,
            'GET',
            request_target,
            ''
        )

        headers = {
            'ACCESS-KEY': api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.get(
            url,
            headers=headers
        ) as response:

            text = await response.text()

            if response.status >= 400:
                raise RuntimeError(
                    f'WEEX GET HTTP {response.status}: {text}'
                )

            try:
                return json.loads(text)

            except Exception:
                return {
                    'raw': text
                }


async def weex_demo_post(
    path,
    payload
):
    """
    Send one authenticated JSON POST only to WEEX's paper-trading order endpoint.

    Production order/mutation paths remain unreachable because this function rejects
    every path except R36F14_DEMO_ORDER_ENDPOINT and independently requires the
    production execution firebreak to remain fully disabled.
    """

    if path != R36F14_DEMO_ORDER_ENDPOINT:
        raise RuntimeError(
            'R36F.15 demo transport refused non-demo endpoint'
        )

    if not (
        R36F15_DEMO_POST_TRANSPORT_ENABLED
        and R36F15_DEMO_ORDER_SUBMISSION_ENABLED
        and R36F15_FIRST_DEMO_ORDER_ALLOWED
    ):
        raise RuntimeError(
            'R36F.15 demo transport is disabled'
        )

    if not (
        REAL_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MODE_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
        and FIRST_REAL_ORDER_ALLOWED is False
    ):
        raise RuntimeError(
            'R36F.15 production firebreak is not intact'
        )

    api_key = os.getenv(
        'WEEX_API_KEY'
    )

    passphrase = os.getenv(
        'WEEX_API_PASSPHRASE'
    )

    if not api_key:
        raise RuntimeError(
            'WEEX_API_KEY missing'
        )

    if not passphrase:
        raise RuntimeError(
            'WEEX_API_PASSPHRASE missing'
        )

    body = canonical_json(payload)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = build_signature(
        timestamp,
        'POST',
        path,
        body
    )

    headers = {
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': signature,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    url = API_BASE_URL + path

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.post(
            url,
            headers=headers,
            data=body
        ) as response:

            text = await response.text()

            try:
                data = json.loads(text)

            except Exception:
                data = {
                    'raw': text
                }

            result = {
                'http_status': response.status,
                'response': data,
                'raw_text': text
            }

            if response.status >= 400:
                raise RuntimeError(
                    f'WEEX DEMO POST HTTP {response.status}: {text}'
                )

            return result


def r36f15_demo_journal_unresolved(
    journal
):
    if (
        not isinstance(journal, dict)
        or not journal
    ):
        return False

    return journal.get(
        'state'
    ) in {
        'PREPARED',
        'SENT_AMBIGUOUS'
    }


def r36f15_demo_journal_completed(
    journal
):
    return bool(
        isinstance(journal, dict)
        and journal.get('state') == 'COMPLETED'
        and journal.get('success') is True
    )


def _r36f153_history_rows(data):
    """
    Normalize WEEX demo history responses without guessing on malformed data.
    """

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            'data',
            'list',
            'rows',
            'orders'
        ):
            value = data.get(key)

            if isinstance(value, list):
                return value

    return None


async def r36f153_lookup_demo_order_by_client_id(
    client_order_id
):
    """
    Read-only lookup of a previously attempted WEEX demo order.

    Returns one of FOUND / NOT_FOUND / UNKNOWN. UNKNOWN is deliberately
    fail-closed: it never clears an ambiguous journal and never permits resend.
    """

    client_order_id = str(
        client_order_id or ''
    ).strip()

    if not client_order_id:
        return {
            'status': 'UNKNOWN',
            'reason': 'MISSING_CLIENT_ORDER_ID',
            'order': None
        }

    try:
        data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            params={
                'symbol': R36F14_DEMO_SYMBOL,
                'limit': 1000,
                'page': 0
            },
            authenticated=True
        )

    except Exception as exc:
        return {
            'status': 'UNKNOWN',
            'reason': 'DEMO_HISTORY_LOOKUP_FAILED',
            'error': str(exc),
            'order': None
        }

    rows = _r36f153_history_rows(
        data
    )

    if rows is None:
        return {
            'status': 'UNKNOWN',
            'reason': 'DEMO_HISTORY_RESPONSE_UNRECOGNIZED',
            'order': None
        }

    for row in rows:
        if not isinstance(row, dict):
            continue

        row_client_id = str(
            row.get('clientOrderId')
            or row.get('newClientOrderId')
            or ''
        ).strip()

        if row_client_id == client_order_id:
            return {
                'status': 'FOUND',
                'reason': 'CLIENT_ORDER_ID_FOUND_IN_DEMO_HISTORY',
                'order': row
            }

    return {
        'status': 'NOT_FOUND',
        'reason': 'CLIENT_ORDER_ID_NOT_FOUND_IN_DEMO_HISTORY',
        'order': None
    }


async def r36f153_reconcile_demo_journal(
    journal
):
    """
    Reconcile the durable R36F.15 demo dispatch journal before any resend.

    Frozen policy from the passed R36F.15.3 reconciliation test:
      * no journal -> retry allowed
      * COMPLETED -> terminal, resend blocked
      * REJECTED -> terminal for that attempt, fresh retry allowed
      * PREPARED/SENT_AMBIGUOUS + order found -> COMPLETED, resend blocked
      * PREPARED/SENT_AMBIGUOUS + order not found -> REJECTED, fresh retry allowed
      * lookup unknown / missing client id / unknown journal state -> fail closed
      * error text alone never clears an ambiguous journal
    """

    if (
        not isinstance(journal, dict)
        or not journal
    ):
        return {
            'resolved': True,
            'retry_allowed': True,
            'reason': 'NO_JOURNAL',
            'journal': {},
            'changed': False
        }

    state = str(
        journal.get('state') or ''
    ).strip().upper()

    if state == 'COMPLETED':
        return {
            'resolved': True,
            'retry_allowed': False,
            'reason': 'COMPLETED_REMAINS_TERMINAL',
            'journal': journal,
            'changed': False
        }

    if state == 'REJECTED':
        return {
            'resolved': True,
            'retry_allowed': True,
            'reason': 'REJECTED_PERMITS_FRESH_RETRY',
            'journal': journal,
            'changed': False
        }

    if state not in {
        'PREPARED',
        'SENT_AMBIGUOUS'
    }:
        return {
            'resolved': False,
            'retry_allowed': False,
            'reason': 'UNKNOWN_JOURNAL_STATE_BLOCKS_RETRY',
            'journal': journal,
            'changed': False
        }

    client_order_id = str(
        journal.get('client_order_id')
        or ''
    ).strip()

    if not client_order_id:
        return {
            'resolved': False,
            'retry_allowed': False,
            'reason': 'MISSING_CLIENT_ID_BLOCKS_RETRY',
            'journal': journal,
            'changed': False
        }

    lookup = await r36f153_lookup_demo_order_by_client_id(
        client_order_id
    )

    lookup_status = lookup.get(
        'status'
    )

    if lookup_status == 'FOUND':
        order = (
            lookup.get('order')
            if isinstance(
                lookup.get('order'),
                dict
            )
            else {}
        )

        reconciled = {
            **journal,
            'state': 'COMPLETED',
            'updated_at': now_iso(),
            'success': True,
            'reconciliation_status': 'FOUND',
            'reconciliation_reason': lookup.get('reason'),
            'order_id': str(
                order.get(
                    'orderId',
                    journal.get(
                        'order_id',
                        ''
                    )
                )
            ),
            'client_order_id_response': str(
                order.get(
                    'clientOrderId',
                    client_order_id
                )
            ),
            'reconciled_order': order
        }

        write_json_file(
            R36F15_DEMO_JOURNAL_FILE,
            reconciled
        )

        return {
            'resolved': True,
            'retry_allowed': False,
            'reason': 'AMBIGUOUS_FOUND_MARKED_COMPLETED',
            'journal': reconciled,
            'changed': True
        }

    if lookup_status == 'NOT_FOUND':
        reconciled = {
            **journal,
            'state': 'REJECTED',
            'updated_at': now_iso(),
            'success': False,
            'reconciliation_status': 'NOT_FOUND',
            'reconciliation_reason': lookup.get('reason')
        }

        write_json_file(
            R36F15_DEMO_JOURNAL_FILE,
            reconciled
        )

        return {
            'resolved': True,
            'retry_allowed': True,
            'reason': 'AMBIGUOUS_NOT_FOUND_MARKED_REJECTED',
            'journal': reconciled,
            'changed': True
        }

    return {
        'resolved': False,
        'retry_allowed': False,
        'reason': lookup.get(
            'reason',
            'AMBIGUOUS_UNKNOWN_BLOCKS_RETRY'
        ),
        'journal': journal,
        'lookup': lookup,
        'changed': False
    }


async def r36f154_validate_fresh_demo_triggers(
    payload
):
    """
    R36F.15.4 just-in-time safety gate.

    Fetch a fresh WEEX mark price immediately before any demo POST and ensure
    the already-selected TP1/protective-stop still bracket that live price in
    the correct direction. If price has crossed either trigger, fail closed
    without writing a PREPARED journal and without sending the demo order.

    This deliberately does NOT move TP or SL to force acceptance. The normal
    runtime reevaluation must construct a fresh direction-specific snapshot.
    """

    payload = (
        payload
        if isinstance(payload, dict)
        else {}
    )

    direction = str(
        payload.get('positionSide')
        or ''
    ).strip().upper()

    try:
        tp = D(
            payload.get(
                'tpTriggerPrice',
                '0'
            )
        )

        sl = D(
            payload.get(
                'slTriggerPrice',
                '0'
            )
        )

    except Exception as exc:
        return {
            'valid': False,
            'reason': 'JIT_TRIGGER_PARSE_FAILED',
            'error': str(exc)
        }

    if direction not in {
        'LONG',
        'SHORT'
    }:
        return {
            'valid': False,
            'reason': 'JIT_DIRECTION_INVALID',
            'direction': direction
        }

    try:
        fresh_mark = D(
            await load_mark_price()
        )

    except Exception as exc:
        return {
            'valid': False,
            'reason': 'JIT_FRESH_MARK_READ_FAILED',
            'error': str(exc)
        }

    if (
        fresh_mark <= 0
        or tp <= 0
        or sl <= 0
    ):
        return {
            'valid': False,
            'reason': 'JIT_NON_POSITIVE_PRICE',
            'direction': direction,
            'fresh_mark_price': decimal_to_string(
                fresh_mark
            ),
            'tp_trigger_price': decimal_to_string(
                tp
            ),
            'sl_trigger_price': decimal_to_string(
                sl
            )
        }

    if direction == 'LONG':
        valid = (
            sl
            < fresh_mark
            < tp
        )

        reason = (
            'JIT_LONG_TRIGGERS_VALID'
            if valid
            else 'JIT_LONG_TRIGGER_STALE_OR_CROSSED'
        )

    else:
        valid = (
            tp
            < fresh_mark
            < sl
        )

        reason = (
            'JIT_SHORT_TRIGGERS_VALID'
            if valid
            else 'JIT_SHORT_TRIGGER_STALE_OR_CROSSED'
        )

    return {
        'valid': bool(valid),
        'reason': reason,
        'direction': direction,
        'fresh_mark_price': decimal_to_string(
            fresh_mark
        ),
        'tp_trigger_price': decimal_to_string(
            tp
        ),
        'sl_trigger_price': decimal_to_string(
            sl
        )
    }


async def submit_r36f15_demo_order(
    preview,
    command_preview
):
    """
    Exactly-once demo dispatch with R36F.15.3 reconciliation
    plus R36F.15.4 JIT trigger validation.
    """

    if not R36F15_DEMO_ARM_REQUESTED:
        return {
            'attempted': False,
            'sent': False,
            'reason': 'DEMO_ARM_NOT_REQUESTED'
        }

    if not command_preview.get(
        'authorized_preview'
    ):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'TELEGRAM_COMMAND_NOT_AUTHORIZED'
        }

    if (
        not preview
        or not preview.get('payload')
    ):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'DEMO_PREVIEW_MISSING'
        }

    existing = read_json_file(
        R36F15_DEMO_JOURNAL_FILE,
        default={}
    )

    reconciliation = (
        await r36f153_reconcile_demo_journal(
            existing
        )
    )

    log(
        'R36F.15.4 DEMO JOURNAL RECONCILIATION = '
        + canonical_json({
            'resolved': reconciliation.get(
                'resolved'
            ),
            'retry_allowed': reconciliation.get(
                'retry_allowed'
            ),
            'reason': reconciliation.get(
                'reason'
            ),
            'changed': reconciliation.get(
                'changed'
            )
        })
    )

    if not reconciliation.get(
        'resolved'
    ):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'UNRESOLVED_DEMO_JOURNAL_BLOCKS_RETRY',
            'reconciliation': reconciliation,
            'journal': reconciliation.get(
                'journal',
                existing
            )
        }

    if not reconciliation.get(
        'retry_allowed'
    ):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'FIRST_DEMO_ORDER_ALREADY_COMPLETED',
            'reconciliation': reconciliation,
            'journal': reconciliation.get(
                'journal',
                existing
            )
        }

    payload = dict(
        preview['payload']
    )

    jit_validation = (
        await r36f154_validate_fresh_demo_triggers(
            payload
        )
    )

    log(
        'R36F.15.4 JIT DEMO TRIGGER VALIDATION = '
        + canonical_json(
            jit_validation
        )
    )

    if not jit_validation.get(
        'valid'
    ):
        return {
            'attempted': False,
            'sent': False,
            'accepted': False,
            'reason': 'JIT_DEMO_TRIGGER_VALIDATION_BLOCKED',
            'jit_validation': jit_validation
        }

    payload_hash = sha256_text(
        canonical_json(
            payload
        )
    )

    prepared = {
        'stage': STAGE,
        'state': 'PREPARED',
        'created_at': now_iso(),
        'endpoint': R36F14_DEMO_ORDER_ENDPOINT,
        'client_order_id': payload.get(
            'newClientOrderId'
        ),
        'payload_sha256': payload_hash,
        'payload': payload,
        'real_order_execution': REAL_ORDER_EXECUTION,
        'prior_reconciliation_reason': reconciliation.get(
            'reason'
        )
    }

    write_json_file(
        R36F15_DEMO_JOURNAL_FILE,
        prepared
    )

    try:
        transport = await weex_demo_post(
            R36F14_DEMO_ORDER_ENDPOINT,
            payload
        )

    except Exception as exc:
        ambiguous = {
            **prepared,
            'state': 'SENT_AMBIGUOUS',
            'updated_at': now_iso(),
            'error': str(exc)
        }

        write_json_file(
            R36F15_DEMO_JOURNAL_FILE,
            ambiguous
        )

        return {
            'attempted': True,
            'sent': False,
            'accepted': False,
            'reason': 'DEMO_POST_EXCEPTION_JOURNALED_AMBIGUOUS',
            'error': str(exc),
            'journal': ambiguous
        }

    response = (
        transport.get('response')
        if isinstance(
            transport,
            dict
        )
        else {}
    )

    response = (
        response
        if isinstance(
            response,
            dict
        )
        else {}
    )

    success = bool(
        response.get('success')
    )

    completed = {
        **prepared,
        'state': (
            'COMPLETED'
            if success
            else 'REJECTED'
        ),
        'updated_at': now_iso(),
        'http_status': transport.get(
            'http_status'
        ),
        'response': response,
        'success': success,
        'order_id': str(
            response.get(
                'orderId',
                ''
            )
        ),
        'client_order_id_response': str(
            response.get(
                'clientOrderId',
                ''
            )
        ),
        'error_code': str(
            response.get(
                'errorCode',
                ''
            )
        ),
        'error_message': str(
            response.get(
                'errorMessage',
                ''
            )
        )
    }

    write_json_file(
        R36F15_DEMO_JOURNAL_FILE,
        completed
    )

    return {
        'attempted': True,
        'sent': True,
        'accepted': success,
        'transport': transport,
        'journal': completed
    }


async def load_mark_price():
    global MARK_PRICE

    data = await weex_get(
        '/capi/v3/market/symbolPrice',
        params={
            'symbol': SYMBOL
        },
        authenticated=False
    )

    candidates = []

    if isinstance(data, dict):
        for key in (
            'price',
            'markPrice',
            'lastPrice'
        ):
            if key in data:
                candidates.append(
                    data[key]
                )

        nested = data.get(
            'data'
        )

        if isinstance(
            nested,
            dict
        ):
            for key in (
                'price',
                'markPrice',
                'lastPrice'
            ):
                if key in nested:
                    candidates.append(
                        nested[key]
                    )

    elif isinstance(
        data,
        list
    ):
        for item in data:
            if isinstance(
                item,
                dict
            ):
                for key in (
                    'price',
                    'markPrice',
                    'lastPrice'
                ):
                    if key in item:
                        candidates.append(
                            item[key]
                        )

    for candidate in candidates:
        try:
            MARK_PRICE = D(
                candidate
            )

            if MARK_PRICE > 0:
                log(
                    'MARK PRICE = '
                    + decimal_to_string(
                        MARK_PRICE
                    )
                )

                return MARK_PRICE

        except Exception:
            continue

    raise RuntimeError(
        'Unable to determine WEEX mark price'
    )


async def load_available_balance():
    global AVAILABLE_BALANCE

    data = await weex_get(
        '/capi/v3/account/balance',
        authenticated=True
    )

    candidates = []

    def collect(value):
        if isinstance(
            value,
            dict
        ):
            for key, item in value.items():
                key_lower = key.lower()

                if key_lower in (
                    'availablebalance',
                    'available_balance',
                    'available',
                    'free',
                    'usdtavailable'
                ):
                    candidates.append(
                        item
                    )

                collect(
                    item
                )

        elif isinstance(
            value,
            list
        ):
            for item in value:
                collect(
                    item
                )

    collect(
        data
    )

    for candidate in candidates:
        try:
            value = D(
                candidate
            )

            if value >= 0:
                AVAILABLE_BALANCE = value

                log(
                    'AVAILABLE USDT = '
                    + decimal_to_string(
                        AVAILABLE_BALANCE
                    )
                )

                return value

        except Exception:
            continue

    raise RuntimeError(
        'Unable to determine available USDT balance'
    )


async def load_open_positions():
    global OPEN_POSITIONS

    data = await weex_get(
        '/capi/v3/account/position/singlePosition',
        params={
            'symbol': SYMBOL
        },
        authenticated=True
    )

    if isinstance(
        data,
        list
    ):
        OPEN_POSITIONS = data

    elif isinstance(
        data,
        dict
    ):
        nested = data.get(
            'data'
        )

        if isinstance(
            nested,
            list
        ):
            OPEN_POSITIONS = nested

        else:
            OPEN_POSITIONS = []

    else:
        OPEN_POSITIONS = []

    log(
        'OPEN POSITIONS = '
        + str(
            len(
                OPEN_POSITIONS
            )
        )
    )

    return OPEN_POSITIONS


async def load_exchange_config():
    global WEEX_CONFIG

    data = await weex_get(
        '/capi/v3/market/exchangeInfo',
        params={
            'symbol': SYMBOL
        },
        authenticated=False
    )

    WEEX_CONFIG = (
        data
        if isinstance(
            data,
            dict
        )
        else {}
    )

    log(
        'WEEX EXCHANGE CONFIG READ COMPLETE'
    )

    return WEEX_CONFIG

