
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

STAGE = 'R36F.15.2'
PURPOSE = 'SELECTED TP SNAPSHOT SCOPE FIX: preserve the complete R36F.15.1 continuous EMA19/EMA50/EMA200 + Telegram + two-cluster TP + quantity/readiness + mandatory protective-stop + stop-risk-envelope + stop-loss-budget + exactly-once WEEX demo dispatch chain, while fixing only the stale selected_tp_snapshot reference so the already-selected direction-specific TP snapshot reaches demo preview construction correctly. Production /capi/v3/order and every real-money mutation remain hard-disabled.'
API_BASE_URL = 'https://api-contract.weex.com'
SYMBOL = 'BTCUSDT'
PUBLIC_TICKER_SYMBOL = 'cmt_btcusdt'
KLINE_INTERVAL = '1m'
HISTORICAL_LIMIT = 250
MAX_HISTORICAL_PAGES = 4
R36F151_REEVALUATION_SECONDS = max(15, int(os.getenv('R36F151_REEVALUATION_SECONDS', '60')))
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
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '').strip()
R36F12_TELEGRAM_ALERTS_ENABLED = os.getenv('R36F12_TELEGRAM_ALERTS_ENABLED', 'false').strip().lower() in {'1', 'true', 'yes', 'on'}
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
CANARY_ARM_REQUESTED = os.getenv('R36F12_LIVE_CANARY_ARM', '').strip() == CANARY_ARM_PHRASE
CANARY_STOP_PRICE_TEXT = os.getenv('R36F12_CANARY_STOP_PRICE', '').strip()
CANARY_STOP_WORKING_TYPE = 'MARK_PRICE'
R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(os.getenv('R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT', '0.50'))

if R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError('R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive')

R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(os.getenv('R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT', '0.75'))

if R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError('R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive')

R36F132_MAX_ACCOUNT_LOSS_PERCENT = Decimal(os.getenv('R36F132_MAX_ACCOUNT_LOSS_PERCENT', '2.50'))

if R36F132_MAX_ACCOUNT_LOSS_PERCENT <= 0:
    raise ValueError('R36F132_MAX_ACCOUNT_LOSS_PERCENT must be positive')

R36F14_DEMO_SYMBOL = os.getenv('R36F14_DEMO_SYMBOL', 'BTCSUSDT').strip().upper()
R36F14_DEMO_ASSET = os.getenv('R36F14_DEMO_ASSET', 'SUSDT').strip().upper()
R36F14_DEMO_BALANCE_ENDPOINT = '/capi/v3/sim/balance'
R36F14_DEMO_POSITIONS_ENDPOINT = '/capi/v3/sim/position/allPosition'
R36F14_DEMO_ORDER_HISTORY_ENDPOINT = '/capi/v3/sim/order/history'
R36F14_DEMO_ORDER_ENDPOINT = '/capi/v3/sim/order'
R36F14_DEMO_READS_ENABLED = True
R36F14_DEMO_POST_TRANSPORT_ENABLED = False
R36F14_DEMO_ORDER_SUBMISSION_ENABLED = False
R36F14_FIRST_DEMO_ORDER_ALLOWED = False
R36F15_DEMO_ARM_PHRASE = 'ARM_FIRST_WEEX_DEMO_ORDER'
R36F15_DEMO_ARM_REQUESTED = os.getenv('R36F15_DEMO_ARM', '').strip() == R36F15_DEMO_ARM_PHRASE
R36F15_DEMO_POST_TRANSPORT_ENABLED = True
R36F15_DEMO_ORDER_SUBMISSION_ENABLED = True
R36F15_FIRST_DEMO_ORDER_ALLOWED = True
R36F15_RECONCILE_DELAY_SECONDS = Decimal(os.getenv('R36F15_RECONCILE_DELAY_SECONDS', '1.0'))
R36A_STATE_DIR = '/var/data/r36a_state'
R36C_STATE_DIR = '/var/data/r36c_state'
R36D_STATE_DIR = '/var/data/r36d_state'
R36F_STATE_DIR = '/var/data/r36f_state'
os.makedirs(R36F_STATE_DIR, exist_ok=True)
R36A_DEDUPE_FILE = os.path.join(R36A_STATE_DIR, 'telegram_processed_updates.json')
R36A_DECISION_FILE = os.path.join(R36A_STATE_DIR, 'synthetic_decisions.json')
R36C_DEDUPE_FILE = os.path.join(R36C_STATE_DIR, 'telegram_processed_updates.json')
R36C_DECISION_FILE = os.path.join(R36C_STATE_DIR, 'synthetic_decisions.json')
R36D_SNAPSHOT_FILE = os.path.join(R36D_STATE_DIR, 'pre_live_readiness_snapshot.json')
R36F_SNAPSHOT_FILE = os.path.join(R36F_STATE_DIR, 'pre_live_readiness_snapshot.json')
R36F12_CANARY_JOURNAL_FILE = os.path.join(R36F_STATE_DIR, 'first_live_canary_dispatch_journal.json')
R36F12_TELEGRAM_SIGNAL_FILE = os.path.join(R36F_STATE_DIR, 'r36f12_ema_telegram_signal_snapshot.json')
R36F12_TELEGRAM_COMMAND_FILE = os.path.join(R36F_STATE_DIR, 'r36f12_telegram_command_preview.json')
R36F15_DEMO_JOURNAL_FILE = os.path.join(R36F_STATE_DIR, 'r36f15_demo_dispatch_journal.json')
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
    print('----------------------------------------------------------------------------------------------------', flush=True)

def log(message):
    print(f'{now_iso()} {message}', flush=True)

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
    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
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
    return json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)

def sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def read_json_file(path, default=None):
    if default is None:
        default = {}
    try:
        if not os.path.exists(path):
            return default
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as exc:
        log(f'READ JSON FAILED path={path} error={exc}')
        return default

def write_json_file(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)
    os.replace(tmp, path)

def collect_ids_from_file(path):
    ids = set()
    data = read_json_file(path, default=None)

    if data is None:
        return ids

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(key, str) and 'id' in key.lower() and isinstance(item, str):
                    ids.add(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    return ids

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = f'stage={STAGE}\nstatus={TEST_STATUS}\n'.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        return

def start_health_server():
    port = int(os.getenv('PORT', '10000'))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log(f'{STAGE}: HEALTH SERVER STARTED ON PORT {port}')

def build_signature(timestamp, method, request_path, body=''):
    api_secret = os.getenv('WEEX_API_SECRET')

    if not api_secret:
        raise RuntimeError('WEEX_API_SECRET missing')

    prehash = str(timestamp) + method.upper() + request_path + body
    digest = hmac.new(api_secret.encode(), prehash.encode(), hashlib.sha256).digest()

    return base64.b64encode(digest).decode()

async def weex_get(path, params=None, authenticated=False):
    params = params or {}

    from urllib.parse import urlencode

    query_string = urlencode(params, doseq=True)
    request_target = path

    if query_string:
        request_target += '?' + query_string

    url = API_BASE_URL + request_target
    headers = {}

    if authenticated:
        api_key = os.getenv('WEEX_API_KEY')
        passphrase = os.getenv('WEEX_API_PASSPHRASE')

        if not api_key:
            raise RuntimeError('WEEX_API_KEY missing')

        if not passphrase:
            raise RuntimeError('WEEX_API_PASSPHRASE missing')

        timestamp = str(int(time.time() * 1000))
        signature = build_signature(timestamp, 'GET', request_target, '')

        headers = {
            'ACCESS-KEY': api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }

    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as response:
            text = await response.text()

            if response.status >= 400:
                raise RuntimeError(f'WEEX GET HTTP {response.status}: {text}')

            try:
                return json.loads(text)
            except Exception:
                return {'raw': text}

async def weex_demo_post(path, payload):
    if path != R36F14_DEMO_ORDER_ENDPOINT:
        raise RuntimeError('R36F.15 demo transport refused non-demo endpoint')

    if not (
        R36F15_DEMO_POST_TRANSPORT_ENABLED
        and R36F15_DEMO_ORDER_SUBMISSION_ENABLED
        and R36F15_FIRST_DEMO_ORDER_ALLOWED
    ):
        raise RuntimeError('R36F.15 demo transport is disabled')

    if not (
        REAL_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MODE_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
        and FIRST_REAL_ORDER_ALLOWED is False
    ):
        raise RuntimeError('R36F.15 production firebreak is not intact')

    api_key = os.getenv('WEEX_API_KEY')
    passphrase = os.getenv('WEEX_API_PASSPHRASE')

    if not api_key:
        raise RuntimeError('WEEX_API_KEY missing')

    if not passphrase:
        raise RuntimeError('WEEX_API_PASSPHRASE missing')

    body = canonical_json(payload)
    timestamp = str(int(time.time() * 1000))
    signature = build_signature(timestamp, 'POST', path, body)

    headers = {
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': signature,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }

    timeout = aiohttp.ClientTimeout(total=20)
    url = API_BASE_URL + path

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, data=body) as response:
            text = await response.text()

            try:
                data = json.loads(text)
            except Exception:
                data = {'raw': text}

            result = {
                'http_status': response.status,
                'response': data,
                'raw_text': text
            }

            if response.status >= 400:
                raise RuntimeError(f'WEEX DEMO POST HTTP {response.status}: {text}')

            return result

def r36f15_demo_journal_unresolved(journal):
    if not isinstance(journal, dict) or not journal:
        return False

    return journal.get('state') in {'PREPARED', 'SENT_AMBIGUOUS'}

def r36f15_demo_journal_completed(journal):
    return bool(
        isinstance(journal, dict)
        and journal.get('state') == 'COMPLETED'
        and journal.get('success') is True
    )

async def submit_r36f15_demo_order(preview, command_preview):
    if not R36F15_DEMO_ARM_REQUESTED:
        return {
            'attempted': False,
            'sent': False,
            'reason': 'DEMO_ARM_NOT_REQUESTED'
        }

    if not command_preview.get('authorized_preview'):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'TELEGRAM_COMMAND_NOT_AUTHORIZED'
        }

    if not preview or not preview.get('payload'):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'DEMO_PREVIEW_MISSING'
        }

    existing = read_json_file(R36F15_DEMO_JOURNAL_FILE, default={})

    if r36f15_demo_journal_unresolved(existing):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'UNRESOLVED_DEMO_JOURNAL_BLOCKS_RETRY',
            'journal': existing
        }

    if r36f15_demo_journal_completed(existing):
        return {
            'attempted': False,
            'sent': False,
            'reason': 'FIRST_DEMO_ORDER_ALREADY_COMPLETED',
            'journal': existing
        }

    payload = dict(preview['payload'])
    payload_hash = sha256_text(canonical_json(payload))

    prepared = {
        'stage': STAGE,
        'state': 'PREPARED',
        'created_at': now_iso(),
        'endpoint': R36F14_DEMO_ORDER_ENDPOINT,
        'client_order_id': payload.get('newClientOrderId'),
        'payload_sha256': payload_hash,
        'payload': payload,
        'real_order_execution': REAL_ORDER_EXECUTION
    }

    write_json_file(R36F15_DEMO_JOURNAL_FILE, prepared)

    try:
        transport = await weex_demo_post(R36F14_DEMO_ORDER_ENDPOINT, payload)

    except Exception as exc:
        ambiguous = {
            **prepared,
            'state': 'SENT_AMBIGUOUS',
            'updated_at': now_iso(),
            'error': str(exc)
        }

        write_json_file(R36F15_DEMO_JOURNAL_FILE, ambiguous)
        raise

    response = transport.get('response') if isinstance(transport, dict) else {}
    response = response if isinstance(response, dict) else {}
    success = bool(response.get('success'))

    completed = {
        **prepared,
        'state': 'COMPLETED' if success else 'REJECTED',
        'updated_at': now_iso(),
        'http_status': transport.get('http_status'),
        'response': response,
        'success': success,
        'order_id': str(response.get('orderId', '')),
        'client_order_id_response': str(response.get('clientOrderId', '')),
        'error_code': str(response.get('errorCode', '')),
        'error_message': str(response.get('errorMessage', ''))
    }

    write_json_file(R36F15_DEMO_JOURNAL_FILE, completed)

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
        params={'symbol': SYMBOL},
        authenticated=False
    )

    candidates = []

    if isinstance(data, dict):
        for key in ('price', 'markPrice', 'lastPrice'):
            if key in data:
                candidates.append(data[key])

        nested = data.get('data')

        if isinstance(nested, dict):
            for key in ('price', 'markPrice', 'lastPrice'):
                if key in nested:
                    candidates.append(nested[key])

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for key in ('price', 'markPrice', 'lastPrice'):
                    if key in item:
                        candidates.append(item[key])

    for candidate in candidates:
        try:
            MARK_PRICE = D(candidate)

            if MARK_PRICE > 0:
                log('MARK PRICE = ' + decimal_to_string(MARK_PRICE))
                return MARK_PRICE

        except Exception:
            continue

    raise RuntimeError('Unable to determine WEEX mark price')

async def load_available_balance():
    global AVAILABLE_BALANCE

    data = await weex_get(
        '/capi/v3/account/balance',
        authenticated=True
    )

    candidates = []

    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = key.lower()

                if key_lower in (
                    'availablebalance',
                    'available_balance',
                    'available',
                    'free',
                    'usdtavailable'
                ):
                    candidates.append(item)

                collect(item)

        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(data)

    for candidate in candidates:
        try:
            value = D(candidate)

            if value >= 0:
                AVAILABLE_BALANCE = value
                log('AVAILABLE USDT = ' + decimal_to_string(AVAILABLE_BALANCE))
                return value

        except Exception:
            continue

    raise RuntimeError('Unable to determine available USDT balance')

async def load_open_positions():
    global OPEN_POSITIONS

    data = await weex_get(
        '/capi/v3/account/position/singlePosition',
        params={'symbol': SYMBOL},
        authenticated=True
    )

    if isinstance(data, list):
        OPEN_POSITIONS = data

    elif isinstance(data, dict):
        nested = data.get('data')

        if isinstance(nested, list):
            OPEN_POSITIONS = nested
        else:
            OPEN_POSITIONS = []

    else:
        OPEN_POSITIONS = []

    log('OPEN POSITIONS = ' + str(len(OPEN_POSITIONS)))

    return OPEN_POSITIONS

async def load_exchange_config():
    global WEEX_CONFIG

    data = await weex_get(
        '/capi/v3/market/exchangeInfo',
        params={'symbol': SYMBOL},
        authenticated=False
    )

    WEEX_CONFIG = data if isinstance(data, dict) else {}

    log('WEEX EXCHANGE CONFIG READ COMPLETE')

    return WEEX_CONFIG

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

