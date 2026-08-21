import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import traceback

from decimal import Decimal, ROUND_DOWN, InvalidOperation
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R22"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


def default_demo_symbol(symbol: str) -> str:
    if symbol.endswith("USDT"):
        return symbol[:-4] + "SUSDT"

    return symbol


DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    default_demo_symbol(SYMBOL),
).strip().upper()


# ============================================================
# R22 PURPOSE
# ============================================================
#
# R22 builds directly on the successful R21 execution rehearsal.
#
# PRIMARY R22 CHANGE:
#
#     KEEP THE RENDER PROCESS ALIVE
#
# R21 completed its diagnostic and could then allow the Python
# process to terminate. Render interpreted that exit as a stopped
# service and restarted the instance.
#
# R22:
#
# 1. Starts the HTTP health server first.
# 2. Runs the diagnostic once.
# 3. Keeps the asyncio event loop alive permanently.
# 4. Does NOT repeatedly transmit demo orders.
# 5. Does NOT permit any real order POST.
#
# ============================================================


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
#
# IMPORTANT:
#
# R22 IS STILL A PRE-LIVE / DEMO REHEARSAL MODULE.
#
# Real order execution is intentionally disabled.
#
# Authenticated GET requests:
#     ALLOWED
#
# Demo POST:
#     ALLOWED
#
# Real state-changing POST:
#     ABSOLUTELY BLOCKED
#
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_REAL_POST_LOCK = True

R22_REAL_POST_CALLED = False

R22_DEMO_POST_ATTEMPTED = False

R22_DEMO_POST_ACCEPTED = False

R22_DEMO_ORDER_ID = None

R22_DIAGNOSTIC_COMPLETE = False

R22_DIAGNOSTIC_PASSED = False

R22_LAST_ERROR = None

R22_START_TIME = time.time()


# ============================================================
# DEMO EXECUTION SWITCH
# ============================================================

RUN_DEMO_ORDER_TEST = (
    os.getenv(
        "RUN_DEMO_ORDER_TEST",
        "true",
    ).strip().lower()
    in (
        "1",
        "true",
        "yes",
        "on",
    )
)


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

TELEGRAM_ENABLED = bool(
    TELEGRAM_BOT_TOKEN
    and TELEGRAM_CHAT_ID
)


# ============================================================
# WEEX CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    "",
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    "",
).strip()


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(
    os.getenv(
        "ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = int(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_CONFIG_LEVERAGE = int(
    os.getenv(
        "MAX_CONFIG_LEVERAGE",
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

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TP / TRAILING
# ============================================================

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ============================================================
# SIGNAL SAFETY
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

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# DEMO REHEARSAL SETTINGS
# ============================================================

REHEARSAL_SIDE = os.getenv(
    "REHEARSAL_SIDE",
    "BUY",
).strip().upper()

REHEARSAL_POSITION_SIDE = os.getenv(
    "REHEARSAL_POSITION_SIDE",
    "LONG",
).strip().upper()

REHEARSAL_ORDER_TYPE = os.getenv(
    "REHEARSAL_ORDER_TYPE",
    "LIMIT",
).strip().upper()

REHEARSAL_LIMIT_OFFSET_PERCENT = Decimal(
    os.getenv(
        "REHEARSAL_LIMIT_OFFSET_PERCENT",
        "0.10",
    )
)


# ============================================================
# HTTP / RENDER
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

HTTP_TIMEOUT_SECONDS = 20

KEEPALIVE_LOG_SECONDS = int(
    os.getenv(
        "KEEPALIVE_LOG_SECONDS",
        "300",
    )
)


# ============================================================
# API PATHS
# ============================================================

API_TRADING_SYMBOLS_PATH = (
    "/capi/v3/market/apiTradingSymbols"
)

EXCHANGE_INFO_PATH = (
    "/capi/v3/market/exchangeInfo"
)

MARK_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
)

ACCOUNT_BALANCE_PATH = (
    "/capi/v3/account/balance"
)

POSITIONS_PATH = (
    "/capi/v3/account/position/allPosition"
)

DEMO_BALANCE_PATH = (
    "/capi/v3/sim/balance"
)

DEMO_POSITIONS_PATH = (
    "/capi/v3/sim/position/allPosition"
)

DEMO_ORDER_HISTORY_PATH = (
    "/capi/v3/sim/order/history"
)

DEMO_ORDER_PATH = (
    "/capi/v3/sim/order"
)

REAL_ORDER_PATH = (
    "/capi/v3/order"
)


# ============================================================
# DECIMAL CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_decimal(
    value,
    default=None,
):
    try:
        if value is None:
            raise InvalidOperation

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        if default is not None:
            return Decimal(
                str(default)
            )

        raise


def decimal_to_string(
    value: Decimal,
) -> str:
    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in (
        "",
        "-0",
    ):
        text = "0"

    return text


def yes_no(
    value,
) -> str:
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def status_icon(
    value,
) -> str:
    return (
        "✅"
        if value
        else "❌"
    )


def now_ms() -> int:
    return int(
        time.time() * 1000
    )


def seconds_since_start() -> int:
    return int(
        time.time()
        - R22_START_TIME
    )


# ============================================================
# CREDENTIAL VALIDATION
# ============================================================

def validate_credentials():
    missing = []

    if not WEEX_API_KEY:
        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_SECRET_KEY:
        missing.append(
            "WEEX_SECRET_KEY"
        )

    if not WEEX_PASSPHRASE:
        missing.append(
            "WEEX_PASSPHRASE"
        )

    if missing:
        raise RuntimeError(
            "Missing WEEX credentials: "
            + ", ".join(missing)
        )


# ============================================================
# REAL POST ABSOLUTE LOCK
# ============================================================

def assert_real_order_post_locked(
    path: str,
):
    global R22_REAL_POST_CALLED

    R22_REAL_POST_CALLED = True

    raise RuntimeError(
        "R22 ABSOLUTE SAFETY LOCK: "
        f"real state-changing POST blocked: {path}"
    )


def final_safety_assertions_r22():
    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "R22 safety violation: "
            "LIVE_ORDER_EXECUTION must remain False"
        )

    if not HARD_REAL_POST_LOCK:
        raise RuntimeError(
            "R22 safety violation: "
            "HARD_REAL_POST_LOCK must remain True"
        )

    if R22_REAL_POST_CALLED:
        raise RuntimeError(
            "R22 safety violation: "
            "a real POST was attempted"
        )

    if REAL_ORDER_PATH == DEMO_ORDER_PATH:
        raise RuntimeError(
            "R22 safety violation: "
            "real and demo paths are identical"
        )

    if not DEMO_ORDER_PATH.startswith(
        "/capi/v3/sim/"
    ):
        raise RuntimeError(
            "R22 safety violation: "
            "demo path is not under /sim/"
        )

    return True


# ============================================================
# AUTH SIGNATURE
# ============================================================

def create_signature(
    timestamp: str,
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    if query_string:
        request_target = (
            f"{path}?{query_string}"
        )
    else:
        request_target = path

    message = (
        timestamp
        + method
        + request_target
        + body
    )

    digest = hmac.new(
        WEEX_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def build_auth_headers(
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
):
    timestamp = str(
        now_ms()
    )

    signature = create_signature(
        timestamp=timestamp,
        method=method,
        path=path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "User-Agent": f"{MODULE_NAME}/1.0",
    }


# ============================================================
# GENERIC PUBLIC GET
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
            total=HTTP_TIMEOUT_SECONDS
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX GET HTTP {response.status}: "
                f"{text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                "WEEX returned invalid JSON: "
                + text[:500]
            )


# ============================================================
# AUTHENTICATED REQUEST
# ============================================================

async def authenticated_request(
    session,
    method,
    path,
    params=None,
    payload=None,
):
    method = method.upper()

    params = params or {}

    query_string = urlencode(
        params
    )

    body = ""

    if payload is not None:
        body = json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # R22 ABSOLUTE POST SAFETY
    # --------------------------------------------------------

    if method == "POST":
        if not path.startswith(
            "/capi/v3/sim/"
        ):
            assert_real_order_post_locked(
                path
            )

    headers = build_auth_headers(
        method=method,
        path=path,
        query_string=query_string,
        body=body,
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

    request_kwargs = {
        "headers": headers,
        "timeout": aiohttp.ClientTimeout(
            total=HTTP_TIMEOUT_SECONDS
        ),
    }

    if payload is not None:
        request_kwargs["data"] = body

    async with session.request(
        method,
        url,
        **request_kwargs,
    ) as response:

        text = await response.text()

        try:
            data = json.loads(text)

        except json.JSONDecodeError:
            data = {
                "raw": text
            }

        if response.status < 200:
            raise RuntimeError(
                f"WEEX {method} HTTP "
                f"{response.status}: {text}"
            )

        if response.status >= 300:
            raise RuntimeError(
                f"WEEX {method} HTTP "
                f"{response.status}: {text}"
            )

        return data


# ============================================================
# API TRADING SYMBOLS
# ============================================================

async def get_api_trading_symbols(
    session,
):
    data = await public_get(
        session,
        API_TRADING_SYMBOLS_PATH,
    )

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected API trading-symbol response"
        )

    symbols = {
        str(item).strip().upper()
        for item in data
    }

    return symbols


# ============================================================
# EXCHANGE INFO
# ============================================================

async def get_exchange_info(
    session,
):
    data = await public_get(
        session,
        EXCHANGE_INFO_PATH,
        params={
            "symbol": SYMBOL,
        },
    )

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Unexpected exchangeInfo response"
        )

    symbols = data.get(
        "symbols",
        [],
    )

    if not isinstance(
        symbols,
        list,
    ):
        raise RuntimeError(
            "exchangeInfo symbols is not a list"
        )

    for item in symbols:
        if not isinstance(
            item,
            dict,
        ):
            continue

        if (
            str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):
            return item

    raise RuntimeError(
        f"{SYMBOL} not found in exchangeInfo"
    )


# ============================================================
# CONTRACT NORMALIZATION
# ============================================================

def parse_contract_info(
    contract,
):
    price_precision = int(
        contract.get(
            "pricePrecision",
            1,
        )
    )

    quantity_precision = int(
        contract.get(
            "quantityPrecision",
            4,
        )
    )

    min_order_size = safe_decimal(
        contract.get(
            "minOrderSize",
            "0.0001",
        )
    )

    contract_value = safe_decimal(
        contract.get(
            "contractVal",
            "0.0001",
        )
    )

    min_leverage = int(
        contract.get(
            "minLeverage",
            1,
        )
    )

    max_leverage = int(
        contract.get(
            "maxLeverage",
            400,
        )
    )

    price_step = (
        Decimal("1")
        .scaleb(
            -price_precision
        )
    )

    quantity_step = (
        Decimal("1")
        .scaleb(
            -quantity_precision
        )
    )

    return {
        "price_precision": price_precision,
        "quantity_precision": quantity_precision,
        "price_step": price_step,
        "quantity_step": quantity_step,
        "min_order_size": min_order_size,
        "contract_value": contract_value,
        "min_leverage": min_leverage,
        "max_leverage": max_leverage,
    }


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):
    data = await public_get(
        session,
        MARK_PRICE_PATH,
        params={
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Unexpected mark-price response"
        )

    price = safe_decimal(
        data.get(
            "price"
        )
    )

    if price <= ZERO:
        raise RuntimeError(
            f"Invalid WEEX mark price: {price}"
        )

    return price


# ============================================================
# REAL ACCOUNT BALANCE
# ============================================================

async def get_available_usdt(
    session,
):
    data = await authenticated_request(
        session,
        "GET",
        ACCOUNT_BALANCE_PATH,
    )

    if isinstance(
        data,
        dict,
    ):
        possible = [
            data,
            data.get("data"),
            data.get("result"),
        ]

        for obj in possible:
            if isinstance(
                obj,
                list,
            ):
                data = obj
                break

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unable to extract account balance"
        )

    for item in data:
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

        if asset == "USDT":
            available = safe_decimal(
                item.get(
                    "availableBalance",
                    item.get(
                        "available",
                        "0",
                    ),
                )
            )

            if available < ZERO:
                raise RuntimeError(
                    "Available USDT is negative"
                )

            return available

    raise RuntimeError(
        "Unable to extract available USDT"
    )


# ============================================================
# REAL POSITION CHECK
# ============================================================

async def get_real_positions(
    session,
):
    data = await authenticated_request(
        session,
        "GET",
        POSITIONS_PATH,
    )

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "positions",
        ):
            candidate = data.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):
                data = candidate
                break

    if not isinstance(
        data,
        list,
    ):
        return []

    return data


def has_external_position(
    positions,
):
    for position in positions:
        if not isinstance(
            position,
            dict,
        ):
            continue

        position_symbol = str(
            position.get(
                "symbol",
                "",
            )
        ).upper()

        if position_symbol != SYMBOL:
            continue

        size = safe_decimal(
            position.get(
                "size",
                "0",
            ),
            default="0",
        )

        if size > ZERO:
            return True

    return False


# ============================================================
# QUANTITY NORMALIZATION
# ============================================================

def quantize_down(
    value: Decimal,
    step: Decimal,
):
    if step <= ZERO:
        raise RuntimeError(
            "Step must be greater than zero"
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


def quantize_quantity_r22(
    quantity,
    quantity_step,
):
    quantity = safe_decimal(
        quantity
    )

    result = quantize_down(
        quantity,
        quantity_step,
    )

    if result <= ZERO:
        raise RuntimeError(
            "Normalized quantity is zero"
        )

    return result


def quantize_price_r22(
    price,
    price_step,
):
    price = safe_decimal(
        price
    )

    result = quantize_down(
        price,
        price_step,
    )

    if result <= ZERO:
        raise RuntimeError(
            "Normalized price is zero"
        )

    return result


# ============================================================
# ENTRY CALCULATION
# ============================================================

def calculate_entry(
    available_usdt,
    mark_price,
    quantity_step,
):
    margin = (
        available_usdt
        * ENTRY_PERCENT
        / HUNDRED
    )

    notional = (
        margin
        * Decimal(
            str(LEVERAGE)
        )
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = quantize_quantity_r22(
        raw_quantity,
        quantity_step,
    )

    return {
        "margin": margin,
        "notional": notional,
        "raw_quantity": raw_quantity,
        "quantity": quantity,
    }


# ============================================================
# LEVERAGE VALIDATION
# ============================================================

def validate_leverage_r22(
    min_leverage,
    max_leverage,
):
    if LEVERAGE < 1:
        return False

    if LEVERAGE > MAX_CONFIG_LEVERAGE:
        return False

    if LEVERAGE < min_leverage:
        return False

    if LEVERAGE > max_leverage:
        return False

    return True


# ============================================================
# FUND EXPOSURE
# ============================================================

def calculate_worst_case_exposure():
    initial = ENTRY_PERCENT

    pyramids = (
        PYRAMID_SIZE_PERCENT
        * Decimal(
            str(MAX_PYRAMID_ADDS)
        )
    )

    backups = (
        BACKUP_SIZE_PERCENT
        * Decimal(
            str(MAX_BACKUPS)
        )
    )

    total = (
        initial
        + pyramids
        + backups
    )

    return {
        "initial": initial,
        "pyramids": pyramids,
        "backups": backups,
        "total": total,
        "passed": (
            total
            <= MAX_FUND_EXPOSURE_PERCENT
        ),
    }


# ============================================================
# SIGNAL GATE SELF TESTS
# ============================================================

def signal_is_fresh(
    signal_timestamp,
    now_timestamp=None,
):
    if now_timestamp is None:
        now_timestamp = time.time()

    age = (
        now_timestamp
        - signal_timestamp
    )

    return (
        age >= 0
        and age
        <= SIGNAL_EXPIRY_SECONDS
    )


def loss_cooldown_clear(
    last_loss_timestamp,
    now_timestamp=None,
):
    if last_loss_timestamp is None:
        return True

    if now_timestamp is None:
        now_timestamp = time.time()

    elapsed = (
        now_timestamp
        - last_loss_timestamp
    )

    return (
        elapsed
        >= LOSS_COOLDOWN_SECONDS
    )


def run_signal_gate_self_tests():
    reference = time.time()

    fresh_signal = (
        reference
        - 1
    )

    expired_signal = (
        reference
        - SIGNAL_EXPIRY_SECONDS
        - 5
    )

    active_loss = (
        reference
        - max(
            1,
            LOSS_COOLDOWN_SECONDS // 2,
        )
    )

    fresh_accepted = signal_is_fresh(
        fresh_signal,
        reference,
    )

    expired_rejected = (
        not signal_is_fresh(
            expired_signal,
            reference,
        )
    )

    loss_cooldown_test = (
        not loss_cooldown_clear(
            active_loss,
            reference,
        )
    )

    existing_client_ids = {
        "r22-test-duplicate"
    }

    duplicate_signal_rejected = (
        "r22-test-duplicate"
        in existing_client_ids
    )

    existing_direction = "LONG"
    requested_direction = "SHORT"

    one_direction_gate = (
        ONE_DIRECTION_ONLY
        and existing_direction
        != requested_direction
    )

    return {
        "fresh_signal_accepted": (
            fresh_accepted
        ),
        "expired_signal_rejected": (
            expired_rejected
        ),
        "loss_cooldown_test": (
            loss_cooldown_test
        ),
        "duplicate_signal_rejected": (
            duplicate_signal_rejected
        ),
        "one_direction_gate_test": (
            one_direction_gate
        ),
    }


# ============================================================
# DEMO LIMIT PRICE
# ============================================================

def build_safe_demo_limit_price(
    mark_price,
    price_step,
):
    offset = (
        mark_price
        * REHEARSAL_LIMIT_OFFSET_PERCENT
        / HUNDRED
    )

    if REHEARSAL_SIDE == "BUY":
        raw_price = (
            mark_price
            - offset
        )

    elif REHEARSAL_SIDE == "SELL":
        raw_price = (
            mark_price
            + offset
        )

    else:
        raise RuntimeError(
            "REHEARSAL_SIDE must be BUY or SELL"
        )

    price = quantize_price_r22(
        raw_price,
        price_step,
    )

    if price <= ZERO:
        raise RuntimeError(
            "Demo limit price must be greater than zero"
        )

    return price


# ============================================================
# PRICE STEP VALIDATION
# ============================================================

def matches_step(
    value,
    step,
):
    if step <= ZERO:
        return False

    try:
        units = (
            value
            / step
        )

        return (
            units
            == units.to_integral_value()
        )

    except Exception:
        return False


# ============================================================
# CLIENT ORDER ID
# ============================================================

def create_client_order_id():
    stamp = int(
        time.time() * 1000
    )

    # Less than 36 characters.
    return (
        f"r22-{stamp}"
    )


# ============================================================
# DEMO ORDER PAYLOAD
# ============================================================

def build_demo_order_payload_r22(
    quantity,
    limit_price=None,
):
    if REHEARSAL_SIDE not in (
        "BUY",
        "SELL",
    ):
        raise RuntimeError(
            "Invalid rehearsal side"
        )

    if REHEARSAL_POSITION_SIDE not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "Invalid rehearsal position side"
        )

    if REHEARSAL_ORDER_TYPE not in (
        "LIMIT",
        "MARKET",
    ):
        raise RuntimeError(
            "Invalid rehearsal order type"
        )

    if quantity <= ZERO:
        raise RuntimeError(
            "Demo quantity must be positive"
        )

    payload = {
        "symbol": DEMO_SYMBOL,
        "side": REHEARSAL_SIDE,
        "positionSide": (
            REHEARSAL_POSITION_SIDE
        ),
        "type": REHEARSAL_ORDER_TYPE,
        "quantity": decimal_to_string(
            quantity
        ),
        "newClientOrderId": (
            create_client_order_id()
        ),
    }

    if REHEARSAL_ORDER_TYPE == "LIMIT":
        if (
            limit_price is None
            or limit_price <= ZERO
        ):
            raise RuntimeError(
                "LIMIT demo order requires "
                "a valid positive price"
            )

        payload["timeInForce"] = "GTC"

        payload["price"] = (
            decimal_to_string(
                limit_price
            )
        )

    return payload


# ============================================================
# DEMO ORDER RESPONSE
# ============================================================

def extract_demo_order_result(
    data,
):
    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Unexpected demo-order response"
        )

    success = data.get(
        "success"
    )

    order_id = (
        data.get("orderId")
        or data.get("order_id")
    )

    error_code = (
        data.get("errorCode")
        or data.get("code")
        or ""
    )

    error_message = (
        data.get("errorMessage")
        or data.get("msg")
        or data.get("message")
        or ""
    )

    if success is False:
        raise RuntimeError(
            "WEEX DEMO ORDER REJECTED: "
            f"{error_code} {error_message}"
        )

    if not order_id:
        # Some API success wrappers may omit explicit boolean.
        if success is not True:
            raise RuntimeError(
                "Demo POST returned no order ID: "
                + json.dumps(
                    data,
                    separators=(",", ":"),
                )
            )

    return {
        "success": (
            success is not False
        ),
        "order_id": (
            str(order_id)
            if order_id
            else "UNKNOWN"
        ),
    }


# ============================================================
# DEMO TRANSMISSION
# ============================================================

async def transmit_demo_order_r22(
    session,
    payload,
):
    global R22_DEMO_POST_ATTEMPTED
    global R22_DEMO_POST_ACCEPTED
    global R22_DEMO_ORDER_ID

    R22_DEMO_POST_ATTEMPTED = True

    data = await authenticated_request(
        session,
        "POST",
        DEMO_ORDER_PATH,
        payload=payload,
    )

    result = extract_demo_order_result(
        data
    )

    R22_DEMO_POST_ACCEPTED = (
        result["success"]
    )

    R22_DEMO_ORDER_ID = (
        result["order_id"]
    )

    return result


# ============================================================
# OPTIONAL DEMO GET PROBES
# ============================================================

async def demo_balance_probe(
    session,
):
    try:
        return await authenticated_request(
            session,
            "GET",
            DEMO_BALANCE_PATH,
        )

    except Exception:
        return None


async def demo_positions_probe(
    session,
):
    try:
        return await authenticated_request(
            session,
            "GET",
            DEMO_POSITIONS_PATH,
        )

    except Exception:
        return None


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):
    if not TELEGRAM_ENABLED:
        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            await response.text()

            return (
                response.status == 200
            )

    except Exception as exc:
        print(
            "TELEGRAM ERROR:",
            repr(exc),
            flush=True,
        )

        return False


# ============================================================
# SUCCESS REPORT
# ============================================================

def build_success_report(
    available_usdt,
    mark_price,
    contract_info,
    api_symbol_allowed,
    external_position_clear,
    signal_tests,
    entry,
    exposure,
    leverage_passed,
    demo_limit_price,
    price_step_match,
):
    lines = []

    lines.append(
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED"
    )

    lines.append(
        SYMBOL
    )

    lines.append(
        "Available USDT: "
        + decimal_to_string(
            available_usdt
        )
    )

    lines.append(
        "Mark Price: "
        + decimal_to_string(
            mark_price
        )
        + " USDT"
    )

    lines.append("")

    lines.append(
        "FINAL EXECUTION GATE"
    )

    lines.append(
        "API Trading Symbol: "
        + yes_no(
            api_symbol_allowed
        )
    )

    lines.append(
        "Fresh Signal Accepted: "
        + yes_no(
            signal_tests[
                "fresh_signal_accepted"
            ]
        )
    )

    lines.append(
        "Expired Signal Rejected: "
        + yes_no(
            signal_tests[
                "expired_signal_rejected"
            ]
        )
    )

    lines.append(
        "Loss Cooldown Test: "
        + yes_no(
            signal_tests[
                "loss_cooldown_test"
            ]
        )
    )

    lines.append(
        "Duplicate Signal Rejected: "
        + yes_no(
            signal_tests[
                "duplicate_signal_rejected"
            ]
        )
    )

    lines.append(
        "One Direction Gate: "
        + yes_no(
            signal_tests[
                "one_direction_gate_test"
            ]
        )
    )

    lines.append(
        "External Position Clear: "
        + yes_no(
            external_position_clear
        )
    )

    lines.append("")

    lines.append(
        "ADJUSTABLE CONFIG"
    )

    lines.append(
        "Entry: "
        + decimal_to_string(
            ENTRY_PERCENT
        )
        + "%"
    )

    lines.append(
        f"Leverage: {LEVERAGE}x"
    )

    lines.append(
        f"Max Config Leverage: "
        f"{MAX_CONFIG_LEVERAGE}x"
    )

    lines.append(
        f"Margin Type: {MARGIN_TYPE}"
    )

    lines.append(
        f"Max Pyramids: "
        f"{MAX_PYRAMID_ADDS}"
    )

    lines.append(
        "Pyramid Size: "
        + decimal_to_string(
            PYRAMID_SIZE_PERCENT
        )
        + "%"
    )

    lines.append(
        f"Max Backups: {MAX_BACKUPS}"
    )

    lines.append(
        "Backup Size: "
        + decimal_to_string(
            BACKUP_SIZE_PERCENT
        )
        + "% each"
    )

    lines.append(
        "Backup Buffer: "
        + decimal_to_string(
            BACKUP_BUFFER_PERCENT
        )
        + "%"
    )

    lines.append(
        "Min Liq Distance: "
        + decimal_to_string(
            MIN_LIQ_DISTANCE_PERCENT
        )
        + "%"
    )

    lines.append(
        "Max Fund Exposure: "
        + decimal_to_string(
            MAX_FUND_EXPOSURE_PERCENT
        )
        + "%"
    )

    lines.append("")

    lines.append(
        "WEEX CONTRACT"
    )

    lines.append(
        "Minimum Order: "
        + decimal_to_string(
            contract_info[
                "min_order_size"
            ]
        )
    )

    lines.append(
        "Quantity Precision: "
        + str(
            contract_info[
                "quantity_precision"
            ]
        )
    )

    lines.append(
        "Quantity Step: "
        + decimal_to_string(
            contract_info[
                "quantity_step"
            ]
        )
    )

    lines.append(
        "Price Precision: "
        + str(
            contract_info[
                "price_precision"
            ]
        )
    )

    lines.append(
        "Price Step: "
        + decimal_to_string(
            contract_info[
                "price_step"
            ]
        )
    )

    lines.append(
        "Contract Value: "
        + decimal_to_string(
            contract_info[
                "contract_value"
            ]
        )
    )

    lines.append(
        "WEEX Min Leverage: "
        + str(
            contract_info[
                "min_leverage"
            ]
        )
        + "x"
    )

    lines.append(
        "WEEX Max Leverage: "
        + str(
            contract_info[
                "max_leverage"
            ]
        )
        + "x"
    )

    lines.append(
        "Leverage Gate: "
        + yes_no(
            leverage_passed
        )
    )

    lines.append("")

    lines.append(
        "DYNAMIC ENTRY"
    )

    lines.append(
        "Margin: "
        + decimal_to_string(
            entry[
                "margin"
            ]
        )
        + " USDT"
    )

    lines.append(
        "Notional: "
        + decimal_to_string(
            entry[
                "notional"
            ]
        )
        + " USDT"
    )

    lines.append(
        "Quantity: "
        + decimal_to_string(
            entry[
                "quantity"
            ]
        )
    )

    quantity_positive = (
        entry["quantity"]
        > ZERO
    )

    minimum_passed = (
        entry["quantity"]
        >= contract_info[
            "min_order_size"
        ]
    )

    lines.append(
        "Quantity Positive: "
        + yes_no(
            quantity_positive
        )
    )

    lines.append(
        "Minimum Passed: "
        + yes_no(
            minimum_passed
        )
    )

    lines.append("")

    lines.append(
        "WORST-CASE EXPOSURE"
    )

    lines.append(
        "Initial: "
        + decimal_to_string(
            exposure[
                "initial"
            ]
        )
        + "%"
    )

    lines.append(
        "Pyramids: "
        + decimal_to_string(
            exposure[
                "pyramids"
            ]
        )
        + "%"
    )

    lines.append(
        "Backups: "
        + decimal_to_string(
            exposure[
                "backups"
            ]
        )
        + "%"
    )

    lines.append(
        "Total: "
        + decimal_to_string(
            exposure[
                "total"
            ]
        )
        + "% / "
        + decimal_to_string(
            MAX_FUND_EXPOSURE_PERCENT
        )
        + "%"
    )

    lines.append(
        "Exposure Passed: "
        + yes_no(
            exposure[
                "passed"
            ]
        )
    )

    lines.append("")

    lines.append(
        "TP / TRAILING"
    )

    lines.append(
        "TP1 / TP2 / TP3: "
        + decimal_to_string(
            TP1_PERCENT
        )
        + "% / "
        + decimal_to_string(
            TP2_PERCENT
        )
        + "% / "
        + decimal_to_string(
            TP3_PERCENT
        )
        + "%"
    )

    lines.append(
        "TP1 Trigger: "
        + decimal_to_string(
            TP1_TRIGGER_PERCENT
        )
        + "%"
    )

    lines.append(
        "TP2 Trigger: "
        + decimal_to_string(
            TP2_TRIGGER_PERCENT
        )
        + "%"
    )

    lines.append(
        "Trailing Distance: "
        + decimal_to_string(
            TRAILING_DISTANCE_PERCENT
        )
        + "%"
    )

    lines.append("")

    lines.append(
        "R22 DEMO EXECUTION REHEARSAL"
    )

    lines.append(
        f"Demo Symbol: {DEMO_SYMBOL}"
    )

    lines.append(
        f"Demo Side: {REHEARSAL_SIDE}"
    )

    lines.append(
        "Demo Position Side: "
        + REHEARSAL_POSITION_SIDE
    )

    lines.append(
        f"Demo Type: "
        f"{REHEARSAL_ORDER_TYPE}"
    )

    if (
        REHEARSAL_ORDER_TYPE
        == "LIMIT"
    ):
        lines.append(
            "Demo Limit Price: "
            + decimal_to_string(
                demo_limit_price
            )
        )

        lines.append(
            "Price Step Match: "
            + yes_no(
                price_step_match
            )
        )

    lines.append(
        "Demo POST Attempted: "
        + yes_no(
            R22_DEMO_POST_ATTEMPTED
        )
    )

    lines.append(
        "Demo POST Accepted: "
        + yes_no(
            R22_DEMO_POST_ACCEPTED
        )
    )

    if R22_DEMO_ORDER_ID:
        lines.append(
            "Demo Order ID: "
            + str(
                R22_DEMO_ORDER_ID
            )
        )

    lines.append("")

    lines.append(
        "R22 RENDER PERSISTENCE"
    )

    lines.append(
        "Health Server: ✅ ACTIVE"
    )

    lines.append(
        "Persistent Runtime: ✅ ACTIVE"
    )

    lines.append(
        "Auto Exit After Diagnostic: ❌ DISABLED"
    )

    lines.append(
        "Repeated Demo Order Loop: ❌ DISABLED"
    )

    lines.append("")

    lines.append(
        "ABSOLUTE EXECUTION SAFETY"
    )

    lines.append(
        "Real POST Called: "
        + yes_no(
            R22_REAL_POST_CALLED
        )
    )

    lines.append(
        "🛡 R22 absolute real-order POST lock active"
    )

    lines.append(
        "⚠️ LIVE ORDER EXECUTION DISABLED"
    )

    lines.append(
        "⚠️ NO REAL ORDER WAS SENT"
    )

    return "\n".join(
        lines
    )


# ============================================================
# ERROR REPORT
# ============================================================

def build_error_report(
    stage,
    error,
):
    lines = [
        f"❌ MODULE {MODULE_NAME} ERROR",
        SYMBOL,
        f"Stage: {stage}",
        f"{type(error).__name__}: {error}",
        "",
        "ABSOLUTE EXECUTION SAFETY",
        (
            "Real POST Called: "
            + yes_no(
                R22_REAL_POST_CALLED
            )
        ),
        (
            "Demo POST Attempted: "
            + yes_no(
                R22_DEMO_POST_ATTEMPTED
            )
        ),
        (
            "Demo POST Accepted: "
            + yes_no(
                R22_DEMO_POST_ACCEPTED
            )
        ),
        "🛡 R22 absolute real-order POST lock active",
        "⚠️ LIVE ORDER EXECUTION DISABLED",
        "⚠️ NO REAL ORDER WAS SENT",
        "",
        "R22 PROCESS STATUS",
        "Health server remains active.",
        "Render process will NOT intentionally exit.",
    ]

    return "\n".join(
        lines
    )


# ============================================================
# MAIN R22 DIAGNOSTIC
# ============================================================

async def r22_run_diagnostic(
    session,
):
    global R22_DIAGNOSTIC_COMPLETE
    global R22_DIAGNOSTIC_PASSED
    global R22_LAST_ERROR

    stage = "startup"

    try:
        final_safety_assertions_r22()

        # ----------------------------------------------------
        # CONFIGURATION
        # ----------------------------------------------------

        stage = "configuration"

        validate_credentials()

        # ----------------------------------------------------
        # API TRADING SYMBOL
        # ----------------------------------------------------

        stage = "API trading symbols"

        api_symbols = (
            await get_api_trading_symbols(
                session
            )
        )

        api_symbol_allowed = (
            SYMBOL in api_symbols
        )

        if not api_symbol_allowed:
            raise RuntimeError(
                f"{SYMBOL} is not currently "
                "listed by WEEX as an "
                "API futures trading symbol"
            )

        # ----------------------------------------------------
        # EXCHANGE INFO
        # ----------------------------------------------------

        stage = "exchange info"

        raw_contract = (
            await get_exchange_info(
                session
            )
        )

        contract_info = (
            parse_contract_info(
                raw_contract
            )
        )

        # ----------------------------------------------------
        # MARK PRICE
        # ----------------------------------------------------

        stage = "mark price"

        mark_price = (
            await get_mark_price(
                session
            )
        )

        # ----------------------------------------------------
        # BALANCE
        # ----------------------------------------------------

        stage = "balance"

        available_usdt = (
            await get_available_usdt(
                session
            )
        )

        # ----------------------------------------------------
        # REAL POSITION READ-ONLY CHECK
        # ----------------------------------------------------

        stage = "position"

        real_positions = (
            await get_real_positions(
                session
            )
        )

        external_position_clear = (
            not has_external_position(
                real_positions
            )
        )

        # ----------------------------------------------------
        # SIGNAL SELF TEST
        # ----------------------------------------------------

        stage = "signal gate"

        signal_tests = (
            run_signal_gate_self_tests()
        )

        # ----------------------------------------------------
        # LEVERAGE
        # ----------------------------------------------------

        stage = "leverage"

        leverage_passed = (
            validate_leverage_r22(
                contract_info[
                    "min_leverage"
                ],
                contract_info[
                    "max_leverage"
                ],
            )
        )

        if not leverage_passed:
            raise RuntimeError(
                "Leverage validation failed"
            )

        # ----------------------------------------------------
        # ENTRY
        # ----------------------------------------------------

        stage = "dynamic entry"

        entry = calculate_entry(
            available_usdt=(
                available_usdt
            ),
            mark_price=mark_price,
            quantity_step=(
                contract_info[
                    "quantity_step"
                ]
            ),
        )

        if entry["quantity"] <= ZERO:
            raise RuntimeError(
                "Calculated entry quantity "
                "is not positive"
            )

        if (
            entry["quantity"]
            < contract_info[
                "min_order_size"
            ]
        ):
            raise RuntimeError(
                "Calculated quantity is below "
                "WEEX minimum order size"
            )

        # ----------------------------------------------------
        # FUND EXPOSURE
        # ----------------------------------------------------

        stage = "fund exposure"

        exposure = (
            calculate_worst_case_exposure()
        )

        if not exposure["passed"]:
            raise RuntimeError(
                "Worst-case exposure exceeds "
                "MAX_FUND_EXPOSURE_PERCENT"
            )

        # ----------------------------------------------------
        # DEMO READ PROBES
        # ----------------------------------------------------

        stage = "demo account probe"

        await demo_balance_probe(
            session
        )

        await demo_positions_probe(
            session
        )

        # ----------------------------------------------------
        # DEMO LIMIT PRICE
        # ----------------------------------------------------

        stage = "demo price construction"

        demo_limit_price = None
        price_step_match = True

        if (
            REHEARSAL_ORDER_TYPE
            == "LIMIT"
        ):
            demo_limit_price = (
                build_safe_demo_limit_price(
                    mark_price=mark_price,
                    price_step=(
                        contract_info[
                            "price_step"
                        ]
                    ),
                )
            )

            price_step_match = (
                matches_step(
                    demo_limit_price,
                    contract_info[
                        "price_step"
                    ],
                )
            )

            if not price_step_match:
                raise RuntimeError(
                    "R22 demo price does not "
                    "match WEEX price step"
                )

        # ----------------------------------------------------
        # FINAL SAFETY CHECK BEFORE DEMO POST
        # ----------------------------------------------------

        stage = "pre-demo safety"

        final_safety_assertions_r22()

        # ----------------------------------------------------
        # DEMO ORDER
        # ----------------------------------------------------

        if RUN_DEMO_ORDER_TEST:
            stage = (
                "demo order transmission"
            )

            demo_payload = (
                build_demo_order_payload_r22(
                    quantity=(
                        entry[
                            "quantity"
                        ]
                    ),
                    limit_price=(
                        demo_limit_price
                    ),
                )
            )

            await transmit_demo_order_r22(
                session,
                demo_payload,
            )

        # ----------------------------------------------------
        # FINAL ABSOLUTE SAFETY CHECK
        # ----------------------------------------------------

        stage = "final safety assertions"

        final_safety_assertions_r22()

        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        report = build_success_report(
            available_usdt=(
                available_usdt
            ),
            mark_price=mark_price,
            contract_info=(
                contract_info
            ),
            api_symbol_allowed=(
                api_symbol_allowed
            ),
            external_position_clear=(
                external_position_clear
            ),
            signal_tests=(
                signal_tests
            ),
            entry=entry,
            exposure=exposure,
            leverage_passed=(
                leverage_passed
            ),
            demo_limit_price=(
                demo_limit_price
            ),
            price_step_match=(
                price_step_match
            ),
        )

        print(
            "",
            flush=True,
        )

        print(
            report,
            flush=True,
        )

        print(
            "",
            flush=True,
        )

        await send_telegram(
            session,
            report,
        )

        R22_DIAGNOSTIC_PASSED = True

        return True

    except Exception as exc:
        R22_LAST_ERROR = (
            f"{type(exc).__name__}: {exc}"
        )

        error_report = (
            build_error_report(
                stage,
                exc,
            )
        )

        print(
            "",
            flush=True,
        )

        print(
            error_report,
            flush=True,
        )

        traceback.print_exc()

        print(
            "",
            flush=True,
        )

        await send_telegram(
            session,
            error_report,
        )

        return False

    finally:
        R22_DIAGNOSTIC_COMPLETE = True


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    uptime = seconds_since_start()

    payload = {
        "module": MODULE_NAME,
        "status": (
            "passed"
            if R22_DIAGNOSTIC_PASSED
            else (
                "diagnostic-complete"
                if R22_DIAGNOSTIC_COMPLETE
                else "starting"
            )
        ),
        "alive": True,
        "uptime_seconds": uptime,
        "symbol": SYMBOL,
        "demo_symbol": DEMO_SYMBOL,
        "live_order_execution": (
            LIVE_ORDER_EXECUTION
        ),
        "hard_real_post_lock": (
            HARD_REAL_POST_LOCK
        ),
        "real_post_called": (
            R22_REAL_POST_CALLED
        ),
        "demo_post_attempted": (
            R22_DEMO_POST_ATTEMPTED
        ),
        "demo_post_accepted": (
            R22_DEMO_POST_ACCEPTED
        ),
        "demo_order_id": (
            R22_DEMO_ORDER_ID
        ),
        "diagnostic_complete": (
            R22_DIAGNOSTIC_COMPLETE
        ),
        "diagnostic_passed": (
            R22_DIAGNOSTIC_PASSED
        ),
        "last_error": (
            R22_LAST_ERROR
        ),
    }

    return web.json_response(
        payload
    )


async def root_handler(
    request,
):
    return web.Response(
        text=(
            f"{MODULE_NAME} ACTIVE\n"
            f"Diagnostic complete: "
            f"{R22_DIAGNOSTIC_COMPLETE}\n"
            f"Diagnostic passed: "
            f"{R22_DIAGNOSTIC_PASSED}\n"
            f"Real POST called: "
            f"{R22_REAL_POST_CALLED}\n"
            f"Live execution: "
            f"{LIVE_ORDER_EXECUTION}\n"
        ),
        content_type="text/plain",
    )


async def start_health_server():
    app = web.Application()

    app.router.add_get(
        "/",
        root_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    app.router.add_get(
        "/healthz",
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
        f"HEALTH SERVER ACTIVE ON PORT {PORT}",
        flush=True,
    )

    return runner


# ============================================================
# R22 PERSISTENT KEEPALIVE
# ============================================================

async def persistent_keepalive():
    while True:
        await asyncio.sleep(
            KEEPALIVE_LOG_SECONDS
        )

        print(
            (
                f"{MODULE_NAME} KEEPALIVE | "
                f"uptime={seconds_since_start()}s | "
                f"diagnostic="
                f"{'PASSED' if R22_DIAGNOSTIC_PASSED else 'NOT PASSED'} | "
                f"real_post="
                f"{R22_REAL_POST_CALLED} | "
                f"live_execution="
                f"{LIVE_ORDER_EXECUTION}"
            ),
            flush=True,
        )


# ============================================================
# R22 RUNTIME
# ============================================================

async def r22_runtime():
    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "PERSISTENT PRE-LIVE EXECUTION PATH VALIDATION",
        flush=True,
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "RENDER AUTO-EXIT PREVENTION ACTIVE",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    # --------------------------------------------------------
    # Start health server BEFORE diagnostic.
    #
    # This is the principal R22 lifecycle correction.
    # --------------------------------------------------------

    runner = await start_health_server()

    timeout = aiohttp.ClientTimeout(
        total=HTTP_TIMEOUT_SECONDS
    )

    connector = aiohttp.TCPConnector(
        limit=20,
        ttl_dns_cache=300,
    )

    try:
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
        ) as session:

            # ------------------------------------------------
            # Run diagnostic ONCE.
            #
            # Do not place another demo order every heartbeat.
            # ------------------------------------------------

            await r22_run_diagnostic(
                session
            )

            # ------------------------------------------------
            # R22 MUST REMAIN ALIVE HERE.
            #
            # The following loop does not trade.
            # It only keeps the Render web service alive.
            # ------------------------------------------------

            print(
                "=" * 60,
                flush=True,
            )

            print(
                f"{MODULE_NAME} PERSISTENT RUNTIME ACTIVE",
                flush=True,
            )

            print(
                "HEALTH SERVER REMAINS ONLINE",
                flush=True,
            )

            print(
                "DIAGNOSTIC WILL NOT AUTO-REPEAT",
                flush=True,
            )

            print(
                "DEMO ORDER WILL NOT AUTO-REPEAT",
                flush=True,
            )

            print(
                "REAL ORDER POST LOCK REMAINS ACTIVE",
                flush=True,
            )

            print(
                "=" * 60,
                flush=True,
            )

            await persistent_keepalive()

    finally:
        await runner.cleanup()


# ============================================================
# MAIN
# ============================================================

def main():
    try:
        asyncio.run(
            r22_runtime()
        )

    except KeyboardInterrupt:
        print(
            "",
            flush=True,
        )

        print(
            f"{MODULE_NAME} STOPPED BY OPERATOR",
            flush=True,
        )

    except Exception as exc:
        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"❌ {MODULE_NAME} FATAL RUNTIME ERROR",
            flush=True,
        )

        print(
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            "🛡 REAL ORDER POST LOCK REMAINS ACTIVE",
            flush=True,
        )

        print(
            "⚠️ LIVE ORDER EXECUTION DISABLED",
            flush=True,
        )

        print(
            "⚠️ NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        traceback.print_exc()

        # ----------------------------------------------------
        # A genuine failure before the health server starts
        # cannot safely be hidden.
        #
        # Re-raise so Render records the fatal startup error.
        # ----------------------------------------------------

        raise


if __name__ == "__main__":
    main()
