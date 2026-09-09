
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
STAGE = 'R36F.15.3'
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
        headers = {'ACCESS-KEY': api_key, 'ACCESS-SIGN': signature, 'ACCESS-TIMESTAMP': timestamp, 'ACCESS-PASSPHRASE': passphrase, 'Content-Type': 'application/json'}
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
    if not (R36F15_DEMO_POST_TRANSPORT_ENABLED and R36F15_DEMO_ORDER_SUBMISSION_ENABLED and R36F15_FIRST_DEMO_ORDER_ALLOWED):
        raise RuntimeError('R36F.15 demo transport is disabled')
    if not (REAL_ORDER_EXECUTION is False and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False and (ORDER_SUBMISSION_ENABLED is False) and (LEVERAGE_MUTATION_ENABLED is False) and (MARGIN_MODE_MUTATION_ENABLED is False) and (POSITION_MUTATION_ENABLED is False) and (FIRST_REAL_ORDER_ALLOWED is False)):
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
    headers = {'ACCESS-KEY': api_key, 'ACCESS-SIGN': signature, 'ACCESS-TIMESTAMP': timestamp, 'ACCESS-PASSPHRASE': passphrase, 'Content-Type': 'application/json'}
    timeout = aiohttp.ClientTimeout(total=20)
    url = API_BASE_URL + path
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, data=body) as response:
            text = await response.text()
            try:
                data = json.loads(text)
            except Exception:
                data = {'raw': text}
            result = {'http_status': response.status, 'response': data, 'raw_text': text}
            if response.status >= 400:
                raise RuntimeError(f'WEEX DEMO POST HTTP {response.status}: {text}')
            return result

def r36f15_demo_journal_unresolved(journal):
    if not isinstance(journal, dict) or not journal:
        return False
    return journal.get('state') in {'PREPARED', 'SENT_AMBIGUOUS'}

def r36f15_demo_journal_completed(journal):
    return bool(isinstance(journal, dict) and journal.get('state') == 'COMPLETED' and (journal.get('success') is True))

def _r36f153_history_rows(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ('data', 'list', 'rows', 'orders'):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return None

async def r36f153_lookup_demo_order_by_client_id(client_order_id):
    client_order_id = str(client_order_id or '').strip()
    if not client_order_id:
        return {'status': 'UNKNOWN', 'reason': 'MISSING_CLIENT_ORDER_ID', 'order': None}
    try:
        data = await weex_get(R36F14_DEMO_ORDER_HISTORY_ENDPOINT, params={'symbol': R36F14_DEMO_SYMBOL, 'limit': 1000, 'page': 0}, authenticated=True)
    except Exception as exc:
        return {'status': 'UNKNOWN', 'reason': 'DEMO_HISTORY_LOOKUP_FAILED', 'error': str(exc), 'order': None}
    rows = _r36f153_history_rows(data)
    if rows is None:
        return {'status': 'UNKNOWN', 'reason': 'DEMO_HISTORY_RESPONSE_UNRECOGNIZED', 'order': None}
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_client_id = str(row.get('clientOrderId') or row.get('newClientOrderId') or '').strip()
        if row_client_id == client_order_id:
            return {'status': 'FOUND', 'reason': 'CLIENT_ORDER_ID_FOUND_IN_DEMO_HISTORY', 'order': row}
    return {'status': 'NOT_FOUND', 'reason': 'CLIENT_ORDER_ID_NOT_FOUND_IN_DEMO_HISTORY', 'order': None}

async def r36f153_reconcile_demo_journal(journal):
    if not isinstance(journal, dict) or not journal:
        return {'resolved': True, 'retry_allowed': True, 'reason': 'NO_JOURNAL', 'journal': {}, 'changed': False}
    state = str(journal.get('state') or '').strip().upper()
    if state == 'COMPLETED':
        return {'resolved': True, 'retry_allowed': False, 'reason': 'COMPLETED_REMAINS_TERMINAL', 'journal': journal, 'changed': False}
    if state == 'REJECTED':
        return {'resolved': True, 'retry_allowed': True, 'reason': 'REJECTED_PERMITS_FRESH_RETRY', 'journal': journal, 'changed': False}
    if state not in {'PREPARED', 'SENT_AMBIGUOUS'}:
        return {'resolved': False, 'retry_allowed': False, 'reason': 'UNKNOWN_JOURNAL_STATE_BLOCKS_RETRY', 'journal': journal, 'changed': False}
    client_order_id = str(journal.get('client_order_id') or '').strip()
    if not client_order_id:
        return {'resolved': False, 'retry_allowed': False, 'reason': 'MISSING_CLIENT_ID_BLOCKS_RETRY', 'journal': journal, 'changed': False}
    lookup = await r36f153_lookup_demo_order_by_client_id(client_order_id)
    lookup_status = lookup.get('status')
    if lookup_status == 'FOUND':
        order = lookup.get('order') if isinstance(lookup.get('order'), dict) else {}
        reconciled = {**journal, 'state': 'COMPLETED', 'updated_at': now_iso(), 'success': True, 'reconciliation_status': 'FOUND', 'reconciliation_reason': lookup.get('reason'), 'order_id': str(order.get('orderId', journal.get('order_id', ''))), 'client_order_id_response': str(order.get('clientOrderId', client_order_id)), 'reconciled_order': order}
        write_json_file(R36F15_DEMO_JOURNAL_FILE, reconciled)
        return {'resolved': True, 'retry_allowed': False, 'reason': 'AMBIGUOUS_FOUND_MARKED_COMPLETED', 'journal': reconciled, 'changed': True}
    if lookup_status == 'NOT_FOUND':
        reconciled = {**journal, 'state': 'REJECTED', 'updated_at': now_iso(), 'success': False, 'reconciliation_status': 'NOT_FOUND', 'reconciliation_reason': lookup.get('reason')}
        write_json_file(R36F15_DEMO_JOURNAL_FILE, reconciled)
        return {'resolved': True, 'retry_allowed': True, 'reason': 'AMBIGUOUS_NOT_FOUND_MARKED_REJECTED', 'journal': reconciled, 'changed': True}
    return {'resolved': False, 'retry_allowed': False, 'reason': lookup.get('reason', 'AMBIGUOUS_UNKNOWN_BLOCKS_RETRY'), 'journal': journal, 'lookup': lookup, 'changed': False}

async def submit_r36f15_demo_order(preview, command_preview):
    if not R36F15_DEMO_ARM_REQUESTED:
        return {'attempted': False, 'sent': False, 'reason': 'DEMO_ARM_NOT_REQUESTED'}
    if not command_preview.get('authorized_preview'):
        return {'attempted': False, 'sent': False, 'reason': 'TELEGRAM_COMMAND_NOT_AUTHORIZED'}
    if not preview or not preview.get('payload'):
        return {'attempted': False, 'sent': False, 'reason': 'DEMO_PREVIEW_MISSING'}
    existing = read_json_file(R36F15_DEMO_JOURNAL_FILE, default={})
    reconciliation = await r36f153_reconcile_demo_journal(existing)
    log('R36F.15.3 DEMO JOURNAL RECONCILIATION = ' + canonical_json({'resolved': reconciliation.get('resolved'), 'retry_allowed': reconciliation.get('retry_allowed'), 'reason': reconciliation.get('reason'), 'changed': reconciliation.get('changed')}))
    if not reconciliation.get('resolved'):
        return {'attempted': False, 'sent': False, 'reason': 'UNRESOLVED_DEMO_JOURNAL_BLOCKS_RETRY', 'reconciliation': reconciliation, 'journal': reconciliation.get('journal', existing)}
    if not reconciliation.get('retry_allowed'):
        return {'attempted': False, 'sent': False, 'reason': 'FIRST_DEMO_ORDER_ALREADY_COMPLETED', 'reconciliation': reconciliation, 'journal': reconciliation.get('journal', existing)}
    payload = dict(preview['payload'])
    payload_hash = sha256_text(canonical_json(payload))
    prepared = {'stage': STAGE, 'state': 'PREPARED', 'created_at': now_iso(), 'endpoint': R36F14_DEMO_ORDER_ENDPOINT, 'client_order_id': payload.get('newClientOrderId'), 'payload_sha256': payload_hash, 'payload': payload, 'real_order_execution': REAL_ORDER_EXECUTION, 'prior_reconciliation_reason': reconciliation.get('reason')}
    write_json_file(R36F15_DEMO_JOURNAL_FILE, prepared)
    try:
        transport = await weex_demo_post(R36F14_DEMO_ORDER_ENDPOINT, payload)
    except Exception as exc:
        ambiguous = {**prepared, 'state': 'SENT_AMBIGUOUS', 'updated_at': now_iso(), 'error': str(exc)}
        write_json_file(R36F15_DEMO_JOURNAL_FILE, ambiguous)
        return {'attempted': True, 'sent': False, 'accepted': False, 'reason': 'DEMO_POST_EXCEPTION_JOURNALED_AMBIGUOUS', 'error': str(exc), 'journal': ambiguous}
    response = transport.get('response') if isinstance(transport, dict) else {}
    response = response if isinstance(response, dict) else {}
    success = bool(response.get('success'))
    completed = {**prepared, 'state': 'COMPLETED' if success else 'REJECTED', 'updated_at': now_iso(), 'http_status': transport.get('http_status'), 'response': response, 'success': success, 'order_id': str(response.get('orderId', '')), 'client_order_id_response': str(response.get('clientOrderId', '')), 'error_code': str(response.get('errorCode', '')), 'error_message': str(response.get('errorMessage', ''))}
    write_json_file(R36F15_DEMO_JOURNAL_FILE, completed)
    return {'attempted': True, 'sent': True, 'accepted': success, 'transport': transport, 'journal': completed}

async def load_mark_price():
    global MARK_PRICE
    data = await weex_get('/capi/v3/market/symbolPrice', params={'symbol': SYMBOL}, authenticated=False)
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
    data = await weex_get('/capi/v3/account/balance', authenticated=True)
    candidates = []
    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = key.lower()
                if key_lower in ('availablebalance', 'available_balance', 'available', 'free', 'usdtavailable'):
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
    data = await weex_get('/capi/v3/account/position/singlePosition', params={'symbol': SYMBOL}, authenticated=True)
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
    data = await weex_get('/capi/v3/market/exchangeInfo', params={'symbol': SYMBOL}, authenticated=False)
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
    return (ema_series(closes, EMA_FAST), ema_series(closes, EMA_MID), ema_series(closes, EMA_SLOW))

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
        return {'ready': False, 'reason': 'INSUFFICIENT_CANDLES_FOR_EMA200_CONFIRMATION', 'rows': len(closes)}
    current19, current50, current200 = calculate_emas(closes)
    previous19, previous50, previous200 = calculate_emas(closes[:-1])
    current_price = closes[-1]
    structure = ema_structure(current19, current50, current200)
    direction = ema_direction(structure)
    separation = ema_separation_percent(current_price, current19, current50)
    crossover = detect_ema19_50_crossover(previous19, previous50, current19, current50)
    quality_ok = separation >= MIN_EMA_19_50_SEPARATION_PERCENT
    ideal_direction = direction if quality_ok else None
    return {'ready': True, 'reason': 'EMA_ENGINE_READY', 'rows': len(closes), 'price': decimal_to_string(current_price), 'ema19': decimal_to_string(current19), 'ema50': decimal_to_string(current50), 'ema200': decimal_to_string(current200), 'structure': structure, 'direction': direction, 'ideal_direction': ideal_direction, 'ema19_50_separation_percent': decimal_to_string(separation), 'minimum_separation_percent': decimal_to_string(MIN_EMA_19_50_SEPARATION_PERCENT), 'quality_ok': quality_ok, 'fresh_crossover': crossover, 'confirmation_policy': 'NEXT_CLOSED_1M_CANDLE', 'signal_expiry_seconds': SIGNAL_EXPIRY_SECONDS}

def normalize_telegram_command(text):
    return ' '.join(str(text or '').strip().upper().split())

def parse_telegram_trade_command(text):
    normalized = normalize_telegram_command(text)
    if normalized == TELEGRAM_BUY_COMMAND:
        return {'recognized': True, 'command': normalized, 'direction': 'LONG'}
    if normalized == TELEGRAM_SELL_COMMAND:
        return {'recognized': True, 'command': normalized, 'direction': 'SHORT'}
    return {'recognized': False, 'command': normalized, 'direction': None}

def validate_telegram_command_against_signal(text, ema_snapshot, long_eligible, short_eligible):
    parsed = parse_telegram_trade_command(text)
    direction = parsed['direction']
    if not parsed['recognized']:
        return {**parsed, 'authorized_preview': False, 'reason': 'UNRECOGNIZED_COMMAND'}
    if not ema_snapshot.get('ready'):
        return {**parsed, 'authorized_preview': False, 'reason': 'EMA_ENGINE_NOT_READY'}
    ideal = ema_snapshot.get('ideal_direction')
    if ideal != direction:
        return {**parsed, 'authorized_preview': False, 'reason': 'COMMAND_DIRECTION_DOES_NOT_MATCH_IDEAL_EMA_CONDITION', 'ema_ideal_direction': ideal}
    market_ok = long_eligible if direction == 'LONG' else short_eligible
    if not market_ok:
        return {**parsed, 'authorized_preview': False, 'reason': 'COMMAND_DIRECTION_TP_MARKET_NOT_ELIGIBLE', 'ema_ideal_direction': ideal}
    return {**parsed, 'authorized_preview': True, 'reason': 'COMMAND_AND_EMA_AND_TP_DIRECTION_AGREE', 'ema_ideal_direction': ideal, 'exchange_order_sent': False}

def build_ideal_condition_alert(ema_snapshot):
    if not ema_snapshot.get('ready'):
        return None
    direction = ema_snapshot.get('ideal_direction')
    if direction not in ('LONG', 'SHORT'):
        return None
    command = TELEGRAM_BUY_COMMAND if direction == 'LONG' else TELEGRAM_SELL_COMMAND
    return f"R36F.13.2 IDEAL {direction} CONDITION | {SYMBOL}\nPrice={ema_snapshot.get('price')} EMA19={ema_snapshot.get('ema19')} EMA50={ema_snapshot.get('ema50')} EMA200={ema_snapshot.get('ema200')}\nStructure={ema_snapshot.get('structure')} EMA19/50 separation={ema_snapshot.get('ema19_50_separation_percent')}%\nManual command: {command}\nR36F.13.2 exchange execution remains disabled."

async def send_r36f12_telegram_alert(message):
    if not message:
        return {'attempted': False, 'sent': False, 'reason': 'NO_IDEAL_ALERT'}
    if not R36F12_TELEGRAM_ALERTS_ENABLED:
        return {'attempted': False, 'sent': False, 'reason': 'ALERTS_DISABLED_BY_DEFAULT'}
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {'attempted': False, 'sent': False, 'reason': 'TELEGRAM_CONFIG_MISSING'}
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'disable_web_page_preview': True}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as response:
                body = await response.text()
                return {'attempted': True, 'sent': 200 <= response.status < 300, 'http_status': response.status, 'response_preview': body[:200]}
    except Exception as exc:
        return {'attempted': True, 'sent': False, 'reason': f'{type(exc).__name__}: {exc}'}

def synthetic_r36f12_ema_telegram_tests():
    bullish = {'ready': True, 'ideal_direction': 'LONG', 'structure': 'STRONG_BULLISH', 'price': '80000', 'ema19': '80100', 'ema50': '80000', 'ema200': '79000', 'ema19_50_separation_percent': '0.125'}
    bearish = {'ready': True, 'ideal_direction': 'SHORT', 'structure': 'STRONG_BEARISH', 'price': '80000', 'ema19': '79900', 'ema50': '80000', 'ema200': '81000', 'ema19_50_separation_percent': '0.125'}
    buy = parse_telegram_trade_command('  buy   btc now ')
    sell = parse_telegram_trade_command('SELL BTC NOW')
    check('R36F12_TELEGRAM_BUY_COMMAND_PARSES_LONG', buy['recognized'] and buy['direction'] == 'LONG')
    check('R36F12_TELEGRAM_SELL_COMMAND_PARSES_SHORT', sell['recognized'] and sell['direction'] == 'SHORT')
    check('R36F12_TELEGRAM_UNKNOWN_COMMAND_REJECTED', parse_telegram_trade_command('BUY ETH NOW')['recognized'] is False)
    buy_ok = validate_telegram_command_against_signal('BUY BTC NOW', bullish, True, False)
    sell_ok = validate_telegram_command_against_signal('SELL BTC NOW', bearish, False, True)
    mismatch = validate_telegram_command_against_signal('SELL BTC NOW', bullish, True, True)
    check('R36F12_BUY_MATCHING_IDEAL_LONG_PREVIEW_APPROVED', buy_ok['authorized_preview'] is True)
    check('R36F12_SELL_MATCHING_IDEAL_SHORT_PREVIEW_APPROVED', sell_ok['authorized_preview'] is True)
    check('R36F12_DIRECTION_MISMATCH_BLOCKED', mismatch['authorized_preview'] is False)
    check('R36F12_COMMAND_PREVIEW_NEVER_SENDS_ORDER', buy_ok.get('exchange_order_sent') is False)
    return True

def build_extrema(values):
    if len(values) < 3:
        return []
    extrema = []
    for index in range(1, len(values) - 1):
        previous_value = D(values[index - 1])
        current_value = D(values[index])
        next_value = D(values[index + 1])
        if current_value >= previous_value and current_value >= next_value:
            extrema.append(current_value)
        elif current_value <= previous_value and current_value <= next_value:
            extrema.append(current_value)
    return extrema

def local_extrema_values(rows, side):
    if side == 'LONG':
        values = historical_highs(rows)
    elif side == 'SHORT':
        values = historical_lows(rows)
    else:
        raise ValueError(f'Unsupported side={side}')
    return build_extrema(values)

def cluster_extrema(extrema):
    if not extrema:
        return []
    sorted_values = sorted([D(value) for value in extrema])
    clusters = []
    current = [sorted_values[0]]
    for value in sorted_values[1:]:
        current_average = sum(current) / Decimal(len(current))
        tolerance = current_average * CLUSTER_TOLERANCE_PERCENT / Decimal('100')
        if abs(value - current_average) <= tolerance:
            current.append(value)
        else:
            clusters.append({'minimum': min(current), 'maximum': max(current), 'average': sum(current) / Decimal(len(current)), 'touches': len(current)})
            current = [value]
    clusters.append({'minimum': min(current), 'maximum': max(current), 'average': sum(current) / Decimal(len(current)), 'touches': len(current)})
    return clusters

def validate_clusters(clusters, entry_price, side):
    entry_price = D(entry_price)
    valid = []
    invalid = []
    for cluster in clusters:
        reasons = []
        touches = cluster['touches']
        average = D(cluster['average'])
        if touches < MIN_CLUSTER_TOUCHES:
            reasons.append('INSUFFICIENT_TOUCHES')
        if side == 'LONG':
            if average <= entry_price:
                reasons.append('CLUSTER_NOT_ABOVE_ENTRY')
        elif side == 'SHORT':
            if average >= entry_price:
                reasons.append('CLUSTER_NOT_BELOW_ENTRY')
        else:
            reasons.append('INVALID_DIRECTION')
        result = dict(cluster)
        result['valid'] = not reasons
        result['reasons'] = reasons
        if reasons:
            invalid.append(result)
        else:
            valid.append(result)
    if side == 'LONG':
        valid.sort(key=lambda item: item['average'])
    elif side == 'SHORT':
        valid.sort(key=lambda item: item['average'], reverse=True)
    return (valid, invalid)

def build_cluster_diagnostics(rows, entry_price, side):
    entry_price = D(entry_price)
    if side == 'LONG':
        values = historical_highs(rows)
    elif side == 'SHORT':
        values = historical_lows(rows)
    else:
        raise ValueError(f'Unsupported side={side}')
    extrema = build_extrema(values)
    clusters = cluster_extrema(extrema)
    valid, invalid = validate_clusters(clusters, entry_price, side)
    diagnostics = {'side': side, 'entry_price': decimal_to_string(entry_price), 'historical_row_count': len(rows), 'extrema_count': len(extrema), 'cluster_count': len(clusters), 'valid_cluster_count': len(valid), 'invalid_cluster_count': len(invalid), 'required_valid_clusters': REQUIRED_TP_CLUSTERS, 'valid_clusters': valid, 'invalid_clusters': invalid}
    if len(valid) >= REQUIRED_TP_CLUSTERS:
        diagnostics['failure_reason'] = None
    elif len(valid) == 1:
        diagnostics['failure_reason'] = 'ONLY_ONE_VALID_CLUSTER'
    elif len(extrema) == 0:
        diagnostics['failure_reason'] = 'NO_LOCAL_EXTREMA'
    elif len(clusters) == 0:
        diagnostics['failure_reason'] = 'NO_HISTORICAL_CLUSTERS'
    else:
        diagnostics['failure_reason'] = 'EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET'
    log(f"{side} HISTORICAL ROW COUNT = {diagnostics['historical_row_count']}")
    log(f"{side} EXTREMA COUNT = {diagnostics['extrema_count']}")
    log(f"{side} CLUSTER COUNT = {diagnostics['cluster_count']}")
    log(f"{side} VALID CLUSTER COUNT = {diagnostics['valid_cluster_count']}")
    for index, cluster in enumerate(clusters, start=1):
        log(f"{side} CLUSTER {index}: average={decimal_to_string(cluster['average'])} minimum={decimal_to_string(cluster['minimum'])} maximum={decimal_to_string(cluster['maximum'])} touches={cluster['touches']}")
    for index, cluster in enumerate(invalid, start=1):
        log(f"{side} INVALID CLUSTER {index}: average={decimal_to_string(cluster['average'])} reasons={','.join(cluster['reasons'])}")
    if diagnostics['failure_reason']:
        log(f"{side} CLUSTER DIAGNOSTIC FAILURE_REASON = {diagnostics['failure_reason']}")
    return diagnostics

def evaluate_tp_approval(diagnostics):
    valid_count = int(diagnostics.get('valid_cluster_count', 0))
    if valid_count >= REQUIRED_TP_CLUSTERS:
        approval = {'status': 'APPROVED', 'approved': True, 'required_valid_clusters': REQUIRED_TP_CLUSTERS, 'available_valid_clusters': valid_count, 'reason': 'TWO_OR_MORE_VALID_HISTORICAL_CLUSTERS'}
    else:
        failure_reason = diagnostics.get('failure_reason') or 'INSUFFICIENT_VALID_HISTORICAL_CLUSTERS'
        approval = {'status': 'REJECTED', 'approved': False, 'required_valid_clusters': REQUIRED_TP_CLUSTERS, 'available_valid_clusters': valid_count, 'reason': failure_reason}
    log(f"{STAGE}_TP_APPROVAL = {approval['status']}")
    log(f"{STAGE}_TP_APPROVAL_REASON = {approval['reason']}")
    log(f'{STAGE}_TP_REQUIRED_CLUSTERS = {REQUIRED_TP_CLUSTERS}')
    log(f'{STAGE}_TP_AVAILABLE_CLUSTERS = {valid_count}')
    return approval

def valid_clusters(rows, entry_price, side):
    entry_price = D(entry_price)
    extrema = local_extrema_values(rows, side)
    clusters = cluster_extrema(extrema)
    valid = []
    for cluster in clusters:
        if cluster['touches'] < MIN_CLUSTER_TOUCHES:
            continue
        average = cluster['average']
        if side == 'LONG':
            if average <= entry_price:
                continue
        elif side == 'SHORT':
            if average >= entry_price:
                continue
        else:
            raise ValueError(f'Unsupported side={side}')
        valid.append(cluster)
    if side == 'LONG':
        valid.sort(key=lambda c: c['average'])
    else:
        valid.sort(key=lambda c: c['average'], reverse=True)
    return valid

def calculate_tp_prices(entry_price, valid_cluster_list, direction):
    entry_price = D(entry_price)
    if len(valid_cluster_list) < REQUIRED_TP_CLUSTERS:
        raise RuntimeError('Cannot calculate complete TP set: fewer than two valid historical clusters')
    cluster1 = D(valid_cluster_list[0]['average'])
    cluster2 = D(valid_cluster_list[1]['average'])
    progress1 = TP1_PROFIT_MARGIN_PERCENT / Decimal('100')
    progress2 = TP2_PROFIT_MARGIN_PERCENT / Decimal('100')
    if direction == 'LONG':
        tp1 = entry_price + (cluster1 - entry_price) * progress1
        tp2 = entry_price + (cluster2 - entry_price) * progress2
    elif direction == 'SHORT':
        tp1 = entry_price - (entry_price - cluster1) * progress1
        tp2 = entry_price - (entry_price - cluster2) * progress2
    else:
        raise RuntimeError('Invalid TP direction')
    return {'tp1': quantize_down(tp1, PRICE_STEP), 'tp2': quantize_down(tp2, PRICE_STEP), 'tp3': {'type': 'TRAILING', 'allocation_percent': TP3_ALLOCATION_PERCENT, 'trailing_distance_percent': TP3_TRAILING_DISTANCE_PERCENT}, 'cluster1_average': cluster1, 'cluster2_average': cluster2}

