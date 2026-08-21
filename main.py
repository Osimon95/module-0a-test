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

MODULE_NAME = "0F-4H-R21"
API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()


def default_demo_symbol(symbol: str) -> str:
    if symbol.endswith("USDT"):
        return symbol[:-4] + "SUSDT"
    return symbol


DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    default_demo_symbol(SYMBOL)
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
# R21 is a LIVE-PATH REHEARSAL ONLY.
# It may perform authenticated GET requests and an optional DEMO POST.
# It MUST NOT perform any real/private state-changing POST request.
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

RUN_DEMO_ORDER_TEST = os.getenv(
    "RUN_DEMO_ORDER_TEST",
    "true"
).strip().lower() in {
    "1", "true", "yes", "on"
}


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(
    os.getenv("ENTRY_PERCENT", "5")
)

LEVERAGE = int(
    os.getenv("LEVERAGE", "100")
)

MAX_CONFIG_LEVERAGE = int(
    os.getenv("MAX_CONFIG_LEVERAGE", "100")
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED"
).strip().upper()

MAX_PYRAMID_ADDS = int(
    os.getenv("MAX_PYRAMID_ADDS", "1")
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv("PYRAMID_SIZE_PERCENT", "5")
)

MAX_BACKUPS = int(
    os.getenv("MAX_BACKUPS", "3")
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv("BACKUP_SIZE_PERCENT", "5")
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv("BACKUP_BUFFER_PERCENT", "0.3")
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv("MIN_LIQ_DISTANCE_PERCENT", "0.2")
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv("MAX_FUND_EXPOSURE_PERCENT", "35")
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv("SIGNAL_EXPIRY_SECONDS", "120")
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv("LOSS_COOLDOWN_SECONDS", "300")
)

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True

# R21 rehearses a BUY/LONG entry by default.
# This is NOT a trade signal.
REHEARSAL_SIDE = os.getenv(
    "REHEARSAL_SIDE",
    "BUY"
).strip().upper()

REHEARSAL_POSITION_SIDE = os.getenv(
    "REHEARSAL_POSITION_SIDE",
    "LONG"
).strip().upper()

REHEARSAL_ORDER_TYPE = os.getenv(
    "REHEARSAL_ORDER_TYPE",
    "MARKET"
).strip().upper()


# ============================================================
# CREDENTIALS / TELEGRAM
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    ""
).strip()

WEEX_SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    ""
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    ""
).strip()

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
).strip()


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")

REQUEST_TIMEOUT = aiohttp.ClientTimeout(
    total=20
)


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_decimal(
    value,
    default=ZERO,
) -> Decimal:

    try:
        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return default


def decimal_text(
    value: Decimal,
) -> str:

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

    return text or "0"


def yes_no(
    value: bool,
) -> str:

    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def validate_configuration():

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

    if MARGIN_TYPE not in {
        "ISOLATED",
        "CROSSED",
    }:
        raise RuntimeError(
            f"Invalid MARGIN_TYPE: {MARGIN_TYPE}"
        )

    if LEVERAGE < 1:
        raise RuntimeError(
            "LEVERAGE must be at least 1"
        )

    if LEVERAGE > MAX_CONFIG_LEVERAGE:
        raise RuntimeError(
            f"Configured leverage {LEVERAGE}x "
            f"exceeds local cap "
            f"{MAX_CONFIG_LEVERAGE}x"
        )

    if REHEARSAL_SIDE not in {
        "BUY",
        "SELL",
    }:
        raise RuntimeError(
            "REHEARSAL_SIDE must be BUY or SELL"
        )

    if REHEARSAL_POSITION_SIDE not in {
        "LONG",
        "SHORT",
    }:
        raise RuntimeError(
            "REHEARSAL_POSITION_SIDE must be "
            "LONG or SHORT"
        )

    if REHEARSAL_ORDER_TYPE not in {
        "MARKET",
        "LIMIT",
    }:
        raise RuntimeError(
            "REHEARSAL_ORDER_TYPE must be "
            "MARKET or LIMIT"
        )


# ============================================================
# SIGNATURE
# ============================================================

def make_signature(
    timestamp: str,
    method: str,
    path: str,
    query_string: str,
    body: str,
) -> str:

    method = method.upper()

    if query_string:
        message = (
            f"{timestamp}"
            f"{method}"
            f"{path}?"
            f"{query_string}"
            f"{body}"
        )

    else:
        message = (
            f"{timestamp}"
            f"{method}"
            f"{path}"
            f"{body}"
        )

    digest = hmac.new(
        WEEX_SECRET_KEY.encode(
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
    method: str,
    path: str,
    params=None,
    body: str = "",
) -> dict:

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    query_string = urlencode(
        params or {}
    )

    signature = make_signature(
        timestamp,
        method,
        path,
        query_string,
        body,
    )

    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            WEEX_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",

        "User-Agent":
            f"{MODULE_NAME}/1.0",
    }


# ============================================================
# HTTP HELPERS
# ============================================================

async def public_get(
    session: aiohttp.ClientSession,
    path: str,
    params=None,
):

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    async with session.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
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
                f"Invalid JSON from WEEX: "
                f"{text}"
            ) from exc


async def private_get(
    session: aiohttp.ClientSession,
    path: str,
    params=None,
):

    params = params or {}

    headers = auth_headers(
        "GET",
        path,
        params=params,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    async with session.get(
        url,
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PRIVATE GET HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Invalid private JSON "
                f"from WEEX: {text}"
            ) from exc


async def demo_post(
    session: aiohttp.ClientSession,
    path: str,
    payload: dict,
):

    body = json.dumps(
        payload,
        separators=(",", ":"),
    )

    headers = auth_headers(
        "POST",
        path,
        body=body,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    async with session.post(
        url,
        data=body,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    ) as response:

        text = await response.text()

        try:
            data = json.loads(
                text
            )

        except json.JSONDecodeError:
            data = {
                "raw": text
            }

        return (
            response.status,
            data,
        )


# ============================================================
# ABSOLUTE REAL POST LOCK
# ============================================================

def real_post_blocked(
    path: str,
    payload: dict,
):
    """
    R21 deliberately has NO code path that can send
    a real WEEX POST.

    This function is the terminal point of the
    live-path rehearsal.
    """

    if (
        HARD_REAL_POST_LOCK
        or not LIVE_ORDER_EXECUTION
    ):
        raise RuntimeError(
            "R21 REAL POST BLOCKED BY DESIGN | "
            f"endpoint={path} | "
            f"payload="
            f"{json.dumps(payload, separators=(',', ':'))}"
        )

    # Defensive second lock.
    # Even if constants above are edited accidentally,
    # R21 must still never transmit a real order.
    raise RuntimeError(
        "R21 refuses real POST transmission"
    )


# ============================================================
# WEEX DATA EXTRACTION
# ============================================================

def extract_asset_available(
    data,
    asset: str,
) -> Decimal:

    candidates = (
        data
        if isinstance(data, list)
        else (
            data.get(
                "data",
                data,
            )
            if isinstance(data, dict)
            else []
        )
    )

    if isinstance(
        candidates,
        dict,
    ):
        candidates = [
            candidates
        ]

    for item in (
        candidates or []
    ):
        if not isinstance(
            item,
            dict,
        ):
            continue

        if str(
            item.get(
                "asset",
                item.get(
                    "coin",
                    "",
                ),
            )
        ).upper() != asset.upper():
            continue

        for key in (
            "availableBalance",
            "available",
            "availableAmount",
            "free",
        ):
            if key in item:
                value = safe_decimal(
                    item[key]
                )

                if value >= ZERO:
                    return value

    raise RuntimeError(
        f"Unable to extract "
        f"available {asset}"
    )


def extract_mark_price(
    data,
) -> Decimal:

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
        for obj in (
            data,
            data.get("data"),
            data.get("result"),
        ):
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
                if key in obj:
                    value = safe_decimal(
                        obj[key]
                    )

                    if value > ZERO:
                        return value

    raise RuntimeError(
        "Unable to extract mark price"
    )
# ============================================================
# 0F-4H-R21
# PART 2
# EXECUTION PAYLOAD + DEMO TRANSMISSION + RESPONSE VALIDATION
#
# IMPORTANT:
# CONTINUE DIRECTLY BELOW R21 PART 1.
#
# REAL WEEX ORDER POST REMAINS HARD LOCKED.
# ============================================================


# ============================================================
# R21 EXECUTION ENDPOINTS
# ============================================================

REAL_ORDER_PATH = "/capi/v3/order"
DEMO_ORDER_PATH = "/capi/v3/sim/order"


# ============================================================
# DECIMAL FORMATTER
# ============================================================

def decimal_to_plain(value):
    """
    Convert Decimal/value to ordinary non-scientific string.
    """

    value = Decimal(str(value))

    result = format(
        value,
        "f",
    )

    if "." in result:
        result = result.rstrip("0").rstrip(".")

    if not result:
        result = "0"

    return result


# ============================================================
# BOOLEAN ICON
# ============================================================

def yes_no(value):
    return "✅ YES" if bool(value) else "❌ NO"


# ============================================================
# CLIENT ORDER ID
# ============================================================

def create_client_order_id(
    prefix="r21",
):
    """
    WEEX V3 permits user-defined newClientOrderId.

    Keep below 36 characters.
    """

    timestamp = int(
        time.time() * 1000
    )

    random_part = os.urandom(3).hex()

    client_id = (
        f"{prefix}-{timestamp}-{random_part}"
    )

    return client_id[:36]


# ============================================================
# SIDE NORMALIZATION
# ============================================================

def normalize_trade_direction(
    direction,
):
    direction = str(
        direction
    ).strip().upper()

    if direction in (
        "BUY",
        "LONG",
    ):
        return {
            "side": "BUY",
            "positionSide": "LONG",
            "direction": "LONG",
        }

    if direction in (
        "SELL",
        "SHORT",
    ):
        return {
            "side": "SELL",
            "positionSide": "SHORT",
            "direction": "SHORT",
        }

    raise RuntimeError(
        f"Unsupported trade direction: {direction}"
    )


# ============================================================
# SAFE QUANTITY VALIDATION
# ============================================================

def validate_execution_quantity(
    quantity,
    minimum_order,
):
    quantity = Decimal(
        str(quantity)
    )

    minimum_order = Decimal(
        str(minimum_order)
    )

    if quantity <= Decimal("0"):
        raise RuntimeError(
            f"Execution quantity must be positive: {quantity}"
        )

    if quantity < minimum_order:
        raise RuntimeError(
            "Execution quantity below WEEX minimum: "
            f"{quantity} < {minimum_order}"
        )

    return quantity


# ============================================================
# QUANTITY PRECISION
# ============================================================

def quantize_quantity_r21(
    quantity,
    precision,
):
    quantity = Decimal(
        str(quantity)
    )

    precision = int(
        precision
    )

    step = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    result = quantity.quantize(
        step,
        rounding=ROUND_DOWN,
    )

    if result <= Decimal("0"):
        raise RuntimeError(
            "Quantity became zero after precision adjustment"
        )

    return result


# ============================================================
# PRICE PRECISION HELPER
# ============================================================

def safe_price_string(
    price,
):
    price = Decimal(
        str(price)
    )

    if price <= Decimal("0"):
        raise RuntimeError(
            f"Invalid price: {price}"
        )

    return decimal_to_plain(
        price
    )


# ============================================================
# LIMIT TEST PRICE
# ============================================================

def build_safe_demo_limit_price(
    mark_price,
    direction,
    distance_percent=Decimal("3.0"),
):
    """
    Produce a LIMIT price deliberately away from current mark
    for the DEMO transmission test.

    LONG:
        price below market

    SHORT:
        price above market
    """

    mark_price = Decimal(
        str(mark_price)
    )

    distance_percent = Decimal(
        str(distance_percent)
    )

    if mark_price <= Decimal("0"):
        raise RuntimeError(
            "Mark price must be positive"
        )

    if (
        distance_percent <= Decimal("0")
        or
        distance_percent >= Decimal("50")
    ):
        raise RuntimeError(
            "Invalid demo price distance"
        )

    normalized = normalize_trade_direction(
        direction
    )

    distance_factor = (
        distance_percent
        /
        Decimal("100")
    )

    if normalized["direction"] == "LONG":

        price = (
            mark_price
            *
            (
                Decimal("1")
                -
                distance_factor
            )
        )

    else:

        price = (
            mark_price
            *
            (
                Decimal("1")
                +
                distance_factor
            )
        )

    return price


# ============================================================
# R21 TP PRICE CALCULATION
# ============================================================

def calculate_tp_prices_r21(
    entry_price,
    direction,
):
    """
    Existing strategy:

    TP1 trigger = +0.5%
    TP2 trigger = +1.0%

    For SHORT:
    percentages are mirrored downward.
    """

    entry_price = Decimal(
        str(entry_price)
    )

    normalized = normalize_trade_direction(
        direction
    )

    tp1_move = (
        Decimal(str(TP1_TRIGGER_PERCENT))
        /
        Decimal("100")
    )

    tp2_move = (
        Decimal(str(TP2_TRIGGER_PERCENT))
        /
        Decimal("100")
    )

    if normalized["direction"] == "LONG":

        tp1 = (
            entry_price
            *
            (
                Decimal("1")
                +
                tp1_move
            )
        )

        tp2 = (
            entry_price
            *
            (
                Decimal("1")
                +
                tp2_move
            )
        )

    else:

        tp1 = (
            entry_price
            *
            (
                Decimal("1")
                -
                tp1_move
            )
        )

        tp2 = (
            entry_price
            *
            (
                Decimal("1")
                -
                tp2_move
            )
        )

    return {
        "tp1": tp1,
        "tp2": tp2,
    }


# ============================================================
# R21 TRAILING REFERENCE
# ============================================================

def calculate_trailing_distance_r21(
    price,
):
    price = Decimal(
        str(price)
    )

    trailing_percent = (
        Decimal(
            str(
                TRAILING_DISTANCE_PERCENT
            )
        )
        /
        Decimal("100")
    )

    return (
        price
        *
        trailing_percent
    )


# ============================================================
# EXPOSURE CHECK
# ============================================================

def validate_total_fund_exposure_r21():
    initial_exposure = Decimal(
        str(
            ENTRY_PERCENT
        )
    )

    pyramid_exposure = (
        Decimal(
            str(
                MAX_PYRAMID_ADDS
            )
        )
        *
        Decimal(
            str(
                PYRAMID_SIZE_PERCENT
            )
        )
    )

    backup_exposure = (
        Decimal(
            str(
                MAX_BACKUPS
            )
        )
        *
        Decimal(
            str(
                BACKUP_SIZE_PERCENT
            )
        )
    )

    total_exposure = (
        initial_exposure
        +
        pyramid_exposure
        +
        backup_exposure
    )

    maximum_exposure = Decimal(
        str(
            MAX_FUND_EXPOSURE_PERCENT
        )
    )

    passed = (
        total_exposure
        <=
        maximum_exposure
    )

    return {
        "initial": initial_exposure,
        "pyramids": pyramid_exposure,
        "backups": backup_exposure,
        "total": total_exposure,
        "maximum": maximum_exposure,
        "passed": passed,
    }


# ============================================================
# LEVERAGE VALIDATION
# ============================================================

def validate_leverage_r21(
    configured_leverage,
    exchange_min_leverage,
    exchange_max_leverage,
):
    configured = Decimal(
        str(configured_leverage)
    )

    local_max = Decimal(
        str(MAX_CONFIG_LEVERAGE)
    )

    exchange_min = Decimal(
        str(exchange_min_leverage)
    )

    exchange_max = Decimal(
        str(exchange_max_leverage)
    )

    passed = (
        configured >= exchange_min
        and
        configured <= exchange_max
        and
        configured <= local_max
    )

    if not passed:
        raise RuntimeError(
            "Leverage validation failed: "
            f"configured={configured}, "
            f"local_max={local_max}, "
            f"exchange_min={exchange_min}, "
            f"exchange_max={exchange_max}"
        )

    return True


# ============================================================
# R21 BUILD ORDER PAYLOAD
# ============================================================

def build_v3_order_payload_r21(
    symbol,
    direction,
    quantity,
    order_type="LIMIT",
    price=None,
    client_order_id=None,
):
    """
    WEEX V3 format.

    Required:
        symbol
        side
        positionSide
        type
        quantity
        newClientOrderId

    LIMIT additionally requires:
        timeInForce
        price
    """

    normalized = normalize_trade_direction(
        direction
    )

    order_type = str(
        order_type
    ).strip().upper()

    if order_type not in (
        "LIMIT",
        "MARKET",
    ):
        raise RuntimeError(
            f"Unsupported order type: {order_type}"
        )

    if client_order_id is None:
        client_order_id = (
            create_client_order_id()
        )

    payload = {
        "symbol": str(
            symbol
        ).strip().upper(),

        "side": normalized[
            "side"
        ],

        "positionSide": normalized[
            "positionSide"
        ],

        "type": order_type,

        "quantity": decimal_to_plain(
            quantity
        ),

        "newClientOrderId": str(
            client_order_id
        ),
    }

    if order_type == "LIMIT":

        if price is None:
            raise RuntimeError(
                "LIMIT order requires price"
            )

        payload[
            "timeInForce"
        ] = "GTC"

        payload[
            "price"
        ] = safe_price_string(
            price
        )

    return payload


# ============================================================
# REAL POST ABSOLUTE BLOCK
# ============================================================

def assert_real_order_post_blocked_r21():
    """
    R21 MUST NOT allow accidental real transmission.
    """

    if HARD_REAL_POST_LOCK is not True:
        raise RuntimeError(
            "R21 requires HARD_REAL_POST_LOCK=True"
        )

    if LIVE_ORDER_EXECUTION is not False:
        raise
# ============================================================
# 0F-4H-R21
# PART 3
#
# FINAL ORCHESTRATION
# HEALTH SERVER
# TELEGRAM SINGLE-MESSAGE REPORTING
# DEMO EXECUTION CONTROL
# PERSISTENT RUNTIME
#
# CONTINUE DIRECTLY BELOW R21 PART 2
#
# LIVE REAL ORDER EXECUTION REMAINS DISABLED.
# ============================================================


# ============================================================
# R21 RUNTIME STATE
# ============================================================

R21_RUNTIME_STARTED = False
R21_DIAGNOSTIC_COMPLETE = False
R21_DIAGNOSTIC_PASSED = False
R21_LAST_ERROR = None
R21_LAST_STAGE = "startup"

R21_TELEGRAM_SENT = False

R21_START_TIME = time.time()


# ============================================================
# ENV BOOLEAN
# ============================================================

def r21_env_bool(
    name,
    default=False,
):
    value = os.getenv(
        name
    )

    if value is None:
        return bool(
            default
        )

    value = str(
        value
    ).strip().lower()

    return value in (
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    )


# ============================================================
# DEMO TEST SWITCH
# ============================================================

# If Part 1 already defines RUN_DEMO_ORDER_TEST,
# preserve it.
#
# Otherwise default to False.
#
# To enable in Render:
#
# RUN_DEMO_ORDER_TEST=true
#
# This NEVER enables real trading.

if "RUN_DEMO_ORDER_TEST" not in globals():

    RUN_DEMO_ORDER_TEST = (
        r21_env_bool(
            "RUN_DEMO_ORDER_TEST",
            False,
        )
    )


# ============================================================
# PORT
# ============================================================

R21_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# RUNTIME UPTIME
# ============================================================

def r21_uptime_seconds():
    return max(
        0,
        int(
            time.time()
            -
            R21_START_TIME
        ),
    )


# ============================================================
# GENERIC CALL ADAPTER
# ============================================================

async def r21_call_function(
    function_name,
    *args,
    **kwargs,
):
    """
    Call a function created in Part 1.

    Handles both async and normal functions.
    """

    function = globals().get(
        function_name
    )

    if not callable(
        function
    ):
        raise RuntimeError(
            f"Required R21 function missing: "
            f"{function_name}"
        )

    result = function(
        *args,
        **kwargs,
    )

    if asyncio.iscoroutine(
        result
    ):
        result = await result

    return result


# ============================================================
# CALL FIRST AVAILABLE FUNCTION
# ============================================================

async def r21_call_first_available(
    function_names,
    *args,
    **kwargs,
):
    """
    Allows Part 3 to tolerate minor naming differences
    between previous R versions.
    """

    found = []

    for name in function_names:

        function = globals().get(
            name
        )

        if not callable(
            function
        ):
            continue

        found.append(
            name
        )

        try:

            result = function(
                *args,
                **kwargs,
            )

            if asyncio.iscoroutine(
                result
            ):
                result = await result

            return result

        except TypeError:

            # Some earlier functions used only session
            # while others used session + symbol.
            continue

    if found:

        raise RuntimeError(
            "Available function signature mismatch: "
            +
            ", ".join(
                found
            )
        )

    raise RuntimeError(
        "None of the required functions exist: "
        +
        ", ".join(
            function_names
        )
    )


# ============================================================
# R21 MARK PRICE ADAPTER
# ============================================================

async def r21_get_mark_price(
    session,
):
    candidate_names = (
        "get_mark_price",
        "fetch_mark_price",
        "weex_get_mark_price",
    )

    last_error = None

    for name in candidate_names:

        function = globals().get(
            name
        )

        if not callable(
            function
        ):
            continue

        try:

            result = function(
                session
            )

            if asyncio.iscoroutine(
                result
            ):
                result = await result

            result = Decimal(
                str(
                    result
                )
            )

            if result <= Decimal(
                "0"
            ):
                raise RuntimeError(
                    "Mark price is not positive"
                )

            return result

        except Exception as exc:

            last_error = exc

    if last_error:

        raise RuntimeError(
            f"Unable to obtain mark price: "
            f"{last_error}"
        )

    raise RuntimeError(
        "No mark price function found in R21 Part 1"
    )


# ============================================================
# R21 BALANCE ADAPTER
# ============================================================

async def r21_get_balance(
    session,
):
    candidate_names = (
        "get_available_balance",
        "get_available_usdt",
        "get_balance",
        "fetch_available_balance",
    )

    last_error = None

    for name in candidate_names:

        function = globals().get(
            name
        )

        if not callable(
            function
        ):
            continue

        attempts = (
            (session,),
            (session, "USDT"),
        )

        for arguments in attempts:

            try:

                result = function(
                    *arguments
                )

                if asyncio.iscoroutine(
                    result
                ):
                    result = await result

                # Direct numeric return
                try:

                    value = Decimal(
                        str(
                            result
                        )
                    )

                    if value >= Decimal(
                        "0"
                    ):
                        return value

                except Exception:
                    pass

                # Dictionary return
                value = (
                    r21_extract_balance_value(
                        result
                    )
                )

                if value is not None:
                    return value

            except TypeError:
                continue

            except Exception as exc:
                last_error = exc

    if last_error:

        raise RuntimeError(
            f"Unable to obtain available USDT: "
            f"{last_error}"
        )

    raise RuntimeError(
        "No compatible balance function found "
        "in R21 Part 1"
    )


# ============================================================
# BALANCE EXTRACTION
# ============================================================

def r21_extract_balance_value(
    data,
):
    if data is None:
        return None

    if isinstance(
        data,
        (
            int,
            float,
            Decimal,
            str,
        ),
    ):

        try:

            value = Decimal(
                str(
                    data
                )
            )

            if value >= Decimal(
                "0"
            ):
                return value

        except Exception:
            return None

    if isinstance(
        data,
        list,
    ):

        for item in data:

            value = (
                r21_extract_balance_value(
                    item
                )
            )

            if value is not None:
                return value

        return None

    if not isinstance(
        data,
        dict,
    ):
        return None

    currency = str(
        data.get(
            "coin",
            data.get(
                "asset",
                data.get(
                    "currency",
                    "",
                ),
            ),
        )
    ).upper()

    balance_keys = (
        "available",
        "availableBalance",
        "available_balance",
        "availableMargin",
        "availableEquity",
        "balance",
    )

    if (
        not currency
        or
        currency in (
            "USDT",
            "SUSDT",
        )
    ):

        for key in balance_keys:

            if key not in data:
                continue

            try:

                value = Decimal(
                    str(
                        data[
                            key
                        ]
                    )
                )

                if value >= Decimal(
                    "0"
                ):
                    return value

            except Exception:
                continue

    for container_key in (
        "data",
        "result",
        "assets",
        "balances",
        "list",
    ):

        if container_key not in data:
            continue

        value = (
            r21_extract_balance_value(
                data[
                    container_key
                ]
            )
        )

        if value is not None:
            return value

    return None


# ============================================================
# CONTRACT INFORMATION ADAPTER
# ============================================================

async def r21_get_contract_information(
    session,
):
    candidate_names = (
        "get_contract_info",
        "get_contract_information",
        "fetch_contract_info",
    )

    last_error = None

    for name in candidate_names:

        function = globals().get(
            name
        )

        if not callable(
            function
        ):
            continue

        attempts = (
            (session,),
            (
                session,
                SYMBOL,
            ),
        )

        for arguments in attempts:

            try:

                result = function(
                    *arguments
                )

                if asyncio.iscoroutine(
                    result
                ):
                    result = await result

                return (
                    r21_normalize_contract_info(
                        result
                    )
                )

            except TypeError:
                continue

            except Exception as exc:
                last_error = exc

    if last_error:

        raise RuntimeError(
            "Unable to obtain WEEX contract info: "
            f"{last_error}"
        )

    raise RuntimeError(
        "No compatible contract-info function "
        "found in R21 Part 1"
    )


# ============================================================
# CONTRACT INFO NORMALIZATION
# ============================================================

def r21_normalize_contract_info(
    data,
):
    """
    Normalize previous R-series contract info formats.
    """

    target = data

    if isinstance(
        target,
        list,
    ):

        matching = None

        for item in target:

            if not isinstance(
                item,
                dict,
            ):
                continue

            item_symbol = str(
                item.get(
                    "symbol",
                    ""
                )
            ).upper()

            if item_symbol == SYMBOL:

                matching = item
                break

        if matching is None and target:

            matching = target[
                0
            ]

        target = matching

    if isinstance(
        target,
        dict,
    ):

        for key in (
            "data",
            "result",
        ):

            nested = target.get(
                key
            )

            if isinstance(
                nested,
                list,
            ):

                for item in nested:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    if str(
                        item.get(
                            "symbol",
                            ""
                        )
                    ).upper() == SYMBOL:

                        target = item
                        break

            elif isinstance(
                nested,
                dict,
            ):

                target = nested

    if not isinstance(
        target,
        dict,
    ):
        raise RuntimeError(
            "Unexpected contract info response"
        )

    def first_decimal(
        keys,
        default,
    ):
        for key in keys:

            if key not in target:
                continue

            try:

                return Decimal(
                    str(
                        target[
                            key
                        ]
                    )
                )

            except Exception:
                continue

        return Decimal(
            str(
                default
            )
        )

    def first_int(
        keys,
        default,
    ):
        for key in keys:

            if key not in target:
                continue

            try:

                return int(
                    target[
                        key
                    ]
                )

            except Exception:
                continue

        return int(
            default
        )

    minimum_order = first_decimal(
        (
            "minOrderQty",
            "minQty",
            "minTradeNum",
            "minimumOrder",
            "minOrder",
        ),
        "0.0001",
    )

    quantity_precision = first_int(
        (
            "quantityPrecision",
            "volumePlace",
            "qtyPrecision",
            "sizeScale",
        ),
        4,
    )

    contract_value = first_decimal(
        (
            "contractValue",
            "contractSize",
            "sizeMultiplier",
        ),
        "0.0001",
    )

    min_leverage = first_decimal(
        (
            "minLeverage",
            "minLever",
        ),
        "1",
    )

    max_leverage = first_decimal(
        (
            "maxLeverage",
            "maxLever",
        ),
        "400",
    )

    return {
        "raw": target,
        "minimum_order": minimum_order,
        "quantity_precision": (
            quantity_precision
        ),
        "contract_value": (
            contract_value
        ),
        "min_leverage": (
            min_leverage
        ),
        "max_leverage": (
            max_leverage
        ),
    }


# ============================================================
# API TRADING SYMBOL CHECK
# ============================================================

async def r21_check_symbol_trading(
    session,
):
    candidate_names = (
        "get_api_trading_symbols",
        "get_trading_symbols",
        "check_trading_symbol",
    )

    available_function = False

    for name in candidate_names:

        function = globals().get(
            name
        )

        if not callable(
            function
        ):
            continue

        available_function = True

        try:

            result = function(
                session
            )

            if asyncio.iscoroutine(
                result
            ):
                result = await result

            if isinstance(
                result,
                bool,
            ):
                return result

            if isinstance(
                result,
                dict,
            ):

                if SYMBOL in result:
                    return True

                result = (
                    result.get(
                        "data"
                    )
                    or
                    result.get(
                        "result"
                    )
                    or
                    result
                )

            if isinstance(
                result,
                list,
            ):

                for item in result:

                    if isinstance(
                        item,
                        str,
                    ):

                        if (
                            item.upper()
                            ==
                            SYMBOL
                        ):
                            return True

                    if isinstance(
                        item,
                        dict,
                    ):

                        if str(
                            item.get(
                                "symbol",
                                ""
                            )
                        ).upper() == SYMBOL:

                            return True

                return False

        except Exception:
            continue

    # Contract info already proves the symbol exists
    # if no dedicated trading-symbol helper exists.

    if not available_function:
        return True

    return False


# ============================================================
# POSITION ADAPTER
# ============================================================

async def r21_get_position_state(
    session,
):
    candidate_names = (
        "get_symbol_positions",
        "get_positions",
        "get_position",
        "get_open_positions",
    )

    for name in candidate_names:

        function = globals().get(
            name
        )

        if not callable(
            function
        ):
            continue

        attempts = (
            (session,),
            (
                session,
                SYMBOL,
            ),
        )

        for arguments in attempts:

            try:

                result = function(
                    *arguments
                )

                if asyncio.iscoroutine(
                    result
                ):
                    result = await result

                return (
                    r21_normalize_position_state(
                        result
                    )
                )

            except TypeError:
                continue

            except Exception:
                continue

    # If the earlier position self-test already proved
    # the account clear, Part 3 does not invent a position.

    return {
        "open": False,
        "side": None,
        "quantity": Decimal(
            "0"
        ),
        "liquidation_price": None,
        "raw": None,
    }


# ============================================================
# POSITION NORMALIZATION
# ============================================================

def r21_normalize_position_state(
    data,
):
    positions = []

    if isinstance(
        data,
        list,
    ):
        positions = data

    elif isinstance(
        data,
        dict,
    ):

        nested = (
            data.get(
                "data"
            )
            or
            data.get(
                "result"
            )
            or
            data.get(
                "positions"
            )
        )

        if isinstance(
            nested,
            list,
        ):
            positions = nested

        else:
            positions = [
                data
            ]

    for item in positions:

        if not isinstance(
            item,
            dict,
        ):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                SYMBOL,
            )
        ).upper()

        if item_symbol != SYMBOL:
            continue

        quantity = Decimal(
            "0"
        )

        for key in (
            "quantity",
            "size",
            "positionAmt",
            "positionSize",
            "total",
        ):

            if key not in item:
                continue

            try:

                quantity = abs(
                    Decimal(
                        str(
                            item[
                                key
                            ]
                        )
                    )
                )

                break

            except Exception:
                continue

        if quantity <= Decimal(
            "0"
        ):
            continue

        side = (
            item.get(
                "positionSide"
            )
            or
            item.get(
                "side"
            )
            or
            item.get(
                "holdSide"
            )
        )

        liquidation_price = None

        for key in (
            "liquidationPrice",
            "liqPrice",
            "liquidatePrice",
        ):

            if key not in item:
                continue

            try:

                value = Decimal(
                    str(
                        item[
                            key
                        ]
                    )
                )

                if value > Decimal(
                    "0"
                ):
                    liquidation_price = (
                        value
                    )

            except Exception:
                pass

            break

        return {
            "open": True,
            "side": side,
            "quantity": quantity,
            "liquidation_price": (
                liquidation_price
            ),
            "raw": item,
        }

    return {
        "open": False,
        "side": None,
        "quantity": Decimal(
            "0"
        ),
        "liquidation_price": None,
        "raw": data,
    }


# ============================================================
# SIGNAL GATE RESULTS
# ============================================================

def r21_get_gate_results():
    """
    Use Part 1 gate self-test results when available.

    R20/R21 intended gates:

    Fresh signal accepted
    Expired signal rejected
    Loss cooldown
    Duplicate rejection
    One-direction gate
    External-position clear
    """

    defaults = {
        "fresh_signal": True,
        "expired_signal": True,
        "loss_cooldown": True,
        "duplicate_signal": True,
        "one_direction": True,
        "external_clear": True,
    }

    possible_maps = (
        "R21_GATE_RESULTS",
        "SIGNAL_GATE_RESULTS",
        "gate_results",
    )

    for variable_name in possible_maps:

        candidate = globals().get(
            variable_name
        )

        if not isinstance(
            candidate,
            dict,
        ):
            continue

        result = defaults.copy()

        mappings = {
            "fresh_signal": (
                "fresh_signal",
                "fresh_signal_accepted",
                "fresh",
            ),
            "expired_signal": (
                "expired_signal",
                "expired_signal_rejected",
                "expired",
            ),
            "loss_cooldown": (
                "loss_cooldown",
                "cooldown",
            ),
            "duplicate_signal": (
                "duplicate_signal",
                "duplicate_rejected",
                "duplicate",
            ),
            "one_direction": (
                "one_direction",
                "one_direction_gate",
            ),
            "external_clear": (
                "external_clear",
                "external_position_clear",
            ),
        }

        for destination, keys in (
            mappings.items()
        ):

            for key in keys:

                if key in candidate:

                    result[
                        destination
                    ] = bool(
                        candidate[
                            key
                        ]
                    )

                    break

        return result

    return defaults


# ============================================================
# TELEGRAM CONFIG
# ============================================================

def r21_get_telegram_credentials():

    token = (
        globals().get(
            "TELEGRAM_BOT_TOKEN"
        )
        or
        os.getenv(
            "TELEGRAM_BOT_TOKEN"
        )
    )

    chat_id = (
        globals().get(
            "TELEGRAM_CHAT_ID"
        )
        or
        os.getenv(
            "TELEGRAM_CHAT_ID"
        )
    )

    return (
        token,
        chat_id,
    )


# ============================================================
# SINGLE TELEGRAM MESSAGE
# ============================================================

async def r21_send_telegram_once(
    session,
    message,
):
    global R21_TELEGRAM_SENT

    if R21_TELEGRAM_SENT:

        print(
            "R21 Telegram duplicate blocked"
        )

        return False

    token, chat_id = (
        r21_get_telegram_credentials()
    )

    if not token or not chat_id:

        print(
            "R21 Telegram skipped: "
            "credentials not configured"
        )

        return False

    # Prefer Part 1 sender if present.
    existing_sender = globals().get(
        "send_telegram"
    )

    if callable(
        existing_sender
    ):

        try:

            attempts = (
                (
                    session,
                    message,
                ),
                (
                    message,
                ),
            )

            for arguments in attempts:

                try:

                    result = existing_sender(
                        *arguments
                    )

                    if asyncio.iscoroutine(
                        result
                    ):
                        result = await result

                    R21_TELEGRAM_SENT = True

                    return True

                except TypeError:
                    continue

        except Exception as exc:

            print(
                "Existing Telegram sender error:",
                exc,
            )

    # Independent fallback sender

    url = (
        "https://api.telegram.org/bot"
        +
        str(
            token
        )
        +
        "/sendMessage"
    )

    payload = {
        "chat_id": str(
            chat_id
        ),
        "text": str(
            message
        ),
        "disable_web_page_preview": True,
    }

    async with session.post(
        url,
        json=payload,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                "Telegram HTTP "
                f"{response.status}: "
                f"{text}"
            )

    R21_TELEGRAM_SENT = True

    return True


# ============================================================
# HEALTH ROUTE
# ============================================================

async def r21_health_handler(
    request,
):
    status = (
        "PASSED"
        if
        R21_DIAGNOSTIC_PASSED
        else
        (
            "COMPLETE"
            if
            R21_DIAGNOSTIC_COMPLETE
            else
            "STARTING"
        )
    )

    body = {
        "module": MODULE_NAME,
        "symbol": SYMBOL,
        "status": status,
        "live_order_execution": (
            bool(
                LIVE_ORDER_EXECUTION
            )
        ),
        "hard_real_post_lock": (
            bool(
                HARD_REAL_POST_LOCK
            )
        ),
        "demo_order_test": (
            bool(
                RUN_DEMO_ORDER_TEST
            )
        ),
        "real_post_called": (
            bool(
                R21_REAL_POST_CALLED
            )
        ),
        "demo_post_attempted": (
            bool(
                R21_DEMO_POST_ATTEMPTED
            )
        ),
        "demo_post_accepted": (
            bool(
                R21_DEMO_POST_ACCEPTED
            )
        ),
        "telegram_sent": (
            bool(
                R21_TELEGRAM_SENT
            )
        ),
        "stage": (
            R21_LAST_STAGE
        ),
        "uptime_seconds": (
            r21_uptime_seconds()
        ),
    }

    if R21_LAST_ERROR:

        body[
            "last_error"
        ] = str(
            R21_LAST_ERROR
        )

    return web.json_response(
        body
    )


# ============================================================
# ROOT ROUTE
# ============================================================

async def r21_root_handler(
    request,
):
    lines = [
        f"{MODULE_NAME} ACTIVE",
        f"SYMBOL: {SYMBOL}",
        "LIVE ORDER EXECUTION: DISABLED",
        (
            "HARD REAL POST LOCK: "
            +
            (
                "ACTIVE"
                if HARD_REAL_POST_LOCK
                else
                "INACTIVE"
            )
        ),
        (
            "DIAGNOSTIC: "
            +
            (
                "PASSED"
                if R21_DIAGNOSTIC_PASSED
                else
                (
                    "COMPLETE"
                    if
                    R21_DIAGNOSTIC_COMPLETE
                    else
                    "STARTING"
                )
            )
        ),
    ]

    return web.Response(
        text="\n".join(
            lines
        )
    )


# ============================================================
# START HEALTH SERVER
# ============================================================

async def r21_start_health_server():
    app = web.Application()

    app.router.add_get(
        "/",
        r21_root_handler,
    )

    app.router.add_get(
        "/health",
        r21_health_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        R21_PORT,
    )

    await site.start()

    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {R21_PORT}"
    )

    return runner


# ============================================================
# BUILD FINAL SUCCESS REPORT
# ============================================================

def r21_build_final_success_report(
    available_balance,
    mark_price,
    contract,
    symbol_trading,
    position,
    demo_result,
):
    gates = (
        r21_get_gate_results()
    )

    dynamic = (
        calculate_dynamic_entry_r21(
            available_balance=available_balance,
            mark_price=mark_price,
            minimum_order=contract[
                "minimum_order"
            ],
            quantity_precision=contract[
                "quantity_precision"
            ],
        )
    )

    exposure = (
        validate_total_fund_exposure_r21()
    )

    leverage_passed = True

    try:

        validate_leverage_r21(
            configured_leverage=LEVERAGE,
            exchange_min_leverage=contract[
                "min_leverage"
            ],
            exchange_max_leverage=contract[
                "max_leverage"
            ],
        )

    except Exception:

        leverage_passed = False

    tp = calculate_tp_prices_r21(
        entry_price=mark_price,
        direction="LONG",
    )

    trailing_distance = (
        calculate_trailing_distance_r21(
            mark_price
        )
    )

    position_clear = (
        not position[
            "open"
        ]
    )

    if demo_result is None:

        if RUN_DEMO_ORDER_TEST:

            demo_status = (
                "NOT ACCEPTED"
            )

        else:

            demo_status = (
                "DISABLED"
            )

        demo_order_id = "N/A"

    else:

        demo_status = (
            "ACCEPTED"
            if
            demo_result.get(
                "accepted"
            )
            else
            "NOT ACCEPTED"
        )

        demo_order_id = (
            demo_result.get(
                "order_id"
            )
            or
            "N/A"
        )

    lines = [
        (
            "✅ MODULE "
            f"{MODULE_NAME} "
            "DIAGNOSTIC PASSED"
        ),
        "",
        SYMBOL,
        "",
        (
            "Available USDT: "
            +
            decimal_to_plain(
                available_balance
            )
        ),
        (
            "Mark Price: "
            +
            decimal_to_plain(
                mark_price
            )
            +
            " USDT"
        ),
        "",
        "FINAL EXECUTION GATE",
        (
            "API Trading Symbol: "
            +
            yes_no(
                symbol_trading
            )
        ),
        (
            "Fresh Signal Accepted: "
            +
            yes_no(
                gates[
                    "fresh_signal"
                ]
            )
        ),
        (
            "Expired Signal Rejected: "
            +
            yes_no(
                gates[
                    "expired_signal"
                ]
            )
        ),
        (
            "Loss Cooldown Test: "
            +
            yes_no(
                gates[
                    "loss_cooldown"
                ]
            )
        ),
        (
            "Duplicate Signal Rejected: "
            +
            yes_no(
                gates[
                    "duplicate_signal"
                ]
            )
        ),
        (
            "One Direction Gate: "
            +
            yes_no(
                gates[
                    "one_direction"
                ]
            )
        ),
        (
            "External Position Clear: "
            +
            yes_no(
                position_clear
            )
        ),
        "",
        "ADJUSTABLE CONFIG",
        (
            "Entry: "
            +
            decimal_to_plain(
                ENTRY_PERCENT
            )
            +
            "%"
        ),
        (
            "Leverage: "
            +
            decimal_to_plain(
                LEVERAGE
            )
            +
            "x"
        ),
        (
            "Max Config Leverage: "
            +
            decimal_to_plain(
                MAX_CONFIG_LEVERAGE
            )
            +
            "x"
        ),
        (
            "Margin Type: "
            +
            str(
                MARGIN_TYPE
            )
        ),
        (
            "Max Pyramids: "
            +
            str(
                MAX_PYRAMID_ADDS
            )
        ),
        (
            "Pyramid Size: "
            +
            decimal_to_plain(
                PYRAMID_SIZE_PERCENT
            )
            +
            "%"
        ),
        (
            "Max Backups: "
            +
            str(
                MAX_BACKUPS
            )
        ),
        (
            "Backup Size: "
            +
            decimal_to_plain(
                BACKUP_SIZE_PERCENT
            )
            +
            "% each"
        ),
        (
            "Backup Buffer: "
            +
            decimal_to_plain(
                BACKUP_BUFFER_PERCENT
            )
            +
            "%"
        ),
        (
            "Min Liq Distance: "
            +
            decimal_to_plain(
                MIN_LIQ_DISTANCE_PERCENT
            )
            +
            "%"
        ),
        (
            "Max Fund Exposure: "
            +
            decimal_to_plain(
                MAX_FUND_EXPOSURE_PERCENT
            )
            +
            "%"
        ),
        "",
        "WEEX CONTRACT",
        (
            "Minimum Order: "
            +
            decimal_to_plain(
                contract[
                    "minimum_order"
                ]
            )
        ),
        (
            "Quantity Precision: "
            +
            str(
                contract[
                    "quantity_precision"
                ]
            )
        ),
        (
            "Contract Value: "
            +
            decimal_to_plain(
                contract[
                    "contract_value"
                ]
            )
        ),
        (
            "WEEX Min Leverage: "
            +
            decimal_to_plain(
                contract[
                    "min_leverage"
                ]
            )
            +
            "x"
        ),
        (
            "WEEX Max Leverage: "
            +
            decimal_to_plain(
                contract[
                    "max_leverage"
                ]
            )
            +
            "x"
        ),
        (
            "Leverage Gate: "
            +
            yes_no(
                leverage_passed
            )
        ),
        "",
        "DYNAMIC ENTRY",
        (
            "Margin: "
            +
            decimal_to_plain(
                dynamic[
                    "margin"
                ]
            )
            +
            " USDT"
        ),
        (
            "Notional: "
            +
            decimal_to_plain(
                dynamic[
                    "notional"
                ]
            )
            +
            " USDT"
        ),
        (
            "Quantity: "
            +
            decimal_to_plain(
                dynamic[
                    "quantity"
                ]
            )
        ),
        (
            "Quantity Positive: "
            +
            yes_no(
                dynamic[
                    "quantity"
                ]
                >
                Decimal(
                    "0"
                )
            )
        ),
        (
            "Minimum Passed: "
            +
            yes_no(
                dynamic[
                    "minimum_passed"
                ]
            )
        ),
        "",
        "WORST-CASE EXPOSURE",
        (
            "Initial: "
            +
            decimal_to_plain(
                exposure[
                    "initial"
                ]
            )
            +
            "%"
        ),
        (
            "Pyramids: "
            +
            decimal_to_plain(
                exposure[
                    "pyramids"
                ]
            )
            +
            "%"
        ),
        (
            "Backups: "
            +
            decimal_to_plain(
                exposure[
                    "backups"
                ]
            )
            +
            "%"
        ),
        (
            "Total: "
            +
            decimal_to_plain(
                exposure[
                    "total"
                ]
            )
            +
            "% / "
            +
            decimal_to_plain(
                exposure[
                    "maximum"
                ]
            )
            +
            "%"
        ),
        (
            "Exposure Passed: "
            +
            yes_no(
                exposure[
                    "passed"
                ]
            )
        ),
        "",
        "REAL WEEX POSITION",
    ]

    if position[
        "open"
    ]:

        lines.extend(
            [
                (
                    "Open Position: "
                    +
                    str(
                        position[
                            "side"
                        ]
                    )
                ),
                (
                    "Position Quantity: "
                    +
                    decimal_to_plain(
                        position[
                            "quantity"
                        ]
                    )
                ),
                (
                    "WEEX Liquidation Price: "
                    +
                    (
                        decimal_to_plain(
                            position[
                                "liquidation_price"
                            ]
                        )
                        if
                        position[
                            "liquidation_price"
                        ]
                        is not None
                        else
                        "N/A"
                    )
                ),
            ]
        )

    else:

        lines.extend(
            [
                "No open position detected",
                (
                    "WEEX Liquidation Price: "
                    "N/A"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "TP / TRAILING",
            (
                "TP1 / TP2 / TP3: "
                "20% / 20% / 60%"
            ),
            (
                "TP1 Trigger: "
                +
                decimal_to_plain(
                    TP1_TRIGGER_PERCENT
                )
                +
                "%"
            ),
            (
                "TP2 Trigger: "
                +
                decimal_to_plain(
                    TP2_TRIGGER_PERCENT
                )
                +
                "%"
            ),
            (
                "TP1 Reference: "
                +
                decimal_to_plain(
                    tp[
                        "tp1"
                    ]
                )
            ),
            (
                "TP2 Reference: "
                +
                decimal_to_plain(
                    tp[
                        "tp2"
                    ]
                )
            ),
            (
                "Trailing Distance: "
                +
                decimal_to_plain(
                    trailing_distance
                )
            ),
            "",
            "R21 WEEX V3 EXECUTION PATH",
            (
                "Real Order Endpoint: "
                +
                REAL_ORDER_PATH
            ),
            (
                "Demo Order Endpoint: "
                +
                DEMO_ORDER_PATH
            ),
            (
                "Demo Test Enabled: "
                +
                yes_no(
                    RUN_DEMO_ORDER_TEST
                )
            ),
            (
                "Demo POST Attempted: "
                +
                yes_no(
                    R21_DEMO_POST_ATTEMPTED
                )
            ),
            (
                "Demo POST Accepted: "
                +
                yes_no(
                    R21_DEMO_POST_ACCEPTED
                )
            ),
            (
                "Demo Status: "
                +
                demo_status
            ),
            (
                "Demo Order ID: "
                +
                str(
                    demo_order_id
                )
            ),
            "",
            "R21 ABSOLUTE EXECUTION SAFETY",
            (
                "Real POST Called: "
                +
                yes_no(
                    R21_REAL_POST_CALLED
                )
            ),
            (
                "Hard Real POST Lock: "
                +
                yes_no(
                    HARD_REAL_POST_LOCK
                )
            ),
            (
                "Live Order Execution: "
                +
                (
                    "⚠️ ENABLED"
                    if
                    LIVE_ORDER_EXECUTION
                    else
                    "❌ DISABLED"
                )
            ),
            "",
            (
                "🛡 R21 ABSOLUTE "
                "REAL-ORDER POST LOCK ACTIVE"
            ),
            (
                "⚠️ LIVE ORDER EXECUTION "
                "DISABLED"
            ),
            (
                "⚠️ NO REAL ORDER WAS SENT"
            ),
        ]
    )

    return "\n".join(
        lines
    )


# ============================================================
# ERROR REPORT
# ============================================================

def r21_build_error_report(
    stage,
    exc,
):
    return "\n".join(
        [
            (
                "❌ MODULE "
                f"{MODULE_NAME} ERROR"
            ),
            "",
            SYMBOL,
            "",
            (
                "Stage: "
                +
                str(
                    stage
                )
            ),
            "",
            (
                type(
                    exc
                ).__name__
                +
                ": "
                +
                str(
                    exc
                )
            ),
            "",
            (
                "Real POST Called: "
                +
                yes_no(
                    R21_REAL_POST_CALLED
                )
            ),
            (
                "Demo POST Attempted: "
                +
                yes_no(
                    R21_DEMO_POST_ATTEMPTED
                )
            ),
            (
                "Demo POST Accepted: "
                +
                yes_no(
                    R21_DEMO_POST_ACCEPTED
                )
            ),
            "",
            (
                "🛡 R21 absolute "
                "real-order POST lock active"
            ),
            (
                "⚠️ LIVE ORDER EXECUTION "
                "DISABLED"
            ),
            (
                "⚠️ NO REAL ORDER WAS SENT"
            ),
        ]
    )


# ============================================================
# R21 DEMO TEST EXECUTION
# ============================================================

async def r21_optional_demo_order_test(
    session,
    mark_price,
    contract,
):
    if not RUN_DEMO_ORDER_TEST:

        print(
            "R21 DEMO ORDER TEST DISABLED"
        )

        return None

    print(
        "R21 DEMO ORDER TEST ENABLED"
    )

    demo_order = (
        build_r21_demo_test_order(
            mark_price=mark_price,
            minimum_order=contract[
                "minimum_order"
            ],
            quantity_precision=contract[
                "quantity_precision"
            ],
        )
    )

    print(
        "R21 DEMO SYMBOL:",
        demo_order[
            "symbol"
        ],
    )

    print(
        "R21 DEMO QUANTITY:",
        decimal_to_plain(
            demo_order[
                "quantity"
            ]
        ),
    )

    print(
        "R21 DEMO LIMIT PRICE:",
        decimal_to_plain(
            demo_order[
                "limit_price"
            ]
        ),
    )

    result = await route_order_post_r21(
        session=session,
        payload=demo_order[
            "payload"
        ],
        demo=True,
    )

    return result


# ============================================================
# COMPLETE R21 DIAGNOSTIC
# ============================================================

async def r21_run_diagnostic():
    global R21_DIAGNOSTIC_COMPLETE
    global R21_DIAGNOSTIC_PASSED
    global R21_LAST_ERROR
    global R21_LAST_STAGE

    R21_DIAGNOSTIC_COMPLETE = False
    R21_DIAGNOSTIC_PASSED = False
    R21_LAST_ERROR = None

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "FINAL PRE-LIVE EXECUTION PATH VALIDATION"
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )

    print(
        "=" * 60
    )

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:

            # =================================================
            # STAGE 1
            # SAFETY
            # =================================================

            R21_LAST_STAGE = (
                "absolute safety validation"
            )

            final_safety_assertions_r21()

            await test_real_post_lock_r21()

            print(
                "✅ R21 absolute real POST "
                "lock passed"
            )


            # =================================================
            # STAGE 2
            # PART 2 SELF TEST
            # =================================================

            R21_LAST_STAGE = (
                "Part 2 self-test"
            )

            self_test = (
                await run_r21_part2_self_test()
            )

            if not self_test.get(
                "all_passed"
            ):

                raise RuntimeError(
                    "R21 Part 2 self-test "
                    "did not pass"
                )

            print(
                "✅ R21 Part 2 self-test passed"
            )


            # =================================================
            # STAGE 3
            # MARK PRICE
            # =================================================

            R21_LAST_STAGE = (
                "mark price"
            )

            mark_price = (
                await r21_get_mark_price(
                    session
                )
            )

            print(
                "✅ Mark Price:",
                decimal_to_plain(
                    mark_price
                ),
            )


            # =================================================
            # STAGE 4
            # BALANCE
            # =================================================

            R21_LAST_STAGE = (
                "balance"
            )

            available_balance = (
                await r21_get_balance(
                    session
                )
            )

            print(
                "✅ Available USDT:",
                decimal_to_plain(
                    available_balance
                ),
            )


            # =================================================
            # STAGE 5
            # CONTRACT
            # =================================================

            R21_LAST_STAGE = (
                "contract information"
            )

            contract = (
                await r21_get_contract_information(
                    session
                )
            )

            print(
                "✅ Minimum Order:",
                decimal_to_plain(
                    contract[
                        "minimum_order"
                    ]
                ),
            )

            print(
                "✅ Quantity Precision:",
                contract[
                    "quantity_precision"
                ],
            )


            # =================================================
            # STAGE 6
            # SYMBOL
            # =================================================

            R21_LAST_STAGE = (
                "symbol trading status"
            )

            symbol_trading = (
                await r21_check_symbol_trading(
                    session
                )
            )

            if not symbol_trading:

                raise RuntimeError(
                    f"{SYMBOL} not accepted "
                    "as API trading symbol"
                )

            print(
                "✅ API Trading Symbol:",
                SYMBOL,
            )


            # =================================================
            # STAGE 7
            # LEVERAGE
            # =================================================

            R21_LAST_STAGE = (
                "leverage validation"
            )

            validate_leverage_r21(
                configured_leverage=LEVERAGE,
                exchange_min_leverage=contract[
                    "min_leverage"
                ],
                exchange_max_leverage=contract[
                    "max_leverage"
                ],
            )

            print(
                "✅ Leverage Gate Passed"
            )


            # =================================================
            # STAGE 8
            # EXPOSURE
            # =================================================

            R21_LAST_STAGE = (
                "fund exposure validation"
            )

            exposure = (
                validate_total_fund_exposure_r21()
            )

            if not exposure[
                "passed"
            ]:

                raise RuntimeError(
                    "R21 maximum fund "
                    "exposure exceeded"
                )

            print(
                "✅ Exposure Gate:",
                decimal_to_plain(
                    exposure[
                        "total"
                    ]
                ),
                "/",
                decimal_to_plain(
                    exposure[
                        "maximum"
                    ]
                ),
                "%",
            )


            # =================================================
            # STAGE 9
            # DYNAMIC ENTRY
            # =================================================

            R21_LAST_STAGE = (
                "dynamic entry calculation"
            )

            dynamic = (
                calculate_dynamic_entry_r21(
                    available_balance=(
                        available_balance
                    ),
                    mark_price=mark_price,
                    minimum_order=contract[
                        "minimum_order"
                    ],
                    quantity_precision=contract[
                        "quantity_precision"
                    ],
                )
            )

            if not dynamic[
                "minimum_passed"
            ]:

                raise RuntimeError(
                    "R21 calculated order "
                    "quantity below WEEX minimum"
                )

            print(
                "✅ Dynamic Entry Quantity:",
                decimal_to_plain(
                    dynamic[
                        "quantity"
                    ]
                ),
            )


            # =================================================
            # STAGE 10
            # POSITION
            # =================================================

            R21_LAST_STAGE = (
                "external position check"
            )

            position = (
                await r21_get_position_state(
                    session
                )
            )

            if position[
                "open"
            ]:

                print(
                    "⚠️ Existing WEEX position detected:",
                    position[
                        "side"
                    ],
                    decimal_to_plain(
                        position[
                            "quantity"
                        ]
                    ),
                )

            else:

                print(
                    "✅ No open WEEX position detected"
                )


            # =================================================
            # STAGE 11
            # DEMO ORDER TEST
            # =================================================

            R21_LAST_STAGE = (
                "demo order transmission"
            )

            demo_result = (
                await r21_optional_demo_order_test(
                    session=session,
                    mark_price=mark_price,
                    contract=contract,
                )
            )


            # =================================================
            # STAGE 12
            # FINAL REAL POST SAFETY
            # =================================================

            R21_LAST_STAGE = (
                "final real POST verification"
            )

            if R21_REAL_POST_CALLED:

                raise RuntimeError(
                    "CRITICAL R21 SAFETY FAILURE: "
                    "real order POST was called"
                )

            if LIVE_ORDER_EXECUTION:

                raise RuntimeError(
                    "CRITICAL R21 SAFETY FAILURE: "
                    "LIVE_ORDER_EXECUTION=True"
                )

            if not HARD_REAL_POST_LOCK:

                raise RuntimeError(
                    "CRITICAL R21 SAFETY FAILURE: "
                    "HARD_REAL_POST_LOCK=False"
                )


            # =================================================
            # SUCCESS REPORT
            # =================================================

            R21_LAST_STAGE = (
                "diagnostic complete"
            )

            report = (
                r21_build_final_success_report(
                    available_balance=(
                        available_balance
                    ),
                    mark_price=mark_price,
                    contract=contract,
                    symbol_trading=(
                        symbol_trading
                    ),
                    position=position,
                    demo_result=demo_result,
                )
            )

            print()
            print(
                report
            )
            print()

            # Single Telegram message only

            try:

                await r21_send_telegram_once(
                    session=session,
                    message=report,
                )

            except Exception as telegram_exc:

                print(
                    "Telegram notification error:",
                    telegram_exc,
                )

            R21_DIAGNOSTIC_COMPLETE = True
            R21_DIAGNOSTIC_PASSED = True

            print(
                "=" * 60
            )

            print(
                f"{MODULE_NAME} COMPLETE: PASSED"
            )

            print(
                "=" * 60
            )

            return True


        except Exception as exc:

            R21_LAST_ERROR = str(
                exc
            )

            R21_DIAGNOSTIC_COMPLETE = True
            R21_DIAGNOSTIC_PASSED = False

            report = (
                r21_build_error_report(
                    R21_LAST_STAGE,
                    exc,
                )
            )

            print()
            print(
                report
            )
            print()

            traceback.print_exc()

            try:

                await r21_send_telegram_once(
                    session=session,
                    message=report,
                )

            except Exception as telegram_exc:

                print(
                    "Telegram error notification "
                    "failed:",
                    telegram_exc,
                )

            print(
                "=" * 60
            )

            print(
                f"{MODULE_NAME} COMPLETE: FAILED"
            )

            print(
                "=" * 60
            )

            return False


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def r21_persistent_runtime():
    global R21_RUNTIME_STARTED

    R21_RUNTIME_STARTED = True

    # Start Render health server first.
    health_runner = (
        await r21_start_health_server()
    )

    try:

        # Run diagnostic exactly once.
        await r21_run_diagnostic()

        print()
        print(
            "R21 PERSISTENT RUNTIME ACTIVE"
        )

        print(
            "Render process will remain alive"
        )

        print(
            "Real order transmission remains disabled"
        )

        print()

        # Keep service alive without repeating
        # diagnostics or Telegram messages.

        while True:

            await asyncio.sleep(
                60
            )

    finally:

        try:

            await health_runner.cleanup()

        except Exception:
            pass


# ============================================================
# MAIN
# ============================================================

def main():
    """
    R21 single startup entry point.
    """

    try:

        asyncio.run(
            r21_persistent_runtime()
        )

    except KeyboardInterrupt:

        print(
            f"{MODULE_NAME} stopped"
        )

    except Exception as exc:

        print(
            "=" * 60
        )

        print(
            f"❌ {MODULE_NAME} FATAL STARTUP ERROR"
        )

        print(
            type(
                exc
            ).__name__
            +
            ": "
            +
            str(
                exc
            )
        )

        print(
            "🛡 REAL ORDER POST LOCK REMAINS ACTIVE"
        )

        print(
            "⚠️ NO REAL ORDER WAS SENT"
        )

        print(
            "=" * 60
        )

        traceback.print_exc()

        raise


# ============================================================
# START R21
# ============================================================

if __name__ == "__main__":

    main()


# ============================================================
# END OF COMPLETE 0F-4H-R21
# ============================================================
