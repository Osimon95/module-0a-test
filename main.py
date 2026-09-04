#!/usr/bin/env python3
"""
R36F.6 - WRITER CONSTRUCTION AND VALIDATION CHECKPOINT

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5.4 safety baseline while
    upgrading ONLY the writer-request construction and validation layer.

R36F.6 CHANGE:

    1. Preserve historical two-cluster TP approval.
    2. Preserve real-market TP rejection as strategy eligibility,
       not as a bot failure.
    3. Construct the intended execution plan as separate legs:
           ENTRY
           TP1 = 20%
           TP2 = 20%
           TP3 = 60% trailing runner
    4. Validate LONG/SHORT side mapping.
    5. Validate quantity step/minimum and exact allocation sum.
    6. Generate deterministic client IDs.
    7. Generate an integrity SHA-256 over the writer legs.
    8. Keep submitted=False.
    9. Keep ALL exchange mutation and real execution disabled.

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

STAGE = "R36F.6"

PURPOSE = (
    "WRITER CONSTRUCTION AND VALIDATION CHECKPOINT: "
    "preserve the proven R36F.5.4 strategy and safety baseline "
    "while constructing separate ENTRY/TP1/TP2/TP3 writer legs "
    "without submitting any exchange mutation"
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

    url = (
        API_BASE_URL
        + path
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
            path,
            "",
        )

        headers = {
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": passphrase,
        }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.get(
            url,
            params=params or {},
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
        "/capi/v3/account/positions",
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
# R36F.6 WRITER HELPERS
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
        f"R36F6-{direction}-{leg}-0001"
    )

    if len(value) > 36:

        raise ValueError(
            "writer client id exceeds WEEX limit"
        )

    return value


# ============================================================
# WRITER QUANTITY ALLOCATION
# ============================================================

def writer_quantities(
    entry_quantity,
):

    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP,
    )

    tp1 = quantize_down(
        entry_quantity
        * TP1_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp2 = quantize_down(
        entry_quantity
        * TP2_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp3 = (
        entry_quantity
        - tp1
        - tp2
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

    checks = {

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
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


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
        or not tp_snapshot.get(
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
            tp1_price > entry_price
            and
            tp2_price > tp1_price
        ):

            raise ValueError(
                "LONG TP ordering invalid"
            )

    elif direction == "SHORT":

        if not (
            tp1_price < entry_price
            and
            tp2_price < tp1_price
        ):

            raise ValueError(
                "SHORT TP ordering invalid"
            )

    else:

        raise ValueError(
            "Invalid writer direction"
        )

    # --------------------------------------------------------
    # ENTRY
    #
    # Deliberately NO TP trigger fields are attached to the
    # entry order. TP1/TP2/TP3 are separate legs so that the
    # intended 20/20/60 allocation is preserved.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # TP1
    # --------------------------------------------------------

    tp1_leg = {

        "endpoint":
            WRITER_ENDPOINT_TPSL,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            close_side,

        "positionSide":
            close_position_side,

        "type":
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

    # --------------------------------------------------------
    # TP2
    # --------------------------------------------------------

    tp2_leg = {

        "endpoint":
            WRITER_ENDPOINT_TPSL,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            close_side,

        "positionSide":
            close_position_side,

        "type":
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

    # --------------------------------------------------------
    # TP3 TRAILING RUNNER
    # --------------------------------------------------------

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

        "allocation_percent":
            {

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
# MAIN R36F.6 TEST
# ============================================================

async def run_r36f6():

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

    # ========================================================
    # EXECUTION FIREBREAK TESTS
    # ========================================================

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

    # ========================================================
    # CREDENTIAL PRESENCE
    # ========================================================

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

    # ========================================================
    # R36A DURABLE EVIDENCE
    # ========================================================

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

    # ========================================================
    # R36C DURABLE EVIDENCE
    # ========================================================

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

    # ========================================================
    # R36D SNAPSHOT EVIDENCE
    # ========================================================

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

    # ========================================================
    # WEEX READ-ONLY RECONCILIATION
    # ========================================================

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

    # ========================================================
    # SYNTHETIC TP ENGINE
    # ========================================================

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

    # ========================================================
    # TP REJECTION TEST
    # ========================================================

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

    # ========================================================
    # HISTORICAL KLINES
    # ========================================================

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

    # ========================================================
    # REAL LONG TP PREVIEW
    #
    # Market eligibility is diagnostic.
    # Lack of two clusters is NOT a bot failure.
    # ========================================================

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

    # ========================================================
    # REAL SHORT TP PREVIEW
    #
    # Market eligibility is diagnostic.
    # Lack of two clusters is NOT a bot failure.
    # ========================================================

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

    # ========================================================
    # CANARY PREVIEW
    # ========================================================

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

    # ========================================================
    # R36F.6 WRITER REQUEST CONSTRUCTION
    # ========================================================

    writer_preview = None

    WRITER_CONSTRUCTION_ELIGIBLE = False

    try:

        selected_direction = None

        selected_snapshot = None

        # Prefer currently eligible SHORT because this is
        # dynamic market selection. If SHORT is not eligible,
        # use eligible LONG.

        if (
            REAL_SHORT_MARKET_ELIGIBLE
            and
            real_short_snapshot is not None
        ):

            selected_direction = "SHORT"

            selected_snapshot = (
                real_short_snapshot
            )

        elif (
            REAL_LONG_MARKET_ELIGIBLE
            and
            real_long_snapshot is not None
        ):

            selected_direction = "LONG"

            selected_snapshot = (
                real_long_snapshot
            )

        if selected_direction is None:

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                (
                    "no currently eligible "
                    "real market TP set"
                ),
            )

        elif (
            AVAILABLE_BALANCE is None
            or
            MARK_PRICE is None
        ):

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                (
                    "balance or mark price unavailable"
                ),
            )

        else:

            leverage = (
                LEVERAGE_SHORT
                if selected_direction == "SHORT"
                else
                LEVERAGE_LONG
            )

            quantity = quantize_down(

                AVAILABLE_BALANCE
                * ENTRY_MARGIN_PERCENT
                / Decimal("100")
                * leverage
                / MARK_PRICE,

                QUANTITY_STEP,
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

            # Explicitly expose each quantity validation
            # without turning a market-size limitation into
            # a final bot failure.

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

    except Exception as exc:

        diagnostic_check(
            "WRITER_REQUEST_CONSTRUCTION",
            False,
            str(exc),
        )

    # ========================================================
    # ZERO-WRITE INVARIANTS
    # ========================================================

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

    # ========================================================
    # FINAL GATE
    #
    # Market TP rejection and writer diagnostic limitations
    # are NOT final blockers.
    #
    # Actual safety invariants remain final blockers.
    # ========================================================

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

    # ========================================================
    # FINAL LOGGING
    # ========================================================

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

    # ========================================================
    # SNAPSHOT
    # ========================================================

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

        await run_r36f6()

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
