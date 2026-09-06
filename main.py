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
