```python
#!/usr/bin/env python3
"""
R36F.12 - FROZEN EMA19/50/200 + TELEGRAM COMMAND INTEGRATION CHECKPOINT

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5.4/R36F.8 safety baseline
    while correcting ONLY the remaining pre-live readiness classification:

        A market may have a valid historical TP set but still be unable to
        represent the frozen 20% / 20% / 60% TP quantity split because the
        planned entry quantity is below the strict exchange-representable
        minimum. That condition is normal TRADE INELIGIBILITY, not a writer
        capability failure and not a FINAL_BLOCKER.

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

    This version DOES NOT send WEEX POST requests. Optional Telegram sendMessage is isolated from exchange execution.

    The writer output is a construction preview only.

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


# ============================================================
# STAGE
# ============================================================

STAGE = "R36F.14"

PURPOSE = (
    "WEEX DEMO-TRADING INTEGRATION CHECKPOINT: preserve the complete R36F.13.2 "
    "EMA19/EMA50/EMA200 + Telegram + two-cluster TP + quantity/readiness + mandatory "
    "protective-stop + stop-risk-envelope + stop-loss-budget chain, add authenticated "
    "read-only WEEX V3 demo-account reconciliation and construct/validate the documented "
    "WEEX demo order payload for BTCSUSDT/SUSDT, while keeping BOTH demo order submission "
    "and real order submission hard-disabled. R36F.14 performs zero POST requests; "
    "R36F.15 is reserved for the first controlled actual WEEX demo order."
)


# ============================================================
# WEEX CONFIGURATION
# ============================================================

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = "BTCUSDT"
PUBLIC_TICKER_SYMBOL = "cmt_btcusdt"

KLINE_INTERVAL = "1m"
HISTORICAL_LIMIT = 250
MAX_HISTORICAL_PAGES = 4

PRICE_STEP = Decimal("0.1")
QUANTITY_STEP = Decimal("0.0001")
MIN_QUANTITY = Decimal("0.0001")


# ============================================================
# TRADE CONFIGURATION
# ============================================================

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


# ============================================================
# R36F.12 FROZEN EMA / TELEGRAM SIGNAL CONFIGURATION
# ============================================================

EMA_FAST = 19
EMA_MID = 50
EMA_SLOW = 200
EMA_CONFIRMATION_CANDLES = 1
MIN_EMA_19_50_SEPARATION_PERCENT = Decimal("0.01")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Outbound Telegram alerts are isolated from exchange execution. Default false
# so deployment cannot unexpectedly send alerts before R36F.12 logs are checked.
R36F12_TELEGRAM_ALERTS_ENABLED = (
    os.getenv("R36F12_TELEGRAM_ALERTS_ENABLED", "false").strip().lower()
    in {"1", "true", "yes", "on"}
)

TELEGRAM_BUY_COMMAND = "BUY BTC NOW"
TELEGRAM_SELL_COMMAND = "SELL BTC NOW"


# ============================================================
# TP CONFIGURATION
# ============================================================

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


# ============================================================
# ABSOLUTE EXECUTION FIREBREAK
# ============================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False

ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False


# ============================================================
# R36F.12 PRE-LIVE CANARY SAFETY CONFIGURATION
# ============================================================

# R36F.12 remains exchange-zero-write. These values validate the complete
# first-live candidate but do not enable exchange mutation transport.
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


# ============================================================
# R36F.13 PROTECTIVE STOP CONFIGURATION
# ============================================================

# R36F.13 preview-only adjustable stop calculation. This validates the
# protective-stop mechanism without enabling exchange writes. The value may be
# changed through Render later without changing code; live activation remains
# forbidden in this stage.
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


# ============================================================
# R36F.13.1 STOP-DISTANCE RISK ENVELOPE
# ============================================================

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


# ============================================================
# R36F.13.2 PROTECTIVE-STOP LOSS BUDGET
# ============================================================

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


# ============================================================
# R36F.14 WEEX DEMO INTEGRATION CONFIGURATION
# ============================================================

# Documented WEEX V3 paper-trading surface. Demo BTC is BTCSUSDT and
# simulated collateral is SUSDT. R36F.14 is read-only toward these endpoints
# and only constructs the POST payload in memory.
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


# ============================================================
# STATE DIRECTORIES
# ============================================================

R36A_STATE_DIR = "/var/data/r36a_state"
R36C_STATE_DIR = "/var/data/r36c_state"
R36D_STATE_DIR = "/var/data/r36d_state"
R36F_STATE_DIR = "/var/data/r36f_state"

os.makedirs(
    R36F_STATE_DIR,
    exist_ok=True,
)


# ============================================================
# DURABLE FILES
# ============================================================

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


# ============================================================
# DURABLE IDS
# ============================================================

OLD_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"

R36C_UPDATE_ID = "R36C_SYNTHETIC_UPDATE_000001"


# ============================================================
# GLOBAL STATE
# ============================================================

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


# ============================================================
# BASIC UTILITIES
# ============================================================

def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def line():
    print(
        "----------------------------------------------------------------------------------------------------",
        flush=True,
    )


def log(
    message,
):
    print(
        f"{now_iso()} {message}",
        flush=True,
    )


# ============================================================
# FINAL CHECK
# ============================================================

def check(
    name,
    condition,
    detail=None,
):

    if condition:

        log(
            f"PASS: {name}"
        )

        if detail:
            log(
                f"      {detail}"
            )

        return True

    log(
        f"FAIL: {name}"
    )

    if detail:
        log(
            f"      {detail}"
        )

    FINAL_BLOCKERS.append(
        name
    )

    return False


# ============================================================
# FROZEN DIAGNOSTIC CHECK
# ============================================================

def diagnostic_check(
    name,
    condition,
    detail=None,
):

    if condition:

        log(
            f"DIAGNOSTIC PASS: {name}"
        )

        if detail:
            log(
                f"      {detail}"
            )

        return True

    log(
        f"DIAGNOSTIC FAIL: {name}"
    )

    if detail:
        log(
            f"      {detail}"
        )

    return False


# ============================================================
# DECIMAL UTILITIES
# ============================================================

def D(
    value,
):
    return Decimal(
        str(value)
    )


def quantize_down(
    value,
    step,
):

    value = D(
        value
    )

    step = D(
        step
    )

    if step <= 0:
        raise ValueError(
            "Invalid quantization step"
        )

    units = (
        value
        / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_to_string(
    value,
):

    if value is None:
        return None

    value = D(
        value
    )

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = (
            text
            .rstrip(
                "0"
            )
            .rstrip(
                "."
            )
        )

    return text


# ============================================================
# JSON UTILITIES
# ============================================================

def canonical_json(
    data,
):

    return json.dumps(
        data,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )


def sha256_text(
    text,
):

    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()


def read_json_file(
    path,
    default=None,
):

    if default is None:
        default = {}

    try:

        if not os.path.exists(
            path
        ):
            return default

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(
                f
            )

    except Exception as exc:

        log(
            f"READ JSON FAILED path={path} error={exc}"
        )

        return default


def write_json_file(
    path,
    data,
):

    tmp = (
        path
        + ".tmp"
    )

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


# ============================================================
# DURABLE ID COLLECTION
# ============================================================

def collect_ids_from_file(
    path,
):

    ids = set()

    data = read_json_file(
        path,
        default=None,
    )

    if data is None:
        return ids

    def walk(
        value,
    ):

        if isinstance(
            value,
            dict,
        ):

            for (
                key,
                item,
            ) in value.items():

                if (
                    isinstance(
                        key,
                        str,
                    )
                    and
                    "id"
                    in key.lower()
                    and
                    isinstance(
                        item,
                        str,
                    )
                ):

                    ids.add(
                        item
                    )

                walk(
                    item
                )

        elif isinstance(
            value,
            list,
        ):

            for item in value:

                walk(
                    item
                )

    walk(
        data
    )

    return ids


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ):

        body = (
            f"stage={STAGE}\n"
            f"status={TEST_STATUS}\n"
        ).encode()

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/plain",
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    body
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

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


# WEEX SIGNING
# ============================================================

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


# ============================================================
# READ-ONLY WEEX REQUEST
# ============================================================

async def weex_get(
    path,
    params=None,
    authenticated=False,
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
            int(
                time.time() * 1000
            )
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


# ============================================================
# MARK PRICE
# ============================================================

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

    if isinstance(
        data,
        dict,
    ):

        for key in (
            "price",
            "markPrice",
            "lastPrice",
        ):

            if key in data:
                candidates.append(
                    data[key]
                )

        nested = data.get(
            "data"
        )

        if isinstance(
            nested,
            dict,
        ):

            for key in (
                "price",
                "markPrice",
                "lastPrice",
            ):

                if key in nested:
                    candidates.append(
                        nested[key]
                    )

    elif isinstance(
        data,
        list,
    ):

        for item in data:

            if isinstance(
                item,
                dict,
            ):

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

            MARK_PRICE = D(
                candidate
            )

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


# ============================================================
# BALANCE
# ============================================================

async def load_available_balance():

    global AVAILABLE_BALANCE

    data = await weex_get(
        "/capi/v3/account/balance",
        authenticated=True,
    )

    candidates = []

    def collect(
        value,
    ):

        if isinstance(
            value,
            dict,
        ):

            for key, item in value.items():

                key_lower = key.lower()

                if key_lower in (
                    "availablebalance",
                    "available_balance",
                    "available",
                    "free",
                    "usdtavailable",
                ):

                    candidates.append(
                        item
                    )

                collect(item)

        elif isinstance(
            value,
            list,
        ):

            for item in value:
                collect(item)

    collect(data)

    for candidate in candidates:

        try:

            value = D(
                candidate
            )

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


# ============================================================
# OPEN POSITIONS
# ============================================================

async def load_open_positions():

    global OPEN_POSITIONS

    data = await weex_get(
        "/capi/v3/account/position/singlePosition",
        params={
            "symbol": SYMBOL
        },
        authenticated=True,
    )

    if isinstance(
        data,
        list,
    ):

        OPEN_POSITIONS = data

    elif isinstance(
        data,
        dict,
    ):

        nested = data.get(
            "data"
        )

        if isinstance(
            nested,
            list,
        ):

            OPEN_POSITIONS = nested

        else:

            OPEN_POSITIONS = []

    else:

        OPEN_POSITIONS = []

    log(
        "OPEN POSITIONS = "
        + str(
            len(
                OPEN_POSITIONS
            )
        )
    )

    return OPEN_POSITIONS


# ============================================================
# EXCHANGE CONFIG
# ============================================================

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
        if isinstance(
            data,
            dict,
        )
        else {}
    )

    log(
        "WEEX EXCHANGE CONFIG READ COMPLETE"
    )

    return WEEX_CONFIG


# ============================================================
# WEEX READ-ONLY RECONCILIATION
# ============================================================

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


# ============================================================
# HISTORICAL KLINES
# ============================================================

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

            params[
                "endTime"
            ] = int(
                time.time() * 1000
            ) - (
                page
                * HISTORICAL_LIMIT
                * 60
                * 1000
            )

        data = await weex_get(
            "/capi/v3/market/klines",
            params=params,
            authenticated=False,
        )

        rows = data

        if isinstance(
            data,
            dict,
        ):

            rows = data.get(
                "data",
                data.get(
                    "result",
                    [],
                ),
            )

        if not isinstance(
            rows,
            list,
        ):

            raise RuntimeError(
                "Unexpected kline response"
            )

        all_rows.extend(
            rows
        )

        if len(rows) < HISTORICAL_LIMIT:
            break

    return all_rows


# ============================================================
# KLINE VALUE HELPERS
# ============================================================

def candle_high(
    row,
):

    if isinstance(
        row,
        dict,
    ):

        for key in (
            "high",
            "highPrice",
        ):

            if key in row:
                return D(
                    row[key]
                )

    if isinstance(
        row,
        list,
    ) and len(row) >= 3:

        return D(
            row[2]
        )

    raise ValueError(
        "Unable to read candle high"
    )


def candle_low(
    row,
):

    if isinstance(
        row,
        dict,
    ):

        for key in (
            "low",
            "lowPrice",
        ):

            if key in row:
                return D(
                    row[key]
                )

    if isinstance(
        row,
        list,
    ) and len(row) >= 4:

        return D(
            row[3]
        )

    raise ValueError(
        "Unable to read candle low"
    )


def historical_highs(
    rows,
):

    return [
        candle_high(row)
        for row in rows
    ]


def historical_lows(
    rows,
):

    return [
        candle_low(row)
        for row in rows
    ]


# ============================================================
# R36F.12 FROZEN EMA19 / EMA50 / EMA200 SIGNAL ENGINE
# ============================================================

def candle_close(row):
    if isinstance(row, dict):
        for key in ("close", "closePrice", "c", "lastPrice"):
            if key in row:
                return D(row[key])

    if isinstance(row, list) and len(row) >= 5:
        return D(row[4])

    raise ValueError("Unable to read candle close")


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

                try:
                    return int(
                        float(
                            row[key]
                        )
                    )

                except Exception:
                    return None

    if isinstance(row, list) and row:

        try:
            return int(
                float(
                    row[0]
                )
            )

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
        and
        all(
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
            for ts in sorted(
                by_ts
            )
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
        / Decimal(
            period + 1
        )
    )

    ema = (
        sum(
            values[:period]
        )
        / Decimal(
            period
        )
    )

    for price in values[
        period:
    ]:

        ema = (
            (
                price
                - ema
            )
            * multiplier
            + ema
        )

    return ema


def calculate_emas(
    closes,
):

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


def ema_direction(
    structure,
):

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
        and
        current19
        > current50
    ):

        return "LONG"

    if (
        previous19
        >= previous50
        and
        current19
        < current50
    ):

        return "SHORT"

    return None


def build_ema_signal_snapshot(
    rows,
):

    ordered = chronological_rows(
        rows
    )

    closes = [
        candle_close(
            row
        )
        for row in ordered
    ]

    if len(
        closes
    ) < (
        EMA_SLOW
        + EMA_CONFIRMATION_CANDLES
    ):

        return {
            "ready":
                False,

            "reason":
                "INSUFFICIENT_CANDLES_FOR_EMA200_CONFIRMATION",

            "rows":
                len(
                    closes
                ),
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

    current_price = closes[
        -1
    ]

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
        >=
        MIN_EMA_19_50_SEPARATION_PERCENT
    )

    ideal_direction = (
        direction
        if quality_ok
        else None
    )

    return {

        "ready":
            True,

        "reason":
            "EMA_ENGINE_READY",

        "rows":
            len(
                closes
            ),

        "price":
            decimal_to_string(
                current_price
            ),

        "ema19":
            decimal_to_string(
                current19
            ),

        "ema50":
            decimal_to_string(
                current50
            ),

        "ema200":
            decimal_to_string(
                current200
            ),

        "structure":
            structure,

        "direction":
            direction,

        "ideal_direction":
            ideal_direction,

        "ema19_50_separation_percent":
            decimal_to_string(
                separation
            ),

        "minimum_separation_percent":
            decimal_to_string(
                MIN_EMA_19_50_SEPARATION_PERCENT
            ),

        "quality_ok":
            quality_ok,

        "fresh_crossover":
            crossover,

        "confirmation_policy":
            "NEXT_CLOSED_1M_CANDLE",

        "signal_expiry_seconds":
            SIGNAL_EXPIRY_SECONDS,
    }


def normalize_telegram_command(
    text,
):

    return " ".join(
        str(
            text or ""
        )
        .strip()
        .upper()
        .split()
    )


def parse_telegram_trade_command(
    text,
):

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
            "recognized":
                True,

            "command":
                normalized,

            "direction":
                "LONG",
        }

    if (
        normalized
        == TELEGRAM_SELL_COMMAND
    ):

        return {
            "recognized":
                True,

            "command":
                normalized,

            "direction":
                "SHORT",
        }

    return {
        "recognized":
            False,

        "command":
            normalized,

        "direction":
            None,
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

            "authorized_preview":
                False,

            "reason":
                "UNRECOGNIZED_COMMAND",
        }

    if not ema_snapshot.get(
        "ready"
    ):

        return {
            **parsed,

            "authorized_preview":
                False,

            "reason":
                "EMA_ENGINE_NOT_READY",
        }

    ideal = ema_snapshot.get(
        "ideal_direction"
    )

    if ideal != direction:

        return {
            **parsed,

            "authorized_preview":
                False,

            "reason":
                "COMMAND_DIRECTION_DOES_NOT_MATCH_IDEAL_EMA_CONDITION",

            "ema_ideal_direction":
                ideal,
        }

    market_ok = (
        long_eligible
        if direction == "LONG"
        else short_eligible
    )

    if not market_ok:

        return {
            **parsed,

            "authorized_preview":
                False,

            "reason":
                "COMMAND_DIRECTION_TP_MARKET_NOT_ELIGIBLE",

            "ema_ideal_direction":
                ideal,
        }

    return {
        **parsed,

        "authorized_preview":
            True,

        "reason":
            "COMMAND_AND_EMA_AND_TP_DIRECTION_AGREE",

        "ema_ideal_direction":
            ideal,

        "exchange_order_sent":
            False,
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
            "attempted":
                False,

            "sent":
                False,

            "reason":
                "NO_IDEAL_ALERT",
        }

    if not R36F12_TELEGRAM_ALERTS_ENABLED:

        return {
            "attempted":
                False,

            "sent":
                False,

            "reason":
                "ALERTS_DISABLED_BY_DEFAULT",
        }

    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):

        return {
            "attempted":
                False,

            "sent":
                False,

            "reason":
                "TELEGRAM_CONFIG_MISSING",
        }

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {

        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            message,

        "disable_web_page_preview":
            True,
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

                body = (
                    await response.text()
                )

                return {

                    "attempted":
                        True,

                    "sent":
                        (
                            200
                            <= response.status
                            < 300
                        ),

                    "http_status":
                        response.status,

                    "response_preview":
                        body[:200],
                }

    except Exception as exc:

        return {
            "attempted":
                True,

            "sent":
                False,

            "reason":
                f"{type(exc).__name__}: {exc}",
        }


def synthetic_r36f12_ema_telegram_tests():

    bullish = {

        "ready":
            True,

        "ideal_direction":
            "LONG",

        "structure":
            "STRONG_BULLISH",

        "price":
            "80000",

        "ema19":
            "80100",

        "ema50":
            "80000",

        "ema200":
            "79000",

        "ema19_50_separation_percent":
            "0.125",
    }

    bearish = {

        "ready":
            True,

        "ideal_direction":
            "SHORT",

        "structure":
            "STRONG_BEARISH",

        "price":
            "80000",

        "ema19":
            "79900",

        "ema50":
            "80000",

        "ema200":
            "81000",

        "ema19_50_separation_percent":
            "0.125",
    }

    buy = (
        parse_telegram_trade_command(
            "  buy   btc now "
        )
    )

    sell = (
        parse_telegram_trade_command(
            "SELL BTC NOW"
        )
    )

    check(
        "R36F12_TELEGRAM_BUY_COMMAND_PARSES_LONG",
        (
            buy[
                "recognized"
            ]
            and
            buy[
                "direction"
            ] == "LONG"
        ),
    )

    check(
        "R36F12_TELEGRAM_SELL_COMMAND_PARSES_SHORT",
        (
            sell[
                "recognized"
            ]
            and
            sell[
                "direction"
            ] == "SHORT"
        ),
    )

    check(
        "R36F12_TELEGRAM_UNKNOWN_COMMAND_REJECTED",
        (
            parse_telegram_trade_command(
                "BUY ETH NOW"
            )[
                "recognized"
            ]
            is False
        ),
    )

    buy_ok = (
        validate_telegram_command_against_signal(
            "BUY BTC NOW",
            bullish,
            True,
            False,
        )
    )

    sell_ok = (
        validate_telegram_command_against_signal(
            "SELL BTC NOW",
            bearish,
            False,
            True,
        )
    )

    mismatch = (
        validate_telegram_command_against_signal(
            "SELL BTC NOW",
            bullish,
            True,
            True,
        )
    )

    check(
        "R36F12_BUY_MATCHING_IDEAL_LONG_PREVIEW_APPROVED",
        (
            buy_ok[
                "authorized_preview"
            ]
            is True
        ),
    )

    check(
        "R36F12_SELL_MATCHING_IDEAL_SHORT_PREVIEW_APPROVED",
        (
            sell_ok[
                "authorized_preview"
            ]
            is True
        ),
    )

    check(
        "R36F12_DIRECTION_MISMATCH_BLOCKED",
        (
            mismatch[
                "authorized_preview"
            ]
            is False
        ),
    )

    check(
        "R36F12_COMMAND_PREVIEW_NEVER_SENDS_ORDER",
        (
            buy_ok.get(
                "exchange_order_sent"
            )
            is False
        ),
    )

    return True


# ============================================================
# LOCAL EXTREMA
# ============================================================

def build_extrema(
    values,
):

    if len(
        values
    ) < 3:

        return []

    extrema = []

    for index in range(
        1,
        len(values) - 1,
    ):

        previous_value = D(
            values[
                index - 1
            ]
        )

        current_value = D(
            values[
                index
            ]
        )

        next_value = D(
            values[
                index + 1
            ]
        )

        if (
            current_value
            >= previous_value
            and
            current_value
            >= next_value
        ):

            extrema.append(
                current_value
            )

        elif (
            current_value
            <= previous_value
            and
            current_value
            <= next_value
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
        [
            D(
                value
            )
            for value in extrema
        ]
    )

    clusters = []

    current = [
        sorted_values[0]
    ]

    for value in sorted_values[
        1:
    ]:

        current_average = (
            sum(
                current
            )
            / Decimal(
                len(
                    current
                )
            )
        )

        tolerance = (
            current_average
            * CLUSTER_TOLERANCE_PERCENT
            / Decimal("100")
        )

        if abs(
            value
            - current_average
        ) <= tolerance:

            current.append(
                value
            )

        else:

            clusters.append(
                {

                    "minimum":
                        min(
                            current
                        ),

                    "maximum":
                        max(
                            current
                        ),

                    "average":
                        (
                            sum(
                                current
                            )
                            / Decimal(
                                len(
                                    current
                                )
                            )
                        ),

                    "touches":
                        len(
                            current
                        ),
                }
            )

            current = [
                value
            ]

    clusters.append(
        {

            "minimum":
                min(
                    current
                ),

            "maximum":
                max(
                    current
                ),

            "average":
                (
                    sum(
                        current
                    )
                    / Decimal(
                        len(
                            current
                        )
                    )
                ),

            "touches":
                len(
                    current
                ),
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

        result[
            "valid"
        ] = not reasons

        result[
            "reasons"
        ] = reasons

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
                item[
                    "average"
                ]
        )

    elif side == "SHORT":

        valid.sort(
            key=lambda item:
                item[
                    "average"
                ],
            reverse=True,
        )

    return (
        valid,
        invalid,
    )


# ============================================================
# CLUSTER DIAGNOSTICS
# ============================================================

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

    (
        valid,
        invalid,
    ) = validate_clusters(
        clusters,
        entry_price,
        side,
    )

    diagnostics = {

        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "historical_row_count":
            len(
                rows
            ),

        "extrema_count":
            len(
                extrema
            ),

        "cluster_count":
            len(
                clusters
            ),

        "valid_cluster_count":
            len(
                valid
            ),

        "invalid_cluster_count":
            len(
                invalid
            ),

        "required_valid_clusters":
            REQUIRED_TP_CLUSTERS,

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,
    }

    if (
        len(
            valid
        )
        >= REQUIRED_TP_CLUSTERS
    ):

        diagnostics[
            "failure_reason"
        ] = None

    elif len(
        valid
    ) == 1:

        diagnostics[
            "failure_reason"
        ] = "ONLY_ONE_VALID_CLUSTER"

    elif len(
        extrema
    ) == 0:

        diagnostics[
            "failure_reason"
        ] = "NO_LOCAL_EXTREMA"

    elif len(
        clusters
    ) == 0:

        diagnostics[
            "failure_reason"
        ] = "NO_HISTORICAL_CLUSTERS"

    else:

        diagnostics[
            "failure_reason"
        ] = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
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

    for (
        index,
        cluster,
    ) in enumerate(
        clusters,
        start=1,
    ):

        log(
            f"{side} CLUSTER {index}: "
            f"average="
            f"{decimal_to_string(cluster['average'])} "
            f"minimum="
            f"{decimal_to_string(cluster['minimum'])} "
            f"maximum="
            f"{decimal_to_string(cluster['maximum'])} "
            f"touches="
            f"{cluster['touches']}"
        )

    for (
        index,
        cluster,
    ) in enumerate(
        invalid,
        start=1,
    ):

        log(
            f"{side} INVALID CLUSTER {index}: "
            f"average="
            f"{decimal_to_string(cluster['average'])} "
            f"reasons="
            f"{','.join(cluster['reasons'])}"
        )

    if diagnostics[
        "failure_reason"
    ]:

        log(
            f"{side} CLUSTER DIAGNOSTIC "
            f"FAILURE_REASON = "
            f"{diagnostics['failure_reason']}"
        )

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
            cluster[
                "touches"
            ]
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
                c[
                    "average"
                ]
        )

    else:

        valid.sort(
            key=lambda c:
                c[
                    "average"
                ],
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

    if len(
        valid_cluster_list
    ) < REQUIRED_TP_CLUSTERS:

        raise RuntimeError(
            "Cannot calculate complete TP set: "
            "fewer than two valid historical clusters"
        )

    cluster1 = D(
        valid_cluster_list[
            0
        ][
            "average"
        ]
    )

    cluster2 = D(
        valid_cluster_list[
            1
        ][
            "average"
        ]
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

    (
        valid,
        invalid,
    ) = validate_clusters(
        clusters,
        entry_price,
        direction,
    )

    approval = evaluate_tp_approval(
        {

            "valid_cluster_count":
                len(
                    valid
                ),

            "failure_reason":
                (
                    "ONLY_ONE_VALID_CLUSTER"
                    if len(valid) == 1
                    else
                    "INSUFFICIENT_VALID_CLUSTERS"
                ),
        }
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

    LAST_TP_APPROVAL = approval

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

    if len(
        clusters
    ) < REQUIRED_TP_CLUSTERS:

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
                prices[
                    "tp1"
                ]
            ),

        "tp2":
            decimal_to_string(
                prices[
                    "tp2"
                ]
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

        [
            1,
            "99000",
            "100000",
            "99500",
            "99500",
            "1",
        ],

        [
            2,
            "99500",
            "100100",
            "99600",
            "99800",
            "1",
        ],

        [
            3,
            "99600",
            "100000",
            "99500",
            "99700",
            "1",
        ],

        [
            4,
            "99500",
            "101000",
            "99900",
            "100100",
            "1",
        ],

        [
            5,
            "99900",
            "100200",
            "99500",
            "100000",
            "1",
        ],

        [
            6,
            "99500",
            "101500",
            "100000",
            "100500",
            "1",
        ],

        [
            7,
            "100000",
            "101000",
            "99500",
            "100500",
            "1",
        ],

        [
            8,
            "99500",
            "101400",
            "99900",
            "100800",
            "1",
        ],
    ]

    short_rows = [

        [
            1,
            "81000",
            "81500",
            "80000",
            "81000",
            "1",
        ],

        [
            2,
            "81000",
            "81500",
            "80100",
            "80800",
            "1",
        ],

        [
            3,
            "80800",
            "81400",
            "80050",
            "80500",
            "1",
        ],

        [
            4,
            "80500",
            "81300",
            "79900",
            "80300",
            "1",
        ],

        [
            5,
            "80300",
            "81200",
            "80000",
            "80500",
            "1",
        ],

        [
            6,
            "80500",
            "81400",
            "79800",
            "80400",
            "1",
        ],

        [
            7,
            "80400",
            "81300",
            "80100",
            "80600",
            "1",
        ],

        [
            8,
            "80600",
            "81500",
            "79950",
            "80800",
            "1",
        ],
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


# ============================================================
# ONE-CLUSTER TP REJECTION
# ============================================================

def synthetic_tp_rejection_test():

    rows = [

        [
            1,
            "99000",
            "100000",
            "99500",
            "99500",
            "1",
        ],

        [
            2,
            "99500",
            "100100",
            "99600",
            "99800",
            "1",
        ],

        [
            3,
            "99600",
            "100000",
            "99500",
            "99700",
            "1",
        ],

        [
            4,
            "99500",
            "100100",
            "99800",
            "99900",
            "1",
        ],
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
# R36F.10 WRITER HELPERS
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
        entry_quantity,
        QUANTITY_STEP,
    )

    percentages = (
        D(tp1_percent),
        D(tp2_percent),
        D(tp3_percent),
    )

    if sum(
        percentages
    ) != Decimal("100"):

        return False

    quantities = [

        entry_quantity
        * percent
        / Decimal("100")

        for percent
        in percentages
    ]

    return bool(

        entry_quantity
        >= MIN_QUANTITY

        and

        all(
            q >= MIN_QUANTITY
            for q in quantities
        )

        and

        all(
            quantize_down(
                q,
                QUANTITY_STEP,
            ) == q
            for q in quantities
        )

        and

        sum(
            quantities
        ) == entry_quantity
    )


def select_tp_allocation(
    entry_quantity,
):
    """
    Prefer 20/20/60; fall back only to the approved 25/25/50 allocation.
    """

    entry_quantity = quantize_down(
        entry_quantity,
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
    """
    Allocate TP quantities using preferred 20/20/60
    or approved 25/25/50 fallback.
    """

    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP,
    )

    allocation = (
        select_tp_allocation(
            entry_quantity
        )
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


# ============================================================
# WRITER QUANTITY VALIDATION
# ============================================================

def validate_writer_quantities(
    entry_quantity,
    tp1,
    tp2,
    tp3,
):

    allocation = (
        select_tp_allocation(
            entry_quantity
        )
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
            ) == entry_quantity,

        "tp1_selected_percent_exact":
            tp1
            == exact_tp1,

        "tp2_selected_percent_exact":
            tp2
            == exact_tp2,

        "tp3_selected_percent_exact":
            tp3
            == exact_tp3,

        "tp3_non_negative":
            tp3
            >= Decimal("0"),
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


def minimum_adjustable_tp_entry_quantity():
    """
    Return first exchange-step quantity supported
    by an approved allocation.
    """

    candidate = QUANTITY_STEP

    for _ in range(
        100000
    ):

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
        "Unable to find adjustable TP minimum entry quantity"
    )


def minimum_strict_tp_entry_quantity():
    """
    Compatibility alias: R36F.10 minimum under the
    approved adjustable allocation policy.
    """

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

    allocation = (
        select_tp_allocation(
            quantity
        )
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
                "POSITION_TOO_SMALL_OR_NOT_REPRESENTABLE_BY_APPROVED_TP_ALLOCATIONS"
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
                and
                allocation[
                    "adjusted"
                ]
            ),

        "selected_tp1_percent":
            (
                decimal_to_string(
                    allocation[
                        "tp1_percent"
                    ]
                )
                if allocation
                else None
            ),

        "selected_tp2_percent":
            (
                decimal_to_string(
                    allocation[
                        "tp2_percent"
                    ]
                )
                if allocation
                else None
            ),

        "selected_tp3_percent":
            (
                decimal_to_string(
                    allocation[
                        "tp3_percent"
                    ]
                )
                if allocation
                else None
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
    """
    Classify balance readiness under R36F.10
    approved adjustable TP allocation.
    """

    available_balance = D(
        available_balance
    )

    mark_price = D(
        mark_price
    )

    leverage = D(
        leverage
    )

    if available_balance < Decimal("0"):

        raise ValueError(
            "available_balance must be non-negative"
        )

    if mark_price <= Decimal("0"):

        raise ValueError(
            "mark_price must be positive"
        )

    if leverage <= Decimal("0"):

        raise ValueError(
            "leverage must be positive"
        )

    entry_fraction = (
        ENTRY_MARGIN_PERCENT
        / Decimal("100")
    )

    if entry_fraction <= Decimal("0"):

        raise ValueError(
            "ENTRY_MARGIN_PERCENT must be positive"
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

    quantity_feasibility = (
        evaluate_writer_quantity_feasibility(
            planned_entry_quantity
        )
    )

    minimum_entry_quantity = (
        minimum_adjustable_tp_entry_quantity()
    )

    required_entry_margin = (
        minimum_entry_quantity
        * mark_price
        / leverage
    )

    required_available_balance = (
        required_entry_margin
        / entry_fraction
    )

    available_balance_shortfall = max(
        Decimal("0"),
        (
            required_available_balance
            - available_balance
        ),
    )

    eligible = bool(

        quantity_feasibility[
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

        "entry_margin_percent":
            decimal_to_string(
                ENTRY_MARGIN_PERCENT
            ),

        "raw_entry_quantity":
            decimal_to_string(
                raw_entry_quantity
            ),

        "planned_entry_quantity":
            decimal_to_string(
                planned_entry_quantity
            ),

        "minimum_strict_tp_entry_quantity":
            decimal_to_string(
                minimum_entry_quantity
            ),

        "required_margin_for_minimum_qty":
            decimal_to_string(
                required_entry_margin
            ),

        "required_available_balance":
            decimal_to_string(
                required_available_balance
            ),

        "available_balance_shortfall":
            decimal_to_string(
                available_balance_shortfall
            ),

        "quantity_feasible":
            quantity_feasibility[
                "feasible"
            ],

        "quantity_feasibility_reason":
            quantity_feasibility[
                "reason"
            ],

        "requested_allocation":
            quantity_feasibility[
                "requested_allocation"
            ],

        "selected_allocation":
            quantity_feasibility[
                "selected_allocation"
            ],

        "allocation_adjusted":
            quantity_feasibility[
                "allocation_adjusted"
            ],

        "tp1_quantity":
            quantity_feasibility[
                "tp1_quantity"
            ],

        "tp2_quantity":
            quantity_feasibility[
                "tp2_quantity"
            ],

        "tp3_quantity":
            quantity_feasibility[
                "tp3_quantity"
            ],
    }


# ============================================================
# R36F.14 WEEX DEMO READ-ONLY RECONCILIATION + PAYLOAD PREVIEW
# ============================================================

async def r36f14_read_demo_account():
    """Read only documented WEEX V3 paper-trading resources."""

    balance_rows = await weex_get(
        R36F14_DEMO_BALANCE_ENDPOINT,
        authenticated=True,
    )

    position_rows = await weex_get(
        R36F14_DEMO_POSITIONS_ENDPOINT,
        authenticated=True,
    )

    history_rows = await weex_get(
        R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
        params={
            "symbol": R36F14_DEMO_SYMBOL,
            "limit": 20,
            "page": 0,
        },
        authenticated=True,
    )

    balance_rows = (
        balance_rows
        if isinstance(
            balance_rows,
            list,
        )
        else []
    )

    position_rows = (
        position_rows
        if isinstance(
            position_rows,
            list,
        )
        else []
    )

    history_rows = (
        history_rows
        if isinstance(
            history_rows,
            list,
        )
        else []
    )

    demo_asset_row = None

    for row in balance_rows:

        if (
            str(
                row.get(
                    "asset",
                    "",
                )
            ).upper()
            == R36F14_DEMO_ASSET
        ):

            demo_asset_row = row
            break

    demo_positions = [

        row
        for row
        in position_rows

        if (
            str(
                row.get(
                    "symbol",
                    "",
                )
            ).upper()
            == R36F14_DEMO_SYMBOL

            and

            D(
                row.get(
                    "size",
                    "0",
                )
            )
            != 0
        )
    ]

    return {

        "balance_endpoint":
            R36F14_DEMO_BALANCE_ENDPOINT,

        "positions_endpoint":
            R36F14_DEMO_POSITIONS_ENDPOINT,

        "history_endpoint":
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,

        "demo_symbol":
            R36F14_DEMO_SYMBOL,

        "demo_asset":
            R36F14_DEMO_ASSET,

        "asset_present":
            demo_asset_row
            is not None,

        "balance":
            (
                str(
                    demo_asset_row.get(
                        "balance"
                    )
                )
                if demo_asset_row
                else None
            ),

        "available_balance":
            (
                str(
                    demo_asset_row.get(
                        "availableBalance"
                    )
                )
                if demo_asset_row
                else None
            ),

        "open_demo_position_count":
            len(
                demo_positions
            ),

        "history_count":
            len(
                history_rows
            ),

        "all_reads_successful":
            demo_asset_row
            is not None,
    }


def build_r36f14_demo_order_preview(
    direction,
    entry_quantity,
    tp_snapshot,
    protective_stop_price,
):
    """
    Construct only the documented WEEX V3 demo Place Order payload.

    WEEX's documented demo surface exposes Place Order with optional single
    tpTriggerPrice/slTriggerPrice but does not document demo equivalents of the
    production multi-TP conditional/trailing endpoints. Therefore the frozen
    TP1/TP2/TP3 plan remains validated and preserved internally; the demo entry
    preview carries TP1 plus the mandatory protective stop. No POST is sent.
    """

    if (
        not tp_snapshot
        or
        not tp_snapshot.get(
            "tp_approval",
            {},
        ).get(
            "approved"
        )
    ):

        raise ValueError(
            "demo writer requires approved complete TP snapshot"
        )

    direction = str(
        direction
    ).upper()

    entry_quantity = quantize_down(
        D(
            entry_quantity
        ),
        QUANTITY_STEP,
    )

    stop_price = quantize_down(
        D(
            protective_stop_price
        ),
        PRICE_STEP,
    )

    tp1_price = quantize_down(
        D(
            tp_snapshot[
                "tp1"
            ]
        ),
        PRICE_STEP,
    )

    if direction == "LONG":

        side = "BUY"
        position_side = "LONG"

    elif direction == "SHORT":

        side = "SELL"
        position_side = "SHORT"

    else:

        raise ValueError(
            "unsupported demo direction"
        )

    if entry_quantity <= 0:

        raise ValueError(
            "demo entry quantity must be positive"
        )

    payload = {

        "symbol":
            R36F14_DEMO_SYMBOL,

        "side":
            side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            decimal_to_string(
                entry_quantity
            ),

        "newClientOrderId":
            writer_client_id(
                direction,
                "D14",
            ),

        "tpTriggerPrice":
            decimal_to_string(
                tp1_price
            ),

        "slTriggerPrice":
            decimal_to_string(
                stop_price
            ),

        "TpWorkingType":
            "MARK_PRICE",

        "SlWorkingType":
            "MARK_PRICE",
    }

    full_tp_plan = {

        "tp1":
            tp_snapshot.get(
                "tp1"
            ),

        "tp2":
            tp_snapshot.get(
                "tp2"
            ),

        "tp3":
            tp_snapshot.get(
                "tp3"
            ),

        "allocation_percent": {

            "tp1":
                decimal_to_string(
                    TP1_ALLOCATION_PERCENT
                ),

            "tp2":
                decimal_to_string(
                    TP2_ALLOCATION_PERCENT
                ),

            "tp3":
                decimal_to_string(
                    TP3_ALLOCATION_PERCENT
                ),
        },

        "tp3_trailing_distance_percent":
            decimal_to_string(
                TP3_TRAILING_DISTANCE_PERCENT
            ),

        "preserved_internally":
            True,

        "demo_api_multi_tp_not_assumed":
            True,
    }

    return {

        "stage":
            STAGE,

        "endpoint":
            R36F14_DEMO_ORDER_ENDPOINT,

        "method":
            "POST",

        "payload":
            payload,

        "full_tp_plan":
            full_tp_plan,

        "submitted":
            False,

        "demo_post_transport_enabled":
            R36F14_DEMO_POST_TRANSPORT_ENABLED,

        "demo_order_submission_enabled":
            R36F14_DEMO_ORDER_SUBMISSION_ENABLED,

        "first_demo_order_allowed":
            R36F14_FIRST_DEMO_ORDER_ALLOWED,

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "integrity_sha256":
            sha256_text(
                canonical_json(
                    payload
                )
            ),
    }


def validate_r36f14_demo_order_preview(
    preview,
    direction,
    entry_price,
):

    if not preview:

        return {
            "all_valid":
                False,

            "reason":
                "DEMO_PREVIEW_MISSING",
        }

    payload = preview.get(
        "payload",
        {},
    )

    direction = str(
        direction
    ).upper()

    entry_price = D(
        entry_price
    )

    required = {

        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
        "tpTriggerPrice",
        "slTriggerPrice",
        "TpWorkingType",
        "SlWorkingType",
    }

    client_id = str(
        payload.get(
            "newClientOrderId",
            "",
        )
    )

    qty = D(
        payload.get(
            "quantity",
            "0",
        )
    )

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

    direction_ok = (

        (
            direction
            == "LONG"

            and

            payload.get(
                "side"
            )
            == "BUY"

            and

            payload.get(
                "positionSide"
            )
            == "LONG"
        )

        or

        (
            direction
            == "SHORT"

            and

            payload.get(
                "side"
            )
            == "SELL"

            and

            payload.get(
                "positionSide"
            )
            == "SHORT"
        )
    )

    price_direction_ok = (

        (
            direction
            == "LONG"

            and

            tp
            > entry_price

            and

            sl
            < entry_price
        )

        or

        (
            direction
            == "SHORT"

            and

            tp
            < entry_price

            and

            sl
            > entry_price
        )
    )

    checks = {

        "documented_endpoint":
            preview.get(
                "endpoint"
            )
            == R36F14_DEMO_ORDER_ENDPOINT,

        "post_preview_only":
            (
                preview.get(
                    "method"
                )
                == "POST"

                and

                preview.get(
                    "submitted"
                )
                is False
            ),

        "required_fields_present":
            required.issubset(
                set(
                    payload.keys()
                )
            ),

        "demo_symbol_exact":
            payload.get(
                "symbol"
            )
            == R36F14_DEMO_SYMBOL,

        "market_order":
            payload.get(
                "type"
            )
            == "MARKET",

        "direction_mapping":
            direction_ok,

        "quantity_positive":
            qty
            > 0,

        "client_id_valid_length":
            (
                1
                <= len(
                    client_id
                )
                <= 36
            ),

        "tp_sl_direction_valid":
            price_direction_ok,

        "working_types_mark_price":
            (
                payload.get(
                    "TpWorkingType"
                )
                == "MARK_PRICE"

                and

                payload.get(
                    "SlWorkingType"
                )
                == "MARK_PRICE"
            ),

        "demo_transport_disabled":
            R36F14_DEMO_POST_TRANSPORT_ENABLED
            is False,

        "demo_submission_disabled":
            R36F14_DEMO_ORDER_SUBMISSION_ENABLED
            is False,

        "first_demo_order_disabled":
            R36F14_FIRST_DEMO_ORDER_ALLOWED
            is False,

        "real_execution_disabled":
            REAL_ORDER_EXECUTION
            is False,
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return {

        "checks":
            checks,

        "all_valid":
            checks[
                "all_valid"
            ],
    }


def synthetic_r36f14_demo_integration_tests():

    synthetic_tp = {

        "tp_approval": {
            "approved":
                True
        },

        "tp1":
            "80400.0",

        "tp2":
            "80800.0",

        "tp3":
            "TRAILING_RUNNER",
    }

    preview = (
        build_r36f14_demo_order_preview(
            "LONG",
            Decimal(
                "0.0004"
            ),
            synthetic_tp,
            Decimal(
                "79600.0"
            ),
        )
    )

    validation = (
        validate_r36f14_demo_order_preview(
            preview,
            "LONG",
            Decimal(
                "80000.0"
            ),
        )
    )

    for (
        name,
        result,
    ) in validation[
        "checks"
    ].items():

        if name == "all_valid":
            continue

        check(
            "R36F14_SYNTHETIC_DEMO_"
            + name.upper(),
            result,
        )

    check(
        "R36F14_SYNTHETIC_DEMO_INTEGRATION_VALID",
        validation[
            "all_valid"
        ],
    )

    check(
        "R36F14_SYNTHETIC_DEMO_POST_NOT_SENT",
        preview[
            "submitted"
        ] is False,
    )

    return {

        "preview":
            preview,

        "validation":
            validation,
    }


# ============================================================
# WRITER REQUEST PREVIEW
# ============================================================

def build_writer_request_preview(
    direction,
    entry_price,
    quantity,
    tp_snapshot,
):

    if (
        not tp_snapshot

        or

        not tp_snapshot.get(
            "tp_approval",
            {},
        ).get(
            "approved"
        )
    ):

        raise ValueError(
            "writer requires an approved complete TP snapshot"
        )

    entry_price = quantize_down(
        entry_price,
        PRICE_STEP,
    )

    (
        entry_quantity,
        tp1_qty,
        tp2_qty,
        tp3_qty,
    ) = writer_quantities(
        quantity
    )

    quantity_checks = (
        validate_writer_quantities(
            entry_quantity,
            tp1_qty,
            tp2_qty,
            tp3_qty,
        )
    )

    (
        entry_side,
        position_side,
    ) = writer_entry_side(
        direction
    )

    (
        close_side,
        close_position_side,
    ) = writer_close_side(
        direction
    )

    tp1_price = quantize_down(
        D(
            tp_snapshot[
                "tp1"
            ]
        ),
        PRICE_STEP,
    )

    tp2_price = quantize_down(
        D(
            tp_snapshot[
                "tp2"
            ]
        ),
        PRICE_STEP,
    )

    if direction == "LONG":

        if not (
            tp1_price
            > entry_price

            and

            tp2_price
            > tp1_price
        ):

            raise ValueError(
                "LONG TP ordering invalid"
            )

    elif direction == "SHORT":

        if not (
            tp1_price
            < entry_price

            and

            tp2_price
            < tp1_price
        ):

            raise ValueError(
                "SHORT TP ordering invalid"
            )

    else:

        raise ValueError(
            "Invalid writer direction"
        )

    entry_leg = {

        "endpoint":
            WRITER_ENDPOINT_ENTRY,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            entry_side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            decimal_to_string(
                entry_quantity
            ),

        "newClientOrderId":
            writer_client_id(
                direction,
                "ENTRY",
            ),

        "reduceOnly":
            False,
    }

    tp1_leg = {

        "endpoint":
            WRITER_ENDPOINT_TPSL,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "positionSide":
            close_position_side,

        "planType":
            "TAKE_PROFIT",

        "triggerPrice":
            decimal_to_string(
                tp1_price
            ),

        "executePrice":
            decimal_to_string(
                tp1_price
            ),

        "quantity":
            decimal_to_string(
                tp1_qty
            ),

        "triggerPriceType":
            "MARK_PRICE",

        "clientAlgoId":
            writer_client_id(
                direction,
                "TP1",
            ),

        "reduceOnly":
            True,
    }

    tp2_leg = {

        "endpoint":
            WRITER_ENDPOINT_TPSL,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "positionSide":
            close_position_side,

        "planType":
            "TAKE_PROFIT",

        "triggerPrice":
            decimal_to_string(
                tp2_price
            ),

        "executePrice":
            decimal_to_string(
                tp2_price
            ),

        "quantity":
            decimal_to_string(
                tp2_qty
            ),

        "triggerPriceType":
            "MARK_PRICE",

        "clientAlgoId":
            writer_client_id(
                direction,
                "TP2",
            ),

        "reduceOnly":
            True,
    }

    tp3_leg = {

        "endpoint":
            WRITER_ENDPOINT_TRAILING,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            close_side,

        "positionSide":
            close_position_side,

        "type":
            "TRAILING_MARKET",

        "quantity":
            decimal_to_string(
                tp3_qty
            ),

        "callbackRate":
            decimal_to_string(
                TP3_TRAILING_DISTANCE_PERCENT
            ),

        "workingType":
            "MARK_PRICE",

        "clientAlgoId":
            writer_client_id(
                direction,
                "TP3",
            ),

        "reduceOnly":
            True,
    }

    legs = {

        "entry":
            entry_leg,

        "tp1":
            tp1_leg,

        "tp2":
            tp2_leg,

        "tp3":
            tp3_leg,
    }

    integrity_hash = (
        sha256_text(
            canonical_json(
                legs
            )
        )
    )

    return {

        "stage":
            STAGE,

        "symbol":
            SYMBOL,

        "direction":
            direction,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "entry_quantity":
            decimal_to_string(
                entry_quantity
            ),

        "tp1_quantity":
            decimal_to_string(
                tp1_qty
            ),

        "tp2_quantity":
            decimal_to_string(
                tp2_qty
            ),

        "tp3_quantity":
            decimal_to_string(
                tp3_qty
            ),

        "allocation_percent": {

            "tp1":
                decimal_to_string(
                    select_tp_allocation(
                        entry_quantity
                    )[
                        "tp1_percent"
                    ]
                ),

            "tp2":
                decimal_to_string(
                    select_tp_allocation(
                        entry_quantity
                    )[
                        "tp2_percent"
                    ]
                ),

            "tp3":
                decimal_to_string(
                    select_tp_allocation(
                        entry_quantity
                    )[
                        "tp3_percent"
                    ]
                ),
        },

        "allocation_label":
            select_tp_allocation(
                entry_quantity
            )[
                "label"
            ],

        "allocation_adjusted":
            select_tp_allocation(
                entry_quantity
            )[
                "adjusted"
            ],

        "quantity_validation":
            quantity_checks,

        "tp_approval":
            tp_snapshot[
                "tp_approval"
            ],

        "tp1":
            tp_snapshot[
                "tp1"
            ],

        "tp2":
            tp_snapshot[
                "tp2"
            ],

        "tp3":
            tp_snapshot[
                "tp3"
            ],

        "legs":
            legs,

        "primary_tp_immutable":
            True,

        "submitted":
            False,

        "transport_enabled":
            EXCHANGE_MUTATION_TRANSPORT_ENABLED,

        "integrity_sha256":
            integrity_hash,
    }


# ============================================================
# R36F.12 FIRST-LIVE WRITER SAFETY COMPLETION
# ============================================================

def validate_weex_v3_writer_shapes(
    writer_preview,
):
    """
    Validate only documented request fields needed
    by the frozen writer.
    """

    if not writer_preview:

        return {

            "all_valid":
                False,

            "reason":
                "WRITER_PREVIEW_MISSING",
        }

    legs = writer_preview.get(
        "legs",
        {},
    )

    entry = legs.get(
        "entry",
        {},
    )

    tp1 = legs.get(
        "tp1",
        {},
    )

    tp2 = legs.get(
        "tp2",
        {},
    )

    tp3 = legs.get(
        "tp3",
        {},
    )

    entry_required = {

        "endpoint",
        "method",
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
        "reduceOnly",
    }

    tpsl_required = {

        "endpoint",
        "method",
        "symbol",
        "positionSide",
        "planType",
        "triggerPrice",
        "executePrice",
        "quantity",
        "triggerPriceType",
        "clientAlgoId",
        "reduceOnly",
    }

    trailing_required = {

        "endpoint",
        "method",
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "callbackRate",
        "workingType",
        "clientAlgoId",
        "reduceOnly",
    }

    checks = {

        "entry_endpoint":
            entry.get(
                "endpoint"
            )
            == "/capi/v3/order",

        "entry_method":
            entry.get(
                "method"
            )
            == "POST",

        "entry_required_fields":
            entry_required.issubset(
                entry.keys()
            ),

        "entry_market_type":
            entry.get(
                "type"
            )
            == "MARKET",

        "entry_reduce_only_false":
            entry.get(
                "reduceOnly"
            )
            is False,

        "tp1_endpoint":
            tp1.get(
                "endpoint"
            )
            == "/capi/v3/placeTpSlOrder",

        "tp2_endpoint":
            tp2.get(
                "endpoint"
            )
            == "/capi/v3/placeTpSlOrder",

        "tp1_plan_type":
            tp1.get(
                "planType"
            )
            == "TAKE_PROFIT",

        "tp2_plan_type":
            tp2.get(
                "planType"
            )
            == "TAKE_PROFIT",

        "tp1_required_fields":
            tpsl_required.issubset(
                tp1.keys()
            ),

        "tp2_required_fields":
            tpsl_required.issubset(
                tp2.keys()
            ),

        "tp1_no_legacy_side":
            "side"
            not in tp1,

        "tp2_no_legacy_side":
            "side"
            not in tp2,

        "tp1_no_legacy_type":
            "type"
            not in tp1,

        "tp2_no_legacy_type":
            "type"
            not in tp2,

        "trailing_endpoint":
            tp3.get(
                "endpoint"
            )
            == "/capi/v3/algoOrder",

        "trailing_type":
            tp3.get(
                "type"
            )
            == "TRAILING_MARKET",

        "trailing_required_fields":
            trailing_required.issubset(
                tp3.keys()
            ),
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


def parse_canary_stop_price(
    text,
):

    if not text:

        return None

    value = D(
        text
    )

    if value <= Decimal("0"):

        raise ValueError(
            "R36F12_CANARY_STOP_PRICE must be positive"
        )

    return quantize_down(
        value,
        PRICE_STEP,
    )


def validate_canary_stop(
    direction,
    entry_price,
    stop_price,
):

    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    if direction == "LONG":

        return (
            stop_price
            < entry_price
        )

    if direction == "SHORT":

        return (
            stop_price
            > entry_price
        )

    return False


def calculate_r36f13_protective_stop(
    direction,
    entry_price,
):
    """
    Calculate the mandatory preview protective stop;
    never submits it.
    """

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

        stop_price = (
            quantize_down(
                raw_stop,
                PRICE_STEP,
            )
        )

    elif direction == "SHORT":

        raw_stop = (
            entry_price
            * (
                Decimal("1")
                + distance
            )
        )

        stop_price = (
            quantize_down(
                raw_stop,
                PRICE_STEP,
            )
        )

        if stop_price <= entry_price:

            stop_price = (
                quantize_down(
                    entry_price,
                    PRICE_STEP,
                )
                + PRICE_STEP
            )

    else:

        raise ValueError(
            "Invalid protective-stop direction"
        )

    return stop_price


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

    on_step = (
        stop_price
        % PRICE_STEP
    ) == 0

    positive = (
        stop_price
        > 0
    )

    if direction == "LONG":

        correct_side = (
            stop_price
            < entry_price
        )

        separated_from_tp = (
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

        separated_from_tp = (
            stop_price
            > entry_price
            > tp1_price
            > tp2_price
        )

    else:

        correct_side = False
        separated_from_tp = False

    checks = {

        "configured_or_calculated":
            True,

        "positive":
            positive,

        "correct_side_of_entry":
            correct_side,

        "price_step_normalized":
            on_step,

        "does_not_cross_entry_or_tp":
            separated_from_tp,
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


def calculate_r36f131_stop_distance_percent(
    entry_price,
    stop_price,
):

    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    if entry_price <= 0:

        raise ValueError(
            "entry_price must be positive"
        )

    return (
        abs(
            stop_price
            - entry_price
        )
        / entry_price
        * Decimal("100")
    )


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

    if leverage <= 0:

        raise ValueError(
            "leverage must be positive"
        )

    distance_percent = (
        calculate_r36f131_stop_distance_percent(
            entry_price,
            stop_price,
        )
    )

    leverage_reference_percent = (
        Decimal("100")
        / leverage
    )

    minimum_step_distance_percent = (
        PRICE_STEP
        / entry_price
        * Decimal("100")
    )

    checks = {

        "direction_valid":
            direction
            in {
                "LONG",
                "SHORT",
            },

        "distance_positive":
            distance_percent
            > 0,

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
                leverage_reference_percent
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

        "configured_maximum_percent":
            decimal_to_string(
                R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT
            ),

        "leverage_reference_percent":
            decimal_to_string(
                leverage_reference_percent
            ),

        "minimum_step_distance_percent":
            decimal_to_string(
                minimum_step_distance_percent
            ),

        "leverage":
            decimal_to_string(
                leverage
            ),

        "reference_is_not_liquidation_price":
            True,

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

    if entry_price <= 0:
        raise ValueError(
            "entry_price must be positive"
        )

    if entry_quantity <= 0:
        raise ValueError(
            "entry_quantity must be positive"
        )

    if available_balance <= 0:
        raise ValueError(
            "available_balance must be positive"
        )

    if leverage <= 0:
        raise ValueError(
            "leverage must be positive"
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
            price_distance
            > 0,

        "expected_loss_positive":
            expected_loss
            > 0,

        "within_account_loss_budget":
            expected_loss
            <= account_loss_budget,

        "within_isolated_entry_margin_budget":
            expected_loss
            <= isolated_entry_margin,
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return {

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "stop_price":
            decimal_to_string(
                stop_price
            ),

        "entry_quantity":
            decimal_to_string(
                entry_quantity
            ),

        "available_balance":
            decimal_to_string(
                available_balance
            ),

        "leverage":
            decimal_to_string(
                leverage
            ),

        "price_distance":
            decimal_to_string(
                price_distance
            ),

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

        "account_loss_budget_usdt":
            decimal_to_string(
                account_loss_budget
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


def apply_r36f132_stop_loss_budget_authorization_gate(
    command_preview,
    loss_budget,
):

    preview = dict(
        command_preview
        or {}
    )

    preview[
        "r36f132_stop_loss_budget_required"
    ] = True

    preview[
        "r36f132_stop_loss_budget_valid"
    ] = bool(
        loss_budget
        and
        loss_budget.get(
            "all_valid"
        )
    )

    if not preview.get(
        "authorized_preview"
    ):

        return preview

    if (
        not loss_budget
        or
        not loss_budget.get(
            "all_valid"
        )
    ):

        preview[
            "authorized_preview"
        ] = False

        preview[
            "reason"
        ] = (
            "PROTECTIVE_STOP_LOSS_BUDGET_NOT_READY"
        )

        preview[
            "exchange_order_sent"
        ] = False

        return preview

    preview[
        "reason"
    ] = (
        "COMMAND_EMA_TP_STOP_RISK_ENVELOPE_AND_LOSS_BUDGET_AGREE"
    )

    preview[
        "exchange_order_sent"
    ] = False

    return preview


def synthetic_r36f132_stop_loss_budget_tests():

    passing = (
        validate_r36f132_stop_loss_budget(
            Decimal(
                "80000"
            ),
            Decimal(
                "79600"
            ),
            Decimal(
                "0.0004"
            ),
            Decimal(
                "7.19"
            ),
            Decimal(
                "100"
            ),
        )
    )

    check(
        "R36F132_SYNTHETIC_STOP_LOSS_BUDGET_APPROVED",
        passing[
            "all_valid"
        ] is True,
    )

    check(
        "R36F132_SYNTHETIC_EXPECTED_LOSS_016_USDT",
        passing[
            "expected_loss_usdt"
        ] == "0.16",
    )

    check(
        "R36F132_SYNTHETIC_WITHIN_ACCOUNT_LOSS_BUDGET",
        passing[
            "checks"
        ][
            "within_account_loss_budget"
        ] is True,
    )

    check(
        "R36F132_SYNTHETIC_WITHIN_ENTRY_MARGIN_BUDGET",
        passing[
            "checks"
        ][
            "within_isolated_entry_margin_budget"
        ] is True,
    )

    failing = (
        validate_r36f132_stop_loss_budget(
            Decimal(
                "80000"
            ),
            Decimal(
                "79200"
            ),
            Decimal(
                "0.0004"
            ),
            Decimal(
                "7.19"
            ),
            Decimal(
                "100"
            ),
        )
    )

    check(
        "R36F132_SYNTHETIC_EXCESSIVE_ACCOUNT_LOSS_REJECTED",
        failing[
            "checks"
        ][
            "within_account_loss_budget"
        ] is False,
    )

    authorized = (
        apply_r36f132_stop_loss_budget_authorization_gate(
            {
                "authorized_preview":
                    True,

                "exchange_order_sent":
                    False,
            },
            passing,
        )
    )

    blocked = (
        apply_r36f132_stop_loss_budget_authorization_gate(
            {
                "authorized_preview":
                    True,

                "exchange_order_sent":
                    False,
            },
            failing,
        )
    )

    check(
        "R36F132_SYNTHETIC_AUTHORIZATION_GATE_APPROVES_SAFE_LOSS",
        authorized[
            "authorized_preview"
        ] is True,
    )

    check(
        "R36F132_SYNTHETIC_AUTHORIZATION_GATE_BLOCKS_EXCESSIVE_LOSS",
        blocked[
            "authorized_preview"
        ] is False,
    )

    check(
        "R36F132_SYNTHETIC_GATE_NEVER_SENDS_ORDER",
        (
            authorized.get(
                "exchange_order_sent"
            )
            is False

            and

            blocked.get(
                "exchange_order_sent"
            )
            is False
        ),
    )

    return True


def apply_r36f131_risk_envelope_authorization_gate(
    command_preview,
    envelope,
):

    preview = dict(
        command_preview
        or {}
    )

    preview[
        "r36f131_stop_risk_envelope_required"
    ] = True

    preview[
        "r36f131_stop_risk_envelope_valid"
    ] = bool(
        envelope
        and
        envelope.get(
            "all_valid"
        )
    )

    if not preview.get(
        "authorized_preview"
    ):

        return preview

    if (
        not envelope
        or
        not envelope.get(
            "all_valid"
        )
    ):

        preview[
            "authorized_preview"
        ] = False

        preview[
            "reason"
        ] = (
            "PROTECTIVE_STOP_RISK_ENVELOPE_NOT_READY"
        )

        preview[
            "exchange_order_sent"
        ] = False

        return preview

    preview[
        "reason"
    ] = (
        "COMMAND_EMA_TP_STOP_AND_RISK_ENVELOPE_AGREE"
    )

    preview[
        "exchange_order_sent"
    ] = False

    return preview


def apply_r36f13_stop_authorization_gate(
    command_preview,
    stop_checks,
):

    preview = dict(
        command_preview
        or {}
    )

    if not preview.get(
        "authorized_preview"
    ):

        preview[
            "r36f13_protective_stop_required"
        ] = True

        preview[
            "r36f13_protective_stop_valid"
        ] = bool(
            stop_checks
            and
            stop_checks.get(
                "all_valid"
            )
        )

        return preview

    if (
        not stop_checks
        or
        not stop_checks.get(
            "all_valid"
        )
    ):

        preview[
            "authorized_preview"
        ] = False

        preview[
            "reason"
        ] = (
            "PROTECTIVE_STOP_NOT_READY"
        )

        preview[
            "r36f13_protective_stop_required"
        ] = True

        preview[
            "r36f13_protective_stop_valid"
        ] = False

        preview[
            "exchange_order_sent"
        ] = False

        return preview

    preview[
        "reason"
    ] = (
        "COMMAND_EMA_TP_AND_PROTECTIVE_STOP_AGREE"
    )

    preview[
        "r36f13_protective_stop_required"
    ] = True

    preview[
        "r36f13_protective_stop_valid"
    ] = True

    preview[
        "exchange_order_sent"
    ] = False

    return preview


def unresolved_canary_journal(
    journal,
):

    if not journal:
        return False

    return (
        str(
            journal.get(
                "status",
                "",
            )
        ).upper()
        in {
            "PREPARED",
            "DISPATCHING",
            "SUBMITTED",
            "AMBIGUOUS",
        }
    )


def build_protected_canary_preview(
    writer_preview,
    stop_price,
    explicit_arm_requested,
    journal,
    flat_position,
):
    """
    Build the R36F.12-ready canary package without sending it.
    """

    if not writer_preview:

        raise ValueError(
            "writer preview required"
        )

    direction = writer_preview[
        "direction"
    ]

    entry_price = D(
        writer_preview[
            "entry_price"
        ]
    )

    entry_quantity = D(
        writer_preview[
            "entry_quantity"
        ]
    )

    stop_price = D(
        stop_price
    )

    schema_checks = (
        validate_weex_v3_writer_shapes(
            writer_preview
        )
    )

    stop_valid = (
        validate_canary_stop(
            direction,
            entry_price,
            stop_price,
        )
    )

    quantity_capped = (
        entry_quantity
        <= CANARY_MAX_ENTRY_QUANTITY
    )

    journal_clear = (
        not unresolved_canary_journal(
            journal
        )
    )

    protected_entry = dict(
        writer_preview[
            "legs"
        ][
            "entry"
        ]
    )

    protected_entry[
        "slTriggerPrice"
    ] = decimal_to_string(
        stop_price
    )

    protected_entry[
        "SlWorkingType"
    ] = CANARY_STOP_WORKING_TYPE

    ready = bool(

        schema_checks.get(
            "all_valid"
        )

        and

        stop_valid

        and

        quantity_capped

        and

        explicit_arm_requested

        and

        journal_clear

        and

        flat_position

        and

        writer_preview.get(
            "quantity_validation",
            {},
        ).get(
            "all_valid"
        )
    )

    return {

        "stage":
            STAGE,

        "status":
            (
                "READY_FOR_R36F12"
                if ready
                else
                "BLOCKED"
            ),

        "ready_for_r36f12":
            ready,

        "direction":
            direction,

        "entry_quantity":
            decimal_to_string(
                entry_quantity
            ),

        "canary_max_entry_quantity":
            decimal_to_string(
                CANARY_MAX_ENTRY_QUANTITY
            ),

        "quantity_capped":
            quantity_capped,

        "stop_price":
            decimal_to_string(
                stop_price
            ),

        "stop_valid":
            stop_valid,

        "stop_working_type":
            CANARY_STOP_WORKING_TYPE,

        "explicit_arm_requested":
            bool(
                explicit_arm_requested
            ),

        "journal_clear":
            journal_clear,

        "flat_position":
            bool(
                flat_position
            ),

        "writer_schema_valid":
            bool(
                schema_checks.get(
                    "all_valid"
                )
            ),

        "writer_schema_checks":
            schema_checks,

        "protected_entry_request":
            protected_entry,

        "tp1_request":
            writer_preview[
                "legs"
            ][
                "tp1"
            ],

        "tp2_request":
            writer_preview[
                "legs"
            ][
                "tp2"
            ],

        "tp3_request":
            writer_preview[
                "legs"
            ][
                "tp3"
            ],

        "submitted":
            False,

        "exchange_request_sent":
            False,

        "r36f12_transport_hard_disabled":
            True,
    }


def synthetic_r36f12_writer_safety_tests():

    synthetic_entry = Decimal(
        "80000"
    )

    synthetic_rows = [

        [
            0,
            "80000",
            "80200",
            "79900",
            "80100",
            "1",
        ],

        [
            1,
            "80100",
            "80300",
            "80000",
            "80200",
            "1",
        ],

        [
            2,
            "80200",
            "80400",
            "80100",
            "80300",
            "1",
        ],

        [
            3,
            "80300",
            "80500",
            "80200",
            "80400",
            "1",
        ],

        [
            4,
            "80400",
            "80600",
            "80300",
            "80500",
            "1",
        ],
    ]

    tp_snapshot = {

        "tp_approval": {

            "approved":
                True,

            "status":
                "APPROVED",

            "reason":
                "SYNTHETIC",
        },

        "tp1":
            "80100",

        "tp2":
            "80300",

        "tp3":
            "TRAILING",
    }

    preview = (
        build_writer_request_preview(
            "LONG",
            synthetic_entry,
            Decimal(
                "0.0004"
            ),
            tp_snapshot,
        )
    )

    shape = (
        validate_weex_v3_writer_shapes(
            preview
        )
    )

    check(
        "R36F12_WEEX_V3_WRITER_SHAPES",
        shape[
            "all_valid"
        ],
    )

    clear = (
        build_protected_canary_preview(
            preview,
            Decimal(
                "79600"
            ),
            True,
            {},
            True,
        )
    )

    check(
        "R36F12_SYNTHETIC_PROTECTED_CANARY_READY",
        clear[
            "ready_for_r36f12"
        ] is True,
    )

    check(
        "R36F12_SYNTHETIC_CANARY_QTY_CAP_00004",
        clear[
            "entry_quantity"
        ] == "0.0004",
    )

    check(
        "R36F12_SYNTHETIC_STOP_ATTACHED",
        clear[
            "protected_entry_request"
        ].get(
            "slTriggerPrice"
        ) == "79600",
    )

    ambiguous = (
        build_protected_canary_preview(
            preview,
            Decimal(
                "79600"
            ),
            True,
            {
                "status":
                    "AMBIGUOUS"
            },
            True,
        )
    )

    check(
        "R36F12_AMBIGUOUS_JOURNAL_BLOCKS",
        ambiguous[
            "ready_for_r36f12"
        ] is False,
    )

    unarmed = (
        build_protected_canary_preview(
            preview,
            Decimal(
                "79600"
            ),
            False,
            {},
            True,
        )
    )

    check(
        "R36F12_EXPLICIT_ARM_REQUIRED",
        unarmed[
            "ready_for_r36f12"
        ] is False,
    )

    wrong_stop = (
        build_protected_canary_preview(
            preview,
            Decimal(
                "80400"
            ),
            True,
            {},
            True,
        )
    )

    check(
        "R36F12_WRONG_SIDE_STOP_BLOCKS",
        wrong_stop[
            "ready_for_r36f12"
        ] is False,
    )

    return True


# ============================================================
# R36F.12 ADJUSTABLE TP QUANTITY FEASIBILITY TESTS
# ============================================================

def synthetic_writer_quantity_tests():

    adjusted = (
        evaluate_writer_quantity_feasibility(
            Decimal(
                "0.0004"
            )
        )
    )

    check(
        "ADJUSTABLE_00004_APPROVED",
        adjusted[
            "feasible"
        ] is True,
    )

    check(
        "ADJUSTABLE_00004_SELECTED_25_25_50",
        adjusted[
            "selected_allocation"
        ] == "25/25/50",
    )

    check(
        "ADJUSTABLE_00004_ADJUSTED_TRUE",
        adjusted[
            "allocation_adjusted"
        ] is True,
    )

    check(
        "ADJUSTABLE_00004_TP1",
        adjusted[
            "tp1_quantity"
        ] == "0.0001",
    )

    check(
        "ADJUSTABLE_00004_TP2",
        adjusted[
            "tp2_quantity"
        ] == "0.0001",
    )

    check(
        "ADJUSTABLE_00004_TP3",
        adjusted[
            "tp3_quantity"
        ] == "0.0002",
    )

    preferred = (
        evaluate_writer_quantity_feasibility(
            Decimal(
                "0.0005"
            )
        )
    )

    check(
        "PREFERRED_00005_APPROVED",
        preferred[
            "feasible"
        ] is True,
    )

    check(
        "PREFERRED_00005_RETAINS_20_20_60",
        preferred[
            "selected_allocation"
        ] == "20/20/60",
    )

    check(
        "PREFERRED_00005_ADJUSTED_FALSE",
        preferred[
            "allocation_adjusted"
        ] is False,
    )

    check(
        "PREFERRED_00005_TP1",
        preferred[
            "tp1_quantity"
        ] == "0.0001",
    )

    check(
        "PREFERRED_00005_TP2",
        preferred[
            "tp2_quantity"
        ] == "0.0001",
    )

    check(
        "PREFERRED_00005_TP3",
        preferred[
            "tp3_quantity"
        ] == "0.0003",
    )

    smaller = (
        evaluate_writer_quantity_feasibility(
            Decimal(
                "0.0003"
            )
        )
    )

    check(
        "ADJUSTABLE_00003_REJECTED",
        smaller[
            "feasible"
        ] is False,
    )

    check(
        "ADJUSTABLE_MINIMUM_ENTRY_00004",
        adjusted[
            "minimum_required_entry_quantity"
        ] == "0.0004",
    )

    return True


def synthetic_balance_readiness_tests():

    approved = (
        evaluate_strict_tp_balance_readiness(
            Decimal(
                "7.19"
            ),
            Decimal(
                "80000"
            ),
            Decimal(
                "100"
            ),
        )
    )

    check(
        "ADJUSTABLE_BALANCE_READINESS_7_19_APPROVED",
        approved[
            "eligible"
        ] is True,
    )

    check(
        "ADJUSTABLE_BALANCE_READINESS_7_19_PLANNED_00004",
        approved[
            "planned_entry_quantity"
        ] == "0.0004",
    )

    check(
        "ADJUSTABLE_BALANCE_READINESS_7_19_SELECTED_25_25_50",
        approved[
            "selected_allocation"
        ] == "25/25/50",
    )

    check(
        "ADJUSTABLE_BALANCE_READINESS_REQUIRED_BALANCE_6_40",
        approved[
            "required_available_balance"
        ] == "6.4",
    )

    preferred = (
        evaluate_strict_tp_balance_readiness(
            Decimal(
                "8"
            ),
            Decimal(
                "80000"
            ),
            Decimal(
                "100"
            ),
        )
    )

    check(
        "PREFERRED_BALANCE_READINESS_8_00_APPROVED",
        preferred[
            "eligible"
        ] is True,
    )

    check(
        "PREFERRED_BALANCE_READINESS_8_00_PLANNED_00005",
        preferred[
            "planned_entry_quantity"
        ] == "0.0005",
    )

    check(
        "PREFERRED_BALANCE_READINESS_8_00_RETAINS_20_20_60",
        preferred[
            "selected_allocation"
        ] == "20/20/60",
    )

    return True


# ============================================================
# MAIN R36F.12 TEST
# ============================================================

async def run_r36f12():

    global TEST_STATUS

    global R36A_EVIDENCE_OK
    global R36C_EVIDENCE_OK
    global R36D_EVIDENCE_OK

    global DURABLE_EVIDENCE_OK
    global WEEX_READ_ONLY_OK

    global ZERO_WRITE_INVARIANT_OK
    global FINAL_GATE_OK

    global LONG_DIAGNOSTICS
    global SHORT_DIAGNOSTICS

    TEST_STATUS = "RUNNING"

    r36f14_demo_account = None
    r36f14_demo_integration = None
    r36f14_demo_order_preview = None
    r36f14_demo_order_validation = None

    FINAL_BLOCKERS.clear()

    line()

    log(
        f"{STAGE}: {PURPOSE}"
    )

    line()

    check(
        "REAL_ORDER_EXECUTION_DISABLED",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "DEMO_ORDER_EXECUTION_DISABLED",
        DEMO_ORDER_EXECUTION is False,
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
        "LEVERAGE_MUTATION_DISABLED",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "MARGIN_MODE_MUTATION_DISABLED",
        MARGIN_MODE_MUTATION_ENABLED
        is False,
    )

    check(
        "POSITION_MUTATION_DISABLED",
        POSITION_MUTATION_ENABLED
        is False,
    )

    check(
        "FIRST_REAL_ORDER_DISABLED",
        FIRST_REAL_ORDER_ALLOWED
        is False,
    )

    check(
        "R36F14_DEMO_POST_TRANSPORT_DISABLED",
        R36F14_DEMO_POST_TRANSPORT_ENABLED
        is False,
    )

    check(
        "R36F14_DEMO_ORDER_SUBMISSION_DISABLED",
        R36F14_DEMO_ORDER_SUBMISSION_ENABLED
        is False,
    )

    check(
        "R36F14_FIRST_DEMO_ORDER_DISABLED",
        R36F14_FIRST_DEMO_ORDER_ALLOWED
        is False,
    )

    check(
        "WEEX_API_KEY_PRESENT",
        bool(
            os.getenv(
                "WEEX_API_KEY"
            )
        ),
    )

    check(
        "WEEX_API_SECRET_PRESENT",
        bool(
            os.getenv(
                "WEEX_API_SECRET"
            )
        ),
    )

    check(
        "WEEX_API_PASSPHRASE_PRESENT",
        bool(
            os.getenv(
                "WEEX_API_PASSPHRASE"
            )
        ),
    )

    r36a_ids = set()

    r36a_ids.update(
        collect_ids_from_file(
            R36A_DEDUPE_FILE
        )
    )

    r36a_ids.update(
        collect_ids_from_file(
            R36A_DECISION_FILE
        )
    )

    R36A_EVIDENCE_OK = (
        OLD_R36A_UPDATE_ID
        in r36a_ids
    )

    check(
        "R36A_DURABLE_EVIDENCE",
        R36A_EVIDENCE_OK,
        (
            f"EXPECTED_UPDATE_ID="
            f"{OLD_R36A_UPDATE_ID}"
        ),
    )

    r36c_ids = set()

    r36c_ids.update(
        collect_ids_from_file(
            R36C_DEDUPE_FILE
        )
    )

    r36c_ids.update(
        collect_ids_from_file(
            R36C_DECISION_FILE
        )
    )

    R36C_EVIDENCE_OK = (
        R36C_UPDATE_ID
        in r36c_ids
    )

    check(
        "R36C_DURABLE_EVIDENCE",
        R36C_EVIDENCE_OK,
        (
            f"EXPECTED_UPDATE_ID="
            f"{R36C_UPDATE_ID}"
        ),
    )

    r36d_snapshot = read_json_file(
        R36D_SNAPSHOT_FILE,
        default={},
    )

    R36D_EVIDENCE_OK = bool(
        r36d_snapshot
    )

    check(
        "R36D_SNAPSHOT_EVIDENCE",
        R36D_EVIDENCE_OK,
        f"path={R36D_SNAPSHOT_FILE}",
    )

    DURABLE_EVIDENCE_OK = (
        R36A_EVIDENCE_OK
        and
        R36C_EVIDENCE_OK
        and
        R36D_EVIDENCE_OK
    )

    try:

        await reconcile_weex()

        WEEX_READ_ONLY_OK = True

        try:

            r36f14_demo_account = (
                await r36f14_read_demo_account()
            )

            diagnostic_check(
                "R36F14_DEMO_READ_ONLY_RECONCILIATION",
                r36f14_demo_account.get(
                    "all_reads_successful",
                    False,
                ),
                (
                    "asset="
                    + str(
                        r36f14_demo_account.get(
                            "demo_asset"
                        )
                    )
                    + " available="
                    + str(
                        r36f14_demo_account.get(
                            "available_balance"
                        )
                    )
                    + " open_positions="
                    + str(
                        r36f14_demo_account.get(
                            "open_demo_position_count"
                        )
                    )
                    + " history_count="
                    + str(
                        r36f14_demo_account.get(
                            "history_count"
                        )
                    )
                ),
            )

        except Exception as exc:

            r36f14_demo_account = {

                "all_reads_successful":
                    False,

                "error":
                    str(
                        exc
                    ),
            }

            diagnostic_check(
                "R36F14_DEMO_READ_ONLY_RECONCILIATION",
                False,
                str(
                    exc
                ),
            )

        diagnostic_check(
            "WEEX_READ_ONLY_RECONCILIATION",
            True,
        )

    except Exception as exc:

        WEEX_READ_ONLY_OK = False

        diagnostic_check(
            "WEEX_READ_ONLY_RECONCILIATION",
            False,
            str(
                exc
            ),
        )

    synthetic_long = None
    synthetic_short = None

    try:

        (
            synthetic_long,
            synthetic_short,
        ) = synthetic_cluster_tests()

        check(
            "SYNTHETIC_TP_ENGINE",
            True,
        )

    except Exception as exc:

        check(
            "SYNTHETIC_TP_ENGINE",
            False,
            str(
                exc
            ),
        )

    try:

        rejection = (
            synthetic_tp_rejection_test()
        )

        check(
            "TP_APPROVAL_REJECTION_FLOW",
            rejection[
                "approved"
            ] is False,
        )

    except Exception as exc:

        check(
            "TP_APPROVAL_REJECTION_FLOW",
            False,
            str(
                exc
            ),
        )

    try:

        synthetic_writer_quantity_tests()

        check(
            "STRICT_TP_QUANTITY_FEASIBILITY_TESTS",
            True,
        )

        synthetic_balance_readiness_tests()

        check(
            "ADJUSTABLE_TP_BALANCE_READINESS_TESTS",
            True,
        )

        synthetic_r36f12_writer_safety_tests()

        synthetic_r36f12_ema_telegram_tests()

        synthetic_r36f132_stop_loss_budget_tests()

        r36f14_demo_integration = (
            synthetic_r36f14_demo_integration_tests()
        )

        check(
            "R36F12_WRITER_SAFETY_TESTS",
            True,
        )

    except Exception as exc:

        check(
            "STRICT_TP_QUANTITY_FEASIBILITY_TESTS",
            False,
            str(
                exc
            ),
        )

        check(
            "ADJUSTABLE_TP_BALANCE_READINESS_TESTS",
            False,
            str(
                exc
            ),
        )

    historical_rows = []

    try:

        historical_rows = (
            await load_historical_klines()
        )

        check(
            "REAL_HISTORICAL_KLINES_LOADED",
            len(
                historical_rows
            ) >= 3,
            f"rows={len(historical_rows)}",
        )

        global EMA_SIGNAL_SNAPSHOT
        global TELEGRAM_COMMAND_PREVIEW

        EMA_SIGNAL_SNAPSHOT = (
            build_ema_signal_snapshot(
                historical_rows
            )
        )

        diagnostic_check(
            "R36F12_EMA_ENGINE_READY",
            EMA_SIGNAL_SNAPSHOT.get(
                "ready"
            ) is True,
            (
                f"reason="
                f"{EMA_SIGNAL_SNAPSHOT.get('reason')}"
            ),
        )

        if EMA_SIGNAL_SNAPSHOT.get(
            "ready"
        ):

            log(
                f"R36F.12 EMA SNAPSHOT "
                f"price={EMA_SIGNAL_SNAPSHOT.get('price')} "
                f"EMA19={EMA_SIGNAL_SNAPSHOT.get('ema19')} "
                f"EMA50={EMA_SIGNAL_SNAPSHOT.get('ema50')} "
                f"EMA200={EMA_SIGNAL_SNAPSHOT.get('ema200')} "
                f"structure={EMA_SIGNAL_SNAPSHOT.get('structure')} "
                f"ideal_direction={EMA_SIGNAL_SNAPSHOT.get('ideal_direction')} "
                f"fresh_crossover={EMA_SIGNAL_SNAPSHOT.get('fresh_crossover')}"
            )

            diagnostic_check(
                "R36F12_EMA_19_50_SEPARATION_QUALITY",
                EMA_SIGNAL_SNAPSHOT.get(
                    "quality_ok"
                ) is True,
                (
                    f"separation="
                    f"{EMA_SIGNAL_SNAPSHOT.get('ema19_50_separation_percent')}%"
                ),
            )

            ideal_alert = (
                build_ideal_condition_alert(
                    EMA_SIGNAL_SNAPSHOT
                )
            )

            if ideal_alert:

                log(
                    "R36F.12 TELEGRAM IDEAL-CONDITION ALERT PREVIEW:"
                )

                for alert_line in ideal_alert.splitlines():

                    log(
                        "      "
                        + alert_line
                    )

                telegram_alert_result = (
                    await send_r36f12_telegram_alert(
                        ideal_alert
                    )
                )

                diagnostic_check(
                    "R36F12_TELEGRAM_IDEAL_ALERT_PATH",
                    True,
                    (
                        f"enabled="
                        f"{R36F12_TELEGRAM_ALERTS_ENABLED} "
                        f"result="
                        f"{telegram_alert_result}"
                    ),
                )

            else:

                diagnostic_check(
                    "R36F12_TELEGRAM_IDEAL_ALERT_PATH",
                    True,
                    (
                        "No current ideal EMA direction; "
                        "no alert sent"
                    ),
                )

    except Exception as exc:

        check(
            "REAL_HISTORICAL_KLINES_LOADED",
            False,
            str(
                exc
            ),
        )

    real_long_snapshot = None

    REAL_LONG_MARKET_ELIGIBLE = False

    if (
        historical_rows
        and
        MARK_PRICE is not None
    ):

        try:

            real_long_snapshot = (
                build_cluster_tp_snapshot(
                    MARK_PRICE,
                    historical_rows,
                    "LONG",
                    "REAL_LONG_PREVIEW",
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

            diagnostic_check(
                "REAL_LONG_TP_MARKET_ELIGIBILITY",
                REAL_LONG_MARKET_ELIGIBLE,
                (
                    "TP_APPROVAL="
                    + real_long_snapshot[
                        "tp_approval"
                    ][
                        "status"
                    ]
                ),
            )

            log(
                "REAL_LONG_TP_APPROVAL="
                + real_long_snapshot[
                    "tp_approval"
                ][
                    "status"
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

            approval = (
                evaluate_tp_approval(
                    LONG_DIAGNOSTICS
                )
            )

            REAL_LONG_MARKET_ELIGIBLE = False

            diagnostic_check(
                "REAL_LONG_TP_MARKET_ELIGIBILITY",
                False,
                (
                    "TP_APPROVAL="
                    + approval[
                        "status"
                    ]
                    + " reason="
                    + approval[
                        "reason"
                    ]
                    + " error="
                    + str(
                        exc
                    )
                ),
            )

    real_short_snapshot = None

    REAL_SHORT_MARKET_ELIGIBLE = False

    if (
        historical_rows
        and
        MARK_PRICE is not None
    ):

        try:

            real_short_snapshot = (
                build_cluster_tp_snapshot(
                    MARK_PRICE,
                    historical_rows,
                    "SHORT",
                    "REAL_SHORT_PREVIEW",
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

            diagnostic_check(
                "REAL_SHORT_TP_MARKET_ELIGIBILITY",
                REAL_SHORT_MARKET_ELIGIBLE,
                (
                    "TP_APPROVAL="
                    + real_short_snapshot[
                        "tp_approval"
                    ][
                        "status"
                    ]
                ),
            )

            log(
                "REAL_SHORT_TP_APPROVAL="
                + real_short_snapshot[
                    "tp_approval"
                ][
                    "status"
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

            approval = (
                evaluate_tp_approval(
                    SHORT_DIAGNOSTICS
                )
            )

            REAL_SHORT_MARKET_ELIGIBLE = False

            diagnostic_check(
                "REAL_SHORT_TP_MARKET_ELIGIBILITY",
                False,
                (
                    "TP_APPROVAL="
                    + approval[
                        "status"
                    ]
                    + " reason="
                    + approval[
                        "reason"
                    ]
                    + " error="
                    + str(
                        exc
                    )
                ),
            )

    canary_preview = None

    try:

        current_command = os.getenv(
            "R36F12_TELEGRAM_COMMAND_TEXT",
            "",
        ).strip()

        if current_command:

            TELEGRAM_COMMAND_PREVIEW = (
                validate_telegram_command_against_signal(
                    current_command,
                    EMA_SIGNAL_SNAPSHOT,
                    REAL_LONG_MARKET_ELIGIBLE,
                    REAL_SHORT_MARKET_ELIGIBLE,
                )
            )

            log(
                f"R36F.12 TELEGRAM COMMAND PREVIEW = "
                f"{TELEGRAM_COMMAND_PREVIEW}"
            )

        else:

            TELEGRAM_COMMAND_PREVIEW = {

                "recognized":
                    False,

                "authorized_preview":
                    False,

                "reason":
                    "NO_COMMAND_SUPPLIED",

                "exchange_order_sent":
                    False,
            }

        canary_preview = (
            build_canary_preview()
        )

        diagnostic_check(
            "CANARY_PREVIEW",
            True,
        )

    except Exception as exc:

        diagnostic_check(
            "CANARY_PREVIEW",
            False,
            str(
                exc
            ),
        )

    writer_preview = None
    protected_canary_preview = None

    r36f13_stop_price = None
    r36f13_stop_checks = None

    r36f131_stop_envelope = None
    r36f132_stop_loss_budget = None

    quantity_feasibility = None
    balance_readiness = None

    WRITER_CONSTRUCTION_ELIGIBLE = False

    try:

        selected_direction = None
        selected_snapshot = None

        if (
            REAL_SHORT_MARKET_ELIGIBLE
            and
            real_short_snapshot is not None
        ):

            selected_direction = "SHORT"
            selected_snapshot = real_short_snapshot

        elif (
            REAL_LONG_MARKET_ELIGIBLE
            and
            real_long_snapshot is not None
        ):

            selected_direction = "LONG"
            selected_snapshot = real_long_snapshot

        if selected_direction is None:

            diagnostic_check(
                "ADJUSTABLE_TP_BALANCE_READINESS",
                False,
                (
                    "TRADE_NOT_ELIGIBLE: "
                    "no currently eligible real market TP set"
                ),
            )

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                (
                    "blocked: no currently eligible "
                    "real market TP set"
                ),
            )

        elif (
            AVAILABLE_BALANCE is None
            or
            MARK_PRICE is None
        ):

            diagnostic_check(
                "ADJUSTABLE_TP_BALANCE_READINESS",
                False,
                (
                    "READINESS_UNAVAILABLE: "
                    "balance or mark price unavailable"
                ),
            )

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                (
                    "blocked: balance or mark price unavailable"
                ),
            )

        else:

            leverage = (
                LEVERAGE_SHORT
                if selected_direction == "SHORT"
                else LEVERAGE_LONG
            )

            balance_readiness = (
                evaluate_strict_tp_balance_readiness(
                    AVAILABLE_BALANCE,
                    MARK_PRICE,
                    leverage,
                )
            )

            quantity_feasibility = (
                evaluate_writer_quantity_feasibility(
                    D(
                        balance_readiness[
                            "planned_entry_quantity"
                        ]
                    )
                )
            )

            log(
                "R36F.12 ADJUSTABLE TP BALANCE READINESS "
                + "direction="
                + selected_direction
                + " status="
                + balance_readiness[
                    "status"
                ]
                + " reason="
                + balance_readiness[
                    "reason"
                ]
                + " available_usdt="
                + balance_readiness[
                    "available_balance"
                ]
                + " planned_entry_qty="
                + balance_readiness[
                    "planned_entry_quantity"
                ]
                + " minimum_entry_qty="
                + balance_readiness[
                    "minimum_strict_tp_entry_quantity"
                ]
                + " required_margin_usdt="
                + balance_readiness[
                    "required_margin_for_minimum_qty"
                ]
                + " required_available_usdt="
                + balance_readiness[
                    "required_available_balance"
                ]
                + " shortfall_usdt="
                + balance_readiness[
                    "available_balance_shortfall"
                ]
            )

            diagnostic_check(
                "ADJUSTABLE_TP_BALANCE_READINESS",
                balance_readiness[
                    "eligible"
                ],
                (
                    "status="
                    + balance_readiness[
                        "status"
                    ]
                    + " reason="
                    + balance_readiness[
                        "reason"
                    ]
                ),
            )

            diagnostic_check(
                "ADJUSTABLE_TP_QUANTITY_FEASIBILITY",
                quantity_feasibility[
                    "feasible"
                ],
                (
                    "reason="
                    + quantity_feasibility[
                        "reason"
                    ]
                ),
            )

            if not balance_readiness[
                "eligible"
            ]:

                log(
                    "R36F.11 TRADE_READINESS = REJECTED "
                    + "reason="
                    + balance_readiness[
                        "reason"
                    ]
                )

                diagnostic_check(
                    "WRITER_REQUEST_CONSTRUCTION",
                    False,
                    (
                        "blocked before construction: "
                        + balance_readiness[
                            "reason"
                        ]
                    ),
                )

            else:

                quantity = D(
                    balance_readiness[
                        "planned_entry_quantity"
                    ]
                )

                log(
                    "R36F.11 TRADE_READINESS = ELIGIBLE "
                    + "reason="
                    + balance_readiness[
                        "reason"
                    ]
                )

                writer_preview = (
                    build_writer_request_preview(
                        selected_direction,
                        MARK_PRICE,
                        quantity,
                        selected_snapshot,
                    )
                )

                WRITER_CONSTRUCTION_ELIGIBLE = bool(
                    writer_preview[
                        "submitted"
                    ] is False

                    and

                    writer_preview[
                        "quantity_validation"
                    ][
                        "all_valid"
                    ]

                    and

                    writer_preview[
                        "transport_enabled"
                    ] is False
                )

                diagnostic_check(
                    "WRITER_REQUEST_CONSTRUCTION",
                    WRITER_CONSTRUCTION_ELIGIBLE,
                    (
                        "direction="
                        + selected_direction
                        + " quantity="
                        + writer_preview[
                            "entry_quantity"
                        ]
                        + " tp1_qty="
                        + writer_preview[
                            "tp1_quantity"
                        ]
                        + " tp2_qty="
                        + writer_preview[
                            "tp2_quantity"
                        ]
                        + " tp3_qty="
                        + writer_preview[
                            "tp3_quantity"
                        ]
                    ),
                )

                for (
                    validation_name,
                    validation_result,
                ) in writer_preview[
                    "quantity_validation"
                ].items():

                    if validation_name == "all_valid":
                        continue

                    diagnostic_check(
                        "WRITER_QUANTITY_"
                        + validation_name.upper(),
                        validation_result,
                    )

                canary_quantity = min(
                    quantity,
                    CANARY_MAX_ENTRY_QUANTITY,
                )

                canary_writer_preview = (
                    build_writer_request_preview(
                        selected_direction,
                        MARK_PRICE,
                        canary_quantity,
                        selected_snapshot,
                    )
                )

                production_journal = (
                    read_json_file(
                        R36F12_CANARY_JOURNAL_FILE,
                        default={},
                    )
                )

                configured_stop = (
                    parse_canary_stop_price(
                        CANARY_STOP_PRICE_TEXT
                    )
                )

                r36f13_stop_price = (
                    configured_stop
                    if configured_stop is not None
                    else
                    calculate_r36f13_protective_stop(
                        selected_direction,
                        canary_writer_preview[
                            "entry_price"
                        ],
                    )
                )

                r36f13_stop_checks = (
                    validate_r36f13_protective_stop(
                        selected_direction,
                        canary_writer_preview[
                            "entry_price"
                        ],
                        r36f13_stop_price,
                        canary_writer_preview[
                            "tp1"
                        ],
                        canary_writer_preview[
                            "tp2"
                        ],
                    )
                )

                diagnostic_check(
                    "R36F13_PROTECTIVE_STOP_CALCULATED_OR_CONFIGURED",
                    r36f13_stop_checks[
                        "configured_or_calculated"
                    ],
                    (
                        "stop="
                        + decimal_to_string(
                            r36f13_stop_price
                        )
                    ),
                )

                for (
                    stop_check_name,
                    stop_check_result,
                ) in r36f13_stop_checks.items():

                    if stop_check_name in {
                        "all_valid",
                        "configured_or_calculated",
                    }:

                        continue

                    diagnostic_check(
                        "R36F13_PROTECTIVE_STOP_"
                        + stop_check_name.upper(),
                        stop_check_result,
                    )

                check(
                    "R36F13_PROTECTIVE_STOP_AUTHORIZATION_GATE",
                    r36f13_stop_checks[
                        "all_valid"
                    ],
                )

                r36f131_stop_envelope = (
                    validate_r36f131_stop_risk_envelope(
                        selected_direction,
                        canary_writer_preview[
                            "entry_price"
                        ],
                        r36f13_stop_price,
                        leverage,
                    )
                )

                log(
                    "R36F.13.1 STOP RISK ENVELOPE "
                    + "distance_percent="
                    + r36f131_stop_envelope[
                        "distance_percent"
                    ]
                    + " max_percent="
                    + r36f131_stop_envelope[
                        "configured_maximum_percent"
                    ]
                    + " leverage_reference_percent="
                    + r36f131_stop_envelope[
                        "leverage_reference_percent"
                    ]
                )

                for (
                    envelope_check_name,
                    envelope_check_result,
                ) in r36f131_stop_envelope[
                    "checks"
                ].items():

                    diagnostic_check(
                        "R36F131_STOP_RISK_ENVELOPE_"
                        + envelope_check_name.upper(),
                        envelope_check_result,
                    )

                check(
                    "R36F131_STOP_RISK_ENVELOPE_AUTHORIZATION_GATE",
                    r36f131_stop_envelope[
                        "all_valid"
                    ],
                )

                r36f132_stop_loss_budget = (
                    validate_r36f132_stop_loss_budget(
                        canary_writer_preview[
                            "entry_price"
                        ],
                        r36f13_stop_price,
                        canary_writer_preview[
                            "entry_quantity"
                        ],
                        AVAILABLE_BALANCE,
                        leverage,
                    )
                )

                log(
                    "R36F.13.2 STOP LOSS BUDGET "
                    + "expected_loss_usdt="
                    + r36f132_stop_loss_budget[
                        "expected_loss_usdt"
                    ]
                    + " expected_loss_percent="
                    + r36f132_stop_loss_budget[
                        "expected_loss_percent_of_available_balance"
                    ]
                    + " max_account_loss_percent="
                    + r36f132_stop_loss_budget[
                        "configured_max_account_loss_percent"
                    ]
                    + " isolated_entry_margin_usdt="
                    + r36f132_stop_loss_budget[
                        "isolated_entry_margin_usdt"
                    ]
                )

                for (
                    loss_check_name,
                    loss_check_result,
                ) in r36f132_stop_loss_budget[
                    "checks"
                ].items():

                    if loss_check_name == "all_valid":
                        continue

                    diagnostic_check(
                        "R36F132_STOP_LOSS_BUDGET_"
                        + loss_check_name.upper(),
                        loss_check_result,
                    )

                check(
                    "R36F132_STOP_LOSS_BUDGET_AUTHORIZATION_GATE",
                    r36f132_stop_loss_budget[
                        "all_valid"
                    ],
                )

                r36f14_demo_order_preview = (
                    build_r36f14_demo_order_preview(
                        selected_direction,
                        canary_writer_preview[
                            "entry_quantity"
                        ],
                        selected_snapshot,
                        r36f13_stop_price,
                    )
                )

                r36f14_demo_order_validation = (
                    validate_r36f14_demo_order_preview(
                        r36f14_demo_order_preview,
                        selected_direction,
                        canary_writer_preview[
                            "entry_price"
                        ],
                    )
                )

                for (
                    demo_check_name,
                    demo_check_result,
                ) in r36f14_demo_order_validation[
                    "checks"
                ].items():

                    if demo_check_name == "all_valid":
                        continue

                    diagnostic_check(
                        "R36F14_DEMO_ORDER_"
                        + demo_check_name.upper(),
                        demo_check_result,
                    )

                check(
                    "R36F14_DEMO_ORDER_INTEGRATION_GATE",
                    r36f14_demo_order_validation[
                        "all_valid"
                    ],
                )

                protected_canary_preview = (
                    build_protected_canary_preview(
                        canary_writer_preview,
                        r36f13_stop_price,
                        CANARY_ARM_REQUESTED,
                        production_journal,
                        len(
                            OPEN_POSITIONS
                        ) == 0,
                    )
                )

                diagnostic_check(
                    "R36F13_CANARY_QUANTITY_CAPPED",
                    protected_canary_preview[
                        "quantity_capped"
                    ],
                    "max=0.0004 BTC",
                )

                diagnostic_check(
                    "R36F13_DURABLE_JOURNAL_CLEAR",
                    protected_canary_preview[
                        "journal_clear"
                    ],
                )

                TELEGRAM_COMMAND_PREVIEW = (
                    apply_r36f13_stop_authorization_gate(
                        TELEGRAM_COMMAND_PREVIEW,
                        r36f13_stop_checks,
                    )
                )

                TELEGRAM_COMMAND_PREVIEW = (
                    apply_r36f131_risk_envelope_authorization_gate(
                        TELEGRAM_COMMAND_PREVIEW,
                        r36f131_stop_envelope,
                    )
                )

                TELEGRAM_COMMAND_PREVIEW = (
                    apply_r36f132_stop_loss_budget_authorization_gate(
                        TELEGRAM_COMMAND_PREVIEW,
                        r36f132_stop_loss_budget,
                    )
                )

                check(
                    "R36F132_LIVE_TRANSPORT_REMAINS_DISABLED",
                    (
                        EXCHANGE_MUTATION_TRANSPORT_ENABLED
                        is False

                        and

                        ORDER_SUBMISSION_ENABLED
                        is False

                        and

                        REAL_ORDER_EXECUTION
                        is False

                        and

                        FIRST_REAL_ORDER_ALLOWED
                        is False
                    ),
                )

    except Exception as exc:

        diagnostic_check(
            "ADJUSTABLE_TP_BALANCE_READINESS",
            False,
            str(
                exc
            ),
        )

        diagnostic_check(
            "WRITER_REQUEST_CONSTRUCTION",
            False,
            str(
                exc
            ),
        )

    zero_write_conditions = (

        REAL_ORDER_EXECUTION is False

        and

        DEMO_ORDER_EXECUTION is False

        and

        EXCHANGE_MUTATION_TRANSPORT_ENABLED
        is False

        and

        ORDER_SUBMISSION_ENABLED
        is False

        and

        LEVERAGE_MUTATION_ENABLED
        is False

        and

        MARGIN_MODE_MUTATION_ENABLED
        is False

        and

        POSITION_MUTATION_ENABLED
        is False

        and

        FIRST_REAL_ORDER_ALLOWED
        is False

        and

        R36F14_DEMO_POST_TRANSPORT_ENABLED
        is False

        and

        R36F14_DEMO_ORDER_SUBMISSION_ENABLED
        is False

        and

        R36F14_FIRST_DEMO_ORDER_ALLOWED
        is False
    )

    ZERO_WRITE_INVARIANT_OK = (
        zero_write_conditions
    )

    check(
        "ZERO_WRITE_INVARIANTS",
        ZERO_WRITE_INVARIANT_OK,
    )

    FINAL_GATE_OK = (
        len(
            FINAL_BLOCKERS
        ) == 0
    )

    TEST_STATUS = (
        "PASS"
        if FINAL_GATE_OK
        else
        "FAIL"
    )

    line()

    log(
        f"{STAGE} FINAL STATUS = "
        f"{TEST_STATUS}"
    )

    log(
        f"{STAGE} FINAL_BLOCKER_COUNT = "
        f"{len(FINAL_BLOCKERS)}"
    )

    for blocker in FINAL_BLOCKERS:

        log(
            f"{STAGE} FINAL_BLOCKER = "
            f"{blocker}"
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
        f"{STAGE} WRITER_CONSTRUCTION_ELIGIBLE = "
        f"{WRITER_CONSTRUCTION_ELIGIBLE}"
    )

    log(
        f"{STAGE} EMA_IDEAL_DIRECTION = "
        f"{EMA_SIGNAL_SNAPSHOT.get('ideal_direction')}"
    )

    log(
        f"{STAGE} EMA_STRUCTURE = "
        f"{EMA_SIGNAL_SNAPSHOT.get('structure')}"
    )

    log(
        f"{STAGE} TELEGRAM_COMMAND_AUTHORIZED_PREVIEW = "
        f"{TELEGRAM_COMMAND_PREVIEW.get('authorized_preview', False)}"
    )

    log(
        f"{STAGE} PROTECTIVE_STOP_PRICE = "
        f"{decimal_to_string(r36f13_stop_price) if r36f13_stop_price is not None else None}"
    )

    log(
        f"{STAGE} PROTECTIVE_STOP_VALID = "
        f"{bool(r36f13_stop_checks and r36f13_stop_checks.get('all_valid'))}"
    )

    log(
        f"{STAGE} PROTECTIVE_STOP_DISTANCE_PERCENT = "
        f"{r36f131_stop_envelope.get('distance_percent') if r36f131_stop_envelope else None}"
    )

    log(
        f"{STAGE} PROTECTIVE_STOP_RISK_ENVELOPE_VALID = "
        f"{bool(r36f131_stop_envelope and r36f131_stop_envelope.get('all_valid'))}"
    )

    log(
        f"{STAGE} PROTECTIVE_STOP_LOSS_BUDGET_VALID = "
        f"{bool(r36f132_stop_loss_budget and r36f132_stop_loss_budget.get('all_valid'))}"
    )

    if r36f132_stop_loss_budget:

        log(
            f"{STAGE} EXPECTED_STOP_LOSS_USDT = "
            f"{r36f132_stop_loss_budget.get('expected_loss_usdt')}"
        )

        log(
            f"{STAGE} EXPECTED_STOP_LOSS_PERCENT = "
            f"{r36f132_stop_loss_budget.get('expected_loss_percent_of_available_balance')}"
        )

        log(
            f"{STAGE} MAX_ACCOUNT_LOSS_PERCENT = "
            f"{r36f132_stop_loss_budget.get('configured_max_account_loss_percent')}"
        )

    log(
        f"{STAGE} STRICT_20_20_60_QUANTITY_FEASIBLE = "
        f"{bool(quantity_feasibility and quantity_feasibility.get('feasible'))}"
    )

    if quantity_feasibility:

        log(
            f"{STAGE} ADJUSTABLE_TP_MIN_ENTRY_QTY = "
            f"{quantity_feasibility.get('minimum_required_entry_quantity')}"
        )

    log(
        f"{STAGE} ADJUSTABLE_TP_BALANCE_READY = "
        f"{bool(balance_readiness and balance_readiness.get('eligible'))}"
    )

    if balance_readiness:

        log(
            f"{STAGE} TRADE_READINESS_STATUS = "
            f"{balance_readiness.get('status')}"
        )

        log(
            f"{STAGE} TRADE_READINESS_REASON = "
            f"{balance_readiness.get('reason')}"
        )

        log(
            f"{STAGE} REQUIRED_AVAILABLE_BALANCE = "
            f"{balance_readiness.get('required_available_balance')}"
        )

        log(
            f"{STAGE} AVAILABLE_BALANCE_SHORTFALL = "
            f"{balance_readiness.get('available_balance_shortfall')}"
        )

    snapshot = {

        "stage":
            STAGE,

        "purpose":
            PURPOSE,

        "timestamp":
            now_iso(),

        "test_status":
            TEST_STATUS,

        "final_gate_ok":
            FINAL_GATE_OK,

        "final_blockers":
            FINAL_BLOCKERS,

        "weex_read_only_ok":
            WEEX_READ_ONLY_OK,

        "durable_evidence_ok":
            DURABLE_EVIDENCE_OK,

        "r36a_evidence_ok":
            R36A_EVIDENCE_OK,

        "r36c_evidence_ok":
            R36C_EVIDENCE_OK,

        "r36d_evidence_ok":
            R36D_EVIDENCE_OK,

        "zero_write_invariant_ok":
            ZERO_WRITE_INVARIANT_OK,

        "mark_price":
            decimal_to_string(
                MARK_PRICE
            ),

        "available_balance":
            decimal_to_string(
                AVAILABLE_BALANCE
            ),

        "open_positions":
            OPEN_POSITIONS,

        "long_diagnostics":
            LONG_DIAGNOSTICS,

        "short_diagnostics":
            SHORT_DIAGNOSTICS,

        "tp_policy":
            {

                "required_valid_clusters":
                    REQUIRED_TP_CLUSTERS,

                "tp1_progress_percent":
                    decimal_to_string(
                        TP1_PROFIT_MARGIN_PERCENT
                    ),

                "tp2_progress_percent":
                    decimal_to_string(
                        TP2_PROFIT_MARGIN_PERCENT
                    ),

                "tp3_allocation_percent":
                    decimal_to_string(
                        TP3_ALLOCATION_PERCENT
                    ),

                "tp1_allocation_percent":
                    decimal_to_string(
                        TP1_ALLOCATION_PERCENT
                    ),

                "tp2_allocation_percent":
                    decimal_to_string(
                        TP2_ALLOCATION_PERCENT
                    ),

                "writer_quantity_policy":
                    {

                        "tp1_minimum":
                            decimal_to_string(
                                MIN_QUANTITY
                            ),

                        "tp2_minimum":
                            decimal_to_string(
                                MIN_QUANTITY
                            ),

                        "tp3_minimum":
                            decimal_to_string(
                                MIN_QUANTITY
                            ),

                        "strict_allocation":
                            "20/20/60",

                        "minimum_strict_entry_quantity":
                            decimal_to_string(
                                minimum_strict_tp_entry_quantity()
                            ),

                        "minimum_leg_promotion_allowed":
                            False,

                        "remainder_redistribution_allowed":
                            False,
                    },

                "cluster_tolerance_percent":
                    decimal_to_string(
                        CLUSTER_TOLERANCE_PERCENT
                    ),

                "minimum_cluster_touches":
                    MIN_CLUSTER_TOUCHES,
            },

        "synthetic_test_policy":
            {

                "long_requires_two_clusters":
                    True,

                "short_requires_two_clusters":
                    True,

                "one_cluster_must_reject":
                    True,

                "synthetic_fixtures_changed":
                    True,

                "production_tp_policy_changed":
                    False,
            },

        "market_eligibility":
            {

                "real_long_market_eligible":
                    REAL_LONG_MARKET_ELIGIBLE,

                "real_short_market_eligible":
                    REAL_SHORT_MARKET_ELIGIBLE,
            },

        "r36f12_ema_signal":
            EMA_SIGNAL_SNAPSHOT,

        "r36f12_telegram_command_preview":
            TELEGRAM_COMMAND_PREVIEW,

        "r36f12_telegram_policy":
            {

                "buy_command":
                    TELEGRAM_BUY_COMMAND,

                "sell_command":
                    TELEGRAM_SELL_COMMAND,

                "alerts_enabled":
                    R36F12_TELEGRAM_ALERTS_ENABLED,

                "command_can_execute_exchange_order":
                    False,

                "requires_ema_direction_agreement":
                    True,

                "requires_tp_market_eligibility":
                    True,
            },

        "canary_preview":
            canary_preview,

        "writer_preview":
            writer_preview,

        "r36f12_protected_canary_preview":
            protected_canary_preview,

        "r36f13_protective_stop":
            {

                "distance_percent":
                    decimal_to_string(
                        R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT
                    ),

                "price":
                    (
                        decimal_to_string(
                            r36f13_stop_price
                        )
                        if r36f13_stop_price is not None
                        else None
                    ),

                "checks":
                    r36f13_stop_checks,

                "mandatory_before_authorization":
                    True,

                "exchange_order_sent":
                    False,
            },

        "r36f131_stop_risk_envelope":
            {

                "configured_maximum_percent":
                    decimal_to_string(
                        R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT
                    ),

                "evaluation":
                    r36f131_stop_envelope,

                "mandatory_before_authorization":
                    True,

                "leverage_reference_is_not_liquidation_price":
                    True,

                "exchange_order_sent":
                    False,
            },

        "r36f132_stop_loss_budget":
            {

                "configured_max_account_loss_percent":
                    decimal_to_string(
                        R36F132_MAX_ACCOUNT_LOSS_PERCENT
                    ),

                "evaluation":
                    r36f132_stop_loss_budget,

                "mandatory_before_authorization":
                    True,

                "exchange_order_sent":
                    False,
            },

        "r36f12_canary_safety":
            {

                "max_entry_quantity":
                    decimal_to_string(
                        CANARY_MAX_ENTRY_QUANTITY
                    ),

                "stop_price_configured":
                    bool(
                        CANARY_STOP_PRICE_TEXT
                    ),

                "explicit_arm_requested":
                    CANARY_ARM_REQUESTED,

                "durable_journal_file":
                    R36F12_CANARY_JOURNAL_FILE,

                "durable_journal_unresolved":
                    unresolved_canary_journal(
                        read_json_file(
                            R36F12_CANARY_JOURNAL_FILE,
                            default={},
                        )
                    ),

                "r36f12_zero_write":
                    True,
            },

        "strict_tp_quantity_feasibility":
            quantity_feasibility,

        "strict_tp_balance_readiness":
            balance_readiness,

        "trade_readiness":
            {

                "status":
                    (
                        balance_readiness.get(
                            "status"
                        )
                        if balance_readiness
                        else "UNAVAILABLE"
                    ),

                "reason":
                    (
                        balance_readiness.get(
                            "reason"
                        )
                        if balance_readiness
                        else "READINESS_NOT_EVALUATED"
                    ),

                "eligible":
                    bool(
                        balance_readiness
                        and
                        balance_readiness.get(
                            "eligible"
                        )
                    ),
            },

        "writer_construction_eligible":
            WRITER_CONSTRUCTION_ELIGIBLE,

        "execution_firebreak":
            {

                "real_order_execution":
                    REAL_ORDER_EXECUTION,

                "demo_order_execution":
                    DEMO_ORDER_EXECUTION,

                "exchange_mutation_transport_enabled":
                    EXCHANGE_MUTATION_TRANSPORT_ENABLED,

                "order_submission_enabled":
                    ORDER_SUBMISSION_ENABLED,

                "leverage_mutation_enabled":
                    LEVERAGE_MUTATION_ENABLED,

                "margin_mode_mutation_enabled":
                    MARGIN_MODE_MUTATION_ENABLED,

                "position_mutation_enabled":
                    POSITION_MUTATION_ENABLED,

                "first_real_order_allowed":
                    FIRST_REAL_ORDER_ALLOWED,

                "demo_post_transport_enabled":
                    R36F14_DEMO_POST_TRANSPORT_ENABLED,

                "demo_order_submission_enabled":
                    R36F14_DEMO_ORDER_SUBMISSION_ENABLED,

                "first_demo_order_allowed":
                    R36F14_FIRST_DEMO_ORDER_ALLOWED,
            },

        "r36f14_weex_demo_integration":
            {

                "demo_symbol":
                    R36F14_DEMO_SYMBOL,

                "demo_asset":
                    R36F14_DEMO_ASSET,

                "balance_endpoint":
                    R36F14_DEMO_BALANCE_ENDPOINT,

                "positions_endpoint":
                    R36F14_DEMO_POSITIONS_ENDPOINT,

                "history_endpoint":
                    R36F14_DEMO_ORDER_HISTORY_ENDPOINT,

                "order_endpoint":
                    R36F14_DEMO_ORDER_ENDPOINT,

                "read_only_reconciliation":
                    r36f14_demo_account,

                "synthetic_integration":
                    r36f14_demo_integration,

                "real_market_demo_order_preview":
                    r36f14_demo_order_preview,

                "real_market_demo_order_validation":
                    r36f14_demo_order_validation,

                "demo_post_transport_enabled":
                    R36F14_DEMO_POST_TRANSPORT_ENABLED,

                "demo_order_submission_enabled":
                    R36F14_DEMO_ORDER_SUBMISSION_ENABLED,

                "first_demo_order_allowed":
                    R36F14_FIRST_DEMO_ORDER_ALLOWED,

                "actual_demo_order_sent":
                    False,

                "actual_real_order_sent":
                    False,
            },

        "writer_endpoints":
            {

                "entry":
                    WRITER_ENDPOINT_ENTRY,

                "tp1_tp2":
                    WRITER_ENDPOINT_TPSL,

                "tp3":
                    WRITER_ENDPOINT_TRAILING,
            },

        "writer_submission_policy":
            {

                "submitted":
                    False,

                "post_requests_sent":
                    False,

                "exchange_mutation_sent":
                    False,
            },
    }

    write_json_file(
        R36F_SNAPSHOT_FILE,
        snapshot,
    )

    write_json_file(
        R36F12_TELEGRAM_SIGNAL_FILE,
        EMA_SIGNAL_SNAPSHOT,
    )

    write_json_file(
        R36F12_TELEGRAM_COMMAND_FILE,
        TELEGRAM_COMMAND_PREVIEW,
    )

    log(
        f"{STAGE} SNAPSHOT WRITTEN = "
        f"{R36F_SNAPSHOT_FILE}"
    )

    line()

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO DEMO ORDER WAS SENT"
    )

    log(
        "NO EXCHANGE MUTATION WAS SENT"
    )

    line()

    return snapshot


# ============================================================
# HEARTBEAT
# ============================================================

async def heartbeat_loop():

    global HEARTBEAT_COUNT

    while True:

        HEARTBEAT_COUNT += 1

        log(
            f"HEARTBEAT "
            f"stage={STAGE} "
            f"status={TEST_STATUS} "
            f"count={HEARTBEAT_COUNT} "
            f"r36a_id={OLD_R36A_UPDATE_ID} "
            f"tp1_margin="
            f"{decimal_to_string(TP1_PROFIT_MARGIN_PERCENT)} "
            f"tp2_margin="
            f"{decimal_to_string(TP2_PROFIT_MARGIN_PERCENT)} "
            f"required_clusters="
            f"{REQUIRED_TP_CLUSTERS} "
            f"long_valid_clusters="
            f"{LONG_DIAGNOSTICS.get('valid_cluster_count')} "
            f"short_valid_clusters="
            f"{SHORT_DIAGNOSTICS.get('valid_cluster_count')} "
            f"write_transport="
            f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED} "
            f"real_execution="
            f"{REAL_ORDER_EXECUTION}"
        )

        await asyncio.sleep(
            60
        )


# ============================================================
# ASYNC MAIN
# ============================================================

async def async_main():

    global TEST_STATUS

    start_health_server()

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


# ============================================================
# MAIN
# ============================================================

def main():

    asyncio.run(
        async_main()
    )


if __name__ == "__main__":

    main()


