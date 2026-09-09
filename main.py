
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

STAGE = "R36F.15.2"

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

# R36F.15.1 runtime correction: rerun the complete fresh read/evaluation
# pipeline periodically instead of reporting startup-cached market state.
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
# R36F.15 ACTUAL WEEX DEMO EXECUTION CONFIGURATION
# ============================================================

R36F15_DEMO_ARM_PHRASE = "ARM_FIRST_WEEX_DEMO_ORDER"
R36F15_DEMO_ARM_REQUESTED = (
    os.getenv("R36F15_DEMO_ARM", "").strip() == R36F15_DEMO_ARM_PHRASE
)

# This is the ONLY exchange mutation transport enabled in R36F.15.
# It is restricted in code to the exact /capi/v3/sim/order endpoint.
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
# R36F.15 DEMO-ONLY WEEX POST TRANSPORT
# ============================================================

async def weex_demo_post(path, payload):
    """
    Send one authenticated JSON POST only to WEEX's paper-trading order endpoint.

    Production order/mutation paths remain unreachable because this function rejects
    every path except R36F14_DEMO_ORDER_ENDPOINT and independently requires the
    production execution firebreak to remain fully disabled.
    """

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
        async with session.post(url, headers=headers, data=body) as response:
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


async def submit_r36f15_demo_order(preview, command_preview):
    """Exactly-once, durably journaled first WEEX demo order."""

    if not R36F15_DEMO_ARM_REQUESTED:
        return {"attempted": False, "sent": False, "reason": "DEMO_ARM_NOT_REQUESTED"}

    if not command_preview.get("authorized_preview"):
        return {"attempted": False, "sent": False, "reason": "TELEGRAM_COMMAND_NOT_AUTHORIZED"}

    if not preview or not preview.get("payload"):
        return {"attempted": False, "sent": False, "reason": "DEMO_PREVIEW_MISSING"}

    existing = read_json_file(R36F15_DEMO_JOURNAL_FILE, default={})
    if r36f15_demo_journal_unresolved(existing):
        return {
            "attempted": False,
            "sent": False,
            "reason": "UNRESOLVED_DEMO_JOURNAL_BLOCKS_RETRY",
            "journal": existing,
        }
    if r36f15_demo_journal_completed(existing):
        return {
            "attempted": False,
            "sent": False,
            "reason": "FIRST_DEMO_ORDER_ALREADY_COMPLETED",
            "journal": existing,
        }

    payload = dict(preview["payload"])
    payload_hash = sha256_text(canonical_json(payload))
    prepared = {
        "stage": STAGE,
        "state": "PREPARED",
        "created_at": now_iso(),
        "endpoint": R36F14_DEMO_ORDER_ENDPOINT,
        "client_order_id": payload.get("newClientOrderId"),
        "payload_sha256": payload_hash,
        "payload": payload,
        "real_order_execution": REAL_ORDER_EXECUTION,
    }
    write_json_file(R36F15_DEMO_JOURNAL_FILE, prepared)

    try:
        transport = await weex_demo_post(R36F14_DEMO_ORDER_ENDPOINT, payload)
    except Exception as exc:
        ambiguous = {
            **prepared,
            "state": "SENT_AMBIGUOUS",
            "updated_at": now_iso(),
            "error": str(exc),
        }
        write_json_file(R36F15_DEMO_JOURNAL_FILE, ambiguous)
        raise

    response = transport.get("response") if isinstance(transport, dict) else {}
    response = response if isinstance(response, dict) else {}
    success = bool(response.get("success"))

    completed = {
        **prepared,
        "state": "COMPLETED" if success else "REJECTED",
        "updated_at": now_iso(),
        "http_status": transport.get("http_status"),
        "response": response,
        "success": success,
        "order_id": str(response.get("orderId", "")),
        "client_order_id_response": str(response.get("clientOrderId", "")),
        "error_code": str(response.get("errorCode", "")),
        "error_message": str(response.get("errorMessage", "")),
    }
    write_json_file(R36F15_DEMO_JOURNAL_FILE, completed)

    return {
        "attempted": True,
        "sent": True,
        "accepted": success,
        "transport": transport,
        "journal": completed,
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
        for key in ("timestamp", "ts", "time", "startTime", "openTime"):
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

### R36F.15.2 — Part 2 of 4


def build_ideal_condition_alert(
    ema_snapshot,
    long_eligible,
    short_eligible,
):

    if not ema_snapshot.get(
        "ready"
    ):

        return {
            "alert":
                False,

            "reason":
                "EMA_ENGINE_NOT_READY",
        }

    direction = ema_snapshot.get(
        "ideal_direction"
    )

    if direction == "LONG":

        market_ok = long_eligible

        command = TELEGRAM_BUY_COMMAND

    elif direction == "SHORT":

        market_ok = short_eligible

        command = TELEGRAM_SELL_COMMAND

    else:

        return {
            "alert":
                False,

            "reason":
                "NO_IDEAL_EMA_DIRECTION",
        }

    if not market_ok:

        return {
            "alert":
                False,

            "reason":
                "IDEAL_EMA_DIRECTION_NOT_TP_MARKET_ELIGIBLE",

            "direction":
                direction,
        }

    return {

        "alert":
            True,

        "reason":
            "IDEAL_EMA_AND_TP_MARKET_CONDITION",

        "direction":
            direction,

        "command":
            command,

        "message":
            (
                f"{STAGE} IDEAL {direction} CONDITION\n"
                f"EMA19={ema_snapshot.get('ema19')}\n"
                f"EMA50={ema_snapshot.get('ema50')}\n"
                f"EMA200={ema_snapshot.get('ema200')}\n"
                f"COMMAND={command}"
            ),
    }


async def send_r36f12_telegram_alert(
    alert,
):

    if not alert.get(
        "alert"
    ):

        return {
            "attempted":
                False,

            "sent":
                False,

            "reason":
                alert.get(
                    "reason"
                ),
        }

    if not R36F12_TELEGRAM_ALERTS_ENABLED:

        return {
            "attempted":
                False,

            "sent":
                False,

            "reason":
                "TELEGRAM_ALERTS_DISABLED",

            "preview_message":
                alert.get(
                    "message"
                ),
        }

    if not TELEGRAM_BOT_TOKEN:

        return {
            "attempted":
                False,

            "sent":
                False,

            "reason":
                "TELEGRAM_BOT_TOKEN_MISSING",
        }

    if not TELEGRAM_CHAT_ID:

        return {
            "attempted":
                False,

            "sent":
                False,

            "reason":
                "TELEGRAM_CHAT_ID_MISSING",
        }

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            alert.get(
                "message",
                "",
            ),
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    try:

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.post(
                url,
                json=payload,
            ) as response:

                text = await response.text()

                try:

                    data = json.loads(
                        text
                    )

                except Exception:

                    data = {
                        "raw":
                            text
                    }

                return {
                    "attempted":
                        True,

                    "sent":
                        (
                            response.status < 400
                            and
                            bool(
                                data.get(
                                    "ok"
                                )
                                if isinstance(
                                    data,
                                    dict,
                                )
                                else False
                            )
                        ),

                    "http_status":
                        response.status,

                    "response":
                        data,
                }

    except Exception as exc:

        return {
            "attempted":
                True,

            "sent":
                False,

            "reason":
                "TELEGRAM_SEND_EXCEPTION",

            "error":
                str(
                    exc
                ),
        }


# ============================================================
# LOCAL EXTREMA
# ============================================================

def local_extrema(
    values,
    mode,
):

    output = []

    if len(
        values
    ) < 3:

        return output

    for index in range(
        1,
        len(values) - 1,
    ):

        previous_value = values[
            index - 1
        ]

        current_value = values[
            index
        ]

        next_value = values[
            index + 1
        ]

        if mode == "HIGH":

            if (
                current_value >= previous_value
                and
                current_value >= next_value
            ):

                output.append(
                    current_value
                )

        elif mode == "LOW":

            if (
                current_value <= previous_value
                and
                current_value <= next_value
            ):

                output.append(
                    current_value
                )

        else:

            raise ValueError(
                "mode must be HIGH or LOW"
            )

    return output


# ============================================================
# CLUSTER ENGINE
# ============================================================

def build_clusters(
    values,
):

    if not values:

        return []

    ordered = sorted(
        [
            D(
                value
            )
            for value in values
        ]
    )

    clusters = []

    current = [
        ordered[0]
    ]

    for value in ordered[
        1:
    ]:

        current_average = (
            sum(
                current
            )
            / D(
                len(
                    current
                )
            )
        )

        distance_percent = (
            abs(
                value
                - current_average
            )
            / current_average
            * Decimal("100")
        )

        if (
            distance_percent
            <= CLUSTER_TOLERANCE_PERCENT
        ):

            current.append(
                value
            )

        else:

            clusters.append(
                current
            )

            current = [
                value
            ]

    clusters.append(
        current
    )

    output = []

    for cluster in clusters:

        average = (
            sum(
                cluster
            )
            / D(
                len(
                    cluster
                )
            )
        )

        output.append(
            {
                "average":
                    average,

                "minimum":
                    min(
                        cluster
                    ),

                "maximum":
                    max(
                        cluster
                    ),

                "touches":
                    len(
                        cluster
                    ),
            }
        )

    return output


# ============================================================
# DIRECTIONAL CLUSTER VALIDATION
# ============================================================

def validate_clusters(
    clusters,
    entry_price,
    direction,
):

    valid = []

    rejected = []

    entry_price = D(
        entry_price
    )

    for cluster in clusters:

        reasons = []

        if (
            cluster[
                "touches"
            ]
            < MIN_CLUSTER_TOUCHES
        ):

            reasons.append(
                "INSUFFICIENT_TOUCHES"
            )

        average = cluster[
            "average"
        ]

        if direction == "LONG":

            if average <= entry_price:

                reasons.append(
                    "CLUSTER_NOT_ABOVE_ENTRY"
                )

        elif direction == "SHORT":

            if average >= entry_price:

                reasons.append(
                    "CLUSTER_NOT_BELOW_ENTRY"
                )

        else:

            raise ValueError(
                "direction must be LONG or SHORT"
            )

        if reasons:

            rejected.append(
                {
                    **cluster,

                    "reasons":
                        reasons,
                }
            )

        else:

            valid.append(
                cluster
            )

    if direction == "LONG":

        valid = sorted(
            valid,
            key=lambda item: item[
                "average"
            ],
        )

    else:

        valid = sorted(
            valid,
            key=lambda item: item[
                "average"
            ],
            reverse=True,
        )

    return (
        valid,
        rejected,
    )


# ============================================================
# TP APPROVAL
# ============================================================

def approve_tp_clusters(
    valid_clusters,
):

    available = len(
        valid_clusters
    )

    if available >= REQUIRED_TP_CLUSTERS:

        return {
            "approved":
                True,

            "status":
                "APPROVED",

            "reason":
                "ENOUGH_VALID_CLUSTERS",

            "required_clusters":
                REQUIRED_TP_CLUSTERS,

            "available_clusters":
                available,

            "selected_clusters":
                valid_clusters[
                    :REQUIRED_TP_CLUSTERS
                ],
        }

    if available == 1:

        reason = (
            "ONLY_ONE_VALID_CLUSTER"
        )

    else:

        reason = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    return {
        "approved":
            False,

        "status":
            "REJECTED",

        "reason":
            reason,

        "required_clusters":
            REQUIRED_TP_CLUSTERS,

        "available_clusters":
            available,

        "selected_clusters":
            [],
    }


# ============================================================
# TP PRICE ENGINE
# ============================================================

def build_tp_prices(
    entry_price,
    direction,
    approval,
):

    if not approval.get(
        "approved"
    ):

        return None

    entry_price = D(
        entry_price
    )

    clusters = approval[
        "selected_clusters"
    ]

    cluster_1 = D(
        clusters[
            0
        ][
            "average"
        ]
    )

    cluster_2 = D(
        clusters[
            1
        ][
            "average"
        ]
    )

    if direction == "LONG":

        tp1 = (
            entry_price
            +
            (
                cluster_1
                - entry_price
            )
            *
            (
                TP1_PROFIT_MARGIN_PERCENT
                / Decimal("100")
            )
        )

        tp2 = (
            entry_price
            +
            (
                cluster_2
                - entry_price
            )
            *
            (
                TP2_PROFIT_MARGIN_PERCENT
                / Decimal("100")
            )
        )

    elif direction == "SHORT":

        tp1 = (
            entry_price
            -
            (
                entry_price
                - cluster_1
            )
            *
            (
                TP1_PROFIT_MARGIN_PERCENT
                / Decimal("100")
            )
        )

        tp2 = (
            entry_price
            -
            (
                entry_price
                - cluster_2
            )
            *
            (
                TP2_PROFIT_MARGIN_PERCENT
                / Decimal("100")
            )
        )

    else:

        raise ValueError(
            "direction must be LONG or SHORT"
        )

    return {
        "entry":
            quantize_down(
                entry_price,
                PRICE_STEP,
            ),

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

        "tp3":
            {
                "allocation_percent":
                    TP3_ALLOCATION_PERCENT,

                "trailing_distance_percent":
                    TP3_TRAILING_DISTANCE_PERCENT,

                "runner":
                    True,
            },

        "cluster_1_average":
            cluster_1,

        "cluster_2_average":
            cluster_2,

        "direction":
            direction,
    }


# ============================================================
# DIRECTION ANALYSIS
# ============================================================

def analyze_direction(
    rows,
    entry_price,
    direction,
):

    if direction == "LONG":

        values = historical_highs(
            rows
        )

        extrema = local_extrema(
            values,
            "HIGH",
        )

    else:

        values = historical_lows(
            rows
        )

        extrema = local_extrema(
            values,
            "LOW",
        )

    clusters = build_clusters(
        extrema
    )

    (
        valid_clusters,
        rejected_clusters,
    ) = validate_clusters(
        clusters,
        entry_price,
        direction,
    )

    approval = approve_tp_clusters(
        valid_clusters
    )

    tp_prices = build_tp_prices(
        entry_price,
        direction,
        approval,
    )

    return {

        "direction":
            direction,

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
                valid_clusters
            ),

        "clusters":
            clusters,

        "valid_clusters":
            valid_clusters,

        "rejected_clusters":
            rejected_clusters,

        "approval":
            approval,

        "tp_prices":
            tp_prices,
    }


# ============================================================
# DIRECTION DIAGNOSTIC LOGGING
# ============================================================

def log_direction_diagnostics(
    diagnostics,
):

    direction = diagnostics[
        "direction"
    ]

    log(
        f"{direction} EXTREMA = "
        + str(
            diagnostics[
                "extrema_count"
            ]
        )
    )

    log(
        f"{direction} CLUSTERS = "
        + str(
            diagnostics[
                "cluster_count"
            ]
        )
    )

    log(
        f"{direction} VALID CLUSTERS = "
        + str(
            diagnostics[
                "valid_cluster_count"
            ]
        )
    )

    for (
        index,
        cluster,
    ) in enumerate(
        diagnostics[
            "valid_clusters"
        ],
        start=1,
    ):

        log(
            f"{direction} VALID CLUSTER {index}: "
            f"AVG={decimal_to_string(cluster['average'])} "
            f"MIN={decimal_to_string(cluster['minimum'])} "
            f"MAX={decimal_to_string(cluster['maximum'])} "
            f"TOUCHES={cluster['touches']}"
        )

    for (
        index,
        cluster,
    ) in enumerate(
        diagnostics[
            "rejected_clusters"
        ],
        start=1,
    ):

        log(
            f"{direction} INVALID CLUSTER {index}: "
            f"average={decimal_to_string(cluster['average'])} "
            f"reasons={','.join(cluster['reasons'])}"
        )

    approval = diagnostics[
        "approval"
    ]

    log(
        f"{direction} CLUSTER DIAGNOSTIC FAILURE_REASON = "
        + (
            "NONE"
            if approval[
                "approved"
            ]
            else approval[
                "reason"
            ]
        )
    )

    log(
        f"{STAGE}_TP_APPROVAL = "
        + approval[
            "status"
        ]
    )

    log(
        f"{STAGE}_TP_APPROVAL_REASON = "
        + approval[
            "reason"
        ]
    )

    log(
        f"{STAGE}_TP_REQUIRED_CLUSTERS = "
        + str(
            approval[
                "required_clusters"
            ]
        )
    )

    log(
        f"{STAGE}_TP_AVAILABLE_CLUSTERS = "
        + str(
            approval[
                "available_clusters"
            ]
        )
    )

    if diagnostics[
        "tp_prices"
    ]:

        tp = diagnostics[
            "tp_prices"
        ]

        log(
            f"{direction} TP1 = "
            + decimal_to_string(
                tp[
                    "tp1"
                ]
            )
        )

        log(
            f"{direction} TP2 = "
            + decimal_to_string(
                tp[
                    "tp2"
                ]
            )
        )

        log(
            f"{direction} TP3 = 60% TRAILING RUNNER"
        )


# ============================================================
# TP QUANTITY ALLOCATION
# ============================================================

def allocate_tp_quantities(
    entry_quantity,
):

    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP,
    )

    tp1_quantity = quantize_down(
        (
            entry_quantity
            *
            TP1_ALLOCATION_PERCENT
            / Decimal("100")
        ),
        QUANTITY_STEP,
    )

    tp2_quantity = quantize_down(
        (
            entry_quantity
            *
            TP2_ALLOCATION_PERCENT
            / Decimal("100")
        ),
        QUANTITY_STEP,
    )

    tp3_quantity = quantize_down(
        (
            entry_quantity
            *
            TP3_ALLOCATION_PERCENT
            / Decimal("100")
        ),
        QUANTITY_STEP,
    )

    return {
        "entry_quantity":
            entry_quantity,

        "tp1_quantity":
            tp1_quantity,

        "tp2_quantity":
            tp2_quantity,

        "tp3_quantity":
            tp3_quantity,

        "total_allocated":
            (
                tp1_quantity
                +
                tp2_quantity
                +
                tp3_quantity
            ),
    }


# ============================================================
# ADJUSTABLE TP QUANTITY REPRESENTABILITY
# ============================================================

def quantity_allocation_exact(
    entry_quantity,
):

    allocation = allocate_tp_quantities(
        entry_quantity
    )

    return (
        allocation[
            "total_allocated"
        ]
        == allocation[
            "entry_quantity"
        ]
        and
        allocation[
            "tp1_quantity"
        ] >= MIN_QUANTITY
        and
        allocation[
            "tp2_quantity"
        ] >= MIN_QUANTITY
        and
        allocation[
            "tp3_quantity"
        ] >= MIN_QUANTITY
    )


def discover_minimum_exact_entry_quantity():

    quantity = MIN_QUANTITY

    for _ in range(
        100000
    ):

        if quantity_allocation_exact(
            quantity
        ):

            return quantity

        quantity += QUANTITY_STEP

    raise RuntimeError(
        "Unable to determine minimum exact TP entry quantity"
    )


# ============================================================
# ENTRY QUANTITY
# ============================================================

def calculate_entry_quantity(
    available_balance,
    price,
    leverage,
):

    available_balance = D(
        available_balance
    )

    price = D(
        price
    )

    leverage = D(
        leverage
    )

    margin = (
        available_balance
        *
        ENTRY_MARGIN_PERCENT
        / Decimal("100")
    )

    notional = (
        margin
        *
        leverage
    )

    raw_quantity = (
        notional
        / price
    )

    quantity = quantize_down(
        raw_quantity,
        QUANTITY_STEP,
    )

    return {
        "available_balance":
            available_balance,

        "margin":
            margin,

        "notional":
            notional,

        "raw_quantity":
            raw_quantity,

        "quantity":
            quantity,
    }


# ============================================================
# STRICT WRITER QUANTITY TEST
# ============================================================

def strict_quantity_feasibility(
    entry_quantity,
):

    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP,
    )

    allocation = allocate_tp_quantities(
        entry_quantity
    )

    minimum_entry_quantity = (
        discover_minimum_exact_entry_quantity()
    )

    feasible = (
        entry_quantity
        >= minimum_entry_quantity
        and
        quantity_allocation_exact(
            entry_quantity
        )
    )

    return {
        **allocation,

        "minimum_entry_quantity":
            minimum_entry_quantity,

        "feasible":
            feasible,

        "reason":
            (
                "STRICT_20_20_60_QUANTITY_FEASIBLE"
                if feasible
                else "POSITION_TOO_SMALL_OR_NOT_EXACTLY_REPRESENTABLE_FOR_20_20_60"
            ),
    }


# ============================================================
# BALANCE READINESS
# ============================================================

def strict_balance_readiness(
    available_balance,
    price,
    direction,
):

    leverage = (
        LEVERAGE_LONG
        if direction == "LONG"
        else LEVERAGE_SHORT
    )

    entry = calculate_entry_quantity(
        available_balance,
        price,
        leverage,
    )

    minimum_quantity = (
        discover_minimum_exact_entry_quantity()
    )

    required_notional = (
        minimum_quantity
        *
        D(
            price
        )
    )

    required_margin = (
        required_notional
        /
        leverage
    )

    required_available_balance = (
        required_margin
        /
        (
            ENTRY_MARGIN_PERCENT
            /
            Decimal("100")
        )
    )

    shortfall = max(
        Decimal("0"),
        required_available_balance
        - D(
            available_balance
        ),
    )

    quantity_feasible = (
        quantity_allocation_exact(
            entry[
                "quantity"
            ]
        )
        and
        entry[
            "quantity"
        ]
        >= minimum_quantity
    )

    eligible = (
        D(
            available_balance
        )
        >= required_available_balance
        and
        quantity_feasible
    )

    return {

        "direction":
            direction,

        "available_usdt":
            D(
                available_balance
            ),

        "planned_entry_qty":
            entry[
                "quantity"
            ],

        "minimum_strict_tp_entry_qty":
            minimum_quantity,

        "required_margin_usdt":
            required_margin,

        "required_available_usdt":
            required_available_balance,

        "available_balance_shortfall":
            shortfall,

        "quantity_feasible":
            quantity_feasible,

        "trade_readiness_status":
            (
                "ELIGIBLE"
                if eligible
                else "TRADE_NOT_ELIGIBLE"
            ),

        "reason":
            (
                "BALANCE_AND_QUANTITY_READY"
                if eligible
                else "INSUFFICIENT_BALANCE_FOR_STRICT_20_20_60"
            ),
    }


# ============================================================
# WRITER REQUEST CONSTRUCTION
# ============================================================

def build_writer_request(
    direction,
    quantity,
    tp_snapshot,
):

    if not tp_snapshot:

        raise ValueError(
            "TP snapshot missing"
        )

    direction = str(
        direction
    ).upper()

    if direction not in (
        "LONG",
        "SHORT",
    ):

        raise ValueError(
            "Invalid direction"
        )

    quantity = quantize_down(
        quantity,
        QUANTITY_STEP,
    )

    tp_quantities = allocate_tp_quantities(
        quantity
    )

    return {

        "symbol":
            SYMBOL,

        "direction":
            direction,

        "side":
            (
                "BUY"
                if direction == "LONG"
                else "SELL"
            ),

        "margin_mode":
            MARGIN_MODE,

        "leverage":
            decimal_to_string(
                LEVERAGE_LONG
                if direction == "LONG"
                else LEVERAGE_SHORT
            ),

        "entry_quantity":
            decimal_to_string(
                quantity
            ),

        "tp1_quantity":
            decimal_to_string(
                tp_quantities[
                    "tp1_quantity"
                ]
            ),

        "tp2_quantity":
            decimal_to_string(
                tp_quantities[
                    "tp2_quantity"
                ]
            ),

        "tp3_quantity":
            decimal_to_string(
                tp_quantities[
                    "tp3_quantity"
                ]
            ),

        "tp1_price":
            decimal_to_string(
                tp_snapshot[
                    "tp1"
                ]
            ),

        "tp2_price":
            decimal_to_string(
                tp_snapshot[
                    "tp2"
                ]
            ),

        "tp3":
            {
                "runner":
                    True,

                "allocation_percent":
                    decimal_to_string(
                        TP3_ALLOCATION_PERCENT
                    ),

                "trailing_distance_percent":
                    decimal_to_string(
                        TP3_TRAILING_DISTANCE_PERCENT
                    ),
            },

        "submitted":
            False,
    }


# ============================================================
# R36F.12 FIRST-LIVE CANARY PREVIEW
# ============================================================

def build_first_live_canary_preview(
    direction,
    quantity,
    entry_price,
    tp_snapshot,
):

    writer_request = build_writer_request(
        direction,
        quantity,
        tp_snapshot,
    )

    quantity = D(
        writer_request[
            "entry_quantity"
        ]
    )

    if quantity > CANARY_MAX_ENTRY_QUANTITY:

        quantity = CANARY_MAX_ENTRY_QUANTITY

    quantity = quantize_down(
        quantity,
        QUANTITY_STEP,
    )

    allocation = allocate_tp_quantities(
        quantity
    )

    return {
        "stage":
            STAGE,

        "direction":
            direction,

        "symbol":
            SYMBOL,

        "entry_price":
            quantize_down(
                entry_price,
                PRICE_STEP,
            ),

        "entry_quantity":
            quantity,

        "tp1_quantity":
            allocation[
                "tp1_quantity"
            ],

        "tp2_quantity":
            allocation[
                "tp2_quantity"
            ],

        "tp3_quantity":
            allocation[
                "tp3_quantity"
            ],

        "tp1_price":
            tp_snapshot[
                "tp1"
            ],

        "tp2_price":
            tp_snapshot[
                "tp2"
            ],

        "tp3_runner":
            True,

        "tp3_trailing_distance_percent":
            TP3_TRAILING_DISTANCE_PERCENT,

        "canary_quantity_cap":
            CANARY_MAX_ENTRY_QUANTITY,

        "arm_requested":
            CANARY_ARM_REQUESTED,

        "stop_price_text":
            CANARY_STOP_PRICE_TEXT,

        "stop_working_type":
            CANARY_STOP_WORKING_TYPE,

        "production_order_sent":
            False,

        "submitted":
            False,
    }


# ============================================================
# R36F.13 PROTECTIVE-STOP PRICE ENGINE
# ============================================================

def calculate_r36f13_protective_stop_price(
    direction,
    entry_price,
    distance_percent=None,
):

    direction = str(
        direction
    ).upper()

    entry_price = D(
        entry_price
    )

    if distance_percent is None:

        distance_percent = (
            R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT
        )

    distance_percent = D(
        distance_percent
    )

    if entry_price <= 0:

        raise ValueError(
            "Entry price must be positive"
        )

    if distance_percent <= 0:

        raise ValueError(
            "Protective stop distance must be positive"
        )

    distance = (
        distance_percent
        / Decimal("100")
    )

    if direction == "LONG":

        raw_stop_price = (
            entry_price
            *
            (
                Decimal("1")
                - distance
            )
        )

    elif direction == "SHORT":

        raw_stop_price = (
            entry_price
            *
            (
                Decimal("1")
                + distance
            )
        )

    else:

        raise ValueError(
            "direction must be LONG or SHORT"
        )

    stop_price = quantize_down(
        raw_stop_price,
        PRICE_STEP,
    )

    return stop_price


def validate_r36f13_protective_stop(
    direction,
    entry_price,
    stop_price,
    tp_snapshot,
):

    direction = str(
        direction
    ).upper()

    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    checks = {}

    checks[
        "stop_present"
    ] = (
        stop_price > 0
    )

    checks[
        "stop_price_step_normalized"
    ] = (
        stop_price
        ==
        quantize_down(
            stop_price,
            PRICE_STEP,
        )
    )

    if direction == "LONG":

        checks[
            "stop_correct_side_of_entry"
        ] = (
            stop_price < entry_price
        )

        checks[
            "stop_separate_from_tp1"
        ] = (
            tp_snapshot is not None
            and
            stop_price
            < D(
                tp_snapshot[
                    "tp1"
                ]
            )
        )

        checks[
            "stop_separate_from_tp2"
        ] = (
            tp_snapshot is not None
            and
            stop_price
            < D(
                tp_snapshot[
                    "tp2"
                ]
            )
        )

    elif direction == "SHORT":

        checks[
            "stop_correct_side_of_entry"
        ] = (
            stop_price > entry_price
        )

        checks[
            "stop_separate_from_tp1"
        ] = (
            tp_snapshot is not None
            and
            stop_price
            > D(
                tp_snapshot[
                    "tp1"
                ]
            )
        )

        checks[
            "stop_separate_from_tp2"
        ] = (
            tp_snapshot is not None
            and
            stop_price
            > D(
                tp_snapshot[
                    "tp2"
                ]
            )
        )

    else:

        checks[
            "stop_correct_side_of_entry"
        ] = False

        checks[
            "stop_separate_from_tp1"
        ] = False

        checks[
            "stop_separate_from_tp2"
        ] = False

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


def apply_r36f13_stop_authorization_gate(
    command_preview,
    stop_checks,
):

    updated = dict(
        command_preview
    )

    previously_authorized = bool(
        updated.get(
            "authorized_preview"
        )
    )

    stop_ok = bool(
        stop_checks.get(
            "all_valid"
        )
    )

    updated[
        "r36f13_protective_stop_gate"
    ] = stop_ok

    updated[
        "authorized_preview"
    ] = (
        previously_authorized
        and stop_ok
    )

    if (
        previously_authorized
        and not stop_ok
    ):

        updated[
            "reason"
        ] = (
            "PROTECTIVE_STOP_VALIDATION_FAILED"
        )

    return updated


# ============================================================
# R36F.13.1 STOP-DISTANCE RISK ENVELOPE
# ============================================================

def calculate_stop_distance_percent(
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
            "Entry price must be positive"
        )

    return (
        abs(
            entry_price
            - stop_price
        )
        / entry_price
        * Decimal("100")
    )


def validate_r36f131_stop_risk_envelope(
    direction,
    entry_price,
    stop_price,
):

    direction = str(
        direction
    ).upper()

    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    distance_percent = (
        calculate_stop_distance_percent(
            entry_price,
            stop_price,
        )
    )

    maximum_percent = (
        R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT
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
            > Decimal("0"),

        "distance_within_maximum":
            distance_percent
            <= maximum_percent,
    }

    if direction == "LONG":

        checks[
            "stop_correct_side"
        ] = (
            stop_price < entry_price
        )

    elif direction == "SHORT":

        checks[
            "stop_correct_side"
        ] = (
            stop_price > entry_price
        )

    else:

        checks[
            "stop_correct_side"
        ] = False

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return {
        **checks,

        "direction":
            direction,

        "entry_price":
            entry_price,

        "stop_price":
            stop_price,

        "distance_percent":
            distance_percent,

        "maximum_allowed_percent":
            maximum_percent,
    }


def apply_r36f131_risk_envelope_authorization_gate(
    command_preview,
    envelope,
):

    updated = dict(
        command_preview
    )

    previously_authorized = bool(
        updated.get(
            "authorized_preview"
        )
    )

    envelope_ok = bool(
        envelope.get(
            "all_valid"
        )
    )

    updated[
        "r36f131_stop_risk_envelope_gate"
    ] = envelope_ok

    updated[
        "authorized_preview"
    ] = (
        previously_authorized
        and envelope_ok
    )

    if (
        previously_authorized
        and not envelope_ok
    ):

        updated[
            "reason"
        ] = (
            "PROTECTIVE_STOP_RISK_ENVELOPE_FAILED"
        )

    return updated


# ============================================================
# R36F.13.2 STOP-LOSS ACCOUNT BUDGET
# ============================================================

def calculate_r36f132_stop_loss_budget(
    available_balance,
    direction,
    entry_price,
    stop_price,
    entry_quantity,
):

    available_balance = D(
        available_balance
    )

    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    entry_quantity = D(
        entry_quantity
    )

    direction = str(
        direction
    ).upper()

    absolute_stop_distance = abs(
        entry_price
        - stop_price
    )

    estimated_loss_usdt = (
        absolute_stop_distance
        *
        entry_quantity
    )

    maximum_loss_usdt = (
        available_balance
        *
        R36F132_MAX_ACCOUNT_LOSS_PERCENT
        / Decimal("100")
    )

    checks = {

        "balance_positive":
            available_balance
            > Decimal("0"),

        "entry_quantity_positive":
            entry_quantity
            > Decimal("0"),

        "stop_distance_positive":
            absolute_stop_distance
            > Decimal("0"),

        "estimated_loss_within_budget":
            estimated_loss_usdt
            <= maximum_loss_usdt,
    }

    if direction == "LONG":

        checks[
            "stop_correct_side"
        ] = (
            stop_price < entry_price
        )

    elif direction == "SHORT":

        checks[
            "stop_correct_side"
        ] = (
            stop_price > entry_price
        )

    else:

        checks[
            "stop_correct_side"
        ] = False

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return {
        **checks,

        "direction":
            direction,

        "available_balance":
            available_balance,

        "entry_price":
            entry_price,

        "stop_price":
            stop_price,

        "entry_quantity":
            entry_quantity,

        "absolute_stop_distance":
            absolute_stop_distance,

        "estimated_loss_usdt":
            estimated_loss_usdt,

        "maximum_account_loss_percent":
            R36F132_MAX_ACCOUNT_LOSS_PERCENT,

        "maximum_loss_usdt":
            maximum_loss_usdt,
    }


def apply_r36f132_stop_loss_budget_authorization_gate(
    command_preview,
    stop_loss_budget,
):

    updated = dict(
        command_preview
    )

    previously_authorized = bool(
        updated.get(
            "authorized_preview"
        )
    )

    budget_ok = bool(
        stop_loss_budget.get(
            "all_valid"
        )
    )

    updated[
        "r36f132_stop_loss_budget_gate"
    ] = budget_ok

    updated[
        "authorized_preview"
    ] = (
        previously_authorized
        and budget_ok
    )

    if (
        previously_authorized
        and not budget_ok
    ):

        updated[
            "reason"
        ] = (
            "PROTECTIVE_STOP_LOSS_BUDGET_FAILED"
        )

    return updated


# ============================================================
# R36F.13 PROTECTED FIRST-LIVE CANARY PREVIEW
# ============================================================

def build_protected_canary_preview(
    canary_preview,
    stop_price,
    arm_requested,
    journal,
    account_flat,
):

    preview = dict(
        canary_preview
    )

    quantity = D(
        preview.get(
            "entry_quantity",
            "0",
        )
    )

    quantity_capped = (
        quantity
        <= CANARY_MAX_ENTRY_QUANTITY
    )

    journal_clear = (
        not r36f15_demo_journal_unresolved(
            journal
        )
        and
        not r36f15_demo_journal_completed(
            journal
        )
    )

    preview.update(
        {

            "protective_stop_price":
                stop_price,

            "protective_stop_working_type":
                CANARY_STOP_WORKING_TYPE,

            "quantity_capped":
                quantity_capped,

            "journal_clear":
                journal_clear,

            "account_flat":
                bool(
                    account_flat
                ),

            "arm_requested":
                bool(
                    arm_requested
                ),

            "production_order_sent":
                False,

            "submitted":
                False,
        }
    )

    return preview


# ============================================================
# R36F.14 WEEX DEMO READS
# ============================================================

async def load_r36f14_demo_balance():

    data = await weex_get(
        R36F14_DEMO_BALANCE_ENDPOINT,
        params={
            "coin":
                R36F14_DEMO_ASSET
        },
        authenticated=True,
    )

    log(
        "R36F.14 DEMO BALANCE READ = "
        + canonical_json(
            data
        )
    )

    return data


async def load_r36f14_demo_positions():

    data = await weex_get(
        R36F14_DEMO_POSITIONS_ENDPOINT,
        authenticated=True,
    )

    log(
        "R36F.14 DEMO POSITIONS READ = "
        + canonical_json(
            data
        )
    )

    return data


async def load_r36f14_demo_order_history():

    data = await weex_get(
        R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
        params={
            "symbol":
                R36F14_DEMO_SYMBOL
        },
        authenticated=True,
    )

    log(
        "R36F.14 DEMO ORDER HISTORY READ = "
        + canonical_json(
            data
        )
    )

    return data


# ============================================================
# R36F.14 DEMO ORDER PREVIEW
# ============================================================

def build_r36f14_demo_order_preview(
    direction,
    quantity,
    tp_snapshot,
    stop_price,
):

    direction = str(
        direction
    ).upper()

    quantity = quantize_down(
        quantity,
        QUANTITY_STEP,
    )

    stop_price = quantize_down(
        stop_price,
        PRICE_STEP,
    )

    if direction == "LONG":

        side = "BUY"

    elif direction == "SHORT":

        side = "SELL"

    else:

        raise ValueError(
            "direction must be LONG or SHORT"
        )

    client_order_id = (
        "R36F14_"
        + direction
        + "_"
        + str(
            int(
                time.time()
            )
        )
    )

    payload = {

        "symbol":
            R36F14_DEMO_SYMBOL,

        "side":
            side,

        "orderType":
            "MARKET",

        "quantity":
            decimal_to_string(
                quantity
            ),

        "newClientOrderId":
            client_order_id,

        "stopLossPrice":
            decimal_to_string(
                stop_price
            ),

        "stopLossWorkingType":
            CANARY_STOP_WORKING_TYPE,
    }

    return {

        "stage":
            STAGE,

        "endpoint":
            R36F14_DEMO_ORDER_ENDPOINT,

        "method":
            "POST",

        "direction":
            direction,

        "payload":
            payload,

        "tp_snapshot":
            tp_snapshot,

        "transport_enabled":
            R36F15_DEMO_POST_TRANSPORT_ENABLED,

        "submission_enabled":
            R36F15_DEMO_ORDER_SUBMISSION_ENABLED,

        "first_demo_order_allowed":
            R36F15_FIRST_DEMO_ORDER_ALLOWED,

        "submitted":
            False,
    }


def validate_r36f14_demo_order_preview(
    preview,
    direction,
    entry_price,
):

    direction = str(
        direction
    ).upper()

    entry_price = D(
        entry_price
    )

    payload = preview.get(
        "payload",
        {}
    )

    quantity = D(
        payload.get(
            "quantity",
            "0",
        )
    )

    stop_price = D(
        payload.get(
            "stopLossPrice",
            "0",
        )
    )

    checks = {

        "endpoint_exact":
            preview.get(
                "endpoint"
            )
            == R36F14_DEMO_ORDER_ENDPOINT,

        "method_post":
            preview.get(
                "method"
            )
            == "POST",

        "demo_symbol_exact":
            payload.get(
                "symbol"
            )
            == R36F14_DEMO_SYMBOL,

        "market_order":
            payload.get(
                "orderType"
            )
            == "MARKET",

        "quantity_positive":
            quantity > 0,

        "quantity_step_normalized":
            quantity
            ==
            quantize_down(
                quantity,
                QUANTITY_STEP,
            ),

        "stop_present":
            stop_price > 0,

        "stop_price_step_normalized":
            stop_price
            ==
            quantize_down(
                stop_price,
                PRICE_STEP,
            ),

        "client_order_id_present":
            bool(
                payload.get(
                    "newClientOrderId"
                )
            ),

        "production_transport_disabled":
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,

        "production_order_submission_disabled":
            ORDER_SUBMISSION_ENABLED
            is False,

        "first_real_order_forbidden":
            FIRST_REAL_ORDER_ALLOWED
            is False,
    }

    if direction == "LONG":

        checks[
            "side_correct"
        ] = (
            payload.get(
                "side"
            )
            == "BUY"
        )

        checks[
            "stop_correct_side"
        ] = (
            stop_price
            < entry_price
        )

    elif direction == "SHORT":

        checks[
            "side_correct"
        ] = (
            payload.get(
                "side"
            )
            == "SELL"
        )

        checks[
            "stop_correct_side"
        ] = (
            stop_price
            > entry_price
        )

    else:

        checks[
            "side_correct"
        ] = False

        checks[
            "stop_correct_side"
        ] = False

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


# ============================================================
# BACKUP ORDER SNAPSHOT
# ============================================================

def build_backup_snapshot(
    direction,
    primary_entry,
    backup_entry,
    rows,
):

    primary_entry = D(
        primary_entry
    )

    backup_entry = D(
        backup_entry
    )

    primary = analyze_direction(
        rows,
        primary_entry,
        direction,
    )

    backup = analyze_direction(
        rows,
        backup_entry,
        direction,
    )

    return {

        "direction":
            direction,

        "primary_entry":
            primary_entry,

        "backup_entry":
            backup_entry,

        "primary_tp_locked":
            primary[
                "tp_prices"
            ],

        "backup_tp_recalculated":
            backup[
                "tp_prices"
            ],
    }


# ============================================================
# STRATEGY QUANTITY PREVIEW
# ============================================================

def strategy_quantity_preview(
    available_balance,
    mark_price,
    direction,
):

    leverage = (
        LEVERAGE_LONG
        if direction == "LONG"
        else LEVERAGE_SHORT
    )

    return calculate_entry_quantity(
        available_balance,
        mark_price,
        leverage,
    )


# ============================================================
# EXPOSURE CHECK
# ============================================================

def exposure_within_limit(
    current_exposure_percent,
    additional_percent,
):

    total = (
        D(
            current_exposure_percent
        )
        +
        D(
            additional_percent
        )
    )

    return (
        total
        <= MAX_FUND_EXPOSURE_PERCENT
    )


# ============================================================
# IMMUTABLE PRIMARY TP SNAPSHOT
# ============================================================

def freeze_primary_tp_snapshot(
    direction,
    entry_price,
    tp_prices,
):

    if not tp_prices:

        return None

    return {

        "direction":
            direction,

        "entry_price":
            D(
                entry_price
            ),

        "tp1":
            D(
                tp_prices[
                    "tp1"
                ]
            ),

        "tp2":
            D(
                tp_prices[
                    "tp2"
                ]
            ),

        "tp3":
            dict(
                tp_prices[
                    "tp3"
                ]
            ),

        "immutable":
            True,

        "created_at":
            now_iso(),
    }


# ============================================================
# BACKUP TP RECALCULATION
# ============================================================

def recalculate_backup_tp_snapshot(
    direction,
    backup_entry,
    rows,
):

    diagnostics = analyze_direction(
        rows,
        backup_entry,
        direction,
    )

    if not diagnostics[
        "approval"
    ][
        "approved"
    ]:

        return {

            "approved":
                False,

            "reason":
                diagnostics[
                    "approval"
                ][
                    "reason"
                ],

            "tp_snapshot":
                None,
        }

    return {

        "approved":
            True,

        "reason":
            "BACKUP_TP_RECALCULATED_ON_BACKUP_FILL",

        "tp_snapshot":
            freeze_primary_tp_snapshot(
                direction,
                backup_entry,
                diagnostics[
                    "tp_prices"
                ],
            ),
    }


# ============================================================
# R36F.11 STRICT BALANCE READINESS GATE
# ============================================================

def minimum_adjustable_tp_entry_quantity():

    return discover_minimum_exact_entry_quantity()


def minimum_strict_tp_entry_quantity():

    return minimum_adjustable_tp_entry_quantity()

### R36F.15.2 — Part 3 of 4


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

    balance_rows = balance_rows if isinstance(balance_rows, list) else []
    position_rows = position_rows if isinstance(position_rows, list) else []
    history_rows = history_rows if isinstance(history_rows, list) else []

    demo_asset_row = None
    for row in balance_rows:
        if str(row.get("asset", "")).upper() == R36F14_DEMO_ASSET:
            demo_asset_row = row
            break

    demo_positions = [
        row for row in position_rows
        if str(row.get("symbol", "")).upper() == R36F14_DEMO_SYMBOL
        and D(row.get("size", "0")) != 0
    ]

    return {
        "balance_endpoint": R36F14_DEMO_BALANCE_ENDPOINT,
        "positions_endpoint": R36F14_DEMO_POSITIONS_ENDPOINT,
        "history_endpoint": R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
        "demo_symbol": R36F14_DEMO_SYMBOL,
        "demo_asset": R36F14_DEMO_ASSET,
        "asset_present": demo_asset_row is not None,
        "balance": (
            str(demo_asset_row.get("balance"))
            if demo_asset_row else None
        ),
        "available_balance": (
            str(demo_asset_row.get("availableBalance"))
            if demo_asset_row else None
        ),
        "open_demo_position_count": len(demo_positions),
        "history_count": len(history_rows),
        "all_reads_successful": demo_asset_row is not None,
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

    if not tp_snapshot or not tp_snapshot.get("tp_approval", {}).get("approved"):
        raise ValueError("demo writer requires approved complete TP snapshot")

    direction = str(direction).upper()
    entry_quantity = quantize_down(D(entry_quantity), QUANTITY_STEP)
    stop_price = quantize_down(D(protective_stop_price), PRICE_STEP)
    tp1_price = quantize_down(D(tp_snapshot["tp1"]), PRICE_STEP)

    if direction == "LONG":
        side = "BUY"
        position_side = "LONG"
    elif direction == "SHORT":
        side = "SELL"
        position_side = "SHORT"
    else:
        raise ValueError("unsupported demo direction")

    if entry_quantity <= 0:
        raise ValueError("demo entry quantity must be positive")

    payload = {
        "symbol": R36F14_DEMO_SYMBOL,
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": decimal_to_string(entry_quantity),
        "newClientOrderId": writer_client_id(direction, "D14"),
        "tpTriggerPrice": decimal_to_string(tp1_price),
        "slTriggerPrice": decimal_to_string(stop_price),
        "TpWorkingType": "MARK_PRICE",
        "SlWorkingType": "MARK_PRICE",
    }

    full_tp_plan = {
        "tp1": tp_snapshot.get("tp1"),
        "tp2": tp_snapshot.get("tp2"),
        "tp3": tp_snapshot.get("tp3"),
        "allocation_percent": {
            "tp1": decimal_to_string(TP1_ALLOCATION_PERCENT),
            "tp2": decimal_to_string(TP2_ALLOCATION_PERCENT),
            "tp3": decimal_to_string(TP3_ALLOCATION_PERCENT),
        },
        "tp3_trailing_distance_percent": decimal_to_string(
            TP3_TRAILING_DISTANCE_PERCENT
        ),
        "preserved_internally": True,
        "demo_api_multi_tp_not_assumed": True,
    }

    return {
        "stage": STAGE,
        "endpoint": R36F14_DEMO_ORDER_ENDPOINT,
        "method": "POST",
        "payload": payload,
        "full_tp_plan": full_tp_plan,
        "submitted": False,
        "demo_post_transport_enabled": R36F14_DEMO_POST_TRANSPORT_ENABLED,
        "demo_order_submission_enabled": R36F14_DEMO_ORDER_SUBMISSION_ENABLED,
        "first_demo_order_allowed": R36F14_FIRST_DEMO_ORDER_ALLOWED,
        "real_order_execution": REAL_ORDER_EXECUTION,
        "integrity_sha256": sha256_text(canonical_json(payload)),
    }


def validate_r36f14_demo_order_preview(preview, direction, entry_price):
    if not preview:
        return {"all_valid": False, "reason": "DEMO_PREVIEW_MISSING"}

    payload = preview.get("payload", {})
    direction = str(direction).upper()
    entry_price = D(entry_price)

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

    client_id = str(payload.get("newClientOrderId", ""))
    qty = D(payload.get("quantity", "0"))
    tp = D(payload.get("tpTriggerPrice", "0"))
    sl = D(payload.get("slTriggerPrice", "0"))

    direction_ok = (
        direction == "LONG"
        and payload.get("side") == "BUY"
        and payload.get("positionSide") == "LONG"
    ) or (
        direction == "SHORT"
        and payload.get("side") == "SELL"
        and payload.get("positionSide") == "SHORT"
    )

    price_direction_ok = (
        direction == "LONG" and tp > entry_price and sl < entry_price
    ) or (
        direction == "SHORT" and tp < entry_price and sl > entry_price
    )

    checks = {
        "documented_endpoint": preview.get("endpoint") == R36F14_DEMO_ORDER_ENDPOINT,
        "post_preview_only": preview.get("method") == "POST" and preview.get("submitted") is False,
        "required_fields_present": required.issubset(set(payload.keys())),
        "demo_symbol_exact": payload.get("symbol") == R36F14_DEMO_SYMBOL,
        "market_order": payload.get("type") == "MARKET",
        "direction_mapping": direction_ok,
        "quantity_positive": qty > 0,
        "client_id_valid_length": 1 <= len(client_id) <= 36,
        "tp_sl_direction_valid": price_direction_ok,
        "working_types_mark_price": (
            payload.get("TpWorkingType") == "MARK_PRICE"
            and payload.get("SlWorkingType") == "MARK_PRICE"
        ),
        "demo_transport_disabled": R36F14_DEMO_POST_TRANSPORT_ENABLED is False,
        "demo_submission_disabled": R36F14_DEMO_ORDER_SUBMISSION_ENABLED is False,
        "first_demo_order_disabled": R36F14_FIRST_DEMO_ORDER_ALLOWED is False,
        "real_execution_disabled": REAL_ORDER_EXECUTION is False,
    }
    checks["all_valid"] = all(checks.values())

    return {
        "checks": checks,
        "all_valid": checks["all_valid"],
    }


def synthetic_r36f14_demo_integration_tests():
    synthetic_tp = {
        "tp_approval": {"approved": True},
        "tp1": "80400.0",
        "tp2": "80800.0",
        "tp3": "TRAILING_RUNNER",
    }

    preview = build_r36f14_demo_order_preview(
        "LONG",
        Decimal("0.0004"),
        synthetic_tp,
        Decimal("79600.0"),
    )
    validation = validate_r36f14_demo_order_preview(
        preview,
        "LONG",
        Decimal("80000.0"),
    )

    for name, result in validation["checks"].items():
        if name == "all_valid":
            continue
        check(
            "R36F14_SYNTHETIC_DEMO_" + name.upper(),
            result,
        )

    check(
        "R36F14_SYNTHETIC_DEMO_INTEGRATION_VALID",
        validation["all_valid"],
    )
    check(
        "R36F14_SYNTHETIC_DEMO_POST_NOT_SENT",
        preview["submitted"] is False,
    )

    return {
        "preview": preview,
        "validation": validation,
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
    entry_price = D(entry_price)
    stop_price = D(stop_price)
    entry_quantity = D(entry_quantity)
    available_balance = D(available_balance)
    leverage = D(leverage)

    if entry_price <= 0:
        raise ValueError("entry_price must be positive")
    if entry_quantity <= 0:
        raise ValueError("entry_quantity must be positive")
    if available_balance <= 0:
        raise ValueError("available_balance must be positive")
    if leverage <= 0:
        raise ValueError("leverage must be positive")

    price_distance = abs(entry_price - stop_price)
    expected_loss = price_distance * entry_quantity
    expected_loss_percent = expected_loss / available_balance * Decimal("100")
    account_loss_budget = available_balance * R36F132_MAX_ACCOUNT_LOSS_PERCENT / Decimal("100")
    isolated_entry_margin = entry_price * entry_quantity / leverage

    checks = {
        "price_distance_positive": price_distance > 0,
        "expected_loss_positive": expected_loss > 0,
        "within_account_loss_budget": expected_loss <= account_loss_budget,
        "within_isolated_entry_margin_budget": expected_loss <= isolated_entry_margin,
    }
    checks["all_valid"] = all(checks.values())

    return {
        "entry_price": decimal_to_string(entry_price),
        "stop_price": decimal_to_string(stop_price),
        "entry_quantity": decimal_to_string(entry_quantity),
        "available_balance": decimal_to_string(available_balance),
        "leverage": decimal_to_string(leverage),
        "price_distance": decimal_to_string(price_distance),
        "expected_loss_usdt": decimal_to_string(expected_loss),
        "expected_loss_percent_of_available_balance": decimal_to_string(expected_loss_percent),
        "configured_max_account_loss_percent": decimal_to_string(R36F132_MAX_ACCOUNT_LOSS_PERCENT),
        "account_loss_budget_usdt": decimal_to_string(account_loss_budget),
        "isolated_entry_margin_usdt": decimal_to_string(isolated_entry_margin),
        "checks": checks,
        "all_valid": checks["all_valid"],
    }


def apply_r36f132_stop_loss_budget_authorization_gate(command_preview, loss_budget):
    preview = dict(command_preview or {})
    preview["r36f132_stop_loss_budget_required"] = True
    preview["r36f132_stop_loss_budget_valid"] = bool(loss_budget and loss_budget.get("all_valid"))
    if not preview.get("authorized_preview"):
        return preview
    if not loss_budget or not loss_budget.get("all_valid"):
        preview["authorized_preview"] = False
        preview["reason"] = "PROTECTIVE_STOP_LOSS_BUDGET_NOT_READY"
        preview["exchange_order_sent"] = False
        return preview
    preview["reason"] = "COMMAND_EMA_TP_STOP_RISK_ENVELOPE_AND_LOSS_BUDGET_AGREE"
    preview["exchange_order_sent"] = False
    return preview


def synthetic_r36f132_stop_loss_budget_tests():
    passing = validate_r36f132_stop_loss_budget(Decimal("80000"), Decimal("79600"), Decimal("0.0004"), Decimal("7.19"), Decimal("100"))
    check("R36F132_SYNTHETIC_STOP_LOSS_BUDGET_APPROVED", passing["all_valid"] is True)
    check("R36F132_SYNTHETIC_EXPECTED_LOSS_016_USDT", passing["expected_loss_usdt"] == "0.16")
    check("R36F132_SYNTHETIC_WITHIN_ACCOUNT_LOSS_BUDGET", passing["checks"]["within_account_loss_budget"] is True)
    check("R36F132_SYNTHETIC_WITHIN_ENTRY_MARGIN_BUDGET", passing["checks"]["within_isolated_entry_margin_budget"] is True)

    failing = validate_r36f132_stop_loss_budget(Decimal("80000"), Decimal("79200"), Decimal("0.0004"), Decimal("7.19"), Decimal("100"))
    check("R36F132_SYNTHETIC_EXCESSIVE_ACCOUNT_LOSS_REJECTED", failing["checks"]["within_account_loss_budget"] is False)

    authorized = apply_r36f132_stop_loss_budget_authorization_gate({"authorized_preview": True, "exchange_order_sent": False}, passing)
    blocked = apply_r36f132_stop_loss_budget_authorization_gate({"authorized_preview": True, "exchange_order_sent": False}, failing)
    check("R36F132_SYNTHETIC_AUTHORIZATION_GATE_APPROVES_SAFE_LOSS", authorized["authorized_preview"] is True)
    check("R36F132_SYNTHETIC_AUTHORIZATION_GATE_BLOCKS_EXCESSIVE_LOSS", blocked["authorized_preview"] is False)
    check("R36F132_SYNTHETIC_GATE_NEVER_SENDS_ORDER", authorized.get("exchange_order_sent") is False and blocked.get("exchange_order_sent") is False)
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
                else "BLOCKED"
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
### R36F.15.2 — Part 4 of 4


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
    r36f15_demo_submission = None
    r36f15_demo_reconciliation_after = None

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
        R36F14_DEMO_POST_TRANSPORT_ENABLED is False,
    )

    check(
        "R36F14_DEMO_ORDER_SUBMISSION_DISABLED",
        R36F14_DEMO_ORDER_SUBMISSION_ENABLED is False,
    )

    check(
        "R36F14_FIRST_DEMO_ORDER_DISABLED",
        R36F14_FIRST_DEMO_ORDER_ALLOWED is False,
    )

    check(
        "R36F15_REAL_MONEY_FIREBREAK_INTACT",
        REAL_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and FIRST_REAL_ORDER_ALLOWED is False,
    )

    check(
        "R36F15_DEMO_ONLY_TRANSPORT_ENABLED",
        R36F15_DEMO_POST_TRANSPORT_ENABLED is True
        and R36F15_DEMO_ORDER_SUBMISSION_ENABLED is True
        and R36F15_FIRST_DEMO_ORDER_ALLOWED is True,
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
        and R36C_EVIDENCE_OK
        and R36D_EVIDENCE_OK
    )

    try:

        await reconcile_weex()

        WEEX_READ_ONLY_OK = True

        try:
            r36f14_demo_account = await r36f14_read_demo_account()
            diagnostic_check(
                "R36F14_DEMO_READ_ONLY_RECONCILIATION",
                r36f14_demo_account.get("all_reads_successful", False),
                (
                    "asset=" + str(r36f14_demo_account.get("demo_asset"))
                    + " available=" + str(r36f14_demo_account.get("available_balance"))
                    + " open_positions=" + str(r36f14_demo_account.get("open_demo_position_count"))
                    + " history_count=" + str(r36f14_demo_account.get("history_count"))
                ),
            )
        except Exception as exc:
            r36f14_demo_account = {
                "all_reads_successful": False,
                "error": str(exc),
            }
            diagnostic_check(
                "R36F14_DEMO_READ_ONLY_RECONCILIATION",
                False,
                str(exc),
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
            str(exc),
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
            str(exc),
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
            str(exc),
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
        r36f14_demo_integration = synthetic_r36f14_demo_integration_tests()

        check(
            "R36F12_WRITER_SAFETY_TESTS",
            True,
        )

    except Exception as exc:

        check(
            "STRICT_TP_QUANTITY_FEASIBILITY_TESTS",
            False,
            str(exc),
        )

        check(
            "ADJUSTABLE_TP_BALANCE_READINESS_TESTS",
            False,
            str(exc),
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

        EMA_SIGNAL_SNAPSHOT = build_ema_signal_snapshot(
            historical_rows
        )

        diagnostic_check(
            "R36F12_EMA_ENGINE_READY",
            EMA_SIGNAL_SNAPSHOT.get(
                "ready"
            ) is True,
            f"reason={EMA_SIGNAL_SNAPSHOT.get('reason')}",
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
                f"separation="
                f"{EMA_SIGNAL_SNAPSHOT.get('ema19_50_separation_percent')}%",
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
                    "No current ideal EMA direction; no alert sent",
                )

    except Exception as exc:

        check(
            "REAL_HISTORICAL_KLINES_LOADED",
            False,
            str(exc),
        )

    real_long_snapshot = None

    REAL_LONG_MARKET_ELIGIBLE = False

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
                    + str(exc)
                ),
            )

    real_short_snapshot = None

    REAL_SHORT_MARKET_ELIGIBLE = False

    if (
        historical_rows
        and MARK_PRICE is not None
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
                    + str(exc)
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
            str(exc),
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
                "TRADE_NOT_ELIGIBLE: no currently eligible real market TP set",
            )

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                "blocked: no currently eligible real market TP set",
            )

        elif (
            AVAILABLE_BALANCE is None
            or
            MARK_PRICE is None
        ):

            diagnostic_check(
                "ADJUSTABLE_TP_BALANCE_READINESS",
                False,
                "READINESS_UNAVAILABLE: balance or mark price unavailable",
            )

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                "blocked: balance or mark price unavailable",
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
                + "direction=" + selected_direction
                + " status=" + balance_readiness["status"]
                + " reason=" + balance_readiness["reason"]
                + " available_usdt="
                + balance_readiness["available_balance"]
                + " planned_entry_qty="
                + balance_readiness["planned_entry_quantity"]
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
                    and writer_preview[
                        "quantity_validation"
                    ][
                        "all_valid"
                    ]
                    and writer_preview[
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

                r36f132_stop_loss_budget = validate_r36f132_stop_loss_budget(
                    canary_writer_preview["entry_price"],
                    r36f13_stop_price,
                    canary_writer_preview["entry_quantity"],
                    AVAILABLE_BALANCE,
                    leverage,
                )

                log(
                    "R36F.13.2 STOP LOSS BUDGET "
                    + "expected_loss_usdt=" + r36f132_stop_loss_budget["expected_loss_usdt"]
                    + " expected_loss_percent=" + r36f132_stop_loss_budget["expected_loss_percent_of_available_balance"]
                    + " max_account_loss_percent=" + r36f132_stop_loss_budget["configured_max_account_loss_percent"]
                    + " isolated_entry_margin_usdt=" + r36f132_stop_loss_budget["isolated_entry_margin_usdt"]
                )

                for loss_check_name, loss_check_result in r36f132_stop_loss_budget["checks"].items():
                    if loss_check_name == "all_valid":
                        continue
                    diagnostic_check(
                        "R36F132_STOP_LOSS_BUDGET_" + loss_check_name.upper(),
                        loss_check_result,
                    )

                check(
                    "R36F132_STOP_LOSS_BUDGET_AUTHORIZATION_GATE",
                    r36f132_stop_loss_budget["all_valid"],
                )

                # R36F.15.2: use the direction-specific TP snapshot selected above.
                # R36F.15.1 accidentally referenced the nonexistent
                # selected_tp_snapshot name here.
                check(
                    "R36F152_SELECTED_TP_SNAPSHOT_AVAILABLE",
                    selected_snapshot is not None,
                )

                r36f14_demo_order_preview = build_r36f14_demo_order_preview(
                    selected_direction,
                    canary_writer_preview["entry_quantity"],
                    selected_snapshot,
                    r36f13_stop_price,
                )

                r36f14_demo_order_validation = validate_r36f14_demo_order_preview(
                    r36f14_demo_order_preview,
                    selected_direction,
                    canary_writer_preview["entry_price"],
                )

                for demo_check_name, demo_check_result in r36f14_demo_order_validation["checks"].items():
                    if demo_check_name == "all_valid":
                        continue
                    diagnostic_check(
                        "R36F14_DEMO_ORDER_" + demo_check_name.upper(),
                        demo_check_result,
                    )

                check(
                    "R36F14_DEMO_ORDER_INTEGRATION_GATE",
                    r36f14_demo_order_validation["all_valid"],
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

                log(
                    f"R36F.15 DEMO ARM REQUESTED = {R36F15_DEMO_ARM_REQUESTED}"
                )

                r36f15_demo_submission = await submit_r36f15_demo_order(
                    r36f14_demo_order_preview,
                    TELEGRAM_COMMAND_PREVIEW,
                )

                log(
                    "R36F.15 DEMO SUBMISSION RESULT = "
                    + canonical_json(r36f15_demo_submission)
                )

                if r36f15_demo_submission.get("attempted"):
                    check(
                        "R36F15_DEMO_ORDER_ACCEPTED",
                        r36f15_demo_submission.get("accepted") is True,
                        str(r36f15_demo_submission.get("transport")),
                    )

                    if r36f15_demo_submission.get("accepted"):
                        await asyncio.sleep(float(R36F15_RECONCILE_DELAY_SECONDS))
                        r36f15_demo_reconciliation_after = await r36f14_read_demo_account()
                        diagnostic_check(
                            "R36F15_POST_TRADE_DEMO_RECONCILIATION",
                            r36f15_demo_reconciliation_after.get("all_reads_successful") is True,
                            canonical_json(r36f15_demo_reconciliation_after),
                        )
                else:
                    diagnostic_check(
                        "R36F15_DEMO_DISPATCH_NOT_ATTEMPTED",
                        True,
                        r36f15_demo_submission.get("reason"),
                    )

                check(
                    "R36F132_LIVE_TRANSPORT_REMAINS_DISABLED",
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
                    is False,
                )

    except Exception as exc:

        diagnostic_check(
            "ADJUSTABLE_TP_BALANCE_READINESS",
            False,
            str(exc),
        )

        diagnostic_check(
            "WRITER_REQUEST_CONSTRUCTION",
            False,
            str(exc),
        )

        # R36F.15.2: an unexpected exception in the eligible writer/demo
        # construction path is a capability failure, not normal market
        # ineligibility, and must therefore become a final blocker.
        check(
            "R36F152_WRITER_DEMO_PIPELINE_EXCEPTION_FREE",
            False,
            str(exc),
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
        "REAL_MONEY_ZERO_WRITE_INVARIANTS",
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
        f"{STAGE} DEMO_ARM_REQUESTED = {R36F15_DEMO_ARM_REQUESTED}"
    )

    log(
        f"{STAGE} DEMO_ORDER_ATTEMPTED = {bool(r36f15_demo_submission and r36f15_demo_submission.get('attempted'))}"
    )

    log(
        f"{STAGE} DEMO_ORDER_ACCEPTED = {bool(r36f15_demo_submission and r36f15_demo_submission.get('accepted'))}"
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
        log(f"{STAGE} EXPECTED_STOP_LOSS_USDT = {r36f132_stop_loss_budget.get('expected_loss_usdt')}")
        log(f"{STAGE} EXPECTED_STOP_LOSS_PERCENT = {r36f132_stop_loss_budget.get('expected_loss_percent_of_available_balance')}")
        log(f"{STAGE} MAX_ACCOUNT_LOSS_PERCENT = {r36f132_stop_loss_budget.get('configured_max_account_loss_percent')}")

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
                        and balance_readiness.get(
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

                "r36f15_demo_post_transport_enabled":
                    R36F15_DEMO_POST_TRANSPORT_ENABLED,

                "r36f15_demo_order_submission_enabled":
                    R36F15_DEMO_ORDER_SUBMISSION_ENABLED,

                "r36f15_demo_arm_requested":
                    R36F15_DEMO_ARM_REQUESTED,
            },

        "r36f14_weex_demo_integration":
            {
                "demo_symbol": R36F14_DEMO_SYMBOL,
                "demo_asset": R36F14_DEMO_ASSET,
                "balance_endpoint": R36F14_DEMO_BALANCE_ENDPOINT,
                "positions_endpoint": R36F14_DEMO_POSITIONS_ENDPOINT,
                "history_endpoint": R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
                "order_endpoint": R36F14_DEMO_ORDER_ENDPOINT,
                "read_only_reconciliation": r36f14_demo_account,
                "synthetic_integration": r36f14_demo_integration,
                "real_market_demo_order_preview": r36f14_demo_order_preview,
                "real_market_demo_order_validation": r36f14_demo_order_validation,
                "demo_post_transport_enabled": R36F14_DEMO_POST_TRANSPORT_ENABLED,
                "demo_order_submission_enabled": R36F14_DEMO_ORDER_SUBMISSION_ENABLED,
                "first_demo_order_allowed": R36F14_FIRST_DEMO_ORDER_ALLOWED,
                "actual_demo_order_sent": bool(
                    r36f15_demo_submission
                    and r36f15_demo_submission.get("sent")
                ),
                "actual_demo_order_accepted": bool(
                    r36f15_demo_submission
                    and r36f15_demo_submission.get("accepted")
                ),
                "r36f15_demo_submission": r36f15_demo_submission,
                "r36f15_post_trade_reconciliation": r36f15_demo_reconciliation_after,
                "actual_real_order_sent": False,
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

    if (
        r36f15_demo_submission
        and r36f15_demo_submission.get("sent")
    ):
        log(
            "WEEX DEMO ORDER WAS SENT; PRODUCTION REAL-MONEY ORDER REMAINS DISABLED"
        )
    else:
        log(
            "NO DEMO ORDER WAS SENT"
        )

    log(
        "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
    )

    line()

    return snapshot


# ============================================================
# HEARTBEAT
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
            f"{REAL_ORDER_EXECUTION} "
            f"demo_arm="
            f"{R36F15_DEMO_ARM_REQUESTED} "
            f"reevaluation_seconds="
            f"{R36F151_REEVALUATION_SECONDS}"
        )

        await asyncio.sleep(
            R36F151_REEVALUATION_SECONDS
        )

        line()
        log(
            f"{STAGE} RUNTIME REEVALUATION START "
            f"heartbeat={HEARTBEAT_COUNT}"
        )
        line()

        try:
            # Deliberately rerun the proven complete R36F.15 pipeline.
            # This refetches mark price/history/account reads, recalculates
            # EMA and historical TP clusters, revalidates the command,
            # rebuilds stop/risk/writer previews, and reaches demo transport
            # only when every existing authorization gate passes.
            # The durable R36F15 demo journal inside submit_r36f15_demo_order()
            # preserves exactly-once first-demo dispatch across every cycle
            # and across service restarts.
            await run_r36f12()

            log(
                f"{STAGE} RUNTIME REEVALUATION COMPLETE "
                f"heartbeat={HEARTBEAT_COUNT} "
                f"status={TEST_STATUS} "
                f"long_valid_clusters="
                f"{LONG_DIAGNOSTICS.get('valid_cluster_count')} "
                f"short_valid_clusters="
                f"{SHORT_DIAGNOSTICS.get('valid_cluster_count')}"
            )

        except Exception as exc:
            TEST_STATUS = "FAIL"
            line()
            log(
                f"{STAGE} RUNTIME REEVALUATION ERROR = {exc}"
            )
            line()


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
