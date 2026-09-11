
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


# ============================================================
# STAGE
# ============================================================

STAGE = "R36F.15.9-MERGED"

PURPOSE = (
    "SELECTED TP SNAPSHOT SCOPE FIX: preserve the complete R36F.15.1 continuous "
    "EMA19/EMA50/EMA200 + Telegram + two-cluster TP + quantity/readiness + mandatory "
    "protective-stop + stop-risk-envelope + stop-loss-budget + exactly-once WEEX demo dispatch chain, "
    "while fixing only the stale selected_tp_snapshot reference so the already-selected direction-specific "
    "TP snapshot reaches demo preview construction correctly. Production /capi/v3/order and every "
    "real-money mutation remain hard-disabled."
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

R36F151_REEVALUATION_SECONDS = max(
    15,
    int(os.getenv("R36F151_REEVALUATION_SECONDS", "60")),
)

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

R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED = (
    os.getenv("R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED", "false").strip().lower()
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
# R36F.15 ACTUAL WEEX DEMO EXECUTION CONFIGURATION
# ============================================================

R36F159_DEMO_ARM_PHRASE = "ARM_SECOND_WEEX_DEMO_ORDER"
R36F159_DEMO_ARM_REQUESTED = (
    os.getenv("R36F159_DEMO_ARM", "").strip() == R36F159_DEMO_ARM_PHRASE
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
# R36F.15 DEMO-ONLY WEEX POST TRANSPORT
# ============================================================

async def weex_demo_post(path, payload):

    if path != R36F14_DEMO_ORDER_ENDPOINT:
        raise RuntimeError("R36F.15 demo transport refused non-demo endpoint")

    if not (
        R36F15_DEMO_POST_TRANSPORT_ENABLED
        and R36F15_DEMO_ORDER_SUBMISSION_ENABLED
        and R36F15_FIRST_DEMO_ORDER_ALLOWED
    ):
        raise RuntimeError("R36F.15 demo transport is disabled")

    if not (
        REAL_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MODE_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
        and FIRST_REAL_ORDER_ALLOWED is False
    ):
        raise RuntimeError("R36F.15 production firebreak is not intact")

    api_key = os.getenv("WEEX_API_KEY")
    passphrase = os.getenv("WEEX_API_PASSPHRASE")

    if not api_key:
        raise RuntimeError("WEEX_API_KEY missing")

    if not passphrase:
        raise RuntimeError("WEEX_API_PASSPHRASE missing")

    body = canonical_json(payload)
    timestamp = str(int(time.time() * 1000))
    signature = build_signature(timestamp, "POST", path, body)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    timeout = aiohttp.ClientTimeout(total=20)
    url = API_BASE_URL + path

    async with aiohttp.ClientSession(timeout=timeout) as session:

        async with session.post(
            url,
            headers=headers,
            data=body,
        ) as response:

            text = await response.text()

            try:
                data = json.loads(text)

            except Exception:
                data = {"raw": text}

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


def r36f15_demo_journal_unresolved(journal):

    if not isinstance(journal, dict) or not journal:
        return False

    return journal.get("state") in {"PREPARED", "SENT_AMBIGUOUS"}


def r36f15_demo_journal_completed(journal):

    return bool(
        isinstance(journal, dict)
        and journal.get("state") == "COMPLETED"
        and journal.get("success") is True
    )


def _r36f153_history_rows(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in ("data", "list", "rows", "orders"):

            value = data.get(key)

            if isinstance(value, list):
                return value

    return None


async def r36f153_lookup_demo_order_by_client_id(client_order_id):

    client_order_id = str(client_order_id or "").strip()

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

    rows = _r36f153_history_rows(data)

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

    state = str(journal.get("state") or "").strip().upper()

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

    if state not in {"PREPARED", "SENT_AMBIGUOUS"}:

        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "UNKNOWN_JOURNAL_STATE_BLOCKS_RETRY",
            "journal": journal,
            "changed": False,
        }

    client_order_id = str(journal.get("client_order_id") or "").strip()

    if not client_order_id:

        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "MISSING_CLIENT_ID_BLOCKS_RETRY",
            "journal": journal,
            "changed": False,
        }

    lookup = await r36f153_lookup_demo_order_by_client_id(client_order_id)
    lookup_status = lookup.get("status")

    if lookup_status == "FOUND":

        order = lookup.get("order") if isinstance(lookup.get("order"), dict) else {}

        reconciled = {
            **journal,
            "state": "COMPLETED",
            "updated_at": now_iso(),
            "success": True,
            "reconciliation_status": "FOUND",
            "reconciliation_reason": lookup.get("reason"),
            "order_id": str(order.get("orderId", journal.get("order_id", ""))),
            "client_order_id_response": str(
                order.get("clientOrderId", client_order_id)
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
        "reason": lookup.get("reason", "AMBIGUOUS_UNKNOWN_BLOCKS_RETRY"),
        "journal": journal,
        "lookup": lookup,
        "changed": False,
    }


async def r36f154_validate_fresh_demo_triggers(payload):

    payload = payload if isinstance(payload, dict) else {}

    direction = str(
        payload.get("positionSide") or ""
    ).strip().upper()

    try:
        tp = D(payload.get("tpTriggerPrice", "0"))
        sl = D(payload.get("slTriggerPrice", "0"))

    except Exception as exc:

        return {
            "valid": False,
            "reason": "JIT_TRIGGER_PARSE_FAILED",
            "error": str(exc),
        }

    if direction not in {"LONG", "SHORT"}:

        return {
            "valid": False,
            "reason": "JIT_DIRECTION_INVALID",
            "direction": direction,
        }

    try:
        fresh_mark = D(await load_mark_price())

    except Exception as exc:

        return {
            "valid": False,
            "reason": "JIT_FRESH_MARK_READ_FAILED",
            "error": str(exc),
        }

    if fresh_mark <= 0 or tp <= 0 or sl <= 0:

        return {
            "valid": False,
            "reason": "JIT_NON_POSITIVE_PRICE",
            "direction": direction,
            "fresh_mark_price": decimal_to_string(fresh_mark),
            "tp_trigger_price": decimal_to_string(tp),
            "sl_trigger_price": decimal_to_string(sl),
        }

    if direction == "LONG":

        valid = sl < fresh_mark < tp

        reason = (
            "JIT_LONG_TRIGGERS_VALID"
            if valid
            else "JIT_LONG_TRIGGER_STALE_OR_CROSSED"
        )

    else:

        valid = tp < fresh_mark < sl

        reason = (
            "JIT_SHORT_TRIGGERS_VALID"
            if valid
            else "JIT_SHORT_TRIGGER_STALE_OR_CROSSED"
        )

    return {
        "valid": bool(valid),
        "reason": reason,
        "direction": direction,
        "fresh_mark_price": decimal_to_string(fresh_mark),
        "tp_trigger_price": decimal_to_string(tp),
        "sl_trigger_price": decimal_to_string(sl),
    }


# ============================================================
# R36F.15.5 POST-ORDER RECONCILIATION MERGER
# ============================================================

R36F155_TARGET_DEMO_ORDER_ID = os.getenv(
    "R36F155_TARGET_DEMO_ORDER_ID",
    "792989056504955607",
).strip()

R36F155_LAST_RECONCILIATION = {}


def r36f155_order_id(row):

    if not isinstance(row, dict):
        return ""

    for key in ("orderId", "order_id", "id"):

        value = row.get(key)

        if value is not None:
            return str(value).strip()

    return ""


def r36f155_order_status(row):

    if not isinstance(row, dict):
        return "UNKNOWN"

    for key in ("status", "orderStatus", "state"):

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

    if position_side in {"LONG", "SHORT"}:
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

    for key in ("positionSide", "side"):

        value = str(
            row.get(key) or ""
        ).strip().upper()

        if value in {"LONG", "SHORT"}:
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

                nested = value.get(nested_key)

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

    log("R36F.15.5 POST-ORDER RECONCILIATION START")
    log("R36F.15.5 TARGET DEMO ORDER ID = " + R36F155_TARGET_DEMO_ORDER_ID)

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
        result["history_count"] = len(history_rows)

        log("R36F.15.5 DEMO ORDER HISTORY READ = PASS")
        log("R36F.15.5 DEMO ORDER HISTORY ROWS = " + str(len(history_rows)))

    except Exception as exc:

        result["history_error"] = str(exc)
        result["duplicate_entry_block_reason"] = "ORDER_HISTORY_READ_FAILED_FAIL_CLOSED"
        result["duplicate_block_reason"] = "ORDER_HISTORY_READ_FAILED_FAIL_CLOSED"

        log("R36F.15.5 DEMO ORDER HISTORY READ = FAIL")
        log("R36F.15.5 DEMO ORDER HISTORY ERROR = " + str(exc))

        R36F155_LAST_RECONCILIATION = result

        line()

        return result

    target_order = None

    for row in history_rows:

        if (
            isinstance(row, dict)
            and
            r36f155_order_id(row) == R36F155_TARGET_DEMO_ORDER_ID
        ):
            target_order = row
            break

    if target_order is not None:

        result["target_order_found"] = True
        result["target_order_status"] = r36f155_order_status(target_order)
        result["target_order_direction"] = r36f155_order_direction(target_order)

        result["target_order_symbol"] = str(
            target_order.get("symbol") or ""
        ).strip().upper()

        result["target_order_qty"] = target_order.get("origQty")
        result["target_order_executed_qty"] = target_order.get("executedQty")
        result["target_order_avg_price"] = target_order.get("avgPrice")
        result["target_order_client_id"] = target_order.get("clientOrderId")

        result.update(
            r36f155_extract_protection_fields(
                target_order
            )
        )

        if (
            result.get("tp_field") is not None
            or
            result.get("sl_field") is not None
        ):

            result["protection_reason"] = (
                "PROTECTION_FIELDS_RETURNED_IN_ORDER_HISTORY"
            )

        else:

            result["protection_reason"] = (
                "TP_SL_NOT_RETURNED_BY_DEMO_ORDER_HISTORY"
            )

        log("R36F.15.5 TARGET ORDER FOUND = True")
        log("R36F.15.5 ORDER ID = " + r36f155_order_id(target_order))
        log("R36F.15.5 ORDER SYMBOL = " + result["target_order_symbol"])
        log("R36F.15.5 ORDER DIRECTION = " + result["target_order_direction"])
        log("R36F.15.5 ORDER STATUS = " + result["target_order_status"])
        log("R36F.15.5 ORDER ORIGINAL QTY = " + str(result.get("target_order_qty")))
        log("R36F.15.5 ORDER EXECUTED QTY = " + str(result.get("target_order_executed_qty")))
        log("R36F.15.5 ORDER AVG PRICE = " + str(result.get("target_order_avg_price")))

    else:

        log("R36F.15.5 TARGET ORDER FOUND = False")

    try:

        position_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            authenticated=True,
        )

        position_rows = r36f155_normalize_rows(
            position_data
        )

        result["position_read_success"] = True
        result["position_count"] = len(position_rows)

        log("R36F.15.5 DEMO POSITION READ = PASS")
        log("R36F.15.5 DEMO POSITION ROWS = " + str(len(position_rows)))

    except Exception as exc:

        result["position_error"] = str(exc)
        result["duplicate_block_reason"] = "POSITION_READ_FAILED_FAIL_CLOSED"

        log("R36F.15.5 DEMO POSITION READ = FAIL")
        log("R36F.15.5 DEMO POSITION ERROR = " + str(exc))

        R36F155_LAST_RECONCILIATION = result

        line()

        return result

    expected_symbol = (
        result.get("target_order_symbol")
        or
        R36F14_DEMO_SYMBOL
    )

    expected_direction = (
        result.get("target_order_direction")
        or
        ""
    )

    matching = []

    for row in position_rows:

        if not isinstance(row, dict):
            continue

        symbol = str(
            row.get("symbol") or ""
        ).strip().upper()

        direction = r36f155_position_direction(row)

        size = r36f155_position_size(row)

        if size <= 0:
            continue

        if expected_symbol and symbol != expected_symbol:
            continue

        if (
            expected_direction
            and
            direction
            and
            direction != expected_direction
        ):
            continue

        matching.append(row)

    result["matching_position_found"] = bool(matching)
    result["matching_position_count"] = len(matching)

    log("R36F.15.5 MATCHING POSITION FOUND = " + str(bool(matching)))
    log("R36F.15.5 MATCHING POSITION COUNT = " + str(len(matching)))

    if matching:

        result["duplicate_entry_blocked"] = True
        result["duplicate_block_reason"] = "POSITION_ALREADY_EXISTS"
        result["safe_to_consider_new_entry"] = False

    elif result["target_order_found"]:

        status = result["target_order_status"]

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
            result["duplicate_block_reason"] = "OPEN_ENTRY_ORDER_ALREADY_EXISTS"

        elif status == "FILLED":

            result["duplicate_entry_blocked"] = True
            result["duplicate_block_reason"] = (
                "FILLED_ORDER_FOUND_POSITION_REQUIRES_CONSERVATIVE_RECONCILIATION"
            )

        elif status == "UNKNOWN":

            result["duplicate_entry_blocked"] = True
            result["duplicate_block_reason"] = "UNKNOWN_ORDER_STATUS_FAIL_CLOSED"

        else:

            result["duplicate_entry_blocked"] = False
            result["duplicate_block_reason"] = (
                "TARGET_ORDER_TERMINAL_AND_NO_MATCHING_POSITION_FOUND"
            )
            result["safe_to_consider_new_entry"] = True

    else:

        active_demo_position = any(
            isinstance(row, dict)
            and
            str(row.get("symbol") or "").strip().upper() == R36F14_DEMO_SYMBOL
            and
            r36f155_position_size(row) > 0
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
        + str(result["duplicate_entry_blocked"])
    )

    log(
        "R36F.15.5 DUPLICATE BLOCK REASON = "
        + str(result["duplicate_block_reason"])
    )

    log(
        "R36F.15.5 SAFE TO CONSIDER NEW ENTRY = "
        + str(result["safe_to_consider_new_entry"])
    )

    log("R36F.15.5 PROTECTION VERIFIED = False")
    log("R36F.15.5 PROTECTION REASON = " + str(result["protection_reason"]))
    log("R36F.15.5 REAL MONEY EXECUTION = " + str(REAL_ORDER_EXECUTION))
    log("R36F.15.5 POST-ORDER RECONCILIATION COMPLETE")

    R36F155_LAST_RECONCILIATION = result

    line()

    return result


# ============================================================
# R36F.15.9 SECOND-DEMO PREFLIGHT / ANTI-REPLAY MERGER
# ============================================================

R36F159_LAST_EXPOSURE_CHECK = {}


def r36f159_command_identity(command_preview):

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
        canonical_json(
            material
        )
    )


def r36f159_client_order_id(command_preview):

    direction = str(
        command_preview.get("direction") or ""
    ).strip().upper()

    prefix = (
        "L"
        if direction == "LONG"
        else
        "S"
        if direction == "SHORT"
        else
        "X"
    )

    digest = (
        r36f159_command_identity(
            command_preview
        )[:16].upper()
    )

    value = f"R36F159-{prefix}-{digest}"

    if len(value) > 36:
        raise ValueError(
            "R36F.15.9 client id exceeds WEEX limit"
        )

    return value


def r36f159_is_open_order_status(status):

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
        result["history_rows"] = len(history_rows)

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
                or
                row.get("newClientOrderId")
                or
                ""
            ).strip()

            if client_id:
                client_ids.append(client_id)

            status = str(
                row.get("status") or ""
            ).strip().upper()

            if r36f159_is_open_order_status(status):
                open_orders += 1

            if status == "FILLED":
                filled_orders += 1

        result["existing_client_ids"] = sorted(
            set(client_ids)
        )

        result["open_symbol_orders"] = open_orders
        result["historical_filled_orders"] = filled_orders

    except Exception as exc:

        result["history_error"] = str(exc)

    try:

        positions_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            authenticated=True,
        )

        position_rows = r36f155_normalize_rows(
            positions_data
        )

        result["position_read_ok"] = True
        result["position_rows"] = len(position_rows)

        active_positions = 0

        for row in position_rows:

            if not isinstance(row, dict):
                continue

            symbol = str(
                row.get("symbol") or ""
            ).strip().upper()

            if symbol and symbol != R36F14_DEMO_SYMBOL:
                continue

            if r36f155_position_size(row) != 0:
                active_positions += 1

        result["active_symbol_positions"] = active_positions

    except Exception as exc:

        result["position_error"] = str(exc)

    if (
        not result["history_read_ok"]
        or
        not result["position_read_ok"]
    ):

        result["duplicate_entry_blocked"] = True
        result["duplicate_block_reason"] = (
            "CURRENT_EXPOSURE_READ_FAILED"
        )

    elif result["active_symbol_positions"] > 0:

        result["duplicate_entry_blocked"] = True
        result["duplicate_block_reason"] = (
            "ACTIVE_DEMO_POSITION_ALREADY_EXISTS"
        )

    elif result["open_symbol_orders"] > 0:

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
        "R36F.15.9 HISTORICAL FILLED ORDERS = "
        + str(result["historical_filled_orders"])
    )

    log(
        "R36F.15.9 OPEN DEMO ORDERS = "
        + str(result["open_symbol_orders"])
    )

    log(
        "R36F.15.9 ACTIVE DEMO POSITIONS = "
        + str(result["active_symbol_positions"])
    )

    log(
        "R36F.15.9 DUPLICATE ENTRY BLOCKED = "
        + str(result["duplicate_entry_blocked"])
    )

    log(
        "R36F.15.9 DUPLICATE BLOCK REASON = "
        + str(result["duplicate_block_reason"])
    )

    log(
        "R36F.15.9 SAFE TO CONSIDER NEW ENTRY = "
        + str(result["safe_to_consider_new_entry"])
    )

    R36F159_LAST_EXPOSURE_CHECK = result

    line()

    return result


async def r36f159_reconcile_second_demo_journal(journal):

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


