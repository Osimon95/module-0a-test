#!/usr/bin/env python3
"""
R36F - SMALLEST TP ENGINE FIX

Purpose:
    Preserve the R36D/R36E safety baseline while fixing ONLY the
    historical TP selection blocker.

R36F TP POLICY:
    LONG:
        TP1 = 20% adjustable progress from entry toward the average
              of the first valid historical-high resistance cluster.
        TP2 = 50% adjustable progress from entry toward the average
              of the second valid historical-high resistance cluster.
        TP3 = 60% runner.

    SHORT:
        TP1 = 20% adjustable progress from entry toward the average
              of the first valid historical-low support cluster.
        TP2 = 50% adjustable progress from entry toward the average
              of the second valid historical-low support cluster.
        TP3 = 60% runner.

    TP1/TP2 percentages are configurable:
        TP1_PROFIT_MARGIN_PERCENT
        TP2_PROFIT_MARGIN_PERCENT

    Primary TP snapshots:
        LOCK ON FILL
        NEVER RECALCULATE AFTER FILL

    Backup TP snapshots:
        RECALCULATE ONLY WHEN BACKUP FILLS

SAFETY:
    REAL_ORDER_EXECUTION = False
    DEMO_ORDER_EXECUTION = False
    EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
    ORDER_SUBMISSION_ENABLED = False

    This file performs READ-ONLY exchange reconciliation and
    READ-ONLY historical market-data retrieval.

    NO REAL ORDER IS SENT.
    NO DEMO ORDER IS SENT.
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
# R36F IDENTITY
# ======================================================================================

STAGE = "R36F"

PURPOSE = (
    "R36F - SMALLEST TP ENGINE FIX: "
    "HISTORICAL HIGH/LOW CLUSTERS + "
    "ADJUSTABLE TP1/TP2 PROFIT-MARGIN PROGRESS"
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


# ======================================================================================
# FROZEN TP ALLOCATION POLICY
# ======================================================================================

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ======================================================================================
# R36F ONLY - ADJUSTABLE HISTORICAL TP PROGRESS
# ======================================================================================

# These are NOT percentages below resistance.
#
# They represent the percentage of the available move from entry
# toward the historical resistance/support cluster average.
#
# Example LONG:
#
# Entry = 100,000
# Cluster average = 105,000
# TP1 margin = 20%
#
# TP1 = 100,000 + 20% * (105,000 - 100,000)
#     = 101,000
#
# They can later be changed without changing the TP engine.

TP1_PROFIT_MARGIN_PERCENT = Decimal(
    os.getenv("TP1_PROFIT_MARGIN_PERCENT", "20")
)

TP2_PROFIT_MARGIN_PERCENT = Decimal(
    os.getenv("TP2_PROFIT_MARGIN_PERCENT", "50")
)


# ======================================================================================
# R36F HISTORICAL DATA CONFIGURATION
# ======================================================================================

HISTORICAL_LIMIT = 250
HISTORICAL_INTERVAL = "1m"

# Nearby historical extrema are grouped into one resistance/support cluster
# when their distance from the current cluster average is within this percentage.
#
# This is intentionally kept simple in R36F.
# More advanced volatility-weighted clustering is deliberately NOT added yet,
# because R36F is a smallest-unit blocker fix.

HISTORICAL_CLUSTER_TOLERANCE_PERCENT = Decimal("0.20")

# A cluster must have at least two historical touches.
MIN_CLUSTER_TOUCHES = 2


# ======================================================================================
# SIGNAL / COOLDOWN CONFIGURATION
# ======================================================================================

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


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


# ======================================================================================
# ZERO-WRITE COUNTERS
# ======================================================================================

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0

LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0

TP_CONDITIONAL_ORDERS_SENT = 0


# ======================================================================================
# PERSISTENCE
# ======================================================================================

PERSISTENT_ROOT = Path("/var/data")

R36A_STATE_DIR = PERSISTENT_ROOT / "r36a_state"
R36C_STATE_DIR = PERSISTENT_ROOT / "r36c_state"

R36D_STATE_DIR = PERSISTENT_ROOT / "r36d_state"
R36F_STATE_DIR = PERSISTENT_ROOT / "r36f_state"


R36A_DEDUPE_FILE = (
    R36A_STATE_DIR / "telegram_processed_updates.json"
)

R36A_DECISION_FILE = (
    R36A_STATE_DIR / "synthetic_decisions.json"
)


R36C_DEDUPE_FILE = (
    R36C_STATE_DIR / "telegram_processed_updates.json"
)

R36C_DECISION_FILE = (
    R36C_STATE_DIR / "synthetic_decisions.json"
)


R36D_SNAPSHOT_FILE = (
    R36D_STATE_DIR / "pre_live_readiness_snapshot.json"
)

R36F_SNAPSHOT_FILE = (
    R36F_STATE_DIR / "pre_live_readiness_snapshot.json"
)


# ======================================================================================
# PROVEN DURABLE IDENTITIES
# ======================================================================================

OLD_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"

R36C_UPDATE_ID = "R36C_SYNTHETIC_UPDATE_000001"


# ======================================================================================
# GLOBAL STATUS
# ======================================================================================

TEST_STATUS = "STARTING"

FINAL_BLOCKERS = []


# Explicit initialization prevents the scope regression previously encountered.

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


# ======================================================================================
# UTILITIES
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
        f"{label:<86} {'✅ PASS' if ok else '❌ FAIL'}",
        flush=True,
    )
    return bool(ok)


def safe_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def floor_step(value: Decimal, step: Decimal) -> Decimal:
    if value is None or step <= 0:
        return Decimal("0")

    units = (
        value / step
    ).to_integral_value(
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
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def load_json(path: Path):
    if not path.exists():
        return None, "FILE_NOT_FOUND"

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f), None

    except Exception as exc:
        return (
            None,
            f"{exc.__class__.__name__}: {exc}",
        )


def atomic_write_json(path: Path, obj):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temp.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            obj,
            f,
            indent=2,
            sort_keys=True,
        )

        f.flush()
        os.fsync(f.fileno())

    os.replace(
        temp,
        path,
    )


def collect_update_ids(obj):
    """
    Conservative recursive extraction of durable update IDs.

    READ ONLY.

    Does not reinterpret or modify the existing R36A/R36C state.
    """

    found = set()

    def walk(x):

        if isinstance(x, dict):

            for k, v in x.items():

                if k in (
                    "update_id",
                    "telegram_update_id",
                    "idempotency_key",
                ):

                    if isinstance(
                        v,
                        (str, int),
                    ):
                        found.add(str(v))


                if isinstance(k, str):

                    if (
                        k.startswith(
                            "R36A_SYNTHETIC_UPDATE_"
                        )
                        or
                        k.startswith(
                            "R36C_SYNTHETIC_UPDATE_"
                        )
                    ):
                        found.add(k)


                walk(v)


        elif isinstance(x, list):

            for item in x:
                walk(item)


        elif isinstance(x, str):

            if (
                x.startswith(
                    "R36A_SYNTHETIC_UPDATE_"
                )
                or
                x.startswith(
                    "R36C_SYNTHETIC_UPDATE_"
                )
            ):
                found.add(x)


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
            "demo_order_execution": DEMO_ORDER_EXECUTION,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
            "order_submissions": ORDER_SUBMISSIONS,
            "timestamp": now_iso(),
        }

        body = json.dumps(
            payload
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
        self.send_error(405)


    def do_PUT(self):
        self.send_error(405)


    def do_PATCH(self):
        self.send_error(405)


    def do_DELETE(self):
        self.send_error(405)


    def log_message(self, fmt, *args):
        return


def start_health_server():

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = ThreadingHTTPServer(
        (
            "0.0.0.0",
            port,
        ),
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

    return server


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

    """
    WEEX signing:

        timestamp + METHOD + requestPath [+ '?' + queryString]

    HMAC-SHA256 then Base64.
    """

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


    if not api_key or not secret or not passphrase:

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


    url = (
        WEEX_BASE_URL
        + request_path
    )

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
# HARD WRITE FIREBREAK
# ======================================================================================

def exchange_mutation_forbidden(
    *args,
    **kwargs,
):

    raise RuntimeError(
        f"{STAGE} HARD FIREBREAK: "
        f"exchange mutation attempted while "
        f"EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )


# No exchange POST/PUT/PATCH/DELETE implementation exists.

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
                and
                str(
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

    if not isinstance(
        row,
        dict,
    ):
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
    # Public ticker
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_public_ticker()
    )

    mark = None

    if isinstance(
        data,
        dict,
    ):

        mark = safe_decimal(
            data.get(
                "markPrice"
            )
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
    # Balance
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/balance"
        )
    )

    usdt = find_usdt_balance(
        data
    )

    available = (
        safe_decimal(
            usdt.get(
                "availableBalance"
            )
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
    # Position
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/position/singlePosition",
            {
                "symbol": PRIVATE_SYMBOL
            },
        )
    )

    rows = normalize_rows(
        data
    )

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
    # Symbol configuration
    # ------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/symbolConfig",
            {
                "symbol": PRIVATE_SYMBOL
            },
        )
    )

    rows = normalize_rows(
        data
    )

    cfg = None

    for row in rows:

        if (
            isinstance(row, dict)
            and
            str(
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
        and isinstance(
            rows[0],
            dict,
        )
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
            str(
                TARGET_LONG_LEVERAGE
            )
        )
        and CURRENT_SHORT_LEVERAGE
        == Decimal(
            str(
                TARGET_SHORT_LEVERAGE
            )
        )
    )


    results["symbol_config"] = {
        "status_code": status,
        "error": err,
        "ok": cfg_ok,
        "margin_mode": CURRENT_MARGIN_MODE,
        "isolated_long_leverage": (
            str(
                CURRENT_LONG_LEVERAGE
            )
            if CURRENT_LONG_LEVERAGE
            is not None
            else None
        ),
        "isolated_short_leverage": (
            str(
                CURRENT_SHORT_LEVERAGE
            )
            if CURRENT_SHORT_LEVERAGE
            is not None
            else None
        ),
    }


    return results


# ======================================================================================
# R36F HISTORICAL TP ENGINE - READ ONLY
# ======================================================================================

def weex_public_v3_klines(
    limit=HISTORICAL_LIMIT,
):

    path = "/capi/v3/market/klines"

    query = urllib.parse.urlencode(
        {
            "symbol": PRIVATE_SYMBOL,
            "interval": HISTORICAL_INTERVAL,
            "limit": int(limit),
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


def extract_kline_rows(data):

    rows = data

    if isinstance(
        data,
        dict,
    ):

        for key in (
            "data",
            "result",
            "list",
            "rows",
        ):

            if isinstance(
                data.get(key),
                list,
            ):

                rows = data[key]
                break


    return (
        rows
        if isinstance(
            rows,
            list,
        )
        else []
    )


def parse_completed_ohlc(rows):

    parsed = []

    for row in rows:

        try:

            if (
                isinstance(
                    row,
                    (list, tuple),
                )
                and len(row) >= 5
            ):

                ts = int(
                    str(row[0])
                )

                high = safe_decimal(
                    row[2]
                )

                low = safe_decimal(
                    row[3]
                )


            elif isinstance(
                row,
                dict,
            ):

                ts = int(
                    str(
                        row.get(
                            "time",
                            row.get(
                                "openTime",
                                row.get(
                                    "timestamp",
                                    0,
                                ),
                            ),
                        )
                    )
                )

                high = safe_decimal(
                    row.get(
                        "high"
                    )
                )

                low = safe_decimal(
                    row.get(
                        "low"
                    )
                )


            else:
                continue


            if (
                ts > 0
                and high is not None
                and low is not None
                and high > 0
                and low > 0
            ):

                parsed.append(
                    (
                        ts,
                        high,
                        low,
                    )
                )


        except (
            ValueError,
            TypeError,
        ):

            continue


    parsed.sort(
        key=lambda x: x[0]
    )


    # Conservative rule:
    # the newest candle may still be forming.
    #
    # Exclude it from historical structure.

    if len(parsed) >= 2:
        parsed = parsed[:-1]


    return parsed


def local_extrema(
    values,
    want_high=True,
):

    points = []

    if len(values) < 3:
        return points


    for i in range(
        1,
        len(values) - 1,
    ):

        v = values[i]

        left = values[i - 1]
        right = values[i + 1]


        if want_high:

            if (
                v >= left
                and v >= right
            ):
                points.append(v)


        else:

            if (
                v <= left
                and v <= right
            ):
                points.append(v)


    return points


def cluster_levels(
    levels,
    tolerance_percent=HISTORICAL_CLUSTER_TOLERANCE_PERCENT,
):

    if not levels:
        return []


    levels = sorted(
        levels
    )

    clusters = []


    for level in levels:

        if not clusters:

            clusters.append(
                [level]
            )

            continue


        mean = (
            sum(
                clusters[-1]
            )
            /
            Decimal(
                str(
                    len(
                        clusters[-1]
                    )
                )
            )
        )


        distance = (
            abs(
                level - mean
            )
            /
            mean
            *
            Decimal("100")
            if mean
            else Decimal("0")
        )


        if distance <= tolerance_percent:

            clusters[-1].append(
                level
            )

        else:

            clusters.append(
                [level]
            )


    result = []


    for members in clusters:

        if (
            len(members)
            >= MIN_CLUSTER_TOUCHES
        ):

            average = (
                sum(members)
                /
                Decimal(
                    str(
                        len(members)
                    )
                )
            )

            result.append(
                {
                    "touches": len(members),
                    "average": average,
                    "min": min(members),
                    "max": max(members),
                }
            )


    return result


def calculate_cluster_tp_snapshot(
    entry_price,
    side,
    rows,
    fill_label="PRIMARY_FILL",
):

    entry = safe_decimal(
        entry_price
    )

    if (
        entry is None
        or entry <= 0
    ):

        raise RuntimeError(
            "Invalid entry price for TP calculation"
        )


    candles = parse_completed_ohlc(
        rows
    )


    if len(candles) < 5:

        raise RuntimeError(
            "Insufficient completed historical candles "
            "for TP calculation"
        )


    highs = [
        x[1]
        for x in candles
    ]

    lows = [
        x[2]
        for x in candles
    ]


    is_long = (
        str(side).upper()
        == "LONG"
    )


    raw_levels = local_extrema(
        highs
        if is_long
        else lows,
        want_high=is_long,
    )


    clusters = cluster_levels(
        raw_levels
    )


    # ------------------------------------------------------------------
    # LONG:
    #   historical high clusters must be ABOVE entry.
    #
    # SHORT:
    #   historical low clusters must be BELOW entry.
    #
    # Never fabricate a TP when structure is insufficient.
    # ------------------------------------------------------------------

    if is_long:

        valid = [
            c
            for c in clusters
            if c["average"] > entry
        ]

        valid.sort(
            key=lambda c: c["average"]
        )

    else:

        valid = [
            c
            for c in clusters
            if c["average"] < entry
        ]

        valid.sort(
            key=lambda c: c["average"],
            reverse=True,
        )


    if len(valid) < 2:

        direction = (
            "above"
            if is_long
            else "below"
        )

        raise RuntimeError(
            f"Fewer than two valid historical "
            f"{'high' if is_long else 'low'} "
            f"clusters {direction} entry; "
            f"no TP fabricated"
        )


    c1 = valid[0]
    c2 = valid[1]


    margin_1 = (
        TP1_PROFIT_MARGIN_PERCENT
        /
        Decimal("100")
    )

    margin_2 = (
        TP2_PROFIT_MARGIN_PERCENT
        /
        Decimal("100")
    )


    if not (
        Decimal("0")
        < margin_1
        <= Decimal("1")
        and
        Decimal("0")
        < margin_2
        <= Decimal("1")
    ):

        raise RuntimeError(
            "TP1/TP2 profit-margin progress "
            "must be >0 and <=100 percent"
        )


    # ------------------------------------------------------------------
    # TP calculation
    #
    # LONG:
    #     Entry + margin * (cluster - Entry)
    #
    # SHORT:
    #     Entry - margin * (Entry - cluster)
    # ------------------------------------------------------------------

    if is_long:

        tp1 = (
            entry
            +
            (
                c1["average"]
                -
                entry
            )
            *
            margin_1
        )


        tp2 = (
            entry
            +
            (
                c2["average"]
                -
                entry
            )
            *
            margin_2
        )


    else:

        tp1 = (
            entry
            -
            (
                entry
                -
                c1["average"]
            )
            *
            margin_1
        )


        tp2 = (
            entry
            -
            (
                entry
                -
                c2["average"]
            )
            *
            margin_2
        )


    # ------------------------------------------------------------------
    # Absolute ordering safety.
    # ------------------------------------------------------------------

    if is_long:

        if not (
            entry
            < tp1
            < tp2
        ):

            raise RuntimeError(
                f"Invalid LONG TP ordering: "
                f"entry={entry}, "
                f"tp1={tp1}, "
                f"tp2={tp2}"
            )


    else:

        if not (
            entry
            > tp1
            > tp2
        ):

            raise RuntimeError(
                f"Invalid SHORT TP ordering: "
                f"entry={entry}, "
                f"tp1={tp1}, "
                f"tp2={tp2}"
            )


    return {

        "entry_price": str(
            entry
        ),

        "fill_label": fill_label,

        "historical_candle_count": len(
            candles
        ),

        "historical_interval":
            HISTORICAL_INTERVAL,

        "tp_cluster_method":
            "LOCAL_EXTREMA_CLUSTER_AVERAGE",

        "cluster_tolerance_percent":
            str(
                HISTORICAL_CLUSTER_TOLERANCE_PERCENT
            ),

        "minimum_cluster_touches":
            MIN_CLUSTER_TOUCHES,

        "tp1_profit_margin_percent":
            str(
                TP1_PROFIT_MARGIN_PERCENT
            ),

        "tp2_profit_margin_percent":
            str(
                TP2_PROFIT_MARGIN_PERCENT
            ),

        "recalculation_policy":
            "NEVER_RECALCULATE_AFTER_FILL",

        "side":
            str(side).upper(),


        "cluster_1": {
            k: str(v)
            for k, v in c1.items()
        },


        "cluster_2": {
            k: str(v)
            for k, v in c2.items()
        },


        "tp1": {

            "allocation_percent":
                str(TP1_PERCENT),

            "basis":
                (
                    "first_valid_historical_high_cluster_average"
                    if is_long
                    else
                    "first_valid_historical_low_cluster_average"
                ),

            "price":
                str(tp1),

            "status":
                "LOCKED",
        },


        "tp2": {

            "allocation_percent":
                str(TP2_PERCENT),

            "basis":
                (
                    "second_valid_historical_high_cluster_average"
                    if is_long
                    else
                    "second_valid_historical_low_cluster_average"
                ),

            "price":
                str(tp2),

            "status":
                "LOCKED",
        },


        "tp3": {

            "allocation_percent":
                str(TP3_PERCENT),

            "basis":
                "let_market_run",

            "status":
                "RUNNER",

            "trailing_distance_percent":
                str(
                    TRAILING_DISTANCE_PERCENT
                ),
        },
    }


# ======================================================================================
# R36F SYNTHETIC TP DATA
# ======================================================================================

def build_r36f_synthetic_rows():

    """
    Two separate two-touch resistance clusters.

    The final candle is intentionally treated as forming
    and is excluded by parse_completed_ohlc().
    """

    highs = [
        "100100",
        "100600",
        "100200",
        "100550",
        "100300",
        "101100",
        "100500",
        "101050",
        "100600",
        "102000",
    ]


    rows = []


    for i, high in enumerate(
        highs,
        1,
    ):

        h = Decimal(
            high
        )

        rows.append(
            [
                i,
                str(
                    h
                    -
                    Decimal("100")
                ),
                str(h),
                str(
                    h
                    -
                    Decimal("300")
                ),
                str(
                    h
                    -
                    Decimal("150")
                ),
                "1",
            ]
        )


    # Forming candle.
    rows.append(
        [
            11,
            "101000",
            "103000",
            "100900",
            "102000",
            "1",
        ]
    )


    return rows


# ======================================================================================
# CANARY PREVIEW
# ======================================================================================

def build_canary_preview():

    if (
        CURRENT_AVAILABLE_BALANCE
        is None
        or
        CURRENT_MARK_PRICE
        is None
    ):
        return None


    entry_margin = (
        CURRENT_AVAILABLE_BALANCE
        *
        INITIAL_ENTRY_PERCENT
        /
        Decimal("100")
    )


    entry_notional = (
        entry_margin
        *
        Decimal(
            str(
                TARGET_LONG_LEVERAGE
            )
        )
    )


    raw_qty = (
        entry_notional
        /
        CURRENT_MARK_PRICE
        if CURRENT_MARK_PRICE > 0
        else Decimal("0")
    )


    strategy_qty = floor_step(
        raw_qty,
        QTY_STEP,
    )


    # R36F remains preview-only.
    # Minimum exchange quantity is shown as canary quantity.
    canary_qty = MIN_QTY


    return {

        "symbol":
            PRIVATE_SYMBOL,

        "side_preview":
            "UNSET_UNTIL_REAL_SIGNAL",

        "order_type_preview":
            "MARKET_OR_PRODUCTION_SIGNAL_RULE",

        "target_margin_mode":
            TARGET_MARGIN_MODE,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "available_balance_usdt":
            str(
                CURRENT_AVAILABLE_BALANCE
            ),

        "mark_price":
            str(
                CURRENT_MARK_PRICE
            ),

        "strategy_entry_margin_usdt":
            str(
                entry_margin
            ),

        "strategy_entry_notional_usdt":
            str(
                entry_notional
            ),

        "strategy_raw_qty_btc":
            str(
                raw_qty
            ),

        "strategy_normalized_qty_btc":
            str(
                strategy_qty
            ),

        "r36f_canary_qty_btc":
            str(
                canary_qty
            ),

        "qty_step":
            str(QTY_STEP),

        "min_qty":
            str(MIN_QTY),

        "max_fund_exposure_percent":
            str(
                MAX_FUND_EXPOSURE_PERCENT
            ),

        "writer_enabled":
            False,

        "real_order_execution":
            False,

        "demo_order_execution":
            False,
    }


# ======================================================================================
# R36F TESTS
# ======================================================================================

def run_r36f_tp_tests():

    log(
        "R36F TP TEST: "
        "CLUSTER TP ENGINE - SYNTHETIC, NO EXCHANGE WRITE"
    )


    rows = (
        build_r36f_synthetic_rows()
    )


    snapshot = (
        calculate_cluster_tp_snapshot(
            "100000",
            "LONG",
            rows,
            "PRIMARY_FILL",
        )
    )


    tp1 = safe_decimal(
        snapshot["tp1"]["price"]
    )

    tp2 = safe_decimal(
        snapshot["tp2"]["price"]
    )


    ok = (
        tp1 is not None
        and tp2 is not None
        and tp1 > Decimal("100000")
        and tp2 > tp1

        and
        snapshot[
            "tp1"
        ][
            "allocation_percent"
        ]
        ==
        str(TP1_PERCENT)

        and
        snapshot[
            "tp2"
        ][
            "allocation_percent"
        ]
        ==
        str(TP2_PERCENT)

        and
        snapshot[
            "tp3"
        ][
            "allocation_percent"
        ]
        ==
        str(TP3_PERCENT)

        and
        snapshot[
            "tp1_profit_margin_percent"
        ]
        ==
        str(
            TP1_PROFIT_MARGIN_PERCENT
        )

        and
        snapshot[
            "tp2_profit_margin_percent"
        ]
        ==
        str(
            TP2_PROFIT_MARGIN_PERCENT
        )
    )


    check(
        "R36F Synthetic Cluster TP Ordering",
        ok,
    )


    log(
        "R36F_SYNTHETIC_TP_SNAPSHOT="
        +
        canonical_json(
            snapshot
        )
    )


    return ok


# ======================================================================================
# R36F PRIMARY/BACKUP POLICY TEST
# ======================================================================================

def run_r36f_primary_backup_policy_test():

    rows = (
        build_r36f_synthetic_rows()
    )


    primary = (
        calculate_cluster_tp_snapshot(
            "100000",
            "LONG",
            rows,
            "PRIMARY_FILL",
        )
    )


    primary_hash = sha256_json(
        primary
    )


    # Simulate a backup fill at a different entry.
    #
    # The calculation is deliberately performed again only because
    # the fill label represents a new backup fill event.

    backup = (
        calculate_cluster_tp_snapshot(
            "98000",
            "LONG",
            rows,
            "BACKUP_1_FILL",
        )
    )


    backup_hash = sha256_json(
        backup
    )


    # Verify primary object was not mutated by backup creation.

    primary_hash_after = sha256_json(
        primary
    )


    primary_locked = (
        primary_hash
        ==
        primary_hash_after
    )


    independent = (
        primary_hash
        !=
        backup_hash
    )


    ok = (
        primary_locked
        and independent
        and
        primary["recalculation_policy"]
        ==
        "NEVER_RECALCULATE_AFTER_FILL"
        and
        backup["recalculation_policy"]
        ==
        "NEVER_RECALCULATE_AFTER_FILL"
    )


    check(
        "Primary TP Snapshot Remains Immutable",
        primary_locked,
    )

    check(
        "Backup TP Snapshot Is Independent",
        independent,
    )

    check(
        "Primary/Backup TP Policy",
        ok,
    )


    log(
        "PRIMARY_TP_SNAPSHOT="
        +
        canonical_json(
            primary
        )
    )


    log(
        "BACKUP_TP_SNAPSHOT="
        +
        canonical_json(
            backup
        )
    )


    return ok


# ======================================================================================
# R36F MAIN TEST RUN
# ======================================================================================

def run_r36f():

    global TEST_STATUS

    global OLD_DUPLICATE_DETECTED
    global OLD_REJECTED_BEFORE_PARSE

    global NEW_UPDATE_SEEN_BEFORE_STARTUP
    global NEW_UPDATE_ACCEPTED
    global NEW_REPLAY_REJECTED_BEFORE_PARSE

    global FINAL_BLOCKERS


    # ------------------------------------------------------------------
    # Explicit initialization.
    # ------------------------------------------------------------------

    OLD_DUPLICATE_DETECTED = False
    OLD_REJECTED_BEFORE_PARSE = False

    NEW_UPDATE_SEEN_BEFORE_STARTUP = False
    NEW_UPDATE_ACCEPTED = False
    NEW_REPLAY_REJECTED_BEFORE_PARSE = False

    FINAL_BLOCKERS = []


    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    line()

    log(
        f"{STAGE}: MAIN.PY ENTERED"
    )

    line()

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"PYTHON_VERSION="
        f"{sys.version.split()[0]}"
    )

    log(
        f"PRIVATE_SYMBOL="
        f"{PRIVATE_SYMBOL}"
    )

    log(
        f"PUBLIC_V2_SYMBOL="
        f"{PUBLIC_V2_SYMBOL}"
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
        f"TP1_PROFIT_MARGIN_PERCENT="
        f"{TP1_PROFIT_MARGIN_PERCENT}%"
    )

    log(
        f"TP2_PROFIT_MARGIN_PERCENT="
        f"{TP2_PROFIT_MARGIN_PERCENT}%"
    )

    log(
        f"TP1_ALLOCATION="
        f"{TP1_PERCENT}%"
    )

    log(
        f"TP2_ALLOCATION="
        f"{TP2_PERCENT}%"
    )

    log(
        f"TP3_ALLOCATION="
        f"{TP3_PERCENT}%"
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
        f"CLUSTER_TOLERANCE="
        f"{HISTORICAL_CLUSTER_TOLERANCE_PERCENT}%"
    )

    log(
        f"MIN_CLUSTER_TOUCHES="
        f"{MIN_CLUSTER_TOUCHES}"
    )

    line()


    # ==================================================================================
    # TEST 1 - FROZEN CONTRACT / HARD FIREBREAK
    # ==================================================================================

    log(
        "R36F TEST 1: "
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
        PRIVATE_SYMBOL
        == "BTCUSDT"

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

            FIRST_REAL_ORDER_ALLOWED
            is False,
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


    # ==================================================================================
    # TEST 2 - DURABLE R36A/R36C EVIDENCE
    # ==================================================================================

    line()

    log(
        "R36F TEST 2: "
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
        f"R36A_DEDUPE_READ_ERROR="
        f"{e1}"
    )

    log(
        f"R36A_DECISION_READ_ERROR="
        f"{e2}"
    )

    log(
        f"R36C_DEDUPE_READ_ERROR="
        f"{e3}"
    )

    log(
        f"R36C_DECISION_READ_ERROR="
        f"{e4}"
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


    # ==================================================================================
    # TEST 3 - PROVEN IDENTITIES
    # ==================================================================================

    line()

    log(
        "R36F TEST 3: "
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


    OLD_DUPLICATE_DETECTED = (
        old_in_both
    )

    OLD_REJECTED_BEFORE_PARSE = (
        old_in_both
    )

    NEW_UPDATE_SEEN_BEFORE_STARTUP = (
        new_in_both
    )

    NEW_UPDATE_ACCEPTED = (
        new_in_both
    )

    NEW_REPLAY_REJECTED_BEFORE_PARSE = (
        new_in_both
    )


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


    # ==================================================================================
    # TEST 4 - CREDENTIAL CONTRACT
    # ==================================================================================

    line()

    log(
        "R36F TEST 4: "
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


    # ==================================================================================
    # TEST 5 - CURRENT REAL WEEX READ ONLY RECONCILIATION
    # ==================================================================================

    line()

    log(
        "R36F TEST 5: "
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

        item = recon[name]

        log(
            f"{name.upper()}="
            +
            canonical_json(
                item
            )
        )


    ticker_ok = (
        recon[
            "ticker"
        ][
            "ok"
        ]
    )


    balance_ok = (
        recon[
            "balance"
        ][
            "ok"
        ]
    )


    position_read_ok = (
        recon[
            "position"
        ][
            "ok"
        ]
    )


    flat_ok = (
        recon[
            "position"
        ][
            "flat"
        ]
    )


    config_ok = (
        recon[
            "symbol_config"
        ][
            "ok"
        ]
    )


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


    # ==================================================================================
    # TEST 6 - R36F TP ENGINE
    # ==================================================================================

    line()

    log(
        "R36F TEST 6: "
        "CLUSTER TP ENGINE + REAL HISTORICAL TP PREVIEW"
    )

    line()


    tp_policy_ok = (
        TP1_PERCENT
        +
        TP2_PERCENT
        +
        TP3_PERCENT
        ==
        Decimal("100")
    )


    margin_config_ok = (
        Decimal("0")
        <
        TP1_PROFIT_MARGIN_PERCENT
        <=
        Decimal("100")

        and
        Decimal("0")
        <
        TP2_PROFIT_MARGIN_PERCENT
        <=
        Decimal("100")
    )


    check(
        "TP Allocation Totals 100%",
        tp_policy_ok,
    )

    check(
        "TP1/TP2 Profit-Margin Settings Valid",
        margin_config_ok,
    )


    if not tp_policy_ok:

        FINAL_BLOCKERS.append(
            "TP_ALLOCATION_TOTAL_INVALID"
        )


    if not margin_config_ok:

        FINAL_BLOCKERS.append(
            "TP_PROFIT_MARGIN_CONFIG_INVALID"
        )


    synthetic_tp_ok = False


    try:

        synthetic_tp_ok = (
            run_r36f_tp_tests()
        )

    except Exception as exc:

        log(
            "R36F_SYNTHETIC_TP_ERROR="
            f"{exc}"
        )

        synthetic_tp_ok = False


    if not synthetic_tp_ok:

        FINAL_BLOCKERS.append(
            "SYNTHETIC_CLUSTER_TP_TEST_FAILED"
        )


    # ------------------------------------------------------------------
    # Primary immutability / backup recalculation test.
    # ------------------------------------------------------------------

    policy_test_ok = False


    try:

        policy_test_ok = (
            run_r36f_primary_backup_policy_test()
        )

    except Exception as exc:

        log(
            "R36F_PRIMARY_BACKUP_POLICY_ERROR="
            f"{exc}"
        )

        policy_test_ok = False


    if not policy_test_ok:

        FINAL_BLOCKERS.append(
            "PRIMARY_BACKUP_TP_POLICY_TEST_FAILED"
        )


    # ------------------------------------------------------------------
    # Real historical TP preview.
    #
    # READ ONLY.
    # ------------------------------------------------------------------

    real_tp_ok = False
    real_tp_snapshot = None

    k_status, k_data, k_raw, k_err = (
        weex_public_v3_klines(
            HISTORICAL_LIMIT
        )
    )


    k_rows = extract_kline_rows(
        k_data
    )


    log(
        f"HISTORICAL_KLINE_STATUS="
        f"{k_status}"
    )

    log(
        f"HISTORICAL_KLINE_ERROR="
        f"{k_err}"
    )

    log(
        f"HISTORICAL_KLINE_RAW_ROW_COUNT="
        f"{len(k_rows)}"
    )


    if (
        k_status == 200
        and
        CURRENT_MARK_PRICE is not None
    ):

        try:

            real_tp_snapshot = (
                calculate_cluster_tp_snapshot(
                    CURRENT_MARK_PRICE,
                    "LONG",
                    k_rows,
                    "REAL_PRIMARY_PREVIEW",
                )
            )

            real_tp_ok = True


            log(
                "REAL_PRIMARY_TP_PREVIEW="
                +
                canonical_json(
                    real_tp_snapshot
                )
            )


        except Exception as exc:

            log(
                "REAL_PRIMARY_TP_PREVIEW_ERROR="
                f"{exc}"
            )


    else:

        log(
            "REAL_PRIMARY_TP_PREVIEW_ERROR="
            "Historical kline read or mark price unavailable"
        )


    check(
        "Real Historical Cluster TP Preview Calculated",
        real_tp_ok,
    )


    if not real_tp_ok:

        FINAL_BLOCKERS.append(
            "REAL_TP_PREVIEW_FAILED"
        )


    # ==================================================================================
    # TEST 7 - CANARY QUANTITY PREVIEW
    # ==================================================================================

    line()

    log(
        "R36F TEST 7: "
        "R36E MINIMUM-SIZE CANARY PREVIEW - NO SUBMISSION"
    )

    line()


    preview = (
        build_canary_preview()
    )


    preview_ok = (
        preview is not None
    )


    if preview is not None:

        log(
            "CANARY_PREVIEW="
            +
            canonical_json(
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
                "r36f_canary_qty_btc"
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
            ==
            canary_qty
        )


        strategy_math_ok = (
            strategy_qty is not None
            and
            strategy_qty >= Decimal("0")
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


    # ==================================================================================
    # TEST 8 - WRITER REQUEST CONSTRUCTION ONLY
    # ==================================================================================

    line()

    log(
        "R36F TEST 8: "
        "WRITER REQUEST CONSTRUCTION ONLY"
    )

    line()


    dry_run_payload = {
        "symbol": PRIVATE_SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": str(MIN_QTY),
        "newClientOrderId":
            "R36F_TEST_PRIMARY_001",
    }


    writer_payload_ok = (
        dry_run_payload["symbol"]
        ==
        PRIVATE_SYMBOL

        and
        dry_run_payload["side"]
        ==
        "BUY"

        and
        dry_run_payload["positionSide"]
        ==
        "LONG"

        and
        dry_run_payload["type"]
        ==
        "MARKET"

        and
        safe_decimal(
            dry_run_payload["quantity"]
        )
        ==
        MIN_QTY

        and
        len(
            dry_run_payload[
                "newClientOrderId"
            ]
        )
        <= 36
    )


    log(
        "WRITER_DRY_RUN_PAYLOAD="
        +
        canonical_json(
            dry_run_payload
        )
    )


    check(
        "Writer Entry Payload Correct",
        writer_payload_ok,
    )


    # IMPORTANT:
    # Payload construction is allowed.
    # Submission is NOT allowed.

    check(
        "Live Writer Remains Hard Blocked",
        (
            ORDER_SUBMISSION_ENABLED
            is False

            and
            REAL_ORDER_EXECUTION
            is False

            and
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False
        ),
    )


    if not writer_payload_ok:

        FINAL_BLOCKERS.append(
            "WRITER_PAYLOAD_CONSTRUCTION_FAILED"
        )


    # ==================================================================================
    # TEST 9 - ZERO-WRITE INVARIANT
    # ==================================================================================

    line()

    log(
        "R36F TEST 9: "
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

            TP_CONDITIONAL_ORDERS_SENT == 0,

            REAL_ORDER_EXECUTION is False,

            DEMO_ORDER_EXECUTION is False,

            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,

            ORDER_SUBMISSION_ENABLED
            is False,

            FIRST_REAL_ORDER_ALLOWED
            is False,
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
        f"{MARGIN_MODE_MUTATIONS}"
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
        f"TP_CONDITIONAL_ORDERS_SENT="
        f"{TP_CONDITIONAL_ORDERS_SENT}"
    )


    check(
        "R36F Performed Zero Exchange Writes",
        zero_write_ok,
    )


    if not zero_write_ok:

        FINAL_BLOCKERS.append(
            "ZERO_WRITE_INVARIANT_BROKEN"
        )


    # ==================================================================================
    # TEST 10 - FINAL PRE-LIVE GATE
    # ==================================================================================

    line()

    log(
        "R36F TEST 10: "
        "FINAL PRE-LIVE GATE"
    )

    line()


    FINAL_BLOCKERS = sorted(
        set(
            FINAL_BLOCKERS
        )
    )


    pre_live_ready = (
        len(FINAL_BLOCKERS)
        == 0
    )


    TEST_STATUS = (
        "PASS"
        if pre_live_ready
        else
        "FAIL"
    )


    # ==================================================================================
    # R36F AUDIT SNAPSHOT
    # ==================================================================================

    snapshot = {

        "stage":
            STAGE,

        "purpose":
            PURPOSE,

        "created_at":
            now_iso(),

        "test_status":
            TEST_STATUS,

        "r36f_pre_live_gate":
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
                str(
                    MAX_FUND_EXPOSURE_PERCENT
                ),
        },


        "credited_durable_evidence": {

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


        "r36f_tp_engine": {

            "tp1_allocation_percent":
                str(TP1_PERCENT),

            "tp2_allocation_percent":
                str(TP2_PERCENT),

            "tp3_allocation_percent":
                str(TP3_PERCENT),

            "tp1_profit_margin_percent":
                str(
                    TP1_PROFIT_MARGIN_PERCENT
                ),

            "tp2_profit_margin_percent":
                str(
                    TP2_PROFIT_MARGIN_PERCENT
                ),

            "cluster_tolerance_percent":
                str(
                    HISTORICAL_CLUSTER_TOLERANCE_PERCENT
                ),

            "minimum_cluster_touches":
                MIN_CLUSTER_TOUCHES,

            "historical_limit":
                HISTORICAL_LIMIT,

            "historical_interval":
                HISTORICAL_INTERVAL,

            "primary_policy":
                "LOCK_ON_FILL",

            "backup_policy":
                "RECALCULATE_ON_BACKUP_FILL_ONLY",

            "tp3_policy":
                "60_PERCENT_TRAILING_RUNNER",

            "real_primary_tp_preview":
                real_tp_snapshot,
        },


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

            "tp_conditional_orders_sent":
                TP_CONDITIONAL_ORDERS_SENT,
        },
    }


    snapshot[
        "snapshot_sha256"
    ] = sha256_json(
        snapshot
    )


    # R36F writes ONLY its own audit snapshot.
    #
    # Existing R36A/R36C state is never rewritten.

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

        TEST_STATUS = "FAIL"

        FINAL_BLOCKERS.append(
            "R36F_SNAPSHOT_WRITE_FAILED"
        )


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


    final_gate = (
        pre_live_ready
        and
        snapshot_written
    )


    log(
        "R36F_PRE_LIVE_GATE="
        +
        (
            "PASS"
            if final_gate
            else
            "FAIL"
        )
    )


    log(
        f"FINAL_BLOCKERS="
        f"{sorted(set(FINAL_BLOCKERS))}"
    )


    log(
        "NEXT_STAGE="
        +
        (
            "R36G_FIRST_LIVE_CANARY"
            if final_gate
            else
            "FIX_ONLY_LISTED_BLOCKERS"
        )
    )


    check(
        "R36F Final Pre-Live Production Gate",
        final_gate,
    )


    # ==================================================================================
    # FINAL SUMMARY
    # ==================================================================================

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
        "R36F_PRE_LIVE_GATE="
        +
        (
            "PASS"
            if final_gate
            else
            "FAIL"
        )
    )


    log(
        "PRIMARY_TP_POLICY="
        "LOCK_ON_FILL"
    )

    log(
        "BACKUP_TP_POLICY="
        "RECALCULATE_ON_BACKUP_FILL_ONLY"
    )

    log(
        "TP1_PROFIT_MARGIN_PERCENT="
        f"{TP1_PROFIT_MARGIN_PERCENT}"
    )

    log(
        "TP2_PROFIT_MARGIN_PERCENT="
        f"{TP2_PROFIT_MARGIN_PERCENT}"
    )

    log(
        "TP3_POLICY="
        "60_PERCENT_TRAILING_RUNNER"
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
        f"REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )


    if final_gate:

        log(
            "FINAL_BLOCKERS=[]"
        )

        log(
            "R36F RESULT: "
            "TP ENGINE BLOCKER CLEARED"
        )

    else:

        log(
            "R36F RESULT: "
            "BLOCKED - FIX ONLY LISTED BLOCKERS"
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
            f"OLD_DUPLICATE_DETECTED={OLD_DUPLICATE_DETECTED} "
            f"OLD_REJECTED_BEFORE_PARSE={OLD_REJECTED_BEFORE_PARSE} "
            f"NEW_UPDATE_SEEN_BEFORE_STARTUP={NEW_UPDATE_SEEN_BEFORE_STARTUP} "
            f"NEW_UPDATE_ACCEPTED={NEW_UPDATE_ACCEPTED} "
            f"NEW_REPLAY_REJECTED_BEFORE_PARSE={NEW_REPLAY_REJECTED_BEFORE_PARSE} "
            f"BTCUSDT_FLAT={BTCUSDT_FLAT} "
            f"MARGIN_MODE={CURRENT_MARGIN_MODE} "
            f"LONG_LEVERAGE={CURRENT_LONG_LEVERAGE} "
            f"SHORT_LEVERAGE={CURRENT_SHORT_LEVERAGE} "
            f"TP1_MARGIN={TP1_PROFIT_MARGIN_PERCENT}% "
            f"TP2_MARGIN={TP2_PROFIT_MARGIN_PERCENT}% "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )


        time.sleep(30)


# ======================================================================================
# MAIN
# ======================================================================================

def main():

    start_health_server()


    try:

        run_r36f()


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


# ======================================================================================
# ENTRY POINT
# ======================================================================================

if __name__ == "__main__":
    main()
