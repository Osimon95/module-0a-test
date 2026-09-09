
#!/usr/bin/env python3
"""
R36F.15.2 - SELECTED TP SNAPSHOT SCOPE FIX FOR CONTROLLED WEEX DEMO

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5.4/R36F.8 safety baseline
    while correcting ONLY the remaining pre-live readiness classification:

        A market may have a valid historical TP set but still be unable to
        represent the frozen 20% / 20% / 60% TP quantity split because the
        planned entry quantity is below the strict exchange-representable
        minimum. That condition is normal TRADE INELIGIBILITY, not a writer
        capability failure and not a FINAL_BLOCKER.

R36F.15.2 CHANGE:

    1. Preserve the complete R36F.15.1 continuous fresh-market reevaluation pipeline.
    2. Fix ONLY the stale selected_tp_snapshot reference in the eligible writer/demo path.
    3. Use the already-selected direction-specific selected_snapshot consistently for demo preview construction.
    4. Add an explicit blocker if the eligible writer/demo construction pipeline raises an unexpected exception.
    5. Preserve normal TRADE_NOT_ELIGIBLE states as non-final-blocking market conditions.
    6. Preserve EMA, two-cluster TP, 20/20/60 quantity allocation, protective stop, stop-risk envelope, stop-loss budget, backup configuration, exactly-once demo journal, and all real-money firebreaks unchanged.

R36F.15.1 CHANGE:

    1. Keep the full R36F.15 startup validation and demo execution chain unchanged.
    2. After each runtime interval, rerun the complete fresh market/account pipeline.
    3. Refetch mark price and up to the existing 1000 one-minute historical candles.
    4. Recalculate EMA19/EMA50/EMA200 and LONG/SHORT historical TP clusters.
    5. Revalidate the configured Telegram command against the fresh EMA direction
       and fresh direction-specific TP market eligibility.
    6. Rebuild quantity, protective-stop, stop-risk-envelope and stop-loss-budget
       authorization previews from the fresh market snapshot.
    7. Permit WEEX demo transport only through the existing R36F.15 arm and full
       authorization chain.
    8. Preserve the durable demo dispatch journal so one completed first demo order
       cannot be submitted again on later reevaluation cycles or restart.
    9. Keep every production / real-money mutation switch hard-disabled.
   10. Make the runtime interval configurable with R36F151_REEVALUATION_SECONDS,
       default 60 seconds and minimum 15 seconds.

R36F.11 CHANGE:

    1. Preserve the R36F.8 WEEX read-only position route and GET signing.
    2. Preserve historical two-cluster TP approval unchanged.
    3. Preserve TP price policy unchanged:
           TP1 = 20% adjustable progress toward Cluster 1
           TP2 = 50% adjustable progress toward Cluster 2
           TP3 = 60% trailing runner
    4. Preserve TP quantity allocation unchanged:
           TP1 = 20%
           TP2 = 20%
           TP3 = 60%
    5. Preserve strict minimum entry quantity discovery unchanged.
    6. Add explicit quantity/balance readiness calculation before writer
       construction:
           planned_entry_qty
           minimum_strict_tp_entry_qty
           required_margin_for_minimum_qty
           required_available_balance
           available_balance_shortfall
           quantity_feasible
           trade_readiness_status/reason
    7. Keep insufficient balance as a TRADE READINESS blocker, not a
       capability blocker.
    8. Keep all production writes hard-disabled.
    9. Preserve demo transport as the only possible mutation path when the
       complete R36F.15 demo authorization chain explicitly arms it.

R36F.10 CHANGE:

    1. Preserve the complete R36F.9 baseline.
    2. Preserve TP1/TP2/TP3 quantity allocation as adjustable configuration.
    3. Keep the frozen production allocation at 20% / 20% / 60%.
    4. Add deterministic feasibility testing proving that alternate
       allocations can be represented when the exchange quantity step allows.
    5. Do not silently change the production allocation merely to fit a
       small balance.
    6. Keep insufficient balance as a trade-readiness condition rather than
       changing strategy semantics automatically.

R36F.9 CHANGE:

    1. Preserve R36F.8 read-only position reconciliation.
    2. Preserve historical two-cluster TP approval unchanged.
    3. Preserve strict 20% / 20% / 60% TP quantity allocation.
    4. Add explicit balance-readiness reporting for the strict TP split.
    5. Keep writer construction blocked unless the strict split is exactly
       exchange-representable.
    6. Keep all exchange mutation disabled.

R36F.8 CHANGE:

    1. Preserve all R36F.5.3 historical-cluster logic.
    2. Preserve all synthetic two-cluster approval/rejection tests.
    3. Preserve all execution safety firebreaks.
    4. Repair only the WEEX read-only position reconciliation route.
    5. Never let a position-read diagnostic failure change the TP engine.
    6. Keep all exchange writes disabled.

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

STAGE = "R36F.15.2"

PURPOSE = (
    "SELECTED TP SNAPSHOT SCOPE FIX: preserve the complete R36F.15.1 continuous "
    "EMA19/EMA50/EMA200 + Telegram + two-cluster TP + quantity/readiness + mandatory "
    "protective-stop + stop-risk-envelope + stop-loss-budget + exactly-once WEEX demo "
    "dispatch chain, while fixing only the stale selected_tp_snapshot reference so the "
    "already-selected direction-specific TP snapshot reaches demo preview construction "
    "correctly. Production /capi/v3/order and every real-money mutation remain hard-disabled."
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

# R36F.15.1 runtime correction: rerun the complete fresh read/evaluation
# pipeline periodically instead of reporting startup-cached market state.
R36F151_REEVALUATION_SECONDS = max(
    15,
    int(os.getenv("R36F151_REEVALUATION_SECONDS", "60")),
)

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

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

TP1_ALLOCATION_PERCENT = Decimal("20")
TP2_ALLOCATION_PERCENT = Decimal("20")
TP3_ALLOCATION_PERCENT = Decimal("60")

TP1_PROGRESS_PERCENT = Decimal("20")
TP2_PROGRESS_PERCENT = Decimal("50")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True

CLUSTER_TOLERANCE_PERCENT = Decimal("0.20")
MIN_CLUSTER_TOUCHES = 2
REQUIRED_CLUSTERS = 2


# ============================================================
# EXECUTION SAFETY
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
# R36F.14 / R36F.15 CONTROLLED DEMO CONFIGURATION
# ============================================================

R36F14_DEMO_MODE_ENABLED = (
    os.getenv("R36F14_DEMO_MODE_ENABLED", "false")
    .strip()
    .lower()
    == "true"
)

R36F14_DEMO_POST_TRANSPORT_ENABLED = False
R36F14_DEMO_ORDER_SUBMISSION_ENABLED = False
R36F14_FIRST_DEMO_ORDER_ALLOWED = False

R36F15_DEMO_EXECUTION_ARM = (
    os.getenv("R36F15_DEMO_EXECUTION_ARM", "false")
    .strip()
    .lower()
    == "true"
)

R36F15_DEMO_ONLY_TRANSPORT_ENABLED = (
    R36F14_DEMO_MODE_ENABLED
    and R36F15_DEMO_EXECUTION_ARM
)

R36F15_FIRST_DEMO_ORDER_ALLOWED = (
    R36F15_DEMO_ONLY_TRANSPORT_ENABLED
)

DEMO_API_BASE_URL = API_BASE_URL
DEMO_SYMBOL = SYMBOL

DEMO_ASSET = "SUSDT"

DEMO_ORDER_PATH = "/capi/v3/order"
DEMO_ACCOUNT_PATH = "/capi/v3/account/assets"
DEMO_POSITION_PATH = "/capi/v3/account/positions"
DEMO_HISTORY_PATH = "/capi/v3/order/history"


# ============================================================
# ENVIRONMENT / CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

R36F12_TELEGRAM_ALERT_ENABLED = (
    os.getenv("R36F12_TELEGRAM_ALERT_ENABLED", "false")
    .strip()
    .lower()
    == "true"
)

R36F12_TELEGRAM_COMMAND = (
    os.getenv("R36F12_TELEGRAM_COMMAND", "")
    .strip()
    .upper()
)


# ============================================================
# DURABLE STATE
# ============================================================

STATE_DIR = os.getenv(
    "R36F_STATE_DIR",
    "/var/data/r36f_state",
).strip()

R36A_EVIDENCE_FILE = os.path.join(
    STATE_DIR,
    "r36a_evidence.json",
)

R36C_EVIDENCE_FILE = os.path.join(
    STATE_DIR,
    "r36c_evidence.json",
)

R36D_SNAPSHOT_FILE = os.path.join(
    STATE_DIR,
    "r36d_snapshot.json",
)

PRE_LIVE_READINESS_SNAPSHOT_FILE = os.path.join(
    STATE_DIR,
    "pre_live_readiness_snapshot.json",
)

R36F15_DEMO_DISPATCH_JOURNAL_FILE = os.path.join(
    STATE_DIR,
    "r36f15_demo_dispatch_journal.json",
)


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )
        self.end_headers()

        self.wfile.write(
            (
                f"{STAGE} PASS\n"
            ).encode("utf-8")
        )

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
        ("0.0.0.0", port),
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
# LOGGING
# ============================================================

def utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat()


def log(message):
    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def separator():
    log(
        "-" * 100
    )


def diagnostic_pass(name):
    log(
        f"PASS: {name}"
    )


def diagnostic_fail(
    name,
    reason=None,
):
    if reason:
        log(
            f"FAIL: {name} = {reason}"
        )
    else:
        log(
            f"FAIL: {name}"
        )


# ============================================================
# DECIMAL HELPERS
# ============================================================

def D(value):
    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def normalize_price(
    value,
):
    value = D(value)

    steps = (
        value
        / PRICE_STEP
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        steps
        * PRICE_STEP
    )


def normalize_quantity(
    value,
):
    value = D(value)

    steps = (
        value
        / QUANTITY_STEP
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        steps
        * QUANTITY_STEP
    )


def decimal_to_str(
    value,
):
    if value is None:
        return None

    value = D(value)

    return format(
        value,
        "f",
    )


def decimal_or_none(
    value,
):
    if value is None:
        return None

    try:
        return D(value)
    except Exception:
        return None


# ============================================================
# JSON HELPERS
# ============================================================

def json_default(
    value,
):
    if isinstance(
        value,
        Decimal,
    ):
        return decimal_to_str(
            value
        )

    raise TypeError(
        f"Unsupported JSON value: {type(value)}"
    )


def canonical_json(
    value,
):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=json_default,
    )


def sha256_text(
    value,
):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_json(
    value,
):
    return sha256_text(
        canonical_json(value)
    )


# ============================================================
# FILE HELPERS
# ============================================================

def ensure_state_dir():
    os.makedirs(
        STATE_DIR,
        exist_ok=True,
    )


def read_json_file(
    path,
):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(
            handle
        )


def write_json_file(
    path,
    value,
):
    ensure_state_dir()

    temporary_path = (
        f"{path}.tmp"
    )

    with open(
        temporary_path,
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            value,
            handle,
            indent=2,
            sort_keys=True,
            default=json_default,
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temporary_path,
        path,
    )


# ============================================================
# BASIC SAFETY TESTS
# ============================================================

def safety_tests():
    results = []

    checks = [
        (
            "REAL_ORDER_EXECUTION_DISABLED",
            REAL_ORDER_EXECUTION is False,
        ),
        (
            "DEMO_ORDER_EXECUTION_DISABLED",
            DEMO_ORDER_EXECUTION is False,
        ),
        (
            "EXCHANGE_MUTATION_TRANSPORT_DISABLED",
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
        ),
        (
            "ORDER_SUBMISSION_DISABLED",
            ORDER_SUBMISSION_ENABLED is False,
        ),
        (
            "LEVERAGE_MUTATION_DISABLED",
            LEVERAGE_MUTATION_ENABLED is False,
        ),
        (
            "MARGIN_MODE_MUTATION_DISABLED",
            MARGIN_MODE_MUTATION_ENABLED is False,
        ),
        (
            "POSITION_MUTATION_DISABLED",
            POSITION_MUTATION_ENABLED is False,
        ),
        (
            "FIRST_REAL_ORDER_DISABLED",
            FIRST_REAL_ORDER_ALLOWED is False,
        ),
    ]

    for (
        name,
        passed,
    ) in checks:
        if passed:
            diagnostic_pass(
                name
            )
        else:
            diagnostic_fail(
                name
            )

        results.append(
            passed
        )

    return all(
        results
    )


# ============================================================
# R36F.14 / R36F.15 DEMO SAFETY TESTS
# ============================================================

def demo_safety_tests():
    results = []

    checks = [
        (
            "R36F14_DEMO_POST_TRANSPORT_DISABLED",
            R36F14_DEMO_POST_TRANSPORT_ENABLED
            is False,
        ),
        (
            "R36F14_DEMO_ORDER_SUBMISSION_DISABLED",
            R36F14_DEMO_ORDER_SUBMISSION_ENABLED
            is False,
        ),
        (
            "R36F14_FIRST_DEMO_ORDER_DISABLED",
            R36F14_FIRST_DEMO_ORDER_ALLOWED
            is False,
        ),
        (
            "R36F15_REAL_MONEY_FIREBREAK_INTACT",
            (
                REAL_ORDER_EXECUTION
                is False
                and EXCHANGE_MUTATION_TRANSPORT_ENABLED
                is False
                and ORDER_SUBMISSION_ENABLED
                is False
                and FIRST_REAL_ORDER_ALLOWED
                is False
            ),
        ),
        (
            "R36F15_DEMO_ONLY_TRANSPORT_CONFIGURATION_VALID",
            (
                R36F15_DEMO_ONLY_TRANSPORT_ENABLED
                == (
                    R36F14_DEMO_MODE_ENABLED
                    and R36F15_DEMO_EXECUTION_ARM
                )
            ),
        ),
    ]

    for (
        name,
        passed,
    ) in checks:
        if passed:
            diagnostic_pass(
                name
            )
        else:
            diagnostic_fail(
                name
            )

        results.append(
            passed
        )

    if (
        R36F15_DEMO_ONLY_TRANSPORT_ENABLED
    ):
        diagnostic_pass(
            "R36F15_DEMO_ONLY_TRANSPORT_ENABLED"
        )
    else:
        log(
            "R36F15_DEMO_ONLY_TRANSPORT_ENABLED = False"
        )

    return all(
        results
    )


# ============================================================
# CREDENTIAL TESTS
# ============================================================

def credential_tests():
    checks = [
        (
            "WEEX_API_KEY_PRESENT",
            bool(
                WEEX_API_KEY
            ),
        ),
        (
            "WEEX_API_SECRET_PRESENT",
            bool(
                WEEX_API_SECRET
            ),
        ),
        (
            "WEEX_API_PASSPHRASE_PRESENT",
            bool(
                WEEX_API_PASSPHRASE
            ),
        ),
    ]

    results = []

    for (
        name,
        passed,
    ) in checks:
        if passed:
            diagnostic_pass(
                name
            )
        else:
            diagnostic_fail(
                name
            )

        results.append(
            passed
        )

    return all(
        results
    )


# ============================================================
# WEEX SIGNING
# ============================================================

def build_query_string(
    params,
):
    if not params:
        return ""

    items = []

    for key in sorted(
        params.keys()
    ):
        value = params[key]

        if value is None:
            continue

        items.append(
            f"{key}={value}"
        )

    return "&".join(
        items
    )


def sign_weex_request(
    timestamp_ms,
    method,
    path,
    query_string="",
    body="",
):
    request_path = path

    if query_string:
        request_path = (
            f"{path}?{query_string}"
        )

    prehash = (
        str(timestamp_ms)
        + method.upper()
        + request_path
        + body
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


def build_auth_headers(
    method,
    path,
    params=None,
    body=None,
):
    timestamp_ms = int(
        time.time()
        * 1000
    )

    query_string = build_query_string(
        params
    )

    body_text = ""

    if body is not None:
        body_text = canonical_json(
            body
        )

    signature = sign_weex_request(
        timestamp_ms=timestamp_ms,
        method=method,
        path=path,
        query_string=query_string,
        body=body_text,
    )

    headers = {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            str(
                timestamp_ms
            ),

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "Content-Type":
            "application/json",
    }

    return (
        headers,
        query_string,
        body_text,
    )


# ============================================================
# HTTP READ HELPERS
# ============================================================

async def http_get_json(
    session,
    url,
    headers=None,
):
    async with session.get(
        url,
        headers=headers,
    ) as response:
        text = await response.text()

        if response.status < 200 or response.status >= 300:
            raise RuntimeError(
                f"HTTP {response.status}: {text}"
            )

        try:
            return json.loads(
                text
            )
        except Exception:
            raise RuntimeError(
                f"INVALID JSON RESPONSE: {text}"
            )


async def weex_private_get(
    session,
    path,
    params=None,
):
    headers, query_string, _ = (
        build_auth_headers(
            method="GET",
            path=path,
            params=params,
        )
    )

    url = (
        API_BASE_URL
        + path
    )

    if query_string:
        url = (
            url
            + "?"
            + query_string
        )

    return await http_get_json(
        session=session,
        url=url,
        headers=headers,
    )


# ============================================================
# PUBLIC MARKET DATA
# ============================================================

async def fetch_mark_price(
    session,
):
    candidate_urls = [
        (
            API_BASE_URL
            + "/capi/v2/market/ticker"
            + f"?symbol={PUBLIC_TICKER_SYMBOL}"
        ),
        (
            API_BASE_URL
            + "/capi/v2/market/tickers"
            + f"?symbol={PUBLIC_TICKER_SYMBOL}"
        ),
    ]

    last_error = None

    for url in candidate_urls:
        try:
            payload = await http_get_json(
                session=session,
                url=url,
            )

            price = extract_mark_price(
                payload
            )

            if price is not None:
                return price

        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError(
        "MARK PRICE NOT FOUND"
    )


def extract_mark_price(
    payload,
):
    candidate_keys = [
        "markPrice",
        "mark_price",
        "price",
        "last",
        "lastPrice",
        "close",
    ]

    def inspect(
        value,
    ):
        if isinstance(
            value,
            dict,
        ):
            for key in candidate_keys:
                if key in value:
                    candidate = decimal_or_none(
                        value[key]
                    )

                    if (
                        candidate
                        is not None
                        and candidate
                        > 0
                    ):
                        return candidate

            for nested in value.values():
                found = inspect(
                    nested
                )

                if found is not None:
                    return found

        elif isinstance(
            value,
            list,
        ):
            for nested in value:
                found = inspect(
                    nested
                )

                if found is not None:
                    return found

        return None

    return inspect(
        payload
    )


# ============================================================
# HISTORICAL KLINES
# ============================================================

async def fetch_historical_klines(
    session,
):
    rows = []

    end_time = None

    for page_index in range(
        MAX_HISTORICAL_PAGES
    ):
        params = {
            "symbol":
                PUBLIC_TICKER_SYMBOL,

            "interval":
                KLINE_INTERVAL,

            "limit":
                HISTORICAL_LIMIT,
        }

        if end_time is not None:
            params["endTime"] = (
                end_time
            )

        query_string = build_query_string(
            params
        )

        candidate_urls = [
            (
                API_BASE_URL
                + "/capi/v2/market/candles"
                + "?"
                + query_string
            ),
            (
                API_BASE_URL
                + "/capi/v2/market/kline"
                + "?"
                + query_string
            ),
            (
                API_BASE_URL
                + "/capi/v2/market/klines"
                + "?"
                + query_string
            ),
        ]

        page_rows = None
        page_error = None

        for url in candidate_urls:
            try:
                payload = await http_get_json(
                    session=session,
                    url=url,
                )

                extracted = extract_kline_rows(
                    payload
                )

                if extracted:
                    page_rows = extracted
                    break

            except Exception as exc:
                page_error = exc

        if not page_rows:
            if page_index == 0:
                if page_error:
                    raise page_error

                raise RuntimeError(
                    "NO HISTORICAL KLINES"
                )

            break

        rows.extend(
            page_rows
        )

        timestamps = []

        for row in page_rows:
            timestamp = (
                row.get(
                    "timestamp"
                )
            )

            if timestamp is not None:
                timestamps.append(
                    int(timestamp)
                )

        if not timestamps:
            break

        oldest = min(
            timestamps
        )

        end_time = (
            oldest
            - 1
        )

        if len(
            page_rows
        ) < HISTORICAL_LIMIT:
            break

    deduplicated = {}

    for row in rows:
        timestamp = row.get(
            "timestamp"
        )

        if timestamp is None:
            continue

        deduplicated[
            int(timestamp)
        ] = row

    ordered = [
        deduplicated[key]
        for key in sorted(
            deduplicated.keys()
        )
    ]

    return ordered


def extract_kline_rows(
    payload,
):
    raw_rows = []

    if isinstance(
        payload,
        list,
    ):
        raw_rows = payload

    elif isinstance(
        payload,
        dict,
    ):
        candidate_keys = [
            "data",
            "rows",
            "list",
            "candles",
            "klines",
        ]

        for key in candidate_keys:
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                raw_rows = value
                break

            if isinstance(
                value,
                dict,
            ):
                for nested_key in candidate_keys:
                    nested = value.get(
                        nested_key
                    )

                    if isinstance(
                        nested,
                        list,
                    ):
                        raw_rows = nested
                        break

                if raw_rows:
                    break

    rows = []

    for item in raw_rows:
        parsed = parse_kline_row(
            item
        )

        if parsed is not None:
            rows.append(
                parsed
            )

    return rows


def parse_kline_row(
    item,
):
    if isinstance(
        item,
        dict,
    ):
        timestamp = first_present(
            item,
            [
                "timestamp",
                "time",
                "ts",
                "openTime",
            ],
        )

        open_price = first_present(
            item,
            [
                "open",
                "o",
            ],
        )

        high_price = first_present(
            item,
            [
                "high",
                "h",
            ],
        )

        low_price = first_present(
            item,
            [
                "low",
                "l",
            ],
        )

        close_price = first_present(
            item,
            [
                "close",
                "c",
            ],
        )

    elif isinstance(
        item,
        list,
    ):
        if len(
            item
        ) < 5:
            return None

        timestamp = item[0]
        open_price = item[1]
        high_price = item[2]
        low_price = item[3]
        close_price = item[4]

    else:
        return None

    timestamp_value = decimal_or_none(
        timestamp
    )

    open_value = decimal_or_none(
        open_price
    )

    high_value = decimal_or_none(
        high_price
    )

    low_value = decimal_or_none(
        low_price
    )

    close_value = decimal_or_none(
        close_price
    )

    if (
        timestamp_value
        is None
        or open_value
        is None
        or high_value
        is None
        or low_value
        is None
        or close_value
        is None
    ):
        return None

    return {
        "timestamp":
            int(
                timestamp_value
            ),

        "open":
            open_value,

        "high":
            high_value,

        "low":
            low_value,

        "close":
            close_value,
    }


def first_present(
    mapping,
    keys,
):
    for key in keys:
        if key in mapping:
            return mapping[key]

    return None


# ============================================================
# EMA ENGINE
# ============================================================

def calculate_ema(
    values,
    period,
):
    if not values:
        return None

    if len(
        values
    ) < period:
        return None

    multiplier = (
        Decimal("2")
        / Decimal(
            period + 1
        )
    )

    seed = (
        sum(
            values[:period]
        )
        / Decimal(
            period
        )
    )

    ema = seed

    for value in values[
        period:
    ]:
        ema = (
            (
                value
                - ema
            )
            * multiplier
            + ema
        )

    return ema


def calculate_ema_snapshot(
    rows,
):
    closes = [
        D(
            row["close"]
        )
        for row in rows
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

    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):
        return {
            "ready":
                False,

            "ema19":
                ema19,

            "ema50":
                ema50,

            "ema200":
                ema200,

            "ideal_direction":
                None,
        }

    ideal_direction = None

    if (
        ema19
        > ema50
        > ema200
    ):
        ideal_direction = (
            "LONG"
        )

    elif (
        ema19
        < ema50
        < ema200
    ):
        ideal_direction = (
            "SHORT"
        )

    return {
        "ready":
            True,

        "ema19":
            ema19,

        "ema50":
            ema50,

        "ema200":
            ema200,

        "ideal_direction":
            ideal_direction,
    }


# ============================================================
# HISTORICAL EXTREMA
# ============================================================

def local_high_extrema(
    rows,
):
    extrema = []

    if len(
        rows
    ) < 3:
        return extrema

    for index in range(
        1,
        len(rows) - 1,
    ):
        previous_row = (
            rows[index - 1]
        )

        current_row = (
            rows[index]
        )

        next_row = (
            rows[index + 1]
        )

        current_high = D(
            current_row["high"]
        )

        if (
            current_high
            >= D(
                previous_row["high"]
            )
            and current_high
            >= D(
                next_row["high"]
            )
        ):
            extrema.append(
                current_high
            )

    return extrema


def local_low_extrema(
    rows,
):
    extrema = []

    if len(
        rows
    ) < 3:
        return extrema

    for index in range(
        1,
        len(rows) - 1,
    ):
        previous_row = (
            rows[index - 1]
        )

        current_row = (
            rows[index]
        )

        next_row = (
            rows[index + 1]
        )

        current_low = D(
            current_row["low"]
        )

        if (
            current_low
            <= D(
                previous_row["low"]
            )
            and current_low
            <= D(
                next_row["low"]
            )
        ):
            extrema.append(
                current_low
            )

    return extrema


# ============================================================
# CLUSTER ENGINE
# ============================================================

def cluster_prices(
    prices,
):
    if not prices:
        return []

    ordered = sorted(
        [
            D(price)
            for price in prices
        ]
    )

    clusters = []

    current = [
        ordered[0]
    ]

    for price in ordered[
        1:
    ]:
        average = (
            sum(
                current
            )
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
            price
            - average
        ) <= tolerance:
            current.append(
                price
            )

        else:
            clusters.append(
                summarize_cluster(
                    current
                )
            )

            current = [
                price
            ]

    clusters.append(
        summarize_cluster(
            current
        )
    )

    return clusters


def summarize_cluster(
    values,
):
    values = [
        D(value)
        for value in values
    ]

    return {
        "average":
            (
                sum(values)
                / Decimal(
                    len(values)
                )
            ),

        "minimum":
            min(
                values
            ),

        "maximum":
            max(
                values
            ),

        "touches":
            len(
                values
            ),
    }


def validate_long_clusters(
    clusters,
    entry_price,
):
    entry_price = D(
        entry_price
    )

    valid = []
    invalid = []

    for cluster in clusters:
        reasons = []

        if (
            cluster["touches"]
            < MIN_CLUSTER_TOUCHES
        ):
            reasons.append(
                "INSUFFICIENT_TOUCHES"
            )

        if (
            cluster["average"]
            <= entry_price
        ):
            reasons.append(
                "CLUSTER_NOT_ABOVE_ENTRY"
            )

        if reasons:
            invalid.append(
                {
                    **cluster,
                    "reasons":
                        reasons,
                }
            )
        else:
            valid.append(
                cluster
            )

    valid.sort(
        key=lambda item:
            item["average"]
    )

    return (
        valid,
        invalid,
    )


def validate_short_clusters(
    clusters,
    entry_price,
):
    entry_price = D(
        entry_price
    )

    valid = []
    invalid = []

    for cluster in clusters:
        reasons = []

        if (
            cluster["touches"]
            < MIN_CLUSTER_TOUCHES
        ):
            reasons.append(
                "INSUFFICIENT_TOUCHES"
            )

        if (
            cluster["average"]
            >= entry_price
        ):
            reasons.append(
                "CLUSTER_NOT_BELOW_ENTRY"
            )

        if reasons:
            invalid.append(
                {
                    **cluster,
                    "reasons":
                        reasons,
                }
            )
        else:
            valid.append(
                cluster
            )

    valid.sort(
        key=lambda item:
            item["average"],
        reverse=True,
    )

    return (
        valid,
        invalid,
    )


# ============================================================
# TP APPROVAL
# ============================================================

def approve_tp_clusters(
    direction,
    valid_clusters,
):
    available = len(
        valid_clusters
    )

    if (
        available
        >= REQUIRED_CLUSTERS
    ):
        return {
            "status":
                "APPROVED",

            "reason":
                "ENOUGH_VALID_CLUSTERS",

            "required_clusters":
                REQUIRED_CLUSTERS,

            "available_clusters":
                available,

            "selected_clusters":
                valid_clusters[
                    :REQUIRED_CLUSTERS
                ],
        }

    if available == 1:
        reason = (
            "ONLY_ONE_VALID_CLUSTER"
        )

    else:
        reason = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    return {
        "status":
            "REJECTED",

        "reason":
            reason,

        "required_clusters":
            REQUIRED_CLUSTERS,

        "available_clusters":
            available,

        "selected_clusters":
            [],
    }


# ============================================================
# TP PRICE ENGINE
# ============================================================

def progress_price(
    entry_price,
    target_price,
    progress_percent,
):
    entry_price = D(
        entry_price
    )

    target_price = D(
        target_price
    )

    progress_percent = D(
        progress_percent
    )

    difference = (
        target_price
        - entry_price
    )

    progress = (
        difference
        * progress_percent
        / Decimal("100")
    )

    return normalize_price(
        entry_price
        + progress
    )


def build_tp_snapshot(
    direction,
    entry_price,
    approval,
):
    if (
        approval.get(
            "status"
        )
        != "APPROVED"
    ):
        return {
            "approved":
                False,

            "direction":
                direction,

            "entry_price":
                D(
                    entry_price
                ),

            "tp1":
                None,

            "tp2":
                None,

            "tp3_mode":
                "TRAILING_RUNNER",

            "tp3_trailing_distance_percent":
                TRAILING_DISTANCE_PERCENT,

            "reason":
                approval.get(
                    "reason"
                ),
        }

    selected = approval[
        "selected_clusters"
    ]

    cluster1 = selected[0]
    cluster2 = selected[1]

    tp1 = progress_price(
        entry_price=entry_price,
        target_price=cluster1[
            "average"
        ],
        progress_percent=TP1_PROGRESS_PERCENT,
    )

    tp2 = progress_price(
        entry_price=entry_price,
        target_price=cluster2[
            "average"
        ],
        progress_percent=TP2_PROGRESS_PERCENT,
    )

    return {
        "approved":
            True,

        "direction":
            direction,

        "entry_price":
            D(
                entry_price
            ),

        "cluster1_average":
            cluster1[
                "average"
            ],

        "cluster2_average":
            cluster2[
                "average"
            ],

        "tp1":
            tp1,

        "tp2":
            tp2,

        "tp3_mode":
            "TRAILING_RUNNER",

        "tp3_trailing_distance_percent":
            TRAILING_DISTANCE_PERCENT,

        "primary_tp_immutable_after_fill":
            True,

        "backup_tp_recalculate_on_backup_fill_only":
            True,
    }


# ============================================================
# SYNTHETIC TP TESTS
# ============================================================

def synthetic_cluster_tests():
    results = []

    synthetic_long_entry = (
        Decimal("100")
    )

    synthetic_long_valid = [
        {
            "average":
                Decimal("110"),

            "minimum":
                Decimal("109"),

            "maximum":
                Decimal("111"),

            "touches":
                3,
        },
        {
            "average":
                Decimal("120"),

            "minimum":
                Decimal("119"),

            "maximum":
                Decimal("121"),

            "touches":
                4,
        },
    ]

    long_approval = (
        approve_tp_clusters(
            "LONG",
            synthetic_long_valid,
        )
    )

    long_snapshot = (
        build_tp_snapshot(
            direction="LONG",
            entry_price=synthetic_long_entry,
            approval=long_approval,
        )
    )

    checks = [
        (
            "SYNTHETIC_LONG_TWO_CLUSTER_APPROVAL",
            long_approval[
                "status"
            ]
            == "APPROVED",
        ),
        (
            "SYNTHETIC_LONG_TP1_CREATED",
            long_snapshot[
                "tp1"
            ]
            is not None,
        ),
        (
            "SYNTHETIC_LONG_TP2_CREATED",
            long_snapshot[
                "tp2"
            ]
            is not None,
        ),
    ]

    synthetic_short_entry = (
        Decimal("100")
    )

    synthetic_short_valid = [
        {
            "average":
                Decimal("90"),

            "minimum":
                Decimal("89"),

            "maximum":
                Decimal("91"),

            "touches":
                3,
        },
        {
            "average":
                Decimal("80"),

            "minimum":
                Decimal("79"),

            "maximum":
                Decimal("81"),

            "touches":
                4,
        },
    ]

    short_approval = (
        approve_tp_clusters(
            "SHORT",
            synthetic_short_valid,
        )
    )

    short_snapshot = (
        build_tp_snapshot(
            direction="SHORT",
            entry_price=synthetic_short_entry,
            approval=short_approval,
        )
    )

    checks.extend(
        [
            (
                "SYNTHETIC_SHORT_TWO_CLUSTER_APPROVAL",
                short_approval[
                    "status"
                ]
                == "APPROVED",
            ),
            (
                "SYNTHETIC_SHORT_TP1_CREATED",
                short_snapshot[
                    "tp1"
                ]
                is not None,
            ),
            (
                "SYNTHETIC_SHORT_TP2_CREATED",
                short_snapshot[
                    "tp2"
                ]
                is not None,
            ),
        ]
    )

    for (
        name,
        passed,
    ) in checks:
        if passed:
            diagnostic_pass(
                name
            )
        else:
            diagnostic_fail(
                name
            )

        results.append(
            passed
        )

    return all(
        results
    )


def synthetic_tp_rejection_test():
    one_cluster = [
        {
            "average":
                Decimal("90"),

            "minimum":
                Decimal("89"),

            "maximum":
                Decimal("91"),

            "touches":
                3,
        }
    ]

    approval = (
        approve_tp_clusters(
            "SHORT",
            one_cluster,
        )
    )

    status_rejected = (
        approval[
            "status"
        ]
        == "REJECTED"
    )

    no_tp_set = (
        len(
            approval[
                "selected_clusters"
            ]
        )
        == 0
    )

    if status_rejected:
        diagnostic_pass(
            "ONE_CLUSTER_APPROVAL_STATUS_REJECTED"
        )
    else:
        diagnostic_fail(
            "ONE_CLUSTER_APPROVAL_STATUS_REJECTED"
        )

    if no_tp_set:
        diagnostic_pass(
            "ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET"
        )
    else:
        diagnostic_fail(
            "ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET"
        )

    return (
        status_rejected
        and no_tp_set
    )


# ============================================================
# CLUSTER DIAGNOSTICS
# ============================================================

def build_cluster_diagnostics(
    direction,
    extrema,
    clusters,
    valid_clusters,
    invalid_clusters,
    approval,
):
    return {
        "direction":
            direction,

        "extrema_count":
            len(
                extrema
            ),

        "cluster_count":
            len(
                clusters
            ),

        "valid_cluster_count":
            len(
                valid_clusters
            ),

        "invalid_cluster_count":
            len(
                invalid_clusters
            ),

        "approval_status":
            approval.get(
                "status"
            ),

        "approval_reason":
            approval.get(
                "reason"
            ),

        "required_clusters":
            approval.get(
                "required_clusters"
            ),

        "available_clusters":
            approval.get(
                "available_clusters"
            ),

        "valid_clusters":
            valid_clusters,

        "invalid_clusters":
            invalid_clusters,
    }


def print_cluster_diagnostics(
    diagnostics,
):
    direction = diagnostics[
        "direction"
    ]

    log(
        f"{direction} EXTREMA = "
        f"{diagnostics['extrema_count']}"
    )

    log(
        f"{direction} CLUSTERS = "
        f"{diagnostics['cluster_count']}"
    )

    log(
        f"{direction} VALID CLUSTERS = "
        f"{diagnostics['valid_cluster_count']}"
    )

    for (
        index,
        cluster,
    ) in enumerate(
        diagnostics[
            "valid_clusters"
        ],
        start=1,
    ):
        log(
            f"{direction} VALID CLUSTER {index}: "
            f"average={decimal_to_str(cluster['average'])} "
            f"minimum={decimal_to_str(cluster['minimum'])} "
            f"maximum={decimal_to_str(cluster['maximum'])} "
            f"touches={cluster['touches']}"
        )

    for (
        index,
        cluster,
    ) in enumerate(
        diagnostics[
            "invalid_clusters"
        ],
        start=1,
    ):
        reasons = ",".join(
            cluster.get(
                "reasons",
                [],
            )
        )

        log(
            f"{direction} INVALID CLUSTER {index}: "
            f"average={decimal_to_str(cluster['average'])} "
            f"reasons={reasons}"
        )

    log(
        f"{direction} CLUSTER DIAGNOSTIC FAILURE_REASON = "
        f"{diagnostics['approval_reason']}"
    )

    log(
        f"{STAGE}_TP_APPROVAL = "
        f"{diagnostics['approval_status']}"
    )

    log(
        f"{STAGE}_TP_APPROVAL_REASON = "
        f"{diagnostics['approval_reason']}"
    )

    log(
        f"{STAGE}_TP_REQUIRED_CLUSTERS = "
        f"{diagnostics['required_clusters']}"
    )

    log(
        f"{STAGE}_TP_AVAILABLE_CLUSTERS = "
        f"{diagnostics['available_clusters']}"
    )


# ============================================================
# ACCOUNT READ
# ============================================================

async def fetch_available_usdt(
    session,
):
    candidate_paths = [
        "/capi/v3/account/assets",
        "/capi/v2/account/assets",
    ]

    last_error = None

    for path in candidate_paths:
        try:
            payload = await weex_private_get(
                session=session,
                path=path,
            )

            available = extract_available_asset(
                payload,
                "USDT",
            )

            if available is not None:
                return available

        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError(
        "AVAILABLE USDT NOT FOUND"
    )


def extract_available_asset(
    payload,
    asset_name,
):
    asset_name = (
        asset_name
        .strip()
        .upper()
    )

    def inspect(
        value,
    ):
        if isinstance(
            value,
            dict,
        ):
            symbol_value = first_present(
                value,
                [
                    "coin",
                    "asset",
                    "currency",
                    "symbol",
                ],
            )

            if (
                symbol_value
                is not None
                and str(
                    symbol_value
                ).upper()
                == asset_name
            ):
                available_value = first_present(
                    value,
                    [
                        "available",
                        "availableBalance",
                        "available_balance",
                        "free",
                    ],
                )

                candidate = decimal_or_none(
                    available_value
                )

                if candidate is not None:
                    return candidate

            for nested in value.values():
                found = inspect(
                    nested
                )

                if found is not None:
                    return found

        elif isinstance(
            value,
            list,
        ):
            for nested in value:
                found = inspect(
                    nested
                )

                if found is not None:
                    return found

        return None

    return inspect(
        payload
    )


# ============================================================
# POSITION READ
# ============================================================

async def fetch_positions(
    session,
):
    candidate_paths = [
        "/capi/v2/account/position",
        "/capi/v2/account/positions",
        "/capi/v3/account/position",
    ]

    last_error = None

    for path in candidate_paths:
        try:
            payload = await weex_private_get(
                session=session,
                path=path,
                params={
                    "symbol":
                        SYMBOL,
                },
            )

            positions = extract_positions(
                payload
            )

            return positions

        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError(
        "POSITION READ FAILED"
    )


def extract_positions(
    payload,
):
    positions = []

    def inspect(
        value,
    ):
        if isinstance(
            value,
            dict,
        ):
            symbol_value = first_present(
                value,
                [
                    "symbol",
                    "contractCode",
                    "contract_code",
                ],
            )

            quantity_value = first_present(
                value,
                [
                    "size",
                    "position",
                    "positionAmt",
                    "quantity",
                    "qty",
                ],
            )

            if (
                symbol_value
                is not None
                and quantity_value
                is not None
            ):
                quantity = decimal_or_none(
                    quantity_value
                )

                if quantity is not None:
                    positions.append(
                        {
                            "symbol":
                                str(
                                    symbol_value
                                ),

                            "quantity":
                                quantity,

                            "raw":
                                value,
                        }
                    )

            for nested in value.values():
                inspect(
                    nested
                )

        elif isinstance(
            value,
            list,
        ):
            for nested in value:
                inspect(
                    nested
                )

    inspect(
        payload
    )

    return positions


# ============================================================
# DEMO READ RECONCILIATION
# ============================================================

async def demo_private_get(
    session,
    path,
    params=None,
):
    headers, query_string, _ = (
        build_auth_headers(
            method="GET",
            path=path,
            params=params,
        )
    )

    url = (
        DEMO_API_BASE_URL
        + path
    )

    if query_string:
        url = (
            url
            + "?"
            + query_string
        )

    return await http_get_json(
        session=session,
        url=url,
        headers=headers,
    )


async def fetch_demo_available_balance(
    session,
):
    payload = await demo_private_get(
        session=session,
        path=DEMO_ACCOUNT_PATH,
    )

    available = extract_available_asset(
        payload,
        DEMO_ASSET,
    )

    if available is None:
        raise RuntimeError(
            f"DEMO {DEMO_ASSET} AVAILABLE BALANCE NOT FOUND"
        )

    return available


async def fetch_demo_positions(
    session,
):
    candidate_paths = [
        DEMO_POSITION_PATH,
        "/capi/v2/account/position",
        "/capi/v2/account/positions",
        "/capi/v3/account/position",
    ]

    last_error = None

    for path in candidate_paths:
        try:
            payload = await demo_private_get(
                session=session,
                path=path,
                params={
                    "symbol":
                        DEMO_SYMBOL,
                },
            )

            return extract_positions(
                payload
            )

        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError(
        "DEMO POSITION READ FAILED"
    )


async def fetch_demo_order_history(
    session,
):
    candidate_paths = [
        DEMO_HISTORY_PATH,
        "/capi/v3/order/history",
        "/capi/v2/order/history",
    ]

    last_error = None

    for path in candidate_paths:
        try:
            payload = await demo_private_get(
                session=session,
                path=path,
                params={
                    "symbol":
                        DEMO_SYMBOL,
                },
            )

            return payload

        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError(
        "DEMO ORDER HISTORY READ FAILED"
    )


def count_open_positions(
    positions,
):
    count = 0

    for position in positions:
        quantity = decimal_or_none(
            position.get(
                "quantity"
            )
        )

        if (
            quantity is not None
            and quantity != 0
        ):
            count += 1

    return count


def count_order_history_items(
    payload,
):
    if isinstance(
        payload,
        list,
    ):
        return len(
            payload
        )

    if isinstance(
        payload,
        dict,
    ):
        candidate_keys = [
            "data",
            "rows",
            "list",
            "orders",
        ]

        for key in candidate_keys:
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return len(
                    value
                )

            if isinstance(
                value,
                dict,
            ):
                for nested_key in candidate_keys:
                    nested = value.get(
                        nested_key
                    )

                    if isinstance(
                        nested,
                        list,
                    ):
                        return len(
                            nested
                        )

    return 0


# ============================================================
# QUANTITY ENGINE
# ============================================================

def calculate_entry_margin(
    available_balance,
):
    available_balance = D(
        available_balance
    )

    return (
        available_balance
        * ENTRY_MARGIN_PERCENT
        / Decimal("100")
    )


def calculate_entry_notional(
    available_balance,
    leverage,
):
    margin = calculate_entry_margin(
        available_balance
    )

    return (
        margin
        * D(
            leverage
        )
    )


def calculate_entry_quantity(
    available_balance,
    mark_price,
    leverage,
):
    notional = calculate_entry_notional(
        available_balance,
        leverage,
    )

    raw_quantity = (
        notional
        / D(
            mark_price
        )
    )

    return normalize_quantity(
        raw_quantity
    )


def writer_quantities(
    entry_quantity,
    tp1_allocation_percent=TP1_ALLOCATION_PERCENT,
    tp2_allocation_percent=TP2_ALLOCATION_PERCENT,
    tp3_allocation_percent=TP3_ALLOCATION_PERCENT,
):
    entry_quantity = D(
        entry_quantity
    )

    tp1_allocation_percent = D(
        tp1_allocation_percent
    )

    tp2_allocation_percent = D(
        tp2_allocation_percent
    )

    tp3_allocation_percent = D(
        tp3_allocation_percent
    )

    allocation_total = (
        tp1_allocation_percent
        + tp2_allocation_percent
        + tp3_allocation_percent
    )

    if (
        allocation_total
        != Decimal("100")
    ):
        return {
            "feasible":
                False,

            "reason":
                "TP_ALLOCATION_TOTAL_NOT_100",

            "entry_quantity":
                entry_quantity,

            "tp1_quantity":
                Decimal("0"),

            "tp2_quantity":
                Decimal("0"),

            "tp3_quantity":
                Decimal("0"),

            "allocation_total":
                allocation_total,
        }

    tp1_raw = (
        entry_quantity
        * tp1_allocation_percent
        / Decimal("100")
    )

    tp2_raw = (
        entry_quantity
        * tp2_allocation_percent
        / Decimal("100")
    )

    tp1_quantity = normalize_quantity(
        tp1_raw
    )

    tp2_quantity = normalize_quantity(
        tp2_raw
    )

    tp3_quantity = (
        entry_quantity
        - tp1_quantity
        - tp2_quantity
    )

    tp3_quantity = normalize_quantity(
        tp3_quantity
    )

    represented_total = (
        tp1_quantity
        + tp2_quantity
        + tp3_quantity
    )

    exact_total = (
        represented_total
        == entry_quantity
    )

    tp1_positive = (
        tp1_quantity
        >= MIN_QUANTITY
    )

    tp2_positive = (
        tp2_quantity
        >= MIN_QUANTITY
    )

    tp3_positive = (
        tp3_quantity
        >= MIN_QUANTITY
    )

    feasible = (
        exact_total
        and tp1_positive
        and tp2_positive
        and tp3_positive
    )

    reason = (
        "EXACTLY_REPRESENTABLE"
        if feasible
        else
        "POSITION_TOO_SMALL_OR_NOT_EXACTLY_REPRESENTABLE_FOR_TP_ALLOCATION"
    )

    return {
        "feasible":
            feasible,

        "reason":
            reason,

        "entry_quantity":
            entry_quantity,

        "tp1_quantity":
            tp1_quantity,

        "tp2_quantity":
            tp2_quantity,

        "tp3_quantity":
            tp3_quantity,

        "represented_total":
            represented_total,

        "allocation_total":
            allocation_total,

        "tp1_allocation_percent":
            tp1_allocation_percent,

        "tp2_allocation_percent":
            tp2_allocation_percent,

        "tp3_allocation_percent":
            tp3_allocation_percent,
    }


def minimum_strict_tp_entry_quantity():
    quantity = MIN_QUANTITY

    for _ in range(
        100000
    ):
        result = writer_quantities(
            quantity
        )

        if result[
            "feasible"
        ]:
            return quantity

        quantity = (
            quantity
            + QUANTITY_STEP
        )

    raise RuntimeError(
        "STRICT TP MINIMUM ENTRY QUANTITY NOT FOUND"
    )


def required_balance_for_entry_quantity(
    entry_quantity,
    mark_price,
    leverage,
):
    entry_quantity = D(
        entry_quantity
    )

    mark_price = D(
        mark_price
    )

    leverage = D(
        leverage
    )

    required_notional = (
        entry_quantity
        * mark_price
    )

    required_margin = (
        required_notional
        / leverage
    )

    required_available = (
        required_margin
        * Decimal("100")
        / ENTRY_MARGIN_PERCENT
    )

    return {
        "required_notional":
            required_notional,

        "required_margin":
            required_margin,

        "required_available":
            required_available,
    }


def balance_readiness(
    available_balance,
    mark_price,
    leverage,
):
    available_balance = D(
        available_balance
    )

    mark_price = D(
        mark_price
    )

    leverage = D(
        leverage
    )

    planned_entry_quantity = (
        calculate_entry_quantity(
            available_balance=available_balance,
            mark_price=mark_price,
            leverage=leverage,
        )
    )

    planned_writer = (
        writer_quantities(
            planned_entry_quantity
        )
    )

    minimum_quantity = (
        minimum_strict_tp_entry_quantity()
    )

    requirement = (
        required_balance_for_entry_quantity(
            entry_quantity=minimum_quantity,
            mark_price=mark_price,
            leverage=leverage,
        )
    )

    required_available = (
        requirement[
            "required_available"
        ]
    )

    shortfall = max(
        Decimal("0"),
        required_available
        - available_balance,
    )

    ready = (
        planned_writer[
            "feasible"
        ]
        and available_balance
        >= required_available
    )

    if ready:
        status = (
            "TRADE_ELIGIBLE"
        )

        reason = (
            "STRICT_TP_BALANCE_READY"
        )

    else:
        status = (
            "TRADE_NOT_ELIGIBLE"
        )

        reason = (
            "INSUFFICIENT_BALANCE_FOR_STRICT_TP_ALLOCATION"
        )

    return {
        "ready":
            ready,

        "status":
            status,

        "reason":
            reason,

        "available_balance":
            available_balance,

        "mark_price":
            mark_price,

        "leverage":
            leverage,

        "planned_entry_quantity":
            planned_entry_quantity,

        "planned_writer":
            planned_writer,

        "minimum_strict_tp_entry_quantity":
            minimum_quantity,

        "required_notional_for_minimum_quantity":
            requirement[
                "required_notional"
            ],

        "required_margin_for_minimum_quantity":
            requirement[
                "required_margin"
            ],

        "required_available_balance":
            required_available,

        "available_balance_shortfall":
            shortfall,
    }


# ============================================================
# ADJUSTABLE TP ALLOCATION TESTS
# ============================================================

def adjustable_tp_allocation_tests():
    results = []

    test_quantity = (
        Decimal("0.0004")
    )

    strict = writer_quantities(
        test_quantity,
        Decimal("20"),
        Decimal("20"),
        Decimal("60"),
    )

    alternative = writer_quantities(
        test_quantity,
        Decimal("25"),
        Decimal("25"),
        Decimal("50"),
    )

    checks = [
        (
            "STRICT_20_20_60_SMALL_QUANTITY_REJECTED",
            strict[
                "feasible"
            ]
            is False,
        ),
        (
            "ADJUSTABLE_25_25_50_SMALL_QUANTITY_APPROVED",
            alternative[
                "feasible"
            ]
            is True,
        ),
        (
            "ADJUSTABLE_TP_ALLOCATION_TOTAL_100",
            alternative[
                "allocation_total"
            ]
            == Decimal("100"),
        ),
        (
            "ADJUSTABLE_TP_QUANTITY_EXACT",
            alternative[
                "represented_total"
            ]
            == test_quantity,
        ),
    ]

    for (
        name,
        passed,
    ) in checks:
        if passed:
            diagnostic_pass(
                name
            )
        else:
            diagnostic_fail(
                name
            )

        results.append(
            passed
        )

    return all(
        results
    )


# ============================================================
# PROTECTIVE STOP
# ============================================================

PROTECTIVE_STOP_PERCENT = Decimal(
    os.getenv(
        "R36F13_PROTECTIVE_STOP_PERCENT",
        "0.5",
    )
)

MAX_STOP_LOSS_BALANCE_PERCENT = Decimal(
    os.getenv(
        "R36F13_MAX_STOP_LOSS_BALANCE_PERCENT",
        "1.0",
    )
)


def calculate_protective_stop(
    direction,
    entry_price,
):
    entry_price = D(
        entry_price
    )

    distance = (
        entry_price
        * PROTECTIVE_STOP_PERCENT
        / Decimal("100")
    )

    if direction == "LONG":
        stop = (
            entry_price
            - distance
        )

    elif direction == "SHORT":
        stop = (
            entry_price
            + distance
        )

    else:
        raise ValueError(
            f"INVALID DIRECTION: {direction}"
        )

    return normalize_price(
        stop
    )


def protective_stop_validation(
    direction,
    entry_price,
    stop_price,
    tp_snapshot,
):
    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    reasons = []

    if direction == "LONG":
        if not (
            stop_price
            < entry_price
        ):
            reasons.append(
                "LONG_STOP_NOT_BELOW_ENTRY"
            )

    elif direction == "SHORT":
        if not (
            stop_price
            > entry_price
        ):
            reasons.append(
                "SHORT_STOP_NOT_ABOVE_ENTRY"
            )

    else:
        reasons.append(
            "INVALID_DIRECTION"
        )

    tp1 = decimal_or_none(
        tp_snapshot.get(
            "tp1"
        )
    )

    tp2 = decimal_or_none(
        tp_snapshot.get(
            "tp2"
        )
    )

    if tp1 is not None:
        if (
            stop_price
            == tp1
        ):
            reasons.append(
                "STOP_EQUALS_TP1"
            )

    if tp2 is not None:
        if (
            stop_price
            == tp2
        ):
            reasons.append(
                "STOP_EQUALS_TP2"
            )

    valid = (
        len(
            reasons
        )
        == 0
    )

    return {
        "valid":
            valid,

        "direction":
            direction,

        "entry_price":
            entry_price,

        "stop_price":
            stop_price,

        "reasons":
            reasons,
    }


# ============================================================
# STOP RISK ENVELOPE
# ============================================================

def stop_risk_envelope(
    direction,
    entry_price,
    stop_price,
    entry_quantity,
):
    entry_price = D(
        entry_price
    )

    stop_price = D(
        stop_price
    )

    entry_quantity = D(
        entry_quantity
    )

    if direction == "LONG":
        distance = (
            entry_price
            - stop_price
        )

    elif direction == "SHORT":
        distance = (
            stop_price
            - entry_price
        )

    else:
        raise ValueError(
            f"INVALID DIRECTION: {direction}"
        )

    if distance < 0:
        distance = (
            -distance
        )

    loss_at_stop = (
        distance
        * entry_quantity
    )

    return {
        "direction":
            direction,

        "entry_price":
            entry_price,

        "stop_price":
            stop_price,

        "entry_quantity":
            entry_quantity,

        "price_distance":
            distance,

        "estimated_loss_at_stop":
            loss_at_stop,
    }


def stop_loss_budget(
    available_balance,
    estimated_loss_at_stop,
):
    available_balance = D(
        available_balance
    )

    estimated_loss_at_stop = D(
        estimated_loss_at_stop
    )

    maximum_loss = (
        available_balance
        * MAX_STOP_LOSS_BALANCE_PERCENT
        / Decimal("100")
    )

    within_budget = (
        estimated_loss_at_stop
        <= maximum_loss
    )

    return {
        "available_balance":
            available_balance,

        "maximum_stop_loss_balance_percent":
            MAX_STOP_LOSS_BALANCE_PERCENT,

        "maximum_loss":
            maximum_loss,

        "estimated_loss_at_stop":
            estimated_loss_at_stop,

        "within_budget":
            within_budget,
    }


# ============================================================
# BACKUP CONFIGURATION
# ============================================================

def backup_configuration():
    return {
        "max_backups":
            MAX_BACKUPS,

        "backup_margin_percent":
            BACKUP_MARGIN_PERCENT,

        "backup_buffer_percent":
            BACKUP_BUFFER_PERCENT,

        "backup_tp_recalculate_on_backup_fill_only":
            True,

        "primary_tp_immutable_after_fill":
            True,
    }


# ============================================================
# EMA + COMMAND VALIDATION
# ============================================================

def normalize_trade_command(
    command,
):
    command = (
        command
        .strip()
        .upper()
    )

    if command == "BUY BTC NOW":
        return "LONG"

    if command == "SELL BTC NOW":
        return "SHORT"

    return None


def command_validation(
    command,
    ema_snapshot,
    long_eligible,
    short_eligible,
):
    command_direction = (
        normalize_trade_command(
            command
        )
    )

    ideal_direction = (
        ema_snapshot.get(
            "ideal_direction"
        )
    )

    if command_direction is None:
        return {
            "valid":
                False,

            "reason":
                "NO_VALID_TRADE_COMMAND",

            "command_direction":
                None,

            "ideal_direction":
                ideal_direction,
        }

    if (
        command_direction
        != ideal_direction
    ):
        return {
            "valid":
                False,

            "reason":
                "COMMAND_DIRECTION_NOT_IDEAL_EMA_DIRECTION",

            "command_direction":
                command_direction,

            "ideal_direction":
                ideal_direction,
        }

    if (
        command_direction
        == "LONG"
        and not long_eligible
    ):
        return {
            "valid":
                False,

            "reason":
                "LONG_MARKET_NOT_ELIGIBLE",

            "command_direction":
                command_direction,

            "ideal_direction":
                ideal_direction,
        }

    if (
        command_direction
        == "SHORT"
        and not short_eligible
    ):
        return {
            "valid":
                False,

            "reason":
                "SHORT_MARKET_NOT_ELIGIBLE",

            "command_direction":
                command_direction,

            "ideal_direction":
                ideal_direction,
        }

    return {
        "valid":
            True,

        "reason":
            "COMMAND_MATCHES_IDEAL_DIRECTION_AND_MARKET_ELIGIBILITY",

        "command_direction":
            command_direction,

        "ideal_direction":
            ideal_direction,
    }


# ============================================================
# IDEAL CONDITION ALERT PAYLOAD
# ============================================================

def build_ideal_condition_alert(
    mark_price,
    ema_snapshot,
    long_eligible,
    short_eligible,
):
    ideal = (
        ema_snapshot.get(
            "ideal_direction"
        )
    )

    if ideal == "LONG":
        eligible = (
            long_eligible
        )

        command = (
            "BUY BTC NOW"
        )

    elif ideal == "SHORT":
        eligible = (
            short_eligible
        )

        command = (
            "SELL BTC NOW"
        )

    else:
        eligible = False
        command = None

    return {
        "stage":
            STAGE,

        "mark_price":
            mark_price,

        "ema19":
            ema_snapshot.get(
                "ema19"
            ),

        "ema50":
            ema_snapshot.get(
                "ema50"
            ),

        "ema200":
            ema_snapshot.get(
                "ema200"
            ),

        "ideal_direction":
            ideal,

        "market_eligible":
            eligible,

        "suggested_command":
            command,

        "telegram_alert_enabled":
            R36F12_TELEGRAM_ALERT_ENABLED,

        "ema_ideal_direction":
            ideal,

        "exchange_order_sent":
            False,
    }

