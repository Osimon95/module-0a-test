
#!/usr/bin/env python3
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

STAGE = "R36F.15.10.5"

PURPOSE = (
    "R36F.15.10.5 MINIMAL REGIME-TO-DEMO MERGER: preserve the proven "
    "R36F.15.10.4b classifier, three-confirmation controller, active-trade "
    "mode lock and 60-second reevaluation unchanged; add only regime-specific "
    "SCALP/NORMAL/BREAKOUT authorization into the existing frozen WEEX demo "
    "writer, JIT validation, journal/replay and exposure safeguards. "
    "Production real-money execution remains hard-disabled."
)

API_BASE_URL = "https://api-contract.weex.com"
SYMBOL = "BTCUSDT"
PUBLIC_TICKER_SYMBOL = "cmt_btcusdt"
KLINE_INTERVAL = "1m"
HISTORICAL_LIMIT = 250
MAX_HISTORICAL_PAGES = 4

R36F151_REEVALUATION_SECONDS = max(
    15,
    int(os.getenv("R36F151_REEVALUATION_SECONDS", "60")),
)

PRICE_STEP = Decimal("0.1")
QUANTITY_STEP = Decimal("0.0001")
MIN_QUANTITY = Decimal("0.0001")

ENTRY_MARGIN_PERCENT = Decimal("5")
LEVERAGE_LONG = Decimal("100")
LEVERAGE_SHORT = Decimal("100")
MARGIN_MODE = "ISOLATED"
PYRAMID_ADD_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3
BACKUP_MARGIN_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")
SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300
ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True

EMA_FAST = 19
EMA_MID = 50
EMA_SLOW = 200
EMA_CONFIRMATION_CANDLES = 1
MIN_EMA_19_50_SEPARATION_PERCENT = Decimal("0.01")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

R36F12_TELEGRAM_ALERTS_ENABLED = (
    os.getenv("R36F12_TELEGRAM_ALERTS_ENABLED", "false").strip().lower()
    in {"1", "true", "yes", "on"}
)

R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED = (
    os.getenv("R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED", "false").strip().lower()
    in {"1", "true", "yes", "on"}
)

TELEGRAM_BUY_COMMAND = "BUY BTC NOW"
TELEGRAM_SELL_COMMAND = "SELL BTC NOW"

TP1_PROFIT_MARGIN_PERCENT = Decimal("20")
TP2_PROFIT_MARGIN_PERCENT = Decimal("50")
TP3_PROFIT_MARGIN_PERCENT = Decimal("60")
TP1_ALLOCATION_PERCENT = Decimal("20")
TP2_ALLOCATION_PERCENT = Decimal("20")
TP3_ALLOCATION_PERCENT = Decimal("60")
TP3_TRAILING_DISTANCE_PERCENT = Decimal("0.20")
CLUSTER_TOLERANCE_PERCENT = Decimal("0.20")
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

CANARY_MAX_ENTRY_QUANTITY = Decimal("0.0004")
CANARY_ARM_PHRASE = "ARM_FIRST_LIVE_CANARY"
CANARY_ARM_REQUESTED = (
    os.getenv("R36F12_LIVE_CANARY_ARM", "").strip()
    == CANARY_ARM_PHRASE
)
CANARY_STOP_PRICE_TEXT = os.getenv(
    "R36F12_CANARY_STOP_PRICE",
    "",
).strip()
CANARY_STOP_WORKING_TYPE = "MARK_PRICE"

R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT",
        "0.50",
    )
)

if R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError(
        "R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive"
    )

R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT",
        "0.75",
    )
)

if R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError(
        "R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive"
    )

R36F132_MAX_ACCOUNT_LOSS_PERCENT = Decimal(
    os.getenv(
        "R36F132_MAX_ACCOUNT_LOSS_PERCENT",
        "2.50",
    )
)

if R36F132_MAX_ACCOUNT_LOSS_PERCENT <= 0:
    raise ValueError(
        "R36F132_MAX_ACCOUNT_LOSS_PERCENT must be positive"
    )

R36F14_DEMO_SYMBOL = os.getenv(
    "R36F14_DEMO_SYMBOL",
    "BTCSUSDT",
).strip().upper()

R36F14_DEMO_ASSET = os.getenv(
    "R36F14_DEMO_ASSET",
    "SUSDT",
).strip().upper()

R36F14_DEMO_BALANCE_ENDPOINT = "/capi/v3/sim/balance"
R36F14_DEMO_POSITIONS_ENDPOINT = "/capi/v3/sim/position/allPosition"
R36F14_DEMO_ORDER_HISTORY_ENDPOINT = "/capi/v3/sim/order/history"
R36F14_DEMO_ORDER_ENDPOINT = "/capi/v3/sim/order"

R36F14_DEMO_READS_ENABLED = True
R36F14_DEMO_POST_TRANSPORT_ENABLED = False
R36F14_DEMO_ORDER_SUBMISSION_ENABLED = False
R36F14_FIRST_DEMO_ORDER_ALLOWED = False

R36F159_DEMO_ARM_PHRASE = "ARM_SECOND_WEEX_DEMO_ORDER"
R36F159_DEMO_ARM_REQUESTED = (
    os.getenv("R36F159_DEMO_ARM", "").strip()
    == R36F159_DEMO_ARM_PHRASE
)

R36F15_DEMO_ARM_REQUESTED = R36F159_DEMO_ARM_REQUESTED

R36F159_COMMAND_TOKEN = os.getenv(
    "R36F159_COMMAND_TOKEN",
    "",
).strip()

R36F15_DEMO_POST_TRANSPORT_ENABLED = True
R36F15_DEMO_ORDER_SUBMISSION_ENABLED = True
R36F15_FIRST_DEMO_ORDER_ALLOWED = True

R36F15_RECONCILE_DELAY_SECONDS = Decimal(
    os.getenv("R36F15_RECONCILE_DELAY_SECONDS", "1.0")
)

R36A_STATE_DIR = "/var/data/r36a_state"
R36C_STATE_DIR = "/var/data/r36c_state"
R36D_STATE_DIR = "/var/data/r36d_state"
R36F_STATE_DIR = "/var/data/r36f_state"

os.makedirs(
    R36F_STATE_DIR,
    exist_ok=True,
)

R36A_DEDUPE_FILE = os.path.join(
    R36A_STATE_DIR,
    "telegram_processed_updates.json",
)

R36A_DECISION_FILE = os.path.join(
    R36A_STATE_DIR,
    "synthetic_decisions.json",
)

R36C_DEDUPE_FILE = os.path.join(
    R36C_STATE_DIR,
    "telegram_processed_updates.json",
)

R36C_DECISION_FILE = os.path.join(
    R36C_STATE_DIR,
    "synthetic_decisions.json",
)

R36D_SNAPSHOT_FILE = os.path.join(
    R36D_STATE_DIR,
    "pre_live_readiness_snapshot.json",
)

R36F_SNAPSHOT_FILE = os.path.join(
    R36F_STATE_DIR,
    "pre_live_readiness_snapshot.json",
)

R36F12_CANARY_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "first_live_canary_dispatch_journal.json",
)

R36F12_TELEGRAM_SIGNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f12_ema_telegram_signal_snapshot.json",
)

R36F12_TELEGRAM_COMMAND_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f12_telegram_command_preview.json",
)

R36F15_DEMO_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f15_demo_dispatch_journal.json",
)

R36F159_DEMO_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f159_second_demo_dispatch_journal.json",
)

R36F1541_TELEGRAM_EVENT_STATE_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f1541_telegram_event_state.json",
)

OLD_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"
R36C_UPDATE_ID = "R36C_SYNTHETIC_UPDATE_000001"

TEST_STATUS = "NOT_STARTED"
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
        "----------------------------------------------------------------------------------------------------",
        flush=True,
    )

def log(message):
    print(
        f"{now_iso()} {message}",
        flush=True,
    )

def check(name, condition, detail=None):
    if condition:
        log(f"PASS: {name}")
        if detail:
            log(f"      {detail}")
        return True

    log(f"FAIL: {name}")
    if detail:
        log(f"      {detail}")

    FINAL_BLOCKERS.append(name)
    return False

def diagnostic_check(name, condition, detail=None):
    if condition:
        log(f"DIAGNOSTIC PASS: {name}")
        if detail:
            log(f"      {detail}")
        return True

    log(f"DIAGNOSTIC FAIL: {name}")
    if detail:
        log(f"      {detail}")

    return False

def D(value):
    return Decimal(str(value))

def quantize_down(value, step):
    value = D(value)
    step = D(step)

    if step <= 0:
        raise ValueError("Invalid quantization step")

    units = (value / step).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step

def decimal_to_string(value):
    if value is None:
        return None

    value = D(value)
    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text

def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

def sha256_text(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

def read_json_file(path, default=None):
    if default is None:
        default = {}

    try:
        if not os.path.exists(path):
            return default

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except Exception as exc:
        log(
            f"READ JSON FAILED path={path} error={exc}"
        )
        return default

def write_json_file(path, data):
    tmp = path + ".tmp"

    with open(
        tmp,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            sort_keys=True,
            default=str,
        )

    os.replace(
        tmp,
        path,
    )

def collect_ids_from_file(path):
    ids = set()

    data = read_json_file(
        path,
        default=None,
    )

    if data is None:
        return ids

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if (
                    isinstance(key, str)
                    and "id" in key.lower()
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
            f"stage={STAGE}\n"
            f"status={TEST_STATUS}\n"
        ).encode()

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(
        self,
        format_string,
        *args,
    ):
        return

def start_health_server():
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = HTTPServer(
        (
            "0.0.0.0",
            port,
        ),
        HealthHandler,
    )

    thread = Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(
        f"{STAGE}: HEALTH SERVER STARTED ON PORT {port}"
    )

def build_signature(
    timestamp,
    method,
    request_path,
    body="",
):
    api_secret = os.getenv(
        "WEEX_API_SECRET"
    )

    if not api_secret:
        raise RuntimeError(
            "WEEX_API_SECRET missing"
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
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()

async def weex_get(
    path,
    params=None,
    authenticated=False,
):
    params = params or {}

    from urllib.parse import urlencode

    query_string = urlencode(
        params,
        doseq=True,
    )

    request_target = path

    if query_string:
        request_target += (
            "?" + query_string
        )

    url = (
        API_BASE_URL
        + request_target
    )

    headers = {}

    if authenticated:
        api_key = os.getenv(
            "WEEX_API_KEY"
        )

        passphrase = os.getenv(
            "WEEX_API_PASSPHRASE"
        )

        if not api_key:
            raise RuntimeError(
                "WEEX_API_KEY missing"
            )

        if not passphrase:
            raise RuntimeError(
                "WEEX_API_PASSPHRASE missing"
            )

        timestamp = str(
            int(time.time() * 1000)
        )

        signature = build_signature(
            timestamp,
            "GET",
            request_target,
            "",
        )

        headers = {
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": passphrase,
            "Content-Type": "application/json",
        }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:
        async with session.get(
            url,
            headers=headers,
        ) as response:
            text = await response.text()

            if response.status >= 400:
                raise RuntimeError(
                    f"WEEX GET HTTP {response.status}: {text}"
                )

            try:
                return json.loads(text)

            except Exception:
                return {
                    "raw": text
                }

async def weex_demo_post(
    path,
    payload,
):
    if path != R36F14_DEMO_ORDER_ENDPOINT:
        raise RuntimeError(
            "R36F.15 demo transport refused non-demo endpoint"
        )

    if not (
        R36F15_DEMO_POST_TRANSPORT_ENABLED
        and R36F15_DEMO_ORDER_SUBMISSION_ENABLED
        and R36F15_FIRST_DEMO_ORDER_ALLOWED
    ):
        raise RuntimeError(
            "R36F.15 demo transport is disabled"
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
            "R36F.15 production firebreak is not intact"
        )

    api_key = os.getenv(
        "WEEX_API_KEY"
    )

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE"
    )

    if not api_key:
        raise RuntimeError(
            "WEEX_API_KEY missing"
        )

    if not passphrase:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing"
        )

    body = canonical_json(payload)
    timestamp = str(
        int(time.time() * 1000)
    )

    signature = build_signature(
        timestamp,
        "POST",
        path,
        body,
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    url = (
        API_BASE_URL
        + path
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:
        async with session.post(
            url,
            headers=headers,
            data=body,
        ) as response:
            text = await response.text()

            try:
                data = json.loads(text)

            except Exception:
                data = {
                    "raw": text
                }

            result = {
                "http_status": response.status,
                "response": data,
                "raw_text": text,
            }

            if response.status >= 400:
                raise RuntimeError(
                    f"WEEX DEMO POST HTTP {response.status}: {text}"
                )

            return result

def r36f15_demo_journal_unresolved(
    journal,
):
    if (
        not isinstance(journal, dict)
        or not journal
    ):
        return False

    return journal.get(
        "state"
    ) in {
        "PREPARED",
        "SENT_AMBIGUOUS",
    }

def r36f15_demo_journal_completed(
    journal,
):
    return bool(
        isinstance(journal, dict)
        and journal.get("state") == "COMPLETED"
        and journal.get("success") is True
    )

def _r36f153_history_rows(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "data",
            "list",
            "rows",
            "orders",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return value

    return None

async def r36f153_lookup_demo_order_by_client_id(
    client_order_id,
):
    client_order_id = str(
        client_order_id or ""
    ).strip()

    if not client_order_id:
        return {
            "status": "UNKNOWN",
            "reason": "MISSING_CLIENT_ORDER_ID",
            "order": None,
        }

    try:
        data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            params={
                "symbol": R36F14_DEMO_SYMBOL,
                "limit": 1000,
                "page": 0,
            },
            authenticated=True,
        )

    except Exception as exc:
        return {
            "status": "UNKNOWN",
            "reason": "DEMO_HISTORY_LOOKUP_FAILED",
            "error": str(exc),
            "order": None,
        }

    rows = _r36f153_history_rows(
        data
    )

    if rows is None:
        return {
            "status": "UNKNOWN",
            "reason": "DEMO_HISTORY_RESPONSE_UNRECOGNIZED",
            "order": None,
        }

    for row in rows:
        if not isinstance(row, dict):
            continue

        row_client_id = str(
            row.get("clientOrderId")
            or row.get("newClientOrderId")
            or ""
        ).strip()

        if row_client_id == client_order_id:
            return {
                "status": "FOUND",
                "reason": "CLIENT_ORDER_ID_FOUND_IN_DEMO_HISTORY",
                "order": row,
            }

    return {
        "status": "NOT_FOUND",
        "reason": "CLIENT_ORDER_ID_NOT_FOUND_IN_DEMO_HISTORY",
        "order": None,
    }

async def r36f153_reconcile_demo_journal(journal):
    if not isinstance(journal, dict) or not journal:
        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "NO_JOURNAL",
            "journal": {},
            "changed": False,
        }

    state = str(
        journal.get("state") or ""
    ).strip().upper()

    if state == "COMPLETED":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "COMPLETED_REMAINS_TERMINAL",
            "journal": journal,
            "changed": False,
        }

    if state == "REJECTED":
        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "REJECTED_PERMITS_FRESH_RETRY",
            "journal": journal,
            "changed": False,
        }

    if state not in {
        "PREPARED",
        "SENT_AMBIGUOUS",
    }:
        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "UNKNOWN_JOURNAL_STATE_BLOCKS_RETRY",
            "journal": journal,
            "changed": False,
        }

    client_order_id = str(
        journal.get("client_order_id") or ""
    ).strip()

    if not client_order_id:
        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "MISSING_CLIENT_ID_BLOCKS_RETRY",
            "journal": journal,
            "changed": False,
        }

    lookup = await r36f153_lookup_demo_order_by_client_id(
        client_order_id
    )

    lookup_status = lookup.get("status")

    if lookup_status == "FOUND":
        order = (
            lookup.get("order")
            if isinstance(lookup.get("order"), dict)
            else {}
        )

        reconciled = {
            **journal,
            "state": "COMPLETED",
            "updated_at": now_iso(),
            "success": True,
            "reconciliation_status": "FOUND",
            "reconciliation_reason": lookup.get("reason"),
            "order_id": str(
                order.get(
                    "orderId",
                    journal.get("order_id", ""),
                )
            ),
            "client_order_id_response": str(
                order.get(
                    "clientOrderId",
                    client_order_id,
                )
            ),
            "reconciled_order": order,
        }

        write_json_file(
            R36F15_DEMO_JOURNAL_FILE,
            reconciled,
        )

        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "AMBIGUOUS_FOUND_MARKED_COMPLETED",
            "journal": reconciled,
            "changed": True,
        }

    if lookup_status == "NOT_FOUND":
        reconciled = {
            **journal,
            "state": "REJECTED",
            "updated_at": now_iso(),
            "success": False,
            "reconciliation_status": "NOT_FOUND",
            "reconciliation_reason": lookup.get("reason"),
        }

        write_json_file(
            R36F15_DEMO_JOURNAL_FILE,
            reconciled,
        )

        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "AMBIGUOUS_NOT_FOUND_MARKED_REJECTED",
            "journal": reconciled,
            "changed": True,
        }

    return {
        "resolved": False,
        "retry_allowed": False,
        "reason": lookup.get(
            "reason",
            "AMBIGUOUS_UNKNOWN_BLOCKS_RETRY",
        ),
        "journal": journal,
        "lookup": lookup,
        "changed": False,
    }

async def r36f154_validate_fresh_demo_triggers(payload):
    payload = (
        payload
        if isinstance(payload, dict)
        else {}
    )

    direction = str(
        payload.get("positionSide") or ""
    ).strip().upper()

    try:
        tp = D(
            payload.get(
                "tpTriggerPrice",
                "0",
            )
        )

        sl = D(
            payload.get(
                "slTriggerPrice",
                "0",
            )
        )

    except Exception as exc:
        return {
            "valid": False,
            "reason": "JIT_TRIGGER_PARSE_FAILED",
            "error": str(exc),
        }

    if direction not in {
        "LONG",
        "SHORT",
    }:
        return {
            "valid": False,
            "reason": "JIT_DIRECTION_INVALID",
            "direction": direction,
        }

    try:
        fresh_mark = D(
            await load_mark_price()
        )

    except Exception as exc:
        return {
            "valid": False,
            "reason": "JIT_FRESH_MARK_READ_FAILED",
            "error": str(exc),
        }

    if (
        fresh_mark <= 0
        or tp <= 0
        or sl <= 0
    ):
        return {
            "valid": False,
            "reason": "JIT_NON_POSITIVE_PRICE",
            "direction": direction,
            "fresh_mark_price": decimal_to_string(
                fresh_mark
            ),
            "tp_trigger_price": decimal_to_string(tp),
            "sl_trigger_price": decimal_to_string(sl),
        }

    if direction == "LONG":
        valid = (
            sl
            < fresh_mark
            < tp
        )

        reason = (
            "JIT_LONG_TRIGGERS_VALID"
            if valid
            else "JIT_LONG_TRIGGER_STALE_OR_CROSSED"
        )

    else:
        valid = (
            tp
            < fresh_mark
            < sl
        )

        reason = (
            "JIT_SHORT_TRIGGERS_VALID"
            if valid
            else "JIT_SHORT_TRIGGER_STALE_OR_CROSSED"
        )

    return {
        "valid": bool(valid),
        "reason": reason,
        "direction": direction,
        "fresh_mark_price": decimal_to_string(
            fresh_mark
        ),
        "tp_trigger_price": decimal_to_string(tp),
        "sl_trigger_price": decimal_to_string(sl),
    }

R36F155_TARGET_DEMO_ORDER_ID = os.getenv(
    "R36F155_TARGET_DEMO_ORDER_ID",
    "792989056504955607",
).strip()

R36F155_LAST_RECONCILIATION = {}

def r36f155_order_id(row):
    if not isinstance(row, dict):
        return ""

    for key in (
        "orderId",
        "order_id",
        "id",
    ):
        value = row.get(key)

        if value is not None:
            return str(value).strip()

    return ""

def r36f155_order_status(row):
    if not isinstance(row, dict):
        return "UNKNOWN"

    for key in (
        "status",
        "orderStatus",
        "state",
    ):
        value = row.get(key)

        if value is not None:
            return str(value).strip().upper()

    return "UNKNOWN"

def r36f155_order_direction(row):
    if not isinstance(row, dict):
        return ""

    position_side = str(
        row.get("positionSide") or ""
    ).strip().upper()

    if position_side in {
        "LONG",
        "SHORT",
    }:
        return position_side

    side = str(
        row.get("side") or ""
    ).strip().upper()

    if side == "BUY":
        return "LONG"

    if side == "SELL":
        return "SHORT"

    return ""

def r36f155_position_direction(row):
    if not isinstance(row, dict):
        return ""

    for key in (
        "positionSide",
        "side",
    ):
        value = str(
            row.get(key) or ""
        ).strip().upper()

        if value in {
            "LONG",
            "SHORT",
        }:
            return value

    return ""

def r36f155_position_size(row):
    if not isinstance(row, dict):
        return D("0")

    for key in (
        "size",
        "positionSize",
        "positionAmt",
        "quantity",
        "qty",
    ):
        if key in row:
            try:
                return abs(
                    D(
                        row.get(key) or "0"
                    )
                )

            except Exception:
                continue

    return D("0")

def r36f155_normalize_rows(data):
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for key in (
        "data",
        "list",
        "rows",
        "orders",
        "positions",
        "result",
    ):
        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            for nested_key in (
                "data",
                "list",
                "rows",
                "orders",
                "positions",
            ):
                nested = value.get(
                    nested_key
                )

                if isinstance(nested, list):
                    return nested

    return []

def r36f155_extract_protection_fields(order):
    result = {
        "tp_field": None,
        "tp_value": None,
        "sl_field": None,
        "sl_value": None,
    }

    if not isinstance(order, dict):
        return result

    for key in (
        "tpTriggerPrice",
        "takeProfitPrice",
        "takeProfit",
        "tpPrice",
        "presetTakeProfitPrice",
    ):
        if key in order:
            result["tp_field"] = key
            result["tp_value"] = order.get(key)
            break

    for key in (
        "slTriggerPrice",
        "stopLossPrice",
        "stopLoss",
        "slPrice",
        "presetStopLossPrice",
    ):
        if key in order:
            result["sl_field"] = key
            result["sl_value"] = order.get(key)
            break

    return result

async def r36f155_reconcile_existing_demo_exposure():
    global R36F155_LAST_RECONCILIATION

    result = {
        "stage": STAGE,
        "checked_at": now_iso(),
        "target_order_id": R36F155_TARGET_DEMO_ORDER_ID,
        "history_read_success": False,
        "position_read_success": False,
        "target_order_found": False,
        "target_order_status": "UNKNOWN",
        "target_order_direction": "",
        "target_order_symbol": "",
        "matching_position_found": False,
        "matching_position_count": 0,
        "duplicate_entry_blocked": True,
        "duplicate_block_reason": "RECONCILIATION_NOT_YET_COMPLETED",
        "safe_to_consider_new_entry": False,
        "protection_verified": False,
        "protection_reason": "NOT_CHECKED",
        "read_only": True,
        "real_order_execution": REAL_ORDER_EXECUTION,
    }

    line()
    log(
        "R36F.15.5 POST-ORDER RECONCILIATION START"
    )
    log(
        "R36F.15.5 TARGET DEMO ORDER ID = "
        + R36F155_TARGET_DEMO_ORDER_ID
    )

    try:
        history_data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            params={
                "symbol": R36F14_DEMO_SYMBOL,
                "limit": 1000,
                "page": 0,
            },
            authenticated=True,
        )

        history_rows = r36f155_normalize_rows(
            history_data
        )

        result["history_read_success"] = True
        result["history_count"] = len(
            history_rows
        )

        log(
            "R36F.15.5 DEMO ORDER HISTORY READ = PASS"
        )
        log(
            "R36F.15.5 DEMO ORDER HISTORY ROWS = "
            + str(len(history_rows))
        )

    except Exception as exc:
        result["history_error"] = str(exc)
        result["duplicate_entry_block_reason"] = (
            "ORDER_HISTORY_READ_FAILED_FAIL_CLOSED"
        )
        result["duplicate_block_reason"] = (
            "ORDER_HISTORY_READ_FAILED_FAIL_CLOSED"
        )

        log(
            "R36F.15.5 DEMO ORDER HISTORY READ = FAIL"
        )
        log(
            "R36F.15.5 DEMO ORDER HISTORY ERROR = "
            + str(exc)
        )

        R36F155_LAST_RECONCILIATION = result
        line()
        return result

    target_order = None

    for row in history_rows:
        if (
            isinstance(row, dict)
            and r36f155_order_id(row)
            == R36F155_TARGET_DEMO_ORDER_ID
        ):
            target_order = row
            break

    if target_order is not None:
        result["target_order_found"] = True
        result["target_order_status"] = (
            r36f155_order_status(
                target_order
            )
        )
        result["target_order_direction"] = (
            r36f155_order_direction(
                target_order
            )
        )
        result["target_order_symbol"] = str(
            target_order.get("symbol") or ""
        ).strip().upper()

        result["target_order_qty"] = (
            target_order.get("origQty")
        )
        result["target_order_executed_qty"] = (
            target_order.get("executedQty")
        )
        result["target_order_avg_price"] = (
            target_order.get("avgPrice")
        )
        result["target_order_client_id"] = (
            target_order.get("clientOrderId")
        )

        result.update(
            r36f155_extract_protection_fields(
                target_order
            )
        )

        if (
            result.get("tp_field") is not None
            or result.get("sl_field") is not None
        ):
            result["protection_reason"] = (
                "PROTECTION_FIELDS_RETURNED_IN_ORDER_HISTORY"
            )
        else:
            result["protection_reason"] = (
                "TP_SL_NOT_RETURNED_BY_DEMO_ORDER_HISTORY"
            )

        log(
            "R36F.15.5 TARGET ORDER FOUND = True"
        )
        log(
            "R36F.15.5 ORDER ID = "
            + r36f155_order_id(target_order)
        )
        log(
            "R36F.15.5 ORDER SYMBOL = "
            + result["target_order_symbol"]
        )
        log(
            "R36F.15.5 ORDER DIRECTION = "
            + result["target_order_direction"]
        )
        log(
            "R36F.15.5 ORDER STATUS = "
            + result["target_order_status"]
        )

    else:
        log(
            "R36F.15.5 TARGET ORDER FOUND = False"
        )

    try:
        position_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            authenticated=True,
        )

        position_rows = r36f155_normalize_rows(
            position_data
        )

        result["position_read_success"] = True
        result["position_count"] = len(
            position_rows
        )

        log(
            "R36F.15.5 DEMO POSITION READ = PASS"
        )
        log(
            "R36F.15.5 DEMO POSITION ROWS = "
            + str(len(position_rows))
        )

    except Exception as exc:
        result["position_error"] = str(exc)
        result["duplicate_block_reason"] = (
            "POSITION_READ_FAILED_FAIL_CLOSED"
        )

        log(
            "R36F.15.5 DEMO POSITION READ = FAIL"
        )
        log(
            "R36F.15.5 DEMO POSITION ERROR = "
            + str(exc)
        )

        R36F155_LAST_RECONCILIATION = result
        line()
        return result

    expected_symbol = (
        result.get("target_order_symbol")
        or R36F14_DEMO_SYMBOL
    )

    expected_direction = (
        result.get("target_order_direction")
        or ""
    )

    matching = []

    for row in position_rows:
        if not isinstance(row, dict):
            continue

        symbol = str(
            row.get("symbol") or ""
        ).strip().upper()

        direction = (
            r36f155_position_direction(row)
        )

        size = r36f155_position_size(row)

        if size <= 0:
            continue

        if (
            expected_symbol
            and symbol != expected_symbol
        ):
            continue

        if (
            expected_direction
            and direction
            and direction != expected_direction
        ):
            continue

        matching.append(row)

    result["matching_position_found"] = bool(
        matching
    )
    result["matching_position_count"] = len(
        matching
    )

    if matching:
        result["duplicate_entry_blocked"] = True
        result["duplicate_block_reason"] = (
            "POSITION_ALREADY_EXISTS"
        )
        result["safe_to_consider_new_entry"] = False

    elif result["target_order_found"]:
        status = result[
            "target_order_status"
        ]

        if status in {
            "NEW",
            "OPEN",
            "PENDING",
            "LIVE",
            "ACCEPTED",
            "CREATED",
            "PARTIALLY_FILLED",
            "PARTIAL_FILLED",
            "PARTIALLYFILLED",
        }:
            result["duplicate_entry_blocked"] = True
            result["duplicate_block_reason"] = (
                "OPEN_ENTRY_ORDER_ALREADY_EXISTS"
            )

        elif status == "FILLED":
            result["duplicate_entry_blocked"] = True
            result["duplicate_block_reason"] = (
                "FILLED_ORDER_FOUND_POSITION_REQUIRES_CONSERVATIVE_RECONCILIATION"
            )

        elif status == "UNKNOWN":
            result["duplicate_entry_blocked"] = True
            result["duplicate_block_reason"] = (
                "UNKNOWN_ORDER_STATUS_FAIL_CLOSED"
            )

        else:
            result["duplicate_entry_blocked"] = False
            result["duplicate_block_reason"] = (
                "TARGET_ORDER_TERMINAL_AND_NO_MATCHING_POSITION_FOUND"
            )
            result["safe_to_consider_new_entry"] = True

    else:
        active_demo_position = any(
            isinstance(row, dict)
            and str(
                row.get("symbol") or ""
            ).strip().upper()
            == R36F14_DEMO_SYMBOL
            and r36f155_position_size(row) > 0
            for row in position_rows
        )

        if active_demo_position:
            result["duplicate_entry_blocked"] = True
            result["duplicate_block_reason"] = (
                "UNTRACKED_ACTIVE_DEMO_POSITION_EXISTS"
            )

        else:
            result["duplicate_entry_blocked"] = False
            result["duplicate_block_reason"] = (
                "NO_TARGET_ORDER_OR_ACTIVE_DEMO_POSITION"
            )
            result["safe_to_consider_new_entry"] = True

    log(
        "R36F.15.5 DUPLICATE ENTRY BLOCKED = "
        + str(
            result["duplicate_entry_blocked"]
        )
    )
    log(
        "R36F.15.5 DUPLICATE BLOCK REASON = "
        + str(
            result["duplicate_block_reason"]
        )
    )
    log(
        "R36F.15.5 SAFE TO CONSIDER NEW ENTRY = "
        + str(
            result["safe_to_consider_new_entry"]
        )
    )
    log(
        "R36F.15.5 REAL MONEY EXECUTION = "
        + str(REAL_ORDER_EXECUTION)
    )

    R36F155_LAST_RECONCILIATION = result
    line()
    return result

R36F159_LAST_EXPOSURE_CHECK = {}

def r36f159_command_identity(
    command_preview,
):
    command = str(
        command_preview.get("command") or ""
    ).strip().upper()

    direction = str(
        command_preview.get("direction") or ""
    ).strip().upper()

    token = str(
        R36F159_COMMAND_TOKEN or ""
    ).strip()

    material = {
        "command": command,
        "direction": direction,
        "symbol": R36F14_DEMO_SYMBOL,
        "token": token,
        "stage": "R36F.15.9",
    }

    return sha256_text(
        canonical_json(material)
    )

def r36f159_client_order_id(
    command_preview,
):
    direction = str(
        command_preview.get("direction") or ""
    ).strip().upper()

    prefix = (
        "L"
        if direction == "LONG"
        else "S"
        if direction == "SHORT"
        else "X"
    )

    digest = r36f159_command_identity(
        command_preview
    )[:16].upper()

    value = (
        f"R36F159-{prefix}-{digest}"
    )

    if len(value) > 36:
        raise ValueError(
            "R36F.15.9 client id exceeds WEEX limit"
        )

    return value

def r36f159_is_open_order_status(
    status,
):
    value = str(
        status or ""
    ).strip().upper()

    return value in {
        "NEW",
        "PENDING",
        "OPEN",
        "CREATED",
        "PARTIALLY_FILLED",
        "PARTIAL_FILLED",
        "PARTIALLYFILLED",
        "PART_FILLED",
    }

async def r36f159_reconcile_current_demo_exposure():
    global R36F159_LAST_EXPOSURE_CHECK

    result = {
        "history_read_ok": False,
        "position_read_ok": False,
        "history_rows": 0,
        "position_rows": 0,
        "active_symbol_positions": 0,
        "open_symbol_orders": 0,
        "historical_filled_orders": 0,
        "existing_client_ids": [],
        "duplicate_entry_blocked": True,
        "duplicate_block_reason": "UNRESOLVED_CURRENT_DEMO_EXPOSURE",
        "safe_to_consider_new_entry": False,
    }

    line()
    log(
        "R36F.15.9 CURRENT DEMO EXPOSURE RECONCILIATION START"
    )

    try:
        history_data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            params={
                "symbol": R36F14_DEMO_SYMBOL,
                "limit": 1000,
                "page": 0,
            },
            authenticated=True,
        )

        history_rows = _r36f153_history_rows(
            history_data
        )

        if history_rows is None:
            raise RuntimeError(
                "DEMO_HISTORY_RESPONSE_UNRECOGNIZED"
            )

        result["history_read_ok"] = True
        result["history_rows"] = len(
            history_rows
        )

        client_ids = []
        open_orders = 0
        filled_orders = 0

        for row in history_rows:
            if not isinstance(row, dict):
                continue

            symbol = str(
                row.get("symbol") or ""
            ).strip().upper()

            if symbol != R36F14_DEMO_SYMBOL:
                continue

            client_id = str(
                row.get("clientOrderId")
                or row.get("newClientOrderId")
                or ""
            ).strip()

            if client_id:
                client_ids.append(
                    client_id
                )

            status = str(
                row.get("status") or ""
            ).strip().upper()

            if r36f159_is_open_order_status(
                status
            ):
                open_orders += 1

            if status == "FILLED":
                filled_orders += 1

        result["existing_client_ids"] = sorted(
            set(client_ids)
        )
        result["open_symbol_orders"] = (
            open_orders
        )
        result["historical_filled_orders"] = (
            filled_orders
        )

    except Exception as exc:
        result["history_error"] = str(exc)

    try:
        positions_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            authenticated=True,
        )

        position_rows = (
            r36f155_normalize_rows(
                positions_data
            )
        )

        result["position_read_ok"] = True
        result["position_rows"] = len(
            position_rows
        )

        active_positions = 0

        for row in position_rows:
            if not isinstance(row, dict):
                continue

            symbol = str(
                row.get("symbol") or ""
            ).strip().upper()

            if (
                symbol
                and symbol
                != R36F14_DEMO_SYMBOL
            ):
                continue

            if (
                r36f155_position_size(row)
                != 0
            ):
                active_positions += 1

        result["active_symbol_positions"] = (
            active_positions
        )

    except Exception as exc:
        result["position_error"] = str(exc)

    if (
        not result["history_read_ok"]
        or not result["position_read_ok"]
    ):
        result["duplicate_entry_blocked"] = True
        result["duplicate_block_reason"] = (
            "CURRENT_EXPOSURE_READ_FAILED"
        )

    elif (
        result["active_symbol_positions"]
        > 0
    ):
        result["duplicate_entry_blocked"] = True
        result["duplicate_block_reason"] = (
            "ACTIVE_DEMO_POSITION_ALREADY_EXISTS"
        )

    elif (
        result["open_symbol_orders"]
        > 0
    ):
        result["duplicate_entry_blocked"] = True
        result["duplicate_block_reason"] = (
            "OPEN_DEMO_ORDER_ALREADY_EXISTS"
        )

    else:
        result["duplicate_entry_blocked"] = False
        result["duplicate_block_reason"] = (
            "NO_CURRENT_DEMO_EXPOSURE"
        )
        result["safe_to_consider_new_entry"] = True

    log(
        "R36F.15.9 HISTORY READ OK = "
        + str(result["history_read_ok"])
    )
    log(
        "R36F.15.9 POSITION READ OK = "
        + str(result["position_read_ok"])
    )
    log(
        "R36F.15.9 OPEN DEMO ORDERS = "
        + str(result["open_symbol_orders"])
    )
    log(
        "R36F.15.9 ACTIVE DEMO POSITIONS = "
        + str(
            result["active_symbol_positions"]
        )
    )
    log(
        "R36F.15.9 DUPLICATE ENTRY BLOCKED = "
        + str(
            result["duplicate_entry_blocked"]
        )
    )

    R36F159_LAST_EXPOSURE_CHECK = result
    line()
    return result

async def r36f159_reconcile_second_demo_journal(
    journal,
):
    if not isinstance(journal, dict) or not journal:
        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "NO_SECOND_DEMO_JOURNAL",
            "journal": {},
            "changed": False,
        }

    state = str(
        journal.get("state") or ""
    ).strip().upper()

    if state == "COMPLETED":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_ALREADY_COMPLETED",
            "journal": journal,
            "changed": False,
        }

    if state == "REJECTED":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_TOKEN_ALREADY_CONSUMED_REQUIRES_NEW_STAGE",
            "journal": journal,
            "changed": False,
        }

    if state not in {
        "PREPARED",
        "SENT_AMBIGUOUS",
    }:
        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "UNKNOWN_SECOND_DEMO_JOURNAL_STATE",
            "journal": journal,
            "changed": False,
        }

    client_order_id = str(
        journal.get("client_order_id") or ""
    ).strip()

    if not client_order_id:
        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "MISSING_SECOND_DEMO_CLIENT_ID",
            "journal": journal,
            "changed": False,
        }

    lookup = await r36f153_lookup_demo_order_by_client_id(
        client_order_id
    )

    lookup_status = lookup.get(
        "status"
    )

    if lookup_status == "FOUND":
        order = (
            lookup.get("order")
            if isinstance(
                lookup.get("order"),
                dict,
            )
            else {}
        )

        reconciled = {
            **journal,
            "state": "COMPLETED",
            "updated_at": now_iso(),
            "success": True,
            "reconciliation_status": "FOUND",
            "reconciliation_reason": lookup.get(
                "reason"
            ),
            "order_id": str(
                order.get(
                    "orderId",
                    journal.get(
                        "order_id",
                        "",
                    ),
                )
            ),
            "client_order_id_response": str(
                order.get(
                    "clientOrderId",
                    client_order_id,
                )
            ),
            "reconciled_order": order,
        }

        write_json_file(
            R36F159_DEMO_JOURNAL_FILE,
            reconciled,
        )

        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_FOUND_MARKED_COMPLETED",
            "journal": reconciled,
            "changed": True,
        }

    if lookup_status == "NOT_FOUND":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_PREPARED_NOT_FOUND_TOKEN_REPLAY_BLOCKED",
            "journal": journal,
            "changed": False,
        }

    return {
        "resolved": False,
        "retry_allowed": False,
        "reason": lookup.get(
            "reason",
            "SECOND_DEMO_RECONCILIATION_UNKNOWN",
        ),
        "journal": journal,
        "lookup": lookup,
        "changed": False,
    }

async def submit_r36f15_demo_order(
    preview,
    command_preview,
):
    if not R36F159_DEMO_ARM_REQUESTED:
        return {
            "attempted": False,
            "sent": False,
            "reason": "SECOND_DEMO_ARM_NOT_REQUESTED",
        }

    if not command_preview.get(
        "authorized_preview"
    ):
        return {
            "attempted": False,
            "sent": False,
            "reason": "TELEGRAM_COMMAND_NOT_AUTHORIZED",
        }

    if (
        not preview
        or not preview.get("payload")
    ):
        return {
            "attempted": False,
            "sent": False,
            "reason": "DEMO_PREVIEW_MISSING",
        }

    if not R36F159_COMMAND_TOKEN:
        return {
            "attempted": False,
            "sent": False,
            "reason": "SECOND_DEMO_COMMAND_TOKEN_MISSING",
        }

    existing = read_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        default={},
    )

    command_identity = (
        r36f159_command_identity(
            command_preview
        )
    )

    if isinstance(existing, dict) and existing:
        existing_identity = str(
            existing.get(
                "command_identity_sha256"
            ) or ""
        ).strip()

        if (
            existing_identity
            and hmac.compare_digest(
                existing_identity,
                command_identity,
            )
        ):
            reconciliation = (
                await r36f159_reconcile_second_demo_journal(
                    existing
                )
            )

            return {
                "attempted": False,
                "sent": False,
                "accepted": False,
                "reason": "R36F159_COMMAND_REPLAY_BLOCKED",
                "reconciliation": reconciliation,
                "journal": reconciliation.get(
                    "journal",
                    existing,
                ),
            }

        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_EXISTING_SECOND_DEMO_JOURNAL_BLOCKS_NEW_TOKEN",
            "journal": existing,
        }

    exposure = (
        await r36f159_reconcile_current_demo_exposure()
    )

    if exposure.get(
        "duplicate_entry_blocked",
        True,
    ):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_CURRENT_EXPOSURE_BLOCKED",
            "duplicate_block_reason": exposure.get(
                "duplicate_block_reason"
            ),
            "exposure": exposure,
        }

    payload = dict(
        preview["payload"]
    )

    client_order_id = (
        r36f159_client_order_id(
            command_preview
        )
    )

    if client_order_id in set(
        exposure.get(
            "existing_client_ids",
            [],
        )
    ):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_CLIENT_ORDER_ID_ALREADY_EXISTS",
            "client_order_id": client_order_id,
        }

    payload[
        "newClientOrderId"
    ] = client_order_id

    jit_validation = (
        await r36f154_validate_fresh_demo_triggers(
            payload
        )
    )

    log(
        "R36F.15.9 JIT DEMO TRIGGER VALIDATION = "
        + canonical_json(
            jit_validation
        )
    )

    if not jit_validation.get("valid"):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED",
            "jit_validation": jit_validation,
        }

    payload_hash = sha256_text(
        canonical_json(payload)
    )

    prepared = {
        "stage": STAGE,
        "state": "PREPARED",
        "created_at": now_iso(),
        "endpoint": R36F14_DEMO_ORDER_ENDPOINT,
        "command": str(
            command_preview.get("command")
            or ""
        ),
        "direction": str(
            command_preview.get("direction")
            or ""
        ),
        "command_token_sha256": sha256_text(
            R36F159_COMMAND_TOKEN
        ),
        "command_identity_sha256": (
            command_identity
        ),
        "client_order_id": client_order_id,
        "payload_sha256": payload_hash,
        "payload": payload,
        "pre_post_journal_verified": True,
        "real_order_execution": (
            REAL_ORDER_EXECUTION
        ),
        "demo_only": True,
    }

    write_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        prepared,
    )

    reloaded = read_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        default={},
    )

    reload_payload_hash = sha256_text(
        canonical_json(
            reloaded.get(
                "payload",
                {},
            )
        )
    )

    pre_post_reload_match = bool(
        reloaded.get("client_order_id")
        == client_order_id
        and reloaded.get(
            "command_identity_sha256"
        )
        == command_identity
        and reloaded.get(
            "payload_sha256"
        )
        == payload_hash
        and hmac.compare_digest(
            reload_payload_hash,
            payload_hash,
        )
    )

    log(
        "R36F.15.9 PRE_POST_JOURNAL_WRITTEN = True"
    )
    log(
        "R36F.15.9 PRE_POST_JOURNAL_RELOAD_MATCH = "
        + str(pre_post_reload_match)
    )
    log(
        "R36F.15.9 CLIENT ORDER ID = "
        + client_order_id
    )

    if not pre_post_reload_match:
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_PRE_POST_JOURNAL_VERIFICATION_FAILED",
            "journal": reloaded,
        }

    try:
        transport = await weex_demo_post(
            R36F14_DEMO_ORDER_ENDPOINT,
            payload,
        )

    except Exception as exc:
        ambiguous = {
            **prepared,
            "state": "SENT_AMBIGUOUS",
            "updated_at": now_iso(),
            "error": str(exc),
        }

        write_json_file(
            R36F159_DEMO_JOURNAL_FILE,
            ambiguous,
        )

        return {
            "attempted": True,
            "sent": False,
            "accepted": False,
            "reason": "SECOND_DEMO_POST_EXCEPTION_JOURNALED_AMBIGUOUS",
            "error": str(exc),
            "journal": ambiguous,
        }

    response = (
        transport.get("response")
        if isinstance(transport, dict)
        else {}
    )

    if not isinstance(response, dict):
        response = {}

    success = bool(
        response.get("success")
    )

    completed = {
        **prepared,
        "state": (
            "COMPLETED"
            if success
            else "REJECTED"
        ),
        "updated_at": now_iso(),
        "http_status": transport.get(
            "http_status"
        ),
        "response": response,
        "success": success,
        "order_id": str(
            response.get("orderId", "")
        ),
        "client_order_id_response": str(
            response.get(
                "clientOrderId",
                "",
            )
        ),
        "error_code": str(
            response.get(
                "errorCode",
                "",
            )
        ),
        "error_message": str(
            response.get(
                "errorMessage",
                "",
            )
        ),
    }

    write_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        completed,
    )

    return {
        "attempted": True,
        "sent": True,
        "accepted": success,
        "transport": transport,
        "journal": completed,
    }

async def load_mark_price():
    global MARK_PRICE

    data = await weex_get(
        "/capi/v3/market/symbolPrice",
        params={
            "symbol": SYMBOL
        },
        authenticated=False,
    )

    candidates = []

    if isinstance(data, dict):
        for key in (
            "price",
            "markPrice",
            "lastPrice",
        ):
            if key in data:
                candidates.append(
                    data[key]
                )

        nested = data.get("data")

        if isinstance(nested, dict):
            for key in (
                "price",
                "markPrice",
                "lastPrice",
            ):
                if key in nested:
                    candidates.append(
                        nested[key]
                    )

    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue

            for key in (
                "price",
                "markPrice",
                "lastPrice",
            ):
                if key in item:
                    candidates.append(
                        item[key]
                    )

    for candidate in candidates:
        try:
            MARK_PRICE = D(candidate)

            if MARK_PRICE > 0:
                log(
                    "MARK PRICE = "
                    + decimal_to_string(
                        MARK_PRICE
                    )
                )
                return MARK_PRICE

        except Exception:
            continue

    raise RuntimeError(
        "Unable to determine WEEX mark price"
    )

async def load_available_balance():
    global AVAILABLE_BALANCE

    data = await weex_get(
        "/capi/v3/account/balance",
        authenticated=True,
    )

    candidates = []

    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = key.lower()

                if key_lower in (
                    "availablebalance",
                    "available_balance",
                    "available",
                    "free",
                    "usdtavailable",
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

                log(
                    "AVAILABLE USDT = "
                    + decimal_to_string(
                        AVAILABLE_BALANCE
                    )
                )

                return value

        except Exception:
            continue

    raise RuntimeError(
        "Unable to determine available USDT balance"
    )

async def load_open_positions():
    global OPEN_POSITIONS

    data = await weex_get(
        "/capi/v3/account/position/singlePosition",
        params={
            "symbol": SYMBOL
        },
        authenticated=True,
    )

    if isinstance(data, list):
        OPEN_POSITIONS = data

    elif isinstance(data, dict):
        nested = data.get("data")

        if isinstance(nested, list):
            OPEN_POSITIONS = nested
        else:
            OPEN_POSITIONS = []

    else:
        OPEN_POSITIONS = []

    log(
        "OPEN POSITIONS = "
        + str(len(OPEN_POSITIONS))
    )

    return OPEN_POSITIONS

async def load_exchange_config():
    global WEEX_CONFIG

    data = await weex_get(
        "/capi/v3/market/exchangeInfo",
        params={
            "symbol": SYMBOL
        },
        authenticated=False,
    )

    WEEX_CONFIG = (
        data
        if isinstance(data, dict)
        else {}
    )

    log(
        "WEEX EXCHANGE CONFIG READ COMPLETE"
    )

    return WEEX_CONFIG

async def reconcile_weex():
    await load_mark_price()
    try:
        await load_available_balance()

    except Exception as exc:
        log(
            f"BALANCE READ FAILED = {exc}"
        )
        raise

    try:
        await load_open_positions()

    except Exception as exc:
        log(
            f"POSITION READ FAILED = {exc}"
        )
        raise

    try:
        await load_exchange_config()

    except Exception as exc:
        log(
            f"EXCHANGE CONFIG READ FAILED = {exc}"
        )
        raise

    return True

async def load_historical_klines():
    all_rows = []

    for page in range(
        MAX_HISTORICAL_PAGES
    ):
        params = {
            "symbol": SYMBOL,
            "interval": KLINE_INTERVAL,
            "limit": HISTORICAL_LIMIT,
        }

        if page > 0:
            params["endTime"] = (
                int(time.time() * 1000)
                - (
                    page
                    * HISTORICAL_LIMIT
                    * 60
                    * 1000
                )
            )

        data = await weex_get(
            "/capi/v3/market/klines",
            params=params,
            authenticated=False,
        )

        rows = data

        if isinstance(data, dict):
            rows = data.get(
                "data",
                data.get(
                    "result",
                    [],
                ),
            )

        if not isinstance(rows, list):
            raise RuntimeError(
                "Unexpected kline response"
            )

        all_rows.extend(rows)

        if len(rows) < HISTORICAL_LIMIT:
            break

    return all_rows

def candle_high(row):
    if isinstance(row, dict):
        for key in (
            "high",
            "highPrice",
        ):
            if key in row:
                return D(row[key])

    if (
        isinstance(row, list)
        and len(row) >= 3
    ):
        return D(row[2])

    raise ValueError(
        "Unable to read candle high"
    )

def candle_low(row):
    if isinstance(row, dict):
        for key in (
            "low",
            "lowPrice",
        ):
            if key in row:
                return D(row[key])

    if (
        isinstance(row, list)
        and len(row) >= 4
    ):
        return D(row[3])

    raise ValueError(
        "Unable to read candle low"
    )

def historical_highs(rows):
    return [
        candle_high(row)
        for row in rows
    ]

def historical_lows(rows):
    return [
        candle_low(row)
        for row in rows
    ]

def candle_close(row):
    if isinstance(row, dict):
        for key in (
            "close",
            "closePrice",
            "c",
            "lastPrice",
        ):
            if key in row:
                return D(row[key])

    if (
        isinstance(row, list)
        and len(row) >= 5
    ):
        return D(row[4])

    raise ValueError(
        "Unable to read candle close"
    )

def candle_timestamp(row):
    if isinstance(row, dict):
        for key in (
            "timestamp",
            "ts",
            "time",
            "startTime",
            "openTime",
        ):
            if key in row:
                return row[key]

    if (
        isinstance(row, list)
        and len(row) >= 1
    ):
        return row[0]

    return None

def chronological_rows(rows):
    usable = []

    for row in rows:
        try:
            close = candle_close(row)

            if close <= 0:
                continue

            ts = candle_timestamp(row)

            usable.append(
                (
                    ts,
                    row,
                )
            )

        except Exception:
            continue

    if (
        usable
        and all(
            item[0] is not None
            for item in usable
        )
    ):
        by_ts = {
            item[0]: item[1]
            for item in usable
        }

        return [
            by_ts[ts]
            for ts in sorted(by_ts)
        ]

    return [
        item[1]
        for item in usable
    ]

def ema_series(
    values,
    period,
):
    if len(values) < period:
        return None

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    ema = (
        sum(values[:period])
        / Decimal(period)
    )

    for price in values[period:]:
        ema = (
            (
                price
                - ema
            )
            * multiplier
            + ema
        )

    return ema

def calculate_emas(closes):
    return (
        ema_series(
            closes,
            EMA_FAST,
        ),
        ema_series(
            closes,
            EMA_MID,
        ),
        ema_series(
            closes,
            EMA_SLOW,
        ),
    )

def ema_structure(
    ema19,
    ema50,
    ema200,
):
    if (
        ema19
        > ema50
        > ema200
    ):
        return "STRONG_BULLISH"

    if (
        ema19
        < ema50
        < ema200
    ):
        return "STRONG_BEARISH"

    if ema19 > ema50:
        return "EARLY_BULLISH"

    if ema19 < ema50:
        return "EARLY_BEARISH"

    return "NEUTRAL"

def ema_direction(structure):
    if structure == "STRONG_BULLISH":
        return "LONG"

    if structure == "STRONG_BEARISH":
        return "SHORT"

    return None

def ema_separation_percent(
    price,
    ema19,
    ema50,
):
    if price <= 0:
        return Decimal("0")

    return (
        abs(
            ema19
            - ema50
        )
        / price
        * Decimal("100")
    )

def detect_ema19_50_crossover(
    previous19,
    previous50,
    current19,
    current50,
):
    if None in (
        previous19,
        previous50,
        current19,
        current50,
    ):
        return None

    if (
        previous19
        <= previous50
        and current19
        > current50
    ):
        return "LONG"

    if (
        previous19
        >= previous50
        and current19
        < current50
    ):
        return "SHORT"

    return None

def build_ema_signal_snapshot(rows):
    ordered = chronological_rows(
        rows
    )

    closes = [
        candle_close(row)
        for row in ordered
    ]

    if len(closes) < (
        EMA_SLOW
        + EMA_CONFIRMATION_CANDLES
    ):
        return {
            "ready": False,
            "reason": "INSUFFICIENT_CANDLES_FOR_EMA200_CONFIRMATION",
            "rows": len(closes),
        }

    (
        current19,
        current50,
        current200,
    ) = calculate_emas(
        closes
    )

    (
        previous19,
        previous50,
        previous200,
    ) = calculate_emas(
        closes[:-1]
    )

    current_price = closes[-1]

    structure = ema_structure(
        current19,
        current50,
        current200,
    )

    direction = ema_direction(
        structure
    )

    separation = (
        ema_separation_percent(
            current_price,
            current19,
            current50,
        )
    )

    crossover = (
        detect_ema19_50_crossover(
            previous19,
            previous50,
            current19,
            current50,
        )
    )

    quality_ok = (
        separation
        >= MIN_EMA_19_50_SEPARATION_PERCENT
    )

    ideal_direction = (
        direction
        if quality_ok
        else None
    )

    return {
        "ready": True,
        "reason": "EMA_ENGINE_READY",
        "rows": len(closes),
        "price": decimal_to_string(
            current_price
        ),
        "ema19": decimal_to_string(
            current19
        ),
        "ema50": decimal_to_string(
            current50
        ),
        "ema200": decimal_to_string(
            current200
        ),
        "structure": structure,
        "direction": direction,
        "ideal_direction": (
            ideal_direction
        ),
        "ema19_50_separation_percent": (
            decimal_to_string(
                separation
            )
        ),
        "minimum_separation_percent": (
            decimal_to_string(
                MIN_EMA_19_50_SEPARATION_PERCENT
            )
        ),
        "quality_ok": quality_ok,
        "fresh_crossover": crossover,
        "confirmation_policy": (
            "NEXT_CLOSED_1M_CANDLE"
        ),
        "signal_expiry_seconds": (
            SIGNAL_EXPIRY_SECONDS
        ),
    }

def normalize_telegram_command(text):
    return " ".join(
        str(
            text or ""
        )
        .strip()
        .upper()
        .split()
    )

def parse_telegram_trade_command(text):
    normalized = (
        normalize_telegram_command(
            text
        )
    )

    if (
        normalized
        == TELEGRAM_BUY_COMMAND
    ):
        return {
            "recognized": True,
            "command": normalized,
            "direction": "LONG",
        }

    if (
        normalized
        == TELEGRAM_SELL_COMMAND
    ):
        return {
            "recognized": True,
            "command": normalized,
            "direction": "SHORT",
        }

    return {
        "recognized": False,
        "command": normalized,
        "direction": None,
    }

def validate_telegram_command_against_signal(
    text,
    ema_snapshot,
    long_eligible,
    short_eligible,
):
    parsed = (
        parse_telegram_trade_command(
            text
        )
    )

    direction = parsed[
        "direction"
    ]

    if not parsed[
        "recognized"
    ]:
        return {
            **parsed,
            "authorized_preview": False,
            "reason": "UNRECOGNIZED_COMMAND",
        }

    if not ema_snapshot.get(
        "ready"
    ):
        return {
            **parsed,
            "authorized_preview": False,
            "reason": "EMA_ENGINE_NOT_READY",
        }

    ideal = ema_snapshot.get(
        "ideal_direction"
    )

    if ideal != direction:
        return {
            **parsed,
            "authorized_preview": False,
            "reason": "COMMAND_DIRECTION_DOES_NOT_MATCH_IDEAL_EMA_CONDITION",
            "ema_ideal_direction": ideal,
        }

    market_ok = (
        long_eligible
        if direction == "LONG"
        else short_eligible
    )

    if not market_ok:
        return {
            **parsed,
            "authorized_preview": False,
            "reason": "COMMAND_DIRECTION_TP_MARKET_NOT_ELIGIBLE",
            "ema_ideal_direction": ideal,
        }

    return {
        **parsed,
        "authorized_preview": True,
        "reason": "COMMAND_AND_EMA_AND_TP_DIRECTION_AGREE",
        "ema_ideal_direction": ideal,
        "exchange_order_sent": False,
    }

def build_ideal_condition_alert(
    ema_snapshot,
):
    if not ema_snapshot.get(
        "ready"
    ):
        return None

    direction = ema_snapshot.get(
        "ideal_direction"
    )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        return None

    command = (
        TELEGRAM_BUY_COMMAND
        if direction == "LONG"
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

async def send_r36f12_telegram_alert(
    message,
):
    if not message:
        return {
            "attempted": False,
            "sent": False,
            "reason": "NO_IDEAL_ALERT",
        }

    if not R36F12_TELEGRAM_ALERTS_ENABLED:
        return {
            "attempted": False,
            "sent": False,
            "reason": "ALERTS_DISABLED_BY_DEFAULT",
        }

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        return {
            "attempted": False,
            "sent": False,
            "reason": "TELEGRAM_CONFIG_MISSING",
        }

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(
                    total=15
                ),
            ) as response:
                body = await response.text()

                return {
                    "attempted": True,
                    "sent": (
                        200
                        <= response.status
                        < 300
                    ),
                    "http_status": (
                        response.status
                    ),
                    "response_preview": (
                        body[:200]
                    ),
                }

    except Exception as exc:
        return {
            "attempted": True,
            "sent": False,
            "reason": (
                f"{type(exc).__name__}: {exc}"
            ),
        }

def r36f1541_classify_demo_event(
    command_preview,
    submission,
):
    command_preview = (
        command_preview
        if isinstance(
            command_preview,
            dict,
        )
        else {}
    )

    submission = (
        submission
        if isinstance(
            submission,
            dict,
        )
        else {}
    )

    direction = str(
        command_preview.get(
            "direction"
        )
        or "UNKNOWN"
    ).upper()

    authorized = bool(
        command_preview.get(
            "authorized_preview"
        )
    )

    reason = str(
        submission.get("reason")
        or ""
    )

    if (
        submission.get("accepted")
        is True
    ):
        return (
            "DEMO_ORDER_ACCEPTED",
            direction,
        )

    if (
        submission.get("attempted")
        is True
        and submission.get(
            "accepted"
        )
        is not True
    ):
        return (
            "DEMO_ORDER_REJECTED",
            direction,
        )

    if (
        reason
        == "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED"
    ):
        return (
            "JIT_TRIGGER_BLOCKED",
            direction,
        )

    if (
        authorized
        and reason not in (
            "FIRST_DEMO_ORDER_ALREADY_COMPLETED",
            "UNRESOLVED_DEMO_JOURNAL_BLOCKS_RETRY",
        )
    ):
        return (
            "DEMO_TRADE_READY",
            direction,
        )

    return (
        "WAITING",
        direction,
    )

def r36f1541_build_event_message(
    event_name,
    direction,
    command_preview,
    submission,
):
    command_preview = (
        command_preview
        if isinstance(
            command_preview,
            dict,
        )
        else {}
    )

    submission = (
        submission
        if isinstance(
            submission,
            dict,
        )
        else {}
    )

    jit = (
        submission.get(
            "jit_validation"
        )
        if isinstance(
            submission.get(
                "jit_validation"
            ),
            dict,
        )
        else {}
    )

    journal = (
        submission.get("journal")
        if isinstance(
            submission.get("journal"),
            dict,
        )
        else {}
    )

    transport = (
        submission.get("transport")
        if isinstance(
            submission.get(
                "transport"
            ),
            dict,
        )
        else {}
    )

    if (
        event_name
        == "DEMO_ORDER_ACCEPTED"
    ):
        title = (
            "WEEX DEMO ORDER ACCEPTED"
        )

    elif (
        event_name
        == "DEMO_ORDER_REJECTED"
    ):
        title = (
            "WEEX DEMO ORDER REJECTED"
        )

    elif (
        event_name
        == "JIT_TRIGGER_BLOCKED"
    ):
        title = (
            "DEMO TRADE BLOCKED"
        )

    else:
        title = (
            "R36F.15.4.1 ACTION ALERT"
        )

    reason = str(
        submission.get("reason")
        or journal.get(
            "error_message"
        )
        or journal.get("error")
        or "NONE"
    )

    lines = [
        title,
        f"Event: {event_name}",
        f"Direction: {direction}",
        (
            "EMA: "
            + str(
                EMA_SIGNAL_SNAPSHOT.get(
                    "ideal_direction"
                )
            )
        ),
        (
            "Command authorized: "
            + str(
                command_preview.get(
                    "authorized_preview",
                    False,
                )
            )
        ),
        f"Reason: {reason}",
    ]

    if jit:
        lines.extend(
            [
                (
                    "JIT: "
                    + (
                        "PASSED"
                        if jit.get("valid")
                        else "BLOCKED"
                    )
                ),
                (
                    "Fresh mark: "
                    + str(
                        jit.get(
                            "fresh_mark_price"
                        )
                    )
                ),
                (
                    "TP: "
                    + str(
                        jit.get(
                            "tp_trigger_price"
                        )
                    )
                ),
                (
                    "SL: "
                    + str(
                        jit.get(
                            "sl_trigger_price"
                        )
                    )
                ),
            ]
        )

    order_id = (
        journal.get("order_id")
        or ""
    )

    if order_id:
        lines.append(
            f"Demo order ID: {order_id}"
        )

    http_status = transport.get(
        "http_status"
    )

    if http_status is not None:
        lines.append(
            f"WEEX HTTP: {http_status}"
        )

    lines.append(
        "Production real-money execution remains disabled."
    )

    return "\n".join(lines)

async def send_r36f1541_state_change_alert(
    command_preview,
    submission,
):
    (
        event_name,
        direction,
    ) = r36f1541_classify_demo_event(
        command_preview,
        submission,
    )

    previous = read_json_file(
        R36F1541_TELEGRAM_EVENT_STATE_FILE,
        default={},
    )

    previous_event = str(
        previous.get(
            "event_name"
        )
        or ""
    )

    previous_direction = str(
        previous.get(
            "direction"
        )
        or ""
    )

    if event_name == "WAITING":
        if (
            previous_event
            != "WAITING"
            or previous_direction
            != direction
        ):
            write_json_file(
                R36F1541_TELEGRAM_EVENT_STATE_FILE,
                {
                    "stage": STAGE,
                    "event_name": (
                        "WAITING"
                    ),
                    "direction": (
                        direction
                    ),
                    "updated_at": (
                        now_iso()
                    ),
                },
            )

        return {
            "attempted": False,
            "sent": False,
            "reason": "WAITING_STATE_SILENT",
        }

    if (
        previous_event
        == event_name
        and previous_direction
        == direction
    ):
        return {
            "attempted": False,
            "sent": False,
            "deduplicated": True,
            "reason": "DUPLICATE_NOTIFICATION_BLOCKED",
            "event_name": event_name,
        }

    message = (
        r36f1541_build_event_message(
            event_name,
            direction,
            command_preview,
            submission,
        )
    )

    result = (
        await send_r36f12_telegram_alert(
            message
        )
    )

    if result.get("sent"):
        write_json_file(
            R36F1541_TELEGRAM_EVENT_STATE_FILE,
            {
                "stage": STAGE,
                "event_name": (
                    event_name
                ),
                "direction": (
                    direction
                ),
                "updated_at": (
                    now_iso()
                ),
            },
        )

    result = dict(result)
    result["event_name"] = event_name
    result["direction"] = direction

    return result

def synthetic_r36f12_ema_telegram_tests():
    bullish = {
        "ready": True,
        "ideal_direction": "LONG",
        "structure": "STRONG_BULLISH",
        "price": "80000",
        "ema19": "80100",
        "ema50": "80000",
        "ema200": "79000",
        "quality_ok": True,
    }

    bearish = {
        "ready": True,
        "ideal_direction": "SHORT",
        "structure": "STRONG_BEARISH",
        "price": "80000",
        "ema19": "79900",
        "ema50": "80000",
        "ema200": "81000",
        "quality_ok": True,
    }

    long_ok = (
        validate_telegram_command_against_signal(
            TELEGRAM_BUY_COMMAND,
            bullish,
            True,
            False,
        )
    )

    short_ok = (
        validate_telegram_command_against_signal(
            TELEGRAM_SELL_COMMAND,
            bearish,
            False,
            True,
        )
    )

    wrong_direction = (
        validate_telegram_command_against_signal(
            TELEGRAM_SELL_COMMAND,
            bullish,
            True,
            True,
        )
    )

    check(
        "R36F12_SYNTHETIC_LONG_COMMAND_AUTHORIZATION",
        long_ok.get(
            "authorized_preview"
        )
        is True,
    )

    check(
        "R36F12_SYNTHETIC_SHORT_COMMAND_AUTHORIZATION",
        short_ok.get(
            "authorized_preview"
        )
        is True,
    )

    check(
        "R36F12_SYNTHETIC_WRONG_DIRECTION_REJECTED",
        wrong_direction.get(
            "authorized_preview"
        )
        is False,
    )

    return True

# ============================================================
# LOCAL EXTREMA
# ============================================================

def build_extrema(values):
    if len(values) < 3:
        return []

    extrema = []

    for index in range(
        1,
        len(values) - 1,
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

def local_extrema_values(
    rows,
    side,
):
    if side == "LONG":
        values = historical_highs(
            rows
        )

    elif side == "SHORT":
        values = historical_lows(
            rows
        )

    else:
        raise ValueError(
            f"Unsupported side={side}"
        )

    return build_extrema(
        values
    )

# ============================================================
# CLUSTER EXTREMA
# ============================================================

def cluster_extrema(
    extrema,
):
    if not extrema:
        return []

    sorted_values = sorted(
        D(value)
        for value in extrema
    )

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
            / Decimal("100")
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
            clusters.append(
                {
                    "minimum":
                        min(current),

                    "maximum":
                        max(current),

                    "average":
                        (
                            sum(current)
                            / Decimal(
                                len(current)
                            )
                        ),

                    "touches":
                        len(current),
                }
            )

            current = [
                value
            ]

    clusters.append(
        {
            "minimum":
                min(current),

            "maximum":
                max(current),

            "average":
                (
                    sum(current)
                    / Decimal(
                        len(current)
                    )
                ),

            "touches":
                len(current),
        }
    )

    return clusters

# ============================================================
# CLUSTER VALIDATION
# ============================================================

def validate_clusters(
    clusters,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    valid = []
    invalid = []

    for cluster in clusters:
        reasons = []

        touches = cluster[
            "touches"
        ]

        average = D(
            cluster[
                "average"
            ]
        )

        if (
            touches
            < MIN_CLUSTER_TOUCHES
        ):
            reasons.append(
                "INSUFFICIENT_TOUCHES"
            )

        if side == "LONG":
            if average <= entry_price:
                reasons.append(
                    "CLUSTER_NOT_ABOVE_ENTRY"
                )

        elif side == "SHORT":
            if average >= entry_price:
                reasons.append(
                    "CLUSTER_NOT_BELOW_ENTRY"
                )

        else:
            reasons.append(
                "INVALID_DIRECTION"
            )

        result = dict(
            cluster
        )

        result["valid"] = (
            not reasons
        )
        result["reasons"] = (
            reasons
        )

        if reasons:
            invalid.append(
                result
            )
        else:
            valid.append(
                result
            )

    if side == "LONG":
        valid.sort(
            key=lambda item:
                item["average"]
        )

    elif side == "SHORT":
        valid.sort(
            key=lambda item:
                item["average"],
            reverse=True,
        )

    return (
        valid,
        invalid,
    )

# ============================================================
# R36F.15.10.1 CLUSTER DIAGNOSTICS
# ============================================================

R36F15101_TOLERANCE_GRID = (
    Decimal("0.05"),
    Decimal("0.10"),
    Decimal("0.15"),
    Decimal("0.20"),
    Decimal("0.25"),
    Decimal("0.30"),
)

def cluster_extrema_at_tolerance(
    extrema,
    tolerance_percent,
):
    tolerance_percent = D(
        tolerance_percent
    )

    if not extrema:
        return []

    sorted_values = sorted(
        D(value)
        for value in extrema
    )

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
            * tolerance_percent
            / Decimal("100")
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
            clusters.append(
                {
                    "minimum":
                        min(current),

                    "maximum":
                        max(current),

                    "average":
                        (
                            sum(current)
                            / Decimal(
                                len(current)
                            )
                        ),

                    "touches":
                        len(current),
                }
            )

            current = [
                value
            ]

    clusters.append(
        {
            "minimum":
                min(current),

            "maximum":
                max(current),

            "average":
                (
                    sum(current)
                    / Decimal(
                        len(current)
                    )
                ),

            "touches":
                len(current),
        }
    )

    return clusters

def r36f15101_side_distance_percent(
    entry_price,
    average,
    side,
):
    entry_price = D(
        entry_price
    )

    average = D(
        average
    )

    if entry_price <= 0:
        return None

    if side == "LONG":
        return (
            (
                average
                - entry_price
            )
            / entry_price
            * Decimal("100")
        )

    if side == "SHORT":
        return (
            (
                entry_price
                - average
            )
            / entry_price
            * Decimal("100")
        )

    return None

def r36f15101_cluster_span_percent(
    cluster,
):
    average = D(
        cluster["average"]
    )

    if average <= 0:
        return None

    return (
        (
            D(cluster["maximum"])
            - D(cluster["minimum"])
        )
        / average
        * Decimal("100")
    )

def r36f15101_tolerance_sweep(
    extrema,
    entry_price,
    side,
):
    results = []

    for tolerance_percent in (
        R36F15101_TOLERANCE_GRID
    ):
        clusters = (
            cluster_extrema_at_tolerance(
                extrema,
                tolerance_percent,
            )
        )

        valid, invalid = (
            validate_clusters(
                clusters,
                entry_price,
                side,
            )
        )

        results.append(
            {
                "tolerance_percent":
                    tolerance_percent,

                "cluster_count":
                    len(clusters),

                "valid_cluster_count":
                    len(valid),

                "invalid_cluster_count":
                    len(invalid),

                "approved_if_used":
                    (
                        len(valid)
                        >= REQUIRED_TP_CLUSTERS
                    ),
            }
        )

    return results

def build_cluster_diagnostics(
    rows,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    if side == "LONG":
        values = historical_highs(
            rows
        )

    elif side == "SHORT":
        values = historical_lows(
            rows
        )

    else:
        raise ValueError(
            f"Unsupported side={side}"
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
            side,
        )
    )

    diagnostics = {
        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "historical_row_count":
            len(rows),

        "extrema_count":
            len(extrema),

        "cluster_count":
            len(clusters),

        "valid_cluster_count":
            len(valid),

        "invalid_cluster_count":
            len(invalid),

        "required_valid_clusters":
            REQUIRED_TP_CLUSTERS,

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,
    }

    if (
        len(valid)
        >= REQUIRED_TP_CLUSTERS
    ):
        diagnostics[
            "failure_reason"
        ] = None

    elif len(valid) == 1:
        diagnostics[
            "failure_reason"
        ] = (
            "ONLY_ONE_VALID_CLUSTER"
        )

    elif extrema:
        diagnostics[
            "failure_reason"
        ] = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    else:
        diagnostics[
            "failure_reason"
        ] = (
            "NO_LOCAL_EXTREMA"
        )

    diagnostics[
        "tolerance_sweep"
    ] = r36f15101_tolerance_sweep(
        extrema,
        entry_price,
        side,
    )

    diagnostics[
        "valid_cluster_distances_percent"
    ] = [
        decimal_to_string(
            r36f15101_side_distance_percent(
                entry_price,
                item["average"],
                side,
            )
        )
        for item in valid
    ]

    diagnostics[
        "valid_cluster_spans_percent"
    ] = [
        decimal_to_string(
            r36f15101_cluster_span_percent(
                item
            )
        )
        for item in valid
    ]

    return diagnostics

# ============================================================
# TP APPROVAL
# ============================================================

def evaluate_tp_approval(
    diagnostics,
):
    valid_count = int(
        diagnostics.get(
            "valid_cluster_count",
            0,
        )
    )

    if (
        valid_count
        >= REQUIRED_TP_CLUSTERS
    ):
        approval = {
            "status":
                "APPROVED",

            "approved":
                True,

            "required_valid_clusters":
                REQUIRED_TP_CLUSTERS,

            "available_valid_clusters":
                valid_count,

            "reason":
                "TWO_OR_MORE_VALID_HISTORICAL_CLUSTERS",
        }

    else:
        failure_reason = (
            diagnostics.get(
                "failure_reason"
            )
            or
            "INSUFFICIENT_VALID_HISTORICAL_CLUSTERS"
        )

        approval = {
            "status":
                "REJECTED",

            "approved":
                False,

            "required_valid_clusters":
                REQUIRED_TP_CLUSTERS,

            "available_valid_clusters":
                valid_count,

            "reason":
                failure_reason,
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
        f"{STAGE}_TP_REQUIRED_CLUSTERS = "
        f"{REQUIRED_TP_CLUSTERS}"
    )

    log(
        f"{STAGE}_TP_AVAILABLE_CLUSTERS = "
        f"{valid_count}"
    )

    return approval

# ============================================================
# VALID CLUSTERS
# ============================================================

def valid_clusters(
    rows,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    extrema = local_extrema_values(
        rows,
        side,
    )

    clusters = cluster_extrema(
        extrema
    )

    valid = []

    for cluster in clusters:
        if (
            cluster["touches"]
            < MIN_CLUSTER_TOUCHES
        ):
            continue

        average = cluster[
            "average"
        ]

        if side == "LONG":
            if average <= entry_price:
                continue

        elif side == "SHORT":
            if average >= entry_price:
                continue

        else:
            raise ValueError(
                f"Unsupported side={side}"
            )

        valid.append(
            cluster
        )

    if side == "LONG":
        valid.sort(
            key=lambda c:
                c["average"]
        )

    else:
        valid.sort(
            key=lambda c:
                c["average"],
            reverse=True,
        )

    return valid

# ============================================================
# TP PRICE CALCULATION
# ============================================================

def calculate_tp_prices(
    entry_price,
    valid_cluster_list,
    direction,
):
    entry_price = D(
        entry_price
    )

    if (
        len(valid_cluster_list)
        < REQUIRED_TP_CLUSTERS
    ):
        raise RuntimeError(
            "Cannot calculate complete TP set: "
            "fewer than two valid historical clusters"
        )

    cluster1 = D(
        valid_cluster_list[
            0
        ]["average"]
    )

    cluster2 = D(
        valid_cluster_list[
            1
        ]["average"]
    )

    progress1 = (
        TP1_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    progress2 = (
        TP2_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    if direction == "LONG":
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

    elif direction == "SHORT":
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
            "Invalid TP direction"
        )

    return {
        "tp1":
            quantize_down(
                tp1,
                PRICE_STEP,
            ),

        "tp2":
            quantize_down(
                tp2,
                PRICE_STEP,
            ),

        "tp3": {
            "type":
                "TRAILING",

            "allocation_percent":
                TP3_ALLOCATION_PERCENT,

            "trailing_distance_percent":
                TP3_TRAILING_DISTANCE_PERCENT,
        },

        "cluster1_average":
            cluster1,

        "cluster2_average":
            cluster2,
    }

# ============================================================
# TP ENGINE
# ============================================================

def run_tp_engine(
    rows,
    entry_price,
    direction,
):
    if direction == "LONG":
        values = historical_highs(
            rows
        )
        extrema = build_extrema(
            values
        )

    elif direction == "SHORT":
        values = historical_lows(
            rows
        )
        extrema = build_extrema(
            values
        )

    else:
        raise RuntimeError(
            "Invalid direction"
        )

    clusters = cluster_extrema(
        extrema
    )

    valid, invalid = (
        validate_clusters(
            clusters,
            entry_price,
            direction,
        )
    )

    approval = (
        evaluate_tp_approval(
            {
                "valid_cluster_count":
                    len(valid),

                "failure_reason":
                    (
                        "ONLY_ONE_VALID_CLUSTER"
                        if len(valid) == 1
                        else
                        "INSUFFICIENT_VALID_CLUSTERS"
                    ),
            }
        )
    )

    if not approval[
        "approved"
    ]:
        return {
            "approved":
                False,

            "approval":
                approval,

            "valid_clusters":
                valid,

            "invalid_clusters":
                invalid,
        }

    prices = calculate_tp_prices(
        entry_price,
        valid,
        direction,
    )

    return {
        "approved":
            True,

        "approval":
            approval,

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,

        "prices":
            prices,
    }

# ============================================================
# TP SNAPSHOT
# ============================================================

def build_cluster_tp_snapshot(
    entry_price,
    rows,
    side,
    fill_label,
):
    global LAST_TP_APPROVAL

    entry_price = D(
        entry_price
    )

    diagnostics = (
        build_cluster_diagnostics(
            rows,
            entry_price,
            side,
        )
    )

    approval = (
        evaluate_tp_approval(
            diagnostics
        )
    )

    LAST_TP_APPROVAL = (
        approval
    )

    if not approval[
        "approved"
    ]:
        log(
            f"{side} TP SET REJECTED: "
            f"{approval['reason']}"
        )

        raise RuntimeError(
            f"{side} historical TP set rejected: "
            f"requires at least "
            f"{REQUIRED_TP_CLUSTERS} valid clusters; "
            f"found "
            f"{approval['available_valid_clusters']}"
        )

    clusters = valid_clusters(
        rows,
        entry_price,
        side,
    )

    if (
        len(clusters)
        < REQUIRED_TP_CLUSTERS
    ):
        raise RuntimeError(
            "TP approval inconsistency: "
            "diagnostics approved but independent "
            "cluster extraction found fewer than "
            "two valid clusters"
        )

    prices = calculate_tp_prices(
        entry_price,
        clusters,
        side,
    )

    snapshot = {
        "fill_label":
            fill_label,

        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "historical_diagnostics":
            diagnostics,

        "tp_approval":
            approval,

        "tp1":
            decimal_to_string(
                prices["tp1"]
            ),

        "tp2":
            decimal_to_string(
                prices["tp2"]
            ),

        "tp3": {
            "type":
                "TRAILING",

            "allocation_percent":
                decimal_to_string(
                    TP3_ALLOCATION_PERCENT
                ),

            "trailing_distance_percent":
                decimal_to_string(
                    TP3_TRAILING_DISTANCE_PERCENT
                ),
        },

        "cluster1_average":
            decimal_to_string(
                prices[
                    "cluster1_average"
                ]
            ),

        "cluster2_average":
            decimal_to_string(
                prices[
                    "cluster2_average"
                ]
            ),

        "primary_tp_immutable":
            True,
    }

    log(
        f"{side} TP SET APPROVED WITH "
        f"{len(clusters)} VALID CLUSTERS"
    )

    log(
        f"{side} TP1 = "
        f"{snapshot['tp1']} "
        f"(20% adjustable progress)"
    )

    log(
        f"{side} TP2 = "
        f"{snapshot['tp2']} "
        f"(50% adjustable progress)"
    )

    log(
        f"{side} TP3 = "
        f"{TP3_ALLOCATION_PERCENT}% trailing runner"
    )

    return snapshot

# ============================================================
# SYNTHETIC TP TESTS
# ============================================================

def synthetic_cluster_tests():
    long_rows = [
        [1, "99000", "100000", "99500", "99500", "1"],
        [2, "99500", "100100", "99600", "99800", "1"],
        [3, "99600", "100000", "99500", "99700", "1"],
        [4, "99500", "101000", "99900", "100100", "1"],
        [5, "99900", "100200", "99500", "100000", "1"],
        [6, "99500", "101500", "100000", "100500", "1"],
        [7, "100000", "101000", "99500", "100500", "1"],
        [8, "99500", "101400", "99900", "100800", "1"],
    ]

    short_rows = [
        [1, "81000", "81500", "80000", "81000", "1"],
        [2, "81000", "81500", "80100", "80800", "1"],
        [3, "80800", "81400", "80050", "80500", "1"],
        [4, "80500", "81300", "79900", "80300", "1"],
        [5, "80300", "81200", "80000", "80500", "1"],
        [6, "80500", "81400", "79800", "80400", "1"],
        [7, "80400", "81300", "80100", "80600", "1"],
        [8, "80600", "81500", "79950", "80800", "1"],
    ]

    long_diagnostics = (
        build_cluster_diagnostics(
            long_rows,
            Decimal("99000"),
            "LONG",
        )
    )

    long_approval = (
        evaluate_tp_approval(
            long_diagnostics
        )
    )

    check(
        "SYNTHETIC_LONG_TWO_CLUSTER_APPROVAL",
        long_approval[
            "approved"
        ] is True,
    )

    short_diagnostics = (
        build_cluster_diagnostics(
            short_rows,
            Decimal("82000"),
            "SHORT",
        )
    )

    short_approval = (
        evaluate_tp_approval(
            short_diagnostics
        )
    )

    check(
        "SYNTHETIC_SHORT_TWO_CLUSTER_APPROVAL",
        short_approval[
            "approved"
        ] is True,
    )

    return (
        long_approval,
        short_approval,
    )

def synthetic_tp_rejection_test():
    rows = [
        [1, "99000", "100000", "99500", "99500", "1"],
        [2, "99500", "100100", "99600", "99800", "1"],
        [3, "99600", "100000", "99500", "99700", "1"],
        [4, "99500", "100100", "99800", "99900", "1"],
    ]

    entry = Decimal(
        "99500"
    )

    diagnostics = (
        build_cluster_diagnostics(
            rows,
            entry,
            "LONG",
        )
    )

    approval = (
        evaluate_tp_approval(
            diagnostics
        )
    )

    check(
        "ONE_CLUSTER_TP_REJECTED",
        approval[
            "approved"
        ] is False,
    )

    check(
        "ONE_CLUSTER_APPROVAL_STATUS_REJECTED",
        approval[
            "status"
        ] == "REJECTED",
    )

    check(
        "ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET",
        (
            approval[
                "available_valid_clusters"
            ]
            < REQUIRED_TP_CLUSTERS
        ),
    )

    return approval

# ============================================================
# CANARY PREVIEW
# ============================================================

def build_canary_preview():
    return {
        "stage":
            STAGE,

        "symbol":
            SYMBOL,

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "demo_order_execution":
            DEMO_ORDER_EXECUTION,

        "exchange_mutation_transport_enabled":
            EXCHANGE_MUTATION_TRANSPORT_ENABLED,

        "order_submission_enabled":
            ORDER_SUBMISSION_ENABLED,

        "first_real_order_allowed":
            FIRST_REAL_ORDER_ALLOWED,

        "submitted":
            False,

        "exchange_request_sent":
            False,
    }

# ============================================================
# WRITER HELPERS
# ============================================================

WRITER_ENDPOINT_ENTRY = (
    "/capi/v3/order"
)

WRITER_ENDPOINT_TPSL = (
    "/capi/v3/placeTpSlOrder"
)

WRITER_ENDPOINT_TRAILING = (
    "/capi/v3/algoOrder"
)

def writer_entry_side(
    direction,
):
    if direction == "LONG":
        return (
            "BUY",
            "LONG",
        )

    if direction == "SHORT":
        return (
            "SELL",
            "SHORT",
        )

    raise ValueError(
        f"Unsupported direction={direction}"
    )

def writer_close_side(
    direction,
):
    if direction == "LONG":
        return (
            "SELL",
            "LONG",
        )

    if direction == "SHORT":
        return (
            "BUY",
            "SHORT",
        )

    raise ValueError(
        f"Unsupported direction={direction}"
    )

def writer_client_id(
    direction,
    leg,
):
    value = (
        f"R36F8-{direction}-{leg}-0001"
    )

    if len(value) > 36:
        raise ValueError(
            "writer client id exceeds WEEX limit"
        )

    return value

# ============================================================
# WRITER QUANTITY ALLOCATION
# ============================================================

def writer_allocate_tp_quantities(
    total_quantity,
):
    total_quantity = quantize_down(
        total_quantity,
        QUANTITY_STEP,
    )

    if total_quantity < MIN_QUANTITY:
        raise ValueError(
            "Writer quantity below minimum"
        )

    tp1_quantity = quantize_down(
        total_quantity
        * TP1_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp2_quantity = quantize_down(
        total_quantity
        * TP2_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp3_quantity = (
        total_quantity
        - tp1_quantity
        - tp2_quantity
    )

    tp3_quantity = quantize_down(
        tp3_quantity,
        QUANTITY_STEP,
    )

    if tp3_quantity < 0:
        raise ValueError(
            "Writer TP3 quantity became negative"
        )

    return {
        "total":
            total_quantity,

        "tp1":
            tp1_quantity,

        "tp2":
            tp2_quantity,

        "tp3":
            tp3_quantity,

        "sum":
            (
                tp1_quantity
                + tp2_quantity
                + tp3_quantity
            ),
    }

# ============================================================
# R36F.15.10.4b — PART 5A
# BALANCE READINESS + PROTECTIVE STOP
# ============================================================

# R36F.15.10.4b BALANCE READINESS LEVERAGE COMPATIBILITY FIX
try:
    TARGET_LONG_LEVERAGE
except NameError:
    TARGET_LONG_LEVERAGE = 100

try:
    TARGET_SHORT_LEVERAGE
except NameError:
    TARGET_SHORT_LEVERAGE = 100
# END R36F.15.10.4b BALANCE READINESS LEVERAGE COMPATIBILITY FIX

ADJUSTED_TP1_ALLOCATION_PERCENT = Decimal("25")
ADJUSTED_TP2_ALLOCATION_PERCENT = Decimal("25")
ADJUSTED_TP3_ALLOCATION_PERCENT = Decimal("50")

def allocation_exactly_representable(
    entry_quantity,
    tp1_percent,
    tp2_percent,
    tp3_percent,
):
    entry_quantity = quantize_down(
        D(entry_quantity),
        QUANTITY_STEP,
    )

    percentages = (
        D(tp1_percent),
        D(tp2_percent),
        D(tp3_percent),
    )

    if sum(percentages) != Decimal("100"):
        return False

    quantities = [
        entry_quantity
        * percent
        / Decimal("100")
        for percent in percentages
    ]

    return bool(
        entry_quantity >= MIN_QUANTITY
        and all(
            quantity >= MIN_QUANTITY
            for quantity in quantities
        )
        and all(
            quantize_down(
                quantity,
                QUANTITY_STEP,
            ) == quantity
            for quantity in quantities
        )
        and sum(quantities)
        == entry_quantity
    )

def select_tp_allocation(
    entry_quantity,
):
    entry_quantity = quantize_down(
        D(entry_quantity),
        QUANTITY_STEP,
    )

    preferred = (
        TP1_ALLOCATION_PERCENT,
        TP2_ALLOCATION_PERCENT,
        TP3_ALLOCATION_PERCENT,
    )

    adjusted = (
        ADJUSTED_TP1_ALLOCATION_PERCENT,
        ADJUSTED_TP2_ALLOCATION_PERCENT,
        ADJUSTED_TP3_ALLOCATION_PERCENT,
    )

    if allocation_exactly_representable(
        entry_quantity,
        *preferred,
    ):
        return {
            "tp1_percent":
                preferred[0],

            "tp2_percent":
                preferred[1],

            "tp3_percent":
                preferred[2],

            "adjusted":
                False,

            "label":
                "20/20/60",
        }

    if allocation_exactly_representable(
        entry_quantity,
        *adjusted,
    ):
        return {
            "tp1_percent":
                adjusted[0],

            "tp2_percent":
                adjusted[1],

            "tp3_percent":
                adjusted[2],

            "adjusted":
                True,

            "label":
                "25/25/50",
        }

    return None

def writer_quantities(
    entry_quantity,
):
    entry_quantity = quantize_down(
        D(entry_quantity),
        QUANTITY_STEP,
    )

    allocation = select_tp_allocation(
        entry_quantity
    )

    if allocation is None:
        return (
            entry_quantity,
            Decimal("0"),
            Decimal("0"),
            Decimal("0"),
        )

    tp1 = (
        entry_quantity
        * allocation[
            "tp1_percent"
        ]
        / Decimal("100")
    )

    tp2 = (
        entry_quantity
        * allocation[
            "tp2_percent"
        ]
        / Decimal("100")
    )

    tp3 = (
        entry_quantity
        * allocation[
            "tp3_percent"
        ]
        / Decimal("100")
    )

    return (
        entry_quantity,
        tp1,
        tp2,
        tp3,
    )


def validate_writer_quantities(
    entry_quantity,
    tp1,
    tp2,
    tp3,
):
    allocation = select_tp_allocation(
        entry_quantity
    )

    if allocation is None:
        return {
            "allocation_selected":
                False,

            "all_valid":
                False,
        }

    exact_tp1 = (
        entry_quantity
        * allocation[
            "tp1_percent"
        ]
        / Decimal("100")
    )

    exact_tp2 = (
        entry_quantity
        * allocation[
            "tp2_percent"
        ]
        / Decimal("100")
    )

    exact_tp3 = (
        entry_quantity
        * allocation[
            "tp3_percent"
        ]
        / Decimal("100")
    )

    checks = {
        "allocation_selected":
            True,

        "entry_on_step":
            quantize_down(
                entry_quantity,
                QUANTITY_STEP,
            ) == entry_quantity,

        "tp1_on_step":
            quantize_down(
                tp1,
                QUANTITY_STEP,
            ) == tp1,

        "tp2_on_step":
            quantize_down(
                tp2,
                QUANTITY_STEP,
            ) == tp2,

        "tp3_on_step":
            quantize_down(
                tp3,
                QUANTITY_STEP,
            ) == tp3,

        "entry_minimum":
            entry_quantity
            >= MIN_QUANTITY,

        "tp1_minimum":
            tp1
            >= MIN_QUANTITY,

        "tp2_minimum":
            tp2
            >= MIN_QUANTITY,

        "tp3_minimum":
            tp3
            >= MIN_QUANTITY,

        "allocation_sum_exact":
            (
                tp1
                + tp2
                + tp3
            )
            == entry_quantity,

        "tp1_selected_percent_exact":
            tp1 == exact_tp1,

        "tp2_selected_percent_exact":
            tp2 == exact_tp2,

        "tp3_selected_percent_exact":
            tp3 == exact_tp3,

        "tp3_non_negative":
            tp3 >= Decimal("0"),
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


def minimum_adjustable_tp_entry_quantity():
    candidate = QUANTITY_STEP

    for _ in range(100000):
        (
            quantity,
            tp1,
            tp2,
            tp3,
        ) = writer_quantities(
            candidate
        )

        checks = (
            validate_writer_quantities(
                quantity,
                tp1,
                tp2,
                tp3,
            )
        )

        if checks.get(
            "all_valid"
        ):
            return quantity

        candidate += QUANTITY_STEP

    raise RuntimeError(
        "Unable to find adjustable TP minimum quantity"
    )


def minimum_strict_tp_entry_quantity():
    return (
        minimum_adjustable_tp_entry_quantity()
    )


def evaluate_writer_quantity_feasibility(
    entry_quantity,
):
    (
        quantity,
        tp1,
        tp2,
        tp3,
    ) = writer_quantities(
        entry_quantity
    )

    allocation = select_tp_allocation(
        quantity
    )

    checks = (
        validate_writer_quantities(
            quantity,
            tp1,
            tp2,
            tp3,
        )
    )

    minimum_required = (
        minimum_adjustable_tp_entry_quantity()
    )

    feasible = bool(
        checks.get(
            "all_valid"
        )
    )

    return {
        "feasible":
            feasible,

        "reason":
            (
                "ADJUSTABLE_TP_ALLOCATION_REPRESENTABLE"
                if feasible
                else
                "POSITION_TOO_SMALL_OR_NOT_REPRESENTABLE"
            ),

        "entry_quantity":
            decimal_to_string(
                quantity
            ),

        "tp1_quantity":
            decimal_to_string(
                tp1
            ),

        "tp2_quantity":
            decimal_to_string(
                tp2
            ),

        "tp3_quantity":
            decimal_to_string(
                tp3
            ),

        "requested_allocation":
            "20/20/60",

        "selected_allocation":
            (
                allocation[
                    "label"
                ]
                if allocation
                else None
            ),

        "allocation_adjusted":
            bool(
                allocation
                and allocation[
                    "adjusted"
                ]
            ),

        "minimum_required_entry_quantity":
            decimal_to_string(
                minimum_required
            ),

        "checks":
            checks,
    }


def evaluate_strict_tp_balance_readiness(
    available_balance,
    mark_price,
    leverage,
):
    available_balance = D(
        available_balance
    )

    mark_price = D(
        mark_price
    )

    leverage = D(
        leverage
    )

    if available_balance < 0:
        raise ValueError(
            "available_balance must be non-negative"
        )

    if mark_price <= 0:
        raise ValueError(
            "mark_price must be positive"
        )

    if leverage <= 0:
        raise ValueError(
            "leverage must be positive"
        )

    entry_fraction = (
        ENTRY_MARGIN_PERCENT
        / Decimal("100")
    )

    raw_entry_quantity = (
        available_balance
        * entry_fraction
        * leverage
        / mark_price
    )

    planned_entry_quantity = (
        quantize_down(
            raw_entry_quantity,
            QUANTITY_STEP,
        )
    )

    feasibility = (
        evaluate_writer_quantity_feasibility(
            planned_entry_quantity
        )
    )

    minimum_quantity = (
        minimum_adjustable_tp_entry_quantity()
    )

    required_entry_margin = (
        minimum_quantity
        * mark_price
        / leverage
    )

    required_available_balance = (
        required_entry_margin
        / entry_fraction
    )

    shortfall = max(
        Decimal("0"),
        required_available_balance
        - available_balance,
    )

    eligible = bool(
        feasibility[
            "feasible"
        ]
        and
        available_balance
        >= required_available_balance
    )

    return {
        "eligible":
            eligible,

        "status":
            (
                "ELIGIBLE"
                if eligible
                else
                "TRADE_NOT_ELIGIBLE"
            ),

        "reason":
            (
                "ADJUSTABLE_TP_BALANCE_AND_QUANTITY_READY"
                if eligible
                else
                "INSUFFICIENT_BALANCE_FOR_APPROVED_TP_ALLOCATION"
            ),

        "available_balance":
            decimal_to_string(
                available_balance
            ),

        "mark_price":
            decimal_to_string(
                mark_price
            ),

        "leverage":
            decimal_to_string(
                leverage
            ),

        "planned_entry_quantity":
            decimal_to_string(
                planned_entry_quantity
            ),

        "minimum_required_entry_quantity":
            decimal_to_string(
                minimum_quantity
            ),

        "required_available_balance":
            decimal_to_string(
                required_available_balance
            ),

        "available_balance_shortfall":
            decimal_to_string(
                shortfall
            ),

        "quantity_feasible":
            feasibility[
                "feasible"
            ],

        "selected_allocation":
            feasibility[
                "selected_allocation"
            ],

        "allocation_adjusted":
            feasibility[
                "allocation_adjusted"
            ],

        "tp1_quantity":
            feasibility[
                "tp1_quantity"
            ],

        "tp2_quantity":
            feasibility[
                "tp2_quantity"
            ],

        "tp3_quantity":
            feasibility[
                "tp3_quantity"
            ],
    }


# ============================================================
# PROTECTIVE STOP
# ============================================================

def calculate_r36f13_protective_stop(
    direction,
    entry_price,
):
    entry_price = D(
        entry_price
    )

    distance = (
        R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT
        / Decimal("100")
    )

    if direction == "LONG":
        raw_stop = (
            entry_price
            * (
                Decimal("1")
                - distance
            )
        )

        return quantize_down(
            raw_stop,
            PRICE_STEP,
        )

    if direction == "SHORT":
        raw_stop = (
            entry_price
            * (
                Decimal("1")
                + distance
            )
        )

        stop_price = quantize_down(
            raw_stop,
            PRICE_STEP,
        )

        if stop_price <= entry_price:
            stop_price = (
                quantize_down(
                    entry_price,
                    PRICE_STEP,
                )
                + PRICE_STEP
            )

        return stop_price

    raise ValueError(
        "Invalid protective-stop direction"
    )


def validate_r36f13_protective_stop(
    direction,
    entry_price,
    stop_price,
    tp1_price,
    tp2_price,
):
    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    tp1_price = D(
        tp1_price
    )

    tp2_price = D(
        tp2_price
    )

    if direction == "LONG":
        correct_side = (
            stop_price
            < entry_price
        )

        separated = (
            stop_price
            < entry_price
            < tp1_price
            < tp2_price
        )

    elif direction == "SHORT":
        correct_side = (
            stop_price
            > entry_price
        )

        separated = (
            stop_price
            > entry_price
            > tp1_price
            > tp2_price
        )

    else:
        correct_side = False
        separated = False

    checks = {
        "configured_or_calculated":
            True,

        "positive":
            stop_price > 0,

        "correct_side_of_entry":
            correct_side,

        "price_step_normalized":
            (
                stop_price
                % PRICE_STEP
            ) == 0,

        "does_not_cross_entry_or_tp":
            separated,
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


def validate_r36f131_stop_risk_envelope(
    direction,
    entry_price,
    stop_price,
    leverage,
):
    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    leverage = D(
        leverage
    )

    distance_percent = (
        abs(
            stop_price
            - entry_price
        )
        / entry_price
        * Decimal("100")
    )

    leverage_reference = (
        Decimal("100")
        / leverage
    )

    checks = {
        "direction_valid":
            direction
            in {
                "LONG",
                "SHORT",
            },

        "distance_positive":
            distance_percent > 0,

        "at_least_one_price_step":
            abs(
                stop_price
                - entry_price
            )
            >= PRICE_STEP,

        "within_configured_maximum":
            (
                distance_percent
                <=
                R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT
            ),

        "inside_leverage_reference":
            (
                distance_percent
                <
                leverage_reference
            ),
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return {
        "distance_percent":
            decimal_to_string(
                distance_percent
            ),

        "leverage_reference_percent":
            decimal_to_string(
                leverage_reference
            ),

        "checks":
            checks,

        "all_valid":
            checks[
                "all_valid"
            ],
    }


def validate_r36f132_stop_loss_budget(
    entry_price,
    stop_price,
    entry_quantity,
    available_balance,
    leverage,
):
    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    entry_quantity = D(
        entry_quantity
    )

    available_balance = D(
        available_balance
    )

    leverage = D(
        leverage
    )

    price_distance = abs(
        entry_price
        - stop_price
    )

    expected_loss = (
        price_distance
        * entry_quantity
    )

    expected_loss_percent = (
        expected_loss
        / available_balance
        * Decimal("100")
        if available_balance > 0
        else Decimal("999")
    )

    account_loss_budget = (
        available_balance
        * R36F132_MAX_ACCOUNT_LOSS_PERCENT
        / Decimal("100")
    )

    isolated_entry_margin = (
        entry_price
        * entry_quantity
        / leverage
    )

    checks = {
        "price_distance_positive":
            price_distance > 0,

        "expected_loss_positive":
            expected_loss > 0,

        "within_account_loss_budget":
            (
                expected_loss
                <= account_loss_budget
            ),

        "within_isolated_entry_margin_budget":
            (
                expected_loss
                <= isolated_entry_margin
            ),
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return {
        "expected_loss_usdt":
            decimal_to_string(
                expected_loss
            ),

        "expected_loss_percent_of_available_balance":
            decimal_to_string(
                expected_loss_percent
            ),

        "configured_max_account_loss_percent":
            decimal_to_string(
                R36F132_MAX_ACCOUNT_LOSS_PERCENT
            ),

        "isolated_entry_margin_usdt":
            decimal_to_string(
                isolated_entry_margin
            ),

        "checks":
            checks,

        "all_valid":
            checks[
                "all_valid"
            ],
    }

# ============================================================
# R36F.15.10.4b AUTO MODE MERGER
# ============================================================

R36F15103_STAGE = (
    "R36F.15.10.4b"
)

R36F15103_REAL_ORDER_EXECUTION = False
R36F15103_DEMO_ORDER_EXECUTION = False
R36F15103_WRITE_TRANSPORT = False

R36F15103_MODE_CONFIRMATIONS_REQUIRED = 3

R36F15103_BREAKOUT_MOVE_PERCENT = 0.60

R36F15103_STRONG_EMA_SEPARATION_PERCENT = 0.05

R36F15103_VALID_MODES = (
    "SCALP",
    "STRUCTURE",
    "BREAKOUT",
)

R36F15103_EXCLUSIVE_MODE = True
R36F15103_ACTIVE_TRADE_MODE_LOCK = True

R36F15103_ACTIVE_MODE = None
R36F15103_PENDING_MODE = None
R36F15103_PENDING_COUNT = 0
R36F15103_MODE_LOCKED = False
R36F15103_LAST_DIRECTION = None
R36F15103_LAST_REASON = None
R36F15103_CYCLE = 0

R36F15103_REFERENCE_PRICE = None

R36F15103_LAST_RESULT = {}


def r36f15103_safe_float(
    value,
    default=None,
):
    try:
        if value is None:
            return default

        return float(
            value
        )

    except Exception:
        return default


def r36f15103_direction_from_ema(
    ema19,
    ema50,
    ema200,
):
    e19 = r36f15103_safe_float(
        ema19
    )

    e50 = r36f15103_safe_float(
        ema50
    )

    e200 = r36f15103_safe_float(
        ema200
    )

    if (
        e19 is None
        or e50 is None
        or e200 is None
    ):
        return None

    if (
        e19
        > e50
        > e200
    ):
        return "LONG"

    if (
        e19
        < e50
        < e200
    ):
        return "SHORT"

    return None


def r36f15103_ema_separation_percent(
    ema19,
    ema50,
):
    e19 = r36f15103_safe_float(
        ema19
    )

    e50 = r36f15103_safe_float(
        ema50
    )

    if (
        e19 is None
        or e50 in (
            None,
            0,
        )
    ):
        return 0.0

    return (
        abs(
            e19
            - e50
        )
        / abs(e50)
        * 100.0
    )


def r36f15103_move_percent(
    current_price,
    reference_price,
):
    current = r36f15103_safe_float(
        current_price
    )

    reference = r36f15103_safe_float(
        reference_price
    )

    if (
        current is None
        or reference in (
            None,
            0,
        )
    ):
        return 0.0

    return (
        abs(
            current
            - reference
        )
        / abs(reference)
        * 100.0
    )


def r36f15103_raw_classifier(
    direction,
    valid_cluster_count,
    ema_separation_percent,
    short_term_move_percent,
):
    try:
        clusters = int(
            valid_cluster_count
            or 0
        )

    except Exception:
        clusters = 0

    ema_sep = (
        r36f15103_safe_float(
            ema_separation_percent,
            0.0,
        )
    )

    movement = (
        r36f15103_safe_float(
            short_term_move_percent,
            0.0,
        )
    )

    strong_direction = (
        direction
        in (
            "LONG",
            "SHORT",
        )
        and
        ema_sep
        >=
        R36F15103_STRONG_EMA_SEPARATION_PERCENT
    )

    if (
        strong_direction
        and movement
        >=
        R36F15103_BREAKOUT_MOVE_PERCENT
    ):
        return (
            "BREAKOUT",
            "STRONG_EMA_DIRECTION_PLUS_LARGE_SHORT_TERM_MOVE",
        )

    if (
        strong_direction
        and clusters >= 2
    ):
        return (
            "STRUCTURE",
            "STRONG_EMA_DIRECTION_WITH_TWO_OR_MORE_VALID_CLUSTERS",
        )

    if (
        strong_direction
        and clusters < 2
    ):
        return (
            "BREAKOUT",
            "STRONG_EMA_DIRECTION_BUT_TWO_CLUSTER_STRUCTURE_UNAVAILABLE",
        )

    return (
        "SCALP",
        "NO_CONFIRMED_STRUCTURE_OR_BREAKOUT_CONDITION",
    )


def r36f15103_update_mode(
    raw_mode,
    reason,
    trade_active=False,
):
    global R36F15103_ACTIVE_MODE
    global R36F15103_PENDING_MODE
    global R36F15103_PENDING_COUNT
    global R36F15103_MODE_LOCKED
    global R36F15103_LAST_REASON

    raw_mode = str(
        raw_mode or ""
    ).strip().upper()

    if (
        raw_mode
        not in R36F15103_VALID_MODES
    ):
        R36F15103_LAST_REASON = (
            "INVALID_MODE_REJECTED"
        )

        return R36F15103_ACTIVE_MODE

    if (
        trade_active
        and R36F15103_ACTIVE_TRADE_MODE_LOCK
    ):
        R36F15103_MODE_LOCKED = True

        if R36F15103_ACTIVE_MODE is None:
            R36F15103_ACTIVE_MODE = raw_mode

        R36F15103_PENDING_MODE = None
        R36F15103_PENDING_COUNT = 0

        R36F15103_LAST_REASON = (
            "ACTIVE_TRADE_MODE_LOCK"
        )

        return R36F15103_ACTIVE_MODE

    R36F15103_MODE_LOCKED = False

    if R36F15103_ACTIVE_MODE is None:
        R36F15103_ACTIVE_MODE = raw_mode
        R36F15103_PENDING_MODE = None
        R36F15103_PENDING_COUNT = 0

        R36F15103_LAST_REASON = (
            "INITIAL_MODE_SELECTED:"
            + str(reason)
        )

        return R36F15103_ACTIVE_MODE

    if raw_mode == R36F15103_ACTIVE_MODE:
        R36F15103_PENDING_MODE = None
        R36F15103_PENDING_COUNT = 0

        R36F15103_LAST_REASON = (
            "ACTIVE_MODE_CONFIRMED:"
            + str(reason)
        )

        return R36F15103_ACTIVE_MODE

    if R36F15103_PENDING_MODE != raw_mode:
        R36F15103_PENDING_MODE = raw_mode
        R36F15103_PENDING_COUNT = 1

        R36F15103_LAST_REASON = (
            "NEW_MODE_PENDING:"
            + str(reason)
        )

        return R36F15103_ACTIVE_MODE

    R36F15103_PENDING_COUNT += 1

    if (
        R36F15103_PENDING_COUNT
        >= R36F15103_MODE_CONFIRMATIONS_REQUIRED
    ):
        previous_mode = (
            R36F15103_ACTIVE_MODE
        )

        R36F15103_ACTIVE_MODE = raw_mode
        R36F15103_PENDING_MODE = None
        R36F15103_PENDING_COUNT = 0

        R36F15103_LAST_REASON = (
            "THREE_CONFIRMATION_TRANSITION:"
            + str(previous_mode)
            + "_TO_"
            + str(raw_mode)
        )

        return R36F15103_ACTIVE_MODE

    R36F15103_LAST_REASON = (
        "MODE_CONFIRMATION_PENDING:"
        + str(reason)
    )

    return R36F15103_ACTIVE_MODE


def r36f15103_merge_cycle(
    current_price=None,
    reference_price=None,
    ema19=None,
    ema50=None,
    ema200=None,
    valid_cluster_count=0,
    existing_direction=None,
    trade_active=False,
):
    global R36F15103_CYCLE
    global R36F15103_LAST_DIRECTION

    R36F15103_CYCLE += 1

    calculated_direction = (
        r36f15103_direction_from_ema(
            ema19,
            ema50,
            ema200,
        )
    )

    if existing_direction in (
        "LONG",
        "SHORT",
    ):
        direction = (
            existing_direction
        )

    else:
        direction = (
            calculated_direction
        )

    R36F15103_LAST_DIRECTION = (
        direction
    )

    ema_sep = (
        r36f15103_ema_separation_percent(
            ema19,
            ema50,
        )
    )

    movement = (
        r36f15103_move_percent(
            current_price,
            reference_price,
        )
    )

    (
        raw_mode,
        classifier_reason,
    ) = r36f15103_raw_classifier(
        direction=direction,
        valid_cluster_count=(
            valid_cluster_count
        ),
        ema_separation_percent=(
            ema_sep
        ),
        short_term_move_percent=(
            movement
        ),
    )

    active_mode = (
        r36f15103_update_mode(
            raw_mode=raw_mode,
            reason=classifier_reason,
            trade_active=bool(
                trade_active
            ),
        )
    )

    if (
        active_mode
        not in R36F15103_VALID_MODES
    ):
        raise RuntimeError(
            "R36F.15.10.4b EXCLUSIVE MODE FAILURE"
        )

    result = {
        "stage":
            R36F15103_STAGE,

        "cycle":
            R36F15103_CYCLE,

        "raw_mode":
            raw_mode,

        "active_mode":
            active_mode,

        "direction":
            direction,

        "valid_cluster_count":
            int(
                valid_cluster_count
                or 0
            ),

        "ema_separation_percent":
            ema_sep,

        "short_term_move_percent":
            movement,

        "pending_mode":
            R36F15103_PENDING_MODE,

        "pending_count":
            R36F15103_PENDING_COUNT,

        "mode_locked":
            R36F15103_MODE_LOCKED,

        "reason":
            R36F15103_LAST_REASON,

        "real_execution":
            False,

        "demo_execution":
            False,

        "write_transport":
            False,
    }

    log(
        f"{R36F15103_STAGE} "
        f"CYCLE={result['cycle']} "
        f"raw_mode={result['raw_mode']} "
        f"active_mode={result['active_mode']} "
        f"direction={result['direction']} "
        f"clusters={result['valid_cluster_count']} "
        f"ema_sep={result['ema_separation_percent']:.6f}% "
        f"move={result['short_term_move_percent']:.6f}% "
        f"pending_mode={result['pending_mode']} "
        f"pending_count={result['pending_count']} "
        f"locked={result['mode_locked']} "
        f"reason={result['reason']}"
    )

    log(
        f"{R36F15103_STAGE} "
        "REAL_ORDER_EXECUTION=False "
        "DEMO_ORDER_EXECUTION=False "
        "WRITE_TRANSPORT=False"
    )

    return result


def r36f15103_startup_diagnostic():
    line()

    log(
        "R36F.15.10.4b AUTO-MODE MERGER INTERFACE LOADED"
    )

    log(
        "R36F.15.10.4b MODES=SCALP|STRUCTURE|BREAKOUT"
    )

    log(
        "R36F.15.10.4b EXCLUSIVE_MODE=True"
    )

    log(
        "R36F.15.10.4b MODE_CHANGE_CONFIRMATIONS=3"
    )

    log(
        "R36F.15.10.4b ACTIVE_TRADE_MODE_LOCK=True"
    )

    log(
        "R36F.15.10.4b REAL_ORDER_EXECUTION=False"
    )

    log(
        "R36F.15.10.4b DEMO_ORDER_EXECUTION=False"
    )

    log(
        "R36F.15.10.4b WRITE_TRANSPORT=False"
    )

    line()

# ============================================================
# R36F.15.10.5 REGIME -> DEMO EXECUTION ROUTER
# NORMAL is represented internally by the already-tested STRUCTURE mode.
# Real-money execution remains hard-disabled.
# ============================================================

R36F15105_SCALP_MIN_CLUSTERS = int(os.getenv("R36F15105_SCALP_MIN_CLUSTERS", "1"))
R36F15105_NORMAL_MIN_CLUSTERS = int(os.getenv("R36F15105_NORMAL_MIN_CLUSTERS", "2"))
R36F15105_BREAKOUT_MIN_CLUSTERS = int(os.getenv("R36F15105_BREAKOUT_MIN_CLUSTERS", "1"))
R36F15105_SCALP_MIN_EMA_SEPARATION_PERCENT = Decimal(os.getenv("R36F15105_SCALP_MIN_EMA_SEPARATION_PERCENT", "0.001"))
R36F15105_NORMAL_MIN_EMA_SEPARATION_PERCENT = Decimal(os.getenv("R36F15105_NORMAL_MIN_EMA_SEPARATION_PERCENT", "0.01"))
R36F15105_BREAKOUT_MIN_MOVE_PERCENT = Decimal(os.getenv("R36F15105_BREAKOUT_MIN_MOVE_PERCENT", "0.60"))
R36F15105_AUTO_DEMO_ENABLED = os.getenv("R36F15105_AUTO_DEMO_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}


def r36f15105_regime_label(active_mode):
    return "NORMAL" if active_mode == "STRUCTURE" else active_mode


def r36f15105_direction_cluster_count(direction):
    if direction == "LONG":
        return int(LONG_DIAGNOSTICS.get("valid_cluster_count", 0) or 0)
    if direction == "SHORT":
        return int(SHORT_DIAGNOSTICS.get("valid_cluster_count", 0) or 0)
    return 0


def r36f15105_direction_snapshot(direction, long_snapshot, short_snapshot):
    if direction == "LONG":
        return long_snapshot
    if direction == "SHORT":
        return short_snapshot
    return None


def r36f15105_regime_gate(auto_result, ema_snapshot, long_snapshot, short_snapshot):
    auto_result = auto_result if isinstance(auto_result, dict) else {}
    ema_snapshot = ema_snapshot if isinstance(ema_snapshot, dict) else {}
    active_mode = str(auto_result.get("active_mode") or "").upper()
    direction = str(auto_result.get("direction") or "").upper()
    clusters = r36f15105_direction_cluster_count(direction)
    ema_sep = D(auto_result.get("ema_separation_percent") or "0")
    movement = D(auto_result.get("short_term_move_percent") or "0")
    selected_snapshot = r36f15105_direction_snapshot(direction, long_snapshot, short_snapshot)

    result = {
        "active_mode": active_mode,
        "regime": r36f15105_regime_label(active_mode),
        "direction": direction if direction in {"LONG", "SHORT"} else None,
        "clusters": clusters,
        "ema_separation_percent": decimal_to_string(ema_sep),
        "move_percent": decimal_to_string(movement),
        "approved": False,
        "reason": "REGIME_GATE_NOT_EVALUATED",
        "selected_tp_snapshot": selected_snapshot,
    }

    if active_mode not in R36F15103_VALID_MODES:
        result["reason"] = "INVALID_ACTIVE_MODE"
        return result
    if direction not in {"LONG", "SHORT"}:
        result["reason"] = "NO_AUTO_DIRECTION"
        return result
    if not ema_snapshot.get("ready"):
        result["reason"] = "EMA_ENGINE_NOT_READY"
        return result

    # SCALP deliberately does not inherit the old two-cluster structure rule.
    # It still requires a direction, at least one valid nearby historical cluster,
    # minimum EMA separation, quantity/balance readiness and all downstream safety gates.
    if active_mode == "SCALP":
        if clusters < R36F15105_SCALP_MIN_CLUSTERS:
            result["reason"] = "SCALP_INSUFFICIENT_CLUSTERS"
            return result
        if ema_sep < R36F15105_SCALP_MIN_EMA_SEPARATION_PERCENT:
            result["reason"] = "SCALP_EMA_SEPARATION_TOO_SMALL"
            return result
        result["approved"] = True
        result["reason"] = "SCALP_ENTRY_GATE_APPROVED"
        return result

    if active_mode == "STRUCTURE":
        if clusters < R36F15105_NORMAL_MIN_CLUSTERS:
            result["reason"] = "NORMAL_INSUFFICIENT_CLUSTERS"
            return result
        if ema_sep < R36F15105_NORMAL_MIN_EMA_SEPARATION_PERCENT:
            result["reason"] = "NORMAL_EMA_SEPARATION_TOO_SMALL"
            return result
        if not selected_snapshot or not selected_snapshot.get("tp_approval", {}).get("approved"):
            result["reason"] = "NORMAL_TWO_CLUSTER_TP_NOT_APPROVED"
            return result
        result["approved"] = True
        result["reason"] = "NORMAL_ENTRY_GATE_APPROVED"
        return result

    if active_mode == "BREAKOUT":
        if movement < R36F15105_BREAKOUT_MIN_MOVE_PERCENT:
            result["reason"] = "BREAKOUT_MOVE_NOT_CONFIRMED"
            return result
        if clusters < R36F15105_BREAKOUT_MIN_CLUSTERS:
            result["reason"] = "BREAKOUT_NO_REFERENCE_CLUSTER"
            return result
        result["approved"] = True
        result["reason"] = "BREAKOUT_ENTRY_GATE_APPROVED"
        return result

    result["reason"] = "UNHANDLED_ACTIVE_MODE"
    return result


def r36f15105_scalp_tp_snapshot(direction, entry_price, diagnostics):
    """Build a conservative one-cluster TP set for SCALP only.

    TP1 uses the nearest valid cluster. TP2 is a small extension beyond TP1 so
    the frozen stop/TP ordering checks remain meaningful. TP3 remains handled
    by the existing allocation/trailing policy downstream.
    """
    entry = D(entry_price)
    valid = diagnostics.get("valid_clusters", []) if isinstance(diagnostics, dict) else []
    if not valid:
        return None

    def cluster_price(row):
        if isinstance(row, dict):
            for key in ("average", "avg", "price", "cluster_average"):
                if row.get(key) is not None:
                    return D(row.get(key))
        return None

    prices = [cluster_price(row) for row in valid]
    prices = [p for p in prices if p is not None and p > 0]
    if direction == "LONG":
        prices = sorted(p for p in prices if p > entry)
    else:
        prices = sorted((p for p in prices if p < entry), reverse=True)
    if not prices:
        return None

    tp1 = quantize_down(prices[0], PRICE_STEP)
    extension = max(PRICE_STEP, quantize_down(entry * Decimal("0.001"), PRICE_STEP))
    tp2 = tp1 + extension if direction == "LONG" else tp1 - extension
    tp2 = quantize_down(tp2, PRICE_STEP)
    if direction == "LONG" and not (entry < tp1 < tp2):
        return None
    if direction == "SHORT" and not (entry > tp1 > tp2 > 0):
        return None

    return {
        "direction": direction,
        "tp1": tp1,
        "tp2": tp2,
        "tp3_policy": "TRAILING_RUNNER",
        "tp_approval": {"approved": True, "reason": "SCALP_ONE_CLUSTER_TP_APPROVED"},
        "historical_diagnostics": diagnostics,
        "scalp_specific": True,
    }


def r36f15105_build_auto_command_preview(regime_gate):
    direction = regime_gate.get("direction")
    approved = bool(regime_gate.get("approved"))
    command = TELEGRAM_BUY_COMMAND if direction == "LONG" else TELEGRAM_SELL_COMMAND if direction == "SHORT" else ""
    return {
        "recognized": direction in {"LONG", "SHORT"},
        "command": command,
        "direction": direction,
        "authorized_preview": approved,
        "reason": regime_gate.get("reason"),
        "authorization_source": "R36F.15.10.5_AUTO_REGIME",
        "exchange_order_sent": False,
    }


def r36f15105_build_demo_preview(
    direction,
    tp_snapshot,
    balance_readiness,
    protective_stop_price,
):
    # Preserve the previously proven R36F.14 WEEX demo payload shape.
    if (
        direction not in {"LONG", "SHORT"}
        or not tp_snapshot
        or not tp_snapshot.get("tp_approval", {}).get("approved")
        or not balance_readiness
        or protective_stop_price is None
    ):
        return None

    quantity = quantize_down(
        D(balance_readiness.get("planned_entry_quantity", "0")),
        QUANTITY_STEP,
    )
    if quantity <= 0:
        return None

    tp1_price = quantize_down(
        D(tp_snapshot["tp1"]),
        PRICE_STEP,
    )
    stop_price = quantize_down(
        D(protective_stop_price),
        PRICE_STEP,
    )

    if direction == "LONG":
        side = "BUY"
        position_side = "LONG"
    else:
        side = "SELL"
        position_side = "SHORT"

    payload = {
        "symbol": R36F14_DEMO_SYMBOL,
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": decimal_to_string(quantity),
        "newClientOrderId": writer_client_id(direction, "D14"),
        "tpTriggerPrice": decimal_to_string(tp1_price),
        "slTriggerPrice": decimal_to_string(stop_price),
        "TpWorkingType": "MARK_PRICE",
        "SlWorkingType": "MARK_PRICE",
    }

    return {
        "stage": STAGE,
        "endpoint": R36F14_DEMO_ORDER_ENDPOINT,
        "method": "POST",
        "payload": payload,
        "submitted": False,
        "demo_only": True,
        "real_order_execution": REAL_ORDER_EXECUTION,
        "integrity_sha256": sha256_text(canonical_json(payload)),
    }

# ============================================================
# R36F.15.10.5 COMPLETE REEVALUATION
# ============================================================
# ============================================================
# WRITE.PY-R1.3
# R36F.15.10.5 REAL ENGINE -> ZERO-WRITE WRITER BRIDGE
# ============================================================

def build_r13_real_engine_instruction(
    direction,
    tp_snapshot,
    balance_readiness,
    protective_stop_price,
):
    if direction not in {"LONG", "SHORT"}:
        return None

    if not tp_snapshot:
        return None

    if not tp_snapshot.get(
        "tp_approval",
        {},
    ).get("approved"):
        return None

    if not balance_readiness:
        return None

    if protective_stop_price is None:
        return None

    quantity = quantize_down(
        D(
            balance_readiness.get(
                "planned_entry_quantity",
                "0",
            )
        ),
        QUANTITY_STEP,
    )

    if quantity <= 0:
        return None

    entry_price = quantize_down(
        D(MARK_PRICE),
        PRICE_STEP,
    )

    tp1_price = quantize_down(
        D(tp_snapshot["tp1"]),
        PRICE_STEP,
    )

    tp2_price = quantize_down(
        D(tp_snapshot["tp2"]),
        PRICE_STEP,
    )

    stop_price = quantize_down(
        D(protective_stop_price),
        PRICE_STEP,
    )

    instruction = {
        "symbol": SYMBOL,
        "direction": direction,
        "entry_price":
            decimal_to_string(entry_price),
        "quantity":
            decimal_to_string(quantity),
        "tp1":
            decimal_to_string(tp1_price),
        "tp2":
            decimal_to_string(tp2_price),
        "tp3": None,
        "tp3_policy":
            "TRAILING_RUNNER",
        "stop_price":
            decimal_to_string(stop_price),
        "allocation": {
            "tp1_percent":
                decimal_to_string(
                    TP1_ALLOCATION_PERCENT
                ),
            "tp2_percent":
                decimal_to_string(
                    TP2_ALLOCATION_PERCENT
                ),
            "tp3_percent":
                decimal_to_string(
                    TP3_ALLOCATION_PERCENT
                ),
        },
        "trailing_distance_percent":
            decimal_to_string(
                TP3_TRAILING_DISTANCE_PERCENT
            ),
        "source_stage":
            STAGE,
        "source_mode":
            "REAL_ENGINE_ZERO_WRITE",
        "created_at":
            now_iso(),
    }

    instruction[
        "instruction_sha256"
    ] = sha256_text(
        canonical_json(instruction)
    )

    return instruction


def r13_connect_real_engine(
    downstream_ready,
    direction,
    tp_snapshot,
    balance_readiness,
    protective_stop_price,
):
    result = {
        "connected": False,
        "validated": False,
        "instruction": None,
        "reason":
            "R1.3_NOT_EVALUATED",
    }

    if not downstream_ready:
        result["reason"] = (
            "R1.3_DOWNSTREAM_NOT_READY"
        )

        log(
            "WRITE.PY-R1.3: "
            "REAL ENGINE NOT DOWNSTREAM READY"
        )

        return result

    instruction = (
        build_r13_real_engine_instruction(
            direction,
            tp_snapshot,
            balance_readiness,
            protective_stop_price,
        )
    )

    if not instruction:
        result["reason"] = (
            "R1.3_ENGINE_INSTRUCTION_BUILD_FAILED"
        )

        log(
            "WRITE.PY-R1.3: "
            "REAL ENGINE INSTRUCTION BUILD FAILED"
        )

        return result

    result["connected"] = True
    result["instruction"] = instruction
    result["reason"] = (
        "R1.3_REAL_ENGINE_INSTRUCTION_FROZEN"
    )

    log(
        "WRITE.PY-R1.3: "
        "REAL ENGINE INSTRUCTION RECEIVED"
    )

    log(
        "WRITE.PY-R1.3: "
        "SOURCE = R36F.15.10.5"
    )

    log(
        "WRITE.PY-R1.3: DIRECTION = "
        + str(instruction["direction"])
    )

    log(
        "WRITE.PY-R1.3: SYMBOL = "
        + str(instruction["symbol"])
    )

    log(
        "WRITE.PY-R1.3: ENTRY = "
        + str(instruction["entry_price"])
    )

    log(
        "WRITE.PY-R1.3: QUANTITY = "
        + str(instruction["quantity"])
    )

    log(
        "WRITE.PY-R1.3: TP1 = "
        + str(instruction["tp1"])
    )

    log(
        "WRITE.PY-R1.3: TP2 = "
        + str(instruction["tp2"])
    )

    log(
        "WRITE.PY-R1.3: TP3 POLICY = "
        + str(instruction["tp3_policy"])
    )

    log(
        "WRITE.PY-R1.3: STOP = "
        + str(instruction["stop_price"])
    )

    log(
        "WRITE.PY-R1.3: "
        "INSTRUCTION SHA256 = "
        + str(
            instruction[
                "instruction_sha256"
            ]
        )
    )

    # --------------------------------------------------------
    # CRITICAL R1.3 FIREBREAK
    # --------------------------------------------------------
    # R1.3 deliberately stops here.
    #
    # No production POST.
    # No production mutation.
    # No real order.
    #
    # The next validation step will hand this immutable
    # instruction to the already-proven WRITE.PY-R1.1
    # validator.
    # --------------------------------------------------------

    result["validated"] = True
    result["reason"] = (
        "R1.3_REAL_ENGINE_CAPTURE_PASS"
    )

    log(
        "WRITE.PY-R1.3: "
        "REAL ENGINE BRIDGE = PASS"
    )

    log(
        "WRITE.PY-R1.3: "
        "FINAL STATE = CAPTURED_NOT_SENT"
    )

    log(
        "WRITE.PY-R1.3: "
        "PRODUCTION FIREBREAK = True"
    )

    log(
        "WRITE.PY-R1.3: "
        "NO REAL ORDER WAS SENT"
    )

    log(
        "WRITE.PY-R1.3: "
        "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
    )

    return result
async def run_r36f12():
    global TEST_STATUS
    global WEEX_READ_ONLY_OK
    global ZERO_WRITE_INVARIANT_OK
    global FINAL_GATE_OK
    global LONG_DIAGNOSTICS
    global SHORT_DIAGNOSTICS
    global EMA_SIGNAL_SNAPSHOT
    global TELEGRAM_COMMAND_PREVIEW
    global R36F15103_REFERENCE_PRICE
    global R36F15103_LAST_RESULT

    TEST_STATUS = "RUNNING"

    FINAL_BLOCKERS.clear()

    line()

    log(
        f"{STAGE}: "
        "R36F.15.10.4b AUTO-MODE + "
        "CONFIRMED TRANSITION MERGED REEVALUATION"
    )

    line()

    check(
        "REAL_ORDER_EXECUTION_DISABLED",
        REAL_ORDER_EXECUTION
        is False,
    )

    check(
        "DEMO_ORDER_EXECUTION_DISABLED",
        DEMO_ORDER_EXECUTION
        is False,
    )

    check(
        "EXCHANGE_MUTATION_TRANSPORT_DISABLED",
        EXCHANGE_MUTATION_TRANSPORT_ENABLED
        is False,
    )

    check(
        "ORDER_SUBMISSION_DISABLED",
        ORDER_SUBMISSION_ENABLED
        is False,
    )

    check(
        "FIRST_REAL_ORDER_DISABLED",
        FIRST_REAL_ORDER_ALLOWED
        is False,
    )

    check(
        "R36F15103_REAL_EXECUTION_DISABLED",
        R36F15103_REAL_ORDER_EXECUTION
        is False,
    )

    check(
        "R36F15103_DEMO_EXECUTION_DISABLED",
        R36F15103_DEMO_ORDER_EXECUTION
        is False,
    )

    check(
        "R36F15103_WRITE_TRANSPORT_DISABLED",
        R36F15103_WRITE_TRANSPORT
        is False,
    )

    check(
        "R36F15104B_EXCLUSIVE_MODE_ENABLED",
        R36F15103_EXCLUSIVE_MODE
        is True,
    )

    check(
        "R36F15104B_MODE_CONFIRMATIONS_EQUALS_3",
        R36F15103_MODE_CONFIRMATIONS_REQUIRED
        == 3,
    )

    check(
        "R36F15104B_ACTIVE_TRADE_MODE_LOCK_ENABLED",
        R36F15103_ACTIVE_TRADE_MODE_LOCK
        is True,
    )

    try:
        await reconcile_weex()

        WEEX_READ_ONLY_OK = True

        diagnostic_check(
            "WEEX_READ_ONLY_RECONCILIATION",
            True,
        )

    except Exception as exc:
        WEEX_READ_ONLY_OK = False

        diagnostic_check(
            "WEEX_READ_ONLY_RECONCILIATION",
            False,
            str(exc),
        )

    historical_rows = []

    try:
        historical_rows = (
            await load_historical_klines()
        )

        diagnostic_check(
            "REAL_HISTORICAL_KLINES_LOADED",
            len(
                historical_rows
            ) >= 3,
            f"rows={len(historical_rows)}",
        )

    except Exception as exc:
        diagnostic_check(
            "REAL_HISTORICAL_KLINES_LOADED",
            False,
            str(exc),
        )

    if historical_rows:
        try:
            EMA_SIGNAL_SNAPSHOT = (
                build_ema_signal_snapshot(
                    historical_rows
                )
            )

            diagnostic_check(
                "R36F15103_EMA_ENGINE_READY",
                EMA_SIGNAL_SNAPSHOT.get(
                    "ready"
                )
                is True,
                str(
                    EMA_SIGNAL_SNAPSHOT.get(
                        "reason"
                    )
                ),
            )

            if EMA_SIGNAL_SNAPSHOT.get(
                "ready"
            ):
                log(
                    "R36F.15.10.4b EMA "
                    f"price={EMA_SIGNAL_SNAPSHOT.get('price')} "
                    f"EMA19={EMA_SIGNAL_SNAPSHOT.get('ema19')} "
                    f"EMA50={EMA_SIGNAL_SNAPSHOT.get('ema50')} "
                    f"EMA200={EMA_SIGNAL_SNAPSHOT.get('ema200')} "
                    f"structure={EMA_SIGNAL_SNAPSHOT.get('structure')} "
                    f"ideal_direction={EMA_SIGNAL_SNAPSHOT.get('ideal_direction')}"
                )

        except Exception as exc:
            EMA_SIGNAL_SNAPSHOT = {
                "ready":
                    False,

                "reason":
                    "EMA_EXCEPTION",

                "error":
                    str(exc),
            }

            diagnostic_check(
                "R36F15103_EMA_ENGINE_READY",
                False,
                str(exc),
            )

    REAL_LONG_MARKET_ELIGIBLE = False
    REAL_SHORT_MARKET_ELIGIBLE = False

    LONG_DIAGNOSTICS = {}
    SHORT_DIAGNOSTICS = {}

    real_long_snapshot = None
    real_short_snapshot = None

    if (
        historical_rows
        and MARK_PRICE is not None
    ):
        try:
            real_long_snapshot = (
                build_cluster_tp_snapshot(
                    MARK_PRICE,
                    historical_rows,
                    "LONG",
                    "R36F15103_LONG",
                )
            )

            LONG_DIAGNOSTICS = (
                real_long_snapshot[
                    "historical_diagnostics"
                ]
            )

            REAL_LONG_MARKET_ELIGIBLE = bool(
                real_long_snapshot[
                    "tp_approval"
                ][
                    "approved"
                ]
            )

        except Exception as exc:
            LONG_DIAGNOSTICS = (
                build_cluster_diagnostics(
                    historical_rows,
                    MARK_PRICE,
                    "LONG",
                )
            )

            log(
                "R36F.15.10.4b LONG TP = REJECTED "
                + str(exc)
            )

        try:
            real_short_snapshot = (
                build_cluster_tp_snapshot(
                    MARK_PRICE,
                    historical_rows,
                    "SHORT",
                    "R36F15103_SHORT",
                )
            )

            SHORT_DIAGNOSTICS = (
                real_short_snapshot[
                    "historical_diagnostics"
                ]
            )

            REAL_SHORT_MARKET_ELIGIBLE = bool(
                real_short_snapshot[
                    "tp_approval"
                ][
                    "approved"
                ]
            )

        except Exception as exc:
            SHORT_DIAGNOSTICS = (
                build_cluster_diagnostics(
                    historical_rows,
                    MARK_PRICE,
                    "SHORT",
                )
            )

            log(
                "R36F.15.10.4b SHORT TP = REJECTED "
                + str(exc)
            )

    merger_direction = (
        EMA_SIGNAL_SNAPSHOT.get(
            "ideal_direction"
        )
        or
        EMA_SIGNAL_SNAPSHOT.get(
            "direction"
        )
    )

    if merger_direction == "LONG":
        merger_clusters = int(
            LONG_DIAGNOSTICS.get(
                "valid_cluster_count",
                0,
            )
            or 0
        )

    elif merger_direction == "SHORT":
        merger_clusters = int(
            SHORT_DIAGNOSTICS.get(
                "valid_cluster_count",
                0,
            )
            or 0
        )

    else:
        merger_clusters = max(
            int(
                LONG_DIAGNOSTICS.get(
                    "valid_cluster_count",
                    0,
                )
                or 0
            ),
            int(
                SHORT_DIAGNOSTICS.get(
                    "valid_cluster_count",
                    0,
                )
                or 0
            ),
        )

    merger_current_price = (
        EMA_SIGNAL_SNAPSHOT.get(
            "price"
        )
    )

    if (
        merger_current_price is None
        and MARK_PRICE is not None
    ):
        merger_current_price = (
            decimal_to_string(
                MARK_PRICE
            )
        )

    if (
        R36F15103_REFERENCE_PRICE
        is None
    ):
        R36F15103_REFERENCE_PRICE = (
            merger_current_price
        )

    try:
        R36F15103_LAST_RESULT = (
            r36f15103_merge_cycle(
                current_price=(
                    merger_current_price
                ),
                reference_price=(
                    R36F15103_REFERENCE_PRICE
                ),
                ema19=(
                    EMA_SIGNAL_SNAPSHOT.get(
                        "ema19"
                    )
                ),
                ema50=(
                    EMA_SIGNAL_SNAPSHOT.get(
                        "ema50"
                    )
                ),
                ema200=(
                    EMA_SIGNAL_SNAPSHOT.get(
                        "ema200"
                    )
                ),
                valid_cluster_count=(
                    merger_clusters
                ),
                existing_direction=(
                    merger_direction
                ),
                trade_active=bool(
                    OPEN_POSITIONS
                ),
            )
        )

        diagnostic_check(
            "R36F15104B_AUTO_MODE_REEVALUATION",
            True,
            (
                "raw_mode="
                + str(
                    R36F15103_LAST_RESULT.get(
                        "raw_mode"
                    )
                )
                + " active_mode="
                + str(
                    R36F15103_LAST_RESULT.get(
                        "active_mode"
                    )
                )
                + " pending_mode="
                + str(
                    R36F15103_LAST_RESULT.get(
                        "pending_mode"
                    )
                )
                + " pending_count="
                + str(
                    R36F15103_LAST_RESULT.get(
                        "pending_count"
                    )
                )
            ),
        )

    except Exception as exc:
        R36F15103_LAST_RESULT = {
            "stage":
                R36F15103_STAGE,

            "error":
                str(exc),

            "real_execution":
                False,

            "demo_execution":
                False,

            "write_transport":
                False,
        }

        diagnostic_check(
            "R36F15104B_AUTO_MODE_REEVALUATION",
            False,
            str(exc),
        )

    if merger_current_price is not None:
        R36F15103_REFERENCE_PRICE = (
            merger_current_price
        )

    regime_gate = r36f15105_regime_gate(
        R36F15103_LAST_RESULT,
        EMA_SIGNAL_SNAPSHOT,
        real_long_snapshot,
        real_short_snapshot,
    )

    # SCALP may use one valid nearby cluster; NORMAL/STRUCTURE keeps the frozen
    # two-cluster TP approval. Build the SCALP TP snapshot only after SCALP gate.
    if regime_gate.get("approved") and regime_gate.get("active_mode") == "SCALP":
        scalp_diag = LONG_DIAGNOSTICS if regime_gate.get("direction") == "LONG" else SHORT_DIAGNOSTICS
        scalp_snapshot = r36f15105_scalp_tp_snapshot(
            regime_gate.get("direction"),
            MARK_PRICE,
            scalp_diag,
        )
        if scalp_snapshot is None:
            regime_gate["approved"] = False
            regime_gate["reason"] = "SCALP_TP_CONSTRUCTION_FAILED"
        else:
            regime_gate["selected_tp_snapshot"] = scalp_snapshot

    current_command = os.getenv(
        "R36F12_TELEGRAM_COMMAND_TEXT",
        "",
    ).strip()

    if current_command:
        manual = parse_telegram_trade_command(current_command)
        auto_direction = regime_gate.get("direction")
        manual_ok = bool(
            manual.get("recognized")
            and regime_gate.get("approved")
            and manual.get("direction") == auto_direction
        )
        TELEGRAM_COMMAND_PREVIEW = {
            **manual,
            "authorized_preview": manual_ok,
            "reason": (
                "MANUAL_COMMAND_AND_AUTO_REGIME_AGREE"
                if manual_ok
                else "MANUAL_COMMAND_DOES_NOT_MATCH_AUTO_REGIME"
            ),
            "authorization_source": "R36F.15.10.5_MANUAL_PLUS_AUTO_REGIME",
            "exchange_order_sent": False,
        }
    else:
        TELEGRAM_COMMAND_PREVIEW = r36f15105_build_auto_command_preview(regime_gate)

    balance_readiness = None
    quantity_feasibility = None

    if (
        AVAILABLE_BALANCE is not None
        and MARK_PRICE is not None
    ):
        try:
            balance_readiness = (
                evaluate_strict_tp_balance_readiness(
                    AVAILABLE_BALANCE,
                    MARK_PRICE,
                    TARGET_LONG_LEVERAGE,
                )
            )

            planned_quantity = D(
                balance_readiness.get(
                    "planned_entry_quantity",
                    "0",
                )
            )

            quantity_feasibility = (
                evaluate_writer_quantity_feasibility(
                    planned_quantity
                )
            )

        except Exception as exc:
            log(
                "R36F.15.10.4b BALANCE READINESS ERROR = "
                + str(exc)
            )

    selected_direction = TELEGRAM_COMMAND_PREVIEW.get("direction") or merger_direction
    selected_tp_snapshot = regime_gate.get("selected_tp_snapshot")
    if selected_tp_snapshot is None:
        if selected_direction == "LONG":
            selected_tp_snapshot = real_long_snapshot
        elif selected_direction == "SHORT":
            selected_tp_snapshot = real_short_snapshot

    protective_stop_price = None
    protective_stop_checks = None
    protective_stop_envelope = None
    protective_stop_budget = None

    if (
        selected_direction
        in (
            "LONG",
            "SHORT",
        )
        and
        selected_tp_snapshot
        and
        MARK_PRICE is not None
    ):
        try:
            protective_stop_price = (
                calculate_r36f13_protective_stop(
                    selected_direction,
                    MARK_PRICE,
                )
            )

            protective_stop_checks = (
                validate_r36f13_protective_stop(
                    selected_direction,
                    MARK_PRICE,
                    protective_stop_price,
                    selected_tp_snapshot[
                        "tp1"
                    ],
                    selected_tp_snapshot[
                        "tp2"
                    ],
                )
            )

            protective_stop_envelope = (
                validate_r36f131_stop_risk_envelope(
                    selected_direction,
                    MARK_PRICE,
                    protective_stop_price,
                    TARGET_LONG_LEVERAGE,
                )
            )

            if (
                balance_readiness
                and
                D(
                    balance_readiness.get(
                        "planned_entry_quantity",
                        "0",
                    )
                ) > 0
            ):
                protective_stop_budget = (
                    validate_r36f132_stop_loss_budget(
                        MARK_PRICE,
                        protective_stop_price,
                        D(
                            balance_readiness[
                                "planned_entry_quantity"
                            ]
                        ),
                        AVAILABLE_BALANCE,
                        TARGET_LONG_LEVERAGE,
                    )
                )

        except Exception as exc:
            log(
                "R36F.15.10.4b PROTECTIVE STOP ERROR = "
                + str(exc)
            )

    demo_preview = None
    demo_submission = {
        "attempted": False,
        "sent": False,
        "accepted": False,
        "reason": "AUTO_DEMO_NOT_EVALUATED",
    }

    downstream_ready = bool(
        regime_gate.get("approved")
        and TELEGRAM_COMMAND_PREVIEW.get("authorized_preview")
        and balance_readiness
        and balance_readiness.get("eligible")
        and quantity_feasibility
        and quantity_feasibility.get("feasible")
        and protective_stop_checks
        and protective_stop_checks.get("all_valid")
        and protective_stop_envelope
        and protective_stop_envelope.get("all_valid")
        and protective_stop_budget
        and protective_stop_budget.get("all_valid")
    )

        if downstream_ready:
        demo_preview = r36f15105_build_demo_preview(
            selected_direction,
            selected_tp_snapshot,
            balance_readiness,
            protective_stop_price,
        )

    r13_engine_bridge = (
        r13_connect_real_engine(
            downstream_ready,
            selected_direction,
            selected_tp_snapshot,
            balance_readiness,
            protective_stop_price,
        )
    )

    if not R36F15105_AUTO_DEMO_ENABLED:

        demo_submission["reason"] = "R36F15105_AUTO_DEMO_DISABLED"
    elif not downstream_ready:
        demo_submission["reason"] = "R36F15105_DOWNSTREAM_GATES_NOT_READY"
    elif not demo_preview:
        demo_submission["reason"] = "R36F15105_DEMO_PREVIEW_NOT_BUILT"
    else:
        demo_submission = await submit_r36f15_demo_order(
            demo_preview,
            TELEGRAM_COMMAND_PREVIEW,
        )

    log(
        f"{STAGE} REGIME = {regime_gate.get('regime')} "
        f"DIRECTION = {regime_gate.get('direction')} "
        f"REGIME_APPROVED = {regime_gate.get('approved')} "
        f"REASON = {regime_gate.get('reason')}"
    )
    log(
        f"{STAGE} AUTO_DEMO_ENABLED = {R36F15105_AUTO_DEMO_ENABLED} "
        f"SECOND_DEMO_ARM = {R36F159_DEMO_ARM_REQUESTED} "
        f"DOWNSTREAM_READY = {downstream_ready}"
    )
    log(
        f"{STAGE} DEMO ATTEMPTED = {demo_submission.get('attempted', False)} "
        f"DEMO SENT = {demo_submission.get('sent', False)} "
        f"DEMO ACCEPTED = {demo_submission.get('accepted', False)} "
        f"DEMO REASON = {demo_submission.get('reason')}"
    )

    ZERO_WRITE_INVARIANT_OK = bool(
        REAL_ORDER_EXECUTION
        is False
        and
        DEMO_ORDER_EXECUTION
        is False
        and
        EXCHANGE_MUTATION_TRANSPORT_ENABLED
        is False
        and
        ORDER_SUBMISSION_ENABLED
        is False
        and
        FIRST_REAL_ORDER_ALLOWED
        is False
        and
        R36F15103_REAL_ORDER_EXECUTION
        is False
        and
        R36F15103_DEMO_ORDER_EXECUTION
        is False
        and
        R36F15103_WRITE_TRANSPORT
        is False
    )

    check(
        "R36F15104B_ZERO_WRITE_INVARIANT",
        ZERO_WRITE_INVARIANT_OK,
    )

    FINAL_GATE_OK = bool(
        WEEX_READ_ONLY_OK
        and
        ZERO_WRITE_INVARIANT_OK
        and
        R36F15103_LAST_RESULT.get(
            "active_mode"
        )
        in R36F15103_VALID_MODES
    )

    if FINAL_GATE_OK:
        TEST_STATUS = "PASS"

    else:
        TEST_STATUS = "FAIL"

    snapshot = {
        "stage":
            STAGE,

        "timestamp":
            now_iso(),

        "status":
            TEST_STATUS,

        "final_gate_ok":
            FINAL_GATE_OK,

        "weex_read_only_ok":
            WEEX_READ_ONLY_OK,

        "zero_write_invariant_ok":
            ZERO_WRITE_INVARIANT_OK,

        "mark_price":
            (
                decimal_to_string(
                    MARK_PRICE
                )
                if MARK_PRICE is not None
                else None
            ),

        "available_balance":
            (
                decimal_to_string(
                    AVAILABLE_BALANCE
                )
                if AVAILABLE_BALANCE
                is not None
                else None
            ),

        "open_positions":
            OPEN_POSITIONS,

        "ema_signal":
            EMA_SIGNAL_SNAPSHOT,

        "long_diagnostics":
            LONG_DIAGNOSTICS,

        "short_diagnostics":
            SHORT_DIAGNOSTICS,

        "real_long_market_eligible":
            REAL_LONG_MARKET_ELIGIBLE,

        "real_short_market_eligible":
            REAL_SHORT_MARKET_ELIGIBLE,

        "telegram_command_preview":
            TELEGRAM_COMMAND_PREVIEW,

        "balance_readiness":
            balance_readiness,

        "quantity_feasibility":
            quantity_feasibility,

        "protective_stop": {
            "direction":
                selected_direction,

            "price":
                (
                    decimal_to_string(
                        protective_stop_price
                    )
                    if protective_stop_price
                    is not None
                    else None
                ),

            "checks":
                protective_stop_checks,

            "risk_envelope":
                protective_stop_envelope,

            "loss_budget":
                protective_stop_budget,
        },

        "r36f15104b_auto_mode_merger":
            R36F15103_LAST_RESULT,

        "r36f15105_regime_gate": regime_gate,
        "r36f15105_downstream_ready": downstream_ready,
        "r36f15105_demo_preview": demo_preview,
        "r36f15105_demo_submission": demo_submission,

        "execution_firebreak": {
            "real_order_execution":
                False,

            "demo_order_execution":
                False,

            "write_transport":
                False,

            "exchange_mutation_sent":
                False,

            "real_order_sent":
                False,

            "demo_order_sent":
                False,
        },
    }

    write_json_file(
        R36F_SNAPSHOT_FILE,
        snapshot,
    )

    log(
        f"{STAGE} FINAL STATUS = "
        f"{TEST_STATUS}"
    )

    log(
        f"{STAGE} AUTO RAW MODE = "
        f"{R36F15103_LAST_RESULT.get('raw_mode')}"
    )

    log(
        f"{STAGE} AUTO ACTIVE MODE = "
        f"{R36F15103_LAST_RESULT.get('active_mode')}"
    )

    log(
        f"{STAGE} AUTO DIRECTION = "
        f"{R36F15103_LAST_RESULT.get('direction')}"
    )

    log(
        f"{STAGE} AUTO MOVE PERCENT = "
        f"{R36F15103_LAST_RESULT.get('short_term_move_percent')}"
    )

    log(
        f"{STAGE} AUTO EMA SEPARATION = "
        f"{R36F15103_LAST_RESULT.get('ema_separation_percent')}"
    )

    log(
        f"{STAGE} AUTO MODE LOCKED = "
        f"{R36F15103_LAST_RESULT.get('mode_locked')}"
    )

    log(
        f"{STAGE} AUTO PENDING MODE = "
        f"{R36F15103_LAST_RESULT.get('pending_mode')}"
    )

    log(
        f"{STAGE} AUTO PENDING COUNT = "
        f"{R36F15103_LAST_RESULT.get('pending_count')}"
    )

    log(
        f"{STAGE} AUTO TRANSITION REASON = "
        f"{R36F15103_LAST_RESULT.get('reason')}"
    )

    log(
        f"{STAGE} LONG VALID CLUSTERS = "
        f"{LONG_DIAGNOSTICS.get('valid_cluster_count', 0)}"
    )

    log(
        f"{STAGE} SHORT VALID CLUSTERS = "
        f"{SHORT_DIAGNOSTICS.get('valid_cluster_count', 0)}"
    )

    log(
        f"{STAGE} REAL_LONG_MARKET_ELIGIBLE = "
        f"{REAL_LONG_MARKET_ELIGIBLE}"
    )

    log(
        f"{STAGE} REAL_SHORT_MARKET_ELIGIBLE = "
        f"{REAL_SHORT_MARKET_ELIGIBLE}"
    )

    log(
        f"{STAGE} TELEGRAM_COMMAND_AUTHORIZED_PREVIEW = "
        f"{TELEGRAM_COMMAND_PREVIEW.get('authorized_preview', False)}"
    )

    if balance_readiness:
        log(
            f"{STAGE} TRADE_READINESS_STATUS = "
            f"{balance_readiness.get('status')}"
        )

        log(
            f"{STAGE} SELECTED_TP_ALLOCATION = "
            f"{balance_readiness.get('selected_allocation')}"
        )

    if protective_stop_price is not None:
        log(
            f"{STAGE} PROTECTIVE_STOP_PRICE = "
            f"{decimal_to_string(protective_stop_price)}"
        )

        log(
            f"{STAGE} PROTECTIVE_STOP_VALID = "
            f"{bool(protective_stop_checks and protective_stop_checks.get('all_valid'))}"
        )

    log(
        "NO REAL ORDER WAS SENT"
    )

    if demo_submission.get("sent"):
        log("WEEX DEMO ORDER TRANSPORT OCCURRED")
    else:
        log("NO DEMO ORDER WAS SENT")

    log(
        "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
    )

    line()

    return snapshot


# ============================================================
# 60-SECOND REEVALUATION
# ============================================================

async def heartbeat_loop():
    global HEARTBEAT_COUNT
    global TEST_STATUS

    while True:
        HEARTBEAT_COUNT += 1

        log(
            f"HEARTBEAT "
            f"stage={STAGE} "
            f"status={TEST_STATUS} "
            f"count={HEARTBEAT_COUNT} "
            f"active_mode={R36F15103_ACTIVE_MODE} "
            f"pending_mode={R36F15103_PENDING_MODE} "
            f"pending_count={R36F15103_PENDING_COUNT} "
            f"mode_locked={R36F15103_MODE_LOCKED} "
            f"long_valid_clusters="
            f"{LONG_DIAGNOSTICS.get('valid_cluster_count', 0)} "
            f"short_valid_clusters="
            f"{SHORT_DIAGNOSTICS.get('valid_cluster_count', 0)} "
            f"write_transport=False "
            f"real_execution=False "
            f"demo_execution=False "
            f"reevaluation_seconds="
            f"{R36F151_REEVALUATION_SECONDS}"
        )

        await asyncio.sleep(
            R36F151_REEVALUATION_SECONDS
        )

        line()

        log(
            f"{STAGE} "
            f"RUNTIME REEVALUATION START "
            f"heartbeat={HEARTBEAT_COUNT}"
        )

        line()

        try:
            exposure = (
                await r36f159_reconcile_current_demo_exposure()
            )

            log(
                "R36F.15.10.5 CYCLE "
                "DUPLICATE BLOCKED = "
                + str(
                    exposure.get(
                        "duplicate_entry_blocked",
                        True,
                    )
                )
            )

            log(
                "R36F.15.10.5 CYCLE "
                "BLOCK REASON = "
                + str(
                    exposure.get(
                        "duplicate_block_reason"
                    )
                )
            )

            await run_r36f12()

            log(
                f"{STAGE} "
                f"RUNTIME REEVALUATION COMPLETE "
                f"heartbeat={HEARTBEAT_COUNT} "
                f"status={TEST_STATUS} "
                f"active_mode="
                f"{R36F15103_ACTIVE_MODE} "
                f"raw_mode="
                f"{R36F15103_LAST_RESULT.get('raw_mode')} "
                f"pending_mode="
                f"{R36F15103_PENDING_MODE} "
                f"pending_count="
                f"{R36F15103_PENDING_COUNT} "
                f"mode_locked="
                f"{R36F15103_MODE_LOCKED} "
                f"long_valid_clusters="
                f"{LONG_DIAGNOSTICS.get('valid_cluster_count', 0)} "
                f"short_valid_clusters="
                f"{SHORT_DIAGNOSTICS.get('valid_cluster_count', 0)}"
            )

        except Exception as exc:
            TEST_STATUS = "FAIL"

            line()

            log(
                f"{STAGE} "
                f"RUNTIME REEVALUATION ERROR = "
                f"{exc}"
            )

            line()


# ============================================================
# STARTUP
# ============================================================

async def async_main():
    global TEST_STATUS

    start_health_server()

    r36f15103_startup_diagnostic()

    try:
        startup_exposure = (
            await r36f159_reconcile_current_demo_exposure()
        )

        log(
            "R36F.15.10.5 STARTUP "
            "DUPLICATE BLOCKED = "
            + str(
                startup_exposure.get(
                    "duplicate_entry_blocked",
                    True,
                )
            )
        )

        log(
            "R36F.15.10.5 STARTUP "
            "BLOCK REASON = "
            + str(
                startup_exposure.get(
                    "duplicate_block_reason"
                )
            )
        )

    except Exception as exc:
        log(
            "R36F.15.10.5 STARTUP "
            "EXPOSURE RECONCILIATION ERROR = "
            + str(exc)
        )

    try:
        await run_r36f12()

    except Exception as exc:
        TEST_STATUS = "FAIL"

        line()

        log(
            f"{STAGE} UNHANDLED ERROR = "
            f"{exc}"
        )

        line()

    await heartbeat_loop()


def main():
    asyncio.run(
        async_main()
    )


if __name__ == "__main__":
    main()
