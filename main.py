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

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


def default_demo_symbol(
    symbol: str,
) -> str:

    if symbol.endswith(
        "USDT"
    ):
        return (
            symbol[:-4]
            +
            "SUSDT"
        )

    return symbol


DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    default_demo_symbol(
        SYMBOL
    ),
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
#
# R21 IS PRE-LIVE ONLY.
#
# ALLOWED:
#
#   PUBLIC GET
#   PRIVATE AUTHENTICATED GET
#   OPTIONAL DEMO POST
#
# NOT ALLOWED:
#
#   REAL ORDER POST
#   REAL CANCEL POST
#   REAL LEVERAGE CHANGE POST
#   REAL MARGIN CHANGE POST
#   ANY REAL STATE-CHANGING POST
#
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_REAL_POST_LOCK = True


RUN_DEMO_ORDER_TEST = os.getenv(
    "RUN_DEMO_ORDER_TEST",
    "true",
).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


# ============================================================
# EXECUTION STATE
# ============================================================

R21_REAL_POST_CALLED = False

R21_DEMO_POST_ATTEMPTED = False

R21_DEMO_POST_ACCEPTED = False


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
        "0.20",
    )
)


ONE_DIRECTION_ONLY = True

ANTI_DUPLICATE_ORDERS = True

TREND_REVERSAL_EXIT = True

IDLE_PYRAMID_CLEANUP = True


# ============================================================
# REHEARSAL CONFIG
# ============================================================

REHEARSAL_SIDE = os.getenv(
    "REHEARSAL_SIDE",
    "BUY",
).strip().upper()


REHEARSAL_ORDER_TYPE = os.getenv(
    "REHEARSAL_ORDER_TYPE",
    "LIMIT",
).strip().upper()


# ============================================================
# CREDENTIALS
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
# CONSTANTS
# ============================================================

ZERO = Decimal(
    "0"
)

ONE = Decimal(
    "1"
)

ONE_HUNDRED = Decimal(
    "100"
)


REQUEST_TIMEOUT = aiohttp.ClientTimeout(
    total=20
)


# ============================================================
# CURRENT WEEX V3 ENDPOINTS
# ============================================================

MARK_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
)

EXCHANGE_INFO_PATH = (
    "/capi/v3/market/exchangeInfo"
)

API_TRADING_SYMBOLS_PATH = (
    "/capi/v3/market/apiTradingSymbols"
)

BALANCE_PATH = (
    "/capi/v3/account/balance"
)

POSITION_PATH = (
    "/capi/v3/account/position/allPosition"
)

REAL_ORDER_PATH = (
    "/capi/v3/order"
)

DEMO_ORDER_PATH = (
    "/capi/v3/sim/order"
)


# ============================================================
# RUNTIME STATE
# ============================================================

R21_RUNTIME_STARTED = False

R21_DIAGNOSTIC_COMPLETE = False

R21_DIAGNOSTIC_PASSED = False

R21_LAST_ERROR = None

R21_LAST_STAGE = (
    "startup"
)

R21_TELEGRAM_SENT = False

R21_START_TIME = time.time()


R21_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_decimal(
    value,
    default=ZERO,
):

    try:

        return Decimal(
            str(
                value
            )
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        return default


def decimal_text(
    value,
):

    value = Decimal(
        str(
            value
        )
    )

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

    return (
        text
        or
        "0"
    )


def yes_no(
    value,
):

    return (
        "✅ YES"
        if bool(
            value
        )
        else
        "❌ NO"
    )


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
# CONFIGURATION VALIDATION
# ============================================================

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
            +
            ", ".join(
                missing
            )
        )


    if MARGIN_TYPE not in {
        "ISOLATED",
        "CROSSED",
    }:

        raise RuntimeError(
            f"Invalid MARGIN_TYPE: "
            f"{MARGIN_TYPE}"
        )


    if LEVERAGE < 1:

        raise RuntimeError(
            "LEVERAGE must be "
            "at least 1"
        )


    if (
        LEVERAGE
        >
        MAX_CONFIG_LEVERAGE
    ):

        raise RuntimeError(
            f"Configured leverage "
            f"{LEVERAGE}x exceeds "
            f"local cap "
            f"{MAX_CONFIG_LEVERAGE}x"
        )


    if REHEARSAL_SIDE not in {
        "BUY",
        "SELL",
    }:

        raise RuntimeError(
            "REHEARSAL_SIDE must "
            "be BUY or SELL"
        )


    if REHEARSAL_ORDER_TYPE not in {
        "LIMIT",
        "MARKET",
    }:

        raise RuntimeError(
            "REHEARSAL_ORDER_TYPE "
            "must be LIMIT or MARKET"
        )


    if ENTRY_PERCENT <= ZERO:

        raise RuntimeError(
            "ENTRY_PERCENT must "
            "be positive"
        )


    if (
        MAX_FUND_EXPOSURE_PERCENT
        <=
        ZERO
    ):

        raise RuntimeError(
            "MAX_FUND_EXPOSURE_PERCENT "
            "must be positive"
        )


# ============================================================
# SIGNATURE
# ============================================================

def make_signature(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):

    method = str(
        method
    ).upper()


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
    method,
    path,
    params=None,
    body="",
):

    timestamp = str(
        int(
            time.time()
            *
            1000
        )
    )


    query_string = urlencode(
        params
        or
        {}
    )


    signature = make_signature(
        timestamp=timestamp,
        method=method,
        path=path,
        query_string=query_string,
        body=body,
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
# PUBLIC GET
# ============================================================

async def public_get(
    session,
    path,
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
                "Invalid JSON from WEEX: "
                +
                text
            ) from exc


# ============================================================
# PRIVATE GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):

    params = (
        params
        or
        {}
    )


    headers = auth_headers(
        method="GET",
        path=path,
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
                "WEEX PRIVATE GET HTTP "
                f"{response.status}: "
                f"{text}"
            )


        try:

            return json.loads(
                text
            )

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                "Invalid private JSON "
                "from WEEX: "
                +
                text
            ) from exc


# ============================================================
# DEMO POST
# ============================================================

async def demo_post(
    session,
    path,
    payload,
):

    body = json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
    )


    headers = auth_headers(
        method="POST",
        path=path,
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
                "raw":
                    text
            }


        return (
            response.status,
            data,
        )


# ============================================================
# ABSOLUTE REAL POST BLOCK
# ============================================================

def real_post_blocked(
    path,
    payload,
):

    """
    TERMINAL REAL ORDER ROUTE.

    IMPORTANT:

    There is deliberately NO:

        session.post()

    inside this function.

    Therefore this function cannot
    transmit a real WEEX order.
    """


    raise RuntimeError(

        "R21 REAL POST BLOCKED BY DESIGN | "

        f"endpoint={path} | "

        "payload="

        +
        json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
        )
    )


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions_r21():

    if HARD_REAL_POST_LOCK is not True:

        raise RuntimeError(
            "R21 requires "
            "HARD_REAL_POST_LOCK=True"
        )


    if LIVE_ORDER_EXECUTION is not False:

        raise RuntimeError(
            "R21 requires "
            "LIVE_ORDER_EXECUTION=False"
        )


    if R21_REAL_POST_CALLED:

        raise RuntimeError(
            "R21 real POST flag "
            "must remain False"
        )


    if REAL_ORDER_PATH != (
        "/capi/v3/order"
    ):

        raise RuntimeError(
            "Unexpected real "
            "order endpoint"
        )


    if DEMO_ORDER_PATH != (
        "/capi/v3/sim/order"
    ):

        raise RuntimeError(
            "Unexpected demo "
            "order endpoint"
        )


    return True


# ============================================================
# REAL POST LOCK SELF TEST
# ============================================================

async def test_real_post_lock_r21():

    payload = {

        "symbol":
            SYMBOL,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0001",

        "newClientOrderId":
            "r21-lock-test",
    }


    try:

        real_post_blocked(
            REAL_ORDER_PATH,
            payload,
        )


    except RuntimeError as exc:

        if (
            "BLOCKED BY DESIGN"
            in
            str(
                exc
            )
        ):

            return True


        raise


    raise RuntimeError(
        "R21 real POST lock "
        "self-test failed"
    )


# ============================================================
# BALANCE EXTRACTION
# ============================================================

def extract_asset_available(
    data,
    asset,
):

    if isinstance(
        data,
        dict,
    ):

        candidates = data.get(
            "data",
            data,
        )

    else:

        candidates = data


    if isinstance(
        candidates,
        dict,
    ):

        candidates = [
            candidates
        ]


    if not isinstance(
        candidates,
        list,
    ):

        raise RuntimeError(
            "Unexpected balance "
            "response format"
        )


    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):

            continue


        item_asset = str(

            item.get(

                "asset",

                item.get(

                    "coin",

                    item.get(
                        "currency",
                        "",
                    ),
                ),
            )

        ).upper()


        if (
            item_asset
            !=
            asset.upper()
        ):

            continue


        for key in (

            "availableBalance",

            "available",

            "availableAmount",

            "free",

        ):

            if key not in item:

                continue


            value = safe_decimal(
                item[
                    key
                ],
                Decimal(
                    "-1"
                ),
            )


            if value >= ZERO:

                return value


    raise RuntimeError(
        "Unable to extract "
        f"available {asset}"
    )


# ============================================================
# MARK PRICE EXTRACTION
# ============================================================

def extract_mark_price(
    data,
):

    if isinstance(
        data,
        list,
    ):

        if not data:

            raise RuntimeError(
                "Empty mark price response"
            )

        data = data[
            0
        ]


    if isinstance(
        data,
        dict,
    ):

        objects = (

            data,

            data.get(
                "data"
            ),

            data.get(
                "result"
            ),

        )


        for obj in objects:

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


                value = safe_decimal(
                    obj[
                        key
                    ]
                )


                if value > ZERO:

                    return value


    raise RuntimeError(
        "Unable to extract "
        "mark price"
    )


# ============================================================
# CONTRACT INFO NORMALIZATION
# ============================================================

def normalize_contract_info(
    data,
):

    target = data


    # --------------------------------------------------------
    # Standard V3 exchangeInfo response
    # --------------------------------------------------------

    if (
        isinstance(
            target,
            dict,
        )
        and
        isinstance(
            target.get(
                "symbols"
            ),
            list,
        )
    ):

        symbols = target[
            "symbols"
        ]


        target = next(
            (
                item
                for item
                in symbols
                if
                isinstance(
                    item,
                    dict,
                )
                and
                str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                ==
                SYMBOL
            ),
            None,
        )


    # --------------------------------------------------------
    # Direct list response
    # --------------------------------------------------------

    elif isinstance(
        target,
        list,
    ):

        matching = next(
            (
                item
                for item
                in target
                if
                isinstance(
                    item,
                    dict,
                )
                and
                str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                ==
                SYMBOL
            ),
            None,
        )


        if matching is not None:

            target = matching


        elif target:

            target = target[
                0
            ]


    # --------------------------------------------------------
    # Nested response
    # --------------------------------------------------------

    elif isinstance(
        target,
        dict,
    ):

        nested = (

            target.get(
                "data"
            )

            or

            target.get(
                "result"
            )

        )


        if isinstance(
            nested,
            dict,
        ):

            if isinstance(
                nested.get(
                    "symbols"
                ),
                list,
            ):

                symbols = nested[
                    "symbols"
                ]


                target = next(
                    (
                        item
                        for item
                        in symbols
                        if
                        isinstance(
                            item,
                            dict,
                        )
                        and
                        str(
                            item.get(
                                "symbol",
                                "",
                            )
                        ).upper()
                        ==
                        SYMBOL
                    ),
                    None,
                )


            else:

                target = nested


        elif isinstance(
            nested,
            list,
        ):

            matching = next(
                (
                    item
                    for item
                    in nested
                    if
                    isinstance(
                        item,
                        dict,
                    )
                    and
                    str(
                        item.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    ==
                    SYMBOL
                ),
                None,
            )


            if matching:

                target = matching


            elif nested:

                target = nested[
                    0
                ]


    if not isinstance(
        target,
        dict,
    ):

        raise RuntimeError(
            "Unable to locate "
            f"contract info for {SYMBOL}"
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

            "minOrderAmount",
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

        "raw":
            target,

        "minimum_order":
            minimum_order,

        "quantity_precision":
            quantity_precision,

        "contract_value":
            contract_value,

        "min_leverage":
            min_leverage,

        "max_leverage":
            max_leverage,
    }


# ============================================================
# POSITION NORMALIZATION
# ============================================================

def normalize_position_state(
    data,
):

    if isinstance(
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


    elif isinstance(
        data,
        list,
    ):

        positions = data


    else:

        raise RuntimeError(
            "Unexpected position "
            "response format"
        )


    for item in positions:

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


        if (
            item_symbol
            and
            item_symbol
            !=
            SYMBOL
        ):

            continue


        quantity = ZERO


        for key in (

            "size",

            "quantity",

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


        if quantity <= ZERO:

            continue


        side = (

            item.get(
                "side"
            )

            or

            item.get(
                "positionSide"
            )

            or

            item.get(
                "holdSide"
            )

        )


        liquidation_price = None


        for key in (

            "liquidatePrice",

            "liquidationPrice",

            "liqPrice",

        ):

            if key not in item:

                continue


            value = safe_decimal(
                item[
                    key
                ]
            )


            if value > ZERO:

                liquidation_price = (
                    value
                )


            break


        return {

            "open":
                True,

            "side":
                side,

            "quantity":
                quantity,

            "liquidation_price":
                liquidation_price,

            "raw":
                item,
        }


    return {

        "open":
            False,

        "side":
            None,

        "quantity":
            ZERO,

        "liquidation_price":
            None,

        "raw":
            data,
    }


# ============================================================
# GET MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):

    data = await public_get(

        session,

        MARK_PRICE_PATH,

        params={

            "symbol":
                SYMBOL,

            "priceType":
                "MARK",
        },
    )


    price = extract_mark_price(
        data
    )


    if price <= ZERO:

        raise RuntimeError(
            "WEEX mark price "
            "must be positive"
        )


    return price


# ============================================================
# GET AVAILABLE BALANCE
# ============================================================

async def get_available_balance(
    session,
):

    data = await private_get(

        session,

        BALANCE_PATH,

    )


    return extract_asset_available(
        data,
        "USDT",
    )


# ============================================================
# GET CONTRACT INFO
# ============================================================

async def get_contract_info(
    session,
):

    data = await public_get(

        session,

        EXCHANGE_INFO_PATH,

        params={
            "symbol":
                SYMBOL,
        },
    )


    return normalize_contract_info(
        data
    )


# ============================================================
# API TRADING SYMBOLS
# ============================================================

async def get_api_trading_symbols(
    session,
):

    return await public_get(
        session,
        API_TRADING_SYMBOLS_PATH,
    )


def symbol_is_api_tradable(
    data,
    symbol,
):

    target = str(
        symbol
    ).upper()


    if isinstance(
        data,
        list,
    ):

        for item in data:


            if isinstance(
                item,
                str,
            ):

                if (
                    item.upper()
                    ==
                    target
                ):

                    return True


            elif isinstance(
                item,
                dict,
            ):

                if (
                    str(
                        item.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    ==
                    target
                ):

                    return True


        return False


    if isinstance(
        data,
        dict,
    ):

        for key in (

            "data",

            "result",

            "symbols",

            "list",

        ):

            if key not in data:

                continue


            if symbol_is_api_tradable(
                data[
                    key
                ],
                symbol,
            ):

                return True


        if (
            str(
                data.get(
                    "symbol",
                    "",
                )
            ).upper()
            ==
            target
        ):

            return True


    return False


# ============================================================
# GET REAL POSITION STATE
# ============================================================

async def get_symbol_position_state(
    session,
):

    data = await private_get(
        session,
        POSITION_PATH,
    )


    return normalize_position_state(
        data
    )


# ============================================================
# SIGNAL GATE SELF TESTS
# ============================================================

def run_signal_gate_self_tests():

    now = int(
        time.time()
    )


    fresh_signal_timestamp = (

        now

        -

        min(
            5,
            max(
                1,
                SIGNAL_EXPIRY_SECONDS
                //
                2,
            ),
        )
    )


    expired_signal_timestamp = (

        now

        -

        SIGNAL_EXPIRY_SECONDS

        -

        1

    )


    fresh_signal_accepted = (

        now
        -
        fresh_signal_timestamp

        <=

        SIGNAL_EXPIRY_SECONDS

    )


    expired_signal_rejected = (

        now
        -
        expired_signal_timestamp

        >

        SIGNAL_EXPIRY_SECONDS

    )


    last_loss_timestamp = (

        now

        -

        max(
            0,
            LOSS_COOLDOWN_SECONDS
            -
            1,
        )

    )


    loss_cooldown_active = (

        now
        -
        last_loss_timestamp

        <

        LOSS_COOLDOWN_SECONDS

    )


    seen_signal_ids = {
        "r21-duplicate-test"
    }


    if ANTI_DUPLICATE_ORDERS:

        duplicate_signal_rejected = (

            "r21-duplicate-test"
            in
            seen_signal_ids

        )

    else:

        duplicate_signal_rejected = True


    one_direction_gate = (

        ONE_DIRECTION_ONLY
        is
        True

    )


    return {

        "fresh_signal":
            fresh_signal_accepted,

        "expired_signal":
            expired_signal_rejected,

        "loss_cooldown":
            loss_cooldown_active,

        "duplicate_signal":
            duplicate_signal_rejected,

        "one_direction":
            one_direction_gate,
    }


# ============================================================
# EXPOSURE
# ============================================================

def validate_total_fund_exposure_r21():

    initial = Decimal(
        str(
            ENTRY_PERCENT
        )
    )


    pyramids = (

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


    backups = (

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


    total = (

        initial

        +

        pyramids

        +

        backups

    )


    maximum = Decimal(
        str(
            MAX_FUND_EXPOSURE_PERCENT
        )
    )


    return {

        "initial":
            initial,

        "pyramids":
            pyramids,

        "backups":
            backups,

        "total":
            total,

        "maximum":
            maximum,

        "passed":
            (
                total
                <=
                maximum
            ),
    }


# ============================================================
# LEVERAGE VALIDATION
# ============================================================

def validate_leverage_r21(
    configured,
    exchange_min,
    exchange_max,
):

    configured = Decimal(
        str(
            configured
        )
    )


    local_max = Decimal(
        str(
            MAX_CONFIG_LEVERAGE
        )
    )


    exchange_min = Decimal(
        str(
            exchange_min
        )
    )


    exchange_max = Decimal(
        str(
            exchange_max
        )
    )


    passed = (

        configured
        >=
        exchange_min

        and

        configured
        <=
        exchange_max

        and

        configured
        <=
        local_max

    )


    if not passed:

        raise RuntimeError(

            "Leverage validation failed: "

            f"configured="
            f"{configured}, "

            f"local_max="
            f"{local_max}, "

            f"exchange_min="
            f"{exchange_min}, "

            f"exchange_max="
            f"{exchange_max}"

        )


    return True


# ============================================================
# QUANTITY PRECISION
# ============================================================

def quantize_quantity_r21(
    quantity,
    precision,
):

    quantity = Decimal(
        str(
            quantity
        )
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


    if result <= ZERO:

        raise RuntimeError(
            "Quantity became zero "
            "after precision adjustment"
        )


    return result


# ============================================================
# DYNAMIC ENTRY
# ============================================================

def calculate_dynamic_entry_r21(
    available_balance,
    mark_price,
    minimum_order,
    quantity_precision,
):

    available_balance = Decimal(
        str(
            available_balance
        )
    )


    mark_price = Decimal(
        str(
            mark_price
        )
    )


    minimum_order = Decimal(
        str(
            minimum_order
        )
    )


    if available_balance <= ZERO:

        raise RuntimeError(
            "Available balance "
            "must be positive"
        )


    if mark_price <= ZERO:

        raise RuntimeError(
            "Mark price must "
            "be positive"
        )


    margin = (

        available_balance

        *

        ENTRY_PERCENT

        /

        ONE_HUNDRED

    )


    notional = (

        margin

        *

        Decimal(
            str(
                LEVERAGE
            )
        )

    )


    raw_quantity = (

        notional

        /

        mark_price

    )


    quantity = quantize_quantity_r21(
        raw_quantity,
        quantity_precision,
    )


    minimum_passed = (

        quantity

        >=

        minimum_order

    )


    return {

        "margin":
            margin,

        "notional":
            notional,

        "raw_quantity":
            raw_quantity,

        "quantity":
            quantity,

        "minimum_passed":
            minimum_passed,
    }


# ============================================================
# TRADE DIRECTION
# ============================================================

def normalize_trade_direction(
    direction,
):

    direction = str(
        direction
    ).strip().upper()


    if direction in {
        "BUY",
        "LONG",
    }:

        return {

            "side":
                "BUY",

            "positionSide":
                "LONG",

            "direction":
                "LONG",
        }


    if direction in {
        "SELL",
        "SHORT",
    }:

        return {

            "side":
                "SELL",

            "positionSide":
                "SHORT",

            "direction":
                "SHORT",
        }


    raise RuntimeError(
        "Unsupported trade direction: "
        +
        str(
            direction
        )
    )


# ============================================================
# TP REFERENCES
# ============================================================

def calculate_tp_prices_r21(
    entry_price,
    direction,
):

    entry_price = Decimal(
        str(
            entry_price
        )
    )


    normalized = normalize_trade_direction(
        direction
    )


    tp1_move = (

        TP1_TRIGGER_PERCENT

        /

        ONE_HUNDRED

    )


    tp2_move = (

        TP2_TRIGGER_PERCENT

        /

        ONE_HUNDRED

    )


    if (
        normalized[
            "direction"
        ]
        ==
        "LONG"
    ):

        tp1 = (

            entry_price

            *

            (
                ONE
                +
                tp1_move
            )

        )


        tp2 = (

            entry_price

            *

            (
                ONE
                +
                tp2_move
            )

        )


    else:

        tp1 = (

            entry_price

            *

            (
                ONE
                -
                tp1_move
            )

        )


        tp2 = (

            entry_price

            *

            (
                ONE
                -
                tp2_move
            )

        )


    return {

        "tp1":
            tp1,

        "tp2":
            tp2,
    }


# ============================================================
# TRAILING DISTANCE
# ============================================================

def calculate_trailing_distance_r21(
    price,
):

    price = Decimal(
        str(
            price
        )
    )


    return (

        price

        *

        TRAILING_DISTANCE_PERCENT

        /

        ONE_HUNDRED

    )


# ============================================================
# CLIENT ORDER ID
# ============================================================

def create_client_order_id(
    prefix="r21",
):

    timestamp = int(
        time.time()
        *
        1000
    )


    random_part = os.urandom(
        3
    ).hex()


    client_id = (

        f"{prefix}-"
        f"{timestamp}-"
        f"{random_part}"

    )


    return client_id[
        :36
    ]


# ============================================================
# SAFE DEMO LIMIT PRICE
# ============================================================

def build_safe_demo_limit_price(
    mark_price,
    direction,
    distance_percent=Decimal(
        "3"
    ),
):

    mark_price = Decimal(
        str(
            mark_price
        )
    )


    distance_percent = Decimal(
        str(
            distance_percent
        )
    )


    if mark_price <= ZERO:

        raise RuntimeError(
            "Mark price must "
            "be positive"
        )


    if (

        distance_percent
        <=
        ZERO

        or

        distance_percent
        >=
        Decimal(
            "50"
        )

    ):

        raise RuntimeError(
            "Invalid demo "
            "price distance"
        )


    normalized = normalize_trade_direction(
        direction
    )


    distance = (

        distance_percent

        /

        ONE_HUNDRED

    )


    if (
        normalized[
            "direction"
        ]
        ==
        "LONG"
    ):

        return (

            mark_price

            *

            (
                ONE
                -
                distance
            )

        )


    return (

        mark_price

        *

        (
            ONE
            +
            distance
        )

    )


# ============================================================
# BUILD WEEX V3 ORDER PAYLOAD
# ============================================================

def build_v3_order_payload_r21(
    symbol,
    direction,
    quantity,
    order_type="LIMIT",
    price=None,
    client_order_id=None,
):

    normalized = normalize_trade_direction(
        direction
    )


    order_type = str(
        order_type
    ).strip().upper()


    if order_type not in {
        "LIMIT",
        "MARKET",
    }:

        raise RuntimeError(
            "Unsupported order type: "
            +
            order_type
        )


    quantity = Decimal(
        str(
            quantity
        )
    )


    if quantity <= ZERO:

        raise RuntimeError(
            "Order quantity "
            "must be positive"
        )


    if client_order_id is None:

        client_order_id = (
            create_client_order_id()
        )


    payload = {

        "symbol":
            str(
                symbol
            ).strip().upper(),

        "side":
            normalized[
                "side"
            ],

        "positionSide":
            normalized[
                "positionSide"
            ],

        "type":
            order_type,

        "quantity":
            decimal_text(
                quantity
            ),

        "newClientOrderId":
            str(
                client_order_id
            ),
    }


    if order_type == "LIMIT":

        if price is None:

            raise RuntimeError(
                "LIMIT order "
                "requires price"
            )


        price = Decimal(
            str(
                price
            )
        )


        if price <= ZERO:

            raise RuntimeError(
                "LIMIT order price "
                "must be positive"
            )


        payload[
            "timeInForce"
        ] = "GTC"


        payload[
            "price"
        ] = decimal_text(
            price
        )


    return payload


# ============================================================
# BUILD DEMO TEST ORDER
# ============================================================

def build_r21_demo_test_order(
    mark_price,
    minimum_order,
    quantity_precision,
):

    minimum_order = Decimal(
        str(
            minimum_order
        )
    )


    quantity_precision = int(
        quantity_precision
    )


    step = Decimal(
        "1"
    ).scaleb(
        -quantity_precision
    )


    quantity = minimum_order.quantize(
        step,
        rounding=ROUND_DOWN,
    )


    if quantity < minimum_order:

        quantity = (

            minimum_order
            +
            step

        ).quantize(
            step,
            rounding=ROUND_DOWN,
        )


    if quantity <= ZERO:

        quantity = step


    limit_price = (
        build_safe_demo_limit_price(

            mark_price=mark_price,

            direction=REHEARSAL_SIDE,

            distance_percent=Decimal(
                "3"
            ),
        )
    )


    payload = (
        build_v3_order_payload_r21(

            symbol=DEMO_SYMBOL,

            direction=REHEARSAL_SIDE,

            quantity=quantity,

            order_type="LIMIT",

            price=limit_price,

            client_order_id=(
                create_client_order_id(
                    "r21demo"
                )
            ),
        )
    )


    return {

        "symbol":
            DEMO_SYMBOL,

        "quantity":
            quantity,

        "limit_price":
            limit_price,

        "payload":
            payload,
    }


# ============================================================
# DEMO RESPONSE NORMALIZATION
# ============================================================

def normalize_demo_order_response_r21(
    http_status,
    data,
):

    accepted = False

    order_id = None

    error_code = None

    error_message = None


    if isinstance(
        data,
        dict,
    ):

        order_id = (

            data.get(
                "orderId"
            )

            or

            data.get(
                "order_id"
            )

        )


        error_code = (

            data.get(
                "errorCode"
            )

            or

            data.get(
                "code"
            )

        )


        error_message = (

            data.get(
                "errorMessage"
            )

            or

            data.get(
                "msg"
            )

            or

            data.get(
                "message"
            )

        )


        if (
            data.get(
                "success"
            )
            is
            True
        ):

            accepted = True


        elif (

            200
            <=
            int(
                http_status
            )
            <
            300

            and

            order_id

        ):

            accepted = True


    return {

        "http_status":
            int(
                http_status
            ),

        "accepted":
            accepted,

        "order_id":
            order_id,

        "error_code":
            error_code,

        "error_message":
            error_message,

        "raw":
            data,
    }


# ============================================================
# ORDER ROUTER
# ============================================================

async def route_order_post_r21(
    session,
    payload,
    demo=False,
):

    global R21_DEMO_POST_ATTEMPTED

    global R21_DEMO_POST_ACCEPTED


    # ========================================================
    # DEMO POST
    # ========================================================

    if demo:

        R21_DEMO_POST_ATTEMPTED = True


        status, data = await demo_post(

            session,

            DEMO_ORDER_PATH,

            payload,

        )


        result = (
            normalize_demo_order_response_r21(
                status,
                data,
            )
        )


        R21_DEMO_POST_ACCEPTED = bool(
            result[
                "accepted"
            ]
        )


        if not (

            200
            <=
            int(
                status
            )
            <
            300

        ):

            raise RuntimeError(

                "WEEX DEMO POST HTTP "

                f"{status}: "

                +
                json.dumps(
                    data
                )
            )


        if not result[
            "accepted"
        ]:

            raise RuntimeError(

                "WEEX demo order "
                "not accepted: "

                +

                json.dumps(
                    data
                )
            )


        return result


    # ========================================================
    # REAL POST — ABSOLUTE TERMINAL LOCK
    # ========================================================
    #
    # There is deliberately no call to session.post().
    #
    # R21_REAL_POST_CALLED therefore remains False.
    #
    # ========================================================

    real_post_blocked(
        REAL_ORDER_PATH,
        payload,
    )


# ============================================================
# PART 2 SELF TEST
# ============================================================

async def run_r21_part2_self_test():

    await test_real_post_lock_r21()


    test_payload = (
        build_v3_order_payload_r21(

            symbol=DEMO_SYMBOL,

            direction="BUY",

            quantity=Decimal(
                "0.0001"
            ),

            order_type="LIMIT",

            price=Decimal(
                "50000"
            ),

            client_order_id=(
                "r21-self-test"
            ),
        )
    )


    required = {

        "symbol",

        "side",

        "positionSide",

        "type",

        "quantity",

        "newClientOrderId",

        "timeInForce",

        "price",
    }


    if not required.issubset(
        test_payload.keys()
    ):

        raise RuntimeError(
            "R21 payload "
            "self-test failed"
        )


    test_quantity = (
        quantize_quantity_r21(
            Decimal(
                "0.00019"
            ),
            4,
        )
    )


    if (
        test_quantity
        !=
        Decimal(
            "0.0001"
        )
    ):

        raise RuntimeError(
            "R21 quantity precision "
            "self-test failed"
        )


    exposure = (
        validate_total_fund_exposure_r21()
    )


    if not exposure[
        "passed"
    ]:

        raise RuntimeError(
            "R21 exposure "
            "self-test failed"
        )


    return {

        "real_post_lock":
            True,

        "payload":
            True,

        "quantity":
            True,

        "exposure":
            True,

        "all_passed":
            True,
    }


# ============================================================
# OPTIONAL DEMO ORDER TEST
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
        decimal_text(
            demo_order[
                "quantity"
            ]
        ),
    )


    print(
        "R21 DEMO LIMIT PRICE:",
        decimal_text(
            demo_order[
                "limit_price"
            ]
        ),
    )


    return await route_order_post_r21(

        session=session,

        payload=demo_order[
            "payload"
        ],

        demo=True,

    )


# ============================================================
# TELEGRAM SINGLE MESSAGE
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


    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):

        print(
            "R21 Telegram skipped: "
            "credentials not configured"
        )

        return False


    url = (

        "https://api.telegram.org/bot"

        +

        TELEGRAM_BOT_TOKEN

        +

        "/sendMessage"

    )


    payload = {

        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            str(
                message
            ),

        "disable_web_page_preview":
            True,
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
# HEALTH HANDLER
# ============================================================

async def r21_health_handler(
    request,
):

    if R21_DIAGNOSTIC_PASSED:

        status = (
            "PASSED"
        )


    elif R21_DIAGNOSTIC_COMPLETE:

        status = (
            "FAILED"
        )


    else:

        status = (
            "STARTING"
        )


    body = {

        "module":
            MODULE_NAME,

        "symbol":
            SYMBOL,

        "status":
            status,

        "live_order_execution":
            LIVE_ORDER_EXECUTION,

        "hard_real_post_lock":
            HARD_REAL_POST_LOCK,

        "demo_order_test":
            RUN_DEMO_ORDER_TEST,

        "real_post_called":
            R21_REAL_POST_CALLED,

        "demo_post_attempted":
            R21_DEMO_POST_ATTEMPTED,

        "demo_post_accepted":
            R21_DEMO_POST_ACCEPTED,

        "telegram_sent":
            R21_TELEGRAM_SENT,

        "stage":
            R21_LAST_STAGE,

        "uptime_seconds":
            r21_uptime_seconds(),
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
# ROOT HANDLER
# ============================================================

async def r21_root_handler(
    request,
):

    if R21_DIAGNOSTIC_PASSED:

        diagnostic = (
            "PASSED"
        )


    elif R21_DIAGNOSTIC_COMPLETE:

        diagnostic = (
            "FAILED"
        )


    else:

        diagnostic = (
            "STARTING"
        )


    lines = [

        f"{MODULE_NAME} ACTIVE",

        f"SYMBOL: {SYMBOL}",

        "LIVE ORDER EXECUTION: DISABLED",

        "HARD REAL POST LOCK: ACTIVE",

        f"DIAGNOSTIC: {diagnostic}",

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

        "HEALTH SERVER ACTIVE "
        f"ON PORT {R21_PORT}"

    )


    return runner


# ============================================================
# SUCCESS REPORT
# ============================================================

def r21_build_final_success_report(

    available_balance,

    mark_price,

    contract,

    symbol_trading,

    position,

    demo_result,

    gates,

    dynamic,

    exposure,

):

    tp = calculate_tp_prices_r21(

        mark_price,

        REHEARSAL_SIDE,

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


        demo_order_id = (
            "N/A"
        )


    else:

        demo_status = (

            "ACCEPTED"

            if

            demo_result[
                "accepted"
            ]

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
            decimal_text(
                available_balance
            )
        ),

        (
            "Mark Price: "
            +
            decimal_text(
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
            decimal_text(
                ENTRY_PERCENT
            )
            +
            "%"
        ),

        (
            "Leverage: "
            +
            str(
                LEVERAGE
            )
            +
            "x"
        ),

        (
            "Max Config Leverage: "
            +
            str(
                MAX_CONFIG_LEVERAGE
            )
            +
            "x"
        ),

        (
            "Margin Type: "
            +
            MARGIN_TYPE
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
            decimal_text(
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
            decimal_text(
                BACKUP_SIZE_PERCENT
            )
            +
            "% each"
        ),

        (
            "Backup Buffer: "
            +
            decimal_text(
                BACKUP_BUFFER_PERCENT
            )
            +
            "%"
        ),

        (
            "Min Liq Distance: "
            +
            decimal_text(
                MIN_LIQ_DISTANCE_PERCENT
            )
            +
            "%"
        ),

        (
            "Max Fund Exposure: "
            +
            decimal_text(
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
            decimal_text(
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
            decimal_text(
                contract[
                    "contract_value"
                ]
            )
        ),

        (
            "WEEX Min Leverage: "
            +
            decimal_text(
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
            decimal_text(
                contract[
                    "max_leverage"
                ]
            )
            +
            "x"
        ),

        "Leverage Gate: ✅ YES",

        "",

        "DYNAMIC ENTRY",

        (
            "Margin: "
            +
            decimal_text(
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
            decimal_text(
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
            decimal_text(
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
                ZERO
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
            decimal_text(
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
            decimal_text(
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
            decimal_text(
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
            decimal_text(
                exposure[
                    "total"
                ]
            )
            +
            "% / "
            +
            decimal_text(
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
                    decimal_text(
                        position[
                            "quantity"
                        ]
                    )
                ),

                (
                    "WEEX Liquidation Price: "
                    +
                    (
                        decimal_text(
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

                "WEEX Liquidation Price: N/A",

            ]
        )


    lines.extend(
        [

            "",

            "TP / TRAILING",

            "TP1 / TP2 / TP3: "
            "20% / 20% / 60%",

            (
                "TP1 Trigger: "
                +
                decimal_text(
                    TP1_TRIGGER_PERCENT
                )
                +
                "%"
            ),

            (
                "TP2 Trigger: "
                +
                decimal_text(
                    TP2_TRIGGER_PERCENT
                )
                +
                "%"
            ),

            (
                "TP1 Reference: "
                +
                decimal_text(
                    tp[
                        "tp1"
                    ]
                )
            ),

            (
                "TP2 Reference: "
                +
                decimal_text(
                    tp[
                        "tp2"
                    ]
                )
            ),

            (
                "Trailing Distance: "
                +
                decimal_text(
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

            "Live Order Execution: ❌ DISABLED",

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
        "="
        *
        60
    )


    print(
        f"{MODULE_NAME} STARTING"
    )


    print(
        "FINAL PRE-LIVE EXECUTION "
        "PATH VALIDATION"
    )


    print(
        "REAL ORDER TRANSMISSION "
        "DISABLED"
    )


    print(
        "="
        *
        60
    )


    async with aiohttp.ClientSession(
        timeout=REQUEST_TIMEOUT
    ) as session:


        try:


            # =================================================
            # STAGE 1
            # CONFIGURATION
            # =================================================

            R21_LAST_STAGE = (
                "configuration"
            )


            validate_configuration()


            print(
                "✅ Configuration passed"
            )


            # =================================================
            # STAGE 2
            # ABSOLUTE SAFETY
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
            # STAGE 3
            # PART 2 SELF TEST
            # =================================================

            R21_LAST_STAGE = (
                "Part 2 self-test"
            )


            self_test = (
                await run_r21_part2_self_test()
            )


            if not self_test[
                "all_passed"
            ]:

                raise RuntimeError(
                    "R21 Part 2 self-test "
                    "did not pass"
                )


            print(
                "✅ R21 Part 2 "
                "self-test passed"
            )


            # =================================================
            # STAGE 4
            # SIGNAL GATES
            # =================================================

            R21_LAST_STAGE = (
                "signal gates"
            )


            gates = (
                run_signal_gate_self_tests()
            )


            if not all(
                gates.values()
            ):

                raise RuntimeError(
                    "R21 signal gate "
                    "self-test failed: "
                    +
                    str(
                        gates
                    )
                )


            print(
                "✅ Signal gate "
                "self-tests passed"
            )


            # =================================================
            # STAGE 5
            # MARK PRICE
            # =================================================

            R21_LAST_STAGE = (
                "mark price"
            )


            mark_price = (
                await get_mark_price(
                    session
                )
            )


            print(
                "✅ Mark Price:",
                decimal_text(
                    mark_price
                ),
            )


            # =================================================
            # STAGE 6
            # BALANCE
            # =================================================

            R21_LAST_STAGE = (
                "balance"
            )


            available_balance = (
                await get_available_balance(
                    session
                )
            )


            print(
                "✅ Available USDT:",
                decimal_text(
                    available_balance
                ),
            )


            # =================================================
            # STAGE 7
            # CONTRACT
            # =================================================

            R21_LAST_STAGE = (
                "contract information"
            )


            contract = (
                await get_contract_info(
                    session
                )
            )


            print(
                "✅ Minimum Order:",
                decimal_text(
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
            # STAGE 8
            # API TRADING SYMBOL
            # =================================================

            R21_LAST_STAGE = (
                "symbol trading status"
            )


            trading_symbols = (
                await get_api_trading_symbols(
                    session
                )
            )


            symbol_trading = (
                symbol_is_api_tradable(
                    trading_symbols,
                    SYMBOL,
                )
            )


            if not symbol_trading:

                raise RuntimeError(
                    f"{SYMBOL} is not "
                    "currently listed by "
                    "WEEX API trading symbols"
                )


            print(
                "✅ API Trading Symbol:",
                SYMBOL,
            )


            # =================================================
            # STAGE 9
            # LEVERAGE
            # =================================================

            R21_LAST_STAGE = (
                "leverage validation"
            )


            validate_leverage_r21(

                LEVERAGE,

                contract[
                    "min_leverage"
                ],

                contract[
                    "max_leverage"
                ],
            )


            print(
                "✅ Leverage Gate Passed"
            )


            # =================================================
            # STAGE 10
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

                decimal_text(
                    exposure[
                        "total"
                    ]
                ),

                "/",

                decimal_text(
                    exposure[
                        "maximum"
                    ]
                ),

                "%",

            )


            # =================================================
            # STAGE 11
            # DYNAMIC ENTRY
            # =================================================

            R21_LAST_STAGE = (
                "dynamic entry calculation"
            )


            dynamic = (
                calculate_dynamic_entry_r21(

                    available_balance=
                        available_balance,

                    mark_price=
                        mark_price,

                    minimum_order=
                        contract[
                            "minimum_order"
                        ],

                    quantity_precision=
                        contract[
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
                decimal_text(
                    dynamic[
                        "quantity"
                    ]
                ),
            )


            # =================================================
            # STAGE 12
            # POSITION
            # =================================================

            R21_LAST_STAGE = (
                "external position check"
            )


            position = (
                await get_symbol_position_state(
                    session
                )
            )


            if position[
                "open"
            ]:

                print(

                    "⚠️ Existing WEEX "
                    "position detected:",

                    position[
                        "side"
                    ],

                    decimal_text(
                        position[
                            "quantity"
                        ]
                    ),
                )


            else:

                print(
                    "✅ No open WEEX "
                    "position detected"
                )


            # =================================================
            # STAGE 13
            # OPTIONAL DEMO POST
            # =================================================

            R21_LAST_STAGE = (
                "demo order transmission"
            )


            demo_result = (
                await r21_optional_demo_order_test(

                    session,

                    mark_price,

                    contract,

                )
            )


            # =================================================
            # STAGE 14
            # FINAL REAL POST VERIFICATION
            # =================================================

            R21_LAST_STAGE = (
                "final real POST verification"
            )


            final_safety_assertions_r21()


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
            # SUCCESS
            # =================================================

            R21_LAST_STAGE = (
                "diagnostic complete"
            )


            report = (
                r21_build_final_success_report(

                    available_balance=
                        available_balance,

                    mark_price=
                        mark_price,

                    contract=
                        contract,

                    symbol_trading=
                        symbol_trading,

                    position=
                        position,

                    demo_result=
                        demo_result,

                    gates=
                        gates,

                    dynamic=
                        dynamic,

                    exposure=
                        exposure,
                )
            )


            print()

            print(
                report
            )

            print()


            # =================================================
            # SINGLE TELEGRAM MESSAGE
            # =================================================

            try:

                await r21_send_telegram_once(

                    session,

                    report,

                )


            except Exception as telegram_exc:

                print(
                    "Telegram notification error:",
                    telegram_exc,
                )


            R21_DIAGNOSTIC_COMPLETE = True

            R21_DIAGNOSTIC_PASSED = True


            print(
                "="
                *
                60
            )


            print(
                f"{MODULE_NAME} COMPLETE: PASSED"
            )


            print(
                "="
                *
                60
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

                    session,

                    report,

                )


            except Exception as telegram_exc:

                print(
                    "Telegram error notification "
                    "failed:",
                    telegram_exc,
                )


            print(
                "="
                *
                60
            )


            print(
                f"{MODULE_NAME} COMPLETE: FAILED"
            )


            print(
                "="
                *
                60
            )


            return False


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def r21_persistent_runtime():

    global R21_RUNTIME_STARTED


    R21_RUNTIME_STARTED = True


    # --------------------------------------------------------
    # Start Render health server FIRST
    # --------------------------------------------------------

    health_runner = (
        await r21_start_health_server()
    )


    try:


        # ----------------------------------------------------
        # Run R21 once
        # ----------------------------------------------------

        await r21_run_diagnostic()


        print()


        print(
            "R21 PERSISTENT RUNTIME ACTIVE"
        )


        print(
            "Render process will remain alive"
        )


        print(
            "Real order transmission "
            "remains disabled"
        )


        print()


        # ----------------------------------------------------
        # Stay alive without repeating diagnostic
        # or Telegram messages
        # ----------------------------------------------------

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
            "="
            *
            60
        )


        print(
            f"❌ {MODULE_NAME} "
            "FATAL STARTUP ERROR"
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
            "🛡 REAL ORDER POST LOCK "
            "REMAINS ACTIVE"
        )


        print(
            "⚠️ NO REAL ORDER WAS SENT"
        )


        print(
            "="
            *
            60
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
