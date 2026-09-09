
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

