#!/usr/bin/env python3
"""
R36F.5.2 - SMALLEST SYNTHETIC-TEST CORRECTION

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

STAGE = "R36F.5.2"

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

        for key in (
            "price",
            "markPrice",
        ):

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
# ABSOLUTE WRITE FIREBREAK
# ============================================================

def write_firebreak(*args, **kwargs):

    raise RuntimeError(
        "ABSOLUTE WRITE FIREBREAK: "
        "exchange mutation is disabled in "
        f"{STAGE}"
    )


place_order = write_firebreak
change_leverage = write_firebreak
change_margin_mode = write_firebreak
close_position = write_firebreak


# ============================================================
# WEEX RECONCILIATION
# ============================================================

async def reconcile_weex():

    global MARK_PRICE
    global AVAILABLE_BALANCE
    global OPEN_POSITIONS
    global WEEX_CONFIG

    async with aiohttp.ClientSession() as session:

        # IMPORTANT: use the dedicated WEEX MARK-price endpoint.
        # bookTicker returns bid/ask data and is not a mark-price source.

        MARK_PRICE = await weex_mark_price(
            session
        )

        log(
            "WEEX MARK PRICE = "
            + decimal_to_string(MARK_PRICE)
        )

        balance_response = await weex_private_get(
            session,
            "/capi/v3/account/balance",
        )

        balance = None

        def find_balance(value):

            nonlocal balance

            if balance is not None:
                return

            if isinstance(value, dict):

                for key in (
                    "availableBalance",
                    "available",
                    "availableMargin",
                    "balance",
                    "equity",
                ):

                    if key in value:

                        try:
                            balance = D(
                                value[key]
                            )

                            return

                        except Exception:
                            pass

                for item in value.values():
                    find_balance(item)

            elif isinstance(value, list):

                for item in value:
                    find_balance(item)

        find_balance(
            balance_response
        )

        if balance is None:
            raise RuntimeError(
                "Unable to extract WEEX available balance"
            )

        AVAILABLE_BALANCE = balance

        log(
            "AVAILABLE USDT = "
            + decimal_to_string(
                AVAILABLE_BALANCE
            )
        )

        positions_response = await weex_private_get(
            session,
            "/capi/v3/account/position",
            params={
                "symbol": SYMBOL
            },
        )

        OPEN_POSITIONS = []

        if isinstance(
            positions_response,
            dict,
        ):

            candidate = positions_response.get(
                "data"
            )

            if isinstance(candidate, list):
                OPEN_POSITIONS = candidate

            elif isinstance(candidate, dict):
                OPEN_POSITIONS = [
                    candidate
                ]

        elif isinstance(
            positions_response,
            list,
        ):

            OPEN_POSITIONS = positions_response

        log(
            f"OPEN POSITIONS = "
            f"{len(OPEN_POSITIONS)}"
        )

        WEEX_CONFIG = await weex_private_get(
            session,
            "/capi/v3/market/exchangeInfo",
        )

        log(
            "WEEX EXCHANGE CONFIG READ = PASS"
        )

    check(
        "WEEX_INITIAL_POSITION_FLAT",
        len(OPEN_POSITIONS) == 0,
        f"open_positions={len(OPEN_POSITIONS)}",
    )

    check(
        "MARGIN_MODE_CONTRACT",
        MARGIN_MODE == "ISOLATED",
        f"expected={MARGIN_MODE}",
    )

    check(
        "LONG_LEVERAGE_CONTRACT",
        LEVERAGE_LONG == Decimal("100"),
        f"expected={LEVERAGE_LONG}",
    )

    check(
        "SHORT_LEVERAGE_CONTRACT",
        LEVERAGE_SHORT == Decimal("100"),
        f"expected={LEVERAGE_SHORT}",
    )

    return True


# ============================================================
# CANARY PREVIEW
# ============================================================

def build_canary_preview():

    if MARK_PRICE is None:
        raise RuntimeError(
            "MARK_PRICE unavailable"
        )

    if AVAILABLE_BALANCE is None:
        raise RuntimeError(
            "AVAILABLE_BALANCE unavailable"
        )

    margin = (
        AVAILABLE_BALANCE
        * ENTRY_MARGIN_PERCENT
        / Decimal("100")
    )

    notional = (
        margin
        * LEVERAGE_LONG
    )

    quantity = quantize_down(
        notional / MARK_PRICE,
        QUANTITY_STEP,
    )

    if quantity < MIN_QUANTITY:
        raise RuntimeError(
            "Canary quantity below minimum"
        )

    return {
        "stage": STAGE,
        "symbol": SYMBOL,
        "side": "LONG",
        "mark_price": MARK_PRICE,
        "available_balance": AVAILABLE_BALANCE,
        "entry_margin_percent":
            ENTRY_MARGIN_PERCENT,
        "leverage":
            LEVERAGE_LONG,
        "margin":
            margin,
        "notional":
            notional,
        "quantity":
            quantity,
        "order_submission":
            False,
        "real_order_execution":
            False,
        "demo_order_execution":
            False,
    }


# ============================================================
# HISTORICAL KLINE HELPERS
# ============================================================

def normalize_kline(row):

    if not isinstance(row, (list, tuple)):
        raise ValueError(
            "Kline row must be list or tuple"
        )

    if len(row) < 6:
        raise ValueError(
            "Kline row has fewer than 6 fields"
        )

    return [
        row[0],
        D(row[1]),
        D(row[2]),
        D(row[3]),
        D(row[4]),
        D(row[5]),
    ]


def extract_kline_rows(payload):

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):

        for key in (
            "data",
            "rows",
            "result",
            "list",
        ):

            value = payload.get(key)

            if isinstance(value, list):
                return value

    raise RuntimeError(
        "Unable to extract historical kline rows"
    )


# ============================================================
# WEEX HISTORICAL KLINES
# ============================================================

async def fetch_historical_klines():

    all_rows = []

    async with aiohttp.ClientSession() as session:

        for page in range(
            MAX_HISTORICAL_PAGES
        ):

            params = {
                "symbol": SYMBOL,
                "interval": KLINE_INTERVAL,
                "limit": HISTORICAL_LIMIT,
            }

            payload = await http_get_json(
                session,
                API_BASE_URL
                + "/capi/v3/market/klines",
                params=params,
            )

            rows = extract_kline_rows(
                payload
            )

            if not rows:
                break

            all_rows.extend(rows)

            if len(rows) < HISTORICAL_LIMIT:
                break

            break

    normalized = []

    for row in all_rows:
        try:
            normalized.append(
                normalize_kline(row)
            )
        except Exception:
            continue

    if not normalized:
        raise RuntimeError(
            "No usable historical klines"
        )

    normalized = normalized[
        -HISTORICAL_LIMIT:
    ]

    log(
        "HISTORICAL KLINES LOADED = "
        + str(len(normalized))
    )

    return normalized


# ============================================================
# EXTREMA EXTRACTION
# ============================================================

def historical_highs(rows):

    highs = []

    for row in rows:

        try:
            highs.append(
                D(row[2])
            )
        except Exception:
            continue

    return highs


def historical_lows(rows):

    lows = []

    for row in rows:

        try:
            lows.append(
                D(row[3])
            )
        except Exception:
            continue

    return lows


def build_extrema(values):

    extrema = []

    if not values:
        return extrema

    for index, value in enumerate(values):

        left = (
            values[index - 1]
            if index > 0
            else value
        )

        right = (
            values[index + 1]
            if index + 1 < len(values)
            else value
        )

        if value >= left and value >= right:
            extrema.append(
                {
                    "index": index,
                    "price": value,
                    "type": "HIGH",
                }
            )

        elif value <= left and value <= right:
            extrema.append(
                {
                    "index": index,
                    "price": value,
                    "type": "LOW",
                }
            )

    return extrema


# ============================================================
# HISTORICAL CLUSTERING
# ============================================================

def cluster_extrema(
    extrema,
    tolerance_percent=None,
):

    if tolerance_percent is None:
        tolerance_percent = (
            CLUSTER_TOLERANCE_PERCENT
        )

    clusters = []

    for item in extrema:

        price = D(
            item["price"]
        )

        placed = False

        for cluster in clusters:

            average = D(
                cluster["average"]
            )

            tolerance = (
                average
                * tolerance_percent
                / Decimal("100")
            )

            if abs(
                price - average
            ) <= tolerance:

                cluster["prices"].append(
                    price
                )

                cluster["indices"].append(
                    item["index"]
                )

                cluster["types"].append(
                    item["type"]
                )

                cluster["average"] = (
                    sum(
                        cluster["prices"],
                        Decimal("0"),
                    )
                    / Decimal(
                        str(
                            len(
                                cluster["prices"]
                            )
                        )
                    )
                )

                placed = True
                break

        if not placed:

            clusters.append(
                {
                    "average": price,
                    "prices": [price],
                    "indices": [
                        item["index"]
                    ],
                    "types": [
                        item["type"]
                    ],
                }
            )

    return clusters


# ============================================================
# VALID CLUSTER FILTER
# ============================================================

def validate_clusters(
    clusters,
    entry_price,
    direction,
):

    valid = []
    invalid = []

    entry_price = D(
        entry_price
    )

    for cluster in clusters:

        average = D(
            cluster["average"]
        )

        touches = len(
            cluster["prices"]
        )

        if touches < MIN_CLUSTER_TOUCHES:

            invalid.append(
                {
                    **cluster,
                    "valid": False,
                    "reason":
                        "INSUFFICIENT_TOUCHES",
                }
            )

            continue

        if direction == "LONG":

            if average <= entry_price:

                invalid.append(
                    {
                        **cluster,
                        "valid": False,
                        "reason":
                            "WRONG_ENTRY_SIDE",
                    }
                )

                continue

        elif direction == "SHORT":

            if average >= entry_price:

                invalid.append(
                    {
                        **cluster,
                        "valid": False,
                        "reason":
                            "WRONG_ENTRY_SIDE",
                    }
                )

                continue

        else:

            invalid.append(
                {
                    **cluster,
                    "valid": False,
                    "reason":
                        "INVALID_DIRECTION",
                }
            )

            continue

        valid.append(
            {
                **cluster,
                "valid": True,
                "reason": "VALID",
            }
        )

    valid.sort(
        key=lambda item:
            D(item["average"])
    )

    return valid, invalid


# ============================================================
# TP APPROVAL
# ============================================================

def approve_tp_set(
    valid_clusters,
):

    valid_count = len(
        valid_clusters
    )

    if valid_count < REQUIRED_TP_CLUSTERS:

        return {
            "status": "REJECTED",
            "valid_cluster_count":
                valid_count,
            "required_cluster_count":
                REQUIRED_TP_CLUSTERS,
            "reason":
                "ONLY_ONE_VALID_CLUSTER"
                if valid_count == 1
                else "INSUFFICIENT_VALID_CLUSTERS",
        }

    return {
        "status": "APPROVED",
        "valid_cluster_count":
            valid_count,
        "required_cluster_count":
            REQUIRED_TP_CLUSTERS,
        "reason":
            "MINIMUM_TWO_VALID_CLUSTERS",
    }


# ============================================================
# TP PRICE CALCULATION
# ============================================================

def calculate_tp_prices(
    entry_price,
    valid_clusters,
    direction,
):

    entry_price = D(
        entry_price
    )

    if len(valid_clusters) < REQUIRED_TP_CLUSTERS:
        raise RuntimeError(
            "Cannot calculate complete TP set: "
            "fewer than two valid historical clusters"
        )

    cluster1 = D(
        valid_clusters[0]["average"]
    )

    cluster2 = D(
        valid_clusters[1]["average"]
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
        "tp1": quantize_down(
            tp1,
            PRICE_STEP,
        ),
        "tp2": quantize_down(
            tp2,
            PRICE_STEP,
        ),
        "tp3": {
            "type": "TRAILING",
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

    approval = approve_tp_set(
        valid
    )

    result = {
        "direction":
            direction,

        "entry_price":
            D(entry_price),

        "extrema_count":
            len(extrema),

        "cluster_count":
            len(clusters),

        "valid_cluster_count":
            len(valid),

        "invalid_cluster_count":
            len(invalid),

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,

        "tp_approval":
            approval,
    }

    if approval["status"] == "APPROVED":

        result["tp_prices"] = (
            calculate_tp_prices(
                entry_price,
                valid,
                direction,
            )
        )

    else:

        result["tp_prices"] = None

    return result


# ============================================================
# SYNTHETIC LONG FIXTURE
# ============================================================

def synthetic_long_rows():

    rows = []

    highs = [
        D("100000"),
        D("100400"),
        D("100400"),
        D("100400"),
        D("100900"),
        D("100900"),
        D("100900"),
        D("99000"),
    ]

    for i, high in enumerate(highs):

        rows.append(
            [
                i,
                high - D("300"),
                high,
                high - D("500"),
                high - D("100"),
                "1",
            ]
        )

    return rows


# ============================================================
# SYNTHETIC SHORT FIXTURE
# ============================================================

def synthetic_short_rows():

    rows = []

    support_groups = [
        D("99500"),
        D("99500"),
        D("99500"),
        D("99000"),
        D("99000"),
        D("99000"),
    ]

    for i, low in enumerate(
        support_groups
    ):

        rows.append(
            [
                i,
                low + D("300"),
                low + D("500"),
                low,
                low + D("100"),
                "1",
            ]
        )

    return rows


# ============================================================
# SYNTHETIC ONE-CLUSTER FIXTURE
# ============================================================

def synthetic_one_cluster_rows():

    rows = []

    highs = [
        D("100400"),
        D("100400"),
        D("100400"),
        D("99000"),
    ]

    for i, high in enumerate(highs):

        rows.append(
            [
                i,
                high - D("300"),
                high,
                high - D("500"),
                high - D("100"),
                "1",
            ]
        )

    return rows


# ============================================================
# SYNTHETIC TESTS
# ============================================================

def run_synthetic_tests():

    global SHORT_DIAGNOSTICS
    global LONG_DIAGNOSTICS
    global LAST_TP_APPROVAL

    line()

    log(
        f"{STAGE}: SYNTHETIC TEST SUITE START"
    )

    # --------------------------------------------------------
    # LONG
    # --------------------------------------------------------

    long_rows = synthetic_long_rows()

    long_diagnostics = run_tp_engine(
        long_rows,
        D("100000"),
        "LONG",
    )

    LONG_DIAGNOSTICS = (
        long_diagnostics
    )

    log(
        "LONG EXTREMA COUNT = "
        + str(
            long_diagnostics[
                "extrema_count"
            ]
        )
    )

    log(
        "LONG CLUSTER COUNT = "
        + str(
            long_diagnostics[
                "cluster_count"
            ]
        )
    )

    log(
        "LONG VALID CLUSTER COUNT = "
        + str(
            long_diagnostics[
                "valid_cluster_count"
            ]
        )
    )

    check(
        "SYNTHETIC_LONG_MINIMUM_TWO_VALID_CLUSTERS",
        long_diagnostics[
            "valid_cluster_count"
        ] >= REQUIRED_TP_CLUSTERS,
        (
            "long synthetic fixture must produce at least "
            + str(REQUIRED_TP_CLUSTERS)
            + " valid clusters"
        ),
    )

    check(
        "SYNTHETIC_LONG_TP_APPROVED",
        long_diagnostics[
            "tp_approval"
        ]["status"] == "APPROVED",
        "long TP approval must be APPROVED",
    )

    check(
        "SYNTHETIC_LONG_TWO_CLUSTERS",
        len(
            long_diagnostics[
                "valid_clusters"
            ]
        ) >= REQUIRED_TP_CLUSTERS,
        "long must contain TP1 and TP2 historical clusters",
    )

    if long_diagnostics[
        "tp_prices"
    ]:

        log(
            "LONG TP1 = "
            + decimal_to_string(
                long_diagnostics[
                    "tp_prices"
                ]["tp1"]
            )
        )

        log(
            "LONG TP2 = "
            + decimal_to_string(
                long_diagnostics[
                    "tp_prices"
                ]["tp2"]
            )
        )

    # --------------------------------------------------------
    # SHORT
    # --------------------------------------------------------

    short_rows = synthetic_short_rows()

    short_diagnostics = run_tp_engine(
        short_rows,
        D("100000"),
        "SHORT",
    )

    SHORT_DIAGNOSTICS = (
        short_diagnostics
    )

    LAST_TP_APPROVAL = (
        short_diagnostics[
            "tp_approval"
        ]
    )

    log(
        "SHORT EXTREMA COUNT = "
        + str(
            short_diagnostics[
                "extrema_count"
            ]
        )
    )

    log(
        "SHORT CLUSTER COUNT = "
        + str(
            short_diagnostics[
                "cluster_count"
            ]
        )
    )

    log(
        "SHORT VALID CLUSTER COUNT = "
        + str(
            short_diagnostics[
                "valid_cluster_count"
            ]
        )
    )

    check(
        "SYNTHETIC_SHORT_MINIMUM_TWO_VALID_CLUSTERS",
        short_diagnostics[
            "valid_cluster_count"
        ] >= REQUIRED_TP_CLUSTERS,
        (
            "short synthetic fixture must produce at least "
            + str(REQUIRED_TP_CLUSTERS)
            + " valid clusters"
        ),
    )

    check(
        "SYNTHETIC_SHORT_TP_APPROVED",
        short_diagnostics[
            "tp_approval"
        ]["status"] == "APPROVED",
        "short TP approval must be APPROVED",
    )

    check(
        "SYNTHETIC_SHORT_TWO_CLUSTERS",
        len(
            short_diagnostics[
                "valid_clusters"
            ]
        ) >= REQUIRED_TP_CLUSTERS,
        "short must contain TP1 and TP2 historical clusters",
    )

    check(
        "SYNTHETIC_SHORT_EXACTLY_TWO_VALID_CLUSTERS",
        short_diagnostics[
            "valid_cluster_count"
        ] == REQUIRED_TP_CLUSTERS,
        (
            "synthetic short fixture must deterministically produce exactly "
            + str(REQUIRED_TP_CLUSTERS)
            + " valid clusters"
        ),
    )

    if short_diagnostics[
        "tp_prices"
    ]:

        log(
            "SHORT TP1 = "
            + decimal_to_string(
                short_diagnostics[
                    "tp_prices"
                ]["tp1"]
            )
        )

        log(
            "SHORT TP2 = "
            + decimal_to_string(
                short_diagnostics[
                    "tp_prices"
                ]["tp2"]
            )
        )

    # --------------------------------------------------------
    # ONE-CLUSTER REJECTION
    # --------------------------------------------------------

    one_cluster_rows = (
        synthetic_one_cluster_rows()
    )

    one_cluster = run_tp_engine(
        one_cluster_rows,
        D("100000"),
        "LONG",
    )

    check(
        "ONE_CLUSTER_TP_REJECTED",
        one_cluster[
            "tp_approval"
        ]["status"] == "REJECTED",
        "one valid historical cluster must reject complete TP set",
    )

    check(
        "ONE_CLUSTER_APPROVAL_STATUS_REJECTED",
        one_cluster[
            "valid_cluster_count"
        ] < REQUIRED_TP_CLUSTERS,
        (
            "one-cluster fixture must remain below required "
            "historical-cluster threshold"
        ),
    )

    check(
        "ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET",
        one_cluster[
            "tp_prices"
        ] is None,
        "missing second cluster must not fabricate TP2",
    )

    return (
        long_diagnostics,
        short_diagnostics,
        one_cluster,
    )


# ============================================================
# TP CONTRACT TESTS
# ============================================================

def run_tp_contract_tests():

    line()

    log(
        "TP CONTRACT TESTS START"
    )

    long_rows = synthetic_long_rows()

    long_result = run_tp_engine(
        long_rows,
        D("100000"),
        "LONG",
    )

    short_rows = synthetic_short_rows()

    short_result = run_tp_engine(
        short_rows,
        D("100000"),
        "SHORT",
    )

    # --------------------------------------------------------
    # PRIMARY TP IMMUTABILITY
    # --------------------------------------------------------

    check(
        "PRIMARY_TP_IMMUTABLE_CONTRACT",
        (
            long_result[
                "tp_prices"
            ] is not None
            and
            short_result[
                "tp_prices"
            ] is not None
            and
            long_result[
                "tp_prices"
            ]["tp1"]
            ==
            D("100080")
            and
            long_result[
                "tp_prices"
            ]["tp2"]
            ==
            D("100450")
            and
            short_result[
                "tp_prices"
            ]["tp1"]
            ==
            D("99900")
            and
            short_result[
                "tp_prices"
            ]["tp2"]
            ==
            D("99500")
        ),
        "primary TP1/TP2 historical calculations remain unchanged",
    )

    # --------------------------------------------------------
    # BACKUP TP CONTRACT
    # --------------------------------------------------------

    backup_valid_clusters = (
        long_result[
            "valid_clusters"
        ]
    )

    check(
        "BACKUP_TP_RECALC_CONTRACT",
        (
            len(
                backup_valid_clusters
            ) >= 2
            and
            calculate_tp_prices(
                D("100000"),
                backup_valid_clusters,
                "LONG",
            )["tp1"]
            ==
            D("100080")
        ),
        "backup TP recalculation preserves primary TP contract",
    )

    line()

    return True
# ============================================================
# R36F.5.2 SYNTHETIC LONG DATA
#
# CORRECTION:
# Deliberately separated resistance groups.
#
# Group 1:
#   approximately 100500
#
# Group 2:
#   approximately 101000
#
# Both groups contain multiple local highs.
# ============================================================

def synthetic_long_rows():

    base = [
        100000,
        100200,

        100500,
        100100,
        100490,
        100150,
        100510,

        100250,
        100800,

        101000,
        100850,
        100980,
        100820,
        101020,

        100700,
    ]

    rows = []

    for i, high in enumerate(base):

        rows.append(
            [
                i,

                str(
                    D(high)
                    - Decimal("500")
                ),

                str(
                    D(high)
                    - Decimal("100")
                ),

                str(
                    D(high)
                ),

                str(
                    D(high)
                    - Decimal("300")
                ),

                "1",
            ]
        )

    return rows


# ============================================================
# R36F.5.2 SYNTHETIC SHORT DATA
#
# CORRECTION:
# Deliberately separated support groups.
#
# Group 1:
#   approximately 99500
#
# Group 2:
#   approximately 99000
#
# Both groups contain multiple local lows.
# ============================================================

def synthetic_short_rows():

    base = [
        100000,
        99800,

        99500,
        99800,
        99490,
        99700,
        99510,

        99700,
        99200,

        99000,
        99200,
        98980,
        99150,
        99020,

        99400,
    ]

    rows = []

    for i, low in enumerate(base):

        rows.append(
            [
                i,

                str(
                    D(low)
                    + Decimal("300")
                ),

                str(
                    D(low)
                    + Decimal("500")
                ),

                str(
                    D(low)
                ),

                str(
                    D(low)
                    + Decimal("100")
                ),

                "1",
            ]
        )

    return rows


# ============================================================
# SYNTHETIC CLUSTER TESTS
# ============================================================

def synthetic_cluster_tests():

    entry = Decimal("100000")

    # --------------------------------------------------------
    # LONG
    # --------------------------------------------------------

    long_rows = synthetic_long_rows()

    long_diagnostics = build_cluster_diagnostics(
        long_rows,
        entry,
        "LONG",
    )

    check(
        "SYNTHETIC_LONG_MINIMUM_TWO_VALID_CLUSTERS",
        long_diagnostics[
            "valid_cluster_count"
        ] >= REQUIRED_TP_CLUSTERS,
        (
            "expected_at_least="
            + str(REQUIRED_TP_CLUSTERS)
            + " actual="
            + str(
                long_diagnostics[
                    "valid_cluster_count"
                ]
            )
        ),
    )

    long_snapshot = build_cluster_tp_snapshot(
        entry,
        long_rows,
        "LONG",
        "SYNTHETIC_LONG_FILL",
    )

    check(
        "SYNTHETIC_LONG_TP_APPROVED",
        long_snapshot[
            "tp_approval"
        ][
            "approved"
        ] is True,
    )

    check(
        "SYNTHETIC_LONG_TWO_CLUSTERS",
        long_snapshot[
            "available_valid_clusters"
        ] >= REQUIRED_TP_CLUSTERS,
    )

    long_tp1 = D(
        long_snapshot[
            "tp1"
        ][
            "price"
        ]
    )

    long_tp2 = D(
        long_snapshot[
            "tp2"
        ][
            "price"
        ]
    )

    check(
        "SYNTHETIC_LONG_TP_ORDERING",
        entry
        < long_tp1
        < long_tp2,
    )

    # --------------------------------------------------------
    # SHORT
    # --------------------------------------------------------

    short_rows = synthetic_short_rows()

    short_diagnostics = build_cluster_diagnostics(
        short_rows,
        entry,
        "SHORT",
    )

    check(
        "SYNTHETIC_SHORT_MINIMUM_TWO_VALID_CLUSTERS",
        short_diagnostics[
            "valid_cluster_count"
        ] >= REQUIRED_TP_CLUSTERS,
        (
            "expected_at_least="
            + str(REQUIRED_TP_CLUSTERS)
            + " actual="
            + str(
                short_diagnostics[
                    "valid_cluster_count"
                ]
            )
        ),
    )

    short_snapshot = build_cluster_tp_snapshot(
        entry,
        short_rows,
        "SHORT",
        "SYNTHETIC_SHORT_FILL",
    )

    check(
        "SYNTHETIC_SHORT_TP_APPROVED",
        short_snapshot[
            "tp_approval"
        ][
            "approved"
        ] is True,
    )

    check(
        "SYNTHETIC_SHORT_TWO_CLUSTERS",
        short_snapshot[
            "available_valid_clusters"
        ] >= REQUIRED_TP_CLUSTERS,
    )

    short_tp1 = D(
        short_snapshot[
            "tp1"
        ][
            "price"
        ]
    )

    short_tp2 = D(
        short_snapshot[
            "tp2"
        ][
            "price"
        ]
    )

    check(
        "SYNTHETIC_SHORT_TP_ORDERING",
        entry
        > short_tp1
        > short_tp2,
    )

    check(
        "SYNTHETIC_SHORT_EXACTLY_TWO_VALID_CLUSTERS",
        short_diagnostics[
            "valid_cluster_count"
        ] == REQUIRED_TP_CLUSTERS,
        "synthetic short fixture must deterministically produce exactly "
        + str(REQUIRED_TP_CLUSTERS)
        + " valid clusters",
    )

    # --------------------------------------------------------
    # IMMUTABILITY CONTRACTS
    # --------------------------------------------------------

    check(
        "PRIMARY_TP_IMMUTABLE_CONTRACT",
        (
            long_snapshot[
                "primary_tp_immutable"
            ] is True
            and
            short_snapshot[
                "primary_tp_immutable"
            ] is True
        ),
    )

    check(
        "BACKUP_TP_RECALC_CONTRACT",
        (
            long_snapshot[
                "backup_tp_recalculated_only_on_backup_fill"
            ] is True
            and
            short_snapshot[
                "backup_tp_recalculated_only_on_backup_fill"
            ] is True
        ),
    )

    return (
        long_snapshot,
        short_snapshot,
    )


# ============================================================
# SYNTHETIC TP REJECTION TEST
# ============================================================

def synthetic_tp_rejection_test():

    entry = Decimal("100000")

    # Only one valid historical-high cluster.
    # This MUST NOT approve the TP1 + TP2 set.

    rows = [

        [
            0,
            "99500",
            "99900",
            "100100",
            "99800",
            "1",
        ],

        [
            1,
            "99900",
            "99950",
            "100550",
            "99900",
            "1",
        ],

        [
            2,
            "99900",
            "100000",
            "100000",
            "99900",
            "1",
        ],

        [
            3,
            "99900",
            "99950",
            "100540",
            "99900",
            "1",
        ],

        [
            4,
            "99500",
            "99900",
            "100100",
            "99800",
            "1",
        ],
    ]

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
# WRITER REQUEST PREVIEW
# ============================================================

def build_writer_request_preview(
    side,
    entry_price,
    quantity,
    tp_snapshot,
):

    return {

        "stage":
            STAGE,

        "symbol":
            SYMBOL,

        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "quantity":
            decimal_to_string(
                quantity
            ),

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

        "primary_tp_immutable":
            True,

        "submitted":
            False,

        "transport_enabled":
            EXCHANGE_MUTATION_TRANSPORT_ENABLED,
    }


# ============================================================
# MAIN R36F.5.2 TEST
# ============================================================

async def run_r36f52():

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
        EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
    )

    check(
        "ORDER_SUBMISSION_DISABLED",
        ORDER_SUBMISSION_ENABLED is False,
    )

    check(
        "LEVERAGE_MUTATION_DISABLED",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "MARGIN_MODE_MUTATION_DISABLED",
        MARGIN_MODE_MUTATION_ENABLED is False,
    )

    check(
        "POSITION_MUTATION_DISABLED",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "FIRST_REAL_ORDER_DISABLED",
        FIRST_REAL_ORDER_ALLOWED is False,
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
        "R36A_DURABLE_ID_PRESENT",
        R36A_EVIDENCE_OK,
        f"expected={OLD_R36A_UPDATE_ID}",
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
        "R36C_DURABLE_ID_PRESENT",
        R36C_EVIDENCE_OK,
        f"expected={R36C_UPDATE_ID}",
    )

    # ========================================================
    # R36D SNAPSHOT
    # ========================================================

    r36d_snapshot = read_json_file(
        R36D_SNAPSHOT_FILE,
        {},
    )

    R36D_EVIDENCE_OK = bool(
        r36d_snapshot
    )

    check(
        "R36D_SNAPSHOT_PRESENT",
        R36D_EVIDENCE_OK,
    )

    DURABLE_EVIDENCE_OK = (
        R36A_EVIDENCE_OK
        and R36C_EVIDENCE_OK
        and R36D_EVIDENCE_OK
    )

    # ========================================================
    # API CREDENTIAL PRESENCE
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
    # FROZEN DIAGNOSTIC:
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
            len(historical_rows) >= 3,
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
    # ========================================================

    real_long_snapshot = None

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

            check(
                "REAL_LONG_TP_PREVIEW",
                real_long_snapshot[
                    "tp_approval"
                ][
                    "approved"
                ] is True,

                "TP_APPROVAL="
                + real_long_snapshot[
                    "tp_approval"
                ][
                    "status"
                ],
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

            check(
                "REAL_LONG_TP_PREVIEW",
                False,

                "TP_APPROVAL="
                + approval[
                    "status"
                ]
                + " reason="
                + approval[
                    "reason"
                ]
                + " error="
                + str(exc),
            )

    # ========================================================
    # REAL SHORT TP PREVIEW
    # ========================================================

    real_short_snapshot = None

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

            check(
                "REAL_SHORT_TP_PREVIEW",
                real_short_snapshot[
                    "tp_approval"
                ][
                    "approved"
                ] is True,

                "TP_APPROVAL="
                + real_short_snapshot[
                    "tp_approval"
                ][
                    "status"
                ],
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

            check(
                "REAL_SHORT_TP_PREVIEW",
                False,

                "TP_APPROVAL="
                + approval[
                    "status"
                ]
                + " reason="
                + approval[
                    "reason"
                ]
                + " error="
                + str(exc),
            )

    # ========================================================
    # FROZEN DIAGNOSTIC:
    # CANARY PREVIEW
    # ========================================================

    canary_preview = None
