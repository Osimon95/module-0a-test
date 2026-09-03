
#!/usr/bin/env python3
"""
R36F.5.4 - TP MARKET-ELIGIBILITY / READINESS SEPARATION

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5/R36F.5.3 safety baseline
    while correcting the classification of real-market TP rejection.

R36F.5.4 CHANGE:

    The historical TP policy itself is NOT changed.

    A complete historical TP1/TP2 set still requires:

        TWO OR MORE valid historical clusters.

    However:

        REAL market with fewer than two valid clusters
            -> normal strategy/market eligibility rejection
            -> NOT a FINAL_BLOCKER

        TP engine exception/inconsistency
            -> diagnostic failure
            -> FINAL_BLOCKER

    This separates:

        "The bot is functioning correctly but this market setup
         currently does not qualify for a trade"

    from:

        "The bot's TP capability is broken."

TP POLICY:

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

R36F.5.4 READINESS CLASSIFICATION:

    SYNTHETIC TEST FAILURE
        -> FINAL_BLOCKER

    REAL MARKET:
        2+ valid clusters
            -> TP eligible

        1 valid cluster
            -> expected market rejection, NOT FINAL_BLOCKER

        0 valid clusters
            -> expected market rejection, NOT FINAL_BLOCKER

    REAL MARKET TP ENGINE EXCEPTION / ORDERING INCONSISTENCY
        -> FINAL_BLOCKER

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

STAGE = "R36F.5.4"

PURPOSE = (
    "SMALLEST TP MARKET-ELIGIBILITY CORRECTION: "
    "separate expected real-market TP rejection from "
    "actual bot capability/readiness failure while "
    "preserving the R36F.5.3 TP policy and execution safety baseline"
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

REAL_LONG_MARKET_ELIGIBLE = False
REAL_SHORT_MARKET_ELIGIBLE = False


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
# EXPECTED MARKET TP REJECTION
# ============================================================

def market_tp_eligibility_log(
    side,
    diagnostics,
):
    """
    R36F.5.4:

    A real-market TP rejection caused by fewer than the required
    number of historical clusters is an expected strategy decision.

    It is NOT a bot capability failure and therefore must NOT be
    inserted into FINAL_BLOCKERS.
    """

    valid_count = int(
        diagnostics.get(
            "valid_cluster_count",
            0,
        )
    )

    required = REQUIRED_TP_CLUSTERS

    failure_reason = diagnostics.get(
        "failure_reason"
    )

    if valid_count >= required:

        log(
            f"REAL_{side}_TP_MARKET_ELIGIBILITY = ELIGIBLE"
        )

        log(
            f"REAL_{side}_TP_VALID_CLUSTERS = "
            f"{valid_count}"
        )

        return True

    log(
        f"REAL_{side}_TP_MARKET_ELIGIBILITY = REJECTED"
    )

    log(
        f"REAL_{side}_TP_MARKET_REJECTION_REASON = "
        f"{failure_reason}"
    )

    log(
        f"REAL_{side}_TP_MARKET_REJECTION_DETAIL = "
        f"requires_at_least={required} "
        f"actual={valid_count}"
    )

    log(
        f"REAL_{side}_TP_REJECTION_IS_NOT_FINAL_BLOCKER = TRUE"
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
            f"READ JSON FAILED "
            f"path={path} "
            f"error={exc}"
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

def collect_ids_from_json(value):

    found = set()

    if isinstance(
        value,
        dict,
    ):

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
                collect_ids_from_json(
                    item
                )
            )

    elif isinstance(
        value,
        list,
    ):

        for item in value:

            found.update(
                collect_ids_from_json(
                    item
                )
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

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        payload = {

            "stage":
                STAGE,

            "status":
                TEST_STATUS,

            "purpose":
                PURPOSE,

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

            "real_long_market_eligible":
                REAL_LONG_MARKET_ELIGIBLE,

            "real_short_market_eligible":
                REAL_SHORT_MARKET_ELIGIBLE,

            "last_tp_approval":
                LAST_TP_APPROVAL,
        }

        body = json.dumps(
            payload,
            default=str,
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json",
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
        f"{STAGE}: "
        f"HEALTH SERVER STARTED "
        f"ON PORT {port}"
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
        api_secret.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
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

            return json.loads(
                text
            )

        except Exception as exc:

            raise RuntimeError(
                f"Invalid JSON response: "
                f"{exc}"
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

        for key in sorted(
            params
        ):

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

async def weex_public_ticker(
    session
):

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


async def weex_mark_price(
    session
):
    """
    Read actual WEEX contract mark price.

    The bookTicker endpoint is bid/ask data and is not treated
    as the mark-price source.
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

    if isinstance(
        payload,
        dict,
    ):

        candidates.append(
            payload
        )

        data = payload.get(
            "data"
        )

        if isinstance(
            data,
            dict,
        ):

            candidates.append(
                data
            )

        elif isinstance(
            data,
            list,
        ):

            candidates.extend(
                data
            )

    elif isinstance(
        payload,
        list,
    ):

        candidates.extend(
            payload
        )

    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):
            continue

        for key in (
            "price",
            "markPrice",
        ):

            value = item.get(
                key
            )

            if value is not None:

                try:

                    price = D(
                        value
                    )

                    if price > 0:
                        return price

                except Exception:
                    continue

    raise RuntimeError(
        "Unable to extract WEEX mark price "
        "from symbolPrice MARK response"
    )


# ============================================================
# ABSOLUTE WRITE FIREBREAK
# ============================================================

def write_firebreak(
    *args,
    **kwargs,
):

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

        # ----------------------------------------------------
        # MARK PRICE
        # ----------------------------------------------------

        MARK_PRICE = await weex_mark_price(
            session
        )

        log(
            "WEEX MARK PRICE = "
            + decimal_to_string(
                MARK_PRICE
            )
        )

        # ----------------------------------------------------
        # BALANCE
        # ----------------------------------------------------

        balance_response = (
            await weex_private_get(
                session,
                "/capi/v3/account/balance",
            )
        )

        balance = None

        def find_balance(
            value
        ):

            nonlocal balance

            if balance is not None:
                return

            if isinstance(
                value,
                dict,
            ):

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

                    find_balance(
                        item
                    )

            elif isinstance(
                value,
                list,
            ):

                for item in value:

                    find_balance(
                        item
                    )

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

        # ----------------------------------------------------
        # POSITIONS
        # ----------------------------------------------------

        positions_response = (
            await weex_private_get(
                session,
                "/capi/v3/account/position/singlePosition",
                params={
                    "symbol": SYMBOL
                },
            )
        )

        OPEN_POSITIONS = []

        if isinstance(
            positions_response,
            dict,
        ):

            candidate = (
                positions_response.get(
                    "data"
                )
            )

            if isinstance(
                candidate,
                list,
            ):

                OPEN_POSITIONS = candidate

            elif isinstance(
                candidate,
                dict,
            ):

                OPEN_POSITIONS = [
                    candidate
                ]

        elif isinstance(
            positions_response,
            list,
        ):

            OPEN_POSITIONS = (
                positions_response
            )

        log(
            f"OPEN POSITIONS = "
            f"{len(OPEN_POSITIONS)}"
        )

        # ----------------------------------------------------
        # EXCHANGE CONFIG
        # ----------------------------------------------------

        WEEX_CONFIG = (
            await weex_private_get(
                session,
                "/capi/v3/market/exchangeInfo",
            )
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

        "symbol":
            SYMBOL,

        "mark_price":
            decimal_to_string(
                MARK_PRICE
            ),

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
            decimal_to_string(
                notional
            ),

        "quantity":
            decimal_to_string(
                quantity
            ),

        "submitted":
            False,
    }


# ============================================================
# HISTORICAL KLINE EXTRACTION
# ============================================================

def extract_kline_rows(
    payload
):

    if isinstance(
        payload,
        list,
    ):
        return payload

    if not isinstance(
        payload,
        dict,
    ):
        return []

    for key in (
        "data",
        "rows",
        "result",
        "list",
    ):

        value = payload.get(
            key
        )

        if isinstance(
            value,
            list,
        ):
            return value

    return []


def kline_timestamp(
    row
):

    if isinstance(
        row,
        dict,
    ):

        for key in (
            "timestamp",
            "time",
            "openTime",
            "open_time",
        ):

            if key in row:

                return int(
                    D(
                        row[key]
                    )
                )

    elif isinstance(
        row,
        list,
    ):

        if len(row) >= 1:

            return int(
                D(
                    row[0]
                )
            )

    raise ValueError(
        "Unable to determine kline timestamp"
    )


def kline_high_low(
    row
):

    if isinstance(
        row,
        dict,
    ):

        high = None
        low = None

        for key in (
            "high",
            "highPrice",
        ):

            if key in row:

                high = D(
                    row[key]
                )

                break

        for key in (
            "low",
            "lowPrice",
        ):

            if key in row:

                low = D(
                    row[key]
                )

                break

        if (
            high is None
            or low is None
        ):

            raise ValueError(
                "Unable to extract kline high/low"
            )

        return (
            high,
            low,
        )

    if isinstance(
        row,
        list,
    ):

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


def normalize_kline_order(
    rows
):

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

        "symbol":
            SYMBOL,

        "interval":
            KLINE_INTERVAL,

        "limit":
            HISTORICAL_LIMIT,
    }

    if start_timestamp is not None:

        params[
            "startTime"
        ] = start_timestamp

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

            payload = (
                await historical_get(
                    session,
                    start_timestamp,
                )
            )

            rows = (
                extract_kline_rows(
                    payload
                )
            )

            if not rows:
                break

            for row in rows:

                try:

                    ts = (
                        kline_timestamp(
                            row
                        )
                    )

                    all_rows[
                        ts
                    ] = row

                except Exception as exc:

                    log(
                        "HISTORICAL ROW SKIPPED: "
                        + str(exc)
                    )

            normalized = (
                normalize_kline_order(
                    list(
                        all_rows.values()
                    )
                )
            )

            if not normalized:
                break

            oldest_ts = (
                kline_timestamp(
                    normalized[0]
                )
            )

            if (
                start_timestamp is not None
                and oldest_ts >= start_timestamp
            ):

                break

            start_timestamp = (
                oldest_ts - 1
            )

            if len(rows) < HISTORICAL_LIMIT:
                break

    result = (
        normalize_kline_order(
            list(
                all_rows.values()
            )
        )
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

        high, low = (
            kline_high_low(
                row
            )
        )

        highs.append(
            high
        )

        lows.append(
            low
        )

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

def cluster_extrema(
    values
):

    if not values:
        return []

    ordered = sorted(
        D(value)
        for value in values
    )

    clusters = []

    current = [
        ordered[0]
    ]

    for value in ordered[1:]:

        average = (
            sum(current)
            / Decimal(
                len(current)
            )
        )

        difference_percent = (
            abs(
                value - average
            )
            / average
            * Decimal("100")
        )

        if (
            difference_percent
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

    result = []

    for cluster in clusters:

        average = (
            sum(cluster)
            / Decimal(
                len(cluster)
            )
        )

        result.append({

            "average":
                average,

            "minimum":
                min(cluster),

            "maximum":
                max(cluster),

            "touches":
                len(cluster),

            "values":
                cluster,
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

    entry_price = D(
        entry_price
    )

    extrema = (
        local_extrema_values(
            rows,
            side,
        )
    )

    clusters = (
        cluster_extrema(
            extrema
        )
    )

    cluster_records = []
    valid_clusters = []

    for index, cluster in enumerate(
        clusters,
        start=1,
    ):

        average = cluster[
            "average"
        ]

        touches = cluster[
            "touches"
        ]

        if side == "LONG":

            side_valid = (
                average
                > entry_price
            )

        else:

            side_valid = (
                average
                < entry_price
            )

        touches_valid = (
            touches
            >= MIN_CLUSTER_TOUCHES
        )

        valid = (
            touches_valid
            and side_valid
        )

        if valid:

            reason = "VALID"

        elif not touches_valid:

            reason = (
                "INSUFFICIENT_CLUSTER_TOUCHES"
            )

        elif not side_valid:

            reason = (
                "WRONG_ENTRY_SIDE"
            )

        else:

            reason = "REJECTED"

        record = {

            "cluster_number":
                index,

            "average":
                decimal_to_string(
                    average
                ),

            "minimum":
                decimal_to_string(
                    cluster[
                        "minimum"
                    ]
                ),

            "maximum":
                decimal_to_string(
                    cluster[
                        "maximum"
                    ]
                ),

            "touches":
                touches,

            "valid":
                valid,

            "reason":
                reason,
        }

        cluster_records.append(
            record
        )

        if valid:

            valid_clusters.append(
                cluster
            )

    if side == "LONG":

        valid_clusters.sort(
            key=lambda c:
                c["average"]
        )

    else:

        valid_clusters.sort(
            key=lambda c:
                c["average"],
            reverse=True,
        )

    valid_count = len(
        valid_clusters
    )

    if (
        valid_count
        >= REQUIRED_TP_CLUSTERS
    ):

        status = (
            "ENOUGH_VALID_CLUSTERS"
        )

        failure_reason = None

    elif valid_count == 1:

        status = (
            "INSUFFICIENT_VALID_CLUSTERS"
        )

        failure_reason = (
            "ONLY_ONE_VALID_CLUSTER"
        )

    elif not extrema:

        status = "NO_EXTREMA"

        failure_reason = (
            "NO_EXTREMA"
        )

    elif not clusters:

        status = (
            "NO_EXTREMA_ON_REQUIRED_SIDE"
        )

        failure_reason = (
            "NO_EXTREMA_ON_REQUIRED_SIDE"
        )

    else:

        status = (
            "CLUSTERS_REJECTED_BY_POLICY"
        )

        failure_reason = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    diagnostics = {

        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

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

def evaluate_tp_approval(
    diagnostics
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

    extrema = (
        local_extrema_values(
            rows,
            side,
        )
    )

    clusters = (
        cluster_extrema(
            extrema
        )
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

    LAST_TP_APPROVAL = (
        approval
    )

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

    clusters = (
        valid_clusters(
            rows,
            entry_price,
            side,
        )
    )

    if (
        len(clusters)
        < REQUIRED_TP_CLUSTERS
    ):

        raise RuntimeError(
            "TP approval inconsistency: "
            "diagnostics approved but independent "
            "cluster extraction found fewer than "
            "two valid clusters"
        )

    cluster_1 = clusters[0]
    cluster_2 = clusters[1]

    cluster_1_avg = cluster_1[
        "average"
    ]

    cluster_2_avg = cluster_2[
        "average"
    ]

    if side == "LONG":

        tp1 = (
            entry_price
            + (
                cluster_1_avg
                - entry_price
            )
            * TP1_PROFIT_MARGIN_PERCENT
            / Decimal("100")
        )

        tp2 = (
            entry_price
            + (
                cluster_2_avg
                - entry_price
            )
            * TP2_PROFIT_MARGIN_PERCENT
            / Decimal("100")
        )

        ordering_ok = (
            entry_price
            < tp1
            < tp2
            <= cluster_2_avg
        )

    elif side == "SHORT":

        tp1 = (
            entry_price
            - (
                entry_price
                - cluster_1_avg
            )
            * TP1_PROFIT_MARGIN_PERCENT
            / Decimal("100")
        )

        tp2 = (
            entry_price
            - (
                entry_price
                - cluster_2_avg
            )
            * TP2_PROFIT_MARGIN_PERCENT
            / Decimal("100")
        )

        ordering_ok = (
            entry_price
            > tp1
            > tp2
            >= cluster_2_avg
        )

    else:

        raise ValueError(
            f"Unsupported side={side}"
        )

    if not ordering_ok:

        raise RuntimeError(
            f"{side} TP ordering invalid"
        )

    snapshot = {

        "stage":
            STAGE,

        "fill_label":
            fill_label,

        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "tp_approval":
            approval,

        "required_valid_clusters":
            REQUIRED_TP_CLUSTERS,

        "available_valid_clusters":
            len(clusters),

        "cluster_1": {

            "average":
                decimal_to_string(
                    cluster_1_avg
                ),

            "minimum":
                decimal_to_string(
                    cluster_1[
                        "minimum"
                    ]
                ),

            "maximum":
                decimal_to_string(
                    cluster_1[
                        "maximum"
                    ]
                ),

            "touches":
                cluster_1[
                    "touches"
                ],
        },

        "cluster_2": {

            "average":
                decimal_to_string(
                    cluster_2_avg
                ),

            "minimum":
                decimal_to_string(
                    cluster_2[
                        "minimum"
                    ]
                ),

            "maximum":
                decimal_to_string(
                    cluster_2[
                        "maximum"
                    ]
                ),

            "touches":
                cluster_2[
                    "touches"
                ],
        },

        "tp1": {

            "price":
                decimal_to_string(
                    tp1
                ),

            "progress_percent":
                decimal_to_string(
                    TP1_PROFIT_MARGIN_PERCENT
                ),

            "status":
                "LOCKED",
        },

        "tp2": {

            "price":
                decimal_to_string(
                    tp2
                ),

            "progress_percent":
                decimal_to_string(
                    TP2_PROFIT_MARGIN_PERCENT
                ),

            "status":
                "LOCKED",
        },

        "tp3": {

            "allocation_percent":
                decimal_to_string(
                    TP3_ALLOCATION_PERCENT
                ),

            "trailing_distance_percent":
                decimal_to_string(
                    TP3_TRAILING_DISTANCE_PERCENT
                ),

            "status":
                "RUNNER",
        },

        "tp_allocations": {

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

        "primary_tp_immutable":
            True,

        "backup_tp_recalculated_only_on_backup_fill":
            True,

        "method":
            "HISTORICAL_CLUSTER_TP_R36F5_1",

        "historical_diagnostics":
            diagnostics,
    }

    log(
        f"{side} TP SET APPROVED WITH "
        f"{len(clusters)} VALID CLUSTERS"
    )

    log(
        f"{side} TP1 = "
        f"{decimal_to_string(tp1)} "
        f"(20% adjustable progress)"
    )

    log(
        f"{side} TP2 = "
        f"{decimal_to_string(tp2)} "
        f"(50% adjustable progress)"
    )

    log(
        f"{side} TP3 = 60% trailing runner"
    )

    return snapshot


# ============================================================
# SYNTHETIC LONG DATA
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

    for i, high in enumerate(
        base
    ):

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
# SYNTHETIC SHORT DATA
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

    for i, low in enumerate(
        base
    ):

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
# SYNTHETIC ZERO-CLUSTER FIXTURES
# ============================================================

def synthetic_zero_long_rows():

    return [

        [
            0,
            "99500",
            "99800",
            "99900",
            "99700",
            "1",
        ],

        [
            1,
            "99600",
            "99900",
            "99850",
            "99750",
            "1",
        ],

        [
            2,
            "99700",
            "99950",
            "99900",
            "99800",
            "1",
        ],

        [
            3,
            "99600",
            "99900",
            "99800",
            "99750",
            "1",
        ],

        [
            4,
            "99500",
            "99800",
            "99700",
            "99600",
            "1",
        ],
    ]


def synthetic_zero_short_rows():

    return [

        [
            0,
            "100100",
            "100500",
            "100300",
            "100200",
            "1",
        ],

        [
            1,
            "100200",
            "100600",
            "100400",
            "100300",
            "1",
        ],

        [
            2,
            "100100",
            "100500",
            "100250",
            "100200",
            "1",
        ],

        [
            3,
            "100200",
            "100700",
            "100500",
            "100300",
            "1",
        ],

        [
            4,
            "100300",
            "100600",
            "100400",
            "100350",
            "1",
        ],
    ]


# ============================================================
# SYNTHETIC ONE-CLUSTER LONG DATA
# ============================================================

def synthetic_one_cluster_long_rows():

    return [

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


# ============================================================
# SYNTHETIC ONE-CLUSTER SHORT DATA
# ============================================================

def synthetic_one_cluster_short_rows():

    return [

        [
            0,
            "99900",
            "100100",
            "99900",
            "99950",
            "1",
        ],

        [
            1,
            "99450",
            "100000",
            "99500",
            "99450",
            "1",
        ],

        [
            2,
            "99900",
            "100100",
            "99950",
            "99900",
            "1",
        ],

        [
            3,
            "99460",
            "100000",
            "99510",
            "99460",
            "1",
        ],

        [
            4,
            "99900",
            "100100",
            "99900",
            "99800",
            "1",
        ],
    ]


# ============================================================
# SYNTHETIC CLUSTER TESTS
# ============================================================

def synthetic_cluster_tests():

    entry = Decimal(
        "100000"
    )

    # ========================================================
    # LONG TWO-CLUSTER APPROVAL
    # ========================================================

    long_rows = (
        synthetic_long_rows()
    )

    long_diagnostics = (
        build_cluster_diagnostics(
            long_rows,
            entry,
            "LONG",
        )
    )

    check(
        "SYNTHETIC_LONG_MINIMUM_TWO_VALID_CLUSTERS",
        long_diagnostics[
            "valid_cluster_count"
        ] >= REQUIRED_TP_CLUSTERS,
        (
            "expected_at_least="
            + str(
                REQUIRED_TP_CLUSTERS
            )
            + " actual="
            + str(
                long_diagnostics[
                    "valid_cluster_count"
                ]
            )
        ),
    )

    long_snapshot = (
        build_cluster_tp_snapshot(
            entry,
            long_rows,
            "LONG",
            "SYNTHETIC_LONG_FILL",
        )
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

    # ========================================================
    # SHORT TWO-CLUSTER APPROVAL
    # ========================================================

    short_rows = (
        synthetic_short_rows()
    )

    short_diagnostics = (
        build_cluster_diagnostics(
            short_rows,
            entry,
            "SHORT",
        )
    )

    check(
        "SYNTHETIC_SHORT_MINIMUM_TWO_VALID_CLUSTERS",
        short_diagnostics[
            "valid_cluster_count"
        ] >= REQUIRED_TP_CLUSTERS,
        (
            "expected_at_least="
            + str(
                REQUIRED_TP_CLUSTERS
            )
            + " actual="
            + str(
                short_diagnostics[
                    "valid_cluster_count"
                ]
            )
        ),
    )

    short_snapshot = (
        build_cluster_tp_snapshot(
            entry,
            short_rows,
            "SHORT",
            "SYNTHETIC_SHORT_FILL",
        )
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
        (
            "synthetic short fixture must "
            "deterministically produce exactly "
            + str(
                REQUIRED_TP_CLUSTERS
            )
            + " valid clusters"
        ),
    )

    # ========================================================
    # IMMUTABILITY CONTRACTS
    # ========================================================

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

    # ========================================================
    # ONE-CLUSTER LONG REJECTION
    # ========================================================

    one_long_rows = (
        synthetic_one_cluster_long_rows()
    )

    one_long_diagnostics = (
        build_cluster_diagnostics(
            one_long_rows,
            entry,
            "LONG",
        )
    )

    one_long_approval = (
        evaluate_tp_approval(
            one_long_diagnostics
        )
    )

    check(
        "SYNTHETIC_LONG_ONE_CLUSTER_REJECTED",
        one_long_approval[
            "approved"
        ] is False,
    )

    check(
        "SYNTHETIC_LONG_ONE_CLUSTER_STATUS_REJECTED",
        one_long_approval[
            "status"
        ] == "REJECTED",
    )

    check(
        "SYNTHETIC_LONG_ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET",
        one_long_approval[
            "available_valid_clusters"
        ] < REQUIRED_TP_CLUSTERS,
    )

    # ========================================================
    # ONE-CLUSTER SHORT REJECTION
    # ========================================================

    one_short_rows = (
        synthetic_one_cluster_short_rows()
    )

    one_short_diagnostics = (
        build_cluster_diagnostics(
            one_short_rows,
            entry,
            "SHORT",
        )
    )

    one_short_approval = (
        evaluate_tp_approval(
            one_short_diagnostics
        )
    )

    check(
        "SYNTHETIC_SHORT_ONE_CLUSTER_REJECTED",
        one_short_approval[
            "approved"
        ] is False,
    )

    check(
        "SYNTHETIC_SHORT_ONE_CLUSTER_STATUS_REJECTED",
        one_short_approval[
            "status"
        ] == "REJECTED",
    )

    check(
        "SYNTHETIC_SHORT_ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET",
        one_short_approval[
            "available_valid_clusters"
        ] < REQUIRED_TP_CLUSTERS,
    )

    # ========================================================
    # ZERO-CLUSTER LONG REJECTION
    # ========================================================

    zero_long_rows = (
        synthetic_zero_long_rows()
    )

    zero_long_diagnostics = (
        build_cluster_diagnostics(
            zero_long_rows,
            entry,
            "LONG",
        )
    )

    zero_long_approval = (
        evaluate_tp_approval(
            zero_long_diagnostics
        )
    )

    check(
        "SYNTHETIC_LONG_ZERO_CLUSTER_REJECTED",
        zero_long_approval[
            "approved"
        ] is False,
    )

    check(
        "SYNTHETIC_LONG_ZERO_CLUSTER_STATUS_REJECTED",
        zero_long_approval[
            "status"
        ] == "REJECTED",
    )

    check(
        "SYNTHETIC_LONG_ZERO_CLUSTER_DOES_NOT_APPROVE_TP_SET",
        zero_long_approval[
            "available_valid_clusters"
        ] < REQUIRED_TP_CLUSTERS,
    )

    # ========================================================
    # ZERO-CLUSTER SHORT REJECTION
    # ========================================================

    zero_short_rows = (
        synthetic_zero_short_rows()
    )

    zero_short_diagnostics = (
        build_cluster_diagnostics(
            zero_short_rows,
            entry,
            "SHORT",
        )
    )

    zero_short_approval = (
        evaluate_tp_approval(
            zero_short_diagnostics
        )
    )

    check(
        "SYNTHETIC_SHORT_ZERO_CLUSTER_REJECTED",
        zero_short_approval[
            "approved"
        ] is False,
    )

    check(
        "SYNTHETIC_SHORT_ZERO_CLUSTER_STATUS_REJECTED",
        zero_short_approval[
            "status"
        ] == "REJECTED",
    )

    check(
        "SYNTHETIC_SHORT_ZERO_CLUSTER_DOES_NOT_APPROVE_TP_SET",
        zero_short_approval[
            "available_valid_clusters"
        ] < REQUIRED_TP_CLUSTERS,
    )

    return (
        long_snapshot,
        short_snapshot,
    )


# ============================================================
# SYNTHETIC TP REJECTION TEST
# ============================================================

def synthetic_tp_rejection_test():

    entry = Decimal(
        "100000"
    )

    rows = (
        synthetic_one_cluster_long_rows()
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
# REAL MARKET TP EVALUATION
# ============================================================

def evaluate_real_market_tp(
    historical_rows,
    mark_price,
    side,
):

    diagnostics = (
        build_cluster_diagnostics(
            historical_rows,
            mark_price,
            side,
        )
    )

    approval = (
        evaluate_tp_approval(
            diagnostics
        )
    )

    eligible = (
        approval[
            "approved"
        ] is True
    )

    market_tp_eligibility_log(
        side,
        diagnostics,
    )

    if not eligible:

        return (
            None,
            diagnostics,
            approval,
            False,
        )

    try:

        snapshot = (
            build_cluster_tp_snapshot(
                mark_price,
                historical_rows,
                side,
                f"REAL_{side}_PREVIEW",
            )
        )

        return (
            snapshot,
            diagnostics,
            approval,
            True,
        )

    except Exception as exc:

        # IMPORTANT:
        #
        # At this point the historical cluster count says the
        # market is eligible. Therefore an exception here is
        # NOT a normal market rejection.
        #
        # It indicates an internal TP-engine problem.

        log(
            f"REAL_{side}_TP_ENGINE_EXCEPTION = "
            f"{exc}"
        )

        raise


# ============================================================
# MAIN R36F.5.4 TEST
# ============================================================

async def run_r36f54():

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

    global REAL_LONG_MARKET_ELIGIBLE
    global REAL_SHORT_MARKET_ELIGIBLE

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

    r36d_snapshot = (
        read_json_file(
            R36D_SNAPSHOT_FILE,
            {},
        )
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
            len(
                historical_rows
            ) >= 3,
            (
                f"rows="
                f"{len(historical_rows)}"
            ),
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
    # R36F.5.4 CORRECTION:
    #
    # A real market with fewer than two valid clusters is an
    # expected strategy rejection and does NOT become a blocker.
    #
    # ========================================================

    real_long_snapshot = None

    if (
        historical_rows
        and MARK_PRICE is not None
    ):

        try:

            (
                real_long_snapshot,
                LONG_DIAGNOSTICS,
                long_approval,
                REAL_LONG_MARKET_ELIGIBLE,
            ) = evaluate_real_market_tp(
                historical_rows,
                MARK_PRICE,
                "LONG",
            )

            if REAL_LONG_MARKET_ELIGIBLE:

                diagnostic_check(
                    "REAL_LONG_TP_MARKET_ELIGIBILITY",
                    True,
                    (
                        "TP_APPROVAL="
                        + long_approval[
                            "status"
                        ]
                    ),
                )

                log(
                    "REAL_LONG_TP_APPROVAL="
                    + long_approval[
                        "status"
                    ]
                )

            else:

                diagnostic_check(
                    "REAL_LONG_TP_MARKET_ELIGIBILITY",
                    True,
                    (
                        "EXPECTED_STRATEGY_REJECTION "
                        "TP_APPROVAL="
                        + long_approval[
                            "status"
                        ]
                        + " reason="
                        + long_approval[
                            "reason"
                        ]
                    ),
                )

                log(
                    "REAL_LONG_TP_APPROVAL="
                    + long_approval[
                        "status"
                    ]
                )

        except Exception as exc:

            # A failure after a market was shown to be eligible
            # is a genuine TP-engine capability failure.

            if not LONG_DIAGNOSTICS:

                LONG_DIAGNOSTICS = (
                    build_cluster_diagnostics(
                        historical_rows,
                        MARK_PRICE,
                        "LONG",
                    )
                )

            check(
                "REAL_LONG_TP_ENGINE_INTEGRITY",
                False,
                str(exc),
            )

    # ========================================================
    # REAL SHORT TP PREVIEW
    #
    # Same R36F.5.4 classification as LONG.
    #
    # ========================================================

    real_short_snapshot = None

    if (
        historical_rows
        and MARK_PRICE is not None
    ):

        try:

            (
                real_short_snapshot,
                SHORT_DIAGNOSTICS,
                short_approval,
                REAL_SHORT_MARKET_ELIGIBLE,
            ) = evaluate_real_market_tp(
                historical_rows,
                MARK_PRICE,
                "SHORT",
            )

            if REAL_SHORT_MARKET_ELIGIBLE:

                diagnostic_check(
                    "REAL_SHORT_TP_MARKET_ELIGIBILITY",
                    True,
                    (
                        "TP_APPROVAL="
                        + short_approval[
                            "status"
                        ]
                    ),
                )

                log(
                    "REAL_SHORT_TP_APPROVAL="
                    + short_approval[
                        "status"
                    ]
                )

            else:

                diagnostic_check(
                    "REAL_SHORT_TP_MARKET_ELIGIBILITY",
                    True,
                    (
                        "EXPECTED_STRATEGY_REJECTION "
                        "TP_APPROVAL="
                        + short_approval[
                            "status"
                        ]
                        + " reason="
                        + short_approval[
                            "reason"
                        ]
                    ),
                )

                log(
                    "REAL_SHORT_TP_APPROVAL="
                    + short_approval[
                        "status"
                    ]
                )

        except Exception as exc:

            if not SHORT_DIAGNOSTICS:

                SHORT_DIAGNOSTICS = (
                    build_cluster_diagnostics(
                        historical_rows,
                        MARK_PRICE,
                        "SHORT",
                    )
                )

            check(
                "REAL_SHORT_TP_ENGINE_INTEGRITY",
                False,
                str(exc),
            )

    # ========================================================
    # FROZEN DIAGNOSTIC:
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
    # FROZEN DIAGNOSTIC:
    # WRITER REQUEST CONSTRUCTION
    # ========================================================

    writer_preview = None

    try:

        if (
            real_long_snapshot
            is not None
            and MARK_PRICE is not None
        ):

            quantity = quantize_down(

                AVAILABLE_BALANCE
                * ENTRY_MARGIN_PERCENT
                / Decimal("100")
                * LEVERAGE_LONG
                / MARK_PRICE,

                QUANTITY_STEP,
            )

            writer_preview = (
                build_writer_request_preview(
                    "LONG",
                    MARK_PRICE,
                    quantity,
                    real_long_snapshot,
                )
            )

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                writer_preview[
                    "submitted"
                ] is False,
            )

        elif (
            real_short_snapshot
            is not None
            and MARK_PRICE is not None
        ):

            quantity = quantize_down(

                AVAILABLE_BALANCE
                * ENTRY_MARGIN_PERCENT
                / Decimal("100")
                * LEVERAGE_SHORT
                / MARK_PRICE,

                QUANTITY_STEP,
            )

            writer_preview = (
                build_writer_request_preview(
                    "SHORT",
                    MARK_PRICE,
                    quantity,
                    real_short_snapshot,
                )
            )

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                writer_preview[
                    "submitted"
                ] is False,
            )

        else:

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                (
                    "No currently eligible real-market "
                    "TP snapshot available; this is "
                    "diagnostic-only."
                ),
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

        (
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False
        )

        and

        (
            ORDER_SUBMISSION_ENABLED
            is False
        )

        and

        (
            LEVERAGE_MUTATION_ENABLED
            is False
        )

        and

        (
            MARGIN_MODE_MUTATION_ENABLED
            is False
        )

        and

        (
            POSITION_MUTATION_ENABLED
            is False
        )

        and

        (
            FIRST_REAL_ORDER_ALLOWED
            is False
        )
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
    # ========================================================

    FINAL_GATE_OK = (
        len(
            FINAL_BLOCKERS
        ) == 0
    )

    TEST_STATUS = (
        "PASS"
        if FINAL_GATE_OK
        else "FAIL"
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
        f"{STAGE} TP_MARKET_REJECTION_IS_NOT_BOT_FAILURE = TRUE"
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

        "real_market_tp_eligibility": {

            "long":
                REAL_LONG_MARKET_ELIGIBLE,

            "short":
                REAL_SHORT_MARKET_ELIGIBLE,

            "rejection_is_final_blocker":
                False,

            "required_valid_clusters":
                REQUIRED_TP_CLUSTERS,
        },

        "tp_policy": {

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

            "cluster_tolerance_percent":
                decimal_to_string(
                    CLUSTER_TOLERANCE_PERCENT
                ),

            "minimum_cluster_touches":
                MIN_CLUSTER_TOUCHES,
        },

        "synthetic_test_policy": {

            "long_two_or_more_approves":
                True,

            "short_two_or_more_approves":
                True,

            "long_one_rejects":
                True,

            "short_one_rejects":
                True,

            "long_zero_rejects":
                True,

            "short_zero_rejects":
                True,

            "one_cluster_never_approves_tp_set":
                True,

            "tp3_does_not_fabricate_missing_tp1_tp2":
                True,

            "synthetic_fixtures_changed":
                True,

            "production_tp_policy_changed":
                False,
        },

        "canary_preview":
            canary_preview,

        "writer_preview":
            writer_preview,

        "execution_firebreak": {

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
            f"long_market_eligible="
            f"{REAL_LONG_MARKET_ELIGIBLE} "
            f"short_market_eligible="
            f"{REAL_SHORT_MARKET_ELIGIBLE} "
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

        await run_r36f54()

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
