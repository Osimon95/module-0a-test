
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

STAGE = "R36F.13"

PURPOSE = (
    "PROTECTIVE STOP PRE-LIVE VALIDATION: preserve the complete R36F.12 "
    "EMA19/EMA50/EMA200 + Telegram + TP/readiness/writer baseline, calculate "
    "and validate a mandatory protective stop before authorization, require "
    "correct stop direction, WEEX price-step normalization, TP/entry separation, "
    "and keep ALL exchange mutation and real execution hard-disabled in R36F.13"
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

CANARY_MAX_ENTRY_QUANTITY = Decimal("0.0004")
CANARY_ARM_PHRASE = "ARM_FIRST_LIVE_CANARY"

CANARY_ARM_REQUESTED = (
    os.getenv("R36F12_LIVE_CANARY_ARM", "").strip() == CANARY_ARM_PHRASE
)

CANARY_STOP_PRICE_TEXT = os.getenv(
    "R36F12_CANARY_STOP_PRICE",
    "",
).strip()

CANARY_STOP_WORKING_TYPE = "MARK_PRICE"


# ============================================================
# R36F.13 PROTECTIVE STOP VALIDATION CONFIGURATION
# ============================================================

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


def D(
    value,
):
    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def decimal_to_string(
    value,
):
    value = D(
        value
    )

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    return text or "0"


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
            "step must be positive"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def is_on_step(
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
        return False

    return (
        value % step
    ) == 0


def percentage_of(
    value,
    percent,
):
    return (
        D(value)
        * D(percent)
        / Decimal("100")
    )


# ============================================================
# JSON HELPERS
# ============================================================

def read_json_file(
    path,
    default=None,
):
    if default is None:
        default = {}

    if not os.path.exists(
        path
    ):
        return default

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as handle:
            return json.load(
                handle
            )

    except Exception as exc:
        log(
            f"JSON READ FAILED path={path} error={exc}"
        )
        return default


def write_json_file(
    path,
    data,
):
    directory = os.path.dirname(
        path
    )

    if directory:
        os.makedirs(
            directory,
            exist_ok=True,
        )

    temp_path = (
        path
        + ".tmp"
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            data,
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_path,
        path,
    )


# ============================================================
# CHECK HELPERS
# ============================================================

def check(
    name,
    condition,
    detail=None,
):

    global FINAL_BLOCKERS

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


def diagnostic_check(
    name,
    condition,
    detail=None,
):

    if condition:

        log(
            f"DIAGNOSTIC PASS: {name}"
        )

    else:

        log(
            f"DIAGNOSTIC FAIL: {name}"
        )

    if detail:
        log(
            f"      {detail}"
        )

    return bool(
        condition
    )


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
            b"R36F.13 OK"
        )

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
                len(body)
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
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


# ============================================================
# HASH HELPERS
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


def sha256_json(
    data,
):

    return hashlib.sha256(
        canonical_json(
            data
        ).encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# DURABLE EVIDENCE
# ============================================================

def load_durable_evidence():

    global DURABLE_EVIDENCE_OK
    global R36A_EVIDENCE_OK
    global R36C_EVIDENCE_OK
    global R36D_EVIDENCE_OK

    r36a_dedupe = read_json_file(
        R36A_DEDUPE_FILE,
        default=[],
    )

    r36a_decisions = read_json_file(
        R36A_DECISION_FILE,
        default=[],
    )

    r36c_dedupe = read_json_file(
        R36C_DEDUPE_FILE,
        default=[],
    )

    r36c_decisions = read_json_file(
        R36C_DECISION_FILE,
        default=[],
    )

    r36d_snapshot = read_json_file(
        R36D_SNAPSHOT_FILE,
        default={},
    )

    R36A_EVIDENCE_OK = bool(
        r36a_dedupe
        and r36a_decisions
    )

    R36C_EVIDENCE_OK = bool(
        r36c_dedupe
        and r36c_decisions
    )

    R36D_EVIDENCE_OK = bool(
        r36d_snapshot
    )

    DURABLE_EVIDENCE_OK = bool(
        R36A_EVIDENCE_OK
        and R36C_EVIDENCE_OK
        and R36D_EVIDENCE_OK
    )

    return DURABLE_EVIDENCE_OK


# ============================================================
# WEEX AUTHENTICATION
# ============================================================

def get_weex_credentials():

    api_key = os.getenv(
        "WEEX_API_KEY",
        "",
    ).strip()

    api_secret = os.getenv(
        "WEEX_API_SECRET",
        "",
    ).strip()

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE",
        "",
    ).strip()

    return (
        api_key,
        api_secret,
        passphrase,
    )


def build_weex_signature(
    timestamp,
    method,
    request_path,
    query_string,
    body,
    api_secret,
):

    payload = (
        timestamp
        + method.upper()
        + request_path
    )

    if query_string:
        payload += (
            "?"
            + query_string
        )

    if body:
        payload += body

    digest = hmac.new(
        api_secret.encode(
            "utf-8"
        ),
        payload.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


# ============================================================
# QUERY STRING
# ============================================================

def build_query_string(
    params,
):

    if not params:
        return ""

    parts = []

    for key in sorted(
        params.keys()
    ):

        value = params[
            key
        ]

        parts.append(
            f"{key}={value}"
        )

    return "&".join(
        parts
    )


# ============================================================
# WEEX GET
# ============================================================

async def weex_get(
    path,
    params=None,
    authenticated=False,
):

    if params is None:
        params = {}

    query_string = build_query_string(
        params
    )

    url = (
        API_BASE_URL
        + path
    )

    if query_string:
        url += (
            "?"
            + query_string
        )

    headers = {}

    if authenticated:

        (
            api_key,
            api_secret,
            passphrase,
        ) = get_weex_credentials()

        if not (
            api_key
            and api_secret
            and passphrase
        ):

            raise RuntimeError(
                "WEEX credentials missing"
            )

        timestamp = str(
            int(
                time.time()
                * 1000
            )
        )

        signature = build_weex_signature(
            timestamp,
            "GET",
            path,
            query_string,
            "",
            api_secret,
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
                return json.loads(
                    text
                )

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

                collect(
                    item
                )

        elif isinstance(
            value,
            list,
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
                time.time()
                * 1000
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

        if len(
            rows
        ) < HISTORICAL_LIMIT:
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
    ) and len(
        row
    ) >= 3:

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
    ) and len(
        row
    ) >= 4:

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
        candle_high(
            row
        )
        for row in rows
    ]


def historical_lows(
    rows,
):

    return [
        candle_low(
            row
        )
        for row in rows
    ]


# ============================================================
# R36F.12 FROZEN EMA19 / EMA50 / EMA200 SIGNAL ENGINE
# ============================================================

def candle_close(
    row,
):

    if isinstance(
        row,
        dict,
    ):

        for key in (
            "close",
            "closePrice",
            "c",
            "lastPrice",
        ):

            if key in row:
                return D(
                    row[key]
                )

    if isinstance(
        row,
        list,
    ) and len(
        row
    ) >= 5:

        return D(
            row[4]
        )

    raise ValueError(
        "Unable to read candle close"
    )


def candle_timestamp(
    row,
):

    if isinstance(
        row,
        dict,
    ):

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

    if isinstance(
        row,
        list,
    ) and row:

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
            usable.append((ts, row))
        except Exception:
            continue
    if usable and all(item[0] is not None for item in usable):
        # Deduplicate timestamp overlaps across paginated historical requests.
        by_ts = {item[0]: item[1] for item in usable}
        return [by_ts[ts] for ts in sorted(by_ts)]
    return [item[1] for item in usable]


def ema_series(values, period):
    if len(values) < period:
        return None
    multiplier = Decimal("2") / Decimal(period + 1)
    ema = sum(values[:period]) / Decimal(period)
    for price in values[period:]:
        ema = (price - ema) * multiplier + ema
    return ema


def calculate_emas(closes):
    return (
        ema_series(closes, EMA_FAST),
        ema_series(closes, EMA_MID),
        ema_series(closes, EMA_SLOW),
    )


def ema_structure(ema19, ema50, ema200):
    if ema19 > ema50 > ema200:
        return "STRONG_BULLISH"
    if ema19 < ema50 < ema200:
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


def ema_separation_percent(price, ema19, ema50):
    if price <= 0:
        return Decimal("0")
    return abs(ema19 - ema50) / price * Decimal("100")


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
        previous19 <= previous50
        and current19 > current50
    ):
        return "LONG"

    if (
        previous19 >= previous50
        and current19 < current50
    ):
        return "SHORT"

    return None


def build_ema_signal_snapshot(rows):
    ordered = chronological_rows(rows)

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
            "reason":
                "INSUFFICIENT_CANDLES_FOR_EMA200_CONFIRMATION",
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

    separation = ema_separation_percent(
        current_price,
        current19,
        current50,
    )

    crossover = detect_ema19_50_crossover(
        previous19,
        previous50,
        current19,
        current50,
    )

    quality_ok = (
        separation
        >= MIN_EMA_19_50_SEPARATION_PERCENT
    )

    # Frozen semantics:
    # a fresh 19/50 crossover becomes a candidate;
    # ideal direction additionally requires the full
    # 19/50/200 stack and minimum separation.
    ideal_direction = (
        direction
        if quality_ok
        else None
    )

    return {
        "ready": True,
        "reason": "EMA_ENGINE_READY",
        "rows": len(closes),
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


def normalize_telegram_command(text):
    return " ".join(
        str(
            text or ""
        ).strip().upper().split()
    )


def parse_telegram_trade_command(text):
    normalized = normalize_telegram_command(
        text
    )

    if normalized == TELEGRAM_BUY_COMMAND:
        return {
            "recognized": True,
            "command": normalized,
            "direction": "LONG",
        }

    if normalized == TELEGRAM_SELL_COMMAND:
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
    parsed = parse_telegram_trade_command(
        text
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
            "reason":
                "UNRECOGNIZED_COMMAND",
        }

    if not ema_snapshot.get(
        "ready"
    ):
        return {
            **parsed,
            "authorized_preview": False,
            "reason":
                "EMA_ENGINE_NOT_READY",
        }

    ideal = ema_snapshot.get(
        "ideal_direction"
    )

    if ideal != direction:
        return {
            **parsed,
            "authorized_preview": False,
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
            "authorized_preview": False,
            "reason":
                "COMMAND_DIRECTION_TP_MARKET_NOT_ELIGIBLE",
            "ema_ideal_direction":
                ideal,
        }

    return {
        **parsed,
        "authorized_preview": True,
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
        f"R36F.13 IDEAL {direction} CONDITION | {SYMBOL}\n"
        f"Price={ema_snapshot.get('price')} "
        f"EMA19={ema_snapshot.get('ema19')} "
        f"EMA50={ema_snapshot.get('ema50')} "
        f"EMA200={ema_snapshot.get('ema200')}\n"
        f"Structure={ema_snapshot.get('structure')} "
        f"EMA19/50 separation="
        f"{ema_snapshot.get('ema19_50_separation_percent')}%\n"
        f"Manual command: {command}\n"
        "R36F.13 exchange execution remains disabled."
    )


async def send_r36f12_telegram_alert(
    message,
):
    if not message:
        return {
            "attempted": False,
            "sent": False,
            "reason":
                "NO_IDEAL_ALERT",
        }

    if not R36F12_TELEGRAM_ALERTS_ENABLED:
        return {
            "attempted": False,
            "sent": False,
            "reason":
                "ALERTS_DISABLED_BY_DEFAULT",
        }

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        return {
            "attempted": False,
            "sent": False,
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

                body = await response.text()

                return {
                    "attempted": True,
                    "sent":
                        200
                        <= response.status
                        < 300,
                    "http_status":
                        response.status,
                    "response_preview":
                        body[:200],
                }

    except Exception as exc:
        return {
            "attempted": True,
            "sent": False,
            "reason":
                f"{type(exc).__name__}: {exc}",
        }


def synthetic_r36f12_ema_telegram_tests():
    bullish = {
        "ready": True,
        "ideal_direction": "LONG",
        "structure": "STRONG_BULLISH",
        "price": "80000",
        "ema19": "80100",
        "ema50": "80000",
        "ema200": "79000",
        "ema19_50_separation_percent":
            "0.125",
    }

    bearish = {
        "ready": True,
        "ideal_direction": "SHORT",
        "structure": "STRONG_BEARISH",
        "price": "80000",
        "ema19": "79900",
        "ema50": "80000",
        "ema200": "81000",
        "ema19_50_separation_percent":
            "0.125",
    }

    buy = parse_telegram_trade_command(
        "  buy   btc now "
    )

    sell = parse_telegram_trade_command(
        "SELL BTC NOW"
    )

    check(
        "R36F12_TELEGRAM_BUY_COMMAND_PARSES_LONG",
        buy["recognized"]
        and buy["direction"] == "LONG",
    )

    check(
        "R36F12_TELEGRAM_SELL_COMMAND_PARSES_SHORT",
        sell["recognized"]
        and sell["direction"] == "SHORT",
    )

    check(
        "R36F12_TELEGRAM_UNKNOWN_COMMAND_REJECTED",
        parse_telegram_trade_command(
            "BUY ETH NOW"
        )["recognized"] is False,
    )

    buy_ok = validate_telegram_command_against_signal(
        "BUY BTC NOW",
        bullish,
        True,
        False,
    )

    sell_ok = validate_telegram_command_against_signal(
        "SELL BTC NOW",
        bearish,
        False,
        True,
    )

    mismatch = validate_telegram_command_against_signal(
        "SELL BTC NOW",
        bullish,
        True,
        True,
    )

    check(
        "R36F12_BUY_MATCHING_IDEAL_LONG_PREVIEW_APPROVED",
        buy_ok[
            "authorized_preview"
        ] is True,
    )

    check(
        "R36F12_SELL_MATCHING_IDEAL_SHORT_PREVIEW_APPROVED",
        sell_ok[
            "authorized_preview"
        ] is True,
    )

    check(
        "R36F12_DIRECTION_MISMATCH_BLOCKED",
        mismatch[
            "authorized_preview"
        ] is False,
    )

    check(
        "R36F12_COMMAND_PREVIEW_NEVER_SENDS_ORDER",
        buy_ok.get(
            "exchange_order_sent"
        ) is False,
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
            and current_value
            >= next_value
        ):
            extrema.append(
                current_value
            )

        elif (
            current_value
            <= previous_value
            and current_value
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
            D(value)
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
                len(current)
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
                        min(current),
                    "maximum":
                        max(current),
                    "average":
                        sum(current)
                        / Decimal(
                            len(current)
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
                sum(current)
                / Decimal(
                    len(current)
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

    if len(valid) >= REQUIRED_TP_CLUSTERS:
        diagnostics[
            "failure_reason"
        ] = None

    elif len(valid) == 1:
        diagnostics[
            "failure_reason"
        ] = "ONLY_ONE_VALID_CLUSTER"

    elif len(extrema) == 0:
        diagnostics[
            "failure_reason"
        ] = "NO_LOCAL_EXTREMA"

    elif len(clusters) == 0:
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

    for index, cluster in enumerate(
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

    for index, cluster in enumerate(
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

    if len(
        valid_cluster_list
    ) < REQUIRED_TP_CLUSTERS:
        raise RuntimeError(
            "Cannot calculate complete TP set: "
            "fewer than two valid historical clusters"
        )

    cluster1 = D(
        valid_cluster_list[0][
            "average"
        ]
    )

    cluster2 = D(
        valid_cluster_list[1][
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

    valid, invalid = validate_clusters(
        clusters,
        entry_price,
        direction,
    )

    approval = evaluate_tp_approval(
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

    diagnostics = build_cluster_diagnostics(
        rows,
        entry_price,
        side,
    )

    approval = evaluate_tp_approval(
        diagnostics
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
