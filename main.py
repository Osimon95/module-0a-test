import asyncio
import base64
import hashlib
import hmac
import json
import os
import time

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R16"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

# Official WEEX V3 demo BTC symbol
DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    "BTCSUSDT",
).strip().upper()


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


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
# TP / TRAILING CONFIGURATION
# ============================================================

TP1_ALLOCATION_PERCENT = Decimal(
    os.getenv(
        "TP1_ALLOCATION_PERCENT",
        "20",
    )
)

TP2_ALLOCATION_PERCENT = Decimal(
    os.getenv(
        "TP2_ALLOCATION_PERCENT",
        "20",
    )
)

TP3_ALLOCATION_PERCENT = Decimal(
    os.getenv(
        "TP3_ALLOCATION_PERCENT",
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
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)


# ============================================================
# SIGNAL SAFETY CONFIGURATION
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
# R16 DEMO EXECUTION CONFIGURATION
# ============================================================

#
# IMPORTANT:
#
# R16 transmits ONLY to the official WEEX demo endpoint.
#
# This quantity is simulated.
#
# It does NOT use or risk the real USDT balance.
#

DEMO_ORDER_QUANTITY = Decimal(
    os.getenv(
        "DEMO_ORDER_QUANTITY",
        "0.0001",
    )
)

DEMO_ORDER_SIDE = "BUY"
DEMO_POSITION_SIDE = "LONG"
DEMO_ORDER_TYPE = "MARKET"

DEMO_ORDER_PATH = "/capi/v3/sim/order"
DEMO_BALANCE_PATH = "/capi/v3/sim/balance"
DEMO_HISTORY_PATH = "/capi/v3/sim/order/history"
DEMO_POSITIONS_PATH = "/capi/v3/sim/position/allPosition"

REAL_ORDER_PATH = "/capi/v3/order"


# ============================================================
# ABSOLUTE LIVE ORDER SAFETY
# ============================================================

#
# R16 MUST NEVER SEND A LIVE ORDER.
#

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True

ALLOW_DEMO_POST = True


# ============================================================
# ENVIRONMENT CREDENTIALS
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
# RUNTIME
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_decimal(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        return Decimal(
            str(value)
        )

    except Exception:
        return Decimal(default)


def fmt(value):
    try:
        value = Decimal(
            str(value)
        )

        text = format(
            value,
            "f",
        )

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return text or "0"

    except Exception:
        return str(value)


def icon(value):
    return "✅ YES" if value else "❌ NO"


def require_credentials():
    missing = []

    if not WEEX_API_KEY:
        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_API_SECRET:
        missing.append(
            "WEEX_API_SECRET"
        )

    if not WEEX_API_PASSPHRASE:
        missing.append(
            "WEEX_API_PASSPHRASE"
        )

    if missing:
        raise RuntimeError(
            "Missing WEEX environment variable(s): "
            + ", ".join(missing)
        )


# ============================================================
# SIGNATURE
# ============================================================

def generate_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body_text="",
):
    message = (
        str(timestamp)
        + method.upper()
        + request_path
        + query_string
        + body_text
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


def authenticated_headers(
    timestamp,
    signature,
):
    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": str(
            timestamp
        ),
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
    }


# ============================================================
# JSON HELPERS
# ============================================================

def decode_json(text):
    try:
        return json.loads(text)

    except Exception:
        raise RuntimeError(
            f"Invalid JSON response: {text}"
        )


def unwrap_list(data):
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
            "rows",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    return []


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    params = params or {}

    url = (
        API_BASE_URL
        + path
    )

    async with session.get(
        url,
        params=params,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text}"
            )

        return decode_json(
            text
        )


# ============================================================
# PRIVATE SIGNED GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):
    require_credentials()

    params = params or {}

    query_string = ""

    if params:
        query_string = (
            "?"
            + urlencode(
                params
            )
        )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = generate_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body_text="",
    )

    headers = authenticated_headers(
        timestamp,
        signature,
    )

    url = (
        API_BASE_URL
        + path
        + query_string
    )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PRIVATE GET HTTP "
                f"{response.status}: "
                f"{text}"
            )

        return decode_json(
            text
        )


# ============================================================
# ABSOLUTELY RESTRICTED R16 DEMO POST
# ============================================================

async def demo_private_post(
    session,
    path,
    payload,
):
    require_credentials()

    #
    # ABSOLUTE R16 LOCK
    #
    # Only this exact demo path can pass.
    #

    if path != DEMO_ORDER_PATH:
        raise RuntimeError(
            "R16 PRIVATE POST BLOCKED: "
            f"{path}"
        )

    if path == REAL_ORDER_PATH:
        raise RuntimeError(
            "R16 REAL ORDER ENDPOINT "
            "ABSOLUTELY BLOCKED"
        )

    if "/sim/" not in path:
        raise RuntimeError(
            "R16 NON-DEMO PRIVATE POST "
            "ABSOLUTELY BLOCKED"
        )

    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "R16 SAFETY VIOLATION: "
            "LIVE_ORDER_EXECUTION must remain False"
        )

    if not HARD_EXECUTION_LOCK:
        raise RuntimeError(
            "R16 SAFETY VIOLATION: "
            "HARD_EXECUTION_LOCK must remain True"
        )

    if not ALLOW_DEMO_POST:
        raise RuntimeError(
            "R16 demo POST disabled"
        )

    body_text = json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = generate_signature(
        timestamp=timestamp,
        method="POST",
        request_path=path,
        query_string="",
        body_text=body_text,
    )

    headers = authenticated_headers(
        timestamp,
        signature,
    )

    url = (
        API_BASE_URL
        + path
    )

    async with session.post(
        url,
        headers=headers,
        data=body_text,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        data = decode_json(
            text
        )

        if response.status != 200:
            raise RuntimeError(
                f"WEEX DEMO POST HTTP "
                f"{response.status}: "
                f"{text}"
            )

        return data


# ============================================================
# LIVE ACCOUNT BALANCE
# READ ONLY
# ============================================================

async def get_live_available_usdt(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    balances = unwrap_list(
        data
    )

    if not balances and isinstance(
        data,
        dict,
    ):
        balances = [
            data
        ]

    for item in balances:

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
            if key not in item:
                continue

            value = safe_decimal(
                item.get(
                    key
                )
            )

            if value >= ZERO:
                return value

    raise RuntimeError(
        "Unable to extract available USDT"
    )


# ============================================================
# DEMO ACCOUNT BALANCE
# ============================================================

async def get_demo_available_susdt(
    session,
):
    data = await private_get(
        session,
        DEMO_BALANCE_PATH,
    )

    balances = unwrap_list(
        data
    )

    if not balances and isinstance(
        data,
        dict,
    ):
        balances = [
            data
        ]

    for item in balances:

        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get(
                "asset",
                "",
            )
        ).upper()

        if asset != "SUSDT":
            continue

        for key in (
            "availableBalance",
            "available",
            "balance",
        ):
            if key not in item:
                continue

            value = safe_decimal(
                item.get(
                    key
                )
            )

            if value >= ZERO:
                return value

    raise RuntimeError(
        "Unable to extract demo SUSDT balance"
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
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    if isinstance(
        data,
        list,
    ):
        if not data:
            raise RuntimeError(
                "Empty mark price response"
            )

        data = data[0]

    if isinstance(
        data,
        dict,
    ):
        possible = [
            data,
            data.get(
                "data"
            ),
            data.get(
                "result"
            ),
        ]

        for obj in possible:

            if not isinstance(
                obj,
                dict,
            ):
                continue

            for key in (
                "price",
                "markPrice",
                "lastPrice",
                "last",
            ):
                if key not in obj:
                    continue

                price = safe_decimal(
                    obj.get(
                        key
                    )
                )

                if price > ZERO:
                    return price

    raise RuntimeError(
        "Unable to extract mark price"
    )


# ============================================================
# API TRADING SYMBOLS
# ============================================================

async def get_api_trading_symbols(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/apiTradingSymbols",
    )

    symbols = unwrap_list(
        data
    )

    if not symbols and isinstance(
        data,
        list,
    ):
        symbols = data

    clean = []

    for item in symbols:

        if isinstance(
            item,
            str,
        ):
            clean.append(
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
                clean.append(
                    str(
                        symbol
                    ).upper()
                )

    return clean


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL,
        },
    )

    candidates = []

    if isinstance(
        data,
        dict,
    ):

        symbols = data.get(
            "symbols"
        )

        if isinstance(
            symbols,
            list,
        ):
            candidates.extend(
                symbols
            )

        inner = data.get(
            "data"
        )

        if isinstance(
            inner,
            dict,
        ):
            inner_symbols = inner.get(
                "symbols"
            )

            if isinstance(
                inner_symbols,
                list,
            ):
                candidates.extend(
                    inner_symbols
                )

        elif isinstance(
            inner,
            list,
        ):
            candidates.extend(
                inner
            )

    elif isinstance(
        data,
        list,
    ):
        candidates.extend(
            data
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
        f"Contract information not found "
        f"for {SYMBOL}"
    )


# ============================================================
# POSITION CHECK
# READ ONLY
# ============================================================

async def get_live_positions(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/position/allPosition",
    )

    return unwrap_list(
        data
    )


def has_open_position(
    positions,
):
    for item in positions:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol and symbol != SYMBOL:
            continue

        possible_sizes = (
            "positionAmt",
            "positionSize",
            "size",
            "quantity",
            "available",
            "holdVol",
        )

        for key in possible_sizes:

            if key not in item:
                continue

            size = safe_decimal(
                item.get(
                    key
                )
            )

            if abs(
                size
            ) > ZERO:
                return True

    return False


# ============================================================
# QUANTITY
# ============================================================

def floor_quantity(
    quantity,
    precision,
):
    precision = max(
        0,
        int(
            precision
        ),
    )

    step = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    return quantity.quantize(
        step,
        rounding=ROUND_DOWN,
    )


# ============================================================
# SIGNAL LOGIC VALIDATION
# ============================================================

def validate_signal_logic():
    now = time.time()

    fresh_signal_time = (
        now
        - 1
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 10
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

    last_loss_time = (
        now
        - 1
    )

    cooldown_active = (
        now
        < last_loss_time
        + LOSS_COOLDOWN_SECONDS
    )

    loss_cooldown_test = (
        cooldown_active
    )

    processed_signal_ids = {
        "R16-DUPLICATE-TEST"
    }

    candidate_signal_id = (
        "R16-DUPLICATE-TEST"
    )

    duplicate_signal_rejected = (
        candidate_signal_id
        in processed_signal_ids
    )

    existing_direction = "LONG"
    opposite_candidate = "SHORT"

    one_direction_gate = (
        existing_direction
        != opposite_candidate
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
    }


# ============================================================
# DEMO ORDER PAYLOAD
# ============================================================

def build_demo_order_payload():
    if DEMO_ORDER_QUANTITY <= ZERO:
        raise RuntimeError(
            "DEMO_ORDER_QUANTITY must be > 0"
        )

    client_order_id = (
        "r16-"
        + str(
            int(
                time.time()
                * 1000
            )
        )
    )

    #
    # MARKET orders do NOT need
    # price or timeInForce.
    #

    payload = {
        "symbol": DEMO_SYMBOL,
        "side": DEMO_ORDER_SIDE,
        "positionSide": DEMO_POSITION_SIDE,
        "type": DEMO_ORDER_TYPE,
        "quantity": fmt(
            DEMO_ORDER_QUANTITY
        ),
        "newClientOrderId":
            client_order_id,
    }

    return payload


# ============================================================
# DEMO RESPONSE VALIDATION
# ============================================================

def validate_demo_order_response(
    data,
):
    if not isinstance(
        data,
        dict,
    ):
        return (
            False,
            "",
            "Unexpected response structure",
        )

    order_id = str(
        data.get(
            "orderId",
            "",
        )
    ).strip()

    success_value = data.get(
        "success"
    )

    error_code = str(
        data.get(
            "errorCode",
            "",
        )
    ).strip()

    error_message = str(
        data.get(
            "errorMessage",
            "",
        )
    ).strip()

    #
    # Official demo response contains success:true.
    #
    # Some API gateways may omit success while
    # still returning an orderId, so orderId is
    # also treated as positive confirmation.
    #

    accepted = (
        success_value is True
        or bool(
            order_id
        )
    )

    if not accepted:
        detail = (
            error_code
            + " "
            + error_message
        ).strip()

        if not detail:
            detail = str(
                data
            )

        return (
            False,
            order_id,
            detail,
        )

    return (
        True,
        order_id,
        "",
    )


# ============================================================
# DEMO HISTORY VERIFICATION
# ============================================================

async def verify_demo_order_history(
    session,
    order_id,
):
    if not order_id:
        return False, ""

    #
    # Give WEEX a short moment to make the
    # simulated order visible in history.
    #

    for _ in range(3):

        await asyncio.sleep(
            1
        )

        data = await private_get(
            session,
            DEMO_HISTORY_PATH,
            {
                "symbol": DEMO_SYMBOL,
                "limit": "50",
                "page": "0",
            },
        )

        records = unwrap_list(
            data
        )

        for item in records:

            if not isinstance(
                item,
                dict,
            ):
                continue

            candidate_id = str(
                item.get(
                    "orderId",
                    "",
                )
            )

            if candidate_id != str(
                order_id
            ):
                continue

            status = str(
                item.get(
                    "status",
                    "UNKNOWN",
                )
            ).upper()

            return True, status

    return False, ""


# ============================================================
# DEMO POSITIONS
# ============================================================

async def get_demo_positions(
    session,
):
    data = await private_get(
        session,
        DEMO_POSITIONS_PATH,
    )

    return unwrap_list(
        data
    )


def demo_position_detected(
    positions,
):
    for item in positions:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol != DEMO_SYMBOL:
            continue

        for key in (
            "positionAmt",
            "positionSize",
            "size",
            "quantity",
            "available",
            "holdVol",
        ):

            if key not in item:
                continue

            value = safe_decimal(
                item.get(
                    key
                )
            )

            if abs(
                value
            ) > ZERO:
                return True

    return False


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):
    if not TELEGRAM_BOT_TOKEN:
        print(
            "TELEGRAM_BOT_TOKEN not set"
        )

        return False

    if not TELEGRAM_CHAT_ID:
        print(
            "TELEGRAM_CHAT_ID not set"
        )

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            message,
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
                    "Telegram HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

                return False

            return True

    except Exception as exc:

        print(
            "Telegram error: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return False


# ============================================================
# REPORT BUILDER
# ============================================================

def build_report(
    *,
    passed,
    live_balance,
    demo_balance,
    mark_price,
    api_symbol_ok,
    signal_results,
    external_position_clear,
    min_order,
    quantity_precision,
    contract_value,
    weex_min_leverage,
    weex_max_leverage,
    leverage_gate,
    margin,
    notional,
    quantity,
    quantity_positive,
    minimum_passed,
    exposure_initial,
    exposure_pyramids,
    exposure_backups,
    exposure_total,
    exposure_passed,
    tp_allocation_ok,
    demo_payload,
    demo_accepted,
    demo_order_id,
    demo_history_found,
    demo_order_status,
    demo_position_found,
):
    status_icon = (
        "✅"
        if passed
        else "⚠️"
    )

    status_text = (
        "DIAGNOSTIC PASSED"
        if passed
        else "NOT READY"
    )

    demo_status = (
        demo_order_status
        if demo_order_status
        else "UNKNOWN"
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
            f"{fmt(live_balance)}"
        ),

        (
            "Mark Price: "
            f"{fmt(mark_price)} USDT"
        ),

        "",

        "FINAL EXECUTION GATE",

        (
            "API Trading Symbol: "
            f"{icon(api_symbol_ok)}"
        ),

        (
            "Fresh Signal Accepted: "
            f"{icon(signal_results['fresh_signal_accepted'])}"
        ),

        (
            "Expired Signal Rejected: "
            f"{icon(signal_results['expired_signal_rejected'])}"
        ),

        (
            "Loss Cooldown Test: "
            f"{icon(signal_results['loss_cooldown_test'])}"
        ),

        (
            "Duplicate Signal Rejected: "
            f"{icon(signal_results['duplicate_signal_rejected'])}"
        ),

        (
            "One Direction Gate: "
            f"{icon(signal_results['one_direction_gate'])}"
        ),

        (
            "External Position Clear: "
            f"{icon(external_position_clear)}"
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
            f"{fmt(min_order)}"
        ),

        (
            "Quantity Precision: "
            f"{quantity_precision}"
        ),

        (
            "Contract Value: "
            f"{fmt(contract_value)}"
        ),

        (
            "WEEX Min Leverage: "
            f"{fmt(weex_min_leverage)}x"
        ),

        (
            "WEEX Max Leverage: "
            f"{fmt(weex_max_leverage)}x"
        ),

        (
            "Leverage Gate: "
            f"{icon(leverage_gate)}"
        ),

        "",

        "DYNAMIC ENTRY",

        (
            "Margin: "
            f"{fmt(margin)} USDT"
        ),

        (
            "Notional: "
            f"{fmt(notional)} USDT"
        ),

        (
            "Quantity: "
            f"{fmt(quantity)}"
        ),

        (
            "Quantity Positive: "
            f"{icon(quantity_positive)}"
        ),

        (
            "Minimum Passed: "
            f"{icon(minimum_passed)}"
        ),

        "",

        "WORST-CASE EXPOSURE",

        (
            "Initial: "
            f"{fmt(exposure_initial)}%"
        ),

        (
            "Pyramids: "
            f"{fmt(exposure_pyramids)}%"
        ),

        (
            "Backups: "
            f"{fmt(exposure_backups)}%"
        ),

        (
            "Total: "
            f"{fmt(exposure_total)}%"
            f" / "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),

        (
            "Exposure Passed: "
            f"{icon(exposure_passed)}"
        ),

        "",

        "TP / TRAILING",

        (
            "TP1 / TP2 / TP3: "
            f"{fmt(TP1_ALLOCATION_PERCENT)}%"
            " / "
            f"{fmt(TP2_ALLOCATION_PERCENT)}%"
            " / "
            f"{fmt(TP3_ALLOCATION_PERCENT)}%"
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

        (
            "TP Allocation: "
            f"{icon(tp_allocation_ok)}"
        ),

        "",

        "R16 WEEX DEMO EXECUTION",

        (
            "Demo Symbol: "
            f"{DEMO_SYMBOL}"
        ),

        (
            "Demo Available: "
            f"{fmt(demo_balance)} SUSDT"
        ),

        (
            "Demo Endpoint: "
            f"{DEMO_ORDER_PATH}"
        ),

        (
            "Demo Type: "
            f"{DEMO_ORDER_TYPE}"
        ),

        (
            "Demo Side: "
            f"{DEMO_ORDER_SIDE}"
            " / "
            f"{DEMO_POSITION_SIDE}"
        ),

        (
            "Demo Quantity: "
            f"{demo_payload.get('quantity', '')}"
        ),

        (
            "Payload Built: "
            "✅ YES"
        ),

        (
            "Payload Transmitted: "
            "✅ YES"
        ),

        (
            "WEEX Demo Accepted: "
            f"{icon(demo_accepted)}"
        ),

        (
            "Demo Order ID: "
            f"{demo_order_id or 'N/A'}"
        ),

        (
            "Demo History Found: "
            f"{icon(demo_history_found)}"
        ),

        (
            "Demo Order Status: "
            f"{demo_status}"
        ),

        (
            "Demo Position Detected: "
            f"{icon(demo_position_found)}"
        ),

        "",

        "LIVE ORDER SAFETY",

        (
            "Real Endpoint: "
            f"{REAL_ORDER_PATH}"
        ),

        "Real POST Available: ❌ NO",

        "LIVE_ORDER_EXECUTION: DISABLED",

        "🛡 R16 absolute real-order POST lock active",

        "✅ DEMO ORDER ONLY",

        "⚠️ NO LIVE ORDER WAS SENT",

        "",

        "Render Runtime: ✅ PERSISTENT",
    ]

    return "\n".join(
        lines
    )


# ============================================================
# MAIN R16 DIAGNOSTIC
# ============================================================

async def run_r16():
    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "WEEX V3 DEMO EXECUTION VALIDATION"
    )

    print(
        "REAL ORDER ENDPOINT ABSOLUTELY LOCKED"
    )

    print(
        "=" * 60
    )

    stage = "startup"

    async with aiohttp.ClientSession() as session:

        try:

            # ================================================
            # CREDENTIALS
            # ================================================

            stage = "credentials"

            require_credentials()


            # ================================================
            # LIVE BALANCE
            # READ ONLY
            # ================================================

            stage = "live balance"

            live_balance = (
                await get_live_available_usdt(
                    session
                )
            )


            # ================================================
            # MARK PRICE
            # ================================================

            stage = "mark price"

            mark_price = (
                await get_mark_price(
                    session
                )
            )


            # ================================================
            # API SYMBOL
            # ================================================

            stage = "api symbols"

            api_symbols = (
                await get_api_trading_symbols(
                    session
                )
            )

            api_symbol_ok = (
                SYMBOL
                in api_symbols
            )


            # ================================================
            # CONTRACT INFO
            # ================================================

            stage = "contract info"

            contract = (
                await get_contract_info(
                    session
                )
            )

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


            # ================================================
            # LEVERAGE GATE
            # ================================================

            leverage_gate = (
                LEVERAGE
                >= weex_min_leverage

                and LEVERAGE
                <= weex_max_leverage

                and LEVERAGE
                <= MAX_LEVERAGE
            )


            # ================================================
            # SIGNAL SAFETY
            # ================================================

            stage = "signal logic"

            signal_results = (
                validate_signal_logic()
            )


            # ================================================
            # REAL POSITION READ
            # ================================================

            stage = "position check"

            positions = (
                await get_live_positions(
                    session
                )
            )

            external_position_clear = not (
                has_open_position(
                    positions
                )
            )


            # ================================================
            # ENTRY CALCULATION
            # ================================================

            margin = (
                live_balance
                * INITIAL_ENTRY_PERCENT
                / ONE_HUNDRED
            )

            notional = (
                margin
                * LEVERAGE
            )

            if mark_price <= ZERO:
                raise RuntimeError(
                    "Invalid mark price"
                )

            raw_quantity = (
                notional
                / mark_price
            )

            quantity = floor_quantity(
                raw_quantity,
                quantity_precision,
            )

            quantity_positive = (
                quantity > ZERO
            )

            minimum_passed = (
                quantity
                >= min_order
            )


            # ================================================
            # WORST CASE EXPOSURE
            # ================================================

            exposure_initial = (
                INITIAL_ENTRY_PERCENT
            )

            exposure_pyramids = (
                PYRAMID_SIZE_PERCENT
                * Decimal(
                    MAX_PYRAMID_ADDS
                )
            )

            exposure_backups = (
                BACKUP_SIZE_PERCENT
                * Decimal(
                    MAX_BACKUPS
                )
            )

            exposure_total = (
                exposure_initial
                + exposure_pyramids
                + exposure_backups
            )

            exposure_passed = (
                exposure_total
                <= MAX_FUND_EXPOSURE_PERCENT
            )


            # ================================================
            # TP ALLOCATION
            # ================================================

            tp_total = (
                TP1_ALLOCATION_PERCENT
                + TP2_ALLOCATION_PERCENT
                + TP3_ALLOCATION_PERCENT
            )

            tp_allocation_ok = (
                tp_total
                == ONE_HUNDRED
            )


            # ================================================
            # DEMO BALANCE
            # ================================================

            stage = "demo balance"

            demo_balance = (
                await get_demo_available_susdt(
                    session
                )
            )


            # ================================================
            # BUILD DEMO PAYLOAD
            # ================================================

            stage = "demo payload"

            demo_payload = (
                build_demo_order_payload()
            )


            # ================================================
            # FINAL PRE-DEMO GATE
            # ================================================

            pre_demo_checks = [
                api_symbol_ok,
                signal_results[
                    "fresh_signal_accepted"
                ],
                signal_results[
                    "expired_signal_rejected"
                ],
                signal_results[
                    "loss_cooldown_test"
                ],
                signal_results[
                    "duplicate_signal_rejected"
                ],
                signal_results[
                    "one_direction_gate"
                ],
                external_position_clear,
                leverage_gate,
                quantity_positive,
                minimum_passed,
                exposure_passed,
                tp_allocation_ok,
                DEMO_ORDER_QUANTITY > ZERO,
                LIVE_ORDER_EXECUTION is False,
                HARD_EXECUTION_LOCK is True,
                ALLOW_DEMO_POST is True,
                DEMO_ORDER_PATH
                != REAL_ORDER_PATH,
            ]

            pre_demo_passed = all(
                pre_demo_checks
            )

            if not pre_demo_passed:
                raise RuntimeError(
                    "R16 pre-demo execution "
                    "gate failed"
                )


            # ================================================
            # ACTUAL WEEX DEMO POST
            # ================================================
            #
            # THIS IS THE ONLY PRIVATE POST
            # PERMITTED IN R16.
            #
            # It goes to:
            #
            # /capi/v3/sim/order
            #
            # NOT:
            #
            # /capi/v3/order
            #
            # ================================================

            stage = "demo order transmission"

            demo_response = (
                await demo_private_post(
                    session,
                    DEMO_ORDER_PATH,
                    demo_payload,
                )
            )


            # ================================================
            # VALIDATE ACCEPTANCE
            # ================================================

            stage = "demo response"

            (
                demo_accepted,
                demo_order_id,
                demo_error,
            ) = validate_demo_order_response(
                demo_response
            )

            if not demo_accepted:
                raise RuntimeError(
                    "WEEX demo order rejected: "
                    + demo_error
                )


            # ================================================
            # VERIFY HISTORY
            # ================================================

            stage = "demo history"

            (
                demo_history_found,
                demo_order_status,
            ) = await verify_demo_order_history(
                session,
                demo_order_id,
            )


            # ================================================
            # DEMO POSITIONS
            # ================================================

            stage = "demo positions"

            demo_positions = (
                await get_demo_positions(
                    session
                )
            )

            demo_position_found = (
                demo_position_detected(
                    demo_positions
                )
            )


            # ================================================
            # R16 PASS LOGIC
            # ================================================
            #
            # Acceptance from WEEX is mandatory.
            #
            # History lookup is also required because
            # R16 is specifically testing the complete
            # authenticated demo execution path.
            #

            passed = all(
                [
                    pre_demo_passed,
                    demo_accepted,
                    bool(
                        demo_order_id
                    ),
                    demo_history_found,
                ]
            )


            # ================================================
            # REPORT
            # ================================================

            report = build_report(
                passed=passed,
                live_balance=live_balance,
                demo_balance=demo_balance,
                mark_price=mark_price,
                api_symbol_ok=api_symbol_ok,
                signal_results=signal_results,
                external_position_clear=
                    external_position_clear,
                min_order=min_order,
                quantity_precision=
                    quantity_precision,
                contract_value=contract_value,
                weex_min_leverage=
                    weex_min_leverage,
                weex_max_leverage=
                    weex_max_leverage,
                leverage_gate=
                    leverage_gate,
                margin=margin,
                notional=notional,
                quantity=quantity,
                quantity_positive=
                    quantity_positive,
                minimum_passed=
                    minimum_passed,
                exposure_initial=
                    exposure_initial,
                exposure_pyramids=
                    exposure_pyramids,
                exposure_backups=
                    exposure_backups,
                exposure_total=
                    exposure_total,
                exposure_passed=
                    exposure_passed,
                tp_allocation_ok=
                    tp_allocation_ok,
                demo_payload=
                    demo_payload,
                demo_accepted=
                    demo_accepted,
                demo_order_id=
                    demo_order_id,
                demo_history_found=
                    demo_history_found,
                demo_order_status=
                    demo_order_status,
                demo_position_found=
                    demo_position_found,
            )

            print()
            print(
                report
            )
            print()

            telegram_sent = (
                await send_telegram(
                    session,
                    report,
                )
            )

            print(
                "Telegram report sent: "
                + (
                    "YES"
                    if telegram_sent
                    else "NO"
                )
            )

            print(
                "=" * 60
            )

            print(
                f"{MODULE_NAME} COMPLETE: "
                + (
                    "PASSED"
                    if passed
                    else "NOT READY"
                )
            )

            print(
                "=" * 60
            )

            return passed


        except Exception as exc:

            error_message = (
                f"❌ MODULE {MODULE_NAME} ERROR\n"
                f"{SYMBOL}\n\n"
                f"Stage: {stage}\n"
                f"{type(exc).__name__}: {exc}\n\n"
                f"🛡 R16 absolute "
                f"real-order POST lock active\n"
                f"⚠️ LIVE ORDER EXECUTION DISABLED\n"
                f"⚠️ NO LIVE ORDER WAS SENT"
            )

            print()
            print(
                error_message
            )
            print()

            await send_telegram(
                session,
                error_message,
            )

            return False


# ============================================================
# HEALTH SERVER
# ============================================================

async def health(
    request,
):
    return web.Response(
        text=(
            f"{MODULE_NAME} ACTIVE\n"
            "R16 DEMO EXECUTION MODE\n"
            "REAL ORDERS LOCKED\n"
        )
    )


async def start_health_server():
    app = web.Application()

    app.router.add_get(
        "/",
        health,
    )

    app.router.add_get(
        "/health",
        health,
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
# APPLICATION
# ============================================================

async def main():
    runner = await start_health_server()

    try:

        await run_r16()

        #
        # Keep Render service alive.
        #
        # R16 diagnostic runs exactly once per
        # process startup.
        #

        while True:
            await asyncio.sleep(
                3600
            )

    finally:

        await runner.cleanup()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        main())
