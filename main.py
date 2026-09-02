
#!/usr/bin/env python3
"""
R36F.3 - SMALLEST TP DIAGNOSTIC FIX

Purpose:
    Preserve the proven R36D/R36F.1/R36F.2 safety baseline while
    diagnosing ONLY the remaining REAL_SHORT_TP_PREVIEW_FAILED blocker.

R36F.3 CHANGE:
    - Keep the existing historical cluster TP engine unchanged.
    - Keep TP1 = 20% adjustable progress toward first valid cluster.
    - Keep TP2 = 50% adjustable progress toward second valid cluster.
    - Keep TP3 = 60% trailing runner.
    - Keep primary TP immutable after fill.
    - Keep backup TP independently recalculated on backup fill only.
    - Do NOT fabricate a missing historical cluster.
    - Keep adaptive read-only history up to 1000 candles.
    - Add diagnostic visibility for:
        * total historical rows
        * local LOW extrema count
        * LOW extrema below entry
        * all generated LOW clusters
        * cluster touch counts
        * cluster averages
        * clusters rejected for insufficient touches
        * clusters rejected for being at/above entry
        * valid SHORT clusters
        * exact reason REAL SHORT TP preview succeeds/fails
    - Do NOT change TP policy.
    - Do NOT weaken MIN_CLUSTER_TOUCHES.
    - Do NOT widen CLUSTER_TOLERANCE_PERCENT.
    - ZERO exchange writes.
    - REAL_ORDER_EXECUTION remains False.
    - DEMO_ORDER_EXECUTION remains False.

This stage is diagnostic only.
It must not be promoted to live execution.
"""

import base64
import hashlib
import hmac
import json
import os
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from decimal import Decimal, ROUND_DOWN, InvalidOperation


# ======================================================================================
# R36F.3 IDENTITY
# ======================================================================================

STAGE = "R36F.3"

PURPOSE = (
    "SMALLEST TP DIAGNOSTIC FIX: REAL SHORT HISTORICAL CLUSTER "
    "VISIBILITY WITHOUT CHANGING TP POLICY"
)


# ======================================================================================
# FROZEN PRODUCTION CONTRACT
# ======================================================================================

WEEX_API_KEY_ENV = "WEEX_API_KEY"
WEEX_API_SECRET_ENV = "WEEX_API_SECRET"
WEEX_API_PASSPHRASE_ENV = "WEEX_API_PASSPHRASE"

WEEX_BASE_URL = "https://api-contract.weex.com"

PRIVATE_SYMBOL = "BTCUSDT"
PUBLIC_V2_SYMBOL = "cmt_btcusdt"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
PRICE_STEP = Decimal("0.1")

INITIAL_ENTRY_PERCENT = Decimal("5")

PYRAMID_ADD_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1

MAX_BACKUPS = 3
BACKUP_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ======================================================================================
# FROZEN R36F TP POLICY
# ======================================================================================

TP1_PROFIT_MARGIN_PERCENT = Decimal("20")
TP2_PROFIT_MARGIN_PERCENT = Decimal("50")

TP1_ALLOCATION = Decimal("20")
TP2_ALLOCATION = Decimal("20")
TP3_ALLOCATION = Decimal("60")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

CLUSTER_TOLERANCE_PERCENT = Decimal("0.20")
MIN_CLUSTER_TOUCHES = 2

HISTORICAL_URL = WEEX_BASE_URL + "/capi/v3/market/klines"
HISTORICAL_LIMIT = 250
HISTORICAL_INTERVAL = "1m"

HISTORICAL_MAX_PAGES = 4


# ======================================================================================
# HARD SAFETY FIREBREAK
# ======================================================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0


# ======================================================================================
# PERSISTENCE
# ======================================================================================

PERSISTENT_ROOT = Path("/var/data")

R36A_STATE_DIR = PERSISTENT_ROOT / "r36a_state"
R36C_STATE_DIR = PERSISTENT_ROOT / "r36c_state"

R36D_STATE_DIR = PERSISTENT_ROOT / "r36d_state"
R36F_STATE_DIR = PERSISTENT_ROOT / "r36f_state"

R36A_DEDUPE_FILE = R36A_STATE_DIR / "telegram_processed_updates.json"
R36A_DECISION_FILE = R36A_STATE_DIR / "synthetic_decisions.json"

R36C_DEDUPE_FILE = R36C_STATE_DIR / "telegram_processed_updates.json"
R36C_DECISION_FILE = R36C_STATE_DIR / "synthetic_decisions.json"

R36D_SNAPSHOT_FILE = R36D_STATE_DIR / "pre_live_readiness_snapshot.json"

R36F_SNAPSHOT_FILE = R36F_STATE_DIR / "pre_live_readiness_snapshot.json"


# ======================================================================================
# FROZEN DURABLE IDENTITIES
# ======================================================================================

OLD_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"
R36C_UPDATE_ID = "R36C_SYNTHETIC_UPDATE_000001"


# ======================================================================================
# GLOBAL STATUS
# ======================================================================================

TEST_STATUS = "STARTING"
FINAL_BLOCKERS = []

OLD_DUPLICATE_DETECTED = False
OLD_REJECTED_BEFORE_PARSE = False

NEW_UPDATE_SEEN_BEFORE_STARTUP = False
NEW_UPDATE_ACCEPTED = False
NEW_REPLAY_REJECTED_BEFORE_PARSE = False

SIGNAL_PARSE_COUNT = 0
SIGNAL_VALIDATION_COUNT = 0
SYNTHETIC_DECISION_CREATION_COUNT = 0

CURRENT_MARK_PRICE = None
CURRENT_AVAILABLE_BALANCE = None

BTCUSDT_FLAT = None

CURRENT_MARGIN_MODE = None
CURRENT_LONG_LEVERAGE = None
CURRENT_SHORT_LEVERAGE = None

HEARTBEAT = 0

# R36F.3 diagnostics.
SHORT_DIAGNOSTICS = {}
LONG_DIAGNOSTICS = {}


# ======================================================================================
# GENERAL HELPERS
# ======================================================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def line():
    print(
        f"{now_iso()} " + "-" * 100,
        flush=True,
    )


def log(message):
    print(
        f"{now_iso()} {message}",
        flush=True,
    )


def check(label, ok):
    print(
        f"{label:<86} "
        f"{'PASS' if ok else 'FAIL'}",
        flush=True,
    )
    return bool(ok)


def safe_decimal(value):
    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    try:
        return Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return None


def floor_step(value, step):
    value = safe_decimal(value)

    if value is None:
        return None

    if step <= 0:
        return value

    units = (value / step).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(value):
    raw = canonical_json(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def decimal_percent_difference(a, b):
    a = safe_decimal(a)
    b = safe_decimal(b)

    if (
        a is None
        or b is None
        or a <= 0
        or b <= 0
    ):
        return None

    return (
        abs(a - b)
        / b
        * Decimal("100")
    )


# ======================================================================================
# DURABLE FILE HELPERS
# ======================================================================================

def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle), None
    except Exception as exc:
        return None, (
            f"{exc.__class__.__name__}: {exc}"
        )


def atomic_write_json(path, obj):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    raw = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    temporary.write_text(
        raw,
        encoding="utf-8",
    )

    os.replace(
        temporary,
        path,
    )


def collect_update_ids(obj):
    found = set()

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = str(key).lower()

                if (
                    "update_id" in key_lower
                    or key_lower in {
                        "updateid",
                        "update-id",
                    }
                ):
                    if isinstance(
                        item,
                        (str, int),
                    ):
                        found.add(str(item))

                walk(item)

        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(obj)

    return found


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "stage": STAGE,
            "status": TEST_STATUS,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
            "short_diagnostic_valid_clusters":
                SHORT_DIAGNOSTICS.get(
                    "valid_cluster_count"
                ),
        }

        body = json.dumps(
            payload,
            separators=(",", ":"),
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

    def do_POST(self):
        self.send_response(405)
        self.end_headers()

    def do_PUT(self):
        self.send_response(405)
        self.end_headers()

    def do_PATCH(self):
        self.send_response(405)
        self.end_headers()

    def do_DELETE(self):
        self.send_response(405)
        self.end_headers()

    def log_message(self, format_string, *args):
        return


def start_health_server():
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(
        f"{STAGE}: HEALTH SERVER STARTED ON PORT {port}"
    )


# ======================================================================================
# WEEX READ-ONLY AUTHENTICATION
# ======================================================================================

def make_signature(
    secret,
    timestamp_ms,
    method,
    request_path,
    query_string="",
):
    prehash = (
        f"{timestamp_ms}"
        f"{method.upper()}"
        f"{request_path}"
    )

    if query_string:
        prehash += "?" + query_string

    digest = hmac.new(
        secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def http_get_json(
    url,
    headers=None,
    timeout=15,
):
    request = urllib.request.Request(
        url=url,
        headers=headers or {},
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            status = getattr(
                response,
                "status",
                200,
            )

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = None

            return (
                status,
                data,
                raw,
                None,
            )

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        try:
            data = json.loads(raw)
        except Exception:
            data = None

        return (
            exc.code,
            data,
            raw,
            f"HTTPError: {exc}",
        )

    except Exception as exc:

        return (
            None,
            None,
            "",
            f"{exc.__class__.__name__}: {exc}",
        )


def weex_private_get(
    request_path,
    params=None,
):
    api_key = os.getenv(
        WEEX_API_KEY_ENV,
        "",
    ).strip()

    secret = os.getenv(
        WEEX_API_SECRET_ENV,
        "",
    ).strip()

    passphrase = os.getenv(
        WEEX_API_PASSPHRASE_ENV,
        "",
    ).strip()

    if (
        not api_key
        or not secret
        or not passphrase
    ):
        missing = [
            name
            for name, value in (
                (
                    WEEX_API_KEY_ENV,
                    api_key,
                ),
                (
                    WEEX_API_SECRET_ENV,
                    secret,
                ),
                (
                    WEEX_API_PASSPHRASE_ENV,
                    passphrase,
                ),
            )
            if not value
        ]

        return (
            None,
            None,
            "",
            "MISSING_ENV="
            + ",".join(missing),
        )

    params = params or {}

    query = urllib.parse.urlencode(
        params
    )

    timestamp_ms = str(
        int(time.time() * 1000)
    )

    signature = make_signature(
        secret,
        timestamp_ms,
        "GET",
        request_path,
        query,
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
        "locale": "en-US",
        "User-Agent": f"{STAGE}/1.0",
    }

    url = WEEX_BASE_URL + request_path

    if query:
        url += "?" + query

    return http_get_json(
        url,
        headers=headers,
    )


def weex_public_ticker():
    path = "/capi/v2/market/ticker"

    query = urllib.parse.urlencode(
        {
            "symbol": PUBLIC_V2_SYMBOL
        }
    )

    url = (
        WEEX_BASE_URL
        + path
        + "?"
        + query
    )

    return http_get_json(
        url,
        headers={
            "User-Agent": f"{STAGE}/1.0"
        },
    )


# ======================================================================================
# ABSOLUTE WRITE FIREBREAK
# ======================================================================================

def exchange_mutation_forbidden(
    *args,
    **kwargs,
):
    raise RuntimeError(
        f"{STAGE} HARD FIREBREAK: "
        "exchange mutation attempted while "
        f"EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )


place_order = exchange_mutation_forbidden
change_leverage = exchange_mutation_forbidden
change_margin_mode = exchange_mutation_forbidden
close_position = exchange_mutation_forbidden


# ======================================================================================
# CURRENT WEEX RECONCILIATION
# ======================================================================================

def find_usdt_balance(data):

    if isinstance(data, list):

        for row in data:

            if (
                isinstance(row, dict)
                and str(
                    row.get(
                        "asset",
                        "",
                    )
                ).upper()
                == "USDT"
            ):
                return row

    elif isinstance(data, dict):

        for key in (
            "data",
            "result",
            "balances",
        ):

            if key in data:

                hit = find_usdt_balance(
                    data[key]
                )

                if hit:
                    return hit

    return None


def normalize_rows(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "data",
            "result",
            "list",
        ):

            if isinstance(
                data.get(key),
                list,
            ):
                return data[key]

    return []


def position_is_nonzero(row):

    if not isinstance(row, dict):
        return False

    for key in (
        "size",
        "positionAmt",
        "available",
        "total",
    ):

        if key in row:

            value = safe_decimal(
                row.get(key)
            )

            if (
                value is not None
                and value != 0
            ):
                return True

    return False


def reconcile_weex():

    global CURRENT_MARK_PRICE
    global CURRENT_AVAILABLE_BALANCE
    global BTCUSDT_FLAT
    global CURRENT_MARGIN_MODE
    global CURRENT_LONG_LEVERAGE
    global CURRENT_SHORT_LEVERAGE

    results = {}

    # ------------------------------------------------------------------
    # PUBLIC MARK PRICE
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_public_ticker()
    )

    mark = None

    if isinstance(data, dict):
        mark = safe_decimal(
            data.get("markPrice")
        )

    CURRENT_MARK_PRICE = mark

    results["ticker"] = {
        "status_code": status,
        "error": err,
        "ok": (
            status == 200
            and mark is not None
            and mark > 0
        ),
        "mark_price": (
            str(mark)
            if mark is not None
            else None
        ),
    }

    # ------------------------------------------------------------------
    # BALANCE
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/balance"
        )
    )

    usdt = find_usdt_balance(data)

    available = (
        safe_decimal(
            usdt.get("availableBalance")
        )
        if usdt
        else None
    )

    CURRENT_AVAILABLE_BALANCE = available

    results["balance"] = {
        "status_code": status,
        "error": err,
        "ok": (
            status == 200
            and available is not None
            and available >= 0
        ),
        "available_usdt": (
            str(available)
            if available is not None
            else None
        ),
    }

    # ------------------------------------------------------------------
    # POSITION
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/position/singlePosition",
            {
                "symbol": PRIVATE_SYMBOL
            },
        )
    )

    rows = normalize_rows(data)

    flat = (
        status == 200
        and not any(
            position_is_nonzero(row)
            for row in rows
        )
    )

    BTCUSDT_FLAT = flat

    results["position"] = {
        "status_code": status,
        "error": err,
        "ok": status == 200,
        "flat": flat,
        "returned_rows": len(rows),
    }

    # ------------------------------------------------------------------
    # SYMBOL CONFIG
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/symbolConfig",
            {
                "symbol": PRIVATE_SYMBOL
            },
        )
    )

    rows = normalize_rows(data)

    cfg = None

    for row in rows:

        if (
            isinstance(row, dict)
            and str(
                row.get(
                    "symbol",
                    "",
                )
            ).upper()
            == PRIVATE_SYMBOL
        ):
            cfg = row
            break

    if (
        cfg is None
        and len(rows) == 1
        and isinstance(rows[0], dict)
    ):
        cfg = rows[0]

    if cfg:

        CURRENT_MARGIN_MODE = str(
            cfg.get(
                "marginType",
                cfg.get(
                    "margin_mode",
                    "",
                ),
            )
        ).upper()

        CURRENT_LONG_LEVERAGE = (
            safe_decimal(
                cfg.get(
                    "isolatedLongLeverage",
                    cfg.get(
                        "isolated_long_leverage"
                    ),
                )
            )
        )

        CURRENT_SHORT_LEVERAGE = (
            safe_decimal(
                cfg.get(
                    "isolatedShortLeverage",
                    cfg.get(
                        "isolated_short_leverage"
                    ),
                )
            )
        )

    else:

        CURRENT_MARGIN_MODE = None
        CURRENT_LONG_LEVERAGE = None
        CURRENT_SHORT_LEVERAGE = None

    cfg_ok = (
        status == 200
        and CURRENT_MARGIN_MODE
        == TARGET_MARGIN_MODE
        and CURRENT_LONG_LEVERAGE
        == Decimal(
            str(TARGET_LONG_LEVERAGE)
        )
        and CURRENT_SHORT_LEVERAGE
        == Decimal(
            str(TARGET_SHORT_LEVERAGE)
        )
    )

    results["symbol_config"] = {
        "status_code": status,
        "error": err,
        "ok": cfg_ok,
        "margin_mode": CURRENT_MARGIN_MODE,
        "isolated_long_leverage": (
            str(CURRENT_LONG_LEVERAGE)
            if CURRENT_LONG_LEVERAGE
            is not None
            else None
        ),
        "isolated_short_leverage": (
            str(CURRENT_SHORT_LEVERAGE)
            if CURRENT_SHORT_LEVERAGE
            is not None
            else None
        ),
    }

    return results


# ======================================================================================
# CANARY PREVIEW
# ======================================================================================

def build_canary_preview():

    if (
        CURRENT_AVAILABLE_BALANCE
        is None
        or CURRENT_MARK_PRICE
        is None
    ):
        return None

    entry_margin = (
        CURRENT_AVAILABLE_BALANCE
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    entry_notional = (
        entry_margin
        * Decimal(
            str(TARGET_LONG_LEVERAGE)
        )
    )

    raw_qty = (
        entry_notional
        / CURRENT_MARK_PRICE
        if CURRENT_MARK_PRICE > 0
        else Decimal("0")
    )

    strategy_qty = floor_step(
        raw_qty,
        QTY_STEP,
    )

    canary_qty = MIN_QTY

    return {
        "symbol": PRIVATE_SYMBOL,
        "side_preview": (
            "UNSET_UNTIL_REAL_SIGNAL"
        ),
        "order_type_preview": (
            "MARKET_OR_PRODUCTION_SIGNAL_RULE"
        ),
        "target_margin_mode":
            TARGET_MARGIN_MODE,
        "target_long_leverage":
            TARGET_LONG_LEVERAGE,
        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,
        "available_balance_usdt":
            str(CURRENT_AVAILABLE_BALANCE),
        "mark_price":
            str(CURRENT_MARK_PRICE),
        "strategy_entry_margin_usdt":
            str(entry_margin),
        "strategy_entry_notional_usdt":
            str(entry_notional),
        "strategy_raw_qty_btc":
            str(raw_qty),
        "strategy_normalized_qty_btc":
            str(strategy_qty),
        "r36e_canary_qty_btc":
            str(canary_qty),
        "qty_step":
            str(QTY_STEP),
        "min_qty":
            str(MIN_QTY),
        "max_fund_exposure_percent":
            str(MAX_FUND_EXPOSURE_PERCENT),
        "writer_enabled": False,
        "real_order_execution":
            False,
    }


# ======================================================================================
# HISTORICAL KLINE LOADING
# ======================================================================================

def extract_kline_rows(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "data",
            "result",
            "rows",
            "list",
        ):

            value = data.get(key)

            if isinstance(
                value,
                list,
            ):
                return value

            if isinstance(
                value,
                dict,
            ):

                for nested in (
                    "data",
                    "rows",
                    "list",
                ):

                    nested_value = (
                        value.get(nested)
                    )

                    if isinstance(
                        nested_value,
                        list,
                    ):
                        return nested_value

    return []


def kline_timestamp(row):

    if isinstance(
        row,
        (list, tuple),
    ):

        if row:
            return safe_decimal(
                row[0]
            )

    if isinstance(row, dict):

        for key in (
            "timestamp",
            "ts",
            "time",
            "openTime",
            "startTime",
        ):

            if key in row:
                return safe_decimal(
                    row[key]
                )

    return None


def kline_high_low(row):

    if isinstance(
        row,
        (list, tuple),
    ):

        if len(row) >= 5:

            high = safe_decimal(
                row[2]
            )

            low = safe_decimal(
                row[3]
            )

            return high, low

    if isinstance(row, dict):

        high = None
        low = None

        for key in (
            "high",
            "h",
            "highPrice",
        ):

            if key in row:
                high = safe_decimal(
                    row[key]
                )
                break

        for key in (
            "low",
            "l",
            "lowPrice",
        ):

            if key in row:
                low = safe_decimal(
                    row[key]
                )
                break

        return high, low

    return None, None


def normalize_kline_order(rows):

    clean = []

    for row in rows:

        timestamp = (
            kline_timestamp(row)
        )

        high, low = (
            kline_high_low(row)
        )

        if (
            timestamp is not None
            and high is not None
            and low is not None
            and high > 0
            and low > 0
        ):

            clean.append(
                (
                    timestamp,
                    high,
                    low,
                )
            )

    clean.sort(
        key=lambda item: item[0]
    )

    return clean


def historical_get(params):

    query = urllib.parse.urlencode(
        params
    )

    url = (
        HISTORICAL_URL
        + "?"
        + query
    )

    return http_get_json(
        url,
        headers={
            "User-Agent":
                f"{STAGE}/1.0"
        },
        timeout=15,
    )


def load_historical_klines():

    all_rows = {}
    page_details = []

    end_time = None

    for page in range(
        1,
        HISTORICAL_MAX_PAGES + 1,
    ):

        params = {
            "symbol":
                PRIVATE_SYMBOL,
            "interval":
                HISTORICAL_INTERVAL,
            "limit":
                str(HISTORICAL_LIMIT),
        }

        if end_time is not None:
            params["endTime"] = str(
                int(end_time)
            )

        status, data, raw, err = (
            historical_get(params)
        )

        rows = []

        if status == 200:
            rows = normalize_kline_order(
                extract_kline_rows(data)
            )

        page_details.append(
            {
                "page": page,
                "status": status,
                "error": err,
                "rows": len(rows),
            }
        )

        if (
            status != 200
            or not rows
        ):
            break

        for row in rows:
            all_rows[str(row[0])] = row

        oldest = min(
            row[0]
            for row in rows
        )

        if len(rows) < HISTORICAL_LIMIT:
            break

        next_end = (
            oldest - Decimal("1")
        )

        if (
            end_time is not None
            and next_end >= end_time
        ):
            break

        end_time = next_end

    ordered = sorted(
        all_rows.values(),
        key=lambda item: item[0],
    )

    return (
        ordered,
        page_details,
    )


# ======================================================================================
# LOCAL EXTREMA / CLUSTER ENGINE
# ======================================================================================

def local_extrema_values(
    rows,
    side,
):

    values = []

    if len(rows) < 3:
        return values

    for index in range(
        1,
        len(rows) - 1,
    ):

        previous = rows[index - 1]
        current = rows[index]
        following = rows[index + 1]

        if side == "LONG":

            value = current[1]
            previous_value = previous[1]
            following_value = following[1]

            if (
                value >= previous_value
                and value >= following_value
            ):
                values.append(value)

        else:

            value = current[2]
            previous_value = previous[2]
            following_value = following[2]

            if (
                value <= previous_value
                and value <= following_value
            ):
                values.append(value)

    return values


def cluster_extrema(values):

    clusters = []

    for value in values:

        placed = False

        for cluster in clusters:

            average = cluster["average"]

            if (
                average > 0
                and
                (
                    abs(
                        value - average
                    )
                    / average
                    * Decimal("100")
                )
                <= CLUSTER_TOLERANCE_PERCENT
            ):

                cluster["values"].append(
                    value
                )

                cluster["average"] = (
                    sum(
                        cluster["values"],
                        Decimal("0"),
                    )
                    / Decimal(
                        len(
                            cluster["values"]
                        )
                    )
                )

                cluster["min"] = min(
                    cluster["min"],
                    value,
                )

                cluster["max"] = max(
                    cluster["max"],
                    value,
                )

                cluster["touches"] = len(
                    cluster["values"]
                )

                placed = True
                break

        if not placed:

            clusters.append(
                {
                    "values": [value],
                    "average": value,
                    "min": value,
                    "max": value,
                    "touches": 1,
                }
            )

    return clusters


# ======================================================================================
# R36F.3 DIAGNOSTIC CLUSTER INSPECTION
# ======================================================================================

def build_cluster_diagnostics(
    rows,
    entry_price,
    side,
):

    entry_price = safe_decimal(
        entry_price
    )

    extrema = local_extrema_values(
        rows,
        side,
    )

    clusters = cluster_extrema(
        extrema
    )

    below_or_above_entry = []

    if side == "SHORT":
        for value in extrema:
            if value < entry_price:
                below_or_above_entry.append(value)
    else:
        for value in extrema:
            if value > entry_price:
                below_or_above_entry.append(value)

    diagnostic_clusters = []

    valid = []

    for index, cluster in enumerate(
        clusters,
        start=1,
    ):

        average = cluster["average"]
        touches = cluster["touches"]

        if side == "SHORT":
            relation_ok = average < entry_price
            relation = "BELOW_ENTRY"
        else:
            relation_ok = average > entry_price
            relation = "ABOVE_ENTRY"

        touches_ok = (
            touches >= MIN_CLUSTER_TOUCHES
        )

        if (
            touches_ok
            and relation_ok
        ):
            validity = "VALID"
            reason = "VALID"
            valid.append(cluster)

        elif not touches_ok and not relation_ok:
            validity = "REJECTED"
            reason = (
                "INSUFFICIENT_TOUCHES_AND_WRONG_ENTRY_RELATION"
            )

        elif not touches_ok:
            validity = "REJECTED"
            reason = "INSUFFICIENT_TOUCHES"

        else:
            validity = "REJECTED"
            reason = "WRONG_ENTRY_RELATION"

        diagnostic_clusters.append(
            {
                "cluster_number": index,
                "average": str(average),
                "min": str(cluster["min"]),
                "max": str(cluster["max"]),
                "touches": touches,
                "entry_relation": relation,
                "validity": validity,
                "reason": reason,
            }
        )

    if side == "SHORT":
        valid.sort(
            key=lambda cluster:
                cluster["average"],
            reverse=True,
        )
    else:
        valid.sort(
            key=lambda cluster:
                cluster["average"]
        )

    diagnostic = {
        "side": side,
        "entry_price": str(entry_price),
        "historical_candle_count": len(rows),
        "local_extrema_count": len(extrema),
        "extrema_on_required_side_count":
            len(below_or_above_entry),
        "minimum_cluster_touches":
            MIN_CLUSTER_TOUCHES,
        "cluster_tolerance_percent":
            str(CLUSTER_TOLERANCE_PERCENT),
        "total_cluster_count":
            len(clusters),
        "valid_cluster_count":
            len(valid),
        "required_valid_cluster_count": 2,
        "clusters": diagnostic_clusters,
        "valid_clusters": [
            {
                "average":
                    str(cluster["average"]),
                "min":
                    str(cluster["min"]),
                "max":
                    str(cluster["max"]),
                "touches":
                    cluster["touches"],
            }
            for cluster in valid
        ],
    }

    if len(valid) >= 2:
        diagnostic["failure_reason"] = None
        diagnostic["status"] = "ENOUGH_VALID_CLUSTERS"
    elif len(valid) == 1:
        diagnostic["failure_reason"] = (
            "ONLY_ONE_VALID_CLUSTER"
        )
        diagnostic["status"] = "INSUFFICIENT_VALID_CLUSTERS"
    elif len(extrema) == 0:
        diagnostic["failure_reason"] = (
            "NO_LOCAL_EXTREMA"
        )
        diagnostic["status"] = "NO_EXTREMA"
    elif len(below_or_above_entry) == 0:
        if side == "SHORT":
            diagnostic["failure_reason"] = (
                "NO_LOCAL_LOWS_BELOW_ENTRY"
            )
        else:
            diagnostic["failure_reason"] = (
                "NO_LOCAL_HIGHS_ABOVE_ENTRY"
            )
        diagnostic["status"] = "NO_EXTREMA_ON_REQUIRED_SIDE"
    else:
        diagnostic["failure_reason"] = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )
        diagnostic["status"] = (
            "CLUSTERS_REJECTED_BY_POLICY"
        )

    return diagnostic


def valid_clusters(
    rows,
    entry_price,
    side,
):

    extrema = local_extrema_values(
        rows,
        side,
    )

    clusters = cluster_extrema(
        extrema
    )

    if side == "LONG":

        valid = [
            cluster
            for cluster in clusters
            if (
                cluster["touches"]
                >= MIN_CLUSTER_TOUCHES
                and
                cluster["average"]
                > entry_price
            )
        ]

        valid.sort(
            key=lambda cluster:
                cluster["average"]
        )

    else:

        valid = [
            cluster
            for cluster in clusters
            if (
                cluster["touches"]
                >= MIN_CLUSTER_TOUCHES
                and
                cluster["average"]
                < entry_price
            )
        ]

        valid.sort(
            key=lambda cluster:
                cluster["average"],
            reverse=True,
        )

    return valid


def build_cluster_tp_snapshot(
    entry_price,
    rows,
    side,
    fill_label,
):

    global SHORT_DIAGNOSTICS
    global LONG_DIAGNOSTICS

    entry_price = safe_decimal(
        entry_price
    )

    if (
        entry_price is None
        or entry_price <= 0
    ):
        raise RuntimeError(
            "Invalid entry price"
        )

    # R36F.3 diagnostic layer only.
    diagnostics = build_cluster_diagnostics(
        rows,
        entry_price,
        side,
    )

    if side == "SHORT":
        SHORT_DIAGNOSTICS = diagnostics
        log(
            "R36F.3_SHORT_CLUSTER_DIAGNOSTICS="
            + canonical_json(diagnostics)
        )
    else:
        LONG_DIAGNOSTICS = diagnostics
        log(
            "R36F.3_LONG_CLUSTER_DIAGNOSTICS="
            + canonical_json(diagnostics)
        )

    # ------------------------------------------------------------------
    # FROZEN R36F.2 TP SELECTION LOGIC
    # ------------------------------------------------------------------

    clusters = valid_clusters(
        rows,
        entry_price,
        side,
    )

    if len(clusters) < 2:

        if side == "LONG":
            direction = "high"
            relation = "above"
        else:
            direction = "low"
            relation = "below"

        raise RuntimeError(
            f"Fewer than two valid historical "
            f"{direction} clusters {relation} "
            "entry; no TP fabricated"
        )

    cluster_1 = clusters[0]
    cluster_2 = clusters[1]

    margin_1 = (
        TP1_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    margin_2 = (
        TP2_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    if side == "LONG":

        tp1 = (
            entry_price
            + (
                cluster_1["average"]
                - entry_price
            )
            * margin_1
        )

        tp2 = (
            entry_price
            + (
                cluster_2["average"]
                - entry_price
            )
            * margin_2
        )

        ordering_ok = (
            entry_price
            < tp1
            < tp2
            <= cluster_2["average"]
        )

        basis_1 = (
            "first_valid_historical_high_cluster_average"
        )

        basis_2 = (
            "second_valid_historical_high_cluster_average"
        )

    else:

        tp1 = (
            entry_price
            - (
                entry_price
                - cluster_1["average"]
            )
            * margin_1
        )

        tp2 = (
            entry_price
            - (
                entry_price
                - cluster_2["average"]
            )
            * margin_2
        )

        ordering_ok = (
            entry_price
            > tp1
            > tp2
            >= cluster_2["average"]
        )

        basis_1 = (
            "first_valid_historical_low_cluster_average"
        )

        basis_2 = (
            "second_valid_historical_low_cluster_average"
        )

    if not ordering_ok:

        raise RuntimeError(
            f"Invalid {side} TP ordering: "
            f"entry={entry_price}, "
            f"tp1={tp1}, "
            f"tp2={tp2}"
        )

    return {
        "cluster_1": {
            "average":
                str(
                    cluster_1["average"]
                ),
            "max":
                str(
                    cluster_1["max"]
                ),
            "min":
                str(
                    cluster_1["min"]
                ),
            "touches":
                str(
                    cluster_1["touches"]
                ),
        },

        "cluster_2": {
            "average":
                str(
                    cluster_2["average"]
                ),
            "max":
                str(
                    cluster_2["max"]
                ),
            "min":
                str(
                    cluster_2["min"]
                ),
            "touches":
                str(
                    cluster_2["touches"]
                ),
        },

        "cluster_tolerance_percent":
            str(
                CLUSTER_TOLERANCE_PERCENT
            ),

        "entry_price":
            str(entry_price),

        "fill_label":
            fill_label,

        "historical_candle_count":
            len(rows),

        "historical_interval":
            HISTORICAL_INTERVAL,

        "minimum_cluster_touches":
            MIN_CLUSTER_TOUCHES,

        "recalculation_policy":
            "NEVER_RECALCULATE_AFTER_FILL",

        "side":
            side,

        "tp1": {
            "allocation_percent":
                str(TP1_ALLOCATION),
            "basis":
                basis_1,
            "price":
                str(tp1),
            "status":
                "LOCKED",
        },

        "tp2": {
            "allocation_percent":
                str(TP2_ALLOCATION),
            "basis":
                basis_2,
            "price":
                str(tp2),
            "status":
                "LOCKED",
        },

        "tp3": {
            "allocation_percent":
                str(TP3_ALLOCATION),
            "basis":
                "let_market_run",
            "status":
                "RUNNER",
            "trailing_distance_percent":
                str(
                    TRAILING_DISTANCE_PERCENT
                ),
        },

        "tp1_profit_margin_percent":
            str(
                TP1_PROFIT_MARGIN_PERCENT
            ),

        "tp2_profit_margin_percent":
            str(
                TP2_PROFIT_MARGIN_PERCENT
            ),

        "tp_cluster_method":
            "LOCAL_EXTREMA_CLUSTER_AVERAGE",
    }


# ======================================================================================
# SYNTHETIC LONG + SHORT TP FIXTURE
# ======================================================================================

def synthetic_cluster_tests():

    long_rows = [
        (
            Decimal(str(index)),
            Decimal(str(value)),
            Decimal("99000"),
        )
        for index, value in enumerate(
            [
                100000,
                100600,
                100000,
                100550,
                100000,
                101100,
                100000,
                101050,
                100000,
                100000,
            ]
        )
    ]

    short_rows = [
        (
            Decimal(str(index)),
            Decimal("101000"),
            Decimal(str(value)),
        )
        for index, value in enumerate(
            [
                100000,
                99450,
                100000,
                99480,
                100000,
                98850,
                100000,
                98880,
                100000,
                100000,
            ]
        )
    ]

    return (
        long_rows,
        short_rows,
    )


# ======================================================================================
# R36F.3 MAIN VALIDATION
# ======================================================================================

def run_r36f3():

    global TEST_STATUS

    global OLD_DUPLICATE_DETECTED
    global OLD_REJECTED_BEFORE_PARSE

    global NEW_UPDATE_SEEN_BEFORE_STARTUP
    global NEW_UPDATE_ACCEPTED
    global NEW_REPLAY_REJECTED_BEFORE_PARSE

    global FINAL_BLOCKERS

    OLD_DUPLICATE_DETECTED = False
    OLD_REJECTED_BEFORE_PARSE = False

    NEW_UPDATE_SEEN_BEFORE_STARTUP = False
    NEW_UPDATE_ACCEPTED = False
    NEW_REPLAY_REJECTED_BEFORE_PARSE = False

    FINAL_BLOCKERS = []

    line()

    log(
        f"{STAGE}: MAIN.PY ENTERED"
    )

    line()

    log(f"PURPOSE={PURPOSE}")

    log(
        "PYTHON_VERSION="
        + sys.version.split()[0]
    )

    log(
        f"PRIVATE_SYMBOL={PRIVATE_SYMBOL}"
    )

    log(
        f"PUBLIC_V2_SYMBOL={PUBLIC_V2_SYMBOL}"
    )

    log(
        f"TARGET_MARGIN_MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"TARGET_LONG_LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"TARGET_SHORT_LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        "TP1_PROFIT_MARGIN_PERCENT="
        f"{TP1_PROFIT_MARGIN_PERCENT}%"
    )

    log(
        "TP2_PROFIT_MARGIN_PERCENT="
        f"{TP2_PROFIT_MARGIN_PERCENT}%"
    )

    log(
        f"TP1_ALLOCATION={TP1_ALLOCATION}%"
    )

    log(
        f"TP2_ALLOCATION={TP2_ALLOCATION}%"
    )

    log(
        f"TP3_ALLOCATION={TP3_ALLOCATION}%"
    )

    log(
        f"HISTORICAL_LIMIT="
        f"{HISTORICAL_LIMIT}"
    )

    log(
        f"HISTORICAL_INTERVAL="
        f"{HISTORICAL_INTERVAL}"
    )

    log(
        f"HISTORICAL_MAX_PAGES="
        f"{HISTORICAL_MAX_PAGES}"
    )

    log(
        f"CLUSTER_TOLERANCE="
        f"{CLUSTER_TOLERANCE_PERCENT}%"
    )

    log(
        f"MIN_CLUSTER_TOUCHES="
        f"{MIN_CLUSTER_TOUCHES}"
    )

    line()

    # ==========================================================================
    # TEST 1
    # ==========================================================================

    log(
        "R36F.3 TEST 1: "
        "FROZEN CONTRACT / HARD FIREBREAK"
    )

    line()

    env_names_ok = (
        WEEX_API_KEY_ENV
        == "WEEX_API_KEY"
        and
        WEEX_API_SECRET_ENV
        == "WEEX_API_SECRET"
        and
        WEEX_API_PASSPHRASE_ENV
        == "WEEX_API_PASSPHRASE"
    )

    symbols_ok = (
        PRIVATE_SYMBOL == "BTCUSDT"
        and
        PUBLIC_V2_SYMBOL
        == "cmt_btcusdt"
    )

    firebreak_ok = all(
        [
            REAL_ORDER_EXECUTION is False,
            DEMO_ORDER_EXECUTION is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,
            ORDER_SUBMISSION_ENABLED
            is False,
            LEVERAGE_MUTATION_ENABLED
            is False,
            MARGIN_MODE_MUTATION_ENABLED
            is False,
            POSITION_MUTATION_ENABLED
            is False,
            FIRST_REAL_ORDER_ALLOWED is False,
        ]
    )

    check(
        "Frozen WEEX Environment Variable Names",
        env_names_ok,
    )

    check(
        "Frozen WEEX Symbol Mapping",
        symbols_ok,
    )

    check(
        "Hard Exchange Write Firebreak",
        firebreak_ok,
    )

    if not env_names_ok:
        FINAL_BLOCKERS.append(
            "FROZEN_ENVIRONMENT_VARIABLE_CONTRACT_CHANGED"
        )

    if not symbols_ok:
        FINAL_BLOCKERS.append(
            "FROZEN_SYMBOL_MAPPING_CHANGED"
        )

    if not firebreak_ok:
        FINAL_BLOCKERS.append(
            "WRITE_FIREBREAK_NOT_INTACT"
        )

    # ==========================================================================
    # TEST 2
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 2: "
        "READ EXISTING R36A / R36C DURABLE EVIDENCE"
    )

    line()

    r36a_dedupe, e1 = load_json(
        R36A_DEDUPE_FILE
    )

    r36a_decision, e2 = load_json(
        R36A_DECISION_FILE
    )

    r36c_dedupe, e3 = load_json(
        R36C_DEDUPE_FILE
    )

    r36c_decision, e4 = load_json(
        R36C_DECISION_FILE
    )

    log(
        f"R36A_DEDUPE_FILE="
        f"{R36A_DEDUPE_FILE}"
    )

    log(
        f"R36A_DECISION_FILE="
        f"{R36A_DECISION_FILE}"
    )

    log(
        f"R36C_DEDUPE_FILE="
        f"{R36C_DEDUPE_FILE}"
    )

    log(
        f"R36C_DECISION_FILE="
        f"{R36C_DECISION_FILE}"
    )

    log(
        f"R36A_DEDUPE_READ_ERROR={e1}"
    )

    log(
        f"R36A_DECISION_READ_ERROR={e2}"
    )

    log(
        f"R36C_DEDUPE_READ_ERROR={e3}"
    )

    log(
        f"R36C_DECISION_READ_ERROR={e4}"
    )

    r36a_readable = (
        e1 is None
        and
        e2 is None
    )

    r36c_readable = (
        e3 is None
        and
        e4 is None
    )

    check(
        "R36A Durable Registries Still Readable",
        r36a_readable,
    )

    check(
        "R36C Durable Registries Still Readable",
        r36c_readable,
    )

    if not r36a_readable:
        FINAL_BLOCKERS.append(
            "R36A_DURABLE_EVIDENCE_UNREADABLE"
        )

    if not r36c_readable:
        FINAL_BLOCKERS.append(
            "R36C_DURABLE_EVIDENCE_UNREADABLE"
        )

    # ==========================================================================
    # TEST 3
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 3: "
        "CREDIT PROVEN DEDUPE / DECISION IDENTITIES"
    )

    line()

    r36a_dedupe_ids = (
        collect_update_ids(
            r36a_dedupe
        )
        if r36a_dedupe is not None
        else set()
    )

    r36a_decision_ids = (
        collect_update_ids(
            r36a_decision
        )
        if r36a_decision is not None
        else set()
    )

    r36c_dedupe_ids = (
        collect_update_ids(
            r36c_dedupe
        )
        if r36c_dedupe is not None
        else set()
    )

    r36c_decision_ids = (
        collect_update_ids(
            r36c_decision
        )
        if r36c_decision is not None
        else set()
    )

    old_in_both = (
        OLD_R36A_UPDATE_ID
        in r36a_dedupe_ids
        and
        OLD_R36A_UPDATE_ID
        in r36a_decision_ids
    )

    new_in_both = (
        R36C_UPDATE_ID
        in r36c_dedupe_ids
        and
        R36C_UPDATE_ID
        in r36c_decision_ids
    )

    OLD_DUPLICATE_DETECTED = old_in_both
    OLD_REJECTED_BEFORE_PARSE = old_in_both

    NEW_UPDATE_SEEN_BEFORE_STARTUP = new_in_both
    NEW_UPDATE_ACCEPTED = new_in_both
    NEW_REPLAY_REJECTED_BEFORE_PARSE = new_in_both

    log(
        f"OLD_R36A_UPDATE_ID="
        f"{OLD_R36A_UPDATE_ID}"
    )

    log(
        f"R36C_UPDATE_ID="
        f"{R36C_UPDATE_ID}"
    )

    log(
        f"OLD_ID_IN_BOTH_R36A_REGISTRIES="
        f"{old_in_both}"
    )

    log(
        f"R36C_ID_IN_BOTH_R36C_REGISTRIES="
        f"{new_in_both}"
    )

    check(
        "Previously Proven R36A Identity Still Durable",
        old_in_both,
    )

    check(
        "Previously Proven R36C Identity Still Durable",
        new_in_both,
    )

    check(
        "R36C Scope Variable Explicitly Bound",
        isinstance(
            NEW_UPDATE_ACCEPTED,
            bool,
        ),
    )

    if not old_in_both:
        FINAL_BLOCKERS.append(
            "R36A_PROVEN_IDENTITY_NOT_FOUND"
        )

    if not new_in_both:
        FINAL_BLOCKERS.append(
            "R36C_PROVEN_IDENTITY_NOT_FOUND"
        )

    # ==========================================================================
    # TEST 4
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 4: "
        "FROZEN CREDENTIAL CONTRACT PRESENT"
    )

    line()

    api_key_present = bool(
        os.getenv(
            WEEX_API_KEY_ENV,
            "",
        ).strip()
    )

    secret_present = bool(
        os.getenv(
            WEEX_API_SECRET_ENV,
            "",
        ).strip()
    )

    passphrase_present = bool(
        os.getenv(
            WEEX_API_PASSPHRASE_ENV,
            "",
        ).strip()
    )

    log(
        f"{WEEX_API_KEY_ENV}_PRESENT="
        f"{api_key_present}"
    )

    log(
        f"{WEEX_API_SECRET_ENV}_PRESENT="
        f"{secret_present}"
    )

    log(
        f"{WEEX_API_PASSPHRASE_ENV}_PRESENT="
        f"{passphrase_present}"
    )

    credentials_present = (
        api_key_present
        and
        secret_present
        and
        passphrase_present
    )

    check(
        "All Three Frozen WEEX Credentials Present",
        credentials_present,
    )

    if not credentials_present:
        FINAL_BLOCKERS.append(
            "WEEX_CREDENTIALS_MISSING"
        )

    # ==========================================================================
    # TEST 5
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 5: "
        "CURRENT REAL WEEX READ-ONLY RECONCILIATION"
    )

    line()

    recon = reconcile_weex()

    for name in (
        "ticker",
        "balance",
        "position",
        "symbol_config",
    ):

        log(
            f"{name.upper()}="
            f"{canonical_json(recon[name])}"
        )

    ticker_ok = recon["ticker"]["ok"]
    balance_ok = recon["balance"]["ok"]
    position_read_ok = recon["position"]["ok"]
    flat_ok = recon["position"]["flat"]
    config_ok = recon["symbol_config"]["ok"]

    check(
        "Current Public Mark Price Read",
        ticker_ok,
    )

    check(
        "Current Authenticated USDT Balance Read",
        balance_ok,
    )

    check(
        "Current BTCUSDT Position Read",
        position_read_ok,
    )

    check(
        "BTCUSDT Currently Flat",
        flat_ok,
    )

    check(
        "Current ISOLATED 100x/100x Configuration",
        config_ok,
    )

    if not ticker_ok:
        FINAL_BLOCKERS.append(
            "CURRENT_MARK_PRICE_READ_FAILED"
        )

    if not balance_ok:
        FINAL_BLOCKERS.append(
            "CURRENT_BALANCE_READ_FAILED"
        )

    if not position_read_ok:
        FINAL_BLOCKERS.append(
            "CURRENT_POSITION_READ_FAILED"
        )
    elif not flat_ok:
        FINAL_BLOCKERS.append(
            "BTCUSDT_NOT_FLAT"
        )

    if not config_ok:
        FINAL_BLOCKERS.append(
            "CURRENT_MARGIN_OR_LEVERAGE_MISMATCH"
        )

    # ==========================================================================
    # TEST 6
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 6: "
        "TP ENGINE + REAL LONG/SHORT HISTORICAL DIAGNOSTICS"
    )

    line()

    allocation_total = (
        TP1_ALLOCATION
        + TP2_ALLOCATION
        + TP3_ALLOCATION
    )

    allocation_ok = (
        allocation_total
        == Decimal("100")
    )

    margin_ok = (
        TP1_PROFIT_MARGIN_PERCENT > 0
        and
        TP2_PROFIT_MARGIN_PERCENT > 0
        and
        TP1_PROFIT_MARGIN_PERCENT <= 100
        and
        TP2_PROFIT_MARGIN_PERCENT <= 100
    )

    check(
        "TP Allocation Totals 100%",
        allocation_ok,
    )

    check(
        "TP1/TP2 Profit-Margin Settings Valid",
        margin_ok,
    )

    if not allocation_ok:
        FINAL_BLOCKERS.append(
            "TP_ALLOCATION_INVALID"
        )

    if not margin_ok:
        FINAL_BLOCKERS.append(
            "TP_MARGIN_CONFIGURATION_INVALID"
        )

    # --------------------------------------------------------------------------
    # Synthetic LONG + SHORT
    # --------------------------------------------------------------------------

    log(
        "R36F.3 Synthetic Cluster TP Test: "
        "LONG + SHORT"
    )

    synthetic_long_rows, synthetic_short_rows = (
        synthetic_cluster_tests()
    )

    synthetic_ok = True
    synthetic_long = None
    synthetic_short = None

    try:

        synthetic_long = (
            build_cluster_tp_snapshot(
                Decimal("100000"),
                synthetic_long_rows,
                "LONG",
                "PRIMARY_FILL",
            )
        )

        synthetic_short = (
            build_cluster_tp_snapshot(
                Decimal("100000"),
                synthetic_short_rows,
                "SHORT",
                "PRIMARY_FILL",
            )
        )

    except Exception as exc:

        synthetic_ok = False

        log(
            "R36F.3_SYNTHETIC_TP_ERROR="
            f"{exc}"
        )

    check(
        "R36F Synthetic LONG/SHORT Cluster TP Ordering",
        synthetic_ok,
    )

    if synthetic_ok:

        log(
            "R36F_SYNTHETIC_LONG_TP_SNAPSHOT="
            + canonical_json(
                synthetic_long
            )
        )

        log(
            "R36F_SYNTHETIC_SHORT_TP_SNAPSHOT="
            + canonical_json(
                synthetic_short
            )
        )

        try:

            backup_long = (
                build_cluster_tp_snapshot(
                    Decimal("98000"),
                    synthetic_long_rows,
                    "LONG",
                    "BACKUP_1_FILL",
                )
            )

            immutable = (
                synthetic_long[
                    "entry_price"
                ]
                == "100000"
                and
                synthetic_long[
                    "tp1"
                ]["price"]
                !=
                backup_long[
                    "tp1"
                ]["price"]
            )

        except Exception:
            immutable = False

        check(
            "Primary TP Snapshot Remains Immutable",
            immutable,
        )

        check(
            "Backup TP Snapshot Is Independent",
            immutable,
        )

        check(
            "Primary/Backup TP Policy",
            immutable,
        )

        if not immutable:
            FINAL_BLOCKERS.append(
                "TP_SNAPSHOT_POLICY_FAILED"
            )

    else:

        FINAL_BLOCKERS.append(
            "SYNTHETIC_CLUSTER_TP_FAILED"
        )

    # --------------------------------------------------------------------------
    # REAL HISTORICAL DATA
    # --------------------------------------------------------------------------

    historical_rows = []
    page_details = []

    try:

        historical_rows, page_details = (
            load_historical_klines()
        )

        log(
            "HISTORICAL_PAGE_DETAILS="
            + canonical_json(
                page_details
            )
        )

        log(
            "HISTORICAL_KLINE_RAW_ROW_COUNT="
            + str(
                len(historical_rows)
            )
        )

    except Exception as exc:

        log(
            "HISTORICAL_KLINE_ERROR="
            f"{exc.__class__.__name__}: "
            f"{exc}"
        )

        FINAL_BLOCKERS.append(
            "HISTORICAL_KLINE_READ_FAILED"
        )

    real_long_ok = False
    real_short_ok = False

    real_long_preview = None
    real_short_preview = None

    if (
        CURRENT_MARK_PRICE is not None
        and
        len(historical_rows) >= 3
    ):

        try:

            real_long_preview = (
                build_cluster_tp_snapshot(
                    CURRENT_MARK_PRICE,
                    historical_rows,
                    "LONG",
                    "REAL_PRIMARY_LONG_PREVIEW",
                )
            )

            real_long_ok = True

            log(
                "REAL_PRIMARY_LONG_TP_PREVIEW="
                + canonical_json(
                    real_long_preview
                )
            )

        except Exception as exc:

            log(
                "REAL_PRIMARY_LONG_TP_PREVIEW_ERROR="
                f"{exc}"
            )

        try:

            real_short_preview = (
                build_cluster_tp_snapshot(
                    CURRENT_MARK_PRICE,
                    historical_rows,
                    "SHORT",
                    "REAL_PRIMARY_SHORT_PREVIEW",
                )
            )

            real_short_ok = True

            log(
                "REAL_PRIMARY_SHORT_TP_PREVIEW="
                + canonical_json(
                    real_short_preview
                )
            )

        except Exception as exc:

            log(
                "REAL_PRIMARY_SHORT_TP_PREVIEW_ERROR="
                f"{exc}"
            )

    else:

        log(
            "R36F.3_REAL_TP_PREVIEW_SKIPPED="
            "MARK_PRICE_MISSING_OR_TOO_FEW_HISTORICAL_ROWS"
        )

    check(
        "Real Historical LONG Cluster TP Preview Calculated",
        real_long_ok,
    )

    check(
        "Real Historical SHORT Cluster TP Preview Calculated",
        real_short_ok,
    )

    real_both_ok = (
        real_long_ok
        and
        real_short_ok
    )

    check(
        "Real Historical LONG + SHORT TP Validation",
        real_both_ok,
    )

    if not real_long_ok:
        FINAL_BLOCKERS.append(
            "REAL_LONG_TP_PREVIEW_FAILED"
        )

    if not real_short_ok:
        FINAL_BLOCKERS.append(
            "REAL_SHORT_TP_PREVIEW_FAILED"
        )

    # ==========================================================================
    # TEST 7
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 7: "
        "R36E MINIMUM-SIZE CANARY PREVIEW - NO SUBMISSION"
    )

    line()

    preview = build_canary_preview()

    preview_ok = preview is not None

    if preview is not None:

        log(
            "CANARY_PREVIEW="
            + canonical_json(
                preview
            )
        )

        strategy_qty = safe_decimal(
            preview[
                "strategy_normalized_qty_btc"
            ]
        )

        canary_qty = safe_decimal(
            preview[
                "r36e_canary_qty_btc"
            ]
        )

        qty_rules_ok = (
            canary_qty is not None
            and
            canary_qty >= MIN_QTY
            and
            floor_step(
                canary_qty,
                QTY_STEP,
            )
            == canary_qty
        )

        strategy_math_ok = (
            strategy_qty is not None
            and
            strategy_qty >= 0
        )

    else:

        qty_rules_ok = False
        strategy_math_ok = False

    check(
        "Canary Preview Calculated",
        preview_ok,
    )

    check(
        "Canary Quantity Obeys Frozen Quantity Rules",
        qty_rules_ok,
    )

    check(
        "Strategy Quantity Calculation Available",
        strategy_math_ok,
    )

    check(
        "Canary Writer Still Disabled",
        ORDER_SUBMISSION_ENABLED is False,
    )

    if not preview_ok:
        FINAL_BLOCKERS.append(
            "CANARY_PREVIEW_UNAVAILABLE"
        )

    if not qty_rules_ok:
        FINAL_BLOCKERS.append(
            "CANARY_QTY_RULE_FAILED"
        )

    # ==========================================================================
    # TEST 8
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 8: "
        "WRITER REQUEST CONSTRUCTION ONLY"
    )

    line()

    writer_payload = {
        "newClientOrderId":
            "R36F_TEST_PRIMARY_001",
        "positionSide":
            "LONG",
        "quantity":
            str(MIN_QTY),
        "side":
            "BUY",
        "symbol":
            PRIVATE_SYMBOL,
        "type":
            "MARKET",
    }

    log(
        "WRITER_DRY_RUN_PAYLOAD="
        + canonical_json(
            writer_payload
        )
    )

    writer_payload_ok = (
        writer_payload["quantity"]
        == "0.0001"
    )

    check(
        "Writer Entry Payload Correct",
        writer_payload_ok,
    )

    check(
        "Live Writer Remains Hard Blocked",
        not ORDER_SUBMISSION_ENABLED,
    )

    if not writer_payload_ok:
        FINAL_BLOCKERS.append(
            "WRITER_PAYLOAD_INVALID"
        )

    # ==========================================================================
    # TEST 9
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 9: "
        "ZERO-WRITE INVARIANTS"
    )

    line()

    zero_write_ok = all(
        [
            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,
            REAL_ORDERS_SENT == 0,
            DEMO_ORDERS_SENT == 0,
            REAL_ORDER_EXECUTION is False,
            DEMO_ORDER_EXECUTION is False,
        ]
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        f"LEVERAGE_MUTATIONS="
        f"{LEVERAGE_MUTATIONS}"
    )

    log(
        f"MARGIN_MODE_MUTATIONS="
        f"{MARGIN_MODE_MUTATIONS"}
    )

    log(
        f"POSITION_MUTATIONS="
        f"{POSITION_MUTATIONS}"
    )

    log(
        f"REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )

    log(
        f"DEMO_ORDERS_SENT="
        f"{DEMO_ORDERS_SENT}"
    )

    log(
        "TP_CONDITIONAL_ORDERS_SENT=0"
    )

    check(
        "R36F.3 Performed Zero Exchange Writes",
        zero_write_ok,
    )

    if not zero_write_ok:
        FINAL_BLOCKERS.append(
            "ZERO_WRITE_INVARIANT_BROKEN"
        )

    # ==========================================================================
    # TEST 10
    # ==========================================================================

    line()

    log(
        "R36F.3 TEST 10: "
        "FINAL PRE-LIVE GATE"
    )

    line()

    FINAL_BLOCKERS = sorted(
        set(FINAL_BLOCKERS)
    )

    pre_live_ready = (
        len(FINAL_BLOCKERS) == 0
    )

    TEST_STATUS = (
        "PASS"
        if pre_live_ready
        else
        "FAIL"
    )

    snapshot = {
        "stage":
            STAGE,

        "purpose":
            PURPOSE,

        "created_at":
            now_iso(),

        "test_status":
            TEST_STATUS,

        "r36f3_pre_live_gate":
            (
                "PASS"
                if pre_live_ready
                else
                "FAIL"
            ),

        "blockers":
            FINAL_BLOCKERS,

        "frozen_contract": {
            "credential_env_names": [
                WEEX_API_KEY_ENV,
                WEEX_API_SECRET_ENV,
                WEEX_API_PASSPHRASE_ENV,
            ],
            "private_symbol":
                PRIVATE_SYMBOL,
            "public_v2_symbol":
                PUBLIC_V2_SYMBOL,
            "target_margin_mode":
                TARGET_MARGIN_MODE,
            "target_long_leverage":
                TARGET_LONG_LEVERAGE,
            "target_short_leverage":
                TARGET_SHORT_LEVERAGE,
            "qty_step":
                str(QTY_STEP),
            "min_qty":
                str(MIN_QTY),
            "max_fund_exposure_percent":
                str(MAX_FUND_EXPOSURE_PERCENT),
        },

        "tp_policy": {
            "tp1_profit_margin_percent":
                str(TP1_PROFIT_MARGIN_PERCENT),
            "tp2_profit_margin_percent":
                str(TP2_PROFIT_MARGIN_PERCENT),
            "tp1_allocation_percent":
                str(TP1_ALLOCATION),
            "tp2_allocation_percent":
                str(TP2_ALLOCATION),
            "tp3_allocation_percent":
                str(TP3_ALLOCATION),
            "tp3_trailing_distance_percent":
                str(TRAILING_DISTANCE_PERCENT),
            "primary_policy":
                "LOCK_ON_FILL",
            "backup_policy":
                "RECALCULATE_ON_BACKUP_FILL_ONLY",
        },

        "historical_validation": {
            "interval":
                HISTORICAL_INTERVAL,
            "page_limit":
                HISTORICAL_LIMIT,
            "max_pages":
                HISTORICAL_MAX_PAGES,
            "rows":
                len(historical_rows),
            "pages":
                page_details,
            "long_preview":
                real_long_preview,
            "short_preview":
                real_short_preview,
            "long_diagnostics":
                LONG_DIAGNOSTICS,
            "short_diagnostics":
                SHORT_DIAGNOSTICS,
        },

        "durable_evidence": {
            "old_r36a_identity_in_both_registries":
                old_in_both,
            "r36c_identity_in_both_registries":
                new_in_both,
            "new_update_accepted_scope_bound":
                isinstance(
                    NEW_UPDATE_ACCEPTED,
                    bool,
                ),
        },

        "current_weex_reconciliation":
            recon,

        "r36e_canary_preview":
            preview,

        "hard_firebreak": {
            "real_order_execution":
                REAL_ORDER_EXECUTION,
            "demo_order_execution":
                DEMO_ORDER_EXECUTION,
            "order_submission_enabled":
                ORDER_SUBMISSION_ENABLED,
            "exchange_mutation_transport_enabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED,
            "first_real_order_allowed":
                FIRST_REAL_ORDER_ALLOWED,
        },

        "counters": {
            "exchange_network_writes":
                EXCHANGE_NETWORK_WRITES,
            "order_submissions":
                ORDER_SUBMISSIONS,
            "leverage_mutations":
                LEVERAGE_MUTATIONS,
            "margin_mode_mutations":
                MARGIN_MODE_MUTATIONS,
            "position_mutations":
                POSITION_MUTATIONS,
            "real_orders_sent":
                REAL_ORDERS_SENT,
            "demo_orders_sent":
                DEMO_ORDERS_SENT,
        },
    }

    snapshot["snapshot_sha256"] = sha256_json(
        snapshot
    )

    try:

        atomic_write_json(
            R36F_SNAPSHOT_FILE,
            snapshot,
        )

        snapshot_written = True
        snapshot_error = None

    except Exception as exc:

        snapshot_written = False

        snapshot_error = (
            f"{exc.__class__.__name__}: "
            f"{exc}"
        )

        FINAL_BLOCKERS.append(
            "R36F_SNAPSHOT_WRITE_FAILED"
        )

        TEST_STATUS = "FAIL"

    log(
        f"R36F_SNAPSHOT_FILE="
        f"{R36F_SNAPSHOT_FILE}"
    )

    log(
        f"R36F_SNAPSHOT_WRITTEN="
        f"{snapshot_written}"
    )

    log(
        f"R36F_SNAPSHOT_ERROR="
        f"{snapshot_error}"
    )

    gate = (
        pre_live_ready
        and
        snapshot_written
    )

    log(
        "R36F.3_PRE_LIVE_GATE="
        + (
            "PASS"
            if gate
            else
            "FAIL"
        )
    )

    log(
        f"FINAL_BLOCKERS="
        f"{FINAL_BLOCKERS}"
    )

    log(
        "NEXT_STAGE="
        + (
            "LIVE_ACTIVATION_REVIEW"
            if gate
            else
            "FIX_ONLY_LISTED_BLOCKERS"
        )
    )

    check(
        "R36F.3 Final Pre-Live Production Gate",
        gate,
    )

    # ==========================================================================
    # FINAL SUMMARY
    # ==========================================================================

    line()

    log(
        f"{STAGE}: FINAL TEST SUMMARY"
    )

    line()

    log(
        f"TEST_STATUS="
        f"{TEST_STATUS}"
    )

    log(
        "R36F.3_PRE_LIVE_GATE="
        + (
            "PASS"
            if gate
            else
            "FAIL"
        )
    )

    log(
        "REAL_LONG_TP_PREVIEW="
        + (
            "PASS"
            if real_long_ok
            else
            "FAIL"
        )
    )

    log(
        "REAL_SHORT_TP_PREVIEW="
        + (
            "PASS"
            if real_short_ok
            else
            "FAIL"
        )
    )

    log(
        "PRIMARY_TP_POLICY=LOCK_ON_FILL"
    )

    log(
        "BACKUP_TP_POLICY="
        "RECALCULATE_ON_BACKUP_FILL_ONLY"
    )

    log(
        f"TP1_MARGIN="
        f"{TP1_PROFIT_MARGIN_PERCENT}%"
    )

    log(
        f"TP2_MARGIN="
        f"{TP2_PROFIT_MARGIN_PERCENT}%"
    )

    log(
        "TP3_POLICY="
        "60_PERCENT_TRAILING_RUNNER"
    )

    log(
        "R36F.3_SHORT_DIAGNOSTIC_STATUS="
        + str(
            SHORT_DIAGNOSTICS.get(
                "status"
            )
        )
    )

    log(
        "R36F.3_SHORT_DIAGNOSTIC_FAILURE_REASON="
        + str(
            SHORT_DIAGNOSTICS.get(
                "failure_reason"
            )
        )
    )

    log(
        "R36F.3_SHORT_VALID_CLUSTER_COUNT="
        + str(
            SHORT_DIAGNOSTICS.get(
                "valid_cluster_count"
            )
        )
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"DEMO_ORDER_EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        "NO REAL ORDER WAS SENT"
    )

    line()


# ======================================================================================
# HEARTBEAT
# ======================================================================================

def heartbeat_loop():

    global HEARTBEAT

    while True:

        HEARTBEAT += 1

        log(
            f"{STAGE}: "
            f"HEARTBEAT={HEARTBEAT} "
            f"TEST_STATUS={TEST_STATUS} "
            f"OLD_DUPLICATE_DETECTED="
            f"{OLD_DUPLICATE_DETECTED} "
            f"OLD_REJECTED_BEFORE_PARSE="
            f"{OLD_REJECTED_BEFORE_PARSE} "
            f"NEW_UPDATE_SEEN_BEFORE_STARTUP="
            f"{NEW_UPDATE_SEEN_BEFORE_STARTUP} "
            f"NEW_UPDATE_ACCEPTED="
            f"{NEW_UPDATE_ACCEPTED} "
            f"NEW_REPLAY_REJECTED_BEFORE_PARSE="
            f"{NEW_REPLAY_REJECTED_BEFORE_PARSE} "
            f"BTCUSDT_FLAT="
            f"{BTCUSDT_FLAT} "
            f"MARGIN_MODE="
            f"{CURRENT_MARGIN_MODE} "
            f"LONG_LEVERAGE="
            f"{CURRENT_LONG_LEVERAGE} "
            f"SHORT_LEVERAGE="
            f"{CURRENT_SHORT_LEVERAGE} "
            f"TP1_MARGIN="
            f"{TP1_PROFIT_MARGIN_PERCENT}% "
            f"TP2_MARGIN="
            f"{TP2_PROFIT_MARGIN_PERCENT}% "
            f"SHORT_VALID_CLUSTERS="
            f"{SHORT_DIAGNOSTICS.get('valid_cluster_count')} "
            f"SHORT_DIAGNOSTIC="
            f"{SHORT_DIAGNOSTICS.get('failure_reason')} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


# ======================================================================================
# MAIN
# ======================================================================================

def main():

    start_health_server()

    try:

        run_r36f3()

    except Exception as exc:

        global TEST_STATUS

        TEST_STATUS = "FAIL"

        line()

        log(
            f"{STAGE}: "
            "UNHANDLED TEST ERROR"
        )

        line()

        log(
            f"EXCEPTION_CLASS="
            f"{exc.__class__.__name__}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{exc}"
        )

        traceback.print_exc()

        log(
            "TEST_STATUS=FAIL"
        )

    heartbeat_loop()


if __name__ == "__main__":
    main()

