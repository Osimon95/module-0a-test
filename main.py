
#!/usr/bin/env python3
"""
R36F.11 - FIRST-LIVE WRITER SAFETY COMPLETION CHECKPOINT

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

    This version DOES NOT send POST requests.

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

STAGE = "R36F.11"

PURPOSE = (
    "FIRST-LIVE WRITER SAFETY COMPLETION: preserve the proven R36F.10 "
    "TP/readiness engine, validate current WEEX V3 writer request shapes, cap "
    "the first canary at 0.0004 BTC, require an explicit protective stop, "
    "require a clear durable dispatch journal, and remain ZERO-WRITE in R36F.11"
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
# R36F.11 FIRST-LIVE CANARY SAFETY CONFIGURATION
# ============================================================

# R36F.11 remains intentionally zero-write.  These values prepare the exact
# gate that R36F.12 may consume; they do not enable transport here.
CANARY_MAX_ENTRY_QUANTITY = Decimal("0.0004")
CANARY_ARM_PHRASE = "ARM_FIRST_LIVE_CANARY"
CANARY_ARM_REQUESTED = (
    os.getenv("R36F11_LIVE_CANARY_ARM", "").strip() == CANARY_ARM_PHRASE
)
CANARY_STOP_PRICE_TEXT = os.getenv("R36F11_CANARY_STOP_PRICE", "").strip()
CANARY_STOP_WORKING_TYPE = "MARK_PRICE"


# ============================================================
# STATE DIRECTORIES
# ============================================================

R36A_STATE_DIR = "/var/data/r36a_state"
R36C_STATE_DIR = "/var/data/r36c_state"
R36D_STATE_DIR = "/var/data/r36d_state"
R36F_STATE_DIR = "/var/data/r36f_state"

os.makedirs(R36F_STATE_DIR, exist_ok=True)


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

R36F11_CANARY_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "first_live_canary_dispatch_journal.json",
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


# ============================================================
# BASIC UTILITIES
# ============================================================

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


# ============================================================
# FINAL CHECK
# ============================================================

def check(name, condition, detail=None):

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

def D(value):
    return Decimal(
        str(value)
    )


def quantize_down(
    value,
    step,
):

    value = D(value)
    step = D(step)

    if step <= 0:
        raise ValueError(
            "Invalid quantization step"
        )

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

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = (
            text
            .rstrip("0")
            .rstrip(".")
        )

    return text


# ============================================================
# JSON UTILITIES
# ============================================================

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


def read_json_file(
    path,
    default=None,
):

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


def write_json_file(
    path,
    data,
):

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

    def walk(value):

        if isinstance(
            value,
            dict,
        ):

            for key, item in value.items():

                if (
                    isinstance(key, str)
                    and "id" in key.lower()
                    and isinstance(item, str)
                ):

                    ids.add(item)

                walk(item)

        elif isinstance(
            value,
            list,
        ):

            for item in value:
                walk(item)

    walk(data)

    return ids


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

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
            str(len(body)),
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


# ============================================================
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

### R36F.11 — Part 2 of 4

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
# LOCAL EXTREMA
# ============================================================

def build_extrema(
    values,
):

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

        return build_extrema(
            historical_highs(
                rows
            )
        )

    if side == "SHORT":

        return build_extrema(
            historical_lows(
                rows
            )
        )

    raise ValueError(
        f"Unsupported side={side}"
    )


# ============================================================
# CLUSTERING
# ============================================================

def cluster_extrema(
    extrema,
):

    if not extrema:
        return []

    values = sorted(
        D(value)
        for value in extrema
    )

    clusters = []

    current = []

    for value in values:

        if not current:

            current = [
                value
            ]

            continue

        average = (
            sum(current)
            / Decimal(
                len(current)
            )
        )

        tolerance = (
            average
            * CLUSTER_TOLERANCE_PERCENT
            / Decimal("100")
        )

        if abs(
            value - average
        ) <= tolerance:

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

    if current:

        clusters.append(
            current
        )

    records = []

    for cluster in clusters:

        average = (
            sum(cluster)
            / Decimal(
                len(cluster)
            )
        )

        records.append(
            {
                "average": average,
                "minimum": min(cluster),
                "maximum": max(cluster),
                "touches": len(cluster),
            }
        )

    return records


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

        average = D(
            cluster["average"]
        )

        touches = int(
            cluster["touches"]
        )

        if touches < MIN_CLUSTER_TOUCHES:

            invalid.append(
                {
                    **cluster,
                    "valid": False,
                    "reason":
                        "INSUFFICIENT_CLUSTER_TOUCHES",
                }
            )

            continue

        if side == "LONG":

            if average <= entry_price:

                invalid.append(
                    {
                        **cluster,
                        "valid": False,
                        "reason":
                            "CLUSTER_NOT_ABOVE_ENTRY",
                    }
                )

                continue

        elif side == "SHORT":

            if average >= entry_price:

                invalid.append(
                    {
                        **cluster,
                        "valid": False,
                        "reason":
                            "CLUSTER_NOT_BELOW_ENTRY",
                    }
                )

                continue

        else:

            raise ValueError(
                f"Unsupported side={side}"
            )

        valid.append(
            {
                **cluster,
                "valid": True,
                "reason": "VALID",
            }
        )

    if side == "LONG":

        valid.sort(
            key=lambda item:
                D(
                    item["average"]
                )
        )

    else:

        valid.sort(
            key=lambda item:
                D(
                    item["average"]
                ),
            reverse=True,
        )

    return valid, invalid


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

    extrema = local_extrema_values(
        rows,
        side,
    )

    clusters = cluster_extrema(
        extrema
    )

    valid, invalid = validate_clusters(
        clusters,
        entry_price,
        side,
    )

    valid_count = len(
        valid
    )

    cluster_records = []

    for cluster in valid:

        cluster_records.append(
            {
                "cluster_number":
                    len(
                        cluster_records
                    ) + 1,
                "average":
                    decimal_to_string(
                        cluster["average"]
                    ),
                "minimum":
                    decimal_to_string(
                        cluster["minimum"]
                    ),
                "maximum":
                    decimal_to_string(
                        cluster["maximum"]
                    ),
                "touches":
                    cluster["touches"],
                "valid":
                    True,
                "reason":
                    "VALID",
            }
        )

    for cluster in invalid:

        cluster_records.append(
            {
                "cluster_number":
                    len(
                        cluster_records
                    ) + 1,
                "average":
                    decimal_to_string(
                        cluster["average"]
                    ),
                "minimum":
                    decimal_to_string(
                        cluster["minimum"]
                    ),
                "maximum":
                    decimal_to_string(
                        cluster["maximum"]
                    ),
                "touches":
                    cluster["touches"],
                "valid":
                    False,
                "reason":
                    cluster["reason"],
            }
        )

    if valid_count >= REQUIRED_TP_CLUSTERS:

        status = (
            "ENOUGH_VALID_CLUSTERS"
        )

        failure_reason = None

    elif valid_count == 1:

        status = (
            "ONLY_ONE_VALID_CLUSTER"
        )

        failure_reason = (
            "ONLY_ONE_VALID_CLUSTER"
        )

    elif clusters:

        status = (
            "CLUSTERS_REJECTED_BY_POLICY"
        )

        failure_reason = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    else:

        status = (
            "NO_VALID_CLUSTERS"
        )

        failure_reason = (
            "NO_VALID_HISTORICAL_CLUSTERS"
        )

    diagnostics = {

        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
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
            valid_count,

        "clusters":
            cluster_records,

        "status":
            status,

        "failure_reason":
            failure_reason,

        "required_valid_clusters":
            REQUIRED_TP_CLUSTERS,
    }

    log(
        f"{side} HISTORICAL EXTREMA COUNT = "
        f"{len(extrema)}"
    )

    log(
        f"{side} HISTORICAL CLUSTER COUNT = "
        f"{len(clusters)}"
    )

    log(
        f"{side} VALID CLUSTER COUNT = "
        f"{valid_count}"
    )

    for record in cluster_records:

        log(
            f"{side} CLUSTER "
            f"{record['cluster_number']}: "
            f"AVG={record['average']} "
            f"MIN={record['minimum']} "
            f"MAX={record['maximum']} "
            f"TOUCHES={record['touches']} "
            f"VALID={record['valid']} "
            f"REASON={record['reason']}"
        )

    log(
        f"{side} CLUSTER DIAGNOSTIC STATUS = "
        f"{status}"
    )

    log(
        f"{side} CLUSTER DIAGNOSTIC FAILURE_REASON = "
        f"{failure_reason}"
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

    if valid_count >= REQUIRED_TP_CLUSTERS:

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
        )

        if not failure_reason:

            failure_reason = (
                "FEWER_THAN_TWO_VALID_HISTORICAL_CLUSTERS"
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

        "tp3":
            {

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
### R36F.11 — Part 3 of 4

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

    long_diagnostics = build_cluster_diagnostics(
        long_rows,
        Decimal("99000"),
        "LONG",
    )

    long_approval = evaluate_tp_approval(
        long_diagnostics
    )

    check(
        "SYNTHETIC_LONG_TWO_CLUSTER_APPROVAL",
        long_approval[
            "approved"
        ] is True,
    )

    short_diagnostics = build_cluster_diagnostics(
        short_rows,
        Decimal("82000"),
        "SHORT",
    )

    short_approval = evaluate_tp_approval(
        short_diagnostics
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

    diagnostics = build_cluster_diagnostics(
        rows,
        entry,
        "LONG",
    )

    approval = evaluate_tp_approval(
        diagnostics
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
        approval[
            "available_valid_clusters"
        ] < REQUIRED_TP_CLUSTERS,
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
            q >= MIN_QUANTITY
            for q in quantities
        )
        and all(
            quantize_down(
                q,
                QUANTITY_STEP,
            ) == q
            for q in quantities
        )
        and sum(quantities)
        == entry_quantity
    )


def select_tp_allocation(
    entry_quantity,
):
    """
    Prefer 20/20/60.

    Fall back only to the approved
    25/25/50 allocation.
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
    Allocate TP quantities using preferred
    20/20/60 or approved 25/25/50 fallback.
    """

    entry_quantity = quantize_down(
        entry_quantity,
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


# ============================================================
# WRITER QUANTITY VALIDATION
# ============================================================

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
            )
            == entry_quantity,

        "tp1_on_step":
            quantize_down(
                tp1,
                QUANTITY_STEP,
            )
            == tp1,

        "tp2_on_step":
            quantize_down(
                tp2,
                QUANTITY_STEP,
            )
            == tp2,

        "tp3_on_step":
            quantize_down(
                tp3,
                QUANTITY_STEP,
            )
            == tp3,

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
    """
    Return first exchange-step quantity
    supported by an approved allocation.
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

        candidate += (
            QUANTITY_STEP
        )

    raise RuntimeError(
        "Unable to find adjustable TP minimum entry quantity"
    )


def minimum_strict_tp_entry_quantity():
    """
    Compatibility alias:
    R36F.10 minimum under the approved
    adjustable allocation policy.
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
                and allocation[
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
    Classify balance readiness under
    R36F.10 approved adjustable TP allocation.
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
# R36F.11 FIRST-LIVE WRITER SAFETY COMPLETION
# ============================================================

def validate_weex_v3_writer_shapes(
    writer_preview,
):
    """
    Validate only documented request fields
    needed by the frozen writer.
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
            "R36F11_CANARY_STOP_PRICE must be positive"
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


def unresolved_canary_journal(
    journal,
):

    if not journal:
        return False

    return str(
        journal.get(
            "status",
            "",
        )
    ).upper() in {
        "PREPARED",
        "DISPATCHING",
        "SUBMITTED",
        "AMBIGUOUS",
    }


def build_protected_canary_preview(
    writer_preview,
    stop_price,
    explicit_arm_requested,
    journal,
    flat_position,
):
    """
    Build the R36F.12-ready canary
    package without sending it.
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
        and stop_valid
        and quantity_capped
        and explicit_arm_requested
        and journal_clear
        and flat_position
        and writer_preview.get(
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

        "r36f11_transport_hard_disabled":
            True,
    }


def synthetic_r36f11_writer_safety_tests():

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
            Decimal("0.0004"),
            tp_snapshot,
        )
    )

    shape = (
        validate_weex_v3_writer_shapes(
            preview
        )
    )

    check(
        "R36F11_WEEX_V3_WRITER_SHAPES",
        shape[
            "all_valid"
        ],
    )

    clear = (
        build_protected_canary_preview(
            preview,
            Decimal("79600"),
            True,
            {},
            True,
        )
    )

    check(
        "R36F11_SYNTHETIC_PROTECTED_CANARY_READY",
        clear[
            "ready_for_r36f12"
        ] is True,
    )

    check(
        "R36F11_SYNTHETIC_CANARY_QTY_CAP_00004",
        clear[
            "entry_quantity"
        ] == "0.0004",
    )

    check(
        "R36F11_SYNTHETIC_STOP_ATTACHED",
        clear[
            "protected_entry_request"
        ].get(
            "slTriggerPrice"
        ) == "79600",
    )

    ambiguous = (
        build_protected_canary_preview(
            preview,
            Decimal("79600"),
            True,
            {
                "status":
                    "AMBIGUOUS"
            },
            True,
        )
    )

    check(
        "R36F11_AMBIGUOUS_JOURNAL_BLOCKS",
        ambiguous[
            "ready_for_r36f12"
        ] is False,
    )

    unarmed = (
        build_protected_canary_preview(
            preview,
            Decimal("79600"),
            False,
            {},
            True,
        )
    )

    check(
        "R36F11_EXPLICIT_ARM_REQUIRED",
        unarmed[
            "ready_for_r36f12"
        ] is False,
    )

    wrong_stop = (
        build_protected_canary_preview(
            preview,
            Decimal("80400"),
            True,
            {},
            True,
        )
    )

    check(
        "R36F11_WRONG_SIDE_STOP_BLOCKS",
        wrong_stop[
            "ready_for_r36f12"
        ] is False,
    )

    return True


# ============================================================
# R36F.11 ADJUSTABLE TP QUANTITY FEASIBILITY TESTS
# ============================================================

def synthetic_writer_quantity_tests():

    adjusted = (
        evaluate_writer_quantity_feasibility(
            Decimal("0.0004")
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
            Decimal("0.0005")
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
            Decimal("0.0003")
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
            Decimal("7.19"),
            Decimal("80000"),
            Decimal("100"),
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
            Decimal("8"),
            Decimal("80000"),
            Decimal("100"),
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
# MAIN R36F.11 TEST
# ============================================================

async def run_r36f11():

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
### R36F.11 — Part 4A

Paste this **immediately after Part 3**. It starts from the exact next line after:

```python
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

        synthetic_r36f11_writer_safety_tests()

        check(
            "R36F11_WRITER_SAFETY_TESTS",
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
                "R36F.11 ADJUSTABLE TP BALANCE READINESS "
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
                balance_readiness["eligible"],
                (
                    "status="
                    + balance_readiness["status"]
                    + " reason="
                    + balance_readiness["reason"]
                ),
            )

            diagnostic_check(
                "ADJUSTABLE_TP_QUANTITY_FEASIBILITY",
                quantity_feasibility["feasible"],
                (
                    "reason="
                    + quantity_feasibility["reason"]
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

                # R36F.11 first-live candidate is always capped at 0.0004 BTC.
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

                production_journal = read_json_file(
                    R36F11_CANARY_JOURNAL_FILE,
                    default={},
                )

                configured_stop = (
                    parse_canary_stop_price(
                        CANARY_STOP_PRICE_TEXT
                    )
                )

                if configured_stop is None:

                    diagnostic_check(
                        "R36F11_PROTECTIVE_STOP_CONFIGURED",
                        False,
                        "R36F11_CANARY_STOP_PRICE is not set; live canary remains blocked",
                    )

                else:

                    protected_canary_preview = (
                        build_protected_canary_preview(
                            canary_writer_preview,
                            configured_stop,
                            CANARY_ARM_REQUESTED,
                            production_journal,
                            len(OPEN_POSITIONS) == 0,
                        )
                    )

                    diagnostic_check(
                        "R36F11_PROTECTIVE_STOP_VALID",
                        protected_canary_preview[
                            "stop_valid"
                        ],
                    )

                    diagnostic_check(
                        "R36F11_CANARY_QUANTITY_CAPPED",
                        protected_canary_preview[
                            "quantity_capped"
                        ],
                        "max=0.0004 BTC",
                    )

                    diagnostic_check(
                        "R36F11_DURABLE_JOURNAL_CLEAR",
                        protected_canary_preview[
                            "journal_clear"
                        ],
                    )

                    diagnostic_check(
                        "R36F11_EXPLICIT_ARM_PRESENT",
                        protected_canary_preview[
                            "explicit_arm_requested"
                        ],
                        "set R36F11_LIVE_CANARY_ARM=ARM_FIRST_LIVE_CANARY only for the later R36F.12 live canary",
                    )

                # R36F.11 itself must never submit regardless of configuration.
                check(
                    "R36F11_LIVE_TRANSPORT_REMAINS_DISABLED",
                    EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
                    and ORDER_SUBMISSION_ENABLED is False
                    and REAL_ORDER_EXECUTION is False
                    and FIRST_REAL_ORDER_ALLOWED is False,
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
### R36F.11 — Part 4B

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

        "canary_preview":
            canary_preview,

        "writer_preview":
            writer_preview,

        "r36f11_protected_canary_preview":
            protected_canary_preview,

        "r36f11_canary_safety":
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
                    R36F11_CANARY_JOURNAL_FILE,

                "durable_journal_unresolved":
                    unresolved_canary_journal(
                        read_json_file(
                            R36F11_CANARY_JOURNAL_FILE,
                            default={},
                        )
                    ),

                "r36f11_zero_write":
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

        await run_r36f11()

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
