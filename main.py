
#!/usr/bin/env python3
"""
R36F.5.3 - SMALLEST READ-ONLY RECONCILIATION CORRECTION

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5 safety baseline while making
    the read-only WEEX position reconciliation use the correct WEEX V3
    single-position endpoint.

R36F.5.3 CHANGE:

    ONLY the read-only position reconciliation endpoint is corrected.

    Previous:
        /capi/v3/account/position

    Correct WEEX V3 single-position endpoint:
        /capi/v3/account/position/singlePosition

    The synthetic historical-cluster fixtures/tests remain unchanged.

    The production TP policy is unchanged.

R36F.5.3 TP POLICY:

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
    "SMALLEST READ-ONLY RECONCILIATION CORRECTION: "
    "correct the WEEX V3 single-position read endpoint while "
    "preserving the R36F.5.2 synthetic TP diagnostics and "
    "execution safety baseline"
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
    """
    Read the actual WEEX contract mark price.

    WEEX V3 exposes mark price through
    /market/symbolPrice with priceType=MARK.

    The bookTicker endpoint is a bid/ask endpoint and
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
        "Unable to extract WEEX mark price "
        "from symbolPrice MARK response"
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

        # IMPORTANT:
        # Use the dedicated WEEX MARK-price endpoint.
        # bookTicker returns bid/ask data and is not
        # a mark-price source.

        MARK_PRICE = await weex_mark_price(
            session
        )

        log(
            "WEEX MARK PRICE = "
            + decimal_to_string(
                MARK_PRICE
            )
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

        # R36F.5.3:
        # Correct WEEX V3 single-position read endpoint.
        #
        # This is READ-ONLY.
        # No exchange mutation is performed.

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

    quantity = (
        notional
        / MARK_PRICE
    )

    quantity = quantize_down(
        quantity,
        QUANTITY_STEP,
    )

    if quantity < MIN_QUANTITY:

        raise RuntimeError(
            "Canary quantity below minimum"
        )

    return {
        "preview_only": True,
        "symbol": SYMBOL,
        "side": "LONG",
        "mark_price":
            decimal_to_string(
                MARK_PRICE
            ),
        "available_balance":
            decimal_to_string(
                AVAILABLE_BALANCE
            ),
        "margin":
            decimal_to_string(
                margin
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
        "exchange_write_sent": False,
    }


# ============================================================
# END PART 1
# ============================================================


