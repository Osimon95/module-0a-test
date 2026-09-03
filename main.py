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
            "/capi/v3/account/position/singlePosition",
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

    raw_quantity = (
        notional
        / MARK_PRICE
    )

    quantity = quantize_down(
        raw_quantity,
        QUANTITY_STEP,
    )

    if quantity < MIN_QUANTITY:
        raise RuntimeError(
            "Canary quantity below minimum"
        )

    return {
        "symbol": SYMBOL,

        "mark_price":
            decimal_to_string(MARK_PRICE),

        "available_balance":
            decimal_to_string(
                AVAILABLE_BALANCE
            ),

        "entry_margin_percent":
            decimal_to_string(
                ENTRY_MARGIN_PERCENT
            ),

        "leverage":
            decimal_to_string(
                LEVERAGE_LONG
            ),

        "notional":
            decimal_to_string(notional),

        "quantity":
            decimal_to_string(quantity),

        "submitted":
            False,
    }


# ============================================================
# HISTORICAL KLINE EXTRACTION
# ============================================================

def extract_kline_rows(payload):

    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    for key in (
        "data",
        "rows",
        "result",
        "list",
    ):

        value = payload.get(key)

        if isinstance(value, list):
            return value

    return []


def kline_timestamp(row):

    if isinstance(row, dict):

        for key in (
            "timestamp",
            "time",
            "openTime",
            "open_time",
        ):

            if key in row:
                return int(
                    D(row[key])
                )

    elif isinstance(row, list):

        if len(row) >= 1:
            return int(
                D(row[0])
            )

    raise ValueError(
        "Unable to determine kline timestamp"
    )


def kline_high_low(row):

    if isinstance(row, dict):

        high = None
        low = None

        for key in (
            "high",
            "highPrice",
        ):

            if key in row:
                high = D(row[key])
                break

        for key in (
            "low",
            "lowPrice",
        ):

            if key in row:
                low = D(row[key])
                break

        if high is None or low is None:
            raise ValueError(
                "Unable to extract kline high/low"
            )

        return high, low

    if isinstance(row, list):

        if len(row) < 4:
            raise ValueError(
                "Kline row too short"
            )

        return (
            D(row[2]),
            D(row[3]),
        )

    raise ValueError(
        "Unsupported kline row"
    )


def normalize_kline_order(rows):

    return sorted(
        rows,
        key=kline_timestamp,
    )


# ============================================================
# HISTORICAL DATA
# ============================================================

async def historical_get(
    session,
    start_timestamp=None,
):

    url = (
        API_BASE_URL
        + "/capi/v3/market/klines"
    )

    params = {
        "symbol": SYMBOL,
        "interval": KLINE_INTERVAL,
        "limit": HISTORICAL_LIMIT,
    }

    if start_timestamp is not None:
        params["startTime"] = start_timestamp

    return await http_get_json(
        session,
        url,
        params=params,
    )


async def load_historical_klines():

    all_rows = {}

    async with aiohttp.ClientSession() as session:

        start_timestamp = None

        for page in range(
            MAX_HISTORICAL_PAGES
        ):

            payload = await historical_get(
                session,
                start_timestamp,
            )

            rows = extract_kline_rows(
                payload
            )

            if not rows:
                break

            for row in rows:

                try:
                    ts = kline_timestamp(row)
                    all_rows[ts] = row

                except Exception as exc:
                    log(
                        "HISTORICAL ROW SKIPPED: "
                        + str(exc)
                    )

            normalized = normalize_kline_order(
                list(all_rows.values())
            )

            if not normalized:
                break

            oldest_ts = kline_timestamp(
                normalized[0]
            )

            if (
                start_timestamp is not None
                and oldest_ts >= start_timestamp
            ):
                break

            start_timestamp = oldest_ts - 1

            if len(rows) < HISTORICAL_LIMIT:
                break

    result = normalize_kline_order(
        list(all_rows.values())
    )

    log(
        f"HISTORICAL KLINES LOADED = "
        f"{len(result)}"
    )

    return result


# ============================================================
# LOCAL EXTREMA
# ============================================================

def local_extrema_values(
    rows,
    side,
):

    values = []

    if len(rows) < 3:
        return values

    highs = []
    lows = []

    for row in rows:

        high, low = kline_high_low(row)

        highs.append(high)
        lows.append(low)

    if side == "LONG":

        for i in range(
            1,
            len(highs) - 1,
        ):

            if (
                highs[i] >= highs[i - 1]
                and highs[i] >= highs[i + 1]
            ):
                values.append(
                    highs[i]
                )

    elif side == "SHORT":

        for i in range(
            1,
            len(lows) - 1,
        ):

            if (
                lows[i] <= lows[i - 1]
                and lows[i] <= lows[i + 1]
            ):
                values.append(
                    lows[i]
                )

    else:

        raise ValueError(
            f"Unsupported side={side}"
        )

    return values


# ============================================================
# CLUSTER ENGINE
# ============================================================

def cluster_extrema(values):

    if not values:
        return []

    ordered = sorted(
        D(value)
        for value in values
    )

    clusters = []

    current = [ordered[0]]

    for value in ordered[1:]:

        average = (
            sum(current)
            / Decimal(len(current))
        )

        difference_percent = (
            abs(value - average)
            / average
            * Decimal("100")
        )

        if (
            difference_percent
            <= CLUSTER_TOLERANCE_PERCENT
        ):

            current.append(value)

        else:

            clusters.append(current)
            current = [value]

    clusters.append(current)

    result = []

    for cluster in clusters:

        average = (
            sum(cluster)
            / Decimal(len(cluster))
        )

        result.append({
            "average": average,
            "minimum": min(cluster),
            "maximum": max(cluster),
            "touches": len(cluster),
            "values": cluster,
        })

    return result


# ============================================================
# CLUSTER DIAGNOSTICS
# ============================================================

def build_cluster_diagnostics(
    rows,
    entry_price,
    side,
):

    entry_price = D(entry_price)

    extrema = local_extrema_values(
        rows,
        side,
    )

    clusters = cluster_extrema(
        extrema
    )

    cluster_records = []
    valid_clusters = []

    for index, cluster in enumerate(
        clusters,
        start=1,
    ):

        average = cluster["average"]
        touches = cluster["touches"]

        if side == "LONG":
            side_valid = average > entry_price
        else:
            side_valid = average < entry_price

        touches_valid = (
            touches >= MIN_CLUSTER_TOUCHES
        )

        valid = (
            touches_valid
            and side_valid
        )

        if valid:
            reason = "VALID"
        elif not touches_valid:
            reason = "INSUFFICIENT_CLUSTER_TOUCHES"
        elif not side_valid:
            reason = "WRONG_ENTRY_SIDE"
        else:
            reason = "REJECTED"

        record = {
            "cluster_number": index,

            "average":
                decimal_to_string(average),

            "minimum":
                decimal_to_string(
                    cluster["minimum"]
                ),

            "maximum":
                decimal_to_string(
                    cluster["maximum"]
                ),

            "touches":
                touches,

            "valid":
                valid,

            "reason":
                reason,
        }

        cluster_records.append(record)

        if valid:
            valid_clusters.append(cluster)

    if side == "LONG":

        valid_clusters.sort(
            key=lambda c: c["average"]
        )

    else:

        valid_clusters.sort(
            key=lambda c: c["average"],
            reverse=True,
        )

    valid_count = len(valid_clusters)

    if valid_count >= REQUIRED_TP_CLUSTERS:

        status = "ENOUGH_VALID_CLUSTERS"
        failure_reason = None

    elif valid_count == 1:

        status = "INSUFFICIENT_VALID_CLUSTERS"
        failure_reason = "ONLY_ONE_VALID_CLUSTER"

    elif not extrema:

        status = "NO_EXTREMA"
        failure_reason = "NO_EXTREMA"

    elif not clusters:

        status = "NO_EXTREMA_ON_REQUIRED_SIDE"
        failure_reason = "NO_EXTREMA_ON_REQUIRED_SIDE"

    else:

        status = "CLUSTERS_REJECTED_BY_POLICY"
        failure_reason = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    diagnostics = {
        "side": side,

        "entry_price":
            decimal_to_string(entry_price),

        "extrema_count":
            len(extrema),

        "cluster_count":
            len(clusters),

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

def evaluate_tp_approval(diagnostics):

    valid_count = int(
        diagnostics.get(
            "valid_cluster_count",
            0,
        )
    )

    if valid_count >= REQUIRED_TP_CLUSTERS:

        approval = {
            "status": "APPROVED",
            "approved": True,

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
            "status": "REJECTED",
            "approved": False,

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

    entry_price = D(entry_price)

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
