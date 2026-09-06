#!/usr/bin/env python3
"""
R36F.5.3 - READ-ONLY RECONCILIATION / FUNCTION-INTEGRITY CORRECTION

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5/R36F.5.2 safety baseline
    while correcting ONLY the remaining R36F.5.2 integration defects:

        1. Restore/retain all historical TP helper functions required by:
               - build_cluster_diagnostics
               - build_cluster_tp_snapshot
               - evaluate_tp_approval
               - load_historical_klines

        2. Correct WEEX read-only position reconciliation from:
               /capi/v3/account/position

           to:
               /capi/v3/account/position/singlePosition

           using:
               symbol=BTCUSDT

    ZERO exchange mutation is permitted.

R36F.5.3 TP POLICY:

    A complete historical TP1/TP2 set requires TWO OR MORE valid
    historical clusters.

    LONG:
        Cluster 1 = first valid historical-high resistance cluster
        Cluster 2 = second valid historical-high resistance cluster

        TP1 = adjustable 20% progress from entry toward Cluster 1 average
        TP2 = adjustable 50% progress from entry toward Cluster 2 average
        TP3 = 60% trailing runner

    SHORT:
        Cluster 1 = first valid historical-low support cluster
        Cluster 2 = second valid historical-low support cluster

        TP1 = adjustable 20% progress from entry toward Cluster 1 average
        TP2 = adjustable 50% progress from entry toward Cluster 2 average
        TP3 = 60% trailing runner

TP APPROVAL:

    TWO OR MORE valid clusters:
        APPROVED

    FEWER THAN TWO valid clusters:
        REJECTED

    One cluster does NOT separately approve TP1.

PRIMARY TP:
    Calculated and locked on primary fill.
    NEVER recalculated after primary fill.

BACKUP TP:
    Independently recalculated ONLY when backup fills.

R36F.5 DIAGNOSTIC-ONLY CHECKS REMAIN:

    - WEEX_READ_ONLY_RECONCILIATION
    - CANARY_PREVIEW
    - WRITER_REQUEST_CONSTRUCTION

SAFETY:

    REAL_ORDER_EXECUTION = False
    DEMO_ORDER_EXECUTION = False

    EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
    ORDER_SUBMISSION_ENABLED = False
    LEVERAGE_MUTATION_ENABLED = False
    MARGIN_MODE_MUTATION_ENABLED = False
    POSITION_MUTATION_ENABLED = False
    FIRST_REAL_ORDER_ALLOWED = False

NO REAL ORDER IS SENT.
NO DEMO ORDER IS SENT.
"""

import os
import json
import time
import hmac
import hashlib
import asyncio

from decimal import (
    Decimal,
    ROUND_DOWN,
)

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

import aiohttp

from aiohttp import web


# ============================================================
# STAGE
# ============================================================

STAGE = "R36F.5.3"

PURPOSE = (
    "READ-ONLY RECONCILIATION / FUNCTION-INTEGRITY CORRECTION "
    "WHILE PRESERVING THE R36F.5.2 TWO-CLUSTER TP POLICY "
    "AND ZERO-WRITE SAFETY BASELINE"
)


# ============================================================
# WEEX CONFIGURATION
# ============================================================

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = "BTCUSDT"

KLINE_INTERVAL = "1m"

HISTORICAL_LIMIT = 250

MAX_HISTORICAL_PAGES = 4

MAX_HISTORICAL_CANDLES = (
    HISTORICAL_LIMIT
    * MAX_HISTORICAL_PAGES
)


# ============================================================
# STRATEGY CONFIGURATION
# ============================================================

TARGET_MARGIN_MODE = "ISOLATED"

LEVERAGE_LONG = Decimal("100")

LEVERAGE_SHORT = Decimal("100")

ENTRY_MARGIN_PERCENT = Decimal("5")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

PRICE_STEP = Decimal("0.1")

QUANTITY_STEP = Decimal("0.0001")

MIN_QUANTITY = Decimal("0.0001")


# ============================================================
# TP CONFIGURATION
# ============================================================

REQUIRED_TP_CLUSTERS = 2

TP1_PROFIT_MARGIN_PERCENT = Decimal("20")

TP2_PROFIT_MARGIN_PERCENT = Decimal("50")

TP1_ALLOCATION_PERCENT = Decimal("20")

TP2_ALLOCATION_PERCENT = Decimal("20")

TP3_ALLOCATION_PERCENT = Decimal("60")

TP3_TRAILING_DISTANCE_PERCENT = Decimal("0.20")

MIN_CLUSTER_TOUCHES = 2

CLUSTER_TOLERANCE_PERCENT = Decimal("0.15")


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
# PERSISTENT STATE
# ============================================================

PERSISTENT_DISK_ROOT = Path(
    os.getenv(
        "PERSISTENT_DISK_ROOT",
        "/var/data",
    )
)

STATE_DIR = (
    PERSISTENT_DISK_ROOT
    / "r36f53_state"
)

STATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

R36A_STATE_DIR = (
    PERSISTENT_DISK_ROOT
    / "r36a_state"
)

R36C_STATE_DIR = (
    PERSISTENT_DISK_ROOT
    / "r36c_state"
)

R36D_STATE_DIR = (
    PERSISTENT_DISK_ROOT
    / "r36d_state"
)


# ============================================================
# DURABLE FILES
# ============================================================

R36A_DEDUPE_FILE = (
    R36A_STATE_DIR
    / "telegram_processed_updates.json"
)

R36A_DECISION_FILE = (
    R36A_STATE_DIR
    / "synthetic_decisions.json"
)

R36C_DEDUPE_FILE = (
    R36C_STATE_DIR
    / "telegram_processed_updates.json"
)

R36C_DECISION_FILE = (
    R36C_STATE_DIR
    / "synthetic_decisions.json"
)

R36D_SNAPSHOT_FILE = (
    R36D_STATE_DIR
    / "final_pre_live_snapshot.json"
)


# ============================================================
# DURABLE IDS
# ============================================================

OLD_R36A_UPDATE_ID = (
    "R36A_SYNTHETIC_UPDATE_000001"
)

R36C_UPDATE_ID = (
    "R36C_SYNTHETIC_UPDATE_000001"
)


# ============================================================
# GLOBAL STATE
# ============================================================

TEST_STATUS = "NOT_STARTED"

FINAL_GATE_OK = False

R36A_EVIDENCE_OK = False

R36C_EVIDENCE_OK = False

R36D_EVIDENCE_OK = False

DURABLE_EVIDENCE_OK = False

WEEX_READ_ONLY_OK = False

ZERO_WRITE_INVARIANT_OK = False

MARK_PRICE = None

AVAILABLE_BALANCE = None

OPEN_POSITIONS = []

LONG_DIAGNOSTICS = None

SHORT_DIAGNOSTICS = None

LAST_TP_APPROVAL = None

FINAL_BLOCKERS = []

DIAGNOSTIC_FAILURES = []


# ============================================================
# GENERAL UTILITIES
# ============================================================

def now_iso():

    return datetime.now(
        timezone.utc
    ).isoformat()


def line():

    print(
        "-" * 100,
        flush=True,
    )


def log(message):

    print(
        f"{now_iso()} {message}",
        flush=True,
    )


def check(
    name,
    condition,
    detail=None,
):

    condition = bool(condition)

    if condition:

        log(
            f"PASS: {name}"
        )

        return True

    if detail:

        log(
            f"FAIL: {name} | {detail}"
        )

    else:

        log(
            f"FAIL: {name}"
        )

    FINAL_BLOCKERS.append(
        name
    )

    return False


def diagnostic_check(
    name,
    condition,
    detail=None,
):

    condition = bool(condition)

    if condition:

        log(
            f"PASS: {name}"
        )

        return True

    if detail:

        log(
            f"DIAGNOSTIC FAIL: {name} | {detail}"
        )

    else:

        log(
            f"DIAGNOSTIC FAIL: {name}"
        )

    DIAGNOSTIC_FAILURES.append(
        name
    )

    return False


def D(value):

    if isinstance(
        value,
        Decimal,
    ):

        return value

    return Decimal(
        str(value)
    )


def decimal_to_string(value):

    if value is None:
        return None

    value = D(value)

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    return text


def quantize_down(
    value,
    step,
):

    value = D(value)

    step = D(step)

    if step <= 0:

        raise ValueError(
            "step must be positive"
        )

    units = (
        value
        / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        units
        * step
    )


def read_json_file(
    path,
    default=None,
):

    path = Path(path)

    if default is None:

        default = {}

    try:

        if not path.exists():

            return default

        with path.open(
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except Exception as exc:

        log(
            f"JSON READ FAILURE "
            f"{path}: {exc}"
        )

        return default


def collect_ids(
    obj,
):

    found = set()

    def walk(value):

        if isinstance(
            value,
            dict,
        ):

            for key, item in value.items():

                key_lower = str(
                    key
                ).lower()

                if (
                    "update" in key_lower
                    and "id" in key_lower
                ):

                    if isinstance(
                        item,
                        (
                            str,
                            int,
                        ),
                    ):

                        found.add(
                            str(item)
                        )

                walk(item)

        elif isinstance(
            value,
            list,
        ):

            for item in value:

                walk(item)

        elif isinstance(
            value,
            str,
        ):

            if (
                "R36" in value
                and "UPDATE" in value
            ):

                found.add(value)

    walk(obj)

    return found


def collect_ids_from_file(
    path,
):

    payload = read_json_file(
        path,
        {},
    )

    return collect_ids(
        payload
    )


# ============================================================
# HEALTH SERVER BOOTSTRAP
# ============================================================

async def simple_health_handler(
    request,
):

    return web.json_response({

        "stage":
            STAGE,

        "status":
            TEST_STATUS,

        "final_gate_ok":
            FINAL_GATE_OK,

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "demo_order_execution":
            DEMO_ORDER_EXECUTION,

    })


async def start_initial_health_server():

    app = web.Application()

    app.router.add_get(
        "/",
        simple_health_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port,
    )

    await site.start()

    log(
        f"{STAGE}: HEALTH SERVER STARTED "
        f"ON PORT {port}"
    )

    return runner


# ============================================================
# WEEX AUTHENTICATION
# ============================================================

def weex_credentials():

    api_key = os.getenv(
        "WEEX_API_KEY",
        "",
    )

    api_secret = os.getenv(
        "WEEX_API_SECRET",
        "",
    )

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE",
        "",
    )

    return (
        api_key,
        api_secret,
        passphrase,
    )


def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):

    (
        api_key,
        api_secret,
        passphrase,
    ) = weex_credentials()

    del api_key
    del passphrase

    if query_string:

        sign_path = (
            request_path
            + "?"
            + query_string
        )

    else:

        sign_path = request_path

    prehash = (
        str(timestamp)
        + method.upper()
        + sign_path
        + body
    )

    signature = hmac.new(
        api_secret.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()

    return signature


def build_auth_headers(
    method,
    request_path,
    query_string="",
    body="",
):

    (
        api_key,
        api_secret,
        passphrase,
    ) = weex_credentials()

    if not api_key:
        raise RuntimeError(
            "WEEX_API_KEY missing"
        )

    if not api_secret:
        raise RuntimeError(
            "WEEX_API_SECRET missing"
        )

    if not passphrase:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing"
        )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = build_signature(
        timestamp,
        method,
        request_path,
        query_string,
        body,
    )

    return {

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

        "locale":
            "en-US",
    }


# ============================================================
# READ-ONLY HTTP
# ============================================================

async def http_get_json(
    session,
    url,
    params=None,
    headers=None,
):

    async with session.get(
        url,
        params=params,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"HTTP {response.status}: "
                f"{text[:500]}"
            )

        try:

            return json.loads(text)

        except Exception:

            raise RuntimeError(
                "Invalid JSON response: "
                + text[:500]
            )


async def private_get(
    session,
    request_path,
    params=None,
):

    params = params or {}

    query_string = "&".join(
        f"{key}={value}"
        for key, value in params.items()
    )

    headers = build_auth_headers(
        "GET",
        request_path,
        query_string,
        "",
    )

    url = (
        API_BASE_URL
        + request_path
    )

    return await http_get_json(
        session,
        url,
        params=params,
        headers=headers,
    )


# ============================================================
# PUBLIC MARK PRICE
# ============================================================

def extract_mark_price(
    payload,
):

    candidates = []

    if isinstance(
        payload,
        dict,
    ):

        candidates.append(payload)

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
                item
                for item in data
                if isinstance(
                    item,
                    dict,
                )
            )

    elif isinstance(
        payload,
        list,
    ):

        candidates.extend(
            item
            for item in payload
            if isinstance(
                item,
                dict,
            )
        )

    for item in candidates:

        for key in (
            "markPrice",
            "mark_price",
            "price",
            "last",
            "lastPrice",
        ):

            if key in item:

                value = item.get(
                    key
                )

                if value not in (
                    None,
                    "",
                ):

                    return D(value)

    raise RuntimeError(
        "Unable to extract mark price"
    )


async def public_ticker():

    candidates = [

        (
            "/capi/v2/market/ticker",
            {
                "symbol":
                    "cmt_btcusdt"
            },
        ),

        (
            "/capi/v3/market/ticker",
            {
                "symbol":
                    SYMBOL
            },
        ),
    ]

    last_error = None

    async with aiohttp.ClientSession() as session:

        for (
            request_path,
            params,
        ) in candidates:

            try:

                payload = (
                    await http_get_json(
                        session,
                        API_BASE_URL
                        + request_path,
                        params=params,
                    )
                )

                return payload

            except Exception as exc:

                last_error = exc

    raise RuntimeError(
        f"Public ticker failed: "
        f"{last_error}"
    )


async def read_mark_price():

    payload = await public_ticker()

    mark_price = extract_mark_price(
        payload
    )

    log(
        f"WEEX MARK PRICE = "
        f"{decimal_to_string(mark_price)}"
    )

    return mark_price


# ============================================================
# READ-ONLY ACCOUNT EXTRACTION
# ============================================================

def recursive_dicts(
    obj,
):

    result = []

    if isinstance(
        obj,
        dict,
    ):

        result.append(obj)

        for value in obj.values():

            result.extend(
                recursive_dicts(
                    value
                )
            )

    elif isinstance(
        obj,
        list,
    ):

        for value in obj:

            result.extend(
                recursive_dicts(
                    value
                )
            )

    return result


def extract_available_balance(
    payload,
):

    for item in recursive_dicts(
        payload
    ):

        for key in (
            "available",
            "availableBalance",
            "available_balance",
            "availableEquity",
            "availableEquityValue",
        ):

            if key in item:

                value = item.get(
                    key
                )

                try:

                    return D(value)

                except Exception:

                    continue

    raise RuntimeError(
        "Unable to extract available USDT balance"
    )


def extract_positions(
    payload,
):

    positions = []

    for item in recursive_dicts(
        payload
    ):

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if (
            symbol
            and symbol != SYMBOL
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

            if key in item:

                try:

                    quantity = D(
                        item.get(
                            key
                        )
                    )

                except Exception:

                    quantity = None

                break

        if (
            quantity is not None
            and quantity != 0
        ):

            positions.append(
                item
            )

    return positions


def extract_margin_mode(
    payload,
):

    for item in recursive_dicts(
        payload
    ):

        for key in (
            "marginMode",
            "margin_mode",
            "marginType",
        ):

            if key in item:

                value = item.get(
                    key
                )

                if value:

                    return str(
                        value
                    ).upper()

    return None


def extract_leverages(
    payload,
):

    long_leverage = None

    short_leverage = None

    for item in recursive_dicts(
        payload
    ):

        if long_leverage is None:

            for key in (
                "isolatedLong",
                "longLeverage",
                "long_leverage",
            ):

                if key in item:

                    try:

                        long_leverage = D(
                            item.get(
                                key
                            )
                        )

                    except Exception:

                        pass

                    break

        if short_leverage is None:

            for key in (
                "isolatedShort",
                "shortLeverage",
                "short_leverage",
            ):

                if key in item:

                    try:

                        short_leverage = D(
                            item.get(
                                key
                            )
                        )

                    except Exception:

                        pass

                    break

    return (
        long_leverage,
        short_leverage,
    )


# ============================================================
# ABSOLUTE WRITE FIREBREAK
# ============================================================

async def forbidden_exchange_mutation(
    *args,
    **kwargs,
):

    del args
    del kwargs

    raise RuntimeError(
        "EXCHANGE MUTATION TRANSPORT "
        "IS HARD DISABLED"
    )


submit_order = forbidden_exchange_mutation

cancel_order = forbidden_exchange_mutation

modify_order = forbidden_exchange_mutation

change_leverage = forbidden_exchange_mutation

change_margin_mode = forbidden_exchange_mutation

change_position_mode = forbidden_exchange_mutation


# ============================================================
# WEEX READ-ONLY RECONCILIATION
# ============================================================

async def reconcile_weex():

    global MARK_PRICE
    global AVAILABLE_BALANCE
    global OPEN_POSITIONS

    MARK_PRICE = (
        await read_mark_price()
    )

    balance_path = (
        "/capi/v3/account/assets"
    )

    position_path = (
        "/capi/v3/account/position/singlePosition"
    )

    symbol_config_path = (
        "/capi/v3/account/symbolConfig"
    )

    async with aiohttp.ClientSession() as session:

        balance_payload = (
            await private_get(
                session,
                balance_path,
            )
        )

        AVAILABLE_BALANCE = (
            extract_available_balance(
                balance_payload
            )
        )

        log(
            "AVAILABLE USDT = "
            + decimal_to_string(
                AVAILABLE_BALANCE
            )
        )

        position_payload = (
            await private_get(
                session,
                position_path,
                {
                    "symbol":
                        SYMBOL
                },
            )
        )

        OPEN_POSITIONS = (
            extract_positions(
                position_payload
            )
        )

        log(
            f"OPEN BTCUSDT POSITIONS = "
            f"{len(OPEN_POSITIONS)}"
        )

        config_payload = (
            await private_get(
                session,
                symbol_config_path,
                {
                    "symbol":
                        SYMBOL
                },
            )
        )

        margin_mode = (
            extract_margin_mode(
                config_payload
            )
        )

        (
            long_leverage,
            short_leverage,
        ) = extract_leverages(
            config_payload
        )

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

        if OPEN_POSITIONS:

            raise RuntimeError(
                "BTCUSDT_NOT_FLAT"
            )

        if (
            margin_mode is not None
            and margin_mode
            != TARGET_MARGIN_MODE
        ):

            raise RuntimeError(
                f"MARGIN_MODE_MISMATCH: "
                f"{margin_mode}"
            )

        if (
            long_leverage is not None
            and long_leverage
            != LEVERAGE_LONG
        ):

            raise RuntimeError(
                "LONG_LEVERAGE_MISMATCH: "
                + decimal_to_string(
                    long_leverage
                )
            )

        if (
            short_leverage is not None
            and short_leverage
            != LEVERAGE_SHORT
        ):

            raise RuntimeError(
                "SHORT_LEVERAGE_MISMATCH: "
                + decimal_to_string(
                    short_leverage
                )
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

        "raw_quantity":
            decimal_to_string(
                raw_quantity
            ),

        "normalized_quantity":
            decimal_to_string(
                quantity
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


# END PART 1
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

            start_timestamp = (
                oldest_ts - 1
            )

            if len(rows) < HISTORICAL_LIMIT:
                break

    result = normalize_kline_order(
        list(all_rows.values())
    )

    if (
        len(result)
        > MAX_HISTORICAL_CANDLES
    ):

        result = result[
            -MAX_HISTORICAL_CANDLES:
        ]

    log(
        "HISTORICAL KLINES LOADED = "
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
            kline_high_low(row)
        )

        highs.append(high)

        lows.append(low)

    if side == "LONG":

        for i in range(
            1,
            len(highs) - 1,
        ):

            if (
                highs[i]
                >= highs[i - 1]
                and highs[i]
                >= highs[i + 1]
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
                lows[i]
                <= lows[i - 1]
                and lows[i]
                <= lows[i + 1]
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

    clusters = cluster_extrema(
        extrema
    )

    cluster_records = []

    valid_clusters = []

    for index, cluster in enumerate(
        clusters,
        start=1,
    ):

        average = (
            cluster[
                "average"
            ]
        )

        touches = (
            cluster[
                "touches"
            ]
        )

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
            "EXTREMA_EXIST_BUT_"
            "CLUSTER_REQUIREMENTS_NOT_MET"
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
        f"{side} HISTORICAL "
        f"EXTREMA COUNT = "
        f"{len(extrema)}"
    )

    log(
        f"{side} HISTORICAL "
        f"CLUSTER COUNT = "
        f"{len(clusters)}"
    )

    log(
        f"{side} VALID "
        f"CLUSTER COUNT = "
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
        f"{side} CLUSTER "
        f"DIAGNOSTIC STATUS = "
        f"{status}"
    )

    log(
        f"{side} CLUSTER "
        f"DIAGNOSTIC FAILURE_REASON = "
        f"{failure_reason}"
    )

    return diagnostics


# ============================================================
# TP APPROVAL
# ============================================================

def evaluate_tp_approval(
    diagnostics,
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
                "TWO_OR_MORE_VALID_"
                "HISTORICAL_CLUSTERS",
        }

    else:

        failure_reason = (
            diagnostics.get(
                "failure_reason"
            )
        )

        if not failure_reason:

            failure_reason = (
                "FEWER_THAN_TWO_VALID_"
                "HISTORICAL_CLUSTERS"
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
            cluster[
                "touches"
            ]
            < MIN_CLUSTER_TOUCHES
        ):

            continue

        average = (
            cluster[
                "average"
            ]
        )

        if side == "LONG":

            if (
                average
                <= entry_price
            ):

                continue

        elif side == "SHORT":

            if (
                average
                >= entry_price
            ):

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
            f"{side} historical TP set "
            f"rejected: requires at least "
            f"{REQUIRED_TP_CLUSTERS} "
            f"valid clusters; found "
            f"{approval['available_valid_clusters']}"
        )

    clusters = valid_clusters(
        rows,
        entry_price,
        side,
    )

    if (
        len(clusters)
        < REQUIRED_TP_CLUSTERS
    ):

        raise RuntimeError(
            "TP approval inconsistency: "
            "diagnostics approved but "
            "independent cluster extraction "
            "found fewer than two "
            "valid clusters"
        )

    cluster_1 = (
        clusters[0]
    )

    cluster_2 = (
        clusters[1]
    )

    cluster_1_avg = (
        cluster_1[
            "average"
        ]
    )

    cluster_2_avg = (
        cluster_2[
            "average"
        ]
    )

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
            "HISTORICAL_CLUSTER_TP_R36F5_3",

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
        f"{side} TP3 = "
        f"60% trailing runner"
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

        rows.append([
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
        ])

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

        rows.append([
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
        ])

    return rows


# ============================================================
# SYNTHETIC CLUSTER TESTS
# ============================================================

def synthetic_cluster_tests():

    entry = Decimal(
        "100000"
    )

    # --------------------------------------------------------
    # LONG
    # --------------------------------------------------------

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
        ]
        >= REQUIRED_TP_CLUSTERS,

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
        ]
        >= REQUIRED_TP_CLUSTERS,
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
        ]
        >= REQUIRED_TP_CLUSTERS,

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
        ]
        >= REQUIRED_TP_CLUSTERS,
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
        ]
        == REQUIRED_TP_CLUSTERS,

        (
            "synthetic short fixture "
            "must deterministically produce exactly "
            + str(
                REQUIRED_TP_CLUSTERS
            )
            + " valid clusters"
        ),
    )

    # --------------------------------------------------------
    # IMMUTABILITY CONTRACTS
    # --------------------------------------------------------

    check(
        "PRIMARY_TP_IMMUTABLE_CONTRACT",

        (
            long_snapshot[
                "primary_tp_immutable"
            ]
            is True

            and

            short_snapshot[
                "primary_tp_immutable"
            ]
            is True
        ),
    )

    check(
        "BACKUP_TP_RECALC_CONTRACT",

        (
            long_snapshot[
                "backup_tp_recalculated_only_on_backup_fill"
            ]
            is True

            and

            short_snapshot[
                "backup_tp_recalculated_only_on_backup_fill"
            ]
            is True
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

    entry = Decimal(
        "100000"
    )

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
        ]
        is False,
    )

    check(
        "ONE_CLUSTER_APPROVAL_STATUS_REJECTED",

        approval[
            "status"
        ]
        == "REJECTED",
    )

    check(
        "ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET",

        approval[
            "available_valid_clusters"
        ]
        < REQUIRED_TP_CLUSTERS,
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
        f"{STAGE}: "
        f"{PURPOSE}"
    )

    line()

    # ========================================================
    # EXECUTION FIREBREAK TESTS
    # ========================================================

    check(
        "REAL_ORDER_EXECUTION_DISABLED",

        REAL_ORDER_EXECUTION
        is False,
    )

    check(
        "DEMO_ORDER_EXECUTION_DISABLED",

        DEMO_ORDER_EXECUTION
        is False,
    )

    check(
        "EXCHANGE_MUTATION_TRANSPORT_DISABLED",

        EXCHANGE_MUTATION_TRANSPORT_ENABLED
        is False,
    )

    check(
        "ORDER_SUBMISSION_DISABLED",

        ORDER_SUBMISSION_ENABLED
        is False,
    )

    check(
        "LEVERAGE_MUTATION_DISABLED",

        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "MARGIN_MODE_MUTATION_DISABLED",

        MARGIN_MODE_MUTATION_ENABLED
        is False,
    )

    check(
        "POSITION_MUTATION_DISABLED",

        POSITION_MUTATION_ENABLED
        is False,
    )

    check(
        "FIRST_REAL_ORDER_DISABLED",

        FIRST_REAL_ORDER_ALLOWED
        is False,
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

        (
            f"expected="
            f"{OLD_R36A_UPDATE_ID}"
        ),
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

        (
            f"expected="
            f"{R36C_UPDATE_ID}"
        ),
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
    # WEEX READ-ONLY RECONCILIATION
    # DIAGNOSTIC ONLY
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
            ]
            is False,
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
            )
            >= 3,

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
    # ========================================================

    real_long_snapshot = None

    if (
        historical_rows
        and MARK_PRICE
        is not None
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
                ]
                is True,

                (
                    "TP_APPROVAL="
                    + real_long_snapshot[
                        "tp_approval"
                    ][
                        "status"
                    ]
                ),
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

                (
                    "TP_APPROVAL="
                    + approval[
                        "status"
                    ]
                    + " reason="
                    + approval[
                        "reason"
                    ]
                    + " error="
                    + str(exc)
                ),
            )

    # ========================================================
    # REAL SHORT TP PREVIEW
    # ========================================================

    real_short_snapshot = None

    if (
        historical_rows
        and MARK_PRICE
        is not None
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
                ]
                is True,

                (
                    "TP_APPROVAL="
                    + real_short_snapshot[
                        "tp_approval"
                    ][
                        "status"
                    ]
                ),
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

                (
                    "TP_APPROVAL="
                    + approval[
                        "status"
                    ]
                    + " reason="
                    + approval[
                        "reason"
                    ]
                    + " error="
                    + str(exc)
                ),
            )

    # ========================================================
    # CANARY PREVIEW
    # DIAGNOSTIC ONLY
    # ========================================================

    canary_preview = None

    try:

        canary_preview = (
            build_canary_preview()
        )

        diagnostic_check(
            "CANARY_PREVIEW",

            True,

            json.dumps(
                canary_preview,
                sort_keys=True,
            ),
        )

    except Exception as exc:

        diagnostic_check(
            "CANARY_PREVIEW",

            False,

            str(exc),
        )

    # ========================================================
    # WRITER REQUEST CONSTRUCTION
    # DIAGNOSTIC ONLY
    # ========================================================

    writer_preview = None

    try:

        if (
            real_long_snapshot
            is None
        ):

            raise RuntimeError(
                "real long TP snapshot unavailable"
            )

        if MARK_PRICE is None:

            raise RuntimeError(
                "mark price unavailable"
            )

        if (
            AVAILABLE_BALANCE
            is None
        ):

            raise RuntimeError(
                "available balance unavailable"
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
            notional
            / MARK_PRICE,

            QUANTITY_STEP,
        )

        if (
            quantity
            < MIN_QUANTITY
        ):

            raise RuntimeError(
                "writer preview quantity below minimum"
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

            True,

            json.dumps(
                writer_preview,
                sort_keys=True,
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

    ZERO_WRITE_INVARIANT_OK = (

        REAL_ORDER_EXECUTION
        is False

        and DEMO_ORDER_EXECUTION
        is False

        and EXCHANGE_MUTATION_TRANSPORT_ENABLED
        is False

        and ORDER_SUBMISSION_ENABLED
        is False

        and LEVERAGE_MUTATION_ENABLED
        is False

        and MARGIN_MODE_MUTATION_ENABLED
        is False

        and POSITION_MUTATION_ENABLED
        is False

        and FIRST_REAL_ORDER_ALLOWED
        is False
    )

    check(
        "ZERO_WRITE_INVARIANTS",

        ZERO_WRITE_INVARIANT_OK,
    )

    # ========================================================
    # FINAL GATE
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

    line()

    log(
        f"{STAGE} FINAL TEST STATUS = "
        f"{TEST_STATUS}"
    )

    log(
        f"{STAGE} FINAL_GATE_OK = "
        f"{FINAL_GATE_OK}"
    )

    log(
        f"{STAGE} FINAL_BLOCKERS = "
        f"{FINAL_BLOCKERS}"
    )

    log(
        f"{STAGE} DIAGNOSTIC_FAILURES = "
        f"{DIAGNOSTIC_FAILURES}"
    )

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO DEMO ORDER WAS SENT"
    )

    line()

    return FINAL_GATE_OK


# ============================================================
# HEALTH ENDPOINT
# ============================================================

async def health_handler(
    request,
):

    return web.json_response({

        "stage":
            STAGE,

        "status":
            TEST_STATUS,

        "final_gate_ok":
            FINAL_GATE_OK,

        "final_blockers":
            FINAL_BLOCKERS,

        "diagnostic_failures":
            DIAGNOSTIC_FAILURES,

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

        "mark_price":
            (
                decimal_to_string(
                    MARK_PRICE
                )
                if MARK_PRICE
                is not None
                else None
            ),

        "available_balance":
            (
                decimal_to_string(
                    AVAILABLE_BALANCE
                )
                if AVAILABLE_BALANCE
                is not None
                else None
            ),

        "open_positions":
            len(
                OPEN_POSITIONS
            ),

        "weex_read_only_ok":
            WEEX_READ_ONLY_OK,

        "zero_write_invariant_ok":
            ZERO_WRITE_INVARIANT_OK,

        "r36a_evidence_ok":
            R36A_EVIDENCE_OK,

        "r36c_evidence_ok":
            R36C_EVIDENCE_OK,

        "r36d_evidence_ok":
            R36D_EVIDENCE_OK,

        "durable_evidence_ok":
            DURABLE_EVIDENCE_OK,

        "long_valid_cluster_count":
            (
                LONG_DIAGNOSTICS.get(
                    "valid_cluster_count"
                )
                if LONG_DIAGNOSTICS
                else None
            ),

        "short_valid_cluster_count":
            (
                SHORT_DIAGNOSTICS.get(
                    "valid_cluster_count"
                )
                if SHORT_DIAGNOSTICS
                else None
            ),
    })


# ============================================================
# FINAL HEALTH SERVER
# ============================================================

async def start_health_server():

    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port,
    )

    await site.start()

    log(
        f"{STAGE}: "
        f"HEALTH SERVER STARTED "
        f"ON PORT {port}"
    )

    return runner


# ============================================================
# ENTRYPOINT
# ============================================================

async def main():

    await start_health_server()

    try:

        await run_r36f53()

    except Exception as exc:

        global TEST_STATUS

        global FINAL_GATE_OK

        TEST_STATUS = "FAIL"

        FINAL_GATE_OK = False

        line()

        log(
            f"{STAGE} "
            f"UNHANDLED TEST FAILURE = "
            f"{exc}"
        )

        log(
            "NO REAL ORDER WAS SENT"
        )

        log(
            "NO DEMO ORDER WAS SENT"
        )

        line()


if __name__ == "__main__":

    asyncio.run(
        main()
    )


# END PART 2
