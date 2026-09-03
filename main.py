#!/usr/bin/env python3
"""
R36F.5.3 - READ-ONLY RECONCILIATION AND FUNCTION-INTEGRITY CORRECTION

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5 safety baseline while making
    the synthetic historical-cluster tests deterministic and explicit.

R36F.5.2 CHANGE:

    ONLY the synthetic diagnostic fixtures/tests are strengthened.

    The production TP policy is unchanged.

R36F.5.2 TP POLICY:

    A complete historical TP1/TP2 set requires TWO OR MORE valid
    historical clusters.

    LONG:
        Cluster 1 = first valid historical-high resistance cluster
        Cluster 2 = second valid historical-high resistance cluster

        TP1 = 20% adjustable progress from entry toward Cluster 1 average
        TP2 = 50% adjustable progress from entry toward Cluster 2 average
        TP3 = 60% trailing runner

    SHORT:
        Cluster 1 = first valid historical-low support cluster
        Cluster 2 = second valid historical-low support cluster

        TP1 = 20% adjustable progress from entry toward Cluster 1 average
        TP2 = 50% adjustable progress from entry toward Cluster 2 average
        TP3 = 60% trailing runner

    APPROVAL:

        valid_cluster_count >= 2
            -> TP_APPROVAL = APPROVED

        valid_cluster_count < 2
            -> TP_APPROVAL = REJECTED

    IMPORTANT:

        The two-cluster requirement approves the TP1 + TP2 historical
        set as a whole.

        TP1 is NOT independently approved with only one cluster.

        TP3 remains the runner and is NOT used to fabricate a missing
        historical TP1 or TP2.

    NO REAL OR DEMO ORDER IS SENT.
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

STAGE = "R36F.5.3"

PURPOSE = (
    "SMALLEST SYNTHETIC-TEST CORRECTION: "
    "make the historical two-cluster synthetic approval/rejection "
    "tests deterministic while preserving the R36F.5 production "
    "TP policy and execution safety baseline"
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
        log(f"PASS: {name}")

        if detail:
            log(f"      {detail}")

        return True

    log(f"FAIL: {name}")

    if detail:
        log(f"      {detail}")

    FINAL_BLOCKERS.append(name)

    return False


# ============================================================
# FROZEN DIAGNOSTIC CHECK
# ============================================================

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


# ============================================================
# DECIMAL UTILITIES
# ============================================================

def D(value):
    return Decimal(str(value))


def quantize_down(value, step):
    value = D(value)
    step = D(step)

    if step <= 0:
        raise ValueError("Invalid quantization step")

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
    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

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


# ============================================================
# DURABLE ID COLLECTION
# ============================================================

def collect_ids_from_json(value):
    found = set()

    if isinstance(value, dict):

        for key, item in value.items():

            if key in {
                "update_id",
                "telegram_update_id",
                "id",
                "decision_id",
            }:

                if isinstance(
                    item,
                    (str, int),
                ):
                    found.add(
                        str(item)
                    )

            found.update(
                collect_ids_from_json(item)
            )

    elif isinstance(value, list):

        for item in value:
            found.update(
                collect_ids_from_json(item)
            )

    return found


def collect_ids_from_file(path):
    data = read_json_file(
        path,
        {},
    )

    return collect_ids_from_json(
        data
    )


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        payload = {
            "stage": STAGE,
            "status": TEST_STATUS,
            "purpose": PURPOSE,

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

            "final_gate_ok":
                FINAL_GATE_OK,

            "short_valid_cluster_count":
                SHORT_DIAGNOSTICS.get(
                    "valid_cluster_count"
                ),

            "long_valid_cluster_count":
                LONG_DIAGNOSTICS.get(
                    "valid_cluster_count"
                ),

            "last_tp_approval":
                LAST_TP_APPROVAL,
        }

        body = json.dumps(
            payload,
            default=str,
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
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
# WEEX AUTHENTICATION
# ============================================================

def make_signature(
    timestamp,
    method,
    request_path,
    query_string="",
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
        + str(method).upper()
        + str(request_path)
        + str(query_string)
        + str(body)
    )

    digest = hmac.new(
        api_secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


# ============================================================
# HTTP GET
# ============================================================

async def http_get_json(
    session,
    url,
    headers=None,
    params=None,
):

    async with session.get(
        url,
        headers=headers or {},
        params=params,
        timeout=20,
    ) as response:

        text = await response.text()

        if response.status >= 400:
            raise RuntimeError(
                f"HTTP {response.status}: "
                f"{text[:500]}"
            )

        try:
            return json.loads(text)

        except Exception as exc:
            raise RuntimeError(
                f"Invalid JSON response: {exc}"
            )


# ============================================================
# WEEX PRIVATE GET
# ============================================================

async def weex_private_get(
    session,
    request_path,
    params=None,
):

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

    query_string = ""

    if params:

        query_parts = []

        for key in sorted(params):
            query_parts.append(
                f"{key}={params[key]}"
            )

        query_string = "&".join(
            query_parts
        )

    signature = make_signature(
        timestamp,
        "GET",
        request_path,
        query_string,
        "",
    )

    headers = {
        "ACCESS-KEY":
            api_key,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            passphrase,

        "Content-Type":
            "application/json",
    }

    url = (
        API_BASE_URL
        + request_path
    )

    return await http_get_json(
        session,
        url,
        headers=headers,
        params=params,
    )


# ============================================================
# WEEX PUBLIC TICKER
# ============================================================

async def weex_public_ticker(session):

    url = (
        API_BASE_URL
        + "/capi/v3/market/ticker/bookTicker"
    )

    return await http_get_json(
        session,
        url,
        params={
            "symbol": SYMBOL
        },
    )


async def weex_mark_price(session):
    """Read the actual WEEX contract mark price.

    WEEX V3 exposes mark price through /market/symbolPrice with
    priceType=MARK.  The bookTicker endpoint is a bid/ask endpoint and
    therefore is not treated as a mark-price source.
    """

    url = (
        API_BASE_URL
        + "/capi/v3/market/symbolPrice"
    )

    payload = await http_get_json(
        session,
        url,
        params={
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    candidates = []

    if isinstance(payload, dict):
        candidates.append(payload)
        data = payload.get("data")
        if isinstance(data, dict):
            candidates.append(data)
        elif isinstance(data, list):
            candidates.extend(data)

    elif isinstance(payload, list):
        candidates.extend(payload)

    for item in candidates:
        if not isinstance(item, dict):
            continue

        for key in ("price", "markPrice"):
            value = item.get(key)
            if value is not None:
                try:
                    price = D(value)
                    if price > 0:
                        return price
                except Exception:
                    continue

    raise RuntimeError(
        "Unable to extract WEEX mark price from symbolPrice MARK response"
    )


# ============================================================
# WEEX BALANCE
# ============================================================

async def weex_balance(session):

    payload = await weex_private_get(
        session,
        "/capi/v3/account/balance",
    )

    return payload


# ============================================================
# WEEX SINGLE POSITION
# ============================================================

async def weex_single_position(session):

    payload = await weex_private_get(
        session,
        "/capi/v3/account/position/singlePosition",
        params={
            "symbol":
                SYMBOL,
        },
    )

    return payload


# ============================================================
# WEEX EXCHANGE INFO
# ============================================================

async def weex_exchange_info(session):

    return await weex_public_get(
        session,
        "/capi/v3/market/exchangeInfo",
    )


# ============================================================
# KLINE FETCH
# ============================================================

async def fetch_klines_page(
    session,
    end_time=None,
):

    params = {
        "symbol":
            SYMBOL,

        "interval":
            KLINE_INTERVAL,

        "limit":
            HISTORICAL_LIMIT,
    }

    if end_time is not None:
        params["endTime"] = str(
            end_time
        )

    return await weex_public_get(
        session,
        "/capi/v3/market/klines",
        params=params,
    )


# ============================================================
# KLINE NORMALIZATION
# ============================================================

def normalize_kline_row(row):

    if isinstance(row, list):

        if len(row) < 5:
            return None

        try:
            return {
                "timestamp":
                    int(row[0]),

                "open":
                    D(row[1]),

                "high":
                    D(row[2]),

                "low":
                    D(row[3]),

                "close":
                    D(row[4]),
            }

        except Exception:
            return None

    if isinstance(row, dict):

        timestamp = (
            row.get("timestamp")
            or
            row.get("openTime")
            or
            row.get("time")
        )

        if timestamp is None:
            return None

        try:
            return {
                "timestamp":
                    int(timestamp),

                "open":
                    D(
                        row.get(
                            "open"
                        )
                    ),

                "high":
                    D(
                        row.get(
                            "high"
                        )
                    ),

                "low":
                    D(
                        row.get(
                            "low"
                        )
                    ),

                "close":
                    D(
                        row.get(
                            "close"
                        )
                    ),
            }

        except Exception:
            return None

    return None


# ============================================================
# HISTORICAL KLINE LOADER
# ============================================================

async def load_historical_klines(
    session,
):

    rows = []
    end_time = None

    for page in range(
        MAX_HISTORICAL_PAGES
    ):

        payload = await fetch_klines_page(
            session,
            end_time=end_time,
        )

        if isinstance(
            payload,
            dict,
        ):

            data = payload.get(
                "data",
                payload.get(
                    "result",
                    [],
                ),
            )

        else:
            data = payload

        if not isinstance(
            data,
            list,
        ):
            raise RuntimeError(
                f"Unexpected kline payload: {payload}"
            )

        if not data:
            break

        normalized = []

        for row in data:

            candle = normalize_kline_row(
                row
            )

            if candle is not None:
                normalized.append(
                    candle
                )

        if not normalized:
            break

        rows.extend(
            normalized
        )

        oldest = min(
            candle["timestamp"]
            for candle in normalized
        )

        end_time = (
            oldest - 1
        )

        if len(normalized) < HISTORICAL_LIMIT:
            break

    unique = {}

    for candle in rows:
        unique[
            candle["timestamp"]
        ] = candle

    candles = [
        unique[key]
        for key in sorted(
            unique
        )
    ]

    return candles


# ============================================================
# EMA CALCULATION
# ============================================================

def calculate_ema(
    values,
    period,
):

    if len(values) < period:
        return None

    multiplier = (
        D("2")
        /
        D(
            period + 1
        )
    )

    ema = (
        sum(
            values[
                :period
            ]
        )
        /
        D(period)
    )

    for value in values[
        period:
    ]:

        ema = (
            (
                value
                -
                ema
            )
            *
            multiplier
        ) + ema

    return ema


# ============================================================
# EMA SNAPSHOT
# ============================================================

def build_ema_snapshot(
    candles,
):

    closes = [
        candle["close"]
        for candle in candles
    ]

    ema19 = calculate_ema(
        closes,
        19,
    )

    ema50 = calculate_ema(
        closes,
        50,
    )

    ema200 = calculate_ema(
        closes,
        200,
    )

    return {
        "EMA19":
            decimal_to_string(
                ema19
            ),

        "EMA50":
            decimal_to_string(
                ema50
            ),

        "EMA200":
            decimal_to_string(
                ema200
            ),
    }


# ============================================================
# TREND DIRECTION
# ============================================================

def determine_trend(
    ema_snapshot,
):

    ema19 = ema_snapshot.get(
        "EMA19"
    )

    ema50 = ema_snapshot.get(
        "EMA50"
    )

    ema200 = ema_snapshot.get(
        "EMA200"
    )

    if (
        ema19 is None
        or
        ema50 is None
        or
        ema200 is None
    ):
        return "UNKNOWN"

    ema19 = D(ema19)
    ema50 = D(ema50)
    ema200 = D(ema200)

    if (
        ema19 > ema50
        and
        ema50 > ema200
    ):
        return "LONG"

    if (
        ema19 < ema50
        and
        ema50 < ema200
    ):
        return "SHORT"

    return "NEUTRAL"


# ============================================================
# SIGNAL SNAPSHOT
# ============================================================

def build_signal_snapshot(
    candles,
    mark_price,
):

    ema_snapshot = build_ema_snapshot(
        candles
    )

    trend = determine_trend(
        ema_snapshot
    )

    return {
        "symbol":
            SYMBOL,

        "mark_price":
            decimal_to_string(
                mark_price
            ),

        "ema":
            ema_snapshot,

        "trend":
            trend,

        "timestamp":
            now_iso(),
    }


# ============================================================
# CLUSTER DISTANCE
# ============================================================

def cluster_distance_percent(
    price_a,
    price_b,
):

    price_a = D(price_a)
    price_b = D(price_b)

    if (
        price_a <= 0
        or
        price_b <= 0
    ):
        return None

    return (
        abs(
            price_a
            -
            price_b
        )
        /
        (
            (
                price_a
                +
                price_b
            )
            /
            D("2")
        )
        *
        D("100")
    )


# ============================================================
# CLUSTER MEMBERSHIP
# ============================================================

def is_cluster_match(
    price_a,
    price_b,
):

    distance = cluster_distance_percent(
        price_a,
        price_b,
    )

    if distance is None:
        return False

    return (
        distance
        <=
        CLUSTER_TOLERANCE_PERCENT
    )


# ============================================================
# HIGH CLUSTER BUILD
# ============================================================

def build_high_clusters(
    candles,
    entry_price,
):

    entry_price = D(
        entry_price
    )

    candidates = []

    for candle in candles:

        high = D(
            candle["high"]
        )

        if high <= entry_price:
            continue

        candidates.append(
            {
                "timestamp":
                    candle["timestamp"],

                "price":
                    high,
            }
        )

    candidates.sort(
        key=lambda item:
            item["price"]
    )

    clusters = []

    for candidate in candidates:

        matched = False

        for cluster in clusters:

            if is_cluster_match(
                candidate["price"],
                cluster["average"],
            ):

                cluster[
                    "prices"
                ].append(
                    candidate["price"]
                )

                cluster[
                    "timestamps"
                ].append(
                    candidate["timestamp"]
                )

                cluster[
                    "average"
                ] = (
                    sum(
                        cluster[
                            "prices"
                        ]
                    )
                    /
                    D(
                        len(
                            cluster[
                                "prices"
                            ]
                        )
                    )
                )

                matched = True
                break

        if not matched:

            clusters.append(
                {
                    "prices": [
                        candidate["price"]
                    ],

                    "timestamps": [
                        candidate["timestamp"]
                    ],

                    "average":
                        candidate["price"],
                }
            )

    valid = [
        cluster
        for cluster in clusters
        if len(
            cluster["prices"]
        )
        >=
        MIN_CLUSTER_TOUCHES
    ]

    valid.sort(
        key=lambda cluster:
            cluster["average"]
    )

    return valid


# ============================================================
# LOW CLUSTER BUILD
# ============================================================

def build_low_clusters(
    candles,
    entry_price,
):

    entry_price = D(
        entry_price
    )

    candidates = []

    for candle in candles:

        low = D(
            candle["low"]
        )

        if low >= entry_price:
            continue

        candidates.append(
            {
                "timestamp":
                    candle["timestamp"],

                "price":
                    low,
            }
        )

    candidates.sort(
        key=lambda item:
            item["price"],
        reverse=True,
    )

    clusters = []

    for candidate in candidates:

        matched = False

        for cluster in clusters:

            if is_cluster_match(
                candidate["price"],
                cluster["average"],
            ):

                cluster[
                    "prices"
                ].append(
                    candidate["price"]
                )

                cluster[
                    "timestamps"
                ].append(
                    candidate["timestamp"]
                )

                cluster[
                    "average"
                ] = (
                    sum(
                        cluster[
                            "prices"
                        ]
                    )
                    /
                    D(
                        len(
                            cluster[
                                "prices"
                            ]
                        )
                    )
                )

                matched = True
                break

        if not matched:

            clusters.append(
                {
                    "prices": [
                        candidate["price"]
                    ],

                    "timestamps": [
                        candidate["timestamp"]
                    ],

                    "average":
                        candidate["price"],
                }
            )

    valid = [
        cluster
        for cluster in clusters
        if len(
            cluster["prices"]
        )
        >=
        MIN_CLUSTER_TOUCHES
    ]

    valid.sort(
        key=lambda cluster:
            cluster["average"],
        reverse=True,
    )

    return valid
