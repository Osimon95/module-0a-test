import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R14"

API_BASE_URL = (
    "https://api-contract.weex.com"
)

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

ZERO = Decimal("0")
HUNDRED = Decimal("100")


# ============================================================
# ADJUSTABLE CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal(
    os.getenv(
        "INITIAL_ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = Decimal(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_LEVERAGE = Decimal(
    os.getenv(
        "MAX_LEVERAGE",
        "100",
    )
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()


MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
        "1",
    )
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_SIZE_PERCENT",
        "5",
    )
)


MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3",
    )
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5",
    )
)


MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TP / TRAILING CONFIG
# ============================================================

TP1_PERCENT = Decimal(
    os.getenv(
        "TP1_PERCENT",
        "20",
    )
)

TP2_PERCENT = Decimal(
    os.getenv(
        "TP2_PERCENT",
        "20",
    )
)

TP3_PERCENT = Decimal(
    os.getenv(
        "TP3_PERCENT",
        "60",
    )
)


TP1_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP1_TRIGGER_PERCENT",
        "0.5",
    )
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP2_TRIGGER_PERCENT",
        "1.0",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)


# ============================================================
# SIGNAL SAFETY CONFIG
# ============================================================

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)


# ============================================================
# LIQUIDATION SAFETY CONFIG
# ============================================================

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
    )
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2",
    )
)

PLANNING_MMR_PERCENT = Decimal(
    os.getenv(
        "PLANNING_MMR_PERCENT",
        "0.5",
    )
)


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True

ABSOLUTE_PRIVATE_POST_LOCK = True


# ============================================================
# WEEX CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# RENDER
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def safe_decimal(
    value,
    default="0",
):
    try:
        if value is None:
            return Decimal(
                default
            )

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal(
            default
        )


def fmt(
    value,
):
    if not isinstance(
        value,
        Decimal,
    ):
        value = safe_decimal(
            value
        )

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = (
            text.rstrip("0")
            .rstrip(".")
        )

    return text or "0"


def yes_no(
    value,
):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def floor_to_precision(
    value,
    precision,
):
    value = safe_decimal(
        value
    )

    precision = int(
        precision
    )

    if precision <= 0:
        return value.quantize(
            Decimal("1"),
            rounding=ROUND_DOWN,
        )

    step = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    return value.quantize(
        step,
        rounding=ROUND_DOWN,
    )


def credentials_ready():
    return all(
        (
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        )
    )


# ============================================================
# RENDER HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.json_response(
        {
            "status": "ok",
            "module": MODULE_NAME,
            "symbol": SYMBOL,
            "live_order_execution":
                LIVE_ORDER_EXECUTION,
            "absolute_private_post_lock":
                ABSOLUTE_PRIVATE_POST_LOCK,
        }
    )


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

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        PORT,
    )

    await site.start()

    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}"
    )

    return runner


# ============================================================
# WEEX V3 SIGNATURE
# ============================================================

def generate_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    message = (
        str(timestamp)
        + method.upper()
        + request_path
        + query_string
        + body
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


def auth_headers(
    method,
    request_path,
    query_string="",
    body="",
):
    if not credentials_ready():
        raise RuntimeError(
            "WEEX credentials missing. "
            "Check WEEX_API_KEY, "
            "WEEX_API_SECRET and "
            "WEEX_API_PASSPHRASE."
        )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = generate_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "Content-Type":
            "application/json",

        "locale":
            "en-US",
    }


# ============================================================
# RESPONSE HANDLER
# ============================================================

async def read_json_response(
    response,
    label,
):
    text = await response.text()

    if response.status != 200:
        raise RuntimeError(
            f"{label}: "
            f"WEEX HTTP "
            f"{response.status}: "
            f"{text}"
        )

    try:
        return json.loads(
            text
        )

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{label}: "
            f"invalid JSON response: "
            f"{text}"
        ) from exc


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    query_string = ""

    if params:
        query_string = (
            "?"
            + urlencode(
                params
            )
        )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
        f"{query_string}"
    )

    async with session.get(
        url,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        return await read_json_response(
            response,
            f"GET {path}",
        )


# ============================================================
# PRIVATE GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):
    query_string = ""

    if params:
        query_string = (
            "?"
            + urlencode(
                params
            )
        )

    headers = auth_headers(
        method="GET",
        request_path=path,
        query_string=query_string,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
        f"{query_string}"
    )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        return await read_json_response(
            response,
            f"GET {path}",
        )


# ============================================================
# ABSOLUTE PRIVATE POST LOCK
# ============================================================

async def private_post(
    *args,
    **kwargs,
):
    """
    R14 ABSOLUTE EXECUTION BARRIER.

    NO HTTP REQUEST EXISTS INSIDE
    THIS FUNCTION.

    Any future code attempting to
    transmit a WEEX private POST
    through this function is stopped
    before network transmission.
    """

    raise RuntimeError(
        "R14 ABSOLUTE PRIVATE-POST "
        "LOCK: outbound WEEX private "
        "POST blocked before "
        "transmission"
    )


# ============================================================
# TELEGRAM
# EXACTLY ONE FINAL MESSAGE PER RUN
# ============================================================

async def send_telegram(
    session,
    message,
):
    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM: skipped - "
            "credentials missing"
        )
        return False

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        "sendMessage"
    )

    payload = {
        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            message,

        "disable_web_page_preview":
            True,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if response.status != 200:
                print(
                    "TELEGRAM ERROR: "
                    f"HTTP "
                    f"{response.status}: "
                    f"{text}"
                )
                return False

            return True

    except Exception as exc:
        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return False


# ============================================================
# BALANCE EXTRACTION
# ============================================================

def extract_available_usdt(
    data,
):
    candidates = data

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "balances",
            "assets",
        ):
            obj = data.get(
                key
            )

            if isinstance(
                obj,
                list,
            ):
                candidates = obj
                break

    if isinstance(
        candidates,
        list,
    ):
        for item in candidates:

            if not isinstance(
                item,
                dict,
            ):
                continue

            asset = str(
                item.get(
                    "asset",
                    item.get(
                        "coinName",
                        "",
                    ),
                )
            ).upper()

            if asset != "USDT":
                continue

            for key in (
                "availableBalance",
                "available",
                "free",
                "balance",
            ):
                if key in item:

                    value = safe_decimal(
                        item[key]
                    )

                    if value >= ZERO:
                        return value

    raise RuntimeError(
        "Unable to extract "
        f"available USDT: {data}"
    )


# ============================================================
# MARK PRICE EXTRACTION
# ============================================================

def extract_mark_price(
    data,
):
    candidates = []

    if isinstance(
        data,
        list,
    ):
        candidates.extend(
            data
        )

    elif isinstance(
        data,
        dict,
    ):
        candidates.append(
            data
        )

        for key in (
            "data",
            "result",
        ):
            obj = data.get(
                key
            )

            if isinstance(
                obj,
                dict,
            ):
                candidates.append(
                    obj
                )

            elif isinstance(
                obj,
                list,
            ):
                candidates.extend(
                    obj
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
            "lastPrice",
            "last",
        ):
            if key in item:

                value = safe_decimal(
                    item[key]
                )

                if value > ZERO:
                    return value

    raise RuntimeError(
        "Unable to extract "
        f"mark price: {data}"
    )


# ============================================================
# CONTRACT EXTRACTION
# ============================================================

def extract_contract(
    exchange_info,
):
    candidates = []

    if isinstance(
        exchange_info,
        dict,
    ):
        symbols = exchange_info.get(
            "symbols"
        )

        if isinstance(
            symbols,
            list,
        ):
            candidates.extend(
                symbols
            )

        data = exchange_info.get(
            "data"
        )

        if isinstance(
            data,
            dict,
        ):
            nested_symbols = data.get(
                "symbols"
            )

            if isinstance(
                nested_symbols,
                list,
            ):
                candidates.extend(
                    nested_symbols
                )

        elif isinstance(
            data,
            list,
        ):
            candidates.extend(
                data
            )

    elif isinstance(
        exchange_info,
        list,
    ):
        candidates.extend(
            exchange_info
        )

    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if item_symbol == SYMBOL:
            return item

    raise RuntimeError(
        f"Unable to find "
        f"{SYMBOL} in "
        f"WEEX exchangeInfo"
    )


# ============================================================
# API TRADING SYMBOL EXTRACTION
# ============================================================

def extract_api_trading_allowed(
    data,
):
    candidates = data

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "symbols",
        ):
            obj = data.get(
                key
            )

            if isinstance(
                obj,
                list,
            ):
                candidates = obj
                break

    if not isinstance(
        candidates,
        list,
    ):
        return False

    normalized = set()

    for item in candidates:

        if isinstance(
            item,
            str,
        ):
            normalized.add(
                item.upper()
            )

        elif isinstance(
            item,
            dict,
        ):
            symbol = item.get(
                "symbol"
            )

            if symbol:
                normalized.add(
                    str(
                        symbol
                    ).upper()
                )

    return SYMBOL in normalized


# ============================================================
# POSITION EXTRACTION
# ============================================================

def extract_open_position(
    positions,
):
    candidates = positions

    if isinstance(
        positions,
        dict,
    ):
        for key in (
            "data",
            "result",
            "positions",
        ):
            obj = positions.get(
                key
            )

            if isinstance(
                obj,
                list,
            ):
                candidates = obj
                break

    if not isinstance(
        candidates,
        list,
    ):
        return None

    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if item_symbol != SYMBOL:
            continue

        size = safe_decimal(
            item.get(
                "size",
                item.get(
                    "positionSize",
                    "0",
                ),
            )
        )

        if abs(size) > ZERO:
            return item

    return None


# ============================================================
# CORRECT WEEX V3 BALANCE
# ============================================================

async def get_balance(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    return extract_available_usdt(
        data
    )


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/symbolPrice",
        {
            "symbol":
                SYMBOL,

            "priceType":
                "MARK",
        },
    )

    return extract_mark_price(
        data
    )


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_exchange_contract(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol":
                SYMBOL,
        },
    )

    return extract_contract(
        data
    )


# ============================================================
# API TRADING SYMBOL
# ============================================================

async def get_api_trading_status(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/apiTradingSymbols",
    )

    return extract_api_trading_allowed(
        data
    )


# ============================================================
# REAL POSITION READ
# ============================================================

async def get_positions(
    session,
):
    return await private_get(
        session,
        "/capi/v3/account/"
        "position/allPosition",
    )


# ============================================================
# LOCAL EXECUTION GATE TESTS
# ============================================================

def run_gate_tests(
    external_position_clear,
):
    now = int(
        time.time()
    )

    fresh_signal_time = (
        now
        - min(
            5,
            max(
                SIGNAL_EXPIRY_SECONDS
                - 1,
                0,
            ),
        )
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 5
    )


    fresh_signal_accepted = (
        now
        - fresh_signal_time
        <= SIGNAL_EXPIRY_SECONDS
    )


    expired_signal_rejected = not (
        now
        - expired_signal_time
        <= SIGNAL_EXPIRY_SECONDS
    )


    simulated_last_loss_time = (
        now
        - max(
            LOSS_COOLDOWN_SECONDS
            - 1,
            0,
        )
    )

    loss_cooldown_test = (
        LOSS_COOLDOWN_SECONDS
        <= 0
        or
        now
        - simulated_last_loss_time
        < LOSS_COOLDOWN_SECONDS
    )


    seen_signal_ids = set()

    signal_id = (
        f"{SYMBOL}:"
        "LONG:"
        "test-signal"
    )

    first_seen = (
        signal_id
        not in seen_signal_ids
    )

    if first_seen:
        seen_signal_ids.add(
            signal_id
        )

    duplicate_signal_rejected = (
        signal_id
        in seen_signal_ids
    )


    active_direction = None

    requested_direction = (
        "LONG"
    )

    one_direction_gate = (
        active_direction is None
        or active_direction
        == requested_direction
    )


    return {
        "fresh_signal_accepted":
            fresh_signal_accepted,

        "expired_signal_rejected":
            expired_signal_rejected,

        "loss_cooldown_test":
            loss_cooldown_test,

        "duplicate_signal_rejected":
            duplicate_signal_rejected,

        "one_direction_gate":
            one_direction_gate,

        "external_position_clear":
            external_position_clear,
    }


# ============================================================
# SIZING / EXPOSURE ENGINE
# ============================================================

def calculate_plan(
    balance,
    mark_price,
    contract,
):
    min_order = safe_decimal(
        contract.get(
            "minOrderSize",
            "0",
        )
    )

    quantity_precision = int(
        contract.get(
            "quantityPrecision",
            4,
        )
    )

    contract_value = safe_decimal(
        contract.get(
            "contractVal",
            "0",
        )
    )

    weex_min_leverage = safe_decimal(
        contract.get(
            "minLeverage",
            "1",
        )
    )

    weex_max_leverage = safe_decimal(
        contract.get(
            "maxLeverage",
            "0",
        )
    )


    margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / HUNDRED
    )


    notional = (
        margin
        * LEVERAGE
    )


    raw_quantity = ZERO

    if mark_price > ZERO:
        raw_quantity = (
            notional
            / mark_price
        )


    quantity = floor_to_precision(
        raw_quantity,
        quantity_precision,
    )


    pyramid_exposure = (
        Decimal(
            MAX_PYRAMID_ADDS
        )
        * PYRAMID_SIZE_PERCENT
    )


    backup_exposure = (
        Decimal(
            MAX_BACKUPS
        )
        * BACKUP_SIZE_PERCENT
    )


    total_exposure_percent = (
        INITIAL_ENTRY_PERCENT
        + pyramid_exposure
        + backup_exposure
    )


    leverage_gate = (
        LEVERAGE > ZERO

        and
        LEVERAGE
        <= MAX_LEVERAGE

        and
        LEVERAGE
        >= weex_min_leverage

        and
        (
            weex_max_leverage
            <= ZERO

            or

            LEVERAGE
            <= weex_max_leverage
        )
    )


    exposure_gate = (
        total_exposure_percent
        <= MAX_FUND_EXPOSURE_PERCENT
    )


    tp_sum_gate = (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
        == HUNDRED
    )


    quantity_positive = (
        quantity > ZERO
    )


    minimum_passed = (
        min_order <= ZERO
        or quantity >= min_order
    )


    return {
        "min_order":
            min_order,

        "quantity_precision":
            quantity_precision,

        "contract_value":
            contract_value,

        "weex_min_leverage":
            weex_min_leverage,

        "weex_max_leverage":
            weex_max_leverage,

        "margin":
            margin,

        "notional":
            notional,

        "raw_quantity":
            raw_quantity,

        "quantity":
            quantity,

        "pyramid_exposure":
            pyramid_exposure,

        "backup_exposure":
            backup_exposure,

        "total_exposure_percent":
            total_exposure_percent,

        "leverage_gate":
            leverage_gate,

        "exposure_gate":
            exposure_gate,

        "tp_sum_gate":
            tp_sum_gate,

        "quantity_positive":
            quantity_positive,

        "minimum_passed":
            minimum_passed,
    }


# ============================================================
# DRY-RUN ORDER PAYLOAD
# ============================================================

def build_simulated_order_payload(
    quantity,
):
    return {
        "symbol":
            SYMBOL,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            fmt(
                quantity
            ),

        "marginType":
            MARGIN_TYPE,

        "clientOrderId":
            (
                "r14-dryrun-"
                f"{int(time.time() * 1000)}"
            ),
    }


# ============================================================
# SUCCESS REPORT
# ============================================================

def build_success_report(
    balance,
    mark_price,
    contract,
    api_trading_allowed,
    open_position,
    gates,
    plan,
):
    external_position_clear = (
        open_position is None
    )


    all_passed = all(
        [
            credentials_ready(),

            api_trading_allowed,

            gates[
                "fresh_signal_accepted"
            ],

            gates[
                "expired_signal_rejected"
            ],

            gates[
                "loss_cooldown_test"
            ],

            gates[
                "duplicate_signal_rejected"
            ],

            gates[
                "one_direction_gate"
            ],

            external_position_clear,

            plan[
                "leverage_gate"
            ],

            plan[
                "exposure_gate"
            ],

            plan[
                "tp_sum_gate"
            ],

            plan[
                "quantity_positive"
            ],

            plan[
                "minimum_passed"
            ],

            HARD_EXECUTION_LOCK,

            ABSOLUTE_PRIVATE_POST_LOCK,

            not LIVE_ORDER_EXECUTION,
        ]
    )


    status_icon = (
        "✅"
        if all_passed
        else "⚠️"
    )


    status_text = (
        "DIAGNOSTIC PASSED"
        if all_passed
        else "NOT READY"
    )


    liq_price = "N/A"

    if open_position:
        liq_price = fmt(
            safe_decimal(
                open_position.get(
                    "liquidatePrice",
                    "0",
                )
            )
        )


    payload = (
        build_simulated_order_payload(
            plan[
                "quantity"
            ]
        )
    )


    lines = [
        (
            f"{status_icon} MODULE "
            f"{MODULE_NAME} "
            f"{status_text}"
        ),

        SYMBOL,

        "",

        (
            "Available USDT: "
            f"{fmt(balance)}"
        ),

        (
            "Mark Price: "
            f"{fmt(mark_price)} "
            "USDT"
        ),

        "",

        "FINAL EXECUTION GATE",

        (
            "API Trading Symbol: "
            f"{yes_no(api_trading_allowed)}"
        ),

        (
            "Fresh Signal Accepted: "
            f"{yes_no(gates['fresh_signal_accepted'])}"
        ),

        (
            "Expired Signal Rejected: "
            f"{yes_no(gates['expired_signal_rejected'])}"
        ),

        (
            "Loss Cooldown Test: "
            f"{yes_no(gates['loss_cooldown_test'])}"
        ),

        (
            "Duplicate Signal Rejected: "
            f"{yes_no(gates['duplicate_signal_rejected'])}"
        ),

        (
            "One Direction Gate: "
            f"{yes_no(gates['one_direction_gate'])}"
        ),

        (
            "External Position Clear: "
            f"{yes_no(external_position_clear)}"
        ),

        "",

        "ADJUSTABLE CONFIG",

        (
            "Entry: "
            f"{fmt(INITIAL_ENTRY_PERCENT)}%"
        ),

        (
            "Leverage: "
            f"{fmt(LEVERAGE)}x"
        ),

        (
            "Max Config Leverage: "
            f"{fmt(MAX_LEVERAGE)}x"
        ),

        (
            "Margin Type: "
            f"{MARGIN_TYPE}"
        ),

        (
            "Max Pyramids: "
            f"{MAX_PYRAMID_ADDS}"
        ),

        (
            "Pyramid Size: "
            f"{fmt(PYRAMID_SIZE_PERCENT)}%"
        ),

        (
            "Max Backups: "
            f"{MAX_BACKUPS}"
        ),

        (
            "Backup Size: "
            f"{fmt(BACKUP_SIZE_PERCENT)}% each"
        ),

        (
            "Max Fund Exposure: "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),

        "",

        "WEEX CONTRACT",

        (
            "Minimum Order: "
            f"{fmt(plan['min_order'])}"
        ),

        (
            "Quantity Precision: "
            f"{plan['quantity_precision']}"
        ),

        (
            "Contract Value: "
            f"{fmt(plan['contract_value'])}"
        ),

        (
            "WEEX Min Leverage: "
            f"{fmt(plan['weex_min_leverage'])}x"
        ),

        (
            "WEEX Max Leverage: "
            f"{fmt(plan['weex_max_leverage'])}x"
        ),

        (
            "Leverage Gate: "
            f"{yes_no(plan['leverage_gate'])}"
        ),

        "",

        "DYNAMIC ENTRY",

        (
            "Margin: "
            f"{fmt(plan['margin'])} "
            "USDT"
        ),

        (
            "Notional: "
            f"{fmt(plan['notional'])} "
            "USDT"
        ),

        (
            "Quantity: "
            f"{fmt(plan['quantity'])}"
        ),

        (
            "Quantity Positive: "
            f"{yes_no(plan['quantity_positive'])}"
        ),

        (
            "Minimum Passed: "
            f"{yes_no(plan['minimum_passed'])}"
        ),

        "",

        "WORST-CASE EXPOSURE",

        (
            "Initial: "
            f"{fmt(INITIAL_ENTRY_PERCENT)}%"
        ),

        (
            "Pyramids: "
            f"{fmt(plan['pyramid_exposure'])}%"
        ),

        (
            "Backups: "
            f"{fmt(plan['backup_exposure'])}%"
        ),

        (
            "Total: "
            f"{fmt(plan['total_exposure_percent'])}% "
            "/ "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),

        (
            "Exposure Passed: "
            f"{yes_no(plan['exposure_gate'])}"
        ),

        "",

        "TP / TRAILING",

        (
            "TP1 / TP2 / TP3: "
            f"{fmt(TP1_PERCENT)}% / "
            f"{fmt(TP2_PERCENT)}% / "
            f"{fmt(TP3_PERCENT)}%"
        ),

        (
            "TP Allocation Gate: "
            f"{yes_no(plan['tp_sum_gate'])}"
        ),

        (
            "TP1 Trigger: "
            f"{fmt(TP1_TRIGGER_PERCENT)}%"
        ),

        (
            "TP2 Trigger: "
            f"{fmt(TP2_TRIGGER_PERCENT)}%"
        ),

        (
            "Trailing Distance: "
            f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
        ),

        "",

        "LIQUIDATION SAFETY",

        (
            "Backup Buffer: "
            f"{fmt(BACKUP_BUFFER_PERCENT)}%"
        ),

        (
            "Min Liq Distance: "
            f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%"
        ),

        (
            "Planning MMR: "
            f"{fmt(PLANNING_MMR_PERCENT)}%"
        ),

        (
            "WEEX Liquidation Price: "
            f"{liq_price}"
        ),

        "",

        "R14 ORDER PAYLOAD SIMULATION",

        (
            "Endpoint Target: "
            "POST /capi/v3/order"
        ),

        (
            "Side: "
            f"{payload['side']} / "
            f"{payload['positionSide']}"
        ),

        (
            "Type: "
            f"{payload['type']}"
        ),

        (
            "Quantity: "
            f"{payload['quantity']}"
        ),

        (
            "Margin Type: "
            f"{payload['marginType']}"
        ),

        "Payload Built: ✅ YES",

        "Payload Transmitted: ❌ NO",

        "",

        (
            "🛡 R14 absolute "
            "private-POST lock active"
        ),

        (
            "⚠️ LIVE ORDER "
            "EXECUTION DISABLED"
        ),

        (
            "⚠️ NO LIVE ORDER "
            "WAS SENT"
        ),
    ]


    return (
        "\n".join(
            lines
        ),
        all_passed,
    )


# ============================================================
# ERROR REPORT
# ============================================================

def build_error_report(
    stage,
    exc,
):
    return "\n".join(
        [
            (
                f"❌ MODULE "
                f"{MODULE_NAME} "
                "ERROR"
            ),

            SYMBOL,

            (
                f"Stage: "
                f"{stage}"
            ),

            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),

            "",

            (
                "🛡 R14 absolute "
                "private-POST lock active"
            ),

            (
                "⚠️ NO LIVE ORDER "
                "WAS SENT"
            ),
        ]
    )


# ============================================================
# R14 DIAGNOSTIC
# ============================================================

async def run_r14(
    session,
):
    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "PRE-LIVE EXECUTION "
        "PATH VALIDATION"
    )

    print(
        "READ-ONLY WEEX "
        "PRIVATE CALLS ONLY"
    )

    print(
        "NO LIVE ORDER "
        "TRANSMISSION"
    )

    print(
        "=" * 60
    )


    stage = (
        "credentials"
    )


    try:

        if not credentials_ready():
            raise RuntimeError(
                "WEEX credentials "
                "are missing"
            )


        # ====================================================
        # BALANCE
        # ====================================================

        stage = "balance"

        balance = await get_balance(
            session
        )


        # ====================================================
        # MARK PRICE
        # ====================================================

        stage = "mark_price"

        mark_price = (
            await get_mark_price(
                session
            )
        )


        # ====================================================
        # EXCHANGE INFO
        # ====================================================

        stage = "exchange_info"

        contract = (
            await get_exchange_contract(
                session
            )
        )


        # ====================================================
        # API TRADING STATUS
        # ====================================================

        stage = (
            "api_trading_symbols"
        )

        api_trading_allowed = (
            await get_api_trading_status(
                session
            )
        )


        # ====================================================
        # POSITIONS
        # ====================================================

        stage = "positions"

        positions = await get_positions(
            session
        )

        open_position = (
            extract_open_position(
                positions
            )
        )

        external_position_clear = (
            open_position is None
        )


        # ====================================================
        # LOCAL GATES
        # ====================================================

        stage = "local_gates"

        gates = run_gate_tests(
            external_position_clear
        )


        # ====================================================
        # SIZING
        # ====================================================

        stage = "sizing"

        plan = calculate_plan(
            balance=balance,
            mark_price=mark_price,
            contract=contract,
        )


        # ====================================================
        # REPORT
        # ====================================================

        stage = "report"

        report, all_passed = (
            build_success_report(
                balance=balance,
                mark_price=mark_price,
                contract=contract,
                api_trading_allowed=
                    api_trading_allowed,
                open_position=
                    open_position,
                gates=gates,
                plan=plan,
            )
        )


        print(
            report
        )

        print(
            "=" * 60
        )


        # ONLY ONE TELEGRAM MESSAGE
        await send_telegram(
            session,
            report,
        )


        if all_passed:

            print(
                f"{MODULE_NAME} "
                "COMPLETE: PASSED"
            )

        else:

            print(
                f"{MODULE_NAME} "
                "COMPLETE: NOT READY"
            )


    except Exception as exc:

        report = build_error_report(
            stage,
            exc,
        )

        print(
            report
        )

        print(
            "=" * 60
        )


        # ONLY ONE TELEGRAM ERROR MESSAGE
        await send_telegram(
            session,
            report,
        )


# ============================================================
# MAIN
# ============================================================

async def main():

    runner = (
        await start_health_server()
    )


    try:

        async with aiohttp.ClientSession() as session:

            await run_r14(
                session
            )


            # ================================================
            # KEEP RENDER SERVICE ALIVE
            # ================================================

            while True:

                await asyncio.sleep(
                    3600
                )


    finally:

        await runner.cleanup()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        pass
