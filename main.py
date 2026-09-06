
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


# END PART 1
# ============================================================
# WEEX READ-ONLY RECONCILIATION
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
            f"{decimal_to_string(MARK_PRICE)}"
        )

        # ----------------------------------------------------
        # AVAILABLE BALANCE
        # ----------------------------------------------------

        balance_payload = await weex_private_get(
            session,
            "/capi/v3/account/assets",
        )

        balance_candidates = []

        if isinstance(
            balance_payload,
            dict,
        ):

            balance_candidates.append(
                balance_payload
            )

            data = balance_payload.get(
                "data"
            )

            if isinstance(
                data,
                dict,
            ):

                balance_candidates.append(
                    data
                )

            elif isinstance(
                data,
                list,
            ):

                balance_candidates.extend(
                    data
                )

        elif isinstance(
            balance_payload,
            list,
        ):

            balance_candidates.extend(
                balance_payload
            )

        AVAILABLE_BALANCE = None

        for item in balance_candidates:

            if not isinstance(
                item,
                dict,
            ):
                continue

            coin = str(
                item.get(
                    "coin",
                    item.get(
                        "currency",
                        "",
                    ),
                )
            ).upper()

            if (
                coin
                and coin != "USDT"
            ):
                continue

            for key in (
                "available",
                "availableBalance",
                "available_balance",
            ):

                value = item.get(
                    key
                )

                if value is None:
                    continue

                try:

                    AVAILABLE_BALANCE = D(
                        value
                    )

                    break

                except Exception:
                    continue

            if (
                AVAILABLE_BALANCE
                is not None
            ):
                break

        if AVAILABLE_BALANCE is None:

            raise RuntimeError(
                "Unable to extract "
                "available USDT balance"
            )

        log(
            "AVAILABLE USDT = "
            f"{decimal_to_string(AVAILABLE_BALANCE)}"
        )

        # ----------------------------------------------------
        # SINGLE BTCUSDT POSITION
        #
        # R36F.5.3 CORRECTION:
        #
        # R36F.5.2 incorrectly used:
        #
        #   /capi/v3/account/position
        #
        # Correct read-only endpoint:
        #
        #   /capi/v3/account/position/singlePosition
        #
        # No exchange mutation is performed.
        # ----------------------------------------------------

        position_payload = await weex_private_get(
            session,
            "/capi/v3/account/position/singlePosition",
            params={
                "symbol": SYMBOL,
            },
        )

        position_candidates = []

        if isinstance(
            position_payload,
            dict,
        ):

            position_candidates.append(
                position_payload
            )

            data = position_payload.get(
                "data"
            )

            if isinstance(
                data,
                dict,
            ):

                position_candidates.append(
                    data
                )

            elif isinstance(
                data,
                list,
            ):

                position_candidates.extend(
                    data
                )

        elif isinstance(
            position_payload,
            list,
        ):

            position_candidates.extend(
                position_payload
            )

        OPEN_POSITIONS = []

        for item in position_candidates:

            if not isinstance(
                item,
                dict,
            ):
                continue

            item_symbol = str(
                item.get(
                    "symbol",
                    SYMBOL,
                )
            ).upper()

            if (
                item_symbol
                and item_symbol != SYMBOL
            ):
                continue

            quantity = None

            for key in (
                "total",
                "size",
                "positionSize",
                "position_size",
                "holdVol",
                "positionAmt",
            ):

                if key not in item:
                    continue

                try:

                    quantity = D(
                        item.get(key)
                    )

                except Exception:

                    quantity = None

                break

            if (
                quantity is not None
                and quantity != 0
            ):

                OPEN_POSITIONS.append(
                    item
                )

        log(
            "OPEN BTCUSDT POSITIONS = "
            f"{len(OPEN_POSITIONS)}"
        )

        # ----------------------------------------------------
        # SYMBOL CONFIG
        # ----------------------------------------------------

        config_payload = await weex_private_get(
            session,
            "/capi/v3/account/symbolConfig",
            params={
                "symbol": SYMBOL,
            },
        )

        config_candidates = []

        if isinstance(
            config_payload,
            dict,
        ):

            config_candidates.append(
                config_payload
            )

            data = config_payload.get(
                "data"
            )

            if isinstance(
                data,
                dict,
            ):

                config_candidates.append(
                    data
                )

            elif isinstance(
                data,
                list,
            ):

                config_candidates.extend(
                    data
                )

        elif isinstance(
            config_payload,
            list,
        ):

            config_candidates.extend(
                config_payload
            )

        WEEX_CONFIG = {}

        for item in config_candidates:

            if not isinstance(
                item,
                dict,
            ):
                continue

            item_symbol = str(
                item.get(
                    "symbol",
                    SYMBOL,
                )
            ).upper()

            if (
                item_symbol
                and item_symbol != SYMBOL
            ):
                continue

            WEEX_CONFIG = item

            break

        margin_mode = None

        for key in (
            "marginMode",
            "margin_mode",
            "marginType",
        ):

            if key in WEEX_CONFIG:

                margin_mode = str(
                    WEEX_CONFIG.get(
                        key
                    )
                ).upper()

                break

        long_leverage = None

        for key in (
            "isolatedLong",
            "longLeverage",
            "long_leverage",
        ):

            if key in WEEX_CONFIG:

                try:

                    long_leverage = D(
                        WEEX_CONFIG.get(
                            key
                        )
                    )

                except Exception:
                    pass

                break

        short_leverage = None

        for key in (
            "isolatedShort",
            "shortLeverage",
            "short_leverage",
        ):

            if key in WEEX_CONFIG:

                try:

                    short_leverage = D(
                        WEEX_CONFIG.get(
                            key
                        )
                    )

                except Exception:
                    pass

                break

        log(
            "MARGIN MODE = "
            f"{margin_mode}"
        )

        log(
            "LONG LEVERAGE = "
            f"{decimal_to_string(long_leverage)}"
        )

        log(
            "SHORT LEVERAGE = "
            f"{decimal_to_string(short_leverage)}"
        )

        # ----------------------------------------------------
        # READ-ONLY CONSISTENCY
        # ----------------------------------------------------

        if OPEN_POSITIONS:

            raise RuntimeError(
                "BTCUSDT_NOT_FLAT"
            )

        if (
            margin_mode is not None
            and margin_mode
            != MARGIN_MODE
        ):

            raise RuntimeError(
                "MARGIN_MODE_MISMATCH: "
                f"{margin_mode}"
            )

        if (
            long_leverage
            is not None
            and long_leverage
            != LEVERAGE_LONG
        ):

            raise RuntimeError(
                "LONG_LEVERAGE_MISMATCH: "
                f"{decimal_to_string(long_leverage)}"
            )

        if (
            short_leverage
            is not None
            and short_leverage
            != LEVERAGE_SHORT
        ):

            raise RuntimeError(
                "SHORT_LEVERAGE_MISMATCH: "
                f"{decimal_to_string(short_leverage)}"
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

    entry_margin = (
        AVAILABLE_BALANCE
        * ENTRY_MARGIN_PERCENT
        / Decimal("100")
    )

    entry_notional = (
        entry_margin
        * LEVERAGE_LONG
    )

    raw_quantity = (
        entry_notional
        / MARK_PRICE
    )

    normalized_quantity = (
        quantize_down(
            raw_quantity,
            QUANTITY_STEP,
        )
    )

    return {

        "stage":
            STAGE,

        "symbol":
            SYMBOL,

        "side":
            "LONG",

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

        "entry_margin":
            decimal_to_string(
                entry_margin
            ),

        "leverage":
            decimal_to_string(
                LEVERAGE_LONG
            ),

        "entry_notional":
            decimal_to_string(
                entry_notional
            ),

        "raw_quantity":
            decimal_to_string(
                raw_quantity
            ),

        "normalized_quantity":
            decimal_to_string(
                normalized_quantity
            ),

        "exchange_write":
            False,

        "order_submission":
            False,

        "real_order_execution":
            False,

        "demo_order_execution":
            False,
    }


# ============================================================
# HISTORICAL KLINE EXTRACTION
# ============================================================

def extract_kline_rows(payload):

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


def kline_timestamp(row):

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
        "Unable to determine "
        "kline timestamp"
    )


def kline_high_low(row):

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
                "Unable to extract "
                "kline high/low"
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
            D(
                row[2]
            ),
            D(
                row[3]
            ),
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
        "symbol":
            SYMBOL,

        "interval":
            KLINE_INTERVAL,

        "limit":
            HISTORICAL_LIMIT,
    }

    if (
        start_timestamp
        is not None
    ):

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

        for page_index in range(
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

                log(
                    "HISTORICAL PAGE "
                    f"{page_index + 1}: "
                    "NO ROWS"
                )

                break

            normalized = (
                normalize_kline_order(
                    rows
                )
            )

            for row in normalized:

                try:

                    timestamp = (
                        kline_timestamp(
                            row
                        )
                    )

                    all_rows[
                        timestamp
                    ] = row

                except Exception:
                    continue

            log(
                "HISTORICAL PAGE "
                f"{page_index + 1}: "
                f"ROWS={len(rows)} "
                f"TOTAL_UNIQUE={len(all_rows)}"
            )

            if (
                len(rows)
                < HISTORICAL_LIMIT
            ):

                break

            try:

                oldest_timestamp = (
                    kline_timestamp(
                        normalized[0]
                    )
                )

            except Exception:

                break

            next_start_timestamp = (
                oldest_timestamp - 1
            )

            if (
                start_timestamp
                is not None
                and next_start_timestamp
                >= start_timestamp
            ):

                break

            start_timestamp = (
                next_start_timestamp
            )

    result = normalize_kline_order(
        list(
            all_rows.values()
        )
    )

    log(
        "HISTORICAL TOTAL ROWS = "
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

    if side not in (
        "LONG",
        "SHORT",
    ):

        raise ValueError(
            f"Unsupported side={side}"
        )

    if len(rows) < 3:

        return []

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

    extrema = []

    for index in range(
        1,
        len(rows) - 1,
    ):

        if side == "LONG":

            previous_value = (
                highs[
                    index - 1
                ]
            )

            current_value = (
                highs[
                    index
                ]
            )

            next_value = (
                highs[
                    index + 1
                ]
            )

            if (
                current_value
                > previous_value
                and current_value
                >= next_value
            ):

                extrema.append(
                    current_value
                )

        else:

            previous_value = (
                lows[
                    index - 1
                ]
            )

            current_value = (
                lows[
                    index
                ]
            )

            next_value = (
                lows[
                    index + 1
                ]
            )

            if (
                current_value
                < previous_value
                and current_value
                <= next_value
            ):

                extrema.append(
                    current_value
                )

    return extrema


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

    current_cluster = [
        ordered[0]
    ]

    for value in ordered[1:]:

        current_average = (
            sum())
        current_cluster
  
id="p83k2m"
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

    entry_price = D(entry_price)

    diagnostics = build_cluster_diagnostics(
        rows,
        entry_price,
        side,
    )

    approval = evaluate_tp_approval(
        diagnostics
    )

    LAST_TP_APPROVAL = approval

    if not approval["approved"]:

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

    if len(clusters) < REQUIRED_TP_CLUSTERS:

        raise RuntimeError(
            "TP approval inconsistency: "
            "diagnostics approved but independent "
            "cluster extraction found fewer than "
            "two valid clusters"
        )

    cluster_1 = clusters[0]
    cluster_2 = clusters[1]

    cluster_1_avg = cluster_1["average"]
    cluster_2_avg = cluster_2["average"]

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

        "stage": STAGE,

        "fill_label": fill_label,

        "side": side,

        "entry_price":
            decimal_to_string(entry_price),

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
                    cluster_1["minimum"]
                ),

            "maximum":
                decimal_to_string(
                    cluster_1["maximum"]
                ),

            "touches":
                cluster_1["touches"],
        },

        "cluster_2": {

            "average":
                decimal_to_string(
                    cluster_2_avg
                ),

            "minimum":
                decimal_to_string(
                    cluster_2["minimum"]
                ),

            "maximum":
                decimal_to_string(
                    cluster_2["maximum"]
                ),

            "touches":
                cluster_2["touches"],
        },

        "tp1": {

            "price":
                decimal_to_string(tp1),

            "progress_percent":
                decimal_to_string(
                    TP1_PROFIT_MARGIN_PERCENT
                ),

            "status":
                "LOCKED",
        },

        "tp2": {

            "price":
                decimal_to_string(tp2),

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


# END PART 3
id="n4v82k"
# ============================================================
# MAIN R36F.5.3 TEST
# ============================================================

async def run_r36f53():

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
    #
    # IMPORTANT:
    # PASS/FAIL is recorded for visibility.
    # It is NOT added to FINAL_BLOCKERS.
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
    #
    # IMPORTANT:
    # PASS/FAIL is recorded for visibility.
    # It is NOT added to FINAL_BLOCKERS.
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
    #
    # IMPORTANT:
    # PASS/FAIL is recorded for visibility.
    # It is NOT added to FINAL_BLOCKERS.
    # ========================================================

    writer_preview = None

    try:

        if (
            real_long_snapshot is not None
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

        else:

            diagnostic_check(
                "WRITER_REQUEST_CONSTRUCTION",
                False,
                "real long TP snapshot unavailable",
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

        and DEMO_ORDER_EXECUTION is False

        and (
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False
        )

        and (
            ORDER_SUBMISSION_ENABLED
            is False
        )

        and (
            LEVERAGE_MUTATION_ENABLED
            is False
        )

        and (
            MARGIN_MODE_MUTATION_ENABLED
            is False
        )

        and (
            POSITION_MUTATION_ENABLED
            is False
        )

        and (
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
    # R36F.5.3 FINAL GATE
    #
    # IMPORTANT:
    #
    # Frozen diagnostics do not participate in this gate.
    #
    # WEEX_READ_ONLY_RECONCILIATION
    # CANARY_PREVIEW
    # WRITER_REQUEST_CONSTRUCTION
    #
    # remain visibility-only diagnostics.
    # ========================================================

    FINAL_GATE_OK = (
        R36A_EVIDENCE_OK
        and R36C_EVIDENCE_OK
        and R36D_EVIDENCE_OK
        and ZERO_WRITE_INVARIANT_OK
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
            decimal_to_string(MARK_PRICE),

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
            f"write_transport="
            f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED} "
            f"real_execution="
            f"{REAL_ORDER_EXECUTION}"
        )

        await asyncio.sleep(60)


# ============================================================
# ASYNC MAIN
# ============================================================

async def async_main():

    global TEST_STATUS

    start_health_server()

    try:

        await run_r36f53()

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


# END PART 4
