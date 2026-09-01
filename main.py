

```python
#!/usr/bin/env python3
"""
R36E - AUTOMATED WEEX V3 WRITER LAYER
=====================================

PURPOSE
-------
R36E preserves the R36D pre-live baseline while adding the next controlled
layer:

    SIGNAL
      -> RISK
      -> AUTHORIZATION
      -> ENTRY WRITER
      -> ACTUAL FILL
      -> IMMUTABLE TP SNAPSHOT
      -> TP1 / TP2 NATIVE CONDITIONAL ORDERS
      -> TP3 RUNNER MANAGEMENT
      -> RECONCILIATION

CRITICAL SAFETY
---------------
REAL LIVE EXECUTION IS HARD-DISABLED IN THIS VERSION.

The code contains the V3 POST transport required for the future writer,
but the final activation gates remain False.

Do NOT change those gates merely to "see if it works".

First validate:
    1. startup
    2. credentials
    3. market reads
    4. historical candles
    5. TP calculations
    6. primary TP immutability
    7. backup TP recalculation
    8. writer request construction
    9. demo execution only, in a later controlled stage
    10. reconciliation

WEEX V3 CURRENT ENDPOINTS
-------------------------
Live order:
    POST /capi/v3/order

Demo order:
    POST /capi/v3/sim/order

TP/SL conditional:
    POST /capi/v3/placeTpSlOrder

Historical candles:
    GET /capi/v3/market/klines

Current authenticated order information:
    GET /capi/v3/order

The live and demo order APIs support:
    symbol
    side
    positionSide
    type
    quantity
    newClientOrderId
    optional TP/SL trigger prices

The TP/SL conditional API permits separate conditional orders, which is
important because this strategy has TP1, TP2 and a TP3 runner.

TP ARCHITECTURE
---------------
PRIMARY FILL
    TP1 = nearest historical resistance above entry, discounted by fixed %
    TP2 = second historical resistance above entry, discounted by fixed %
    TP3 = 60% runner
    Snapshot is immutable.

BACKUP FILL
    Recalculate using historical structure available at the backup fill.
    Create a NEW immutable snapshot.
    Never overwrite primary snapshot.

For SHORT:
    TP1/TP2 use historical support below entry, with a fixed upward buffer.

NO CONTINUOUS TP RECALCULATION
------------------------------
Primary TP values are NOT recalculated merely because BTC moves.

Backup TPs are recalculated ONLY when a backup actually fills.
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
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


# =============================================================================
# IDENTITY
# =============================================================================

STAGE = "R36E"

PURPOSE = (
    "AUTOMATED WEEX V3 WRITER LAYER WITH IMMUTABLE PRIMARY TP "
    "AND RECALCULATED BACKUP TP SNAPSHOTS"
)


# =============================================================================
# FROZEN WEEX CONTRACT
# =============================================================================

WEEX_API_KEY_ENV = "WEEX_API_KEY"
WEEX_API_SECRET_ENV = "WEEX_API_SECRET"
WEEX_API_PASSPHRASE_ENV = "WEEX_API_PASSPHRASE"

WEEX_BASE_URL = "https://api-contract.weex.com"

PRIVATE_SYMBOL = "BTCUSDT"
DEMO_SYMBOL = "BTCSUSDT"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100


# =============================================================================
# STRATEGY / EXECUTION PARAMETERS
# =============================================================================

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
PRICE_STEP = Decimal("0.1")

INITIAL_ENTRY_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")
MAX_BACKUPS = 3
MAX_PYRAMID_ADDS = 1

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

# TP allocation.
TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

# Historical resistance/support discount.
#
# LONG:
#   target = historical high * (1 - discount)
#
# SHORT:
#   target = historical low * (1 + discount)
#
# This is deliberately separate from the TP allocation percentages above.
HISTORICAL_TARGET_DISCOUNT_PERCENT = Decimal("0.20")

# Minimum separation between TP1 and TP2.
MIN_TP_SEPARATION_PERCENT = Decimal("0.10")

# TP3 runner trail distance.
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

HISTORICAL_CANDLE_LIMIT = 250
HISTORICAL_INTERVAL = "1m"


# =============================================================================
# HARD SAFETY GATES
# =============================================================================

# DO NOT CHANGE THESE IN R36E.
#
# They deliberately prevent live exchange mutation.

HARD_EXECUTION_LOCK = True

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

ORDER_SUBMISSION_ENABLED = False
EXCHANGE_MUTATION_TRANSPORT_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False


# =============================================================================
# COUNTERS
# =============================================================================

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
DEMO_ORDERS_SENT = 0
REAL_ORDERS_SENT = 0

TP_CONDITIONAL_ORDERS_SENT = 0

LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0


# =============================================================================
# PERSISTENCE
# =============================================================================

PERSISTENT_ROOT = Path("/var/data")

R36A_STATE_DIR = PERSISTENT_ROOT / "r36a_state"
R36C_STATE_DIR = PERSISTENT_ROOT / "r36c_state"
R36D_STATE_DIR = PERSISTENT_ROOT / "r36d_state"
R36E_STATE_DIR = PERSISTENT_ROOT / "r36e_state"

R36A_DEDUPE_FILE = R36A_STATE_DIR / "telegram_processed_updates.json"
R36A_DECISION_FILE = R36A_STATE_DIR / "synthetic_decisions.json"

R36C_DEDUPE_FILE = R36C_STATE_DIR / "telegram_processed_updates.json"
R36C_DECISION_FILE = R36C_STATE_DIR / "synthetic_decisions.json"

R36D_SNAPSHOT_FILE = R36D_STATE_DIR / "pre_live_readiness_snapshot.json"

R36E_TP_SNAPSHOT_FILE = (
    R36E_STATE_DIR / "immutable_tp_snapshots.json"
)

R36E_WRITER_AUDIT_FILE = (
    R36E_STATE_DIR / "writer_audit.json"
)

OLD_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"
R36C_UPDATE_ID = "R36C_SYNTHETIC_UPDATE_000001"


# =============================================================================
# GLOBAL STATUS
# =============================================================================

TEST_STATUS = "STARTING"

FINAL_BLOCKERS = []

OLD_DUPLICATE_DETECTED = False
OLD_REJECTED_BEFORE_PARSE = False

NEW_UPDATE_SEEN_BEFORE_STARTUP = False
NEW_UPDATE_ACCEPTED = False
NEW_REPLAY_REJECTED_BEFORE_PARSE = False

CURRENT_MARK_PRICE = None
CURRENT_AVAILABLE_BALANCE = None
BTCUSDT_FLAT = None

CURRENT_MARGIN_MODE = None
CURRENT_LONG_LEVERAGE = None
CURRENT_SHORT_LEVERAGE = None

HEARTBEAT = 0


# =============================================================================
# UTILITIES
# =============================================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(f"{now_iso()} {message}", flush=True)


def line():
    print(
        f"{now_iso()} " + "-" * 100,
        flush=True,
    )


def check(label, ok):
    print(
        f"{label:<88} "
        f"{'PASS' if ok else 'FAIL'}",
        flush=True,
    )
    return bool(ok)


def safe_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def floor_step(value, step):
    if value is None or step <= 0:
        return Decimal("0")

    units = (
        value / step
    ).to_integral_value(rounding=ROUND_DOWN)

    return units * step


def round_price(value):
    return floor_step(value, PRICE_STEP)


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


def load_json(path):
    if not path.exists():
        return None, "FILE_NOT_FOUND"

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as exc:
        return None, (
            f"{exc.__class__.__name__}: {exc}"
        )


def atomic_write_json(path, obj):
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

    os.replace(temp, path)


def collect_update_ids(obj):
    found = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():

                if k in (
                    "update_id",
                    "telegram_update_id",
                    "idempotency_key",
                ):
                    if isinstance(v, (str, int)):
                        found.add(str(v))

                if (
                    isinstance(k, str)
                    and (
                        k.startswith(
                            "R36A_SYNTHETIC_UPDATE_"
                        )
                        or k.startswith(
                            "R36C_SYNTHETIC_UPDATE_"
                        )
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
                or x.startswith(
                    "R36C_SYNTHETIC_UPDATE_"
                )
            ):
                found.add(x)

    walk(obj)
    return found


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "stage": STAGE,
            "status": TEST_STATUS,
            "live_order_execution": LIVE_ORDER_EXECUTION,
            "demo_order_execution": DEMO_ORDER_EXECUTION,
            "hard_execution_lock": HARD_EXECUTION_LOCK,
            "exchange_network_writes":
                EXCHANGE_NETWORK_WRITES,
            "order_submissions":
                ORDER_SUBMISSIONS,
            "timestamp": now_iso(),
        }

        body = json.dumps(payload).encode(
            "utf-8"
        )

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
        ("0.0.0.0", port),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(
        f"{STAGE}: HEALTH SERVER STARTED "
        f"ON PORT {port}"
    )

    return server


# =============================================================================
# WEEX SIGNATURE
# =============================================================================

def make_signature(
    secret,
    timestamp_ms,
    method,
    request_path,
    query_string="",
    body="",
):
    """
    WEEX V3 signature:

        timestamp
        + METHOD
        + requestPath
        + queryString
        + body

    The body string used for signing must be byte-identical
    to the body actually transmitted.
    """

    message = (
        str(timestamp_ms)
        + method.upper()
        + request_path
    )

    if query_string:
        message += "?" + query_string

    message += body or ""

    digest = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# =============================================================================
# HTTP
# =============================================================================

def http_request(
    method,
    url,
    headers=None,
    body_bytes=None,
    timeout=15,
):
    request = urllib.request.Request(
        url=url,
        headers=headers or {},
        data=body_bytes,
        method=method.upper(),
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


# =============================================================================
# PRIVATE GET
# =============================================================================

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
        return (
            None,
            None,
            "",
            "MISSING_WEEX_CREDENTIALS",
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
        "",
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP":
            timestamp_ms,
        "ACCESS-PASSPHRASE":
            passphrase,
        "Content-Type":
            "application/json",
        "locale": "en-US",
        "User-Agent":
            f"{STAGE}/1.0",
    }

    url = (
        WEEX_BASE_URL
        + request_path
    )

    if query:
        url += "?" + query

    return http_request(
        "GET",
        url,
        headers=headers,
    )


# =============================================================================
# PUBLIC GET
# =============================================================================

def weex_public_get(
    request_path,
    params=None,
):
    params = params or {}

    query = urllib.parse.urlencode(
        params
    )

    url = (
        WEEX_BASE_URL
        + request_path
    )

    if query:
        url += "?" + query

    return http_request(
        "GET",
        url,
        headers={
            "User-Agent":
                f"{STAGE}/1.0"
        },
    )


# =============================================================================
# PRIVATE POST WRITER
# =============================================================================

def weex_private_post(
    request_path,
    payload,
    demo=False,
):
    """
    Generic WEEX V3 POST writer.

    HARD SAFETY:
        This function refuses to transmit unless the
        explicit writer gates have been enabled.

    R36E starts with every gate disabled.
    """

    global EXCHANGE_NETWORK_WRITES
    global ORDER_SUBMISSIONS
    global DEMO_ORDERS_SENT
    global REAL_ORDERS_SENT

    if HARD_EXECUTION_LOCK:
        raise RuntimeError(
            "R36E HARD_EXECUTION_LOCK=True: "
            "POST writer blocked."
        )

    if not EXCHANGE_MUTATION_TRANSPORT_ENABLED:
        raise RuntimeError(
            "R36E EXCHANGE_MUTATION_TRANSPORT_ENABLED=False"
        )

    if not ORDER_SUBMISSION_ENABLED:
        raise RuntimeError(
            "R36E ORDER_SUBMISSION_ENABLED=False"
        )

    if demo:
        if not DEMO_ORDER_EXECUTION:
            raise RuntimeError(
                "R36E DEMO_ORDER_EXECUTION=False"
            )
    else:
        if not LIVE_ORDER_EXECUTION:
            raise RuntimeError(
                "R36E LIVE_ORDER_EXECUTION=False"
            )

        if not FIRST_REAL_ORDER_ALLOWED:
            raise RuntimeError(
                "R36E FIRST_REAL_ORDER_ALLOWED=False"
            )

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
        raise RuntimeError(
            "WEEX credentials missing."
        )

    body = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    timestamp_ms = str(
        int(time.time() * 1000)
    )

    signature = make_signature(
        secret,
        timestamp_ms,
        "POST",
        request_path,
        "",
        body,
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP":
            timestamp_ms,
        "ACCESS-PASSPHRASE":
            passphrase,
        "Content-Type":
            "application/json",
        "locale":
            "en-US",
        "User-Agent":
            f"{STAGE}/1.0",
    }

    url = (
        WEEX_BASE_URL
        + request_path
    )

    status, data, raw, err = (
        http_request(
            "POST",
            url,
            headers=headers,
            body_bytes=body.encode(
                "utf-8"
            ),
        )
    )

    EXCHANGE_NETWORK_WRITES += 1

    if demo:
        DEMO_ORDERS_SENT += 1
    else:
        REAL_ORDERS_SENT += 1

    if status == 200:
        ORDER_SUBMISSIONS += 1

    return (
        status,
        data,
        raw,
        err,
    )


# =============================================================================
# CURRENT PUBLIC MARK PRICE
# =============================================================================

def get_mark_price():
    status, data, raw, err = (
        weex_public_get(
            "/capi/v3/market/klines",
            {
                "symbol":
                    PRIVATE_SYMBOL,
                "interval":
                    "1m",
                "limit":
                    "1",
            },
        )
    )

    if status != 200:
        return None

    if not isinstance(data, list):
        return None

    if not data:
        return None

    row = data[-1]

    if not isinstance(row, list):
        return None

    if len(row) < 5:
        return None

    return safe_decimal(row[4])


# =============================================================================
# HISTORICAL KLINES
# =============================================================================

def get_historical_klines(
    symbol=PRIVATE_SYMBOL,
    interval=HISTORICAL_INTERVAL,
    limit=HISTORICAL_CANDLE_LIMIT,
):
    status, data, raw, err = (
        weex_public_get(
            "/capi/v3/market/klines",
            {
                "symbol": symbol,
                "interval": interval,
                "limit": str(limit),
            },
        )
    )

    if status != 200:
        log(
            "HISTORICAL_KLINES_ERROR="
            + str(err)
        )
        return []

    if not isinstance(data, list):
        return []

    cleaned = []

    for row in data:
        if not isinstance(row, list):
            continue

        if len(row) < 7:
            continue

        try:
            cleaned.append(
                {
                    "open_time":
                        int(row[0]),
                    "open":
                        safe_decimal(row[1]),
                    "high":
                        safe_decimal(row[2]),
                    "low":
                        safe_decimal(row[3]),
                    "close":
                        safe_decimal(row[4]),
                    "close_time":
                        int(row[6]),
                }
            )
        except Exception:
            continue

    return [
        x
        for x in cleaned
        if x["high"] is not None
        and x["low"] is not None
    ]


# =============================================================================
# HISTORICAL TP ENGINE
# =============================================================================

def historical_levels(
    side,
    entry_price,
    candles,
):
    """
    LONG:
        Find historical highs above entry.

    SHORT:
        Find historical lows below entry.

    We use distinct historical levels rather than repeatedly
    selecting the same extreme.

    Returned values are sorted in directional order.
    """

    entry_price = safe_decimal(
        entry_price
    )

    if entry_price is None:
        raise ValueError(
            "Invalid entry price."
        )

    if side == "LONG":

        candidates = sorted(
            {
                c["high"]
                for c in candles
                if (
                    c["high"] is not None
                    and c["high"] > entry_price
                )
            }
        )

        return candidates

    if side == "SHORT":

        candidates = sorted(
            {
                c["low"]
                for c in candles
                if (
                    c["low"] is not None
                    and c["low"] < entry_price
                )
            },
            reverse=True,
        )

        return candidates

    raise ValueError(
        "side must be LONG or SHORT"
    )


def calculate_tp_snapshot(
    side,
    entry_price,
    fill_time,
    fill_label,
    candles,
):
    """
    Calculate ONE immutable TP snapshot.

    IMPORTANT:
        This function is called when a fill occurs.

    It is NOT called continuously.

    Primary fill and backup fill each receive
    their own independent snapshot.
    """

    entry_price = safe_decimal(
        entry_price
    )

    if entry_price is None or entry_price <= 0:
        raise ValueError(
            "Invalid fill price."
        )

    levels = historical_levels(
        side,
        entry_price,
        candles,
    )

    if len(levels) < 2:
        raise ValueError(
            "Not enough historical "
            "resistance/support levels "
            "to calculate TP1 and TP2."
        )

    level1 = levels[0]
    level2 = levels[1]

    discount = (
        HISTORICAL_TARGET_DISCOUNT_PERCENT
        / Decimal("100")
    )

    if side == "LONG":

        tp1 = level1 * (
            Decimal("1") - discount
        )

        tp2 = level2 * (
            Decimal("1") - discount
        )

        # Safety: both targets must remain above fill.
        if tp1 <= entry_price:
            tp1 = (
                entry_price
                * (
                    Decimal("1")
                    + TP1_TRIGGER_PERCENT
                    / Decimal("100")
                )
            )

        if tp2 <= tp1:
            tp2 = (
                tp1
                * (
                    Decimal("1")
                    + MIN_TP_SEPARATION_PERCENT
                    / Decimal("100")
                )
            )

    else:

        tp1 = level1 * (
            Decimal("1") + discount
        )

        tp2 = level2 * (
            Decimal("1") + discount
        )

        if tp1 >= entry_price:
            tp1 = (
                entry_price
                * (
                    Decimal("1")
                    - TP1_TRIGGER_PERCENT
                    / Decimal("100")
                )
            )

        if tp2 >= tp1:
            tp2 = (
                tp1
                * (
                    Decimal("1")
                    - MIN_TP_SEPARATION_PERCENT
                    / Decimal("100")
                )
            )

    tp1 = round_price(tp1)
    tp2 = round_price(tp2)

    snapshot = {
        "stage": STAGE,
        "snapshot_version": 1,
        "fill_label": fill_label,
        "side": side,
        "entry_price": str(
            entry_price
        ),
        "fill_time": fill_time,
        "historical_interval":
            HISTORICAL_INTERVAL,
        "historical_candle_count":
            len(candles),

        "historical_reference_1":
            str(level1),

        "historical_reference_2":
            str(level2),

        "historical_target_discount_percent":
            str(
                HISTORICAL_TARGET_DISCOUNT_PERCENT
            ),

        "tp1": {
            "price": str(tp1),
            "allocation_percent":
                str(TP1_PERCENT),
            "status": "LOCKED",
            "basis":
                "nearest_historical_structure",
        },

        "tp2": {
            "price": str(tp2),
            "allocation_percent":
                str(TP2_PERCENT),
            "status": "LOCKED",
            "basis":
                "second_historical_structure",
        },

        "tp3": {
            "allocation_percent":
                str(TP3_PERCENT),
            "status": "RUNNER",
            "trailing_distance_percent":
                str(
                    TRAILING_DISTANCE_PERCENT
                ),
            "basis":
                "let_market_run",
        },

        "recalculation_policy":
            "NEVER_RECALCULATE_AFTER_FILL",

        "snapshot_created_at":
            now_iso(),
    }

    snapshot["snapshot_sha256"] = (
        sha256_json(snapshot)
    )

    return snapshot


# =============================================================================
# IMMUTABLE TP SNAPSHOT STORE
# =============================================================================

def load_tp_snapshots():
    data, err = load_json(
        R36E_TP_SNAPSHOT_FILE
    )

    if err is not None:
        return {
            "snapshots": [],
            "integrity": None,
        }

    return data


def save_new_tp_snapshot(
    snapshot,
):
    """
    Append-only behavior.

    Existing snapshots are never overwritten.
    """

    existing = load_tp_snapshots()

    if not isinstance(
        existing,
        dict,
    ):
        existing = {
            "snapshots": []
        }

    snapshots = existing.get(
        "snapshots",
        [],
    )

    if not isinstance(
        snapshots,
        list,
    ):
        snapshots = []

    # Duplicate snapshot identity check.
    snapshot_hash = snapshot[
        "snapshot_sha256"
    ]

    for old in snapshots:

        if (
            isinstance(old, dict)
            and old.get(
                "snapshot_sha256"
            )
            == snapshot_hash
        ):
            raise RuntimeError(
                "IDENTICAL TP SNAPSHOT "
                "ALREADY EXISTS."
            )

    snapshots.append(snapshot)

    document = {
        "stage": STAGE,
        "updated_at": now_iso(),
        "snapshots": snapshots,
    }

    document[
        "document_sha256"
    ] = sha256_json(
        document
    )

    atomic_write_json(
        R36E_TP_SNAPSHOT_FILE,
        document,
    )

    return document


def verify_tp_snapshot_integrity(
    snapshot,
):
    if not isinstance(
        snapshot,
        dict,
    ):
        return False

    supplied = snapshot.get(
        "snapshot_sha256"
    )

    if not supplied:
        return False

    copy = dict(snapshot)

    copy.pop(
        "snapshot_sha256",
        None,
    )

    return (
        sha256_json(copy)
        == supplied
    )


# =============================================================================
# WRITER CLIENT ID
# =============================================================================

def make_client_order_id(
    prefix,
    fill_label,
    sequence,
):
    raw = (
        f"{prefix}_{fill_label}_{sequence}"
    )

    # WEEX limit is 36 characters.
    return raw[:36]


# =============================================================================
# ENTRY ORDER BUILDER
# =============================================================================

def build_entry_order(
    side,
    position_side,
    quantity,
    client_order_id,
):
    quantity = floor_step(
        safe_decimal(quantity),
        QTY_STEP,
    )

    if quantity < MIN_QTY:
        raise ValueError(
            "Quantity below exchange minimum."
        )

    if side not in (
        "BUY",
        "SELL",
    ):
        raise ValueError(
            "Invalid order side."
        )

    if position_side not in (
        "LONG",
        "SHORT",
    ):
        raise ValueError(
            "Invalid position side."
        )

    return {
        "symbol": PRIVATE_SYMBOL,
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": str(quantity),
        "newClientOrderId":
            client_order_id,
    }


# =============================================================================
# TP CONDITIONAL ORDER BUILDERS
# =============================================================================

def build_tp1_conditional(
    side,
    quantity,
    snapshot,
    client_algo_id,
):
    """
    TP1 closes 20% of the filled position.
    """

    quantity = floor_step(
        safe_decimal(quantity)
        * TP1_PERCENT
        / Decimal("100"),
        QTY_STEP,
    )

    if quantity < MIN_QTY:
        return None

    return {
        "symbol": PRIVATE_SYMBOL,
        "clientAlgoId":
            client_algo_id,
        "planType":
            "TAKE_PROFIT",
        "triggerPrice":
            snapshot["tp1"]["price"],
        "executePrice":
            "0",
        "quantity":
            str(quantity),
        "positionSide":
            "LONG"
            if side == "LONG"
            else "SHORT",
        "triggerPriceType":
            "MARK_PRICE",
    }


def build_tp2_conditional(
    side,
    quantity,
    snapshot,
    client_algo_id,
):
    """
    TP2 closes 20% of the filled position.
    """

    quantity = floor_step(
        safe_decimal(quantity)
        * TP2_PERCENT
        / Decimal("100"),
        QTY_STEP,
    )

    if quantity < MIN_QTY:
        return None

    return {
        "symbol": PRIVATE_SYMBOL,
        "clientAlgoId":
            client_algo_id,
        "planType":
            "TAKE_PROFIT",
        "triggerPrice":
            snapshot["tp2"]["price"],
        "executePrice":
            "0",
        "quantity":
            str(quantity),
        "positionSide":
            "LONG"
            if side == "LONG"
            else "SHORT",
        "triggerPriceType":
            "MARK_PRICE",
    }


# =============================================================================
# FUTURE LIVE/DEMO ENTRY WRITER
# =============================================================================

def submit_entry(
    side,
    position_side,
    quantity,
    client_order_id,
    demo=False,
):
    payload = build_entry_order(
        side,
        position_side,
        quantity,
        client_order_id,
    )

    endpoint = (
        "/capi/v3/sim/order"
        if demo
        else "/capi/v3/order"
    )

    return weex_private_post(
        endpoint,
        payload,
        demo=demo,
    )


def submit_tp_conditional(
    payload,
    demo=False,
):
    """
    The current V3 documentation exposes the native TP/SL
    conditional endpoint for contract trading.

    R36E keeps this behind the same hard writer gate.

    NOTE:
    A later demo validation must confirm whether the demo
    environment accepts the same conditional-order endpoint
    semantics before any production activation.
    """

    endpoint = (
        "/capi/v3/placeTpSlOrder"
    )

    return weex_private_post(
        endpoint,
        payload,
        demo=demo,
    )


# =============================================================================
# CANARY STRATEGY QUANTITY
# =============================================================================

def build_canary_preview():
    global CURRENT_AVAILABLE_BALANCE
    global CURRENT_MARK_PRICE

    if (
        CURRENT_AVAILABLE_BALANCE
        is None
        or CURRENT_MARK_PRICE is None
    ):
        return None

    margin = (
        CURRENT_AVAILABLE_BALANCE
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    notional = (
        margin
        * Decimal(
            str(
                TARGET_LONG_LEVERAGE
            )
        )
    )

    raw_qty = (
        notional
        / CURRENT_MARK_PRICE
    )

    strategy_qty = floor_step(
        raw_qty,
        QTY_STEP,
    )

    return {
        "symbol":
            PRIVATE_SYMBOL,
        "available_balance_usdt":
            str(
                CURRENT_AVAILABLE_BALANCE
            ),
        "mark_price":
            str(
                CURRENT_MARK_PRICE
            ),
        "strategy_margin_usdt":
            str(margin),
        "strategy_notional_usdt":
            str(notional),
        "strategy_raw_qty_btc":
            str(raw_qty),
        "strategy_normalized_qty_btc":
            str(strategy_qty),
        "minimum_canary_qty_btc":
            str(MIN_QTY),
        "qty_step":
            str(QTY_STEP),
        "writer_enabled":
            ORDER_SUBMISSION_ENABLED,
        "live_execution":
            LIVE_ORDER_EXECUTION,
        "demo_execution":
            DEMO_ORDER_EXECUTION,
    }


# =============================================================================
# RECONCILIATION
# =============================================================================

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
    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):

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


def reconcile():
    global CURRENT_MARK_PRICE
    global CURRENT_AVAILABLE_BALANCE
    global BTCUSDT_FLAT
    global CURRENT_MARGIN_MODE
    global CURRENT_LONG_LEVERAGE
    global CURRENT_SHORT_LEVERAGE

    results = {}

    # -------------------------------------------------------------------------
    # Market price
    # -------------------------------------------------------------------------

    mark = get_mark_price()

    CURRENT_MARK_PRICE = mark

    results["mark_price"] = {
        "ok":
            mark is not None
            and mark > 0,
        "price":
            str(mark)
            if mark is not None
            else None,
    }

    # -------------------------------------------------------------------------
    # Balance
    # -------------------------------------------------------------------------

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

    CURRENT_AVAILABLE_BALANCE = (
        available
    )

    results["balance"] = {
        "status":
            status,
        "error":
            err,
        "ok":
            status == 200
            and available is not None
            and available >= 0,
        "available_usdt":
            str(available)
            if available is not None
            else None,
    }

    # -------------------------------------------------------------------------
    # Position
    # -------------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/position/singlePosition",
            {
                "symbol":
                    PRIVATE_SYMBOL
            },
        )
    )

    rows = normalize_rows(
        data
    )

    flat = (
        status == 200
        and not any(
            position_is_nonzero(
                row
            )
            for row in rows
        )
    )

    BTCUSDT_FLAT = flat

    results["position"] = {
        "status":
            status,
        "error":
            err,
        "ok":
            status == 200,
        "flat":
            flat,
        "rows":
            len(rows),
    }

    # -------------------------------------------------------------------------
    # Symbol config
    # -------------------------------------------------------------------------

    status, data, raw, err = (
        weex_private_get(
            "/capi/v3/account/symbolConfig",
            {
                "symbol":
                    PRIVATE_SYMBOL
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

    config_ok = (
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
        "status":
            status,
        "error":
            err,
        "ok":
            config_ok,
        "margin_mode":
            CURRENT_MARGIN_MODE,
        "long_leverage":
            str(
                CURRENT_LONG_LEVERAGE
            )
            if CURRENT_LONG_LEVERAGE
            is not None
            else None,
        "short_leverage":
            str(
                CURRENT_SHORT_LEVERAGE
            )
            if CURRENT_SHORT_LEVERAGE
            is not None
            else None,
    }

    return results


# =============================================================================
# TP ENGINE SELF TEST
# =============================================================================

def synthetic_candles(
    entry,
    side,
):
    """
    Deterministic local test data only.

    This never reaches WEEX.

    It proves that:
        primary snapshot
        backup snapshot
        TP separation
        snapshot immutability
    work independently.
    """

    entry = safe_decimal(
        entry
    )

    if side == "LONG":

        highs = [
            entry * Decimal("1.010"),
            entry * Decimal("1.020"),
            entry * Decimal("1.030"),
            entry * Decimal("1.040"),
        ]

        return [
            {
                "open_time": i,
                "open": entry,
                "high": h,
                "low": entry * Decimal("0.995"),
                "close": entry,
                "close_time": i + 1,
            }
            for i, h in enumerate(
                highs
            )
        ]

    lows = [
        entry * Decimal("0.990"),
        entry * Decimal("0.980"),
        entry * Decimal("0.970"),
        entry * Decimal("0.960"),
    ]

    return [
        {
            "open_time": i,
            "open": entry,
            "high": entry * Decimal("1.005"),
            "low": low,
            "close": entry,
            "close_time": i + 1,
        }
        for i, low in enumerate(
            lows
        )
    ]


def run_tp_self_test():
    line()
    log(
        "R36E TP TEST: PRIMARY "
        "IMMUTABILITY + BACKUP RECALCULATION"
    )
    line()

    primary_entry = Decimal(
        "100000"
    )

    backup_entry = Decimal(
        "98000"
    )

    candles_primary = (
        synthetic_candles(
            primary_entry,
            "LONG",
        )
    )

    candles_backup = (
        synthetic_candles(
            backup_entry,
            "LONG",
        )
    )

    primary = calculate_tp_snapshot(
        "LONG",
        primary_entry,
        now_iso(),
        "PRIMARY_FILL",
        candles_primary,
    )

    backup = calculate_tp_snapshot(
        "LONG",
        backup_entry,
        now_iso(),
        "BACKUP_1_FILL",
        candles_backup,
    )

    primary_ok = (
        primary["fill_label"]
        == "PRIMARY_FILL"
        and primary["tp1"]["status"]
        == "LOCKED"
        and primary["tp2"]["status"]
        == "LOCKED"
        and primary["tp3"]["status"]
        == "RUNNER"
    )

    backup_ok = (
        backup["fill_label"]
        == "BACKUP_1_FILL"
        and backup["tp1"]["status"]
        == "LOCKED"
        and backup["tp2"]["status"]
        == "LOCKED"
        and backup["tp3"]["status"]
        == "RUNNER"
    )

    primary_hash_ok = (
        verify_tp_snapshot_integrity(
            primary
        )
    )

    backup_hash_ok = (
        verify_tp_snapshot_integrity(
            backup
        )
    )

    primary_not_overwritten = (
        primary["entry_price"]
        != backup["entry_price"]
        and primary["fill_label"]
        != backup["fill_label"]
    )

    check(
        "Primary TP Snapshot Created",
        primary_ok,
    )

    check(
        "Backup TP Snapshot Created",
        backup_ok,
    )

    check(
        "Primary Snapshot Hash Valid",
        primary_hash_ok,
    )

    check(
        "Backup Snapshot Hash Valid",
        backup_hash_ok,
    )

    check(
        "Primary And Backup Are Independent",
        primary_not_overwritten,
    )

    log(
        "PRIMARY_TP_SNAPSHOT="
        + canonical_json(
            primary
        )
    )

    log(
        "BACKUP_TP_SNAPSHOT="
        + canonical_json(
            backup
        )
    )

    return all(
        [
            primary_ok,
            backup_ok,
            primary_hash_ok,
            backup_hash_ok,
            primary_not_overwritten,
        ]
    )


# =============================================================================
# WRITER DRY-RUN TEST
# =============================================================================

def run_writer_dry_run():
    line()
    log(
        "R36E WRITER TEST: REQUEST "
        "CONSTRUCTION ONLY"
    )
    line()

    payload = build_entry_order(
        "BUY",
        "LONG",
        MIN_QTY,
        "R36E_TEST_PRIMARY_001",
    )

    correct = all(
        [
            payload["symbol"]
            == PRIVATE_SYMBOL,

            payload["side"]
            == "BUY",

            payload["positionSide"]
            == "LONG",

            payload["type"]
            == "MARKET",

            payload["quantity"]
            == str(MIN_QTY),

            payload["newClientOrderId"]
            == "R36E_TEST_PRIMARY_001",
        ]
    )

    check(
        "Writer Entry Payload Correct",
        correct,
    )

    log(
        "WRITER_DRY_RUN_PAYLOAD="
        + canonical_json(
            payload
        )
    )

    # Explicitly prove the actual POST writer remains blocked.
    blocked = False

    try:
        weex_private_post(
            "/capi/v3/order",
            payload,
            demo=False,
        )

    except RuntimeError:
        blocked = True

    check(
        "Live Writer Remains Hard Blocked",
        blocked,
    )

    return correct and blocked


# =============================================================================
# ZERO-WRITE INVARIANT
# =============================================================================

def zero_write_invariant():
    return all(
        [
            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            DEMO_ORDERS_SENT == 0,
            REAL_ORDERS_SENT == 0,
            TP_CONDITIONAL_ORDERS_SENT == 0,

            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,

            LIVE_ORDER_EXECUTION is False,
            DEMO_ORDER_EXECUTION is False,
            ORDER_SUBMISSION_ENABLED is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,
            FIRST_REAL_ORDER_ALLOWED is False,
            HARD_EXECUTION_LOCK is True,
        ]
    )


# =============================================================================
# R36D DURABLE EVIDENCE CHECK
# =============================================================================

def check_previous_evidence():
    results = {}

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

    results["r36a_readable"] = (
        e1 is None
        and e2 is None
    )

    results["r36c_readable"] = (
        e3 is None
        and e4 is None
    )

    r36a_ids = (
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

    r36c_ids = (
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

    results[
        "r36a_identity"
    ] = (
        OLD_R36A_UPDATE_ID
        in r36a_ids
        and
        OLD_R36A_UPDATE_ID
        in r36a_decision_ids
    )

    results[
        "r36c_identity"
    ] = (
        R36C_UPDATE_ID
        in r36c_ids
        and
        R36C_UPDATE_ID
        in r36c_decision_ids
    )

    return results


# =============================================================================
# R36E MAIN TEST
# =============================================================================

def run_r36e():

    global TEST_STATUS
    global FINAL_BLOCKERS

    line()

    log(
        f"{STAGE}: MAIN.PY ENTERED"
    )

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
        f"DEMO_SYMBOL="
        f"{DEMO_SYMBOL}"
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

    line()


    # =========================================================================
    # TEST 1 - HARD FIREBREAK
    # =========================================================================

    log(
        "R36E TEST 1: HARD EXECUTION FIREBREAK"
    )

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

    firebreak_ok = all(
        [
            HARD_EXECUTION_LOCK is True,
            LIVE_ORDER_EXECUTION is False,
            DEMO_ORDER_EXECUTION is False,
            ORDER_SUBMISSION_ENABLED is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,
            FIRST_REAL_ORDER_ALLOWED is False,
        ]
    )

    check(
        "Frozen WEEX Environment Names",
        env_names_ok,
    )

    check(
        "R36E Hard Execution Firebreak",
        firebreak_ok,
    )

    if not env_names_ok:
        FINAL_BLOCKERS.append(
            "ENVIRONMENT_CONTRACT_CHANGED"
        )

    if not firebreak_ok:
        FINAL_BLOCKERS.append(
            "EXECUTION_FIREBREAK_BROKEN"
        )


    # =========================================================================
    # TEST 2 - PREVIOUS DURABLE EVIDENCE
    # =========================================================================

    line()

    log(
        "R36E TEST 2: PRESERVE R36A/R36C DURABLE EVIDENCE"
    )

    evidence = (
        check_previous_evidence()
    )

    log(
        "R36A_DURABLE="
        + str(
            evidence[
                "r36a_readable"
            ]
        )
    )

    log(
        "R36C_DURABLE="
        + str(
            evidence[
                "r36c_readable"
            ]
        )
    )

    log(
        "R36A_ID_PROVEN="
        + str(
            evidence[
                "r36a_identity"
            ]
        )
    )

    log(
        "R36C_ID_PROVEN="
        + str(
            evidence[
                "r36c_identity"
            ]
        )
    )

    check(
        "R36A Durable Registries Readable",
        evidence[
            "r36a_readable"
        ],
    )

    check(
        "R36C Durable Registries Readable",
        evidence[
            "r36c_readable"
        ],
    )

    check(
        "R36A Proven Identity Still Present",
        evidence[
            "r36a_identity"
        ],
    )

    check(
        "R36C Proven Identity Still Present",
        evidence[
            "r36c_identity"
        ],
    )

    if not evidence[
        "r36a_readable"
    ]:
        FINAL_BLOCKERS.append(
            "R36A_EVIDENCE_UNREADABLE"
        )

    if not evidence[
        "r36c_readable"
    ]:
        FINAL_BLOCKERS.append(
            "R36C_EVIDENCE_UNREADABLE"
        )


    # =========================================================================
    # TEST 3 - CREDENTIALS
    # =========================================================================

    line()

    log(
        "R36E TEST 3: WEEX CREDENTIAL CONTRACT"
    )

    key_present = bool(
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

    credentials_ok = (
        key_present
        and secret_present
        and passphrase_present
    )

    log(
        "WEEX_API_KEY_PRESENT="
        + str(key_present)
    )

    log(
        "WEEX_API_SECRET_PRESENT="
        + str(secret_present)
    )

    log(
        "WEEX_API_PASSPHRASE_PRESENT="
        + str(passphrase_present)
    )

    check(
        "All Frozen WEEX Credentials Present",
        credentials_ok,
    )

    if not credentials_ok:
        FINAL_BLOCKERS.append(
            "WEEX_CREDENTIALS_MISSING"
        )


    # =========================================================================
    # TEST 4 - CURRENT WEEX READS
    # =========================================================================

    line()

    log(
        "R36E TEST 4: CURRENT WEEX READ-ONLY RECONCILIATION"
    )

    recon = reconcile()

    log(
        "RECONCILIATION="
        + canonical_json(
            recon
        )
    )

    mark_ok = recon[
        "mark_price"
    ]["ok"]

    balance_ok = recon[
        "balance"
    ]["ok"]

    position_ok = recon[
        "position"
    ]["ok"]

    flat_ok = recon[
        "position"
    ]["flat"]

    config_ok = recon[
        "symbol_config"
    ]["ok"]

    check(
        "Current Mark Price Read",
        mark_ok,
    )

    check(
        "Authenticated Balance Read",
        balance_ok,
    )

    check(
        "Current Position Read",
        position_ok,
    )

    check(
        "BTCUSDT Currently Flat",
        flat_ok,
    )

    check(
        "ISOLATED 100x/100x Configuration",
        config_ok,
    )

    if not mark_ok:
        FINAL_BLOCKERS.append(
            "MARK_PRICE_READ_FAILED"
        )

    if not balance_ok:
        FINAL_BLOCKERS.append(
            "BALANCE_READ_FAILED"
        )

    if not position_ok:
        FINAL_BLOCKERS.append(
            "POSITION_READ_FAILED"
        )

    elif not flat_ok:
        FINAL_BLOCKERS.append(
            "BTCUSDT_NOT_FLAT"
        )

    if not config_ok:
        FINAL_BLOCKERS.append(
            "MARGIN_OR_LEVERAGE_MISMATCH"
        )


    # =========================================================================
    # TEST 5 - HISTORICAL CANDLE ENGINE
    # =========================================================================

    line()

    log(
        "R36E TEST 5: HISTORICAL CANDLE / TP ENGINE"
    )

    candles = get_historical_klines()

    historical_ok = (
        len(candles)
        >= 10
    )

    log(
        "HISTORICAL_CANDLE_COUNT="
        + str(
            len(candles)
        )
    )

    check(
        "Historical BTCUSDT Candles Available",
        historical_ok,
    )

    if not historical_ok:
        FINAL_BLOCKERS.append(
            "HISTORICAL_KLINE_DATA_UNAVAILABLE"
        )


    # =========================================================================
    # TEST 6 - TP IMMUTABILITY
    # =========================================================================

    line()

    tp_test_ok = (
        run_tp_self_test()
    )

    if not tp_test_ok:
        FINAL_BLOCKERS.append(
            "TP_IMMUTABILITY_TEST_FAILED"
        )


    # =========================================================================
    # TEST 7 - REAL HISTORICAL TP PREVIEW
    # =========================================================================

    line()

    log(
        "R36E TEST 7: REAL HISTORICAL TP PREVIEW"
    )

    if (
        CURRENT_MARK_PRICE is not None
        and historical_ok
    ):

        try:

            preview_primary = (
                calculate_tp_snapshot(
                    "LONG",
                    CURRENT_MARK_PRICE,
                    now_iso(),
                    "PREVIEW_PRIMARY",
                    candles,
                )
            )

            log(
                "REAL_PRIMARY_TP_PREVIEW="
                + canonical_json(
                    preview_primary
                )
            )

            preview_ok = True

        except Exception as exc:

            log(
                "REAL_PRIMARY_TP_PREVIEW_ERROR="
                + str(exc)
            )

            preview_ok = False

    else:

        preview_ok = False

    check(
        "Real Historical TP Preview Calculated",
        preview_ok,
    )

    if not preview_ok:
        FINAL_BLOCKERS.append(
            "REAL_TP_PREVIEW_FAILED"
        )


    # =========================================================================
    # TEST 8 - CANARY QUANTITY
    # =========================================================================

    line()

    log(
        "R36E TEST 8: CANARY QUANTITY PREVIEW"
    )

    canary = build_canary_preview()

    canary_ok = (
        canary is not None
    )

    if canary:

        log(
            "CANARY_PREVIEW="
            + canonical_json(
                canary
            )
        )

        qty = safe_decimal(
            canary[
                "minimum_canary_qty_btc"
            ]
        )

        qty_ok = (
            qty is not None
            and
            qty >= MIN_QTY
            and
            floor_step(
                qty,
                QTY_STEP,
            )
            == qty
        )

    else:

        qty_ok = False

    check(
        "Canary Preview Available",
        canary_ok,
    )

    check(
        "Canary Quantity Obeys Exchange Rules",
        qty_ok,
    )

    if not canary_ok:
        FINAL_BLOCKERS.append(
            "CANARY_PREVIEW_FAILED"
        )

    if not qty_ok:
        FINAL_BLOCKERS.append(
            "CANARY_QUANTITY_RULE_FAILED"
        )


    # =========================================================================
    # TEST 9 - WRITER DRY RUN
    # =========================================================================

    line()

    writer_test_ok = (
        run_writer_dry_run()
    )

    if not writer_test_ok:
        FINAL_BLOCKERS.append(
            "WRITER_DRY_RUN_FAILED"
        )


    # =========================================================================
    # TEST 10 - ZERO WRITE
    # =========================================================================

    line()

    log(
        "R36E TEST 10: ZERO-WRITE INVARIANT"
    )

    zero_write_ok = (
        zero_write_invariant()
    )

    log(
        "EXCHANGE_NETWORK_WRITES="
        + str(
            EXCHANGE_NETWORK_WRITES
        )
    )

    log(
        "ORDER_SUBMISSIONS="
        + str(
            ORDER_SUBMISSIONS
        )
    )

    log(
        "DEMO_ORDERS_SENT="
        + str(
            DEMO_ORDERS_SENT
        )
    )

    log(
        "REAL_ORDERS_SENT="
        + str(
            REAL_ORDERS_SENT
        )
    )

    log(
        "TP_CONDITIONAL_ORDERS_SENT="
        + str(
            TP_CONDITIONAL_ORDERS_SENT
        )
    )

    check(
        "R36E Performed Zero Exchange Writes",
        zero_write_ok,
    )

    if not zero_write_ok:
        FINAL_BLOCKERS.append(
            "ZERO_WRITE_INVARIANT_BROKEN"
        )


    # =========================================================================
    # TEST 11 - SAVE AUDIT SNAPSHOT
    # =========================================================================

    line()

    FINAL_BLOCKERS = sorted(
        set(FINAL_BLOCKERS)
    )

    pre_live_ready = (
        len(FINAL_BLOCKERS)
        == 0
    )

    TEST_STATUS = (
        "PASS"
        if pre_live_ready
        else "FAIL"
    )

    audit = {
        "stage": STAGE,
        "created_at": now_iso(),
        "test_status":
            TEST_STATUS,
        "pre_live_writer_gate":
            (
                "PASS"
                if pre_live_ready
                else "FAIL"
            ),

        "blockers":
            FINAL_BLOCKERS,

        "tp_policy": {
            "primary_fill":
                "CALCULATE_ON_FILL_AND_LOCK",
            "backup_fill":
                "RECALCULATE_ON_BACKUP_FILL_AND_LOCK",
            "primary_overwritten_by_backup":
                False,
            "tp1_allocation_percent":
                str(TP1_PERCENT),
            "tp2_allocation_percent":
                str(TP2_PERCENT),
            "tp3_allocation_percent":
                str(TP3_PERCENT),
            "tp3_type":
                "TRAILING_RUNNER",
            "historical_discount_percent":
                str(
                    HISTORICAL_TARGET_DISCOUNT_PERCENT
                ),
        },

        "execution_gates": {
            "hard_execution_lock":
                HARD_EXECUTION_LOCK,
            "live_order_execution":
                LIVE_ORDER_EXECUTION,
            "demo_order_execution":
                DEMO_ORDER_EXECUTION,
            "order_submission_enabled":
                ORDER_SUBMISSION_ENABLED,
            "exchange_mutation_transport_enabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED,
            "first_real_order_allowed":
                FIRST_REAL_ORDER_ALLOWED,
        },

        "current_reconciliation":
            recon,

        "canary_preview":
            canary,

        "writer_counters": {
            "exchange_network_writes":
                EXCHANGE_NETWORK_WRITES,
            "order_submissions":
                ORDER_SUBMISSIONS,
            "demo_orders_sent":
                DEMO_ORDERS_SENT,
            "real_orders_sent":
                REAL_ORDERS_SENT,
            "tp_conditional_orders_sent":
                TP_CONDITIONAL_ORDERS_SENT,
        },
    }

    audit[
        "audit_sha256"
    ] = sha256_json(
        audit
    )

    try:

        atomic_write_json(
            R36E_WRITER_AUDIT_FILE,
            audit,
        )

        audit_ok = True

    except Exception as exc:

        audit_ok = False

        log(
            "AUDIT_WRITE_ERROR="
            + str(exc)
        )

        FINAL_BLOCKERS.append(
            "R36E_AUDIT_WRITE_FAILED"
        )

    check(
        "R36E Writer Audit Snapshot Saved",
        audit_ok,
    )


    # =========================================================================
    # FINAL
    # =========================================================================

    FINAL_BLOCKERS = sorted(
        set(FINAL_BLOCKERS)
    )

    final_ok = (
        len(FINAL_BLOCKERS)
        == 0
        and audit_ok
        and zero_write_ok
    )

    TEST_STATUS = (
        "PASS"
        if final_ok
        else "FAIL"
    )

    line()

    log(
        f"{STAGE}: FINAL TEST SUMMARY"
    )

    line()

    log(
        f"TEST_STATUS={TEST_STATUS}"
    )

    log(
        "R36E_WRITER_PRE_LIVE_GATE="
        + (
            "PASS"
            if final_ok
            else "FAIL"
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
        "TP3_POLICY="
        "60_PERCENT_TRAILING_RUNNER"
    )

    log(
        "REAL_ORDER_EXECUTION="
        + str(
            LIVE_ORDER_EXECUTION
        )
    )

    log(
        "DEMO_ORDER_EXECUTION="
        + str(
            DEMO_ORDER_EXECUTION
        )
    )

    log(
        "EXCHANGE_NETWORK_WRITES="
        + str(
            EXCHANGE_NETWORK_WRITES
        )
    )

    log(
        "REAL_ORDERS_SENT="
        + str(
            REAL_ORDERS_SENT
        )
    )

    log(
        "FINAL_BLOCKERS="
        + canonical_json(
            FINAL_BLOCKERS
        )
    )

    if final_ok:

        log(
            "NEXT_STAGE="
            "R36E_DEMO_WRITER_VALIDATION"
        )

    else:

        log(
            "NEXT_STAGE="
            "FIX_ONLY_LISTED_BLOCKERS"
        )

    line()


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():

    global HEARTBEAT

    while True:

        HEARTBEAT += 1

        log(
            f"{STAGE}: "
            f"HEARTBEAT={HEARTBEAT} "
            f"TEST_STATUS={TEST_STATUS} "
            f"BTCUSDT_FLAT={BTCUSDT_FLAT} "
            f"MARK_PRICE={CURRENT_MARK_PRICE} "
            f"LONG_LEVERAGE={CURRENT_LONG_LEVERAGE} "
            f"SHORT_LEVERAGE={CURRENT_SHORT_LEVERAGE} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDERS_SENT="
            f"{REAL_ORDERS_SENT} "
            f"LIVE_ORDER_EXECUTION="
            f"{LIVE_ORDER_EXECUTION}"
        )

        time.sleep(30)


# =============================================================================
# MAIN
# =============================================================================

def main():

    start_health_server()

    try:

        run_r36e()

    except Exception as exc:

        global TEST_STATUS

        TEST_STATUS = "FAIL"

        line()

        log(
            f"{STAGE}: UNHANDLED ERROR"
        )

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

        line()

    heartbeat_loop()


if __name__ == "__main__":
    main()
```

