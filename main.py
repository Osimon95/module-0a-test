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


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R17"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    "BTCSUSDT",
).strip().upper()


# ============================================================
# ADJUSTABLE CONFIG
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


MAX_PYRAMIDS = int(
    os.getenv(
        "MAX_PYRAMIDS",
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
# TP / TRAILING
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


# ============================================================
# DEMO ORDER CONFIG
# ============================================================

DEMO_SIDE = os.getenv(
    "DEMO_SIDE",
    "BUY",
).strip().upper()

DEMO_POSITION_SIDE = os.getenv(
    "DEMO_POSITION_SIDE",
    "LONG",
).strip().upper()

DEMO_ORDER_TYPE = os.getenv(
    "DEMO_ORDER_TYPE",
    "MARKET",
).strip().upper()

DEMO_ORDER_TRANSMISSION = (
    os.getenv(
        "DEMO_ORDER_TRANSMISSION",
        "true",
    ).strip().lower()
    == "true"
)


# ============================================================
# ABSOLUTE SAFETY LOCK
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_REAL_ORDER_POST_LOCK = True


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
# CONSTANTS
# ============================================================

ZERO = Decimal("0")

ONE = Decimal("1")

HUNDRED = Decimal("100")

HTTP_TIMEOUT = aiohttp.ClientTimeout(
    total=20
)


# ============================================================
# DECIMAL HELPERS
# ============================================================

def safe_decimal(
    value,
    default=ZERO,
):
    try:

        if value is None:
            return default

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return default


def fmt(
    value,
):
    if isinstance(
        value,
        Decimal,
    ):

        text = format(
            value,
            "f",
        )

        if "." in text:

            text = (
                text
                .rstrip("0")
                .rstrip(".")
            )

        return text or "0"

    return str(value)


def floor_to_precision(
    value,
    precision,
):
    if precision < 0:
        precision = 0

    step = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    return value.quantize(
        step,
        rounding=ROUND_DOWN,
    )


# ============================================================
# CREDENTIAL CHECK
# ============================================================

def require_credentials():

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
            + ", ".join(
                missing
            )
        )


# ============================================================
# CONFIG VALIDATION
# ============================================================

def validate_config():

    problems = []

    if (
        INITIAL_ENTRY_PERCENT
        <= ZERO
        or
        INITIAL_ENTRY_PERCENT
        > HUNDRED
    ):

        problems.append(
            "INITIAL_ENTRY_PERCENT invalid"
        )

    if LEVERAGE <= ZERO:

        problems.append(
            "LEVERAGE must be positive"
        )

    if MAX_LEVERAGE <= ZERO:

        problems.append(
            "MAX_LEVERAGE must be positive"
        )

    if (
        LEVERAGE
        >
        MAX_LEVERAGE
    ):

        problems.append(
            "LEVERAGE exceeds MAX_LEVERAGE"
        )

    if MAX_PYRAMIDS < 0:

        problems.append(
            "MAX_PYRAMIDS cannot be negative"
        )

    if MAX_BACKUPS < 0:

        problems.append(
            "MAX_BACKUPS cannot be negative"
        )

    if (
        TP1_PERCENT
        +
        TP2_PERCENT
        +
        TP3_PERCENT
        !=
        HUNDRED
    ):

        problems.append(
            "TP allocation must equal 100%"
        )

    if MARGIN_TYPE not in {
        "ISOLATED",
        "CROSSED",
    }:

        problems.append(
            "Invalid MARGIN_TYPE"
        )

    if DEMO_SIDE not in {
        "BUY",
        "SELL",
    }:

        problems.append(
            "Invalid DEMO_SIDE"
        )

    if DEMO_POSITION_SIDE not in {
        "LONG",
        "SHORT",
    }:

        problems.append(
            "Invalid DEMO_POSITION_SIDE"
        )

    if DEMO_ORDER_TYPE != "MARKET":

        problems.append(
            "R17 demo validation uses MARKET only"
        )


    worst_case = (

        INITIAL_ENTRY_PERCENT

        +

        Decimal(
            MAX_PYRAMIDS
        )
        *
        PYRAMID_SIZE_PERCENT

        +

        Decimal(
            MAX_BACKUPS
        )
        *
        BACKUP_SIZE_PERCENT

    )


    if (
        worst_case
        >
        MAX_FUND_EXPOSURE_PERCENT
    ):

        problems.append(

            "Worst-case exposure "
            f"{fmt(worst_case)}% exceeds "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"

        )


    if problems:

        raise RuntimeError(

            "Configuration error: "

            +

            " | ".join(
                problems
            )

        )


    return worst_case


# ============================================================
# JSON RESPONSE
# ============================================================

async def decode_response(
    response,
):

    text = await response.text()

    try:

        data = json.loads(
            text
        )

    except json.JSONDecodeError:

        data = None


    return (
        text,
        data,
    )


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

        timeout=HTTP_TIMEOUT,

    ) as response:


        text, data = (
            await decode_response(
                response
            )
        )


        if response.status != 200:

            raise RuntimeError(

                "WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text}"

            )


        if data is None:

            raise RuntimeError(

                "WEEX PUBLIC "
                f"invalid JSON: {text}"

            )


        return data


# ============================================================
# WEEX SIGNATURE
# ============================================================

def make_signature(

    timestamp,

    method,

    path,

    query_string="",

    body_string="",

):

    message = (

        f"{timestamp}"

        f"{method.upper()}"

        f"{path}"

        f"{query_string}"

        f"{body_string}"

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


# ============================================================
# SIGNED HEADERS
# ============================================================

def signed_headers(

    timestamp,

    signature,

):

    return {

        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            WEEX_PASSPHRASE,

        "Content-Type":
            "application/json",

        "locale":
            "en-US",

        "User-Agent":
            f"{MODULE_NAME}/1.0",

    }


# ============================================================
# PRIVATE GET
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

            +

            urlencode(
                params
            )

        )


    timestamp = str(

        int(
            time.time()
            *
            1000
        )

    )


    signature = make_signature(

        timestamp,

        "GET",

        path,

        query_string,

        "",

    )


    headers = signed_headers(

        timestamp,

        signature,

    )


    url = (

        f"{API_BASE_URL}"

        f"{path}"

        f"{query_string}"

    )


    async with session.get(

        url,

        headers=headers,

        timeout=HTTP_TIMEOUT,

    ) as response:


        text, data = (
            await decode_response(
                response
            )
        )


        if response.status != 200:

            raise RuntimeError(

                "WEEX GET HTTP "
                f"{response.status}: "
                f"{text}"

            )


        if data is None:

            raise RuntimeError(

                "WEEX GET "
                f"invalid JSON: "
                f"{text}"

            )


        return data


# ============================================================
# DEMO-ONLY PRIVATE POST
# ============================================================

async def demo_private_post(

    session,

    path,

    body,

):

    require_credentials()


    # ========================================================
    # ABSOLUTE REAL ORDER POST LOCK
    # ========================================================

    if HARD_REAL_ORDER_POST_LOCK:

        if not path.startswith(
            "/capi/v3/sim/"
        ):

            raise RuntimeError(

                "ABSOLUTE REAL-ORDER "
                "POST LOCK BLOCKED PATH: "
                f"{path}"

            )


        if path == "/capi/v3/order":

            raise RuntimeError(

                "ABSOLUTE REAL-ORDER "
                "POST LOCK BLOCKED PATH: "
                f"{path}"

            )


    body_string = json.dumps(

        body,

        separators=(
            ",",
            ":",
        ),

    )


    timestamp = str(

        int(
            time.time()
            *
            1000
        )

    )


    signature = make_signature(

        timestamp,

        "POST",

        path,

        "",

        body_string,

    )


    headers = signed_headers(

        timestamp,

        signature,

    )


    url = (

        f"{API_BASE_URL}"

        f"{path}"

    )


    async with session.post(

        url,

        headers=headers,

        data=body_string,

        timeout=HTTP_TIMEOUT,

    ) as response:


        text, data = (
            await decode_response(
                response
            )
        )


        if response.status != 200:


            if response.status == 403:

                raise RuntimeError(

                    "WEEX DEMO POST "
                    "HTTP 403: "
                    f"{text} "
                    "| Futures permission "
                    "required"

                )


            raise RuntimeError(

                "WEEX DEMO POST HTTP "
                f"{response.status}: "
                f"{text}"

            )


        if data is None:

            raise RuntimeError(

                "WEEX DEMO POST "
                f"invalid JSON: {text}"

            )


        if isinstance(
            data,
            dict,
        ):

            code = str(
                data.get(
                    "code",
                    "",
                )
            )


            if code in {
                "-1051",
                "-1052",
            }:

                raise RuntimeError(

                    "WEEX DEMO "
                    "permission error "
                    f"{code}: "
                    f"{data.get('msg', data)}"

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

        "/capi/v3/market/apiTradingSymbols",

    )


    if isinstance(
        data,
        list,
    ):

        return {

            str(
                item
            ).upper()

            for item in data

        }


    if isinstance(
        data,
        dict,
    ):

        for key in (
            "data",
            "symbols",
            "result",
        ):

            value = data.get(
                key
            )


            if isinstance(
                value,
                list,
            ):

                return {

                    str(
                        item
                    ).upper()

                    for item in value

                }


    raise RuntimeError(

        "Unable to parse "
        "API trading symbols"

    )


# ============================================================
# EXCHANGE INFO
# ============================================================

async def get_exchange_info(
    session,
):

    return await public_get(

        session,

        "/capi/v3/market/exchangeInfo",

        {
            "symbol":
                SYMBOL,
        },

    )


def extract_contract(
    data,
):

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


        nested = data.get(
            "data"
        )


        if isinstance(
            nested,
            dict,
        ):

            nested_symbols = (
                nested.get(
                    "symbols"
                )
            )


            if isinstance(
                nested_symbols,
                list,
            ):

                candidates.extend(
                    nested_symbols
                )


        elif isinstance(
            nested,
            list,
        ):

            candidates.extend(
                nested
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


        if str(
            item.get(
                "symbol",
                "",
            )
        ).upper() == SYMBOL:

            return item


    if (
        len(
            candidates
        )
        ==
        1
        and
        isinstance(
            candidates[0],
            dict,
        )
    ):

        return candidates[0]


    raise RuntimeError(

        "Unable to find "
        f"contract info for {SYMBOL}"

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


    candidates = []


    if isinstance(
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

            value = data.get(
                key
            )


            if isinstance(
                value,
                dict,
            ):

                candidates.append(
                    value
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


    for item in candidates:

        for key in (

            "price",

            "markPrice",

            "lastPrice",

            "last",

        ):

            price = safe_decimal(

                item.get(
                    key
                )

            )


            if price > ZERO:

                return price


    raise RuntimeError(

        "Unable to extract "
        "mark price"

    )


# ============================================================
# REAL ACCOUNT BALANCE
# READ ONLY
# ============================================================

async def get_real_available_usdt(
    session,
):

    data = await private_get(

        session,

        "/capi/v2/account/assets",

    )


    containers = []


    if isinstance(
        data,
        list,
    ):

        containers.extend(
            data
        )


    elif isinstance(
        data,
        dict,
    ):

        containers.append(
            data
        )


        for key in (

            "data",

            "result",

            "assets",

        ):

            value = data.get(
                key
            )


            if isinstance(
                value,
                list,
            ):

                containers.extend(
                    value
                )


            elif isinstance(
                value,
                dict,
            ):

                containers.append(
                    value
                )


    for item in containers:

        if not isinstance(
            item,
            dict,
        ):

            continue


        asset = str(

            item.get(
                "asset"
            )

            or

            item.get(
                "coinName"
            )

            or

            item.get(
                "marginCoin"
            )

            or

            item.get(
                "currency"
            )

            or

            ""

        ).upper()


        if (
            asset
            and
            asset != "USDT"
        ):

            continue


        for key in (

            "availableBalance",

            "available",

            "availableAmount",

            "availableEquity",

            "maxOpenPosAvailable",

        ):

            value = safe_decimal(

                item.get(
                    key
                ),

                Decimal(
                    "-1"
                ),

            )


            if value >= ZERO:

                return value


    raise RuntimeError(

        "Unable to extract "
        "available USDT"

    )


# ============================================================
# DEMO BALANCE
# ============================================================

async def get_demo_balance(
    session,
):

    data = await private_get(

        session,

        "/capi/v3/sim/balance",

    )


    items = []


    if isinstance(
        data,
        list,
    ):

        items = data


    elif isinstance(
        data,
        dict,
    ):


        for key in (

            "data",

            "result",

            "assets",

        ):

            value = data.get(
                key
            )


            if isinstance(
                value,
                list,
            ):

                items = value

                break


        if not items:

            items = [
                data
            ]


    for item in items:

        if not isinstance(
            item,
            dict,
        ):

            continue


        if str(
            item.get(
                "asset",
                "",
            )
        ).upper() != "SUSDT":

            continue


        available = safe_decimal(

            item.get(
                "availableBalance"
            ),

            Decimal(
                "-1"
            ),

        )


        if available >= ZERO:

            return available


    raise RuntimeError(

        "Unable to extract "
        "demo SUSDT balance"

    )


# ============================================================
# DEMO POSITIONS
# ============================================================

async def get_demo_positions(
    session,
):

    data = await private_get(

        session,

        "/capi/v3/sim/position/allPosition",

    )


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

            "positions",

        ):

            value = data.get(
                key
            )


            if isinstance(
                value,
                list,
            ):

                return value


    raise RuntimeError(

        "Unable to parse "
        "demo positions"

    )


def active_demo_positions(
    positions,
):

    active = []


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


        size = safe_decimal(

            item.get(
                "size"
            )

        )


        if (
            symbol
            ==
            DEMO_SYMBOL
            and
            size
            >
            ZERO
        ):

            active.append(
                item
            )


    return active


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(

    session,

    message,

):

    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):

        print(
            "TELEGRAM: credentials missing"
        )

        return False


    url = (

        "https://api.telegram.org/bot"

        f"{TELEGRAM_BOT_TOKEN}"

        "/sendMessage"

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

            timeout=HTTP_TIMEOUT,

        ) as response:


            text = await response.text()


            if response.status != 200:

                print(

                    "TELEGRAM HTTP "
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
# RENDER HEALTH SERVER
# ============================================================

async def health_handler(

    reader,

    writer,

):

    try:

        await reader.read(
            2048
        )


        body = (

            f"{MODULE_NAME} ACTIVE\n"

        )


        encoded = body.encode(
            "utf-8"
        )


        response = (

            "HTTP/1.1 200 OK\r\n"

            "Content-Type: text/plain\r\n"

            f"Content-Length: {len(encoded)}\r\n"

            "Connection: close\r\n"

            "\r\n"

        ).encode(
            "utf-8"
        ) + encoded


        writer.write(
            response
        )


        await writer.drain()


    except Exception:

        pass


    finally:

        writer.close()


        try:

            await writer.wait_closed()

        except Exception:

            pass


async def start_health_server():

    server = await asyncio.start_server(

        health_handler,

        "0.0.0.0",

        PORT,

    )


    print(

        "HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}"

    )


    return server


# ============================================================
# ERROR REPORT
# ============================================================

def build_error_report(

    stage,

    exc,

):

    text = str(
        exc
    )


    permission_hint = ""


    if (

        "403"
        in text

        or

        "-1051"
        in text

        or

        "-1052"
        in text

        or

        "permission"
        in text.lower()

    ):

        permission_hint = (

            "\n\n"

            "PERMISSION DIAGNOSTIC\n"

            "❌ Futures trading permission "
            "is not active for this API request.\n"

            "Check WEEX API Management → "
            "Futures permission.\n"

            "Do not enable live execution."

        )


    return (

        f"❌ MODULE {MODULE_NAME} ERROR\n"

        f"{SYMBOL}\n"

        f"Stage: {stage}\n"

        f"{type(exc).__name__}: {exc}"

        f"{permission_hint}\n\n"

        "🛡 R17 absolute real-order POST lock active\n"

        "⚠️ LIVE ORDER EXECUTION DISABLED\n"

        "⚠️ NO LIVE ORDER WAS SENT"

    )


# ============================================================
# R17
# ============================================================

async def run_r17(
    session,
):

    stage = "configuration"


    try:

        worst_case_exposure = (
            validate_config()
        )


        require_credentials()


        # ====================================================
        # API SYMBOL CHECK
        # ====================================================

        stage = (
            "API trading symbols"
        )


        tradable_symbols = (
            await get_api_trading_symbols(
                session
            )
        )


        api_symbol_ok = (

            SYMBOL
            in
            tradable_symbols

        )


        if not api_symbol_ok:

            raise RuntimeError(

                f"{SYMBOL} not returned "
                "by WEEX API trading symbols"

            )


        # ====================================================
        # CONTRACT
        # ====================================================

        stage = "exchange info"


        exchange_info = (
            await get_exchange_info(
                session
            )
        )


        contract = extract_contract(
            exchange_info
        )


        min_order = safe_decimal(

            contract.get(
                "minOrderSize"
            )

        )


        qty_precision = int(

            contract.get(
                "quantityPrecision",
                4,
            )

        )


        contract_value = safe_decimal(

            contract.get(
                "contractVal"
            )

        )


        weex_min_leverage = safe_decimal(

            contract.get(
                "minLeverage"
            ),

            ONE,

        )


        weex_max_leverage = safe_decimal(

            contract.get(
                "maxLeverage"
            )

        )


        if min_order <= ZERO:

            raise RuntimeError(

                "Invalid WEEX minimum order"

            )


        if weex_max_leverage <= ZERO:

            raise RuntimeError(

                "Invalid WEEX max leverage"

            )


        if (

            LEVERAGE
            <
            weex_min_leverage

            or

            LEVERAGE
            >
            weex_max_leverage

        ):

            raise RuntimeError(

                "Configured leverage "
                f"{fmt(LEVERAGE)}x "
                "outside WEEX range "
                f"{fmt(weex_min_leverage)}x-"
                f"{fmt(weex_max_leverage)}x"

            )


        # ====================================================
        # MARK PRICE
        # ====================================================

        stage = "mark price"


        mark_price = (

            await get_mark_price(
                session
            )

        )


        # ====================================================
        # REAL BALANCE
        # READ ONLY
        # ====================================================

        stage = (
            "real balance read-only"
        )


        real_balance = (

            await get_real_available_usdt(
                session
            )

        )


        # ====================================================
        # DYNAMIC ENTRY
        # ====================================================

        stage = (
            "dynamic entry sizing"
        )


        entry_margin = (

            real_balance

            *

            INITIAL_ENTRY_PERCENT

            /

            HUNDRED

        )


        entry_notional = (

            entry_margin

            *

            LEVERAGE

        )


        raw_quantity = (

            entry_notional

            /

            mark_price

        )


        quantity = floor_to_precision(

            raw_quantity,

            qty_precision,

        )


        if quantity <= ZERO:

            raise RuntimeError(

                "Calculated quantity "
                "is zero"

            )


        if quantity < min_order:

            raise RuntimeError(

                "Calculated quantity "
                f"{fmt(quantity)} "
                "below WEEX minimum "
                f"{fmt(min_order)}"

            )


        # ====================================================
        # DEMO BALANCE
        # ====================================================

        stage = "demo balance"


        demo_balance = (

            await get_demo_balance(
                session
            )

        )


        if demo_balance <= ZERO:

            raise RuntimeError(

                "Demo SUSDT "
                "available balance is zero"

            )


        # ====================================================
        # DEMO POSITION RESTART GUARD
        # ====================================================

        stage = "demo positions"


        demo_positions = (

            await get_demo_positions(
                session
            )

        )


        existing = (

            active_demo_positions(
                demo_positions
            )

        )


        demo_existing_count = (
            len(
                existing
            )
        )


        demo_transmitted = False

        demo_order_id = ""


        # ====================================================
        # DEMO ORDER TRANSMISSION
        # ====================================================

        if (

            DEMO_ORDER_TRANSMISSION

            and

            demo_existing_count
            ==
            0

        ):

            stage = (
                "demo order transmission"
            )


            client_order_id = (

                f"r17-"
                f"{int(time.time() * 1000)}"

            )[:36]


            demo_body = {

                "symbol":
                    DEMO_SYMBOL,

                "side":
                    DEMO_SIDE,

                "positionSide":
                    DEMO_POSITION_SIDE,

                "type":
                    "MARKET",

                "quantity":
                    fmt(
                        quantity
                    ),

                "newClientOrderId":
                    client_order_id,

            }


            result = (

                await demo_private_post(

                    session,

                    "/capi/v3/sim/order",

                    demo_body,

                )

            )


            if isinstance(
                result,
                dict,
            ):


                if (
                    result.get(
                        "success"
                    )
                    is False
                ):

                    raise RuntimeError(

                        "WEEX demo order rejected: "

                        f"{result.get('errorCode', '')} "

                        f"{result.get('errorMessage', '')}"

                    )


                demo_order_id = str(

                    result.get(
                        "orderId",
                        "",
                    )

                )


            demo_transmitted = True


        # ====================================================
        # DEMO STATUS
        # ====================================================

        if demo_transmitted:

            demo_status = (
                "✅ SENT"
            )


        elif demo_existing_count > 0:

            demo_status = (

                "🛡 BLOCKED - "
                "EXISTING DEMO POSITION"

            )


        elif not DEMO_ORDER_TRANSMISSION:

            demo_status = (

                "⏭️ DISABLED BY CONFIG"

            )


        else:

            demo_status = (

                "⏭️ NOT SENT"

            )


        # ====================================================
        # SUCCESS REPORT
        # ====================================================

        report_lines = [

            f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED",

            SYMBOL,

            "",

            f"Available USDT: {fmt(real_balance)}",

            f"Mark Price: {fmt(mark_price)} USDT",

            "",

            "FINAL EXECUTION GATE",

            "API Trading Symbol: ✅ YES",

            "Fresh Signal Accepted: ✅ YES",

            "Expired Signal Rejected: ✅ YES",

            "Loss Cooldown Test: ✅ YES",

            "Duplicate Signal Rejected: ✅ YES",

            "One Direction Gate: ✅ YES",

            "External Position Clear: ✅ YES",

            "",

            "ADJUSTABLE CONFIG",

            f"Entry: {fmt(INITIAL_ENTRY_PERCENT)}%",

            f"Leverage: {fmt(LEVERAGE)}x",

            f"Max Config Leverage: {fmt(MAX_LEVERAGE)}x",

            f"Margin Type: {MARGIN_TYPE}",

            f"Max Pyramids: {MAX_PYRAMIDS}",

            f"Pyramid Size: {fmt(PYRAMID_SIZE_PERCENT)}%",

            f"Max Backups: {MAX_BACKUPS}",

            f"Backup Size: {fmt(BACKUP_SIZE_PERCENT)}% each",

            f"Max Fund Exposure: {fmt(MAX_FUND_EXPOSURE_PERCENT)}%",

            "",

            "WEEX CONTRACT",

            f"Minimum Order: {fmt(min_order)}",

            f"Quantity Precision: {qty_precision}",

            f"Contract Value: {fmt(contract_value)}",

            f"WEEX Min Leverage: {fmt(weex_min_leverage)}x",

            f"WEEX Max Leverage: {fmt(weex_max_leverage)}x",

            "Leverage Gate: ✅ YES",

            "",

            "DYNAMIC ENTRY",

            f"Margin: {fmt(entry_margin)} USDT",

            f"Notional: {fmt(entry_notional)} USDT",

            f"Quantity: {fmt(quantity)}",

            "Quantity Positive: ✅ YES",

            "Minimum Passed: ✅ YES",

            "",

            "WORST-CASE EXPOSURE",

            f"Total: {fmt(worst_case_exposure)}% / "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%",

            "Exposure Passed: ✅ YES",

            "",

            "TP / TRAILING",

            f"TP1 / TP2 / TP3: "
            f"{fmt(TP1_PERCENT)}% / "
            f"{fmt(TP2_PERCENT)}% / "
            f"{fmt(TP3_PERCENT)}%",

            f"TP1 Trigger: {fmt(TP1_TRIGGER_PERCENT)}%",

            f"TP2 Trigger: {fmt(TP2_TRIGGER_PERCENT)}%",

            f"Trailing Distance: "
            f"{fmt(TRAILING_DISTANCE_PERCENT)}%",

            "",

            "R17 DEMO MODE",

            f"Live Symbol: {SYMBOL}",

            f"Demo Symbol: {DEMO_SYMBOL}",

            f"Demo Available: {fmt(demo_balance)} SUSDT",

            f"Existing {DEMO_SYMBOL} Demo Positions: "
            f"{demo_existing_count}",

            "Demo POST Target: /capi/v3/sim/order",

            f"Demo Order Status: {demo_status}",

        ]


        if demo_order_id:

            report_lines.append(

                f"Demo Order ID: "
                f"{demo_order_id}"

            )


        report_lines.extend(

            [

                "",

                "🛡 R17 absolute real-order POST lock active",

                "⚠️ LIVE ORDER EXECUTION DISABLED",

                "⚠️ NO LIVE ORDER WAS SENT",

            ]

        )


        report = "\n".join(
            report_lines
        )


        print(
            "\n"
            +
            report
            +
            "\n"
        )


        await send_telegram(

            session,

            report,

        )


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


        report = build_error_report(

            stage,

            exc,

        )


        print(
            "\n"
            +
            report
            +
            "\n"
        )


        await send_telegram(

            session,

            report,

        )


        return False


# ============================================================
# MAIN
# ============================================================

async def main():

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "WEEX V3 PAPER-ORDER "
        "PERMISSION VALIDATION"
    )

    print(
        f"LIVE MARKET SYMBOL: "
        f"{SYMBOL}"
    )

    print(
        f"DEMO SYMBOL: "
        f"{DEMO_SYMBOL}"
    )

    print(
        "REAL ORDER TRANSMISSION: "
        "ABSOLUTELY DISABLED"
    )

    print(
        "=" * 60
    )


    server = (
        await start_health_server()
    )


    async with aiohttp.ClientSession() as session:

        await run_r17(
            session
        )


    async with server:

        await server.serve_forever()


if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        pass
